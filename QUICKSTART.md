# Quick Start Guide - Phase 0

## What You Have

✅ **Snowflake Notebook:** `phase_0_baseline.ipynb` - Ready to import  
✅ **Sample PDF:** `Prot_000.pdf` - Clinical protocol document  
✅ **README:** Complete project documentation  

## Next Steps (3 Simple Actions)

### 1️⃣ Import the Notebook into Snowflake

**Option A: Snowflake Web UI**
1. Log into your Snowflake account
2. Navigate to **Projects** → **Notebooks**
3. Click **"+ Notebook"** → **"Import .ipynb file"**
4. Upload `phase_0_baseline.ipynb`

**Option B: Snowsight**
1. Go to **Worksheets** → **Projects** → **Notebooks**
2. Import the notebook file

### 2️⃣ Upload the PDF to Snowflake

**After running the setup cells in the notebook**, use one of these methods:

**SnowSQL (Command Line):**
```bash
snowsql -a <your_account> -u <your_username>
USE DATABASE pdf_ocr_demo;
USE SCHEMA public;
PUT file:///Users/akelkar/src/Cursor/pdf-ocr-with-position/Prot_000.pdf @pdf AUTO_COMPRESS=FALSE;
```

**Snowflake Web UI:**
1. Navigate to **Data** → **Databases** → **PDF_OCR_DEMO** → **PUBLIC** → **Stages** → **PDF**
2. Click **"+ Files"**
3. Upload `Prot_000.pdf`

**Python (if you're in Snowpark):**
```python
session.file.put(
    "Prot_000.pdf", 
    "@pdf", 
    auto_compress=False
)
```

### 3️⃣ Run the Notebook

Execute each cell in order:
1. ✅ Cell 1-4: Setup roles and permissions
2. ✅ Cell 5-7: Create database/schema
3. ✅ Cell 8-10: Create PDF stage
4. ✅ Cell 11-13: Create the UDF (this takes ~30 seconds)
5. ✅ Cell 14-15: Verify PDF upload
6. ✅ Cell 16-17: **Test extraction** (this is the magic! 🎉)
7. ✅ Cell 18-19: Analyze output

## Expected Results

### After Cell 17 (Test Extraction):
You should see output like:
```python
[
  {'pos': (54.0, 720.3), 'txt': 'CLINICAL PROTOCOL\n'}, 
  {'pos': (72.0, 680.1), 'txt': 'Study Title: Phase III Study...\n'},
  {'pos': (54.0, 650.2), 'txt': 'Protocol Number: ABC-123\n'},
  ...
]
```

### After Cell 19 (Statistics):
```
output_length_chars: ~500000
output_length_kb: ~488
```

## Troubleshooting

### "Permission Denied" Error
```sql
-- Make sure you're ACCOUNTADMIN when running:
USE ROLE accountadmin;
GRANT DATABASE ROLE SNOWFLAKE.PYPI_REPOSITORY_USER TO ROLE sysadmin;
```

### "File Not Found" Error
```sql
-- Verify your file is uploaded:
LIST @pdf;
-- Should show: Prot_000.pdf
```

### Function Takes Forever
- Normal for first run (30-60 seconds for large PDFs)
- Increase warehouse size if needed:
  ```sql
  USE WAREHOUSE COMPUTE_WH;  -- or your warehouse
  ALTER WAREHOUSE COMPUTE_WH SET WAREHOUSE_SIZE = 'MEDIUM';
  ```

## What You'll Learn

By the end of Phase 0, you'll understand:
- ✅ How Snowflake UDFs process PDFs
- ✅ How `pdfminer` extracts text with coordinates
- ✅ The baseline data structure
- ✅ Current limitations (no page numbers, sections, etc.)

## After Phase 0

Once you've successfully extracted text from `Prot_000.pdf`, you're ready for:

**Phase 1:** Add page numbers and store in a table  
**Phase 2:** Capture full bounding boxes  
**Phase 3:** Detect fonts and headers  
**Phase 4:** Build section hierarchy  
**Phase 5:** Implement smart chunking  
**Phase 6:** Add LLM Q&A with citations  

---

## Need Help?

**Common Questions:**

**Q: Can I use my own PDF?**  
A: Yes! Upload any PDF to the `@pdf` stage and change `'Prot_000.pdf'` in the query.

**Q: Why is the output so long?**  
A: The UDF extracts EVERY text box with coordinates. A 100-page PDF might have 5,000+ text boxes.

**Q: Is this production-ready?**  
A: Phase 0 is a baseline. Future phases add the structure needed for production (tables, sections, LLM integration).

**Q: How does this compare to other solutions?**  
A: Unlike AISQL/ParseDoc, this maintains **position data** and enables **precise citations** - critical for GCP compliance.

---

**Ready?** Open `phase_0_baseline.ipynb` in Snowflake and let's go! 🚀

