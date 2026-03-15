import os
import asyncio
import random
import threading
from flask import Flask, render_template_string, request, jsonify
from playwright.async_api import async_playwright

app = Flask(__name__)

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Facebook React Bot</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
            text-align: center;
            font-size: 28px;
        }
        h1 span {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .form-group {
            margin-bottom: 25px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 600;
            font-size: 14px;
        }
        textarea, input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            transition: all 0.3s;
            font-family: monospace;
        }
        textarea:focus, input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
        }
        textarea {
            height: 120px;
            resize: vertical;
        }
        .button-group {
            display: flex;
            gap: 15px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }
        button {
            flex: 1;
            padding: 15px 25px;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 16px;
            min-width: 120px;
        }
        .btn-start {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-stop {
            background: #f44336;
            color: white;
        }
        .btn-status {
            background: #4CAF50;
            color: white;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        .status-card {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
            border-left: 4px solid #667eea;
        }
        .status-item {
            display: flex;
            justify-content: space-between;
            margin: 12px 0;
            padding: 8px 0;
            border-bottom: 1px dashed #dee2e6;
        }
        .status-label {
            font-weight: 600;
            color: #555;
        }
        .status-value {
            color: #333;
            font-weight: 500;
        }
        .badge {
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge-success {
            background: #d4edda;
            color: #155724;
        }
        .badge-danger {
            background: #f8d7da;
            color: #721c24;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #999;
            font-size: 12px;
        }
        .url-box {
            background: #f0f0f0;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            word-break: break-all;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 <span>Facebook React Bot</span></h1>
        
        <div class="form-group">
            <label>📝 Facebook Cookie</label>
            <textarea id="cookie" placeholder="datr=xxx; c_user=xxx; xs=xxx; ..."></textarea>
        </div>
        
        <div class="form-group">
            <label>🔗 Target URL (Optional)</label>
            <input type="url" id="targetUrl" placeholder="https://www.facebook.com/...">
        </div>
        
        <div class="button-group">
            <button class="btn-start" onclick="startBot()" id="startBtn">▶️ Start Bot</button>
            <button class="btn-stop" onclick="stopBot()" id="stopBtn" disabled>⏹️ Stop Bot</button>
            <button class="btn-status" onclick="checkStatus()">🔄 Refresh</button>
        </div>
        
        <div class="status-card">
            <h3 style="margin-bottom: 15px; color: #333;">📊 Current Status</h3>
            <div class="status-item">
                <span class="status-label">Bot Status:</span>
                <span class="status-value" id="botStatus">⏳ Stopped</span>
            </div>
            <div class="status-item">
                <span class="status-label">Total Reacts:</span>
                <span class="status-value" id="totalReacts">0</span>
            </div>
            <div class="status-item">
                <span class="status-label">Current Page:</span>
                <span class="status-value" id="currentPage">-</span>
            </div>
            <div class="status-item">
                <span class="status-label">Last Error:</span>
                <span class="status-value" id="error">None</span>
            </div>
        </div>
        
        <div class="url-box">
            🌐 Your Bot URL: <span id="botUrl"></span>
        </div>
        
        <div class="footer">
            ⚡ Bot is running on Heroku | Made with ❤️
        </div>
    </div>

    <script>
        // Show current URL
        document.getElementById('botUrl').textContent = window.location.href;
        
        async function startBot() {
            const cookie = document.getElementById('cookie').value;
            const targetUrl = document.getElementById('targetUrl').value;
            
            if (!cookie) {
                alert('❌ Please enter Facebook cookie!');
                return;
            }
            
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            
            const response = await fetch('/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    cookie: cookie,
                    target_url: targetUrl
                })
            });
            
            const data = await response.json();
            alert(data.message);
            checkStatus();
        }
        
        async function stopBot() {
            const response = await fetch('/stop', {method: 'POST'});
            const data = await response.json();
            
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            
            alert(data.message);
            checkStatus();
        }
        
        async function checkStatus() {
            const response = await fetch('/status');
            const data = await response.json();
            
            const statusEl = document.getElementById('botStatus');
            statusEl.textContent = data.is_running ? '🟢 Running' : '🔴 Stopped';
            document.getElementById('totalReacts').textContent = data.total_reacts;
            document.getElementById('currentPage').textContent = data.current_page || '-';
            document.getElementById('error').textContent = data.error || 'None';
            
            if (data.is_running) {
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
            } else {
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
            }
        }
        
        // Auto refresh every 10 seconds
        setInterval(checkStatus, 10000);
    </script>
</body>
</html>
"""

# Bot Class
class FacebookBot:
    def __init__(self):
        self.is_running = False
        self.total_reacts = 0
        self.current_page = None
        self.error = None
        self.playwright = None
        self.browser = None
        self.page = None
        
    async def start(self, cookie_string, target_url=None):
        try:
            self.is_running = True
            self.error = None
            
            # Playwright start
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            context = await self.browser.new_context()
            
            # Parse cookies
            cookies = []
            for c in cookie_string.split(';'):
                if '=' in c:
                    name, value = c.strip().split('=', 1)
                    cookies.append({
                        'name': name.strip(),
                        'value': value.strip(),
                        'domain': '.facebook.com',
                        'path': '/'
                    })
            
            if cookies:
                await context.add_cookies(cookies)
            
            self.page = await context.new_page()
            
            # Navigate
            if target_url:
                await self.page.goto(target_url)
                self.current_page = target_url
            else:
                await self.page.goto('https://www.facebook.com')
                self.current_page = 'Facebook Home'
            
            # Main loop
            await self.bot_loop()
            
        except Exception as e:
            self.error = str(e)
            self.is_running = False
    
    async def bot_loop(self):
        while self.is_running:
            try:
                # Scroll
                await self.page.mouse.wheel(0, random.randint(400, 900))
                await asyncio.sleep(random.randint(2, 4))
                
                # Find Like buttons
                likes = await self.page.query_selector_all('[aria-label="Like"]')
                
                if likes and self.is_running:
                    btn = random.choice(likes)
                    await btn.hover()
                    await asyncio.sleep(1)
                    
                    # Click Love
                    love = await self.page.query_selector('[aria-label="Love"]')
                    if love and self.is_running:
                        await love.click()
                        self.total_reacts += 1
                        print(f'❤️ React #{self.total_reacts}')
                
                await asyncio.sleep(random.randint(3, 7))
                
            except Exception as e:
                print(f'Loop error: {e}')
                await asyncio.sleep(5)
    
    async def stop(self):
        self.is_running = False
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

# Global bot instance
bot = FacebookBot()
bot_thread = None

def run_bot(cookie, target_url):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bot.start(cookie, target_url))

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/start', methods=['POST'])
def start_bot():
    global bot_thread
    
    if bot.is_running:
        return jsonify({'status': 'error', 'message': 'Bot already running!'})
    
    data = request.json
    cookie = data.get('cookie')
    target_url = data.get('target_url', '')
    
    if not cookie:
        return jsonify({'status': 'error', 'message': 'Cookie required!'})
    
    bot_thread = threading.Thread(target=run_bot, args=(cookie, target_url))
    bot_thread.daemon = True
    bot_thread.start()
    
    return jsonify({'status': 'success', 'message': 'Bot started!'})

@app.route('/stop', methods=['POST'])
def stop_bot():
    if bot.is_running:
        asyncio.run_coroutine_threadsafe(bot.stop(), asyncio.new_event_loop())
        return jsonify({'status': 'success', 'message': 'Bot stopping...'})
    return jsonify({'status': 'error', 'message': 'Bot not running!'})

@app.route('/status')
def get_status():
    return jsonify({
        'is_running': bot.is_running,
        'total_reacts': bot.total_reacts,
        'current_page': bot.current_page,
        'error': bot.error
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
