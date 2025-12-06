   # PDF OCR with Position Tracking - Snowflake Solution

## Project Overview

This project demonstrates a **complete Snowflake-native solution** for extracting text from PDF documents while maintaining precise location information. Built for regulated industries (e.g., clinical trials, pharmaceuticals) who need **intelligent search with audit-grade citations**.

## Architecture

```
PDFs → @PDF_STAGE → Python UDF → document_chunks → Cortex Search → Streamlit App
           ↓                            ↓                   ↓
    Directory Table          Position Calculator     Semantic Search
         ↓                                                   ↓
  Automated Processing                           User-Friendly UI
```

## Customer Requirements

This solution addresses:

1. ✅ **Document Intelligence - Positioning Capability**: Extract text with exact page coordinates
2. ✅ **Citation & Traceability**: Answer "Where did this information come from?" with section-level precision
3. ✅ **Semantic Search**: Use Cortex Search for intelligent Q&A
4. ✅ **Regulatory Compliance**: GCP audit trails for clinical protocol documents
5. ✅ **User-Friendly Interface**: Streamlit app for non-technical users

## Project Structure

```
pdf-ocr-with-position/
├── README.md                    # This file
├── setup.sql                    # Database setup (run once)
├── streamlit_app.py             # Streamlit in Snowflake app
├── QUICKSTART.md                # Quick setup instructions
├── PDF_SAMPLE_NOTE.md           # Sample PDF usage notes
└── Prot_000.pdf                 # Sample clinical protocol PDF
```

## What's Included

### 📄 `setup.sql` - Database Setup

Creates all Snowflake objects:
- **Stage**: `@PDF_STAGE` for storing PDFs
- **UDF**: `pdf_txt_mapper_v3` - Extracts text with full bounding boxes
- **Table**: `document_chunks` - Stores extracted text with metadata
- **Function**: `calculate_position_description` - Converts coordinates to readable positions
- **Cortex Search**: `protocol_search` - Semantic search service
- **Automation**: Stored procedure + task for auto-processing new PDFs

**Run once to set up environment.**

### 🎨 `streamlit_app.py` - Interactive Web Interface

Features:
- **Semantic Search**: Natural language queries across protocols
- **Precise Citations**: Every result shows document, page, and position (e.g., "top-right")
- **Document Browser**: View available documents with metadata
- **Page Viewer**: Browse specific pages and positions
- **Export**: Download results to CSV
- **Search History**: Track previous queries

**Deploy as Streamlit in Snowflake app.**

---

## Key Features

### ✅ Advanced PDF Processing

**Bounding Box Extraction:**
```python
{
  'page': 5,
  'bbox': [320, 680, 550, 720],  # [x0, y0, x1, y1]
  'page_width': 612,
  'page_height': 792,
  'txt': 'Dosing is BID for 28 days...'
}
```

- Full bounding box coordinates (x0, y0, x1, y1)
- Page dimensions for relative positioning
- Human-readable positions ("top-right", "middle-center")

### ✅ Cortex Search Integration

```sql
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'protocol_search',
    '{"query": "dosing schedule", "columns": [...], "limit": 10}'
)
```

- Automatic embeddings (no manual vector management)
- Hybrid search (semantic + keyword)
- Filter by document, page, or other attributes

### ✅ Streamlit in Snowflake App

Direct search implementation:
- **Faster**: No agent overhead, direct Cortex Search calls
- **Simpler**: Python code you control
- **Richer UI**: PDF viewer, filters, exports, visualizations
- **Lower cost**: No extra LLM calls for orchestration

### ✅ Production Automation

```sql
CALL process_new_pdfs();  -- Manual trigger
-- Or enable scheduled task:
ALTER TASK process_pdfs_task RESUME;  -- Runs every hour
```

- Auto-detects new PDFs in stage
- Processes and indexes automatically
- Immediate searchability

---

## Getting Started

### Prerequisites

- Snowflake account with ACCOUNTADMIN access
- Access to PyPI repository packages (for pdfminer)
- A warehouse (e.g., `compute_wh`)

### Quick Start (10 Minutes)

#### **Step 1: Run Database Setup**

```bash
# In Snowflake UI or SnowSQL:
-- Copy contents of setup.sql and execute
```

This creates:
- Schema: `SANDBOX.PDF_OCR`
- All database objects
- Cortex Search service

#### **Step 2: Upload Sample PDF**

Option A - Web UI:
1. Navigate to: Data → Databases → SANDBOX → PDF_OCR → Stages → PDF_STAGE
2. Click "+ Files" and upload `Prot_000.pdf`

Option B - SQL:
```sql
PUT file:///path/to/Prot_000.pdf @SANDBOX.PDF_OCR.PDF_STAGE AUTO_COMPRESS=FALSE;
```

#### **Step 3: Process PDF**

```sql
CALL SANDBOX.PDF_OCR.process_new_pdfs();
-- Output: "Processed 1 new PDF(s)"
```

#### **Step 4: Deploy Streamlit App**

1. In Snowflake UI: **Projects → Streamlit**
2. Click **+ Streamlit App**
3. Name: `Clinical_Protocol_QA`
4. Warehouse: `compute_wh`
5. Copy/paste contents of `streamlit_app.py`
6. Click **Run**

#### **Step 5: Try It Out!**

In the Streamlit app:
- Enter query: "What is the dosing schedule?"
- View results with precise citations
- Browse documents and pages
- Export results

---

## Solution Advantages

### vs. Agent-Based Architecture

