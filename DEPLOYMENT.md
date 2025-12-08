# Deployment Guide - Clinical Protocol Intelligence

This guide will help you deploy the Clinical Protocol Intelligence solution in your Snowflake environment.

## Prerequisites

### Snowflake Requirements
- ✅ **Snowflake Account** with Enterprise Edition or higher
- ✅ **Cortex Search** enabled (contact Snowflake if not available)
- ✅ **Cortex AI Services** enabled (AI Complete, LLMs)
- ✅ **Streamlit in Snowflake** enabled
- ✅ **ACCOUNTADMIN** role (for initial setup)
- ✅ **Compute warehouse** (recommend Small or Medium)

### Permissions Required
- `CREATE DATABASE` or access to existing database
- `CREATE SCHEMA`
- `CREATE STAGE`, `CREATE TABLE`, `CREATE FUNCTION`
- `CREATE CORTEX SEARCH SERVICE`
- `CREATE STREAMLIT`
- `USAGE` on PYPI packages (`SNOWFLAKE.PYPI_REPOSITORY_USER` role)

---

## Step 1: Configuration

1. **Copy the configuration template:**
   ```bash
   cp config.example.py config.py
   ```

2. **Edit `config.py` with your values:**
   ```python
   DATABASE_NAME = "PRODUCTION"        # Your database name
   SCHEMA_NAME = "PDF_OCR"             # Your schema name
   WAREHOUSE_NAME = "COMPUTE_WH"       # Your warehouse
   ```

3. **Update `setup.sql` (lines 27-32):**
   ```sql
   -- Replace these with your values:
   CREATE SCHEMA IF NOT EXISTS PRODUCTION.PDF_OCR;
   USE DATABASE PRODUCTION;
   USE SCHEMA PDF_OCR;
   ```

4. **Update `streamlit_app.py` (lines 42-43):**
   - Import from your `config.py` file (see Step 3 below)

---

## Step 2: Database Setup

### Run the setup script:

```sql
-- Connect to Snowflake (Snowsight, SnowSQL, or Python)
-- Execute setup.sql in order

-- Verify completion:
SHOW STAGES LIKE 'PDF_STAGE';
SHOW FUNCTIONS LIKE 'pdf_txt_mapper_v3';
SHOW TABLES LIKE 'document_chunks';
SHOW CORTEX SEARCH SERVICES LIKE 'protocol_search';
SHOW PROCEDURES LIKE 'process_new_pdfs';
```

**Expected objects created:**
- ✅ Stage: `@PDF_STAGE`
- ✅ UDF: `pdf_txt_mapper_v3()`
- ✅ Table: `document_chunks`
- ✅ Function: `calculate_position_description()`
- ✅ Cortex Search Service: `protocol_search`
- ✅ Stored Procedure: `process_new_pdfs()`
- ✅ Task: `process_pdfs_task` (suspended)

---

## Step 3: Deploy Streamlit App

### Option A: Snowsight UI

1. Navigate to **Streamlit** tab in Snowsight
2. Click **+ Streamlit App**
3. Name: `Clinical_Protocol_Intelligence`
4. Warehouse: Select your compute warehouse
5. App location: Choose database and schema
6. Copy contents of `streamlit_app.py` into the editor
7. Click **Run**

### Option B: SnowCLI (Command Line)

```bash
# Install SnowCLI if not already installed
pip install snowflake-cli

# Deploy
snow streamlit deploy \
  --name clinical_protocol_intelligence \
  --file streamlit_app.py \
  --database PRODUCTION \
  --schema PDF_OCR \
  --warehouse COMPUTE_WH
```

---

## Step 4: Upload Sample PDFs

### Upload PDFs to the stage:

**Option A: Snowsight UI**
1. Navigate to **Data** → **Databases** → Your Database → Your Schema
2. Click on `PDF_STAGE`
3. Click **Upload Files**
4. Select your PDF files
5. Click **Upload**

**Option B: SnowSQL**
```sql
PUT file:///path/to/your/protocol.pdf @PDF_STAGE AUTO_COMPRESS=FALSE;
```

**Option C: Python (Snowpark)**
```python
from snowflake.snowpark import Session

session.file.put(
    "local_file.pdf",
    "@PRODUCTION.PDF_OCR.PDF_STAGE",
    auto_compress=False,
    overwrite=True
)
```

---

## Step 5: Process PDFs

Run the stored procedure to extract text and build search index:

```sql
-- Process all new PDFs
CALL PRODUCTION.PDF_OCR.process_new_pdfs();

-- Expected output:
-- "Successfully processed N new PDF(s)"

-- Verify processing:
SELECT 
    doc_name,
    COUNT(*) as total_chunks,
    MAX(page) as total_pages,
    MAX(extracted_at) as processed_at
FROM PRODUCTION.PDF_OCR.document_chunks
GROUP BY doc_name
ORDER BY processed_at DESC;
```

---

## Step 6: Test the Application

1. **Open your Streamlit app** (from Snowsight → Streamlit)

