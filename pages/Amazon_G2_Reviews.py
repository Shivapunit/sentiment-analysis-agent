import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud
from utils.amazon_api import fetch_amazon_product
from utils.g2_api import fetch_g2_vendors
from utils.sentiment import analyze_sentiment

analyzer = SentimentIntensityAnalyzer()

st.set_page_config(page_title="Amazon & G2 Reviews", page_icon="🛒", layout="wide")
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
                wc = WordCloud(width=800, height=400, background_color='white', colormap='plasma').generate(' '.join(df_reviews['text']))
                fig, ax = plt.subplots()
                ax.imshow(wc, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
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

st.markdown("---")
st.markdown(
    "<div style='text-align:center; font-size:0.85em; color:grey;'>© 2025 TrendTrackr | Created by <b>Shivakant Dubey</b> | <a href='https://www.linkedin.com/in/shivapunit/' target='_blank'>Connect on LinkedIn</a></div>",
    unsafe_allow_html=True
)
