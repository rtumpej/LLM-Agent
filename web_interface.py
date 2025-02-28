from flask import Flask, render_template, request, jsonify, send_from_directory, Response
from agent.agent import Agent  # Import Agent class from local agent directory
import os
from dotenv import load_dotenv
import re
import markdown
import json

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
        f'<div class="code-block-wrapper">'
        f'<div class="code-header">'
        f'<span class="code-language">{m.group(1) or "plaintext"}</span>'
        f'<button class="copy-button" onclick="copyCode(this)">Copy</button>'
        f'</div>'
        f'<pre><code class="language-{m.group(1) or "plaintext"}">{m.group(2)}</code></pre>'
        f'</div>', 
        response, flags=re.DOTALL)
    
    # Then convert the rest of markdown
    response = markdown.markdown(response)
    
    return response

def format_sse(data: dict, event=None) -> str:
    msg = f"data: {json.dumps(data)}\n\n"
    if event is not None:
        msg = f"event: {event}\n{msg}"
    return msg

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
    thinking_step_limit = data.get('thinking_steps', 3)  # Get thinking_steps from request, default to 5
    
    def generate():
        has_more = True
        step = 0
        thinking = thinking_step_limit > 1
        
        try:
            while has_more and step < thinking_step_limit:
                # Process the message through your agent
                response, tool_results = agent.process_message(user_message, think_step=step, thinking=thinking)

                # Check if not thinking
                if not thinking:
                    response = "[FINAL]" + response+"[/FINAL]"
                
                # Check if we're done
                has_more = "[/FINAL]" not in response
                
                # Format tool results
                formatted_tool_results = []
                for result in tool_results:
                    tool_name = result.get('tool_name', 'Unknown Tool')
                    tool_output = result.get('output', '')
                    timestamp = result.get('timestamp', '')
                    formatted_result = {
                        'tool_name': tool_name,
                        'output': tool_output,
                        'timestamp': timestamp,
                        'type': tool_name.lower().replace(' ', '_')
                    }
                    formatted_tool_results.append(formatted_result)
                
                if response.strip():
                    # Send response immediately
                    yield format_sse({
                        'response': format_response(response),
                        'tool_results': formatted_tool_results,
                        'step': step,
                        'is_final': not has_more or thinking_step_limit - step <= 1
                    })
                
                step += 1
                
        except Exception as e:
            yield format_sse({'error': str(e)}, event='error')
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/models', methods=['GET'])
def get_models():
    return jsonify(agent.get_available_models())

@app.route('/settings', methods=['POST'])
def update_settings():
    data = request.json
    try:
        if 'model' in data:
            agent.update_model(data['model'])
        if 'temperature' in data:
            temperature = float(data['temperature'])
            agent.update_temperature(temperature)
        return jsonify({'status': 'success'})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    if not agent:
        print("Warning: OPENAI_API_KEY not set. Chat functionality will be disabled.")
    app.run(debug=True, port=5000)
