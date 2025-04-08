import csv
import os
import json

def combine_csv_files():
    # Read scrape_name from User_Inputs.json
    try:
        with open('User_Inputs.json', 'r') as json_file:
            user_inputs = json.load(json_file)
            scrape_name = user_inputs.get('scrape_name', 'final_output')
    except Exception as e:
        print(f"Error reading User_Inputs.json: {str(e)}")
        scrape_name = 'final_output'
    
    # Define file paths
    with_prospecting_file = os.path.join(os.getcwd(), 'with_prospecting.csv')
    without_prospecting_file = os.path.join(os.getcwd(), 'without_prospecting.csv')
    final_output_file = os.path.join(os.getcwd(), f'{scrape_name}.csv')
    
    # Define the specific headers we want in the final output
    desired_headers = [
        'Full Name', 'First Name', 'Last Name', 'Headline',
        'Lead City', 'Lead State', 'Lead Country', 'LinkedIn Link',
        'Company Name', 'Title', 'Company Website Short',
        'Email', 'id', 'org_id', 'Company Linkedin Url',
    ]
    
    # Define header mapping from source headers to desired headers
    # This maps various possible source headers to our desired output headers
    header_mapping = {
        # Common variations for name fields
        'full_name': 'Full Name',
        'contact_name': 'Full Name',
        'person_name': 'Full Name',
        
        'first_name': 'First Name',
        'firstname': 'First Name',
        'given_name': 'First Name',
        
        'last_name': 'Last Name',
        'lastname': 'Last Name',
        'family_name': 'Last Name',
        'surname': 'Last Name',
        
        # Job related fields
        'headline': 'Headline',
        'bio': 'Headline',
        'description': 'Headline',
        'profile_headline': 'Headline',
        
        
        'title': 'Title',
        'job_title': 'Title',
        'position': 'Title',
        'role': 'Title',
        'contact_title': 'Title',
        
        # Location fields
        'city': 'Lead City',
        'lead_city': 'Lead City',
        'person_city': 'Lead City',
        'contact_city': 'Lead City',
        
        'state': 'Lead State',
        'lead_state': 'Lead State',
        'person_state': 'Lead State',
        'contact_state': 'Lead State',
        'province': 'Lead State',
        
        'country': 'Lead Country',
        'lead_country': 'Lead Country',
        'person_country': 'Lead Country',
        'contact_country': 'Lead Country',
        
        # Company fields
        'company': 'Company Name',
        'company_name': 'Company Name',
        'organization_name': 'Company Name',
        'employer': 'Company Name',
        'account_name': 'Company Name',
        'contact_organization_name': 'Company Name',
        'org_name': 'Company Name',
        
        'website': 'Company Website Short',
        'company_website': 'Company Website Short',
        'company_website_short': 'Company Website Short',
        'org_website': 'Company Website Short',
        'account_website': 'Company Website Short',

        'account_linkedin_url': 'Company Linkedin Url',
        'org_linkedin_url': 'Company Linkedin Url',
    
        
        # Contact fields
        'linkedin_url': 'LinkedIn Link',
        'contact_linkedin_url': 'LinkedIn Link',
        
        'contact_email': 'Email',
        
        # ID fields
        'id': 'id',
        'person_id': 'id',
        'contact_id': 'id',
        'apollo_id': 'id',
        
        'organization_id': 'org_id',
        'account_id': 'org_id',
    }
    
    # Lists to store all rows and headers from both files
    all_rows = []
    all_headers = set()
    source_headers_mapping = {}
    
    # Function to process a CSV file and add its data to our collection
    def process_csv_file(file_path, file_name):
        # Check if the file exists before attempting to open it
        if not os.path.exists(file_path):
            print(f"Warning: {file_name} not found at {file_path}")
            return 0
            
        rows_before = len(all_rows)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                reader = csv.DictReader(file)
                source_headers = reader.fieldnames
                
                # Map source headers to desired headers
                for header in source_headers:
                    # Convert header to lowercase for case-insensitive matching
                    header_lower = header.lower().strip()
                    if header_lower in header_mapping:
                        source_headers_mapping[header] = header_mapping[header_lower]
                    else:
                        # If exact match not found, try partial matching
                        for key in header_mapping:
                            if key in header_lower:
                                source_headers_mapping[header] = header_mapping[key]
                                break
                
                # Add all headers to our set
                all_headers.update(source_headers)
                
                # Add all rows to our list with mapped headers
                for row in reader:
                    all_rows.append(row)
            
            return len(all_rows) - rows_before
        except Exception as e:
            print(f"Error processing {file_name}: {str(e)}")
            return 0
    
    # Read the with_prospecting file
    print("Reading with_prospecting.csv...")
    rows_added = process_csv_file(with_prospecting_file, "with_prospecting.csv")
    print(f"Read {rows_added} rows from with_prospecting.csv")
    
    # Read the without_prospecting file
    print("Reading without_prospecting.csv...")
    rows_added = process_csv_file(without_prospecting_file, "without_prospecting.csv")
    print(f"Read {rows_added} rows from without_prospecting.csv")
    
    # Check if we have any data to write
    if not all_rows:
        print("No data found in any of the input files. No output file will be created.")
        return
    
    # Write all rows to the final output file with only the desired headers
    print(f"Writing {len(all_rows)} total rows to {scrape_name}.csv...")
    
    # Counter for cleaned email addresses
    email_count = 0
    
    with open(final_output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=desired_headers)
        writer.writeheader()
        
        # Write all rows, mapping headers and filling in missing values with empty strings
        for row in all_rows:
            mapped_row = {}
            
            # Initialize all desired headers with empty strings
            for header in desired_headers:
                mapped_row[header] = ''
            
            # Map values from source headers to desired headers
            for source_header, value in row.items():
                if source_header in source_headers_mapping:
                    target_header = source_headers_mapping[source_header]
                    if target_header in desired_headers:
                        mapped_row[target_header] = value
            
            # Clean the email if it's "email_not_unlocked@domain.com"
            if mapped_row['Email'] == 'email_not_unlocked@domain.com':
                mapped_row['Email'] = ''
                email_count += 1
            
            writer.writerow(mapped_row)
    
    print(f"Cleaned {email_count} locked email addresses")
    
    # Count how many desired headers were successfully mapped
    mapped_headers = set()
    for source_header in source_headers_mapping.values():
        if source_header in desired_headers:
            mapped_headers.add(source_header)
    
    missing_headers = set(desired_headers) - mapped_headers
    
    print(f"Combined data saved to {final_output_file}")
    print(f"Total rows: {len(all_rows)}")
    print(f"Total columns: {len(desired_headers)}")
    print(f"Successfully mapped {len(mapped_headers)} of {len(desired_headers)} desired headers")
    if missing_headers:
        print(f"Warning: Could not find source headers for: {', '.join(missing_headers)}")

if __name__ == "__main__":
    combine_csv_files()
