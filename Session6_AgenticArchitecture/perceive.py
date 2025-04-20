import os
import google.generativeai as genai
import ast
from DataStructures import UserOrder
import json

# Access your API key and initialize Gemini client correctly
api_key=os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

def extract_facts(message):
    """Extract facts from a message using Gemini LLM and return a UserOrder."""
    if not api_key:
        raise EnvironmentError("GOOGLE_API_KEY environment variable not set.")

    prompt = (
        "Extract the user's mood, time, and action from the following message. "
        "Return a valid Python dictionary with keys: mood, time, action. Give 'unknown' as value if any value is not known. "
        "Time could also include - morning, afternoon, evening, night, breakfast, lunch, dinner, late night, midnight. "
        "The action value should be detailed and descriptive enough."
        "Do NOT include any explanations or formatting, just output the Python dictionary. "
        f"Message: \"{message}\""
    )

    response = model.generate_content(prompt)
    
    response_text = response.text.strip()

    # Clean code block markers, 'python', and extra whitespace
    if response_text.startswith('```'):
        lines = response_text.splitlines()
        # Remove first line if it's a code block marker or language hint
        if lines[0].strip().startswith('```'):
            lines = lines[1:]
        # Remove last line if it's a code block marker
        if lines and lines[-1].strip().startswith('```'):
            lines = lines[:-1]
        # Remove 'python' language hint if present
        if lines and lines[0].strip().lower() == 'python':
            lines = lines[1:]
        response_text = '\n'.join(lines).strip()

    try:
        facts = ast.literal_eval(response_text)
        # Ensure both 'action' and 'preference' keys are supported for backward compatibility
        return UserOrder(
            mood=facts.get("mood", ""),
            time=facts.get("time", ""),
            action=facts.get("action")
        )
    except Exception as e:
        raise ValueError(f"Failed to parse Gemini response as Python dict: {response_text}") from e