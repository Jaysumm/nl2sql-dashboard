"""
NL2SQL Dashboard — ask questions about sales data in plain English.

Run:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
from nl2sql import ask, NL2SQLError

st.set_page_config(page_title="NL2SQL Sales Dashboard", layout="wide")

st.title("💬 Ask Your Sales Data")
st.caption(
    "Type a question in plain English. Claude converts it to SQL, runs it "
    "against a local SQLite database, and shows you the result."
)

EXAMPLE_QUESTIONS = [
    "What are the top 5 sub-categories by total profit?",
    "Show monthly sales for 2025",
    "Which region has the highest average discount?",
    "Compare profit by customer segment",
    "What are the 10 worst-performing products by profit?",
]

with st.sidebar:
    st.header("Example questions")
    for q in EXAMPLE_QUESTIONS:
        if st.button(q, use_container_width=True):
            st.session_state["question"] = q
    st.divider()
    st.caption(
        "Data: synthetic retail sales dataset (5,000 orders) — "
        "see data/generate_data.py"
    )

question = st.text_input(
    "Your question",
    value=st.session_state.get("question", ""),
    placeholder="e.g. What was total revenue by region last year?",
)

col1, col2 = st.columns([1, 5])
run_clicked = col1.button("Ask", type="primary")

if run_clicked and question.strip():
    with st.spinner("Generating SQL and running query..."):
        try:
            sql, df = ask(question)
        except NL2SQLError as e:
            st.error(str(e))
            df = None
            sql = None
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            df = None
            sql = None

    if df is not None:
        with st.expander("Generated SQL", expanded=False):
            st.code(sql, language="sql")

        if df.empty:
            st.info("Query ran successfully but returned no rows.")
        else:
            st.subheader("Results")
            st.dataframe(df, use_container_width=True)

            # Auto-chart: if there's one numeric column and one categorical/date
            # column, offer a quick bar or line chart.
            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            other_cols = [c for c in df.columns if c not in numeric_cols]

            if numeric_cols and other_cols and len(df) <= 100:
                st.subheader("Quick chart")
                x_col = other_cols[0]
                y_col = numeric_cols[0]
                chart_df = df.set_index(x_col)[[y_col]]
                if "date" in x_col.lower() or "month" in x_col.lower():
                    st.line_chart(chart_df)
                else:
                    st.bar_chart(chart_df)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download results as CSV", csv, "results.csv", "text/csv")

elif run_clicked:
    st.warning("Please enter a question first.")
