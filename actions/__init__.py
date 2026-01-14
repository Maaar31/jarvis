import inspect

TOOL_REGISTRY = {}

class Tool:
    def __init__(self, name, func, description):
        self.name = name
        self.func = func
        self.description = description
        self.signature = str(inspect.signature(func))

def register_tool(description):
    """Decorator to register a function as a tool."""
    def decorator(func):
        tool = Tool(func.__name__, func, description)
        TOOL_REGISTRY[func.__name__] = tool
        return func
    return decorator

def get_tools_schema():
    """Generates a string description of all available tools for the LLM."""
    schema_lines = ["Available Actions:"]
    for name, tool in TOOL_REGISTRY.items():
        schema_lines.append(f"- {name}: {tool.description}")
        schema_lines.append(f"  Usage: {name}{tool.signature}")
    return "\n".join(schema_lines)

def execute_action(action_name, args):
    """Executes a registered action."""
    if action_name in TOOL_REGISTRY:
        try:
            return TOOL_REGISTRY[action_name].func(**args)
        except Exception as e:
            return f"Error executing {action_name}: {str(e)}"
    return f"Action '{action_name}' not found."
