from flask import Flask, request, render_template_string
import requests
import time

API_URL = "https://justanotherpanel.com/api/v2"
API_KEY = "c849788f60dd591e636c5d079b0a8d62"
SERVICE_ID = 9998
DELAY = 2.5

app = Flask(__name__)

HTML = """
<h3>TikTok Comment Likes – JAP 9998</h3>
<p>Format: <b>COMMENT_LINK COMMENT_USERNAME QUANTITY</b></p>
<form method="post">
<textarea name="orders" style="width:100%;height:220px;"></textarea><br>
<button type="submit">Send</button>
</form>
<pre>{{log}}</pre>
"""

def send_order(link, username, quantity):
    payload = {
        "key": API_KEY,
        "action": "add",
        "service": SERVICE_ID,
        "link": link,
        "quantity": quantity,
        "username": username
    }
    r = requests.post(API_URL, data=payload, timeout=20)
    return r.json()

@app.route("/", methods=["GET","POST"])
def index():
    log = []
    if request.method == "POST":
        lines = request.form.get("orders","").splitlines()
        for line in lines:
            parts = line.strip().split()
            if len(parts) != 3:
                log.append(f"[SKIP] Format: LINK USERNAME QTY → {line}")
                continue

            link, username, qty = parts
            try:
                qty = int(qty)
                if qty <= 0:
                    raise ValueError
            except:
                log.append(f"[SKIP] Nevažeća količina → {line}")
                continue

            log.append(f"[SEND] @{username} x{qty}")
            resp = send_order(link, username, qty)
            log.append(str(resp))
            time.sleep(DELAY)

    return render_template_string(HTML, log="\n".join(log))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
