import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)
print("Testing gemini-3.6-flash with API key...")
try:
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Hello! Confirm that API key is valid."
    )
    print("SUCCESS Result:", response.text)
except Exception as e:
    print("Error:", e)
