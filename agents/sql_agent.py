import openai
import os
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clean_sql(raw_output: str) -> str:
    if "```sql" in raw_output:
        return raw_output.split("```sql")[1].split("```")[0].strip()
    elif "SELECT" in raw_output.upper():
        return raw_output[raw_output.upper().find("SELECT"):].strip()
    else:
        return raw_output.strip()

def generate_sql(user_query, schema_str, table_name):
    prompt = f"""
You are a SQL expert. Based on the user's question and table schema, write a valid SQL query only.
Respond with SQL only — do not add explanations or markdown.

User question: {user_query}
Table schema:
{schema_str}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw_sql = response.choices[0].message.content.strip()
    return clean_sql(raw_sql)