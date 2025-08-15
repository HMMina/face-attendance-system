#!/bin/bash
# Script cấu hình local server
set -e

# Tạo venv và cài đặt backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Khởi tạo database
alembic upgrade head

echo "Local server setup hoàn tất!"
