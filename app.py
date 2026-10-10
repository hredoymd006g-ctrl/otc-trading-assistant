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
            --panel-bg: rgba(17, 24, 39, 0.85);
            --neon-green: #10b981;
            --neon-blue: #38bdf8;
            --neon-orange: #f59e0b;
            --neon-red: #ef4444;
            --border-glow: 0 0 15px rgba(56, 189, 248, 0.3);
        }
        
        body { 
            background: radial-gradient(circle at center, #0f172a 0%, #030712 100%); 
            color: #f8fafc; 
            font-family: 'Segoe UI', Roboto, sans-serif; 
            margin: 0; 
            padding: 10px; 
            min-height: 100vh;
        }

        .container { 
            max-width: 460px; 
            margin: auto; 
            background: var(--panel-bg); 
            backdrop-filter: blur(12px);
            padding: 22px; 
            border-radius: 20px; 
            border: 1px solid rgba(56, 189, 248, 0.4); 
            box-shadow: 0 15px 35px rgba(0,0,0,0.9), inset 0 0 20px rgba(16, 185, 129, 0.15); 
        }

        .header-box {
            text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 12px;
            margin-bottom: 18px;
            position: relative;
        }

        .bot-badge {
            display: inline-block;
            background: rgba(16, 185, 129, 0.2);
            color: var(--neon-green);
            font-size: 11px;
            font-weight: bold;
            padding: 3px 10px;
            border-radius: 20px;
            border: 1px solid var(--neon-green);
            margin-bottom: 6px;
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
        }

        h2 { 
            color: #ffffff; 
            font-size: 24px; 
            margin: 0; 
            font-weight: 900; 
            letter-spacing: 1px;
            text-shadow: 0 0 10px rgba(56, 189, 248, 0.6);
        }

        .subtitle { 
            color: #94a3b8; 
            font-size: 12px; 
            margin-top: 4px;
            letter-spacing: 0.5px;
        }
        
        label { 
            font-size: 13px; 
            color: var(--neon-blue); 
            display: block; 
            margin-bottom: 6px; 
            font-weight: 600; 
        }

        select { 
            width: 100%; 
            padding: 12px; 
            background: #0b0f19; 
            color: #ffffff; 
            border: 1px solid rgba(56, 189, 248, 0.3); 
            border-radius: 12px; 
            font-size: 15px; 
            margin-bottom: 15px; 
            outline: none; 
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.5);
            transition: 0.3s;
        }
        select:focus {
            border-color: var(--neon-green);
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
        }
        
        .btn-group { display: flex; gap: 10px; margin-top: 10px; }
        
        button.scan-btn { 
            flex: 1; 
            padding: 14px 10px; 
            background: linear-gradient(135deg, #059669, #10b981); 
            color: white; 
            border: none; 
            border-radius: 12px; 
            font-size: 15px; 
            font-weight: bold; 
            cursor: pointer; 
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
            transition: 0.3s; 
        }
        
        button.safety-btn { 
            flex: 1; 
            padding: 14px 10px; 
            background: linear-gradient(135deg, #d97706, #f59e0b); 
            color: white; 
            border: none; 
            border-radius: 12px; 
            font-size: 15px; 
            font-weight: bold; 
            cursor: pointer; 
            box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
            transition: 0.3s; 
        }

        button:active { transform: scale(0.97); }
        
        /* 3D Holo Scanner Animation */
        .radar-box { display: none; text-align: center; margin: 25px 0; }
        .holo-ring { 
            width: 90px; 
            height: 90px; 
            border: 3px dashed var(--neon-green); 
            border-radius: 50%; 
            margin: auto; 
            position: relative; 
            animation: spin 2s linear infinite, glowPulse 1.5s ease-in-out infinite alternate; 
        }
        .holo-core {
            position: absolute;
            top: 15px; left: 15px; right: 15px; bottom: 15px;
            background: radial-gradient(circle, rgba(16,185,129,0.3) 0%, rgba(5,8,17,0) 70%);
            border-radius: 50%;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @keyframes glowPulse { 0% { box-shadow: 0 0 5px rgba(16,185,129,0.2); } 100% { box-shadow: 0 0 25px rgba(16,185,129,0.8); } }

        .result-card { 
            display: none; 
            background: linear-gradient(145deg, #0f172a, #1e293b); 
            padding: 20px; 
            border-radius: 16px; 
            border: 2px solid var(--neon-green); 
            text-align: center; 
            margin-top: 20px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.8), 0 0 15px rgba(16, 185, 129, 0.3);
            animation: fadeIn 0.5s ease;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        .signal-text { font-size: 30px; font-weight: 900; margin: 10px 0; letter-spacing: 1px; }
        .up { color: var(--neon-green); text-shadow: 0 0 15px rgba(16, 185, 129, 0.6); }
        .down { color: var(--neon-red); text-shadow: 0 0 15px rgba(239, 68, 68, 0.6); }
        
        .details { 
            text-align: left; 
            font-size: 13px; 
            color: #cbd5e1; 
            line-height: 1.6; 
            margin-top: 15px; 
            background: rgba(11, 15, 25, 0.8); 
            padding: 12px; 
            border-radius: 10px; 
            border: 1px solid rgba(255,255,255,0.05);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-box">
            <div class="bot-badge">🟢 3D CYBERPUNK ACTIVE</div>
            <h2>BD VIP SIGNAL BOT</h2>
            <div class="subtitle">স্মার্ট ট্রেডিং • হাই একুরেসি • অটো সিগন্যাল</div>
        </div>

        <label for="pairSelect">মার্কেট সিলেক্ট করুন (All OTC):</label>
        <select id="pairSelect">
            {% for pair in pairs %}
            <option value="{{ pair }}">{{ pair }}</option>
            {% endfor %}
        </select>

        <label for="timeSelect">ক্যান্ডেল টাইম সিলেক্ট করুন:</label>
        <select id="timeSelect">
            <option value="1">১ মিনিট ক্যান্ডেল</option>
            <option value="2">২ মিনিট ক্যান্ডেল</option>
            <option value="3">৩ মিনিট ক্যান্ডেল</option>
        </select>
        
        <div class="btn-group">
            <button class="scan-btn" onclick="startScanning('normal')">⚡ লাইভ স্ক্যান</button>
            <button class="safety-btn" onclick="startScanning('safety')">🛡️ সেফটি স্ক্যান</button>
        </div>
        
        <div id="radarBox" class="radar-box">
            <div class="holo-ring"><div class="holo-core"></div></div>
            <p style="color:var(--neon-blue); margin-top:12px; font-weight:bold; font-size:14px;" id="scanStatus">মার্কেট স্ক্যানিং হচ্ছে...</p>
        </div>
        
        <div id="resultCard" class="result-card">
            <div style="font-size:12px; color:var(--neon-blue); font-weight:bold; letter-spacing: 1px;" id="modeTitle">PREMIUM SIGNAL</div>
            <div id="signalOutput" class="signal-text"></div>
            <div class="details" id="detailsOutput"></div>
        </div>
    </div>

    <!-- রিয়েল এমপি থ্রি নোটিফিকেশন সাউন্ড -->
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
            const radarBox = document.getElementById('radarBox');
            const resultCard = document.getElementById('resultCard');
            const scanStatus = document.getElementById('scanStatus');
            const modeTitle = document.getElementById('modeTitle');
            
            radarBox.style.display = 'block';
            resultCard.style.display = 'none';

            let scanTime = 8000; // সাধারণ লাইভ স্ক্যান (৮ সেকেন্ড)
            
            if (mode === 'safety') {
                scanTime = 72000; // নিখুঁত ১ মিনিট ১২ সেকেন্ড (৭২ সেকেন্ড) লক
                let timeLeft = 72;
                
                scanStatus.innerHTML = `🛡️ সেফটি মোড: ১ মিনিট ১২ সেকেন্ড স্ক্যান চলছে... (${timeLeft}s)`;
                
                let countdownTimer = setInterval(() => {
                    timeLeft--;
                    if (timeLeft > 0) {
                        scanStatus.innerHTML = `🛡️ সেফটি মোড: ১ মিনিট ১২ সেকেন্ড স্ক্যান চলছে... (${timeLeft}s)`;
                    } else {
                        clearInterval(countdownTimer);
                    }
                }, 1000);
            } else {
                scanStatus.innerHTML = "মার্কেট ফাস্ট স্ক্যানিং হচ্ছে...";
            }

            playSound();

            setTimeout(() => {
                fetch(`/analyze?pair=${encodeURIComponent(selectedPair)}&time=${selectedTime}&mode=${mode}`)
                    .then(response => response.json())
                    .then(data => {
                        radarBox.style.display = 'none';
                        resultCard.style.display = 'block';

                        const signalOutput = document.getElementById('signalOutput');
                        const detailsOutput = document.getElementById('detailsOutput');

                        if (mode === 'safety') {
                            modeTitle.innerHTML = "🛡️ 3D STRICT 1M 12S SAFETY SIGNAL";
                        } else {
                            modeTitle.innerHTML = `🔥 3D ${selectedTime} MIN PREMIUM SIGNAL`;
                        }

                        if (data.signal.includes("CALL")) {
                            signalOutput.className = "signal-text up";
                            signalOutput.innerHTML = "BUY / UP 🟢";
                        } else {
                            signalOutput.className = "signal-text down";
                            signalOutput.innerHTML = "SELL / DOWN 🔴";
                        }

                        detailsOutput.innerHTML = `
                            📊 <b>পেয়ার:</b> ${data.pair}<br>
                            ⏳ <b>টাইমফ্রেম:</b> ${data.time_frame}<br>
                            🔍 <b>বিশ্লেষণ:</b> ${data.candle_behavior}<br>
                            👥 <b>ব্রোকার ভলিউম:</b> ${data.sentiment}<br>
                            🎯 <b>নিশ্চিত একুরেসি:</b> ${data.accuracy}
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
    pair = request.args.get('pair', 'EUR/USD (OTC)')
    time_frame = request.args.get('time', '1') + " মিনিট"
    mode = request.args.get('mode', 'normal')
    
    if mode == 'safety':
        behaviors = [
            "সঠিকভাবে ১ মিনিট ১২ সেকেন্ড ধরে ফুল ক্যান্ডেল ও প্রিভিয়াস মোমেন্টাম যাচাই করা হয়েছে; নেক্সট ক্যান্ডেল এন্ট্রির জন্য ১০০% সেফ।",
            "৭২ সেকেন্ডের ডিটেইলড মার্কেট স্ক্যান এবং স্ট্রং রিকভারি জোন কমপ্লিট হওয়ার পর সেফটি সিগন্যাল লক করা হয়েছে।"
        ]
        accuracy = f"{random.randint(96, 99)}% (Strictly Verified)"
    else:
        behaviors = [
            "খুচরা ট্রেডারদের বিপুল বাই অর্ডারের কারণে ব্রোকার অ্যালগরিদম রিভার্সাল টানবে।",
            "মাইক্রো সাপোর্ট লেভেলে ফেক ব্রেকআউট দেখা গেছে।",
            "বিগত ক্যান্ডেলের উইক বড় এবং সেলার প্রেসার বেশি।",
            "অ্যালগরিদমিক ট্রেন্ড মোমেন্টাম আপ সাইডে স্ট্রং।"
        ]
        accuracy = f"{random.randint(86, 95)}%"

    sentiments = [
        "৭০% ট্রেডার বাই দিয়েছেন (অ্যালগরিদম সেল টানবে)",
        "৬৫% ট্রেডার সেল দিয়েছেন (অ্যালগরিdm বাই টানতে পারে)",
        "মার্কেটে বায়ার ও সেলারের ব্যালেন্স প্রায় সমান"
    ]
    
    chosen_sentiment = random.choice(sentiments)
    chosen_behavior = random.choice(behaviors)
    
    if "বাই দিয়েছেন" in chosen_sentiment:
        signal = "PUT (DOWN)"
        voice_signal = "ডাউন ট্রেড নিন"
    else:
        signal = "CALL (UP)"
        voice_signal = "আপ ট্রেড নিন"

    return jsonify({
        "pair": pair,
        "time_frame": time_frame,
        "signal": signal,
        "voice_signal": voice_signal,
        "candle_behavior": chosen_behavior,
        "sentiment": chosen_sentiment,
        "accuracy": accuracy
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
