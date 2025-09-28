import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from newsapi import NewsApiClient

# --- Page Configuration ---
st.set_page_config(page_title="TrendTrackr", page_icon="🧠", layout="wide")

# --- Sidebar ---
st.sidebar.header("📈 TrendTrackr")
st.sidebar.caption("Tracking trends, decoding sentiment.")
page = st.sidebar.radio("📂 Select Dashboard", ["News Sentiment", "Amazon & G2 Reviews"])
st.sidebar.markdown("---")
with st.sidebar.expander("ℹ️ About & Data Source", expanded=True):
    st.markdown("""
        - **News Sentiment:** Headlines from [NewsAPI.org](https://newsapi.org)
        - **Amazon Reviews:** Product data via RapidAPI
        - **G2 Vendors:** B2B software autocomplete via RapidAPI
        - **Model:** VADER Sentiment Analysis
    """)
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style='text-align: center; font-size: 0.9em;'>
        Created by <b>Shivakant Dubey</b><br>
        <a href='https://www.linkedin.com/in/shivapunit/' target='_blank'>🔗 LinkedIn Profile</a>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Sentiment Setup ---
analyzer = SentimentIntensityAnalyzer()
NEWS_API_KEY = st.secrets.get("NEWS_API_KEY", "0ac47642d2d8408e9bf075473df6cbc7")
RAPIDAPI_KEY = "b5add04a2amsh97b53fc17139a3ep11f058jsn6a762af25aea"

# --- Shared Functions ---
def analyze_sentiment(texts):
    df = pd.DataFrame(texts, columns=["text"])
    df["compound"] = df["text"].apply(lambda t: analyzer.polarity_scores(t)["compound"])
    df["sentiment"] = df["compound"].apply(lambda c: "Positive" if c >= 0.05 else "Negative" if c <= -0.05 else "Neutral")
    return df

def generate_wordcloud(text_series):
    text = ' '.join(text_series)
    if not text: return None
    wc = WordCloud(width=800, height=400, background_color='white', colormap='plasma').generate(text)
    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    return fig

# --- NewsAPI Fetch ---
@st.cache_data(ttl=3600)
def fetch_news(query):
    newsapi = NewsApiClient(api_key=NEWS_API_KEY)
    try:
        articles = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=100).get('articles', [])
        return [{'title': a.get('title', ''), 'publishedAt': a.get('publishedAt', '')} for a in articles if a.get('title')]
    except Exception as e:
        return {"error": str(e)}

# --- Amazon API ---
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

# --- G2 API ---
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

# --- News Sentiment Dashboard ---
if page == "News Sentiment":
    st.title("🧠 TrendTrackr: Real-Time News Sentiment")
    providers = ["General", "AWS", "Azure", "Cloudflare", "Fastly", "Google Cloud"]
    selected_provider = st.selectbox("Choose Provider", providers)
    default_query = selected_provider if selected_provider != "General" else ""

    with st.form(key='search_form'):
        search_query = st.text_input("Search Query", value=default_query, placeholder="e.g., Apple, Climate Change, The latest Marvel movie")
        submitted = st.form_submit_button("Analyze Sentiment")

    if NEWS_API_KEY == "0ac47642d2d8408e9bf075473df6cbc7":
        st.warning("Using fallback API key. Consider configuring secrets for security.")

    if submitted:
        with st.spinner("Brewing insights... ☕"):
            articles = fetch_news(search_query)
            if isinstance(articles, dict) and "error" in articles:
                st.error(articles["error"])
            elif not articles:
                st.warning("No articles found.")
            else:
                df = pd.DataFrame(articles)
                df["text"] = df["title"]
                df = analyze_sentiment(df[["text"]])
                df["publishedAt"] = pd.to_datetime([a["publishedAt"] for a in articles])
                st.success(f"Found {len(df)} articles.")
                avg_score = df["compound"].mean()
                sentiment_label = "Positive" if avg_score >= 0.05 else "Negative" if avg_score <= -0.05 else "Neutral"
                col1, col2, col3 = st.columns(3)
                col1.metric("📰 Total Headlines", len(df))
                col2.metric("💬 Overall Sentiment", sentiment_label)
                col3.metric("📈 Avg. Score", f"{avg_score:.2f}")

                tab1, tab2, tab3 = st.tabs(["📊 Distribution", "📈 Trend", "☁️ Word Cloud"])
                with tab1:
                    sentiment_counts = df["sentiment"].value_counts()
                    fig_pie = px.pie(sentiment_counts, values=sentiment_counts.values, names=sentiment_counts.index,
                                     color=sentiment_counts.index,
                                     color_discrete_map={'Positive': '#2ecc71', 'Negative': '#e74c3c', 'Neutral': '#95a5a6'})
                    st.plotly_chart(fig_pie, use_container_width=True)
                with tab2:
                    df["date"] = df["publishedAt"].dt.date
                    sentiment_by_day = df.groupby("date")["compound"].mean().reset_index()
                    fig_line = px.line(sentiment_by_day, x="date", y="compound", markers=True)
                    st.plotly_chart(fig_line, use_container_width=True)
                with tab3:
                    fig_wc = generate_wordcloud(df["text"])
                    if fig_wc: st.pyplot(fig_wc)

# --- Amazon & G2 Dashboard ---
elif page == "Amazon & G2 Reviews":
    st.title("🛒 Amazon & G2 Review Sentiment")
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
    """
    <div style='text-align:center; font-size:0.85em; color:grey;'>
        © 2025 TrendTrackr | Created by <b>Shivakant Dubey</b> |
        <a href='https://www.linkedin.com/in/shivapunit/' target='_blank'>Connect on LinkedIn</a>
    </div>
    """,
    unsafe_allow_html=True
)
