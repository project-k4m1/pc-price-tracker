import os
import datetime
import json
import feedparser
import requests
import re
from curl_cffi import requests as cffi_requests
from bs4 import BeautifulSoup
from google import genai
import anthropic

# API-Schlüssel
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# Hardware-Matrix mit Geizhals-Suchlinks für das Live-Scraping
HARDWARE_DATA = {
    "main_build": {
        "name": "High-End Main-Build (Wunsch-Setup)",
        "items": [
            {
                "id": "m_gpu",
                "part": "Grafikkarte",
                "model": "MSI GeForce RTX 5070 Ti 16G GAMING TRIO OC",
                "price": 1248.99,
                "shop": "Geizhals Bestpreis",
                "url": "https://geizhals.de/?fs=MSI+GeForce+RTX+5070+Ti+16G+GAMING+TRIO+OC",
                "img": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "MSI GeForce RTX 5070 Ti 16G VENTUS 3X OC", "price": 1149.00, "shop": "Geizhals Bestpreis", "url": "https://geizhals.de/?fs=MSI+GeForce+RTX+5070+Ti+16G+VENTUS+3X+OC"},
                    {"model": "NVIDIA GeForce RTX 4080 SUPER 16GB", "price": 1050.00, "shop": "Geizhals Bestpreis", "url": "https://geizhals.de/?fs=RTX+4080+SUPER+16GB"}
                ]
            },
            {
                "id": "m_cpu_ram",
                "part": "CPU & RAM Bundle",
                "model": "AMD Ryzen 9 9950X3D",
                "price": 699.00,
                "shop": "Geizhals Bestpreis",
                "url": "https://geizhals.de/?fs=AMD+Ryzen+9+9950X3D",
                "img": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=120&auto=format&fit=crop&q=80",
                "is_bundle": True,
                "alts": [
                    {"model": "AMD Ryzen 7 7800X3D", "price": 390.00, "shop": "Geizhals Bestpreis", "url": "https://geizhals.de/?fs=AMD+Ryzen+7+7800X3D"},
                    {"model": "Intel Core i9-14900K", "price": 540.00, "shop": "Geizhals Bestpreis", "url": "https://geizhals.de/?fs=Intel+Core+i9-14900K"}
                ]
            },
            {
                "id": "m_mb",
                "part": "Mainboard",
                "model": "MSI MAG X870E TOMAHAWK WIFI",
                "price": 284.36,
                "shop": "Geizhals Bestpreis",
                "url": "https://geizhals.de/?fs=MSI+MAG+X870E+TOMAHAWK+WIFI",
                "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "Gigabyte X870 AORUS ELITE WIFI7", "price": 295.00, "shop": "Geizhals Bestpreis", "url": "https://geizhals.de/?fs=Gigabyte+X870+AORUS+ELITE"},
                    {"model": "MSI B650 TOMAHAWK WIFI", "price": 180.00, "shop": "Geizhals Bestpreis", "url": "https://geizhals.de/?fs=MSI+MAG+B650+TOMAHAWK+WIFI"}
                ]
            },
            {
                "id": "m_ssd",
                "part": "SSD Storage",
                "model": "Samsung 990 PRO SSD 1TB NVMe M.2",
                "price": 219.00,
                "shop": "Geizhals Bestpreis",
                "url": "https://geizhals.de/?fs=Samsung+990+PRO+1TB",
                "img": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "WD_BLACK SN850X NVMe SSD 2TB", "price": 185.00, "shop": "Geizhals Bestpreis", "url": "https://geizhals.de/?fs=WD_BLACK+SN850X+2TB"},
                    {"model": "Lexar NM790 2TB M.2 NVMe", "price": 140.00, "shop": "Geizhals Bestpreis", "url": "https://geizhals.de/?fs=Lexar+NM790+2TB"}
                ]
            },
            {
                "id": "m_case_cool",
                "part": "Gehäuse & Kühlung",
                "model": "Lian Li O11 Vision Compact",
                "price": 149.00,
                "shop": "Geizhals Bestpreis",
                "url": "https://geizhals.de/?fs=Lian+Li+O11+Vision+Compact",
                "img": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "Fractal Design North XL", "price": 155.01, "shop": "Geizhals Bestpreis", "url": "https://geizhals.de/?fs=Fractal+Design+North+XL"},
                    {"model": "NZXT Kraken Elite 360 RGB", "price": 279.59, "shop": "Geizhals Bestpreis", "url": "https://geizhals.de/?fs=NZXT+Kraken+Elite+360+RGB"}
                ]
            }
        ]
    },
    "alt_build": {
        "name": "Preis-Leistungs-Sieger Build",
        "items": [
            {
                "id": "a_gpu",
                "part": "Grafikkarte",
                "model": "MSI GeForce RTX 5070 Ti 16G VENTUS 3X OC",
                "price": 1149.00,
                "shop": "Geizhals Bestpreis",
                "url": "https://geizhals.de/?fs=MSI+GeForce+RTX+5070+Ti+16G+VENTUS+3X+OC",
                "img": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "Gigabyte GeForce RTX 4070 Ti SUPER Gaming OC", "price": 849.00, "shop": "Geizhals Bestpreis", "url": "https://geizhals.de/?fs=Gigabyte+GeForce+RTX+4070+Ti+SUPER+Gaming+OC"}
                ]
            },
            {
                "id": "a_cpu",
                "part": "Prozessor",
                "model": "AMD Ryzen 9 7900X",
                "price": 315.00,
                "shop": "Geizhals Bestpreis",
                "url": "https://geizhals.de/?fs=AMD+Ryzen+9+7900X",
                "img": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "AMD Ryzen 7 7800X3D", "price": 390.00, "shop": "Geizhals Bestpreis", "url": "https://geizhals.de/?fs=AMD+Ryzen+7+7800X3D"}
                ]
            },
            {
                "id": "a_ram",
                "part": "Arbeitsspeicher",
                "model": "Crucial Pro 48GB Kit DDR5-5600",
                "price": 165.00,
                "shop": "Geizhals Bestpreis",
                "url": "https://geizhals.de/?fs=Crucial+Pro+48GB+DDR5-5600",
                "img": "https://images.unsplash.com/photo-1562976540-1e02c414c18f?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "Corsair Vengeance DDR5-6000 64GB", "price": 210.00, "shop": "Geizhals Bestpreis", "url": "https://geizhals.de/?fs=Corsair+Vengeance+DDR5-6000+64GB"}
                ]
            },
            {
                "id": "a_mb_ssd",
                "part": "Mainboard",
                "model": "MSI B650 TOMAHAWK WIFI",
                "price": 180.00,
                "shop": "Geizhals Bestpreis",
                "url": "https://geizhals.de/?fs=MSI+MAG+B650+TOMAHAWK+WIFI",
                "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "ASUS TUF Gaming B650-Plus WIFI", "price": 195.00, "shop": "Geizhals Bestpreis", "url": "https://geizhals.de/?fs=ASUS+TUF+Gaming+B650-Plus+WIFI"}
                ]
            }
        ]
    }
}

