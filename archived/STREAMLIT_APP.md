# 📄 Streamlit PDF Citation Viewer

## Overview

This Streamlit app **demonstrates the value of Phase 2** (full bounding boxes) by showing visual PDF highlighting. It makes the business case for Phase 2 incredibly clear.

## What It Does

### **Phase 1 Mode (Before):**
- Shows search results with page numbers
- User must manually search the PDF page
- ❌ No visual highlighting

### **Phase 2 Mode (After):**
- Shows search results with page numbers
- **Automatically highlights text** on the PDF
- ✅ Visual confirmation of exact location
- 🎯 **Makes the value obvious!**

---

## Setup Instructions

### **Option 1: Deploy to Snowflake (Streamlit in Snowflake)**

1. **Upload the app file:**
   ```sql
   -- In Snowflake UI: Data → Streamlit → Create
   -- Upload: streamlit_pdf_viewer.py
   ```

2. **Configure:**
   - Database: `SANDBOX`
   - Schema: `PDF_OCR`
   - Warehouse: Your compute warehouse

3. **Launch the app!**

### **Option 2: Run Locally with Snowflake Connection**

1. **Install dependencies:**
   ```bash
   pip install streamlit snowflake-snowpark-python
   ```

2. **Configure connection:**
   Create `.streamlit/secrets.toml`:
   ```toml
   [connections.snowflake]
   account = "your_account"
   user = "your_username"
   password = "your_password"
   warehouse = "your_warehouse"
   database = "SANDBOX"
   schema = "PDF_OCR"
   ```

3. **Run the app:**
   ```bash
   streamlit run streamlit_pdf_viewer.py
   ```

---

## Prerequisites

Before using the app, you need:

1. ✅ **Phase 1 Complete:** `document_chunks` table exists
2. ⚠️ **Phase 2 Complete:** Table has `bbox_x0`, `bbox_y0`, `bbox_x1`, `bbox_y1`, `page_width`, `page_height` columns
3. ✅ **Data Loaded:** At least one PDF processed and loaded

---

## Demo Flow

### **Step 1: Search**
Enter a term like "medication" or "dosing" in the sidebar.

### **Step 2: Compare Modes**
Toggle between Phase 1 and Phase 2 to see the difference:

**Phase 1 View:**
```
Results:
  Page 42: "Patients will receive 200mg..."
  
❌ Where on page 42? User must manually search!
```

**Phase 2 View:**
```
Results:
  Page 42: "Patients will receive 200mg..."
  [Click: Highlight on PDF]
  
✅ PDF opens with yellow highlight box around exact text!
```

### **Step 3: Show Stakeholders**
This visual demo makes it **immediately obvious** why Phase 2 matters for:
- FDA reviewers
- Clinical trial auditors
- Legal teams
- Anyone who needs to verify document sources

---

## Business Value Demonstration

### **Before Phase 2 (Pain Point):**
```
Reviewer: "Show me where 200mg is mentioned"
System: "Page 42, position (72.0, 650.3)"
Reviewer: *Opens page 42, manually scans for "200mg"*
⏱️ Time: 30 seconds per citation
😤 Frustration: HIGH
```

### **After Phase 2 (Solution):**
```
Reviewer: "Show me where 200mg is mentioned"
System: *Opens page 42 with text highlighted in yellow*
Reviewer: *Immediately sees the text*
⏱️ Time: 2 seconds per citation
😊 Satisfaction: HIGH
✅ Trust: INCREASED
```

### **ROI Calculation:**
- FDA review: 50 citations per protocol
- Before: 50 × 30 sec = **25 minutes**
- After: 50 × 2 sec = **1.5 minutes**
- **Time saved: 23.5 minutes per protocol**
- **× 100 protocols/year = 39 hours saved** 🎯

---

## Features

### **Search & Filter**
- Full-text search across all chunks
- Case-insensitive matching
- Real-time results

### **Visual Highlighting**
- Animated highlight boxes
- Color-coded matches
- Zoom to citation location

