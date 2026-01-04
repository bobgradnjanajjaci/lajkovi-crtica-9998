from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

# 🔧 KONFIGURACIJA – JAP PANEL
PANEL_URL = "https://justanotherpanel.com/api/v2"
API_KEY = "c849788f60dd591e636c5d079b0a8d62"
SERVICE_ID = 9407  # TikTok Comment Likes na JAP-u

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
  <title>TikTok Comment Likes Sender</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * {
      box-sizing: border-box;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    body {
      margin: 0;
      padding: 0;
      background: radial-gradient(circle at top, #1f2937 0, #020617 55%);
      color: #e5e7eb;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .wrapper {
      width: 100%;
      max-width: 960px;
      padding: 20px;
    }

    .card {
      background: rgba(15, 23, 42, 0.96);
      border-radius: 16px;
      padding: 22px 22px 18px;
      border: 1px solid rgba(148, 163, 184, 0.35);
      box-shadow: 0 20px 50px rgba(15, 23, 42, 0.9);
    }

    .header {
      display: flex;
      flex-direction: column;
      gap: 6px;
      margin-bottom: 18px;
    }

    .title {
      font-size: 22px;
      font-weight: 700;
      letter-spacing: 0.03em;
      text-transform: uppercase;
      color: #e5e7eb;
    }

    .subtitle {
      font-size: 13px;
      color: #9ca3af;
    }

    .subtitle span {
      color: #a855f7;
      font-weight: 600;
    }

    .grid {
      display: grid;
      grid-template-columns: 1.4fr 1fr;
      gap: 16px;
    }

    @media (max-width: 820px) {
      .grid {
        grid-template-columns: 1fr;
      }
    }

    label {
      font-size: 12px;
      color: #9ca3af;
      margin-bottom: 6px;
      display: block;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    textarea {
      width: 100%;
      min-height: 190px;
      background: rgba(15, 23, 42, 0.85);
      border-radius: 10px;
      border: 1px solid rgba(55, 65, 81, 0.9);
      padding: 10px 11px;
      font-size: 13px;
      color: #e5e7eb;
      resize: vertical;
      outline: none;
    }

    textarea::placeholder {
      color: #6b7280;
      font-size: 12px;
    }

    .hint {
      font-size: 11px;
      color: #6b7280;
      margin-top: 4px;
      line-height: 1.4;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      padding: 4px 9px;
      border-radius: 999px;
      background: rgba(30, 64, 175, 0.35);
      border: 1px solid rgba(59, 130, 246, 0.7);
      color: #bfdbfe;
      margin-bottom: 8px;
    }

    .pill span {
      font-weight: 600;
      color: #e5e7eb;
    }

    .pill small {
      opacity: 0.8;
    }

    .btn-row {
      margin-top: 14px;
      display: flex;
      justify-content: flex-end;
    }

    .btn-primary {
      cursor: pointer;
      padding: 9px 18px;
      border-radius: 999px;
      border: none;
      font-size: 13px;
      font-weight: 600;
      letter-spacing: 0.03em;
      text-transform: uppercase;
      background: linear-gradient(90deg, #6366f1, #a855f7);
      color: white;
      box-shadow: 0 8px 22px rgba(79, 70, 229, 0.6);
      transition: transform 0.1s ease, box-shadow 0.1s ease;
    }

    .btn-primary:hover {
      transform: translateY(-1px);
      box-shadow: 0 12px 30px rgba(79, 70, 229, 0.8);
    }

    .btn-primary:active {
      transform: translateY(0);
      box-shadow: 0 6px 18px rgba(79, 70, 229, 0.6);
    }

    .status {
      text-align: center;
      font-size: 12px;
      color: #9ca3af;
      min-height: 18px;
      margin-top: 6px;
    }

    .status strong {
      color: #e5e7eb;
    }

    .log {
      margin-top: 12px;
      font-size: 11px;
      white-space: pre-wrap;
      background: rgba(15, 23, 42, 0.9);
      border-radius: 10px;
      padding: 10px;
      border: 1px solid rgba(55, 65, 81, 0.9);
      max-height: 260px;
      overflow-y: auto;
    }

    .field-box {
      background: radial-gradient(circle at top left, rgba(56, 189, 248, 0.08), rgba(15,23,42,1));
      border-radius: 12px;
      padding: 12px;
      border: 1px solid rgba(31, 41, 55, 0.95);
    }

  </style>
</head>
<body>
  <div class="wrapper">
    <div class="card">
      <div class="header">
        <div class="title">TikTok Comment Likes Sender</div>
        <div class="subtitle">
          Service ID: <span>{{ service_id }}</span> · Panel: <span>JAP API v2</span>
        </div>
      </div>

      <form method="post">
        <div class="grid">
          <div class="field-box">
            <div class="pill">
              <span>INPUT</span>
              <small>One order per line · LINK USERNAME QUANTITY</small>
            </div>
            <label for="orders">Orders</label>
            <textarea id="orders" name="orders" placeholder="Example:
https://www.tiktok.com/@user/video/6356041221485235461 username 100
https://www.tiktok.com/@another/video/1234567890123456789 user123 250">{{ orders or '' }}</textarea>
            <div class="hint">
              Format: <strong>link username quantity</strong><br>
              Script automatski pretvara u: <code>link|username</code> za API.
            </div>
          </div>

          <div class="field-box">
            <div class="pill">
              <span>INFO</span>
              <small>Service {{ service_id }}</small>
            </div>
            <div class="hint">
              • Panel: <strong>justanotherpanel.com</strong><br>
              • API key se čita iz koda.<br>
              • Svaka linija → jedan order.<br>
              • Ako je linija pogrešno upisana, biće preskočena uz poruku u logu.<br><br>
              Primjer:
              <br><code>https://www.tiktok.com/@asdadsd/video/6356041221485235461 username 100</code>
              <br>API dobija:
              <br><code>link = .../video/6356041221485235461|username</code>
              <br><code>quantity = 100</code>
            </div>
          </div>
        </div>

        <div class="btn-row">
          <button type="submit" class="btn-primary">🚀 Send to panel (API)</button>
        </div>
      </form>

      <div class="status">{{ status or '' }}</div>
      {% if log %}
      <div class="log">{{ log }}</div>
      {% endif %}
    </div>
  </div>
</body>
</html>
"""

def send_like_order(full_link: str, quantity: int):
    """
    Šalje JEDAN order na JAP za TikTok comment likes.
    full_link -> 'video_url|username'
    quantity  -> broj lajkova
    """
    payload = {
        "key": API_KEY,
        "action": "add",
        "service": SERVICE_ID,
        "link": full_link,
        "quantity": quantity,
    }

    try:
        r = requests.post(PANEL_URL, data=payload, timeout=20)
        try:
            data = r.json()
        except Exception:
            return False, f"HTTP {r.status_code}, body={r.text[:200]}"

        if "order" in data:
            return True, f"order={data['order']}"
        else:
            return False, f"resp={data}"
    except Exception as e:
        return False, f"exception={e}"

@app.route("/", methods=["GET", "POST"])
def index():
    orders = ""
    status = ""
    log_lines = []

    if request.method == "POST":
        orders = request.form.get("orders", "")
        lines = [l.strip() for l in orders.splitlines() if l.strip()]

        sent_ok = 0
        sent_fail = 0

        for raw in lines:
            # Očekujemo: link username quantity
            parts = raw.split()
            if len(parts) < 3:
                sent_fail += 1
                log_lines.append(f"[SKIP] Pogrešan format (treba: LINK USERNAME QUANTITY): {raw}")
                continue

            link = parts[0]
            username = parts[1]
            qty_str = parts[2]

            # quantity mora biti broj
            try:
                quantity = int(qty_str)
                if quantity <= 0:
                    raise ValueError("qty<=0")
            except Exception:
                sent_fail += 1
                log_lines.append(f"[SKIP] Nevažeća količina (mora biti broj > 0): {raw}")
                continue

            full_link = f"{link}|{username}"

            ok, msg = send_like_order(full_link, quantity)
            if ok:
                sent_ok += 1
                log_lines.append(f"[OK] {full_link} x{quantity} -> {msg}")
            else:
                sent_fail += 1
                log_lines.append(f"[FAIL] {full_link} x{quantity} -> {msg}")

        status = f"<strong>Gotovo.</strong> Uspješno: {sent_ok}, greške: {sent_fail}."

    log = "\n".join(log_lines)
    return render_template_string(
        HTML_TEMPLATE,
        orders=orders,
        status=status,
        log=log,
        service_id=SERVICE_ID,
    )

if __name__ == "__main__":
    app.run(debug=True)

