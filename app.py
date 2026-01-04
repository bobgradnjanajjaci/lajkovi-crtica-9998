from flask import Flask, request, render_template_string
import requests
import time
import re

# ================= CONFIG =================

API_URL = "https://justanotherpanel.com/api/v2"
API_KEY = "c849788f60dd591e636c5d079b0a8d62"
SERVICE_ID = 9998

REQUEST_DELAY = 2.5  # sekunde između ordera (OBAVEZNO)

app = Flask(__name__)

# ================= HTML =================

HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>TikTok Comment Likes – JAP 9998</title>
  <style>
    body { background:#0f172a; color:#e5e7eb; font-family:system-ui; padding:40px }
    textarea { width:100%; height:220px; background:#020617; color:#e5e7eb; padding:12px }
    button { margin-top:12px; padding:10px 18px; font-weight:600 }
    pre { background:#020617; padding:12px; margin-top:16px; white-space:pre-wrap }
  </style>
</head>
<body>
  <h2>TikTok Comment Likes (Service 9998)</h2>
  <p>Format: <b>COMMENT_LINK QUANTITY</b></p>

  <form method="post">
    <textarea name="orders" placeholder="https://www.tiktok.com/@user/video/...?...cid=XXX 500"></textarea>
    <br>
    <button type="submit">Send</button>
  </form>

  {% if log %}
    <pre>{{ log }}</pre>
  {% endif %}
</body>
</html>
"""

# ================= HELPERS =================

def extract_username_from_link(link: str):
    """
    Izvlači @username iz TikTok comment linka
    """
    m = re.search(r"tiktok\\.com/@([^/]+)/", link)
    return m.group(1) if m else None


def send_order(comment_link: str, quantity: int):
    """
    Šalje order na JAP 9998 sa:
    - direct comment link
    - quantity
    - username (OBAVEZNO, ide u Additional data)
    """
    username = extract_username_from_link(comment_link)

    if not username:
        return {"error": "Username nije pronađen u linku"}

    payload = {
        "key": API_KEY,
        "action": "add",
        "service": SERVICE_ID,
        "link": comment_link,
        "quantity": quantity,
        "username": username  # 👈 KLJUČNO za JAP 9998
    }

    try:
        r = requests.post(API_URL, data=payload, timeout=20)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# ================= ROUTE =================

@app.route("/", methods=["GET", "POST"])
def index():
    log = []

    if request.method == "POST":
        raw = request.form.get("orders", "")
        lines = [l.strip() for l in raw.splitlines() if l.strip()]

        for line in lines:
            parts = line.split()

            # ✅ FORMAT: COMMENT_LINK QUANTITY
            if len(parts) != 2:
                log.append(f"[SKIP] Pogrešan format: {line}")
                continue

            comment_link = parts[0]
            qty_str = parts[1]

            try:
                quantity = int(qty_str)
                if quantity <= 0:
                    raise ValueError
            except Exception:
                log.append(f"[SKIP] Nevažeća količina: {line}")
                continue

            username = extract_username_from_link(comment_link)
            if not username:
                log.append(f"[SKIP] Username nije pronađen u linku: {comment_link}")
                continue

            log.append(f"[SEND] @{username} | {quantity} likes")
            resp = send_order(comment_link, quantity)
            log.append(str(resp))

            time.sleep(REQUEST_DELAY)

    return render_template_string(HTML, log="\n".join(log))

# ================= ENTRY =================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
