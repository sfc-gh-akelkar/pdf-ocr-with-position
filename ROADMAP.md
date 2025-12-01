# PDF OCR with Citations - Development Roadmap

## Vision: From Text Extraction → LLM Q&A with Audit-Grade Citations

```
Phase 0 (Baseline)           Phase 3 (Fonts)              Phase 6 (LLM + Citations)
     |                            |                              |
     v                            v                              v
[Raw Text + XY]  →  [+ Pages]  →  [+ Sections]  →  [+ Chunks]  →  [Q&A with Citations]
     |                |                |                |              |
   Phase 0          Phase 1          Phase 4          Phase 5       Phase 6
                      |                                                |
                   Phase 2                                        "Where did
               (Full BBox)                                     this info come from?"
                                                                     ✅ SOLVED
```

---

## Phase 0: Baseline ✅ COMPLETE

### Deliverable
- Snowflake notebook with PDF extraction UDF
- PDF stage and UDF deployed
- Extraction works end-to-end

### Output Format
```python
[
  {'pos': (54.0, 720.3), 'txt': 'CLINICAL PROTOCOL\n'},
  {'pos': (72.0, 680.1), 'txt': 'Study Title: ...\n'}
]
```

### Capabilities
- ✅ Text extraction
- ✅ X,Y coordinates
- ✅ Snowflake-native

### Limitations
- ❌ No page numbers
- ❌ String output (not queryable)
- ❌ No sections
- ❌ Can't answer "where did this come from?"

### Time Investment: 30 minutes

---

## Phase 1: Add Page Numbers & Structured Storage

### Goal
Make the extracted data **queryable** and add **page number tracking**.

### Changes to UDF
```python
# Add page tracking
for page_num, page in enumerate(pages, start=1):
    # ... process page ...
    finding += [{
        'page': page_num,      # NEW!
        'pos': (x, y),
        'txt': text
    }]
```

### New Database Objects
```sql
CREATE TABLE document_chunks (
    chunk_id VARCHAR,
    doc_name VARCHAR,
    page NUMBER,
    x NUMBER,
    y NUMBER,
    text VARCHAR,
    extracted_at TIMESTAMP
);
```

### New Capabilities
- ✅ Query by page number
- ✅ Store results in table
- ✅ Track when extraction happened
- ✅ Compare multiple documents

### Example Query
```sql
-- Find all mentions of "medication" on pages 5-10
SELECT page, text 
FROM document_chunks 
WHERE doc_name = 'Prot_000.pdf'
  AND page BETWEEN 5 AND 10
  AND text ILIKE '%medication%';
```

### Time Investment: 45 minutes

---

## Phase 2: Richer Positioning Data

### Goal
Capture **full bounding boxes** to enable "highlight this text" functionality.

### Changes to UDF
```python
# Capture full bbox instead of just top-left corner
finding += [{
    'page': page_num,
    'bbox': [x0, y0, x1, y1],  # Full rectangle
    'page_width': page.width,
    'page_height': page.height,
    'txt': text
}]
```

### New Capabilities
- ✅ Draw rectangles around extracted text
- ✅ Calculate relative positions (% from top/left)
- ✅ Detect multi-column layouts
- ✅ Measure text height/width

### Use Case
When an LLM answers a question, you can:
1. Return the citation text
2. Return the page number
3. Return the **bounding box coordinates**
4. Frontend can **highlight the exact text** in the PDF viewer

### Time Investment: 30 minutes

---

## Phase 3: Font Information

### Goal
Extract **font name and size** to distinguish headers from body text.

### Changes to UDF
```python
# Extract font from first character in text box
for char in lobj:
    if isinstance(char, LTChar):
        font_name = char.fontname
        font_size = char.size
        break

finding += [{
    'page': page_num,
    'bbox': [...],
    'txt': text,
    'font_name': font_name,   # NEW!
    'font_size': font_size,   # NEW!
}]
```

### New Capabilities
- ✅ Identify headers (larger font, bold)
- ✅ Distinguish body text from titles
- ✅ Detect emphasis (italic, bold)
- ✅ Foundation for section detection

### Example Analysis
```sql
-- Find all text boxes with large fonts (likely headers)
SELECT page, font_size, text
FROM document_chunks
WHERE font_size > 14
ORDER BY page, font_size DESC;
```

### Time Investment: 45 minutes

---

## Phase 4: Section Detection

### Goal
Build a **hierarchical section structure** from the document.

