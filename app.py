
import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ==========================================
# 1. PAGE CONFIGURATION AND COLOUR THEME
# ==========================================

st.set_page_config(
    page_title="Student Learning Agent",
    page_icon="🎓",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        135deg, #eef2ff 0%, #f5f3ff 50%, #eff6ff 100%
    );
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

h1 {
    color: #4338ca !important;
    font-weight: 800 !important;
}

h2, h3 {
    color: #3730a3 !important;
    font-weight: 700 !important;
}

p, label, .stMarkdown {
    color: #1e293b;
}

.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(90deg, #4f46e5, #7c3aed);
    color: white !important;
    border: none;
    border-radius: 10px;
    padding: 0.55rem 1.2rem;
    font-weight: 600;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: linear-gradient(90deg, #4338ca, #6d28d9);
    border: none;
}

.stTextInput input {
    border: 1px solid #c7d2fe;
    border-radius: 9px;
    background-color: white;
    color: #1e293b;
}

.stSelectbox [data-baseweb="select"] > div {
    border-radius: 9px;
    border-color: #c7d2fe;
    background-color: white;
}

.stRadio label {
    color: #334155 !important;
}

div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #ffffff, #eef2ff);
    border: 1px solid #c7d2fe;
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.08);
}

div[data-testid="stMetricLabel"] {
    color: #4338ca !important;
}

div[data-testid="stMetricValue"] {
    color: #312e81 !important;
    font-weight: 800;
}

div[data-testid="stChatMessage"] {
    background-color: rgba(255, 255, 255, 0.9);
    border: 1px solid #e0e7ff;
    border-radius: 12px;
    padding: 12px;
}

hr {
    border-color: #c7d2fe;
}

@media (max-width: 768px) {
    .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. HEADER
# ==========================================

st.title("🎓 Student Learning Agent")

st.markdown("""
Welcome to your personal learning space! 💜

Learn Python with AI assistance, practise with quizzes,
and discover which topics you should revise next.
""")

st.divider()


# ==========================================
# 3. INITIALIZE GEMINI
# ==========================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = None

if api_key:
    try:
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=30000000)
        )
    except Exception as e:
        st.warning("Could not initialize the AI assistant.")
        st.caption(f"Technical details: {type(e).__name__}: {e}")


# ==========================================
# 4. AI LEARNING ASSISTANT WITH MEMORY
# ==========================================

st.header("🤖 AI Learning Assistant")

st.write(
    "Ask Python questions, request examples, "
    "and ask follow-up questions."
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if st.session_state.chat_history:
    if st.button("🗑️ Clear Conversation"):
        st.session_state.chat_history = []
        st.rerun()

# Display previous messages
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

with st.form("ai_question_form"):
    user_question = st.text_input(
        "What would you like to learn?",
        placeholder="Example: What is a Python function?"
    )

    ask_ai = st.form_submit_button(
        "✨ Ask AI",
        use_container_width=True
    )

if ask_ai:
    if not user_question.strip():
        st.warning("Please enter a question.")

    elif client is None:
        st.error(
            "Gemini is unavailable. Check GEMINI_API_KEY "
            "in your .env file and restart the app."
        )

    else:
        try:
            previous_messages = st.session_state.chat_history[-6:]

            conversation_context = "\n".join(
                f"{'Student' if msg['role'] == 'user' else 'Tutor'}: "
                f"{msg['content']}"
                for msg in previous_messages
            )

            prompt = f"""
You are a helpful Python tutor for a college student.

Instructions:
- Explain concepts in simple English.
- For Python concepts, include a definition,
  a short code example, expected output, and explanation.
- Understand follow-up questions using the conversation.
- Refer to previous examples when asked.
- Keep answers clear and concise.
- Do not invent previous conversation details.

Previous conversation:
{conversation_context}

Student's latest question:
{user_question}
"""

            with st.spinner("✨ Your AI tutor is preparing an answer..."):
                response = client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=prompt,
                    config={
                        "max_output_tokens": 700,
                        "temperature": 0.3
                    }
                )

            answer = response.text

            if answer and answer.strip():
                st.session_state.chat_history.extend([
                    {"role": "user", "content": user_question},
                    {"role": "assistant", "content": answer}
                ])

                with st.chat_message("user"):
                    st.markdown(user_question)

                with st.chat_message("assistant"):
                    st.markdown(answer)

            else:
                st.warning(
                    "The AI returned an empty answer. Please try again."
                )

        except Exception as e:
            st.error(
                "The AI could not complete the request. "
                "Check your internet connection, API access, "
                "and model availability."
            )
            st.caption(
                f"Technical details: {type(e).__name__}: {e}"
            )

st.divider()


# ==========================================
# 5. PYTHON QUIZ
# ==========================================

