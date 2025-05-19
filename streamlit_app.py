from gpt_utils import generate_dynamic_presets
from agents.export_agent import export_to_pdf
from agents.summary_agent import generate_summary
from agents.chart_agent import extract_chart_info, render_chart
from agents.sql_agent import generate_sql
from agents.query_runner import run_query
from gpt_utils import detect_intent
import streamlit as st
import pandas as pd
import sqlite3
import os

DATA_FOLDER = "data"

# Create SQLite in-memory DB
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

st.title("📊 AI Analyst Copilot")  # Fixed: replaced surrogate emoji with proper unicode character

# Upload CSV files
uploaded_files = st.file_uploader("Upload one or more CSV files", type="csv", accept_multiple_files=True)

# Load CSVs into SQLite
if uploaded_files:
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        table_name = os.path.splitext(file_name)[0].replace(" ", "_").lower()

        # Save file to disk
        file_path = os.path.join(DATA_FOLDER, file_name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Read CSV into DataFrame
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='ISO-8859-1')  # fallback encoding

        # Save DataFrame to SQLite
        df.to_sql(table_name, conn, if_exists="replace", index=False)

    st.success("✅ All files uploaded and loaded into database.")

    # Show list of tables in the DB
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
table_names = [row[0] for row in cursor.fetchall()]

if table_names:
    st.subheader("📋 Tables in Database")
    selected_table_for_schema = st.selectbox("Select a table to view its columns", table_names)

    # Show selected table's schema
    st.markdown(f"### 🧾 `{selected_table_for_schema}` Schema:")
    cursor.execute(f'PRAGMA table_info("{selected_table_for_schema}");')
    columns = cursor.fetchall()
    for col in columns:
        st.markdown(f"- {col[1]} ({col[2]})")

# Add a dropdown to select a table for preview
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
table_names = [row[0] for row in cursor.fetchall()]

st.subheader("🔍 Preview a Table")
selected_table = st.selectbox("Select a table to preview", table_names)

if selected_table:
    df_preview = pd.read_sql_query(f"SELECT * FROM '{selected_table}' LIMIT 10;", conn)
    st.dataframe(df_preview)

user_query = ""

# Show table selection first
if table_names:
    st.subheader("🧠 Ask a Question")

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = [row[0] for row in cursor.fetchall()]

    selected_table_for_query = st.selectbox(
        "Select table to run the query on", table_names, key="table_selector_main"
    )

    # Get column names for the selected table
    cursor.execute(f"PRAGMA table_info('{selected_table_for_query}');")
    columns = [col[1] for col in cursor.fetchall()]

    # Generate dynamic suggestions using GPT
    dynamic_presets = generate_dynamic_presets(selected_table_for_query, columns)

    # Initialize session state variables
    if "user_query" not in st.session_state:
        st.session_state.user_query = ""
    if "preset_clicked" not in st.session_state:
        st.session_state.preset_clicked = False

    # Show preset buttons
    if dynamic_presets:
        st.markdown("**💡 Suggested questions:**")
        for i, preset in enumerate(dynamic_presets):
            if st.button(preset, key=f"preset_btn_{i}"):
                st.session_state.user_query = preset
                st.session_state.preset_clicked = True

    # Handle input and auto-trigger on button click
    user_query = st.text_input("Or enter your own question", value=st.session_state.user_query)
    if st.session_state.preset_clicked:
        user_query = st.session_state.user_query
        st.session_state.preset_clicked = False

if user_query:
    # Detect multiple intents using GPT
    intents = detect_intent(user_query)
    st.markdown(f"**Detected Intents:** `{', '.join(intents)}`")

    # Let user choose a table to run the query against
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = [row[0] for row in cursor.fetchall()]

    if "SQL_QUERY" in intents:
        cursor.execute(f"PRAGMA table_info('{selected_table_for_query}');")
        columns = cursor.fetchall()
        schema_str = f"Table `{selected_table_for_query}` has columns:\n" + "\n".join(
            [f"- {col[1]} ({col[2]})" for col in columns]
        )
        sql_query = generate_sql(user_query, schema_str, selected_table_for_query)
        st.code(sql_query, language="sql")
        result_df = run_query(conn, sql_query)
        st.dataframe(result_df)

    if "CHART_RENDER" in intents:
        cursor.execute(f"PRAGMA table_info('{selected_table_for_query}');")
        columns = cursor.fetchall()
        schema_str = f"Table `{selected_table_for_query}` has columns:\n" + "\n".join(
            [f"- {col[1]} ({col[2]})" for col in columns]
        )
        sql_query = generate_sql(user_query, schema_str, selected_table_for_query)
        st.code(sql_query, language="sql")
        df_result = run_query(conn, sql_query)

        if "error" in df_result.columns:
            st.error(df_result["error"][0])
        else:
            st.dataframe(df_result)
            chart_types = ["Auto", "bar", "line", "scatter", "pie"]
            user_chart_type = st.selectbox("📈 Choose chart type (optional)", chart_types)
            chart_info = extract_chart_info(user_query, df_result.columns.tolist())
            chart_type = chart_info["chart_type"]
            if user_chart_type != "Auto":
                chart_type = user_chart_type
            fig = render_chart(chart_type, df_result, chart_info["x"], chart_info["y"])
            st.plotly_chart(fig, use_container_width=True)

    if "INSIGHT_SUMMARY" in intents:
        cursor.execute(f"PRAGMA table_info('{selected_table_for_query}');")
        columns = cursor.fetchall()
        schema_str = f"Table `{selected_table_for_query}` has columns:\n" + "\n".join(
            [f"- {col[1]} ({col[2]})" for col in columns]
        )
        sql_query = generate_sql(user_query, schema_str, selected_table_for_query)
        st.code(sql_query, language="sql")
        df_result = run_query(conn, sql_query)

        if "error" in df_result.columns:
            st.error(df_result["error"][0])
        else:
            st.dataframe(df_result)
            summary = generate_summary(user_query, df_result)
            st.success("💡 Business Insight:")
            st.markdown(f"> {summary}")

    if "DATA_EXPORT" in intents:
        cursor.execute(f"PRAGMA table_info('{selected_table_for_query}');")
        columns = cursor.fetchall()
        schema_str = f"Table `{selected_table_for_query}` has columns:\n" + "\n".join(
            [f"- {col[1]} ({col[2]})" for col in columns]
        )
        sql_query = generate_sql(user_query, schema_str, selected_table_for_query)
        st.code(sql_query, language="sql")
        df_result = run_query(conn, sql_query)

        if "error" in df_result.columns:
            st.error(df_result["error"][0])
        else:
            st.dataframe(df_result)
            try:
                summary = generate_summary(user_query, df_result)
                st.success("💡 Insight:")
                st.markdown(f"> {summary}")
            except Exception:
                summary = None
            chart_fig = None
            try:
                chart_info = extract_chart_info(user_query, df_result.columns.tolist())
                chart_fig = render_chart(chart_info["chart_type"], df_result, chart_info["x"], chart_info["y"])
                st.plotly_chart(chart_fig, use_container_width=True)
            except Exception:
                st.warning("Chart could not be generated automatically.")
            pdf_path = export_to_pdf(sql_query, df_result, summary, chart_fig=chart_fig)
            with open(pdf_path, "rb") as f:
                st.download_button("📥 Download Report as PDF", f, file_name="report.pdf")

    if not intents:
        st.warning("❓ Couldn’t detect what you meant. Try rephrasing your question.")
