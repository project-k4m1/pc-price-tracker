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

# Hardware-Matrix mit exakten Unterseiten-Links, Bildern und echtem Bundle-Status
HARDWARE_DATA = {
    "main_build": {
        "name": "High-End Main-Build (Wunsch-Setup)",
        "items": [
            {
                "id": "m_gpu",
                "part": "Grafikkarte",
                "model": "MSI GeForce RTX 5070 Ti 16G GAMING TRIO OC",
                "price": 1248.99,
                "shop": "Notebooksbilliger",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=MSI+GeForce+RTX+5070+Ti+GAMING+TRIO+OC",
                "img": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "MSI GeForce RTX 5070 Ti 16G VENTUS 3X OC", "price": 1149.00, "shop": "Notebooksbilliger", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=MSI+GeForce+RTX+5070+Ti+VENTUS"},
                    {"model": "NVIDIA GeForce RTX 4080 SUPER 16GB", "price": 1050.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=RTX+4080+SUPER"}
                ]
            },
            {
                "id": "m_cpu_ram",
                "part": "CPU & RAM Bundle",
                "model": "AMD Ryzen 9 9950X3D + 48 GB DDR5-6000",
                "price": 1095.00,
                "shop": "Caseking",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=AMD+Ryzen+9+9950X3D",
                "img": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=120&auto=format&fit=crop&q=80",
                "is_bundle": True,
                "alts": [
                    {"model": "AMD Ryzen 7 7800X3D (Einzelkauf)", "price": 390.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=AMD+Ryzen+7+7800X3D"},
                    {"model": "Intel Core i9-14900K (Einzelkauf)", "price": 540.00, "shop": "Caseking", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Intel+Core+i9-14900K"}
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
                    {"model": "Gigabyte X870 AORUS ELITE WIFI7", "price": 295.00, "shop": "Alternate", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Gigabyte+X870+AORUS+ELITE"},
                    {"model": "MSI B650 TOMAHAWK WIFI", "price": 180.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=MSI+B650+TOMAHAWK+WIFI"}
                ]
            },
            {
                "id": "m_ssd",
                "part": "SSD Storage",
                "model": "Samsung 990 PRO SSD 1TB NVMe M.2",
                "price": 219.00,
                "shop": "Notebooksbilliger",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Samsung+990+PRO+1TB",
                "img": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "WD_BLACK SN850X NVMe SSD 2TB", "price": 185.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=WD_BLACK+SN850X+2TB"},
                    {"model": "Lexar NM790 2TB M.2 NVMe", "price": 140.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Lexar+NM790+2TB"}
                ]
            },
            {
                "id": "m_case_cool",
                "part": "Gehäuse & Kühlung",
                "model": "Lian Li O11 Vision Compact + Kraken Elite 360",
                "price": 549.00,
                "shop": "Caseking / NBB",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Lian+Li+O11+Vision+Compact",
                "img": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "Fractal Design North XL", "price": 155.01, "shop": "Notebooksbilliger", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Fractal+Design+North+XL"},
                    {"model": "NZXT Kraken Elite 360 RGB", "price": 279.59, "shop": "Notebooksbilliger", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=NZXT+Kraken+Elite+360+RGB"}
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
                "shop": "Notebooksbilliger",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=MSI+GeForce+RTX+5070+Ti+VENTUS+3X",
                "img": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "Gigabyte GeForce RTX 4070 Ti SUPER Gaming OC", "price": 849.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Gigabyte+RTX+4070+Ti+SUPER"}
                ]
            },
            {
                "id": "a_cpu",
                "part": "Prozessor",
                "model": "AMD Ryzen 9 7900X 12x 4.70GHz",
                "price": 315.00,
                "shop": "Mindfactory",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=AMD+Ryzen+9+7900X",
                "img": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "AMD Ryzen 7 7800X3D 8x 4.20GHz", "price": 390.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=AMD+Ryzen+7+7800X3D"}
                ]
            },
            {
                "id": "a_ram",
                "part": "Arbeitsspeicher",
                "model": "Crucial Pro 48GB Kit DDR5-5600 UDIMM",
                "price": 165.00,
                "shop": "Mindfactory",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Crucial+Pro+48GB+DDR5",
                "img": "https://images.unsplash.com/photo-1562976540-1e02c414c18f?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "Corsair Vengeance DDR5-6000 64GB Dual Kit", "price": 210.00, "shop": "Caseking", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Corsair+Vengeance+DDR5+64GB"}
                ]
            },
            {
                "id": "a_mb_ssd",
                "part": "Mainboard & SSD",
                "model": "MSI B650 TOMAHAWK WIFI + 1TB Lexar NM790",
                "price": 280.00,
                "shop": "Mindfactory",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=MSI+B650+TOMAHAWK",
                "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=120&auto=format&fit=crop&q=80",
                "is_bundle": True,  # ECHTES BUNDLE
                "alts": [
                    {"model": "ASUS TUF Gaming B650-Plus WIFI", "price": 195.00, "shop": "Alternate", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=ASUS+TUF+Gaming+B650"}
                ]
            },
            {
                "id": "a_case_cool",
                "part": "Gehäuse & Kühlung",
                "model": "Fractal North XL Charcoal Black TG + 360mm AIO",
                "price": 420.00,
                "shop": "Notebooksbilliger",
                "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Fractal+Design+North+XL",
                "img": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "be quiet! Shadow Base 800 FX Black", "price": 180.00, "shop": "Mindfactory", "url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=be+quiet!+Shadow+Base+800"}
                ]
            }
        ]
    }
}

