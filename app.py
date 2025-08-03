import streamlit as st
import requests
import pandas as pd
import os
import base64
import json

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

- If the answer is not directly found in the BOOK, say: "Consult your department for details about this question."
- Do NOT use your own knowledge.
- Do NOT make assumptions.
- Do NOT explain anything.
- Only output the answer found in the BOOK.
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
        "temperature": 0.0
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

# ✅ Save questions and answers to Excel
def save_to_excel(question, answer, filename="chat_history.xlsx"):
    data = {"Question": [question], "Answer": [answer]}
    new_df = pd.DataFrame(data)

    if os.path.exists(filename):
        existing_df = pd.read_excel(filename)
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        updated_df = new_df

    updated_df.to_excel(filename, index=False)



#push excel to github
def push_to_github(filename="chat_history.xlsx"):
    if not os.path.exists(filename):
        return "❌ Excel file not found."

    # Load file content and encode to base64
    with open(filename, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    # GitHub setup
    token = st.secrets["GITHUB_TOKEN"]
    repo = st.secrets["GITHUB_REPO"]  # e.g., "yourusername/kustbot-chat-history"
    branch = st.secrets.get("GITHUB_BRANCH", "main")
    path = f"chat_logs/{filename}"  # Target path in repo

    api_url = f"https://api.github.com/repos/{repo}/contents/{path}"

    # Check if file exists (to update instead of create)
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(api_url, headers=headers, params={"ref": branch})
    
    if r.status_code == 200:
        sha = r.json()["sha"]
        message = "Update chat history"
    else:
        sha = None
        message = "Create chat history"

    data = {
        "message": message,
        "branch": branch,
        "content": content,
    }

    if sha:
        data["sha"] = sha

    # Push file
    push_response = requests.put(api_url, headers=headers, data=json.dumps(data))

    if push_response.status_code in [200, 201]:
        return f"✅ Excel file pushed to GitHub: [chat_logs/{filename}](https://github.com/{repo}/blob/{branch}/chat_logs/{filename})"
    else:
        return f"❌ GitHub push failed: {push_response.status_code} — {push_response.text}"


# ✅ --- Streamlit App Config ---
st.set_page_config(page_title="📘 KUSTBOT")

# ✅ --- Global CSS for dark theme and white text ---
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
    }

    html, body, [class*="css"] {
        color: white !important;
    }

    h2, h3, h4, h5, h6, label, textarea {
        color: white !important;
    }

    .stMarkdown p {
        color: white !important;
    }

    div[data-testid="stCaptionContainer"] {
        color: white !important;
    }

    input {
        color: white !important;
        background-color: #222222 !important;
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

# ✅ Custom white label
st.markdown("<div style='color: white; font-weight: 400; font-size: 16px;'>Your question</div>", unsafe_allow_html=True)

# ✅ --- Question form ---
if "book_content" in st.session_state:
    with st.form("question_form"):
        question = st.text_input(label="", key="question_input")
        submitted = st.form_submit_button("Ask")

    if submitted and question:
        with st.spinner("Processing ..."):
            answer = ask_openrouter(question, st.session_state.book_content)

        # ✅ Save to session and Excel
        st.session_state.chat_history.append({"question": question, "answer": answer})
        save_to_excel(question, answer)
        push_result = push_to_github()
        
        # the following line of code is meant to show in the interface (UI) that the answer has been exported to Excel
        #st.info(push_result)
        

# ✅ --- Display chat history ---
if st.session_state.chat_history:
    st.markdown("### 📚 Conversation History")
    for chat in st.session_state.chat_history:
        st.markdown(f"<p style='color: white'><b>You:</b> {chat['question']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: white'><b>KUSTBOT:</b> {chat['answer']}</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 0.5px solid #444;'>", unsafe_allow_html=True)
