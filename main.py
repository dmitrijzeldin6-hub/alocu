import sqlite3
import requests
import datetime
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)
# ВСТАВЬ СВОЙ ТОКЕН НИЖЕ
BOT_TOKEN = "8723694663:AAEKRDMJ3JvrNDMUR_6vc12ztF8npLFdO54"

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS stats 
                      (user_id INTEGER PRIMARY KEY, daily_count INTEGER, last_date TEXT)''')
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT daily_count, last_date FROM stats WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    today = str(datetime.date.today())
    if not res or res[1] != today:
        return 0, today
    return res[0], today

def increment_spins(user_id, count, date):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO stats VALUES (?, ?, ?)", (user_id, count + 1, date))
    conn.commit()
    conn.close()

init_db()

html_template = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>ALOCU gift | NFT Wheel</title>
    <script src="https://telegram.org"></script>
    <style>
        body { margin: 0; height: 100vh; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, #463305 0%, #000 100%); font-family: 'Segoe UI', sans-serif; overflow: hidden; }
        .main-container { text-align: center; position: relative; }
        h1 { color: #d4af37; font-size: 3rem; margin: 0 0 10px 0; text-transform: uppercase; letter-spacing: 5px; text-shadow: 0 0 15px rgba(212, 175, 55, 0.5); }
        .attempts-text { color: #fff; margin-bottom: 20px; font-size: 1.1rem; opacity: 0.8; }
        .arrow { position: absolute; top: 115px; left: 50%; transform: translateX(-50%); width: 0; height: 0; border-left: 15px solid transparent; border-right: 15px solid transparent; border-top: 35px solid #ff4400; z-index: 10; filter: drop-shadow(0 0 5px red); }
        #wheel { width: 350px; height: 350px; border-radius: 50%; border: 8px solid #d4af37; background: conic-gradient(#d4af37 0deg 45deg, #222 45deg 90deg, #d4af37 90deg 135deg, #222 135deg 180deg, #444 180deg 225deg, #333 225deg 270deg, #444 270deg 315deg, #333 315deg 360deg); position: relative; transition: transform 4s cubic-bezier(0.15, 0, 0.15, 1); box-shadow: 0 0 50px rgba(212, 175, 55, 0.4); }
        .label { position: absolute; width: 100%; height: 100%; text-align: center; color: white; font-weight: bold; text-transform: uppercase; font-size: 13px; pointer-events: none; }
        .spin-btn { margin-top: 30px; padding: 15px 50px; font-size: 20px; background: #d4af37; color: black; border: none; cursor: pointer; font-weight: bold; border-radius: 8px; transition: 0.3s; }
        .spin-btn:disabled { opacity: 0.3; cursor: not-allowed; }
    </style>
</head>
<body>
<div class="main-container">
    <h1>ALOCU gift</h1>
    <div class="attempts-text">Осталось сегодня: <span id="tries">3</span></div>
    <div class="arrow"></div>
    <div id="wheel">
        <div class="label" style="transform: rotate(22.5deg)">Bear</div>
        <div class="label" style="transform: rotate(67.5deg)">Rocket</div>
        <div class="label" style="transform: rotate(112.5deg)">Heart</div>
        <div class="label" style="transform: rotate(157.5deg)">Rose</div>
        <div class="label" style="transform: rotate(202.5deg)">Ничего</div>
        <div class="label" style="transform: rotate(247.5deg)">Ничего</div>
        <div class="label" style="transform: rotate(292.5deg)">Ничего</div>
        <div class="label" style="transform: rotate(337.5deg)">Ничего</div>
    </div>
    <button class="spin-btn" id="btn" onclick="startSpin()">Крутить (6 ⭐)</button>
</div>

<script>
    const tg = window.Telegram.WebApp;
    const userId = tg.initDataUnsafe?.user?.id || 0;
    const wheel = document.getElementById('wheel');
    const btn = document.getElementById('btn');
    const triesDisplay = document.getElementById('tries');
    const prizes = ["Bear", "Rocket", "Heart", "Rose", "Ничего", "Ничего", "Ничего", "Ничего"];

    async function updateStatus() {
        const res = await fetch(`/get_status?id=${userId}`);
        const data = await res.json();
        triesDisplay.innerText = data.spins_left;
        btn.disabled = (data.spins_left <= 0);
    }

    async function startSpin() {
        btn.disabled = true;
        const res = await fetch(`/create_spin_invoice?id=${userId}`, {method: 'POST'});
        const data = await res.json();

        if (data.url) {
            tg.openInvoice(data.url, async function(status) {
                if (status === 'paid') {
                    await fetch(`/confirm_spin?id=${userId}`, {method: 'POST'});
                    const randomIndex = Math.floor(Math.random() * prizes.length);
                    const totalRotation = 3600 + (360 - (randomIndex * 45));
                    wheel.style.transition = 'transform 4s cubic-bezier(0.15, 0, 0.15, 1)';
                    wheel.style.transform = `rotate(${totalRotation}deg)`;
                    setTimeout(() => {
                        alert("Ваш приз: " + prizes[randomIndex]);
                        updateStatus();
                    }, 4100);
                } else {
                    alert("Оплата не прошла");
                    btn.disabled = false;
                }
            });
        } else {
            alert(data.error || "Ошибка");
            btn.disabled = false;
        }
    }
    updateStatus();
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html_template)

@app.route('/get_status')
def get_status():
    user_id = request.args.get('id', type=int)
    count, _ = get_user_stats(user_id)
    return jsonify({"spins_left": 3 - count})

@app.route('/create_spin_invoice', methods=['POST'])
def create_spin_invoice():
    user_id = request.args.get('id', type=int)
    count, today = get_user_stats(user_id)
    if count >= 3:
        return jsonify({"error": "Лимит исчерпан"}), 400

    payload = {
        "title": "Один прокрут",
        "description": "Попытка в NFT Wheel",
        "payload": f"spin_{user_id}",
        "currency": "XTR",
        "prices": [{"label": "Spin", "amount": 6}]
    }

    url = f"https://telegram.org{BOT_TOKEN}/createInvoiceLink"
    r = requests.post(url, json=payload)
    return jsonify({"url": r.json().get("result")})

@app.route('/confirm_spin', methods=['POST'])
def confirm_spin():
    user_id = request.args.get('id', type=int)
    count, today = get_user_stats(user_id)
    increment_spins(user_id, count, today)
    return jsonify({"success": True})

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
