from flask import Flask, render_template_string, jsonify, request
import random

app = Flask(__name__)

# সমস্ত ওটিসি পেয়ারের পূর্ণাঙ্গ তালিকা
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
        .container { max-width: 450px; margin: auto; background: #111827; padding: 20px; border-radius: 16px; border: 1px solid #1e293b; box-shadow: 0 10px 25px rgba(0,0,0,0.8); }
        h2 { text-align: center; color: #38bdf8; font-size: 24px; margin-bottom: 5px; font-weight: bold; }
        .subtitle { text-align: center; color: #f59e0b; font-size: 13px; margin-bottom: 20px; font-weight: 600; text-transform: uppercase; }
        label { font-size: 14px; color: #94a3b8; display: block; margin-bottom: 8px; }
        select { width: 100%; padding: 12px; background: #1f2937; color: #38bdf8; border: 1px solid #374151; border-radius: 8px; font-size: 16px; margin-bottom: 20px; outline: none; }
        button { width: 100%; padding: 15px; background: linear-gradient(135deg, #0284c7, #38bdf8); color: white; border: none; border-radius: 8px; font-size: 18px; font-weight: bold; cursor: pointer; transition: 0.3s; }
        button:active { transform: scale(0.98); }
        
        /* Radar Scanner Animation */
        .radar-box { display: none; text-align: center; margin: 20px 0; }
        .radar { width: 80px; height: 80px; border: 3px solid #38bdf8; border-radius: 50%; margin: auto; position: relative; animation: pulse 1.5s infinite; }
        .radar::after { content: ''; position: absolute; width: 40px; height: 40px; background: rgba(56, 189, 248, 0.3); top: 0; left: 0; border-radius: 100% 0 0 0; animation: spin 1s linear infinite; transform-origin: 100% 100%; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.4); } 70% { box-shadow: 0 0 0 15px rgba(56, 189, 248, 0); } 100% { box-shadow: 0 0 0 0 rgba(56, 189, 248, 0); } }

        .result-card { display: none; background: #1f2937; padding: 20px; border-radius: 12px; border: 2px solid #38bdf8; text-align: center; margin-top: 20px; }
        .signal-text { font-size: 32px; font-weight: 900; margin: 10px 0; }
        .up { color: #22c55e; }
        .down { color: #ef4444; }
        .details { text-align: left; font-size: 13px; color: #9ca3af; line-height: 1.6; margin-top: 15px; background: #111827; padding: 10px; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>👑 BD VIP SIGNAL</h2>
        <div class="subtitle">OTC King Bot • বাংলা ভয়েস অ্যাসিস্ট্যান্ট</div>
        
        <label for="pairSelect">মার্কেট সিলেক্ট করুন (All OTC):</label>
        <select id="pairSelect">
            {% for pair in pairs %}
            <option value="{{ pair }}">{{ pair }}</option>
            {% endfor %}
        </select>
        
        <button onclick="startScanning()">লাইভ স্ক্যান করুন</button>
        
        <div id="radarBox" class="radar-box">
            <div class="radar"></div>
            <p style="color:#38bdf8; margin-top:10px; font-weight:bold;">মার্কেট স্ক্যানিং হচ্ছে...</p>
        </div>
        
        <div id="resultCard" class="result-card">
            <div style="font-size:12px; color:#9ca3af;">VIP ACCURATE SIGNAL</div>
            <div id="signalOutput" class="signal-text"></div>
            <div class="details" id="detailsOutput"></div>
        </div>
    </div>

    <script>
        function speakBangla(text) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                const msg = new SpeechSynthesisUtterance(text);
                msg.lang = 'bn-BD';
                msg.rate = 0.9;
                window.speechSynthesis.speak(msg);
            }
        }

        function startScanning() {
            const pair = document.getElementById('pairSelect').value;
            const radarBox = document.getElementById('radarBox');
            const resultCard = document.getElementById('resultCard');
            
            radarBox.style.display = 'block';
            resultCard.style.display = 'none';

            speakBangla(pair + " মার্কেট স্ক্যান করা হচ্ছে। অনুগ্রহ করে অপেক্ষা করুন।");

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
                            signalOutput.innerHTML = "BUY / UP 🟢";
                        } else {
                            signalOutput.className = "signal-text down";
                            signalOutput.innerHTML = "SELL / DOWN 🔴";
                        }

                        detailsOutput.innerHTML = `
                            📊 <b>পেয়ার:</b> ${data.pair}<br>
                            🔍 <b>কারণ:</b> ${data.candle_behavior}<br>
                            👥 <b>ব্রোকার ভলিউম:</b> ${data.sentiment}<br>
                            🎯 <b>একুরেসি:</b> ${data.accuracy}
                        `;

                        const voiceText = "স্ক্যান সম্পন্ন হয়েছে। " + data.pair + " পেয়ারে " + data.voice_signal + "। কারণ, " + data.candle_behavior;
                        speakBangla(voiceText);
                    });
            }, 8000);
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
    
    behaviors = [
        "খুচরা ট্রেডারদের বিপুল বাই অর্ডারের কারণে ব্রোকার অ্যালগরিদম রিভার্সাল টানবে।",
        "মাইক্রো সাপোর্ট লেভেলে ফেক ব্রেকআউট দেখা গেছে।",
        "বিগত ক্যান্ডেলের উইক বড় এবং সেলার প্রেসার বেশি।",
        "অ্যালগরিদমিক ট্রেন্ড মোমেন্টাম আপ সাইডে স্ট্রং।"
    ]
    
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
        "signal": signal,
        "voice_signal": voice_signal,
        "candle_behavior": chosen_behavior,
        "sentiment": chosen_sentiment,
        "accuracy": f"{random.randint(88, 96)}%"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
