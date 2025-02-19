from langchain_openai import ChatOpenAI
from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.schema.messages import SystemMessage, HumanMessage, AIMessage
import os
from typing import List, Dict, Any
from datetime import datetime
import json
from .langchain_tools import DEFAULT_TOOLS

class LangChainAgent:
    AVAILABLE_MODELS = [
        {"id": "gpt-4-0125-preview", "name": "GPT-4 Turbo"},
        {"id": "gpt-4-1106-preview", "name": "GPT-4 Turbo Preview"},
        {"id": "gpt-4", "name": "GPT-4"},
        {"id": "gpt-4-32k", "name": "GPT-4 32k"},
        {"id": "gpt-4o", "name": "GPT-4 Online"},
        {"id": "gpt-4o-mini", "name": "GPT-4 Online Mini"},
        {"id": "gpt-3.5-turbo-0125", "name": "GPT-3.5 Turbo Latest"},
        {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"},
        {"id": "gpt-3.5-turbo-16k", "name": "GPT-3.5 Turbo 16k"}
    ]

    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.7):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        if model not in [m["id"] for m in self.AVAILABLE_MODELS]:
            raise ValueError(f"Invalid model. Must be one of: {', '.join([m['id'] for m in self.AVAILABLE_MODELS])}")
        
        if not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")

        self.model = model
        self.temperature = temperature
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            openai_api_key=api_key
        )
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # Initialize tools
        self.tools = []
        for tool_config in DEFAULT_TOOLS:
            self.tools.append(Tool(
                name=tool_config["name"],
                func=tool_config["func"],
                description=tool_config["description"]
            ))

        # Initialize the agent with system prompt
        system_prompt = """Your name is Marjan. You are a helpful, friendly, optimistic scientist with memory capabilities. 
        You maintain context throughout the conversation and can remember previous interactions.
        Your tone of conversation is mainly casual, friendly and funny - except when you get a professional question, then you respond formally.
        
        Guidelines:
        1. ALWAYS maintain context from previous messages
        2. When asked about past information, refer to the conversation history
        3. Be direct and specific in your responses
        4. Use appropriate tools when needed
        5. If you don't find relevant information in the history, say so clearly"""

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create the agent
        agent = create_openai_functions_agent(self.llm, self.tools, self.prompt)
        
        # Create the executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True
        )

    def process_message(self, user_input: str, think_step: int = 0, thinking: bool = False) -> tuple[str, list[dict]]:
        """Process a user message and return the response with tool results."""
        try:
            # Process the message through the agent
            response = self.agent_executor.invoke({
                "input": user_input,
            })

            # Extract tool results if any were used
            tool_results = []
            if hasattr(response, 'intermediate_steps'):
                for action, output in response.intermediate_steps:
                    tool_results.append({
                        "tool_name": action.tool,
                        "output": str(output),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

            # Format the response
            final_response = response["output"]
            if not thinking:
                final_response = f"[FINAL]{final_response}[/FINAL]"

            return final_response, tool_results

        except Exception as e:
            error_response = f"Error processing message: {str(e)}"
            return error_response, []

    def get_available_models(self) -> List[Dict[str, str]]:
        """Get list of available models."""
        return self.AVAILABLE_MODELS

    def update_model(self, model: str) -> None:
        """Update the model being used."""
        if model not in [m["id"] for m in self.AVAILABLE_MODELS]:
            raise ValueError(f"Invalid model. Must be one of: {', '.join([m['id'] for m in self.AVAILABLE_MODELS])}")
        
        self.model = model
        self.llm = ChatOpenAI(
            model=model,
            temperature=self.temperature
        )
        
        # Recreate the agent with new model
        agent = create_openai_functions_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True
        )

    def update_temperature(self, temperature: float) -> None:
        """Update the temperature setting."""
        if not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        
        self.temperature = temperature
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=temperature
        )
        
        # Recreate the agent with new temperature
        agent = create_openai_functions_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True
        )
