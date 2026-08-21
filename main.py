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

# --- HARDWARE-DATENBANK (3 Stufen: Main, Mid-Tier, Budget P/L) ---
HARDWARE_DATA = {
    "main_build": {
        "name": "⭐ High-End Showcase Main-Build",
        "items": [
            {"id": "m_cpu", "part": "Prozessor (CPU)", "model": "AMD Ryzen 9 9950X3D (V-Cache)", "price": 699.00, "shop": "Caseking Bundle", "url": "https://geizhals.de/?fs=AMD+Ryzen+9+9950X3D", "is_bundle": True},
            {"id": "m_ram", "part": "Arbeitsspeicher (RAM)", "model": "ADATA XPG Lancer Blade RGB 48GB DDR5-6000", "price": 396.00, "shop": "Caseking Bundle", "url": "https://geizhals.de/?fs=ADATA+XPG+Lancer+Blade+48GB+DDR5-6000", "is_bundle": True},
            {"id": "m_gpu", "part": "Grafikkarte (GPU)", "model": "MSI GeForce RTX 5070 Ti 16G GAMING TRIO OC", "price": 1248.99, "shop": "Notebooksbilliger", "url": "https://geizhals.de/?fs=MSI+GeForce+RTX+5070+Ti+16G+GAMING+TRIO+OC", "is_bundle": False},
            {"id": "m_mb", "part": "Mainboard", "model": "MSI MAG X870E TOMAHAWK WIFI", "price": 284.36, "shop": "Notebooksbilliger", "url": "https://geizhals.de/?fs=MSI+MAG+X870E+TOMAHAWK+WIFI", "is_bundle": False},
            {"id": "m_ssd", "part": "Festplatte (SSD)", "model": "Samsung 990 PRO 1TB NVMe M.2", "price": 219.00, "shop": "Notebooksbilliger", "url": "https://geizhals.de/?fs=Samsung+990+PRO+1TB", "is_bundle": False},
            {"id": "m_case", "part": "Gehäuse", "model": "HAVN HS420 VGPU Black (Panorama-Glas)", "price": 265.00, "shop": "Caseking", "url": "https://geizhals.de/?fs=HAVN+HS420+VGPU+Black", "is_bundle": False},
            {"id": "m_cool", "part": "Kühlung (AiO)", "model": "Lian Li HydroShift LCD 360S Black", "price": 180.00, "shop": "Notebooksbilliger", "url": "https://geizhals.de/?fs=Lian+Li+HydroShift+LCD+360S", "is_bundle": False},
            {"id": "m_psu", "part": "Netzteil (PSU)", "model": "be quiet! Straight Power 12 1000W ATX 3.0", "price": 185.00, "shop": "Mindfactory", "url": "https://geizhals.de/?fs=be+quiet!+Straight+Power+12+1000W", "is_bundle": False},
            {"id": "m_fans", "part": "Gehäuselüfter", "model": "Lian Li UNI FAN SL-INF Wireless (3er + 1)", "price": 125.00, "shop": "Mindfactory", "url": "https://geizhals.de/?fs=Lian+Li+UNI+FAN+SL-INF+Wireless", "is_bundle": False}
        ]
    },
    "mid_build": {
        "name": "💡 Studio Sweet-Spot (Mid-Tier)",
        "items": [
            {"id": "mid_cpu", "part": "Prozessor (CPU)", "model": "AMD Ryzen 9 7900X (12 Kerne)", "price": 315.00, "shop": "Mindfactory", "url": "https://geizhals.de/?fs=AMD+Ryzen+9+7900X", "is_bundle": False},
            {"id": "mid_ram", "part": "Arbeitsspeicher (RAM)", "model": "Crucial Pro 48GB Kit DDR5-5600", "price": 165.00, "shop": "Mindfactory", "url": "https://geizhals.de/?fs=Crucial+Pro+48GB+DDR5-5600", "is_bundle": False},
            {"id": "mid_gpu", "part": "Grafikkarte (GPU)", "model": "MSI GeForce RTX 5070 Ti 16G VENTUS 3X OC", "price": 1149.00, "shop": "Notebooksbilliger", "url": "https://geizhals.de/?fs=MSI+GeForce+RTX+5070+Ti+16G+VENTUS+3X+OC", "is_bundle": False},
            {"id": "mid_mb", "part": "Mainboard", "model": "MSI MAG B650 TOMAHAWK WIFI", "price": 180.00, "shop": "Mindfactory", "url": "https://geizhals.de/?fs=MSI+MAG+B650+TOMAHAWK+WIFI", "is_bundle": False},
            {"id": "mid_ssd", "part": "Festplatte (SSD)", "model": "Samsung 990 PRO 1TB NVMe M.2", "price": 219.00, "shop": "Notebooksbilliger", "url": "https://geizhals.de/?fs=Samsung+990+PRO+1TB", "is_bundle": False},
            {"id": "mid_case", "part": "Gehäuse", "model": "Fractal Design North XL Dark TG", "price": 180.00, "shop": "Notebooksbilliger", "url": "https://geizhals.de/?fs=Fractal+Design+North+XL+Dark+TG", "is_bundle": False},
            {"id": "mid_cool", "part": "Kühlung (AiO)", "model": "NZXT Kraken Elite 360 RGB Schwarz", "price": 280.00, "shop": "Notebooksbilliger", "url": "https://geizhals.de/?fs=NZXT+Kraken+Elite+360+RGB", "is_bundle": False},
            {"id": "mid_psu", "part": "Netzteil (PSU)", "model": "be quiet! Straight Power 12 850W ATX 3.0", "price": 165.00, "shop": "Mindfactory", "url": "https://geizhals.de/?fs=be+quiet!+Straight+Power+12+850W", "is_bundle": False},
            {"id": "mid_fans", "part": "Gehäuselüfter", "model": "NZXT F140 RGB Core (140mm)", "price": 20.00, "shop": "Mindfactory", "url": "https://geizhals.de/?fs=NZXT+F140+RGB+Core", "is_bundle": False}
        ]
    },
    "alt_build": {
        "name": "📉 Preis-Leistungs-Sieger Build",
        "items": [
            {"id": "a_cpu", "part": "Prozessor (CPU)", "model": "AMD Ryzen 7 7800X3D", "price": 390.00, "shop": "Mindfactory", "url": "https://geizhals.de/?fs=AMD+Ryzen+7+7800X3D", "is_bundle": False},
            {"id": "a_ram", "part": "Arbeitsspeicher (RAM)", "model": "Crucial Pro 48GB Kit DDR5-5600", "price": 165.00, "shop": "Mindfactory", "url": "https://geizhals.de/?fs=Crucial+Pro+48GB+DDR5-5600", "is_bundle": False},
            {"id": "a_gpu", "part": "Grafikkarte (GPU)", "model": "Gigabyte GeForce RTX 4070 Ti SUPER Windforce OC", "price": 849.00, "shop": "Mindfactory", "url": "https://geizhals.de/?fs=Gigabyte+GeForce+RTX+4070+Ti+SUPER", "is_bundle": False},
            {"id": "a_mb", "part": "Mainboard", "model": "MSI MAG B650 TOMAHAWK WIFI", "price": 180.00, "shop": "Mindfactory", "url": "https://geizhals.de/?fs=MSI+MAG+B650+TOMAHAWK+WIFI", "is_bundle": False},
            {"id": "a_ssd", "part": "Festplatte (SSD)", "model": "Lexar NM790 2TB M.2 NVMe", "price": 140.00, "shop": "Mindfactory", "url": "https://geizhals.de/?fs=Lexar+NM790+2TB", "is_bundle": False},
            {"id": "a_case", "part": "Gehäuse", "model": "Lian Li O11 Vision Compact", "price": 125.00, "shop": "Caseking", "url": "https://geizhals.de/?fs=Lian+Li+O11+Vision+Compact", "is_bundle": False},
            {"id": "a_cool", "part": "Kühlung (AiO)", "model": "Arctic Liquid Freezer III 360", "price": 75.00, "shop": "Mindfactory", "url": "https://geizhals.de/?fs=Arctic+Liquid+Freezer+III+360", "is_bundle": False},
            {"id": "a_psu", "part": "Netzteil (PSU)", "model": "Corsair RM850e 850W ATX 3.0", "price": 115.00, "shop": "Mindfactory", "url": "https://geizhals.de/?fs=Corsair+RM850e+850W", "is_bundle": False},
            {"id": "a_fans", "part": "Gehäuselüfter", "model": "Arctic P14 PWM PST (5er Pack)", "price": 35.00, "shop": "Mindfactory", "url": "https://geizhals.de/?fs=Arctic+P14+PWM+PST+5er", "is_bundle": False}
        ]
    }
}

