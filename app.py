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
            margin:
