from typing import Dict

class Prompts:
    def __init__(self):
        self.prompts: Dict[str, str] = {
            "system": """You are a helpful AI assistant with memory capabilities. You maintain context throughout the conversation and can remember previous interactions.

When asked about previous conversations or information shared earlier, ALWAYS check the conversation history provided in the messages.

Available tools:
{tools}

To use a tool, you MUST use the following format:
<tool>tool_name|param1=value1,param2=value2</tool>

For example:
- To get time: <tool>get_time|</tool>
- To calculate: <tool>calculate|expression=2+2</tool>
- To run Python code: <tool>python|code="x = 5
print('Value of x:', x)"</tool>

Guidelines:
1. ALWAYS maintain context from previous messages
2. When asked about past information, refer to the conversation history
3. Be direct and specific in your responses
4. Use appropriate tools when needed
5. If you don't find relevant information in the history, say so clearly
6. When using the Python tool, format multi-line code using a single set of quotes
7. USE PYTHON to run system commands""",
            
            "user": "{user_input}",
            
            "error": "I encountered an error: {error_message}"
        }

    def get_prompt(self, prompt_type: str, **kwargs) -> str:
        """Get a prompt with formatted parameters."""
        if prompt_type not in self.prompts:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        
        return self.prompts[prompt_type].format(**kwargs)

    def update_prompt(self, prompt_type: str, new_prompt: str) -> None:
        """Update an existing prompt template."""
        if prompt_type not in self.prompts:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        
        self.prompts[prompt_type] = new_prompt

    def add_prompt(self, prompt_type: str, prompt: str) -> None:
        """Add a new prompt template."""
        if prompt_type in self.prompts:
            raise ValueError(f"Prompt type already exists: {prompt_type}")
        
        self.prompts[prompt_type] = prompt
