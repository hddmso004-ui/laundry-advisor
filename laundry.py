import os
import requests
import pandas as pd

# ==========================================
# Location (Ayutthaya)
# ==========================================
LATITUDE = 14.3532
LONGITUDE = 100.5689

WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")

# ==========================================
# Get Location Name
# ==========================================
geo_url = (
    f"https://nominatim.openstreetmap.org/reverse"
    f"?lat={LATITUDE}"
    f"&lon={LONGITUDE}"
    f"&format=jsonv2"
)

location = requests.get(
    geo_url,
    headers={"User-Agent": "LaundryAdvisor"}
).json()

location_name = location.get("display_name", "Unknown")

# ==========================================
# Open-Meteo
# ==========================================
weather_url = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LATITUDE}"
    f"&longitude={LONGITUDE}"
    "&daily=precipitation_probability_max,"
    "precipitation_sum,"
    "temperature_2m_max"
    "&forecast_days=8"
    "&timezone=Asia/Bangkok"
)

weather = requests.get(weather_url).json()

df = pd.DataFrame({
    "date": weather["daily"]["time"],
    "rain_prob": weather["daily"]["precipitation_probability_max"],
    "rain_mm": weather["daily"]["precipitation_sum"],
    "temp": weather["daily"]["temperature_2m_max"]
})

# ==========================================
# Laundry Score
# ==========================================
df["score"] = (
    (100 - df["rain_prob"]) * 0.7
    +
    (100 - (df["rain_mm"] * 5).clip(upper=100)) * 0.3
)

best = df.loc[df["score"].idxmax()]

forecast_text = ""

for _, row in df.iterrows():

    if row["score"] >= 80:
        icon = "⭐"
    elif row["score"] >= 60:
        icon = "✅"
    else:
        icon = "❌"

    forecast_text += (
        f"{icon} {row['date']} | "
        f"Score {row['score']:.0f} | "
        f"Rain {row['rain_prob']}%\n"
    )

# ==========================================
# Adaptive Card
# ==========================================
payload = {
    "type": "AdaptiveCard",
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.4",
    "body": [
        {
            "type": "TextBlock",
            "size": "Large",
            "weight": "Bolder",
            "text": "🧺 Laundry Advisor"
        },
        {
            "type": "TextBlock",
            "wrap": True,
            "text": location_name
        },
        {
            "type": "FactSet",
            "facts": [
                {
                    "title": "Best Day",
                    "value": best["date"]
                },
                {
                    "title": "Score",
                    "value": f"{best['score']:.1f}/100"
                },
                {
                    "title": "Rain",
                    "value": f"{best['rain_prob']}%"
                },
                {
                    "title": "Temperature",
                    "value": f"{best['temp']}°C"
                }
            ]
        },
        {
            "type": "TextBlock",
            "weight": "Bolder",
            "text": "7-Day Recommendation"
        },
        {
            "type": "TextBlock",
            "wrap": True,
            "text": forecast_text
        }
    ]
}

print(payload)

requests.post(
    WEBHOOK_URL,
    json=payload,
    timeout=30
)
