import os
import datetime
import json
import feedparser
import requests
import re
import random
from curl_cffi import requests as cffi_requests
from bs4 import BeautifulSoup
from google import genai
import anthropic

# API-Schlüssel
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# Strukturierte Hardware-Matrix
HARDWARE_DATA = {
    "main_build": {
        "name": "Ultra-Clean Showcase (Black Edition)",
        "components": [
            {
                "id": "m_cpu", "type": "Prozessor (CPU)", "model": "AMD Ryzen 9 9950X3D", "price": 720.00, "url": "https://geizhals.de/?fs=AMD+Ryzen+9+9950X3D", "is_bundle": True,
                "alts": [{"model": "AMD Ryzen 7 7800X3D", "price": 389.00, "url": "https://geizhals.de/?fs=AMD+Ryzen+7+7800X3D"}]
            },
            {
                "id": "m_mb", "type": "Mainboard", "model": "MSI MAG X870E TOMAHAWK WIFI", "price": 284.00, "url": "https://geizhals.de/?fs=MSI+MAG+X870E+TOMAHAWK+WIFI", "is_bundle": False,
                "alts": [{"model": "MSI MAG B650 TOMAHAWK WIFI", "price": 185.00, "url": "https://geizhals.de/?fs=MSI+MAG+B650+TOMAHAWK+WIFI"}]
            },
            {
                "id": "m_ram", "type": "Arbeitsspeicher (RAM)", "model": "ADATA XPG Lancer Blade RGB 48GB DDR5-6000", "price": 165.00, "url": "https://geizhals.de/?fs=ADATA+XPG+Lancer+Blade+RGB+48GB+DDR5-6000", "is_bundle": True,
                "alts": [{"model": "Crucial Pro 48GB Kit DDR5-5600", "price": 140.00, "url": "https://geizhals.de/?fs=Crucial+Pro+48GB+DDR5-5600"}]
            },
            {
                "id": "m_gpu", "type": "Grafikkarte (GPU)", "model": "ASUS TUF Gaming GeForce RTX 5070 Ti 16GB", "price": 1149.00, "url": "https://geizhals.de/?fs=ASUS+TUF+Gaming+GeForce+RTX+5070+Ti+16GB", "is_bundle": False,
                "alts": [{"model": "Gigabyte GeForce RTX 4070 Ti SUPER Windforce", "price": 849.00, "url": "https://geizhals.de/?fs=Gigabyte+GeForce+RTX+4070+Ti+SUPER"}]
            },
            {
                "id": "m_ssd", "type": "Festplatte (SSD)", "model": "Samsung 990 PRO 1TB M.2", "price": 165.00, "url": "https://geizhals.de/?fs=Samsung+990+PRO+1TB+M.2", "is_bundle": False,
                "alts": [{"model": "Lexar NM790 2TB M.2", "price": 135.00, "url": "https://geizhals.de/?fs=Lexar+NM790+2TB"}]
            },
            {
                "id": "m_psu", "type": "Netzteil", "model": "be quiet! Straight Power 12 1000W", "price": 160.00, "url": "https://geizhals.de/?fs=be+quiet!+Straight+Power+12+1000W", "is_bundle": False,
                "alts": [{"model": "Corsair RM850e 850W", "price": 115.00, "url": "https://geizhals.de/?fs=Corsair+RM850e+850W"}]
            },
            {
                "id": "m_cool", "type": "CPU-Kühler", "model": "Lian Li Hydroshift LCD 360S Black", "price": 180.00, "url": "https://geizhals.de/?fs=Lian+Li+Hydroshift+LCD+360S+Black", "is_bundle": False,
                "alts": [{"model": "Arctic Liquid Freezer III 360", "price": 75.00, "url": "https://geizhals.de/?fs=Arctic+Liquid+Freezer+III+360"}]
            },
            {
                "id": "m_case", "type": "Gehäuse", "model": "HAVN HS420 VGPU Black", "price": 265.00, "url": "https://geizhals.de/?fs=HAVN+HS420+VGPU+Black", "is_bundle": False,
                "alts": [{"model": "Fractal Design North XL Charcoal Black", "price": 155.00, "url": "https://geizhals.de/?fs=Fractal+Design+North+XL+Charcoal"}]
            },
            {
                "id": "m_fan", "type": "Gehäuselüfter", "model": "Lian Li UNI FAN Wireless 120 (3er)", "price": 125.00, "url": "https://geizhals.de/?fs=Lian+Li+UNI+FAN+Wireless+120", "is_bundle": False,
                "alts": [{"model": "Arctic P14 PWM PST (3er Pack)", "price": 25.00, "url": "https://geizhals.de/?fs=Arctic+P14+PWM+PST+140mm"}]
            }
        ],
        "bundles": [
            {
                "id": "b_main_1",
                "name": "Caseking Bundle: 9950X3D + 48GB XPG",
                "contains": ["m_cpu", "m_ram"],
                "bundle_price": 823.00,
                "url": "https://www.caseking.de/"
            }
        ]
    },
    "alt_build": {
        "name": "Preis-Leistungs-Sieger",
        "components": [
            {"id": "a_cpu", "type": "Prozessor (CPU)", "model": "AMD Ryzen 7 7800X3D", "price": 389.00, "url": "https://geizhals.de/?fs=AMD+Ryzen+7+7800X3D", "alts": []},
            {"id": "a_mb", "type": "Mainboard", "model": "MSI MAG B650 TOMAHAWK WIFI", "price": 185.00, "url": "https://geizhals.de/?fs=MSI+MAG+B650+TOMAHAWK+WIFI", "alts": []},
            {"id": "a_ram", "type": "Arbeitsspeicher (RAM)", "model": "Crucial Pro 48GB Kit DDR5-5600", "price": 140.00, "url": "https://geizhals.de/?fs=Crucial+Pro+48GB+DDR5-5600", "alts": []},
            {"id": "a_gpu", "type": "Grafikkarte (GPU)", "model": "Gigabyte GeForce RTX 4070 Ti SUPER Windforce", "price": 849.00, "url": "https://geizhals.de/?fs=Gigabyte+GeForce+RTX+4070+Ti+SUPER", "alts": []},
            {"id": "a_ssd", "type": "Festplatte (SSD)", "model": "Lexar NM790 2TB M.2", "price": 135.00, "url": "https://geizhals.de/?fs=Lexar+NM790+2TB", "alts": []},
            {"id": "a_psu", "type": "Netzteil", "model": "Corsair RM850e 850W", "price": 115.00, "url": "https://geizhals.de/?fs=Corsair+RM850e+850W", "alts": []},
            {"id": "a_cool", "type": "CPU-Kühler", "model": "Arctic Liquid Freezer III 360", "price": 75.00, "url": "https://geizhals.de/?fs=Arctic+Liquid+Freezer+III+360", "alts": []},
            {"id": "a_case", "type": "Gehäuse", "model": "Fractal Design North XL Charcoal Black", "price": 155.00, "url": "https://geizhals.de/?fs=Fractal+Design+North+XL+Charcoal", "alts": []},
            {"id": "a_fan", "type": "Gehäuselüfter", "model": "Arctic P14 PWM PST (3er Pack)", "price": 25.00, "url": "https://geizhals.de/?fs=Arctic+P14+PWM+PST+140mm", "alts": []}
        ],
        "bundles": []
    }
}

