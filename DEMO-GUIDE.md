# Clinical Protocol Intelligence - 15-Minute Power Demo
## WOW the Customer: Multi-Document Intelligence with Audit-Grade Precision

---

## 📋 **Pre-Demo Setup Checklist**
- [x] **ALL 3 PDFs pre-loaded and processed:**
  - Prot_000.pdf (Original protocol)
  - Prot_000_Secukinumab.pdf 
  - Prot_000_Ligelizumab.pdf
- [ ] Streamlit app running and tested
- [ ] Start with "All Documents" selected to showcase cross-document search
- [ ] Have Technical Deep Dive tab pre-opened in background browser tab
- [ ] Close all unnecessary tabs/windows for clean screen
- [ ] Set LLM model to **Claude 4 Sonnet** (highest quality)

---

## 🎬 **15-Minute Power Demo Script**

### **⏱️ SEGMENT 1: The Wow Moment (3 min)**

**🎤 Opening:**
*"In the next 15 minutes, I'm going to show you something that will fundamentally change how you work with clinical protocols. We have three protocols loaded here, and I'm going to show you AI-powered intelligence that finds, synthesizes, and cites information across all of them—with the audit-grade precision you need."*

**ACTION**: Show main interface with sidebar showing 3 documents

**🎤 Transition:**
*"Watch this. I'm going to ask a complex question across all three protocols."*

**DEMO**: Type: **"What are the dosing schedules?"**
- ⏱️ Wait for AI answer to appear (~3-5 seconds)
- **Don't talk while it's processing** - let the speed impress them

**🎤 After results appear:**
*"Notice what just happened. In 3 seconds:"*
- ✅ *"AI searched across all THREE protocols"*
- ✅ *"Found relevant sections using semantic understanding, not keywords"*
- ✅ *"Synthesized a coherent answer using Claude 4 Sonnet"*
- ✅ *"And gave me exact citations with coordinates for every claim"*

**ACTION**: Scroll to show AI answer, then expand "Sources Used"

**🎤 Highlight Citations:**
*"Look at the precision here: Page 31, top-center, coordinates [126.0, 706.3, 464.0, 722.3]. An auditor can go directly to this exact location and verify the source. That's audit-grade precision."*

**💡 Key Message:** Speed + Intelligence + Precision = Transformative

---

### **⏱️ SEGMENT 2: Cross-Document Intelligence (4 min)**

**🎤 Setup:**
*"Now let me show you the real power - comparing across multiple protocol versions. This is where teams typically spend hours doing manual comparison."*

**DEMO 1**: **"Compare the inclusion criteria across protocols"**

**ACTION**: Execute search, show AI synthesizing differences

**🎤 While results load:**
*"The AI is now reading through hundreds of pages across three documents, extracting inclusion criteria, and identifying variations. This would take a clinical team hours of manual work."*

**ACTION**: Show results with citations from multiple documents

**🎤 Point out:**
- Different document names in citations
- Consistent coordinate format
- AI identifying similarities AND differences

**DEMO 2**: **"What are the safety monitoring requirements?"**

**ACTION**: Execute search

**🎤 Highlight:**
*"Notice how it's pulling from different sections across documents - the AI understands semantic relationships. 'Safety monitoring' might be called 'adverse event tracking' or 'safety assessments' in different protocols, but the AI understands they're related."*

**ACTION**: Click through to show different source documents in citations

**💡 Key Message:** One query, three documents, comprehensive answer - automatically

---

### **⏱️ SEGMENT 3: Document Filtering & Precision (2 min)**

**🎤 Transition:**
*"Now let's focus on a specific protocol version."*

**ACTION**: Select **Prot_000_Secukinumab.pdf** from sidebar dropdown

**DEMO**: **"What are the exclusion criteria?"**

**🎤 Point out:**
*"Now it's only searching this specific version. Notice the results are still precise, still coordinate-tracked, but scoped to exactly what you asked for."*

**ACTION**: Expand a citation to show bounding box coordinates

