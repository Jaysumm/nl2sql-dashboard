# NL2SQL Sales Dashboard

Ask questions about sales data in plain English — Claude converts the question
into SQL, runs it against a local database, and returns a table + auto-generated
chart. Built to explore how LLMs can automate the "write a quick SQL query"
step of everyday data-analysis work.

**Example:** Type *"What are the top 5 sub-categories by total profit?"* and
get back the SQL query, a results table, and a bar chart — no manual SQL writing.

## How it works

1. A synthetic retail sales dataset (5,000 orders — orders, products,
   categories, regions, customers, sales, profit) is generated and loaded
   into a local SQLite database.
2. The user asks a question in plain English via a Streamlit UI.
3. The question + database schema are sent to Claude, which returns a SQL
   `SELECT` query.
4. The query passes through a safety check (read-only `SELECT` statements
   only — no `INSERT`/`UPDATE`/`DELETE`/`DROP`) before running against SQLite.
5. Results are displayed as a table, with an automatic bar/line chart and a
   CSV export option.

## Tech stack

- **Python** — pandas, SQLite
- **Claude API** (Anthropic) — natural language → SQL translation
- **Streamlit** — interactive UI

## Setup

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd nl2sql-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate the sample data and build the database
python data/generate_data.py
python db/setup_db.py

# 4. Set your Anthropic API key
cp .env.example .env
# then edit .env and paste your key from https://console.anthropic.com/

# 5. Run the app
streamlit run app.py
```

## Project structure

```
nl2sql-dashboard/
├── app.py                 # Streamlit UI
├── nl2sql.py               # Core NL -> SQL engine (prompt, safety check, execution)
├── data/
│   └── generate_data.py    # Synthetic dataset generator
├── db/
│   └── setup_db.py         # Loads CSV into SQLite
├── requirements.txt
└── .env.example
```

## Safety notes

This is a portfolio/demo project. The safety check in `nl2sql.py` restricts
generated queries to single, read-only `SELECT` statements as a guardrail
against destructive SQL — but it is a basic keyword-based check, not a
production-grade sandbox. Don't point this at a database with real or
sensitive data without hardening it further (e.g. a dedicated read-only DB
user, parameterized query validation, or an allow-listed query pattern).

## Possible extensions

- Swap the synthetic dataset for a real one (e.g. a Kaggle sales dataset)
- Add conversation memory so follow-up questions ("now break that down by region")
  work without repeating context
- Support Postgres/Snowflake instead of SQLite for larger datasets
- Cache repeated questions to reduce API calls

---

### Why I built this

Most of my SQL work has been writing queries by hand — this project explores
the other side of that: using an LLM to generate and validate SQL from plain-English
questions, so non-technical stakeholders could query data without knowing SQL
themselves. It's a small end-to-end example of pairing a traditional data
stack (SQLite, pandas) with an AI-assisted workflow layer on top.
