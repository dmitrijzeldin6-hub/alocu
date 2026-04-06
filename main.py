import os
import requests
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8723694663:AAEKRDMJ3JvrNDMUR_6vc12ztF8npLFdO54" 
PRICE_STARS = 5

html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <script src="https://telegram.org"></script>
    <style>
        body {
            margin: 0; height: 100vh; display: flex; align-items: center; justify-content: center;
            background: #000; font-family: sans-serif; overflow: hidden; color: white;
        }
        .main-container { text-align: center; width: 100%; }
        h1 { color: #d4af37; text-transform: uppercase; margin: 0; }
        .price-info { color: #ffd700; margin: 10px 0 20px; font-weight: bold; }
        #wheel {
            width: 280px; height: 280px; border-radius: 50%; border: 8px solid #d4af37;
            margin: 0 auto; position: relative; transition: transform 4s cubic-bezier(0.15, 0, 0.15, 1);
            background: conic-gradient(#d4af37 0deg 45deg, #222 45deg 90deg, #d4af37 90deg 135deg, #222 135deg 180deg, #444 180deg 225deg, #333 225deg 270deg, #444 270deg 315deg, #333 315deg 360deg);
        }
        .label { position: absolute; width: 100%; height: 100%; text-align: center; font-weight: bold; font-size: 10px; padding-top: 15px; box-sizing: border-box; }
        .spin-btn { 
            margin-top: 30px; padding: 15px 40px; font-size: 18px; 
            background: #d4af37; color: black; border: none; 
            border-radius: 50px; font-weight: bold; cursor: pointer; 
        }
        .spin-btn:disabled { opacity: 0.3; }
    </style>
</head>
<body>
<div class="main-container">
    <h1>ALOCU gift</h1>
    <div class="price-info">5 ⭐️ звёзд за прокрут</div>
    <div id="wheel">
        <div class="label" style="transform: rotate(22.5deg)">Bear</div>
        <div class="label" style="transform: rotate(67.5deg)">Rocket</div>
        <div class="label" style="transform: rotate(112.5deg)">Heart</div>
        <div class="label" style="transform: rotate(157.5deg)">Rose</div>
        <div class="label" style="transform: rotate(202.5deg)">Пусто</div>
        <div class="label" style="transform: rotate(247.5deg)">Пусто</div>
        <div class="label" style="transform: rotate(292.5deg)">Пусто</div>
        <div class="label" style="transform: rotate(337.5deg)">Пусто</div>
    </div>
    <button class="spin-btn" id="btn">КРУТИТЬ</button>
</div>

<script>
    const tg = window.Telegram.WebApp;
    tg.ready();
    tg.expand();

    const btn = document.getElementById('btn');
    const wheel = document.getElementById('wheel');
    const prizes = ["Bear", "Rocket", "Heart", "Rose", "Пусто", "Пусто", "Пусто", "Пусто"];
    let currentRotation = 0;

    btn.addEventListener('click', async () => {
        btn.disabled = true;
        
        try {
            const response = await fetch('/create-stars-invoice', { method: 'POST' });
            const data = await response.json();

            if (data.ok && data.result) {
                // Вызываем окно оплаты
                tg.openInvoice(data.result, (status) => {
                    if (status === 'paid') {
                        runWheel();
                    } else {
                        tg.showAlert("Оплата не прошла или была отменена.");
                        btn.disabled = false;
                    }
                });
            } else {
                tg.showAlert("Ошибка API: " + (data.description || "Не удалось создать счет"));
                btn.disabled = false;
            }
        } catch (e) {
            tg.showAlert("Ошибка сервера. Проверьте логи Render.");
            btn.disabled = false;
        }
    });

    function runWheel() {
        const randomIndex = Math.floor(Math.random() * prizes.length);
        const extraRotation = 1800 + (360 - (randomIndex * 45));
        currentRotation += extraRotation;
        
        wheel.style.transform = `rotate(${currentRotation}deg)`;
        
        setTimeout(() => {
            const result = prizes[randomIndex];
            tg.showPopup({
                title: 'Результат',
                message: result === "Пусто" ? "В этот раз ничего!" : "Вы выиграли: " + result,
                buttons: [{type: 'ok'}]
            });
            btn.disabled = false;
        }, 4500);
    }
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html_template)

@app.route('/create-stars-invoice', methods=['POST'])
def create_invoice():
    url = f"https://telegram.org{BOT_TOKEN}/createInvoiceLink"
    payload = {
        "title": "Удача NFT",
        "description": "Прокрут колеса за 5 звёзд",
        "payload": "spin_pay",
        "provider_token": "", 
        "currency": "XTR", 
        "prices": [{"label": "Stars", "amount": PRICE_STARS}]
    }
    try:
        r = requests.post(url, json=payload)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"ok": False, "description": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
