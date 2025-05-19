import openai
import os
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_chart_info(user_query: str, df_columns: list) -> dict:
    prompt = f"""
You are a chart-building assistant.
From the user query and column list, decide:

- Which column is the X-axis?
- Which column is the Y-axis?
- What chart type to use (bar, line, pie, scatter)?

### Columns:
{', '.join(df_columns)}

### User Query:
{user_query}

Respond in this format:
chart_type: <bar|line|pie|scatter>
x: <column>
y: <column>
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    output = response.choices[0].message.content.strip()

    try:
        lines = output.splitlines()
        chart_type = lines[0].split(":")[1].strip().lower()
        x_col = lines[1].split(":")[1].strip()
        y_col = lines[2].split(":")[1].strip()
        return {"chart_type": chart_type, "x": x_col, "y": y_col}
    except Exception:
        return {"chart_type": "bar", "x": df_columns[0], "y": df_columns[1]}

def render_chart(chart_type, df, x, y):
    if chart_type == "line":
        fig = px.line(df, x=x, y=y)
    elif chart_type == "scatter":
        fig = px.scatter(df, x=x, y=y)
    elif chart_type == "pie":
        fig = px.pie(df, names=x, values=y)
    else:
        fig = px.bar(df, x=x, y=y)
    return fig