### Algorithm
```python
def detect_section(text, font_size, font_name):
    # Pattern: "1.0 Introduction"
    if re.match(r'^\d+\.\d+\s+[A-Z]', text):
        return 'header', extract_section_number(text)
    
    # Pattern: "STUDY DESIGN" (all caps)
    if text.isupper() and font_size > median_font_size:
        return 'header', None
    
    # Clinical protocol keywords
    if text.strip() in PROTOCOL_SECTIONS:
        return 'header', None
    
    return 'body', current_section
```

### New Data Structure
```python
{
    'chunk_id': 'doc1_p5_c42',
    'page': 5,
    'bbox': [...],
    'txt': 'Dosing schedule is ...',
    'section': '5.2.3 Dosing Schedule',        # NEW!
    'section_level': 3,                        # NEW!
    'section_hierarchy': ['5.0', '5.2', '5.2.3'],  # NEW!
    'is_header': False
}
```

### New Capabilities
- ✅ Answer "What sections exist in this protocol?"
- ✅ Query by section: "Show me all text from section 5.2"
- ✅ Navigate document hierarchy
- ✅ Precise citations: "Found in section 5.2.3, page 42"

### Example Query
```sql
-- Get table of contents
SELECT DISTINCT section, MIN(page) as first_page
FROM document_chunks
WHERE is_header = TRUE
ORDER BY first_page;

-- Find medication info
SELECT section, page, text
FROM document_chunks
WHERE section ILIKE '%medication%'
   OR section ILIKE '%dosing%';
```

### Time Investment: 2 hours

---

## Phase 5: Better Chunking

### Goal
Combine small text boxes into **semantic chunks** optimized for LLM retrieval.

### Strategies

#### A. Section-Based Chunking
```python
# Combine all text boxes in a section
chunks = group_by_section(text_boxes)
```
**Pro:** Semantically coherent  
**Con:** Sections might be too large (>4000 tokens)

#### B. Fixed-Size with Overlap
```python
# Split into 512-1024 token chunks with 100-token overlap
chunks = sliding_window(text_boxes, size=1024, overlap=100)
```
**Pro:** LLM-friendly size  
**Con:** Might split mid-thought

#### C. Hybrid Approach (RECOMMENDED)
```python
# Start with sections, then split large ones
for section in sections:
    if len(section) > MAX_TOKENS:
        chunks += split_section_by_paragraph(section, overlap=50)
    else:
        chunks += [section]
```

### New Data Structure
```python
{
    'chunk_id': 'doc1_p5_s3_c2',
    'doc_name': 'Prot_000.pdf',
    'page': 5,
    'bbox': [(x1,y1,x2,y2), ...],  # Multiple bboxes
    'section': '5.2.3 Dosing Schedule',
    'text': 'Full paragraph text here...',
    'char_count': 850,
    'token_estimate': 213,
    'chunk_position': 'middle',  # first/middle/last in section
    'prev_chunk_id': 'doc1_p5_s3_c1',
    'next_chunk_id': 'doc1_p5_s3_c3'
}
```

### New Capabilities
- ✅ Chunks are LLM-ready (optimal size)
- ✅ Maintain context across chunk boundaries
- ✅ Link related chunks (prev/next)
- ✅ Balance semantic coherence with size

### Time Investment: 2 hours

---

## Phase 6: LLM Integration with Citations 🎯

### Goal
Answer questions using LLMs while providing **audit-grade citations** back to source.

### Architecture

```
User Question
    ↓
[Vector Search / Cortex Search]
    ↓
Retrieve Top-K Relevant Chunks (with metadata)
    ↓
[LLM (Cortex Complete / Claude)]
    ↓
Generate Answer + Return Chunk IDs
    ↓
Look Up Chunk Metadata (page, bbox, section)
    ↓
Present: Answer + Citations
```

### Implementation Steps

#### A. Add Embeddings
```sql
-- Add embedding column
ALTER TABLE document_chunks 
ADD COLUMN embedding VECTOR(FLOAT, 768);

-- Generate embeddings using Cortex
UPDATE document_chunks
SET embedding = SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', text);
```

#### B. Vector Search Function
```sql
CREATE OR REPLACE FUNCTION search_documents(
    query VARCHAR,
    top_k NUMBER DEFAULT 5
)
RETURNS TABLE(chunk_id VARCHAR, text VARCHAR, page NUMBER, section VARCHAR, similarity FLOAT)
AS
$$
SELECT 
    chunk_id,
    text,
    page,
    section,
    VECTOR_COSINE_SIMILARITY(
        embedding,
        SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', query)
    ) as similarity
FROM document_chunks
ORDER BY similarity DESC
LIMIT top_k
$$;
```

