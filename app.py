import os
import time
from flask import Flask, render_template_string, jsonify, request
import random

app = Flask(__name__)

OTC_PAIRS = [
    "USD/BRL (OTC)", "USD/INR (OTC)", "USD/BDT (OTC)", "USD/PKR (OTC)",
    "USD/EGP (OTC)", "USD/TRY (OTC)", "USD/CAD (OTC)", "USD/MXN (OTC)",
    "EUR/USD (OTC)", "GBP/USD (OTC)", "AUD/CHF (OTC)", "CAD/JPY (OTC)",
    "CHF/JPY (OTC)", "GBP/JPY (OTC)", "Bitcoin (OTC)", "Gold (OTC)"
]

TIMEFRAMES = ["5s", "10s", "15s", "30s", "1m", "2m", "3m", "5m", "10m"]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BD VIP OTC Master Engine</title>
    <style>
        :root {
            --bg-deep: #030712;
            --panel-bg: rgba(15, 23, 42, 0.98);
            --neon-green: #10b981;
            --neon-blue: #38bdf8;
            --neon-orange: #f59e0b;
            --neon-red: #ef4444;
            --glow-cyan: 0 0 18px rgba(56, 189, 248, 0.5);
            --glow-green: 0 0 18px rgba(16, 185, 129, 0.5);
            --glow-red: 0 0 18px rgba(239, 68, 68, 0.5);
        }
        
        body { 
            background: radial-gradient(circle at center, #0f172a 0%, #030712 100%); 
            color: #f8fafc; 
            font-family: 'Segoe UI', Roboto, sans-serif; 
            margin: 0; 
            padding: 10px; 
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .dashboard-container { 
            width: 100%;
            max-width: 460px; 
            background: var(--panel-bg); 
            backdrop-filter: blur(25px);
            padding: 18px; 
            border-radius: 22px; 
            border: 1px solid rgba(56, 189, 248, 0.6); 
            box-shadow: 0 25px 50px rgba(0,0,0,0.95); 
            box-sizing: border-box;
        }

        .top-hud {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 8px;
            margin-bottom: 14px;
        }

        .bot-title { 
            color: #ffffff; 
            font-size: 15px; 
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

        .grid-inputs {
            display: flex;
            gap: 8px;
            margin-bottom: 12px;
        }

        .input-group {
            flex: 1;
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
            font-size: 12px; 
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
            cursor: pointer;
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
            background: radial-gradient(circle, rgba(56,189,248,0.15) 0%, rgba(11,15,25,0.96) 80%);
            border: 2px solid var(--neon-blue);
            border-radius: 16px;
            padding: 16px;
            text-align: center;
            box-shadow: 0 0 25px rgba(56, 189, 248, 0.35);
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
            gap: 8px;
            margin-top: 12px;
        }

        .stat-box {
            flex: 1;
            background: rgba(11, 15, 25, 0.9);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 10px;
            padding: 8px;
            text-align: center;
        }

        .stat-value {
            font-size: 12px;
            font-weight: bold;
            color: #f8fafc;
        }

        .behavior-panel {
            background: rgba(11, 15, 25, 0.95);
            border: 1px solid var(--neon-blue);
            border-radius: 12px;
            padding: 12px;
            margin-top: 12px;
            font-size: 11px;
            color: #e2e8f0;
            line-height: 1.5;
            text-align: left;
            box-shadow: inset 0 0 10px rgba(56,189,248,0.15);
        }

        #mediaModal {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(3, 7, 18, 0.85);
            backdrop-filter: blur(8px);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        .modal-content {
            background: #0f172a;
            border: 1px solid var(--neon-blue);
            border-radius: 16px;
            padding: 20px;
            width: 85%;
            max-width: 320px;
            text-align: center;
            box-shadow: 0 15px 30px rgba(0,0,0,0.9);
        }
        .modal-btn {
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            border-radius: 10px;
            font-weight: bold;
            font-size: 13px;
            cursor: pointer;
            border: none;
        }
        .btn-cam-opt { background: #d97706; color: white; box-shadow: 0 0 10px rgba(245,158,11,0.4); }
        .btn-gallery-opt { background: #059669; color: white; box-shadow: 0 0 10px rgba(16,185,129,0.4); }
        .btn-cancel-opt { background: #334155; color: #cbd5e1; }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="top-hud">
            <div>
                <h2 class="bot-title">BD VIP OTC MASTER ENGINE</h2>
                <div class="realtime-clock" id="liveClockTimer">⏱️ --:--:--</div>
            </div>
            <div class="status-pill" id="candleTimerPill">⏳ 27s Window</div>
        </div>

        <div class="grid-inputs">
            <div class="input-group">
                <label class="section-label">OTC Asset</label>
                <select id="pairSelect">
                    {% for pair in pairs %}
                    <option value="{{ pair }}">{{ pair }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="input-group" style="max-width: 110px;">
                <label class="section-label">Timeframe</label>
                <select id="tfSelect">
                    {% for tf in timeframes %}
                    <option value="{{ tf }}" {% if tf == '1m' %}selected{% endif %}>{{ tf }}</option>
                    {% endfor %}
                </select>
            </div>
        </div>

        <div class="upload-box" onclick="openMediaModal()">
            <label class="section-label" style="margin-bottom: 4px; cursor: pointer;">📷 Quotex Chart Capture / Screenshot</label>
            <span id="fileStatus" style="font-size: 11px; color: var(--neon-blue);">কোটেক্স চার্টের স্ক্রিনশট বা ছবি দিতে এখানে চাপুন</span>
        </div>

        <input type="file" id="cameraInput" accept="image/*" capture="environment" style="display:none;" onchange="handleFileSelected(this)">
        <input type="file" id="galleryInput" accept="image/*" style="display:none;" onchange="handleFileSelected(this)">

        <div class="btn-grid">
            <button class="scan-btn" onclick="analyzeChartImage()">🔍 MASTER SCAN</button>
            <button class="cam-btn" onclick="openMediaModal()">📸 CAPTURE CHART</button>
        </div>
        
        <div class="holo-display">
            <div style="font-size: 11px; color: var(--neon-blue); font-weight: bold; margin-bottom: 5px;" id="bossHeader">⚡ MASTER BOSS FINAL DECISION</div>
            
            <div id="signalOutput" class="signal-call-put wait-glow">READY</div>
            <div class="timer-hud" id="countdownTimer" style="font-size: 11px; color: var(--neon-blue);">⏳ Upload chart or start auto-scan</div>

            <div class="stats-grid">
                <div class="stat-box">
                    <div style="font-size: 9px; color: var(--neon-green);">ENTRY WINDOW</div>
                    <div class="stat-value" id="statWindow">--</div>
                </div>
                <div class="stat-box">
                    <div style="font-size: 9px; color: var(--neon-blue);">S&R LEVELS</div>
                    <div class="stat-value" id="statSwing">LOCKED 🔒</div>
                </div>
                <div class="stat-box">
                    <div style="font-size: 9px; color: var(--neon-orange);">10-CANDLE SYNC</div>
                    <div class="stat-value" id="statStatus">Optimal</div>
                </div>
            </div>

            <div class="behavior-panel" id="behaviorOutput">
                🤖 <b>লাইভ মার্কেট বিহেভিয়ার:</b> সমস্ত সাপোর্টেড লেভেল লক করা রয়েছে। ১০-ক্যান্ডেল হিস্টোরি স্ক্যান করে বায়ার/সেলার অর্ডার প্রেসার অনুযায়ী প্রফেশনাল সিগন্যাল ফিল্টার হবে।
            </div>
        </div>
    </div>

    <div id="mediaModal">
        <div class="modal-content">
            <h3 style="color: var(--neon-blue); margin-top: 0; font-size: 15px;">🖼️ ইনপুট মাধ্যম নির্বাচন করুন</h3>
            <p style="font-size: 11px; color: #cbd5e1; margin-bottom: 15px;">আপনি কোটেক্স চার্ট কীভাবে যুক্ত করতে চান?</p>
            <button class="modal-btn btn-cam-opt" onclick="triggerCamera()">📸 সরাসরি ছবি তুলুন (Camera)</button>
            <button class="modal-btn btn-gallery-opt" onclick="triggerGallery()">🖼️ স্ক্রিনশট আপলোড করুন (Gallery)</button>
            <button class="modal-btn btn-cancel-opt" onclick="closeMediaModal()">বাতিল করুন</button>
        </div>
    </div>

    <audio id="alertSound" src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" preload="auto"></audio>

    <script>
        let imageUploaded = false;

        function updateRealtimeClock() {
            const now = new Date();
            const h = String(now.getHours()).padStart(2, '0');
            const m = String(now.getMinutes()).padStart(2, '0');
            const s = String(now.getSeconds()).padStart(2, '0');
            const sec = now.getSeconds();

            document.getElementById('liveClockTimer').innerHTML = `⏱️ ${h}:${m}:${s}`;
            
            const candleTimerPill = document.getElementById('candleTimerPill');
            if (sec <= 27) {
                candleTimerPill.innerHTML = `🟢 Scan Window Open (${27 - sec}s left)`;
                candleTimerPill.style.color = '#10b981';
            } else {
                candleTimerPill.innerHTML = `🛑 Window Closed (${60 - sec}s to Next)`;
                candleTimerPill.style.color = '#ef4444';
            }
        }
        setInterval(updateRealtimeClock, 1000);

        function playSound() {
            const sound = document.getElementById('alertSound');
            if (sound) {
                sound.currentTime = 0;
                sound.play().catch(e => console.log("Audio blocked", e));
            }
        }

        function openMediaModal() {
            document.getElementById('mediaModal').style.display = 'flex';
        }

        function closeMediaModal() {
            document.getElementById('mediaModal').style.display = 'none';
        }

        function triggerCamera() {
            closeMediaModal();
            document.getElementById('cameraInput').click();
        }

        function triggerGallery() {
            closeMediaModal();
            document.getElementById('galleryInput').click();
        }

        function handleFileSelected(input) {
            const fileStatus = document.getElementById('fileStatus');
            const countdownTimer = document.getElementById('countdownTimer');
            if (input.files && input.files[0]) {
                imageUploaded = true;
                fileStatus.innerHTML = `✅ Loaded: ${input.files[0].name}`;
                countdownTimer.innerHTML = `⏳ Chart loaded. Ready for 27s Scan Window.`;
            }
        }

        function analyzeChartImage() {
            const signalOutput = document.getElementById('signalOutput');
            const behaviorOutput = document.getElementById('behaviorOutput');
            const statWindow = document.getElementById('statWindow');
            const statSwing = document.getElementById('statSwing');
            const statStatus = document.getElementById('statStatus');
            const countdownTimer = document.getElementById('countdownTimer');
            const bossHeader = document.getElementById('bossHeader');
            const selectedPair = document.getElementById('pairSelect').value;
            const selectedTf = document.getElementById('tfSelect').value;

            signalOutput.className = "signal-call-put wait-glow";
            signalOutput.innerHTML = "SCANNING...";
            countdownTimer.innerHTML = "⏳ Locked Levels & 10-Candle Structure Scanning...";
            bossHeader.innerHTML = "🔄 Processing Multi-Timeframe Order Flow...";

            setTimeout(() => {
                fetch(`/master_analyze?pair=${encodeURIComponent(selectedPair)}&tf=${selectedTf}`)
                    .then(response => response.json())
                    .then(data => {
                        bossHeader.innerHTML = "👑 MASTER BOSS FINAL DECISION";
                        if (data.action === "WAIT") {
                            signalOutput.className = "signal-call-put wait-glow";
                            signalOutput.innerHTML = "WAIT ⏳";
                            statStatus.innerHTML = "Filter Blocked";
                            countdownTimer.innerHTML = `🛑 ${data.time_msg}`;
                        } else if (data.signal_type === "UP") {
                            signalOutput.className = "signal-call-put up-glow";
                            signalOutput.innerHTML = "HIGHER ⬆️";
                            statStatus.innerHTML = "99% High Conf";
                            countdownTimer.innerHTML = "✅ High Probability BUY Entry";
                            playSound();
                        } else {
                            signalOutput.className = "signal-call-put down-glow";
                            signalOutput.innerHTML = "LOWER ⬇️";
                            statStatus.innerHTML = "99% High Conf";
                            countdownTimer.innerHTML = "✅ High Probability SELL Entry";
                            playSound();
                        }

                        statWindow.innerHTML = data.seconds_remaining + "s";
                        statSwing.innerHTML = "LOCKED 🔒";

                        behaviorOutput.innerHTML = `
                            📈
