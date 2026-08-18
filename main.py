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
                "url": "https://www.notebooksbilliger.de/msi+geforce+rtx+5070+ti+16g+gaming+trio+oc+grafikkarte-879823",
                "img": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "MSI GeForce RTX 5070 Ti 16G VENTUS 3X OC", "price": 1149.00, "shop": "Notebooksbilliger", "url": "https://www.notebooksbilliger.de/msi+geforce+rtx+5070+ti+16g+ventus+3x+oc+grafikkarte-879820"},
                    {"model": "NVIDIA GeForce RTX 4080 SUPER 16GB", "price": 1050.00, "shop": "Mindfactory", "url": "https://www.mindfactory.de/product_info.php/16GB-MSI-GeForce-RTX-4080-SUPER"}
                ]
            },
            {
                "id": "m_cpu_ram",
                "part": "CPU & RAM Bundle",
                "model": "AMD Ryzen 9 9950X3D + ADATA XPG Lancer BLADE RGB 48 GB DDR5-6000",
                "price": 1095.00,
                "shop": "Caseking",
                "url": "https://www.caseking.de/amd-ryzen-9-9950x3d-bundle-48gb-ddr5-6000-hpam-254.html",
                "img": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=120&auto=format&fit=crop&q=80",
                "is_bundle": True,  # ECHTES BUNDLE
                "alts": [
                    {"model": "AMD Ryzen 7 7800X3D (Einzelkauf)", "price": 390.00, "shop": "Mindfactory", "url": "https://www.mindfactory.de/product_info.php/AMD-Ryzen-7-7800X3D"},
                    {"model": "Intel Core i9-14900K (Einzelkauf)", "price": 540.00, "shop": "Caseking", "url": "https://www.caseking.de/intel-core-i9-14900k-hpit-752.html"}
                ]
            },
            {
                "id": "m_mb",
                "part": "Mainboard",
                "model": "MSI MAG X870E TOMAHAWK WIFI",
                "price": 284.36,
                "shop": "Notebooksbilliger",
                "url": "https://www.notebooksbilliger.de/msi+mag+x870e+tomahawk+wifi+mainboard-865412",
                "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "Gigabyte X870 AORUS ELITE WIFI7", "price": 295.00, "shop": "Alternate", "url": "https://www.alternate.de/Gigabyte/X870-AORUS-ELITE-WIFI7-Mainboard"},
                    {"model": "MSI B650 TOMAHAWK WIFI", "price": 180.00, "shop": "Mindfactory", "url": "https://www.mindfactory.de/product_info.php/MSI-MAG-B650-Tomahawk-WIFI"}
                ]
            },
            {
                "id": "m_ssd",
                "part": "SSD Storage",
                "model": "Samsung 990 PRO SSD 1TB NVMe M.2",
                "price": 219.00,
                "shop": "Notebooksbilliger",
                "url": "https://www.notebooksbilliger.de/samsung+990+pro+1tb+m2+pcie+40+ssd-785412",
                "img": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=120&auto=format&fit=crop&q=80",
                "is_bundle": False,
                "alts": [
                    {"model": "WD_BLACK SN850X NVMe SSD 2TB", "price": 185.00, "shop": "Mindfactory", "url": "https://www.mindfactory.de/product_info.php/2TB-WD-Black-SN850X"},
                    {"model": "Lexar NM790 2TB M.2 NVMe", "price": 140.00, "shop": "Mindfactory", "url": "https://www.mindfactory.de/product_info.php/2TB-Lexar-NM790"}
                ]
            },
            {
                "id": "m_case_cool",
                "part": "Gehäuse & Kühlung",
                "model": "Lian Li O11 Vision Compact + NZXT Kraken Elite 360 RGB",
                "price": 549.00,
                "shop": "Caseking / NBB",
                "url": "https://www.caseking.de/lian-li-o11-vision-compact-midi-tower-gehaeuse-geli-942.html",
                "img": "
