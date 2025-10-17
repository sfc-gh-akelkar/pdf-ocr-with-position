# Sample PDF Note

## About Prot_000.pdf

The sample clinical protocol PDF (`Prot_000.pdf`) is **not included in this repository** due to its large size (~16,000 lines) and because it's sample data.

### To Test This Solution:

You have three options:

#### Option 1: Use Your Own PDF
Upload any PDF document to test the extraction:
- Clinical protocols
- Research papers  
- Technical documentation
- Any multi-page PDF

#### Option 2: Generate a Test PDF
Create a simple test PDF:
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_test_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(100, 750, "Test Protocol Document")
    c.drawString(100, 700, "Section 1: Introduction")
    c.drawString(100, 650, "This is a test protocol for PDF extraction.")
    c.drawString(100, 600, "Section 2: Methods")
    c.drawString(100, 550, "Medications: Test Drug A, 200mg daily")
    c.showPage()
    c.save()

create_test_pdf("test_protocol.pdf")
```

#### Option 3: Download a Public Clinical Protocol
Find publicly available clinical trial protocols from:
- ClinicalTrials.gov
- FDA archives
- Published research repositories

### File Format Requirements:

- **Format:** PDF (not scanned images)
- **Size:** Works best with < 100 pages for initial testing
- **Content:** Text-based PDFs (OCR of scanned images not supported in Phase 0)

### Where to Upload:

Once you have a PDF, follow the instructions in `QUICKSTART.md` to upload it to the Snowflake stage.

---

**Note:** If you're from Snowflake or have access to the original repository context, the sample `Prot_000.pdf` may be available in internal resources or can be shared separately.

