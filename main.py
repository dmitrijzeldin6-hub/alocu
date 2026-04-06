import os, requests
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

BOT_TOKEN = "8723694663:AAEKRDMJ3JvrNDMUR_6vc12ztF8npLFdO54"

@app.route('/')
def home():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://telegram.org"></script>
    <style>
        body { background: #000; color: #d4af37; font-family: sans-serif; text-align: center; margin: 0; padding: 20px; }
        #wheel { 
            width: 250px; height: 250px; border: 5px solid #d4af37; border-radius: 50%; 
            margin: 20px auto; transition: transform 4s cubic-bezier(0.1, 0, 0.1, 1);
            background: conic-gradient(#d4af37 0% 50%, #222 50% 100%);
        }
        .btn { background: #d4af37; color: #000; padding: 15px 30px; border: none; border-radius: 10px; font-weight: bold; font-size: 18px; cursor: pointer; }
        .btn:disabled { opacity: 0.3; }
        #log { font-size: 10px; color: gray; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>ALOCU NFT</h1>
    <div id="wheel"></div>
    <button class="btn" id="spinBtn">КРУТИТЬ (5 ⭐️)</button>
    <div id="log">Status: Ready</div>

    <script>
        const tg = window.Telegram.WebApp;
        const btn = document.getElementById('spinBtn');
        const log = document.getElementById('log');
        let rotation = 0;

        tg.ready();
        tg.expand();

        btn.onclick = async () => {
            btn.disabled = true;
            log.innerText = "Status: Requesting invoice...";
            
            try {
                const res = await fetch('/pay', { method: 'POST' });
                const data = await res.json();
                
                if (data.ok && data.result) {
                    log.innerText = "Status: Opening invoice...";
                    tg.openInvoice(data.result, (status) => {
                        if (status === 'paid') {
                            log.innerText = "Status: PAID! Spinning...";
                            rotation += 1800 + Math.random() * 360;
                            document.getElementById('wheel').style.transform = `rotate(${rotation}deg)`;
                            setTimeout(() => { 
                                tg.showAlert("NFT Выигран!"); 
                                btn.disabled = false; 
                            }, 4500);
                        } else {
                            tg.showAlert("Оплата не прошла: " + status);
                            btn.disabled = false;
                        }
                    });
                } else {
                    log.innerText = "Error: " + JSON.stringify(data);
                    btn.disabled = false;
                }
            } catch (e) {
                log.innerText = "Fetch Error: " + e.message;
                btn.disabled = false;
            }
        };
    </script>
</body>
</html>
""")

@app.route('/pay', methods=['POST'])
def pay():
    url = f"https://telegram.org{BOT_TOKEN}/createInvoiceLink"
    payload = {
        "title": "NFT Spin", "description": "1 Spin", "payload": "p1",
        "provider_token": "", "currency": "XTR",
        "prices": [{"label": "Stars", "amount": 5}]
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"ok": False, "description": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
