import sys
from io import StringIO
from typing import Dict, Any, Tuple

class PythonExecutor:
    def __init__(self):
        # Use the full Python environment
        self.globals: Dict[str, Any] = {
            '__builtins__': __builtins__,
            '__name__': '__main__'
        }
        self.locals: Dict[str, Any] = {}

    def execute(self, code: str) -> Tuple[str, str, bool]:
        """
        Execute Python code with full access to Python features.
        Returns: (output, error_message, success)
        """
        # Remove surrounding quotes if present
        if (code.startswith('"') and code.endswith('"')) or (code.startswith("'") and code.endswith("'")):
            code = code[1:-1]
        
        # Replace escaped quotes with regular quotes
        code = code.replace('\\"', '"').replace("\\'", "'")
        
        # Remove any leading/trailing whitespace
        code = code.strip()
        
        print("DEBUG - Executing code:")
        print("-------------------")
        print(code)
        print("-------------------")

        # Capture stdout
        old_stdout = sys.stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            # Execute the code with full access
            exec(code, self.globals, self.locals)
            output = captured_output.getvalue()
            return output, "", True
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"DEBUG - Error details: {error_details}")
            return "", str(e), False
        finally:
            sys.stdout = old_stdout

    def get_variable(self, name: str) -> Any:
        """Get a variable from the execution environment."""
        return self.locals.get(name)
