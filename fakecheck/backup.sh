#!/bin/bash
cd "$(dirname "$0")"

BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
echo "Starting FakeCheck Backup..."

mkdir -p $BACKUP_DIR

# Backup databases/data volumes
cp -r data/ $BACKUP_DIR/ 2>/dev/null || true

# Backup environment config
cp .env $BACKUP_DIR/ 2>/dev/null || true

echo "Backup successfully saved to $BACKUP_DIR"
