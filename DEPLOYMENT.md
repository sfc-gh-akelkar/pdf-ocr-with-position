# Deployment Guide

## Prerequisites

- Snowflake account with Cortex AI & Cortex Search enabled
- ACCOUNTADMIN role (or sufficient privileges)

---

## 3-Step Deployment

### Step 1: Update Database & Schema Names

**In `setup.sql` (line 27, 31, 32):**
```sql
-- Change these to your values:
CREATE SCHEMA IF NOT EXISTS YOUR_DATABASE.YOUR_SCHEMA;
USE DATABASE YOUR_DATABASE;
USE SCHEMA YOUR_SCHEMA;
```

**In `streamlit_app.py` (lines 42-43):**
```python
# Change these to your values:
DATABASE_NAME = "YOUR_DATABASE"
SCHEMA_NAME = "YOUR_SCHEMA"
```

---

### Step 2: Run Setup Script

Execute `setup.sql` in Snowsight or SnowSQL.

This creates:
- Stage for PDF storage
- Python UDF for text extraction
- Table for document chunks
- Cortex Search service
- Stored procedure for automation

**Verify:**
```sql
SHOW STAGES LIKE 'PDF_STAGE';
SHOW FUNCTIONS LIKE 'pdf_txt_mapper_v3';
SHOW TABLES LIKE 'document_chunks';
SHOW CORTEX SEARCH SERVICES LIKE 'protocol_search';
```

---

### Step 3: Deploy Streamlit App

**In Snowsight:**
1. Go to **Streamlit** → **+ Streamlit App**
2. Name it (e.g., `Clinical_Protocol_Intelligence`)
3. Select warehouse, database, schema
4. Paste contents of `streamlit_app.py`
5. Click **Run**

**Done!** 🎉

---

## Usage

### Upload PDFs

**Via Snowsight:**
Data → Your Schema → PDF_STAGE → Upload Files

**Via SQL:**
```sql
PUT file:///path/to/your.pdf @PDF_STAGE AUTO_COMPRESS=FALSE;
```

### Process PDFs

```sql
CALL process_new_pdfs();
-- Returns: "Successfully processed N new PDF(s)"
```

### Start Searching

Open your Streamlit app and ask questions!

---

## Optional: Access Control

```sql
-- Create read-only role for users
CREATE ROLE PDF_VIEWER;
GRANT USAGE ON DATABASE YOUR_DATABASE TO ROLE PDF_VIEWER;
GRANT USAGE ON SCHEMA YOUR_SCHEMA TO ROLE PDF_VIEWER;
GRANT SELECT ON ALL TABLES IN SCHEMA YOUR_SCHEMA TO ROLE PDF_VIEWER;
GRANT USAGE ON STREAMLIT YOUR_SCHEMA.YOUR_APP_NAME TO ROLE PDF_VIEWER;

-- Assign to users
GRANT ROLE PDF_VIEWER TO USER username;
```

---

## Troubleshooting

**Search returns no results?**
```sql
-- Refresh the index
ALTER CORTEX SEARCH SERVICE protocol_search REFRESH;
```

**Processing fails?**
```sql
-- Check errors
SELECT query_text, error_message 
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE query_text ILIKE '%process_new_pdfs%'
ORDER BY start_time DESC LIMIT 5;
```

---

That's it! See [TUTORIAL.md](TUTORIAL.md) for detailed walkthrough.
