# PDF OCR with Position Tracking - Snowflake Solution

## Project Overview

This project demonstrates a **complete Snowflake-native solution** for extracting text from PDF documents while maintaining precise location information and enabling AI-powered Q&A with exact citations. Built for Snowflake customers in regulated industries (e.g., clinical trials, pharmaceuticals) who need audit-grade traceability.

## Customer Requirements

This solution addresses:

1. ✅ **Document Intelligence - Positioning Capability**: Extract text with exact page coordinates
2. ✅ **Citation & Traceability**: Answer "Where did this information come from?" with section-level precision
3. ✅ **LLM Integration**: Use Cortex/Claude to answer questions with citations back to source
4. ✅ **Regulatory Compliance**: GCP audit trails for clinical protocol documents
5. ✅ **Unstructured Data Processing**: Handle protocol PDFs in Snowflake data pipelines

## Project Structure

```
pdf-ocr-with-position/
├── README.md                    # This file
├── pdf-ocr-with-position.ipynb  # Complete solution notebook (27 cells, 30-min demo)
├── DEMO-GUIDE.md                # Presentation guide with minute-by-minute script
├── QUICKSTART.md                # Quick setup instructions
├── ROADMAP.md                   # Phase-by-phase development details
└── Prot_000.pdf                 # Sample clinical protocol PDF
```

## What's Included (Complete Solution)

### ✅ PDF Extraction with Position Tracking
- Custom Python UDF using pdfminer for robust PDF parsing
- Extracts text with full bounding boxes [x0, y0, x1, y1]
- Captures page numbers and page dimensions
- Enables precise location citations

**Output:**
```python
{
  'page': 5,
  'bbox': [320, 680, 550, 720],
  'page_width': 612,
  'page_height': 792,
  'txt': 'Dosing is BID for 28 days...'
}
```

### ✅ Structured Storage
- Queryable table (`document_chunks`)
- Change tracking enabled for Cortex Search
- Unique chunk IDs for traceability

```sql
SELECT * FROM document_chunks 
WHERE page = 5 AND text ILIKE '%dosing%';
```

### ✅ Semantic Search (Cortex Search)
- Auto-embedding generation (no manual vector management)
- Hybrid search (semantic + keyword)
- Filters by page, document name

### ✅ AI Agent (Cortex Agent + Claude 4 Sonnet)
- Natural language Q&A interface
- Orchestrates 3 tools automatically:
  1. Cortex Search (content questions)
  2. Document metadata (page counts, timestamps)
  3. Location-specific search (find text at page positions)
- **Returns precise citations:** "Page 5 (top-right, coordinates [320, 680, 550, 720])"

### ✅ Production Automation
- Auto-processes new PDFs dropped in stage
- Snowflake Tasks + Directory Tables
- Immediate searchability

### ✅ Snowflake Intelligence Access
- Beautiful chat UI for non-technical users
- Zero code required
- Native RBAC and governance

---

## Getting Started

### Prerequisites
- Snowflake account with ACCOUNTADMIN access
- Access to PyPI repository packages (for pdfminer)
- A warehouse (e.g., `COMPUTE_WH`)

### Quick Start (5 Minutes)

1. **Import the Notebook:**
   - Upload `pdf-ocr-with-position.ipynb` to Snowflake Notebooks

2. **Upload the Sample PDF:**
   - Use Web UI: `Data` → `Stages` → `PDF_STAGE` → Upload `Prot_000.pdf`

3. **Run the Setup Cells (pre-run before demo):**
   - Cell 2: Environment setup
   - Cell 4: Create PDF extraction UDF
   - Cell 8: Create table and load data
   - Cells 12-16: Create AI components (Cortex Search, Agent)

4. **Try the Agent (live demo):**
   - Cell 18: Ask "What is the dosing schedule?"
   - Watch it return precise citations!

**For full demo instructions:** See `DEMO-GUIDE.md`

### Using Your Own PDFs

1. Upload PDFs to `@PDF_STAGE`
2. The auto-processing task will detect and process them
3. Ask questions via the agent or Snowflake Intelligence UI

## Key Technologies

- **Snowflake UDFs**: Python 3.12 for serverless processing
- **pdfminer**: Robust PDF parsing with layout analysis
- **SnowflakeFile**: Direct stage access without external storage
- **Cortex AI** (future): LLM integration and embeddings

## Solution Advantages

### vs. External RAG Tools
✅ **Zero data movement** - PDFs stay in Snowflake stages  
✅ **Native governance** - Snowflake RBAC, audit logs  
✅ **No infrastructure** - Deploy with SQL commands  
✅ **Precise citations** - Not just "Page 5", but "Page 5, top-right, [320, 680, 550, 720]"  
✅ **Auto-managed** - Cortex handles embeddings, models, scaling  

### vs. Snowflake PARSE_DOCUMENT
✅ **Bounding box coordinates** - PARSE_DOCUMENT doesn't capture precise positions  
✅ **Exact citations** - Enable regulatory-grade traceability  
✅ **Visual verification** - Coordinates can be used to highlight source text  

### For Regulated Industries
✅ **Audit-grade citations** - Page, position, exact coordinates  
✅ **GCP compliance** - All data stays in governed Snowflake environment  
✅ **Deterministic extraction** - Open-source pdfminer (no black box)  
✅ **Version-controlled** - UDF code is part of your git repo  

## Next Steps

1. **Demo it:** Follow `DEMO-GUIDE.md` for 30-minute presentation
2. **Customize it:** Add your own agent tools or document types
3. **Scale it:** Enable auto-processing for your entire protocol library
4. **Deploy it:** Grant access via Snowflake Intelligence for end users

## Questions?

This is a proof-of-concept built incrementally. Each phase can be tested independently before moving forward.

---

**Built for Snowflake by:** Solution Engineering Team  
**Use Case:** Clinical Trials & Pharmaceutical Document Intelligence  
**Last Updated:** October 2025