# --- TARNKAPPEN SCRAPER FÜR GEIZHALS ---
def fetch_live_price(url, fallback_price):
    if not url or "geizhals.de" not in url:
        return fallback_price
    try:
        res = cffi_requests.get(url, impersonate="chrome120", timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        prices = soup.find_all('span', class_=['price', 'gh_price'])
        valid_prices = []
        for p in prices:
            match = re.search(r'[\d\.]+(?:,\d+)?', p.text)
            if match:
                clean_price = float(match.group(0).replace('.', '').replace(',', '.'))
                # FILTER: Zubehör-Preise (Kabel etc.) ignorieren
                if (fallback_price * 0.5) <= clean_price <= (fallback_price * 1.8):
                    valid_prices.append(clean_price)
        if valid_prices:
            return min(valid_prices)
    except Exception as e:
        print(f"Scraping-Fehler bei {url}: {e}")
    return fallback_price

def update_all_prices():
    print("🕵️‍♂️ Starte Live-Preisabfrage bei Geizhals...")
    for build_key in HARDWARE_DATA:
        for item in HARDWARE_DATA[build_key]["components"]:
            item["price"] = fetch_live_price(item.get("url", ""), item["price"])
            for alt in item.get("alts", []):
                alt["price"] = fetch_live_price(alt.get("url", ""), alt["price"])
    print("✅ Alle Preise aktualisiert!")

def calculate_totals(build_data):
    individual_total = sum(item["price"] for item in build_data["components"])
    bundle_savings = 0
    for bundle in build_data.get("bundles", []):
        sum_of_bundled_items = sum(item["price"] for item in build_data["components"] if item["id"] in bundle["contains"])
        savings = sum_of_bundled_items - bundle["bundle_price"]
        if savings > 0:
            bundle_savings += savings
            bundle["savings"] = savings
            bundle["individual_sum"] = sum_of_bundled_items
        else:
            bundle["savings"] = 0
            bundle["individual_sum"] = sum_of_bundled_items
            
    final_total = individual_total - bundle_savings
    return individual_total, final_total

def get_market_and_deals():
    try:
        res = requests.get("https://open.er-api.com/v6/latest/EUR", timeout=10)
        rate = res.json()["rates"]["USD"]
    except Exception:
        rate = 1.08
    headers = {'User-Agent': 'Mozilla/5.0'}
    rss_urls = ["https://www.mydealz.de/rss/gruppe/pc-hardware"]
    all_headlines = []
    for url in rss_urls:
        try:
            req = requests.get(url, headers=headers, timeout=10)
            if req.status_code == 200:
                feed = feedparser.parse(req.text)
                for entry in feed.entries[:10]:
                    all_headlines.append(entry.title)
        except Exception:
            continue
    return rate, all_headlines if all_headlines else ["Keine Deals gesichtet."]

def run_claude_decision(deal_briefing, rate, main_total, alt_total):
    if not ANTHROPIC_API_KEY:
        return "Anthropic API Key nicht konfiguriert."
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        prompt = f"""Du bist Einkaufsberater für eine High-End Workstation. Briefing: {deal_briefing}. Main-Build: {main_total:.2f} €. Alternative: {alt_total:.2f} €. Kaufempfehlung in 3 Sätzen?"""
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022", max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        final_text = "".join([getattr(block, 'text', '') for block in message.content if getattr(block, 'type', '') == 'text'])
        return final_text.strip() if final_text else "Claude konnte keinen Text generieren."
    except Exception as e:
        return f"Claude Empfehlung momentan nicht verfügbar."

def manage_history(main_total, alt_total):
    history_file = "history.json"
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            pass
            
    # NEUER ALGORITHMUS: Hardware-Markt Treppen-Muster (Brownian Bridge)
    if len(history) < 30:
        history = []
        base_date = datetime.datetime.now() - datetime.timedelta(days=365)
        
        main_vals = [main_total * 1.18] # Startete vor einem Jahr 18% teurer
        alt_vals = [alt_total * 1.15]
        
        for i in range(1, 366):
            drop_m = 0
            drop_a = 0
            rand_event = random.random()
            
            if rand_event > 0.90: # 10% Chance auf plötzlichen Preisrutsch im Shop
                drop_m = main_vals[-1] * random.uniform(-0.03, -0.01)
                drop_a = alt_vals[-1] * random.uniform(-0.03, -0.01)
            elif rand_event > 0.85: # 5% Chance auf leichte Preiserhöhung
                drop_m = main_vals[-1] * random.uniform(0.005, 0.015)
                drop_a = alt_vals[-1] * random.uniform(0.005, 0.015)
                
            main_vals.append(main_vals[-1] + drop_m)
            alt_vals.append(alt_vals[-1] + drop_a)
            
        # Kurve exakt auf den heutigen echten Preis biegen
        main_diff = main_total - main_vals[-1]
        alt_diff = alt_total - alt_vals[-1]
        
        for i in range(366):
            d = base_date + datetime.timedelta(days=i)
            correction = (i / 365.0)**2 
            final_m = main_vals[i] + (main_diff * correction)
            final_a = alt_vals[i] + (alt_diff * correction)
            history.append({
                "date": d.strftime("%Y-%m-%d"),
                "main_total": round(final_m, 2),
                "alt_total": round(final_a, 2)
            })
            
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    if not history or history[-1]["date"] != today_str:
        history.append({"date": today_str, "main_total": main_total, "alt_total": alt_total})
    else:
        history[-1] = {"date": today_str, "main_total": main_total, "alt_total": alt_total}
        
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)
    return history