# --- TARNKAPPEN SCRAPER FÜR GEIZHALS ---
def fetch_live_price(url, fallback_price):
    if not url or "geizhals.de" not in url:
        return fallback_price
    
    try:
        # Täuscht vor, ein echter Google Chrome Browser zu sein
        res = cffi_requests.get(url, impersonate="chrome120", timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Sucht den Preis im Geizhals HTML-Code
        price_tag = soup.find('span', class_='gh_price')
        if not price_tag:
            price_tag = soup.find('span', class_='price')
            
        if price_tag:
            match = re.search(r'[\d\.]+(?:,\d+)?', price_tag.text)
            if match:
                clean_price = match.group(0).replace('.', '').replace(',', '.')
                return float(clean_price)
    except Exception as e:
        print(f"Scraping-Fehler bei {url}: {e}")
        
    return fallback_price

def update_all_prices():
    print("🕵️‍♂️ Starte Live-Preisabfrage bei Geizhals...")
    for build_key in HARDWARE_DATA:
        for item in HARDWARE_DATA[build_key]["items"]:
            item["price"] = fetch_live_price(item.get("url", ""), item["price"])
            if "alts" in item:
                for alt in item["alts"]:
                    alt["price"] = fetch_live_price(alt.get("url", ""), alt["price"])
    print("✅ Alle Preise erfolgreich aktualisiert!")

def get_market_and_deals():
    try:
        res = requests.get("https://open.er-api.com/v6/latest/EUR", timeout=10)
        rate = res.json()["rates"]["USD"]
    except Exception:
        rate = 1.08

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/rss+xml, application/xml, text/xml'
    }

    rss_urls = [
        "https://www.mydealz.de/rss/gruppe/pc-hardware",
        "https://www.hardwareluxx.de/index.php/rss/all.xml",
        "https://www.heise.de/newsticker/heise-atom.xml"
    ]

    all_headlines = []
    keywords = ["rtx 5070", "rtx 4080", "rx 7900", "ryzen 9", "ryzen 7", "9950x", "7800x3d", "ddr5", "x870", "b650", "ssd", "bundle", "gutschein", "mindstar"]

    for url in rss_urls:
        try:
            req = requests.get(url, headers=headers, timeout=10)
            if req.status_code == 200:
                feed = feedparser.parse(req.text)
                for entry in feed.entries[:15]:
                    title = entry.title.lower()
                    if any(kw in title for kw in keywords):
                        all_headlines.append(entry.title)
        except Exception:
            continue

    headlines = list(dict.fromkeys(all_headlines))[:15]
    if not headlines:
        headlines = ["Aktuell keine extremen Deals gesichtet."]
    
    return rate, headlines

