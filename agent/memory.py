from typing import List, Dict, Optional
import json
from datetime import datetime

class Memory:
    def __init__(self, max_messages: int = 100):
        self.messages: List[Dict] = []
        self.max_messages = max_messages
        self.persistent_memory: Dict = {}

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.messages.append(message)
        
        # Keep only the last max_messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_conversation_history(self, last_n: Optional[int] = None) -> List[Dict]:
        """Get the conversation history, optionally limited to last n messages."""
        if last_n is None:
            return self.messages
        return self.messages[-last_n:]

    def store_memory(self, key: str, value: any) -> None:
        """Store a persistent memory item."""
        self.persistent_memory[key] = value

    def retrieve_memory(self, key: str) -> Optional[any]:
        """Retrieve a persistent memory item."""
        return self.persistent_memory.get(key)

    def save_to_file(self, filename: str) -> None:
        """Save memory to a file."""
        data = {
            "messages": self.messages,
            "persistent_memory": self.persistent_memory
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    def load_from_file(self, filename: str) -> None:
        """Load memory from a file."""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.messages = data.get("messages", [])
                self.persistent_memory = data.get("persistent_memory", {})
        except FileNotFoundError:
            pass  # Start with empty memory if file doesn't exist
