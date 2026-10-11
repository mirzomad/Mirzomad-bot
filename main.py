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
    return "Mirzomad AI is Live!"

SYSTEM_PROMPT = """
Ту Mirzomad AI ҳастӣ. Туро Мирзомад Мирзомадзода сохтааст.
Забонат: тоҷикии адабии фаҳмо, боадабона, кӯтоҳ ва аниқ.
Номро танҳо вақте бигӯ ки пурсанд "Туро кӣ сохт?". Дар дигар ҳолат номи касеро нагӯ.
Ҳеҷ гоҳ нагӯ ту ChatGPT ҳастӣ.
"""

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "Салом акаҷон! 🙏 Ман омодаам. Акс, овоз ё матн фиристед!")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        file_info = bot.get_file(message.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        base64_image = base64.b64encode(downloaded_file).decode('utf-8')

        # Модели дурусти Groq барои акс
        response = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": "Ин аксро бо тоҷикии адабии фаҳмо таҳлил кун. Дар акс чӣ ҳаст?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}
            ],
            max_tokens=700
        )
        bot.reply_to(message, response.choices[0].message.content)
    except Exception as e:
        print(f"Photo Error: {e}")
        bot.reply_to(message, f"Аксро гирифтам акаҷон! Таҳлил кардам, аммо хатои техникӣ шуд: {e}. Лутфан боз як акси дигар фиристед.")

@bot.message_handler(content_types=['text'])
def chat_text(message):
    try:
        if message.text.startswith('/'): return
        bot.send_chat_action(message.chat.id, 'typing')
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ],
            temperature=0.6, max_tokens=600
        )
        bot.reply_to(message, response.choices[0].message.content)
    except Exception as e:
        print(f"Text Error: {e}")
        bot.reply_to(message, "Бубахшед акаҷон, Groq каме банд аст. 5 сония баъд боз нависед.")

@bot.message_handler(content_types=['voice'])
def chat_voice(message):
    try:
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp:
            tmp.write(downloaded_file)
            tmp_path = tmp.name
        with open(tmp_path, "rb") as f:
            transcription = client.audio.transcriptions.create(file=(tmp_path, f), model="whisper-large-v3-turbo", language="tg")
        os.remove(tmp_path)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": transcription.text}],
        )
        bot.reply_to(message, response.choices[0].message.content)
    except Exception as e:
        print(f"Voice Error: {e}")
        bot.reply_to(message, "Овозро нафаҳмидам.")

# Барои хомӯш нашудан
def keep_alive():
    while True:
        time.sleep(200)
        try:
            url = os.environ.get("RENDER_EXTERNAL_URL")
            if url: requests.get(url)
        except: pass

def run_bot():
    while True:
        try:
            bot.remove_webhook()
            time.sleep(2)
            bot.infinity_polling(timeout=90, long_polling_timeout=90)
        except: time.sleep(5)

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=keep_alive, daemon=True).start()
    run_bot()
