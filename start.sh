#!/bin/bash
echo "📦 Installing Playwright browsers..."
python -m playwright install chromium
echo "✅ Starting Flask app..."
gunicorn app:app
