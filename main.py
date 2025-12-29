import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from groq import Groq

# ====== НАСТРОЙКИ ======
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Память диалогов
user_memory = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Как можно помочь вам сегодня?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    history = user_memory.get(user_id, [])
    history.append({"role": "user", "content": text})

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=history,
            temperature=0.7,
            max_tokens=1024,
        )

        answer = response.choices[0].message.content
        history.append({"role": "assistant", "content": answer})
        user_memory[user_id] = history[-10:]  # храним последние 10 сообщений

        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text(f"Ошибка 🤕\n{e}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
