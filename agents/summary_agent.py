import openai
import os
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_summary(user_query, df):
    # Convert DataFrame to Markdown table
    sample = df.head(15).to_markdown(index=False)

    prompt = f"""
You are a business analyst assistant.

Here is a user's question:
{user_query}

And here is the result data in table form:
{sample}

Please write a 2-3 sentence business insight summary based on the data.
Avoid repeating exact numbers unless important.
Make it readable and analytical.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    return response.choices[0].message.content.strip()
