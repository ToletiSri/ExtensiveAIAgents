from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json
from typing import Dict, Any
from DataStructures import SuggestedDish, WeatherInputs

class MCPClient:
    def __init__(self):
        self.session = None
        self.tools = []
        self.tools_description = ""
        self._read = None
        self._write = None
        self._stdio_context = None
        self._session_cm = None

    async def __aenter__(self):
        print("Establishing connection to MCP server...", flush=True)
        server_params = StdioServerParameters(command="python", args=["MCPServer.py"])
        self._stdio_context = stdio_client(server_params)
        self._read, self._write = await self._stdio_context.__aenter__()
        print("Connection established, creating session...", flush=True)
        self._session_cm = ClientSession(self._read, self._write)
        self.session = await self._session_cm.__aenter__()
        print("Session created, initializing...", flush=True)
        await self.session.initialize()
        print("Requesting tool list...", flush=True)
        tools_result = await self.session.list_tools()
        self.tools = tools_result.tools

        desc_lines = []
        for i, tool in enumerate(self.tools):
            try:
                params = tool.inputSchema
                desc = getattr(tool, 'description', 'No description available')
                name = getattr(tool, 'name', f'tool_{i}')

                if 'properties' in params:
                    param_details = []
                    for param_name, param_info in params['properties'].items():
                        param_type = param_info.get('type', 'unknown')
                        param_details.append(f"{param_name}: {param_type}")
                    params_str = ', '.join(param_details)
                else:
                    params_str = 'no parameters'

                tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                desc_lines.append(tool_desc)
                print(f"Added description for tool: {tool_desc}", flush=True)
            except Exception as e:
                print(f"Error processing tool {i}: {e}", flush=True)
                desc_lines.append(f"{i+1}. Error processing tool")

        self.tools_description = "\n".join(desc_lines)
        print("Successfully created tools description", flush=True)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
        if self._stdio_context:
            await self._stdio_context.__aexit__(exc_type, exc_val, exc_tb)

    async def call_tool(self, tool_name, param_parts):
        """
        Calls the specified tool with the given parameters.
        """
        try:
            tool = next((t for t in self.tools if t.name == tool_name), None)
            if not tool:
                print(f"DEBUG: Available tools: {[t.name for t in self.tools]}", flush=True)
                raise ValueError(f"Unknown tool: {tool_name}")

            print(f"DEBUG: Found tool: {tool.name}", flush=True)
            print(f"DEBUG: Tool schema: {tool.inputSchema}", flush=True)

            arguments = self.parse_function_call_params(tool_name, param_parts)
            print(f"DEBUG: Final arguments: {arguments}", flush=True)
            print(f"DEBUG: Calling tool {tool_name} with arguments {arguments}", flush=True)
            result = await self.session.call_tool(tool_name, arguments=arguments)
            return result
        except Exception as e:
            print(f"DEBUG: Error calling tool {tool_name}: {e}", flush=True)
            raise ValueError(f"Failed to call tool {tool_name}: {e}")

   

    def parse_function_call_params(self, func_name, param_parts: dict) -> dict:
        """
        Creates the pydantic structure corresponding to the function, parsing the input dict as needed.
        """
        if isinstance(param_parts, str):
            try:
                print(f"[DEBUG] Attempting to load param_parts as JSON: {param_parts}", flush=True)
                param_parts = json.loads(param_parts)
                print(f"[DEBUG] Successfully loaded param_parts: {param_parts}", flush=True)
            except Exception as e:
                print(f"[DEBUG] Failed to parse param_parts as JSON: {e}", flush=True)
                raise ValueError(f"Failed to parse param_parts as JSON: {e}")

        if func_name == 'order_food':
            if isinstance(param_parts, dict):
                dish = param_parts.get('dish')
                if dish is None:
                    raise ValueError("Missing 'dish' in parameters for order_food")
                # Wrap in dict per tool schema
                return {"input": SuggestedDish(dish=dish).model_dump()}
            raise ValueError("param_parts must be a dict for order_food")
        elif func_name == 'get_weather':
            if isinstance(param_parts, dict):
                time = param_parts.get('time')
                place = param_parts.get('place')
                if time is None or place is None:
                    raise ValueError("Missing 'time' or 'place' in parameters for get_weather")
                # Wrap in dict per tool schema
                return {"input": WeatherInputs(time=time, place=place).model_dump()}
            raise ValueError("param_parts must be a dict for get_weather")
        else:
            raise ValueError(f"Unknown function name: {func_name}")

    def get_tools_description(self):
        return self.tools_description
