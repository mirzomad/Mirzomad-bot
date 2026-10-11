import os
import telebot
from groq import Groq
from flask import Flask
import threading
import time

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Live!"

@bot.message_handler(commands=['start', 'help'])
def welcome(message):
    bot.reply_to(message, "Салом ака! Ман Mirzomad AI!")

@bot.message_handler(func=lambda m: True)
def chat(message):
    try:
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Ту ёрдамчии тоҷикӣ ҳастӣ."},
                {"role": "user", "content": message.text}
            ]
        )
        bot.reply_to(message, r.choices[0].message.content)
    except Exception as e:
        bot.reply_to(message, f"Хато: {e}")

def run_bot():
    bot.remove_webhook()
    time.sleep(2)
    bot.infinity_polling(skip_pending=True)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    run_bot()
