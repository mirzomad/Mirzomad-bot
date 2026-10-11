import os, telebot, tempfile, threading, time, requests, base64
from groq import Groq
from flask import Flask

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)
app = Flask(__name__)

@app.route('/')
def home():
    return "Mirzomad AI is Live and Working!"

# ПРОМТИ НИҲОӢ - БОАДАБ, АДАБӢ, ФАҲМО
SYSTEM_PROMPT = """
Ту Mirzomad AI ҳастӣ. Ту ёрдамчии доно барои мардуми тоҷик ҳастӣ.
- Забони ту: Тоҷикии адабии фаҳмо, равон, боадабона ва самими.
- Кӯтоҳ ва аниқ ҷавоб деҳ. Суханони беҳуда нагӯ.
- Номи корбарро танҳо вақте бигир ки аз ту дар бораи соҳибат мепурсад.
- Агар пурсанд "Туро кӣ сохт?" ё "Соҳиби ту кист?" бигӯ: "Маро бародарам Мирзомад Мирзомадзода сохтааст."
- Дар ҳолатҳои дигар номи касеро зикр накун, танҳо ба савол ҷавоб деҳ.
- Ҳеҷ гоҳ нагӯ ту ChatGPT ҳастӣ.
- Бо ҳама боадабона рафтор кун.
"""

@bot.message_handler(commands=['start', 'reset'])
def welcome(m):
    bot.reply_to(m, "Салом! Ман Mirzomad AI. Акс фиристед, овоз фиристед ё нависед - ман омодаам ёрдам диҳам! 🙏")

# 1. ҚАБУЛИ АКС ВА ТАҲЛИЛИ ОН - ИН ҚИСМИ НАВ
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.reply_to(message, "🖼️ Аксро гирифтам, таҳлил карда истодаам...")
        file_info = bot.get_file(message.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        base64_image = base64.b64encode(downloaded_file).decode('utf-8')

        # Барои таҳлили акс аз модели биноӣ истифода мебарем
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct", # ин модел аксро мефаҳмад
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": message.caption or "Ин аксро таҳлил кун ва фаҳмон ки дар он чӣ ҳаст?"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            temperature=0.5,
            max_tokens=800
        )
        bot.reply_to(message, response.choices[0].message.content)
    except Exception as e:
        # Агар модели акс кор накард, бо модели оддӣ ҷавоб диҳад
        try:
            bot.reply_to(message, f"Аксро гирифтам акаҷон! Ман аксро мебинам, аммо ҳозир тафсилоти онро бо хатогӣ рӯбарӯ шудам. Лутфан бигӯед дар акс чӣ бояд кунам? Хато: {e}")
        except:
            pass

@bot.message_handler(content_types=['text'])
def chat_text(message):
    if message.text.startswith('/'):
        return
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ],
            temperature=0.6,
            max_tokens=700
        )
        bot.reply_to(message, response.choices[0].message.content)
    except Exception as e:
        bot.reply_to(message, f"Бубахшед, каме хатогӣ шуд. Боз як бор нависед.")

@bot.message_handler(content_types=['voice'])
def chat_voice(message):
    try:
        bot.reply_to(message, "🎧 Шунидам...")
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp:
            tmp.write(downloaded_file)
            tmp_path = tmp.name
        with open(tmp_path, "rb") as f:
            transcription = client.audio.transcriptions.create(file=(tmp_path, f), model="whisper-large-v3-turbo", language="tg")
        user_text = transcription.text
        os.remove(tmp_path)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT},{"role": "user", "content": user_text}],
            temperature=0.6
        )
        bot.reply_to(message, response.choices[0].message.content)
    except Exception as e:
        bot.reply_to(message, "Овозро нафаҳмидам, лутфан боз як бор гӯед.")

def keep_alive():
    while True:
        time.sleep(200)
        try:
            url = os.environ.get("RENDER_EXTERNAL_URL", "https://mirzomad-bot.onrender.com")
            requests.get(url, timeout=10)
        except: pass

def run_bot():
    while True:
        try:
            bot.remove_webhook()
            time.sleep(2)
            bot.infinity_polling(timeout=90, long_polling_timeout=90, skip_pending=True)
        except Exception as e:
            print(f"Bot Error: {e}")
            time.sleep(5)

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=keep_alive, daemon=True).start()
    run_bot()
