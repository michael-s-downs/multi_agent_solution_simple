# Multi-Agent WebApp Setup Guide

This guide walks you through setting up the required environment, services, and configurations to run the Multi-Agent WebApp locally.

---

## 📦 Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Install Dapr CLI

```bash
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | /bin/bash
```

---

## 🔧 Install Redis

### On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install redis-server
```

### On macOS:

```bash
brew install redis
```

### On Windows (using Docker):

```bash
docker run -d --name redis -p 6379:6379 redis:alpine
```

---

## ☁️ Azure OpenAI Setup

### 1. Create Azure OpenAI Resource

```bash
# Login to Azure
az login

# Create resource group
az group create --name "multi-agent-rg" --location "East US"

# Create Azure OpenAI resource
az cognitiveservices account create \
  --name "multi-agent-openai" \
  --resource-group "multi-agent-rg" \
  --location "East US" \
  --kind "OpenAI" \
  --sku "S0"
```

### 2. Deploy GPT Model

```bash
# Deploy GPT-4 or GPT-3.5-turbo model
az cognitiveservices account deployment create \
  --resource-group "multi-agent-rg" \
  --name "multi-agent-openai" \
  --deployment-name "gpt-4" \
  --model-name "gpt-4" \
  --model-version "0613" \
  --model-format "OpenAI" \
  --scale-settings-scale-type "Standard"
```

### 3. Get API Keys and Endpoint

```bash
# Get API key
az cognitiveservices account keys list \
  --resource-group "multi-agent-rg" \
  --name "multi-agent-openai"

# Get endpoint
az cognitiveservices account show \
  --resource-group "multi-agent-rg" \
  --name "multi-agent-openai" \
  --query "properties.endpoint"
```

### 4. Update `.env` File

```env
AZURE_OPENAI_API_KEY=your_actual_api_key_from_step_3
AZURE_OPENAI_ENDPOINT=https://multi-agent-openai.openai.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4
```

---

## 🔗 Optional: GitHub Integration

### 1. Create GitHub Repository

```bash
# Create new repo on GitHub (via web UI or CLI)
gh repo create your-username/multi-agent-webapp --public

# Initialize git in your project
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-username/multi-agent-webapp.git
git push -u origin main
```

### 2. Generate GitHub Token

- Go to **GitHub Settings → Developer Settings → Personal access tokens**
- Generate a token with `repo` permissions
- Add it to your `.env` file:

```env
GITHUB_TOKEN=your_github_token
```

---

## ✅ Complete Setup Checklist

- [x] Azure OpenAI Resource - Created and configured  
- [x] GPT Model Deployment - Deployed and accessible  
- [x] API Keys - Retrieved and added to `.env`  
- [x] Redis Server - Installed and running  
- [x] Dapr CLI - Installed and initialized  
- [x] Python Dependencies - Installed via pip  
- [x] Project Structure - Fixed imports and paths  
- [x] GitHub Repository - Created (optional)  

---

## 🧪 Final Test

```bash
# Initialize Dapr
dapr init

# Test Redis connection
redis-cli ping

# Run the project
chmod +x run.sh
./run.sh
```

Your Streamlit app should now be accessible at:  
👉 **http://localhost:8501**
