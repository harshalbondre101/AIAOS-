import requests
# Telegram bot configuration
BOT_TOKEN = "7346635088:AAENB-uxueycqzKMin8ZI2QjT0LkbFqxAgo"
CHAT_ID = "-1002152343881"  # Replace with the chat ID you obtained

# Function to send Telegram message
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    response = requests.post(url, json=payload)
    return response.json()

