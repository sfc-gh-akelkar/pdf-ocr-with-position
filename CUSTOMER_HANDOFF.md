# Customer Handoff Checklist

This document outlines the steps to make this repository customer-ready.

## ✅ Completed Items

### Documentation
- [x] Professional README.md with overview and architecture
- [x] DEPLOYMENT.md with step-by-step setup guide
- [x] DEMO-GUIDE.md for 15-minute presentations
- [x] SAMPLE_DATA.md for getting test PDFs
- [x] LICENSE file (MIT License)
- [x] .gitignore to exclude sensitive files

### Configuration
- [x] config.example.py template created
- [x] Database names documented for customization
- [x] All hardcoded values identified

## ⚠️ Action Items Before Sharing

### 1. Remove Sensitive Files
```bash
# Remove actual PDF files (keep example paths in documentation)
git rm *.pdf

# Remove any customer-specific data
git rm -r customer_data/ (if exists)
```

### 2. Update Hardcoded Values

**Files to update:**

**`streamlit_app.py` (lines 42-43):**
```python
# BEFORE:
DATABASE_NAME = "SANDBOX"
SCHEMA_NAME = "PDF_OCR"

# AFTER - Option 1 (Recommended):
try:
    from config import DATABASE_NAME, SCHEMA_NAME
except ImportError:
    DATABASE_NAME = "YOUR_DATABASE"
    SCHEMA_NAME = "YOUR_SCHEMA"
    st.error("Please create config.py from config.example.py")

# AFTER - Option 2 (Simpler):
DATABASE_NAME = "YOUR_DATABASE"  # Customer updates this
SCHEMA_NAME = "YOUR_SCHEMA"      # Customer updates this
```

**`setup.sql` (lines 27-32):**
```sql
-- BEFORE:
CREATE SCHEMA IF NOT EXISTS SANDBOX.PDF_OCR;
USE DATABASE SANDBOX;
USE SCHEMA PDF_OCR;

-- AFTER:
-- UPDATE THESE VALUES FOR YOUR ENVIRONMENT:
CREATE SCHEMA IF NOT EXISTS YOUR_DATABASE.YOUR_SCHEMA;
USE DATABASE YOUR_DATABASE;
USE SCHEMA YOUR_SCHEMA;
```

### 3. Add Placeholder Files

Create a `docs/` folder for screenshots:
```bash
mkdir -p docs
# Add placeholder images or links to where screenshots should go
```

### 4. Review and Clean

**Check for:**
- [ ] No passwords or credentials in code
- [ ] No internal Snowflake account IDs
- [ ] No customer-specific data or file names
- [ ] No TODO comments that reference internal items
- [ ] No debug/test code that's not production-ready

**Search for common issues:**
```bash
# Search for potential secrets
grep -r "password" .
grep -r "secret" .
grep -r "token" .
grep -r "api_key" .

# Search for internal references
grep -r "internal" .
grep -r "TODO.*internal" .
```

### 5. Test Clean Install

**In a fresh environment:**
1. Clone the repository
2. Follow DEPLOYMENT.md exactly
3. Verify all steps work without assuming prior knowledge
4. Note any missing instructions or assumptions

### 6. Final Repository Hygiene

```bash
# Ensure .gitignore is working
git status  # Should not show config.py or *.pdf

# Create clean commit history (optional)
# Consider squashing old commits if they contain sensitive data

# Add git tags for versioning
git tag -a v1.0.0 -m "Initial customer release"
git push --tags
```

### 7. Create GitHub/GitLab Repository

**Repository settings:**
- [ ] Set visibility: Public or Private (customer decision)
- [ ] Add description: "AI-powered clinical protocol search with Snowflake Cortex"
- [ ] Add topics/tags: snowflake, cortex, ai, clinical-trials, document-intelligence
- [ ] Enable Issues for support
- [ ] Add README as repository description
- [ ] Set up branch protection for `main`

### 8. Optional Enhancements

**Consider adding:**
- [ ] GitHub Actions for automated testing
- [ ] SECURITY.md for vulnerability reporting
- [ ] CODE_OF_CONDUCT.md for community guidelines
- [ ] Wiki pages for extended documentation
- [ ] Example notebooks (.ipynb) for data scientists
- [ ] Docker container for local testing (if applicable)
- [ ] Terraform/IaC for automated deployment

## 📋 Pre-Delivery Checklist

Before sharing with customers:

- [ ] All PDFs removed from repository
- [ ] All hardcoded `SANDBOX` / `PDF_OCR` replaced with placeholders
- [ ] config.py is in .gitignore and not committed
- [ ] README.md tested and renders correctly on GitHub
- [ ] All links in documentation work
- [ ] LICENSE file is appropriate for your use case
- [ ] Copyright notices are accurate
- [ ] No internal Snowflake account identifiers
- [ ] All documentation reviewed for customer readiness
- [ ] DEPLOYMENT.md tested by someone unfamiliar with the code
- [ ] Demo queries in DEMO-GUIDE.md actually work

## 🎯 Customer Success Criteria

**Customers should be able to:**
1. ✅ Clone the repository
2. ✅ Understand the architecture from README
3. ✅ Deploy in <30 minutes using DEPLOYMENT.md
4. ✅ Upload their own PDFs
5. ✅ Get meaningful search results
6. ✅ Understand cost implications
7. ✅ Configure RBAC for their team
8. ✅ Modify for their use case

## 📞 Support Plan

**After handoff:**
- Provide a support contact (email/Slack)
- Specify response SLA (e.g., 24 hours for questions)
- Offer optional onboarding call
- Schedule a 30-day check-in

## 🚀 Launch Checklist

- [ ] Repository published (GitHub/GitLab)
- [ ] Customer notified with repository link
- [ ] Onboarding call scheduled (optional)
- [ ] Support channel established
- [ ] Success metrics defined
- [ ] Feedback loop established

---

**Ready to share?** Complete the checklist above, then send the repository link to your customer with the README.md as the starting point.

