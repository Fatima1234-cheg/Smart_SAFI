#!/bin/bash

# SmartSafi - Smart City Management System
# Backup Script

set -e

# Configuration
BACKUP_DIR="/var/backups/smartsafi"
MONGODB_HOST="localhost"
MONGODB_PORT="27017"
MONGODB_DB="smart_city"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="smartsafi_backup_${DATE}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    log_error "Please run as root or with sudo"
    exit 1
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"

log_info "Starting backup process..."
log_info "Backup directory: $BACKUP_DIR"
log_info "Backup name: $BACKUP_NAME"

# Check MongoDB connection
log_info "Checking MongoDB connection..."
if ! mongosh --host "$MONGODB_HOST" --port "$MONGODB_PORT" --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    log_error "Cannot connect to MongoDB"
    exit 1
fi
log_info "MongoDB connection successful"

# Create MongoDB backup
log_info "Creating MongoDB backup..."
mongodump --host "$MONGODB_HOST" --port "$MONGODB_PORT" --db "$MONGODB_DB" --out "$BACKUP_DIR/$BACKUP_NAME/mongodb"

if [ $? -eq 0 ]; then
    log_info "MongoDB backup completed successfully"
else
    log_error "MongoDB backup failed"
    exit 1
fi

# Backup application files
log_info "Backing up application files..."

# Backup .env file
if [ -f "/opt/smartsafi/.env" ]; then
    cp "/opt/smartsafi/.env" "$BACKUP_DIR/$BACKUP_NAME/"
    log_info "Environment file backed up"
fi

# Backup configuration files
if [ -d "/opt/smartsafi/config" ]; then
    cp -r "/opt/smartsafi/config" "$BACKUP_DIR/$BACKUP_NAME/"
    log_info "Configuration files backed up"
fi

# Backup uploads
if [ -d "/opt/smartsafi/uploads" ]; then
    cp -r "/opt/smartsafi/uploads" "$BACKUP_DIR/$BACKUP_NAME/"
    log_info "Uploads backed up"
fi

# Create backup info file
cat > "$BACKUP_DIR/$BACKUP_NAME/backup_info.txt" << EOF
SmartSafi Backup Information
============================
Backup Name: $BACKUP_NAME
Backup Date: $(date)
Database: $MONGODB_DB
MongoDB Host: $MONGODB_HOST
MongoDB Port: $MONGODB_PORT
Backup Size: $(du -sh "$BACKUP_DIR/$BACKUP_NAME" | cut -f1)
EOF

log_info "Backup information file created"

# Create tar archive
log_info "Creating compressed archive..."
cd "$BACKUP_DIR"
tar -czf "$BACKUP_NAME.tar.gz" "$BACKUP_NAME"

if [ $? -eq 0 ]; then
    log_info "Compressed archive created: $BACKUP_NAME.tar.gz"
    # Remove uncompressed backup
    rm -rf "$BACKUP_NAME"
else
    log_warn "Failed to create compressed archive, keeping uncompressed backup"
fi

# Clean up old backups
log_info "Cleaning up old backups..."
find "$BACKUP_DIR" -name "smartsafi_backup_*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete
log_info "Backups older than $RETENTION_DAYS days have been removed"

# Calculate backup statistics
BACKUP_COUNT=$(find "$BACKUP_DIR" -name "smartsafi_backup_*.tar.gz" | wc -l)
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)

log_info "Backup Statistics:"
echo "  - Total backups: $BACKUP_COUNT"
echo "  - Total size: $BACKUP_SIZE"
echo "  - Retention period: $RETENTION_DAYS days"

log_info "Backup process completed successfully!"
exit 0
