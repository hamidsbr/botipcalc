from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, MessageHandler, Filters
from netaddr import IPNetwork
import os

# === Konfigurasi Token dan Grup ===
TOKEN = '7648919226:AAHhat3D1JWA5dbhTiF_Md0tHeC9PgUVQaM'
GROUP_ID = '-1002081701359'  # Ganti dengan ID grup kamu

# === Inisialisasi Bot ===
bot = Bot(token=TOKEN)

# Kirim pesan ke grup saat bot aktif
try:
    bot.send_message(chat_id=GROUP_ID,
                     text="✅ Bot aktif dan siap menerima subnet!")
except Exception as e:
    print("❌ Gagal kirim pesan ke grup:", e)

# === Inisialisasi Flask dan Dispatcher ===
app = Flask(__name__)
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)


# === Fungsi Balasan Pesan ===
def subnet_reply(update, context):
    if not update.message or not update.message.text:
        return  # Lewatkan jika bukan pesan teks

    text = update.message.text.strip()
    try:
        net = IPNetwork(text)
        reply = (f"📡 Subnet Info:\n"
                 f"Network: {net.network}\n"
                 f"Broadcast: {net.broadcast}\n"
                 f"Usable: {net[1]} – {net[-2]}\n"
                 f"Total IP: {net.size}\n"
                 f"Usable Host: {net.size - 2 if net.size > 2 else 0}")
    except:
        reply = "⚠️ Format salah. Kirim dalam format: 192.168.1.70/27"
    update.message.reply_text(reply)


# === Tambahkan Handler ===
dispatcher.add_handler(
    MessageHandler(Filters.text & ~Filters.command, subnet_reply))


# === Endpoint Webhook Telegram ===
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    print("📥 Menerima webhook dari Telegram...")
    try:
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
    except Exception as e:
        print("❌ Error saat memproses update:", e)
    return "ok"


# === Endpoint Home ===
@app.route('/')
def home():
    return "Bot is running!"


# === Jalankan Server Flask ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
