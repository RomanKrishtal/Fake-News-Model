import streamlit as st
from newspaper import Article
from transformers import pipeline

# Cached model loading
@st.cache_resource
def load_model():
    model_name = "philschmid/MiniLM-L6-H384-uncased-fake-news"
    return pipeline("text-classification", model=model_name, tokenizer=model_name)

# Extract text from a news article URL
def extract_text_from_url(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        return None

# Truncate long articles to avoid model errors
def truncate_text(text, max_chars=1000):
    return text[:max_chars]

# UI
def main():
    st.title("📰 Fake News Detection (via URL)")
    st.subheader("Paste a news article link to check if it's Fake or Real")

    url = st.text_input("Enter News Article URL")

    if st.button("Analyze"):
        if not url.strip():
            st.warning("Please enter a valid URL.")
            return

        article_text = extract_text_from_url(url)
        if article_text:
            if len(article_text) > 1000:
                st.warning("Article was too long — only the first 1000 characters were analyzed.")
            safe_text = truncate_text(article_text)
            model = load_model()
            result = model(safe_text)
            label_map = {
                "LABEL_0": "❌ Fake",
                "LABEL_1": "✅ Real"
            }
            label = label_map.get(result[0]['label'], result[0]['label'])
            st.success(f"Prediction: {label} (Confidence: {result[0]['score']:.2f})")
        else:
            st.error("Failed to extract text from the URL. Please try another link.")

if __name__ == "__main__":
    main()
