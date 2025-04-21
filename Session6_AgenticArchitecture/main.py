import asyncio
from flask import Flask, jsonify, request, Response
from perceive import extract_facts
from decision import process_order_facts
from action import MCPClient
from memory import Memory

# Global singleton
mcp = None
memory = Memory()
app = Flask(__name__)

# Initialize MCP client and cache tools
def init_mcp():
    global mcp
    print("Connecting client to MCP server...", flush=True)
    mcp = MCPClient()
    print("MCP client-server connected. Tools loaded.", flush=True)


@app.route('/preference', methods=['POST'])
def set_preference():
    data = request.json
    if not data or 'cuisine' not in data or 'is_vegetarian' not in data:
        return jsonify({'error': 'Missing cuisine or is_vegetarian'}), 400
    memory.addPreference(data)
    return jsonify({'message': 'Preference saved successfully'})

@app.route('/preference', methods=['GET'])
def get_preference():
    pref = memory.getPreference()
    if pref is None:
        return jsonify({'error': 'No preference set'}), 404
    return jsonify({'cuisine': pref.cuisine, 'is_vegetarian': pref.is_vegetarian})

@app.route('/order', methods=['POST'])
def handle_order():
    """Handle food order request."""
    data = request.json
    if not data or 'order_text' not in data:
        return jsonify({'error': 'Missing order_text'}), 400

    try:
        # Extract facts and process synchronously
        facts = extract_facts(data['order_text'])
        decision = asyncio.run(process_order_facts(facts, memory=memory, mcpClient=mcp))
        # Return plain text decision
        return Response(decision or '', status=200, mimetype='text/plain')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    init_mcp()
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
