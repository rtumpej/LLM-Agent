from flask import Flask, render_template, request, jsonify
from agent.agent import Agent  # Import your Agent class
import os
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize agent only if API key is available
agent = None
if os.getenv("OPENAI_API_KEY"):
    agent = Agent()

def format_response(text):
    """Format the response to properly handle code blocks and other markdown elements."""
    # Replace triple backtick code blocks with proper markdown
    text = re.sub(
        r'```(\w+)?\n(.*?)```',
        lambda m: f"```{m.group(1) or 'plaintext'}\n{m.group(2).strip()}\n```",
        text,
        flags=re.DOTALL
    )
    
    # Ensure proper spacing around code blocks
    text = re.sub(r'(\n```\w*\n)', r'\n\1', text)
    text = re.sub(r'(\n```\n)', r'\1\n', text)
    
    return text

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    if not agent:
        return jsonify({
            'error': 'OpenAI API key not set. Please set the OPENAI_API_KEY environment variable.'
        }), 500

    data = request.get_json()
    user_message = data.get('message', '')
    
    try:
        # Process the message through your agent
        response = agent.process_message(user_message)
        # Format the response for better code display
        formatted_response = format_response(response)
        return jsonify({'response': formatted_response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    if not agent:
        print("Warning: OPENAI_API_KEY not set. Chat functionality will be disabled.")
    app.run(debug=True, port=5000)
