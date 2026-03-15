import os
import logging
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Initialize a single shared Groq client instance
_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def call_groq(system_prompt: str, user_prompt: str, max_tokens: int = 500) -> str:
    try:
        completion = _client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=max_tokens
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Groq API call failed: {e}")
        return "AI feedback unavailable."
