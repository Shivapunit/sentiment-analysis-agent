import streamlit as st
import pandas as pd
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud
import matplotlib.pyplot as plt

analyzer = SentimentIntensityAnalyzer()
RAPIDAPI_KEY = "b5add04a2amsh97b53fc17139a3ep11f058jsn6a762af25aea"

# --- Agent 1: Fetch Amazon Product ---
def fetch_amazon_product(asin, country="US"):
    url = "https://real-time-amazon-data.p.rapidapi.com/product-details"
    headers = {
        "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com",
        "x-rapidapi-key": RAPIDAPI_KEY
    }
    params = {"asin": asin, "country": country}
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        return {
            "title": data.get("product_title", ""),
            "reviews": [r.get("review_text", "") for r in data.get("reviews", [])]
        }
    except Exception as e:
        return {"error": str(e)}

# --- Agent 2: Fetch G2 Vendors ---
def fetch_g2_vendors(query):
    url = "https://g2-products-reviews-users2.p.rapidapi.com/vendor/autocomplete"
    headers = {
        "x-rapidapi-host": "g2-products-reviews-users2.p.rapidapi.com",
        "x-rapidapi-key": RAPIDAPI_KEY
    }
    try:
        response = requests.get(url, headers=headers, params={"Query": query})
        return response.json().get("vendors", [])
    except Exception as e:
        return {"error": str(e)}

# --- Sentiment Analyzer ---
def analyze_sentiment(texts):
    df = pd.DataFrame(texts, columns=["text"])
    df["compound"] = df["text"].apply(lambda t: analyzer.polarity_scores(t)["compound"])
    df["sentiment"] = df["compound"].apply(lambda c: "Positive" if c >= 0.05 else "Negative" if c <= -0.05 else "Neutral")
    return df

# --- WordCloud ---
def generate_wordcloud(text_series):
    text = ' '.join(text_series)
    if not text: return None
    wc = WordCloud(width=800, height=400, background_color='white', colormap='plasma').generate(text)
    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    return fig

# --- UI ---
st.title("🛒 Amazon & G2 Review Sentiment")
st.markdown("Analyze product reviews and vendor mentions using agent-to-agent orchestration.")

tab1, tab2 = st.tabs(["Amazon Product Reviews", "G2 Vendor Search"])

with tab1:
    asin = st.text_input("Enter Amazon ASIN", value="B07ZPKBL9V")
    if st.button("Analyze Amazon Product"):
        product = fetch_amazon_product(asin)
        if "error" in product:
            st.error(product["error"])
        else:
            st.write(f"**Product Title:** {product['title']}")
            title_sentiment = analyzer.polarity_scores(product['title'])
            st.write(f"**Title Sentiment:** {title_sentiment}")
            if product['reviews']:
                df_reviews = analyze_sentiment(product['reviews'])
                st.dataframe(df_reviews)
                fig_wc = generate_wordcloud(df_reviews['text'])
                if fig_wc: st.pyplot(fig_wc)
            else:
                st.info("No reviews available.")

with tab2:
    vendor_query = st.text_input("Search G2 Vendor", value="Salesfor")
    if st.button("Search G2 Vendors"):
        vendors = fetch_g2_vendors(vendor_query)
        if isinstance(vendors, dict) and "error" in vendors:
            st.error(vendors["error"])
        elif not vendors:
            st.warning("No vendors found.")
        else:
            st.write("Matching Vendors:")
            for v in vendors:
                st.markdown(f"- {v.get('Name', 'Unknown')}")

# --- Footer ---
st.markdown("---")
st.markdown(
    "<div style='text-align:center; font-size:0.85em; color:grey;'>© 2025 TrendTrackr | Created by <b>Shivakant Dubey</b> | <a href='https://www.linkedin.com/in/shivapunit/' target='_blank'>Connect on LinkedIn</a></div>",
    unsafe_allow_html=True
)
