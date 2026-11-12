"""Quick check that your Gemini API key works. Run: python check_gemini.py"""
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()  # reads GEMINI_API_KEY and GEMINI_MODEL from .env

api_key = os.getenv("GEMINI_API_KEY")
model = "gemini-3.6-flash"

if not api_key:
    raise SystemExit("No API key found. Put GEMINI_API_KEY=... in your .env file.")

client = genai.Client(api_key=api_key)
response = client.models.generate_content(
    model=model,
    contents="In one sentence, how often should a 3-month-old puppy eat?",
)
print(f"Model: {model}")
print(f"Gemini says: {response.text}")