import os
import re
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ضع القيم لاحقاً في Render Environment Variables
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "my_verify_token")

WHATSAPP_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")


@app.route("/")
def home():
    return "WhatsApp Bot Server Running"


# فحص اتصال Meta Webhook
@app.route("/webhook", methods=["GET"])
def verify_webhook():

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


# استقبال رسائل واتساب
@app.route("/webhook", methods=["POST"])
def receive_message():

    data = request.get_json()

    print("Incoming:")
    print(data)

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]

        sender = message["from"]

        text = message.get("text", {}).get("body", "")

        reply = (
            "تم استقبال طلبك ✅\n\n"
            "النص الذي أرسلته:\n"
            f"{text}"
        )

        send_message(sender, reply)

    except Exception as e:
        print("Error:", e)

    return jsonify({"status": "ok"})


def send_message(number, text):

    if not WHATSAPP_TOKEN:
        print("No token yet")
        return

    url = (
        f"https://graph.facebook.com/v23.0/"
        f"{PHONE_NUMBER_ID}/messages"
    )

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": number,
        "type": "text",
        "text": {
            "body": text
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    print(response.text)


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000
    )
