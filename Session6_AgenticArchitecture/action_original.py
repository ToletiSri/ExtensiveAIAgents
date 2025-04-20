# basic import 
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

from DataStructures import SuggestedDish, WeatherInputs

def parse_function_call_params(func_name, param_parts: dict) -> dict:
    """
    Creates the pydantic structure corresponding to the function, parsing the input dict as needed.
    Accepts a dict or a JSON string as param_parts.
    """
    # If param_parts is a JSON string, parse it
    if isinstance(param_parts, str):
        try:
            print(f"[DECISION DEBUG] Attempting to load param_parts as JSON: {param_parts}", flush=True)
            param_parts = json.loads(param_parts)
            print(f"[DECISION DEBUG] Successfully loaded param_parts: {param_parts}", flush=True)
        except Exception as e:
            print(f"[DECISION DEBUG] Failed to parse param_parts as JSON: {e}", flush=True)
            raise ValueError(f"Failed to parse param_parts as JSON: {e}")

    if func_name == 'order_food':
        # Expecting param_parts to be a dict with key 'dish'
        print(f"[DECISION DEBUG] order_food param_parts: {param_parts}", flush=True)
        if isinstance(param_parts, dict):
            dish = param_parts.get('dish')
            print(f"[DECISION DEBUG] order_food dish: {dish}", flush=True)
            if dish is None:
                raise ValueError("Missing 'dish' in parameters for order_food")
            return SuggestedDish(dish=dish)
        else:
            print(f"[DECISION DEBUG] order_food param_parts is not a dict: {type(param_parts)}", flush=True)
            raise ValueError("param_parts must be a dict for order_food")
    elif func_name == 'get_weather':
        # Expecting param_parts to be a dict with keys 'time' and 'place'
        print(f"[DECISION DEBUG] get_weather param_parts: {param_parts}", flush=True)
        if isinstance(param_parts, dict):
            time = param_parts.get('time')
            place = param_parts.get('place')
            print(f"[DECISION DEBUG] get_weather time: {time}, place: {place}", flush=True)
            if time is None or place is None:
                raise ValueError("Missing 'time' or 'place' in parameters for get_weather")
            return WeatherInputs(time=time, place=place)
        else:
            print(f"[DECISION DEBUG] get_weather param_parts is not a dict: {type(param_parts)}", flush=True)
            raise ValueError("param_parts must be a dict for get_weather")
    else:
        print(f"[DECISION DEBUG] Unknown function name: {func_name}", flush=True)
        raise ValueError(f"Unknown function name: {func_name}")

async def takeActionFunctionCall(func_name, param_parts):
    """
    This function calls the appropriate function from MCP tools
    """
    
    try:
        tool = next((t for t in tools if t.name == func_name), None)
        if not tool:
            print(f"DEBUG: Available tools: {[t.name for t in tools]}", flush=True)
            raise ValueError(f"Unknown tool: {func_name}")

        print(f"DEBUG: Found tool: {tool.name}", flush=True)
        print(f"DEBUG: Tool schema: {tool.inputSchema}", flush=True)

        arguments = parse_function_call_params(func_name, param_parts)
        print(f"DEBUG: Final arguments: {arguments}", flush=True)
        print(f"DEBUG: Calling tool {func_name}", flush=True)

        result = await session.call_tool(func_name, arguments=arguments)

    except Exception as e:
        print(f"DEBUG: Error calling tool {func_name}: {e}", flush=True)
        raise ValueError(f"Failed to call tool {func_name}: {e}")

    return result


def get_mcp_tools():
    return tools_description  # Referring to the same global variable as in connectToMCPServer


async def connectToMCPServer():
    global tools_description, session, tools

    tools_description = []

    try:
        print("Establishing connection to MCP server...", flush=True)
        server_params = StdioServerParameters(
            command="python",
            args=["MCPServer.py"]
        )

        # Keep stdio_client as async context manager
        async with stdio_client(server_params) as (read, write):
            print("Connection established, creating session...")

            # Manually assign to global session (NO 'async with')
            session = ClientSession(read, write)
            await session.__aenter__()  # Open the session

            print("Session created, initializing...")
            await session.initialize()

            print("Requesting tool list...", flush=True)
            tools_result = await session.list_tools()
            tools = tools_result.tools
            print(f"Successfully retrieved {len(tools)} tools", flush=True)

            for i, tool in enumerate(tools):
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
                    tools_description.append(tool_desc)
                    print(f"Added description for tool: {tool_desc}", flush=True)
                except Exception as e:
                    print(f"Error processing tool {i}: {e}", flush=True)
                    tools_description.append(f"{i+1}. Error processing tool")

            tools_description = "\n".join(tools_description)
            print("Successfully created tools description", flush=True)

    except Exception as e:
        print(f"Failed to get tools: {e}", flush=True)
        raise ValueError(f"Failed to get tools: {e}")

