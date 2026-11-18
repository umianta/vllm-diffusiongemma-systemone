"""Render the sample images used by the Postman collection (synthetic, no real data)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "postman/images")
OUT.mkdir(parents=True, exist_ok=True)
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
font = lambda s, p=F: ImageFont.truetype(p, s)


def page(w=640, h=480, bg="white"):
    im = Image.new("RGB", (w, h), bg)
    return im, ImageDraw.Draw(im)


def save(im, name):
    im.save(OUT / f"{name}.png", optimize=True)


# 1 invoice
im, d = page()
d.text((30, 25), "INVOICE", font=font(36, FB), fill="black")
d.text((420, 35), "No. INV-1042", font=font(18), fill="black")
d.text((30, 85), "From: Northwind Office Supply Co.", font=font(16), fill="black")
d.text((30, 110), "Bill to: Contoso Labs, Accounts Payable", font=font(16), fill="black")
d.text((30, 135), "Date: 2026-11-02     Due: 2026-12-02 (Net 30)", font=font(16), fill="black")
d.line((30, 175, 610, 175), fill="black", width=2)
rows = [("Ergonomic chairs x10", "3,200.00"), ("Standing desks x2", "1,400.00"), ("Delivery", "250.00")]
y = 190
for item, amt in rows:
    d.text((30, y), item, font=font(16), fill="black")
    d.text((500, y), f"${amt}", font=font(16), fill="black")
    y += 32
d.line((30, y + 5, 610, y + 5), fill="black", width=2)
d.text((300, y + 20), "TOTAL DUE: $4,850.00 USD", font=font(20, FB), fill="black")
d.text((30, 420), "Status: UNPAID - please remit by bank transfer", font=font(15), fill="#b00")
save(im, "invoice")

# 2 receipt
im, d = page(360, 520, "#fbfaf5")
d.text((80, 20), "BLUE HARBOR GRILL", font=font(20, FB), fill="black")
d.text((95, 50), "Seattle, WA  12 Nov 2026", font=font(13), fill="black")
y = 100
for item, amt in [("Salmon entree x2", "58.00"), ("Caesar salad", "12.50"), ("Sparkling water x2", "8.00"), ("Coffee x2", "7.90")]:
    d.text((20, y), item, font=font(15, FM), fill="black")
    d.text((270, y), amt, font=font(15, FM), fill="black")
    y += 30
d.line((20, y, 340, y), fill="black")
d.text((20, y + 15), "Tax", font=font(15, FM), fill="black")
d.text((270, y + 15), "8.60", font=font(15, FM), fill="black")
d.text((20, y + 50), "TOTAL", font=font(18, FB), fill="black")
d.text((255, y + 50), "$95.00", font=font(18, FB), fill="black")
d.text((20, y + 100), "Paid: VISA ****4421", font=font(14, FM), fill="black")
d.text((60, y + 150), "Thank you for dining with us!", font=font(13), fill="black")
save(im, "receipt")

# 3 error dialog
im, d = page(560, 260, "#dcdcdc")
d.rectangle((20, 20, 540, 240), fill="white", outline="#555", width=2)
d.rectangle((20, 20, 540, 55), fill="#2b579a")
d.text((32, 28), "Orders Service", font=font(16, FB), fill="white")
d.ellipse((45, 85, 105, 145), fill="#d32f2f")
d.text((63, 92), "X", font=font(40, FB), fill="white")
d.text((130, 85), "FATAL ERROR", font=font(20, FB), fill="#d32f2f")
d.text((130, 118), "Database connection lost.", font=font(16), fill="black")
d.text((130, 142), "All checkout requests are failing.", font=font(16), fill="black")
d.text((130, 166), "Code: DB_CONN_REFUSED (5432)", font=font(14, FM), fill="#333")
d.rectangle((420, 195, 520, 228), fill="#e0e0e0", outline="#888")
d.text((452, 202), "OK", font=font(15), fill="black")
save(im, "error_dialog")


# 4/5 charts
def chart(name, vals, title):
    im, d = page(560, 380)
    d.text((20, 15), title, font=font(18, FB), fill="black")
    d.line((60, 330, 530, 330), fill="black", width=2)
    d.line((60, 60, 60, 330), fill="black", width=2)
    for i, (q, v) in enumerate(zip(["Q1", "Q2", "Q3", "Q4"], vals)):
        x = 90 + i * 110
        d.rectangle((x, 330 - v * 2.5, x + 60, 330), fill="#1976d2")
        d.text((x + 18, 340), q, font=font(14), fill="black")
        d.text((x + 10, 330 - v * 2.5 - 22), f"${v}M", font=font(13), fill="black")
    save(im, name)


chart("chart_growth", [20, 42, 68, 95], "Revenue 2026 (USD millions)")
chart("chart_decline", [95, 70, 44, 18], "Revenue 2026 (USD millions)")

# 6 stop sign on a road
im, d = page(480, 480, "#87ceeb")
d.rectangle((0, 300, 480, 480), fill="#555")
d.rectangle((0, 380, 480, 392), fill="white")
d.rectangle((320, 230, 332, 400), fill="#777")
import math
cx, cy, r = 326, 160, 90
pts = [(cx + r * math.cos(math.radians(22.5 + 45 * k)), cy + r * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]
d.polygon(pts, fill="#c62828", outline="white")
d.text((cx - 62, cy - 26), "STOP", font=font(46, FB), fill="white")
save(im, "stop_sign")

# 7 signed form
im, d = page()
d.text((30, 25), "VENDOR ONBOARDING AGREEMENT", font=font(24, FB), fill="black")
d.text((30, 80), "Company: Fabrikam Logistics LLC", font=font(16), fill="black")
d.text((30, 110), "Tax ID: on file", font=font(16), fill="black")
for i, (txt, ticked) in enumerate([("I agree to the Terms of Service", True), ("I agree to the Data Processing Addendum", True), ("Subscribe to marketing emails", False)]):
    y = 160 + i * 40
    d.rectangle((30, y, 52, y + 22), outline="black", width=2)
    if ticked:
        d.line((34, y + 11, 41, y + 19), fill="black", width=3)
        d.line((41, y + 19, 50, y + 3), fill="black", width=3)
    d.text((65, y), txt, font=font(16), fill="black")
d.text((30, 330), "Signature:", font=font(16), fill="black")
d.line((130, 370, 400, 370), fill="black")
sig = [(140, 360), (160, 335), (175, 362), (195, 338), (215, 365), (240, 340), (260, 358), (300, 345), (340, 360), (380, 342)]
d.line(sig, fill="#1a237e", width=3)
d.text((30, 400), "Date: 2026-11-10", font=font(16), fill="black")
save(im, "signed_form")

# 8 confidential document
im, d = page(520, 640)
d.text((30, 30), "Project Atlas - Q1 Acquisition Plan", font=font(20, FB), fill="black")
for i in range(14):
    d.line((30, 90 + i * 30, 490 - (i % 3) * 40, 90 + i * 30), fill="#999", width=6)
st = Image.new("RGBA", (400, 90), (0, 0, 0, 0))
sd = ImageDraw.Draw(st)
sd.rectangle((2, 2, 397, 87), outline=(200, 0, 0, 255), width=5)
sd.text((18, 15), "CONFIDENTIAL", font=font(46, FB), fill=(200, 0, 0, 255))
st = st.rotate(20, expand=True)
im.paste(st, (70, 230), st)
save(im, "confidential_doc")

# 9 monitoring dashboard
im, d = page(640, 360, "#1e1e1e")
d.text((20, 15), "prod-cluster-east  |  Service Health", font=font(18, FB), fill="white")
tiles = [("CPU", "98%", "#e53935"), ("Memory", "91%", "#e53935"), ("p99 latency", "4.2 s", "#e53935"), ("Error rate", "23%", "#e53935"), ("Pods ready", "3/12", "#fb8c00"), ("Disk", "41%", "#43a047")]
for i, (k, v, c) in enumerate(tiles):
    x, y = 20 + (i % 3) * 205, 60 + (i // 3) * 140
    d.rectangle((x, y, x + 190, y + 120), fill="#2c2c2c", outline=c, width=3)
    d.text((x + 12, y + 10), k, font=font(15), fill="#ccc")
    d.text((x + 12, y + 45), v, font=font(34, FB), fill=c)
d.text((20, 330), "ALERT: HighErrorRate firing for 14m", font=font(14, FB), fill="#e53935")
save(im, "dashboard_alert")

# 10 phishing login page
im, d = page(560, 420, "#f4f6f9")
d.rectangle((0, 0, 560, 36), fill="#e0e0e0")
d.text((12, 9), "http://nimbuspay-secure-verify.top/login", font=font(14, FM), fill="#c62828")
d.rectangle((130, 70, 430, 390), fill="white", outline="#ccc")
d.text((170, 90), "NimbusPay Security", font=font(22, FB), fill="#003087")
d.text((150, 135), "Your account is suspended!", font=font(15, FB), fill="#c62828")
d.text((150, 158), "Verify within 24 hours or lose access.", font=font(12), fill="black")
for i, lbl in enumerate(["Email", "Password", "Card number"]):
    y = 195 + i * 50
    d.text((150, y), lbl, font=font(12), fill="#555")
    d.rectangle((150, y + 16, 410, y + 40), outline="#999")
d.rectangle((150, 345, 410, 375), fill="#0070ba")
d.text((222, 351), "Verify now", font=font(15, FB), fill="white")
save(im, "phishing_login")

print(sorted(p.name for p in OUT.iterdir()))
