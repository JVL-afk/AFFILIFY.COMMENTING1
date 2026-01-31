#!/bin/bash
# AFFILIFY.COMMENTING1 Setup Script

echo "🚀 AFFILIFY Setup Script"
echo "========================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it and add your API keys."
    echo ""
    echo "Required API keys:"
    echo "  - SADCAPTCHA_API_KEY: Get from https://www.sadcaptcha.com/"
    echo "  - GEMINI_API_KEY: Get from https://aistudio.google.com/apikey"
    echo ""
    exit 1
fi

echo "✅ .env file found"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
sudo pip3 install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
sudo playwright install chromium

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the program, run:"
echo "  export \$(cat .env | grep -v '^#' | xargs) && python3.11 main_launcher.py"
echo ""
