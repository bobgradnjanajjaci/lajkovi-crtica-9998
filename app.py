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
        textarea { width:100%; height:320px; background:#020617; color:#e5e7eb; padding:15px; border:1px solid #475569; border-radius:8px; font-family:monospace; font-size:14px; }
        button { margin-top:15px; padding:14px 28px; font-size:17px; font-weight:bold; background:#22c55e; color:#0f172a; border:none; border-radius:6px; cursor:pointer; width: 100%; }
        button:hover { background:#16a34a; }
        pre { background:#020617; padding:16px; margin-top:20px; border-radius:8px; white-space:pre-wrap; line-height:1.6; border: 1px solid #1e293b; }
        .success { color:#86efac; }
        .error { color:#fda4af; }
        .info { color:#93c5fd; }
        h2 { color: #f8fafc; }
        p { color: #94a3b8; margin-bottom: 10px; }
    </style>
</head>
<body>
<div class="container">
    <h2>🚀 TikTok Comment Likes Sender</h2>
    <p>Format unosa: <strong>LINK_VIDEA USERNAME KOLIČINA</strong> (razmak između)</p>
    <form method="post">
        <textarea name="orders" placeholder="https://www.tiktok.com/@user/video/123456789 profil_koji_je_ostavio_komentar 100"></textarea>
        <br>
        <button type="submit">POŠALJI NARUDŽBE</button>
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
        "link": video_url,           # Link na video
        "quantity": quantity,        # Broj lajkova
        "username": username         # Username osobe čiji komentar lajkamo
    }

    try:
        r = requests.post(PANEL_URL, data=payload, timeout=20)
        response = r.json()

        if response.get("status") == "success":
            order_id = response.get("order", "N/A")
            return f'<span class="success">[SUCCESS] Order #{order_id} | {quantity} lajkova za @{username}</span>'
        else:
            error = response.get("error", str(response))
            return f'<span class="error">[ERROR] {error} | Profil: @{username}</span>'
    except Exception as e:
        return f'<span class="error">[EXCEPTION] {str(e)}</span>'

@app.route("/", methods=["GET", "POST"])
def index():
    log_lines = []

    if request.method == "POST":
        raw = request.form.get("orders", "").strip()

        if not raw:
            log_lines.append('<span class="error">[ERROR] Polje je prazno!</span>')
        else:
            lines = [line.strip() for line in raw.splitlines() if line.strip()]
            log_lines.append(f'<span class="info">[INFO] Obrađujem {len(lines)} linija...</span>\n')

            for i, line in enumerate(lines, 1):
                # Splitamo liniju na 3 dijela: LINK, USERNAME, QTY
                parts = line.split()
                
                if len(parts) < 3:
                    log_lines.append(f'<span class="error">[SKIP] #{i} Nedostaju podaci (potrebno: Link, Username, Količina)</span>')
                    continue

                video_link = parts[0]
                username = parts[1].strip().lstrip('@')
                qty_raw = parts[2]

                # Provjera linka
                if not is_valid_url(video_link):
                    log_lines.append(f'<span class="error">[SKIP] #{i} Neispravan URL → {video_link}</span>')
                    continue

                # Provjera količine
                try:
                    qty = int(qty_raw)
                    if qty < 1: raise ValueError
                except ValueError:
                    log_lines.append(f'<span class="error">[SKIP] #{i} Neispravna količina → {qty_raw}</span>')
                    continue

                # Slanje na API
                result = send_order(video_link, username, qty)
                log_lines.append(result)

    return render_template_string(HTML, log="\n".join(log_lines))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
