#!/bin/bash
# Script backup dữ liệu local
set -e

tar czf data/backups/database/backup_$(date +%Y%m%d).tar.gz data/uploads/

echo "Backup local hoàn tất!"
