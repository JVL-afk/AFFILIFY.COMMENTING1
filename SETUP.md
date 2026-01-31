# AFFILIFY.COMMENTING1 Setup Guide

## Prerequisites

- Python 3.11+
- pip3
- Git

## Installation Steps

### 1. Clone the Repository

```bash
gh repo clone AFFILIFY.COMMENTING1
cd AFFILIFY.COMMENTING1
```

### 2. Set Up Environment Variables

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your actual API keys:
- **SADCAPTCHA_API_KEY**: Get from [SadCaptcha](https://www.sadcaptcha.com/)
- **GEMINI_API_KEY**: Get from [Google AI Studio](https://aistudio.google.com/apikey)

### 3. Run Setup Script

```bash
./setup.sh
```

Or manually install dependencies:

```bash
sudo pip3 install -r requirements.txt
sudo playwright install chromium
```

### 4. Start the Program

```bash
export $(cat .env | grep -v '^#' | xargs) && python3.11 main_launcher.py
```

## Features

- 🧠 **JARVIS AI Brain**: Powered by Gemini 2.5 Flash
- 📊 **Real-time Dashboard**: Monitor at http://localhost:8000
- 🤖 **TikTok Automation**: Automated commenting system
- 🎯 **Smart Targeting**: AI-powered video discovery
- 🛡️ **Anti-Detection**: Stealth mode with human-like behavior

## Security Notes

⚠️ **IMPORTANT**: Never commit your `.env` file to git. It contains sensitive API keys.

The `.gitignore` file is already configured to exclude:
- `.env` files
- Database files
- Log files
- Cache files

## Troubleshooting

### Missing Dependencies

If you encounter `ModuleNotFoundError`, install the missing package:

```bash
sudo pip3 install <package-name>
```

### Playwright Browser Issues

Reinstall Playwright browsers:

```bash
sudo playwright install chromium
```

### API Key Errors

Ensure your `.env` file contains valid API keys and is properly formatted.
