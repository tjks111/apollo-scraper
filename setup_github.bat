@echo off
echo Setting up GitHub repository for Apollo Scraper...
echo.

REM Check if git is installed
where git >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Git is not installed. Please install Git from https://git-scm.com/downloads
    pause
    exit /b
)

REM Initialize git repository if not already initialized
if not exist .git (
    echo Initializing Git repository...
    git init
) else (
    echo Git repository already initialized.
)

REM Add all files to git
echo Adding files to Git...
git add .

REM Commit changes
echo Committing changes...
git commit -m "Initial commit of Apollo Scraper"

echo.
echo Now you need to create a GitHub repository and push your code.
echo.
echo 1. Go to https://github.com/new
echo 2. Create a new repository named "apollo-scraper" (or any name you prefer)
echo 3. Do NOT initialize the repository with a README, .gitignore, or license
echo 4. After creating the repository, run the following commands:
echo.
echo    git remote add origin https://github.com/YOUR_USERNAME/apollo-scraper.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo Replace YOUR_USERNAME with your GitHub username.
echo.
pause
