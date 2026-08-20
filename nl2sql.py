"""
Core NL -> SQL engine.

Takes a plain-English question, asks Claude to translate it into a SQLite
query against the `sales` table schema, runs it safely (read-only), and
returns both the generated SQL and the resulting DataFrame.
"""

import os
import re
import sqlite3
import pandas as pd
from anthropic import Anthropic

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "sales.db")

SCHEMA_DESCRIPTION = """
Table: sales
Columns:
  order_id      TEXT   -- unique order identifier
  order_date    TEXT   -- format YYYY-MM-DD
  ship_date     TEXT   -- format YYYY-MM-DD
  ship_mode     TEXT   -- 'Standard Class', 'Second Class', 'First Class', 'Same Day'
  customer_id   TEXT
  segment       TEXT   -- 'Consumer', 'Corporate', 'Home Office'
  region        TEXT   -- 'East', 'West', 'Central', 'South'
  product_id    TEXT
  category      TEXT   -- 'Furniture', 'Office Supplies', 'Technology'
  sub_category  TEXT   -- e.g. 'Chairs', 'Binders', 'Phones'
  quantity      INTEGER
  unit_price    REAL
  discount      REAL   -- fraction, e.g. 0.2 = 20%
  sales         REAL   -- revenue for the line item, after discount
  profit        REAL   -- profit for the line item
"""

SYSTEM_PROMPT = f"""You are a SQL generator for a SQLite database. Given a user's
plain-English question, output ONLY a single valid SQLite SELECT query that answers it.

{SCHEMA_DESCRIPTION}

Rules:
- Output ONLY the raw SQL query. No explanation, no markdown code fences, no preamble.
- Only generate SELECT statements. Never generate INSERT, UPDATE, DELETE, DROP, or ALTER.
- Use standard SQLite date functions (e.g. strftime) for date grouping.
- If the question is ambiguous, make a reasonable assumption and answer it anyway.
- Limit results to 200 rows unless the user asks for a specific smaller number.
"""


class NL2SQLError(Exception):
    pass


def _get_client() -> Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise NL2SQLError(
            "ANTHROPIC_API_KEY is not set. Create a .env file (see .env.example) "
            "or export it in your shell before running the app."
        )
    return Anthropic(api_key=api_key)


def _extract_sql(raw_text: str) -> str:
    """Strip markdown fences if the model adds them despite instructions."""
    text = raw_text.strip()
    fence_match = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()
    return text


def _is_safe_select(sql: str) -> bool:
    """Basic guardrail: only allow single read-only SELECT statements."""
    normalized = sql.strip().rstrip(";").strip().lower()
    if not normalized.startswith("select"):
        return False
    forbidden = ["insert", "update", "delete", "drop", "alter", "attach", "pragma", ";"]
    # allow the query itself to not contain a second statement or forbidden keywords
    body = normalized
    for word in forbidden:
        if word in body:
            return False
    return True


def question_to_sql(question: str, model: str = "claude-sonnet-4-6") -> str:
    """Calls Claude to translate a natural language question into SQL."""
    client = _get_client()
    response = client.messages.create(
        model=model,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": question}],
    )
    raw_text = "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )
    sql = _extract_sql(raw_text)

    if not _is_safe_select(sql):
        raise NL2SQLError(f"Generated query failed safety check:\n{sql}")

    return sql


def run_query(sql: str) -> pd.DataFrame:
    """Executes a SQL query against the local read-only sales database."""
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    try:
        df = pd.read_sql_query(sql, conn)
    finally:
        conn.close()
    return df


def ask(question: str, model: str = "claude-sonnet-4-6"):
    """
    Full pipeline: question -> SQL -> results.
    Returns (sql, dataframe).
    """
    sql = question_to_sql(question, model=model)
    df = run_query(sql)
    return sql, df


if __name__ == "__main__":
    # Quick manual test (requires ANTHROPIC_API_KEY to be set)
    q = "What are the top 5 sub-categories by total profit?"
    sql, df = ask(q)
    print("Question:", q)
    print("Generated SQL:\n", sql)
    print("\nResults:\n", df)
