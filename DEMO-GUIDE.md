# Demo Guide - Clinical Protocol Intelligence with Streamlit

## 📋 Pre-Demo Checklist

### ✅ Setup Requirements (Run BEFORE demo):

1. **Database setup complete**
   - Run `setup.sql` to create all objects
   - Verify: `SHOW CORTEX SEARCH SERVICES LIKE 'protocol_search';`

2. **PDF uploaded and processed**
   - Upload `Prot_000.pdf` to `@PDF_STAGE`
   - Run: `CALL process_new_pdfs();`
   - Verify: `SELECT COUNT(*) FROM document_chunks;` (should show > 0)

3. **Streamlit app deployed**
   - Deploy `streamlit_app.py` as Streamlit in Snowflake
   - Test: Open app and verify document browser shows PDF

4. **Warehouse running**
   - `compute_wh` should be active and sized appropriately (Small/Medium)

5. **Browser tabs open:**
   - Streamlit app (primary demo)
   - SQL worksheet (for showing backend if needed)

### 🎯 What to Pre-Test:

- [ ] Open Streamlit app - loads without errors
- [ ] Document browser shows uploaded PDF with metadata
- [ ] Run test search: "dosing schedule" returns results
- [ ] Results show proper citations (page + position)
- [ ] Browse by page works
- [ ] Export to CSV works

---

## 🎬 Demo Flow

### **Opening Hook (2 minutes)**

**YOU SAY:**
> "Pharmaceutical companies deal with hundreds of clinical protocol PDFs. When regulatory teams need to find specific information - like dosing schedules, inclusion criteria, or safety data - they face these challenges..."

**SHOW:** Open a sample PDF in another tab and simulate manual search:
- Ctrl+F for "dosing"
- Multiple matches, no context
- No way to know if you found everything
- No citation for audit trail

**YOU SAY:**
> "What if instead of this manual process, they could just ask questions in natural language and get instant answers with **audit-grade citations** - not just page numbers, but exact positions like 'Page 5, top-right'?"

**TRANSITION:** "Let me show you what we built, 100% native in Snowflake."

---

### **Part 1: The Streamlit App (10 minutes)**

**OPEN:** Streamlit app in full screen

#### **1. Show the Interface (1 minute)**

**YOU SAY:**
> "This is a Streamlit in Snowflake app. It's 100% native - no external services, no data leaving Snowflake. Everything runs inside your Snowflake environment with full governance."

**POINT OUT:**
- Clean, user-friendly interface
- Document browser in sidebar
- Search bar for natural language queries
- Tabs for different features

#### **2. Document Browser (2 minutes)**

**SHOW:** Sidebar

**YOU SAY:**
> "The document browser shows all available protocols. Notice it shows metadata automatically - total pages, number of text chunks extracted, when it was processed."

**CLICK:** On a document in the sidebar

**SHOW:** Metadata updates (pages, chunks, processed date)

**KEY POINT:** "This metadata is automatically extracted. No manual cataloging needed."

#### **3. Semantic Search Demo (5 minutes)**

**YOU SAY:**
> "Now let's ask a real question. I'm going to ask: 'What is the dosing schedule?'"

**TYPE:** `What is the dosing schedule?`

**CLICK:** Search

**WAIT:** for results (should be < 2 seconds)

**POINT OUT as results appear:**

1. **Speed:** "Notice how fast that was - semantic search across the entire document"

2. **Citations:** "Every result shows:"
   - Document name (`Prot_000.pdf`)
   - Page number (`Page 5`)
   - Position on page (`top-right`, `middle-center`, etc.)

3. **Relevance:** "These are semantically ranked - not just keyword matching. Cortex Search understands meaning."

4. **Details:** Click "Details" expander
   - Show chunk ID (for traceability)
   - Show bounding box coordinates
   - **KEY POINT:** "These coordinates could be used to highlight the exact text in a PDF viewer"

**TRY ANOTHER QUERY:**

**YOU SAY:**
> "Let's try something more complex: 'What are the inclusion criteria?'"

**TYPE:** `What are the inclusion criteria?`

**SHOW:** Results with different pages and positions

**POINT OUT:** "Notice it found relevant sections across multiple pages, all with precise locations."

#### **4. Export Results (1 minute)**

**CLICK:** "Export Results to CSV"

**DOWNLOAD:** the CSV file

**SHOW:** Open CSV in preview

**YOU SAY:**
> "Users can export results for documentation, regulatory submissions, or offline analysis. Every citation is preserved for audit trails."

#### **5. Browse by Page (1 minute)**

**CLICK:** "Browse by Page" tab