st.header("📝 Python Knowledge Quiz")

st.write(
    "Test your Python basics and identify topics "
    "that need more practice."
)

questions = [
    {
        "question": "Which keyword is used to define a function?",
        "options": ["func", "def", "function", "define"],
        "answer": "def",
        "topic": "Functions"
    },
    {
        "question": "Which data type stores key-value pairs?",
        "options": ["List", "Tuple", "Dictionary", "Set"],
        "answer": "Dictionary",
        "topic": "Data Types"
    },
    {
        "question": "Which loop commonly iterates over a list?",
        "options": ["for", "switch", "case", "define"],
        "answer": "for",
        "topic": "Loops"
    },
    {
        "question": "Which symbol starts a single-line comment?",
        "options": ["//", "#", "/*", "&"],
        "answer": "#",
        "topic": "Syntax"
    },
    {
        "question": "Which keyword checks another condition after if?",
        "options": ["else if", "elseif", "elif", "then"],
        "answer": "elif",
        "topic": "Conditions"
    }
]

topics = ["All Topics"] + sorted({
    question["topic"] for question in questions
})

selected_topic = st.selectbox(
    "📚 Choose a quiz topic:",
    topics
)

if selected_topic == "All Topics":
    quiz_questions = questions
else:
    quiz_questions = [
        question
        for question in questions
        if question["topic"] == selected_topic
    ]

st.info(f"📌 Number of questions: {len(quiz_questions)}")

with st.form("quiz_form"):
    answers = []

    for i, question in enumerate(quiz_questions):
        with st.container(border=True):
            st.subheader(f"Question {i + 1}")
            st.write(question["question"])

            answer = st.radio(
                "Choose your answer:",
                question["options"],
                key=f"quiz_{question['topic']}",
                index=None
            )

            answers.append(answer)

    submitted = st.form_submit_button(
        "🎯 Submit Quiz",
        use_container_width=True
    )


# ==========================================
# 6. QUIZ RESULTS AND ADAPTIVE DIFFICULTY
# ==========================================

if submitted:
    score = 0
    weak_topics = []

    st.header("📊 Your Quiz Results")

    for i, question in enumerate(quiz_questions):
        if answers[i] == question["answer"]:
            score += 1
            st.success(f"Question {i + 1}: Correct! 🎉")
        else:
            st.error(
                f"Question {i + 1}: Incorrect. "
                f"Correct answer: {question['answer']}"
            )
            weak_topics.append(question["topic"])

    total = len(quiz_questions)
    incorrect = total - score
    percentage = (score / total * 100) if total else 0

    col1, col2, col3 = st.columns(3)

    col1.metric("✅ Correct Answers", score)
    col2.metric("❌ Incorrect Answers", incorrect)
    col3.metric("🏆 Percentage", f"{percentage:.1f}%")

    st.progress(percentage / 100)

    st.markdown(f"### Final Score: {score}/{total}")

    # Adaptive difficulty based on score
    st.subheader("🧠 Adaptive Learning")

    if percentage >= 80:
        difficulty = "Hard"
        st.success("Excellent performance! 🌟")
        st.write(
            "You're ready for harder questions. "
            "Try more challenging Python problems."
        )

    elif percentage >= 40:
        difficulty = "Medium"
        st.info("Good effort! Keep improving. 💪")
        st.write(
            "Practise medium-level questions to strengthen "
            "your Python understanding."
        )

    else:
        difficulty = "Easy"
        st.warning("Let's strengthen your basics first. 📖")
        st.write(
            "Start with easier questions and revise the "
            "concepts you missed."
        )

    st.markdown(f"### 📚 Recommended Difficulty: {difficulty}")

    st.divider()

    # Weak-topic recommendation
    st.subheader("🎯 Agent Recommendation")

    if not weak_topics:
        st.success(
            "You answered every question correctly! "
            "Try a more advanced Python quiz next."
        )

    else:
        topic_counts = {}

        for topic in weak_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        recommended_topic = max(
            topic_counts,
            key=topic_counts.get
        )

        st.markdown(
            f"### 📌 Recommended topic: {recommended_topic}"
        )

        st.write(
            "Revise this topic first. This recommendation is "
            "based on the topics associated with your incorrect answers."
        )

        st.info(
            "Tip: Use the AI Learning Assistant above to ask "
            f"questions about **{recommended_topic}**."
        )


# ==========================================
# 7. FOOTER
# ==========================================

st.divider()

st.markdown(
    "<div style='text-align:center; color:#6366f1;'>"
    "<b>Student Learning Agent</b><br>"
    "AI-Assisted Python Learning and Assessment System 🎓"
    "</div>",
    unsafe_allow_html=True
)
