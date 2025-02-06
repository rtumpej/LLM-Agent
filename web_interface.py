from flask import Flask, render_template, request, jsonify, send_from_directory
from agent.agent import Agent  # Import your Agent class
import os
from dotenv import load_dotenv
import re
import markdown

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize agent only if API key is available
agent = None
if os.getenv("OPENAI_API_KEY"):
    agent = Agent()

def format_response(response):
    # First handle code blocks with language specification
    code_block_pattern = r'```(\w+)?\n(.*?)\n```'
    response = re.sub(code_block_pattern, lambda m: 
        f'<pre><code class="language-{m.group(1) or "plaintext"}">{m.group(2)}</code></pre>', 
        response, flags=re.DOTALL)
    
    # Then convert the rest of markdown
    response = markdown.markdown(response)
    
    return response

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('templates', filename)

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
        # Format code blocks first, then convert markdown
        formatted_response = format_response(response)
        return jsonify({'response': formatted_response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    if not agent:
        print("Warning: OPENAI_API_KEY not set. Chat functionality will be disabled.")
    app.run(debug=True, port=5000)
