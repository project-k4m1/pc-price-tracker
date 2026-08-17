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

# Hardware-Matrix: Main-Build vs. Alternative
HARDWARE_DATA = {
    "main_build": {
        "name": "High-End Main-Build (Wunsch-Setup)",
        "items": [
            {"part": "Grafikkarte", "model": "MSI GeForce RTX 5070 Ti Gaming Trio OC", "price": 1248.99, "shop": "Notebooksbilliger"},
            {"part": "CPU & RAM Bundle", "model": "AMD Ryzen 9 9950X3D + 48GB DDR5-6000", "price": 1095.00, "shop": "Caseking"},
            {"part": "Mainboard", "model": "MSI MAG X870E TOMAHAWK WIFI", "price": 284.36, "shop": "Notebooksbilliger"},
            {"part": "SSD", "model": "Samsung 990 PRO SSD 1TB", "price": 219.00, "shop": "Notebooksbilliger"},
            {"part": "Gehäuse & Kühlung", "model": "Lian Li O11 Vision Compact + NZXT Kraken Elite 360", "price": 549.00, "shop": "Idealo / Mix"}
        ]
    },
    "alt_build": {
        "name": "Alternative / Preis-optimierter Build",
        "items": [
            {"part": "Grafikkarte", "model": "MSI GeForce RTX 5070 Ti Ventus 3X", "price": 1149.00, "shop": "Idealo"},
            {"part": "Prozessor", "model": "AMD Ryzen 9 7900X (Einzelkauf)", "price": 315.00, "shop": "Mindfactory"},
            {"part": "Arbeitsspeicher", "model": "Crucial Pro 48GB DDR5-5600", "price": 165.00, "shop": "Mindfactory"},
            {"part": "Mainboard & SSD", "model": "MSI B650 Tomahawk + 1TB Lexar SSD", "price": 280.00, "shop": "Mindfactory"},
            {"part": "Gehäuse & Kühlung", "model": "Fractal North XL + Standard AIO", "price": 420.00, "shop": "Idealo"}
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
    
    # NEUES GOOGLE SDK
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"Analysiere kurz (max. 3 Sätze auf Deutsch) die Marktlage für PC-Komponenten:\n- EUR/USD: {rate}\n- News: {headlines}"
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

def run_claude_decision(briefing, rate, main_total, alt_total):
    if not ANTHROPIC_API_KEY:
        return "Anthropic API Key nicht konfiguriert."
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    prompt = f"""
    Du bist der Chef-Einkaufsberater für eine High-End Workstation.
    Spezifischer Einsatzzweck: Gigantische Ableton 12 Projekte (viele VSTs), 3D-Scannen mit dem Revopoint POP 4 (riesige Punktewolken verarbeiten und Meshing) UND aktuelles High-End Gaming mit aktivem Raytracing.
    Markt-Briefing: {briefing}
    Wechselkurs EUR/USD: {rate}
    Gesamtpreis Main-Build (9950X3D + 48GB + RTX 5070 Ti Gaming Trio): {main_total:.2f} €
    Gesamtpreis Alternative (7900X + 48GB + RTX 5070 Ti Ventus): {alt_total:.2f} €
    
    Gib eine klare Empfehlung ab: Lohnt sich der Aufpreis für das Main-Build in Bezug auf diese extremen Anforderungen (Ableton, 3D, Raytracing-Gaming), und soll man JETZT KAUFEN oder WARTEN? 
    Begründe deine Entscheidung präzise in 3 bis 4 Sätzen auf Deutsch.
    """
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
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
            
    today_str = datetime.datetime.now().strftime("%d.%m.%Y")
    
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
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ background-color: #334155; color: #e2e8f0; }}
        .total {{ font-weight: bold; color: #34d399; font-size: 1.1rem; }}
        .badge {{ background: #0284c7; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; }}
        .focus-badge {{ display: inline-block; background: #8b5cf6; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; margin-bottom: 10px; font-weight: bold; }}
        canvas {{ max-height: 300px; width: 100%; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🖥️ KI PC-Preis-Tracker Dashboard</h1>
        <div class="subtitle">Zuletzt aktualisiert: {now} | EUR/USD: {rate}</div>

        <div class="card">
            <h2>🤖 KI-Kaufberatung (Claude & Gemini)</h2>
            <div class="focus-badge">🎯 Optmiert für Ableton 12, Revopoint 3D & Raytracing</div>
            <p><strong>Markt-Briefing:</strong> {briefing}</p>
            <div class="ai-box">
                <strong>Experten-Empfehlung:</strong><br><br>{decision.replace(chr(10), '<br>')}
            </div>
        </div>
        
        <div class="card">
            <h2>📈 Preisverlauf (Historie)</h2>
            <canvas id="priceChart"></canvas>
        </div>

        <div class="card">
            <h2>⭐ {HARDWARE_DATA['main_build']['name']}</h2>
            <table>
                <tr><th>Kategorie</th><th>Komponente</th><th>Shop</th><th>Preis</th></tr>"""
    
    for item in HARDWARE_DATA['main_build']['items']:
        html_content += f"<tr><td><span class='badge'>{item['part']}</span></td><td>{item['model']}</td><td>{item['shop']}</td><td>{item['price']:.2f} €</td></tr>"
    
    html_content += f"""
            </table>
            <p style="text-align: right;" class="total">Gesamtsumme Main-Build: {main_total:.2f} €</p>
        </div>

        <div class="card">
            <h2>💡 {HARDWARE_DATA['alt_build']['name']}</h2>
            <table>
                <tr><th>Kategorie</th><th>Komponente</th><th>Shop</th><th>Preis</th></tr>"""
    
    for item in HARDWARE_DATA['alt_build']['items']:
        html_content += f"<tr><td><span class='badge'>{item['part']}</span></td><td>{item['model']}</td><td>{item['shop']}</td><td>{item['price']:.2f} €</td></tr>"
        
    html_content += f"""
            </table>
            <p style="text-align: right;" class="total">Gesamtsumme Alternative: {alt_total:.2f} €</p>
        </div>
    </div>
    
    <script>
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
    payload = {"content": "🚨 **Workstation Preis-Tracker (Ableton/3D/Raytracing) Update** 🚨\n\n" + text}
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    print("Starte Daten-Sammlung...")
    rate, headlines = get_market_data()
    
    main_total = sum(item["price"] for item in HARDWARE_DATA["main_build"]["items"])
    alt_total = sum(item["price"] for item in HARDWARE_DATA["alt_build"]["items"])
    
    print("Speichere Historie...")
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
