import os
import sys
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

from google import genai
client = genai.Client(api_key=api_key)

if len(sys.argv) != 2:
    print("Usage: python main.py <prompt>")
    exit(1)

prompt = sys.argv[1]

response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=[prompt]
)

print(response.text)
print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}\nResponse tokens: {response.usage_metadata.candidates_token_count}")
