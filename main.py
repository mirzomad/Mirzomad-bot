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

SYSTEM_PROMPT = "Ту Mirzomad AI, сохтаи Мирзомад. Бо тоҷикии фаҳмо, адабӣ, кӯтоҳ ва боадабона ҷавоб деҳ."

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "Салом акаҷон! 🙏 Омодаам!")

@bot.message_handler(content_types=['text'])
def chat(m):
    try:
        if m.text.startswith('/'): return
        # Модели аз ҳама устувор
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant", # Ин модел ҳеҷ гоҳ банд намешавад!
            messages=[
                {"role":"system","content":SYSTEM_PROMPT},
                {"role":"user","content":m.text}
            ]
        )
        bot.reply_to(m, r.choices[0].message.content)
    except Exception as e:
        # Ҳамин ҷо хатои аслиро мебинем!
        bot.reply_to(m, f"Хатои Groq: {str(e)[:300]}")

@bot.message_handler(content_types=['photo'])
def photo(m):
    bot.reply_to(m, "Акаҷон, аксро гирифтам! 🙏 Ҳозир калиди Groq нав карда истодаед, баъди он аксро ҳам таҳлил мекунам. Лутфан ҳозир бо матн нависед!")

def keep_alive():
    while True:
        time.sleep(300)
        try: requests.get(os.environ.get("RENDER_EXTERNAL_URL",""))
        except: pass

def run_bot():
    while True:
        try:
            bot.remove_webhook()
            bot.infinity_polling(timeout=90)
        except: time.sleep(5)

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=keep_alive, daemon=True).start()
    run_bot()
