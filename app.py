from flask import Flask, request, render_template_string
from urllib.parse import urlparse
import requests

app = Flask(__name__)

# ======================
# CONFIG
# ======================
PANEL_URL = "https://smmcoder.com/api/v2"
API_KEY = "8343861aaa02d131406e07fbf55c6c10"
SERVICE_ID = 8330  # TikTok Comment Likes (Slanje putem Username-a)

# ======================
# HTML
# ======================
HTML = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>TikTok Comment Likes Fast Sender</title>
    <style>
        body { background:#0f172a; color:#e5e7eb; font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding:30px; }
        .container { max-width: 900px; margin: 0 auto; }
        textarea { width:100%; height:350px; background:#020617; color:#86efac; padding:15px; border:1px solid #334155; border-radius:8px; font-family:monospace; font-size: 14px; outline: none; }
        textarea:focus { border-color: #22c55e; }
        button { margin-top:15px; padding:15px 30px; font-size:16px; font-weight:bold; background:#22c55e; color:#0f172a; border:none; border-radius:6px; cursor:pointer; width: 100%; transition: 0.3s; }
        button:hover { background:#16a34a; transform: translateY(-2px); }
        pre { background:#020617; padding:16px; margin-top:20px; border-radius:8px; white-space:pre-wrap; line-height:1.6; border-left: 4px solid #3b82f6; }
        .success { color:#4ade80; font-weight: bold; }
        .error { color:#f87171; font-weight: bold; }
        .info { color:#60a5fa; }
        h2 { margin-bottom: 5px; }
        p { color: #94a3b8; margin-bottom: 20px; }
    </style>
</head>
<body>
<div class="container">
    <h2>🚀 TikTok Comment Likes (Triple Mode)</h2>
    <p>Format unosa: <code>LINK_VIDEA USERNAME KOLIČINA</code></p>
    
    <form method="post">
        <textarea name="orders" placeholder="https://www.tiktok.com/@user/video/123456... nails_vivian 100"></textarea>
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
        "link": video_url,      # Video link
        "username": username,   # Dodatni podatak: Username komentara
        "quantity": quantity
    }

    try:
        r = requests.post(PANEL_URL, data=payload, timeout=20)
        response = r.json()

        # Provjera prema tvom API-ju (klasik ili 'order' key)
        if "order" in response:
            order_id = response.get("order")
            return f'<span class="success">[OK] Order #{order_id} | {quantity} likes → @{username}</span>'
        elif response.get("status") == "success":
            order_id = response.get("order", "N/A")
            return f'<span class="success">[OK] Order #{order_id} | {quantity} likes → @{username}</span>'
        else:
            error = response.get("error", str(response))
            return f'<span class="error">[ERROR] {error} (@{username})</span>'

    except Exception as e:
        return f'<span class="error">[EXCEPTION] {str(e)}</span>'

@app.route("/", methods=["GET", "POST"])
def index():
    log_lines = []

    if request.method == "POST":
        raw = request.form.get("orders", "").strip()

        if not raw:
            log_lines.append('<span class="error">[SISTEM] Polje je prazno!</span>')
        else:
            lines = [line.strip() for line in raw.splitlines() if line.strip()]
            log_lines.append(f'<span class="info">[SISTEM] Procesuiram {len(lines)} narudžbi...</span>\n')

            for i, line in enumerate(lines, 1):
                # Splitamo na 3 dijela: LINK, USERNAME, KOLIČINA
                parts = line.split() 
                
                if len(parts) < 3:
                    log_lines.append(f'<span class="error">[SKIP] #{i} Nedostaju podaci (Link Username Kol) → {line}</span>')
                    continue

                video_link = parts[0]
                username = parts[1].strip().lstrip('@')
                qty_raw = parts[2]

                if not is_valid_url(video_link):
                    log_lines.append(f'<span class="error">[SKIP] #{i} Neispravan URL → {video_link}</span>')
                    continue

                try:
                    qty = int(qty_raw)
                    if qty < 1: raise ValueError
                except:
                    log_lines.append(f'<span class="error">[SKIP] #{i} Neispravna količina → {qty_raw}</span>')
                    continue

                # Slanje na panel
                result = send_order(video_link, username, qty)
                log_lines.append(result)

    return render_template_string(HTML, log="\n".join(log_lines))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