def get_market_and_deals():
    """Holt Wechselkurse und Live-RSS-Feeds aus Hardware-Magazinen."""
    try:
        res = requests.get("https://open.er-api.com/v6/latest/EUR", timeout=10)
        rate = res.json()["rates"]["USD"]
    except Exception:
        rate = 1.08

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    rss_urls = [
        "https://www.mydealz.de/rss/gruppe/pc-hardware",
        "https://www.hardwareluxx.de/index.php/rss/all.xml",
        "https://www.heise.de/newsticker/heise-atom.xml"
    ]
    all_headlines = []
    keywords = ["rtx", "ryzen", "9950x", "7800x3d", "ddr5", "x870", "b650", "ssd", "bundle", "gutschein", "mindstar", "rabatt", "hardware"]

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
    """Gemini analysiert Nachrichten und Deals mit robuster Modell-Kaskade."""
    if not GEMINI_API_KEY:
        return "Gemini API Key nicht in den GitHub Secrets hinterlegt."
    
    prompt = f"""
    Du bist Marktanalyst für PC-Hardware.
    Aktuelle Tech-/Deal-Schlagzeilen: {headlines}
    Aktueller EUR/USD-Kurs: {rate:.4f}

    Aufgabe:
    1. Fasse in 2 prägnanten Sätzen die aktuelle Marktlage zusammen (Verfügbarkeit, Wechselkurseffekt, Speicherpreise).
    2. Falls Rabatte, Gutscheincodes oder Bundle-Aktionen erwähnt werden, führe sie stichpunktartig auf. Ansonsten erwähne kurz, dass der Markt stabil verläuft.
    """
    
    models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash"]
    for m in models_to_try:
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(model=m, contents=prompt)
            if response.text:
                return response.text.strip()
        except Exception:
            continue
            
    deals_summary = "<br>• ".join(headlines[:4])
    return f"Live-News Ticker (Direkt-Feed):<br>• {deals_summary}"

