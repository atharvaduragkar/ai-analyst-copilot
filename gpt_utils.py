import openai
import os
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def detect_intent(user_query: str) -> list:
    prompt = f"""
You are an intent classification assistant. Classify the following user query into one or more of the following intents:

- SQL_QUERY: When the user wants to see a table result from a question
- CHART_RENDER: When the user wants to visualize the result as a chart
- INSIGHT_SUMMARY: When the user wants a business summary of the result
- DATA_EXPORT: When the user wants to export result/chart/summary as PDF

Query: "{user_query}"

Respond with a valid Python list of strings, like:
["SQL_QUERY", "CHART_RENDER"]
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    content = response.choices[0].message.content.strip()
    try:
        detected_intents = eval(content)
        return detected_intents if isinstance(detected_intents, list) else []
    except:
        return [s.strip().upper() for s in intents_text.strip("[]").replace('"', '').split(',') if s.strip()]



def generate_dynamic_presets(table_name: str, columns: list) -> list:
    column_str = ", ".join(columns)
    prompt = f"""
You are an AI assistant that suggests 4 useful and insightful business questions a user might ask based on a dataset.

The dataset is a table named '{table_name}' with the following columns: {column_str}.

Respond with 4 questions in a bullet-point list. Do not add explanations.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    lines = response.choices[0].message.content.strip().split("\n")
    return [line.strip("-•123. ").strip() for line in lines if line.strip()]


