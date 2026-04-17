import asyncio
import threading
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import LabeledPrice, PreCheckoutQuery, Message

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8723694663:AAEKRDMJ3JvrNDMUR_6vc12ztF8npLFdO54"  # Замени на свой из @BotFather
app = Flask(__name__)

# Инициализация aiogram
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# --- ЛОГИКА ОПЛАТЫ (AIOGRAM) ---

@dp.pre_checkout_query()
async def process_pre_checkout_query(query: PreCheckoutQuery):
    # Обязательное подтверждение, что мы готовы принять деньги
    await query.answer(ok=True)


@dp.message(F.successful_payment)
async def success_payment_handler(message: Message):
    # Здесь логика начисления попыток в базу данных
    print(f"Оплата получена! Юзер: {message.from_user.id}")
    await message.answer("Попытки начислены! Обновите Mini App.")


# Функция для запуска бота в фоне
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(dp.start_polling(bot))


# --- FLASK ROUTES ---

@app.route('/')
def home():
    # Я добавил только одну кнопку и скрипт вызова оплаты
    return html_template


@app.route('/create-invoice', methods=['POST'])
def create_invoice():
    data = request.json
    user_id = data.get('user_id')

    # Создаем ссылку на оплату Stars
    async def get_link():
        link = await bot.create_invoice_link(
            title="Дополнительные попытки",
            description="Купить 5 попыток для NFT колеса",
            payload=f"buy_tries_{user_id}",
            provider_token="",  # Для Stars пусто
            currency="XTR",
            prices=[LabeledPrice(label="5 попыток", amount=50)]  # 50 Stars
        )
        return link

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    invoice_link = loop.run_until_complete(get_link())

    return jsonify({"link": invoice_link})


# --- ТВОЙ HTML (С ДОБАВЛЕННОЙ КНОПКОЙ) ---
html_template = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>ALOCU gift | NFT Wheel</title>
    <script src="https://telegram.org"></script>
    <style>
        /* Твой оригинальный стиль */
        body { margin: 0; height: 100vh; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, #463305 0%, #000 100%); font-family: 'Segoe UI', sans-serif; overflow: hidden; }
        .main-container { text-align: center; position: relative; }
        h1 { color: #d4af37; font-size: 3rem; margin: 0 0 10px 0; text-transform: uppercase; letter-spacing: 5px; text-shadow: 0 0 15px rgba(212, 175, 55, 0.5); }
        .attempts-text { color: #fff; margin-bottom: 20px; font-size: 1.1rem; opacity: 0.8; }
        .arrow { position: absolute; top: 115px; left: 50%; transform: translateX(-50%); width: 0; height: 0; border-left: 15px solid transparent; border-right: 15px solid transparent; border-top: 35px solid #ff4400; z-index: 10; filter: drop-shadow(0 0 5px red); }
        #wheel { width: 350px; height: 350px; border-radius: 50%; border: 8px solid #d4af37; background: conic-gradient(#d4af37 0deg 45deg, #222 45deg 90deg, #d4af37 90deg 135deg, #222 135deg 180deg, #444 180deg 225deg, #333 225deg 270deg, #444 270deg 315deg, #333 315deg 360deg); position: relative; transition: transform 4s cubic-bezier(0.15, 0, 0.15, 1); box-shadow: 0 0 50px rgba(212, 175, 55, 0.4); }
        .label { position: absolute; width: 100%; height: 100%; text-align: center; color: white; font-weight: bold; text-transform: uppercase; font-size: 13px; pointer-events: none; }
        .spin-btn { margin-top: 30px; padding: 15px 50px; font-size: 20px; background: #d4af37; color: black; border: none; cursor: pointer; font-weight: bold; border-radius: 8px; transition: 0.3s; }
        .buy-btn { margin-top: 10px; background: transparent; color: #d4af37; border: 1px solid #d4af37; padding: 5px 20px; border-radius: 5px; cursor: pointer; display: block; width: 100%; }
    </style>
</head>
<body>
<div class="main-container">
    <h1>ALOCU gift</h1>
    <div class="attempts-text">Попыток: <span id="tries">3</span></div>
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
    <button class="spin-btn" id="btn" onclick="spin()">Крутить</button>
    <button class="buy-btn" onclick="buyTries()">+ Купить попытки</button>
</div>

<script>
    const tg = window.Telegram.WebApp;
    tg.expand();

    const wheel = document.getElementById('wheel');
    const btn = document.getElementById('btn');
    const triesDisplay = document.getElementById('tries');
    const prizes = ["Bear", "Rocket", "Heart", "Rose", "Ничего", "Ничего", "Ничего", "Ничего"];
    let attempts = 3;

    async function buyTries() {
        const userId = tg.initDataUnsafe.user?.id || 0;
        const response = await fetch('/create-invoice', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ user_id: userId })
        });
        const data = await response.json();

        if (data.link) {
            tg.openInvoice(data.link, function(status) {
                if (status === 'paid') {
                    attempts += 5;
                    triesDisplay.innerText = attempts;
                    btn.disabled = false;
                    alert("Оплата прошла! Вам добавлено 5 попыток.");
                }
            });
        }
    }

    function spin() {
        if (attempts <= 0) return;
        btn.disabled = true;
        attempts--;
        triesDisplay.innerText = attempts;
        const randomIndex = Math.floor(Math.random() * prizes.length);
        const totalRotation = 3600 + (360 - (randomIndex * 45));
        wheel.style.transition = 'transform 4s cubic-bezier(0.15, 0, 0.15, 1)';
        wheel.style.transform = `rotate(${totalRotation}deg)`;

        setTimeout(() => {
            const result = prizes[randomIndex];
            alert(result === "Ничего" ? "Эх, ничего!" : "ПОЗДРАВЛЯЕМ! NFT: " + result);
            if (attempts > 0) {
                btn.disabled = false;
                wheel.style.transition = 'none';
                wheel.style.transform = `rotate(${totalRotation % 360}deg)`;
            }
        }, 4100);
    }
</script>
</body>
</html>
"""

if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    threading.Thread(target=run_bot, daemon=True).start()
    # Запускаем Flask
    app.run(debug=True, port=8080)