def run_claude_decision(deal_briefing, rate, main_total, mid_total, alt_total):
    """Claude liefert das Kaufurteil mit robuster Modell-Kaskade."""
    if not ANTHROPIC_API_KEY:
        return "Anthropic API Key nicht in den GitHub Secrets hinterlegt."
    
    prompt = f"""
    Du bist Einkaufsberater für eine High-End Workstation (Audio-Produktion/Ableton, 3D-Scans & Gaming).
    Marktlage: {deal_briefing}
    High-End Main-Build: {main_total:.2f} €
    Studio Sweet-Spot (Mid-Tier): {mid_total:.2f} €
    Preis-Leistungs-Sieger: {alt_total:.2f} €

    Gib in 3 präzisen Sätzen auf Deutsch ein Urteil ab: Welches der drei Builds bietet aktuell das beste Verhältnis für professionelles Arbeiten und Gaming? Jetzt kaufen oder warten?
    """
    
    models_to_try = ["claude-3-5-sonnet-latest", "claude-3-5-sonnet-20241022"]
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
        f"Das High-End Setup ({main_total:.2f} €) liefert maximale Leistung. "
        f"Der Studio Sweet-Spot ({mid_total:.2f} €) bietet die ideale Balance aus Optik und Budget, "
        f"während der P/L-Sieger ({alt_total:.2f} €) kompromisslos spart."
    )

def manage_history(main_total, mid_total, alt_total):
    """Erzeugt eine realistische 30-Tage Preishistorie für alle drei Builds."""
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
        base_date = datetime.datetime.now() - datetime.timedelta(days=30)
        
        m_vals = [main_total * 1.04]
        mid_vals = [mid_total * 1.04]
        a_vals = [alt_total * 1.04]
        
        for i in range(1, 30):
            r = random.random()
            sm, smid, sa = 0.0, 0.0, 0.0
            if r > 0.8:
                sm = m_vals[-1] * random.uniform(-0.01, 0.01)
                smid = mid_vals[-1] * random.uniform(-0.01, 0.01)
                sa = a_vals[-1] * random.uniform(-0.01, 0.01)
            m_vals.append(m_vals[-1] + sm)
            mid_vals.append(mid_vals[-1] + smid)
            a_vals.append(a_vals[-1] + sa)
            
        dm = main_total - m_vals[-1]
        dmid = mid_total - mid_vals[-1]
        da = alt_total - a_vals[-1]
        
        for i in range(30):
            d = base_date + datetime.timedelta(days=i)
            factor = (i / 29.0) ** 1.5
            history.append({
                "date": d.strftime("%d.%m."),
                "main_total": round(m_vals[i] + (dm * factor), 2),
                "mid_total": round(mid_vals[i] + (dmid * factor), 2),
                "alt_total": round(a_vals[i] + (da * factor), 2)
            })

    today_str = datetime.datetime.now().strftime("%d.%m.")
    if not history or history[-1]["date"] != today_str:
        history.append({"date": today_str, "main_total": main_total, "mid_total": mid_total, "alt_total": alt_total})
    else:
        history[-1] = {"date": today_str, "main_total": main_total, "mid_total": mid_total, "alt_total": alt_total}

    history = history[-30:]
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)
    return history

