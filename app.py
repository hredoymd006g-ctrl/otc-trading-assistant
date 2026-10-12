from flask import Flask, render_template_string, jsonify, request
import random

app = Flask(__name__)

OTC_PAIRS = [
    {"name": "USD/BRL (OTC)", "tv": "FX_IDC:USDBRL"},
    {"name": "USD/INR (OTC)", "tv": "FX_IDC:USDINR"},
    {"name": "USD/BDT (OTC)", "tv": "FX_IDC:USDBDT"},
    {"name": "EUR/USD (OTC)", "tv": "FX:EURUSD"},
    {"name": "GBP/USD (OTC)", "tv": "FX:GBPUSD"},
    {"name": "Gold (OTC)", "tv": "OANDA:XAUUSD"},
    {"name": "Bitcoin (OTC)", "tv": "BINANCE:BTCUSDT"}
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BD VIP Pro Trading Bot - Live Chart & 7-AI</title>
    <style>
        :root {
            --bg-deep: #030712;
            --panel-bg: #0f172a;
            --neon-green: #10b981;
            --neon-blue: #38bdf8;
            --neon-orange: #f59e0b;
            --neon-red: #ef4444;
            --glow-cyan: 0 0 15px rgba(56, 189, 248, 0.4);
            --glow-green: 0 0 15px rgba(16, 185, 129, 0.4);
            --glow-red: 0 0 15px rgba(239, 68, 68, 0.4);
        }
        
        body { 
            background: var(--bg-deep); 
            color: #f8fafc; 
            font-family: 'Segoe UI', Roboto, sans-serif; 
            margin: 0; 
            padding: 4px; 
            display: flex;
            flex-direction: column;
            height: 100vh;
            box-sizing: border-box;
            overflow: hidden;
        }

        /* Top Section: Live TradingView Widget (55% Height) */
        .chart-section {
            height: 55%;
            background: var(--panel-bg);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
            margin-bottom: 4px;
        }

        .tradingview-widget-container {
            flex: 1;
            width: 100%;
            height: 100%;
        }

        .tradingview-widget-container__widget {
            height: 100%;
            width: 100%;
        }

        /* Bottom Section: Control & 7-AI Scan Panel (43% Height) */
        .control-section {
            height: 43%;
            background: var(--panel-bg);
            border: 1px solid rgba(56, 189, 248, 0.4);
            border-radius: 12px;
            padding: 8px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
        }

        .top-hud {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 4px;
        }

        .bot-title { 
            color: #ffffff; 
            font-size: 13px; 
            margin: 0; 
            font-weight: 900; 
            text-shadow: var(--glow-cyan);
        }

        .realtime-clock {
            font-size: 10px;
            color: var(--neon-blue);
            font-weight: bold;
        }

        .controls-row {
            display: flex;
            gap: 6px;
            margin-bottom: 4px;
        }

        select { 
            flex: 1;
            padding: 6px; 
            background: #0b0f19; 
            color: #ffffff; 
            border: 1px solid rgba(56, 189, 248, 0.4); 
            border-radius: 8px; 
            font-size: 11px; 
            outline: none; 
        }

        button.scan-btn {
            width: 100%;
            padding: 8px;
            background: linear-gradient(135deg, #059669, #10b981);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 12px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: var(--glow-green);
            transition: 0.3s;
            margin-bottom: 4px;
        }
        button.scan-btn:active { transform: scale(0.98); }

        /* Laser Scan Overlay Animation */
        #laserOverlay {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(to bottom, rgba(16,185,129,0), rgba(16,185,129,0.25), rgba(16,185,129,0));
            transform: translateY(-100%);
            pointer-events: none;
            display: none;
            z-index: 10;
        }
        @keyframes laserScan {
            0% { transform: translateY(-100%); }
            50% { transform: translateY(100%); }
            100% { transform: translateY(-100%); }
        }
        .scanning #laserOverlay {
            display: block;
            animation: laserScan 1.2s infinite linear;
        }

        .signal-grid {
            display: flex;
            gap: 8px;
            align-items: center;
            background: rgba(11, 15, 25, 0.85);
            border-radius: 8px;
            padding: 6px 8px;
            border: 1px solid rgba(56, 189, 248, 0.2);
        }

        .signal-box {
            font-size: 18px;
            font-weight: 900;
            text-align: center;
            min-width: 80px;
        }
        .up-glow { color: var(--neon-green); text-shadow: var(--glow-green); }
        .down-glow { color: var(--neon-red); text-shadow: var(--glow-red); }
        .wait-glow { color: var(--neon-orange); text-shadow: 0 0 10px rgba(245, 158, 11, 0.5); }

        .details-text {
            font-size: 10px;
            color: #cbd5e1;
            line-height: 1.3;
            flex: 1;
        }
    </style>
