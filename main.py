import os, requests
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# ТВОЙ ТОКЕН (Проверь его еще раз в BotFather, чтобы не было пробелов)
BOT_TOKEN = "8723694663:AAEKRDMJ3JvrNDMUR_6vc12ztF8npLFdO54"

html_template = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>ALOCU gift | NFT Wheel</title>
    <script src="https://telegram.org"></script>
    <style>
        body {
            margin: 0; height: 100vh; display: flex; align-items: center; justify-content: center;
            background: radial-gradient(circle, #463305 0%, #000 100%);
            font-family: 'Segoe UI', sans-serif; overflow: hidden; color: white;
        }
        .main-container { text-align: center; position: relative; width: 100%; }
        h1 { color: #d4af37; font-size: 2.2rem; text-transform: uppercase; margin: 0 0 5px 0; text-shadow: 0 0 15px rgba(212, 175, 55, 0.5); }
        .price-info { color: #ffd700; margin-bottom: 20px; font-weight: bold; }
        .arrow {
            position: absolute; top: 105px; left: 50%; transform: translateX(-50%);
            width: 0; height: 0; border-left: 15px solid transparent;
            border-right: 15px solid transparent; border-top: 30px solid #ff4400;
            z-index: 10; filter: drop-shadow(0 0 5px red);
        }
        #wheel {
            width: 300px; height: 300px; border-radius: 50%; border: 8px solid #d4af37;
            margin: 0 auto; position: relative; transition: transform 4s cubic-bezier(0.15, 0, 0.15, 1);
            background: conic-gradient(#d4af37 0deg 45deg, #222 45deg 90deg, #d4af37 90deg 135deg, #222 135deg 180deg, #444 180deg 225deg, #333 225deg 270deg, #444 270deg 315deg, #333 315deg 360deg);
            box-shadow: 0 0 40px rgba(212, 175, 55, 0.3);
        }
        .label { position: absolute; width: 100%; height: 100%; text-align: center; font-weight: bold; font-size: 11px; padding-top: 15px; box-sizing: border-box; }
        .spin-btn { margin-top: 30px; padding: 15px 50px; font-size: 18px; background: linear-gradient(45deg, #d4af37, #f9e29c); color: black; border: none; border-radius: 50px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4); }
        .spin-btn:disabled { opacity: 0.4; }
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
    <button class="spin-btn" id="btn">КРУТИТЬ</button>
</div>

<script>
    // Инициализация
    var tg = window.Telegram.WebApp;
    tg.ready();
    tg.expand();

    var btn = document.getElementById('btn');
    var wheel = document.getElementById('wheel');
    var prizes = ["Bear", "Rocket", "Heart", "Rose", "Пусто", "Пусто", "Пусто", "Пусто"];
    var currentRotation = 0;

    // Сразу проверяем, работает ли кнопка (визуальный тест)
    btn.style.border = "2px solid green"; 

    btn.addEventListener('click', function() {
        btn.disabled = true;
        btn.innerText = "ЗАГРУЗКА...";

        // Используем полный путь (замени ТВОЕ-ИМЯ на реальное имя с Render)
        fetch('/create-invoice', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            if (data.ok && data.result) {
                btn.innerText = "ОПЛАТА...";
                tg.openInvoice(data.result, function(status) {
                    if (status === 'paid') {
                        runWheel();
                    } else {
                        tg.showAlert("Оплата отменена: " + status);
                        resetBtn();
                    }
                });
            } else {
                tg.showAlert("Ошибка API: " + (data.description || "Нет ответа"));
                resetBtn();
            }
        })
        .catch(function(error) {
            tg.showAlert("Ошибка сервера: " + error.message);
            resetBtn();
        });
    });

    function resetBtn() {
        btn.disabled = false;
        btn.innerText = "КРУТИТЬ";
    }

    function runWheel() {
        btn.innerText = "УДАЧИ!";
        var randomIndex = Math.floor(Math.random() * prizes.length);
        var extraRotation = 1800 + (360 - (randomIndex * 45));
        currentRotation += extraRotation;
        
        wheel.style.transform = "rotate(" + currentRotation + "deg)";
        
        setTimeout(function() {
            var result = prizes[randomIndex];
            tg.showAlert(result === "Пусто" ? "Ничего не выпало!" : "ВЫ ВЫИГРАЛИ: " + result);
            resetBtn();
        }, 4500);
    }
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html_template)

@app.route('/create-invoice', methods=['POST'])
def create_invoice():
    url = f"https://telegram.org{BOT_TOKEN}/createInvoiceLink"
    payload = {
        "title": "Удача NFT",
        "description": "5 Stars",
        "payload": "spin_pay",
        "provider_token": "", 
        "currency": "XTR", 
        "prices": [{"label": "Stars", "amount": 5}]
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"ok": False, "description": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
