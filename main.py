import requests
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8723694663:AAEKRDMJ3JvrNDMUR_6vc12ztF8npLFdO54" 
PRICE_STARS = 5

# HTML шаблон (Фронтенд)
html_template = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ALOCU gift | NFT Wheel</title>
    <!-- ИСПРАВЛЕНО: Правильный путь к скрипту Telegram -->
    <script src="https://telegram.org"></script>
    <style>
        body {
            margin: 0; height: 100vh; display: flex; align-items: center; justify-content: center;
            background: radial-gradient(circle, #463305 0%, #000 100%);
            font-family: 'Segoe UI', sans-serif; overflow: hidden; color: white;
        }
        .main-container { text-align: center; position: relative; }
        h1 {
            color: #d4af37; font-size: 2.5rem; margin: 0 0 5px 0;
            text-transform: uppercase; letter-spacing: 3px;
            text-shadow: 0 0 15px rgba(212, 175, 55, 0.5);
        }
        .price-info { color: #ffd700; margin-bottom: 20px; font-weight: bold; font-size: 1.1rem; }

        .arrow {
            position: absolute; top: 105px; left: 50%; transform: translateX(-50%);
            width: 0; height: 0; border-left: 15px solid transparent;
            border-right: 15px solid transparent; border-top: 30px solid #ff4400;
            z-index: 10; filter: drop-shadow(0 0 5px red);
        }

        #wheel {
            width: 320px; height: 320px; border-radius: 50%;
            border: 8px solid #d4af37;
            background: conic-gradient(
                #d4af37 0deg 45deg, #222 45deg 90deg,
                #d4af37 90deg 135deg, #222 135deg 180deg,
                #444 180deg 225deg, #333 225deg 270deg,
                #444 270deg 315deg, #333 315deg 360deg
            );
            position: relative; 
            transition: transform 4s cubic-bezier(0.15, 0, 0.15, 1);
            box-shadow: 0 0 40px rgba(212, 175, 55, 0.3);
        }

        .label {
            position: absolute; width: 100%; height: 100%;
            text-align: center; color: white; font-weight: bold;
            text-transform: uppercase; font-size: 12px; pointer-events: none;
            padding-top: 15px; box-sizing: border-box;
        }

        .spin-btn {
            margin-top: 30px; padding: 15px 50px; font-size: 18px;
            background: linear-gradient(45deg, #d4af37, #f9e29c);
            color: black; border: none; cursor: pointer;
            font-weight: bold; border-radius: 50px; transition: 0.3s;
            box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4);
        }
        .spin-btn:disabled { opacity: 0.4; filter: grayscale(1); }
    </style>
</head>
<body>

<div class="main-container">
    <h1>ALOCU gift</h1>
    <div class="price-info">Цена: 5 ⭐️</div>

    <div class="arrow"></div>
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

    <button class="spin-btn" id="btn" onclick="handleSpinClick()">Крутить</button>
</div>

<script>
    const btn = document.getElementById('btn');
    const wheel = document.getElementById('wheel');
    const prizes = ["Bear", "Rocket", "Heart", "Rose", "Пусто", "Пусто", "Пусто", "Пусто"];
    let currentRotation = 0;

    const tg = window.Telegram ? window.Telegram.WebApp : null;

    if (tg) {
        tg.expand();
    }

    async function handleSpinClick() {
        if (!tg || !tg.initData) {
            alert("Ошибка: Откройте приложение внутри Telegram!");
            return;
        }

        btn.disabled = true;

        try {
            const response = await fetch('/create-stars-invoice', { method: 'POST' });
            const data = await response.json();

            if (data.ok && data.result) {
                tg.openInvoice(data.result, function(status) {
                    if (status === 'paid') {
                        runWheel();
                    } else {
                        tg.showAlert("Оплата не прошла.");
                        btn.disabled = false;
                    }
                });
            } else {
                tg.showAlert("Ошибка API: " + (data.description || "Не удалось создать счет"));
                btn.disabled = false;
            }
        } catch (e) {
            tg.showAlert("Ошибка сервера: " + e.message);
            btn.disabled = false;
        }
    }

    function runWheel() {
        const randomIndex = Math.floor(Math.random() * prizes.length);
        const extraRotation = 1800 + (360 - (randomIndex * 45));
        currentRotation += extraRotation;

        wheel.style.transition = 'transform 4s cubic-bezier(0.15, 0, 0.15, 1)';
        wheel.style.transform = `rotate(${currentRotation}deg)`;

        setTimeout(() => {
            const result = prizes[randomIndex];
            tg.showAlert(result === "Пусто" ? "Ничего не выпало!" : "ВЫ ВЫИГРАЛИ: " + result);
            btn.disabled = false;
        }, 4100);
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
    # ИСПРАВЛЕНО: Правильный URL для API Telegram
    url = f"https://telegram.org{BOT_TOKEN}/createInvoiceLink"

    payload = {
        "title": "Прокрут колеса",
        "description": "Попытка выбить NFT",
        "payload": "wheel_spin_payment",
        "provider_token": "", 
        "currency": "XTR", 
        "prices": [{"label": "Stars", "amount": PRICE_STARS}]
    }

    try:
        r = requests.post(url, json=payload)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

if __name__ == '__main__':
    # Для Render лучше оставить стандартный запуск или добавить os.environ.get('PORT')
    app.run(debug=True, port=8080)
