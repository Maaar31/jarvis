import os
import subprocess
import platform
from . import register_tool

@register_tool("Opens an application or file. Args: app_name (str)")
def open_app(app_name):
    system_platform = platform.system()
    try:
        if system_platform == "Windows":
            os.startfile(app_name)
        elif system_platform == "Darwin": # macOS
            subprocess.run(["open", "-a", app_name])
        else: # Linux
            subprocess.run(["xdg-open", app_name])
        return f"Opened {app_name}"
    except Exception as e:
        return f"Error opening app: {e}"
