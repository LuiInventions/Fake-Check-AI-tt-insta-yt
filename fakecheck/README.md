# FakeCheck

Fake News Detector für Social Media Plattformen. KI-gestützt zur Analyse von Videos auf Falschinformationen.

## Features
- **Video Download Pipeline**: Native yt-dlp integration.
- **Transcript Extraction**: Local whisper models for accurate audio-to-text.
- **Truth Verification**: LLM analysis utilizing GPT-4o-mini to verify statements.
- **Generative AI Chat**: Talk directly to the context bot about the assessed video content.

## Tech Stack
- Frontend: Next.js 15, Tailwind CSS
- Backend: FastAPI, Celery, Redis
- Infrastructure: Docker Compose, Nginx Reverse Proxy

## Installation

### Local Development
```bash
# Clone the repository
git clone <repo-url>
cd fakecheck

# Create the environment file
cp .env.example .env

# Start the stack
docker compose up -d --build
```
Access the application locally via `http://localhost:3000` (or proxy logic through your OS configs).

### Production
For production deployment, overlay the secondary configuration which limits Docker metrics, enforces auto-restarts, and invokes `healthchecks`:
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

You can use the built-in update scripts to perform seamless upgrades via `git pull`:
```bash
./update.sh
```

## API Endpoints
- `POST /api/video/analyze` | Request Body: `{"url": "domain.com/video"}`
- `GET /api/video/{id}` | Fetches status and AI analysis payload
- `POST /api/chat/` | Send message against video context
- `GET /api/chat/{id}/history` | Retrieves Chat History
