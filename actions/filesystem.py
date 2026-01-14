import os
from . import register_tool

@register_tool("Reads the FULL content of a text file. Args: path (str) - Absolute path preferred.")
def read_file(path):
    if not os.path.exists(path):
        return f"File not found: {path}"
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@register_tool("Writes content to a file. Args: path (str), content (str)")
def write_file(path, content):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {e}"

@register_tool("Lists all files and folders in a specific directory. Args: path (str) - e.g., '.' for current folder or 'C:/Users'")
def list_dir(path="."):
    if not os.path.exists(path):
        return f"Directory not found: {path}"
    try:
        return "\n".join(os.listdir(path))
    except Exception as e:
        return f"Error listing directory: {e}"
