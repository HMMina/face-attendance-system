#!/bin/bash
# Script giám sát thiết bị kiosk
set -e

while true; do
  curl -s http://localhost:8000/api/v1/devices/ | jq .
  sleep 10
done
