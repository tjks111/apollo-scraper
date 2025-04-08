import requests
import csv
import json
import pandas as pd
import time
import concurrent.futures

# Apollo API URL
url = "https://api.apollo.io/v1/mixed_people/search"

# Initialize an empty list to store all results
all_results = []

# Load payload from apollo_json.txt
with open('apollo_json.txt', 'r') as file:
    payload = json.load(file)

# Get API key from environment variable or use default for local development
import os
api_key = os.environ.get('APOLLO_API_KEY', 'sgrCA-qFxNiJbx1NCYuZUA')

# Headers for the API request
headers = {
    "Content-Type": "application/json",
    "Cache-Control": "no-cache",
    "X-Api-Key": api_key
}

# Function to process a single page
def process_page(page_num):
    current_payload = payload.copy()
    current_payload["page"] = str(page_num)
    
    # Sending the POST request to the Apollo API
    response = requests.post(url, json=current_payload, headers=headers)
    
    page_results = []
    
    if response.status_code == 200:
        data = response.json()
        
        # Process people data from the response
        if 'people' in data and data['people']:
            for person in data['people']:
                # Create a copy of the person data
                processed_person = {}
                
                # Add all person fields directly
                for key, value in person.items():
                    processed_person[key] = value
                
                # Add contact information with contact_ prefix for specific fields
                processed_person['contact_id'] = person.get('id', '')
                processed_person['contact_first_name'] = person.get('first_name', '')
                processed_person['contact_last_name'] = person.get('last_name', '')
                processed_person['contact_name'] = person.get('name', '')
                processed_person['contact_email'] = person.get('email', '')
                processed_person['contact_title'] = person.get('title', '')
                processed_person['contact_city'] = person.get('city', '')
                processed_person['contact_state'] = person.get('state', '')
                processed_person['contact_country'] = person.get('country', '')
                
                # If organization details exist, extract and flatten them
                if 'organization' in person and person['organization']:
                    org = person['organization']
                    # Add organization fields with org_ prefix
                    for key, value in org.items():
                        processed_person[f'org_{key}'] = value
                    
                    # Create account object similar to the example
                    processed_person['contact_account'] = {
                        'id': org.get('id', ''),
                        'name': org.get('name', ''),
                        'domain': org.get('primary_domain', ''),
                        'phone': org.get('phone', ''),
                        'website_url': org.get('website_url', ''),
                        'linkedin_url': org.get('linkedin_url', ''),
                        'city': org.get('city', ''),
                        'state': org.get('state', ''),
                        'country': org.get('country', ''),
                        'industry': org.get('industry', '')
                    }
                
                # Process account data if it exists
                if 'account' in person and person['account']:
                    account = person['account']
                    processed_person['account_id'] = account.get('id', '')
                    processed_person['account'] = account
                
                page_results.append(processed_person)
        # Check for contacts in the response (new format)
        elif 'contacts' in data and data['contacts']:
            for contact in data['contacts']:
                # Create a copy of the contact data
                processed_contact = {}
                
                # Add all contact fields directly
                for key, value in contact.items():
                    if key != 'account' and key != 'organization':
                        processed_contact[key] = value
                
                # Add contact information with contact_ prefix for specific fields
                processed_contact['contact_id'] = contact.get('id', '')
                processed_contact['contact_first_name'] = contact.get('first_name', '')
                processed_contact['contact_last_name'] = contact.get('last_name', '')
                processed_contact['contact_name'] = contact.get('name', '')
                processed_contact['contact_title'] = contact.get('title', '')
                processed_contact['contact_city'] = contact.get('city', '')
                processed_contact['contact_state'] = contact.get('state', '')
                processed_contact['contact_country'] = contact.get('country', '')
                
                # Process organization data if it exists
                if 'organization' in contact and contact['organization']:
                    org = contact['organization']
                    # Add organization fields with org_ prefix
                    for key, value in org.items():
                        processed_contact[f'org_{key}'] = value
                
                # Process account data if it exists
                if 'account' in contact and contact['account']:
                    account = contact['account']
                    processed_contact['account_id'] = account.get('id', '')
                    processed_contact['account'] = account
                
                page_results.append(processed_contact)
        else:
            print(f"No 'people' or 'contacts' key found in response for page {page_num}.")
        
        print(f"Page {page_num} processed.")
        return page_results
    else:
        print(f"Failed to fetch data for page {page_num}: {response.status_code} - {response.text}")
        return []

# First request to get total pages
initial_response = requests.post(url, json=payload, headers=headers)

# Default number of pages if we can't determine from response
num_pages = 5

if initial_response.status_code == 200:
    initial_data = initial_response.json()
    
    # Extract total pages from pagination info
    if 'pagination' in initial_data and 'total_pages' in initial_data['pagination']:
        total_pages = initial_data['pagination']['total_pages']
        num_pages = min(total_pages, 500)  # Limit to 500 pages
        print(f"Found {total_pages} total pages. Will scrape {num_pages} pages.")
    
    # Process the first page results
    first_page_results = process_page(1)
    all_results.extend(first_page_results)
    
    # Process remaining pages in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all page processing tasks
        future_to_page = {executor.submit(process_page, page): page for page in range(2, num_pages + 1)}
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_page):
            page = future_to_page[future]
            try:
                page_results = future.result()
                all_results.extend(page_results)
            except Exception as exc:
                print(f"Page {page} generated an exception: {exc}")
else:
    print(f"Failed to fetch initial data: {initial_response.status_code} - {initial_response.text}")

# Check if we have results to save
if all_results:
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(all_results)
    
    # Save the DataFrame to a CSV file
    df.to_csv('without_prospecting.csv', index=False, encoding='utf-8')
    print(f"Results have been written to 'without_prospecting.csv' with {len(df.columns)} columns including contact and organization details.")
    print(f"Total records scraped: {len(all_results)}")
else:
    print("No data to write to CSV.")
