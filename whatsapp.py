from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# === CONFIGURATION ===
GROQ_API_KEY = ""
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

GREEN_API_INSTANCE_ID = ""
GREEN_API_TOKEN = ""
GREEN_API_URL = f"https://7105.api.greenapi.com/waInstance{GREEN_API_INSTANCE_ID}/sendMessage/{GREEN_API_TOKEN}"

user_states = {}

# === FUNCTIONS ===
def send_message(chat_id, message):
    print(f"📤 Sending message to {chat_id}: {message}")
    payload = {
        "chatId": chat_id,
        "message": message
    }
    response = requests.post(GREEN_API_URL, json=payload)
    print("✅ GreenAPI response:", response.json())
    return jsonify(response.json())

def ask_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    res = requests.post(GROQ_URL, headers=headers, json=payload)
    try:
        reply = res.json()["choices"][0]["message"]["content"]
        print("🧠 Groq response:", reply)
        return reply.strip()
    except Exception as e:
        print("❌ Groq error:", e)
        return "Sorry, something went wrong with our AI."

# === WEBHOOK ===
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📥 Incoming data:", data)

    if "senderData" not in data or "messageData" not in data:
        return jsonify({"status": "ignored"}), 400

    chat_id = data["senderData"].get("chatId")
    message = data["messageData"].get("textMessageData", {}).get("textMessage", "").lower()

    if not chat_id or not message:
        return jsonify({"status": "invalid"}), 400

    if chat_id not in user_states:
        user_states[chat_id] = {"stage": "intro", "history": []}

    state = user_states[chat_id]

    if state["stage"] == "intro":
        if "yes" in message:
            state["stage"] = "interview"
            question = ask_groq("Ask a technical interview question for a software developer.")
            state["history"].append({"q": question})
            return send_message(chat_id, question)
        else:
            return send_message(chat_id, "Hi, are you interested in this job opportunity? Reply 'yes' to begin.")

    elif state["stage"] == "interview":
        state["history"][-1]["a"] = message
        if len(state["history"]) >= 3:
            state["stage"] = "budget"
            return send_message(chat_id, "The budget for this role is $3500/month. Does this align with your expectations?")
        else:
            question = ask_groq("Ask another interview question for a software developer.")
            state["history"].append({"q": question})
            return send_message(chat_id, question)

    elif state["stage"] == "budget":
        if any(word in message for word in ["more", "less", "negotiate", "$", "₹"]):
            state["stage"] = "negotiate"
            return send_message(chat_id, "Let us know your expected range, and we’ll see what we can do.")
        else:
            state["stage"] = "done"
            return send_message(chat_id, "Great! You're being considered for the role. We'll get back to you shortly.")

    elif state["stage"] == "negotiate":
        state["stage"] = "done"
        return send_message(chat_id, "Thanks for sharing. We'll review your expectations and respond soon.")

    return jsonify({"status": "ok"})

# === RUN FLASK ===
if __name__ == "__main__":
    app.run(port=3000)
