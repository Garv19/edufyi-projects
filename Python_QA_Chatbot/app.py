import streamlit as st

from chatbot import get_answer


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Garv's chatbot",
    page_icon="🤖💬",
    layout="centered"
)


# ==========================================
# 2. TITLE
# ==========================================

st.title("🤖💬 Garv's chatbot")

st.write(
    "Ask questions about Python programming "
    "and get answers from a local AI model."
)


# ==========================================
# 3. CHAT HISTORY
# ==========================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ==========================================
# 4. DISPLAY PREVIOUS MESSAGES
# ==========================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.write(
            message["content"]
        )


# ==========================================
# 5. USER INPUT
# ==========================================

user_question = st.chat_input(
    "Ask a Python question..."
)


# ==========================================
# 6. PROCESS QUESTION
# ==========================================

if user_question:

    # Display user message
    with st.chat_message("user"):

        st.write(
            user_question
        )


    # Save user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_question
        }
    )


    # ======================================
    # GET LLM RESPONSE
    # ======================================

    with st.chat_message("assistant"):

        with st.spinner(
            "Thinking..."
        ):

            try:

                answer = get_answer(
                    user_question
                )

                st.write(answer)


            except Exception as e:

                answer = (
                    "Sorry, I could not connect "
                    "to the local AI model."
                )

                st.error(
                    str(e)
                )


    # ======================================
    # SAVE ASSISTANT RESPONSE
    # ======================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )