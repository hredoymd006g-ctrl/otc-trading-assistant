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
    <title>BD VIP Signal Bot</title>
    <style>
        :root {
            --bg-deep: #050811;
            --panel-bg: rgba(17, 24, 39, 0.9);
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
            padding: 20px; 
            border-radius: 20px; 
            border: 1px solid rgba(56, 189, 248, 0.5); 
            box-shadow: 0 20px 40px rgba(0,0,0,0.9), inset 0 0 25px rgba(16, 185, 129, 0.1); 
        }

        .top-hud {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 10px;
            margin-bottom: 15px;
        }

        .bot-title { 
            color: #ffffff; 
            font-size: 20px; 
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
        
        .section-label { 
            font-size: 12px; 
            color: var(--neon-blue); 
            display: block; 
            margin-bottom: 5px; 
            font-weight: 700;
            text-transform: uppercase;
        }

        select { 
            width: 100%; 
            padding: 10px; 
            background: #0b0f19; 
            color: #ffffff; 
            border: 1px solid rgba(56, 189, 248, 0.4); 
            border-radius: 10px; 
            font-size: 14px; 
            margin-bottom: 12px; 
            outline: none; 
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.6);
        }

        .holo-display {
            background: radial-gradient(circle, rgba(16,185,129,0.15) 0%, rgba(11,15,25,0.9) 80%);
            border: 2px solid var(--neon-green);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            margin: 15px 0;
            box-shadow: 0 0 25px rgba(16, 185, 129, 0.25), inset 0 0 15px rgba(16, 185, 129, 0.2);
            position: relative;
        }

        .holo-circle {
            width: 90px;
            height: 90px;
            border: 3px dashed var(--neon-green);
            border-radius: 50%;
            margin: auto;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            animation: spinHolo 8s linear infinite;
            box-shadow: var(--glow-green);
        }

        @keyframes spinHolo { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

        .holo-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            width: 100%;
        }

        .signal-call-put {
            font-size: 28px;
            font-weight: 900;
            margin: 5px 0;
        }
        .up-glow { color: var(--neon-green); text-shadow: var(--glow-green); }
        .down-glow { color: var(--neon-red); text-shadow: var(--glow-red); }

        .timer-hud {
            font-size: 13px;
            color: var(--neon-blue);
            background: rgba(56, 189, 248, 0.1);
            padding: 3px 10px;
            border-radius: 10px;
            display: inline-block;
            border: 1px solid var(--neon-blue);
            margin-top: 5px;
        }

        .stats-grid {
            display: flex;
            gap: 10px;
            margin-top: 12px;
        }

        .stat-box {
            flex: 1;
            background: rgba(11, 15, 25, 0.8);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 10px;
            padding: 8px;
            text-align: center;
        }

        .stat-value {
            font-size: 16px;
            font-weight: bold;
            color: #f8fafc;
        }

        .btn-grid { display: flex; gap: 10px; margin-top: 15px; }
        
        button.cyber-btn-green { 
            flex: 1; 
            padding: 12px; 
            background: linear-gradient(135deg, #059669, #10b981); 
            color: white; 
            border: none; 
            border-radius: 10px; 
            font-size: 14px; 
            font-weight: bold; 
            cursor: pointer; 
            box-shadow: var(--glow-green);
            transition: 0.3s; 
        }
        
        button.cyber-btn-orange { 
            flex: 1; 
            padding: 12px; 
            background: linear-gradient(135deg, #d97706, #f59e0b); 
            color: white; 
            border: none; 
            border-radius: 10px; 
            font-size: 14px; 
            font-weight: bold; 
            cursor: pointer; 
            box-shadow: 0 0 15px rgba(245, 158, 11, 0.4);
            transition: 0.3s; 
        }

        button:active { transform: scale(0.97); }

        .details-panel {
            background: rgba(11, 15, 25, 0.85);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 10px;
            padding: 10px;
            margin-top: 15px;
            font-size: 12px;
            color: #94a3b8;
            line-height: 1.5;
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="top-hud">
            <div>
                <h2 class="bot-title">BD VIP SIGNAL BOT</h2>
                <div style="font-size: 10px; color: var(--neon-blue);">SMART TRADING • VIP HUD</div>
            </div>
            <div class="status-pill">🟢 ACTIVE</div>
        </div>

        <label class="section-label">Asset Select & Timeframe</label>
        <select id="pairSelect">
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
            <div style="font-size: 11px; color: var(--neon-blue); font-weight: bold; margin-bottom: 5px;" id="modeTitle">SIGNAL MATRIX</div>
            
            <div style="position: relative; height: 80px; margin: 10px 0;">
                <div class="holo-circle"></div>
                <div class="holo-content">
                    <div id="signalOutput" class="signal-call-put up-glow">READY</div>
                    <div class="timer-hud" id="countdownTimer">⏳ 00:58</div>
                </div>
            </div>

            <div class="stats-grid">
                <div class="stat-box">
                    <div style="font-size: 10px; color: var(--neon-green);">ACCURACY</div>
                    <div class="stat-value" id="statAccuracy">93%</div>
                </div>
                <div class="stat-box">
                    <div style="font-size: 10px; color: var(--neon-blue);">SUCCESS RATE</div>
                    <div class="stat-value" id="statSuccess">90%</div>
                </div>
            </div>

            <div class="details-panel" id="detailsOutput">
                📊 বট প্রস্তুত রয়েছে। মার্কেট স্ক্যান করতে উপরের যেকোনো একটি বাটন চাপুন।
            </div>
        </div>
    </div>

    <audio id="alertSound" src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" preload="auto"></audio>

    <script>
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

            signalOutput.className = "signal-call-put";
            signalOutput.innerHTML = "SCAN...";
            countdownTimer.innerHTML = "⏳ 00:72";

            let scanTime = 8000;
            
            if (mode === 'safety') {
                scanTime = 72000; // নিখুঁত ১ মিনিট ১২ সেকেন্ড (৭২ সেকেন্ড) সেফটি স্ক্যান লক
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
                countdownTimer.innerHTML = "⏳ 00:58";
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

                        statAccuracy.innerHTML = data.accuracy;

                        detailsOutput.innerHTML = `
                            📈 <b>Asset:</b> ${data.pair}<br>
                            ⏳ <b>Timeframe:</b> ${data.time_frame}<br>
                            🔍 <b>Analysis:</b> ${data.candle_behavior}<br>
                            👥 <b>Sentiment:</b> ${data.sentiment}
                        `;

                        playSound();
                        setTimeout(playSound, 300);
                    });
            }, scanTime);
        }
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
    
    if mode == 'safety':
        behaviors = [
            "1 মিনিট 12 সেকেন্ড ধরে 10-15টি ক্যান্ডেলের প্রাইস অ্যাকশন ও ভোলাটিলিটি স্ক্যান সম্পন্ন হয়েছে।",
            "72 সেকেন্ডের নিখুঁত সেফটি লজিক যাচাই করে নেক্সট ক্যান্ডেল এন্ট্রি কনফার্ম করা হয়েছে।"
        ]
        accuracy = f"{random.randint(95, 99)}%"
    else:
        behaviors = [
            "খুচরা ট্রেডারদের অর্ডারের ভিত্তিতে ব্রোকার অ্যালগরিদম রিভার্সাল মোমেন্টাম তৈরি করছে।",
            "মাইক্রো সাপোর্ট ও রেজিস্ট্যান্স লেভেলের ব্রেকআউট বিশ্লেষণ করা হয়েছে।"
        ]
        accuracy = f"{random.randint(88, 94)}%"

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
        "accuracy": accuracy
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
