#!/bin/bash
# Script kiểm tra kết nối mạng
set -e

ping -c 4 8.8.8.8
ping -c 4 localhost
curl -I http://localhost:8000/

# Kiểm tra mDNS
avahi-browse -a

echo "Network test hoàn tất!"
