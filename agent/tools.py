from typing import List, Dict, Any, Callable
import datetime
import subprocess
import sys
from io import StringIO

class Tool:
    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func

    def execute(self, **kwargs) -> Any:
        return self.func(**kwargs)

def get_time() -> str:
    """Get the current time."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculate(**kwargs) -> str:
    """Perform basic calculations."""
    expression = kwargs.get('expression', '')
    try:
        result = eval(expression, {"__builtins__": __builtins__})
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

def execute_cmd(**kwargs) -> str:
    """Execute a terminal command."""
    command = kwargs.get('command', '')

    if not command:
        return "Error: No command provided"

    # Remove surrounding quotes if present
    if (command.startswith('"') and command.endswith('"')) or (command.startswith("'") and command.endswith("'")):
        command = command[1:-1]
    
    try:
        # Execute command and capture output
        process = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # Combine stdout and stderr
        output = process.stdout
        if process.stderr:
            output += "\nErrors:\n" + process.stderr
            
        return output if output else "Command executed successfully (no output)"
    except Exception as e:
        return f"Error executing command: {str(e)}"

def execute_code(code: str) -> tuple:
    # Capture stdout
    old_stdout = sys.stdout
    captured_output = StringIO()
    sys.stdout = captured_output

    try:
        # Create a namespace with builtins
        namespace = {"__builtins__": __builtins__}
        # Execute the code in this namespace
        exec(code, namespace)
        # Get captured output
        output = captured_output.getvalue()
        return output, None, True
    except Exception as e:
        return None, str(e), False
    finally:
        sys.stdout = old_stdout

def execute_python(**kwargs) -> str:
    """Execute Python code."""
    code = kwargs.get('code', '')
    if not code:
        return "Error: No code provided"
    
    # Remove surrounding quotes if present
    if (code.startswith('"') and code.endswith('"')) or (code.startswith("'") and code.endswith("'")):
        code = code[1:-1]
    
    # Replace escaped quotes with regular quotes
    code = code.replace('\\"', '"').replace("\\'", "'")

    print("DEBUG Executing Python code:")
    print(code)
    output, error, success = execute_code(code)
    if not success:
        return f"Error: {error}"
    return output if output else "Code executed successfully"

# Default tools
DEFAULT_TOOLS = [
    Tool(
        name="get_time",
        description="Get the current time",
        func=get_time
    ),
    Tool(
        name="calculate",
        description="Perform basic calculations. Input: expression (str)",
        func=calculate
    ),
    Tool(
        name="cmd",
        description="Execute terminal command. Input: command (str). Example: <tool>cmd|command=\"dir\"</tool>",
        func=execute_cmd
    ),
    Tool(
        name="python",
        description="Execute Python code. Input: code (str). Example: <tool>python|code=\"print('Hello')\"</tool>",
        func=execute_python
    )
]

def get_tool_descriptions() -> str:
    """Generate tool descriptions for the agent prompt."""
    descriptions = []
    for tool in DEFAULT_TOOLS:
        descriptions.append(f"- {tool.name}: {tool.description}")
    return "\n".join(descriptions)
