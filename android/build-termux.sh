#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
: "${ANDROID_HOME:=$HOME/android-sdk}"
export ANDROID_HOME
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
echo "ANDROID_HOME=$ANDROID_HOME"
gradle :app:assembleDebug
printf '\nAPK: %s\n' "$PWD/app/build/outputs/apk/debug/app-debug.apk"
