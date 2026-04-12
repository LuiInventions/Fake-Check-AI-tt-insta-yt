#!/bin/bash

# --- CONFIGURATION ---
ENV_FILE=".env"

# --- COLORS ---
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting Fake Check App Setup...${NC}"

# 0. Docker Check (CRITICAL)
echo -e "\n${YELLOW}⚠️  IMPORTANT: Please ensure Docker Desktop is running before proceeding.${NC}"
read -p "Is Docker running? (y/n): " docker_running
if [[ ! "$docker_running" =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ Please start Docker and try again.${NC}"
    exit 1
fi

# 1. Dependency Checks
echo -e "\n${BLUE}🔍 Checking dependencies...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed.${NC} Please install it from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not available.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker and Docker Compose are ready.${NC}"

# 2. Interactive Credential Setup
if [ ! -f "$ENV_FILE" ]; then
    echo -e "\n${YELLOW}⚠️  Setting up configuration...${NC}"
    echo -e "You will need several API keys. I will provide the links where you can get them."
    
    cp .env.example .env
    
    # helper for reading input
    get_input() {
        local var_name=$1
        local prompt_text=$2
        local link=$3
        local default_val=$4
        
        echo -e "\n${BLUE}--- $var_name ---${NC}"
        echo -e "Get it here: ${GREEN}$link${NC}"
        read -p "$prompt_text [$default_val]: " user_val
        
        if [ -z "$user_val" ]; then
            user_val=$default_val
        fi
        
        sed -i "s|^$var_name=.*|$var_name=$user_val|" "$ENV_FILE"
    }

    get_input "OPENAI_API_KEY" "Enter your OpenAI API Key" "https://platform.openai.com/api-keys" "your_openai_api_key_here"
    get_input "RAPIDAPI_KEY" "Enter your RapidAPI Key (Required for 'News API' and 'Instagram Looter')" "https://rapidapi.com/" "your_rapidapi_key_here"
    get_input "TELEGRAM_BOT_TOKEN" "Enter your Telegram Bot Token" "https://t.me/botfather" "your_telegram_bot_token_here"
    
    echo -e "\n${BLUE}--- Optional: Sightengine (for advanced AI detection) ---${NC}"
    echo -e "Get it here: ${GREEN}https://sightengine.com/${NC}"
    read -p "Enter Sightengine User (leave empty to skip): " sight_user
    if [ ! -z "$sight_user" ]; then
        sed -i "s|^SIGHTENGINE_API_USER=.*|SIGHTENGINE_API_USER=$sight_user|" "$ENV_FILE"
        read -p "Enter Sightengine Secret: " sight_secret
        sed -i "s|^SIGHTENGINE_API_SECRET=.*|SIGHTENGINE_API_SECRET=$sight_secret|" "$ENV_FILE"
    fi

    # Generate Secret Key
    GEN_SECRET="secret_$(date +%s)_$RANDOM"
    sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$GEN_SECRET|" "$ENV_FILE"

    echo -e "\n${GREEN}✅ .env file configured!${NC}"
else
    echo -e "\n${GREEN}✅ Using existing .env configuration.${NC}"
fi

# 3. Final Confirmation
echo -e "\n${YELLOW}📦 Setup Complete!${NC}"
echo -e "The app is now configured for Telegram-only mode."

# Create necessary local directories
mkdir -p data/db data/videos data/frames

read -p "Do you want to start the Docker containers now? (y/n): " start_now
if [[ "$start_now" =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}🤖 Starting Docker containers...${NC}"
    docker compose up --build -d

    echo -e "\n${GREEN}✨ Fake Check App is running!${NC}"
    echo -e "-----------------------------------"
    echo -e "Backend:  ${GREEN}http://localhost:8000${NC}"
    echo -e "Telegram: ${GREEN}Bot is active via Polling${NC}"
    echo -e "-----------------------------------"
    echo -e "To see logs: ${BLUE}docker compose logs -f${NC}"
    echo -e "To stop:     ${BLUE}docker compose down${NC}"
else
    echo -e "\n${YELLOW}Operation cancelled.${NC} You can start it later with: ${BLUE}docker compose up -d${NC}"
fi
