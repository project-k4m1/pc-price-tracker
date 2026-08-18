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

# Hardware-Matrix mit intelligenten Such-Links (Geizhals), die nie ablaufen
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
                "url": "https://geizhals.de/?fs=MSI+GeForce+RTX+5070+Ti+Gaming+Trio",
                "img": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "MSI GeForce RTX 5070 Ti 16G VENTUS 3X OC", "price": 1149.00, "shop": "Geizhals", "url": "https://geizhals.de/?fs=MSI+GeForce+RTX+5070+Ti+Ventus+3X"},
                    {"model": "NVIDIA GeForce RTX 4080 SUPER 16GB", "price": 1050.00, "shop": "Geizhals", "url": "https://geizhals.de/?fs=RTX+4080+SUPER+16GB"}
                ]
            },
            {
                "id": "m_cpu_ram",
                "part": "CPU & RAM Bundle",
                "model": "AMD Ryzen 9 9950X3D + 48 GB DDR5-6000",
                "price": 1095.00,
                "shop": "Caseking",
                "url": "https://geizhals.de/?fs=AMD+Ryzen+9+9950X3D",
                "img": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=120&auto=format&fit=crop&q=80",
                "is_bundle": True,
                "alts": [
                    {"model": "AMD Ryzen 7 7800X3D (Einzelkauf)", "price": 390.00, "shop": "Geizhals", "url": "https://geizhals.de/?fs=AMD+Ryzen+7+7800X3D"},
                    {"model": "Intel Core i9-14900K (Einzelkauf)", "price": 540.00, "shop": "Geizhals", "url": "https://geizhals.de/?fs=Intel+Core+i9-14900K"}
                ]
            },
            {
                "id": "m_mb",
                "part": "Mainboard",
                "model": "MSI MAG X870E TOMAHAWK WIFI",
                "price": 284.36,
                "shop": "Notebooksbilliger",
                "url": "https://geizhals.de/?fs=MSI+MAG+X870E+TOMAHAWK+WIFI",
                "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "Gigabyte X870 AORUS ELITE WIFI7", "price": 295.00, "shop": "Geizhals", "url": "https://geizhals.de/?fs=Gigabyte+X870+AORUS+ELITE+WIFI7"},
                    {"model": "MSI B650 TOMAHAWK WIFI", "price": 180.00, "shop": "Geizhals", "url": "https://geizhals.de/?fs=MSI+MAG+B650+TOMAHAWK+WIFI"}
                ]
            },
            {
                "id": "m_ssd",
                "part": "SSD Storage",
                "model": "Samsung 990 PRO SSD 1TB NVMe M.2",
                "price": 219.00,
                "shop": "Notebooksbilliger",
                "url": "https://geizhals.de/?fs=Samsung+990+PRO+1TB",
                "img": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "WD_BLACK SN850X NVMe SSD 2TB", "price": 185.00, "shop": "Geizhals", "url": "https://geizhals.de/?fs=WD_BLACK+SN850X+2TB"},
                    {"model": "Lexar NM790 2TB M.2 NVMe", "price": 140.00, "shop": "Geizhals", "url": "https://geizhals.de/?fs=Lexar+NM790+2TB"}
                ]
            },
            {
                "id": "m_case_cool",
                "part": "Gehäuse & Kühlung",
                "model": "Lian Li O11 Vision Compact + NZXT Kraken Elite 360",
                "price": 549.00,
                "shop": "Idealo / Mix",
                "url": "https://geizhals.de/?fs=Lian+Li+O11+Vision+Compact",
                "img": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "Fractal Design North XL Charcoal Black TG", "price": 155.01, "shop": "Geizhals", "url": "https://geizhals.de/?fs=Fractal+Design+North+XL"},
                    {"model": "NZXT Kraken Elite 360 RGB Schwarz", "price": 279.59, "shop": "Geizhals", "url": "https://geizhals.de/?fs=NZXT+Kraken+Elite+360+RGB"}
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
                "url": "https://geizhals.de/?fs=MSI+GeForce+RTX+5070+Ti+Ventus+3X",
                "img": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "Gigabyte GeForce RTX 4070 Ti SUPER Gaming OC", "price": 849.00, "shop": "Geizhals", "url": "https://geizhals.de/?fs=RTX+4070+Ti+SUPER+Gigabyte"}
                ]
            },
            {
                "id": "a_cpu",
                "part": "Prozessor",
                "model": "AMD Ryzen 9 7900X 12x 4.70GHz",
                "price": 315.00,
                "shop": "Mindfactory",
                "url": "https://geizhals.de/?fs=AMD+Ryzen+9+7900X",
                "img": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "AMD Ryzen 7 7800X3D 8x 4.20GHz", "price": 390.00, "shop": "Geizhals", "url": "https://geizhals.de/?fs=AMD+Ryzen+7+7800X3D"}
                ]
            },
            {
                "id": "a_ram",
                "part": "Arbeitsspeicher",
                "model": "Crucial Pro 48GB Kit DDR5-5600 UDIMM",
                "price": 165.00,
                "shop": "Mindfactory",
                "url": "https://geizhals.de/?fs=Crucial+Pro+48GB+DDR5",
                "img": "https://images.unsplash.com/photo-1562976540-1e02c414c18f?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "Corsair Vengeance DDR5-6000 64GB Dual Kit", "price": 210.00, "shop": "Geizhals", "url": "https://geizhals.de/?fs=Corsair+Vengeance+DDR5+64GB"}
                ]
            },
            {
                "id": "a_mb_ssd",
                "part": "Mainboard & SSD",
                "model": "MSI B650 TOMAHAWK WIFI + 1TB Lexar SSD",
                "price": 280.00,
                "shop": "Mindfactory",
                "url": "https://geizhals.de/?fs=MSI+MAG+B650+TOMAHAWK",
                "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=120&auto=format&fit=crop&q=80",
                "is_bundle": True,
                "alts": [
                    {"model": "ASUS TUF Gaming B650-Plus WIFI", "price": 195.00, "shop": "Geizhals", "url": "https://geizhals.de/?fs=ASUS+TUF+Gaming+B650-Plus"}
                ]
            },
            {
                "id": "a_case_cool",
                "part": "Gehäuse & Kühlung",
                "model": "Fractal North XL Charcoal Black + 360mm AIO",
                "price": 420.00,
                "shop": "Notebooksbilliger",
                "url": "https://geizhals.de/?fs=Fractal+Design+North+XL",
                "img": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "be quiet! Shadow Base 800 FX Black", "price": 180.00, "shop": "Geizhals", "url": "https://geizhals.de/?fs=be+quiet!+Shadow+Base+800"}
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
        "https://www.hardwareluxx.de/index.php/rss/all.xml"
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
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>KI PC-Komponenten Preis-Tracker & Dashboard</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🖥️</text></svg>">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Inter', -apple-system, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px 10px; overflow-x: hidden; }}
        .container {{ width: 100%; max-width: 1050px; margin: auto; }}
        h1 {{ color: #38bdf8; text-align: center; margin-bottom: 5px; font-size: 1.8rem; font-weight: 800; letter-spacing: -0.5px; }}
        .subtitle {{ text-align: center; color: #94a3b8; margin-bottom: 30px; font-size: 0.9rem; }}
        
        /* Modern Cards */
        .card {{ background: #1e293b; border-radius: 16px; border: 1px solid #334155; padding: 24px; margin-bottom: 24px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3); width: 100%; }}
        .card h2 {{ font-size: 1.3rem; margin-bottom: 16px; font-weight: 600; color: #f1f5f9; }}
        
        /* Header Stats */
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-bottom: 20px; }}
        .stat-box {{ background: #0f172a; padding: 20px; border-radius: 12px; border-left: 4px solid #38bdf8; border-top: 1px solid #1e293b; border-right: 1px solid #1e293b; border-bottom: 1px solid #1e293b; }}
        .stat-box.alt-box {{ border-left-color: #34d399; }}
        .stat-label {{ font-size: 0.85rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }}
        .stat-val {{ font-size: 1.6rem; font-weight: 800; margin-top: 8px; color: #f8fafc; }}
        .stat-sub {{ font-size: 0.85rem; color: #34d399; font-weight: 600; margin-top: 4px; }}

        /* AI Boxes */
        .ai-box {{ background: #0f172a; border-left: 4px solid #38bdf8; padding: 18px; border-radius: 8px; margin-top: 15px; line-height: 1.6; font-size: 0.95rem; border: 1px solid #1e293b; border-left-width: 4px; }}
        .deal-box {{ background: rgba(245, 158, 11, 0.05); border-left: 4px solid #f59e0b; padding: 18px; border-radius: 8px; margin-top: 15px; line-height: 1.6; font-size: 0.95rem; border: 1px solid #452a0a; border-left-width: 4px; }}
        
        .chart-controls {{ display: flex; gap: 10px; margin-bottom: 16px; }}
        .btn-filter {{ background: #334155; color: #f8fafc; border: none; padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; cursor: pointer; font-weight: 600; transition: all 0.2s ease; }}
        .btn-filter.active, .btn-filter:hover {{ background: #0ea5e9; box-shadow: 0 4px 6px rgba(14, 165, 233, 0.3); }}

        /* Tables */
        .table-wrapper {{ width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; margin-top: 10px; border-radius: 8px; border: 1px solid #334155; }}
        table {{ width: 100%; border-collapse: collapse; min-width: 600px; background: #0f172a; }}
        th, td {{ padding: 14px 12px; text-align: left; border-bottom: 1px solid #1e293b; vertical-align: middle; font-size: 0.95rem; }}
        th {{ background-color: #1e293b; color: #94a3b8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #334155; }}
        
        .row-item {{ cursor: pointer; transition: background 0.2s; }}
        .row-item:hover {{ background-color: #1e293b; }}
        
        /* Badges & Links */
        .badge {{ background: #0284c7; color: white; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 800; white-space: nowrap; text-transform: uppercase; }}
        .badge-alt {{ background: #059669; }}
        .badge-bundle {{ background: linear-gradient(135deg, #fbbf24, #d97706); color: #0f172a; padding: 4px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; display: inline-block; margin-left: 8px; box-shadow: 0 2px 4px rgba(251, 191, 36, 0.2); vertical-align: text-bottom; }}
        .focus-badge {{ display: inline-block; background: #8b5cf6; color: white; padding: 6px 12px; border-radius: 20px; font-size: 0.8rem; margin-bottom: 12px; font-weight: 800; box-shadow: 0 2px 6px rgba(139, 92, 246, 0.3); }}
        
        .prod-img {{ width: 44px; height: 44px; border-radius: 8px; object-fit: cover; margin-right: 12px; vertical-align: middle; border: 1px solid #334155; display: inline-block; }}
        a.shop-link {{ color: #38bdf8; text-decoration: none; font-weight: 600; word-break: break-word; transition: color 0.2s; }}
        a.shop-link:hover {{ color: #7dd3fc; text-decoration: underline; }}
        
        /* Alternativen Klappbereich */
