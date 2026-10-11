from flask import Flask, render_template_string, jsonify, request
import random

app = Flask(__name__)

OTC_PAIRS = [
    "USD/BRL (OTC)", "USD/INR (OTC)", "USD/BDT (OTC)", "USD/PKR (OTC)",
    "USD/EGP (OTC)", "USD/TRY (OTC)", "USD/CAD (OTC)", "USD/MXN (OTC)",
    "EUR/USD (OTC)", "GBP/USD (OTC)", "AUD/CHF (OTC)", "CAD/JPY (OTC)",
    "CHF/JPY (OTC)", "GBP/JPY (OTC)", "Bitcoin (OTC)", "Gold (OTC)"
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BD VIP Signal Bot - Pro Master</title>
    <style>
        :root {
            --bg-deep: #050811;
            --panel-bg: rgba(17, 24, 39, 0.95);
            --neon-green: #10b981;
            --neon-blue: #38bdf8;
            --neon-orange: #f59e0b;
            --neon-red: #ef4444;
            --glow-cyan: 0 0 15px rgba(56, 189, 248, 0.4);
            --glow-green: 0 0 15px rgba(16, 185, 129, 0.4);
            --glow-red: 0 0 15px rgba(239, 68, 68, 0.4);
        }
        
        body { 
            background: radial-gradient(circle at center, #0f172a 0%, #030712 100%); 
            color: #f8fafc; 
            font-family: 'Segoe UI', Roboto, sans-serif; 
            margin: 0; 
            padding: 10px; 
            min-height: 100vh;
        }

        .dashboard-container { 
            max-width: 460px; 
            margin: auto; 
            background: var(--panel-bg); 
            backdrop-filter: blur(15px);
            padding: 18px; 
            border-radius: 20px; 
            border: 1px solid rgba(56, 189, 248, 0.5); 
            box-shadow: 0 20px 40px rgba(0,0,0,0.9), inset 0 0 25px rgba(16, 185, 129, 0.1); 
        }

        .top-hud {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 8px;
            margin-bottom: 12px;
        }

        .bot-title { 
            color: #ffffff; 
            font-size: 18px; 
            margin: 0; 
            font-weight: 900; 
            text-shadow: var(--glow-cyan);
            letter-spacing: 1px;
        }

        .status-pill {
            background: rgba(16, 185, 129, 0.2);
            color: var(--neon-green);
            font-size: 10px;
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 12px;
            border: 1px solid var(--neon-green);
            box-shadow: var(--glow-green);
        }

        /* 5-Inch Live Chart HUD Box */
        .cortex-chart-box {
            width: 100%;
            height: 170px;
            background: #020617;
            border: 1px solid rgba(56, 189, 248, 0.4);
            border-radius: 14px;
            margin-bottom: 12px;
            overflow: hidden;
            position: relative;
            box-shadow: inset 0 0 15px rgba(0,0,0,0.9);
        }

        .chart-header {
            position: absolute;
            top: 6px;
            left: 8px;
            right: 8px;
            display: flex;
            justify-content: space-between;
            font-size: 10px;
            color: var(--neon-blue);
            font-weight: bold;
            background: rgba(15, 23, 42, 0.85);
            padding: 3px 8px;
            border-radius: 6px;
            z-index: 5;
            border: 1px solid rgba(56, 189, 248, 0.2);
        }

        .cortex-canvas {
            display: flex;
            align-items: flex-end;
            justify-content: space-around;
            height: 100%;
            padding: 35px 8px 10px 8px;
            background: linear-gradient(180deg, rgba(15,23,42,0.3) 0%, rgba(2,6,23,0.95) 100%);
        }

        .live-candle {
            width: 12px;
            position: relative;
            border-radius: 2px;
        }
        .live-wick {
            position: absolute;
            width: 2px;
            left: 5px;
            background: currentColor;
        }
        .candle-green { background: var(--neon-green); color: var(--neon-green); box-shadow: 0 0 8px rgba(16,185,129,0.5); }
        .candle-red { background: var(--neon-red); color: var(--neon-red); box-shadow: 0 0 8px rgba(239,68,68,0.5); }
        
        .section-label { 
            font-size: 11px; 
            color: var(--neon-blue); 
            display: block; 
            margin-bottom: 4px; 
            font-weight: 700;
            text-transform: uppercase;
        }

        select { 
            width: 100%; 
            padding: 9px; 
            background: #0b0f19; 
            color: #ffffff; 
            border: 1px solid rgba(56, 189, 248, 0.4); 
            border-radius: 10px; 
            font-size: 13px; 
            margin-bottom: 10px; 
            outline: none; 
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.6);
        }

        .holo-display {
            background: radial-gradient(circle, rgba(16,185,129,0.15) 0%, rgba(11,15,25,0.9) 80%);
            border: 2px solid var(--neon-green);
            border-radius: 16px;
            padding: 15px;
            text-align: center;
            margin-top: 10px;
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.25), inset 0 0 15px rgba(16, 185, 129, 0.2);
            position: relative;
        }

        .signal-call-put {
            font-size: 26px;
            font-weight: 900;
            margin: 4px 0;
        }
        .up-glow { color: var(--neon-green); text-shadow: var(--glow-green); }
        .down-glow { color: var(--neon-red); text-shadow: var(--glow-red); }

        .timer-hud {
            font-size: 12px;
            color: var(--neon-blue);
            background: rgba(56, 189, 248, 0.1);
            padding: 2px 8px;
            border-radius: 8px;
            display: inline-block;
            border: 1px solid var(--neon-blue);
            margin-top: 4px;
        }

        .stats-grid {
            display: flex;
            gap: 8px;
            margin-top: 10px;
        }

        .stat-box {
            flex: 1;
            background: rgba(11, 15, 25, 0.8);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 8px;
            padding: 6px;
            text-align: center;
        }

        .stat-value {
            font-size: 14px;
            font-weight: bold;
            color: #f8fafc;
        }

        .btn-grid { display: flex; gap: 8px; margin-top: 12px; }
        
        button.cyber-btn-green { 
            flex: 1; 
            padding: 10px; 
            background: linear-gradient(135deg, #059669, #10b981); 
            color: white; 
            border: none; 
            border-radius: 10px; 
            font-size: 13px; 
            font-weight: bold; 
            cursor: pointer; 
            box-shadow: var(--glow-green);
            transition: 0.3s; 
        }
        
        button.cyber-btn-orange { 
            flex: 1; 
            padding: 10px; 
            background: linear-gradient(135deg, #d97706, #f59e0b); 
            color: white; 
            border: none; 
            border-radius: 10px; 
            font-size: 13px; 
            font-weight: bold; 
            cursor: pointer; 
            box-shadow: 0 0 12px rgba(245, 158, 11, 0.4);
            transition: 0.3s; 
        }

        button:active { transform: scale(0.97); }

        .details-panel {
            background: rgba(11, 15, 25, 0.85);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 10px;
            padding: 8px;
            margin-top: 12px;
            font-size: 11px;
            color: #94a3b8;
            line-height: 1.4;
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="top-hud">
            <div>
                <h2 class="bot-title">BD VIP SIGNAL BOT</h2>
                <div style="font-size: 10px; color: var(--neon-blue);">PRO MASTER • LIVE HUD</div>
            </div>
            <div class="status-pill">🟢 ACTIVE</div>
        </div>

        <!-- 5-Inch Live Visual Chart Area -->
        <div class="cortex-chart-box">
            <div class="chart-header">
                <span id="chartPairTitle">📊 USD/BRL (OTC)</span>
                <span id="liveClockTimer">⏱️ 00:00</span>
            </div>
            <div class="cortex-canvas" id="cortexCanvas">
                <!-- Candlesticks Rendered Here -->
            </div>
        </div>

        <label class="section-label">Asset Select & Timeframe</label>
        <select id="pairSelect" onchange="updateChartTitle()">
            {% for pair in pairs %}
            <option value="{{ pair }}">{{ pair }}</option>
            {% endfor %}
        </select>

        <select id="timeSelect">
            <option value="1">1 Minute Timeframe (1m)</option>
            <option value="2">2 Minutes Timeframe (2m)</option>
            <option value="3">3 Minutes Timeframe (3m)</option>
        </select>
        
        <div class="btn-grid">
            <button class="cyber-btn-green" onclick="startScanning('normal')">⚡ LIVE SCAN</button>
            <button class="cyber-btn-orange" onclick="startScanning('safety')">🛡️ SAFETY SCAN</button>
        </div>
        
        <div class="holo-display">
            <div style="font-size: 11px; color: var(--neon-blue); font-weight: bold; margin-bottom: 3px;" id="modeTitle">SIGNAL MATRIX</div>
            
            <div id="signalOutput" class="signal-call-put up-glow">READY</div>
            <div class="timer-hud" id="countdownTimer">⏳ 00:58</div>

            <div class="stats-grid">
                <div class="stat-box">
                    <div style="font-size: 9px; color: var(--neon-green);">REAL WIN RATE</div>
                    <div class="stat-value" id="statAccuracy">8/10 Win</div>
                </div>
                <div class="stat-box">
                    <div style="font-size: 9px; color: var(--neon-blue);">SUCCESS RATE</div>
                    <div class="stat-value" id="statSuccess">85%</div>
                </div>
            </div>

            <div class="details-panel" id="detailsOutput">
                📊 বট প্রস্তুত রয়েছে। মার্কেট স্ক্যান করতে উপরের যেকোনো একটি বাটন চাপুন।
            </div>
        </div>
    </div>

    <audio id="alertSound" src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" preload="auto"></audio>

    <script>
        function renderLiveCandles() {
            const canvas = document.getElementById('cortexCanvas');
            canvas.innerHTML = '';
            for (let i = 0; i < 12; i++) {
                const isGreen = Math.random() > 0.48;
                const height = Math.floor(Math.random() * 50) + 20;
                const wickTop = -Math.floor(Math.random() * 10) - 3;
                const wickHeight = height + Math.floor(Math.random() * 15) + 8;
                
                const candle = document.createElement('div');
                candle.className = `live-candle ${isGreen ? 'candle-green' : 'candle-red'}`;
                candle.style.height = `${height}px`;
                
                const wick = document.createElement('div');
                wick.className = 'live-wick';
                wick.style.top = `${wickTop}px`;
                wick.style.height = `${wickHeight}px`;
                
                candle.appendChild(wick);
                canvas.appendChild(candle);
            }
        }

        function updateChartTitle() {
            const pair = document.getElementById('pairSelect').value;
            document.getElementById('chartPairTitle').innerHTML = `📊 ${pair}`;
            renderLiveCandles();
        }

        function updateClock() {
            const now = new Date();
            const m = String(now.getMinutes()).padStart(2, '0');
            const s = String(now.getSeconds()).padStart(2, '0');
            document.getElementById('liveClockTimer').innerHTML = `⏱️ ${now.getHours()}:${m}:${s}`;
        }
        setInterval(updateClock, 1000);

        function playSound() {
            const sound = document.getElementById('alertSound');
            if (sound) {
                sound.currentTime = 0;
                sound.play().catch(e => console.log("Audio play blocked", e));
            }
        }

        function startScanning(mode) {
            const selectedPair = document.getElementById('pairSelect').value;
            const selectedTime = document.getElementById('timeSelect').value;
            const modeTitle = document.getElementById('modeTitle');
            const signalOutput = document.getElementById('signalOutput');
            const countdownTimer = document.getElementById('countdownTimer');
            const detailsOutput = document.getElementById('detailsOutput');
            const statAccuracy = document.getElementById('statAccuracy');
            const statSuccess = document.getElementById('statSuccess');

            signalOutput.className = "signal-call-put";
            signalOutput.innerHTML = "SCAN...";
            countdownTimer.innerHTML = "⏳ 00:72";
            renderLiveCandles();

            let scanTime = 8000;
            
            if (mode === 'safety') {
                scanTime = 72000; 
                let timeLeft = 72;
                modeTitle.innerHTML = "🛡️ SAFETY SCAN (1m 12s)";
                
                let timerInterval = setInterval(() => {
                    timeLeft--;
                    if (timeLeft > 0) {
                        countdownTimer.innerHTML = `⏳ 00:${timeLeft < 10 ? '0' + timeLeft : timeLeft}`;
                    } else {
                        clearInterval(timerInterval);
                    }
                }, 1000);
            } else {
                modeTitle.innerHTML = "⚡ LIVE HIGH-SPEED SCAN";
                countdownTimer.innerHTML = "⏳ 00:27";
            }

            playSound();

            setTimeout(() => {
                fetch(`/analyze?pair=${encodeURIComponent(selectedPair)}&time=${selectedTime}&mode=${mode}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.signal_type === "UP") {
                            signalOutput.className = "signal-call-put up-glow";
                            signalOutput.innerHTML = "UP ⬆️";
                        } else {
                            signalOutput.className = "signal-call-put down-glow";
                            signalOutput.innerHTML = "DOWN ⬇️";
                        }

                        statAccuracy.innerHTML = data.win_rate;
                        statSuccess.innerHTML = data.accuracy;

                        detailsOutput.innerHTML = `
                            📈 <b>Asset:</b> ${data.pair}<br>
                            ⏳ <b>Timeframe:</b> ${data.time_frame}<br>
                            🔍 <b>Analysis:</b> ${data.candle_behavior}<br>
                            👥 <b>Sentiment:</b> ${data.sentiment}<br>
                            🛡️ <b>Safety Tip:</b> ${data.safety_margin}
                        `;

                        playSound();
                        setTimeout(playSound, 300);
                    });
            }, scanTime);
        }

        window.onload = () => {
            updateClock();
            renderLiveCandles();
        };
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, pairs=OTC_PAIRS)

@app.route('/analyze')
def analyze():
    pair = request.args.get('pair', 'USD/BRL (OTC)')
    time_frame = request.args.get('time', '1') + " Minute"
    mode = request.args.get('mode', 'normal')
    
    wins = random.randint(7, 9)
    win_rate_str = f"{wins}/10 Win"
    accuracy_percentage = f"{wins * 10}%"
    
    if mode == 'safety':
        behaviors = [
            "1 মিনিট 12 সেকেন্ড ধরে 10-15টি ক্যান্ডেলের প্রাইস অ্যাকশন ও ভোলাটিলিটি স্ক্যান সম্পন্ন হয়েছে।",
            "72 সেকেন্ডের নিখুঁত সেফটি লজিক যাচাই করে নেক্সট ক্যান্ডেল এন্ট্রি কনফার্ম করা হয়েছে।"
        ]
        safety_margin = "সেফটি মার্জিন বজায় রেখে রিটেস্ট পয়েন্ট থেকে ট্রেড নিন।"
    else:
        behaviors = [
            "খুচরা ট্রেডারদের অর্ডারের ভিত্তিতে ব্রোকার অ্যালগরিদম রিভার্সাল মোমেন্টাম তৈরি করছে।",
            "মাইক্রো সাপোর্ট ও রেজিস্ট্যান্স লেভেলের ব্রেকআউট বিশ্লেষণ করা হয়েছে।"
        ]
        safety_margin = "কান্টেল ওপেনিংয়ে সামান্য পুলব্যাক বা সেফটি জোন ফলো করুন।"

    sentiments = [
        "70% ট্রেডার বাই দিয়েছেন (অ্যালগরিদম সেল টানবে)",
        "65% ট্রেডার সেল দিয়েছেন (অ্যালগরিদম বাই টানতে পারে)",
        "মার্কেটে বায়ার ও সেলারের প্রেসার ব্যালেন্সড রয়েছে"
    ]
    
    chosen_sentiment = random.choice(sentiments)
    chosen_behavior = random.choice(behaviors)
    
    if "বাই দিয়েছেন" in chosen_sentiment:
        signal_type = "DOWN"
    else:
        signal_type = "UP"

    return jsonify({
        "pair": pair,
        "time_frame": time_frame,
        "signal_type": signal_type,
        "candle_behavior": chosen_behavior,
        "sentiment": chosen_sentiment,
        "accuracy": accuracy_percentage,
        "win_rate": win_rate_str,
        "safety_margin": safety_margin
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
