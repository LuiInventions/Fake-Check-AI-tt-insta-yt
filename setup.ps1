# Fake Check App Local Setup (Windows PowerShell)

Write-Host "--- Starting Fake Check App Setup ---" -ForegroundColor Cyan

# 0. Docker Check (CRITICAL)
Write-Host "`nâš ï¸  IMPORTANT: Please ensure Docker Desktop is running before proceeding." -ForegroundColor Yellow
$docker_running = Read-Host "Is Docker running? (y/n)"
if ($docker_running -notmatch "y") {
    Write-Host "âŒ Please start Docker and try again." -ForegroundColor Red
    exit 1
}

# 1. Dependency Checks
Write-Host "`nChecking dependencies..." -ForegroundColor Cyan

if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "âŒ Docker is not installed. Please install it from: https://www.docker.com/products/docker-desktop" -ForegroundColor Red
    exit 1
}

if (!(docker compose version 2>&1)) {
    Write-Host "âŒ Docker Compose is not available." -ForegroundColor Red
    exit 1
}
Write-Host "âœ… Docker and Docker Compose are ready." -ForegroundColor Green

$ENV_FILE = ".env"

# 2. Interactive Credential Setup
if (!(Test-Path $ENV_FILE)) {
    Write-Host "`nâš ï¸  Setting up configuration..." -ForegroundColor Yellow
    Write-Host "You will need several API keys. I will provide the links where you can get them."
    
    Copy-Item ".env.example" -Destination $ENV_FILE
    
    function Get-UserInput {
        param($VarName, $Prompt, $Link, $Default)
        Write-Host "`n--- $VarName ---" -ForegroundColor Cyan
        Write-Host "Get it here: $Link" -ForegroundColor Green
        $val = Read-Host "$Prompt [$Default]"
        if ([string]::IsNullOrWhiteSpace($val)) { $val = $Default }
        
        # Update .env
        $content = Get-Content $ENV_FILE
        $content = $content -replace "^$VarName=.*", "$VarName=$val"
        $content | Set-Content $ENV_FILE -Encoding UTF8
    }

    Get-UserInput "OPENAI_API_KEY" "Enter your OpenAI API Key" "https://platform.openai.com/api-keys" "your_openai_api_key_here"
    Get-UserInput "RAPIDAPI_KEY" "Enter your RapidAPI Key (Required for 'News API' and 'Instagram Looter')" "https://rapidapi.com/" "your_rapidapi_key_here"
    Get-UserInput "TELEGRAM_BOT_TOKEN" "Enter your Telegram Bot Token" "https://t.me/botfather" "your_telegram_bot_token_here"

    Write-Host "`n--- Optional: Sightengine (for advanced AI detection) ---" -ForegroundColor Cyan
    Write-Host "Get it here: https://sightengine.com/" -ForegroundColor Green
    $sight_user = Read-Host "Enter Sightengine User (leave empty to skip)"
    if (![string]::IsNullOrWhiteSpace($sight_user)) {
        (Get-Content $ENV_FILE) -replace "^SIGHTENGINE_API_USER=.*", "SIGHTENGINE_API_USER=$sight_user" | Set-Content $ENV_FILE -Encoding UTF8
        $sight_secret = Read-Host "Enter Sightengine Secret"
        (Get-Content $ENV_FILE) -replace "^SIGHTENGINE_API_SECRET=.*", "SIGHTENGINE_API_SECRET=$sight_secret" | Set-Content $ENV_FILE -Encoding UTF8
    }

    # Generate Secret Key
    $gen_secret = "secret_" + [guid]::NewGuid().ToString("N")
    (Get-Content $ENV_FILE) -replace "^SECRET_KEY=.*", "SECRET_KEY=$gen_secret" | Set-Content $ENV_FILE -Encoding UTF8

    Write-Host "âœ… .env file configured!" -ForegroundColor Green
} else {
    Write-Host "âœ… Using existing .env configuration." -ForegroundColor Green
}

# 3. Final Confirmation
Write-Host "`nSetup Complete!" -ForegroundColor Yellow
Write-Host "The app is now configured for Telegram-only mode."

# Create necessary local directories
if (!(Test-Path "data\db")) { New-Item -Path "data\db" -ItemType Directory -Force | Out-Null }
if (!(Test-Path "data\videos")) { New-Item -Path "data\videos" -ItemType Directory -Force | Out-Null }
if (!(Test-Path "data\frames")) { New-Item -Path "data\frames" -ItemType Directory -Force | Out-Null }

$start_now = Read-Host "Do you want to start the Docker containers now? (y/n)"
if ($start_now -match "y") {
    Write-Host "Starting Docker containers..." -ForegroundColor Cyan
    docker compose up --build -d

    Write-Host "Fake Check App is running!" -ForegroundColor Green
    Write-Host "-----------------------------------"
    Write-Host "Backend:  http://localhost:8000" -ForegroundColor Green
    Write-Host "Telegram: Bot is active via Polling" -ForegroundColor Green
    Write-Host "-----------------------------------"
    Write-Host "To see logs: docker compose logs -f" -ForegroundColor Cyan
    Write-Host "To stop:     docker compose down" -ForegroundColor Cyan
} else {
    Write-Host "`nOperation cancelled." -ForegroundColor Yellow
}
