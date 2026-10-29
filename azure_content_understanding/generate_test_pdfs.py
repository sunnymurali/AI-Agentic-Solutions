"""Generate synthetic test PDFs (2 variations x 7 types) for Content Understanding experiments."""
import io, math, random, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

OUT = Path(__file__).resolve().parent  # PDFs are written next to this script
FD = Path(r"C:\Windows\Fonts")
pdfmetrics.registerFont(TTFont("Arial", str(FD / "arial.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Bold", str(FD / "arialbd.ttf")))
random.seed(7)


# ---------- helpers -------------------------------------------------------
def handwriting(text, font="Inkfree.ttf", size=64, color=(20, 40, 150), angle=0, flourish=False):
    f = ImageFont.truetype(str(FD / font), size)
    w = int(f.getlength(text)) + 60
    h = int(size * 1.9)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((30, size * 0.3), text, font=f, fill=color + (235,))
    if flourish:  # loose underline swoosh, like a real signature
        pts = [(20 + i * (w - 40) / 40, h * 0.82 + math.sin(i / 3.0) * 6 - i * 0.15) for i in range(41)]
        d.line(pts, fill=color + (235,), width=max(3, size // 18))
    if angle:
        im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    return im


def put(c, im, x, y, width):
    """Place an RGBA PIL image on a reportlab canvas with its lower-left at (x, y)."""
    buf = io.BytesIO(); im.save(buf, "PNG"); buf.seek(0)
    c.drawImage(ImageReader(buf), x, y, width=width, height=width * im.height / im.width, mask="auto")


def put_h(c, im, x, y, height):
    """Place an RGBA PIL image scaled to a fixed height (pts)."""
    put(c, im, x, y, height * im.width / im.height)


def scan_look(img, skew=0.8, noise=10, blur=0.6):
    """Make a clean render look like a photocopy/scan."""
    img = img.convert("L").rotate(skew, expand=True, fillcolor=255, resample=Image.BICUBIC)
    px = img.load()
    w, h = img.size
    for _ in range(w * h // 40):
        x, y = random.randrange(w), random.randrange(h)
        px[x, y] = max(0, min(255, px[x, y] + random.randint(-noise * 6, noise * 2)))
    return img.filter(ImageFilter.GaussianBlur(blur))


def image_pdf(img, path):
    img.convert("RGB").save(path, "PDF", resolution=200.0)


def wrapped_image_page(lines, title, W=1654, H=2339):
    """lines: list of (text, bold, indent). Render a text page to a PIL image (A4 @200dpi)."""
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    reg = ImageFont.truetype(str(FD / "arial.ttf"), 38)
    bold = ImageFont.truetype(str(FD / "arialbd.ttf"), 38)
    big = ImageFont.truetype(str(FD / "arialbd.ttf"), 62)
    d.text((140, 150), title, font=big, fill="black")
    d.line((140, 240, W - 140, 240), fill="black", width=4)
    y = 300
    for text, b, ind in lines:
        d.text((140 + ind, y), text, font=bold if b else reg, fill="black"); y += 64
    return im


# ---------- 1. Polish / accented names (image PDFs) -----------------------
def t1():
    rows = [("Zażółć Gęślą-Jaźń", "PL61 1090 1014 0000 0712 1981 2874"),
            ("Łukasz Wójcik", "PL27 1140 2004 0000 3002 0135 5387"),
            ("Małgorzata Szymańska", "PL10 1050 1214 1000 0090 3200 0500"),
            ("Józef Kowalczyk-Żelazny", "PL83 1020 1026 0000 0422 7020 1111"),
            ("Ćwikła Dąbrowska-Nożyk", "PL66 1240 6292 1111 0010 5090 5432"),
            ("José Ñúñez Peña", "ES91 2100 0418 4502 0005 1332"),
            ("François Lefèvre-Müller", "FR14 2004 1010 0505 0001 3M02 606"),
            ("Søren Ærøskøbing", "DK50 0040 0440 1162 43")]
    lines = [("Register of Beneficial Owners - Fund Units", True, 0), ("As of 30 June 2026", False, 0), ("", False, 0),
             ("Investor name                                   Account / IBAN", True, 0)]
    for n, i in rows:
        lines.append((f"{n:<34}{i}", False, 0))
    lines += [("", False, 0), ("Prepared by: Wojciech Przybylski, Dział Obsługi Klienta", False, 0)]
    image_pdf(scan_look(wrapped_image_page(lines, "Rejestr Uczestników / Investor Register")), OUT / "01_polish_names_image_v1_register.pdf")

    W, H = 1654, 2339
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    F = lambda s, b=False: ImageFont.truetype(str(FD / ("arialbd.ttf" if b else "arial.ttf")), s)
    d.text((140, 140), "WNIOSEK O OTWARCIE RACHUNKU", font=F(64, True), fill="black")
    d.text((140, 225), "Account Opening Application / Demande d'ouverture de compte", font=F(34), fill="#333")
    fields = [("Imię i nazwisko:", "Agnieszka Wiśniewska-Ślązak"), ("Nazwisko rodowe:", "Błaszczyk"),
              ("Miejsce urodzenia:", "Łódź"), ("Adres:", "ul. Świętojańska 12/4, 81-368 Gdynia"),
              ("Reprezentant:", "Przemysław Gołębiowski"), ("Beneficiary / Bénéficiaire:", "Hélène Dubois-Côté"),
              ("Contact:", "Björn Åkesson, Göteborg")]
    y = 380
    for k, v in fields:
        d.text((140, y), k, font=F(36, True), fill="black")
        d.text((700, y), v, font=F(40), fill="black")
        d.line((700, y + 52, W - 140, y + 52), fill="#666", width=2); y += 110
    d.text((140, y + 60), "Data / Date: 12.06.2026", font=F(36), fill="black")
    image_pdf(scan_look(im, skew=-1.1, noise=14, blur=0.8), OUT / "01_polish_names_image_v2_account_form.pdf")


# ---------- 2. Watermarks -------------------------------------------------
def t2():
    # v1: diagonal CONFIDENTIAL over a factsheet
    c = canvas.Canvas(str(OUT / "02_watermark_v1_confidential_factsheet.pdf"), pagesize=A4); w, h = A4
    c.setFont("Arial-Bold", 20); c.drawString(50, h - 70, "Northbridge Global Equity Fund - Factsheet")
    c.setFont("Arial", 11)
    body = ["NAV per unit: USD 142.37   |   Fund size: USD 1.84bn   |   Inception: 14 March 2014",
            "Objective: long-term capital growth through a diversified portfolio of global equities.",
            "Top holdings: Microsoft 5.8%, Apple 5.1%, NVIDIA 4.7%, Nestle 3.2%, ASML 2.9%.",
            "Fees: Management fee 0.85% p.a.; Ongoing charges 1.02%; Performance fee none.",
            "Risk: SRRI 6. Past performance is not a reliable indicator of future results."]
    y = h - 110
    for ln in body * 6:
        c.drawString(50, y, ln); y -= 22
    c.saveState(); c.setFillColor(colors.Color(0.8, 0.1, 0.1, alpha=0.18)); c.setFont("Arial-Bold", 90)
    c.translate(w / 2, h / 2); c.rotate(45); c.drawCentredString(0, 0, "CONFIDENTIAL"); c.restoreState()
    c.save()
    # v2: tiled DRAFT watermark + header watermark on a letter, 2 pages
    c = canvas.Canvas(str(OUT / "02_watermark_v2_draft_tiled_letter.pdf"), pagesize=letter); w, h = letter
    for p in (1, 2):
        c.setFont("Arial", 11)
        c.drawString(72, h - 72, "Meridian Capital Partners LLP"); c.drawString(72, h - 90, "12 Fenchurch Street, London EC3M 3BY")
        c.drawString(72, h - 130, "Dear Investor,")
        txt = ("We are pleased to confirm the proposed terms of your commitment of EUR 5,000,000 to the "
               "Meridian Credit Opportunities Fund III. Closing is expected on 30 September 2026. "
               "This document remains subject to legal review and must not be relied upon.")
        y = h - 160
        for ln in textwrap.wrap(txt, 85):
            c.drawString(72, y, ln); y -= 18
        c.saveState(); c.setFillColor(colors.Color(0.2, 0.2, 0.2, alpha=0.10)); c.setFont("Arial-Bold", 34)
        for gx in range(-100, int(w) + 200, 340):
            for gy in range(-100, int(h) + 200, 170):
                c.saveState(); c.translate(gx, gy); c.rotate(30); c.drawString(0, 0, "DRAFT - NOT FOR DISTRIBUTION"); c.restoreState()
        c.restoreState(); c.setFont("Arial", 9); c.drawString(72, 40, f"Page {p} of 2"); c.showPage()
    c.save()


# ---------- 3. Names with signature overlapping the printed name ----------
def t3():
    c = canvas.Canvas(str(OUT / "03_signature_overlap_v1_signatories.pdf"), pagesize=A4); w, h = A4
    c.setFont("Arial-Bold", 16); c.drawString(50, h - 70, "Authorised Signatories - Schedule 2")
    people = [("Katarzyna Nowak", "Director"), ("Michael O'Brien", "Chief Financial Officer"),
              ("Przemysław Zieliński", "Authorised Signatory"), ("Hélène Moreau", "Compliance Officer")]
    y = h - 140
    for i, (n, t) in enumerate(people):
        c.setFont("Arial", 10); c.drawString(50, y + 22, "Name:"); c.drawString(300, y + 22, "Title:")
        c.setFont("Arial-Bold", 14); c.drawString(50, y, n)
        c.setFont("Arial", 12); c.drawString(300, y, t)
        c.line(50, y - 4, 280, y - 4)
        sig = handwriting(n.split()[0][0] + ". " + n.split()[-1], font=["segoesc.ttf", "BRUSHSCI.TTF"][i % 2], size=70,
                          angle=random.randint(2, 9), flourish=True)
        put(c, sig, 60 + i * 6, y - 22, 190)  # lands on top of the printed name
        y -= 120
    c.save()
    c = canvas.Canvas(str(OUT / "03_signature_overlap_v2_subscription_block.pdf"), pagesize=letter); w, h = letter
    c.setFont("Arial-Bold", 15); c.drawString(72, h - 72, "Subscription Agreement - Signature Page")
    c.setFont("Arial", 11)
    c.drawString(72, h - 110, "IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.")
    for j, (n, role, y0) in enumerate([("Alexandre Dupont-Lefèvre", "For and on behalf of the Subscriber", h - 230),
                                      ("Sofia Andersson", "For and on behalf of the Fund", h - 400)]):
        c.setFont("Arial", 11); c.drawString(72, y0 + 40, role)
        c.setFont("Arial-Bold", 13); c.drawString(110, y0, n)
        c.setFont("Arial", 10); c.drawString(72, y0 - 18, "Name (printed)"); c.line(72, y0 - 4, 380, y0 - 4)
        sig = handwriting("ADL" if j == 0 else "S. Andersson", font="BRUSHSCI.TTF" if j == 0 else "segoesc.ttf",
                          size=95, angle=-4, flourish=True)
        put(c, sig, 100, y0 - 40, 260)  # strikes through the printed name
        c.drawString(72, y0 - 50, "Date: 18 / 09 / 2026")
    c.save()


# ---------- 4. Tabular (text) + trade order as image ----------------------
def t4():
    c = canvas.Canvas(str(OUT / "04_table_v1_trade_blotter_text.pdf"), pagesize=A4)
    w, h = A4; c.setFont("Arial-Bold", 15); c.drawString(40, h - 60, "Daily Trade Blotter - 24 Sep 2026")
    cols = ["Trade ID", "Side", "Ticker", "Security", "Qty", "Price", "Amount (USD)"]; xs = [40, 105, 145, 195, 320, 380, 450]
    data = [["T-100231", "BUY", "MSFT", "Microsoft Corp", "1,200", "421.50", "505,800.00"],
            ["T-100232", "SELL", "AAPL", "Apple Inc", "800", "228.10", "182,480.00"],
            ["T-100233", "BUY", "NESN", "Nestle SA", "2,500", "96.40", "241,000.00"],
            ["T-100234", "BUY", "ASML", "ASML Holding NV", "150", "712.00", "106,800.00"],
            ["T-100235", "SELL", "NVDA", "NVIDIA Corp", "600", "131.25", "78,750.00"],
            ["T-100236", "BUY", "SAP", "SAP SE", "900", "208.75", "187,875.00"]]
    y = h - 100; c.setFillColor(colors.HexColor("#1f3a5f")); c.rect(36, y - 6, w - 72, 22, fill=1, stroke=0)
    c.setFillColor(colors.white); c.setFont("Arial-Bold", 9)
    for x, t in zip(xs, cols): c.drawString(x, y, t)
    c.setFillColor(colors.black); c.setFont("Arial", 9); y -= 24
    for i, r in enumerate(data):
        if i % 2: c.setFillColor(colors.HexColor("#eef2f7")); c.rect(36, y - 6, w - 72, 20, fill=1, stroke=0); c.setFillColor(colors.black)
        for x, t in zip(xs, r): c.drawString(x, y, t)
        y -= 20
    c.setFont("Arial-Bold", 10); c.drawString(380, y - 10, "Total:"); c.drawString(450, y - 10, "1,302,705.00")
    c.save()
    # v2: trade order scanned to image (no text layer)
    W, H = 1654, 2339
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    F = lambda s, b=False: ImageFont.truetype(str(FD / ("arialbd.ttf" if b else "arial.ttf")), s)
    d.text((140, 130), "TRADE ORDER TICKET", font=F(66, True), fill="black")
    d.text((140, 220), "Order ref: TO-2026-004871      Date: 24/09/2026", font=F(36), fill="black")
    hdr = ["Side", "Ticker", "Security", "Quantity", "Limit", "Account"]; xs = [140, 300, 460, 860, 1060, 1260]
    d.rectangle((130, 340, W - 130, 410), fill="#d9d9d9")
    for x, t in zip(xs, hdr): d.text((x, 352), t, font=F(36, True), fill="black")
    rows = [["BUY", "MSFT", "Microsoft Corp", "1,200", "421.50", "ACC-77120"], ["SELL", "AAPL", "Apple Inc", "800", "MKT", "ACC-77120"],
            ["BUY", "ASML", "ASML Holding NV", "150", "712.00", "ACC-90311"]]
    y = 430
    for r in rows:
        for x, t in zip(xs, r): d.text((x, y + 10), t, font=F(36), fill="black")
        d.line((130, y + 75, W - 130, y + 75), fill="#888", width=2); y += 90
    d.rectangle((130, 340, W - 130, y - 15), outline="black", width=4)
    d.text((140, y + 60), "Broker: Halden & Roe Securities       Settlement: T+1", font=F(34), fill="black")
    image_pdf(scan_look(im, skew=0.9, noise=12), OUT / "04_table_v2_trade_order_image.pdf")


# ---------- 5. Fund hierarchy flow charts ---------------------------------
def box(c, cx, cy, w, h, text, sub=None, fill="#e8eef7"):
    c.setFillColor(colors.HexColor(fill)); c.setStrokeColor(colors.HexColor("#1f3a5f")); c.setLineWidth(1.3)
    c.roundRect(cx - w / 2, cy - h / 2, w, h, 5, fill=1, stroke=1); c.setFillColor(colors.black)
    c.setFont("Arial-Bold", 9); c.drawCentredString(cx, cy + (3 if sub else -3), text)
    if sub: c.setFont("Arial", 8); c.drawCentredString(cx, cy - 8, sub)


def link(c, x1, y1, x2, y2, label=None):
    """Elbow connector from bottom of upper box to top of lower box."""
    c.setStrokeColor(colors.HexColor("#444")); c.setLineWidth(1)
    mid = (y1 + y2) / 2; p = c.beginPath(); p.moveTo(x1, y1); p.lineTo(x1, mid); p.lineTo(x2, mid); p.lineTo(x2, y2); c.drawPath(p, stroke=1, fill=0)
    d = 6 if y2 < y1 else -6  # arrowhead points in the direction of travel
    c.line(x2, y2, x2 - 3, y2 + d); c.line(x2, y2, x2 + 3, y2 + d)
    if label: c.setFont("Arial", 7); c.drawString(x2 + 4, mid + 3, label)


def t5():
    c = canvas.Canvas(str(OUT / "05_fund_hierarchy_v1_master_feeder.pdf"), pagesize=(842, 595)); w, h = 842, 595
    c.setFont("Arial-Bold", 14); c.drawString(30, h - 35, "Orion Strategies - Master-Feeder Structure")
    box(c, 421, 520, 200, 36, "Orion Capital GP Ltd", "General Partner / Investment Manager", "#fff2cc")
    box(c, 421, 440, 220, 36, "Orion Master Fund LP", "Cayman Islands", "#d9ead3")
    link(c, 421, 502, 421, 458, "manages")
    feeders = [(130, "Orion Onshore Feeder LP", "Delaware - US taxable"), (421, "Orion Offshore Feeder Ltd", "Cayman - non-US / tax-exempt"),
               (712, "Orion Europe Feeder SICAV", "Luxembourg - UCITS-like")]
    for x, n, s in feeders:
        box(c, x, 330, 200, 40, n, s); link(c, x, 350, 421, 422, "invests" if x == 130 else None)
    inv = [(130, "US Taxable Investors"), (421, "Non-US Investors"), (712, "EU Investors")]
    for x, n in inv: box(c, x, 220, 160, 30, n, fill="#f4cccc"); link(c, x, 235, x, 310)
    svc = [(180, "Prime Broker: Goldman Sachs"), (421, "Administrator: Apex Fund Services"), (662, "Custodian: BNP Paribas")]
    for x, n in svc: box(c, x, 100, 200, 30, n, fill="#ead1dc")
    c.setFont("Arial", 9); c.drawString(30, 150, "Service providers (to the Master Fund):")
    c.save()
    c = canvas.Canvas(str(OUT / "05_fund_hierarchy_v2_umbrella_subfunds.pdf"), pagesize=(842, 595))
    c.setFont("Arial-Bold", 14); c.drawString(30, h - 35, "Aldgate Umbrella ICAV - Sub-funds and Share Classes")
    box(c, 421, 520, 230, 36, "Aldgate UCITS ICAV", "Umbrella - Ireland", "#fff2cc")
    box(c, 130, 520, 190, 40, "Management Company", "Aldgate ManCo (Ireland) Ltd", "#ead1dc")
    box(c, 712, 520, 190, 40, "Depositary", "State Street Custodial Services", "#ead1dc")
    c.setStrokeColor(colors.HexColor('#444')); c.line(306, 520, 225, 520); c.line(536, 520, 617, 520)
    subs = [(130, "Global Equity Fund"), (421, "Euro Bond Fund"), (712, "Multi-Asset Income Fund")]
    for x, n in subs:
        box(c, x, 350, 190, 36, n, "Sub-fund", "#d9ead3"); link(c, 421, 502, x, 368)
        for k, cls in enumerate(["Class A (EUR Acc)", "Class I (USD Dist)", "Class Z (GBP Acc)"]):
            xx = x - 80 + k * 80
            box(c, xx, 230, 74, 40, cls.split(" (")[0], "(" + cls.split(" (")[1], "#cfe2f3"); link(c, x, 332, xx, 250)
    c.setFont("Arial", 9); c.drawString(30, 120, "Investment Manager: Aldgate Asset Management LLP   |   Administrator: Northern Trust   |   Auditor: KPMG")
    c.save()


# ---------- 6. Forms with checked checkboxes ------------------------------
def t6():
    # v1: genuine AcroForm checkboxes / text fields
    c = canvas.Canvas(str(OUT / "06_form_checkbox_v1_acroform_kyc.pdf"), pagesize=letter); w, h = letter
    c.setFont("Arial-Bold", 16); c.drawString(72, h - 72, "Investor Classification Form")
    c.setFont("Arial", 11); c.drawString(72, h - 100, "Please tick all boxes that apply.")
    items = [("Professional client", True), ("Eligible counterparty", False), ("Retail client", False),
             ("US person (FATCA)", False), ("Politically exposed person (PEP)", False), ("I confirm the information above is accurate", True)]
    y = h - 140
    for i, (label, checked) in enumerate(items):
        c.acroForm.checkbox(name=f"cb{i}", x=72, y=y - 3, size=14, checked=checked, buttonStyle="check",
                            borderColor=colors.black, fillColor=colors.white, textColor=colors.black, forceBorder=True)
        c.drawString(96, y, label); y -= 30
    c.drawString(72, y - 20, "Investor name:"); c.acroForm.textfield(name="name", x=160, y=y - 26, width=250, height=20, value="Marta Kowalska", borderStyle="underlined")
    c.save()
    # v2: flat form with hand-ticked boxes (X marks drawn as strokes, one ambiguous half-mark)
    c = canvas.Canvas(str(OUT / "06_form_checkbox_v2_flat_tickbox_form.pdf"), pagesize=A4); w, h = A4
    c.setFont("Arial-Bold", 16); c.drawString(50, h - 70, "Redemption Request Form")
    c.setFont("Arial", 11)
    opts = [("Full redemption", False), ("Partial redemption", True), ("Switch to another sub-fund", False), ("Pay proceeds by wire transfer", True),
            ("Pay proceeds by cheque", False), ("Terms and conditions accepted", True)]
    y = h - 120
    for lbl, on in opts:
        c.setStrokeColor(colors.black); c.setLineWidth(1); c.rect(50, y - 3, 14, 14)
        if on:
            c.setStrokeColor(colors.HexColor("#14289a")); c.setLineWidth(2)
            c.line(52, y, 62, y + 9); c.line(52, y + 9, 62, y);
        c.setFillColor(colors.black); c.drawString(75, y, lbl); y -= 28
    c.drawString(50, y - 20, "Units to redeem: 2,450.000     Fund: Northbridge Global Equity Fund")
    c.save()


# ---------- 7. Trade order forms with handwriting -------------------------
def order_form(path, note, extra_fields, sig_text, pagesize=A4):
    c = canvas.Canvas(str(path), pagesize=pagesize); w, h = pagesize
    c.setFont("Arial-Bold", 16); c.drawString(50, h - 60, "TRADE ORDER INSTRUCTION")
    c.setFont("Arial", 10); c.drawString(50, h - 78, "Halden & Roe Securities - Dealing Desk   |   dealing@haldenroe.example")
    labels = ["Account No.", "Side (Buy/Sell)", "Security / ISIN", "Quantity", "Order type", "Limit price"]
    y = h - 130
    for i, lab in enumerate(labels):
        c.setFont("Arial", 10); c.drawString(50, y, lab + ":"); c.line(160, y - 3, w - 60, y - 3)
        if extra_fields: put_h(c, handwriting(extra_fields[i], size=44, angle=random.randint(-2, 2)), 165, y - 6, 24)
        y -= 34
    c.setFont("Arial-Bold", 11); c.drawString(50, y - 20, "Special instructions / certification")
    c.rect(50, y - 120, w - 100, 85)
    put(c, handwriting(note, size=60, angle=-2), 60, y - 112, 330)
    c.setFont("Arial", 10); c.drawString(50, y - 160, "Client name (print):  Tomasz Wróbel"); c.line(50, y - 200, 280, y - 200)
    c.drawString(50, y - 214, "Authorised signature")
    put(c, handwriting(sig_text, font="segoesc.ttf", size=80, angle=5, flourish=True), 55, y - 205, 200)
    c.drawString(330, y - 214, "Date: 24/09/2026")
    c.save()


def t7():
    order_form(OUT / "07_handwritten_order_v1_please_process.pdf", "Please process Order", None, "T. Wrobel")
    order_form(OUT / "07_handwritten_order_v2_certify_filled_by_hand.pdf", "I certify the order",
               ["ACC-77120", "BUY", "MSFT US5949181045", "1,200", "Limit", "421.50"], "Tomasz W.", pagesize=letter)


if __name__ == "__main__":
    for t in (t1, t2, t3, t4, t5, t6, t7):
        t(); print("done", t.__name__)
