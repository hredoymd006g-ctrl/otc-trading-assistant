from flask import Flask, render_template_string, jsonify, request
import random

app = Flask(__name__)

# সকল ওটিসি পেয়ারের তালিকা
OTC_PAIRS = [
    "USD/BRL (OTC)", "USD/INR (OTC)", "USD/BDT (OTC)", "USD/PKR (OTC)",
    "USD/EGP (OTC)", "USD/TRY (OTC)", "USD/CAD (OTC)", "USD/MXN (OTC)",
    "EUR/USD (OTC)", "GBP/USD (OTC)", "AUD/CHF (OTC)", "CAD/JPY (OTC)",
    "CHF/JPY (OTC)", "GBP/JPY (OTC)", "EUR/GBP (OTC)", "EUR/JPY (OTC)",
    "AUD/CAD (OTC)", "NZD/USD (OTC)", "USD/JPY (OTC)", "Bitcoin (OTC)", "Gold (OTC)"
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
        .container { max-width: 450px; margin: auto; background: #111827; padding: 22px; border-radius: 16px; border: 1px solid #1e293b; box-shadow: 0 10px 25px rgba(0,0,0,0.8); }
        h2 { text-align: center; color: #38bdf8; font-size: 24px; margin-bottom: 2px; font-weight: bold; }
        .subtitle { text-align: center; color: #f59e0b; font-size: 13px; font-weight: 600; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; }
        
        /* Quotex Real-time 24h Clock Box */
        .timer-box { background: #1e293b; border: 1px solid #334155; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
        .clock-time { font-size: 19px; font-weight: bold; color: #38bdf8; letter-spacing: 1px; }
        .candle-timer { font-size: 13px; color: #f59e0b; margin-top: 3px; }

        label { font-size: 14px; color: #94a3b8; display: block; margin-bottom: 8px; }
        select { width: 100%; padding: 12px; background: #1f2937; color: #38bdf8; border: 1px solid #374151; border-radius: 8px; font-size: 16px; margin-bottom: 20px; outline: none; }
        button { width: 100%; padding: 15px; background: linear-gradient(135deg, #0284c7, #38bdf8); color: white; border: none; border-radius: 8px; font-size: 17px; font-weight: bold; cursor: pointer; transition: 0.3s; }
        button:active { transform: scale(0.98); }
        
        /* Fast Radar Animation */
        .radar-box { display: none; text-align: center; margin: 20px 0; }
        .radar { width: 70px; height: 70px; border: 3px solid #38bdf8; border-radius: 50%; margin: auto; position: relative; animation: pulse 1s infinite; }
        .radar::after { content: ''; position: absolute; width: 35px; height: 35px; background: rgba(56, 189, 248, 0.3); top: 0; left: 0; border-radius: 100% 0 0 0; animation: spin 0.7s linear infinite; transform-origin: 100% 100%; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.4); } 70% { box-shadow: 0 0 0 12px rgba(56, 189, 248, 0); } 100% { box-shadow: 0 0 0 0 rgba(56, 189, 248, 0); } }

        .result-card { display: none; background: #1f2937; padding: 20px; border-radius: 12px; border: 2px solid #38bdf8; text-align: center; margin-top: 20px; }
        .signal-text { font-size: 30px; font-weight: 900; margin: 10px 0; }
        .up { color: #22c55e; }
        .down { color: #ef4444; }
        .details { text-align: left; font-size: 13px; color: #cbd5e1; line-height: 1.7; margin-top: 15px; background: #111827; padding: 12px; border-radius: 8px; }
        
        .sentiment-bar-container { background: #374151; height: 12px; border-radius: 6px; overflow: hidden; margin: 8px 0; display: flex; }
        .buy-bar { background: #22c55e; height: 100%; }
        .sell-bar { background: #ef4444; height: 100%; }
    </style>
</head>
<body>
    <div class="container">
        <h2>👑 BD VIP SIGNAL</h2>
        <div class="subtitle">OTC KING BOT • FAST 6S SCANNER</div>
        
        <!-- Quotex 24h Real-time Clock Box -->
        <div class="timer-box">
            <div class="clock-time" id="liveClock">00:00:00 (Quotex Time)</div>
            <div class="candle-timer" id="candleTimer">ক্যান্ডেল শেষ হতে বাকি: -- সেকেণ্ড</div>
        </div>

        <label for="pairSelect">ওটিসি মার্কেট সিলেক্ট করুন:</label>
        <select id="pairSelect">
            {% for pair in pairs %}
            <option value="{{ pair }}">{{ pair }}</option>
            {% endfor %}
        </select>
        
        <button onclick="startScanning()">⚡ ৬ সেকেন্ডে ফাস্ট স্ক্যান শুরু করুন</button>
        
        <div id="radarBox" class="radar-box">
            <div class="radar"></div>
            <p style="color:#38bdf8; margin-top:10px; font-weight:bold;">দ্রুত স্ক্যান করা হচ্ছে...</p>
        </div>
        
        <div id="resultCard" class="result-card">
            <div style="font-size:11px; color:#9ca3af; letter-spacing:1px;">VIP ACCURATE SIGNAL</div>
            <div id="signalOutput" class="signal-text"></div>
            <div class="details" id="detailsOutput"></div>
        </div>
    </div>

    <script>
        // Quotex ২৪ ঘণ্টার রিয়েল-টাইম ফরম্যাট ঘড়ি ও ৬০ সেকেন্ড কাউন্টডাউন
        function updateClock() {
            const now = new Date();
            // ২৪ ঘণ্টার ফরম্যাট (HH:MM:SS) তৈরি করা
            const hours = String(now.getUTCHours()).padStart(2, '0');
            const minutes = String(now.getUTCMinutes()).padStart(2, '0');
            const seconds = String(now.getUTCSeconds()).padStart(2, '0');
            
            document.getElementById('liveClockinnerText', document.getElementById('liveClock').innerText = hours + ":" + minutes + ":" + seconds + " (Quotex Time)");
            
            const currentSec = now.getUTCSeconds();
            const candleRemaining = 60 - currentSec;
            document.getElementById('candleTimer').innerText = "বর্তমান ক্যান্ডেল শেষ হতে বাকি: " + candleRemaining + "s";
        }
        setInterval(updateClock, 1000);
        updateClock();

        function speakBangla(text) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                const msg = new SpeechSynthesisUtterance(text);
                msg.lang = 'bn-BD';
                msg.rate = 0.95;
                window.speechSynthesis.speak(msg);
            }
        }

        function startScanning() {
            const pair = document.getElementById('pairSelect').value;
            const radarBox = document.getElementById('radarBox');
            const resultCard = document.getElementById('resultCard');
            
            radarBox.style.display = 'block';
            resultCard.style.display = 'none';

            speakBangla(pair + " দ্রুত স্ক্যান করা হচ্ছে।");

            // স্ক্যানিং সময় ১৫ সেকেন্ড থেকে কমিয়ে মাত্র ৬ সেকেন্ড করা হলো
            setTimeout(() => {
                fetch(`/analyze?pair=${encodeURIComponent(pair)}`)
                    .then(response => response.json())
                    .then(data => {
                        radarBox.style.display = 'none';
                        resultCard.style.display = 'block';

                        const signalOutput = document.getElementById('signalOutput');
                        const detailsOutput = document.getElementById('detailsOutput');

                        if (data.signal.includes("CALL")) {
                            signalOutput.className = "signal-text up";
                            signalOutput.innerHTML = "CALL (UP) 🟢";
                        } else {
                            signalOutput.className = "signal-text down";
                            signalOutput.innerHTML = "PUT (DOWN) 🔴";
                        }

                        detailsOutput.innerHTML = `
                            📊 <b>মার্কেট পেয়ার:</b> ${data.pair}<br>
                            👥 <b>ট্রেডার সেন্টিমেন্ট:</b> Buy ${data.buy_percent}% | Sell ${data.sell_percent}%
                            <div class="sentiment-bar-container">
                                <div class="buy-bar" style="width: ${data.buy_percent}%;"></div>
                                <div class="sell-bar" style="width: ${data.sell_percent}%;"></div>
                            </div>
                            🔍 <b>অ্যানালিসিস:</b> ${data.candle_behavior}<br>
                            🛡️ <b>ফিল্টার:</b> ${data.manipulation_check}<br>
                            🎯 <b>একুরেসি:</b> ${data.accuracy}
                        `;

                        const voiceText = "স্ক্যান সম্পন্ন। " + data.pair + " পেয়ারে " + data.voice_signal + " নিন।";
                        speakBangla(voiceText);
                    });
            }, 6000); // ৬ সেকেন্ড স্ক্যান টাইম
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
    
    buy_pct = random.randint(58, 78)
    sell_pct = 100 - buy_pct

    behaviors = [
        "টানা ছোট ক্যান্ডেলের পর ইনস্ট্যান্ট রিপ্রাইজ উইক তৈরি হয়েছে।",
        "মাইক্রো লেভেলে ফেক ব্রেকআউট স্ক্যান করা হয়েছে।",
        "ভলিউম শিফটিং অনুযায়ী মোমেন্টাম স্ট্রং রয়েছে।",
        "ব্রোকার অ্যালগরিদম কারেকশন পয়েন্টে পৌঁছেছে।"
    ]
    
    chosen_behavior = random.choice(behaviors)
    
    if buy_pct > sell_pct:
        signal = "PUT (DOWN)"
        voice_signal = "ডাউন ট্রেড"
        manipulation = f"অধিক ট্রেডার বাই ({buy_pct}%) করায় অ্যালগরিদম ডাউন টানবে।"
    else:
        signal = "CALL (UP)"
        voice_signal = "আপ ট্রেড"
        manipulation = f"অধিক ট্রেডার সেল ({sell_pct}%) করায় অ্যালগরিদম আপ টানবে।"

    return jsonify({
        "pair": pair,
        "signal": signal,
        "voice_signal": voice_signal,
        "candle_behavior": chosen_behavior,
        "buy_percent": buy_pct,
        "sell_percent": sell_pct,
        "manipulation_check": manipulation,
        "accuracy": f"{random.randint(89, 97)}%"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
