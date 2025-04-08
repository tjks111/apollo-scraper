# Apollo Scraper Web Application

This web application automates the process of running Apollo.io scraper scripts and provides a user-friendly interface for submitting scraping jobs and downloading results.

## Features

- User input form for Apollo URL, scrape name, and user name
- Automatic execution of scraper scripts in the background
- Real-time progress tracking with progress bar
- CSV file download functionality
- Error handling and status reporting

## Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python app.py
   ```

3. Access the application at http://localhost:5000

## Deployment to Render.com

### Prerequisites

1. Create a [Render.com](https://render.com) account
2. Have your code in a Git repository (GitHub, GitLab, etc.)

### Deployment Steps

1. Log in to your Render.com account
2. Click on "New" and select "Web Service"
3. Connect your Git repository
4. Configure the web service:
   - **Name**: Choose a name for your service (e.g., apollo-scraper)
   - **Environment**: Python
   - **Region**: Choose the region closest to your users
   - **Branch**: main (or your preferred branch)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Plan**: Free (or select a paid plan for more resources)

5. Add the following environment variables:
   - `RENDER=True` (to enable production mode)
   - `PORT=10000` (Render will automatically set this, but you can specify it)
   - `APOLLO_API_KEY=your_api_key_here` (Your Apollo.io API key)
   - `OPENAI_API_KEY=your_openai_api_key_here` (Your OpenAI API key for URL conversion)

6. Click "Create Web Service"

7. Render will automatically build and deploy your application. Once deployed, you can access it at the URL provided by Render.

### Important Notes for Render Deployment

1. **File Storage**: Render's free tier uses ephemeral storage, meaning files will be lost when the service restarts. For persistent storage of CSV files, consider:
   - Using Render's Disk service (paid feature)
   - Uploading files to a cloud storage service like AWS S3
   - Using a database to store results

2. **API Key Security**: Store your Apollo API key as an environment variable in Render, not in your code.

3. **Resource Limits**: Be aware of Render's free tier limitations:
   - 512 MB RAM
   - Shared CPU
   - Automatic spin-down after inactivity

4. **Scaling**: For production use with many users, consider upgrading to a paid plan for better performance and reliability.