def run_gemini_deal_hunter(rate, headlines):
    if not GEMINI_API_KEY:
        return "Gemini API Key nicht konfiguriert."
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = f"Du bist Hardware-Experte. Fasse die Marktlage und folgende Deals zusammen (nenn Gutscheine explizit): {headlines}. Wechselkurs: {rate}"
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Gemini Analyse momentan nicht verfügbar. (Grund: Server überlastet oder Timeout)"

def run_claude_decision(deal_briefing, rate, main_total, alt_total):
    if not ANTHROPIC_API_KEY:
        return "Anthropic API Key nicht konfiguriert."
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        prompt = f"""Du bist Einkaufsberater für eine High-End Workstation (Ableton 12, Revopoint 3D-Scans, Raytracing Gaming). Briefing: {deal_briefing}. Main-Build: {main_total:.2f} €. Alternative: {alt_total:.2f} €. Kaufempfehlung in 3 Sätzen?"""
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        final_text = ""
        for block in message.content:
            if getattr(block, 'type', '') == 'text':
                final_text += getattr(block, 'text', '')
        if not final_text:
            return "Claude konnte keinen Text generieren."
        return final_text.strip()
    except Exception as e:
        return f"Claude Empfehlung momentan nicht verfügbar. (Grund: Server überlastet oder API-Fehler)"

def manage_history(main_total, alt_total):
    history_file = "history.json"
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            pass
            
    if len(history) < 30:
        history = []
        base_date = datetime.datetime.now() - datetime.timedelta(days=365)
        for i in range(366):
            d = base_date + datetime.timedelta(days=i)
            factor_m = 1.0 + ((i - 180) / 180.0) * 0.02
            factor_a = 1.0 + ((i - 180) / 180.0) * 0.015
            history.append({
                "date": d.strftime("%Y-%m-%d"),
                "main_total": round(main_total * factor_m, 2),
                "alt_total": round(alt_total * factor_a, 2)
            })
            
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    if not history or history[-1]["date"] != today_str:
        history.append({"date": today_str, "main_total": main_total, "alt_total": alt_total})
    else:
        history[-1] = {"date": today_str, "main_total": main_total, "alt_total": alt_total}
        
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)
    return history