**🎤 Deep dive on one citation:**
*"Let me show you what makes this regulatory-ready. This citation shows:"*
- 📄 *"Document name: Prot_000_Secukinumab.pdf"*
- 📍 *"Page 45, middle-left"*
- 🎯 *"Exact coordinates: [x0, y0, x1, y1]"*
- 📝 *"Source text preview for verification"*

*"You can feed these coordinates to downstream systems, create automated verification tools, or simply hand them to an auditor. The precision is there."*

**💡 Key Message:** Precision at scale - every claim is verifiable

---

### **⏱️ SEGMENT 4: Technical Architecture Showcase (3 min)**

**🎤 Transition:**
*"Let me show you what makes this possible - and why it's different from other AI solutions."*

**ACTION**: Click **Technical Deep Dive** tab

**🎤 Architecture Overview:**
*"This is 100% Snowflake-native. Every component runs inside your Snowflake environment:"*

**SHOW**: Architecture diagram section

**Key Points (rapid fire):**
1. **PDF Processing**:
   - *"PDFs uploaded to Snowflake stage - internal storage"*
   - *"Python UDF extracts text with pdfminer - runs in Snowflake"*
   - *"Bounding boxes captured at extraction time"*

2. **Search & Indexing**:
   - *"Cortex Search Service - Snowflake's semantic search"*
   - *"Auto-embedding with Arctic model"*
   - *"Real-time indexing, no external services"*

3. **AI Synthesis**:
   - *"Cortex AI Complete - Snowflake's LLM service"*
   - *"Multiple models: Claude, Llama, GPT, Mistral"*
   - *"RAG pattern: Retrieval → Augmentation → Generation"*

**ACTION**: Scroll to Performance Metrics

**🎤 Show Metrics:**
*"Real-time performance monitoring. You can see:"*
- Number of searches this session
- Average response time
- LLM calls and token usage
- **Estimated cost** (if metrics available)

*"Full transparency, full observability, full control."*

**💡 Key Message:** Enterprise-grade architecture, not a black box

---

### **⏱️ SEGMENT 5: Document Upload & Scale (1 min)**

