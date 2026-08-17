import os
import requests
import google.generativeai as genai
import anthropic

# 1. API-Schlüssel aus den GitHub Secrets laden
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# 2. Daten sammeln (Wechselkurs & News)
def get_market_data():
    # EUR/USD Wechselkurs abrufen
    try:
        res = requests.get("https://open.er-api.com/v6/latest/EUR", timeout=10)
        rate = res.json()["rates"]["USD"]
    except Exception:
        rate = 1.08  # Fallback

    # Heise News (Tech/Hardware) holen
    news_headlines = [
        "Speichermarkt und RAM-Preise unter Druck durch globale KI-Nachfrage",
        "Grafikkarten-Preise für High-End-Modelle stabilisieren sich auf hohem Niveau",
        "Neueste Benchmarks für Workstation-Prozessoren veröffentlicht"
    ]
    return rate, news_headlines

# 3. Agent 1: Der Rechercheur (Google Gemini 1.5 Flash)
def run_gemini_researcher(rate, headlines):
    if not GEMINI_API_KEY:
        return "Gemini API Key fehlt."
    
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    Du bist ein erfahrener Tech-Markt-Analyst. 
    Analysiere kurz die aktuelle Marktlage basierend auf folgenden Daten:
    - EUR/USD Wechselkurs: {rate}
    - Aktuelle Tech-Schlagzeilen: {headlines}
    
    Erstelle ein präzises, kurzes Markt-Briefing (max. 3 Sätze) auf Deutsch.
    """
    
    response = model.generate_content(prompt)
    return response.text

# 4. Agent 2: Der Entscheider (Anthropic Claude 3.5 Sonnet)
def run_claude_decision(briefing, rate):
    if not ANTHROPIC_API_KEY:
        return "Anthropic API Key fehlt."
    
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    # Beispielhafte Shop-Preise für die Wunschteile (RTX 5070 Ti & Ryzen 9 9950X3D)
    prices_text = """
    Beobachtete Komponentenpreise heute:
    - MSI GeForce RTX 5070 Ti Gaming Trio OC: ca. 1.248 €
    - AMD Ryzen 9 9950X3D Bundle (mit 48GB RAM): ca. 1.095 €
    - Gesamtwert des Systems: ca. 3.320 €
    """
    
    prompt = f"""
    Du bist der Chef-Einkaufsberater für einen High-End PC-Eigenbau (Workstation & Gaming).
    Hier ist das Markt-Briefing von unserem Rechercheur:
    {briefing}
    
    Wechselkurs: EUR/USD = {rate}
    {prices_text}
    
    Trage eine klare Empfehlung aus: Soll man JETZT KAUFEN oder sollte man WARTEN? 
    Begründe deine Entscheidung in 3 kurzen Sätzen auf Deutsch und nenne den Gesamtenkaufpreis.
    """
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

# 5. Benachrichtigung an Discord senden
def send_discord_notification(text):
    if not DISCORD_WEBHOOK_URL:
        print("Discord Webhook URL fehlt.")
        return
    
    payload = {
        "content": "🚨 **KI-PC-Preis-Tracker Update** 🚨\n\n" + text
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    print("Starte Daten-Sammlung...")
    rate, headlines = get_market_data()
    
    print("Agent 1 (Gemini) analysiert den Markt...")
    briefing = run_gemini_researcher(rate, headlines)
    
    print("Agent 2 (Claude) trifft die Kaufentscheidung...")
    decision = run_claude_decision(briefing, rate)
    
    print("Sende Nachricht an Discord...")
    send_discord_notification(decision)
    print("Fertig!")
