from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import requests
import json
from datetime import datetime

app = Flask(__name__)
GROQ_API_KEY = ''
GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'
sessions = {}
SYSTEM_PROMPT = """You are conducting a concise technical interview for a software engineering position. 
Ask only these 3 specific questions in order:
1. "Can you walk me through your experience with backend development and which technologies you're most proficient in?"
2. "How would you approach debugging a production issue that's affecting multiple users?"
3. "Can you explain a challenging technical problem you solved recently and how you approached it?"

After each answer, provide a brief 1-2 sentence acknowledgment or follow-up, then move to the next question.
After the 3rd question, thank the candidate and end the call."""


def save_transcript(call_sid, transcript):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"transcript_{call_sid}_{timestamp}.txt"
    with open(filename, 'w') as f:
        f.write(transcript)
    print(f"Transcript saved to {filename}")


def generate_groq_response(messages, max_tokens=100):
    headers = {
        'Authorization': f'Bearer {GROQ_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": "llama3-70b-8192",
        "messages": messages,
        "temperature": 0.5,  # Lower for more focused responses
        "max_tokens": max_tokens
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        print(f"Groq API error: {e}")
        return "Let's move on to the next question."


def ask_question(call_sid, question):
    resp = VoiceResponse()
    gather = Gather(
        input='speech',
        action=f'/process_answer?call_sid={call_sid}',
        method='POST',
        timeout=10,  # Increased timeout for longer answers
        speechTimeout='auto',
        language='en-US'
    )
    gather.say(question, voice='alice', language='en-US')
    resp.append(gather)
    return str(resp)


@app.route('/voice', methods=['POST'])
def voice():
    call_sid = request.values.get('CallSid')
    if not call_sid:
        resp = VoiceResponse()
        resp.say("Error in call setup. Please try again later.")
        resp.hangup()
        return Response(str(resp), mimetype='text/xml')

    # Initialize session
    sessions[call_sid] = {
        'conversation': [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": "Thank you for joining this interview. We'll discuss three key technical topics. First," +
             "can you walk me through your experience with backend development and which technologies you're most proficient in?"}
        ],
        'question_count': 0,
        'transcript': "AI: Thank you for joining this interview. We'll discuss three key technical topics.\n"
    }

    return Response(ask_question(call_sid, sessions[call_sid]['conversation'][-1]['content']),
                    mimetype='text/xml')


@app.route('/process_answer', methods=['POST'])
def process_answer():
    call_sid = request.args.get('call_sid')
    if call_sid not in sessions:
        resp = VoiceResponse()
        resp.say("Session error. Please call again.")
        resp.hangup()
        return Response(str(resp), mimetype='text/xml')

    # Get user's speech input
    speech_result = request.values.get('SpeechResult', '(No response)')
    print(f"Received answer: {speech_result}")  # Debug logging

    # Update conversation history
    sessions[call_sid]['conversation'].append({"role": "user", "content": speech_result})
    sessions[call_sid]['transcript'] += f"Candidate: {speech_result}\n"
    sessions[call_sid]['question_count'] += 1

    # Generate response based on the structured questions
    if sessions[call_sid]['question_count'] == 1:
        next_question = "Thank you. Next question: How would you approach debugging a production issue that's affecting multiple users?"
    elif sessions[call_sid]['question_count'] == 2:
        next_question = "Interesting. Final question: Can you explain a challenging technical problem you solved recently and how you approached it?"
    else:
        # End the interview after 3 questions
        resp = VoiceResponse()
        closing = "Thank you for your time and detailed answers. We'll review your responses and be in touch. Have a great day!"
        resp.say(closing)
        sessions[call_sid]['transcript'] += f"AI: {closing}\n"
        save_transcript(call_sid, sessions[call_sid]['transcript'])
        del sessions[call_sid]  # Clean up session
        resp.hangup()
        return Response(str(resp), mimetype='text/xml')

    # Add AI response to conversation and transcript
    sessions[call_sid]['conversation'].append({"role": "assistant", "content": next_question})
    sessions[call_sid]['transcript'] += f"AI: {next_question}\n"

    return Response(ask_question(call_sid, next_question), mimetype='text/xml')


if __name__ == "__main__":
    app.run(port=3000, debug=True)