2. **Verify documents appear** in the sidebar

3. **Test a search query:**
   - "What is the dosing schedule for nivolumab?"
   - Should return results with citations

4. **Verify AI synthesis** is working (check sidebar toggle)

5. **Test document upload** (sidebar uploader)

---

## Step 7: Configure Automated Processing (Optional)

Enable the task to automatically process new PDFs:

```sql
-- Enable automatic processing (runs every 60 minutes)
ALTER TASK PRODUCTION.PDF_OCR.process_pdfs_task RESUME;

-- Check task status:
SHOW TASKS LIKE 'process_pdfs_task';

-- View task history:
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    TASK_NAME => 'PROCESS_PDFS_TASK',
    SCHEDULED_TIME_RANGE_START => DATEADD('day', -7, CURRENT_TIMESTAMP())
))
ORDER BY SCHEDULED_TIME DESC;
```

---

## Security & Governance

### Role-Based Access Control (RBAC)

```sql
-- Create a read-only role for end users
CREATE ROLE IF NOT EXISTS PDF_VIEWER;

-- Grant usage permissions
GRANT USAGE ON DATABASE PRODUCTION TO ROLE PDF_VIEWER;
GRANT USAGE ON SCHEMA PRODUCTION.PDF_OCR TO ROLE PDF_VIEWER;
GRANT SELECT ON ALL TABLES IN SCHEMA PRODUCTION.PDF_OCR TO ROLE PDF_VIEWER;
GRANT USAGE ON CORTEX SEARCH SERVICE PRODUCTION.PDF_OCR.protocol_search TO ROLE PDF_VIEWER;

-- Grant Streamlit access
GRANT USAGE ON STREAMLIT PRODUCTION.PDF_OCR.CLINICAL_PROTOCOL_INTELLIGENCE TO ROLE PDF_VIEWER;

-- Assign to users
GRANT ROLE PDF_VIEWER TO USER your_user_name;
```

### Data Governance

- **Network Policies**: Restrict access by IP if needed
- **Audit Logging**: All queries are automatically logged
- **Data Masking**: Apply if PDFs contain PII/PHI
- **Row Access Policies**: Restrict document access by user

---

## Monitoring & Troubleshooting

### Check Cortex Search Status
```sql
DESCRIBE CORTEX SEARCH SERVICE PRODUCTION.PDF_OCR.protocol_search;
```

### View Query History
```sql
SELECT 
    query_text,
    execution_status,
    error_message,
    total_elapsed_time,
    start_time
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE query_text ILIKE '%protocol_search%'
   OR query_text ILIKE '%process_new_pdfs%'
ORDER BY start_time DESC
LIMIT 20;
```

### Refresh Search Index Manually
```sql
ALTER CORTEX SEARCH SERVICE PRODUCTION.PDF_OCR.protocol_search REFRESH;
```

### Debug Upload Issues
```sql
-- Check what's in the stage
SELECT * FROM DIRECTORY(@PRODUCTION.PDF_OCR.PDF_STAGE);

-- Check what's been processed
SELECT DISTINCT doc_name FROM PRODUCTION.PDF_OCR.document_chunks;

-- Find files that need processing
SELECT RELATIVE_PATH 
FROM DIRECTORY(@PRODUCTION.PDF_OCR.PDF_STAGE)
WHERE RELATIVE_PATH LIKE '%.pdf'
AND RELATIVE_PATH NOT IN (SELECT DISTINCT doc_name FROM PRODUCTION.PDF_OCR.document_chunks);
```

---

## Cost Optimization

### Recommended Settings
- **Warehouse**: AUTO_SUSPEND = 60 seconds
- **Warehouse Size**: Small (sufficient for most workloads)
- **Cortex Search**: TARGET_LAG = '1 hour' (faster = more cost)
- **Task Schedule**: Adjust based on upload frequency

### Monitor Costs
```sql
-- Check warehouse usage
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE WAREHOUSE_NAME = 'COMPUTE_WH'
  AND START_TIME >= DATEADD('day', -7, CURRENT_TIMESTAMP())
ORDER BY START_TIME DESC;

-- Check Cortex AI usage
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY
WHERE SERVICE_TYPE IN ('AI_SERVICES', 'SEARCH_OPTIMIZATION')
ORDER BY START_TIME DESC;
```

---

## Support & Resources

### Documentation
- [Snowflake Cortex Search](https://docs.snowflake.com/en/user-guide/cortex-search)
- [Snowflake Cortex AI](https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions)
- [Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)

### Getting Help
- **Snowflake Support**: support.snowflake.com
- **Community**: community.snowflake.com
- **GitHub Issues**: (this repository)

---

## Next Steps

1. ✅ Upload your clinical protocol PDFs
2. ✅ Train your team on the UI
3. ✅ Configure RBAC for your users
4. ✅ Set up monitoring dashboards
5. ✅ Schedule regular index maintenance

**🎉 Your Clinical Protocol Intelligence solution is ready for production!**

