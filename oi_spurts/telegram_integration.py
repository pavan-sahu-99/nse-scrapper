import requests

BOT_TOKEN = "Your Bot Token"
CHAT_ID = "Your ID"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    response = requests.post(url, data=payload)
    return response.json()

if __name__ == "__main__":
    send_telegram_message("Test- Bullish Stocks Alert")

