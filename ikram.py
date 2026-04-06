import os
import json
import random
import time
import requests
from flask import Flask, request

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# صورة البوت
WELCOME_PHOTO = "https://i.postimg.cc/Y99hJmjX/file-00000000ef0871f7a407fbe643baee0d.png"

# معلومات المطور
DEVELOPER_NAME = "ikram Dev"
DEV_FACEBOOK = "https://www.facebook.com/profile.php?id=61575429936062"
DEV_TELEGRAM = "https://t.me/@milouddev02"
DEV_WEBSITE = "https://guns.lol/miloud"

app = Flask(__name__)

DATA_FILE = "user_data.json"

try:
    with open(DATA_FILE) as f:
        user_data = json.load(f)
except:
    user_data = {}

LAST_ACTION = {}


# حفظ البيانات
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(user_data, f)


# إرسال رسالة
def send_text(user_id, text):

    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

    data = {
        "recipient": {"id": user_id},
        "message": {"text": text}
    }

    requests.post(url, json=data)


# بطاقة البريد مع زر النسخ
def send_email_card(user_id, email):

    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

    data = {
        "recipient": {"id": user_id},
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": f"📧 بريدك المؤقت:\n\n{email}\n\nاضغط لنسخه",
                    "buttons": [
                        {
                            "type": "web_url",
                            "title": "📋 نسخ البريد",
                            "url": f"https://api.whatsapp.com/send?text={email}"
                        }
                    ]
                }
            }
        }
    }

    requests.post(url, json=data)


# القائمة الرئيسية Carousel
def send_menu(user_id):

    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

    data = {
        "recipient": {"id": user_id},
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [

                        {
                            "title": "👑 TempMail Pro",
                            "image_url": WELCOME_PHOTO,
                            "subtitle": "إنشاء بريد مؤقت بسرعة",
                            "buttons": [
                                {
                                    "type": "postback",
                                    "title": "📧 إنشاء بريد",
                                    "payload": "CREATE_EMAIL"
                                },
                                {
                                    "type": "postback",
                                    "title": "📥 البريد الوارد",
                                    "payload": "INBOX"
                                }
                            ]
                        },

                        {
                            "title": "📬 إدارة البريد",
                            "image_url": WELCOME_PHOTO,
                            "subtitle": "تحديث الرسائل أو حذف البريد",
                            "buttons": [
                                {
                                    "type": "postback",
                                    "title": "🔄 تحديث البريد",
                                    "payload": "REFRESH"
                                },
                                {
                                    "type": "postback",
                                    "title": "🗑 حذف البريد",
                                    "payload": "DELETE"
                                }
                            ]
                        },

                        {
                            "title": "⚙️ معلومات",
                            "image_url": WELCOME_PHOTO,
                            "subtitle": "تعرف على البوت والمطور",
                            "buttons": [
                                {
                                    "type": "postback",
                                    "title": "ℹ️ معلومات البوت",
                                    "payload": "ABOUT"
                                },
                                {
                                    "type": "postback",
                                    "title": "👨‍💻 المطور",
                                    "payload": "DEV"
                                }
                            ]
                        }

                    ]
                }
            }
        }
    }

    requests.post(url, json=data)


# إنشاء بريد
def create_email(user_id):

    if time.time() - LAST_ACTION.get(user_id, 0) < 10:
        send_text(user_id, "⏳ انتظر قليلاً قبل إنشاء بريد جديد")
        return

    LAST_ACTION[user_id] = time.time()

    name = f"user{random.randint(1000,9999)}"

    try:

        r = requests.post(
            "https://api.internal.temp-mail.io/api/v3/email/new",
            data={"name": name, "domain": "greencafe24.com"}
        )

        email = r.json()["email"]

        user_data[user_id] = email
        save_data()

        send_email_card(user_id, email)

    except:

        send_text(user_id, "❌ فشل إنشاء البريد")


# inbox
def inbox(user_id):

    email = user_data.get(user_id)

    if not email:
        send_text(user_id, "❌ ليس لديك بريد")
        return

    try:

        url = f"https://api.internal.temp-mail.io/api/v3/email/{email}/messages"

        messages = requests.get(url).json()

        if not messages:
            send_text(user_id, "📭 لا توجد رسائل")
            return

        for msg in messages[:3]:

            send_text(
                user_id,
                f"""
📨 رسالة جديدة

📌 الموضوع:
{msg['subject']}

📝 الرسالة:
{msg['body_text'][:500]}
"""
            )

    except:

        send_text(user_id, "❌ فشل جلب الرسائل")


# حذف البريد
def delete_email(user_id):

    if user_id in user_data:

        del user_data[user_id]
        save_data()

        send_text(user_id, "✅ تم حذف البريد")

    else:

        send_text(user_id, "❌ لا يوجد بريد")


# معلومات المطور
def developer(user_id):

    send_text(
        user_id,
        f"""
👨‍💻 Developer

{DEVELOPER_NAME}

Facebook
{DEV_FACEBOOK}

Telegram
{DEV_TELEGRAM}

Website
{DEV_WEBSITE}
"""
    )


# معلومات البوت
def about(user_id):

    send_text(
        user_id,
        """
👑 TempMail Pro

بوت لإنشاء بريد مؤقت
لاستقبال أكواد التفعيل

⚡ سريع
🔒 آمن
📩 يستقبل الرسائل فوراً
"""
    )


# معالجة الأزرار
def handle_postback(sender, payload):

    if payload == "CREATE_EMAIL":
        create_email(sender)

    elif payload == "INBOX":
        inbox(sender)

    elif payload == "REFRESH":
        inbox(sender)

    elif payload == "DELETE":
        delete_email(sender)

    elif payload == "DEV":
        developer(sender)

    elif payload == "ABOUT":
        about(sender)


# webhook التحقق
@app.route("/webhook", methods=["GET"])
def verify():

    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if token == VERIFY_TOKEN:
        return challenge

    return "error"


# استقبال الرسائل
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    for entry in data.get("entry", []):

        for messaging in entry.get("messaging", []):

            sender = messaging["sender"]["id"]

            if "postback" in messaging:

                payload = messaging["postback"]["payload"]
                handle_postback(sender, payload)

            elif "message" in messaging:

                send_menu(sender)

    return "ok"


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
