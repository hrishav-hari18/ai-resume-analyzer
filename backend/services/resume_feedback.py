from services.groqapi import query_llm


def generate_resume_feedback(
    resume,
    role,
    score
):

    prompt = f"""
You are an ATS resume reviewer.

Candidate Role:
{role}

Resume:
{resume}

ATS Score:
{score}

Give:

1. Strengths
2. Missing skills
3. Resume improvements
4. Suggested projects
5. Certification suggestions

Keep response concise.
"""

    return query_llm(prompt)