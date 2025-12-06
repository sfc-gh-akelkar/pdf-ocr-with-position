# Quick Start Guide - PDF OCR with Position Tracking

Get up and running in **10 minutes** with this streamlined setup guide.

---

## Prerequisites

✅ Snowflake account with `ACCOUNTADMIN` access  
✅ A warehouse (e.g., `compute_wh`)  
✅ Sample PDF file (e.g., `Prot_000.pdf`)

---

## Step-by-Step Setup

### **Step 1: Run Database Setup (5 minutes)**

1. Open Snowflake UI → **Worksheets**
2. Create a new SQL worksheet
3. Copy the **entire contents** of `setup.sql`
4. Execute the worksheet

**What this creates:**
- Schema: `SANDBOX.PDF_OCR`
- Stage: `@PDF_STAGE` for PDFs
- UDF: `pdf_txt_mapper_v3` for text extraction
- Table: `document_chunks` for storage
- Function: `calculate_position_description`
- Cortex Search service: `protocol_search`
- Automated processing: Stored procedure + task

**Verify it worked:**
```sql
USE SCHEMA SANDBOX.PDF_OCR;
SHOW STAGES LIKE 'PDF_STAGE';
SHOW FUNCTIONS LIKE 'pdf_txt_mapper_v3';
SHOW CORTEX SEARCH SERVICES LIKE 'protocol_search';
```

---

### **Step 2: Upload Sample PDF (2 minutes)**

**Option A - Web UI (easiest):**
1. Navigate to: **Data → Databases → SANDBOX → PDF_OCR → Stages**
2. Click **PDF_STAGE**
3. Click **+ Files** button (top right)
4. Upload `Prot_000.pdf`
5. Verify with **Refresh** button

**Option B - SnowSQL:**
```bash
snowsql -a <your_account> -u <your_user>
USE SCHEMA SANDBOX.PDF_OCR;
PUT file:///path/to/Prot_000.pdf @PDF_STAGE AUTO_COMPRESS=FALSE;
LIST @PDF_STAGE;
```

**Option C - Python:**
```python
from snowflake.snowpark import Session
session = Session.builder.configs(connection_params).create()
session.file.put("Prot_000.pdf", "@SANDBOX.PDF_OCR.PDF_STAGE", auto_compress=False)
```

---

### **Step 3: Process PDF (1 minute)**

Run this SQL to extract and index the PDF:

```sql
USE SCHEMA SANDBOX.PDF_OCR;

-- Process all new PDFs in the stage
CALL process_new_pdfs();

-- Expected output: "Processed 1 new PDF(s)"
```

**Verify extraction worked:**
```sql
-- Check how many chunks were extracted
SELECT 
    doc_name,
    MAX(page) as total_pages,
    COUNT(*) as total_chunks
FROM document_chunks
GROUP BY doc_name;

-- View sample chunks
SELECT 
    page,
    SUBSTR(text, 1, 100) as text_preview
FROM document_chunks
LIMIT 10;
```

---

### **Step 4: Deploy Streamlit App (2 minutes)**

1. In Snowflake UI: **Projects → Streamlit**
2. Click **+ Streamlit App**
3. Configure:
   - **Name**: `Clinical_Protocol_QA`
   - **Location**: `SANDBOX.PDF_OCR`
   - **Warehouse**: `compute_wh`
4. **Delete** the default template code
5. **Copy/paste** entire contents of `streamlit_app.py`
6. Click **Run** (top right)

**The app will open showing:**
- Search interface
- Document browser (showing your uploaded PDF)
- Tabs for browsing, history, and info

---

### **Step 5: Try It Out! (Demo Time 🎉)**

**In the Streamlit App:**

1. **Simple Search:**
   - Enter: `What is the dosing schedule?`
   - Press **Search**
   - View results with precise citations (Page X, position)

2. **Browse Document:**
   - Select your PDF from the sidebar
   - Go to **Browse by Page** tab
   - Enter page number
   - Click **Load Page** to see all content

3. **Export Results:**
   - Run a search
   - Click **Export Results to CSV**
   - Download for offline analysis

4. **Search History:**
   - Go to **Search History** tab
   - See all your previous queries

---

## Validation Checklist

After setup, verify everything works:

- [ ] Database objects created (run `setup.sql`)
- [ ] PDF uploaded to `@PDF_STAGE`
- [ ] PDF processed (chunks in `document_chunks` table)
- [ ] Cortex Search service active
- [ ] Streamlit app deployed and running
- [ ] Search returns results with citations
- [ ] Document browser shows your PDF

---

## Example Queries to Try

Once your app is running, try these queries:

### Clinical Protocol Questions:
```
What is the dosing schedule?
What are the inclusion criteria?
List all adverse events
What is the primary endpoint?
How long is the treatment period?
```

