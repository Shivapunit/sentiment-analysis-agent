import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from newsapi import NewsApiClient
import time

# --- Page Configuration ---
st.set_page_config(page_title="TrendTrackr", page_icon="🧠", layout="wide")

# --- Sidebar ---
st.sidebar.header("📈 TrendTrackr")
st.sidebar.caption("Tracking trends, decoding sentiment.")
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

# --- API & Sentiment Setup ---
analyzer = SentimentIntensityAnalyzer()
NEWS_API_KEY = st.secrets.get("NEWS_API_KEY", "0ac47642d2d8408e9bf075473df6cbc7")
RAPIDAPI_KEY = st.secrets.get("RAPIDAPI_KEY", "b5add04a2amsh97b53fc17139a3ep11f058jsn6a762af25aea")

# --- Shared Functions ---
@st.cache_data(ttl=3600)
def analyze_sentiment(texts):
    df = pd.DataFrame(texts, columns=["text"])
    df["compound"] = df["text"].apply(lambda t: analyzer.polarity_scores(t)["compound"])
    df["sentiment"] = df["compound"].apply(lambda c: "Positive" if c >= 0.05 else "Negative" if c <= -0.05 else "Neutral")
    return df

@st.cache_data(ttl=3600)
def generate_wordcloud(text_series):
    text = ' '.join(text_series)
    if not text: return None
    wc = WordCloud(width=800, height=400, background_color='white', colormap='plasma').generate(text)
    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    return fig

@st.cache_data(ttl=3600)
def fetch_news(query):
    newsapi = NewsApiClient(api_key=NEWS_API_KEY)
    try:
        articles = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=100).get('articles', [])
        return [{'title': a.get('title', ''), 'publishedAt': a.get('publishedAt', '')} for a in articles if a.get('title')]
    except Exception as e:
        return {"error": str(e)}

@st.cache_data(ttl=3600)
def fetch_amazon_product(asin, country="US"):
    url = "https://real-time-amazon-data.p.rapidapi.com/product-details"
    headers = {"x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com", "x-rapidapi-key": RAPIDAPI_KEY}
    params = {"asin": asin, "country": country}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json().get("data", {})
        return {
            "title": data.get("product_title", ""),
            "reviews": [r.get("review_text", "") for r in data.get("product_reviews", {}).get("reviews", [])]
        }
    except Exception as e:
        return {"error": str(e)}

# --- Main Dashboard UI ---
st.title("📈 TrendTrackr: Unified Sentiment & Research Dashboard")

tab_news, tab_reviews, tab_research = st.tabs(["🧠 News Sentiment", "🛒 Amazon & G2 Reviews", "🔬 Research Projects"])

with tab_news:
    st.header("Analyze Public Sentiment from News Headlines")
    providers = ["General", "AWS", "Azure", "Cloudflare", "Fastly", "Google Cloud"]
    selected_provider = st.selectbox("Choose Provider", providers, key='news_provider_select')
    default_query = selected_provider if selected_provider != "General" else ""

    with st.form(key='news_search_form'):
        search_query = st.text_input("Search Query", value=default_query, placeholder="e.g., Apple, Climate Change", key='news_query_input')
        submitted = st.form_submit_button("Analyze News Sentiment")

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
                df_sentiment = analyze_sentiment(df[["text"]])
                df["publishedAt"] = pd.to_datetime([a["publishedAt"] for a in articles])
                df = pd.concat([df, df_sentiment], axis=1)
                st.session_state['news_df'] = df

    if 'news_df' in st.session_state:
        df = st.session_state['news_df']
        st.success(f"Found {len(df)} articles.")
        avg_score = df["compound"].mean()
        sentiment_label = "Positive" if avg_score >= 0.05 else "Negative" if avg_score <= -0.05 else "Neutral"
        col1, col2, col3 = st.columns(3)
        col1.metric("📰 Total Headlines", len(df))
        col2.metric("💬 Overall Sentiment", sentiment_label)
        col3.metric("📈 Avg. Score", f"{avg_score:.2f}")

with tab_reviews:
    st.header("Analyze Product and Vendor Reviews")
    sub_tab_amazon, sub_tab_g2 = st.tabs(["📦 Amazon Product Reviews", "🏢 G2 Vendor Search"])

    with sub_tab_amazon:
        asin = st.text_input("Enter Amazon ASIN", value="B07ZPKBL9V", key='amazon_asin_input')
        if st.button("Analyze Amazon Product", key='amazon_button'):
            with st.spinner("Fetching Amazon reviews..."):
                product = fetch_amazon_product(asin)
                if "error" in product:
                    st.error(product["error"])
                else:
                    st.write(f"**Product Title:** {product['title']}")
                    if product['reviews']:
                        df_reviews = analyze_sentiment(product['reviews'])
                        st.dataframe(df_reviews)
                        st.write("**Review Word Cloud:**")
                        fig_wc = generate_wordcloud(df_reviews['text'])
                        if fig_wc: st.pyplot(fig_wc)
                    else:
                        st.info("No reviews available for this product.")

