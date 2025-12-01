# 30-Minute Demo Guide - Clinical Protocol Intelligence

## 📋 Pre-Demo Checklist (5 mins before)

### ✅ Setup Requirements:
1. **Notebook imported** - `pdf-ocr-with-position.ipynb` loaded in Snowflake
2. **PDF uploaded** - `Prot_000.pdf` in `@PDF_STAGE`
3. **Cells pre-run** - Run cells 1-16 BEFORE the demo (setup through agent creation)
4. **Warehouse running** - `COMPUTE_WH` active
5. **Browser tabs open:**
   - Snowflake notebook
   - Snowflake Intelligence UI (for finale)

### 🎯 What to Pre-Run (BEFORE customer arrives):
- Cell 3: `setup` (environment)
- Cell 5: `create_udf` (PDF extraction function)
- Cell 9: `load_data` (load the PDF - takes ~30 seconds)
- Cell 13: `position_func` (position calculator)
- Cell 14: `cortex_search` (Cortex Search service)
- Cell 15: `agent_tools` (agent tools)
- Cell 17: `create_agent` (the agent itself)

**Why pre-run?** These take time and aren't the "wow" moments. Save demo time for the exciting parts!

---

## 🎬 Demo Flow (30 Minutes)

### **Minutes 0-5: The Story**

**Start here:** Cell 1 (intro markdown)

**YOU SAY:**
> "Pharmaceutical companies process hundreds of clinical protocol PDFs. When regulatory teams ask questions like 'What's the dosing schedule in Protocol ABC-123?', they face these problems..."

**SHOW:** The 4 pain points (manual search, no traceability, etc.)

**YOU SAY:**
> "We built a Snowflake-native solution that changes the game. Instead of hours of manual work, they get instant answers with PRECISE citations."

**SHOW:** The example answer with Page 5, top-right, coordinates

**KEY POINT:** Emphasize "PRECISE citations" - not just "Page 5", but exact coordinates. This is the differentiator.

---

### **Minutes 5-8: PDF Extraction**

**Jump to:** Cell 4 (extraction intro)

**YOU SAY:**
> "Our Snowflake FCTO gave us this baseline - solid PDF extraction using pdfminer. We enhanced it with 3 critical additions..."

**SHOW:** The before/after comparison:
- Before: `{'pos': (x, y), 'txt': '...'}`
- After: Full page numbers, bounding boxes, dimensions

**RUN:** Cell 7 (`test_extract`)

**WHILE IT RUNS, SAY:**
> "Watch - we're extracting the PDF right now, capturing EXACT coordinates for every text element..."

**WHEN RESULTS APPEAR:**
> "See? Page number, text preview, and the full bounding box. This is what enables precise citations."

**TIME CHECK:** Should be at minute 7-8

---

### **Minutes 8-11: Structured Storage**

**YOU SAY:**
> "We load this into a Snowflake table - fully queryable, governed, and ready for AI."

**RUN:** Cell 11 (`query_data`) - *Already has data from pre-run*

**SHOW:** The structured table output

**YOU SAY:**
> "Now it's not just raw PDF data - it's structured, queryable, and indexed. This feeds our AI layer."

**TIME CHECK:** Should be at minute 10-11

---

### **Minutes 11-14: AI Setup (Quick Overview)**

**Jump to:** Cell 12 (AI header)

**YOU SAY:**
> "Now for the AI magic. We built 4 components..." *(point to the list)*

**DON'T RUN ANYTHING** - these are pre-run. Just explain:

1. **Position calculator** - "Converts coordinates to 'top-right', 'middle-left', etc."
2. **Cortex Search** - "Semantic search with auto-embeddings. No vector management!"
3. **Agent tools** - "Custom functions for metadata and location search"
4. **Cortex Agent** - "The orchestrator - Claude 4 Sonnet that picks the right tool"

**YOU SAY:**
> "All of this is already set up. Now watch what it can do..."

**TIME CHECK:** Should be at minute 13-14

---

### **Minutes 14-25: THE WOW - Agent Demo** 🎯

**This is the money moment!** Slow down, let it breathe.

**Jump to:** Cell 18 (demo3_header)

**YOU SAY:**
> "This is where it gets exciting. I'm going to ask the agent some questions. Watch how it responds..."

**RUN:** Cell 19 (`test_content`) - "What is the dosing schedule?"

**WHILE IT RUNS:**
> "The agent is now: 1) Understanding the question, 2) Picking the right tool - probably Cortex Search, 3) Synthesizing the answer..."

**WHEN RESULTS APPEAR:**
*(Read the response out loud, especially the citation part)*

**HIGHLIGHT:**
> "Notice - Page 5, top-right, coordinates [320, 680, 550, 720]. This is PRECISE. A regulatory reviewer can go EXACTLY to that spot and verify."

**PAUSE** - Let it sink in.

**RUN:** Cell 20 (`test_metadata`) - "How many pages?"

**YOU SAY:**
> "Different question type - watch how it picks a different tool..."

**WHEN RESULTS APPEAR:**
> "See? It used the metadata tool, not search. The agent is smart about which tool to use."

**RUN:** Cell 21 (`test_location`) - "What's on page 1, top-center?"

**YOU SAY:**
> "And here's a location-specific query..."

**WHEN RESULTS APPEAR:**
> "Used the location tool. Same precise citation format."

**NOW THE CRESCENDO:**

**Jump to:** Cell 23 (`live_demo`)

