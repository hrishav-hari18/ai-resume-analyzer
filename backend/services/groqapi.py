import requests
from config import GROQ_API_KEY, GROQ_URL, MODEL

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}


def query_llm(prompt):

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7
    }

    try:

        response = requests.post(
            GROQ_URL,
            headers=HEADERS,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:

        return f"LLM Error: {str(e)}"