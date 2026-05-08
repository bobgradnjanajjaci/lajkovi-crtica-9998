from flask import Flask, request, render_template_string
from urllib.parse import urlparse
import requests

app = Flask(__name__)

# ======================
# CONFIG
# ======================
PANEL_URL = "https://smmcoder.com/api/v2"
API_KEY = "e299815c2c2eef18a6632eebcaec1271"
SERVICE_ID = 8330  # TikTok Comment Likes

# ======================
# HTML
# ======================
HTML = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>TikTok Comment Likes Sender</title>
    <style>
        body { background:#0f172a; color:#e5e7eb; font-family:Arial, sans-serif; padding:30px; }
        .container { max-width: 900px; margin: auto; }
        textarea { width:100%; height:320px; background:#020617; color:#e5e7eb; padding:15px; border:1px solid #475569; border-radius:8px; font-family:monospace; font-size:14px; border: 1px solid #334155; }
        button { margin-top:15px; padding:14px 28px; font-size:17px; font-weight:bold; background:#22c55e; color:#0f172a; border:none; border-radius:6px; cursor:pointer; width: 100%; transition: 0.3s; }
        button:hover { background:#16a34a; }
        pre { background:#020617; padding:16px; margin-top:20px; border-radius:8px; white-space:pre-wrap; line-height:1.6; border: 1px solid #1e293b; font-size: 13px; }
        .success { color:#4ade80; font-weight: bold; }
        .error { color:#fb7185; font-weight: bold; }
        .info { color:#60a5fa; font-weight: bold; }
        h2 { color: #f8fafc; margin-bottom: 5px; }
        p { color: #94a3b8; margin-bottom: 20px; }
    </style>
</head>
<body>
<div class="container">
    <h2>🚀 TikTok Comment Likes Sender</h2>
    <p>Redoslijed unosa: <strong>LINK_VIDEA USERNAME KOLIČINA</strong> (razmak između njih)</p>
    <form method="post">
        <textarea name="orders" placeholder="https://www.tiktok.com/@user/video/123456789 nails_vivian 100"></textarea>
        <br>
        <button type="submit">POŠALJI NA PANEL</button>
    </form>

    {% if log %}
    <pre>{{ log|safe }}</pre>
    {% endif %}
</div>
</body>
</html>
"""

def is_valid_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except:
        return False

def send_order(video_url: str, username: str, quantity: int):
    payload = {
        "key": API_KEY,
        "action": "add",
        "service": SERVICE_ID,
        "link": video_url,
        "quantity": quantity,
        "username": username
    }

    try:
        # Slanje zahtjeva prema SMM panelu
        r = requests.post(PANEL_URL, data=payload, timeout=20)
        response = r.json()

        # POPRAVAK: Provjeravamo postoji li 'order' ključ u odgovoru
        if "order" in response:
            order_id = response.get("order")
            return f'<span class="success">[SUCCESS] Order #{order_id} | {quantity} lajkova poslano na @{username}</span>'
        
        # Ako API vrati grešku
        elif "error" in response:
            return f'<span class="error">[ERROR] {response["error"]} | Profil: @{username}</span>'
        
        # Bilo koji drugi neočekivani odgovor
        else:
            return f'<span class="error">[UNKNOWN] {str(response)} | @{username}</span>'

    except Exception as e:
        return f'<span class="error">[EXCEPTION] Problem s povezivanjem: {str(e)}</span>'

@app.route("/", methods=["GET", "POST"])
def index():
    log_lines = []

    if request.method == "POST":
        raw = request.form.get("orders", "").strip()

        if not raw:
            log_lines.append('<span class="error">[SISTEM] Polje je prazno!</span>')
        else:
            lines = [line.strip() for line in raw.splitlines() if line.strip()]
            log_lines.append(f'<span class="info">[INFO] Pokrećem obradu za {len(lines)} narudžbi...</span>\n')

            for i, line in enumerate(lines, 1):
                # Dijeljenje linije na dijelove (razmak je separator)
                parts = line.split()
                
                if len(parts) < 3:
                    log_lines.append(f'<span class="error">[SKIP] #{i} Krivi format linije (fali podatak)</span>')
                    continue

                # Dodjela varijabli po tvom zahtjevu: LINK -> USERNAME -> QUANTITY
                video_link = parts[0]
                username = parts[1].strip().lstrip('@')
                qty_raw = parts[2]

                # Provjera je li URL ispravan
                if not is_valid_url(video_link):
                    log_lines.append(f'<span class="error">[SKIP] #{i} Neispravan URL → {video_link}</span>')
                    continue

                # Provjera je li količina broj
                try:
                    qty = int(qty_raw)
                    if qty < 1: raise ValueError
                except ValueError:
                    log_lines.append(f'<span class="error">[SKIP] #{i} Neispravna količina → {qty_raw}</span>')
                    continue

                # Pozivanje funkcije za slanje
                result = send_order(video_link, username, qty)
                log_lines.append(result)

    # Spajamo logove u jedan string i šaljemo u HTML
    return render_template_string(HTML, log="\n".join(log_lines))

if __name__ == "__main__":
    print("✅ Skripta je pokrenuta na http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
