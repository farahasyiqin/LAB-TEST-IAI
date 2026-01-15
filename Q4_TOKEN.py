import streamlit as st
from PyPDF2 import PdfReader
import nltk

# Download NLTK resources
nltk.download('punkt')

st.title("Semantic Text Chunking")
uploaded_file = st.file_uploader("Upload PDF", type="pdf")  # Step 1 [cite: 128]

if uploaded_file:
    # Step 2: Extract text [cite: 129]
    reader = PdfReader(uploaded_file)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text()

    # Step 3 & 4: Tokenize [cite: 130, 131]
    sentences = nltk.sent_tokenize(full_text)

    st.subheader("Sample Chunked Text (Indices 58-68)")
    if len(sentences) > 68:
        for i in range(58, 69):
            st.write(f"**Sentence {i}:** {sentences[i]}")
    else:
        st.write("The document does not have enough sentences for the requested range.")