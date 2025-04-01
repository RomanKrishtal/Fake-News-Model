import streamlit as st
from newspaper import Article
from transformers import pipeline

# Function to extract article text from URL
def extract_text_from_url(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        return None

# Load Hugging Face fake news model (lighter version for Streamlit Cloud)
model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
fake_news_detector = pipeline("text-classification", model=model_name, tokenizer=model_name)

# Label mapping for readability
label_map = {
    "LABEL_0": "❌ Fake",
    "LABEL_1": "✅ Real"
}

# Truncate long article text to avoid model input errors
def truncate_text(text, max_chars=1000):
    return text[:max_chars]

# Streamlit UI
st.title("📰 Fake News Detection App")
st.subheader("Paste a news article link to check if it's Fake or Real")

url = st.text_input("Enter News Article URL:")

if st.button("Analyze"):
    if url:
        article_text = extract_text_from_url(url)
        if article_text:
            if len(article_text) > 1000:
                st.warning("⚠️ Article was too long — we truncated it for analysis.")
            safe_text = truncate_text(article_text)
            prediction = fake_news_detector(safe_text)
            raw_label = prediction[0]['label']
            label = label_map.get(raw_label, raw_label)
            st.subheader(f"Prediction: {label}")
        else:
            st.error("Could not extract text from the URL. Try another link.")