**YOU SAY:**
> "Now let's go off-script. What do YOU want to know about this protocol?"

**TAKE SUGGESTIONS** from the audience. Edit Cell 23 with their question and run it.

**SUGGESTED QUESTIONS IF THEY FREEZE:**
- "What are the inclusion criteria?"
- "Find mentions of adverse events"
- "Compare primary and secondary endpoints"

**RUN 2-3 LIVE QUESTIONS**

**TIME CHECK:** Should be at minute 24-25

---

### **Minutes 25-28: The Value Prop**

**Jump to:** Cell 26 (summary)

**YOU SAY:**
> "Let's talk about why this matters compared to external RAG solutions..."

**SHOW:** The comparison table

**EMPHASIZE:**
- ✅ **Zero data movement** - "PDFs never leave Snowflake"
- ✅ **Precise coordinates** - "Not just page-level citations"
- ✅ **SQL deployment** - "No Kubernetes, no infrastructure"
- ✅ **Snowflake-managed** - "We don't maintain embeddings, models, or infrastructure"

**YOU SAY:**
> "This is production-ready TODAY. No POC, no infrastructure setup."

**TIME CHECK:** Should be at minute 27-28

---

### **Minutes 28-30: The Finale**

**OPEN NEW TAB:** Snowflake Intelligence UI

**RUN:** Cell 27 (`grant_access`) to show the grant command

**YOU SAY:**
> "For end users, they don't even see SQL. Let me show you..."

**SWITCH TO INTELLIGENCE UI:**
1. Select the `protocol_intelligence_agent`
2. Type a question in the chat
3. **Let the audience see the clean UX**

**YOU SAY:**
> "This is what regulatory reviewers see. Clean chat interface, zero code. They type questions, get answers with citations. That's it."

**ASK FOR QUESTIONS**

**TIME CHECK:** Should be at minute 29-30

---

## 🎤 Key Talking Points to Hit

### 1. **Precise Citations** (mention 5+ times)
- Not just "Page 5"
- Exact position: "top-right"
- Coordinates: [320, 680, 550, 720]
- **Why it matters:** Regulatory compliance, audit trails

### 2. **Snowflake-Native** (mention 3+ times)
- Zero data movement
- Native governance (RBAC)
- No external tools
- **Why it matters:** Security, compliance, simplicity

### 3. **Building on FCTO's Foundation** (mention 1-2 times)
- Started with solid baseline
- Added surgical enhancements
- **Why it matters:** Shows partnership, not reinvention

### 4. **Production-Ready** (mention 2-3 times)
- Not a POC
- Auto-processing
- Snowflake-managed
- **Why it matters:** Time to value

---

## ⚠️ Common Pitfalls to Avoid

### ❌ Don't:
1. **Run cells 5, 9, 13-17 during demo** - Pre-run these! They're slow and not exciting
2. **Rush the agent demo** - This is the wow moment, let it breathe
3. **Skip the comparison table** - This sells the value vs. external tools
4. **Forget to show Intelligence UI** - Non-technical users need to see this!
5. **Over-explain the code** - Focus on WHAT it does, not HOW

### ✅ Do:
1. **Tell the story** - Pain point → Solution → Value
2. **Show precise citations multiple times** - This is the differentiator
3. **Take live questions** - Shows confidence and engagement
4. **Emphasize "Snowflake-native"** - No data movement, native governance
5. **End with Intelligence UI** - Beautiful UX for end users

---

## 🚨 Troubleshooting

### If PDF extraction fails:
- **Check:** Is `Prot_000.pdf` in `@PDF_STAGE`?
- **Fix:** Upload via UI, then re-run cell 9

### If agent doesn't respond:
- **Check:** Is `COMPUTE_WH` running?
- **Check:** Did cells 13-17 complete successfully?
- **Fix:** Re-run the agent creation (cell 17)

### If you run out of time:
- **Skip:** Cell 25 (automation) - nice to have, not critical
- **Skip:** Extra live demo questions
- **Keep:** Agent demo (cells 19-21) - this is non-negotiable!

---

## 📊 Success Metrics

**You nailed the demo if:**
- ✅ Audience says "Wow!" when they see precise citations
- ✅ Someone asks "Can we try this on our protocols?"
- ✅ You finish with 2-3 minutes for Q&A
- ✅ Non-technical stakeholders understand the value
- ✅ Technical stakeholders are impressed by Snowflake-native approach

---

## 🎯 Customization Tips

### If audience is:

**Non-technical (regulatory, clinical reviewers):**
- Spend MORE time on agent demo (minutes 14-25)
- Emphasize Snowflake Intelligence UI
- Skip technical details of UDF, Cortex Search internals
- Focus on precise citations and ease of use

**Technical (data engineers, architects):**
- Show the UDF code (cell 5) - explain enhancements
- Discuss Cortex Search architecture
- Emphasize zero vector management, auto-scaling
- Show automation (cell 25)

**Mixed audience:**
- Follow the standard flow
- Use non-technical language, but have technical answers ready
- Emphasize both UX (Intelligence) and architecture (Snowflake-native)

---

## 🎬 Final Checklist

**Before you start:**
- [ ] Cells 1-17 pre-run successfully
- [ ] PDF uploaded to stage
- [ ] Warehouse running
- [ ] Snowflake Intelligence UI tab open
- [ ] Timer set for 30 minutes
- [ ] Water nearby (you'll be talking a lot!)

**Good luck! You've got this! 🚀**

