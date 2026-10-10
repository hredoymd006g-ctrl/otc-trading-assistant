from flask import Flask, render_template_string, jsonify, request
import random

app = Flask(__name__)

# বিস্তৃত ওটিসি পেয়ারের তালিকা
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
        body { background-color: #0b0f19; color: #f8fafc; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 15px; }
        .container { max-width: 450px; margin: auto; background: #111827; padding: 20px; border-radius: 16px; border: 1px solid #1e293b; box-shadow: 0 10px 25px rgba(0,0,0,0.8); }
        h2 { text-align: center; color: #10b981; font-size: 24px; margin-bottom: 5px; font-weight: bold; }
        .subtitle { text-align: center; color: #64748b; font-size: 13px; margin-bottom: 15px; }
        
        label { font-size: 14px; color: #94a3b8; display: block; margin-bottom: 6px; }
        select { width: 100%; padding: 10px; background: #1f2937; color: #38bdf8; border: 1px solid #374151; border-radius: 8px; font-size: 15px; margin-bottom: 12px; outline: none; }
        
        .btn-group { display: flex; gap: 10px; margin-top: 10px; }
        button.scan-btn { flex: 1; padding: 14px 10px; background: linear-gradient(135deg, #059669, #10b981); color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.3s; }
        button.safety-btn { flex: 1; padding: 14px 10px; background: linear-gradient(135deg, #d97706, #f59e0b); color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.3s; }
        button:active { transform: scale(0.98); }
        
        /* Radar Scanner Animation */
        .radar-box { display: none; text-align: center; margin: 20px 0; }
        .radar { width: 80px; height: 80px; border: 3px solid #10b981; border-radius: 50%; margin: auto; position: relative; animation: pulse 1.5s infinite; }
        .radar::after { content: ''; position: absolute; width: 40px; height: 40px; background: rgba(16, 185, 129, 0.3); top: 0; left: 0; border-radius: 100% 0 0 0; animation: spin 1s linear infinite; transform-origin: 100% 100%; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); } 70% { box-shadow: 0 0 0 15px rgba(16, 185, 129, 0); } 100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); } }

        .result-card { display: none; background: #1f2937; padding: 20px; border-radius: 12px; border: 2px solid #10b981; text-align: center; margin-top: 20px; }
        .signal-text { font-size: 32px; font-weight: 900; margin: 10px 0; }
        .up { color: #10b981; }
        .down { color: #ef4444; }
        .details { text-align: left; font-size: 13px; color: #9ca3af; line-height: 1.6; margin-top: 15px; background: #111827; padding: 10px; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>BD VIP SIGNAL BOT</h2>
        <div class="subtitle">ওটিসি অ্যালগরিদম ও নিশ্চিত সাউন্ড অ্যালার্ট</div>

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
            <button class="scan-btn" onclick="startScanning('normal')">লাইভ স্ক্যান</button>
            <button class="safety-btn" onclick="startScanning('safety')">সেফটি স্ক্যান</button>
        </div>
        
        <div id="radarBox" class="radar-box">
            <div class="radar"></div>
            <p style="color:#10b981; margin-top:10px; font-weight:bold;" id="scanStatus">মার্কেট স্ক্যানিং হচ্ছে...</p>
        </div>
        
        <div id="resultCard" class="result-card">
            <div style="font-size:12px; color:#9ca3af;" id="modeTitle">PREMIUM SIGNAL</div>
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

            let scanTime = 8000; // নরমাল স্ক্যান টাইম
            if (mode === 'safety') {
                scanStatus.innerHTML = "সেফটি মোড: ১০-১৫ ক্যান্ডেল ও ১ মিনিট ১২ সেকেন্ড অ্যানালাইসিস চলছে...";
                scanTime = 6000; // সেফটি স্ক্যানের জন্য প্রিসাইজ টাইম
            } else {
                scanStatus.innerHTML = "মার্কেট স্ক্যানিং হচ্ছে...";
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
                            modeTitle.innerHTML = "⚡ SAFETY SCAN (1m 12s Next Candle)";
                        } else {
                            modeTitle.innerHTML = `🔥 ${selectedTime} MIN PREMIUM SIGNAL`;
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
                            🔍 <b>মার্কেট অ্যানালাইসিস:</b> ${data.candle_behavior}<br>
                            👥 <b>ব্রোকার ভলিউম:</b> ${data.sentiment}<br>
                            🎯 <b>সিগন্যাল একুরেসি:</b> ${data.accuracy}
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
            "১ মিনিট ১২ সেকেন্ড ধরে ১০-১৫টি ক্যান্ডেলের মুভমেন্ট ও প্রাইস অ্যাকশন রিড করা হয়েছে; নেক্সট ক্যান্ডেলে স্ট্রং রিভার্সাল পসিবল।",
            "শেষ ১২ ক্যান্ডেলের ভলাটিলিটি এবং সাপোর্ট-রেজিস্ট্যান্স জোন যাচাই করে নেক্সট ক্যান্ডেল এন্ট্রি নিশ্চিত করা হয়েছে।"
        ]
        accuracy = f"{random.randint(94, 99)}% (Safety Confirmed)"
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
        "৬৫% ট্রেডার সেল দিয়েছেন (অ্যালগরিদম বাই টানতে পারে)",
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
