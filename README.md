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

### Cross-Document Intelligence
*Search across hundreds of protocols simultaneously*

![Multi-Doc Search](docs/screenshot-multi-doc.png)

---

## 🚀 Quick Start

### Prerequisites
- Snowflake Enterprise Edition or higher
- Cortex Search & Cortex AI enabled
- Streamlit in Snowflake enabled
- ACCOUNTADMIN role (for initial setup)

### 5-Minute Setup

```bash
# 1. Clone this repository
git clone https://github.com/Snowflake-Labs/clinical-protocol-intelligence.git
cd clinical-protocol-intelligence

# 2. Update database/schema names
# Edit setup.sql lines 27, 31-32
# Edit streamlit_app.py lines 42-43

# 3. Run setup in Snowflake
# Execute setup.sql in Snowsight or SnowSQL

# 4. Deploy Streamlit app
# Copy streamlit_app.py to Streamlit in Snowflake

# 5. Upload PDFs and start searching!
```

**📖 Detailed Instructions**: See [DEPLOYMENT.md](DEPLOYMENT.md)

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

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | This file - project overview |
| `DEPLOYMENT.md` | Step-by-step deployment guide |
| `DEMO-GUIDE.md` | 15-minute demo presentation script |
| `QUICKSTART.md` | Fast setup for experienced users |
| `SAMPLE_DATA.md` | Where to get test PDFs |

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

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Reporting Issues
- **Bug reports**: Use GitHub Issues with detailed description
- **Feature requests**: Describe use case and expected behavior
- **Security issues**: Email security@snowflake.com (do not use GitHub)

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

**Copyright (c) 2025 Snowflake Inc.**

---

## 🆘 Support

### Getting Help
1. **Documentation**: Check [DEPLOYMENT.md](DEPLOYMENT.md) first
2. **Snowflake Support**: support.snowflake.com (for account-specific issues)
3. **Community**: community.snowflake.com
4. **GitHub Issues**: For bugs and feature requests

### Professional Services
For enterprise deployments, custom integrations, or training:
- Contact your Snowflake account team
- Email: professional-services@snowflake.com

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
