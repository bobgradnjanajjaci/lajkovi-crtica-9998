from flask import Flask, request, render_template_string
from urllib.parse import urlparse

app = Flask(__name__)

# ======================
# JAP CONFIG (STRUCTURE ONLY)
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
  <title>Video Order Parser</title>
  <style>
    body { background:#0f172a; color:#e5e7eb; font-family:Arial; padding:30px }
    textarea { width:100%; height:220px; background:#020617; color:#e5e7eb; padding:12px }
    button { margin-top:12px; padding:10px 18px; font-weight:bold }
    pre { background:#020617; padding:12px; margin-top:15px; white-space:pre-wrap }
  </style>
</head>
<body>

<h2>🚀 TikTok Input Parser (VIDEO + USERNAME + QTY)</h2>

<form method="post">
<textarea name="orders" placeholder="VIDEO_LINK USERNAME QUANTITY
https://www.tiktok.com/@user/video/123456 username123 400"></textarea>
<br>
<button type="submit">PARSE</button>
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

            if len(parts) != 3:
                log.append(f"[SKIP] Format: VIDEO_LINK USERNAME QUANTITY → {line}")
                continue

            video_link, username, qty_raw = parts

            # URL check
            if not is_valid_url(video_link):
                log.append(f"[SKIP] Invalid URL → {video_link}")
                continue

            # Username check
            if not username.strip():
                log.append(f"[SKIP] Invalid username → {line}")
                continue

            # Quantity check
            try:
                qty = int(qty_raw)
                if qty < 1:
                    raise ValueError
            except:
                log.append(f"[SKIP] Invalid quantity → {qty_raw}")
                continue

            # Final log output
            log.append(
                f"[READY] video={video_link} | user={username} | qty={qty}"
            )

    return render_template_string(HTML, log="\n".join(log))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
