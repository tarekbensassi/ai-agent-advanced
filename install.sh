#!/usr/bin/env bash
set -e

echo "🚀 Setup AI Agent (advanced)"

# System deps
sudo apt update -y
sudo apt install -y python3 python3-pip git curl ca-certificates

# Install Ollama if not present
if ! command -v ollama >/dev/null 2>&1; then
  curl -fsSL https://ollama.com/install.sh | sh
fi

# Start Ollama in background (idempotent)
if ! pgrep -f "ollama serve" >/dev/null 2>&1; then
  nohup ollama serve > ~/ollama.log 2>&1 &
  sleep 8
fi

# Pull models only if missing
for m in mistral codellama llama3; do
  if ! ollama list | grep -q "$m"; then
    echo "📦 pulling $m"
    ollama pull $m
  else
    echo "✔ $m already present"
  fi
done

mkdir -p ~/ai-agent
cp agent.py ~/ai-agent/agent.py

echo "✅ Done. Run: python3 ~/ai-agent/agent.py"
