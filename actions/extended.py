import psutil
import pyautogui
import os
import datetime
from . import register_tool

@register_tool("Returns system statistics (CPU, RAM). Args: none")
def system_stats():
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory()
    return f"CPU Usage: {cpu}%\nRAM Usage: {ram.percent}% ({ram.used // (1024*1024)}MB / {ram.total // (1024*1024)}MB)"

@register_tool("Takes a screenshot of the main screen and saves it. Args: filename (optional)")
def take_screenshot(filename=None):
    if not filename:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
    
    # Save in current directory or a screenshots folder
    try:
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        path = os.path.join("screenshots", filename)
        pyautogui.screenshot(path)
        return f"Screenshot saved to {path}"
    except Exception as e:
        return f"Error taking screenshot: {e}"
