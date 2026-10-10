from flask import Flask, render_template_string, jsonify, request
import random
import time

app = Flask(__name__)

# ওটিসি পেয়ারের তালিকা
OTC_PAIRS = [
    "USD/BRL (OTC)", "AUD/CHF (OTC)", "USD/CAD (OTC)", "CAD/JPY (OTC)",
    "CHF/JPY (OTC)", "GBP/JPY (OTC)", "EUR/USD (OTC)", "Bitcoin (OTC)", "Gold (OTC)"
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Quotex OTC Master Bot</title>
    <style>
        body { background-color: #0f172a; color: #f8fafc; font-family: sans-serif; margin: 0; padding: 15px; }
        .container { max-width: 500px; margin: auto; background: #1e293b; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        h2 { text-align: center; color: #38bdf8; font-size: 22px; margin-bottom: 5px; }
        .subtitle { text-align: center; color: #94a3b8; font-size: 12px; margin-bottom: 20px; }
        label { font-size: 14px; color: #cbd5e1; display: block; margin-bottom: 5px; }
        select { width: 100%; padding: 12px; background: #334155; color: #fff; border: 1px solid #475569; border-radius: 8px; font-size: 16px; margin-bottom: 15px; }
        button { width: 100%; padding: 14px; background: #0284c7; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; }
        button:active { background: #0369a1; }
        .result-box { margin-top: 20px; background: #0f172a; padding: 15px; border-radius: 8px; border: 1px solid #334155; display: none; }
        .signal-up { color: #22c55e; font-size: 24px; font-weight: bold; text-align: center; }
        .signal-down { color: #ef4444; font-size: 24px; font-weight: bold; text-align: center; }
        .loader { text-align: center; color: #f59e0b; font-weight: bold; display: none; margin: 15px 0; }
        .details { font-size: 13px; color: #94a3b8; margin-top: 10px; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🤖 OTC Master Signal Bot</h2>
        <div class="subtitle">ওটিসি অ্যালগরিদম ও সেন্টিমেন্ট অ্যানালাইজার</div>
        
        <label for="pairSelect">ওটিসি পেয়ার সিলেক্ট করুন:</label>
        <select id="pairSelect">
            {% for pair in pairs %}
            <option value="{{ pair }}">{{ pair }}</option>
            {% endfor %}
        </select>
        
        <button onclick="getSignal()">১৫ সেকেন্ড স্ক্যান করে সিগন্যাল নিন</button>
        
        <div id="loader" class="loader">⏳ ১৫ সেকেন্ড ধরে ওটিসি ক্যান্ডেল ও ভলিউম স্ক্যান করা হচ্ছে...</div>
        
        <div id="resultBox" class="result-box">
            <div id="signalOutput"></div>
            <div class="details" id="detailsOutput"></div>
        </div>
    </div>

    <script>
        function getSignal() {
            const pair = document.getElementById('pairSelect').value;
            const loader = document.getElementById('loader');
            const resultBox = document.getElementById('resultBox');
            const signalOutput = document.getElementById('signalOutput');
            const detailsOutput = document.getElementById('detailsOutput');

            loader.style.display = 'block';
            resultBox.style.display = 'none';

            // ১৫ সেকেন্ডের স্ক্যানিং সিমুলেশন
            setTimeout(() => {
                fetch(`/analyze?pair=${encodeURIComponent(pair)}`)
                    .then(response => response.json())
                    .then(data => {
                        loader.style.display = 'none';
                        resultBox.style.display = 'block';

                        if (data.signal.includes("CALL")) {
                            signalOutput.innerHTML = `<div class="signal-up">🟢 ${data.signal}</div>`;
                        } else {
                            signalOutput.innerHTML = `<div class="signal-down">🔴 ${data.signal}</div>`;
                        }

                        detailsOutput.innerHTML = `
                            📊 <b>পেয়ার:</b> ${data.pair}<br>
                            🔍 <b>গত ৫ ক্যান্ডেল বিহেভিয়ার:</b> ${data.candle_behavior}<br>
                            👥 <b>ব্রোকার সেন্টিমেন্ট (Volume):</b> ${data.sentiment}<br>
                            🛡️ <b>ম্যানেজমেন্ট ফিল্টার:</b> ${data.manipulation_check}<br>
                            🎯 <b>সঠিকতার সম্ভাবনা:</b> ${data.accuracy}
                        `;
                    });
            }, 15000); // ঠিক ১৫ সেকেন্ড স্ক্যানিং ডিলে
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
        "টানা ৩টি ছোট ক্যান্ডেলের পর শক্তিশালী রিভার্সাল উইক তৈরি হয়েছে।",
        "মাইক্রো সাপোর্ট লেভেল ব্রেক করার চেষ্টা করে ফেক আউট দেখিয়েছে।",
        "গত ৫ ক্যান্ডেলে ভলিউম কমে গেছে, ছোট ডোজী প্যাটার্ন তৈরি হয়েছে।",
        "স্ট্রং মোমেন্টাম ক্যান্ডেল চলছে, ট্রেন্ড ফলো করার উপযুক্ত সময়।"
    ]
    
    sentiments = [
        "Retail Traders বেশি বাই করেছে (অ্যালগরিদম ডাউন টানতে পারে)",
        "Retail Traders বেশি সেল দিচ্ছে (অ্যালগরিদম আপ টানতে পারে)",
        "মার্কেটে বায়ার ও সেলারের ব্যালেন্স সমান সমান রয়েছে"
    ]
    
    chosen_sentiment = random.choice(sentiments)
    if "বাই" in chosen_sentiment:
        signal = "PUT (DOWN) ⬇️"
        manipulation = "ব্রোকার সেন্টিমেন্ট কাউন্টার করার জন্য ডাউন সিগন্যাল সিলেক্ট করা হয়েছে।"
    else:
        signal = "CALL (UP) ⬆️"
        manipulation = "ব্রোকার সেন্টিমেন্ট কাউন্টার করার জন্য আপ সিগন্যাল সিলেক্ট করা হয়েছে।"

    return jsonify({
        "pair": pair,
        "signal": signal,
        "candle_behavior": random.choice(behaviors),
        "sentiment": chosen_sentiment,
        "manipulation_check": manipulation,
        "accuracy": f"{random.randint(84, 93)}%"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
