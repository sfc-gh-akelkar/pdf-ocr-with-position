-- ============================================================================
-- PDF OCR with Position Tracking - Database Setup
-- ============================================================================
-- This script creates all database objects needed for the PDF Q&A solution.
-- Run this once to set up the environment.
--
-- What this creates:
-- 1. Database schema and stage for PDFs
-- 2. UDF for PDF text extraction with bounding boxes
-- 3. Table for storing document chunks
-- 4. Position calculator function
-- 5. Cortex Search service for semantic search
-- 6. Automated PDF processing (directory table, procedure, task)
-- ============================================================================

-- ============================================================================
-- PART 1: Environment Setup
-- ============================================================================

-- Use administrative role
USE ROLE accountadmin;

-- Grant access to PyPI packages (needed for pdfminer library)
GRANT DATABASE ROLE SNOWFLAKE.PYPI_REPOSITORY_USER TO ROLE accountadmin;

-- Create schema
CREATE SCHEMA IF NOT EXISTS SANDBOX.PDF_OCR
    COMMENT = 'Schema for PDF OCR with position tracking solution';

-- Set context
USE DATABASE SANDBOX;
USE SCHEMA PDF_OCR;

-- ============================================================================
-- PART 2: Stage for PDF Storage
-- ============================================================================

-- Create internal stage for PDF files with directory table enabled
CREATE STAGE IF NOT EXISTS PDF_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Stage for storing clinical protocol PDFs and other documents';

-- Create directory table to track files
CREATE OR REPLACE TABLE PDF_STAGE_DIR AS
    SELECT * FROM DIRECTORY(@PDF_STAGE);

-- ============================================================================
-- PART 3: PDF Text Extraction UDF
-- ============================================================================

-- Enhanced UDF that extracts text with full bounding boxes and page info
CREATE OR REPLACE FUNCTION pdf_txt_mapper_v3(scoped_file_url string)
RETURNS VARCHAR
LANGUAGE PYTHON
RUNTIME_VERSION = '3.12'
ARTIFACT_REPOSITORY = snowflake.snowpark.pypi_shared_repository
PACKAGES = ('snowflake-snowpark-python', 'pdfminer')
HANDLER = 'main'
AS
$$
import json
from snowflake.snowpark.files import SnowflakeFile
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator

def main(scoped_file_url):
    finding = []
    with SnowflakeFile.open(scoped_file_url, 'rb') as f:
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        pages = PDFPage.get_pages(f)
        
        # Track page numbers
        for page_num, page in enumerate(pages, start=1):
            interpreter.process_page(page)
            layout = device.get_result()
            
            # Get page dimensions
            page_width = layout.width
            page_height = layout.height
            
            for lobj in layout:
                if isinstance(lobj, LTTextBox):
                    # Capture FULL bounding box (all 4 corners)
                    x0, y0, x1, y1 = lobj.bbox
                    text = lobj.get_text()
                    
                    finding.append({
                        'page': page_num,
                        'bbox': [x0, y0, x1, y1],  # Full rectangle!
                        'page_width': page_width,
                        'page_height': page_height,
                        'txt': text
                    })
    
    return json.dumps(finding)
$$;

-- ============================================================================
-- PART 4: Document Chunks Table
-- ============================================================================

