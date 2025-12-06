"""
Clinical Protocol Q&A - Streamlit in Snowflake App

This app provides intelligent search over clinical protocol PDFs with precise citations.

Features:
- Semantic search powered by Snowflake Cortex Search
- Precise citations with page number and position (e.g., "Page 5, top-right")
- Document browser and metadata
- Search history
- Export results

Requirements:
- Run setup.sql first to create all database objects
- Upload PDFs to @PDF_STAGE and run process_new_pdfs()
"""

import streamlit as st
import pandas as pd
import json
from snowflake.snowpark.context import get_active_session

# ============================================================================
# Configuration
# ============================================================================

st.set_page_config(
    page_title="Clinical Protocol Q&A",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get Snowpark session
session = get_active_session()

# Set context
session.sql("USE SCHEMA SANDBOX.PDF_OCR").collect()

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
    Search protocol documents using Cortex Search.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        doc_filter: Optional document name filter
    
    Returns:
        List of search results with citations
    """
    # Build filter clause if document filter is provided
    filter_clause = ""
    if doc_filter:
        filter_clause = f', "filter": {{"@eq": {{"doc_name": "{doc_filter}"}}}}'
    
    # Execute Cortex Search
    search_sql = f"""
        SELECT 
            result.chunk_id,
            result.doc_name,
            result.page,
            result.text,
            result.bbox_x0,
            result.bbox_y0,
            result.bbox_x1,
            result.bbox_y1,
            result.page_width,
            result.page_height
        FROM TABLE(
            SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
                'SANDBOX.PDF_OCR.protocol_search',
                '{{
                    "query": "{query}",
                    "columns": ["chunk_id", "doc_name", "page", "text", "bbox_x0", "bbox_y0", "bbox_x1", "bbox_y1", "page_width", "page_height"],
                    "limit": {max_results}
                    {filter_clause}
                }}'
            )
        ) AS result
    """
    
    results = session.sql(search_sql).collect()
    
    # Format results with positions
    formatted_results = []
    for row in results:
        position = calculate_position_python(
            row['BBOX_X0'], row['BBOX_Y0'], row['BBOX_X1'], row['BBOX_Y1'],
            row['PAGE_WIDTH'], row['PAGE_HEIGHT']
        )
        
        formatted_results.append({
            'chunk_id': row['CHUNK_ID'],
            'doc_name': row['DOC_NAME'],
            'page': row['PAGE'],
            'position': position,
            'text': row['TEXT'],
            'bbox': [row['BBOX_X0'], row['BBOX_Y0'], row['BBOX_X1'], row['BBOX_Y1']]
        })
    
    return formatted_results


def get_available_documents():
    """Get list of available protocol documents with metadata."""
    sql = """
        SELECT 
            doc_name,
            MAX(page) as total_pages,
            COUNT(*) as total_chunks,
            MIN(extracted_at) as first_extracted,
            MAX(extracted_at) as last_extracted
        FROM document_chunks
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
        FROM document_chunks
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


# ============================================================================
# Session State Initialization
# ============================================================================

if 'search_history' not in st.session_state:
    st.session_state.search_history = []

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
                results = search_protocols(query, max_results, doc_filter)
                
                # Add to search history
                st.session_state.search_history.insert(0, {
                    'query': query,
                    'results_count': len(results),
                    'doc_filter': selected_doc
                })
                
                # Display results
                if len(results) > 0:
                    st.success(f"Found {len(results)} relevant result(s)")
                    
                    # Display each result as a card
                    for i, result in enumerate(results, 1):
                        with st.container():
                            # Citation header
                            st.markdown(f"### 📌 Result {i}: {result['doc_name']}")
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
    - **Custom Python UDF**: Extracts text with bounding box coordinates using `pdfminer`
    - **Streamlit in Snowflake**: Interactive web interface
    - **Snowflake Native**: 100% within Snowflake, no external services
    
    ### 📚 How It Works
    
    1. **Upload PDFs** to `@PDF_STAGE`
    2. **Process with UDF** to extract text + positions
    3. **Index with Cortex Search** for semantic search
    4. **Query in this app** with natural language
    5. **Get precise citations** with page and position
    
    ### 🚀 Key Features
    
    - ✅ Semantic search (understands meaning, not just keywords)
    - ✅ Precise citations (page + position on page)
    - ✅ Full bounding box coordinates
    - ✅ Document filtering
    - ✅ Page browsing
    - ✅ Export results to CSV
    - ✅ Search history
    
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

