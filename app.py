import streamlit as st
import requests

# ✅ Get API key safely from secrets
API_KEY = st.secrets["OPENROUTER_API_KEY"]

# ✅ Function to call OpenRouter
def ask_openrouter(question, context):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Referer": "https://kustchatbot-ltnmhsnxyvylihsdxut2ud.streamlit.app",
        "X-Title": "KUSTBOT Chat"
    }

    data = {
        "model": "deepseek/deepseek-r1-0528-qwen3-8b:free",
        "messages": [{
            "role": "user",
            "content": f"""You are a helpful assistant. Answer the following question using only the provided BOOK content.
- Your answer must be short, clear, and in one or two sentences.
- Do NOT explain your reasoning.
- Do NOT show your thinking.
- Do NOT show your thought process.
- Do NOT add extra information.
- Only output the final answer.

BOOK:
{context}

QUESTION: {question}
"""
        }],
        "temperature": 0.2
    }

    r = requests.post(url, headers=headers, json=data)

    try:
        response_json = r.json()
    except Exception as e:
        return f"Error decoding response: {e}. Raw response: {r.text}"

    if r.status_code == 200:
        if 'choices' in response_json and len(response_json['choices']) > 0:
            return response_json['choices'][0]['message']['content'].strip()
        else:
            return f"Error: 'choices' not found in response. Full response: {response_json}"
    else:
        if 'error' in response_json:
            return f"API Error {r.status_code}: {response_json['error']}"
        else:
            return f"Error {r.status_code}: {r.text}"

# ✅ --- Streamlit App Config ---
st.set_page_config(page_title="📘 KUSTBOT")

# ✅ --- Global CSS for dark theme and white text ---
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
    }

    html, body, [class*="css"] {
        color: white;
    }

    h2, h3, h4, h5, h6 {
        color: white;
    }

    label, textarea, {
        color: white !important;
    }

    .stMarkdown p {
        color: white !important;
    }

    div[data-testid="stCaptionContainer"] {
        color: white !important;
    }
    input{
        color: black;
    }

    .stSpinner {
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ✅ --- Header with title and logo ---
col1, col2 = st.columns([6, 2])

with col1:
    st.markdown("""
        <h1 style='color: #FFCE44; margin-bottom: 0;'>KUSTBOT</h1>
    """, unsafe_allow_html=True)
    st.markdown("""
        <p style='color: white; margin-top: 5px;'>YOUR ULTIMATE ACADEMIC ADVISOR</p>
    """, unsafe_allow_html=True)

with col2:
    st.image("KUSTLogo.png", width=200)

# ✅ Caption under header
st.markdown("""
    <p style='color: white; font-size: 0.875rem; opacity: 0.8; margin-top: -10px;'>
        How can I help you with your academic plan?
    </p>
""", unsafe_allow_html=True)

# ✅ --- Load book content ---
try:
    with open("book.txt", "r", encoding="utf-8") as f:
        book_content = f.read()
        st.session_state.book_content = book_content
except FileNotFoundError:
    st.error("❌ No book.txt found. Please add it to your project folder!")

# ✅ --- Initialize chat history ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Custom white label using markdown
st.markdown("<div style='color: white; font-weight: 600; font-size: 10px;'>Your question</div>", unsafe_allow_html=True)

# ✅ --- Question form ---
if "book_content" in st.session_state:
    with st.form("question_form"):
        question = st.text_input(label="", key="question_input")
        submitted = st.form_submit_button("Ask")

    if submitted and question:
        with st.spinner("Processing ..."):
            answer = ask_openrouter(question, st.session_state.book_content)

        # Save Q&A pair to chat history
        st.session_state.chat_history.append({"question": question, "answer": answer})

# ✅ --- Display chat history ---
if st.session_state.chat_history:
    st.markdown("### 📚 Conversation History")
    for chat in st.session_state.chat_history:
        st.markdown(f"<p style='color: white'><b>You:</b> {chat['question']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: white'><b>KUSTBOT:</b> {chat['answer']}</p>", unsafe_allow_html=True)
        st.markdown("---")
