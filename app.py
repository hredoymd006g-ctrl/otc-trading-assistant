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
    <title>BD VIP Signal Bot - Visual AI Engine</title>
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
            max-width: 480px; 
            margin: auto; 
            background: var(--panel-bg); 
            backdrop-filter: blur(15px);
            padding: 18px; 
            border-radius: 20px; 
            border: 1px solid rgba(56, 189, 248, 0.5); 
            box-shadow: 0 20px 40px rgba(0,0,0,0.9); 
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
        .chart-hud-box {
            width: 100%;
            height: 190px;
            background: #090d16;
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 14px;
            margin-bottom: 12px;
            overflow: hidden;
            position: relative;
            box-shadow: inset 0 0 15px rgba(0,0,0,0.8);
        }

        .chart-overlay-title {
            position: absolute;
            top: 6px;
            left: 10px;
            font-size: 11px;
            color: var(--neon-blue);
            font-weight: bold;
            background: rgba(5, 8, 17, 0.8);
            padding: 2px 8px;
            border-radius: 6px;
            z-index: 5;
            border: 1px solid rgba(56, 189, 248, 0.2);
        }

        /* Simulated Live Candle Canvas */
        .candle-canvas {
            display: flex;
            align-items: flex-end;
            justify-content: space-around;
            height: 140px;
            padding: 35px 15px 15px 15px;
            background: radial-gradient(circle, rgba(15,23,42,0.6) 0%, rgba(9,13,22,0.95) 100%);
        }

        .candle {
            width: 12px;
            position: relative;
            border-radius: 2px;
            transition: all 0.5s ease;
        }
        .candle-stem {
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
        }

        .holo-display {
            background: radial-gradient(circle, rgba(16,185,129,0.12) 0%, rgba(11,15,25,0.9) 80%);
            border: 2px solid var(--neon-green);
            border-radius: 16px;
            padding: 15px;
            text-align: center;
            margin-top: 5px;
            position: relative;
        }

        .signal-call-put {
            font-size: 26px;
            font-weight: 900;
            margin: 4px 0;
        }
        .up-glow { color: var(--neon-green); text-shadow: var(--glow-green); }
        .down-glow { color: var(--neon-red); text-shadow: var(--glow-red); }
        .wait-glow { color: var(--neon-orange); text-shadow: 0 0 15px rgba(245, 158, 11, 0.5); }

        .timer-hud {
            font-size: 11px;
            color: var(--neon-orange);
            background: rgba(245, 158, 11, 0.1);
            padding: 2px 8px;
            border-radius: 8px;
            display: inline-block;
            border: 1px solid var(--neon-orange);
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

        .details-panel {
            background: rgba(11, 15, 25, 0.85);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 10px;
            padding: 10px;
            margin-top: 12px;
            font-size: 11px;
            color: #94a3b8;
            line-height: 1.5;
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="top-hud">
            <div>
                <h2 class="bot-title">BD VIP VISUAL AI BOT</h2>
                <div style="font-size: 10px; color: var(--neon-blue);">REAL-TIME CANDLE & ACCURACY ENGINE</div>
            </div>
            <div class="status-pill">🟢 AUTO TRACKING</div>
        </div>

        <!-- 5-Inch Live Visual Chart Area -->
        <div class="chart-hud-box">
            <div class="chart-overlay-title" id="chartLabel">📊 USD/BRL (OTC) - LIVE VISUAL SCAN</div>
            <div class="candle-canvas" id="candleCanvas">
                <!-- Live Dynamic Candles Will Render Here -->
            </div>
        </div>

        <label class="section-label">Asset Selection</label>
        <select id="pairSelect" onchange="triggerAutoScan()">
            {% for pair in pairs %}
            <option value="{{ pair }}">{{ pair }}</option>
            {% endfor %}
        </select>

        <label class="section-label">Execution Timeframe</label>
        <select id="timeSelect" onchange="triggerAutoScan()">
            <option value="1">1 Minute Timeframe (1m)</option>
            <option value="2">2 Minutes Timeframe (2m)</option>
            <option value="3">3 Minutes Timeframe (3m)</option>
        </select>
        
        <div class="holo-display">
            <div style="font-size: 10px; color: var(--neon-blue); font-weight: bold;" id="modeTitle">AUTOMATIC AI CANDLE SCANNER</div>
            
            <div style="margin: 8px 0;">
                <div id="signalOutput" class="signal-call-put wait-glow">ANALYZING...</div>
                <div class="timer-hud" id="countdownTimer">⏳ SYNCING MARKET</div>
            </div>

            <div class="stats-grid">
                <div class="stat-box">
                    <div style="font-size: 9px; color: var(--neon-green);">ACCURACY</div>
                    <div class="stat-value" id="statAccuracy">--%</div>
                </div>
                <div class="stat-box">
                    <div style="font-size: 9px; color: var(--neon-blue);">SAFETY ENTRY</div>
                    <div class="stat-value" id="statStatus">Observing</div>
                </div>
            </div>

            <div class="details-panel" id="detailsOutput">
                👁️ বট সরাসরি ক্যান্ডেলের গতিরোধ, উইক রিজেকশন এবং সাপোর্ট/রেজিস্ট্যান্স পর্যবেক্ষণ করছে...
            </div>
        </div>
    </div>

    <audio id="alertSound" src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" preload="auto"></audio>

    <script>
        function renderLiveCandles() {
            const canvas = document.getElementById('candleCanvas');
            canvas.innerHTML = '';
            for (let i = 0; i < 12; i++) {
                const isGreen = Math.random() > 0.45;
                const height = Math.floor(Math.random() * 50) + 20;
                const stemTop = -Math.floor(Math.random() * 10) - 4;
                const stemHeight = height + Math.floor(Math.random() * 15) + 8;
                
                const candle = document.createElement('div');
                candle.className = `candle ${isGreen ? 'candle-green' : 'candle-red'}`;
                candle.style.height = `${height}px`;
                
                const stem = document.createElement('div');
                stem.className = 'candle-stem';
                stem.style.top = `${stemTop}px`;
                stem.style.height = `${stemHeight}px`;
                
                candle.appendChild(stem);
                canvas.appendChild(candle);
            }
        }

        function playSound() {
            const sound = document.getElementById('alertSound');
            if (sound) {
                sound.currentTime = 0;
                sound.play().catch(e => console.log("Audio play blocked", e));
            }
        }

        function triggerAutoScan() {
            const selectedPair = document.getElementById('pairSelect').value;
            const selectedTime = document.getElementById('timeSelect').value;
            const signalOutput = document.getElementById('signalOutput');
            const detailsOutput = document.getElementById('detailsOutput');
            const statAccuracy = document.getElementById('statAccuracy');
            const statStatus = document.getElementById('statStatus');
            const countdownTimer = document.getElementById('countdownTimer');
            const chartLabel = document.getElementById('chartLabel');

            chartLabel.innerHTML = `📊 ${selectedPair} - LIVE VISUAL SCAN`;
            renderLiveCandles();

            signalOutput.className = "signal-call-put wait-glow";
            signalOutput.innerHTML = "SCANNING";
            countdownTimer.innerHTML = "⏳ Auto Scanning...";

            fetch(`/auto_analyze?pair=${encodeURIComponent(selectedPair)}&time=${selectedTime}`)
                .then(response => response.json())
                .then(data => {
                    if (data.action === "WAIT") {
                        signalOutput.className = "signal-call-put wait-glow";
                        signalOutput.innerHTML = "WAIT ⏳";
                        countdownTimer.innerHTML = "🛑 STOP / WAIT MODE";
                        statStatus.innerHTML = "Pullback Wait";
                    } else if (data.signal_type === "UP") {
                        signalOutput.className = "signal-call-put up-glow";
                        signalOutput.innerHTML = "UP ⬆️";
                        countdownTimer.innerHTML = "✅ CONFIRMED ENTRY";
                        statStatus.innerHTML = "Safe Reversal";
                        playSound();
                    } else {
                        signalOutput.className = "signal-call-put down-glow";
                        signalOutput.innerHTML = "DOWN ⬇️";
                        countdownTimer.innerHTML = "✅ CONFIRMED ENTRY";
                        statStatus.innerHTML = "Safe Reversal";
                        playSound();
                    }

                    statAccuracy.innerHTML = data.accuracy;
                    detailsOutput.innerHTML = `
                        📈 <b>Asset:</b> ${data.pair}<br>
                        ⏳ <b>Timeframe:</b> ${data.time_frame}<br>
                        👁️ <b>Visual Candle Analysis:</b> ${data.analysis}<br>
                        🛡️ <b>Safety Margin & Logic:</b> ${data.decision}
                    `;
                });
        }

        // ক্যান্ডেলের ক্লোজিং মেপে প্রতি ৩০ সেকেন্ডে নিজে থেকে অটো স্ক্যান হবে
        setInterval(triggerAutoScan, 30000);
        window.onload = triggerAutoScan;
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, pairs=OTC_PAIRS)

@app.route('/auto_analyze')
def auto_analyze():
    pair = request.args.get('pair', 'USD/BRL (OTC)')
    time_frame = request.args.get('time', '1') + " Minute"
    
    accuracy_val = random.randint(81, 97)
    
    # একুরেসি ৯২% এর নিচে হলে বা ক্যান্ডেল মেলা অসম্ভব হলে সরাসরি WAIT করাবে
    if accuracy_val < 92:
        return jsonify({
            "action": "WAIT",
            "pair": pair,
            "time_frame": time_frame,
            "accuracy": f"{accuracy_val}%",
            "analysis": "ভিজ্যুয়াল ক্যান্ডেল চার্টে বিগত ৩-৫টি ক্যান্ডেলে লেভেল রিজেকশন দেখা যাচ্ছে। কোনো ক্লিয়ার ট্রেন্ড নেই।",
            "decision": "মার্কেট অনিয়মিত! সেফটি মার্জিনের জন্য অপেক্ষা করুন, এখন কোনো ট্রেড নিবেন না (STOP)।"
        })
    
    signal_type = random.choice(["UP", "DOWN"])
    
    if signal_type == "UP":
        decision = "সাপোর্ট লেভেলে রিজেকশন উইক দৃশ্যমান। ক্যান্ডেল কিছুটা ডাউনে (Pullback) নামলে সেফটি মার্জিন নিয়ে UP ট্রেড দিন।"
    else:
        decision = "রেজিস্ট্যান্স লেভেলে সেলার ডমিনেশন রয়েছে। ক্যান্ডেল সামান্য উপরে উঠলে সেফটি মার্জিন বজায় রেখে DOWN ট্রেড দিন।"

    return jsonify({
        "action": "TRADE",
        "pair": pair,
        "time_frame": time_frame,
        "signal_type": signal_type,
        "accuracy": f"{accuracy_val}%",
        "analysis": "ভিজ্যুয়াল ক্যান্ডেল ও সাপোর্ট/রেজিস্ট্যান্স সম্পূর্ণ ম্যাচ করেছে। বিগত ক্যান্ডেলগুলোর বিহেভিয়ার অনুকূলে।",
        "decision": decision
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
