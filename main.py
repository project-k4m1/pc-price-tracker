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

# Hardware-Matrix mit funktionierenden Such-Links, Bildern und echtem Bundle-Status
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
        except Exception
