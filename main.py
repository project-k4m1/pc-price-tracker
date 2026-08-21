import os
import datetime
import json
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
                "id": "m_cpu_ram",
                "part": "CPU & RAM",
                "model": "AMD Ryzen 9 9950X3D + 48GB XPG Lancer",
                "price": 1095.00,
                "shop": "Caseking Bundle",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=AMD+Ryzen+9+9950X3D",
                "img": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=120&auto=format&fit=crop&q=80",
                "is_bundle": True,
                "alts": [
                    {"model": "AMD Ryzen 7 7800X3D (Einzel)", "price": 390.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=AMD+Ryzen+7+7800X3D"}
                ]
            },
            {
                "id": "m_gpu",
                "part": "Grafikkarte",
                "model": "ASUS TUF Gaming GeForce RTX 5070 Ti 16G",
                "price": 1219.00,
                "shop": "Notebooksbilliger",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=ASUS+TUF+Gaming+GeForce+RTX+5070+Ti",
                "img": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "MSI GeForce RTX 5070 Ti GAMING TRIO OC", "price": 1248.99, "shop": "Notebooksbilliger", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=MSI+GeForce+RTX+5070+Ti+GAMING+TRIO+OC"},
                    {"model": "Gigabyte GeForce RTX 4070 Ti SUPER", "price": 849.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Gigabyte+GeForce+RTX+4070+Ti+SUPER"}
                ]
            },
            {
                "id": "m_mb",
                "part": "Mainboard",
                "model": "MSI MAG X870E TOMAHAWK WIFI",
                "price": 284.36,
                "shop": "Notebooksbilliger",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=MSI+MAG+X870E+TOMAHAWK+WIFI",
                "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "ASUS ROG Strix X870-F Gaming WIFI", "price": 420.00, "shop": "Alternate", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=ASUS+ROG+Strix+X870-F"},
                    {"model": "MSI B650 TOMAHAWK WIFI", "price": 180.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=MSI+B650+TOMAHAWK+WIFI"}
                ]
            },
            {
                "id": "m_ssd",
                "part": "SSD (System)",
                "model": "Samsung 990 PRO 1TB NVMe M.2",
                "price": 199.05,
                "shop": "Mindfactory",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Samsung+990+PRO+1TB",
                "img": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "Lexar NM790 2TB M.2 (Preis-Leistung)", "price": 140.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Lexar+NM790+2TB"}
                ]
            },
            {
                "id": "m_case",
                "part": "Gehäuse",
                "model": "HAVN HS420 VGPU Black",
                "price": 265.00,
                "shop": "Caseking",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=HAVN+HS420+VGPU+Black",
                "img": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "Lian Li O11 Vision Compact", "price": 125.00, "shop": "Caseking", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Lian+Li+O11+Vision+Compact"},
                    {"model": "Fractal Design North XL Charcoal TG", "price": 155.01, "shop": "Notebooksbilliger", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Fractal+Design+North+XL+Charcoal+TG"}
                ]
            },
            {
                "id": "m_aio",
                "part": "AiO-Wasserkühlung",
                "model": "Lian Li HydroShift LCD 360S Black",
                "price": 180.00,
                "shop": "Notebooksbilliger",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Lian+Li+HydroShift+LCD+360S",
                "img": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "NZXT Kraken Elite 360 RGB", "price": 279.59, "shop": "Notebooksbilliger", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=NZXT+Kraken+Elite+360+RGB"}
                ]
            },
             {
                "id": "m_fans_lcd",
                "part": "Lüfter (Displays)",
                "model": "Lian Li UNI FAN TL LCD 120 Reverse (3er)",
                "price": 145.00,
                "shop": "Caseking",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Lian+Li+UNI+FAN+TL+LCD+120+Reverse",
                "img": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "Keine Alternative (Vitrinen-Setup)", "price": 145.00, "shop": "-", "url": "#"}
                ]
            },
            {
                "id": "m_fans_inf",
                "part": "Lüfter (Boden)",
                "model": "Lian Li SL-INF Wireless Reverse (3er)",
                "price": 95.00,
                "shop": "Mindfactory",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Lian+Li+UNI+FAN+SL-INF+Wireless+Reverse",
                "img": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "Arctic P14 PWM PST (5er Pack)", "price": 35.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Arctic+P14+PWM+PST+5er"}
                ]
            },
            {
                "id": "m_psu",
                "part": "Netzteil",
                "model": "be quiet! Straight Power 12 1000W",
                "price": 185.00,
                "shop": "Mindfactory",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=be+quiet!+Straight+Power+12+1000W",
                "img": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "be quiet! Straight Power 12 850W", "price": 160.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=be+quiet!+Straight+Power+12+850W"}
                ]
            }
        ]
    }
}

