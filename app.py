import streamlit as st
import requests
import streamlit as st
API_KEY=st.secrets["OPENROUTER_API_KEY"]   # Replace with your actual key

def ask_openrouter(question, context):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Referer": "https://kustchatbot-ltnmhsnxyvylihsdxut2ud.streamlit.app",  # Correct header
        "X-Title": "Colab Book Chatbot"
    }

    data = {
        "model": "deepseek/deepseek-r1-0528-qwen3-8b:free",  # or your model
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

# --- Streamlit Interface ---
st.set_page_config(page_title="📘 Book Chatbot")
# the code block below defines the interface bg color
st.markdown(
    """
    <style>
    .stApp {
        background-color: #1A335E; /* Replace with your hex code */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Use columns to align title on the left and logo on the right
col1, col2 = st.columns([6, 2])  # Adjust width ratio as needed

with col1:
    st.markdown("""
    <h1 style='color: #FFCE44;'>KUSTBOT</h1>
""", unsafe_allow_html=True) 

st.markdown("""
    <p style='color: #FFCE44;'>YOUR ULTIMATE ACADEMIC ADVISOR</p>
""", unsafe_allow_html=True)

with col2:
    st.image("KUSTLogo.png", width=200)  # Replace with your filename and size

st.caption("How can I help you with your academic plan?")

# Load book content from file saved by Colab
try:
    with open("book.txt", "r", encoding="utf-8") as f:
        book_content = f.read()
        st.session_state.book_content = book_content
    # st.success("✅ Book loaded from book.txt") # This line ensures the book is loaded
    # with st.expander("📖 Show Book Content"): # this line displays book content
    #     st.text_area("Book Content", book_content, height=300) # specifies size of the displayed content
except FileNotFoundError:
    st.error("❌ No /content/book.txt found. Please run your extract_text_from_pdf() and save book.txt first.")

# Ask a question
if "book_content" in st.session_state:
    question = st.text_input("Your question")
    if question:
        with st.spinner("Processing ..."):
            response = ask_openrouter(question, st.session_state.book_content)
        st.markdown(f"**Answer:** {response}")
