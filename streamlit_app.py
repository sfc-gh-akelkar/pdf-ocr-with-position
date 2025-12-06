"""
Clinical Protocol Q&A - Streamlit in Snowflake App

This app provides intelligent search over clinical protocol PDFs with AI-powered
answer synthesis and precise citations.

Features:
- AI Answer Synthesis using Snowflake Cortex AI Complete (RAG pattern)
- Multiple LLM models: Claude 4 Sonnet, Claude 3.7/3.5 Sonnet, Llama 4 Maverick, Llama 3.1 (405B, 70B, 8B)
- Semantic search powered by Snowflake Cortex Search (using Core API)
- Precise citations with page number and position (e.g., "Page 5, top-right")
- Document browser and metadata
- Presigned URLs to view source PDFs
- Search history
- Export results
- Debug mode for raw Cortex Search responses

Technical Implementation:
- RAG Pattern: Retrieval (Cortex Search) → Augmentation (Build Prompt) → Generation (AI Complete)
- Uses Snowflake Core API (snowflake.core.Root) for type-safe Cortex Search access
- SNOWFLAKE.CORTEX.AI_COMPLETE for LLM answer synthesis
- Python dict filters instead of JSON string manipulation
- Returns structured JSON responses for better error handling
- Presigned URLs for secure document access

Requirements:
- Run setup.sql first to create all database objects
- Upload PDFs to @PDF_STAGE and run process_new_pdfs()
"""

import streamlit as st
import pandas as pd
import json
from snowflake.snowpark.context import get_active_session
from snowflake.core import Root

# ============================================================================
# Configuration
# ============================================================================

# IMPORTANT: Update these constants if you use different database/schema names
DATABASE_NAME = "SANDBOX"
SCHEMA_NAME = "PDF_OCR"

