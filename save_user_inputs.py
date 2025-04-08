import os
import json

def save_user_inputs(apollo_url, scrape_name, user_name):
    """
    Save user inputs to a JSON file named User_Inputs.json
    
    Args:
        apollo_url (str): The Apollo URL provided by the user
        scrape_name (str): The name of the scrape
        user_name (str): The name of the user
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create the data structure
        user_inputs = {
            "apollo_url": apollo_url,
            "scrape_name": scrape_name,
            "user_name": user_name
        }
        
        # Define the file path
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "User_Inputs.json")
        
        # Write the data to the file
        with open(file_path, 'w') as f:
            json.dump(user_inputs, f, indent=4)
            
        return True
    except Exception as e:
        print(f"Error saving user inputs: {e}")
        return False

# This function can be imported and used by other Python scripts
# or called directly from a web server handling the form submission