import os
import datetime
import feedparser
import requests
import google.generativeai as genai
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
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"Analysiere kurz (max. 3 Sätze auf Deutsch) die Marktlage für PC-Komponenten:\n- EUR/USD: {rate}\n- News: {headlines}"
    return model.generate_content(prompt).text

def run_claude_decision(briefing, rate, main_total, alt_total):
    if not ANTHROPIC_API_KEY:
        return "Anthropic API Key nicht konfiguriert."
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    prompt = f"""
    Du bist der Chef-Einkaufsberater für eine High-End Workstation.
    Markt-Briefing: {briefing}
    Wechselkurs EUR/USD: {rate}
    Gesamtpreis Main-Build: {main_total:.2f} €
    Gesamtpreis Alternative: {alt_total:.2f} €
    
    Gib eine klare Empfehlung ab: JETZT KAUFEN oder WARTEN? 
    Begründe deine Entscheidung in 3 präzisen Sätzen auf Deutsch.
    """
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

def generate_html_dashboard(rate, briefing, decision, main_total, alt_total):
    now = datetime.datetime.now().strftime("%d.%m.%Y um %H:%M Uhr")
    
    html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KI PC-Komponenten Preis-Tracker & Dashboard</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
        .container {{ max-width: 1000px; margin: auto; }}
        h1 {{ color: #38bdf8; text-align: center; margin-bottom: 5px; }}
        .subtitle {{ text-align: center; color: #94a3b8; margin-bottom: 30px; font-size: 0.9rem; }}
        .card {{ background: #1e293b; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
        .ai-box {{ background: #0f172a; border-left: 4px solid #38bdf8; padding: 15px; border-radius: 4px; margin-top: 15px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ background-color: #334155; color: #e2e8f0; }}
        .total {{ font-weight: bold; color: #34d399; font-size: 1.1rem; }}
        .badge {{ background: #0284c7; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🖥️ KI PC-Preis-Tracker Dashboard</h1>
        <div class="subtitle">Zuletzt aktualisiert: {now} | EUR/USD: {rate}</div>

        <div class="card">
            <h2>🤖 KI-Kaufberatung (Claude & Gemini)</h2>
            <p><strong>Markt-Briefing:</strong> {briefing}</p>
            <div class="ai-box">
                <strong>Empfehlung:</strong><br>{decision.replace(chr(10), '<br>')}
            </div>
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
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("HTML Dashboard erfolgreich als index.html generiert.")

def send_discord_notification(text):
    if not DISCORD_WEBHOOK_URL:
        return
    payload = {"content": "🚨 **KI-Workstation Preis-Tracker Update** 🚨\n\n" + text}
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    print("Starte Daten-Sammlung...")
    rate, headlines = get_market_data()
    
    main_total = sum(item["price"] for item in HARDWARE_DATA["main_build"]["items"])
    alt_total = sum(item["price"] for item in HARDWARE_DATA["alt_build"]["items"])
    
    print("Analysiere Markt mit Gemini...")
    briefing = run_gemini_researcher(rate, headlines)
    
    print("Berechne Entscheidung mit Claude...")
    decision = run_claude_decision(briefing, rate, main_total, alt_total)
    
    print("Generiere HTML-Dashboard...")
    generate_html_dashboard(rate, briefing, decision, main_total, alt_total)
    
    print("Sende Discord-Benachrichtigung...")
    discord_msg = f"{decision}\n\n💰 Main-Build: **{main_total:.2f} €**\n📉 Alternative: **{alt_total:.2f} €**\n🌐 Dashboard online unter deinen GitHub Pages!"
    send_discord_notification(discord_msg)
    print("Skript fehlerfrei beendet!")