| Aspect | **Cortex Agent** | **Streamlit App** ✅ |
|--------|------------------|----------------------|
| Complexity | High (YAML, tools, orchestration) | Low (direct Python) |
| Speed | Slower (multiple LLM calls) | **Faster** (direct API) |
| Cost | Higher (agent + search LLM calls) | **Lower** (search only) |
| UI/UX | Text-only chat | **Rich UI** (PDF viewer, exports) |
| Debugging | Difficult (black box) | **Easy** (your code) |
| Customization | Limited by agent capabilities | **Full control** |

### vs. External RAG Tools

✅ **Zero data movement** - PDFs stay in Snowflake stages  
✅ **Native governance** - Snowflake RBAC, audit logs  
✅ **No infrastructure** - Deploy with SQL commands  
✅ **Precise citations** - "Page 5, top-right, [320, 680, 550, 720]"  

### vs. Snowflake PARSE_DOCUMENT

✅ **Bounding box coordinates** - PARSE_DOCUMENT doesn't capture precise positions  
✅ **Exact citations** - Enable regulatory-grade traceability  
✅ **Visual verification** - Coordinates can highlight source text  

### For Regulated Industries

✅ **Audit-grade citations** - Page, position, exact coordinates  
✅ **GCP compliance** - All data stays in governed environment  
✅ **Deterministic extraction** - Open-source pdfminer (no black box)  
✅ **Version-controlled** - UDF code in git repo  

---

## Technical Deep Dive

### PDF Processing UDF

**Technology:**
- Python 3.12 runtime
- `pdfminer` library for robust PDF parsing
- `SnowflakeFile` for direct stage access

**What it does:**
1. Opens PDF from Snowflake stage
2. Iterates through pages
3. Extracts text boxes with bounding boxes
4. Returns JSON with page, bbox, dimensions, text

### Position Calculator

Converts raw coordinates to human-readable positions:

```sql
calculate_position_description(320, 680, 550, 720, 612, 792)
-- Returns: {"position_description": "top-right", "relative_x": 71.4, "relative_y": 88.8, ...}
```

### Cortex Search Service

- **Embedding Model**: `snowflake-arctic-embed-l-v2.0`
- **Search Columns**: `text` (auto-embedded)
- **Attributes**: `page`, `doc_name`, `bbox_x0`, `bbox_y0`, `bbox_x1`, `bbox_y1`, etc.
- **Target Lag**: 1 hour (auto-refresh)

### Streamlit App Architecture

```python
# Direct Cortex Search call (no agent middleware)
results = session.sql(f"""
    SELECT * FROM TABLE(
        SNOWFLAKE.CORTEX.SEARCH_PREVIEW('protocol_search', '{query_json}')
    )
""").collect()

# Format citations in Python
for result in results:
    position = calculate_position_python(bbox_coords...)
    display(f"Page {page} ({position}): {text}")
```

**Why this is better:**
- No agent overhead
- Full control over formatting
- Can add custom UI elements (filters, charts, PDF viewer)
- Easier to debug and customize

---

## Usage Examples

### Search Query Example

**User enters:** "What are the inclusion criteria?"

**App flow:**
1. Calls Cortex Search with query
2. Gets top 5 results with bounding boxes
3. Calculates position for each result
4. Displays:

```
📌 Result 1: Prot_000.pdf
Page 12 (middle-left)

> Inclusion Criteria:
> 1. Age 18-65 years
> 2. Confirmed diagnosis of condition X
> ...
```

### Document Browser

```
📚 Document Browser
✅ 3 document(s) available

Prot_000.pdf
  Pages: 42
  Chunks: 1,247
  Processed: 2024-01-15

Prot_001.pdf
  Pages: 38
  Chunks: 1,089
  Processed: 2024-01-16
```

### Export Results

Download CSV with:
- Query text
- Document name
- Page number
- Position description
- Full text
- Chunk ID for traceability

---

## Next Steps

### For Demos

1. ✅ Run `setup.sql`
2. ✅ Upload sample PDF
3. ✅ Process PDF
4. ✅ Deploy Streamlit app
5. ✅ Show live search

**Demo talking points:** See `DEMO-GUIDE.md`

### For Production

1. **Upload your protocol library** to `@PDF_STAGE`
2. **Enable automated processing**: `ALTER TASK process_pdfs_task RESUME;`
3. **Grant access** to business users
4. **Customize UI** with your branding
5. **Add features**: PDF viewer with highlights, multi-doc comparison

### Customization Ideas

- Add document type filters (protocols, amendments, reports)
- Integrate with approval workflows
- Add visual PDF viewer with bounding box highlights
- Multi-document comparison side-by-side
- Export to regulatory submission formats
- Integrate with electronic trial master file (eTMF) systems

---

## Troubleshooting

### "No documents found"

**Cause:** PDFs not processed yet  
**Fix:** Run `CALL process_new_pdfs();`

### "Search error: Cortex Search service not found"

**Cause:** Setup incomplete  
**Fix:** Run all sections of `setup.sql`

### "PyPI repository access denied"

**Cause:** Missing permissions  
**Fix:** Run as ACCOUNTADMIN: `GRANT DATABASE ROLE SNOWFLAKE.PYPI_REPOSITORY_USER TO ROLE accountadmin;`

### Slow search performance

**Cause:** Large result set or warehouse size  
**Fix:** Adjust `max_results` or use larger warehouse

---

## Questions?

This is a production-ready solution built on Snowflake best practices. The core innovation is the **combination of bounding box extraction + Cortex Search**, enabling precise citations that meet regulatory requirements.

**Key advantage:** 100% Snowflake-native, no external services or data movement.

---

**Built for Snowflake Customers**  
**Use Case:** Clinical Trials & Pharmaceutical Document Intelligence  
**Architecture:** Streamlit in Snowflake + Cortex Search  
**Last Updated:** December 2024