with tab_research:
    st.header("Research Projects & Simulations")
    sub_tab_rdma, sub_tab_cdn = st.tabs(["RDMA for AI Training", "CDN Paywall Analysis"])

    with sub_tab_rdma:
        st.subheader("Interactive Simulation: TCP/IP vs. RDMA")
        st.markdown("Simulate a gradient synchronization step in distributed AI training to see the performance difference.")

        gradient_size_mb = st.slider("Gradient Size (MB) to Synchronize", 16, 1024, 128, key='rdma_slider')

        if st.button("▶️ Run Simulation", key='rdma_button'):
            network_speed_gbps = 100
            tcp_latency_us = 50
            rdma_latency_us = 2
            tcp_cpu_overhead_ms = gradient_size_mb * 0.1
            rdma_cpu_overhead_ms = gradient_size_mb * 0.01
            transfer_time_s = (gradient_size_mb * 8) / (network_speed_gbps * 1000)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Traditional TCP/IP Path")
                st.markdown("--- ")
                st.markdown("1. 💾 **App Memory (GPU)** → `CPU Copy` → 2. 🖥️ **Kernel Memory** → `CPU Copy` → 3. 🌐 **NIC Buffer**")
                st.info(f"**Estimated Time:** `{((transfer_time_s * 1000) + (tcp_latency_us / 1000)):.2f} ms`")
                st.warning(f"**CPU Overhead:** `{tcp_cpu_overhead_ms:.2f} ms` (High)")
                st.error("**Data Copies:** 2 (Inefficient)")

            with col2:
                st.markdown("#### High-Speed RDMA Path")
                st.markdown("--- ")
                st.markdown("1. 💾 **App Memory (GPU)** → `Direct Hardware Access` → 2. 🚀 **NIC Buffer**")
                st.markdown("*(Kernel Bypassed)*")
                st.success(f"**Estimated Time:** `{((transfer_time_s * 1000) + (rdma_latency_us / 1000)):.2f} ms`")
                st.success(f"**CPU Overhead:** `{rdma_cpu_overhead_ms:.2f} ms` (Minimal)")
                st.success("**Data Copies:** 0 (Zero-Copy)")

        st.markdown("---")
        st.subheader("Understanding RDMA in AI Architectures")
        with st.expander("What is RDMA? The Core Idea of Kernel Bypass"):
            st.markdown("**Remote Direct Memory Access (RDMA)** allows a network card (NIC) to directly access the memory of another computer without involving the CPU or Operating System (OS) of either. This **kernel bypass** is the key to its performance.")
            st.image("https://i.imgur.com/3Yt8BZy.png", caption="RDMA bypasses the CPU and OS, enabling direct memory-to-memory communication.")

        with st.expander("Why is RDMA Critical for Distributed AI Training?"):
            st.markdown("In distributed training, the bottleneck is synchronizing model gradients across all GPUs. RDMA allows one GPU's memory to be directly accessed by another's network card, enabling high-speed, low-latency communication that keeps expensive GPUs fully utilized and drastically reduces training time.")

    with sub_tab_cdn:
        st.subheader("Simulating Cloudflare's 'Pay Per Crawl' for AI Bots")
        publisher_price = st.slider("Publisher's Price per Crawl ($)", 0.10, 5.00, 0.50, 0.05, key='cdn_price_slider')
        crawler_bid = st.number_input("AI Crawler's Max Bid ($)", min_value=0.0, value=0.25, step=0.05, format="%.2f", key='cdn_bid_input')

        if st.button("Attempt to Crawl Content", key='cdn_button'):
            if crawler_bid >= publisher_price:
                st.success(f"**HTTP 200 OK** - Request Successful! Bid of ${crawler_bid:.2f} was sufficient.")
                st.code(f"crawler-charged: USD {publisher_price:.2f}", language="http")
            else:
                st.error(f"**HTTP 402 Payment Required** - Bid of ${crawler_bid:.2f} was too low.")
                st.code(f"crawler-price: USD {publisher_price:.2f}", language="http")

# --- Footer ---
st.markdown("---")
st.markdown("<div style='text-align:center; font-size:0.85em; color:grey;'>© 2025 TrendTrackr | Created by <b>Shivakant Dubey</b> | <a href='https://www.linkedin.com/in/shivapunit/' target='_blank'>Connect on LinkedIn</a></div>", unsafe_allow_html=True)
