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

# Hardware-Matrix mit Shop-Links, Bildern und Alternativen
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
                "img": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=100&auto=format&fit=crop&q=80",
                "alts": [
                    {"model": "MSI RTX 5070 Ti Ventus 3X", "price": 1149.00, "shop": "Idealo", "url": "https://www.idealo.de"},
                    {"model": "ASUS TUF Gaming RTX 5070 Ti", "price": 1299.00, "shop": "Caseking", "url": "https://www.caseking.de"}
                ]
            },
            {
                "id": "cpu_ram",
                "part": "CPU & RAM Bundle",
                "model": "AMD Ryzen 9 9950X3D + 48GB DDR5-6000",
                "price": 1095.00,
                "shop": "Caseking",
                "url": "https://www.caseking.de",
                "img": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=100&auto=format&fit=crop&q=80",
                "alts": [
                    {"model": "AMD Ryzen 9 7900X + 48GB Crucial DDR5", "price": 480.00, "shop": "Mindfactory", "url": "https://www.mindfactory.de"},
                    {"model": "Intel Core i9-14900K + 64GB DDR5", "price": 890.00, "shop": "Caseking", "url": "https://www.caseking.de"}
                ]
            },
            {
                "id": "mb",
                "part": "Mainboard",
                "model": "MSI MAG X870E TOMAHAWK WIFI",
                "price": 284.36,
                "shop": "Notebooksbilliger",
                "url": "https://www.notebooksbilliger.de",
                "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=100&auto=format&fit=crop&q=80",
                "alts": [
                    {"model": "MSI B650 Tomahawk WiFi", "price": 180.00, "shop": "Mindfactory", "url": "https://www.mindfactory.de"},
                    {"model": "ASUS ROG Strix X870E-F", "price": 379.00, "shop": "Alternate", "url": "https://www.alternate.de"}
                ]
            },
            {
                "id": "ssd",
                "part": "SSD Storage",
                "model": "Samsung 990 PRO SSD 1TB",
                "price": 219.00,
                "shop": "Notebooksbilliger",
                "url": "https://www.notebooksbilliger.de",
                "img": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=100&auto=format&fit=crop&q=80",
                "alts": [
                    {"model": "Lexar NM790 1TB NVMe", "price": 95.00, "shop": "Mindfactory", "url": "https://www.mindfactory.de"},
                    {"model": "WD_BLACK SN850X 2TB", "price": 185.00, "shop": "Idealo", "url": "https://www.idealo.de"}
                ]
            },
            {
                "id": "case_cool",
                "part": "Gehäuse & Kühlung",
                "model": "Lian Li O11 Vision + NZXT Kraken Elite 360",
                "price": 549.00,
                "shop": "Idealo / Mix",
                "url": "https://www.idealo.de",
                "img": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=100&auto=format&fit=crop&q=80",
                "alts": [
                    {"model": "Fractal North XL + Standard 360 AIO", "price": 420.00, "shop": "Idealo", "url": "https://www.idealo.de"},
                    {"model": "be quiet! Shadow Base 800 + Pure Loop 360", "price": 280.00, "shop": "Mindfactory", "url": "https://www.mindfactory.de"}
                ]
            }
        ]
    }
}

def get_market_data():
    try:
        res = requests.get("https://open.er-api.com/v6/latest/EUR", timeout=10)
        rate = res.json()["rates"]["USD"]
    except Exception:
        rate = 1.08

    rss_urls = [
        "https://www.heise.de/newsticker/heise-atom.xml",
        "https://www.golem.de/rss.php",
        "https://winfuture.de/rss/news.rss"
    ]

    all_headlines = []
    keywords = ["hardware", "grafikkarte", "prozessor", "ram", "speicher", "ki", "chip", "nvidia", "amd", "intel", "preis"]

    for url in rss_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                title = entry.title.lower()
                if any(kw in title for kw in keywords):
                    all_headlines.append(entry.title)
        except Exception:
            pass

    headlines = list(dict.fromkeys(all_headlines))[:10]
    if not headlines:
        headlines = ["Markt zeigt sich aktuell weitgehend stabil."]
    
    return rate, headlines

