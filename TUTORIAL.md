# Clinical Protocol Intelligence - Tutorial
**Build AI-Powered Document Q&A with Snowflake Cortex**

## What You'll Build

An intelligent document search application that:
- ⚡ Searches clinical protocols with natural language
- 📍 Provides audit-grade citations with exact page coordinates
- 🤖 Synthesizes answers using multiple LLM models
- 🔒 Runs 100% within your Snowflake environment

## What You'll Learn

- How to extract text from PDFs with position tracking using Python UDFs
- How to build semantic search with Snowflake Cortex Search
- How to implement RAG (Retrieval Augmented Generation) patterns
- How to create interactive apps with Streamlit in Snowflake

## Prerequisites

- ✅ Snowflake account (Enterprise Edition or higher)
- ✅ ACCOUNTADMIN role access
- ✅ Cortex Search and Cortex AI enabled
- ✅ Basic SQL knowledge
- ✅ Sample PDF files (clinical protocols or similar documents)

**⏱️ Estimated Time:** 30-45 minutes

---

## Architecture Overview

```
PDF → @STAGE → Python UDF → Table → Cortex Search → LLM → Streamlit UI
```

**Data Flow:**
1. Upload PDFs to Snowflake stage
2. Python UDF extracts text + bounding boxes
3. Store in structured table
4. Cortex Search creates semantic index
5. User asks questions via Streamlit
6. RAG pattern: Search → Context → LLM Answer
7. Display results with precise citations

---

## Step 1: Setup Your Snowflake Environment

**Duration:** 5 minutes

### What You'll Do
- Create database and schema
- Grant PyPI package access
- Set up compute warehouse

### SQL Commands

```sql
-- 1. Use administrative role
USE ROLE ACCOUNTADMIN;

-- 2. Grant access to Python packages
GRANT DATABASE ROLE SNOWFLAKE.PYPI_REPOSITORY_USER TO ROLE ACCOUNTADMIN;

-- 3. Create schema
CREATE SCHEMA IF NOT EXISTS YOUR_DATABASE.YOUR_SCHEMA
    COMMENT = 'Clinical Protocol Intelligence Solution';

-- 4. Set context
USE DATABASE YOUR_DATABASE;
USE SCHEMA YOUR_SCHEMA;

-- 5. Verify compute warehouse exists
SHOW WAREHOUSES LIKE 'COMPUTE_WH';
-- If not exists, create one:
-- CREATE WAREHOUSE COMPUTE_WH WITH WAREHOUSE_SIZE = 'SMALL' AUTO_SUSPEND = 60;
```

### ✅ Verify Success
```sql
-- Should see your schema
SHOW SCHEMAS IN DATABASE YOUR_DATABASE;
```

---

## Step 2: Create PDF Storage Stage

**Duration:** 2 minutes

### What You'll Do
- Create internal stage for PDF storage
- Enable directory table for file tracking

### SQL Commands

```sql
-- Create stage with directory tracking
CREATE STAGE IF NOT EXISTS PDF_STAGE
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Storage for clinical protocol PDFs';

-- Verify
SHOW STAGES LIKE 'PDF_STAGE';
```

### ✅ Verify Success
```sql
-- Should show your stage
DESC STAGE PDF_STAGE;
```

---

## Step 3: Create PDF Text Extraction UDF

**Duration:** 3 minutes

### What You'll Do
- Create Python UDF using pdfminer library
- Extract text with full bounding box coordinates
- Return structured JSON with page info

### SQL Commands

```sql
-- Run the entire CREATE FUNCTION statement from setup.sql
-- Lines 52-102

-- After creation, verify:
SHOW FUNCTIONS LIKE 'pdf_txt_mapper_v3';
```

### 🧪 Test the UDF

Upload a test PDF first:
```sql
-- Upload via Snowsight UI: Data → Databases → Your Schema → PDF_STAGE → Upload

-- Then test extraction:
SELECT pdf_txt_mapper_v3(
    build_scoped_file_url(@PDF_STAGE, 'your_test_file.pdf')
) AS extracted_json;
```

