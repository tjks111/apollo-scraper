import subprocess
import os
import sys
import time

def run_command(command, description):
    """Run a command and print its output in real-time"""
    print(f"\n{'=' * 80}")
    print(f"RUNNING: {description}")
    print(f"{'=' * 80}\n")
    
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line, end='')
            sys.stdout.flush()  # Ensure output is displayed immediately
        
        process.wait()
        
        if process.returncode != 0:
            print(f"\nERROR: {description} failed with return code {process.returncode}")
            return False
        
        print(f"\nSUCCESS: {description} completed successfully")
        return True
        
    except Exception as e:
        print(f"\nERROR: Failed to run {description}: {str(e)}")
        return False

def run_scraper(background=False):
    """
    Run the complete Apollo scraper sequence
    
    Args:
        background (bool): If True, minimal output will be printed
                          If False, detailed output will be printed
    
    Returns:
        dict: Results of the scraper run including success status, runtime, and output file info
    """
    start_time = time.time()
    if not background:
        print("Starting Apollo scraper sequence...")
    
    # Step 1: Run apollo_with_prospecting.py
    if not background:
        print("\nStep 1/3: Running with_prospecting scraper...")
    if not run_command([sys.executable, "apollo_with_prospecting.py"], "With Prospecting Scraper"):
        if not background:
            print("Error in Step 1. Aborting sequence.")
        return {"success": False, "step": 1, "error": "With Prospecting Scraper failed"}
    
    # Step 2: Run apollo_without_prospecting.py
    if not background:
        print("\nStep 2/3: Running without_prospecting scraper...")
    if not run_command([sys.executable, "apollo_without_prospecting.py"], "Without Prospecting Scraper"):
        if not background:
            print("Error in Step 2. Aborting sequence.")
        return {"success": False, "step": 2, "error": "Without Prospecting Scraper failed"}
    
    # Step 3: Run combine_csv_files.py
    if not background:
        print("\nStep 3/3: Combining CSV files...")
    if not run_command([sys.executable, "combine_csv_files.py"], "CSV Combiner"):
        if not background:
            print("Error in Step 3. Aborting sequence.")
        return {"success": False, "step": 3, "error": "CSV Combiner failed"}
    
    # Calculate total runtime
    end_time = time.time()
    total_time = end_time - start_time
    hours, remainder = divmod(total_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    # Format runtime as string
    runtime_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    
    # Check if the final output file exists
    try:
        import json
        with open('User_Inputs.json', 'r') as json_file:
            user_inputs = json.load(json_file)
            scrape_name = user_inputs.get('scrape_name', 'final_output')
    except Exception:
        scrape_name = 'final_output'
    
    output_file = f"{scrape_name}.csv"
    file_info = {}
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # Size in MB
        file_info = {
            "name": output_file,
            "path": os.path.abspath(output_file),  # Include absolute path
            "size_mb": round(file_size, 2),
            "exists": True
        }
        if not background:
            print(f"\nOutput file: {output_file} ({file_size:.2f} MB)")
    else:
        file_info = {
            "name": output_file,
            "exists": False
        }
        if not background:
            print(f"\nWarning: Expected output file {output_file} not found.")
    
    if not background:
        print("\n" + "=" * 80)
        print(f"SCRAPER SEQUENCE COMPLETED SUCCESSFULLY")
        print(f"Total runtime: {runtime_str}")
        print("=" * 80)
    
    return {
        "success": True,
        "runtime": total_time,
        "runtime_formatted": runtime_str,
        "output_file": file_info
    }

def main():
    """Command-line entry point for the scraper"""
    result = run_scraper(background=False)
    return 0 if result["success"] else 1

if __name__ == "__main__":
    main()
