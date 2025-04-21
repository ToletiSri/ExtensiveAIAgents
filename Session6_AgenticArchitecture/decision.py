import google.generativeai as genai
import os
import asyncio
from concurrent.futures import TimeoutError
from action import MCPClient
from dotenv import load_dotenv
load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.environ.get('GOOGLE_API_KEY')
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


async def process_order_facts(facts, memory=None, mcpClient: MCPClient=None):
    """
    Receives the output from extract_facts (likely a UserOrder or dict).
    Optionally receives the shared memory object from main.py.
    Returns a decision or suggestion (stub for now).
    """
    reset_state()
    print(f"[DECISION DEBUG] Received facts: {facts}", flush=True)
    
    if hasattr(facts, 'model_dump'):
        facts = facts.model_dump()
    print(f"[DECISION DEBUG] Facts after model_dump: {facts}", flush=True)

       
    # Use the shared memory object if provided
    pref_dict = None
    if memory is not None:
        pref = memory.getPreference()
        pref_dict = {'cuisine': pref.cuisine, 'is_vegetarian': pref.is_vegetarian} if pref else None
    print(f"[DECISION DEBUG] User preference: {pref_dict}", flush=True)

    # Ensure tools are fetched and description generated
    tools_description = mcpClient.get_tools_description()
    print(f"[DECISION DEBUG] Available tools: {tools_description}", flush=True)

    system_prompt = f"""
    You are a Food ordering agent, ordering food items for the user. Your job is to first check the user order and then make a decision based on the user order. 
    You are given the user order as a json string and user preferences as a dictionary. Assume that the current location is bangalore
    
    You also have access to the following tool functions:
    {tools_description}
    
    You can call the functions from list above depending on the action from json user query. You must respond with EXACTLY ONE line in one of these formats (no additional text):
    
    1. For function calls:
    FUNCTION_CALL: function_name|<JSON string>

    2. For intermediate food suggestion:
    INTERMEDIATE_RESULT_FOOD_SUGGESTION: [string]
    
    3. For final suggestion:
    FINAL_RESULT: [string]

    
    IMPORTANT:
    - Only give FINAL_RESULT when you have completed all necessary function calls
    - Make sure you have checked all the functions that you need to call based on the action key from user    
    - Do not repeat function calls with the same parameters
    - FINAL_RESULT is the final output to user. It summarises the order for the user. This also describes how the decision was made. Present this well
    
    Examples:
    
    - FUNCTION_CALL: order_food|{{"dish": "fries"}}
    - FUNCTION_CALL: get_weather|{{"time": "now", "place": "bangalore"}}
    - INTERMEDIATE_RESULT_FOOD_SUGGESTION: 'Because you are feeling stressed, we suggest ordering chamomile tea'
    - FINAL_RESULT: 'We have ordered the popular benne masala dosa for your breakfast! Enjoy your meal!!'
    
    DO NOT include any explanations or additional text.
    Your entire response should be a single line starting with either FUNCTION_CALL: or FINAL_SUGGESTION:
    """

    query = f"""User query: {facts}, MEMORY: {pref_dict}"""

    # Use global iteration variables
    global iteration, last_response

    while iteration < max_iterations:
        print(f"\n--- Iteration {iteration + 1} ---", flush=True)
        
        # Update query for this iteration
        if last_response is None:
            current_query = query
        else:
            current_query = current_query + "\n\n" + " ".join(iteration_response)
            current_query = current_query + "  What should I do next?"

        # Prepare the prompt for the LLM model
        print("Preparing to generate LLM response...", flush=True)
        prompt = f"{system_prompt}\n\nQuery: {current_query}"
        
        try:
            response = await generate_with_timeout(prompt)
            response_text = response.text.strip()
            print(f"LLM Response: {response_text}", flush=True)
            
            
       

            # Process FUNCTION_CALL or FINAL_SUGGESTION
            if response_text.startswith("FUNCTION_CALL:"):
                try:
                    _, function_info = response_text.split(":", 1)
                    parts = [p.strip() for p in function_info.split("|")]
                    func_name, param_parts = parts[0], parts[1]
                    print(f"\nDEBUG: Raw function info: {function_info}", flush=True)
                    print(f"DEBUG: Split parts: {parts}", flush=True)
                    print(f"DEBUG: Function name: {func_name}", flush=True)
                    print(f"DEBUG: Raw parameters: {param_parts}", flush=True)

                    result = await mcpClient.call_tool(func_name, param_parts)
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


            elif response_text.startswith("FINAL_RESULT:"):
                print("\n=== Agent Execution Complete ===", flush=True)
                # Remove FINAL_RESULT: from response_text and return it
                final_suggestion = response_text.replace("FINAL_RESULT:", "").strip()
                print("\n=== Returning final result ===", flush=True)
                return final_suggestion

            elif response_text.startswith("INTERMEDIATE_RESULT_FOOD_SUGGESTION:"):
                # Remove FINAL_RESULT: from response_text and return it
                iteration_result = response_text.replace("INTERMEDIATE_RESULT_FOOD_SUGGESTION:", "").strip()
                print(f"DEBUG: INTERMEDIATE_RESULT_FOOD_SUGGESTION: {iteration_result}", flush=True)
                result_str = f"[{', '.join(iteration_result)}]" if isinstance(iteration_result, list) else str(iteration_result)
                iteration_response.append(
                    f"In the {iteration + 1} iteration you called {func_name} with {param_parts} parameters, "
                    f"and the function returned {result_str}."
                )
                last_response = iteration_result
            iteration += 1

        except Exception as e:
            print(f"Failed to get LLM response: {e}", flush=True)
            break


def get_user_cuisine_preference(memory):
    """
    Fetches the user's cuisine preference from the provided memory object
    """
    pref = memory.getPreference()
    if pref is None:
        return None
    return {'cuisine': pref.cuisine, 'is_vegetarian': pref.is_vegetarian}