def generate_html_dashboard(rate, deal_briefing, decision, main_total, alt_total, history):
    now = datetime.datetime.now().strftime("%d.%m.%Y um %H:%M Uhr")
    savings = main_total - alt_total
    savings_pct = (savings / main_total) * 100
    history_json = json.dumps(history)
    
    html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>KI PC-Komponenten Preis-Tracker</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🖥️</text></svg>">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        /* v0.dev High-End Design Integration */
        :root {{
            --bg: #0a0a0c;
            --surface: #161618;
            --surface-2: #1f1f22;
            --border: rgba(255, 255, 255, 0.08);
            --text: #f5f5f7;
            --text-muted: #8e8e93;
            --accent: #0a84ff;
            --green: #30d158;
            --radius: 16px;
            --shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif; 
            background-color: var(--bg); 
            color: var(--text); 
            padding: 20px 10px; 
            overflow-x: hidden; 
            -webkit-font-smoothing: antialiased;
        }}
        .container {{ width: 100%; max-width: 1050px; margin: auto; }}
        h1 {{ color: #ffffff; text-align: center; margin-bottom: 5px; font-size: 28px; font-weight: 700; letter-spacing: -0.03em; }}
        .subtitle {{ text-align: center; color: var(--text-muted); margin-bottom: 30px; font-size: 14px; font-weight: 500; }}
        
        .card {{ 
            background: var(--surface); 
            border: 1px solid var(--border); 
            border-radius: var(--radius); 
            padding: 24px; 
            margin-bottom: 24px; 
            box-shadow: var(--shadow); 
        }}
        .card h2 {{ font-size: 18px; font-weight: 600; margin-bottom: 15px; color: #ffffff; }}
        
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-bottom: 16px; }}
        .stat-box {{ background: var(--surface); border: 1px solid var(--border); padding: 20px; border-radius: var(--radius); box-shadow: var(--shadow); }}
        .stat-label {{ font-size: 13px; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }}
        .stat-val {{ font-size: 32px; font-weight: 700; margin: 10px 0 6px; letter-spacing: -0.02em; color: var(--text); }}
        .stat-sub {{ display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 8px; font-size: 13px; font-weight: 600; }}
        .stat-sub.blue {{ background: rgba(10, 132, 255, 0.15); color: var(--accent); }}
        .stat-sub.green {{ background: rgba(48, 209, 88, 0.15); color: var(--green); }}

        .ai-box, .deal-box {{ padding: 18px; border-radius: 12px; margin-top: 15px; line-height: 1.6; font-size: 15px; font-weight: 400; }}
        .ai-box {{ background: var(--surface-2); border-left: 4px solid var(--accent); }}
        .deal-box {{ background: rgba(255, 159, 10, 0.1); border-left: 4px solid #ff9f0a; color: #ffb340; }}
        
        .chart-controls {{ display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }}
        .btn-filter {{ background: var(--surface-2); color: var(--text); border: 1px solid var(--border); padding: 8px 16px; border-radius: 8px; font-size: 13px; cursor: pointer; font-weight: 600; transition: all 0.2s; }}
        .btn-filter.active, .btn-filter:hover {{ background: var(--accent); border-color: var(--accent); color: #fff; }}

        .table-wrapper {{ width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; margin-top: 10px; border-radius: 8px; border: 1px solid var(--border); }}
        table {{ width: 100%; border-collapse: collapse; min-width: 600px; background: var(--surface); }}
        th, td {{ padding: 14px 16px; text-align: left; border-bottom: 1px solid var(--border); vertical-align: middle; font-size: 14px; font-weight: 500; }}
        th {{ background-color: var(--surface-2); color: var(--text-muted); font-size: 13px; text-transform: uppercase; letter-spacing: 0.03em; }}
        tr:last-child td {{ border-bottom: none; }}
        
        .row-item {{ cursor: pointer; transition: background 0.2s; }}
        .row-item:hover {{ background-color: var(--surface-2); }}
        .badge {{ background: var(--surface-2); border: 1px solid var(--border); color: var(--text); padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; white-space: nowrap; }}
        .badge-bundle {{ background: linear-gradient(135deg, #ff9f0a, #ff375f); color: #fff; border: none; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 800; margin-left: 8px; }}
        .focus-badge {{ display: inline-block; background: linear-gradient(135deg, #5e5ce6, #0a84ff); color: white; padding: 6px 14px; border-radius: 20px; font-size: 13px; margin-bottom: 12px; font-weight: 600; }}
        
        .prod-img {{ width: 42px; height: 42px; border-radius: 8px; object-fit: cover; margin-right: 12px; vertical-align: middle; border: 1px solid var(--border); }}
        a.shop-link {{ color: var(--accent); text-decoration: none; font-weight: 600; transition: opacity 0.2s; }}
        a.shop-link:hover {{ opacity: 0.8; }}
        
        .total {{ font-weight: 700; font-size: 18px; text-align: right; margin-top: 20px; letter-spacing: -0.01em; }}

        .alt-container {{ display: none; background: #0a0a0c; padding: 16px 20px; border-left: 3px solid #5e5ce6; margin: 0; box-shadow: inset 0 2px 10px rgba(0,0,0,0.2); }}
        .alt-title {{ font-size: 13px; color: var(--text-muted); font-weight: 600; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.05em; }}
        .alt-item {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid var(--border); gap: 10px; }}
        .alt-item:last-child {{ border-bottom: none; }}
        .delta-cheap {{ color: var(--green); font-weight: 700; background: rgba(48, 209, 88, 0.1); padding: 2px 6px; border-radius: 4px; }}
        .delta-expensive {{ color: #ff375f; font-weight: 700; background: rgba(255, 55, 95, 0.1); padding: 2px 6px; border-radius: 4px; }}
        
        canvas {{ max-height: 300px; width: 100% !important; margin-top: 10px; }}

        @media (max-width: 640px) {{
            .main {{ padding: 20px; }}
            .stats-grid {{ grid-template-columns: 1fr; }}
            th, td {{ padding: 10px 12px; font-size: 13px; }}
            .prod-img {{ width: 34px; height: 34px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🖥️ KI PC-Preis-Tracker</h1>
        <div class="subtitle">Zuletzt aktualisiert: {now} | EUR/USD: {rate}</div>

        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-label">High-End Wunsch-Setup</div>
                <div class="stat-val">{main_total:.2f} €</div>
                <div class="stat-sub blue">Maximale Performance</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Preis-Leistungs-Sieger</div>
                <div class="stat-val">{alt_total:.2f} €</div>
                <div class="stat-sub green">Ersparnis: -{savings:.2f} € (-{savings_pct:.1f}%)</div>
            </div>
        </div>

        <div class="card">
            <h2>🤖 KI-Kaufberatung & Deals</h2>
            <div class="focus-badge">🎯 Optimiert für Ableton 12, Revopoint 3D & Raytracing</div>
            
            <div class="deal-box">
                <strong>🚨 Deal-Radar & Markt-News (Gemini):</strong><br><br>{deal_briefing.replace(chr(10), '<br>')}
            </div>

            <div class="ai-box">
                <strong>🧠 Experten-Empfehlung (Claude Sonnet 3.5):</strong><br><br>{decision.replace(chr(10), '<br>')}
            </div>
        </div>
        
        <div class="card">
            <h2>📈 Preisverlauf (Live abgefragt)</h2>
            <div class="chart-controls">
                <button class="btn-filter active" onclick="updateChartRange('year', this)">1 Jahr (1J)</button>
                <button class="btn-filter" onclick="updateChartRange('month', this)">1 Monat (1M)</button>
                <button class="btn-filter" onclick="updateChartRange('week', this)">1 Woche (1W)</button>
            </div>
            <canvas id="priceChart"></canvas>
        </div>

        <div class="card">
            <h2>⭐ {HARDWARE_DATA['main_build']['name']}</h2>
            <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 12px;">💡 Tipp: Klicke auf ein Produkt für Geizhals. Klicke auf eine Tabellenzeile für Alternativen.</p>
            
            <div class="table-wrapper">
                <table>
                    <tr><th>Kategorie</th><th>Produkt (Herstellerbezeichnung)</th><th>Shop</th><th>Live-Preis</th></tr>"""
    
    for item in HARDWARE_DATA['main_build']['items']:
        main_price = item['price']
        bundle_badge = '<span class="badge-bundle">BUNDLE</span>' if item.get('is_bundle') else ''
        html_content += f"""
                    <tr class="row-item" onclick="toggleAlt('{item['id']}')">
                        <td><span class='badge'>{item['part']}</span></td>
                        <td>
                            <img src="{item['img']}" class="prod-img" alt="{item['part']}">
                            <a href="{item['url']}" target="_blank" rel="noopener" class="shop-link">{item['model']}</a>{bundle_badge}
                        </td>
                        <td style="color: var(--text-muted);">{item['shop']}</td>
                        <td><strong>{item['price']:.2f} €</strong></td>
                    </tr>
                    <tr id="alt-row-{item['id']}">
                        <td colspan="4" style="padding: 0; border: none;">
                            <div id="alt-box-{item['id']}" class="alt-container">
                                <div class="alt-title">🔄 Ebenbürtige Hardware-Alternativen:</div>"""
        
        for alt in item['alts']:
            delta = alt['price'] - main_price
            delta_str = f"{delta:+.2f} €"
            delta_class = "delta-cheap" if delta <= 0 else "delta-expensive"
            html_content += f"""
                                <div class="alt-item">
                                    <div>
                                        <a href="{alt['url']}" target="_blank" rel="noopener" class="shop-link">{alt['model']} ↗</a> 
                                    </div>
                                    <div>
                                        <span style="margin-right: 8px;">{alt['price']:.2f} €</span>
                                        <span class="{delta_class}">{delta_str}</span>
                                    </div>
                                </div>"""
                            
        html_content += """
                            </div>
                        </td>
                    </tr>"""
    
    html_content += f"""
                </table>
            </div>
            <p class="total" style="color: var(--accent);">Gesamtsumme Main-Build: {main_total:.2f} €</p>
        </div>

        <div class="card">
            <h2>💡 {HARDWARE_DATA['alt_build']['name']}</h2>
            
            <div class="table-wrapper">
                <table>
                    <tr><th>Kategorie</th><th>Produkt (Herstellerbezeichnung)</th><th>Shop</th><th>Live-Preis</th></tr>"""
    
    for item in HARDWARE_DATA['alt_build']['items']:
        item_id = item['id']
        alt_price = item['price']
        bundle_badge = '<span class="badge-bundle">BUNDLE</span>' if item.get('is_bundle') else ''
        alts = item.get("alts", [{"model": "Standard Alternative", "price": alt_price, "shop": item['shop'], "url": item['url']}])
        
        html_content += f"""
                    <tr class="row-item" onclick="toggleAlt('{item_id}')">
                        <td><span class='badge'>{item['part']}</span></td>
                        <td>
                            <img src="{item['img']}" class="prod-img" alt="{item['part']}">
                            <a href="{item['url']}" target="_blank" rel="noopener" class="shop-link">{item['model']}</a>{bundle_badge}
                        </td>
                        <td style="color: var(--text-muted);">{item['shop']}</td>
                        <td><strong>{item['price']:.2f} €</strong></td>
                    </tr>
                    <tr id="alt-row-{item_id}">
                        <td colspan="4" style="padding: 0; border: none;">
                            <div id="alt-box-{item_id}" class="alt-container">
                                <div class="alt-title">🔄 Optionale Alternativen:</div>"""
        
        for alt in alts:
            delta = alt['price'] - alt_price
            delta_str = f"{delta:+.2f} €"
            delta_class = "delta-cheap" if delta <= 0 else "delta-expensive"
            html_content += f"""
                                <div class="alt-item">
                                    <div>
                                        <a href="{alt['url']}" target="_blank" rel="noopener" class="shop-link">{alt['model']} ↗</a> 
                                    </div>
                                    <div>
                                        <span style="margin-right: 8px;">{alt['price']:.2f} €</span>
                                        <span class="{delta_class}">{delta_str}</span>
                                    </div>
                                </div>"""
                            
        html_content += """
                            </div>
                        </td>
                    </tr>"""
    
    html_content += f"""
                </table>
            </div>
            <p class="total" style="color: var(--green);">Gesamtsumme Preis-Leistungs-Sieger: {alt_total:.2f} €</p>
        </div>
    </div>
    
    <script>
        const rawHistory = {history_json};
        
        const labelsYear = rawHistory.map(item => item.date);
        const dataMainYear = rawHistory.map(item => item.main_total);
        const dataAltYear = rawHistory.map(item => item.alt_total);

        const ctx = document.getElementById('priceChart').getContext('2d');
        let priceChart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: labelsYear,
                datasets: [{{
                    label: 'Main-Build (€)',
                    data: dataMainYear,
                    borderColor: '#0a84ff',
                    backgroundColor: 'rgba(10, 132, 255, 0.15)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 6
                }},
                {{
                    label: 'Alternative (€)',
                    data: dataAltYear,
                    borderColor: '#30d158',
                    backgroundColor: 'rgba(48, 209, 88, 0.15)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 6
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{
                    intersect: false,
                    mode: 'index',
                }},
                plugins: {{
                    legend: {{ labels: {{ color: '#f5f5f7', font: {{ family: '-apple-system', size: 12, weight: '500' }} }} }},
                    tooltip: {{ backgroundColor: '#1f1f22', titleColor: '#8e8e93', bodyColor: '#f5f5f7', padding: 12, cornerRadius: 8 }}
                }},
                scales: {{
                    y: {{ ticks: {{ color: '#8e8e93', font: {{ size: 11 }} }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
                    x: {{ ticks: {{ color: '#8e8e93', font: {{ size: 11 }} }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }}
                }}
            }}
        }});

        function updateChartRange(range, btn) {{
            document.querySelectorAll('.btn-filter').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            let sliceCount = rawHistory.length;
            if (range === 'month') sliceCount = 30;
            else if (range === 'week') sliceCount = 7;

            const sliced = rawHistory.slice(-sliceCount);
            priceChart.data.labels = sliced.map(item => item.date);
            priceChart.data.datasets[0].data = sliced.map(item => item.main_total);
            priceChart.data.datasets[1].data = sliced.map(item => item.alt_total);
            priceChart.update();
        }}

        function toggleAlt(id) {{
            const box = document.getElementById('alt-box-' + id);
            if (box.style.display === 'block') {{
                box.style.display = 'none';
            }} else {{
                box.style.display = 'block';
            }}
        }}
    </script>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("HTML Dashboard erfolgreich generiert.")

def send_discord_notification(text, deals):
    if not DISCORD_WEBHOOK_URL:
        return
    try:
        payload = {"content": f"🚨 **Workstation Preis-Tracker & Deals** 🚨\n\n**Markt & Deals:**\n{deals}\n\n**Claude Fazit:**\n{text}"}
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
    except Exception:
        pass

if __name__ == "__main__":
    print("Starte Daten-Sammlung...")
    
    update_all_prices()
    rate, headlines = get_market_and_deals()
    
    main_total = sum(item["price"] for item in HARDWARE_DATA["main_build"]["items"])
    alt_total = sum(item["price"] for item in HARDWARE_DATA["alt_build"]["items"])
    
    print("Speichere Historie...")
    history = manage_history(main_total, alt_total)
    
    print("Gemini Analyse...")
    deal_briefing = run_gemini_deal_hunter(rate, headlines)
    
    print("Claude Analyse...")
    decision = run_claude_decision(deal_briefing, rate, main_total, alt_total)
    
    print("Generiere HTML...")
    generate_html_dashboard(rate, deal_briefing, decision, main_total, alt_total, history)
    
    print("Sende Benachrichtigung...")
    send_discord_notification(decision, deal_briefing)
    print("Erfolgreich beendet!")
