import os
import sys
from dotenv import load_dotenv
from google.genai import types
from google import genai

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if len(sys.argv) == 1:
        print("Usage: python main.py '<prompt here>'")
        exit(1)
prompt = sys.argv[1]
arguments_list = sys.argv[2:]

def main():
    client = genai.Client(api_key=api_key)
    messages = [
        types.Content(role="user", parts=[types.Part(text=prompt)]),
    ]
    response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=messages,
    )

    print(response.text)
    if len(sys.argv) > 2:
        for argument in arguments_list:
            if argument == "--verbose":
                print(f"User prompt: {prompt}\nPrompt tokens: {response.usage_metadata.prompt_token_count}\nResponse tokens: {response.usage_metadata.candidates_token_count}")

main()
