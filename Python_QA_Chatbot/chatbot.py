import ollama


# ==========================================
# 1. MODEL CONFIGURATION
# ==========================================

MODEL_NAME = "llama3.2:3b"


# ==========================================
# 2. CHATBOT FUNCTION
# ==========================================

def get_answer(user_question):
    """
    Send the user's question to the local
    Ollama LLM and return its answer.
    """

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": """
You are a helpful Python programming tutor.

Your main purpose is to answer questions
related to Python programming.

Follow these rules:

1. Give clear and beginner-friendly explanations.

2. Use Python code examples when useful.

3. Explain code when necessary.

4. Keep answers reasonably concise.

5. If the user asks something unrelated
   to Python programming, politely explain
   that you are designed to answer
   Python-related questions.

6. Do not make up information.

7. If a question is unclear, ask the user
   to clarify it.

8. Always try to make your explanations
   easy for a beginner to understand.
"""
            },
            {
                "role": "user",
                "content": user_question
            }
        ]
    )


    # ==========================================
    # 3. EXTRACT ANSWER
    # ==========================================

    answer = response["message"]["content"]


    # ==========================================
    # 4. RETURN ANSWER
    # ==========================================

    return answer