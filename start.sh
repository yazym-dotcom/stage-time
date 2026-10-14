#!/usr/bin/env bash
# Stage Time launcher for macOS and Linux.
#
# The first run creates a private Python workspace at ~/.stage-time/venv and
# installs what the app needs (5 to 15 minutes). Later runs start in seconds.
#
#   chmod +x start.sh    (once)
#   ./start.sh           (optional port: ./start.sh 8001)

set -e
here="$(cd "$(dirname "$0")" && pwd)"
venv="${HOME}/.stage-time/venv"
py="$venv/bin/python"
port="${1:-8000}"

if [ ! -x "$py" ]; then
  echo "First run: creating the app's private workspace at $venv"
  if command -v python3.12 >/dev/null 2>&1; then python3.12 -m venv "$venv"
  elif command -v python3.13 >/dev/null 2>&1; then python3.13 -m venv "$venv"
  elif command -v python3.11 >/dev/null 2>&1; then python3.11 -m venv "$venv"
  else python3 -m venv "$venv"; fi
  echo "Installing the app's parts. Expect a wall of scrolling text for 5 to 15 minutes."
  "$py" -m pip install --disable-pip-version-check -r "$here/requirements.txt"
fi

command -v ffmpeg >/dev/null 2>&1 || echo "ffmpeg is not installed, so recordings cannot be converted. Run: brew install ffmpeg"
command -v ollama >/dev/null 2>&1 || echo "Ollama is not installed. Coaching, roleplay follow-ups and lookups stay off until it is: https://ollama.com/download then: ollama pull qwen2.5:3b"

cd "$here"
echo "Stage Time is starting on http://127.0.0.1:$port"
echo "Leave this window open. Press Ctrl+C to stop the app."
if [ -z "$STAGE_TIME_NO_BROWSER" ]; then
  ( sleep 4; open "http://127.0.0.1:$port" 2>/dev/null || xdg-open "http://127.0.0.1:$port" 2>/dev/null || true ) &
fi
exec "$py" -m uvicorn main:app --host 127.0.0.1 --port "$port"