#### C. Q&A Function with Citations
```sql
CREATE OR REPLACE FUNCTION ask_protocol(question VARCHAR)
RETURNS VARIANT
AS
$$
DECLARE
    context VARCHAR;
    chunks VARIANT;
    answer VARCHAR;
BEGIN
    -- 1. Retrieve relevant chunks
    chunks := (SELECT ARRAY_AGG(OBJECT_CONSTRUCT(
        'chunk_id', chunk_id,
        'text', text,
        'page', page,
        'section', section
    ))
    FROM TABLE(search_documents(:question, 5)));
    
    -- 2. Build context for LLM
    context := (SELECT LISTAGG(text, '\n\n') 
                FROM TABLE(search_documents(:question, 5)));
    
    -- 3. Call LLM
    answer := SNOWFLAKE.CORTEX.COMPLETE(
        'claude-3-5-sonnet',
        CONCAT(
            'Answer this question based on the context below.\n\n',
            'Context:\n', context, '\n\n',
            'Question: ', :question, '\n\n',
            'Answer:'
        )
    );
    
    -- 4. Return answer + citations
    RETURN OBJECT_CONSTRUCT(
        'answer', answer,
        'citations', chunks
    );
END;
$$;
```

### Usage Example
```sql
SELECT ask_protocol('What is the dosing schedule for this medication?');
```

### Output
```json
{
  "answer": "The medication is administered as follows: 200mg daily for the first week, then 400mg daily thereafter. Dosing should occur in the morning with food.",
  "citations": [
    {
      "chunk_id": "doc1_p42_s5_c3",
      "page": 42,
      "section": "5.2.3 Dosing Schedule",
      "text": "Subjects will receive 200mg daily...",
      "bbox": [72.0, 450.2, 520.0, 520.8]
    },
    {
      "chunk_id": "doc1_p43_s5_c5",
      "page": 43,
      "section": "5.2.4 Administration Guidelines",
      "text": "All doses should be taken in the morning...",
      "bbox": [72.0, 380.1, 520.0, 420.3]
    }
  ]
}
```

### New Capabilities
- ✅ **Natural language Q&A** over protocol documents
- ✅ **Precise citations** with page, section, and coordinates
- ✅ **Audit trail** for GCP compliance
- ✅ **Frontend can highlight** cited text in PDF viewer
- ✅ **Multi-document search** across all protocols

### Solving the Original Problem
This directly addresses the gap mentioned in the requirements:

> "GCP 'good clinical practice'…need to be able to show where things came from... **This is where AISQL/ParseDoc is lacking. That's why he's looking elsewhere.**"

✅ **SOLVED:** Every answer includes section, page, and exact coordinates.

### Time Investment: 3 hours

---

## Total Journey

| Phase | Focus | Time | Cumulative |
|-------|-------|------|------------|
| Phase 0 | Baseline extraction | 30 min | 30 min |
| Phase 1 | Page numbers + tables | 45 min | 1h 15m |
| Phase 2 | Full bounding boxes | 30 min | 1h 45m |
| Phase 3 | Font information | 45 min | 2h 30m |
| Phase 4 | Section detection | 2 hours | 4h 30m |
| Phase 5 | Smart chunking | 2 hours | 6h 30m |
| Phase 6 | LLM + citations | 3 hours | **9h 30m** |

### Decision Points

After each phase, you can decide:
- ✅ **Continue:** Move to next enhancement
- ⏸️ **Pause:** Test with real documents, gather feedback
- 🔄 **Iterate:** Refine current phase before advancing
- 🚀 **Production:** Package and deploy

---

## Success Metrics

### Phase 0-2: Foundation
- Can extract text from 100+ page PDFs?
- Extraction time < 2 minutes per 100 pages?
- Data is queryable in Snowflake?

### Phase 3-5: Intelligence
- Correctly identifies 90%+ of section headers?
- Chunks are semantically coherent?
- Average chunk size 500-1000 tokens?

### Phase 6: Value Delivery
- LLM answers are accurate?
- Citations link to correct page/section?
- Regulatory auditors can trace information flow?
- **Users trust the system** because they can verify sources?

---

## Beyond Phase 6

### Potential Enhancements
- **Table extraction:** Dedicated handling for dosing tables, eligibility matrices
- **Multi-document reasoning:** "Compare dosing schedules across 5 protocols"
- **Approval workflows:** Route extracted info to SMEs for validation
- **Change tracking:** Detect when protocols are amended, show diffs
- **Figure/image handling:** OCR for protocol diagrams
- **Structured extraction:** Convert free text into relational tables

### Enterprise Features
- **Role-based access:** Different users see different protocols
- **Data quality scores:** Confidence metrics on extraction accuracy
- **Performance optimization:** Parallel processing for large document sets
- **Integration:** Connect to clinical trial management systems

---

**Current Status:** ✅ Phase 0 Complete  
**Next Action:** Review baseline results, then proceed to Phase 1

