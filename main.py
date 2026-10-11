import os
import telebot
from groq import Groq
from flask import Flask
import threading

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
    bot.reply_to(message, "Салом ака! Савол диҳед!")

@bot.message_handler(func=lambda m: True)
def chat(message):
    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Ту ёрдамчии тоҷикӣ ҳастӣ."},
                {"role": "user", "content": message.text}
            ]
        )
        bot.reply_to(message, resp.choices[0].message.content)
    except Exception as e:
        bot.reply_to(message, f"Хато: {e}")

def run_bot():
    bot.infinity_polling()

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
