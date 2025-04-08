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

# Load payload from apollo_json2.txt
with open('apollo_json2.txt', 'r') as file:
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
        
        # Check for the new 'contacts' key in the response
        if 'contacts' in data:
            for contact in data['contacts']:
                # Create a copy of the contact data
                processed_contact = {}
                
                # Add contact information with contact_ prefix
                for key, value in contact.items():
                    if key != 'account' and key != 'organization':
                        processed_contact[f'contact_{key}'] = value
                
                # If account details exist, extract and flatten them
                if 'account' in contact and contact['account']:
                    account = contact['account']
                    # Add account fields with account_ prefix
                    for key, value in account.items():
                        processed_contact[f'account_{key}'] = value
                
                # If organization details exist, extract and flatten them
                if 'organization' in contact and contact['organization']:
                    org = contact['organization']
                    # Add organization fields with org_ prefix
                    for key, value in org.items():
                        processed_contact[f'org_{key}'] = value
                
                page_results.append(processed_contact)
        # Fallback to the old 'people' key for backward compatibility
        elif 'people' in data:
            for person in data['people']:
                # Create a copy of the person data
                processed_person = {}
                
                # Add contact information with contact_ prefix
                for key, value in person.items():
                    if key != 'organization':
                        processed_person[f'contact_{key}'] = value
                
                # If organization details exist, extract and flatten them
                if 'organization' in person and person['organization']:
                    org = person['organization']
                    # Add organization fields with org_ prefix
                    for key, value in org.items():
                        processed_person[f'org_{key}'] = value
                
                page_results.append(processed_person)
        else:
            print(f"No 'contacts' or 'people' key found in response for page {page_num}.")
        
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
    
    # Define the specific headers to export in the requested order
    headers = [
        'contact_id','contact_first_name', 'contact_last_name', 'contact_name', 'contact_linkedin_url',
        'contact_title','contact_seniority', 'contact_organization_name', 'contact_headline', 'contact_city',
        'contact_country', 'contact_state', 'contact_sanitized_phone', 'contact_email',
        'contact_time_zone', 'account_id', 'account_name', 'account_website_url',
        'account_linkedin_url', 'account_twitter_url', 'account_facebook_url',
        'account_alexa_ranking', 'account_phone', 'account_linkedin_uid',
        'account_founded_year', 'account_primary_domain', 'account_sanitized_phone',
        'account_raw_address', 'account_street_address', 'account_city', 'account_state',
        'account_country', 'account_postal_code', 'account_domain', 'org_industry', 'account_angellist_url'
    ]
    
    # Ensure all headers exist in the DataFrame (add empty columns for missing headers)
    for header in headers:
        if header not in df.columns:
            df[header] = ''
    
    # Select only the specified headers and in the specified order
    df_export = df[headers]
    
    # Save the DataFrame to a CSV file
    df_export.to_csv('with_prospecting.csv', index=False, encoding='utf-8')
    print(f"Results have been written to 'with_prospecting.csv' with {len(headers)} columns.")
    print(f"Total records scraped: {len(all_results)}")
else:
    print("No data to write to CSV.")
