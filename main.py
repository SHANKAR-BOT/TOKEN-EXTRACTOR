import os
import telebot
import requests
import threading
import time
from flask import Flask
from threading import Thread

# Yaha direct token daalo
TOKEN = "7785881475:AAEJc1n7WSOIi6gLzY3J6zKne_xvqqXDBkg"  # <-- Yaha apna Telegram bot token daal do
bot = telebot.TeleBot(TOKEN)

FB_TOKEN = None
loop_running = False

@bot.message_handler(commands=['settoken'])
def set_token(message):
    global FB_TOKEN
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Usage: /settoken <Facebook_Token>")
        return
    FB_TOKEN = parts[1]
    bot.reply_to(message, "Facebook Token set successfully!")

@bot.message_handler(commands=['sendmsg'])
def send_message(message):
    global FB_TOKEN
    if not FB_TOKEN:
        bot.reply_to(message, "Please set a Facebook token first using /settoken")
        return
    
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.reply_to(message, "Usage: /sendmsg <UID> <Message>")
        return
    
    uid, text = parts[1], parts[2]
    
    url = f"https://graph.facebook.com/v17.0/{uid}/messages"
    payload = {"recipient": {"id": uid}, "message": {"text": text}, "messaging_type": "RESPONSE"}
    headers = {"Authorization": f"Bearer {FB_TOKEN}", "Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        bot.reply_to(message, f"✅ Message Sent!\nConvo ID: {uid}\nMessage: {text}")
    else:
        bot.reply_to(message, "❌ Message Sending Failed!")

@bot.message_handler(commands=['startloop'])
def start_loop(message):
    global loop_running, FB_TOKEN
    if not FB_TOKEN:
        bot.reply_to(message, "Please set a Facebook token first using /settoken")
        return
    
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.reply_to(message, "Usage: /startloop <UID> <Message>")
        return
    
    uid, text = parts[1], parts[2]
    loop_running = True
    bot.reply_to(message, "⏳ Infinite loop started for sending messages...")
    
    def loop_send():
        global loop_running
        while loop_running:
            url = f"https://graph.facebook.com/v17.0/{uid}/messages"
            payload = {"recipient": {"id": uid}, "message": {"text": text}, "messaging_type": "RESPONSE"}
            headers = {"Authorization": f"Bearer {FB_TOKEN}", "Content-Type": "application/json"}
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                bot.send_message(message.chat.id, f"✅ Message Sent!\nConvo ID: {uid}\nMessage: {text}")
            else:
                bot.send_message(message.chat.id, "❌ Message Sending Failed!")
            
            time.sleep(60)  # 1-minute delay to avoid spam detection
    
    threading.Thread(target=loop_send).start()

@bot.message_handler(commands=['stoploop'])
def stop_loop(message):
    global loop_running
    loop_running = False
    bot.reply_to(message, "⏹️ Loop stopped successfully!")

# Flask web server to keep the bot alive
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)), debug=False)).start()
    bot.polling(none_stop=True)
