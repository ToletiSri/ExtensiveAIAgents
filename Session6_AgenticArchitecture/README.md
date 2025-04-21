# Session 6: Agentic Architecture

This repo demonstrates a structured, layered AI‐agent design in Python, following Class 6’s four cognitive layers:
Perception, Memory, Decision‐Making and Action.

## 📖 Overview of class 6:

The agent is structured in 4 cognitive layers:
1. **Perception** (`perception.py`): Extracts structured info from raw input via an LLM.
2. **Memory** (`memory.py`): Stores/retrieves user facts and state (JSON/YAML).
3. **Decision-Making** (`decision.py`): Plans next steps using input + memory.
4. **Action** (`action.py`): Executes choices (LLM response, API call, file/calendar write).



## 💻 Application for Assignment

To demonstrate the assignment, we implement an agentic food-ordering application.
This agentic food-ordering application is implemented as a Chrome extension (see `chrome_plugin/`).

**Popup UI Features:**
- **Order Input:** a text field (`#orderInput`) for natural-language requests.
- **Settings Panel:** toggled by the ⚙️ button, lets users set cuisine preference and vegetarian toggle.
- **Submit Button:** sends the order to the Flask backend (`/order`).
- **Response Box:** displays the agent’s final confirmation and reasoning.

**Key Capabilities:**
- **Preferences Management:** saves/retrieves cuisine preference and vegetarian flags via `/preference` endpoints.
- **Natural-Language Ordering:** free-form requests parsed by the Perception layer.
- **Iterative Planning:** chain-of-thought tool calls (order_food, get_weather) via the Action layer.
- **Real-Time Feedback:** shows function-call logs and final suggestion directly in the popup.

## 📝 Agentic Architecture Implemented in this assignment

### 1. Perception Layer (`perceive.py`)
- **Input**: raw user string (e.g. "Order pizza this evening").
- **LLM Call**: prompts Google Gemini to extract `mood`, `time`, `action` keys in a plain Python dict.
- **Parsing**: strips code fences, uses `ast.literal_eval`, wraps into `DataStructures.UserOrder` (Pydantic).

### 2. Memory Layer (`memory.py`)
- **Stores**: user cuisine preference and vegetarian flag in a singleton `Memory` object.
- **API**: `addPreference(dict)` → saves a `CuisinePreference`; `getPreference()` → returns it or `None`.
- **Scope**: in-memory only; persisted until process restarts.

### 3. Decision-Making Layer (`decision.py`)
- **Entry**: `process_order_facts(facts, memory, mcpClient)`.
- **Steps**:
  1. Normalize facts (`.model_dump()` if Pydantic).
  2. Retrieve memory → build `pref_dict`.
  3. Fetch & describe MCP tools via `mcpClient.get_tools_description()`.
  4. Compose strict system prompt with tool list and response format (`FUNCTION_CALL:`, `INTERMEDIATE_RESULT_FOOD_SUGGESTION:`, `FINAL_RESULT:`).
  5. Loop up to `max_iterations`: send prompt → parse single-line response → call tools or collect suggestions → on `FINAL_RESULT` return final string.

### 4. Action Layer (`action.py` & `MCPServer.py`)
- **MCPClient**:
  - Launches `MCPServer.py` over stdio, caches tool schemas.
  - `parse_function_call_params` wraps JSON into Pydantic `.model_dump()` for `order_food` and `get_weather`.
  - `call_tool(name, params)` reconnects, finds tool, invokes it, returns result.
- **MCPServer Tools**:
  - `order_food(SuggestedDish) -> bool`: stub prints debug and returns `True`.
  - `get_weather(WeatherInputs) -> WeatherDetails`: calls OpenWeather API (`OPEN_WEATHER_KEY`), returns weather + description.
  - Additional: dynamic greeting resource, code-review and debug prompts.

### 5. Orchestration (`main.py`)
- **Flask API**:
  - `POST /preference`: `memory.addPreference` stores cuisine and veg flag.
  - `GET /preference`: returns saved preferences.
  - `POST /order`: extracts `order_text`, runs `extract_facts` → `process_order_facts` via `asyncio.run`, returns `FINAL_RESULT`.
- **Initialization**: `init_mcp()` creates global `MCPClient` so tools are loaded once.

### 🔖 Summary
- **Layers**: perception (LLM→Pydantic), memory (in-process prefs), decision (iterative LLM planning), action (tool calls via MCP), orchestration (Flask endpoints).
- **Flow**: User sets preferences → agent perceives order → reasons over facts + memory → calls tools → returns final confirmation.

---
Enjoy extending and experimenting with the layered AI agent!

## 🔧 Prerequisites

- Python 3.10+
- (optional) virtualenv
- Google Gemini API key in `.env`:
  ```env
  GOOGLE_API_KEY=your_key_here
```
- Open Weather API key in `.env`:
  ```env
  OPEN_WEATHER_KEY=your_key_here
```

## 🚀 Installation & Running

1. **Clone & env**
   ```bash
   git clone <repo_url>
   cd Session6_AgenticArchitecture
   cp .env.example .env   # fill GOOGLE_API_KEY, OPEN_WEATHER_KEY
   ```
2. **Install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
   pip install -r requirements.txt
   ```
3. **Start backend**
   ```bash
   python main.py
   ```
   The Flask server will listen on http://127.0.0.1:5000.
4. **Load Chrome extension**
   - Open `chrome://extensions/` in Chrome
   - Enable **Developer mode**
   - Click **Load unpacked** and select the `chrome_plugin/` folder
   - Click the extension icon to open the popup UI and interact with the agent
