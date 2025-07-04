import streamlit as st
import requests

API_KEY = "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"  # Replace with your actual key

def ask_openrouter(question, context):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Referer": "http://localhost",  # Correct header
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
st.title("📘 Ask the Book")
st.caption("Ask questions about the book you loaded in Colab.")

# Load book content from file saved by Colab
try:
    with open("book.txt", "r", encoding="utf-8") as f:
        book_content = f.read()
        st.session_state.book_content = book_content
    st.success("✅ Book loaded from book.txt")
    with st.expander("📖 Show Book Content"):
        st.text_area("Book Content", book_content, height=300)
except FileNotFoundError:
    st.error("❌ No /content/book.txt found. Please run your extract_text_from_pdf() and save book.txt first.")

# Ask a question
if "book_content" in st.session_state:
    question = st.text_input("Your question")
    if question:
        with st.spinner("Thinking..."):
            response = ask_openrouter(question, st.session_state.book_content)
        st.markdown(f"**Answer:** {response}")