**YOU SAY:**
> "Users can also browse specific pages directly if they know where to look."

**SELECT:** Document from sidebar (if not already selected)

**ENTER:** Page number (e.g., 5)

**CLICK:** "Load Page"

**SHOW:** All text chunks from that page with positions

**YOU SAY:**
> "This shows all extracted content from the page, organized by position. Great for verification or detailed review."

---

### **Part 2: The Technology Behind It (5 minutes)**

**SWITCH TO:** SQL worksheet (optional, depending on technical audience)

**YOU SAY:**
> "Let me show you what makes this possible. It's all Snowflake-native."

#### **1. PDF Extraction UDF**

**SHOW:** (don't run, just show code)
```sql
SHOW FUNCTIONS LIKE 'pdf_txt_mapper_v3';
```

**YOU SAY:**
> "We built a Python UDF using pdfminer that extracts text with full bounding box coordinates - the x,y coordinates of every text box on every page."

**SHOW:** Example output structure (from `setup.sql` comments):
```json
{
  "page": 5,
  "bbox": [320, 680, 550, 720],
  "page_width": 612,
  "page_height": 792,
  "txt": "Dosing is BID for 28 days..."
}
```

**KEY POINT:** "This is the secret sauce - extracting not just text, but WHERE it appears on the page."

#### **2. Document Chunks Table**

**RUN:**
```sql
SELECT * FROM document_chunks LIMIT 5;
```

**YOU SAY:**
> "All that extracted data goes into a structured table that we can query. Notice the bounding box columns - x0, y0, x1, y1 - that define exact rectangles around text."

#### **3. Cortex Search**

**SHOW:**
```sql
SHOW CORTEX SEARCH SERVICES LIKE 'protocol_search';
```

**YOU SAY:**
> "Cortex Search automatically generates embeddings for semantic search. We don't manage vectors - Snowflake handles all of that. The service auto-refreshes as new documents are added."

**RUN:** Direct Cortex Search query:
```sql
SELECT * FROM TABLE(
    SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
        'protocol_search',
        '{"query": "dosing schedule", "columns": ["text", "page", "doc_name"], "limit": 3}'
    )
);
```

**YOU SAY:**
> "This is what the Streamlit app calls under the hood. Direct semantic search with one function call."

#### **4. Position Calculator**

**SHOW/RUN:**
```sql
SELECT 
    page,
    calculate_position_description(bbox_x0, bbox_y0, bbox_x1, bbox_y1, page_width, page_height) AS position,
    SUBSTR(text, 1, 50) AS text_preview
FROM document_chunks
LIMIT 5;
```

**YOU SAY:**
> "We convert raw coordinates into human-readable positions like 'top-right' or 'middle-center'. Makes citations more intuitive for users."

---

### **Part 3: Automated Pipeline (3 minutes)**

**YOU SAY:**
> "Now here's where it gets operationally powerful. This isn't a one-off demo - it's production-ready with automated processing."

#### **1. Show Directory Monitoring**

**RUN:**
```sql
SELECT * FROM DIRECTORY(@PDF_STAGE);
```

**YOU SAY:**
> "Snowflake's directory tables automatically track files in stages. We can detect new PDFs as soon as they're uploaded."

#### **2. Processing Procedure**

**SHOW** (don't run, just show):
```sql
CALL process_new_pdfs();
```

**YOU SAY:**
> "This stored procedure automatically:
> 1. Finds new PDFs in the stage
> 2. Extracts text with our UDF
> 3. Loads it into the table
> 4. Refreshes the Cortex Search index
> 
> It can be called manually or scheduled with Snowflake Tasks."

#### **3. Scheduled Task**

**RUN:**
```sql
SHOW TASKS LIKE 'process_pdfs_task';
```

**YOU SAY:**
> "We created a task that runs every hour. Drop new PDFs in the stage, and within an hour, they're automatically indexed and searchable. Zero manual work."

---

### **Part 4: The Snowflake-Native Advantage (3 minutes)**

**SWITCH BACK TO:** Streamlit app

**YOU SAY:**
> "What makes this solution different from external RAG tools?"

**ENUMERATE benefits:**

1. **Zero Data Movement**
   - "PDFs stay in Snowflake stages. No copying to vector databases or cloud storage."

2. **Native Governance**
   - "Snowflake RBAC controls who can see what. Full audit logs. GxP compliant."

3. **No Infrastructure**
   - "No servers to manage, no vector databases to maintain. Just SQL and Streamlit."

4. **Precise Citations**
   - "Not just 'found on page 5' - we give exact positions with coordinates. Regulatory teams can verify every answer."

5. **Automatic Scaling**
   - "Cortex Search and UDFs scale automatically. Works with 10 PDFs or 10,000."

**KEY POINT for Pharma/Regulated Industries:**
> "For clinical trials and regulatory submissions, you need audit-grade traceability. This solution provides exact citations - page, position, coordinates - that meet FDA and EMA requirements for source data verification."

---

### **Finale: Value Summary (2 minutes)**

**YOU SAY:**
> "Let's recap what we've shown:"

**SUMMARIZE:**

✅ **Instant Search**
- "Seconds instead of hours to find information"

✅ **Precise Citations**
- "Audit-grade traceability with page and position"

✅ **100% Snowflake-Native**
- "No external services, full governance, zero data movement"

✅ **Automated Pipeline**
- "Drop PDFs in a stage, get searchable in an hour"

✅ **User-Friendly Interface**
- "Streamlit app for non-technical users, no SQL required"

**CLOSE:**
> "This isn't just a demo - it's production-ready code. We can deploy this in your environment today and have you searching your protocol library by tomorrow."

---

## 🎯 Talking Points by Audience

### For **Regulatory Affairs / Clinical Ops:**
- Emphasize **audit-grade citations** and **traceability**
- Mention **FDA/EMA compliance** for source data verification
- Highlight **export to CSV** for regulatory submissions
- Show **bounding box coordinates** for verification

### For **IT / Data Engineering:**
- Show **SQL setup** and **UDF code**
- Emphasize **Snowflake-native** (no external dependencies)
- Demo **automated pipeline** with tasks
- Discuss **scalability** and **governance**

### For **Business Users:**
- Focus on **Streamlit app UI**
- Keep it simple: "Ask questions, get answers"
- Show **document browser** and **export**
- Avoid technical details

### For **Executives:**
- **Speed:** "Hours → seconds for document research"
- **Cost:** "No infrastructure, pay only for what you use"
- **Risk:** "No data movement, full Snowflake governance"
- **Value:** "Faster trial startup, faster regulatory submissions"

---

## 🛠️ Troubleshooting During Demo

### Issue: Streamlit app is slow
**Fix:** Pre-warm the warehouse before the demo:
```sql
SELECT COUNT(*) FROM document_chunks;
```

### Issue: No search results
**Check:**
- Document was processed: `SELECT COUNT(*) FROM document_chunks;`
- Cortex Search is active: `SHOW CORTEX SEARCH SERVICES;`
- Refresh index: `ALTER CORTEX SEARCH SERVICE protocol_search REFRESH;`

### Issue: Streamlit app error on load
**Fix:** Restart the app or refresh the browser

### Issue: "No documents found" in sidebar
**Fix:** 
- Check data exists: `SELECT DISTINCT doc_name FROM document_chunks;`
- Ensure schema is correct in app: `USE SCHEMA SANDBOX.PDF_OCR;`

---

## 📊 Sample Questions for Different Use Cases

### Clinical Protocols:
```
What is the dosing schedule?
What are the inclusion criteria?
List all adverse events
What is the primary endpoint?
How long is the treatment period?
Describe the patient population
What are the exclusion criteria?
```

### Regulatory Documents:
```
What are the safety monitoring procedures?
Describe the data monitoring committee
What are the stopping rules?
Find information about informed consent
```

### Operational:
```
How many pages is this protocol?
What documents mention chemotherapy?
Find all references to FDA guidance
```

---

## 🎁 Leave-Behinds

After the demo, provide:

1. **GitHub Repo** (if public)
2. **setup.sql** - Complete setup script
3. **streamlit_app.py** - App source code
4. **README.md** - Full documentation
5. **QUICKSTART.md** - Setup guide

**Next Steps:**
1. "Let's schedule a technical workshop to deploy in your environment"
2. "What other document types would you like to add?"
3. "Would you like to see this integrated with your eTMF system?"

---

## 💡 Advanced Features to Mention (If Time)

- **Multi-document comparison**: "We could add side-by-side protocol comparison"
- **PDF viewer integration**: "Bounding boxes could highlight source text in a PDF viewer"
- **Document versioning**: "Track protocol amendments and changes over time"
- **Custom metadata**: "Add trial phase, indication, sponsor info for richer filtering"
- **Alerts**: "Get notified when specific terms appear in new protocols"

---

**Remember:** The key differentiator is **precise citations with positions**. Keep coming back to "Page 5, top-right, coordinates [320, 680, 550, 720]" - this is what competitors can't do.

🎉 **Good luck with your demo!**