### ✅ Expected Output
Should return JSON like:
```json
[
  {
    "page": 1,
    "bbox": [118.92, 678.14, 508.78, 697.29],
    "page_width": 595.25,
    "page_height": 841.9,
    "txt": "Protocol Title..."
  }
]
```

---

## Step 4: Create Document Chunks Table

**Duration:** 2 minutes

### What You'll Do
- Create structured table for extracted text
- Include position metadata (bbox, page dimensions)
- Set up for Cortex Search indexing

### SQL Commands

```sql
CREATE TABLE IF NOT EXISTS document_chunks (
    chunk_id VARCHAR PRIMARY KEY,
    doc_name VARCHAR NOT NULL,
    page INTEGER NOT NULL,
    text VARCHAR,
    bbox_x0 FLOAT,
    bbox_y0 FLOAT,
    bbox_x1 FLOAT,
    bbox_y1 FLOAT,
    page_width FLOAT,
    page_height FLOAT,
    extracted_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Verify
DESC TABLE document_chunks;
```

---

## Step 5: Create Cortex Search Service

**Duration:** 3 minutes (+ 2-5 min index build time)

### What You'll Do
- Create semantic search service
- Configure Arctic embedding model
- Set update frequency

### SQL Commands

```sql
CREATE CORTEX SEARCH SERVICE protocol_search
    ON text
    ATTRIBUTES page, doc_name, bbox_x0, bbox_y0, bbox_x1, bbox_y1, 
               page_width, page_height
    WAREHOUSE = COMPUTE_WH
    TARGET_LAG = '1 hour'
    EMBEDDING_MODEL = 'snowflake-arctic-embed-l-v2.0'
    AS (
        SELECT 
            chunk_id,
            doc_name,
            page,
            text,
            bbox_x0, bbox_y0, bbox_x1, bbox_y1,
            page_width, page_height
        FROM document_chunks
    );

-- Verify
SHOW CORTEX SEARCH SERVICES LIKE 'protocol_search';
```

### ⏳ Index Building
The service will build its index in the background. Check status:
```sql
DESCRIBE CORTEX SEARCH SERVICE protocol_search;
```

---

## Step 6: Create Processing Automation

**Duration:** 3 minutes

### What You'll Do
- Create stored procedure to process PDFs
- Automate text extraction and indexing

### SQL Commands

```sql
-- Run the entire CREATE PROCEDURE statement from setup.sql
-- Lines 208-270

-- Verify
SHOW PROCEDURES LIKE 'process_new_pdfs';
```

---

## Step 7: Upload and Process Your First PDF

**Duration:** 5 minutes

### Upload PDF

**Option A: Snowsight UI**
1. Navigate to **Data** → **Databases** → Your Schema
2. Click **PDF_STAGE**
3. Click **Upload Files**
4. Select your PDF
5. Click **Upload**

**Option B: SnowSQL**
```sql
PUT file:///path/to/your/protocol.pdf @PDF_STAGE AUTO_COMPRESS=FALSE;
```

### Process the PDF

```sql
-- Run the processing procedure
CALL process_new_pdfs();

-- Expected output:
-- "Successfully processed 1 new PDF(s)"
```

### ✅ Verify Processing

```sql
-- Check extracted chunks
SELECT 
    doc_name,
    COUNT(*) as total_chunks,
    MAX(page) as total_pages
FROM document_chunks
GROUP BY doc_name;

-- View sample content
SELECT 
    doc_name,
    page,
    LEFT(text, 100) as text_preview
FROM document_chunks
LIMIT 10;
```

---

## Step 8: Test Cortex Search

**Duration:** 3 minutes

### Try a Search Query

