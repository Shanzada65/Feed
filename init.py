import subprocess
import sys
import os

print("📦 Installing Playwright browsers...")
subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
print("✅ Playwright browsers installed!")