-- Table to store extracted text with position metadata
CREATE TABLE IF NOT EXISTS document_chunks (
    chunk_id VARCHAR PRIMARY KEY,
    doc_name VARCHAR NOT NULL,
    page INTEGER NOT NULL,
    text VARCHAR,
    -- Bounding box coordinates (PDF coordinate system: 0,0 at bottom-left)
    bbox_x0 FLOAT,  -- Bottom-left x
    bbox_y0 FLOAT,  -- Bottom-left y
    bbox_x1 FLOAT,  -- Top-right x
    bbox_y1 FLOAT,  -- Top-right y
    -- Page dimensions
    page_width FLOAT,
    page_height FLOAT,
    -- Metadata
    extracted_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ============================================================================
-- PART 5: Position Calculator Function
-- ============================================================================

-- Converts bounding box coordinates to human-readable positions
-- (e.g., "top-right", "middle-center", etc.)
CREATE OR REPLACE FUNCTION calculate_position_description(
    bbox_x0 FLOAT,
    bbox_y0 FLOAT,
    bbox_x1 FLOAT,
    bbox_y1 FLOAT,
    page_width FLOAT,
    page_height FLOAT
)
RETURNS OBJECT
LANGUAGE SQL
AS
$$
    SELECT OBJECT_CONSTRUCT(
        'position_description',
        CASE 
            -- Vertical position (PDF coords: 0 at bottom)
            -- Top third (y > 67%)
            WHEN ((bbox_y0 + bbox_y1) / 2 / page_height) > 0.67 THEN 
                CASE 
                    WHEN ((bbox_x0 + bbox_x1) / 2 / page_width) < 0.33 THEN 'top-left'
                    WHEN ((bbox_x0 + bbox_x1) / 2 / page_width) > 0.67 THEN 'top-right'
                    ELSE 'top-center'
                END
            -- Bottom third (y < 33%)
            WHEN ((bbox_y0 + bbox_y1) / 2 / page_height) < 0.33 THEN 
                CASE 
                    WHEN ((bbox_x0 + bbox_x1) / 2 / page_width) < 0.33 THEN 'bottom-left'
                    WHEN ((bbox_x0 + bbox_x1) / 2 / page_width) > 0.67 THEN 'bottom-right'
                    ELSE 'bottom-center'
                END
            -- Middle third (33% < y < 67%)
            ELSE 
                CASE 
                    WHEN ((bbox_x0 + bbox_x1) / 2 / page_width) < 0.33 THEN 'middle-left'
                    WHEN ((bbox_x0 + bbox_x1) / 2 / page_width) > 0.67 THEN 'middle-right'
                    ELSE 'middle-center'
                END
        END,
        'relative_x', ROUND(((bbox_x0 + bbox_x1) / 2 / page_width) * 100, 1),
        'relative_y', ROUND(((bbox_y0 + bbox_y1) / 2 / page_height) * 100, 1),
        'bbox', ARRAY_CONSTRUCT(bbox_x0, bbox_y0, bbox_x1, bbox_y1)
    )
$$;

-- ============================================================================
-- PART 6: Cortex Search Service
-- ============================================================================

-- Create Cortex Search Service for semantic search
-- Note: This may take a few minutes for initial index build
CREATE OR REPLACE CORTEX SEARCH SERVICE protocol_search
    ON text  -- Column to search (embeddings auto-generated)
    ATTRIBUTES page, doc_name  -- Columns available for filtering
    WAREHOUSE = compute_wh
    TARGET_LAG = '1 hour'
    EMBEDDING_MODEL = 'snowflake-arctic-embed-l-v2.0'  -- Best quality model
    AS (
        SELECT 
            chunk_id,
            doc_name,
            page,
            text,
            bbox_x0,
            bbox_y0,
            bbox_x1,
            bbox_y1,
            page_width,
            page_height
        FROM document_chunks
    );

-- ============================================================================
-- PART 7: Automated PDF Processing Pipeline
-- ============================================================================

-- Stored procedure to process new PDFs from the stage
CREATE OR REPLACE PROCEDURE process_new_pdfs()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
DECLARE
    processed_count INTEGER DEFAULT 0;
    result_message VARCHAR;
BEGIN
    -- Process each PDF in the stage that isn't already in document_chunks
    FOR pdf_file IN (
        SELECT RELATIVE_PATH 
        FROM DIRECTORY(@PDF_STAGE)
        WHERE RELATIVE_PATH LIKE '%.pdf'
        AND RELATIVE_PATH NOT IN (SELECT DISTINCT doc_name FROM document_chunks)
    ) DO
        -- Extract text with bounding boxes
        INSERT INTO document_chunks (
            chunk_id, doc_name, page, text,
            bbox_x0, bbox_y0, bbox_x1, bbox_y1,
            page_width, page_height
        )
        SELECT 
            :pdf_file.RELATIVE_PATH || '_p' || value:page || '_c' || 
                ROW_NUMBER() OVER (ORDER BY value:page, value:bbox[0], value:bbox[1]) AS chunk_id,
            :pdf_file.RELATIVE_PATH AS doc_name,
            value:page::INTEGER AS page,
            value:txt::VARCHAR AS text,
            value:bbox[0]::FLOAT AS bbox_x0,
            value:bbox[1]::FLOAT AS bbox_y0,
            value:bbox[2]::FLOAT AS bbox_x1,
            value:bbox[3]::FLOAT AS bbox_y1,
            value:page_width::FLOAT AS page_width,
            value:page_height::FLOAT AS page_height
        FROM (
            SELECT PARSE_JSON(
                pdf_txt_mapper_v3(
                    build_scoped_file_url(@PDF_STAGE, :pdf_file.RELATIVE_PATH)
                )
            ) AS parsed_data
        ),
        LATERAL FLATTEN(input => parsed_data) AS f;
        
        processed_count := processed_count + 1;
    END FOR;
    
    -- Refresh Cortex Search index
    IF (processed_count > 0) THEN
        ALTER CORTEX SEARCH SERVICE protocol_search REFRESH;
    END IF;
    
    result_message := 'Processed ' || processed_count || ' new PDF(s)';
    RETURN result_message;
END;
$$;

-- Create task to automatically process new PDFs every hour
CREATE OR REPLACE TASK process_pdfs_task
    WAREHOUSE = compute_wh
    SCHEDULE = '60 MINUTE'
AS
    CALL process_new_pdfs();

-- Note: Task is created in SUSPENDED state. To activate:
-- ALTER TASK process_pdfs_task RESUME;

-- ============================================================================
-- PART 8: Verification Queries
-- ============================================================================

-- Verify all objects were created
SHOW STAGES LIKE 'PDF_STAGE';
SHOW FUNCTIONS LIKE 'pdf_txt_mapper_v3';
SHOW FUNCTIONS LIKE 'calculate_position_description';
SHOW TABLES LIKE 'document_chunks';
SHOW CORTEX SEARCH SERVICES LIKE 'protocol_search';
SHOW PROCEDURES LIKE 'process_new_pdfs';
SHOW TASKS LIKE 'process_pdfs_task';

-- ============================================================================
-- MANUAL PROCESSING (First Time Setup)
-- ============================================================================

-- After uploading PDFs to @PDF_STAGE, run this to process them:
-- CALL process_new_pdfs();

-- Or process a specific PDF manually:
-- Example for 'Prot_000.pdf':
/*
INSERT INTO document_chunks (
    chunk_id, doc_name, page, text,
    bbox_x0, bbox_y0, bbox_x1, bbox_y1,
    page_width, page_height
)
SELECT 
    'Prot_000_p' || value:page || '_c' || 
        ROW_NUMBER() OVER (ORDER BY value:page, value:bbox[0], value:bbox[1]) AS chunk_id,
    'Prot_000.pdf' AS doc_name,
    value:page::INTEGER AS page,
    value:txt::VARCHAR AS text,
    value:bbox[0]::FLOAT AS bbox_x0,
    value:bbox[1]::FLOAT AS bbox_y0,
    value:bbox[2]::FLOAT AS bbox_x1,
    value:bbox[3]::FLOAT AS bbox_y1,
    value:page_width::FLOAT AS page_width,
    value:page_height::FLOAT AS page_height
FROM (
    SELECT PARSE_JSON(
        pdf_txt_mapper_v3(build_scoped_file_url(@PDF_STAGE, 'Prot_000.pdf'))
    ) AS parsed_data
),
LATERAL FLATTEN(input => parsed_data) AS f;
*/

-- ============================================================================
-- CLEANUP (Optional - only if you need to start over)
-- ============================================================================

-- DROP TASK IF EXISTS process_pdfs_task;
-- DROP PROCEDURE IF EXISTS process_new_pdfs();
-- DROP CORTEX SEARCH SERVICE IF EXISTS protocol_search;
-- DROP FUNCTION IF EXISTS calculate_position_description(FLOAT, FLOAT, FLOAT, FLOAT, FLOAT, FLOAT);
-- DROP TABLE IF EXISTS document_chunks;
-- DROP FUNCTION IF EXISTS pdf_txt_mapper_v3(STRING);
-- DROP STAGE IF EXISTS PDF_STAGE;
-- DROP SCHEMA IF EXISTS SANDBOX.PDF_OCR;

