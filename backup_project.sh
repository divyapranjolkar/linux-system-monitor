
#!/usr/bin/env bash

set -Eeuo pipefail

# Locate the project directory from this script's location.
PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

BACKUP_DIR="$PROJECT_DIR/backups"

TIMESTAMP="$(date '+%Y%m%d_%H%M%S')"

BACKUP_FILE="$BACKUP_DIR/linux_monitor_$TIMESTAMP.tar.gz"

# Create the backup directory if it does not exist.
mkdir -p "$BACKUP_DIR"

echo "Starting Linux System Monitor backup..."

# Archive the project while excluding unnecessary files.
tar -czf "$BACKUP_FILE" \
    --exclude='./.venv' \
    --exclude='./__pycache__' \
    --exclude='*/__pycache__' \
    --exclude='./backups' \
    --exclude='./logs' \
    --exclude='./.git' \
    -C "$PROJECT_DIR" .

# Verify that the archive can be read.
if tar -tzf "$BACKUP_FILE" > /dev/null; then

    echo "Backup completed successfully."
    echo "Backup location: $BACKUP_FILE"
    echo "Backup size:"

    ls -lh "$BACKUP_FILE"

else

    echo "ERROR: Backup verification failed."

    rm -f "$BACKUP_FILE"

    exit 1

fi

# Remove backups older than seven days.
find "$BACKUP_DIR" \
    -maxdepth 1 \
    -type f \
    -name 'linux_monitor_*.tar.gz' \
    -mtime +7 \
    -delete

echo "Old backup cleanup completed."
