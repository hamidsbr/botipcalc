from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, MessageHandler, Filters
from netaddr import IPNetwork
import os

TOKEN = '7648919226:AAHhat3D1JWA5dbhTiF_Md0tHeC9PgUVQaM'
bot = Bot(token=TOKEN)

app = Flask(__name__)

dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

def subnet_reply(update, context):
    text = update.message.text.strip()
    try:
        net = IPNetwork(text)
        reply = (
            f"📡 Subnet Info:\n"
            f"Network: {net.network}\n"
            f"Broadcast: {net.broadcast}\n"
            f"Usable: {net[1]} – {net[-2]}\n"
            f"Total IP: {net.size}\n"
            f"Usable Host: {net.size - 2 if net.size > 2 else 0}"
        )
    except:
        reply = "⚠️ Format salah. Kirim dalam format: 192.168.1.70/27"
    update.message.reply_text(reply)

dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, subnet_reply))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route('/')
def home():
    return "Bot is running!"

if __name__ == '__main__':
    # Jalankan Flask
    app.run(host='0.0.0.0', port=8080)