st.set_page_config(
    page_title="Clinical Protocol Q&A",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get Snowpark session
session = get_active_session()

# Initialize Snowflake Core API root
root = Root(session)

# Get Cortex Search service handle using Core API (cleaner than SQL approach)
cortex_search_service = root.databases[DATABASE_NAME].schemas[SCHEMA_NAME].cortex_search_services["protocol_search"]

# Note: Streamlit in Snowflake doesn't support USE SCHEMA statements
# All queries use fully qualified names: DATABASE.SCHEMA.OBJECT
# To use different database/schema, update the constants above

# ============================================================================
# Helper Functions
# ============================================================================

def calculate_position_python(bbox_x0, bbox_y0, bbox_x1, bbox_y1, page_width, page_height):
    """
    Calculate human-readable position from bounding box coordinates.
    Pure Python version of the SQL function.
    """
    # Calculate center points
    center_x = (bbox_x0 + bbox_x1) / 2
    center_y = (bbox_y0 + bbox_y1) / 2
    
    # Calculate relative positions (0-1)
    rel_x = center_x / page_width
    rel_y = center_y / page_height
    
    # Determine vertical position (PDF coords: 0 at bottom)
    if rel_y > 0.67:
        vertical = "top"
    elif rel_y < 0.33:
        vertical = "bottom"
    else:
        vertical = "middle"
    
    # Determine horizontal position
    if rel_x < 0.33:
        horizontal = "left"
    elif rel_x > 0.67:
        horizontal = "right"
    else:
        horizontal = "center"
    
    return f"{vertical}-{horizontal}"


def search_protocols(query, max_results=10, doc_filter=None):
    """
    Search protocol documents using Cortex Search with Snowflake Core API.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        doc_filter: Optional document name filter
    
    Returns:
        Tuple of (formatted_results, raw_response_json)
    """
    # Define columns to retrieve from Cortex Search
    columns = [
        "chunk_id",
        "doc_name", 
        "page",
        "text",
        "bbox_x0",
        "bbox_y0",
        "bbox_x1",
        "bbox_y1",
        "page_width",
        "page_height"
    ]
    
    # Execute Cortex Search using Core API (cleaner than SQL approach)
    if doc_filter:
        # Search with document filter
        filter_obj = {"@eq": {"doc_name": doc_filter}}
        response = cortex_search_service.search(
            query=query,
            columns=columns,
            filter=filter_obj,
            limit=max_results
        )
    else:
        # Search without filter
        response = cortex_search_service.search(
            query=query,
            columns=columns,
            limit=max_results
        )
    
    # Parse response JSON
    results_json = response.json()
    
    # Format results with positions
    formatted_results = []
    for result in results_json.get('results', []):
        position = calculate_position_python(
            result['bbox_x0'],
            result['bbox_y0'],
            result['bbox_x1'],
            result['bbox_y1'],
            result['page_width'],
            result['page_height']
        )
        
        formatted_results.append({
            'chunk_id': result['chunk_id'],
            'doc_name': result['doc_name'],
            'page': result['page'],
            'position': position,
            'text': result['text'],
            'bbox': [
                result['bbox_x0'],
                result['bbox_y0'],
                result['bbox_x1'],
                result['bbox_y1']
            ]
        })
    
    return formatted_results, results_json


def get_available_documents():
    """Get list of available protocol documents with metadata."""
    sql = """
        SELECT 
            doc_name,
            MAX(page) as total_pages,
            COUNT(*) as total_chunks,
            MIN(extracted_at) as first_extracted,
            MAX(extracted_at) as last_extracted
        FROM SANDBOX.PDF_OCR.document_chunks
        GROUP BY doc_name
        ORDER BY doc_name
    """
    return session.sql(sql).to_pandas()


def get_page_content(doc_name, page_num):
    """Get all text chunks from a specific page."""
    sql = f"""
        SELECT 
            text,
            bbox_x0, bbox_y0, bbox_x1, bbox_y1,
            page_width, page_height
        FROM SANDBOX.PDF_OCR.document_chunks
        WHERE doc_name = '{doc_name}'
          AND page = {page_num}
        ORDER BY bbox_y0 DESC, bbox_x0
    """
    results = session.sql(sql).collect()
    
    # Add positions
    page_content = []
    for row in results:
        position = calculate_position_python(
            row['BBOX_X0'], row['BBOX_Y0'], row['BBOX_X1'], row['BBOX_Y1'],
            row['PAGE_WIDTH'], row['PAGE_HEIGHT']
        )
        page_content.append({
            'text': row['TEXT'],
            'position': position,
            'bbox': [row['BBOX_X0'], row['BBOX_Y0'], row['BBOX_X1'], row['BBOX_Y1']]
        })
    
    return page_content


def get_presigned_url(doc_name, expiration_seconds=360):
    """
    Get a presigned URL to view/download the source PDF.
    
    Args:
        doc_name: Document filename in the stage
        expiration_seconds: URL validity duration (default 6 minutes)
    
    Returns:
        Presigned URL string or None if error
    """
    try:
        sql = f"""
            SELECT GET_PRESIGNED_URL(
                @{DATABASE_NAME}.{SCHEMA_NAME}.PDF_STAGE,
                '{doc_name}',
                {expiration_seconds}
            ) AS URL
        """
        result = session.sql(sql).collect()
        return result[0]['URL'] if result else None
    except Exception as e:
        st.error(f"Error generating presigned URL: {str(e)}")
        return None


def _display_result_card(result_num, result):
    """Helper function to display a search result card."""
    with st.container():
        # Citation header
        st.markdown(f"### 📌 Result {result_num}: {result['doc_name']}")
        st.caption(f"**Page {result['page']} ({result['position']})**")
        
        # Text content
        st.markdown(f"> {result['text']}")
        
        # Expandable details
        with st.expander("🔍 Details"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**Chunk ID:** `{result['chunk_id']}`")
                st.write(f"**Position:** {result['position']}")
            with col_b:
                st.write(f"**Bounding Box:**")
                st.code(f"[{', '.join([f'{x:.1f}' for x in result['bbox']])}]")
        
        st.divider()


def synthesize_answer_with_llm(question, search_results, model_name='claude-3-5-sonnet'):
    """
    Use Snowflake Cortex AI Complete to synthesize a natural language answer
    from search results (RAG pattern).
    
    Args:
        question: User's question
        search_results: List of search results from Cortex Search
        model_name: LLM model to use for synthesis (claude-4-sonnet, llama3.1-70b, etc.)
    
    Returns:
        Tuple of (synthesized_answer, source_citations)
    """
    # Build context from search results
    context_chunks = []
    citations = []
    
    for i, result in enumerate(search_results, 1):
        chunk_text = f"[Source {i}] Document: {result['doc_name']}, Page {result['page']} ({result['position']})\n{result['text']}"
        context_chunks.append(chunk_text)
        citations.append({
            'source_num': i,
            'doc_name': result['doc_name'],
            'page': result['page'],
            'position': result['position'],
            'bbox': result['bbox'],  # Include bounding box coordinates
            'text': result['text'][:200] + '...' if len(result['text']) > 200 else result['text']
        })
    
    context = "\n\n".join(context_chunks)
    
    # Build prompt following best practices from Snowflake guide
    prompt = f"""You are an expert clinical protocol assistant that extracts information from the CONTEXT provided
between <context> and </context> tags.

When answering the question between <question> and </question> tags:
- Be concise and accurate
- Do NOT hallucinate or make up information
- If you don't have the information in the CONTEXT, clearly say so
- Only answer based on information in the CONTEXT
- Always cite your sources using the [Source N] references
- Mention the document name, page, and position when citing

Do not mention "the CONTEXT" in your answer - write naturally as if you're an expert.

<context>
{context}
</context>

<question>
{question}
</question>

Answer:"""
    
    # Call Cortex AI Complete
    try:
        sql = """
            SELECT SNOWFLAKE.CORTEX.AI_COMPLETE(?, ?) AS response
        """
        result = session.sql(sql, params=[model_name, prompt]).collect()
        
        if result:
            answer = result[0]['RESPONSE']
            return answer, citations
        else:
            return "Error: No response from LLM", citations
            
    except Exception as e:
        return f"Error synthesizing answer: {str(e)}", citations


# ============================================================================
# Session State Initialization
# ============================================================================

if 'search_history' not in st.session_state:
    st.session_state.search_history = []

if 'show_debug' not in st.session_state:
    st.session_state.show_debug = False

if 'use_llm_synthesis' not in st.session_state:
    st.session_state.use_llm_synthesis = True

if 'selected_model' not in st.session_state:
    st.session_state.selected_model = 'claude-3-5-sonnet'

# ============================================================================
# Sidebar - Document Browser
# ============================================================================

st.sidebar.title("📚 Document Browser")

# Get available documents
try:
    docs_df = get_available_documents()
    
    if len(docs_df) > 0:
        st.sidebar.success(f"📄 {len(docs_df)} document(s) available")
        
        # Document selector
        selected_doc = st.sidebar.selectbox(
            "Select a document:",
            options=['All Documents'] + docs_df['DOC_NAME'].tolist()
        )
        
        # Show metadata for selected document
        if selected_doc != 'All Documents':
            doc_info = docs_df[docs_df['DOC_NAME'] == selected_doc].iloc[0]
            st.sidebar.metric("Total Pages", doc_info['TOTAL_PAGES'])
            st.sidebar.metric("Text Chunks", doc_info['TOTAL_CHUNKS'])
            st.sidebar.caption(f"Processed: {doc_info['FIRST_EXTRACTED']}")
        
        st.sidebar.divider()
        
        # Document details expander
        with st.sidebar.expander("📊 All Documents"):
            st.dataframe(
                docs_df[['DOC_NAME', 'TOTAL_PAGES', 'TOTAL_CHUNKS']],
                hide_index=True,
                use_container_width=True
            )
        
        # LLM Settings
        st.sidebar.divider()
        st.sidebar.subheader("🤖 AI Settings")
        
        st.session_state.use_llm_synthesis = st.sidebar.checkbox(
            '✨ Use AI Answer Synthesis',
            value=st.session_state.use_llm_synthesis,
            help="Use LLM to generate natural language answers from search results (RAG pattern)"
        )
        
        if st.session_state.use_llm_synthesis:
            st.session_state.selected_model = st.sidebar.selectbox(
                'Select LLM Model:',
                options=[
                    'claude-4-sonnet',
                    'claude-3-7-sonnet',
                    'claude-3-5-sonnet',
                    'llama4-maverick',
                    'llama3.3-70b',
                    'llama3.1-405b',
                    'llama3.1-70b',
                    'llama3.1-8b',
                    'llama3-70b',
                    'llama3-8b'
                ],
                index=2,  # Default to claude-3-5-sonnet
                help="Model for answer synthesis"
            )
        
        # Debug toggle
        st.sidebar.divider()
        st.session_state.show_debug = st.sidebar.checkbox(
            '🔧 Show Debug Info',
            value=st.session_state.show_debug,
            help="Display raw Cortex Search response JSON"
        )
    else:
        st.sidebar.warning("⚠️ No documents found")
        st.sidebar.info("Upload PDFs to @PDF_STAGE and run:\n```sql\nCALL process_new_pdfs();\n```")
        selected_doc = 'All Documents'

except Exception as e:
    st.sidebar.error(f"Error loading documents: {str(e)}")
    selected_doc = 'All Documents'

# ============================================================================
# Main Content - Search Interface
# ============================================================================

st.title("🔍 Clinical Protocol Q&A")
st.markdown("Ask questions about your clinical protocols and get answers with **precise citations**.")

# Search input
col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input(
        "Ask a question:",
        placeholder="e.g., What is the dosing schedule? What are the inclusion criteria?",
        label_visibility="collapsed"
    )
with col2:
    max_results = st.number_input("Results", min_value=1, max_value=20, value=5, label_visibility="collapsed")

# Search button
if st.button("Search", type="primary", use_container_width=True) or query:
    if query:
        with st.spinner("Searching protocols..."):
            try:
                # Filter by selected document if not "All Documents"
                doc_filter = None if selected_doc == 'All Documents' else selected_doc
                
                # Execute search
                results, raw_response = search_protocols(query, max_results, doc_filter)
                
                # Show debug info if enabled
                if st.session_state.show_debug:
                    with st.sidebar.expander("🔍 Raw Cortex Search Response", expanded=False):
                        st.json(raw_response)
                
                # Add to search history
                st.session_state.search_history.insert(0, {
                    'query': query,
                    'results_count': len(results),
                    'doc_filter': selected_doc
                })
                
                # Display results
                if len(results) > 0:
                    st.success(f"Found {len(results)} relevant result(s)")
                    
                    # Show source documents in sidebar
                    unique_docs = list(set(r['doc_name'] for r in results))
                    if len(unique_docs) > 0:
                        with st.sidebar.expander("📄 Source Documents", expanded=True):
                            for doc in unique_docs:
                                presigned_url = get_presigned_url(doc)
                                if presigned_url:
                                    st.markdown(f"[📎 View {doc}]({presigned_url})")
                                else:
                                    st.text(f"📎 {doc}")
                    
                    # LLM-Synthesized Answer (if enabled)
                    if st.session_state.use_llm_synthesis:
                        st.divider()
                        st.subheader("💬 AI-Generated Answer")
                        
                        with st.spinner(f"Generating answer with {st.session_state.selected_model}..."):
                            answer, citations = synthesize_answer_with_llm(
                                query, 
                                results[:5],  # Use top 5 results for context
                                st.session_state.selected_model
                            )
                        
                        # Display the synthesized answer
                        st.markdown(f"**Answer:** {answer}")
                        
                        st.caption("💡 **Precise citations below** - Each source includes page, position, and exact bounding box coordinates for audit-grade traceability.")
                        
                        # Show citations with coordinates
                        with st.expander("📚 Sources Used (with exact coordinates)", expanded=True):
                            for cite in citations:
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.markdown(
                                        f"**[Source {cite['source_num']}]** {cite['doc_name']}, "
                                        f"Page {cite['page']} ({cite['position']})"
                                    )
                                    st.caption(cite['text'])
                                with col2:
                                    st.caption("**Bounding Box:**")
                                    bbox_str = f"[{cite['bbox'][0]:.1f}, {cite['bbox'][1]:.1f}, {cite['bbox'][2]:.1f}, {cite['bbox'][3]:.1f}]"
                                    st.code(bbox_str, language=None)
                                st.divider()
                        
                        st.divider()
                        st.caption("💡 Toggle 'Use AI Answer Synthesis' in the sidebar to see raw search results")
                    
                    # Raw Search Results
                    else:
                        st.subheader("🔍 Search Results")
                    
                    # Display each result as a card (show if no LLM synthesis, or in expander if LLM synthesis)
                    if st.session_state.use_llm_synthesis:
                        with st.expander("📄 View All Search Results", expanded=False):
                            for i, result in enumerate(results, 1):
                                _display_result_card(i, result)
                    else:
                        for i, result in enumerate(results, 1):
                            _display_result_card(i, result)
                    
                    # Export option
                    if st.button("📥 Export Results to CSV"):
                        export_df = pd.DataFrame([
                            {
                                'Query': query,
                                'Document': r['doc_name'],
                                'Page': r['page'],
                                'Position': r['position'],
                                'Text': r['text'],
                                'Chunk_ID': r['chunk_id']
                            }
                            for r in results
                        ])
                        csv = export_df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"protocol_search_{query[:20]}.csv",
                            mime="text/csv"
                        )
                
                else:
                    st.warning("No results found. Try a different query or select 'All Documents'.")
                    st.info("💡 **Tip:** Try broader terms or check if documents have been processed.")
            
            except Exception as e:
                st.error(f"Search error: {str(e)}")
                st.code(str(e))
    else:
        st.info("👆 Enter a question above to search")

# ============================================================================
# Additional Features Tabs
# ============================================================================

st.divider()

tab1, tab2, tab3 = st.tabs(["📖 Browse by Page", "🕒 Search History", "ℹ️ About"])

with tab1:
    st.subheader("Browse Document by Page")
    
    if selected_doc != 'All Documents':
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            page_num = st.number_input(
                "Page number:",
                min_value=1,
                max_value=int(docs_df[docs_df['DOC_NAME'] == selected_doc]['TOTAL_PAGES'].iloc[0]),
                value=1
            )
        with col_p2:
            if st.button("Load Page", use_container_width=True):
                try:
                    page_content = get_page_content(selected_doc, page_num)
                    
                    st.success(f"Page {page_num} - {len(page_content)} text chunk(s)")
                    
                    for chunk in page_content:
                        with st.expander(f"📍 {chunk['position']} - {chunk['text'][:50]}..."):
                            st.write(chunk['text'])
                            st.caption(f"Position: {chunk['position']}")
                
                except Exception as e:
                    st.error(f"Error loading page: {str(e)}")
    else:
        st.info("Select a specific document from the sidebar to browse by page.")

with tab2:
    st.subheader("Recent Searches")
    
    if st.session_state.search_history:
        for i, search in enumerate(st.session_state.search_history[:10], 1):
            st.write(f"{i}. **\"{search['query']}\"** ({search['results_count']} results) - *{search['doc_filter']}*")
        
        if st.button("Clear History"):
            st.session_state.search_history = []
            st.rerun()
    else:
        st.info("No search history yet. Start searching to see your queries here.")

with tab3:
    st.subheader("About This Application")
    
    st.markdown("""
    ### 🎯 What This Does
    
    This application provides **intelligent search** over clinical protocol PDFs with 
    **audit-grade precision**. Every answer includes:
    
    - 📄 **Document name**
    - 📍 **Page number**
    - 🎯 **Position on page** (e.g., "top-right", "middle-center")
    - 📦 **Bounding box coordinates** for exact location
    
    ### 🔧 Technology Stack
    
    - **Snowflake Cortex Search**: Semantic search with automatic embeddings
    - **Snowflake Cortex AI Complete**: LLM-powered answer synthesis (RAG pattern)
    - **Claude & Llama Models**: claude-4-sonnet, llama3.1-405b, llama4-maverick, and more
    - **Custom Python UDF**: Extracts text with bounding box coordinates using `pdfminer`
    - **Streamlit in Snowflake**: Interactive web interface
    - **Snowflake Core API**: Modern, type-safe Python API
    - **Snowflake Native**: 100% within Snowflake, no external services
    
    ### 📚 How It Works (RAG Pattern)
    
    1. **Upload PDFs** to `@PDF_STAGE`
    2. **Process with UDF** to extract text + positions
    3. **Index with Cortex Search** for semantic search
    4. **User asks a question** in natural language
    5. **Cortex Search retrieves** relevant chunks with citations
    6. **LLM synthesizes** natural language answer (if enabled)
    7. **Display answer + sources** with page and position
    
    ### 🤖 Two Modes
    
    **AI Answer Synthesis (Default):**
    - LLM reads search results and generates a natural language answer
    - Similar to ChatGPT, but with **exact citations**
    - Uses Snowflake Cortex AI Complete with Claude 4 Sonnet (default) or Llama models
    - Choose from: claude-4-sonnet, claude-3-7-sonnet, llama4-maverick, llama3.1-405b, and more
    - Best for: Quick answers to specific questions
    
    **Raw Search Results:**
    - Shows individual text chunks ranked by relevance
    - Good for: Exploring what's in documents, detailed research
    - Toggle in sidebar: Turn off "Use AI Answer Synthesis"
    
    ### 🚀 Key Features
    
    - ✅ **AI Answer Synthesis** - Natural language answers using LLM (RAG pattern)
    - ✅ **Semantic search** - Understands meaning, not just keywords
    - ✅ **Precise citations** - Page + position + bounding box coordinates
    - ✅ **Multiple LLM models** - Claude 4 Sonnet, Claude 3.7 Sonnet, Llama 4 Maverick, Llama 3.1 (405B, 70B, 8B)
    - ✅ **Presigned URLs** - Click to view source PDFs
    - ✅ **Document filtering** - Search specific documents
    - ✅ **Page browsing** - View content by page
    - ✅ **Export to CSV** - Download results
    - ✅ **Debug mode** - View raw Cortex Search responses
    - ✅ **Search history** - Track previous queries
    
    ### 📖 Setup Instructions
    
    1. Run `setup.sql` to create database objects
    2. Upload PDFs to `@PDF_STAGE`
    3. Run `CALL process_new_pdfs();` to index documents
    4. Start searching!
    
    ---
    
    **Need help?** Check the sidebar for available documents and metadata.
    """)

# ============================================================================
# Footer
# ============================================================================

st.divider()
st.caption("Powered by Snowflake Cortex Search | Built with Streamlit in Snowflake")

