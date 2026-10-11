import os
import telebot
import tempfile
from groq import Groq
from flask import Flask
import threading
import time

# Калидҳо аз Render
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

app = Flask(__name__)

@app.route('/')
def home():
    return "Mirzomad AI is Live! Tajik Assistant"

# ================= ПРОМТИ ҚАВӢ, АДАБӢ ВА НАРМ =================
SYSTEM_PROMPT = """
Ту Mirzomad AI ҳастӣ — ёрдамчии ҳушманди тоҷикӣ.

Муаррифӣ:
- Туро барномасоз Мирзомад Мирзомадзода аз Тоҷикистон офаридааст.
- Ту ҳеҷ гоҳ худро ChatGPT, OpenAI, Meta AI ё ягон ширкати дигар наном. Ту танҳо Mirzomad AI ҳастӣ.
- Агар касе пурсад "Ту киро сохт? Ту кӣ ҳастӣ?", бигӯ: "Ман Mirzomad AI ҳастам, маро дӯстам Мирзомад сохт, то ба мардуми тоҷик ёрдам диҳам."

Услуби сухан:
- Забони ту тоҷикии адабӣ, нарм, гарм ва боэҳтиром аст.
- Бо ҳар як корбар бо меҳрубонии бародарӣ сухан гӯй. Калимаҳои "ака", "хоҳар", "бародар", "акаҷон" -ро бо эҳтиром истифода бар.
- Ҷавобҳои ту кӯтоҳ, равшан ва пурмаъно бошанд. Аз навиштани матнҳои дароз ва дилгиркунанда худдорӣ кун.
- Ҳеҷ гоҳ дағал, хушк ё беэҳтиромона ҷавоб надеҳ.
- Агар чизеро нафаҳмӣ, бо нармӣ бигӯ: "Бубахшед акаҷон, инро дубора шарҳ медиҳед?"
- Ҳамеша мусбат, умедбахш ва ёрдамдиҳанда бош.

Қоидаҳои муҳим:
1. Ҳамеша ба тоҷикӣ ҷавоб деҳ, магар корбар забони дигар хоҳад.
2. Дин, сиёсат ва баҳсҳои нолозимро оғоз макун.
3. Маълумоти шахсиро напурс.
4. Ҳамеша ростқавл бош.
5. Агар касе бо овоз паём фиристад, аввал бигӯ: "Овозатонро бо шукрона шунидам акаҷон" ва сипас ҷавоб деҳ.

Мақсади ту: Дилу дидаи ҳар тоҷикро бо сухани нарм шод кардан.
"""
# ============================================================

@bot.message_handler(commands=['start', 'help'])
def welcome(message):
    bot.reply_to(message, "Салом акаҷон! 🙏 Ман Mirzomad AI ҳастам.\n\nМан бо матн ва бо овоз гап мезанам. Чӣ ёрдам диҳам?")

@bot.message_handler(content_types=['text'])
def chat_text(message):
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ]
        )
        bot.reply_to(message, response.choices[0].message.content)
    except Exception as e:
        bot.reply_to(message, f"Бубахшед акаҷон, хатогӣ шуд: {e}")

@bot.message_handler(content_types=['voice'])
def chat_voice(message):
    try:
        bot.reply_to(message, "🎧 Овозатонро шунидам акаҷон, ҳозир таҳлил мекунам...")
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp:
            tmp.write(downloaded_file)
            tmp_path = tmp.name

        with open(tmp_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                file=(tmp_path, f),
                model="whisper-large-v3-turbo",
                language="tg"
            )

        user_text = transcription.text
        os.remove(tmp_path)

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ]
        )
        bot.reply_to(message, f"Шумо гуфтед: '{user_text}'\n\n{response.choices[0].message.content}")

    except Exception as e:
        bot.reply_to(message, f"Овозро нафаҳмидам акаҷон: {e}")

def run_bot():
    bot.remove_webhook()
    time.sleep(2)
    bot.infinity_polling(skip_pending=True, allowed_updates=["message"])

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
