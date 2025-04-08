import requests
import csv
import json
import pandas as pd
import time

# Apollo API URL for company search
url = "https://api.apollo.io/api/v1/organizations/search"

# Initialize an empty list to store all results
all_results = []

# Headers for the API request
headers = {
    "Content-Type": "application/json",
    "Cache-Control": "no-cache",
    "X-Api-Key": "sgrCA-qFxNiJbx1NCYuZUA",
}

# Initial payload for the first API request to get total pages
payload = {
  "page": 1,
   "organization_num_employees_ranges": ["1,10", "11,20"],
  "organization_locations": ["United Kingdom"],
  "q_organization_keyword_tags": [
    "tech", "saas", "adtech", "fintech", "api", "data", "b2b",
    "software", "application", "app", "android", "internet",
    "dev", "website", "plugin", "web", "ios", "artificial", "ai", "analytics"
  ],
  "included_organization_keyword_fields": ["tags", "name"],
  "organization_not_industry_tag_ids": [
    "5567e09973696410db020800", 
    "5567cd467369644d39040000",  
    "5567cdbc73696439d90b0000"  
  ],
  "organization_founded_year_range": {
    "min": 2019
  },
  "organization_include_unknown_founded_year": True,
  "organization_latest_funding_stage_cd": [
    "4",  
    "2"  
  ],
  "per_page": 100
}

# Function to process organizations from response
def process_organizations(orgs_data):
    results = []
    for organization in orgs_data:
        # Create a copy of the organization data
        processed_org = {}
        
        # Add all organization fields directly
        for key, value in organization.items():
            # Handle nested phone object
            if key == 'primary_phone' and isinstance(value, dict):
                for phone_key, phone_value in value.items():
                    processed_org[f'primary_phone_{phone_key}'] = phone_value
            # Handle nested industry_tag_hash
            elif key == 'industry_tag_hash' and isinstance(value, dict):
                for industry_key, industry_value in value.items():
                    processed_org[f'industry_tag_hash_{industry_key}'] = industry_value
            # Handle arrays by joining with commas
            elif isinstance(value, list):
                processed_org[key] = ", ".join(str(item) for item in value if item is not None)
            else:
                processed_org[key] = value
        
        results.append(processed_org)
    return results

# First request to get total pages
initial_response = requests.post(url, json=payload, headers=headers)

# Default number of pages if we can't determine from response
num_pages = 5

if initial_response.status_code == 200:
    initial_data = initial_response.json()
    
    # Extract total pages from pagination info
    if 'pagination' in initial_data and 'total_pages' in initial_data['pagination']:
        total_pages = initial_data['pagination']['total_pages']
        num_pages = min(total_pages, 500)  # Limit to 500 pages to avoid excessive requests
        print(f"Found {total_pages} total pages. Will scrape {num_pages} pages.")
    
    # Process the first page results
    if 'organizations' in initial_data and initial_data['organizations']:
        first_page_results = process_organizations(initial_data['organizations'])
        all_results.extend(first_page_results)
        print(f"Page 1 processed. Found {len(first_page_results)} organizations.")
    else:
        print(f"No 'organizations' key found in response for page 1.")
else:
    print(f"Failed to fetch initial data: {initial_response.status_code} - {initial_response.text}")

# Now process remaining pages (starting from page 2)
for page in range(2, num_pages + 1):
    # Update page number in payload
    payload["page"] = page
    
    # Sending the POST request to the Apollo API
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        # Process organization data from the response
        if 'organizations' in data and data['organizations']:
            page_results = process_organizations(data['organizations'])
            all_results.extend(page_results)
            print(f"Page {page} processed. Found {len(page_results)} organizations.")
        else:
            print(f"No 'organizations' key found in response for page {page}.")
    else:
        print(f"Failed to fetch data for page {page}: {response.status_code} - {response.text}")
    
    # Add a delay between requests to be polite to the server
    time.sleep(1)

# Check if we have results to save
if all_results:
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(all_results)
    
    # Define the specific headers we want in the output based on the provided list
    desired_headers = [
        'id', 'name', 'city', 'state', 'country', 'industry', 'keywords',
        'logo_url', 'industries', 'market_cap', 'postal_code', 'raw_address',
        'show_intent', 'twitter_url', 'website_url', 'linkedin_uid', 'linkedin_url',
        'alexa_ranking', 'angellist_url', 'primary_phone_number', 'primary_phone_source',
        'primary_phone_sanitized_number', 'primary_domain', 'street_address',
        'industry_tag_id', 'intent_strength', 'sanitized_phone', 'snippets_loaded',
        'industry_tag_hash_internet', 'industry_tag_hash_computer_software',
        'industry_tag_hash_information_technology_&_services', 'secondary_industries',
        'intent_signal_account', 'retail_location_count', 'publicly_traded_symbol',
        'estimated_num_employees', 'publicly_traded_exchange', 'has_intent_signal_account',
        'phone', 'blog_url', 'facebook_url', 'founded_year', 'languages'
    ]
    
    # Ensure all desired headers exist in the DataFrame (add empty columns for missing headers)
    for header in desired_headers:
        if header not in df.columns:
            df[header] = ''
    
    # Select only the columns that exist in our data or are in the desired headers list
    all_columns = list(set(list(df.columns) + desired_headers))
    
    # Save the DataFrame to a CSV file with all columns
    df.to_csv('c:\\Users\\rento\\OneDrive\\Apps\\apollo scrape\\companies.csv', index=False)
    
    print(f"Results have been written to 'companies.csv' with {len(df.columns)} columns.")
    print(f"Total records scraped: {len(all_results)}")
    
    # Print which headers were found and which were missing from the desired list
    missing_headers = [h for h in desired_headers if h not in df.columns]
    if missing_headers:
        print(f"Warning: The following desired headers were not found in the data: {', '.join(missing_headers)}")
else:
    print("No data to write to CSV.")