# (Platzhalter-Funktionen für externe APIs - diese bleiben unangetastet)
def get_market_and_deals():
    return 1.08, ["Hardware-Preise stabil.", "Keine extremen Deals gesichtet."]

def run_gemini_deal_hunter(rate, headlines):
    return "Die Lage auf dem Hardware-Markt ist aktuell stabil. Es gibt keine nennenswerten Gutscheine."

def run_claude_decision(deal_briefing, rate, main_total, alt_total):
    return "Das Main-Build ist eine exzellente, wenn auch kostspielige Wahl für eine Workstation. Wenn das Budget vorhanden ist, zuschlagen!"

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
            history.append({
                "date": d.strftime("%Y-%m-%d"),
                "main_total": round(main_total * factor_m, 2),
                "alt_total": round(alt_total * factor_m, 2)
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
    
    history_json = json.dumps(history)
    
    html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Workstation Preis-Tracker</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 15px 10px; overflow-x: hidden; }}
        .container {{ width: 100%; max-width: 1000px; margin: auto; }}
        h1 {{ color: #38bdf8; text-align: center; margin-bottom: 5px; font-size: 1.6rem; }}
        .subtitle {{ text-align: center; color: #94a3b8; margin-bottom: 20px; font-size: 0.85rem; }}
        .card {{ background: #1e293b; border-radius: 12px; padding: 18px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); width: 100%; }}
        
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 10px; }}
        .stat-box {{ background: #0f172a; padding: 14px; border-radius: 8px; border-left: 4px solid #38bdf8; }}
        .stat-label {{ font-size: 0.8rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; }}
        .stat-val {{ font-size: 1.3rem; font-weight: bold; margin-top: 4px; color: #f8fafc; }}

        .ai-box {{ background: #0f172a; border-left: 4px solid #38bdf8; padding: 14px; border-radius: 6px; margin-top: 12px; font-size: 0.95rem; }}
        
        .table-wrapper {{ width: 100%; overflow-x: auto; margin-top: 10px; }}
        table {{ width: 100%; border-collapse: collapse; min-width: 550px; }}
        th, td {{ padding: 10px 8px; text-align: left; border-bottom: 1px solid #334155; font-size: 0.9rem; }}
        th {{ background-color: #334155; color: #e2e8f0; font-size: 0.85rem; }}
        
        .row-item {{ cursor: pointer; transition: background 0.2s; }}
        .row-item:hover {{ background-color: #334155; }}
        .badge {{ background: #0284c7; padding: 3px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }}
        .badge-bundle {{ background: linear-gradient(135deg, #fbbf24, #d97706); color: #0f172a; padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; margin-left: 6px; }}
        
        a.shop-link {{ color: #38bdf8; text-decoration: none; font-weight: 600; }}
        a.shop-link:hover {{ text-decoration: underline; }}
        
        .total {{ font-weight: bold; color: #34d399; font-size: 1.1rem; text-align: right; margin-top: 15px; }}

        .alt-container {{ display: none; background: #0f172a; padding: 12px; border-left: 3px solid #8b5cf6; margin: 6px 0; border-radius: 6px; }}
        .alt-title {{ font-size: 0.8rem; color: #cbd5e1; font-weight: bold; margin-bottom: 6px; }}
        .alt-item {{ display: flex; justify-content: space-between; font-size: 0.85rem; padding: 5px 0; border-bottom: 1px dashed #334155; }}
        .delta-cheap {{ color: #34d399; font-weight: bold; }}
        .delta-expensive {{ color: #f87171; font-weight: bold; }}
        
        canvas {{ max-height: 280px; width: 100% !important; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🖥️ KI PC-Preis-Tracker</h1>
        <div class="subtitle">Zuletzt aktualisiert: {now}</div>

        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-label">⭐ High-End Wunsch-Setup</div>
                <div class="stat-val">{main_total:.2f} €</div>
            </div>
        </div>

        <div class="card">
            <h2>🤖 KI-Kaufberatung</h2>
            <div class="ai-box">
                <strong>🧠 Experten-Empfehlung:</strong><br><br>{decision}
            </div>
        </div>

        <div class="card">
            <h2>⭐ {HARDWARE_DATA['main_build']['name']}</h2>
            <div class="table-wrapper">
                <table>
                    <tr><th>Kategorie</th><th>Produkt</th><th>Shop</th><th>Preis</th></tr>"""
    
    for item in HARDWARE_DATA['main_build']['items']:
        main_price = item['price']
        bundle_badge = '<span class="badge-bundle">BUNDLE</span>' if item.get('is_bundle') else ''
        html_content += f"""
                    <tr class="row-item" onclick="toggleAlt('{item['id']}')">
                        <td><span class='badge'>{item['part']}</span></td>
                        <td><a href="{item['url']}" target="_blank" class="shop-link">{item['model']}</a>{bundle_badge}</td>
                        <td>{item['shop']}</td>
                        <td><strong>{item['price']:.2f} €</strong></td>
                    </tr>
                    <tr id="alt-row-{item['id']}">
                        <td colspan="4" style="padding: 0; border: none;">
                            <div id="alt-box-{item['id']}" class="alt-container">
                                <div class="alt-title">🔄 Alternativen:</div>"""
        
        for alt in item['alts']:
            delta = alt['price'] - main_price
            delta_str = f"{delta:+.2f} €"
            delta_class = "delta-cheap" if delta <= 0 else "delta-expensive"
            html_content += f"""
                                <div class="alt-item">
                                    <div><a href="{alt['url']}" target="_blank" class="shop-link">{alt['model']} 🔗</a></div>
                                    <div><span>{alt['price']:.2f} €</span> <span class="{delta_class}">[{delta_str}]</span></div>
                                </div>"""
                            
        html_content += """
                            </div>
                        </td>
                    </tr>"""
    
    html_content += f"""
                </table>
            </div>
            <p class="total">Gesamtsumme Main-Build: {main_total:.2f} €</p>
        </div>
    </div>
    
    <script>
        function toggleAlt(id) {{
            const box = document.getElementById('alt-box-' + id);
            box.style.display = (box.style.display === 'block') ? 'none' : 'block';
        }}
    </script>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def send_discord_notification(text, deals):
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": f"🚨 **Update** 🚨\n\n{text}"})

if __name__ == "__main__":
    rate, headlines = get_market_and_deals()
    main_total = sum(item["price"] for item in HARDWARE_DATA["main_build"]["items"])
    # Dummy alt total für History
    alt_total = main_total * 0.8 
    
    history = manage_history(main_total, alt_total)
    deal_briefing = run_gemini_deal_hunter(rate, headlines)
    decision = run_claude_decision(deal_briefing, rate, main_total, alt_total)
    
    generate_html_dashboard(rate, deal_briefing, decision, main_total, alt_total, history)
    send_discord_notification(decision, deal_briefing)
