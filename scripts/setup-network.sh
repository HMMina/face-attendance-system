#!/bin/bash
# Script cấu hình mạng local
set -e

# Cấu hình mDNS (Avahi)
systemctl start avahi-daemon
systemctl enable avahi-daemon

# Cấu hình WiFi hotspot (nmcli)
nmcli dev wifi hotspot ifname wlan0 ssid FaceAttendance password 12345678

echo "Network setup hoàn tất!"
