from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json
from typing import Dict, Any
from DataStructures import SuggestedDish, WeatherInputs
import asyncio

class MCPClient:
    def __init__(self):
        self.tools = []
        self.tools_description = ""
        # Initialize MCP session and cache tools
        server_params = StdioServerParameters(command="python", args=["MCPServer.py"])
        async def _init():
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools_result = await session.list_tools()
                    self.tools = tools_result.tools
                    # Build tools description
                    desc_lines = []
                    for i, tool in enumerate(self.tools):
                        try:
                            params = tool.inputSchema
                            desc = getattr(tool, 'description', 'No description available')
                            name = getattr(tool, 'name', f'tool_{i}')
                            if 'properties' in params:
                                param_details = []
                                for k,v in params['properties'].items():
                                    t = v.get('type','unknown')
                                    param_details.append(f"{k}: {t}")
                                params_str = ', '.join(param_details)
                            else:
                                params_str = 'no parameters'
                            desc_lines.append(f"{i+1}. {name}({params_str}) - {desc}")
                        except Exception:
                            desc_lines.append(f"{i+1}. Error processing tool")
                    self.tools_description = "\n".join(desc_lines)
        asyncio.run(_init())

    async def call_tool(self, tool_name, param_parts):
        """
        Calls the specified tool with the given parameters.
        """
        try:
            server_params = StdioServerParameters(command="python", args=["MCPServer.py"])
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    # Use cached tools list from initialization
                    print(f"DEBUG: Available tools (cached): {[t.name for t in self.tools]}", flush=True)
                    # Ensure tool exists
                    tool = next((t for t in self.tools if t.name == tool_name), None)
                    if not tool:
                        print(f"DEBUG: Tool not found in cache: {tool_name}", flush=True)
                        raise ValueError(f"Unknown tool: {tool_name}")
                    print(f"DEBUG: Found tool: {tool.name}", flush=True)
                    print(f"DEBUG: Tool schema: {tool.inputSchema}", flush=True)
                    arguments = self.parse_function_call_params(tool_name, param_parts)
                    print(f"DEBUG: Final arguments: {arguments}", flush=True)
                    print(f"DEBUG: Calling tool {tool_name} with arguments {arguments}", flush=True)
                    result = await session.call_tool(tool_name, arguments=arguments)
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
                place = param_parts.get('place')
                if place is None:
                    raise ValueError("Missing 'place' in parameters for get_weather")
                # Wrap in dict per tool schema
                return {"input": WeatherInputs(place=place).model_dump()}
            raise ValueError("param_parts must be a dict for get_weather")
        else:
            raise ValueError(f"Unknown function name: {func_name}")

    def get_tools_description(self):
        return self.tools_description
