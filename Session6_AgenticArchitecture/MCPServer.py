# basic import 
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

import sys
from DataStructures import SuggestedDish, WeatherDetails, WeatherInputs


# instantiate an MCP server client
mcp = FastMCP("FoodOrderAgent")

# DEFINE TOOLS

#Food order tool
@mcp.tool()
def order_food(input: SuggestedDish) -> bool:
    """Orders food that is passed as a parameter
    Param: SuggestedDish - pydantic structure having 'dish' as a key. Value is a string
     Eg: {"dish": "pizza"}
     Returns true on a succssful operation, else returns false"""
        
    # TODO - Implement the actual food ordering, using available APIs from food delivery companies
    #Since nothing is available as of now, just print and return true
    print(f"[ORDER_FOOD DEBUG] Ordered: {input.dish}", flush=True)
    return True

# Get weather tool
@mcp.tool()
def get_weather(input: WeatherInputs) -> WeatherDetails:
    """Gets weather for a given location and time
    Param: WeatherInputs - Pydantic data structure that contains variables -  time: str and place: str
      Eg: {"time": "now", "place": "bangalore"}  
    ReturnType - WeatherDetails - Pydantic data structure that contains variables - weather: str
      Eg: {"weather": "rainy"}
    """
    
    # TODO - Implement the actual weather getting tool 
    print(f"[GET_WEATHER DEBUG] Weather requested for time: {input.time}, place: {input.place}", flush=True)
    return WeatherDetails(weather = 'rainy')


# DEFINE RESOURCES

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    print(f"[GET_GREETING DEBUG] CALLED: get_greeting(name: str) -> str:", flush=True)
    return f"Hello, {name}!"


# DEFINE AVAILABLE PROMPTS
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"
    print(f"[REVIEW_CODE DEBUG] CALLED: review_code(code: str) -> str:", flush=True)


@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

if __name__ == "__main__":
    # Check if running with mcp dev command
    print("STARTING")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution