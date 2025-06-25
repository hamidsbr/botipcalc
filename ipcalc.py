from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, MessageHandler, Filters
from netaddr import IPNetwork, AddrFormatError
import requests
import os

# === Konfigurasi Token dan Grup ===
TOKEN = os.getenv('BOT_TOKEN', 'ISI_TOKEN_DI_SINI')
GROUP_ID = os.getenv('GROUP_ID', '-1002081701359')

# === Inisialisasi Bot ===
bot = Bot(token=TOKEN)

try:
    bot.send_message(chat_id=GROUP_ID, text="✅ Bot aktif dan siap menerima subnet!")
except Exception as e:
    print("❌ Gagal kirim pesan ke grup:", e)

# === Inisialisasi Flask dan Dispatcher ===
app = Flask(__name__)
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

# === Fungsi Balasan Pesan ===
def subnet_reply(update, context):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    print("📨 Pesan masuk:", text)

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
    except AddrFormatError:
        reply = "⚠️ Format salah. Contoh: 192.168.1.0/27"
    except Exception as e:
        reply = f"❌ Error: {e}"

    update.message.reply_text(reply)

# === Tambahkan Handler ===
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, subnet_reply))

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
    return "🚀 Bot is running!"

# === Fungsi Set Webhook Otomatis ===
def set_webhook():
    slug = os.getenv("REPL_SLUG")
    owner = os.getenv("REPL_OWNER")

    if slug and owner:
        domain = f"{slug}.{owner}.repl.co"
        webhook_url = f"https://{domain}/{TOKEN}"
        try:
            res = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}")
            if res.status_code == 200:
                print(f"✅ Webhook otomatis diset ke: {webhook_url}")
            else:
                print(f"❌ Gagal set webhook: {res.status_code} - {res.text}")
        except Exception as e:
            print("❌ Error saat set webhook:", e)
    else:
        print("⚠️ Tidak berjalan di Replit atau env tidak lengkap.")

# === Jalankan Server Flask ===
if __name__ == '__main__':
    set_webhook()
    app.run(host='0.0.0.0', port=8080)
