# 2026 – Project Portfolio

This repository is a portfolio of my data/analytics projects. Several projects were developed in collaborative/team environments, so this repo focuses on **my contributions, technical approach, and sample outputs** (when shareable).

---

## Projects

### 1) LLM nDCG (Candidate Ranking + Think-Budget Optimization)
**Goal:** Retrieve and rank the most appropriate candidates for a job description while using the **least “thinking budget”** (token usage), then evaluate ranking quality with **nDCG@K**.

**What I did (technical)**
- Used company-provided API credentials to connect to a **MongoDB** candidate database (credentials/data not included)
- Ran multiple LLM configurations (different think-budget / reasoning settings) and logged token usage
- Computed **nDCG@K** to compare ranking quality across configurations
- Produced summary artifacts to visualize **quality vs. cost/latency** tradeoffs

**Sample outputs**
- nDCG summary report/table (per run/config)
- Thinking-budget summary (tokens/cost/latency per run/config)

---

### 2) Auto Agenda (Sales + Influencer Performance Report → Word)
**Goal:** Generate a shareable stakeholder report that summarizes **sales performance** and **video engagement**, and compares a selected time window to the prior window.

**What I did (technical)**
- Built the initial **Word (.docx) report template** (sections + tables)
- Implemented **two-timeline comparison** in Python/Jupyter: input a start/end date and produce a summary for the current window vs. the immediately preceding window of equal length
- Implemented ~50% of the KPI matrix/table generation (team project; remaining components were built by collaborators)

**Sample outputs**
- Completed Word report (`.docx`) with populated tables and filled metrics

---

### 3) Category Clean (Cosine Similarity Category Mapping)
**Goal:** Clean and standardize unstructured merchandise category fields in a master dataset (13,000+ rows) by mapping them to TikTok’s current **main** and **detailed** category taxonomy.

**What I did (technical)**
- Built a Jupyter/Python workflow to normalize category text (cleaning + standardization)
- Implemented **cosine similarity** matching to map messy categories to the closest TikTok taxonomy labels
- Produced a clean output that can be merged back into the masterpool dataset
- Added basic guardrails (e.g., skipping/flagging low-confidence matches)

**Sample outputs**
- Excel output with matched main/detailed categories
- Combined/merged version back into the masterpool dataset

---

### 4) Web Automation / Data Collection for Research (Selenium)
**Goal:** Practice browser automation and structured data extraction from search result pages for research/analysis.

**What I did (technical)**
- Built Python **Selenium** automation to:
  - search by keyword
  - paginate across result pages
  - parse visible fields (e.g., name, title/headline) from page content
- Implemented waits/timeouts for more stable scraping and exported structured outputs (CSV/JSON)

**Ethical / compliance note**
This project is for learning and research purposes. It should only be used in ways that comply with website terms of service and applicable laws, and should avoid collecting private data.

---

## Tools / Skills
Python, SQL, pandas, Jupyter, MongoDB, **LLMs (API-based integration + prompt workflows)**, evaluation metrics (nDCG), cosine similarity, Selenium, reporting automation (Word export)

---

## Contact
LinkedIn: https://www.linkedin.com/in/chen-xie-8640612b5/
