import os
import requests
import pandas as pd

# ---------------------------------
# Location
# ---------------------------------
LATITUDE = 14.3532
LONGITUDE = 100.5689

TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")

# ---------------------------------
# Get location name
# ---------------------------------
geo_url = (
    f"https://nominatim.openstreetmap.org/reverse"
    f"?lat={LATITUDE}"
    f"&lon={LONGITUDE}"
    f"&format=jsonv2"
)

geo = requests.get(
    geo_url,
    headers={"User-Agent": "LaundryAdvisor"}
).json()

location_name = geo.get(
    "display_name",
    "Unknown Location"
)

# ---------------------------------
# Open Meteo Forecast
# ---------------------------------
weather_url = (
    f"https://api.open-meteo.com/v1/forecast"
    f"?latitude={LATITUDE}"
    f"&longitude={LONGITUDE}"
    f"&daily=precipitation_probability_max,"
    f"precipitation_sum,"
    f"temperature_2m_max"
    f"&forecast_days=8"
    f"&timezone=auto"
)

weather = requests.get(weather_url).json()

df = pd.DataFrame({
    "date": weather["daily"]["time"],
    "rain": weather["daily"]["precipitation_probability_max"],
    "rain_mm": weather["daily"]["precipitation_sum"],
    "temp": weather["daily"]["temperature_2m_max"]
})

# ---------------------------------
# Score
# ---------------------------------
df["score"] = (
    (100 - df["rain"]) * 0.8 +
    (100 - df["rain_mm"] * 5).clip(lower=0) * 0.2
)

best_day = df.loc[df["score"].idxmax()]

# ---------------------------------
# Build message
# ---------------------------------
message = f"""
🧺 Laundry Advisor

📍 {location_name}

🏆 Recommended Day
{best_day['date']}

Score: {best_day['score'\]:.1f}/100

🌧 Rain Chance: {best_day['rain']}%
🌦 Rainfall: {best_day['rain_mm']} mm
🌡 Max Temp: {best_day['temp']}°C

7-Day Forecast

"""

for _, row in df.iterrows():
    message += (
        f"\n{row['date']} "
        f"| Score {row['score'\]:.0f}"
        f" | Rain {row['rain']}%"
    )

print(message)

# ---------------------------------
# Send to Teams
# ---------------------------------
if TEAMS_WEBHOOK_URL:

    payload = {
        "text": message
    }

    requests.post(
        TEAMS_WEBHOOK_URL,
        json=payload,
        timeout=30
    )
