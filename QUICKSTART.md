# Quick Start Guide

## What You Have

✅ **Snowflake Notebook:** `pdf-ocr-with-position.ipynb` - Ready to import  
✅ **Sample PDF:** `Prot_000.pdf` - Clinical protocol document  
✅ **README:** Complete project documentation  

## Next Steps (3 Simple Actions)

### 1️⃣ Import the Notebook into Snowflake

**Option A: Snowflake Web UI**
1. Log into your Snowflake account
2. Navigate to **Projects** → **Notebooks**
3. Click **"+ Notebook"** → **"Import .ipynb file"**
4. Upload `pdf-ocr-with-position.ipynb`

**Option B: Snowsight**
1. Go to **Worksheets** → **Projects** → **Notebooks**
2. Import the notebook file

### 2️⃣ Upload the PDF to Snowflake

**After running the setup cells in the notebook**, use one of these methods:

**SnowSQL (Command Line):**
```bash
snowsql -a <your_account> -u <your_username>
USE DATABASE SANDBOX;
USE SCHEMA PDF_OCR;
PUT file:///path/to/Prot_000.pdf @PDF_STAGE AUTO_COMPRESS=FALSE;
```

**Snowflake Web UI:**
1. Navigate to **Data** → **Databases** → **SANDBOX** → **PDF_OCR** → **Stages** → **PDF_STAGE**
2. Click **"+ Files"**
3. Upload `Prot_000.pdf`

**Python (if you're in Snowpark):**
```python
session.file.put(
    "Prot_000.pdf", 
    "@PDF_STAGE", 
    auto_compress=False
)
```

### 3️⃣ Run the Notebook

Execute each cell in order:

**Part 1: Setup**
- Cell 2: Environment setup (database, schema, stage)

**Part 2: PDF Extraction**
- Cell 4: Create the extraction UDF
- Cell 6: Test extraction (see output with coordinates!)

**Part 3: Storage**
- Cell 8: Create table and load data
- Cell 10: Query the structured data

**Part 4: AI Layer**
- Cell 12: Position calculator function
- Cell 13: Cortex Search service
- Cell 14: Agent tools
- Cell 16: Create the Cortex Agent
- Cells 18-22: Test the agent!

**Part 5: Automation (Optional)**
- Cell 24: Enable auto-processing

## Expected Results

### After Test Extraction (Cell 6):
You should see output like:
```
| PAGE | TEXT_PREVIEW                                    | BBOX              |
|------|------------------------------------------------|-------------------|
| 1    | CLINICAL PROTOCOL                               | [54, 720, 200, 735] |
| 1    | Study Title: Phase III Study...                | [72, 680, 500, 695] |
| 1    | Protocol Number: ABC-123                       | [54, 650, 250, 665] |
```

### After Agent Test (Cells 18-21):
The agent will respond with precise citations:
```
According to Prot_000.pdf, Page 5 (top-right, [320, 680, 550, 720]), 
the dosing schedule is BID for 28 days...
```

## Troubleshooting

### "Permission Denied" Error
```sql
-- Make sure you're ACCOUNTADMIN when running:
USE ROLE accountadmin;
```

### "File Not Found" Error
```sql
-- Verify your file is uploaded:
LIST @PDF_STAGE;
-- Should show: Prot_000.pdf
```

### Function Takes Too Long
- Normal for first run (30-60 seconds for large PDFs)
- Increase warehouse size if needed:
  ```sql
  ALTER WAREHOUSE COMPUTE_WH SET WAREHOUSE_SIZE = 'MEDIUM';
  ```

## What You'll Learn

By running this notebook, you'll understand:
- ✅ How Snowflake UDFs process PDFs with position data
- ✅ How `pdfminer` extracts text with coordinates
- ✅ How Cortex Search enables semantic search
- ✅ How Cortex Agent orchestrates tools for Q&A
- ✅ How to get PRECISE citations (page + position + coordinates)

---

## Need Help?

**Common Questions:**

**Q: Can I use my own PDF?**  
A: Yes! Upload any PDF to the `@PDF_STAGE` and change `'Prot_000.pdf'` in the queries.

**Q: Why is the output so long?**  
A: The UDF extracts EVERY text box with coordinates. A 100-page PDF might have 5,000+ text boxes.

**Q: Is this production-ready?**  
A: Yes! The solution includes auto-processing for new PDFs and can be accessed via Snowflake Intelligence UI.

**Q: How does this compare to other solutions?**  
A: Unlike generic RAG tools, this maintains **position data** and enables **precise citations** - critical for GCP compliance in regulated industries.

---

**Ready?** Open `pdf-ocr-with-position.ipynb` in Snowflake and let's go! 🚀
