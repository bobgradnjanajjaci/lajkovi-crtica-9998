from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

# ======================
# JAP CONFIG
# ======================
PANEL_URL = "https://smmcoder.com/api/v2"
API_KEY = "e299815c2c2eef18a6632eebcaec1271"
SERVICE_ID = 8330  # TikTok Comment Likes (DIRECT COMMENT LINK)

# ======================
# HTML UI
# ======================
HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>TikTok Comment Likes – JAP 9998</title>
  <style>
    body { background:#0f172a; color:#e5e7eb; font-family:Arial; padding:30px }
    textarea { width:100%; height:220px; background:#020617; color:#e5e7eb; padding:12px }
    button { margin-top:12px; padding:10px 18px; font-weight:bold }
    pre { background:#020617; padding:12px; margin-top:15px }
  </style>
</head>
<body>

<h2>🚀 TikTok Comment Likes (Service 9998)</h2>

<form method="post">
<textarea name="orders" placeholder="COMMENT_LINK QUANTITY
https://www.tiktok.com/@user/video/123?cid=XXXX 400"></textarea>
<br>
<button type="submit">SEND</button>
</form>

{% if log %}
<pre>{{ log }}</pre>
{% endif %}

</body>
</html>
"""

# ======================
# CORE SENDER
# ======================
def send_order(comment_link: str, quantity: int):
    payload = {
        "key": API_KEY,
        "action": "add",
        "service": SERVICE_ID,
        "link": comment_link,
        "quantity": quantity
    }

    try:
        r = requests.post(PANEL_URL, data=payload, timeout=20)
        data = r.json()
        if "order" in data:
            return True, f"ORDER OK → {data['order']}"
        return False, f"ERROR → {data}"
    except Exception as e:
        return False, f"EXCEPTION → {e}"

# ======================
# ROUTE
# ======================
@app.route("/", methods=["GET", "POST"])
def index():
    log = []

    if request.method == "POST":
        raw = request.form.get("orders", "")
        lines = [l.strip() for l in raw.splitlines() if l.strip()]

        for line in lines:
            parts = line.split()
            if len(parts) != 2:
                log.append(f"[SKIP] Format mora biti: LINK QTY → {line}")
                continue

            link, qty = parts

            try:
                qty = int(qty)
                if qty < 1:
                    raise ValueError
            except:
                log.append(f"[SKIP] Neispravna količina → {line}")
                continue

            ok, msg = send_order(link, qty)
            status = "OK" if ok else "FAIL"
            log.append(f"[{status}] {link} x{qty} → {msg}")

    return render_template_string(HTML, log="\n".join(log))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