```sql
-- Using modern SEARCH_PREVIEW function
SELECT
  SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'protocol_search',
    '{
      "query": "dosing schedule",
      "columns": ["doc_name", "page", "text", "bbox_x0", "bbox_y0"],
      "limit": 5
    }'
  ) AS search_results;
```

### ✅ Expected Output
Should return JSON with relevant chunks containing "dosing schedule" information.

---

## Step 9: Deploy Streamlit Application

**Duration:** 5 minutes

### Configure the App

1. Copy `config.example.py` to `config.py`
2. Edit `config.py`:
```python
DATABASE_NAME = "YOUR_DATABASE"
SCHEMA_NAME = "YOUR_SCHEMA"
```

### Deploy via Snowsight

1. Go to **Streamlit** tab in Snowsight
2. Click **+ Streamlit App**
3. **Name:** Clinical_Protocol_Intelligence
4. **Warehouse:** COMPUTE_WH
5. **App location:** Your database and schema
6. Copy contents of `streamlit_app.py`
7. Click **Run**

### ✅ Verify App Launches
- Should see the main interface
- Sidebar shows "Document Browser"
- Your uploaded PDF appears in the dropdown

---

## Step 10: Test the Complete Solution

**Duration:** 5 minutes

### Try These Queries

1. **Simple fact extraction:**
   ```
   "What is the study title?"
   ```

2. **Dosing information:**
   ```
   "What is the dosing schedule for nivolumab?"
   ```

3. **Study design:**
   ```
   "What is the study phase and design?"
   ```

### ✅ Success Criteria

You should see:
- ✅ AI-generated answer in natural language
- ✅ Multiple source citations with page numbers
- ✅ Exact coordinates [x0, y0, x1, y1] for each citation
- ✅ Ability to expand and view full source text

---

## Troubleshooting

### Issue: Search returns no results

**Solution:**
```sql
-- Manually refresh the search index
ALTER CORTEX SEARCH SERVICE protocol_search REFRESH;

-- Wait 30 seconds, then retry
```

### Issue: PDF processing fails

**Check:**
```sql
-- View recent errors
SELECT 
    query_text,
    error_message,
    start_time
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE query_text ILIKE '%process_new_pdfs%'
ORDER BY start_time DESC
LIMIT 5;
```

### Issue: Streamlit app won't load

**Verify:**
- Warehouse is running
- Database and schema names match config
- No firewall/network policies blocking Streamlit

---

## Next Steps

### Add More Documents
```sql
-- Upload more PDFs to @PDF_STAGE
-- Then process them:
CALL process_new_pdfs();
```

### Try Different LLM Models
In the Streamlit app sidebar:
- Switch between Claude, Llama, GPT, Mistral
- Compare answer quality and speed

### Configure Access Control
```sql
-- Create role for end users
CREATE ROLE PDF_VIEWER;
GRANT USAGE ON DATABASE YOUR_DATABASE TO ROLE PDF_VIEWER;
GRANT USAGE ON SCHEMA YOUR_SCHEMA TO ROLE PDF_VIEWER;
GRANT SELECT ON ALL TABLES IN SCHEMA YOUR_SCHEMA TO ROLE PDF_VIEWER;
GRANT USAGE ON STREAMLIT YOUR_SCHEMA.CLINICAL_PROTOCOL_INTELLIGENCE TO ROLE PDF_VIEWER;
```

---

## Congratulations! 🎉

You've built a production-ready AI document intelligence application!

**What You've Accomplished:**
- ✅ PDF text extraction with position tracking
- ✅ Semantic search with Cortex Search
- ✅ RAG-based Q&A with multiple LLMs
- ✅ Interactive Streamlit interface
- ✅ Audit-grade citations with coordinates

**Learn More:**
- [Snowflake Cortex Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex)
- [Streamlit in Snowflake Guide](https://docs.snowflake.com/en/developer-guide/streamlit)
- [DEPLOYMENT.md](DEPLOYMENT.md) for production setup

---

**Questions?** Open an issue on GitHub or contact your Snowflake account team.

