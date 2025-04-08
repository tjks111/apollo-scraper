from flask import Flask, request, render_template, jsonify, send_from_directory
import os
import json
import threading
from run_scraper import run_scraper

app = Flask(__name__)

# Global variable to track scraper status
scraper_status = {
    "running": False,
    "last_run": None
}

@app.route('/')
def index():
    # Serve the HTML form
    return send_from_directory('.', 'user_input_form.html')

@app.route('/submit', methods=['POST'])
def submit():
    global scraper_status
    
    # Get form data
    data = request.json
    apollo_url = data.get('apollo_url')
    scrape_name = data.get('scrape_name')
    user_name = data.get('user_name')
    
    # Validate inputs
    if not apollo_url or not scrape_name or not user_name:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    
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
        
        # Check if scraper is already running
        if scraper_status["running"]:
            return jsonify({
                'success': True, 
                'message': 'Data saved successfully, but scraper is already running. Please wait for it to complete.',
                'scraper_running': True
            })
        
        # Start the scraper in a background thread
        def run_scraper_thread():
            global scraper_status
            scraper_status["running"] = True
            try:
                result = run_scraper(background=True)
                scraper_status["last_run"] = result
            finally:
                scraper_status["running"] = False
        
        thread = threading.Thread(target=run_scraper_thread)
        thread.daemon = True  # Thread will exit when main program exits
        thread.start()
        
        return jsonify({
            'success': True, 
            'message': 'Data saved successfully and scraper has started',
            'scraper_running': True
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/status', methods=['GET'])
def status():
    """Endpoint to check the status of the scraper"""
    global scraper_status
    
    return jsonify({
        'running': scraper_status["running"],
        'last_run': scraper_status["last_run"]
    })

@app.route('/results', methods=['GET'])
def results():
    """Endpoint to get the results of the last scraper run"""
    global scraper_status
    
    if scraper_status["last_run"] is None:
        return jsonify({
            'success': False,
            'message': 'No scraper results available yet'
        })
    
    return jsonify({
        'success': True,
        'results': scraper_status["last_run"]
    })

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Endpoint to download the generated CSV file"""
    # For security, only allow downloading CSV files
    if not filename.endswith('.csv'):
        return jsonify({
            'success': False,
            'message': 'Only CSV files can be downloaded'
        }), 400
    
    # Check if the file exists
    if not os.path.exists(filename):
        return jsonify({
            'success': False,
            'message': f'File {filename} not found'
        }), 404
    
    # Return the file for download
    return send_from_directory(
        os.getcwd(),  # Current working directory
        filename,
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    # Use environment variable for port if available (for Render.com and other hosting services)
    port = int(os.environ.get('PORT', 5000))
    # In production, set debug to False
    is_prod = os.environ.get('RENDER', False)
    # Run the server with appropriate settings based on environment
    app.run(host='0.0.0.0', debug=not is_prod, port=port)