### Document Discovery:
```
How many pages is this protocol?
What documents are available?
```

### Specific Location (in Browse tab):
```
Page: 1
(Shows all content on page 1 with positions)
```

---

## Next Steps

### Add More Documents

1. **Upload more PDFs** to `@PDF_STAGE`
2. **Process them:**
   ```sql
   CALL process_new_pdfs();
   ```
3. **Search across all documents** in the app

### Enable Automated Processing

Set up hourly auto-processing for new PDFs:

```sql
-- Resume the scheduled task (runs every 60 minutes)
ALTER TASK process_pdfs_task RESUME;

-- Verify it's running
SHOW TASKS LIKE 'process_pdfs_task';
-- Check "state" column should show "started"
```

### Customize the App

Edit `streamlit_app.py` to:
- Add your company branding
- Customize search parameters
- Add document type filters
- Integrate with other Snowflake tables
- Add PDF viewer with bounding box highlights

### Grant Access to Users

```sql
-- Create role for app users
CREATE ROLE protocol_qa_users;

-- Grant permissions
GRANT USAGE ON DATABASE SANDBOX TO ROLE protocol_qa_users;
GRANT USAGE ON SCHEMA SANDBOX.PDF_OCR TO ROLE protocol_qa_users;
GRANT SELECT ON TABLE SANDBOX.PDF_OCR.document_chunks TO ROLE protocol_qa_users;
GRANT USAGE ON FUNCTION SANDBOX.PDF_OCR.calculate_position_description(...) TO ROLE protocol_qa_users;

-- Grant to users
GRANT ROLE protocol_qa_users TO USER user1, user2, user3;
```

---

## Troubleshooting

### Issue: "PyPI repository access denied"

**Fix:** Run as ACCOUNTADMIN:
```sql
USE ROLE accountadmin;
GRANT DATABASE ROLE SNOWFLAKE.PYPI_REPOSITORY_USER TO ROLE accountadmin;
```

### Issue: "Cortex Search service not found"

**Cause:** Setup incomplete or wrong schema context

**Fix:**
```sql
USE SCHEMA SANDBOX.PDF_OCR;
SHOW CORTEX SEARCH SERVICES;
-- If not found, re-run the Cortex Search section of setup.sql
```

### Issue: "No documents found" in Streamlit app

**Cause:** PDF not processed yet

**Fix:**
```sql
-- Check if PDFs are in stage
LIST @PDF_STAGE;

-- Process them
CALL process_new_pdfs();

-- Verify chunks were created
SELECT COUNT(*) FROM document_chunks;
```

### Issue: Streamlit app shows error

**Cause:** Wrong schema or missing permissions

**Fix:** Check first few lines of `streamlit_app.py`:
```python
session.sql("USE SCHEMA SANDBOX.PDF_OCR").collect()
```

Ensure the schema matches your setup.

### Issue: Search is slow

**Causes & Fixes:**
- **Large warehouse needed**: Use Medium or Large warehouse
- **Too many results**: Reduce `max_results` parameter
- **Cortex Search lag**: Wait for index refresh or run:
  ```sql
  ALTER CORTEX SEARCH SERVICE protocol_search REFRESH;
  ```

---

## Support

**Common Questions:**

**Q: Can I use a different schema/database name?**  
A: Yes! Edit `setup.sql` to change `SANDBOX.PDF_OCR` to your preferred path. Also update the schema reference in `streamlit_app.py`.

**Q: How do I delete everything and start over?**  
A: Run the cleanup section at the bottom of `setup.sql` (uncomment the DROP statements).

**Q: Can I process PDFs larger than 100 pages?**  
A: Yes, but use a larger warehouse (Medium or Large) for processing.

**Q: How do I update the Cortex Search index?**  
A: It auto-refreshes every hour. For immediate refresh:
```sql
ALTER CORTEX SEARCH SERVICE protocol_search REFRESH;
```

**Q: Can I use this with PDFs in external stages?**  
A: Yes, but modify the UDF to handle external stage URLs.

---

## Architecture Summary

```
Your PDFs
   ↓
@PDF_STAGE (Snowflake internal stage)
   ↓
pdf_txt_mapper_v3() [Python UDF with pdfminer]
   ↓
document_chunks [Table with text + bounding boxes]
   ↓
protocol_search [Cortex Search with auto-embeddings]
   ↓
Streamlit App [User-friendly search interface]
```

**Key Innovation:** Bounding box extraction enables precise citations (page + position), meeting regulatory audit requirements.

---

**Ready to Demo?**  
See `DEMO-GUIDE.md` for presentation talking points and use cases.

**Questions?**  
Check `README.md` for detailed architecture and technical deep dive.

---

🎉 **Congratulations!** You now have a production-ready, Snowflake-native PDF search solution with audit-grade citations.
