import streamlit as st
from pypdf import PdfReader
from docx import Document
from bs4 import BeautifulSoup
from google import genai

# Initialize Gemini client using Streamlit Secrets
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Helper function to extract text from supported file formats
def extract_text(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    
    file_name = uploaded_file.name.lower()
    
    if file_name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")
    
    elif file_name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    
    elif file_name.endswith(".docx"):
        doc = Document(uploaded_file)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    
    elif file_name.endswith((".html", ".htm")):
        soup = BeautifulSoup(uploaded_file.read(), "html.parser")
        return soup.get_text(separator="\n", strip=True)
    
    return ""

# --- UI Layout matching the sample interface ---
st.header("Input to AI")

question = st.text_input("Enter your question:")

uploaded_file = st.file_uploader(
    "Upload attachment:",
    type=["txt", "pdf", "docx", "html", "htm"]
)

if question:
    st.header("AI Response:")
    
    context = extract_text(uploaded_file)
    
    if context.strip():
        prompt = (
            f"Use the following document context to answer the user's question.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}"
        )
    else:
        prompt = (
            f"No document context was provided. Answer the user's question directly.\n\n"
            f"Question: {question}"
        )

    with st.spinner("Generating response..."):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt
            )
            st.write(response.text)
        except Exception as e:
            st.error(f"Error communicating with Gemini: {e}")
