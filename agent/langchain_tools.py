import subprocess
from typing import Optional
import sys
import datetime

def get_time() -> str:
    """Get the current time."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculate(expression: str) -> str:
    """Calculate the result of a mathematical expression."""
    try:
        # Using eval is generally not safe, but for this demo it's acceptable
        # In production, you'd want to use a safer evaluation method
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error calculating: {str(e)}"

def run_python(code: str) -> str:
    """Run Python code and return the output."""
    try:
        # Create a string buffer to capture print output
        import io
        from contextlib import redirect_stdout

        output_buffer = io.StringIO()
        
        # Redirect stdout to our buffer
        with redirect_stdout(output_buffer):
            # Execute the code
            exec(code)
        
        # Get the captured output
        output = output_buffer.getvalue()
        return output if output else "Code executed successfully (no output)"
    except Exception as e:
        return f"Error executing Python code: {str(e)}"

def run_command(command: str, cwd: Optional[str] = None) -> str:
    """Run a system command and return the output."""
    try:
        # Run the command and capture output
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        
        # Combine stdout and stderr
        output = result.stdout
        if result.stderr:
            output += f"\nErrors:\n{result.stderr}"
            
        return output.strip() or "Command executed successfully (no output)"
    except Exception as e:
        return f"Error executing command: {str(e)}"

# Define the default tools
DEFAULT_TOOLS = [
    {
        "name": "get_time",
        "func": get_time,
        "description": "Get the current time"
    },
    {
        "name": "calculate",
        "func": calculate,
        "description": "Calculate the result of a mathematical expression"
    },
    {
        "name": "python",
        "func": run_python,
        "description": "Run Python code and return the output"
    },
    {
        "name": "run_command",
        "func": run_command,
        "description": "Run a system command and return the output"
    }
]
