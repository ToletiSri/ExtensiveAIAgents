# main.py
from flask import Flask, request, jsonify
from memory import Memory
from dotenv import load_dotenv
import asyncio
from action import MCPClient

app = Flask(__name__)
memory = Memory()
load_dotenv()
mcp = None  # Global singleton


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
    data = request.json
    if not data or 'order_text' not in data:
        return jsonify({'error': 'Missing order_text'}), 400

    from perceive import extract_facts
    from decision import process_order_facts
    try:
        facts = extract_facts(data['order_text'])
        decision = asyncio.run(process_order_facts(facts, memory=memory, mcpClient=mcp))
        return jsonify({'Result': decision})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

async def run():
    global mcp
    import threading
    print("[SERVER INIT] Connecting to MCP client...", flush=True)

    async with MCPClient() as client:
        mcp = client
        print("[SERVER INIT] MCP connection established.", flush=True)
        print("\nAvailable Tools:\n", mcp.get_tools_description(), flush=True)

        # Start Flask server in a separate thread to avoid blocking
        def start_flask():
            app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)

        flask_thread = threading.Thread(target=start_flask)
        flask_thread.start()

        while flask_thread.is_alive():
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run())
