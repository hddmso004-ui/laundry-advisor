import requests
import os

webhook_url = os.environ["TEAMS_WEBHOOK_URL"]

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
            "text": """
📍 พระนครศรีอยุธยา

✅ วันนี้เหมาะกับการซักผ้า

🌧 โอกาสฝน 15%
☀️ แดด 8 ชั่วโมง
💧 ความชื้น 58%

🏆 วันที่ดีที่สุด:
14 ต.ค. 2026
คะแนน 91/100
"""
        }
    ]
}

requests.post(webhook_url, json=payload)
