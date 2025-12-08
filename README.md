# Clinical Protocol Intelligence
## AI-Powered Document Q&A with Audit-Grade Citations

<p align="center">
  <strong>Snowflake-Native Solution for Intelligent Clinical Protocol Search</strong>
</p>

---

## 🎯 Overview

**Clinical Protocol Intelligence** is a production-ready, Snowflake-native solution that transforms how regulated industries work with complex documents. Built for pharmaceutical, biotech, and clinical research organizations, it provides:

- ⚡ **AI-Powered Search**: Semantic understanding, not just keyword matching
- 📍 **Audit-Grade Citations**: Every answer includes exact page + coordinates
- 🔒 **Enterprise Security**: 100% Snowflake-native, data never leaves your environment
- 🤖 **Multiple LLM Models**: Claude, Llama, GPT, Mistral - choose what fits your needs
- 🎨 **User-Friendly UI**: No SQL knowledge required

---

## 📸 Screenshots

### AI-Powered Q&A with Precise Citations
*Natural language questions → Instant answers with page-level precision*

![Search Interface](docs/screenshot-search.png)


---

## 🚀 Getting Started

### Prerequisites
- Snowflake account with Cortex Search & Cortex AI enabled
- ACCOUNTADMIN role access (or sufficient privileges to create schemas, functions, and services)

### 3-Step Setup

#### Step 1: Update Database & Schema Names

**In `setup.sql` (lines 27, 31-32):**
```sql
-- Change to your values:
CREATE SCHEMA IF NOT EXISTS YOUR_DATABASE.YOUR_SCHEMA;
USE DATABASE YOUR_DATABASE;
USE SCHEMA YOUR_SCHEMA;
```

**In `streamlit_app.py` (lines 42-43):**
```python
# Change to your values:
DATABASE_NAME = "YOUR_DATABASE"
SCHEMA_NAME = "YOUR_SCHEMA"
```

#### Step 2: Run Database Setup

Execute `setup.sql` in Snowsight or SnowSQL.

This creates:
- Stage for PDF storage (`@PDF_STAGE`)
- Python UDF for text extraction (`pdf_txt_mapper_v3`)
- Table for document chunks (`document_chunks`)
- Cortex Search service (`protocol_search`)
- Stored procedure for automation (`process_new_pdfs()`)

**Verify:**
```sql
SHOW STAGES LIKE 'PDF_STAGE';
SHOW FUNCTIONS LIKE 'pdf_txt_mapper_v3';
SHOW CORTEX SEARCH SERVICES LIKE 'protocol_search';
```

#### Step 3: Deploy Streamlit App

1. In Snowsight, go to **Streamlit** → **+ Streamlit App**
2. Name it (e.g., `Clinical_Protocol_Intelligence`)
3. Select your warehouse, database, and schema
4. Paste contents of `streamlit_app.py`
5. Click **Run**

**Done!** 🎉

---

### Usage

**Upload PDFs:**
- Via Streamlit app (sidebar file uploader), or
- Via Snowsight: Data → Your Schema → PDF_STAGE → Upload Files

**Process PDFs:**
```sql
CALL process_new_pdfs();
```

**Start Searching:**
Open your Streamlit app and ask questions like:
- "What is the dosing schedule for nivolumab?"
- "What disease or tumor types are being studied?"
- "How is clinical response evaluated?"

---

### Optional: Access Control

```sql
-- Create read-only role for end users
CREATE ROLE PDF_VIEWER;
GRANT USAGE ON DATABASE YOUR_DATABASE TO ROLE PDF_VIEWER;
GRANT USAGE ON SCHEMA YOUR_SCHEMA TO ROLE PDF_VIEWER;
GRANT SELECT ON ALL TABLES IN SCHEMA YOUR_SCHEMA TO ROLE PDF_VIEWER;
GRANT USAGE ON STREAMLIT YOUR_SCHEMA.YOUR_APP_NAME TO ROLE PDF_VIEWER;

-- Assign to users
GRANT ROLE PDF_VIEWER TO USER username;
```

---

## 🏗️ Architecture

```
┌─────────────────┐
│   PDF Files     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  @PDF_STAGE     │  ← Snowflake Internal Stage
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ pdf_txt_mapper  │  ← Python UDF (pdfminer)
│   (UDF)         │     Extracts text + coordinates
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ document_chunks │  ← Structured table
│    (Table)      │     Text + bbox + page info
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Cortex Search   │  ← Semantic search with embeddings
│   Service       │     Arctic-embed-l-v2.0 model
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Cortex AI       │  ← LLM answer synthesis (RAG)
│  Complete       │     Claude/Llama/GPT/Mistral
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Streamlit     │  ← User interface
│      App        │     Search + Citations + Upload
└─────────────────┘
```

**Key Features:**
- ✅ **100% Snowflake-Native**: No external APIs or data movement
- ✅ **Enterprise Governance**: RBAC, audit logs, data classification
- ✅ **Scalable**: Serverless compute, auto-scaling
- ✅ **Cost-Optimized**: Pay only for what you use

---

## 📚 What's Included

### Core Components

| File | Description |
|------|-------------|
| `setup.sql` | Database setup script (stages, tables, UDFs, search service) |
| `streamlit_app.py` | Main application (Streamlit in Snowflake) |


---

## 💡 Use Cases

### 🏥 Regulatory Compliance & Audit Preparation
**Scenario:** FDA inspector asks "Show me all adverse event monitoring procedures"

**Before:** Hours of manual search through 200-page PDFs
**After:** Instant answer with exact page locations and verifiable citations

