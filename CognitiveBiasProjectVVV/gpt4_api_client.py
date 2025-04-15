import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file (if any)
load_dotenv()

def sendMessage(prompt):
    """
    Sends a message to the OpenAI O1 API and returns the response content.
    
    Args:
        prompt (str): The message prompt to send to the API
        
    Returns:
        str: The message content from the API response or error message
    """
    # Get API key from environment variable or use the one provided
    api_key = os.getenv("OPENAI_API_KEY", "APIKEY")

    # Define the API endpoint
    url = "https://api.openai.com/v1/chat/completions"

    # Define headers with authentication
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Define the request payload
    payload = {
        "model": "gpt-4-0613",
        "temperature": 1,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        # Make the API call using requests
        response = requests.post(url, headers=headers, json=payload)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the JSON response
        response_data = response.json()
        
        # Return the completion
        if "choices" in response_data and len(response_data["choices"]) > 0:
            print(response_data['model'])
            return response_data["choices"][0]["message"]["content"]
        else:
            return f"No completion found in the response: {response_data}"
    except Exception as e:
        return f"Error calling the API: {e}"


# Example usage (only runs if this file is executed directly)
if __name__ == "__main__":
    result = sendMessage("Write a one-sentence bedtime story about a unicorn.")
    print(result)