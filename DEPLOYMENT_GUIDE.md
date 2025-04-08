# Detailed Deployment Guide for Apollo Scraper on Render.com

This guide provides step-by-step instructions for deploying the Apollo Scraper application to Render.com.

## Prerequisites

1. A [Render.com](https://render.com) account
2. Your Apollo.io API key
3. Your code pushed to a Git repository (GitHub, GitLab, etc.)

## Step 1: Prepare Your Repository

Ensure your repository contains all the necessary files:

- `app.py` - The main Flask application
- `run_scraper.py` - The script that runs the scraper
- `apollo_with_prospecting.py` - The script for scraping with prospecting
- `apollo_without_prospecting.py` - The script for scraping without prospecting
- `combine_csv_files.py` - The script for combining CSV files
- `user_input_form.html` - The HTML form for user input
- `requirements.txt` - The list of Python dependencies
- `Procfile` - The Procfile for Render.com
- `render.yaml` - The Render.com configuration file
- Other necessary files like `apollo_json.txt` and `apollo_json2.txt`

## Step 2: Create a New Web Service on Render.com

1. Log in to your Render.com account
2. Click on the "New" button in the top right corner
3. Select "Web Service" from the dropdown menu

## Step 3: Connect Your Repository

1. Choose your Git provider (GitHub, GitLab, etc.)
2. Select the repository containing your Apollo Scraper code
3. If you haven't connected your Git account to Render.com yet, you'll be prompted to do so

## Step 4: Configure Your Web Service

Fill in the following details:

1. **Name**: Choose a name for your service (e.g., apollo-scraper)
2. **Environment**: Select "Python"
3. **Region**: Choose the region closest to your users
4. **Branch**: Select your main branch (usually "main" or "master")
5. **Build Command**: `pip install -r requirements.txt`
6. **Start Command**: `python app.py`
7. **Plan**: Choose the "Free" plan (or a paid plan if you need more resources)

## Step 5: Set Environment Variables

Scroll down to the "Environment" section and add the following environment variables:

1. `RENDER=True` - This enables production mode
2. `APOLLO_API_KEY=your_api_key_here` - Replace with your actual Apollo.io API key
3. `OPENAI_API_KEY=your_openai_api_key_here` - Replace with your actual OpenAI API key

Render will automatically set the `PORT` environment variable.

## Step 6: Configure Advanced Options (Optional)

If you need persistent storage for your CSV files, you can add a disk:

1. Scroll down to the "Disks" section
2. Click "Add Disk"
3. Set the following:
   - **Name**: `data`
   - **Mount Path**: `/data`
   - **Size**: `1 GB` (or more if needed)

Note: Disks are only available on paid plans.

## Step 7: Deploy Your Application

1. Click the "Create Web Service" button at the bottom of the page
2. Render will start building and deploying your application
3. You can monitor the build process in the "Logs" tab

## Step 8: Access Your Application

Once the deployment is complete:

1. Click on the URL provided by Render (e.g., https://apollo-scraper.onrender.com)
2. You should see the Apollo Scraper user input form
3. Test the application by submitting a scraping job

## Troubleshooting

If you encounter any issues:

1. Check the "Logs" tab in your Render.com dashboard for error messages
2. Verify that all environment variables are set correctly
3. Make sure your Apollo.io API key is valid
4. Check that all required files are present in your repository

## Updating Your Application

To update your application:

1. Push changes to your Git repository
2. Render will automatically detect the changes and redeploy your application
3. You can monitor the deployment in the "Logs" tab

## Additional Resources

- [Render.com Documentation](https://render.com/docs)
- [Flask Deployment Guide](https://render.com/docs/deploy-flask)
- [Python on Render](https://render.com/docs/python)