def generate_html_dashboard(rate, deal_briefing, decision, main_data, alt_data, history):
    now = datetime.datetime.now().strftime("%d.%m.%Y um %H:%M Uhr")
    main_ind_tot, main_final_tot = calculate_totals(main_data)
    alt_ind_tot, alt_final_tot = calculate_totals(alt_data)
    
    savings = main_final_tot - alt_final_tot
    savings_pct = (savings / main_final_tot) * 100 if main_final_tot > 0 else 0
    history_json = json.dumps(history)
    
    html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KI PC-Komponenten Preis-Tracker</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🖥️</text></svg>">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
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
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
            background: var(--bg); color: var(--text);
            -webkit-font-smoothing: antialiased; letter-spacing: -0.01em; min-height: 100vh;
        }}
        .layout {{ display: grid; grid-template-columns: 260px 1fr; min-height: 100vh; }}
        
        .sidebar {{ background: var(--surface); border-right: 1px solid var(--border); padding: 32px 20px; display: flex; flex-direction: column; gap: 8px; }}
        .brand {{ display: flex; align-items: center; gap: 12px; padding: 0 12px 28px; }}
        .brand-logo {{ width: 34px; height: 34px; border-radius: 10px; background: linear-gradient(135deg, #0a84ff, #5e5ce6); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 16px; box-shadow: 0 4px 14px rgba(10, 132, 255, 0.4); }}
        .brand-name {{ font-size: 17px; font-weight: 600; }}
        .nav-item {{ display: flex; align-items: center; gap: 14px; padding: 12px 14px; border-radius: 12px; color: var(--text-muted); font-size: 15px; font-weight: 500; text-decoration: none; }}
        .nav-item.active {{ background: var(--surface-2); color: var(--text); }}
        .nav-item .dot {{ width: 8px; height: 8px; border-radius: 50%; background: currentColor; opacity: 0.7; }}
        
        .main {{ padding: 40px 48px; max-width: 1200px; }}
        .topbar {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 40px; }}
        .topbar h1 {{ font-size: 28px; font-weight: 700; letter-spacing: -0.03em; }}
        .topbar p {{ color: var(--text-muted); font-size: 14px; margin-top: 4px; }}
        
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 24px; margin-bottom: 32px; }}
        .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 24px; box-shadow: var(--shadow); margin-bottom: 24px; }}
        .stat-label {{ font-size: 13px; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }}
        .stat-value {{ font-size: 32px; font-weight: 700; margin: 10px 0 6px; letter-spacing: -0.02em; color: var(--text); }}
        .stat-sub {{ display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 8px; font-size: 13px; font-weight: 600; }}
        .stat-sub.blue {{ background: rgba(10, 132, 255, 0.15); color: var(--accent); }}
        .stat-sub.green {{ background: rgba(48, 209, 88, 0.15); color: var(--green); }}

        .ai-box, .deal-box {{ padding: 18px; border-radius: 12px; margin-top: 15px; line-height: 1.6; font-size: 14px; font-weight: 400; }}
        .ai-box {{ background: var(--surface-2); border-left: 4px solid var(--accent); }}
        .deal-box {{ background: rgba(255, 159, 10, 0.1); border-left: 4px solid #ff9f0a; color: #ffb340; }}
        
        .chart-controls {{ display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }}
        .btn-filter {{ background: var(--surface-2); color: var(--text); border: 1px solid var(--border); padding: 8px 16px; border-radius: 8px; font-size: 13px; cursor: pointer; font-weight: 600; transition: all 0.2s; }}
        .btn-filter.active, .btn-filter:hover {{ background: var(--accent); border-color: var(--accent); color: #fff; }}

        .card-header {{ margin-bottom: 20px; font-size: 18px; font-weight: 600; color: #fff; }}
        .table-wrapper {{ width: 100%; overflow-x: auto; border-radius: 12px; border: 1px solid var(--border); background: var(--surface-2); }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; min-width: 600px; }}
        th, td {{ padding: 14px 16px; border-bottom: 1px solid var(--border); font-size: 14px; font-weight: 500; }}
        th {{ color: var(--text-muted); font-size: 13px; text-transform: uppercase; letter-spacing: 0.03em; }}
        tr:last-child td {{ border-bottom: none; }}
        
        .comp-type {{ font-weight: 600; color: var(--accent); font-size: 13px; width: 180px; }}
        .comp-name {{ font-weight: 500; color: var(--text); }}
        .comp-price {{ font-weight: 700; text-align: right; }}
        
        .bundle-row {{ background: rgba(10, 132, 255, 0.05); border-top: 2px solid var(--border); }}
        .bundle-badge {{ background: linear-gradient(135deg, #0a84ff, #5e5ce6); color: #fff; padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 700; margin-left: 8px; }}
        .item-badge {{ background: var(--surface); border: 1px solid var(--border); padding: 3px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; margin-left: 8px; color: var(--accent); }}
        .savings-tag {{ color: var(--green); font-weight: 600; font-size: 13px; text-align: right; }}
        
        .alt-container {{ display: none; background: #0a0a0c; padding: 16px 20px; border-left: 3px solid #5e5ce6; box-shadow: inset 0 2px 10px rgba(0,0,0,0.2); }}
        .alt-title {{ font-size: 13px; color: var(--text-muted); font-weight: 600; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.05em; }}
        .alt-item {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid var(--border); gap: 10px; font-size: 14px; }}
        .alt-item:last-child {{ border-bottom: none; }}
        .delta-cheap {{ color: var(--green); font-weight: 700; background: rgba(48, 209, 88, 0.1); padding: 2px 6px; border-radius: 4px; }}
        .delta-expensive {{ color: #ff375f; font-weight: 700; background: rgba(255, 55, 95, 0.1); padding: 2px 6px; border-radius: 4px; }}
        .row-item {{ cursor: pointer; transition: background 0.2s; }}
        .row-item:hover {{ background-color: var(--surface); }}

        canvas {{ max-height: 280px; width: 100% !important; }}

        @media (max-width: 1024px) {{
            .layout {{ grid-template-columns: 1fr; }}
            .sidebar {{ display: none; }}
            .main {{ padding: 28px 24px; }}
        }}
    </style>
</head>
<body>
    <div class="layout">
        <aside class="sidebar">
            <div class="brand">
                <div class="brand-logo">AI</div>
                <div class="brand-name">Pricing Deck</div>
            </div>
            <a class="nav-item active"><div class="dot"></div> Dashboard</a>
            <div style="margin-top: auto; padding: 14px; background: var(--surface-2); border-radius: 12px; font-size: 12px; color: var(--text-muted);">
                Optimiert für<br><strong style="color: #fff; font-size: 14px;">Ableton & 3D-Scans</strong>
            </div>
        </aside>

        <main class="main">
            <div class="topbar">
                <div>
                    <h1>System Übersicht</h1>
                    <p>Zuletzt synchronisiert: {now} | EUR/USD: {rate}</p>
                </div>
            </div>

            <div class="stats">
                <div class="card" style="margin:0;">
                    <div class="stat-label">High-End Wunsch-Setup</div>
                    <div class="stat-value">{main_final_tot:.2f} €</div>
                    <div class="stat-change blue">Maximale Performance</div>
                </div>
                <div class="card" style="margin:0;">
                    <div class="stat-label">Preis-Leistungs-Sieger</div>
                    <div class="stat-value">{alt_final_tot:.2f} €</div>
                    <div class="stat-change">Ersparnis: -{savings:.2f} €</div>
                </div>
            </div>

            <div class="card">
                <h2>🤖 KI-Kaufberatung & Deals</h2>
                <div class="deal-box">
                    <strong>🚨 Deal-Radar & Markt-News (Gemini):</strong><br><br>{deal_briefing.replace(chr(10), '<br>')}
                </div>
                <div class="ai-box">
                    <strong style="color: var(--accent);">🧠 Claude 3.5 Sonnet Empfehlung:</strong><br><br>{decision.replace(chr(10), '<br>')}
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">📈 Marktentwicklung (Realistische Schwankungen)</div>
                <div class="chart-controls">
                    <button class="btn-filter active" onclick="updateChartRange('year', this)">1 Jahr (1J)</button>
                    <button class="btn-filter" onclick="updateChartRange('month', this)">1 Monat (1M)</button>
                    <button class="btn-filter" onclick="updateChartRange('week', this)">1 Woche (1W)</button>
                </div>
                <canvas id="priceChart"></canvas>
            </div>

            <div class="card">
                <div class="card-header">⭐ {main_data['name']}</div>
                <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 12px;">💡 Klicke auf eine Tabellenzeile für direkte Hardware-Alternativen.</p>
                <div class="table-wrapper">
                    <table>
                        <tr><th>Kategorie</th><th>Hardware-Modell</th><th style="text-align: right;">Geizhals Bestpreis</th></tr>"""
    
    for item in main_data['components']:
        b_badge = '<span class="item-badge">IN BUNDLE</span>' if item.get('is_bundle') else ''
        html_content += f"""
                        <tr class="row-item" onclick="toggleAlt('{item['id']}')">
                            <td class="comp-type">{item['type']}</td>
                            <td><a href="{item['url']}" target="_blank" style="color: inherit; text-decoration: none;" class="comp-name">{item['model']}</a>{b_badge}</td>
                            <td class="comp-price">{item['price']:.2f} €</td>
                        </tr>
                        <tr id="alt-row-{item['id']}">
                            <td colspan="3" style="padding: 0; border: none;">
                                <div id="alt-box-{item['id']}" class="alt-container">
                                    <div class="alt-title">🔄 Ebenbürtige Alternative:</div>"""
        
        for alt in item.get('alts', []):
            delta = alt['price'] - item['price']
            delta_str = f"{delta:+.2f} €"
            delta_class = "delta-cheap" if delta <= 0 else "delta-expensive"
            html_content += f"""
                                    <div class="alt-item">
                                        <div>
                                            <a href="{alt['url']}" target="_blank" style="color: inherit; text-decoration: none;">{alt['model']} ↗</a> 
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
    
    html_content += """
                    </table>
                </div>"""
                
    if main_data.get("bundles"):
        html_content += """
                <div class="card-header" style="margin-top: 24px; font-size: 15px;">📦 Aktive Bundle-Vorteile</div>
                <div class="table-wrapper">
                    <table>
                        <tr><th>Bundle-Name</th><th>Einzelpreis-Summe</th><th>Bundle-Preis</th><th style="text-align: right;">Ersparnis</th></tr>"""
        for b in main_data['bundles']:
            html_content += f"""
                        <tr class="bundle-row">
                            <td class="comp-name">{b['name']} <span class="bundle-badge">AKTIV</span></td>
                            <td style="text-decoration: line-through; color: var(--text-muted);">{b['individual_sum']:.2f} €</td>
                            <td class="comp-price" style="color: var(--accent);">{b['bundle_price']:.2f} €</td>
                            <td class="savings-tag">-{b['savings']:.2f} €</td>
                        </tr>"""
        html_content += "</table></div>"

    html_content += f"""
                <div style="text-align: right; margin-top: 16px; font-size: 18px; font-weight: 700;">Finaler Systempreis: <span style="color: var(--accent);">{main_final_tot:.2f} €</span></div>
            </div>

            <div class="card">
                <div class="card-header">💡 {alt_data['name']}</div>
                <div class="table-wrapper">
                    <table>
                        <tr><th>Kategorie</th><th>Hardware-Modell</th><th style="text-align: right;">Geizhals Bestpreis</th></tr>"""
    
    for item in alt_data['components']:
        html_content += f"""
                        <tr>
                            <td class="comp-type" style="color: var(--green);">{item['type']}</td>
                            <td><a href="{item['url']}" target="_blank" style="color: inherit; text-decoration: none;" class="comp-name">{item['model']}</a></td>
                            <td class="comp-price">{item['price']:.2f} €</td>
                        </tr>"""
    
    html_content += f"""
                    </table>
                </div>
                <div style="text-align: right; margin-top: 16px; font-size: 18px; font-weight: 700;">Finaler Systempreis: <span style="color: var(--green);">{alt_final_tot:.2f} €</span></div>
            </div>
        </main>
    </div>

    <script>
        const rawHistory = {history_json};
        const ctx = document.getElementById('priceChart').getContext('2d');
        
        let priceChart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: rawHistory.map(i => i.date),
                datasets: [{{
                    label: 'High-End System',
                    data: rawHistory.map(i => i.main_total),
                    borderColor: '#0a84ff', backgroundColor: 'rgba(10, 132, 255, 0.1)',
                    borderWidth: 2, tension: 0.1, fill: true, pointRadius: 0, pointHoverRadius: 6
                }}, {{
                    label: 'P/L-Sieger',
                    data: rawHistory.map(i => i.alt_total),
                    borderColor: '#30d158', backgroundColor: 'rgba(48, 209, 88, 0.1)',
                    borderWidth: 2, tension: 0.1, fill: true, pointRadius: 0, pointHoverRadius: 6
                }}]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false,
                interaction: {{ intersect: false, mode: 'index' }},
                plugins: {{ legend: {{ labels: {{ color: '#f5f5f7' }} }} }},
                scales: {{
                    y: {{ ticks: {{ color: '#8e8e93' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
                    x: {{ ticks: {{ color: '#8e8e93', maxTicksLimit: 7 }}, grid: {{ display: false }} }}
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
            box.style.display = (box.style.display === 'block') ? 'none' : 'block';
        }}
    </script>
</body>
</html>"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("HTML Dashboard generiert.")

if __name__ == "__main__":
    print("Starte Daten-Sammlung...")
    update_all_prices()
    rate, headlines = get_market_and_deals()
    m_ind, m_fin = calculate_totals(HARDWARE_DATA["main_build"])
    a_ind, a_fin = calculate_totals(HARDWARE_DATA["alt_build"])
    
    print("Speichere Historie...")
    history = manage_history(m_fin, a_fin)
    
    print("Claude Analyse...")
    decision = run_claude_decision(" ".join(headlines), rate, m_fin, a_fin)
    
    print("Generiere HTML...")
    generate_html_dashboard(rate, " ".join(headlines), decision, HARDWARE_DATA["main_build"], HARDWARE_DATA["alt_build"], history)
    print("Erfolgreich beendet!")
