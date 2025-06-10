import requests

# Configuration
GROQ_API_KEY = ""
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def ask_groq(prompt, context=None):
    """Get real responses from Groq API"""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [{"role": "user", "content": context + "\n\n" + prompt}] if context else [
        {"role": "user", "content": prompt}]

    payload = {
        "model": "llama3-8b-8192",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 300
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload)
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return "[AI Unavailable]"


def evaluate_candidate(history):
    """Get Groq to evaluate all Q&A and provide rating"""
    evaluation_prompt = f"""
    Candidate Interview History:
    {history}

    Evaluate this candidate for a software developer position considering:
    1. Technical accuracy (0-10)
    2. Depth of knowledge (0-10)
    3. Communication clarity (0-10)
    4. Problem-solving approach (0-10)

    Provide:
    - Overall score (0-100)
    - Strengths
    - Areas for improvement
    - Hiring recommendation (Strong Yes/Yes/No/Strong No)
    - Brief written feedback
    """
    return ask_groq(evaluation_prompt)


def run_interview():
    print("🧠 GROQ-POWERED TECHNICAL INTERVIEW")
    print("Type 'exit' anytime to quit\n")

    candidate = input("Candidate name: ").strip()
    if not candidate:
        candidate = "Test Candidate"

    context = f"Interviewing {candidate} for mid-level software developer position ($3500 budget)"
    history = []

    # Interview Loop (5 Questions)
    for q_num in range(1, 6):
        # Generate question based on previous answers
        prompt = f"Ask technical question #{q_num} about programming (be specific)"
        if history:
            last_answer = history[-1]["answer"]
            prompt += f" Consider this previous answer: {last_answer[:100]}..."

        question = ask_groq(prompt, context)
        print(f"\n🔍 QUESTION {q_num}: {question}")

        answer = input("💬 YOUR ANSWER: ")
        if answer.lower() == "exit":
            print("\nInterview terminated early.")
            return

        history.append({
            "question": question,
            "answer": answer,
            "question_num": q_num
        })

    # Evaluation
    print("\n⏳ Generating evaluation...")
    formatted_history = "\n".join(
        f"Q{q['question_num']}: {q['question']}\nA: {q['answer']}"
        for q in history
    )

    evaluation = evaluate_candidate(formatted_history)

    print("\n📊 FINAL EVALUATION")
    print("=" * 50)
    print(evaluation)
    print("=" * 50)

    # Save to file
    with open(f"interview_{candidate.replace(' ', '_')}.txt", "w") as f:
        f.write(f"Candidate: {candidate}\n")
        f.write(f"Evaluation:\n{evaluation}\n\n")
        f.write("Full Interview:\n" + formatted_history)

    print(f"\n📝 Report saved to 'interview_{candidate.replace(' ', '_')}.txt'")


if __name__ == "__main__":
    run_interview()