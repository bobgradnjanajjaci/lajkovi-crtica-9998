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
# HTML (poboljšana)
# ======================
HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>TikTok Order Sender</title>
  <style>
    body { background:#0f172a; color:#e5e7eb; font-family:Arial, sans-serif; padding:30px; }
    textarea { width:100%; height:300px; background:#020617; color:#e5e7eb; padding:15px; border-radius:8px; font-family:monospace; }
    button { margin-top:15px; padding:14px 28px; font-size:17px; font-weight:bold; background:#22c55e; color:#111827; border:none; border-radius:6px; cursor:pointer; }
    button:hover { background:#16a34a; }
    pre { background:#020617; padding:15px; margin-top:20px; border-radius:8px; white-space:pre-wrap; line-height:1.5; }
    .success { color:#86efac; }
    .error   { color:#fda4af; }
    .info    { color:#93c5fd; }
  </style>
</head>
<body>
<h2>🚀 TikTok Comment Likes Sender (Direct to Panel)</h2>
<form method="post">
  <textarea name="orders" placeholder="VIDEO_LINK USERNAME QUANTITY
https://www.tiktok.com/@user/video/123456789 username123 500
https://vt.tiktok.com/ABC123/ @drugiuser 300"></textarea>
  <br>
  <button type="submit">PARSE & SEND TO PANEL</button>
</form>

{% if log %}
<pre>{{ log }}</pre>
{% endif %}
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
    # Većina SMM panela za TikTok comment likes traži link u ovom formatu:
    link = f"{video_url} {username}"   # ili samo video_url – testiraj oba

    payload = {
        "key": API_KEY,
        "action": "add",
        "service": SERVICE_ID,
        "link": link,
        "quantity": quantity
    }

    try:
        r = requests.post(PANEL_URL, data=payload, timeout=20)
        response = r.json()

        if response.get("status") == "success":
            order_id = response.get("order", "N/A")
            return f'[SUCCESS] Order #{order_id} | {quantity} likes | @{username}'
        else:
            error_msg = response.get("error", r.text[:200])
            return f'[ERROR] {error_msg} | @{username}'

    except requests.exceptions.RequestException as e:
        return f'[CONNECTION ERROR] {str(e)}'
    except Exception as e:
        return f'[EXCEPTION] {str(e)}'


# ======================
# ROUTE
# ======================
@app.route("/", methods=["GET", "POST"])
def index():
    log_lines = []

    if request.method == "POST":
        raw_text = request.form.get("orders", "").strip()

        if not raw_text:
            log_lines.append('<span class="error">[ERROR] Nema unosa!</span>')
        else:
            lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
            log_lines.append(f'<span class="info">[INFO] Pronađeno {len(lines)} narudžbi. Šaljem na panel...</span>\n')

            for i, line in enumerate(lines, 1):
                parts = line.split(maxsplit=2)
                if len(parts) != 3:
                    log_lines.append(f'[SKIP] #{i} Pogrešan format → {line}')
                    continue

                video_link, username, qty_raw = parts
                username = username.strip().lstrip('@')

                if not is_valid_url(video_link):
                    log_lines.append(f'[SKIP] #{i} Neispravan URL → {video_link}')
                    continue

                try:
                    qty = int(qty_raw)
                    if qty < 1:
                        raise ValueError
                except:
                    log_lines.append(f'[SKIP] #{i} Neispravna količina → {qty_raw}')
                    continue

                # === SLANJE NA PANEL ===
                result = send_order(video_link, username, qty)
                log_lines.append(result)

    return render_template_string(HTML, log="\n".join(log_lines))


if __name__ == "__main__":
    print("✅ TikTok Sender je pokrenut → http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
