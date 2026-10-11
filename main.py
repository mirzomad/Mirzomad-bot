import os, telebot, threading, time, requests
from groq import Groq
from flask import Flask

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)
app = Flask(__name__)

@app.route('/')
def home():
    return "Mirzomad AI Live!"

SYSTEM_PROMPT = "Ту Mirzomad AI, сохтаи Мирзомад Мирзомадзода. Бо тоҷикии фаҳмо ва боадабона ҷавоб деҳ."

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "Салом акаҷон! 🙏 Ман кор мекунам!")

@bot.message_handler(content_types=['text'])
def chat(m):
    try:
        if m.text.startswith('/'): return
        # МОДЕЛИ НАВИ ДУРУСТ
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role":"system","content":SYSTEM_PROMPT},
                {"role":"user","content":m.text}
            ],
            temperature=0.6,
            max_tokens=600
        )
        bot.reply_to(m, r.choices[0].message.content)
    except Exception as e:
        bot.reply_to(m, f"Хато: {e}")

@bot.message_handler(content_types=['photo'])
def photo(m):
    bot.reply_to(m, "Акаҷон аксро гирифтам! Ҳозир матн кор мекунад, баъди он аксро ҳам дуруст мекунем!")

# Барои 409 Conflict - танҳо як бор polling
def run_bot():
    bot.remove_webhook()
    time.sleep(3)
    bot.infinity_polling(skip_pending=True, timeout=90, long_polling_timeout=60)

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
    
