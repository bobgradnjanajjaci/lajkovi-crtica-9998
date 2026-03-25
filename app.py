from flask import Flask, request, render_template_string
from urllib.parse import urlparse
import requests  # dodano za slanje na API

app = Flask(__name__)

# ======================
# CONFIG
# ======================
PANEL_URL = "https://smmcoder.com/api/v2"
API_KEY = "e299815c2c2eef18a6632eebcaec1271"
SERVICE_ID = 8330  # TikTok Comment Likes (DIRECT COMMENT LINK)

# ======================
# HTML UI (malo poboljšana)
# ======================
HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>TikTok Order Parser</title>
  <style>
    body { background:#0f172a; color:#e5e7eb; font-family:Arial, sans-serif; padding:30px; line-height:1.6; }
    textarea { width:100%; height:280px; background:#020617; color:#e5e7eb; padding:15px; border:1px solid #334155; border-radius:8px; font-family:monospace; }
    button { margin-top:15px; padding:12px 24px; font-size:16px; font-weight:bold; background:#22c55e; color:#0f172a; border:none; border-radius:6px; cursor:pointer; }
    button:hover { background:#16a34a; }
    pre { background:#020617; padding:15px; margin-top:20px; border-radius:8px; white-space:pre-wrap; border:1px solid #334155; }
    .success { color:#86efac; }
    .error { color:#fda4af; }
  </style>
</head>
<body>
<h2>🚀 TikTok Video + Username + Quantity Parser</h2>
<form method="post">
  <textarea name="orders" placeholder="VIDEO_LINK USERNAME QUANTITY
https://www.tiktok.com/@user/video/123456 username123 400
https://vt.tiktok.com/abc123/ @drugiuser 250"></textarea>
  <br>
  <button type="submit">PARSE & PREPARE ORDERS</button>
</form>

{% if log %}
<pre>{{ log }}</pre>
{% endif %}
</body>
</html>
"""

# ======================
# VALIDATION
# ======================
def is_valid_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except:
        return False


# ======================
# SEND TO PANEL (funkcija koju možeš kasnije koristiti)
# ======================
def send_to_panel(video_url: str, username: str, quantity: int):
    payload = {
        "key": API_KEY,
        "action": "add",
        "service": SERVICE_ID,
        "link": video_url,           # ili f"{video_url} {username}" ako panel to traži
        "quantity": quantity,
        # Ako panel traži username posebno:
        # "username": username
    }
    
    try:
        response = requests.post(PANEL_URL, data=payload, timeout=15)
        result = response.json()
        
        if result.get("status") == "success":
            order_id = result.get("order", "N/A")
            return f"[SUCCESS] Order #{order_id} | {quantity} likes → {video_url}"
        else:
            error = result.get("error", "Unknown error")
            return f"[ERROR] {error} → {video_url}"
    except Exception as e:
        return f"[EXCEPTION] {str(e)} → {video_url}"


# ======================
# MAIN ROUTE
# ======================
@app.route("/", methods=["GET", "POST"])
def index():
    log_lines = []

    if request.method == "POST":
        raw = request.form.get("orders", "").strip()
        lines = [line.strip() for line in raw.splitlines() if line.strip()]

        if not lines:
            log_lines.append("[ERROR] Nema unesenih narudžbi!")
        else:
            log_lines.append(f"[INFO] Učitano {len(lines)} linija\n")

            for i, line in enumerate(lines, 1):
                parts = line.split(maxsplit=2)   # bolje splitanje (link može imati razmake u nekim slučajevima)
                
                if len(parts) != 3:
                    log_lines.append(f"[SKIP] #{i} Pogrešan format (treba 3 dijela) → {line}")
                    continue

                video_link, username, qty_raw = parts
                username = username.strip().lstrip('@')  # uklanja @ ako ga korisnik stavi

                # Validacije
                if not is_valid_url(video_link):
                    log_lines.append(f"[SKIP] #{i} Nevažeći URL → {video_link}")
                    continue

                if not username:
                    log_lines.append(f"[SKIP] #{i} Prazno korisničko ime → {line}")
                    continue

                try:
                    qty = int(qty_raw)
                    if qty < 1 or qty > 100000:   # razumna gornja granica
                        raise ValueError
                except ValueError:
                    log_lines.append(f"[SKIP] #{i} Nevažeća količina → {qty_raw}")
                    continue

                # Spremno za slanje
                log_lines.append(
                    f'<span class="success">[READY] #{i} video={video_link} | user=@{username} | qty={qty}</span>'
                )

                # === OVDJE MOŽEŠ ODMAH SLATI (za sada zakomentirano) ===
                # result = send_to_panel(video_link, username, qty)
                # log_lines.append(result)

    # Spoji sve u string za prikaz
    log_output = "\n".join(log_lines)

    return render_template_string(HTML, log=log_output)


if __name__ == "__main__":
    print("✅ Server pokrenut na http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
