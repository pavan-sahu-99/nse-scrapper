import requests

BOT_TOKEN = "8276185483:AAF3vOFCd6rB_R8Jh8UX2Vhbbustp0WSTV4"
CHAT_ID = "889852654"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    response = requests.post(url, data=payload)
    return response.json()

if __name__ == "__main__":
    send_telegram_message("Test- Bullish Stocks Alert")
