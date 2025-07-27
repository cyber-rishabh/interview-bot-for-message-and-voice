# Interview Bot for Message and Voice

An AI-powered interview bot that conducts candidate interviews over **WhatsApp messages** and **phone calls**, intelligently analyzing responses using **LLMs** and tracking interview progress in real-time.

## 🚀 Features

- 💬 WhatsApp-based interview bot using Green API
- 📞 Voice-based calling interview system using Twilio
- 🤖 LLM (Groq-hosted LLaMA 3) for analyzing candidate responses
- ⏱️ Silence timeout detection (15 seconds) to move to next question
- 📝 Stores and tracks all interview answers
- 🌐 Webhook integration for real-time updates

## 🛠️ Tech Stack

- Node.js (Express)
- Python (Groq API + OpenAI Whisper for STT)
- Twilio API (voice calls)
- Green API (WhatsApp messaging)
- Docker (for deployment)
- Ngrok (for local webhook testing)

## 📂 Folder Structure

interview-bot/
├── client/ # WhatsApp & Twilio handlers
├── server/ # LLM processing and question handling
├── webhook/ # Endpoint for incoming messages and calls
├── .env # API keys and secrets
└── README.md


## ⚙️ Setup Instructions

1. **Clone the repo:**
   ```bash
   git clone https://github.com/cyber-rishabh/interview-bot-for-message-and-voice.git
   cd interview-bot-for-message-and-voice

    Configure .env:

GREEN_API_ID=your_greenapi_id
GREEN_API_TOKEN=your_token
GROQ_API_KEY=your_groq_api_key
TWILIO_SID=your_twilio_sid
TWILIO_TOKEN=your_twilio_token
TWILIO_PHONE=your_twilio_phone_number
WEBHOOK_URL=https://your-ngrok-url/webhook

Install dependencies:

npm install

Start the bot:

    npm run dev

📞 How It Works

    Bot sends the first question via WhatsApp or call.

    Listens to response (text or voice), uses LLM to analyze.

    If 15 seconds of silence, auto-moves to next question.

    Stores responses for review.

🤝 Contribution

Feel free to fork and contribute. PRs are welcome!
📜 License

MIT License
