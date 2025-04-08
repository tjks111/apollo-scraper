import requests
import csv
import json
import pandas as pd
import time

# Apollo API URL for bulk enrichment
url = "https://api.apollo.io/api/v1/people/bulk_match"

# Headers for the API request
headers = {
    "Content-Type": "application/json",
    "Cache-Control": "no-cache",
    "X-Api-Key": "sgrCA-qFxNiJbx1NCYuZUA"
}

# Rate limiting parameters
RATE_LIMIT = 2000  # 200 IDs per minute
REQUEST_INTERVAL = 60 / RATE_LIMIT  # Time between requests in seconds

# Read the IDs from test.csv
df = pd.read_csv('test.csv')
ids = df['id'].tolist()

# Initialize an empty list to store all enriched results
all_enriched_results = []

# Process IDs in batches of 10
for i in range(0, len(ids), 10):
    batch_start_time = time.time()
    batch_ids = ids[i:i+10]
    
    # Create the payload for the bulk enrichment API with the correct structure
    payload = {
        "details": [{"id": person_id} for person_id in batch_ids]
    }
    
    # Sending the POST request to the Apollo API
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        # Check if the response contains matches
        if 'matches' in data:
            all_enriched_results.extend(data['matches'])
            print(f"Successfully enriched {len(data['matches'])} records in batch {i//10 + 1}")
        else:
            print(f"No 'matches' key found in response for batch {i//10 + 1}.")
    else:
        print(f"Failed to fetch data for batch {i//10 + 1}: {response.status_code} - {response.text}")

    print(f"Processed batch {i//10 + 1} of {(len(ids) + 9) // 10}")
    
    # Rate limiting: wait if needed to maintain the rate limit
    elapsed = time.time() - batch_start_time
    if elapsed < REQUEST_INTERVAL and i + 10 < len(ids):
        time.sleep(REQUEST_INTERVAL - elapsed)

# Check if we have results to save
if all_enriched_results:
    # Convert the list of dictionaries to a DataFrame
    enriched_df = pd.DataFrame(all_enriched_results)
    
    # Save the DataFrame to a CSV file named 'final.csv'
    enriched_df.to_csv('final.csv', index=False)
    
    print(f"Enriched data for {len(all_enriched_results)} people has been written to 'final.csv'.")
else:
    print("No enriched data to write to CSV.")