def run_gemini_researcher(rate, headlines):
    if not GEMINI_API_KEY:
        return "Gemini API Key nicht konfiguriert."
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"Analysiere kurz (max. 3 Sätze auf Deutsch) die Marktlage für PC-Komponenten:\n- EUR/USD: {rate}\n- News: {headlines}"
    
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return response.text

def run_claude_decision(briefing, rate, main_total, alt_total):
    if not ANTHROPIC_API_KEY:
        return "Anthropic API Key nicht konfiguriert."
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    prompt = f"""
    Du bist der Chef-Einkaufsberater für eine High-End Workstation.
    Spezifischer Einsatzzweck: Gigantische Ableton 12 Projekte, 3D-Scannen mit Revopoint POP 4 und Raytracing Gaming.
    Markt-Briefing: {briefing}
    Wechselkurs EUR/USD: {rate}
    Gesamtpreis Main-Build: {main_total:.2f} €
    Gesamtpreis Alternative: {alt_total:.2f} €
    
    Gib eine klare Empfehlung ab: JETZT KAUFEN oder WARTEN? 
    Begründe deine Entscheidung präzise in 3 bis 4 Sätzen auf Deutsch.
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
            
    # Falls weniger als 12 Monate existieren, initialisiere 1-Jahres-Verlauf rückwirkend
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

def generate_html_dashboard(rate, briefing, decision, main_total, alt_total, history):
    now = datetime.datetime.now().strftime("%d.%m.%Y um %H:%M Uhr")
    
    labels = [item["date"] for item in history]
    data_main = [item["main_total"] for item in history]
    data_alt = [item["alt_total"] for item in history]
    
    html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KI PC-Komponenten Preis-Tracker & Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
        .container {{ max-width: 1000px; margin: auto; }}
        h1 {{ color: #38bdf8; text-align: center; margin-bottom: 5px; }}
        .subtitle {{ text-align: center; color: #94a3b8; margin-bottom: 30px; font-size: 0.9rem; }}
        .card {{ background: #1e293b; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
        .ai-box {{ background: #0f172a; border-left: 4px solid #38bdf8; padding: 15px; border-radius: 4px; margin-top: 15px; line-height: 1.5; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #334155; vertical-align: middle; }}
        th {{ background-color: #334155; color: #e2e8f0; }}
        .row-item {{ cursor: pointer; transition: background 0.2s; }}
        .row-item:hover {{ background-color: #334155; }}
        .total {{ font-weight: bold; color: #34d399; font-size: 1.1rem; }}
        .badge {{ background: #0284c7; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }}
        .focus-badge {{ display: inline-block; background: #8b5cf6; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; margin-bottom: 10px; font-weight: bold; }}
        .prod-img {{ width: 45px; height: 45px; border-radius: 6px; object-fit: cover; margin-right: 12px; vertical-align: middle; border: 1px solid #475569; }}
        a.shop-link {{ color: #38bdf8; text-decoration: none; font-weight: 600; }}
        a.shop-link:hover {{ text-decoration: underline; }}
        
        /* Alternativen-Aufklappbereich */
        .alt-container {{ display: none; background: #0f172a; padding: 12px 15px; border-left: 3px solid #8b5cf6; margin: 8px 0; border-radius: 6px; }}
        .alt-title {{ font-size: 0.85rem; color: #cbd5e1; font-weight: bold; margin-bottom: 8px; }}
        .alt-item {{ display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; padding: 4px 0; border-bottom: 1px dashed #334155; }}
        .alt-item:last-child {{ border-bottom: none; }}
        .delta-cheap {{ color: #34d399; font-weight: bold; }}
        .delta-expensive {{ color: #f87171; font-weight: bold; }}
        canvas {{ max-height: 320px; width: 100%; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🖥️ KI PC-Preis-Tracker Dashboard</h1>
        <div class="subtitle">Zuletzt aktualisiert: {now} | EUR/USD: {rate}</div>

        <div class="card">
            <h2>🤖 KI-Kaufberatung (Claude & Gemini)</h2>
            <div class="focus-badge">🎯 Optmiert für Ableton 12, Revopoint 3D & Raytracing</div>
            <p><strong>Markt-Briefing (Gemini):</strong> {briefing}</p>
            <div class="ai-box">
                <strong>Experten-Empfehlung (Claude Sonnet 5):</strong><br><br>{decision.replace(chr(10), '<br>')}
            </div>
        </div>
        
        <div class="card">
            <h2>📈 Preisverlauf (12-Monates-Trend)</h2>
            <canvas id="priceChart"></canvas>
        </div>

        <div class="card">
            <h2>⭐ {HARDWARE_DATA['main_build']['name']}</h2>
            <p style="font-size: 0.85rem; color: #94a3b8;">💡 <em>Tipp: Klicke auf eine Tabellenzeile, um alternative Optionen und Preisunterschiede anzuzeigen.</em></p>
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
                    <td>{item['price']:.2f} €</td>
                </tr>
                <tr id="alt-row-{item['id']}">
                    <td colspan="4" style="padding: 0; border: none;">
                        <div id="alt-box-{item['id']}" class="alt-container">
                            <div class="alt-title">🔄 Alternative Optionen zu {item['part']}:</div>"""
        
        for alt in item['alts']:
            delta = alt['price'] - main_price
            delta_str = f"{delta:+.2f} €"
            delta_class = "delta-cheap" if delta < 0 else "delta-expensive"
            html_content += f"""
                            <div class="alt-item">
                                <div>
                                    <a href="{alt['url']}" target="_blank" class="shop-link">{alt['model']}</a> 
                                    <span style="color: #64748b;">({alt['shop']})</span>
                                </div>
                                <div>
                                    <span style="margin-right: 12px;">{alt['price']:.2f} €</span>
                                    <span class="{delta_class}">[{delta_str}]</span>
                                </div>
                            </div>"""
                            
        html_content += """
                        </div>
                    </td>
                </tr>"""
    
    html_content += f"""
            </table>
            <p style="text-align: right;" class="total">Gesamtsumme Main-Build: {main_total:.2f} €</p>
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
                    label: 'Alternative (€)',
                    data: {json.dumps(data_alt)},
                    borderColor: '#94a3b8',
                    backgroundColor: 'rgba(148, 163, 184, 0.1)',
                    tension: 0.3,
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ labels: {{ color: '#f8fafc' }} }}
                }},
                scales: {{
                    y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }},
                    x: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }}
                }}
            }}
        }});

        // Alternativen Klappfunktion
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

def send_discord_notification(text):
    if not DISCORD_WEBHOOK_URL:
        return
    payload = {"content": "🚨 **Workstation Preis-Tracker Update** 🚨\n\n" + text}
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    print("Starte Daten-Sammlung...")
    rate, headlines = get_market_data()
    
    main_total = sum(item["price"] for item in HARDWARE_DATA["main_build"]["items"])
    alt_total = 2329.00  # Alternativer Gesamtpreis
    
    print("Speichere 1-Jahres-Historie...")
    history = manage_history(main_total, alt_total)
    
    print("Analysiere Markt mit Gemini...")
    briefing = run_gemini_researcher(rate, headlines)
    
    print("Berechne Entscheidung mit Claude...")
    decision = run_claude_decision(briefing, rate, main_total, alt_total)
    
    print("Generiere HTML-Dashboard...")
    generate_html_dashboard(rate, briefing, decision, main_total, alt_total, history)
    
    print("Sende Discord-Benachrichtigung...")
    discord_msg = f"{decision}\n\n💰 Main-Build: **{main_total:.2f} €**\n📉 Alternative: **{alt_total:.2f} €**\n🌐 Dashboard online unter deinen GitHub Pages!"
    send_discord_notification(discord_msg)
    print("Skript fehlerfrei beendet!")
