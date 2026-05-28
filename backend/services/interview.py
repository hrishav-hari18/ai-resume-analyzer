import time
import re

from services.groqapi import query_llm


# ================= QUESTION =================

def generate_question(role, history):

    context = "\n".join(history)

    prompt = f"""
You are an interviewer for {role}.

Conversation:
{context}

Ask ONE interview question only.
"""

    res = query_llm(prompt)

    if isinstance(res, str):
        return res

    return "Tell me about yourself."


# ================= EVALUATION =================

def evaluate_answer(
    question,
    answer,
    role
):

    prompt = f"""
Evaluate this interview answer.

Role:
{role}

Question:
{question}

Answer:
{answer}

Give response in this format:

Score: X/10
Feedback: short feedback
"""

    res = query_llm(prompt)

    if isinstance(res, str):
        return res

    return "Score: 5/10\nFeedback: Average answer"


# ================= SCORE EXTRACTION =================

def extract_score(text):

    try:

        match = re.search(
            r"Score:\\s*(\\d+)",
            text
        )

        if match:

            return float(
                match.group(1)
            )

    except:
        pass

    return 5


# ================= SESSION =================

def start_session(duration):

    return {

        "start": time.time(),

        "duration": duration * 60,

        "history": [],

        "scores": [],

        "questions": [],

        "answers": []
    }


# ================= ACTIVE =================

def is_active(session):

    return (
        time.time()
        - session["start"]
    ) < session["duration"]


# ================= END =================

def end_session(session):

    if not session["scores"]:

        return {
            "final_score": 0
        }

    avg = sum(
        session["scores"]
    ) / len(session["scores"])

    return {

        "final_score":
        round(avg, 2),

        "questions":
        session["questions"],

        "answers":
        session["answers"],

        "scores":
        session["scores"]
    }