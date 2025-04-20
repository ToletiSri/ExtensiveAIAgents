import google.generativeai as genai
from DataStructures import SuggestedDish, WeatherDetails, WeatherInputs
from action import takeActionFunctionCall, get_mcp_tools
import os

import asyncio
from concurrent.futures import TimeoutError
import json
import ast

# Access your API key and initialize Gemini client correctly
api_key=os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=api_key)
model_decision = genai.GenerativeModel('gemini-2.0-flash-exp')

max_iterations = 7
last_response = None
iteration = 0
iteration_response = []



async def generate_with_timeout(prompt, timeout=10):
    """Generate content with a timeout"""
    print("[DECISION DEBUG] Starting LLM generation...", flush=True)
    try:
        # Convert the synchronous generate_content call to run in a thread
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: model_decision.generate_content(prompt)
            ),
            timeout=timeout
        )
        print("[DECISION DEBUG] LLM generation completed", flush=True)
        return response
    except TimeoutError:
        print("[DECISION DEBUG] LLM generation timed out!", flush=True)
        raise
    except Exception as e:
        print(f"[DECISION DEBUG] Error in LLM generation: {e}", flush=True)
        raise

def reset_state():
    """Reset all global variables to their initial state"""
    global last_response, iteration, iteration_response
    last_response = None
    iteration = 0
    iteration_response = []

async def process_order_facts(facts, memory=None):
    """
    Receives the output from extract_facts (likely a UserOrder or dict).
    Optionally receives the shared memory object from main.py.
    Returns a decision or suggestion (stub for now).
    """
    print(f"[DECISION DEBUG] Received facts: {facts}", flush=True)
    # Example: facts could be a dict or a pydantic model
    if hasattr(facts, 'model_dump'):
        facts = facts.model_dump()
    print(f"[DECISION DEBUG] Facts after model_dump: {facts}", flush=True)
    # Use the shared memory object if provided
    if memory is not None:
        pref = memory.getPreference()
        pref_dict = {'cuisine': pref.cuisine, 'is_vegetarian': pref.is_vegetarian} if pref else None
    else:
        pref_dict = None
    print(f"[DECISION DEBUG] User preference: {pref_dict}", flush=True)
    # Implement your decision logic here

    # Ensure tools are fetched and description generated
    tools_description = await get_mcp_tools()
    print(f"[DECISION DEBUG] Available tools: {tools_description}", flush=True)

    system_prompt = f"""
    You are a Food suggestion and ordering agent, either suggesting food items 
    either suggesting food items to the user or ordering food items for the user.
    
    You are given the user query as a json and memory as a dictionary.
    
    You also have access to various tools.
    
    Available tools:
    {tools_description}
    
    You must respond with EXACTLY ONE line in one of these formats (no additional text):
    
    1. For function calls:
    FUNCTION_CALL: function_name|<JSON string>
    
    2. For final suggestion:
    FINAL_SUGGESTION: [string]
    
    IMPORTANT:
    
    - When a function returns multiple values, you need to process all of them
    - Only give FINAL_SUGGESTION when you have completed all necessary function calls
    - Do not repeat function calls with the same parameters
    - FINAL_SUGGESTION is the final output to user. It either summarises the order for the user, or suggest the food and give brief description on decision criteria like weather or mood if available. Present this well
    
    Examples:
    
    - FUNCTION_CALL: order_food|{{"dish": "fries"}}
    - FUNCTION_CALL: get_weather|{{"time": "now", "place": "bangalore"}}
    - FINAL_SUGGESTION: 'We suggest you order some fries as the weather is rainy'
    - FINAL_SUGGESTION: 'We suggest you a hot cup of chamomile tea as you are feeling stressed'
    - FINAL_SUGGESTION: 'We have ordered the popular benne masala dosa for your breakfast! Enjoy your meal!!'
    
    DO NOT include any explanations or additional text.
    Your entire response should be a single line starting with either FUNCTION_CALL: or FINAL_SUGGESTION:
    """

    query = f"""User query: {facts}, MEMORY: {pref_dict}"""

                
    # Use global iteration variables
    global iteration, last_response
                
    while iteration < max_iterations:
                    print(f"\n--- Iteration {iteration + 1} ---", flush=True)
                    if last_response is None:
                        current_query = query
                    else:
                        current_query = current_query + "\n\n" + " ".join(iteration_response)
                        current_query = current_query + "  What should I do next?"

                    # Get model's response with timeout
                    print("Preparing to generate LLM response...", flush=True)
                    prompt = f"{system_prompt}\n\nQuery: {current_query}"
                    try:
                        response = await generate_with_timeout(prompt)
                        response_text = response.text.strip()
                        print(f"LLM Response: {response_text}", flush=True)
                        
                        # Find the FUNCTION_CALL line in the response
                        for line in response_text.split('\n'):
                            line = line.strip()
                            if line.startswith("FUNCTION_CALL:"):
                                response_text = line
                                break
                        
                    except Exception as e:
                        print(f"Failed to get LLM response: {e}", flush=True)
                        break


                    if response_text.startswith("FUNCTION_CALL:"):
                        try:
                            _, function_info = response_text.split(":", 1)
                            parts = [p.strip() for p in function_info.split("|")]
                            func_name, param_parts = parts[0], parts[1:]
                            print(f"\nDEBUG: Raw function info: {function_info}", flush=True)
                            print(f"DEBUG: Split parts: {parts}", flush=True)
                            print(f"DEBUG: Function name: {func_name}", flush=True)
                            print(f"DEBUG: Raw parameters: {param_parts}", flush=True)  

                            result = await takeActionFunctionCall(func_name, param_parts)
                            print(f"DEBUG: Raw result: {result}", flush=True)

                            if hasattr(result, 'content'):
                                print(f"DEBUG: Result has content attribute", flush=True)
                                if isinstance(result.content, list):
                                    iteration_result = [
                                        item.text if hasattr(item, 'text') else str(item)
                                        for item in result.content
                                    ]
                                else:
                                    iteration_result = str(result.content)
                            else:
                                print(f"DEBUG: Result has no content attribute", flush=True)
                                iteration_result = str(result)

                            print(f"DEBUG: Final iteration result: {iteration_result}", flush=True)

                            result_str = f"[{', '.join(iteration_result)}]" if isinstance(iteration_result, list) else str(iteration_result)

                            iteration_response.append(
                                f"In the {iteration + 1} iteration you called {func_name} with {param_parts} parameters, "
                                f"and the function returned {result_str}."
                            )
                            last_response = iteration_result

                        except Exception as e:
                            print(f"DEBUG: Error details: {str(e)}", flush=True)
                            print(f"DEBUG: Error type: {type(e)}", flush=True)
                            import traceback
                            traceback.print_exc()
                            iteration_response.append(f"Error in iteration {iteration + 1}: {str(e)}")
                            break


                    elif response_text.startswith("FINAL_ANSWER:"):
                        print("\n=== Agent Execution Complete ===", flush=True)
                        # Remove FINAL_DESCRIPTION: from response_text and print it
                        final_suggestion = response_text.replace("FINAL_DESCRIPTION:", "").strip()
                        print("\n=== Returning final suggestion ===", flush=True)
                        return final_suggestion




def get_user_cuisine_preference(memory):
    """
    Fetches the user's cuisine preference from the provided memory object
    """
    pref = memory.getPreference()
    if pref is None:
        return None
    return {'cuisine': pref.cuisine, 'is_vegetarian': pref.is_vegetarian}