**🎤 Quick mention (don't demo):**
*"Adding new documents is straightforward - there's a file uploader in the sidebar."*

**ACTION**: Point to upload section in sidebar (don't click)

**🎤 Talking points:**
- *"Supports up to 50MB PDFs"*
- *"Automatic text extraction and coordinate capture"*
- *"Search index builds in background (~30 seconds)"*
- *"Three-step process: Upload → Extract → Index"*

*"We have three protocols loaded here, but you could have 30, 300, or 3,000. Cortex Search scales with Snowflake's serverless infrastructure."*

**💡 Key Message:** Easy to expand, scales infinitely

---

### **⏱️ SEGMENT 6: Live Q&A + Model Selection (2 min)**

**🎤 Engage audience:**
*"Give me a question - anything about these protocols - and I'll show you the system in action."*

**[If audience provides question]:**
- Execute search
- Highlight answer quality
- Show citations
- Verify one source

**[If no question from audience]:**

**DEMO**: **"What biomarkers are measured in these studies?"**

**THEN**: Switch models mid-demo

**ACTION**: 
1. Show result with Claude 4 Sonnet
2. Switch to **Llama 3.3 70B** in sidebar
3. Re-run same query

**🎤 Compare:**
*"Same question, different AI model. You can choose based on:"*
- ✅ *Quality vs speed*
- ✅ *Cost considerations*
- ✅ *Specific model strengths*

*"Claude 4 is our default for highest quality, but you have 10 models to choose from."*

**💡 Key Message:** Flexible, configurable, customizable

---

## 🎯 **Closing Power Statement (30 sec)**

**🎤 Final words:**
*"In 15 minutes, you've seen:"*

1. **Speed**: *Seconds instead of hours*
2. **Intelligence**: *AI that understands context, not just keywords*
3. **Precision**: *Audit-grade citations with exact coordinates*
4. **Scale**: *Search across multiple documents simultaneously*
5. **Architecture**: *100% Snowflake-native, enterprise-ready*

*"This isn't a prototype. This is production-ready AI for clinical protocol intelligence, running entirely within your Snowflake environment with full governance, security, and compliance."*

**Next Steps:**
- Hands-on session with YOUR protocols
- Technical architecture deep dive with your IT team
- ROI analysis and pilot program design

**🎤 Final ask:**
*"Questions?"*

---

## 🎯 **Suggested Demo Queries (Pre-tested)**

Use these if you need guaranteed good results:

### **Cross-Document Queries:**
1. "What are the dosing schedules?"
2. "Compare the inclusion criteria across protocols"
3. "What are the safety monitoring requirements?"
4. "What adverse events are tracked?"

### **Single-Document Queries:**
(Select specific document first)
1. "What are the exclusion criteria?"
2. "How long is the treatment period?"
3. "What is the primary endpoint?"
4. "What biomarkers are measured?"

### **Complex Queries:**
1. "What are the stopping rules?"
2. "How is response evaluated?"
3. "What are the contraindications?"
4. "Describe the study design"

---

## 🎯 **Timing Breakdown**

| Segment | Time | Key Deliverable |
|---------|------|----------------|
| 1. Wow Moment | 3 min | Speed + Intelligence impression |
| 2. Cross-Document | 4 min | Multi-doc search power |
| 3. Precision | 2 min | Citation quality |
| 4. Architecture | 3 min | Technical credibility |
| 5. Upload & Scale | 1 min | Expansion capability |
| 6. Live Q&A | 2 min | Interactivity + flexibility |
| **TOTAL** | **15 min** | Complete picture |

---

## 💡 **Key Differentiators to Emphasize**

### **vs. Manual Search:**
- ⚡ 100x faster
- 🎯 Never miss information
- 📊 Consistent results

### **vs. External AI Tools (ChatGPT, etc.):**
- 🔒 Data never leaves Snowflake
- 🎯 Audit-grade citations with coordinates
- ⚖️ Regulatory compliant
- 🏢 Enterprise governance

### **vs. Traditional Document Management:**
- 🧠 Semantic understanding
- 🔗 Cross-document intelligence
- 🤖 AI synthesis, not just retrieval

---

## 🚨 **Recovery Scripts**

### **If search is slow:**
*"As you can see, it's processing hundreds of pages in real-time. Still faster than manual review!"*

### **If results aren't perfect:**
*"Notice it still provides sources - you can always verify and refine. The goal is to accelerate your team, not replace human judgment."*

### **If technical questions get deep:**
*"Let me show you the Technical Deep Dive tab - we have full execution logs, performance metrics, and architecture details. We can schedule a dedicated technical session to go deeper."*

---

## 📸 **Screen Setup Checklist**

**Before demo starts:**
- [ ] Close unnecessary browser tabs
- [ ] Clear any test queries from search box
- [ ] Set sidebar to "All Documents"
- [ ] Verify AI synthesis is enabled
- [ ] Confirm Claude 4 Sonnet is selected
- [ ] Pre-open Technical Deep Dive in background tab (Cmd+T)
- [ ] Zoom browser to 110-125% for visibility
- [ ] Turn off notifications/Slack/email

---

## 🎯 **Success Metrics**

**You've nailed it if they say:**
- ✅ *"Can we try this with our documents?"*
- ✅ *"What's the timeline to get this running?"*
- ✅ *"Can you show our IT team the architecture?"*
- ✅ *"How much does this cost to run?"*

**Warning signs to address:**
- ⚠️ *"We already have [other tool]"* → Emphasize Snowflake-native advantage
- ⚠️ *"Is this production-ready?"* → Show Technical Deep Dive metrics
- ⚠️ *"How accurate is the AI?"* → Emphasize citations allow verification

---

**🚀 Remember: You're not selling technology, you're demonstrating transformation. Keep it fast, keep it impressive, keep it real!**