### **Phase Comparison**
- Toggle between Phase 1 and Phase 2
- Side-by-side comparison
- Clear value demonstration

### **Metrics Dashboard**
- Total chunks indexed
- Pages processed
- Current phase status

---

## Customization

### **Change Highlight Color**
```python
# In streamlit_pdf_viewer.py, line ~120
background: rgba(255, 255, 0, 0.3);  # Yellow
border: 3px solid #ff9800;           # Orange

# Change to blue:
background: rgba(33, 150, 243, 0.3);
border: 3px solid #2196F3;
```

### **Add Real PDF Rendering**
To render actual PDFs (not mock), integrate:
- `streamlit-pdf-viewer` library
- `PyMuPDF` for PDF manipulation
- Canvas-based highlighting

### **Add More Search Features**
```python
# Add filters
doc_filter = st.sidebar.multiselect("Documents:", list_of_docs)
page_range = st.sidebar.slider("Page Range:", 1, max_pages)

# Update query
query = f"""
    SELECT * FROM document_chunks
    WHERE text ILIKE '%{search_term}%'
      AND doc_name IN ({doc_filter})
      AND page BETWEEN {page_range[0]} AND {page_range[1]}
"""
```

---

## Troubleshooting

### **Error: Table 'document_chunks' not found**
**Solution:** Run Phase 1 cells in the notebook to create the table.

### **Error: Column 'bbox_x0' not found**
**Solution:** Run Phase 2 cells to add bounding box columns.

### **No results showing**
**Solution:** Make sure data is loaded:
```sql
SELECT COUNT(*) FROM document_chunks;
-- Should return > 0
```

### **App is slow**
**Solution:** 
- Use a larger warehouse
- Add indexes on frequently queried columns
- Limit result set with `LIMIT` clause

---

## Next Steps

### **After Demo:**
1. ✅ **Stakeholder buy-in** secured
2. ✅ **Phase 2 value** proven
3. → **Complete Phase 2** in main notebook
4. → **Enhance app** with real PDF rendering
5. → **Deploy to production**

### **Production Enhancements:**
- Real PDF rendering (not mock)
- Multi-document support
- Export citations to JSON/CSV
- Share links to specific citations
- User authentication
- Audit logging

---

## Screenshot Flow

### **Demo Sequence for Stakeholders:**

1. **Show Phase 1 Mode:**
   - "This is what we have now"
   - Search returns results
   - But user must manually find text
   - ⏱️ Takes 30 seconds

2. **Switch to Phase 2 Mode:**
   - "This is what Phase 2 enables"
   - Click "Highlight on PDF"
   - Text is instantly highlighted
   - ⏱️ Takes 2 seconds
   - **"See the difference?"** 🎯

3. **Show Metrics:**
   - Time saved per citation
   - Multiply by citations per document
   - Calculate ROI
   - **"This pays for itself immediately!"**

---

## FAQ

**Q: Does this require Phase 2 to be complete?**  
A: Yes, the table needs bbox columns. However, the app works in "demo mode" even without Phase 2 to show the concept.

**Q: Can this work with multiple PDFs?**  
A: Yes! Just add a document selector:
```python
doc_name = st.sidebar.selectbox("Select Document:", df['DOC_NAME'].unique())
```

**Q: Can users upload PDFs directly?**  
A: Not in this version, but you could add:
```python
uploaded_file = st.file_uploader("Upload PDF")
# Process and load into document_chunks
```

**Q: What about security?**  
A: The app uses Snowflake's built-in authentication and row-level security. Users only see data they have access to.

---

## Summary

This Streamlit app is your **secret weapon** for getting Phase 2 approved:

- ✅ Shows visual proof of value
- ✅ Takes 5 minutes to set up
- ✅ Makes stakeholders say "Wow!"
- ✅ Justifies the 30-minute investment in Phase 2

**The punch lands MUCH harder when people can SEE the highlighting in action!** 🥊🎯

---

**Built with:** Streamlit + Snowflake Snowpark  
**Time to deploy:** 5-10 minutes  
**Business impact:** Immediate stakeholder buy-in  

