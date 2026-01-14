import sys
from termcolor import cprint

def print_jarvis(text):
    """Print a message from Jarvis in a specific color."""
    cprint(f"Jarvis: {text}", "cyan", attrs=["bold"])

def print_system(text):
    """Print a system message."""
    cprint(f"[SYSTEM] {text}", "yellow")

def print_error(text):
    """Print an error message."""
    cprint(f"[ERROR] {text}", "red")

def parse_code_block(text):
    """
    Extracts JSON content from a markdown code block if present.
    Often LLMs wrap JSON in ```json ... ```.
    """
    if "```json" in text:
        try:
            start = text.find("```json") + 7
            end = text.find("```", start)
            return text[start:end].strip()
        except:
            return text
    elif "```" in text:
        try:
            start = text.find("```") + 3
            end = text.find("```", start)
            return text[start:end].strip()
        except:
            return text
    return text.strip()
