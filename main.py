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

    schema_get_files_info = types.FunctionDeclaration(
        name="get_files_info",
        description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "directory": types.Schema(
                    type=types.Type.STRING,
                    description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
                ),
            },
        ),
    )

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
        ]
    )

    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories

    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
    """

    response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions],
                system_instruction=[system_prompt]
            ),
    )


    if response.function_calls:
        function_call_part = response.function_calls[0]
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(response.text)

    if len(sys.argv) > 2:
        for argument in arguments_list:
            if argument == "--verbose":
                print(f"User prompt: {prompt}\nPrompt tokens: {response.usage_metadata.prompt_token_count}\nResponse tokens: {response.usage_metadata.candidates_token_count}")

main()
