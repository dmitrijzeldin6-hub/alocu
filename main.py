import sqlite3
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)


# --- РАБОТА С БАЗОЙ ДАННЫХ ---
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Создаем таблицу: id пользователя, баланс и статус (0 - запрещено, 1 - разрешено)
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, balance INTEGER, allowed INTEGER)''')
    conn.commit()
    conn.close()


def get_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance, allowed FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def add_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, balance, allowed) VALUES (?, ?, ?)", (user_id, 0, 0))
    conn.commit()
    conn.close()


def update_user(user_id, balance, allowed):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = ?, allowed = ? WHERE user_id = ?", (balance, allowed, user_id))
    conn.commit()
    conn.close()


# Инициализируем БД при запуске
init_db()

# --- ФРОНТЕНД (Твой код с правками под API) ---
html_template = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>ALOCU gift | NFT Wheel</title>
    <script src="https://telegram.org">const tg = window.Telegram.WebApp;
    // Пытаемся получить ID пользователя из Телеграм, если нет - ставим 0 (для тестов)
    const userId = tg.initDataUnsafe?.user?.id || 0;
    const wheel = document.getElementById('wheel');
    const btn = document.getElementById('btn');
    const triesDisplay = document.getElementById('tries');

    const prizes = ["Bear", "Rocket", "Heart", "Rose", "Ничего", "Ничего", "Ничего", "Ничего"];
    let currentBalance = 0;

    // Функция обновления данных с сервера
    async function updateInfo() {
        if (!userId) return;
        try {
            const res = await fetch(`/check?id=${userId}`);
            const data = await res.json();
            currentBalance = data.balance;
            triesDisplay.innerText = currentBalance;
            
            // Если баланса нет или админ не разрешил - кнопка выключена
            btn.disabled = (!data.allowed || currentBalance <= 0);
        } catch (e) {
            console.error("Ошибка связи с сервером");
        }
    }

    async function startSpin() {
        btn.disabled = true; // Сразу выключаем кнопку
        
        // Запрос к бэкенду на списание попытки
        try {
            const res = await fetch(`/spin?id=${userId}`, {method: 'POST'});
            const data = await res.json();
            
            if (data.success) {
                // ВЫЧИСЛЯЕМ УГОЛ (Твоя оригинальная анимация)
                const randomIndex = Math.floor(Math.random() * prizes.length);
                const totalRotation = 3600 + (360 - (randomIndex * 45));
                
                wheel.style.transition = 'transform 4s cubic-bezier(0.15, 0, 0.15, 1)';
                wheel.style.transform = `rotate(${totalRotation}deg)`;

                // Ждем окончания вращения
                setTimeout(() => {
                    const result = prizes[randomIndex];
                    if(result === "Ничего") {
                        alert("Эх, ничего не выпало!");
                    } else {
                        alert("ПОЗДРАВЛЯЕМ! Ваш NFT: " + result);
                    }
                    
                    // Сбрасываем угол визуально (чтобы не копились тысячи градусов)
                    const finalAngle = totalRotation % 360;
                    wheel.style.transition = 'none';
                    wheel.style.transform = `rotate(${finalAngle}deg)`;
                    
                    updateInfo(); // Обновляем баланс после прокрута
                }, 4100);
            } else {
                alert("Доступ запрещен или закончились звёзды!");
                updateInfo();
            }
        } catch (e) {
            alert("Ошибка сети!");
            btn.disabled = false;
        }
    }

    // Запускаем проверку при входе
    updateInfo();
    </script>
    <style>
        body { margin: 0; height: 100vh; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, #463305 0%, #000 100%); font-family: 'Segoe UI', sans-serif; overflow: hidden; color: white; }
        .main-container { text-align: center; position: relative; }
        h1 { color: #d4af37; font-size: 3rem; margin: 0; text-transform: uppercase; letter-spacing: 5px; text-shadow: 0 0 15px rgba(212, 175, 55, 0.5); }
        .attempts-text { margin-bottom: 20px; font-size: 1.1rem; opacity: 0.8; }
        .arrow { position: absolute; top: 115px; left: 50%; transform: translateX(-50%); width: 0; height: 0; border-left: 15px solid transparent; border-right: 15px solid transparent; border-top: 35px solid #ff4400; z-index: 10; filter: drop-shadow(0 0 5px red); }
        #wheel { width: 350px; height: 350px; border-radius: 50%; border: 8px solid #d4af37; background: conic-gradient(#d4af37 0deg 45deg, #222 45deg 90deg, #d4af37 90deg 135deg, #222 135deg 180deg, #444 180deg 225deg, #333 225deg 270deg, #444 270deg 315deg, #333 315deg 360deg); position: relative; transition: transform 4s cubic-bezier(0.15, 0, 0.15, 1); box-shadow: 0 0 50px rgba(212, 175, 55, 0.4); }
        .label { position: absolute; width: 100%; height: 100%; text-align: center; font-weight: bold; text-transform: uppercase; font-size: 13px; pointer-events: none; }
        .spin-btn { margin-top: 30px; padding: 15px 50px; font-size: 20px; background: #d4af37; color: black; border: none; cursor: pointer; font-weight: bold; border-radius: 8px; transition: 0.3s; }
        .spin-btn:disabled { opacity: 0.3; cursor: not-allowed; }
    </style>
</head>
<body>
<div class="main-container">
    <h1>ALOCU gift</h1>
    <div class="attempts-text">Баланс: <span id="tries">0</span> ⭐</div>
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
    <button class="spin-btn" id="btn" onclick="startSpin()">Крутить</button>
</div>

<script>
    const tg = window.Telegram.WebApp;
    const userId = tg.initDataUnsafe?.user?.id || 0;
    const prizes = ["Bear", "Rocket", "Heart", "Rose", "Ничего", "Ничего", "Ничего", "Ничего"];
    let currentBalance = 0;

    async function updateInfo() {
        if (!userId) return;
        const res = await fetch(`/check?id=${userId}`);
        const data = await res.json();
        currentBalance = data.balance;
        document.getElementById('tries').innerText = currentBalance;
        if (!data.allowed || currentBalance <= 0) {
            document.getElementById('btn').disabled = true;
        } else {
            document.getElementById('btn').disabled = false;
        }
    }

    async function startSpin() {
        document.getElementById('btn').disabled = true;

        // Списываем 1 попытку на сервере
        const res = await fetch(`/spin?id=${userId}`, {method: 'POST'});
        const data = await res.json();

        if (data.success) {
            const randomIndex = Math.floor(Math.random() * prizes.length);
            const totalRotation = 3600 + (360 - (randomIndex * 45));
            document.getElementById('wheel').style.transform = `rotate(${totalRotation}deg)`;

            setTimeout(() => {
                alert(prizes[randomIndex] === "Ничего" ? "Ничего не выпало" : "Вы выиграли: " + prizes[randomIndex]);
                updateInfo();
            }, 4100);
        } else {
            alert("Доступ запрещен или нет звёзд!");
        }
    }

    updateInfo();
</script>
</body>
</html>
"""


# --- МАРШРУТЫ API ---

@app.route('/')
def home():
    return render_template_string(html_template)


@app.route('/check')
def check():
    user_id = request.args.get('id', type=int)
    user = get_user(user_id)
    if not user:
        add_user(user_id)
        return jsonify({"balance": 0, "allowed": False})
    return jsonify({"balance": user[0], "allowed": bool(user[1])})


@app.route('/spin', methods=['POST'])
def spin():
    user_id = request.args.get('id', type=int)
    user = get_user(user_id)
    if user and user[1] == 1 and user[0] > 0:
        new_balance = user[0] - 1
        update_user(user_id, new_balance, 1)
        return jsonify({"success": True})
    return jsonify({"success": False})


# Админка: https://onrender.com
@app.route('/give')
def give_access():
    user_id = request.args.get('id', type=int)
    stars = request.args.get('stars', type=int, default=1)
    update_user(user_id, stars, 1)
    return f"Готово! У пользователя {user_id} теперь {stars} звёзд и доступ открыт."


if __name__ == '__main__':
    app.run(debug=True, port=8080)
