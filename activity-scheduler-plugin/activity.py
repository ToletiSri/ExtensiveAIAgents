from UtilityFunctions import (
    send_reminder_email, 
    add_calendar_invite, 
    send_stock_email, 
    schedule_daily_stock_email
)
import google.generativeai as genai
import json
from datetime import datetime, timedelta

# Configure Gemini AI
google_api_key = "YOUR_API_KEY"  # Replace with your API key
genai.configure(api_key=google_api_key)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

def process_input(user_text):
    prompt = f'''You are a AI assistant. Your job is to break a task into smaller 
    tasks that could be executed as code. Do not write the code, but just list the tasks as steps.
    Here is your task - {user_text}'''
    
    response = model.generate_content(prompt)
    tasks = response.text.split('\n')
    
    # Get function descriptions for available functions
    functions_list = [
        send_reminder_email.__doc__,
        add_calendar_invite.__doc__,
        send_stock_email.__doc__,
        schedule_daily_stock_email.__doc__
    ]
    
    prompt2 = f'''You are a AI assistant. Generate Python function calls for these steps using only these functions:
    {functions_list}
    Steps: {tasks}
    Return only the function calls, one per line.'''
    
    response2 = model.generate_content(prompt2)
    function_calls = [call.strip() for call in response2.text.split('\n') if call.strip()]
    
    return function_calls

def execute_task(task):
    try:
        # Create a new local dictionary for execution
        local_dict = {}
        # Execute in the context of available functions
        exec(f"result = {task}", globals(), local_dict)
        return str(local_dict.get('result', 'Task executed successfully'))
    except Exception as e:
        return f"Error: {str(e)}"