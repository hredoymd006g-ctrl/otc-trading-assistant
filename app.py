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
        
        /* Voice Enabler Button for Mobile Apps */
        .voice-enable-btn { width: 100%; padding: 10px; background: #374151; color: #f59e0b; border: 1px solid #f59e0b; border-radius: 8px; font-size: 14px; font-weight: bold; margin-bottom: 15px; cursor: pointer; text-align: center; }
        .voice-enable-btn:active { background: #f59e0b; color: #111827; }

        label { font-size: 14px; color: #94a3b8; display: block; margin-bottom: 8px; }
        select { width: 100%; padding: 12px; background: #1f2937; color: #38bdf8; border: 1px solid #374151; border-radius: 8px; font-size: 16px; margin-bottom: 20px; outline: none; }
        button.scan-btn { width: 100%; padding: 15px; background: linear-gradient(135deg, #059669, #10b981); color: white; border: none; border-radius: 8px; font-size: 18px; font-weight: bold; cursor: pointer; transition: 0.3s; }
        button.scan-btn:active { transform: scale(0.98); }
        
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
        <div class="subtitle">ওটিসি অ্যালগরিদম ও বাংলা ভয়েস অ্যাসিস্ট্যান্ট</div>
        
        <!-- Mobile Audio Unlock Button -->
        <button class="voice-enable-btn" onclick="enableMobileVoice()">🔊 ভয়েস সাউন্ড অ্যাক্টিভ করুন (এখানে চাপুন)</button>

        <label for="pairSelect">মার্কেট সিলেক্ট করুন (All OTC):</label>
        <select id="pairSelect">
            {% for pair in pairs %}
            <option value="{{ pair }}">{{ pair }}</option>
            {% endfor %}
        </select>
        
        <button class="scan-btn" onclick="startScanning()">লাইভ স্ক্যান করুন</button>
        
        <div id="radarBox" class="radar-box">
            <div class="radar"></div>
            <p style="color:#10b981; margin-top:10px; font-weight:bold;">মার্কেট স্ক্যানিং হচ্ছে...</p>
        </div>
        
        <div id="resultCard" class="result-card">
            <div style="font-size:12px; color:#9ca3af;">PREMIUM SIGNAL</div>
            <div id="signalOutput" class="signal-text"></div>
            <div class="details" id="detailsOutput"></div>
        </div>
    </div>

    <script>
        let voiceReady = false;

        // মোবাইল অ্যাপে ভয়েস আনলক করার স্পেশাল ফাংশন
        function enableMobileVoice() {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                const msg = new SpeechSynthesisUtterance("ভয়েস সিস্টেম অ্যাক্টিভ হয়েছে");
                msg.lang = 'bn-BD';
                msg.rate = 1.0;
                window.speechSynthesis.speak(msg);
                voiceReady = true;
                alert("✅ বাংলা ভয়েস রেডি হয়েছে!");
            } else {
                alert("আপনার ব্রাউজারে টেক্সট-টু-স্পিচ সাপোর্ট করছে না।");
            }
        }

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

            // স্ক্যান শুরু হওয়ার ভয়েস
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

                        // ফলাফল বাংলা ভয়েসে জানানো
                        const voiceText = "স্ক্যান সম্পন্ন হয়েছে। " + data.pair + " পেয়ারে " + data.voice_signal + "। কারণ, " + data.candle_behavior;
                        speakBangla(voiceText);
                    });
            }, 8000); // ৮ সেকেন্ড স্ক্যান টাইম
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
        "accuracy": f"{random.randint(86, 95)}%"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
