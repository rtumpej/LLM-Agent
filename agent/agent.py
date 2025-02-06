import os
from typing import List, Dict, Any
import re
import openai
from .tools import Tool, DEFAULT_TOOLS
from .prompts import Prompts
from .memory import Memory

class Agent:
    AVAILABLE_MODELS = [
        {"id": "gpt-4", "name": "GPT-4"},
        {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"},
        {"id": "gpt-4o", "name": "GPT-4 Online"},
        {"id": "gpt-4o-mini", "name": "GPT-4 Online Mini"}
    ]

    def __init__(self, model: str = "gpt-4"): 
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        if model not in [m["id"] for m in self.AVAILABLE_MODELS]:
            raise ValueError(f"Invalid model. Must be one of: {', '.join([m['id'] for m in self.AVAILABLE_MODELS])}")
        
        self.model = model
        self.api_key = api_key
        self.tools = {tool.name: tool for tool in DEFAULT_TOOLS}
        self.prompts = Prompts()
        self.memory = Memory()

    def add_tool(self, tool: Tool) -> None:
        """Add a new tool to the agent."""
        self.tools[tool.name] = tool

    def parse_tool_call(self, tool_call: str) -> tuple[str, Dict[str, Any]]:
        """Parse a tool call string into tool name and parameters."""
        match = re.match(r'<tool>(\w+)\|(.*)</tool>', tool_call.strip())
        if not match:
            raise ValueError("Invalid tool call format")

        tool_name, params_str = match.groups()
        params = {}
        if params_str:
            for param in params_str.split(','):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key.strip()] = value.strip()

        return tool_name, params

    def execute_tool(self, tool_call: str) -> str:
        """Execute a tool call and return the result."""
        try:
            # Extract tool content
            match = re.search(r'<tool>(.*?)</tool>', tool_call, re.DOTALL)
            if not match:
                return "Error: Invalid tool call format"
            
            tool_content = match.group(1).strip()
            
            # Split into tool name and parameters
            if '|' not in tool_content:
                tool_name = tool_content
                params = {}
            else:
                tool_name, param_str = tool_content.split('|', 1)
                tool_name = tool_name.strip()
                params = {}
                
                # Find parameters using regex to handle quoted values and preserve newlines
                param_matches = re.finditer(
                    r'(\w+)=("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|[^,\s]+)',
                    param_str,
                    re.DOTALL
                )
                for match in param_matches:
                    key = match.group(1)
                    value = match.group(2)
                    # Normalize newlines in the value
                    value = value.replace('\\n', '\n')
                    params[key] = value

            print(f"DEBUG - Tool name: {tool_name}")
            print(f"DEBUG - Parameters: {params}")

            if tool_name not in self.tools:
                return f"Error: Unknown tool '{tool_name}'"

            return self.tools[tool_name].execute(**params)
            
        except Exception as e:
            import traceback
            print(f"DEBUG - Error details: {traceback.format_exc()}")
            return f"Error: {str(e)}"

    def process_message(self, user_input: str) -> str:
        """Process a user message and return the response."""
        try:
            # Add user message to memory
            self.memory.add_message("user", user_input)

            # Prepare the system message with available tools
            system_message = self.prompts.get_prompt(
                "system",
                tools="\n".join(f"- {name}: {tool.description}" 
                              for name, tool in self.tools.items())
            )

            # Create the conversation with history
            messages = [
                {"role": "system", "content": system_message}
            ]
            
            # Add recent conversation history
            history = self.memory.get_conversation_history(last_n=10)
            messages.extend([
                {"role": msg["role"], "content": msg["content"]}
                for msg in history
            ])

            # Get response from OpenAI
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )

            response_text = response.choices[0].message['content']

            # Process any tool calls in the response
            while '<tool>' in response_text:
                match = re.search(r'<tool>(.*?)</tool>', response_text, re.DOTALL)
                if not match:
                    break
                tool_call = match.group(0)
                tool_content = match.group(1)
                print("Executing TOOL:", tool_call, tool_content)
                tool_result = self.execute_tool(tool_call)
                response_text = response_text.replace(tool_call, tool_result)

            # Add assistant's response to memory
            self.memory.add_message("assistant", response_text)
            return response_text

        except Exception as e:
            error_msg = self.prompts.get_prompt("error", error_message=str(e))
            self.memory.add_message("assistant", error_msg)
            return error_msg

    @classmethod
    def get_available_models(cls):
        return cls.AVAILABLE_MODELS

    def update_model(self, model: str):
        if model not in [m["id"] for m in self.AVAILABLE_MODELS]:
            raise ValueError(f"Invalid model. Must be one of: {', '.join([m['id'] for m in self.AVAILABLE_MODELS])}")
        self.model = model
