from flask import Flask, request, render_template_string
from urllib.parse import urlparse
import requests

app = Flask(__name__)

# ======================
# CONFIG
# ======================
PANEL_URL = "https://smmcoder.com/api/v2"
API_KEY = "e299815c2c2eef18a6632eebcaec1271"
SERVICE_ID = 8330  # TikTok Comment Likes (DIRECT COMMENT LINK)

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
    textarea { width:100%; height:320px; background:#020617; color:#e5e7eb; padding:15px; border:1px solid #475569; border-radius:8px; font-family:monospace; }
    button { margin-top:15px; padding:14px 28px; font-size:17px; font-weight:bold; background:#22c55e; color:#0f172a; border:none; border-radius:6px; cursor:pointer; }
    button:hover { background:#16a34a; }
    pre { background:#020617; padding:16px; margin-top:20px; border-radius:8px; white-space:pre-wrap; line-height:1.6; }
    .success { color:#86efac; }
    .error { color:#fda4af; }
    .info { color:#93c5fd; }
  </style>
</head>
<body>
<h2>🚀 TikTok Comment Likes Sender - Ispravljeno</h2>
<form method="post">
  <textarea name="orders" placeholder="VIDEO_LINK USERNAME QUANTITY
https://www.tiktok.com/@committee.of.affairs/video/76198528196796 arthurlcallahan67 100
https://vt.tiktok.com/xyz123/ user123 250"></textarea>
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
    payload = {
        "key": API_KEY,
        "action": "add",
        "service": SERVICE_ID,
        "link": video_url,        # ← SAMO ČISTI VIDEO LINK (najvažnije!)
        "quantity": quantity
        # username se NE šalje u "link" polje za ovaj service
    }

    try:
        r = requests.post(PANEL_URL, data=payload, timeout=20)
        response = r.json()

        if response.get("status") == "success":
            order_id = response.get("order", "N/A")
            return f'<span class="success">[SUCCESS] Order #{order_id} | {quantity}x likes → @{username}</span>'
        else:
            error = response.get("error", response.get("message", str(response)))
            return f'<span class="error">[ERROR] {error} | @{username}</span>'

    except requests.exceptions.RequestException as e:
        return f'<span class="error">[CONNECTION ERROR] {str(e)}</span>'
    except Exception as e:
        return f'<span class="error">[EXCEPTION] {str(e)}</span>'


@app.route("/", methods=["GET", "POST"])
def index():
    log_lines = []

    if request.method == "POST":
        raw = request.form.get("orders", "").strip()

        if not raw:
            log_lines.append('<span class="error">[ERROR] Nema unosa!</span>')
        else:
            lines = [line.strip() for line in raw.splitlines() if line.strip()]
            log_lines.append(f'<span class="info">[INFO] Obrada {len(lines)} narudžbi...</span>\n')

            for i, line in enumerate(lines, 1):
                # Split na maksimalno 3 dijela
                parts = line.split(maxsplit=2)
                if len(parts) != 3:
                    log_lines.append(f'[SKIP] #{i} Pogrešan format (treba: link username količina)')
                    continue

                video_link, username, qty_raw = parts
                username = username.strip().lstrip('@')

                if not is_valid_url(video_link):
                    log_lines.append(f'[SKIP] #{i} Neispravan video link → {video_link}')
                    continue

                try:
                    qty = int(qty_raw)
                    if qty < 1 or qty > 50000:
                        raise ValueError("Količina izvan opsega")
                except:
                    log_lines.append(f'[SKIP] #{i} Neispravna količina → {qty_raw}')
                    continue

                # SLANJE NA PANEL
                result = send_order(video_url=video_link, username=username, quantity=qty)
                log_lines.append(result)

    return render_template_string(HTML, log="\n".join(log_lines))


if __name__ == "__main__":
    print("✅ Server pokrenut na http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
