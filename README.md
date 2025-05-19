<p align="center">
  <img src="assets/thumbnail.png" alt="AI Analyst Copilot Banner" width="80%">
</p>


# 📊 AI Analyst Copilot

An intelligent data analysis assistant built with GPT-4 (or 3.5), Streamlit, and Plotly. The tool allows users to ask business questions in plain English and get answers as SQL queries, charts, summaries, and downloadable PDF reports.

---

## 🎯 Key Features

- **Natural Language Interface**  
  Ask questions like _“What are the top 5 regions by sales in Q1?”_ — the AI translates it into SQL instantly.

- **Multi-Agent Routing with Intent Detection**  
  Each user query is automatically classified into one or more intents:
  - `SQL_QUERY`
  - `CHART_RENDER`
  - `INSIGHT_SUMMARY`
  - `DATA_EXPORT`

- **Modular Architecture**  
  Each feature (SQL agent, chart agent, summary agent, export agent) is handled independently for clean extensibility.

- **Interactive Visualizations**  
  Automatically generates Plotly charts with user override for type selection.

- **Auto PDF Reports**  
  Results (table + chart + summary) are exported to a beautiful, one-click downloadable PDF.

- **Dynamic Query Suggestions**  
  The app reads the uploaded dataset's schema and suggests intelligent questions using GPT.

- **Streamlit Frontend + SQLite Backend**  
  Clean UI with multi-CSV uploads, schema previews, and table switching.

---

## 🧠 Tech Stack

- `Python` + `Streamlit` + `SQLite` + `Plotly`
- `OpenAI GPT-3.5/GPT-4 API`
- `Pandas`, `FPDF`, `dotenv`, `session_state`

---

## 💡 Example Use Cases

- Upload a `Superstore Sales` dataset
- Ask: _“Show me sales by region and export to PDF”_
- View chart + table + insight, then download the report

---

## 🔗 Demo Preview (Optional)

> Screenshots or Loom link here

---

## 🚀 Future Enhancements

- Multi-table joins
- Save to Excel / CSV
- Feedback on AI-generated answers
- LangChain agent comparison (optional)

---