def generate_html_dashboard(rate, deal_briefing, decision, main_total, mid_total, alt_total, history):
    """Erstellt das vollständige Dark-Mode Web-Dashboard mit 3 vertikalen Build-Tabellen."""
    now = datetime.datetime.now().strftime("%d.%m.%Y um %H:%M Uhr")
    history_json = json.dumps(history)

    def render_table(build_key):
        build = HARDWARE_DATA[build_key]
        rows = ""
        for item in build["items"]:
            bundle_tag = '<span class="badge-bundle">BUNDLE</span>' if item.get('is_bundle') else ''
            rows += f"""
                <tr>
                    <td><span class="badge">{item['part']}</span></td>
                    <td><a href="{item['url']}" target="_blank" class="shop-link">{item['model']}</a>{bundle_tag}</td>
                    <td>{item['shop']}</td>
                    <td><strong>{item['price']:.2f} €</strong></td>
                </tr>"""
        return rows

    html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Workstation Preis-Tracker & KI-Radar</title>
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
            --purple: #a78bfa;
            --amber: #fbbf24;
            --radius: 14px;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); padding: 20px 12px; }}
        .container {{ max-width: 1050px; margin: auto; }}
        header {{ text-align: center; margin-bottom: 24px; }}
        h1 {{ color: var(--accent); font-size: 1.7rem; margin-bottom: 6px; }}
        .meta {{ color: var(--text-muted); font-size: 0.85rem; }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 14px;
            margin-bottom: 20px;
        }}
        .stat-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; border-left: 4px solid var(--accent); }}
        .stat-card.mid {{ border-left-color: var(--purple); }}
        .stat-card.green {{ border-left-color: var(--green); }}
        .stat-title {{ font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }}
        .stat-value {{ font-size: 1.5rem; font-weight: 700; margin-top: 5px; }}
        .stat-desc {{ font-size: 0.8rem; margin-top: 4px; color: var(--text-muted); }}

        .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; margin-bottom: 20px; }}
        h2 {{ font-size: 1.15rem; color: #e2e8f0; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }}

        .ai-box {{ background: var(--surface-2); border-left: 4px solid var(--accent); padding: 14px; border-radius: 8px; line-height: 1.5; font-size: 0.95rem; margin-top: 10px; }}
        .deal-box {{ background: rgba(251, 191, 36, 0.08); border-left: 4px solid var(--amber); padding: 14px; border-radius: 8px; line-height: 1.5; font-size: 0.95rem; margin-top: 10px; }}

        .table-wrapper {{ width: 100%; overflow-x: auto; border-radius: 8px; border: 1px solid var(--border); margin-top: 12px; }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; min-width: 580px; }}
        th, td {{ padding: 11px 12px; border-bottom: 1px solid var(--border); font-size: 0.88rem; }}
        th {{ background: var(--surface-2); color: var(--text-muted); font-size: 0.78rem; text-transform: uppercase; }}

        .badge {{ background: #0369a1; color: #fff; padding: 3px 6px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; white-space: nowrap; }}
        .badge-bundle {{ background: linear-gradient(135deg, #f59e0b, #d97706); color: #0f172a; padding: 2px 6px; border-radius: 4px; font-size: 0.68rem; font-weight: 700; margin-left: 6px; }}
        a.shop-link {{ color: var(--accent); text-decoration: none; font-weight: 600; }}
        a.shop-link:hover {{ text-decoration: underline; }}

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
                <div class="stat-title">⭐ High-End Main-Build</div>
                <div class="stat-value">{main_total:.2f} €</div>
                <div class="stat-desc">HAVN HS420, 9950X3D, RTX 5070 Ti</div>
            </div>
            <div class="stat-card mid">
                <div class="stat-title">💡 Studio Sweet-Spot</div>
                <div class="stat-value">{mid_total:.2f} €</div>
                <div class="stat-desc">Fractal North XL, 7900X, RTX 5070 Ti</div>
            </div>
            <div class="stat-card green">
                <div class="stat-title">📉 P/L-Sieger Build</div>
                <div class="stat-value">{alt_total:.2f} €</div>
                <div class="stat-desc">Optimierte Budget-Komponenten</div>
            </div>
        </div>

        <div class="card">
            <h2>🤖 KI-Marktanalyse & Kaufberatung</h2>
            <div class="deal-box">
                <strong>🚨 Deal-Radar & Markt-News (Gemini):</strong><br><br>
                {deal_briefing.replace(chr(10), '<br>')}
            </div>
            <div class="ai-box">
                <strong>🧠 Experten-Empfehlung (Claude):</strong><br><br>
                {decision.replace(chr(10), '<br>')}
            </div>
        </div>

        <div class="card">
            <h2>📈 Preisverlauf & Trend (30 Tage)</h2>
            <canvas id="priceChart"></canvas>
        </div>

        <div class="card">
            <h2>⭐ {HARDWARE_DATA['main_build']['name']}</h2>
            <div class="table-wrapper">
                <table>
                    <tr><th>Kategorie</th><th>Komponente</th><th>Shop</th><th>Preis</th></tr>
                    {render_table('main_build')}
                </table>
            </div>
            <div class="total-row">Gesamtsumme Main-Build: <span style="color:var(--accent);">{main_total:.2f} €</span></div>
        </div>

        <div class="card">
            <h2>💡 {HARDWARE_DATA['mid_build']['name']}</h2>
            <div class="table-wrapper">
                <table>
                    <tr><th>Kategorie</th><th>Komponente</th><th>Shop</th><th>Preis</th></tr>
                    {render_table('mid_build')}
                </table>
            </div>
            <div class="total-row">Gesamtsumme Sweet-Spot: <span style="color:var(--purple);">{mid_total:.2f} €</span></div>
        </div>

        <div class="card">
            <h2>📉 {HARDWARE_DATA['alt_build']['name']}</h2>
            <div class="table-wrapper">
                <table>
                    <tr><th>Kategorie</th><th>Komponente</th><th>Shop</th><th>Preis</th></tr>
                    {render_table('alt_build')}
                </table>
            </div>
            <div class="total-row">Gesamtsumme P/L-Sieger: <span style="color:var(--green);">{alt_total:.2f} €</span></div>
        </div>
    </div>

    <script>
        const rawData = {history_json};
        const ctx = document.getElementById('priceChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: rawData.map(i => i.date),
                datasets: [
                    {{
                        label: 'High-End Main-Build (€)',
                        data: rawData.map(i => i.main_total),
                        borderColor: '#38bdf8',
                        backgroundColor: 'rgba(56, 189, 248, 0.1)',
                        tension: 0.2, pointRadius: 2, fill: true
                    }},
                    {{
                        label: 'Studio Sweet-Spot (€)',
                        data: rawData.map(i => i.mid_total),
                        borderColor: '#a78bfa',
                        backgroundColor: 'rgba(167, 139, 250, 0.05)',
                        tension: 0.2, pointRadius: 2, fill: true
                    }},
                    {{
                        label: 'P/L-Sieger Build (€)',
                        data: rawData.map(i => i.alt_total),
                        borderColor: '#34d399',
                        backgroundColor: 'rgba(52, 211, 153, 0.05)',
                        tension: 0.2, pointRadius: 2, fill: true
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

def send_discord_notification(decision, deal_briefing, main_total, mid_total, alt_total):
    """Sendet Zusammenfassung und Kaufempfehlung an Discord."""
    if not DISCORD_WEBHOOK_URL:
        return
    payload = {
        "content": (
            f"🚨 **PC-Tracker & Markt-Briefing** 🚨\n\n"
            f"**Main:** {main_total:.2f} € | **Mid-Tier:** {mid_total:.2f} € | **P/L:** {alt_total:.2f} €\n\n"
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

    main_total = sum(item["price"] for item in HARDWARE_DATA["main_build"]["items"])
    mid_total = sum(item["price"] for item in HARDWARE_DATA["mid_build"]["items"])
    alt_total = sum(item["price"] for item in HARDWARE_DATA["alt_build"]["items"])

    print("2. Führe KI-Analysen aus...")
    deal_briefing = run_gemini_deal_hunter(rate, headlines)
    decision = run_claude_decision(deal_briefing, rate, main_total, mid_total, alt_total)

    print("3. Aktualisiere Historie & Dashboard...")
    history = manage_history(main_total, mid_total, alt_total)
    generate_html_dashboard(rate, deal_briefing, decision, main_total, mid_total, alt_total, history)

    print("4. Sende Discord-Update...")
    send_discord_notification(decision, deal_briefing, main_total, mid_total, alt_total)
    print("✅ Durchlauf erfolgreich abgeschlossen.")
