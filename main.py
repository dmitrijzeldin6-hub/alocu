import threading
from flask import Flask, request, jsonify
import telebot
from telebot import types

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8723694663:AAEKRDMJ3JvrNDMUR_6vc12ztF8npLFdO54"
app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN)


# --- ТВОИ ФУНКЦИИ (Telebot) ---

def create_invoice(chat_id, user_id, amount):
    prices = [types.LabeledPrice(label=f"{amount} запросов", amount=amount)]

    bot.send_invoice(
        chat_id=chat_id,
        title=f"Покупка {amount} запросов",
        description=f"Пополнение баланса на {amount} запросов",
        invoice_payload=f"requests_{amount}_{user_id}",
        provider_token="",
        currency="XTR",
        prices=prices
    )


@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@bot.message_handler(content_types=['successful_payment'])
def process_successful_payment(message):
    payment_info = message.successful_payment
    payload_parts = payment_info.invoice_payload.split('_')
    amount = int(payload_parts[1])
    user_id = int(payload_parts[2])

    # Тут твоя логика БД (закомментил, чтобы не падало)
    # db_manager.add_requests(user_id, amount)

    bot.send_message(message.chat.id, f"✅ Оплата прошла успешно! {amount} попыток добавлено.")


# --- FLASK РОУТЫ ---

@app.route('/')
def home():
    return html_template


@app.route('/pay', methods=['POST'])
def pay():
    data = request.json
    user_id = data.get('user_id')
    # Вызываем твою функцию создания инвойса
    # В Mini App chat_id обычно совпадает с user_id
    try:
        create_invoice(user_id, user_id, 50)  # Например, 50 звезд
        return jsonify({"status": "sent"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# --- HTML (Обновленная кнопка) ---
html_template = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <script src="https://telegram.org"></script>
    <style>
        /* Твой стиль из прошлых сообщений */
        body { margin: 0; height: 100vh; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, #463305 0%, #000 100%); font-family: 'Segoe UI', sans-serif; }
        .main-container { text-align: center; }
        #wheel { width: 300px; height: 300px; border: 5px solid #d4af37; border-radius: 50%; transition: 4s; }
        .spin-btn { padding: 10px 30px; background: #d4af37; border: none; cursor: pointer; margin-top: 20px; }
    </style>
</head>
<body>
<div class="main-container">
    <h1 style="color: #d4af37;">ALOCU GIFT</h1>
    <div id="wheel"></div>
    <button class="spin-btn" onclick="spin()">Крутить</button>
    <button onclick="buy()" style="display:block; width:100%; margin-top:10px; color: gold; background: none; border: 1px solid gold; cursor:pointer;">Купить попытки</button>
</div>

<script>
    const tg = window.Telegram.WebApp;
    tg.ready();

    async function buy() {
        const userId = tg.initDataUnsafe.user?.id;
        if (!userId) {
            alert("Запустите через бота!");
            return;
        }

        // Запрос к Flask, чтобы бот кинул инвойс в чат
        await fetch('/pay', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ user_id: userId })
        });

        alert("Счет на оплату отправлен вам в личные сообщения с ботом!");
        tg.close(); // Закрываем приложение, чтобы юзер увидел инвойс в чате
    }

    function spin() { alert("Крутим..."); }
</script>
</body>
</html>
"""

if __name__ == '__main__':
    # Запуск бота в потоке
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    app.run(port=8080)