### 📊 Cross-Study Protocol Comparison
**Scenario:** Ensure dosing consistency across protocol versions

**Before:** Manual side-by-side comparison, risk of missing changes
**After:** Query "dosing schedule" across all versions, identify variations instantly

### ⚖️ Legal & IP Documentation
**Scenario:** Patent application requiring precise source citations

**Before:** Manual documentation, imprecise references
**After:** Exact coordinates [x0, y0, x1, y1] for every claim

### 📚 Training & Knowledge Management  
**Scenario:** Train new team members on protocol content

**Before:** Time-intensive material preparation
**After:** Auto-generated references with audit-grade citations

---

## 🎯 Key Differentiators

### vs. Manual Search
- ⚡ **100x faster** document review
- 🎯 **Never miss information** with semantic understanding
- 📊 **Consistent results** across reviewers

### vs. External AI Tools (ChatGPT, etc.)
- 🔒 **Data never leaves Snowflake** environment
- 🎯 **Audit-grade citations** with exact coordinates
- ⚖️ **Regulatory compliant** with enterprise governance
- 🏢 **Native RBAC** and data classification

### vs. Traditional Document Management
- 🧠 **Semantic understanding**, not just keyword matching
- 🔗 **Cross-document intelligence** automatically
- 🤖 **AI synthesis** with verifiable sources

---

## 🛠️ Technical Details

### Snowflake Features Used
- **Cortex Search**: Hybrid (semantic + keyword) search
- **Cortex AI Complete**: LLM-powered answer synthesis
- **Python UDFs**: Custom PDF text extraction
- **Streamlit in Snowflake**: Native web application
- **Snowpark**: Data processing and transformations
- **Tasks & Procedures**: Automated PDF processing

### PDF Extraction
- **Library**: pdfminer (robust, layout-aware)
- **Captures**: Text, bounding boxes [x0, y0, x1, y1], page dimensions
- **Handles**: Multi-column layouts, tables, headers, footers
- **Output**: JSON with full position metadata

### Search & Indexing
- **Embedding Model**: `snowflake-arctic-embed-l-v2.0`
- **Index Type**: Hybrid (vector similarity + keyword matching)
- **Update Frequency**: Real-time with TARGET_LAG = 1 hour
- **Filters**: Document name, page number, custom attributes

### LLM Models Supported
- **Claude**: 4-sonnet, 3.7-sonnet, 3.5-sonnet, haiku
- **Llama**: 4-maverick, 4-scout, 3.1-405b, 3.1-70b, 3.1-8b
- **GPT**: openai-gpt-4.1, openai-o4-mini
- **Mistral**: mistral-large2
- **Snowflake**: snowflake-arctic

---

## 📊 Performance & Cost

### Typical Performance
- **Search Response Time**: 2-5 seconds (including LLM synthesis)
- **PDF Processing**: 30-60 seconds per document (automatic, background)
- **Concurrent Users**: Scales with Snowflake warehouse size

### Cost Estimates (Approximate)
- **Search Query**: ~$0.001 per query (Cortex Search)
- **LLM Synthesis**: ~$0.02 per response (varies by model)
- **Storage**: Standard Snowflake rates for table data
- **Compute**: Based on warehouse usage (auto-suspend recommended)

*Costs vary by region, warehouse size, and usage patterns. See Snowflake pricing for details.*

---

## 🔐 Security & Governance

### Built-in Security Features
- ✅ **Data Residency**: All processing within your Snowflake account
- ✅ **RBAC**: Role-based access control for users
- ✅ **Audit Logging**: All queries automatically logged
- ✅ **Data Classification**: Tag and classify sensitive data
- ✅ **Row Access Policies**: Restrict document access by user
- ✅ **Network Policies**: IP whitelisting if needed

### Compliance Considerations
- **HIPAA**: Snowflake is HIPAA compliant (BAA required)
- **GxP**: Audit trails and data lineage built-in
- **SOC 2**: Snowflake SOC 2 Type II certified
- **GDPR**: Data residency and right-to-delete supported

---

## 🆘 Troubleshooting

**Search returns no results?**
```sql
-- Refresh the search index
ALTER CORTEX SEARCH SERVICE YOUR_SCHEMA.protocol_search REFRESH;
```

**PDF processing fails?**
```sql
-- Check for errors in query history
SELECT query_text, error_message 
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE query_text ILIKE '%process_new_pdfs%'
ORDER BY start_time DESC LIMIT 5;
```

**Questions?**
- Open a GitHub Issue
- Contact your Snowflake account team
- Visit [community.snowflake.com](https://community.snowflake.com)

---

## 🎓 Resources

### Snowflake Documentation
- [Cortex Search Guide](https://docs.snowflake.com/en/user-guide/cortex-search)
- [Cortex AI Functions](https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions)
- [Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [Python UDFs](https://docs.snowflake.com/en/developer-guide/udf/python/udf-python)

### Related Solutions
- [Snowflake Cortex Examples](https://github.com/Snowflake-Labs/cortex-examples)
- [Document AI Solutions](https://quickstarts.snowflake.com/guide/document-ai/)

---

## 🌟 Acknowledgments

Built with:
- **pdfminer**: PDF parsing library
- **Snowflake Cortex**: AI and search capabilities
- **Streamlit**: User interface framework

Special thanks to the Snowflake Cortex and Document AI teams.

---

<p align="center">
  <strong>Made with ❄️ by Snowflake</strong><br>
  <a href="https://www.snowflake.com">www.snowflake.com</a>
</p>
