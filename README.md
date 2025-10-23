# PDF OCR with Position Tracking - Snowflake Solution

## Project Overview

This project demonstrates an **incremental solution** for extracting text from PDF documents while maintaining precise location information and enabling LLM-based Q&A with citations. Built for Snowflake customers in regulated industries (e.g., clinical trials, pharmaceuticals) who need GCP-compliant audit trails.

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
├── pdf-ocr-with-position.ipynb  # Phase 0: FCTO's baseline solution
├── Prot_000.pdf                 # Sample clinical protocol PDF
└── (future phases...)
```

## Incremental Development Phases

### ✅ Phase 0: Setup & Baseline (COMPLETE)
**Notebook:** `pdf-ocr-with-position.ipynb`

**What it does:**
- Sets up Snowflake environment
- Creates PDF stage
- Deploys baseline UDF that extracts text with (x,y) coordinates
- Tests with sample protocol PDF

**Output:**
```python
[{'pos': (54.0, 720.3), 'txt': 'CLINICAL PROTOCOL\n'}, ...]
```

**Limitations:**
- ❌ No page numbers
- ❌ No section detection
- ❌ Returns string, not queryable data
- ❌ No LLM integration

---

### 🔄 Phase 1: Add Page Numbers & Structured Storage (NEXT)
**Planned Enhancements:**
1. Track page numbers in the UDF
2. Create a table to store results
3. Add chunk IDs for traceability
4. Enable SQL queries on extracted text

**Target Output:**
```sql
SELECT * FROM document_chunks 
WHERE page = 5 
AND txt ILIKE '%medication%';
```

---

### 📋 Phase 2: Richer Positioning Data
- Full bounding box (x0, y0, x1, y1)
- Page dimensions for context
- Enable "highlight this text" functionality

---

### 🎨 Phase 3: Font Information
- Extract font name and size
- Detect headers vs. body text
- Foundation for section detection

---

### 🗂️ Phase 4: Section Detection
- Pattern matching for section headers
- Build section hierarchy
- Tag each chunk with section path

---

### 🧩 Phase 5: Better Chunking
- Combine text boxes into semantic chunks
- Section-based or fixed-token-size
- Optimal for LLM retrieval

---

### 🤖 Phase 6: LLM Integration
- Cortex embeddings on chunks
- Vector search or Cortex Search
- Q&A with citations

---

## Getting Started

### Prerequisites
- Snowflake account with ACCOUNTADMIN access
- Access to PyPI repository packages
- A warehouse for running queries

### Quick Start

1. **Open the Phase 0 Notebook:**
   ```bash
   # Import phase_0_baseline.ipynb into Snowflake Notebooks
   ```

2. **Upload the sample PDF:**
   - Use SnowSQL, Web UI, or Snowpark to upload `Prot_000.pdf` to the stage

3. **Run the notebook cells in order:**
   - Setup environment
   - Create UDF
   - Test with PDF

4. **Verify output:**
   - Check that text is extracted with positions

### Using Your Own PDFs

Replace `Prot_000.pdf` with any clinical protocol or multi-page document:
```sql
SELECT pdf_txt_mapper(build_scoped_file_url(@pdf, 'your_document.pdf'));
```

## Key Technologies

- **Snowflake UDFs**: Python 3.12 for serverless processing
- **pdfminer**: Robust PDF parsing with layout analysis
- **SnowflakeFile**: Direct stage access without external storage
- **Cortex AI** (future): LLM integration and embeddings

## Solution Advantages

### vs. AISQL/ParseDoc (Current Gap)
✅ Maintains position/location data  
✅ Enables precise citations  
✅ Snowflake-native (no external dependencies)  
✅ Queryable results  
✅ Extensible for LLM integration  

### For Regulated Industries
✅ Complete audit trail  
✅ GCP compliance ready  
✅ Deterministic extraction (no black box APIs)  
✅ Version-controlled processing logic  

## Next Steps

After completing Phase 0:
1. Review the extracted data structure
2. Identify any PDF parsing issues
3. Move to Phase 1 to add page numbers and storage

## Questions?

This is a proof-of-concept built incrementally. Each phase can be tested independently before moving forward.

---

**Built for Snowflake by:** Solution Engineering Team  
**Use Case:** Clinical Trials & Pharmaceutical Document Intelligence  
**Last Updated:** October 2025

