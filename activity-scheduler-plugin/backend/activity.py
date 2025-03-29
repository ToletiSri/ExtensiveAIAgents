import google.generativeai as genai
from datetime import datetime, timedelta
import traceback
import sys

from UtilityFunctions import (
            send_reminder_email,
            add_calendar_invite,
            get_stock_price,
            schedule_daily_stock_email
        )

# Configure the Google Generative AI API
genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-exp')


functions = 'function - send_reminder_email - ' +  send_reminder_email.__doc__ + ''' 
\n function - add_calendar_invite - ''' +  add_calendar_invite.__doc__ + '''
\n function - get_stock_price - ''' +  get_stock_price.__doc__ + '''
\n function - schedule_daily_stock_email - ''' +  schedule_daily_stock_email.__doc__ 

# Get model's response
system_prompt = f"""You are a AI assistant decomposing a  task in iterations.   
Respond with EXACTLY ONE of these formats:
1. FUNCTION_CALL: python_function_name|input1,input2,...
2. FINAL_ANSWER: [text]

where python_function_name is one of the following functions:
{functions}"""


def function_caller(func_name, params):
    """
    Call a function by name with given parameters.
    """
    try:
        # Get the function from the imported functions
        available_functions = {
            'send_reminder_email': send_reminder_email,
            'add_calendar_invite': add_calendar_invite,
            'get_stock_price': get_stock_price,
            'schedule_daily_stock_email': schedule_daily_stock_email
        }
        
        if func_name not in available_functions:
            return f"Error: Function '{func_name}' not found"
            
        func = available_functions[func_name]
        
        # Parse parameters
        if params.strip():
            param_list = [p.strip() for p in params.split(',')]
        else:
            param_list = []
            
        # Call the function with parameters
        result = func(*param_list)
        return str(result)
        
    except Exception as e:
        error_msg = f"Error calling {func_name}: {str(e)}"
        print(error_msg)
        print("Traceback:", traceback.format_exc())
        return error_msg


def decompose_task(task):
    """
    Decompose a task into a list of function calls using Google's Generative AI.
    """
    try:     
        max_iterations = 3
        last_response = None
        iteration = 0
        iteration_response = []        

        prompt = f"{system_prompt}\n\nTask: {task}"
        
        while iteration < max_iterations:
            print(f"\n--- Iteration {iteration + 1} ---")
            if last_response == None:
                current_query = task
            else:
                current_query = current_query + "\n\n" + " ".join(iteration_response)
                current_query = current_query + "  What should I do next?"

            # Get model's response
            prompt = f"{system_prompt}\n\nQuery: {current_query}"
            try:
                response = model.generate_content(prompt)
                response_text = response.text.strip()
                print(f"LLM Response: {response_text}")
            except Exception as error:
                print(f"Failed to connect to Gemini API: {error}")
                raise  # Re-raise the exception after logging
            
            if response_text.startswith("FUNCTION_CALL:"):
                response_text = response.text.strip()
                _, function_info = response_text.split(":", 1)
                func_name, params = [x.strip() for x in function_info.split("|", 1)]
                iteration_result = function_caller(func_name, params)

            # Check if it's the final answer
            elif response_text.startswith("FINAL_ANSWER:"):
                print("\n=== Agent Execution Complete ===")
                break
                

            print(f"  Result: {iteration_result}")
            last_response = iteration_result
            iteration_response.append(f"In the {iteration + 1} iteration you called {func_name} with {params} parameters, and the function returned {iteration_result}.")

            iteration += 1
    
    except Exception as e:
        print("Error in decompose_task:", str(e))
        print("Traceback:", traceback.format_exc())
        raise

def execute_task(task):
    """
    Execute a single task function call.
    """
    try:
        from UtilityFunctions import (
            send_reminder_email,
            add_calendar_invite,
            send_stock_email,
            schedule_daily_stock_email
        )
        
        # Get the function from the global namespace
        func = globals()[task['function']]
        
        # Call the function with the provided arguments
        result = func(*task['args'], **task['kwargs'])
        
        return f"Successfully executed {task['function']}"
    except Exception as e:
        print("Error in execute_task:", str(e))
        print("Task:", task)
        print("Traceback:", traceback.format_exc())
        raise