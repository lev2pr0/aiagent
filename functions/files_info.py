import os

def get_files_info(working_directory, directory=None):

    if directory is None:
        directory = '.'

    abs_working_dir = os.path.abspath(working_directory)
    target_dir = os.path.abspath(os.path.join(working_directory, directory))

    if not target_dir.startswith(abs_working_dir):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    if not os.path.isdir(target_dir):
        return f'Error: "{directory}" is not a directory'

    output = []
    for item in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item)

        try:
            size = os.path.getsize(item_path)
        except FileNotFoundError:
            size = "Error: File/Directory not found"
        except PermissionError:
            size = "Error: Permission denied"
        try:
            is_dir = os.path.isdir(item_path)
        except PermissionError:
            is_dir = "Error: Permission denied"

        output.append(f"- {item}: file_size={size} bytes, is_dir={is_dir}")
    return "\n".join(output)