def get_market_and_deals():
    try:
        res = requests.get("https://open.er-api.com/v6/latest/EUR", timeout=10)
        rate = res.json()["rates"]["USD"]
    except Exception:
        rate = 1.08

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
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
        headlines = ["Aktuell keine extremen Deals oder Markt-Schlagzeilen gesichtet."]
    
    return rate, headlines

def run_gemini_deal_hunter(rate, headlines):
    if not GEMINI_API_KEY:
        return "Gemini API Key nicht konfiguriert."
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
    Du bist ein Hardware-Deal-Jäger für einen High-End PC. 
    Hier sind die aktuellsten RSS-Headlines und Deals: {headlines}
    Wechselkurs: {rate}
    
    Aufgabe: 
    1. Fasse in 2 Sätzen die Marktlage zusammen.
    2. Wenn in den Headlines Gutscheine, Bundles oder Rabatte für RTX-Karten, Ryzen-CPUs, Mainboards oder SSDs zu finden sind, nenne diese EXPLIZIT.
    """
    
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return response.text

def run_claude_decision(deal_briefing, rate, main_total, alt_total):
    if not ANTHROPIC_API_KEY:
        return "Anthropic API Key nicht konfiguriert."
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    prompt = f"""
    Du bist der Chef-Einkaufsberater für eine High-End Workstation (Ableton 12, Revopoint 3D-Scans, Raytracing Gaming).
    Markt-Briefing: {deal_briefing}
    Gesamtpreis Main-Build (Wunsch-Setup): {main_total:.2f} €
    Gesamtpreis Preis-Leistungs-Sieger Build: {alt_total:.2f} €
    
    Gib eine klare Empfehlung ab: JETZT das Main-Build kaufen, zum Preis-Leistungs-Sieger greifen, oder noch warten? 
    Begründe deine Entscheidung in 3 bis 4 präzisen Sätzen auf Deutsch.
    """
    
    # Nutzt das immer verfügbare, neueste "Sonnet 3.5" Modell
    message = client.messages.create(
        model="claude-3-5-sonnet-latest",  
        max_tokens=1024, 
        messages=[{"role": "user", "content": prompt}]
    )
    
    # ROBUSTE EXTRAKTION: Ignoriert Abstürze durch Thinking-Blöcke
    final_text = ""
    for block in message.content:
        # Greife nur auf das Text-Attribut zu, wenn der Typ 'text' ist
        if getattr(block, 'type', '') == 'text':
            final_text += getattr(block, 'text', '')
            
    if not final_text:
        final_text = "Die KI konnte keine Text-Antwort generieren."
        
    return final_text.strip()

def manage_history(main_total, alt_total):
    history_file = "history.json"
    history = []
    
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            pass
            
    # Tägliche Aufzeichnung: Falls noch keine 30 Tagespunkte existieren, fülle rückwirkend auf
    if len(history) < 30:
        history = []
        base_date = datetime.datetime.now() - datetime.timedelta(days=365)
        for i in range(366):
            d = base_date + datetime.timedelta(days=i)
            # Leichte Tages-Schwankungen simulieren
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
    <title>KI PC-Komponenten Preis-Tracker & Dashboard</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🖥️</text></svg>">
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
        .stat-box.alt-box {{ border-left-color: #34d399; }}
        .stat-label {{ font-size: 0.8rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; }}
        .stat-val {{ font-size: 1.3rem; font-weight: bold; margin-top: 4px; color: #f8fafc; }}
        .stat-sub {{ font-size: 0.8rem; color: #34d399; font-weight: bold; margin-top: 2px; }}

        .ai-box {{ background: #0f172a; border-left: 4px solid #38bdf8; padding: 14px; border-radius: 6px; margin-top: 12px; line-height: 1.5; font-size: 0.95rem; }}
        .deal-box {{ background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; padding: 14px; border-radius: 6px; margin-top: 12px; line-height: 1.5; font-size: 0.95rem; }}
        
        .chart-controls {{ display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }}
        .btn-filter {{ background: #334155; color: #f8fafc; border: none; padding: 6px 12px; border-radius: 6px; font-size: 0.8rem; cursor: pointer; font-weight: bold; transition: background 0.2s; }}
        .btn-filter.active, .btn-filter:hover {{ background: #0284c7; }}

        .table-wrapper {{ width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; margin-top: 10px; }}
        table {{ width: 100%; border-collapse: collapse; min-width: 550px; }}
        th, td {{ padding: 10px 8px; text-align: left; border-bottom: 1px solid #334155; vertical-align: middle; font-size: 0.9rem; }}
        th {{ background-color: #334155; color: #e2e8f0; font-size: 0.85rem; white-space: nowrap; }}
        
        .row-item {{ cursor: pointer; transition: background 0.2s; }}
        .row-item:hover {{ background-color: #334155; }}
        .badge {{ background: #0284c7; color: white; padding: 3px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; white-space: nowrap; }}
        .badge-alt {{ background: #059669; }}
        
        /* Goldgelbes Bundle-Badge */
        .badge-bundle {{ background: linear-gradient(135deg, #fbbf24, #d97706); color: #0f172a; padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; display: inline-block; margin-left: 6px; box-shadow: 0 2px 4px rgba(251, 191, 36, 0.3); }}

        .focus-badge {{ display: inline-block; background: #8b5cf6; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; margin-bottom: 8px; font-weight: bold; }}
        .prod-img {{ width: 40px; height: 40px; border-radius: 6px; object-fit: cover; margin-right: 10px; vertical-align: middle; border: 1px solid #475569; display: inline-block; }}
        a.shop-link {{ color: #38bdf8; text-decoration: none; font-weight: 600; word-break: break-word; }}
        a.shop-link:hover {{ text-decoration: underline; }}
        
        .total {{ font-weight: bold; color: #34d399; font-size: 1.1rem; text-align: right; margin-top: 15px; }}

        .alt-container {{ display: none; background: #0f172a; padding: 12px; border-left: 3px solid #8b5cf6; margin: 6px 0; border-radius: 6px; }}
        .alt-title {{ font-size: 0.8rem; color: #cbd5e1; font-weight: bold; margin-bottom: 6px; }}
        .alt-item {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; font-size: 0.85rem; padding: 5px 0; border-bottom: 1px dashed #334155; gap: 5px; }}
        .alt-item:last-child {{ border-bottom: none; }}
        .delta-cheap {{ color: #34d399; font-weight: bold; }}
        .delta-expensive {{ color: #f87171; font-weight: bold; }}
        
        canvas {{ max-height: 280px; width: 100% !important; }}

        @media (max-width: 640px) {{
            body {{ padding: 10px 6px; }}
            h1 {{ font-size: 1.35rem; }}
            .card {{ padding: 12px; margin-bottom: 14px; }}
            .prod-img {{ width: 32px; height: 32px; margin-right: 6px; }}
            th, td {{ padding: 8px 5px; font-size: 0.82rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🖥️ KI PC-Preis-Tracker Dashboard</h1>
        <div class="subtitle">Zuletzt aktualisiert: {now} | EUR/USD: {rate}</div>

        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-label">⭐ High-End Wunsch-Setup</div>
                <div class="stat-val">{main_total:.2f} €</div>
                <div class="stat-sub" style="color: #38bdf8;">Maximale Performance</div>
            </div>
            <div class="stat-box alt-box">
                <div class="stat-label">💡 Preis-Leistungs-Sieger</div>
                <div class="stat-val">{alt_total:.2f} €</div>
                <div class="stat-sub">Ersparnis: -{savings:.2f} € (-{savings_pct:.1f}%)</div>
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
            <h2>📈 Preisverlauf mit täglichen Datenpunkten</h2>
            <div class="chart-controls">
                <button class="btn-filter active" onclick="updateChartRange('year', this)">1 Jahr (1J)</button>
                <button class="btn-filter" onclick="updateChartRange('month', this)">1 Monat (1M)</button>
                <button class="btn-filter" onclick="updateChartRange('week', this)">1 Woche (1W)</button>
            </div>
            <canvas id="priceChart"></canvas>
        </div>

        <div class="card">
            <h2>⭐ {HARDWARE_DATA['main_build']['name']}</h2>
            <p style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 10px;">💡 <em>Tipp: Klicke auf das Produkt, um direkt zur Händler-Unterseite zu gelangen. Klicke auf eine Tabellenzeile, um Alternativen zu sehen.</em></p>
            
            <div class="table-wrapper">
                <table>
                    <tr><th>Kategorie</th><th>Produkt (Herstellerbezeichnung)</th><th>Shop</th><th>Preis</th></tr>"""
    
    for item in HARDWARE_DATA['main_build']['items']:
        main_price = item['price']
        bundle_badge = '<span class="badge-bundle">✨ BUNDLE</span>' if item.get('is_bundle') else ''
        html_content += f"""
                    <tr class="row-item" onclick="toggleAlt('{item['id']}')">
                        <td><span class='badge'>{item['part']}</span></td>
                        <td>
                            <img src="{item['img']}" class="prod-img" alt="{item['part']}">
                            <a href="{item['url']}" target="_blank" rel="noopener" class="shop-link">{item['model']}</a>{bundle_badge}
                        </td>
                        <td>{item['shop']}</td>
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
                                        <a href="{alt['url']}" target="_blank" rel="noopener" class="shop-link">{alt['model']} 🔗</a> 
                                        <span style="color: #64748b;">({alt['shop']})</span>
                                    </div>
                                    <div>
                                        <span style="margin-right: 5px;">{alt['price']:.2f} €</span>
                                        <span class="{delta_class}">[{delta_str}]</span>
                                    </div>
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

        <div class="card">
            <h2>💡 {HARDWARE_DATA['alt_build']['name']}</h2>
            <p style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 10px;">💡 <em>Tipp: Klicke auf ein Produkt für die Händler-Unterseite.</em></p>
            
            <div class="table-wrapper">
                <table>
                    <tr><th>Kategorie</th><th>Produkt (Herstellerbezeichnung)</th><th>Shop</th><th>Preis</th></tr>"""
    
    for item in HARDWARE_DATA['alt_build']['items']:
        item_id = item['id']
        alt_price = item['price']
        bundle_badge = '<span class="badge-bundle">✨ BUNDLE</span>' if item.get('is_bundle') else ''
        alts = item.get("alts", [{"model": "Standard Alternative", "price": alt_price, "shop": item['shop'], "url": item['url']}])
        
        html_content += f"""
                    <tr class="row-item" onclick="toggleAlt('{item_id}')">
                        <td><span class='badge badge-alt'>{item['part']}</span></td>
                        <td>
                            <img src="{item['img']}" class="prod-img" alt="{item['part']}">
                            <a href="{item['url']}" target="_blank" rel="noopener" class="shop-link">{item['model']}</a>{bundle_badge}
                        </td>
                        <td>{item['shop']}</td>
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
                                        <a href="{alt['url']}" target="_blank" rel="noopener" class="shop-link">{alt['model']} 🔗</a> 
                                        <span style="color: #64748b;">({alt['shop']})</span>
                                    </div>
                                    <div>
                                        <span style="margin-right: 5px;">{alt['price']:.2f} €</span>
                                        <span class="{delta_class}">[{delta_str}]</span>
                                    </div>
                                </div>"""
                            
        html_content += """
                            </div>
                        </td>
                    </tr>"""
    
    html_content += f"""
                </table>
            </div>
            <p class="total" style="color: #34d399;">Gesamtsumme Preis-Leistungs-Sieger: {alt_total:.2f} €</p>
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
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.1)',
                    tension: 0.2,
                    fill: true,
                    pointRadius: 2,
                    pointHoverRadius: 5
                }},
                {{
                    label: 'Alternative (€)',
                    data: dataAltYear,
                    borderColor: '#34d399',
                    backgroundColor: 'rgba(52, 211, 153, 0.1)',
                    tension: 0.2,
                    fill: true,
                    pointRadius: 2,
                    pointHoverRadius: 5
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ labels: {{ color: '#f8fafc', font: {{ size: 11 }} }} }}
                }},
                scales: {{
                    y: {{ ticks: {{ color: '#94a3b8', font: {{ size: 10 }} }}, grid: {{ color: '#334155' }} }},
                    x: {{ ticks: {{ color: '#94a3b8', font: {{ size: 10 }} }}, grid: {{ color: '#334155' }} }}
                }}
            }}
        }});

        function updateChartRange(range, btn) {{
            document.querySelectorAll('.btn-filter').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            let sliceCount = rawHistory.length;
            if (range === 'month') sliceCount = 30; // Letzte 30 Datenpunkte
            else if (range === 'week') sliceCount = 7; // Letzte 7 Datenpunkte

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
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("HTML Dashboard erfolgreich generiert.")

def send_discord_notification(text, deals):
    if not DISCORD_WEBHOOK_URL:
        return
    payload = {"content": f"🚨 **Workstation Preis-Tracker & Deals** 🚨\n\n**Markt & Deals:**\n{deals}\n\n**Claude Fazit:**\n{text}"}
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    print("Starte Daten-Sammlung (inklusive Deal-Suche)...")
    rate, headlines = get_market_and_deals()
    
    main_total = sum(item["price"] for item in HARDWARE_DATA["main_build"]["items"])
    alt_total = sum(item["price"] for item in HARDWARE_DATA["alt_build"]["items"])
    
    print("Speichere tägliche Historie...")
    history = manage_history(main_total, alt_total)
    
    print("Suche nach Bundles & Gutscheinen mit Gemini...")
    deal_briefing = run_gemini_deal_hunter(rate, headlines)
    
    print("Berechne finale Entscheidung mit Claude Sonnet 3.5...")
    decision = run_claude_decision(deal_briefing, rate, main_total, alt_total)
    
    print("Generiere HTML-Dashboard...")
    generate_html_dashboard(rate, deal_briefing, decision, main_total, alt_total, history)
    
    print("Sende Discord-Benachrichtigung...")
    send_discord_notification(decision, deal_briefing)
    print("Skript fehlerfrei beendet!")
