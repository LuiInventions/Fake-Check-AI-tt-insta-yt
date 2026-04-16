# Fake Check App 🕵️‍♂️ (Fake Check AI)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/LuiInventions/Fake-Check-AI-tt-insta-yt)

**Fake Check App** (Fake Check AI) is a powerful open-source tool designed to verify social media videos (TikTok, Instagram, YouTube) for misinformation and AI manipulation.

The bot combines state-of-the-art AI (**OpenAI GPT-4o & Whisper**) with live web search to not just "guess" claims, but to back them up with real sources.

> [!IMPORTANT]
> **This application is now Telegram-only.** The web frontend has been removed to simplify the infrastructure and focus on the chat experience.

## 🌟 Core Features
- **AI & Deepfake Detection**: Detects if a video was AI-generated or manipulated.
- **Real-time Fact-Checking**: Extracts claims from the video and checks them immediately via Google/DuckDuckGo & News APIs.
- **Telegram Integration**: Your bot is your interface – send it a link, and it responds with a full analysis.
- **No Public Server Needed**: Runs locally using Telegram Polling.
- **Multi-platform**: Full support for TikTok, Instagram Reels, and YouTube Shorts/Videos.

## 🚀 Getting Started

### 📦 Prerequisites
- **[Docker Desktop](https://www.docker.com/)** (Must be running before starting setup)
-
- **OpenAI API Key** ([Get it here](https://platform.openai.com/api-keys))
-
- **RapidAPI Key** ([Get it here](https://rapidapi.com/))
- 
- IMPORTANT: activate these two APIs for RapidAPI:
-
- Instagram Downloader API: https://rapidapi.com/irrors-apis/api/instagram-looter2
- News API: https://rapidapi.com/bonaipowered/api/news-api14
- (bot has already acces to a browser, so the news API is optional)
- 
- **Telegram Bot Token** ([@BotFather](https://t.me/botfather))

### 🛠️ Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/LuiInventions/Fake-Check-AI-tt-insta-yt
   cd fakecheck-app
   ```

2. **Interactive Setup**
   We have simplified the process. Just run the setup script for your operating system. It will ask for your API keys and configure the environment automatically.

   **For Windows (PowerShell):**
   ```powershell
   .\setup.ps1
   ```

   **For Linux/macOS:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Running the App**
   The setup script will ask if you want to start the containers immediately. If you want to start them manually later:
   ```bash
   docker compose up -d
   ```

## 🔍 How it Works
1. **Send Link**: Send any TikTok, Instagram, or YouTube link to your Telegram bot.
2. **Analysis**: The backend downloads the video, transcribes the audio, and performs a frame-by-frame AI detection.
3. **Fact-Check**: GPT-4o extracts key claims and searches the web for verification.
4. **Report**: You receive a comprehensive report directly in Telegram.

## 🔒 Security
This project is intended for local use. Your API keys are stored in a local `.env` file and are never shared.

## 📜 License
This project is licensed under the MIT License.
