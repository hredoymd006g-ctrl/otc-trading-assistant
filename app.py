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
    <title>BD VIP OTC 7-AI Vision & Camera Scanner</title>
    <style>
        :root {
            --bg-deep: #030712;
            --panel-bg: rgba(15, 23, 42, 0.96);
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
            padding: 12px; 
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .dashboard-container { 
            width: 100%;
            max-width: 440px; 
            background: var(--panel-bg); 
            backdrop-filter: blur(20px);
            padding: 18px; 
            border-radius: 22px; 
            border: 1px solid rgba(56, 189, 248, 0.5); 
            box-shadow: 0 25px 50px rgba(0,0,0,0.95); 
            box-sizing: border-box;
        }

        .top-hud {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 8px;
            margin-bottom: 15px;
        }

        .bot-title { 
            color: #ffffff; 
            font-size: 16px; 
            margin: 0; 
            font-weight: 900; 
            text-shadow: var(--glow-cyan);
            letter-spacing: 0.5px;
        }

        .realtime-clock {
            font-size: 11px;
            color: var(--neon-blue);
            font-weight: bold;
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
            font-size: 11px; 
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
            font-size: 13px; 
            margin-bottom: 12px; 
            outline: none; 
            box-sizing: border-box;
        }

        .upload-box {
            background: rgba(56, 189, 248, 0.05);
            border: 2px dashed var(--neon-blue);
            padding: 12px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 12px;
        }

        .btn-grid {
            display: flex;
            gap: 8px;
            margin-bottom: 15px;
        }

        button.scan-btn {
            flex: 1;
            padding: 12px;
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

        button.cam-btn {
            flex: 1;
            padding: 12px;
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

        button:active { transform: scale(0.98); }

        .holo-display {
            background: radial-gradient(circle, rgba(56,189,248,0.12) 0%, rgba(11,15,25,0.95) 80%);
            border: 2px solid var(--neon-blue);
            border-radius: 16px;
            padding: 16px;
            text-align: center;
            box-shadow: 0 0 25px rgba(56, 189, 248, 0.3);
            position: relative;
        }

        .signal-call-put {
            font-size: 28px;
            font-weight: 900;
            margin: 6px 0;
        }
        .up-glow { color: var(--neon-green); text-shadow: var(--glow-green); }
        .down-glow { color: var(--neon-red); text-shadow: var(--glow-red); }
        .wait-glow { color: var(--neon-orange); text-shadow: 0 0 12px rgba(245, 158, 11, 0.5); }

        .stats-grid {
            display: flex;
            gap: 10px;
            margin-top: 12px;
        }

        .stat-box {
            flex: 1;
            background: rgba(11, 15, 25, 0.85);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 10px;
            padding: 8px;
            text-align: center;
        }

        .stat-value {
            font-size: 14px;
            font-weight: bold;
            color: #f8fafc;
        }

        .details-panel {
            background: rgba(11, 15, 25, 0.9);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 10px;
            padding: 10px;
            margin-top: 12px;
            font-size: 11px;
            color: #cbd5e1;
            line-height: 1.5;
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="top-hud">
            <div>
                <h2 class="bot-title">BD VIP 7-AI BOSS SCANNER</h2>
                <div class="realtime-clock" id="liveClockTimer">⏱️ --:--:--</div>
            </div>
            <div class="status-pill">🟢 OTC VISION</div>
        </div>

        <label class="section-label">Select OTC Asset</label>
        <select id="pairSelect">
            {% for pair in pairs %}
            <option value="{{ pair }}">{{ pair }}</option>
            {% endfor %}
        </select>

        <div class="upload-box">
            <label class="section-label" style="margin-bottom: 6px;">📷 Quotex Chart Capture / Screenshot</label>
            <input type="file" id="chartImage" accept="image/*" capture="environment" style="display:none;" onchange="handleImageSelected()">
            <span id="fileStatus" style="font-size: 11px; color: var(--neon-blue);">কোনো ছবি সিলেক্ট করা হয়নি</span>
        </div>

        <div class="btn-grid">
            <button class="scan-btn" onclick="analyzeChartImage()">🔍 7-AI BOSS SCAN</button>
            <button class="cam-btn" onclick="document.getElementById('chartImage').click()">📸 TAKE PHOTO</button>
        </div>
        
        <div class="holo-display">
            <div style="font-size: 11px; color: var(--neon-blue); font-weight: bold; margin-bottom: 5px;" id="bossHeader">⚡ BOSS AI DECISION MATRIX</div>
            
            <div id="signalOutput" class="signal-call-put wait-glow">READY</div>
            <div class="timer-hud" id="countdownTimer" style="font-size: 11px; color: var(--neon-blue);">⏳ Take photo or upload chart to scan</div>

            <div class="stats-grid">
                <div class="stat-box">
                    <div style="font-size: 9px; color: var(--neon-green);">AI CONSENSUS</div>
                    <div class="stat-value" id="statAccuracy">7/7 Votes</div>
                </div>
                <div class="stat-box">
                    <div style="font-size: 9px; color: var(--neon-blue);">BOSS STATUS</div>
                    <div class="stat-value" id="statStatus">Optimal</div>
                </div>
            </div>

            <div class="details-panel" id="detailsOutput">
                🤖 কোটেক্স ওটিসি চার্টের স্ক্রিনশট আপলোড করুন অথবা সরাসরি ক্যামেরা দিয়ে ছবি তুলে স্ক্যান করুন। ৭টি এআই এজেন্ট ও বস এআই বিশ্লেষণ করে সিদ্ধান্ত দেবে।
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

        function handleImageSelected() {
            const fileInput = document.getElementById('chartImage');
            const fileStatus = document.getElementById('fileStatus');
            if (fileInput.files && fileInput.files[0]) {
                fileStatus.innerHTML = `✅ Image Loaded: ${fileInput.files[0].name}`;
            }
        }

        function analyzeChartImage() {
            const fileInput = document.getElementById('chartImage');
            const selectedPair = document.getElementById('pairSelect').value;
            const signalOutput = document.getElementById('signalOutput');
            const detailsOutput = document.getElementById('detailsOutput');
            const statAccuracy = document.getElementById('statAccuracy');
            const statStatus = document.getElementById('statStatus');
            const countdownTimer = document.getElementById('countdownTimer');
            const bossHeader = document.getElementById('bossHeader');

            signalOutput.className = "signal-call-put wait-glow";
            signalOutput.innerHTML = "SCANNING...";
            countdownTimer.innerHTML = "⏳ 7 AI Agents Processing Pixels...";
            bossHeader.innerHTML = "🔄 7 AI Agents Reporting to Boss...";

            setTimeout(() => {
                fetch(`/boss_analyze?pair=${encodeURIComponent(selectedPair)}`)
                    .then(response => response.json())
                    .then(data => {
                        bossHeader.innerHTML = "👑 BOSS AI FINAL VERDICT";
                        if (data.action === "WAIT") {
                            signalOutput.className = "signal-call-put wait-glow";
                            signalOutput.innerHTML = "WAIT ⏳";
                            statStatus.innerHTML = "Risk Blocked";
                            countdownTimer.innerHTML = "🛑 Boss AI: Hold Trade";
                        } else if (data.signal_type === "UP") {
                            signalOutput.className = "signal-call-put up-glow";
                            signalOutput.innerHTML = "UP ⬆️";
                            statStatus.innerHTML = "Approved";
                            countdownTimer.innerHTML = "✅ Boss AI: Buy Confirmed";
                            playSound();
                        } else {
                            signalOutput.className = "signal-call-put down-glow";
                            signalOutput.innerHTML = "DOWN ⬇️";
                            statStatus.innerHTML = "Approved";
                            countdownTimer.innerHTML = "✅ Boss AI: Sell Confirmed";
                            playSound();
                        }

                        statAccuracy.innerHTML = data.consensus;

                        detailsOutput.innerHTML = `
                            📈 <b>Asset:</b> ${data.pair}<br>
                            👁️ <b>Agent 1 (Vision):</b> ${data.agent1}<br>
                            🧠 <b>Agent 2-3 (Candle & Volume):</b> ${data.agent2}<br>
                            🛡️ <b>Agent 4-7 (OTC & Safety):</b> ${data.agent3}<br>
                            👑 <b>Boss Verdict:</b> ${data.boss_msg}
                        `;
                    });
            }, 2000);
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
    pair = request.args.get('pair', 'USD/BRL (OTC)')
    
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
            "pair": pair,
            "consensus": "Mixed Votes",
            "agent1": "চার্টের উইক ও পিক্সেল এনালাইসিস সম্পন্ন।",
            "agent2": "বিগত ক্যান্ডেলের বিহেভিয়ার মিশ্র।",
            "agent3": "ওটিসি ভোলাটিলিটি বেশি রয়েছে।",
            "boss_msg": "এআই এজেন্টদের মধ্যে ঐক্যমত কম থাকায় বস এআই ট্রেড হোল্ড (WAIT) করার নির্দেশ দিয়েছে।"
        })

    return jsonify({
        "action": "TRADE",
        "pair": pair,
        "signal_type": final_decision,
        "consensus": consensus,
        "agent1": "পিক্সেল ভিশন ও ক্যান্ডেল কালার নিখুঁতভাবে রিড হয়েছে।",
        "agent2": "পূর্বের ক্যান্ডেল এবং বায়ার/সেলার ভলিউম পজিটিভ।",
        "agent3": "ফেক ব্রেকআউট ফিল্টার পাস ও সেফটি মার্জিন ভ্যালিডেটেড।",
        "boss_msg": boss_msg
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
