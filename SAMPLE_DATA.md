# Sample Data for Testing

This solution works with any PDF documents, but clinical trial protocols are ideal for demonstration.

## Where to Get Sample PDFs

### Option 1: ClinicalTrials.gov
Download publicly available clinical trial protocols:

1. Visit [ClinicalTrials.gov](https://clinicaltrials.gov/)
2. Search for a trial (e.g., "NCT01714739")
3. Look for "Documents" or "Study Protocol" sections
4. Download PDF protocol documents

### Option 2: Public Clinical Trial Databases
- **FDA.gov**: Search approved drug applications with protocols
- **EMA (European Medicines Agency)**: Clinical trial documentation
- **WHO ICTRP**: International Clinical Trials Registry Platform

### Option 3: Academic Repositories
- **PubMed Central**: Some published protocols
- **University repositories**: Research protocols (check licensing)

## Sample Queries to Test

Once you have PDFs uploaded, try these queries:

### Basic Queries:
- "What is the study title and NCT number?"
- "What is the dosing schedule?"
- "What disease is being studied?"
- "What is the study phase?"

### Cross-Document Queries:
- "What is the dosing schedule for nivolumab?"
- "What disease or tumor types are being studied?"
- "How is clinical response evaluated?"

### Methodology Queries:
- "How is response evaluated?"
- "What are the primary endpoints?"
- "What is the study design?"

## Data Privacy & Compliance

**⚠️ Important:**
- Only upload **publicly available** or **properly authorized** documents
- Do NOT upload documents containing:
  - Patient identifiable information (PII)
  - Protected health information (PHI)
  - Proprietary/confidential information without authorization
- Ensure compliance with your organization's data governance policies
- Use Snowflake's data classification and masking features if needed

## Testing the Upload Feature

1. Prepare a PDF (max 50MB)
2. Open the Streamlit app
3. Use the file uploader in the sidebar
4. Click "Upload & Process"
5. Wait ~30-60 seconds for processing
6. Document should appear in the dropdown
7. Try searching the content

## Recommended Test Set

For a comprehensive demo, have:
- **3-5 PDFs** from different protocols/studies
- **100-200 pages each** (good size for testing)
- **Similar document types** (e.g., all clinical protocols)
- **Different versions** (to show cross-document comparison)

This allows you to demonstrate:
- ✅ Multi-document search
- ✅ Cross-protocol comparison
- ✅ Precise citations across documents
- ✅ Upload and processing capabilities