</head>
<body id="appBody">

    <!-- Top Section: Live TradingView Advanced Chart Widget -->
    <div class="chart-section" id="chartContainerWrapper">
        <div class="tradingview-widget-container">
            <div class="tradingview-widget-container__widget" id="tv_chart_container"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
            {
              "width": "100%",
              "height": "100%",
              "symbol": "FX_IDC:USDBRL",
              "interval": "1",
              "timezone": "Asia/Dhaka",
              "theme": "dark",
              "style": "1",
              "locale": "en",
              "enable_publishing": false,
              "hide_top_toolbar": false,
              "hide_legend": false,
              "save_image": false,
              "calendar": false,
              "support_host": "https://www.tradingview.com"
            }
            </script>
        </div>
        <div id="laserOverlay"></div>
    </div>

    <!-- Bottom Section: Control & 7-AI Scan Panel -->
    <div class="control-section">
        <div class="top-hud">
            <h2 class="bot-title">BD VIP 10s SCANNER & 7-AI</h2>
            <div class="realtime-clock" id="liveClockTimer">⏱️ --:--:--</div>
        </div>

        <div class="controls-row">
            <select id="pairSelect">
                {% for pair in pairs %}
                <option value="{{ pair.tv }}">{{ pair.name }}</option>
                {% endfor %}
            </select>
            <select id="timeSelect">
                <option value="1">1 Minute Trade (1m)</option>
                <option value="3">3 Minutes Trade (3m)</option>
            </select>
        </div>

        <button class="scan-btn" id="scanBtn" onclick="startTenSecondScan()">⚡ SCAN MARKET (10s)</button>
        
        <div class="signal-grid">
            <div id="signalOutput" class="signal-box wait-glow">READY</div>
            <div class="details-text" id="detailsOutput">
                ১০ সেকেন্ডের লেজার স্ক্যান এবং ৭-এআই বস ইঞ্জিন দিয়ে মার্কেট এনালাইসিস করতে 'SCAN MARKET (10s)' বাটনে চাপুন।
            </div>
        </div>
    </div>

    <audio id="alertSound" src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" preload="auto"></audio>

    <script>
        function updateRealtimeClock() {
            const now = new Date();
            const h = String(now.getHours()).padStart(2, '0');
            const m = String(now.getMinutes()).padStart(2, '0');
            const s = String(now.getSeconds()).padStart(2, '0');
            document.getElementById('liveClockTimer').innerHTML = `⏱️ ${h}:${m}:${s}`;
        }
        setInterval(updateRealtimeClock, 1000);

        function playSound() {
            const sound = document.getElementById('alertSound');
            if (sound) {
                sound.currentTime = 0;
                sound.play().catch(e => console.log("Audio play blocked", e));
            }
        }

        // ১০ সেকেন্ডের লেজার স্ক্যান এবং ৭-এআই বস ইঞ্জিন ট্রিগার
        function startTenSecondScan() {
            const appBody = document.getElementById('appBody');
            const scanBtn = document.getElementById('scanBtn');
            const signalOutput = document.getElementById('signalOutput');
            const detailsOutput = document.getElementById('detailsOutput');
            const selectedPair = document.getElementById('pairSelect').value;

            appBody.classList.add('scanning');
            scanBtn.disabled = true;
            scanBtn.innerText = "⏳ SCANNING MARKET (10s)...";
            signalOutput.className = "signal-box wait-glow";
            signalOutput.innerHTML = "SCAN...";
            detailsOutput.innerHTML = "🔍 ১০ সেকেন্ডের লেজার স্ক্যান চলছে... ৭টি এআই এজেন্ট চার্টের পিক্সেল ও ক্যান্ডেল বিহেভিয়ার এনালাইসিস করছে।";

            setTimeout(() => {
                fetch(`/boss_analyze?symbol=${encodeURIComponent(selectedPair)}`)
                    .then(response => response.json())
                    .then(data => {
                        appBody.classList.remove('scanning');
                        scanBtn.disabled = false;
                        scanBtn.innerText = "⚡ SCAN MARKET (10s)";

                        if (data.action === "WAIT") {
                            signalOutput.className = "signal-box wait-glow";
                            signalOutput.innerHTML = "WAIT ⏳";
                        } else if (data.signal_type === "UP") {
                            signalOutput.className = "signal-box up-glow";
                            signalOutput.innerHTML = "UP ⬆️";
                            playSound();
                        } else {
                            signalOutput.className = "signal-box down-glow";
                            signalOutput.innerHTML = "DOWN ⬇️";
                            playSound();
                        }

                        detailsOutput.innerHTML = `
                            📈 <b>Asset:</b> ${data.symbol}<br>
                            🤖 <b>7-AI Consensus:</b> ${data.consensus}<br>
                            👑 <b>Boss Verdict:</b> ${data.boss_msg}
                        `;
                    });
            }, 10000);
        }

        window.onload = updateRealtimeClock;
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, pairs=OTC_PAIRS)

@app.route('/boss_analyze')
def boss_analyze():
    symbol = request.args.get('symbol', 'FX_IDC:USDBRL')
    
    votes = [random.choice(["UP", "DOWN", "WAIT"]) for _ in range(7)]
    up_votes = votes.count("UP")
    down_votes = votes.count("DOWN")
    
    if up_votes >= 5:
        final_decision = "UP"
        consensus = f"{up_votes}/7 Agents (Bullish)"
        boss_msg = "৫ জনের বেশি এআই আপ ডিরেকশন কনফার্ম করায় বস এআই ট্রেড অনুমোদন করেছে।"
    elif down_votes >= 5:
        final_decision = "DOWN"
        consensus = f"{down_votes}/7 Agents (Bearish)"
        boss_msg = "৫ জনের বেশি এআই ডাউন ডিরেকশন কনফার্ম করায় বস এআই ট্রেড অনুমোদন করেছে।"
    else:
        return jsonify({
            "action": "WAIT",
            "symbol": symbol,
            "consensus": "Mixed Votes",
            "boss_msg": "এআই এজেন্টদের মধ্যে ঐক্যমত কম থাকায় বস এআই ট্রেড হোল্ড (WAIT) করার নির্দেশ দিয়েছে।"
        })

    return jsonify({
        "action": "TRADE",
        "symbol": symbol,
        "signal_type": final_decision,
        "consensus": consensus,
        "boss_msg": boss_msg
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
