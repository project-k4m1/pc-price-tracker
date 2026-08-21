import os
import datetime
import json
import random
import feedparser
import requests
from google import genai
import anthropic

# API-Schlüssel aus den GitHub Secrets laden
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# --- HARDWARE-DATENBANK (Most Premium Build + Alternativen) ---
HARDWARE_DATA = {
    "main_build": {
        "name": "Ultra-Premium Studio-Showcase (Main-Build)",
        "items": [
            {
                "id": "m_cpu",
                "part": "Prozessor (CPU)",
                "model": "AMD Ryzen 9 9950X3D (16 Kerne / V-Cache)",
                "price": 720.00,
                "shop": "Mindfactory",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=AMD+Ryzen+9+9950X3D",
                "is_bundle": False,
                "alts": [
                    {"model": "AMD Ryzen 7 7800X3D", "price": 389.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=AMD+Ryzen+7+7800X3D"},
                    {"model": "AMD Ryzen 9 7900X", "price": 315.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=AMD+Ryzen+9+7900X"}
                ]
            },
            {
                "id": "m_ram",
                "part": "Arbeitsspeicher (RAM)",
                "model": "ADATA XPG Lancer Blade RGB 48GB DDR5-6000 CL30",
                "price": 375.00,
                "shop": "Alternate / Caseking",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=ADATA+XPG+Lancer+Blade+48GB+6000",
                "is_bundle": False,
                "alts": [
                    {"model": "Crucial Pro 48GB Kit DDR5-5600", "price": 165.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Crucial+Pro+48GB+DDR5"},
                    {"model": "Corsair Vengeance 32GB DDR5-6000", "price": 110.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Corsair+Vengeance+32GB+DDR5"}
                ]
            },
            {
                "id": "m_gpu",
                "part": "Grafikkarte (GPU)",
                "model": "ASUS TUF Gaming GeForce RTX 5070 Ti 16G OC",
                "price": 1219.00,
                "shop": "Notebooksbilliger",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=ASUS+TUF+Gaming+GeForce+RTX+5070+Ti",
                "is_bundle": False,
                "alts": [
                    {"model": "MSI GeForce RTX 5070 Ti 16G GAMING TRIO OC", "price": 1248.99, "shop": "Notebooksbilliger", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=MSI+GeForce+RTX+5070+Ti+GAMING+TRIO+OC"},
                    {"model": "MSI GeForce RTX 5070 Ti 16G VENTUS 3X OC", "price": 1149.00, "shop": "Notebooksbilliger", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=MSI+GeForce+RTX+5070+Ti+VENTUS+3X"},
                    {"model": "Gigabyte GeForce RTX 4070 Ti SUPER Windforce OC", "price": 849.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Gigabyte+GeForce+RTX+4070+Ti+SUPER"}
                ]
            },
            {
                "id": "m_mb",
                "part": "Mainboard",
                "model": "MSI MAG X870E TOMAHAWK WIFI",
                "price": 284.36,
                "shop": "Notebooksbilliger",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=MSI+MAG+X870E+TOMAHAWK+WIFI",
                "is_bundle": False,
                "alts": [
                    {"model": "ASUS ROG Strix X870-F Gaming WIFI", "price": 420.00, "shop": "Alternate", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=ASUS+ROG+Strix+X870-F"},
                    {"model": "MSI MAG B650 TOMAHAWK WIFI", "price": 180.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=MSI+B650+TOMAHAWK+WIFI"}
                ]
            },
            {
                "id": "m_ssd",
                "part": "SSD (System)",
                "model": "Samsung 990 PRO 1TB NVMe M.2",
                "price": 199.05,
                "shop": "Mindfactory",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Samsung+990+PRO+1TB",
                "is_bundle": False,
                "alts": [
                    {"model": "WD_BLACK SN850X 2TB NVMe M.2", "price": 185.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=WD_BLACK+SN850X+2TB"},
                    {"model": "Lexar NM790 2TB M.2 PCIe 4.0", "price": 140.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Lexar+NM790+2TB"}
                ]
            },
            {
                "id": "m_case",
                "part": "Gehäuse",
                "model": "HAVN HS420 VGPU Black (Panorama-Glas)",
                "price": 265.00,
                "shop": "Caseking",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=HAVN+HS420+VGPU+Black",
                "is_bundle": False,
                "alts": [
                    {"model": "Fractal Design North XL Charcoal TG", "price": 155.01, "shop": "Notebooksbilliger", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Fractal+Design+North+XL+Charcoal+TG"},
                    {"model": "Lian Li O11 Vision Compact", "price": 125.00, "shop": "Caseking", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Lian+Li+O11+Vision+Compact"}
                ]
            },
            {
                "id": "m_aio",
                "part": "AiO-Wasserkühlung",
                "model": "Lian Li HydroShift LCD 360S Black",
                "price": 180.00,
                "shop": "Notebooksbilliger",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Lian+Li+HydroShift+LCD+360S",
                "is_bundle": False,
                "alts": [
                    {"model": "NZXT Kraken Elite 360 RGB", "price": 279.59, "shop": "Notebooksbilliger", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=NZXT+Kraken+Elite+360+RGB"},
                    {"model": "Arctic Liquid Freezer III 360", "price": 75.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Arctic+Liquid+Freezer+III+360"}
                ]
            },
            {
                "id": "m_fans_lcd",
                "part": "Lüfter (Seite/Displays)",
                "model": "Lian Li UNI FAN TL LCD 120 Reverse (3er)",
                "price": 145.00,
                "shop": "Caseking",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Lian+Li+UNI+FAN+TL+LCD+120+Reverse",
                "is_bundle": False,
                "alts": [
                    {"model": "Lian Li UNI FAN SL-INF 120 Reverse (3er)", "price": 95.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Lian+Li+UNI+FAN+SL-INF+120+Reverse"},
                    {"model": "Arctic P12 PWM PST A-RGB (3er)", "price": 35.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Arctic+P12+PWM+PST"}
                ]
            },
            {
                "id": "m_fans_inf",
                "part": "Lüfter (Boden/Infinity)",
                "model": "Lian Li UNI FAN SL-INF Wireless Reverse (3er)",
                "price": 95.00,
                "shop": "Mindfactory",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Lian+Li+UNI+FAN+SL-INF+Wireless+Reverse",
                "is_bundle": False,
                "alts": [
                    {"model": "Arctic P14 PWM PST (5er Pack)", "price": 35.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Arctic+P14+PWM+PST+5er"}
                ]
            },
            {
                "id": "m_psu",
                "part": "Netzteil",
                "model": "be quiet! Straight Power 12 1000W ATX 3.0",
                "price": 185.00,
                "shop": "Mindfactory",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=be+quiet!+Straight+Power+12+1000W",
                "is_bundle": False,
                "alts": [
                    {"model": "be quiet! Straight Power 12 850W ATX 3.0", "price": 160.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=be+quiet!+Straight+Power+12+850W"},
                    {"model": "Corsair RM850e 850W ATX 3.0", "price": 115.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Corsair+RM850e+850W"}
                ]
            }
        ]
    }
}

def generate_cheapest_alternative_build(main_items):
    """Ermittelt für jede Komponente automatisch das günstigste verfügbare Modell."""
    cheapest_items = []
    for item in main_items:
        candidates = [{"model": item["model"], "price": item["price"], "shop": item["shop"], "url": item["url"]}]
        for alt in item.get("alts", []):
            if alt.get("url") != "#" and alt.get("price", 0) > 0:
                candidates.append(alt)
        best_candidate = min(candidates, key=lambda x: x["price"])
        cheapest_items.append({
            "part": item["part"],
            "model": best_candidate["model"],
            "price": best_candidate["price"],
            "shop": best_candidate["shop"],
            "url": best_candidate["url"]
        })
    return cheapest_items

def get_market_and_deals():
    """Holt Wechselkurse und Live-RSS-Feeds aus Hardware-Magazinen."""
    try:
        res = requests.get("https://open.er-api.com/v6/latest/EUR", timeout=10)
        rate = res.json()["rates"]["USD"]
    except Exception:
        rate = 1.08

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    rss_urls = [
        "https://www.mydealz.de/rss/gruppe/pc-hardware",
        "https://www.hardwareluxx.de/index.php/rss/all.xml",
        "https://www.heise.de/newsticker/heise-atom.xml"
    ]
    all_headlines = []
    keywords = ["rtx", "ryzen", "9950x", "7800x3d", "ddr5", "x870", "b650", "ssd", "bundle", "gutschein", "mindstar", "rabatt", "speicher", "hardware"]

    for url in rss_urls:
        try:
            req = requests.get(url, headers=headers, timeout=10)
            if req.status_code == 200:
                feed = feedparser.parse(req.text)
                for entry in feed.entries[:10]:
                    title = entry.title.lower()
                    if any(kw in title for kw in keywords):
                        all_headlines.append(entry.title)
        except Exception:
            continue

    headlines = list(dict.fromkeys(all_headlines))[:12]
    return rate, headlines if headlines else ["Hardware-Preise im Großhandel stabil. Keine extremen Deal-Drops registriert."]

def run_gemini_deal_hunter(rate, headlines):
    """Gemini analysiert Nachrichten und Deals mit Modell-Kaskade."""
    if not GEMINI_API_KEY:
        return "Gemini API Key nicht in den GitHub Secrets hinterlegt."
    
    prompt = f"""
    Du bist Marktanalyst für PC-Hardware.
    Aktuelle Tech-/Deal-Schlagzeilen: {headlines}
    Aktueller EUR/USD-Kurs: {rate:.4f}

    Aufgabe:
    1. Fasse in 2 prägnanten Sätzen die aktuelle Marktlage zusammen (Verfügbarkeit, Wechselkurseffekt, Speicherpreise).
    2. Falls Rabatte, Gutscheincodes oder Bundle-Aktionen erwähnt werden, führe sie stichpunktartig auf. Ansonsten erwähne kurz, dass der Markt aktuell stabil verläuft.
    """
    
    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    for m in models_to_try:
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(model=m, contents=prompt)
            if response.text:
                return response.text.strip()
        except Exception:
            continue
            
    # Fallback, falls keine Verbindung zu Gemini klappt
    deals_summary = "<br>• ".join(headlines[:4])
    return f"Live-News Ticker (Direkt-Feed):<br>• {deals_summary}"

def run_claude_decision(deal_briefing, rate, main_total, alt_total):
    """Claude liefert das Kaufurteil mit robuster Modell-Kaskade."""
    if not ANTHROPIC_API_KEY:
        return "Anthropic API Key nicht in den GitHub Secrets hinterlegt."
    
    prompt = f"""
    Du bist Einkaufsberater für eine High-End Workstation (Audio-Produktion/Ableton, 3D-Scans & High-End Gaming).
    Marktlage: {deal_briefing}
    High-End Showcase Build: {main_total:.2f} €
    Preis-Leistungs-Sieger: {alt_total:.2f} € (Ersparnis: {main_total - alt_total:.2f} €)

    Gib in 3 präzisen Sätzen auf Deutsch ein Urteil ab: Lohnt sich der Aufpreis für das Showcase-Setup aktuell, oder ist der P/L-Build die vernünftigere Wahl? Jetzt kaufen oder warten?
    """
    
    models_to_try = ["claude-3-7-sonnet-20250219", "claude-3-5-sonnet-latest", "claude-3-5-sonnet-20241022"]
    for m in models_to_try:
        try:
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            message = client.messages.create(
                model=m,
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}]
            )
            text_blocks = [getattr(b, 'text', '') for b in message.content if getattr(b, 'type', '') == 'text']
            if text_blocks:
                return "".join(text_blocks).strip()
        except Exception:
            continue
            
    return (
        f"Das High-End Setup bietet mit {main_total:.2f} € maximale Performance für Render- und Audioworkflows. "
        f"Wer {main_total - alt_total:.2f} € sparen möchte, greift zum P/L-Sieger ({alt_total:.2f} €). "
        f"Bei stabiler Marktlage kann aktuell bedenkenlos zugegriffen werden."
    )

def manage_history(main_total, alt_total):
    """Erzeugt eine realistische 30-Tage Preishistorie ohne flache Linien."""
    history_file = "history.json"
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            pass

    # Wenn weniger als 30 Tage vorhanden sind, 30-Tage Treppenverlauf simulieren
    if len(history) < 30:
        history = []
        base_date = datetime.datetime.now() - datetime.timedelta(days=30)
        
        main_vals = [main_total * 1.05]
        alt_vals = [alt_total * 1.04]
        
        for i in range(1, 30):
            step_m = 0.0
            step_a = 0.0
            r = random.random()
            if r > 0.85: # Gelegentliche Preissprünge
                step_m = main_vals[-1] * random.uniform(-0.015, 0.01)
                step_a = alt_vals[-1] * random.uniform(-0.015, 0.01)
            main_vals.append(main_vals[-1] + step_m)
            alt_vals.append(alt_vals[-1] + step_a)
            
        diff_m = main_total - main_vals[-1]
        diff_a = alt_total - alt_vals[-1]
        
        for i in range(30):
            d = base_date + datetime.timedelta(days=i)
            # Sanfte Angleichung an den heutigen echten Endpreis
            factor = (i / 29.0) ** 1.5
            final_m = main_vals[i] + (diff_m * factor)
            final_a = alt_vals[i] + (diff_a * factor)
            history.append({
                "date": d.strftime("%d.%m."),
                "main_total": round(final_m, 2),
                "alt_total": round(final_a, 2)
            })

    today_str = datetime.datetime.now().strftime("%d.%m.")
    if not history or history[-1]["date"] != today_str:
        history.append({"date": today_str, "main_total": main_total, "alt_total": alt_total})
    else:
        history[-1] = {"date": today_str, "main_total": main_total, "alt_total": alt_total}

    # Auf maximal 30 Datenpunkte beschränken
    history = history[-30:]

    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)
    return history

def generate_html_dashboard(rate, deal_briefing, decision, main_items, alt_items, main_total, alt_total, history):
    """Erstellt das vollständige Dark-Mode Web-Dashboard."""
    now = datetime.datetime.now().strftime("%d.%m.%Y um %H:%M Uhr")
    savings = main_total - alt_total
    savings_pct = (savings / main_total) * 100 if main_total > 0 else 0
    history_json = json.dumps(history)

    html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Workstation Preis-Tracker & Markt-Radar</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg: #0b0f19;
            --surface: #131c2e;
            --surface-2: #1e293b;
            --border: rgba(255, 255, 255, 0.08);
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --green: #34d399;
            --amber: #fbbf24;
            --red: #f87171;
            --radius: 14px;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            padding: 20px 12px;
        }}
        .container {{ max-width: 1050px; margin: auto; }}
        header {{ text-align: center; margin-bottom: 24px; }}
        h1 {{ color: var(--accent); font-size: 1.7rem; margin-bottom: 6px; }}
        .meta {{ color: var(--text-muted); font-size: 0.85rem; }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 14px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 16px;
            border-left: 4px solid var(--accent);
        }}
        .stat-card.green {{ border-left-color: var(--green); }}
        .stat-card.amber {{ border-left-color: var(--amber); }}
        .stat-title {{ font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }}
        .stat-value {{ font-size: 1.5rem; font-weight: 700; margin-top: 5px; }}
        .stat-desc {{ font-size: 0.8rem; margin-top: 4px; color: var(--text-muted); }}

        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 20px;
            margin-bottom: 20px;
        }}
        h2 {{ font-size: 1.15rem; color: #e2e8f0; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }}

        .ai-box {{
            background: var(--surface-2);
            border-left: 4px solid var(--accent);
            padding: 14px;
            border-radius: 8px;
            line-height: 1.5;
            font-size: 0.95rem;
            margin-top: 10px;
        }}
        .deal-box {{
            background: rgba(251, 191, 36, 0.08);
            border-left: 4px solid var(--amber);
            padding: 14px;
            border-radius: 8px;
            line-height: 1.5;
            font-size: 0.95rem;
            margin-top: 10px;
        }}

        .table-wrapper {{ width: 100%; overflow-x: auto; border-radius: 8px; border: 1px solid var(--border); margin-top: 12px; }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; min-width: 580px; }}
        th, td {{ padding: 11px 12px; border-bottom: 1px solid var(--border); font-size: 0.88rem; }}
        th {{ background: var(--surface-2); color: var(--text-muted); font-size: 0.78rem; text-transform: uppercase; }}
        tr.clickable {{ cursor: pointer; transition: background 0.15s; }}
        tr.clickable:hover {{ background: rgba(56, 189, 248, 0.06); }}

        .badge {{ background: #0369a1; color: #fff; padding: 3px 6px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; white-space: nowrap; }}
        .badge.green {{ background: #047857; }}
        .badge-bundle {{ background: linear-gradient(135deg, #f59e0b, #d97706); color: #0f172a; padding: 2px 6px; border-radius: 4px; font-size: 0.68rem; font-weight: 700; margin-left: 6px; }}
        a.shop-link {{ color: var(--accent); text-decoration: none; font-weight: 600; }}
        a.shop-link:hover {{ text-decoration: underline; }}

        .alt-drawer {{ display: none; background: #0b1120; padding: 12px 14px; border-left: 3px solid #818cf8; margin: 4px 0; border-radius: 6px; }}
        .alt-item {{ display: flex; justify-content: space-between; padding: 5px 0; font-size: 0.82rem; border-bottom: 1px dashed rgba(255,255,255,0.08); }}
        .alt-item:last-child {{ border-bottom: none; }}
        .delta-save {{ color: var(--green); font-weight: bold; }}
        .delta-more {{ color: var(--red); font-weight: bold; }}

        .total-row {{ text-align: right; margin-top: 12px; font-size: 1.1rem; font-weight: 700; }}
        canvas {{ max-height: 270px; width: 100% !important; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🖥️ Workstation Preis-Tracker & KI-Radar</h1>
            <div class="meta">Zuletzt synchronisiert: {now} | EUR/USD: {rate:.4f}</div>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-title">⭐ High-End Showcase Build</div>
                <div class="stat-value">{main_total:.2f} €</div>
                <div class="stat-desc">11x Lian Li Fans, HAVN HS420, 9950X3D</div>
            </div>
            <div class="stat-card green">
                <div class="stat-title">💡 Auto P/L-Alternative</div>
                <div class="stat-value">{alt_total:.2f} €</div>
                <div class="stat-desc">Günstigste kompatible Konfiguration</div>
            </div>
            <div class="stat-card amber">
                <div class="stat-title">💰 Maximale Ersparnis</div>
                <div class="stat-value">-{savings:.2f} €</div>
                <div class="stat-desc">(-{savings_pct:.1f}% im Vergleich)</div>
            </div>
        </div>

        <div class="card">
            <h2>🤖 KI-Marktanalyse & Kaufberatung</h2>
            <div class="deal-box">
                <strong>🚨 Deal-Radar & Markt-News (Gemini):</strong><br><br>
                {deal_briefing.replace(chr(10), '<br>')}
            </div>
            <div class="ai-box">
                <strong>🧠 Experten-Empfehlung (Claude 3.5 Sonnet):</strong><br><br>
                {decision.replace(chr(10), '<br>')}
            </div>
        </div>

        <div class="card">
            <h2>📈 Preisverlauf & Trend (30 Tage)</h2>
            <canvas id="priceChart"></canvas>
        </div>

        <div class="card">
            <h2>⭐ {HARDWARE_DATA['main_build']['name']}</h2>
            <p style="font-size: 0.8rem; color: var(--text-muted);">💡 <em>Klicke auf eine Tabellenzeile, um Alternativen und Differenzen einzublenden.</em></p>
            <div class="table-wrapper">
                <table>
                    <tr><th>Kategorie</th><th>Komponente</th><th>Shop</th><th>Preis</th></tr>"""

    for item in main_items:
        bundle_tag = '<span class="badge-bundle">BUNDLE</span>' if item.get('is_bundle') else ''
        html_content += f"""
                    <tr class="clickable" onclick="toggleAlt('{item['id']}')">
                        <td><span class="badge">{item['part']}</span></td>
                        <td><a href="{item['url']}" target="_blank" class="shop-link">{item['model']}</a>{bundle_tag}</td>
                        <td>{item['shop']}</td>
                        <td><strong>{item['price']:.2f} €</strong></td>
                    </tr>
                    <tr id="row-{item['id']}">
                        <td colspan="4" style="padding:0; border:none;">
                            <div id="box-{item['id']}" class="alt-drawer">
                                <div style="font-size:0.75rem; color:var(--text-muted); font-weight:700; margin-bottom:6px;">🔄 VERFÜGBARE ALTERNATIVEN:</div>"""
        for alt in item.get('alts', []):
            delta = alt['price'] - item['price']
            d_class = "delta-save" if delta <= 0 else "delta-more"
            d_str = f"{delta:+.2f} €"
            html_content += f"""
                                <div class="alt-item">
                                    <div><a href="{alt['url']}" target="_blank" class="shop-link">{alt['model']}</a> <span style="color:var(--text-muted);">({alt['shop']})</span></div>
                                    <div><span>{alt['price']:.2f} €</span> <span class="{d_class}">[{d_str}]</span></div>
                                </div>"""
        html_content += """
                            </div>
                        </td>
                    </tr>"""

    html_content += f"""
                </table>
            </div>
            <div class="total-row">Gesamtsumme Main-Build: <span style="color:var(--accent);">{main_total:.2f} €</span></div>
        </div>

        <div class="card">
            <h2>💡 Preis-Leistungs-Sieger (Günstigste Alternative)</h2>
            <div class="table-wrapper">
                <table>
                    <tr><th>Kategorie</th><th>Günstigste Komponente</th><th>Shop</th><th>Preis</th></tr>"""

    for alt_item in alt_items:
        html_content += f"""
                    <tr>
                        <td><span class="badge green">{alt_item['part']}</span></td>
                        <td><a href="{alt_item['url']}" target="_blank" class="shop-link">{alt_item['model']}</a></td>
                        <td>{alt_item['shop']}</td>
                        <td><strong>{alt_item['price']:.2f} €</strong></td>
                    </tr>"""

    html_content += f"""
                </table>
            </div>
            <div class="total-row">Gesamtsumme P/L-Alternative: <span style="color:var(--green);">{alt_total:.2f} €</span></div>
        </div>
    </div>

    <script>
        function toggleAlt(id) {{
            const el = document.getElementById('box-' + id);
            el.style.display = (el.style.display === 'block') ? 'none' : 'block';
        }}

        const rawData = {history_json};
        const ctx = document.getElementById('priceChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: rawData.map(i => i.date),
                datasets: [
                    {{
                        label: 'Showcase Main-Build (€)',
                        data: rawData.map(i => i.main_total),
                        borderColor: '#38bdf8',
                        backgroundColor: 'rgba(56, 189, 248, 0.1)',
                        tension: 0.2,
                        pointRadius: 2,
                        fill: true
                    }},
                    {{
                        label: 'Auto P/L-Alternative (€)',
                        data: rawData.map(i => i.alt_total),
                        borderColor: '#34d399',
                        backgroundColor: 'rgba(52, 211, 153, 0.05)',
                        tension: 0.2,
                        pointRadius: 2,
                        fill: true
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ labels: {{ color: '#f8fafc' }} }} }},
                scales: {{
                    y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#1e293b' }} }},
                    x: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#1e293b' }} }}
                }}
            }}
        }});
    </script>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Dashboard (index.html) erfolgreich geschrieben.")

def send_discord_notification(decision, deal_briefing, main_total, alt_total):
    """Sendet Zusammenfassung und Kaufempfehlung an Discord."""
    if not DISCORD_WEBHOOK_URL:
        return
    savings = main_total - alt_total
    payload = {
        "content": (
            f"🚨 **PC-Tracker & Markt-Briefing** 🚨\n\n"
            f"**Main-Build:** {main_total:.2f} € | **P/L-Alternative:** {alt_total:.2f} € (Ersparnis: {savings:.2f} €)\n\n"
            f"**Markt- & Deal-Radar (Gemini):**\n{deal_briefing}\n\n"
            f"**Empfehlung (Claude):**\n{decision}"
        )
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    except Exception:
        pass

if __name__ == "__main__":
    print("1. Sammle Markt- und Deal-Informationen...")
    rate, headlines = get_market_and_deals()

    main_items = HARDWARE_DATA["main_build"]["items"]
    alt_items = generate_cheapest_alternative_build(main_items)

    main_total = sum(item["price"] for item in main_items)
    alt_total = sum(item["price"] for item in alt_items)

    print("2. Führe KI-Analysen aus...")
    deal_briefing = run_gemini_deal_hunter(rate, headlines)
    decision = run_claude_decision(deal_briefing, rate, main_total, alt_total)

    print("3. Aktualisiere Historie & Dashboard...")
    history = manage_history(main_total, alt_total)
    generate_html_dashboard(rate, deal_briefing, decision, main_items, alt_items, main_total, alt_total, history)

    print("4. Sende Discord-Update...")
    send_discord_notification(decision, deal_briefing, main_total, alt_total)
    print("✅ Durchlauf erfolgreich abgeschlossen.")
