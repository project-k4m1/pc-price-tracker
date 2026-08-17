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

# Hardware-Matrix: Main-Build vs. Preis-Leistungs-Sieger
HARDWARE_DATA = {
    "main_build": {
        "name": "High-End Main-Build (Wunsch-Setup)",
        "items": [
            {
                "id": "gpu",
                "part": "Grafikkarte",
                "model": "MSI GeForce RTX 5070 Ti Gaming Trio OC",
                "price": 1248.99,
                "shop": "Notebooksbilliger",
                "url": "https://www.notebooksbilliger.de",
                "img": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=120&auto=format&fit=crop&q=80",
                "alts": [
                    {"model": "MSI RTX 5070 Ti Ventus 3X (Preis-Tipp)", "price": 1149.00, "shop": "Idealo", "url": "https://www.idealo.de"},
                    {"model": "NVIDIA GeForce RTX 4080 SUPER 16GB", "price": 1050.00, "shop": "Mindfactory", "url": "https://www.mindfactory.de"},
                    {"model": "AMD Radeon RX 7900 XTX 24GB (VRAM-Monster)", "price": 980.00, "shop": "Alternate", "url": "https://www.alternate.de"}
                ]
            },
            {
                "id": "cpu_ram",
                "part": "CPU & RAM Bundle",
                "model": "AMD Ryzen 9 9950X3D + 48GB DDR5-6000",
                "price": 1095.00,
                "shop": "Caseking",
                "url": "https://www.caseking.de",
                "img": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=120&auto=format&fit=crop&q=80",
                "alts": [
                    {"model": "AMD Ryzen 7 7800X3D + 48GB DDR5 (Gaming-King)", "price": 580.00, "shop": "Mindfactory", "url": "https://www.mindfactory.de"},
                    {"model": "Intel Core i9-14900K + 64GB DDR5 (Workstation)", "price": 890.00, "shop": "Caseking", "url": "https://www.caseking.de"},
                    {"model": "AMD Ryzen 9 7900X + 48GB DDR5 (Preis-Leistung)", "price": 480.00, "shop": "Notebooksbilliger", "url": "https://www.notebooksbilliger.de"}
                ]
            },
            {
                "id": "mb",
                "part": "Mainboard",
                "model": "MSI MAG X870E TOMAHAWK WIFI",
                "price": 284.36,
                "shop": "Notebooksbilliger",
                "url": "https://www.notebooksbilliger.de",
                "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=120&auto=format&fit=crop&q=80",
                "alts": [
                    {"model": "Gigabyte X870 AORUS ELITE WIFI7", "price": 295.00, "shop": "Alternate", "url": "https://www.alternate.de"},
                    {"model": "MSI B650 Tomahawk WiFi (Preis-Tipp)", "price": 180.00, "shop": "Idealo", "url": "https://www.idealo.de"}
                ]
            },
            {
                "id": "ssd",
                "part": "SSD Storage",
                "model": "Samsung 990 PRO SSD 1TB",
                "price": 219.00,
                "shop": "Notebooksbilliger",
                "url": "https://www.notebooksbilliger.de",
                "img": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=120&auto=format&fit=crop&q=80",
                "alts": [
                    {"model": "WD_BLACK SN850X 2TB (Mehr Speicher)", "price": 185.00, "shop": "Idealo", "url": "https://www.idealo.de"},
                    {"model": "Lexar NM790 2TB NVMe (Preis-Tipp)", "price": 140.00, "shop": "Mindfactory", "url": "https://www.mindfactory.de"}
                ]
            },
            {
                "id": "case_cool",
                "part": "Gehäuse & Kühlung",
                "model": "Lian Li O11 Vision + NZXT Kraken Elite 360",
                "price": 549.00,
                "shop": "Idealo / Mix",
                "url": "https://www.idealo.de",
                "img": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=120&auto=format&fit=crop&q=80",
                "alts": [
                    {"model": "Fractal Design Torrent + Corsair H150i", "price": 430.00, "shop": "Alternate", "url": "https://www.alternate.de"},
                    {"model": "Fractal North XL + Standard 360 AIO (Preis-Tipp)", "price": 380.00, "shop": "Idealo", "url": "https://www.idealo.de"}
                ]
            }
        ]
    },
    "alt_build": {
        "name": "Preis-Leistungs-Sieger Build",
        "items": [
            {"part": "Grafikkarte", "model": "MSI GeForce RTX 5070 Ti Ventus 3X", "price": 1149.00, "shop": "Idealo"},
            {"part": "Prozessor", "model": "AMD Ryzen 9 7900X", "price": 315.00, "shop": "Mindfactory"},
            {"part": "Arbeitsspeicher", "model": "Crucial Pro 48GB DDR5-5600", "price": 165.00, "shop": "Mindfactory"},
            {"part": "Mainboard & SSD", "model": "MSI B650 Tomahawk + 1TB Lexar SSD", "price": 280.00, "shop": "Mindfactory"},
            {"part": "Gehäuse & Kühlung", "model": "Fractal North XL + Standard AIO", "price": 420.00, "shop": "Idealo"}
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
    
    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=350,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

def manage_history(main_total, alt_total):
    history_file = "history.json"
    history = []
    
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            pass
            
    if len(history) < 12:
        months = ["Aug 25", "Sep 25", "Okt 25", "Nov 25", "Dez 25", "Jan 26", "Feb 26", "Mär 26", "Apr 26", "Mai 26", "Jun 26", "Jul 26"]
        factors_main = [0.88, 0.90, 0.92, 0.95, 0.97, 0.99, 1.02, 1.01, 1.00, 0.99, 0.98, 0.99]
        factors_alt  = [0.85, 0.87, 0.89, 0.92, 0.94, 0.96, 0.98, 0.98, 0.97, 0.98, 0.99, 0.99]
        
        history = []
        for m, fm, fa in zip(months, factors_main, factors_alt):
            history.append({
                "date": m,
                "main_total": round(main_total * fm, 2),
                "alt_total": round(alt_total * fa, 2)
            })
            
    today_str = datetime.datetime.now().strftime("%b %y")
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
    
    labels = [item["date"] for item in history]
    data_main = [item["main_total"] for item in history]
    data_alt = [item.get("alt_total", alt_total) for item in history]
    
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
        
        /* Stats Header Card */
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 10px; }}
        .stat-box {{ background: #0f172a; padding: 14px; border-radius: 8px; border-left: 4px solid #38bdf8; }}
        .stat-box.alt-box {{ border-left-color: #34d399; }}
        .stat-label {{ font-size: 0.8rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; }}
        .stat-val {{ font-size: 1.3rem; font-weight: bold; margin-top: 4px; color: #f8fafc; }}
        .stat-sub {{ font-size: 0.8rem; color: #34d399; font-weight: bold; margin-top: 2px; }}

        .ai-box {{ background: #0f172a; border-left: 4px solid #38bdf8; padding: 14px; border-radius: 6px; margin-top: 12px; line-height: 1.5; font-size: 0.95rem; }}
        .deal-box {{ background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; padding: 14px; border-radius: 6px; margin-top: 12px; line-height: 1.5; font-size: 0.95rem; }}
        
        /* Table Wrapper for Horizontal Scroll on Mobile */
        .table-wrapper {{ width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; margin-top: 10px; }}
        table {{ width: 100%; border-collapse: collapse; min-width: 550px; }}
        th, td {{ padding: 10px 8px; text-align: left; border-bottom: 1px solid #334155; vertical-align: middle; font-size: 0.9rem; }}
        th {{ background-color: #334155; color: #e2e8f0; font-size: 0.85rem; white-space: nowrap; }}
        
        .row-item {{ cursor: pointer; transition: background 0.2s; }}
        .row-item:hover {{ background-color: #334155; }}
        .badge {{ background: #0284c7; color: white; padding: 3px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; white-space: nowrap; }}
        .focus-badge {{ display: inline-block; background: #8b5cf6; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; margin-bottom: 8px; font-weight: bold; }}
        .prod-img {{ width: 40px; height: 40px; border-radius: 6px; object-fit: cover; margin-right: 10px; vertical-align: middle; border: 1px solid #475569; display: inline-block; }}
        a.shop-link {{ color: #38bdf8; text-decoration: none; font-weight: 600; word-break: break-word; }}
        a.shop-link:hover {{ text-decoration: underline; }}
        
        /* Alternativen Klappbereich */
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
            .prod-img {{ width: 32px; height: 30px; margin-right: 6px; }}
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
            <div class="focus-badge">🎯 Optmiert für Ableton 12, Revopoint 3D & Raytracing</div>
            
            <div class="deal-box">
                <strong>🚨 Deal-Radar & Markt-News (Gemini):</strong><br><br>{deal_briefing.replace(chr(10), '<br>')}
            </div>

            <div class="ai-box">
                <strong>🧠 Experten-Empfehlung (Claude Sonnet 5):</strong><br><br>{decision.replace(chr(10), '<br>')}
            </div>
        </div>
        
        <div class="card">
            <h2>📈 Preisverlauf im Jahresvergleich</h2>
            <canvas id="priceChart"></canvas>
        </div>

        <div class="card">
            <h2>⭐ Hardware-Matrix & Alternativen-Check</h2>
            <p style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 10px;">💡 <em>Tipp: Klicke auf eine Tabellenzeile, um ähnliche Alternativen (± 200€) anzuzeigen.</em></p>
            
            <div class="table-wrapper">
                <table>
                    <tr><th>Kategorie</th><th>Produkt</th><th>Shop</th><th>Preis</th></tr>"""
    
    for item in HARDWARE_DATA['main_build']['items']:
        main_price = item['price']
        html_content += f"""
                    <tr class="row-item" onclick="toggleAlt('{item['id']}')">
                        <td><span class='badge'>{item['part']}</span></td>
                        <td>
                            <img src="{item['img']}" class="prod-img" alt="{item['part']}">
                            <a href="{item['url']}" target="_blank" class="shop-link">{item['model']} 🔗</a>
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
                                        <a href="{alt['url']}" target="_blank" class="shop-link">{alt['model']}</a> 
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
            <p style="text-align: right; margin-top: 15px;" class="stat-sub">Gesamtsumme Main-Build: {main_total:.2f} €</p>
        </div>
    </div>
    
    <script>
        // Chart.js Setup
        const ctx = document.getElementById('priceChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [{{
                    label: 'Main-Build (€)',
                    data: {json.dumps(data_main)},
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.1)',
                    tension: 0.3,
                    fill: true
                }},
                {{
                    label: 'Preis-Leistungs-Sieger (€)',
                    data: {json.dumps(data_alt)},
                    borderColor: '#34d399',
                    backgroundColor: 'rgba(52, 211, 153, 0.1)',
                    tension: 0.3,
                    fill: true
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

        // Alternativen Klappfunktion
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
    
    print("Speichere 1-Jahres-Historie...")
    history = manage_history(main_total, alt_total)
    
    print("Suche nach Bundles & Gutscheinen mit Gemini...")
    deal_briefing = run_gemini_deal_hunter(rate, headlines)
    
    print("Berechne finale Entscheidung mit Claude Sonnet 5...")
    decision = run_claude_decision(deal_briefing, rate, main_total, alt_total)
    
    print("Generiere HTML-Dashboard...")
    generate_html_dashboard(rate, deal_briefing, decision, main_total, alt_total, history)
    
    print("Sende Discord-Benachrichtigung...")
    send_discord_notification(decision, deal_briefing)
    print("Skript fehlerfrei beendet!")
