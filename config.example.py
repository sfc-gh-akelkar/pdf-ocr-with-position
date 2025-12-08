# Configuration Template for Clinical Protocol Intelligence
# Copy this file to 'config.py' and update with your values

# Snowflake Database Configuration
# Update these to match your Snowflake environment
DATABASE_NAME = "YOUR_DATABASE"      # e.g., "PRODUCTION" or "SANDBOX"
SCHEMA_NAME = "YOUR_SCHEMA"          # e.g., "PDF_OCR" or "DOCUMENT_AI"

# Cortex Search Configuration
SEARCH_SERVICE_NAME = "protocol_search"
EMBEDDING_MODEL = "snowflake-arctic-embed-l-v2.0"

# Default LLM Configuration
DEFAULT_LLM_MODEL = "claude-4-sonnet"

# Application Settings
MAX_PDF_SIZE_MB = 50
DEFAULT_SEARCH_RESULTS = 5
MAX_SEARCH_RESULTS = 20

# Snowflake Compute
WAREHOUSE_NAME = "compute_wh"  # Update to your warehouse name

# Notes:
# - Ensure your Snowflake user has appropriate permissions
# - The warehouse should have AUTO_SUSPEND enabled for cost optimization
# - Cortex Search and AI services must be enabled in your account

