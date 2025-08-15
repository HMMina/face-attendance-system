#!/bin/bash
# Script deploy kiosk device
set -e

# Cài đặt Flutter
flutter pub get
flutter build apk

# Copy APK sang thiết bị
# adb install build/app/outputs/flutter-apk/app-release.apk

echo "Kiosk device deploy hoàn tất!"
