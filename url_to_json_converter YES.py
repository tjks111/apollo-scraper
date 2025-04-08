import requests
import sys
import json
import urllib.parse

def convert_url_to_json(url):
    """Send the URL to OpenAI for conversion to JSON"""
    # OpenAI API endpoint
    openai_url = "https://api.openai.com/v1/chat/completions"
    
    # Get API key from environment variable or prompt user
    import os
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # If API key is not set in environment, prompt user
    if not api_key:
        print("OPENAI_API_KEY environment variable not found.")
        print("Please set this environment variable or enter your API key now:")
        api_key = input("OpenAI API Key: ").strip()
        
        if not api_key:
            raise ValueError("API key is required to use this tool")
    
    # Headers for the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Payload for the API request - using the chat completions endpoint format
    payload = {
        "model": "gpt-4",  # Using a standard model that's widely available
        "messages": [
            {
                "role": "system",
                "content": "Convert the query string from the provided Apollo URL into a JSON object with keys formatted in snake_case. Follow these rules:\n\n1. Extract the query parameters from the URL, especially if they appear after the # fragment.\n2. Decode URL-encoded characters (e.g., %5B → [, %20 → space).\n3. Remove unnecessary square brackets ([]) from the keys.\n4. Convert all keys to snake_case format (e.g., finderViewId → finder_view_id).\n5. Replace spaces and hyphens with underscores.\n6. Add these additional key-value pairs:\n   - \"prospected_by_current_team\": [\"yes\"]\n   - \"per_page\": 100\n7. Exclude these keys from the output:\n   - sort_by_field\n   - sort_ascending\n8. Output as a well-formatted JSON string with proper indentation. Do NOT give any other text other than the JSON string"
            },
            {
                "role": "user",
                "content": url
            }
        ],
        "temperature": 0.7,
        "max_tokens": 2048,
        "top_p": 1
    }
    
    try:
        # Send the request to OpenAI
        response = requests.post(openai_url, headers=headers, json=payload)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        
        # Extract the converted JSON from the response using the standard chat completions format
        if "choices" in result and len(result["choices"]) > 0 and "message" in result["choices"][0]:
            response_text = result["choices"][0]["message"]["content"]
            
            # Try to parse the response as JSON to validate it
            try:
                # Check if the response is already valid JSON
                json_obj = json.loads(response_text)
                # If it is, return it as a formatted string
                return json.dumps(json_obj, indent=2)
            except json.JSONDecodeError:
                # If not valid JSON, return the raw text
                return response_text
        else:
            return f"Error: Unexpected response format: {json.dumps(result, indent=2)}"
            
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to send request to OpenAI: {str(e)}"
    except json.JSONDecodeError as e:
        return f"Error: Failed to parse response from OpenAI: {str(e)}"
    except Exception as e:
        return f"Error: An unexpected error occurred: {str(e)}"

def main():
    # Get the URL from User_Inputs.json
    print("\nApollo URL to JSON Converter (YES)")
    print("================================\n")
    print("This tool converts Apollo URLs to JSON format with snake_case keys.")
    print("Reading Apollo URL from User_Inputs.json...")
    
    try:
        # Read the URL from User_Inputs.json
        with open("User_Inputs.json", "r") as f:
            user_inputs = json.load(f)
            url = user_inputs.get("apollo_url", "")
        
        if not url:
            print("Error: No apollo_url found in User_Inputs.json")
            return
            
        print(f"Using URL: {url}")
    except Exception as e:
        print(f"Error reading User_Inputs.json: {str(e)}")
        return
    
    # Basic validation - just make sure we have some input
    if not url or url.strip() == "":
        print("Error: Please enter a valid URL")
        return
        
    # If URL doesn't start with http, add it (Apollo URLs might be provided without the protocol)
    if not url.startswith("http"):
        url = "https://" + url
    
    # Check if it's likely an Apollo URL
    if "apollo.io" not in url and not url.startswith("https://app.apollo.io"):
        print("Warning: This doesn't appear to be an Apollo URL. Results may not be as expected.")
        proceed = input("Do you want to proceed anyway? (y/n): ").lower()
        if proceed != 'y':
            return
    
    print("\nSending URL to OpenAI for conversion...\n")
    
    try:
        # Convert the URL to JSON
        result = convert_url_to_json(url)
        
        # Print the result
        print(result)
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return
    
    # Automatically save the result to apollo_json.txt
    filename = "apollo_json2.txt"
    try:
        with open(filename, "w") as f:
            f.write(result)
        print(f"\nResult automatically saved to {filename}")
    except Exception as e:
        print(f"Error saving to file: {str(e)}")

if __name__ == "__main__":
    main()
