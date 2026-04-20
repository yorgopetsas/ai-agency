# 🤖 AI Agency Complete Tutorial Set


Ollama
======
# 🦙 Ollama Complete Tutorial

## Why Ollama?
- Free - runs locally
- Private - no data leaves your Mac
- Fast - no internet needed after install

## Install Steps:

### 1. Install Homebrew (if needed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

### 2. Install Python 3.11
brew install python@3.11

### 3. Install Ollama
curl -fsSL https://ollama.com | sh

### 4. Download Model
ollama pull llama3

### 5. Run!
python3.11 agency.py "hello world"

## Troubleshooting:
- If ollama command not found: restart terminal
- If port in use: pkill -f ollama


OpenAI
======
# 🔥 OpenAI Complete Tutorial

## Why OpenAI?
- Best AI quality
- Reliable service

## Steps:

### 1. Get API Key
1. Go to platform.openai.com/api-keys
2. Create account  
3. Make secret key

### 2. Set Key
export OPENAI_API_KEY="sk-\..."

### 3. Run!
python3.11 agency.py "your task"


Anthropic
=========
# 🔵 Anthropic Complete Tutorial

## Why Anthropic?
- Great for coding
- Claude AI

## Steps:

### 1. Get API Key
1. Go to console.anthropic.com
2. Create API key

### 2. Set Key
export ANTHROPIC_API_KEY="sk-ant-\..."

### 3. Run!
python3.11 agency.py "your task"


Hybrid
======
# ⚡ Hybrid Complete Tutorial

## Why Hybrid?
- Fast + Smart = Best of both

## Steps:

### 1. Install Ollama (from Ollama tutorial)
### 2. Get OpenAI key (from OpenAI tutorial)

### 3. Set both:
export OPENAI_API_KEY="sk-\..."
export OLLAMA_HOST="http://localhost:11434"

### 4. Run smart!
python3.11 agency.py "complex task"

