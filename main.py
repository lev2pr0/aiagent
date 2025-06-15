import os
import sys
from dotenv import load_dotenv
from google.genai import types
from google import genai
from functions import get_files_info, write_file, run_python_file, get_file_content

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

    schema_get_file_content = types.FunctionDeclaration(
        name="get_file_content",
        description="Read file contents, constrained to working directory",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The file path, relative to the working directory. If file path not provided / readable / found / valid file, then return a string with an error.",
                ),
            },
        ),
    )

    schema_run_python_file = types.FunctionDeclaration(
        name="run_python_file",
        description="Execute Python files with optional arguments, constrained to working directory",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The file path, relative to the working directory. If file path not provided / readable / found / valid file, then return a string with an error.",
                ),
            },
        ),
    )

    schema_write_file = types.FunctionDeclaration(
        name="write_file",
        description="Write or overwrite files, constrained to working directory",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The file path, relative to the working directory. If file path not provided / readable / found / valid file, then return a string with an error.",
                ),
                "content": types.Schema(
                    type=types.Type.STRING,
                    description="The content used to write or overwrite files with.",
                ),
            },
        ),
    )

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,
        ]
    )

    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories
    - Read file contents
    - Execute Python files with optional arguments
    - Write or overwrite files

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

    myFuncs = {
        "get_file_content": get_file_content,
        "get_files_info": get_files_info,
        "write_file": write_file,
        "run_python_file": run_python_file,
        }

    def call_function(function_call_part, verbose=False):
        function_call_part = response.function_calls[0]
        function_call_part.args["working_directory"] = "./calculator"
        function_result = myFuncs[function_call_part.name](**function_call_part.args)

        if verbose:
            print(f"Calling function: {function_call_part.name}({function_call_part.args})")
        else:
            print(f"Calling function: {function_call_part.name}")

        if function_call_part.name not in myFuncs:
            return types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=function_call_part.name,
                        response={"error": f"Unknown function: {function_call_part.name}"},
                    )
                ],
            )
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"result": function_result},
                )
            ],
        )

    # Call call_function and set vebose to True/False; Else print response.text
    function_call_result = None # Initialize before the if/else
    if "--verbose" in arguments_list:
        function_call_result = call_function(function_call_part, verbose=True)
    else:
        function_call_result = call_function(function_call_part, verbose=False)

    if "--verbose" in arguments_list:
        print(f"-> {function_call_result.parts[0].function_response.response}")
    else:
        print(response.text)

    # Check for --verbose to add prompt and token counts
    if len(sys.argv) > 2:
        for argument in arguments_list:
            if argument == "--verbose":
                print(f"User prompt: {prompt}\nPrompt tokens: {response.usage_metadata.prompt_token_count}\nResponse tokens: {response.usage_metadata.candidates_token_count}")

main()
