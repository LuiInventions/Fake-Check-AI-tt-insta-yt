#!/bin/bash
cd "$(dirname "$0")"

echo "Starting FakeCheck Update Process..."
git pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
docker system prune -f

echo "Update complete! You can verify status with 'docker compose ps'"
