from flask import Flask, render_template_string, request, jsonify
import os
import random
import asyncio
from threading import Thread
from maher_zubair_baileys import Gifted_Tech, useMultiFileAuthState, makeCacheableSignalKeyStore
import pino

# Setting environment variables directly in the script
os.environ["PORT"] = "5000"  # You can change this if needed (Railway automatically handles this, but here for reference)
os.environ["FLASK_ENV"] = "production"  # Set to 'production' for Railway deployment

# Flask app initialization
app = Flask(__name__)

# Sessions dictionary to store WhatsApp sessions
sessions = {}

# 🔥 Pairing Code Generate करने का फंक्शन 🔥
async def generate_pair_code(number):
    session_id = f"session_{random.randint(1000, 9999)}"
    sessions[number] = session_id
    state, saveCreds = await useMultiFileAuthState(f'./temp/{session_id}')

    bot = Gifted_Tech({
        "auth": {
            "creds": state.creds,
            "keys": makeCacheableSignalKeyStore(state.keys, pino.Logger(level="fatal"))
        },
        "printQRInTerminal": False,
        "logger": pino.Logger(level="fatal"),
        "browser": ["Chrome (Linux)", "", ""]
    })

    await asyncio.sleep(2)
    code = await bot.requestPairingCode(number)
    return code

# 🔥 WhatsApp Connection का Route 🔥
@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>WhatsApp Bot</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; background: black; color: white; }
            .container { margin-top: 50px; }
            input, button { padding: 10px; margin: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Pair Your WhatsApp</h2>
            <input type="text" id="number" placeholder="Enter your WhatsApp Number">
            <button onclick="getCode()">Get Pairing Code</button>
            <p id="pair_code"></p>

            <h2>Send Message</h2>
            <input type="text" id="target" placeholder="Enter Target Number / Group ID">
            <input type="text" id="message" placeholder="Enter Message">
            <select id="is_group">
                <option value="false">Send to Number</option>
                <option value="true">Send to Group</option>
            </select>
            <button onclick="sendMessage()">Send</button>
            <p id="status"></p>
        </div>

        <script>
            async function getCode() {
                let num = document.getElementById("number").value;
                if (!num) {
                    document.getElementById("pair_code").innerText = "Enter a valid number";
                    return;
                }
                document.getElementById("pair_code").innerText = "Generating Pairing Code...";
                let res = await fetch(`/code?number=${num}`);
                let data = await res.json();
                document.getElementById("pair_code").innerText = "Pair Code: " + (data.code || "Error");
            }

            async function sendMessage() {
                let number = document.getElementById("number").value;
                let target = document.getElementById("target").value;
                let message = document.getElementById("message").value;
                let isGroup = document.getElementById("is_group").value === "true";

                if (!number || !target || !message) {
                    document.getElementById("status").innerText = "Please fill all fields";
                    return;
                }

                document.getElementById("status").innerText = "Sending...";
                let res = await fetch("/send", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ number, target, message, is_group: isGroup })
                });
                let data = await res.json();
                document.getElementById("status").innerText = data.status || "Error";
            }
        </script>
    </body>
    </html>
    """)

@app.route('/code', methods=['GET'])
def get_code():
    number = request.args.get("number")
    if not number:
        return jsonify({"error": "Enter a valid number"}), 400
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    code = loop.run_until_complete(generate_pair_code(number))
    return jsonify({"code": code})

# 🔥 मैसेज भेजने का फंक्शन 🔥
async def send_message(session_id, target, message, is_group):
    state, saveCreds = await useMultiFileAuthState(f'./temp/{session_id}')
    
    bot = Gifted_Tech({
        "auth": {
            "creds": state.creds,
            "keys": makeCacheableSignalKeyStore(state.keys, pino.Logger(level="fatal"))
        },
        "logger": pino.Logger(level="fatal"),
        "browser": ["Chrome (Linux)", "", ""]
    })

    await asyncio.sleep(2)

    if is_group:
        await bot.sendMessage(target, {"text": message})
    else:
        await bot.sendMessage(f"{target}@s.whatsapp.net", {"text": message})

@app.route('/send', methods=['POST'])
def send():
    data = request.json
    number = data.get("number")
    target = data.get("target")
    message = data.get("message")
    is_group = data.get("is_group", False)

    if not number or not target or not message:
        return jsonify({"error": "Invalid input"}), 400

    session_id = sessions.get(number)
    if not session_id:
        return jsonify({"error": "Session not found"}), 400

    thread = Thread(target=lambda: asyncio.run(send_message(session_id, target, message, is_group)))
    thread.start()

    return jsonify({"status": "Message Sent!"})

# Load environment variables from Railway or .env file (in this case added directly)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Railway will provide the port dynamically
    app.run(host="0.0.0.0", port=port, debug=True)
