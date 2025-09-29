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
st.sidebar.caption("AI-Powered Dashboard")
st.sidebar.markdown("---")
with st.sidebar.expander("ℹ️ About & Data Source", expanded=True):
    st.markdown("""
        - **News Sentiment:** Live data from [NewsAPI.org](https://newsapi.org)
        - **Amazon & G2 Reviews:** Mock data for demonstration
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

# --- Core Functions / Tools ---
analyzer = SentimentIntensityAnalyzer()

@st.cache_data(ttl=3600)
def analyze_sentiment(texts):
    df = pd.DataFrame(texts, columns=["text"])
    df["compound"] = df["text"].apply(lambda t: analyzer.polarity_scores(t)["compound"])
    df["sentiment"] = df["compound"].apply(lambda c: "Positive" if c >= 0.05 else "Negative" if c <= -0.05 else "Neutral")
    return df

@st.cache_data(ttl=3600)
def generate_wordcloud(text_series, colormap='plasma'):
    text = ' '.join(text for text in text_series if text and isinstance(text, str))
    if not text:
        return None
    wc = WordCloud(width=1200, height=600, background_color='white', colormap=colormap, max_words=150, contour_width=3, contour_color='steelblue').generate(text)
    return wc

@st.cache_data(ttl=3600)
def fetch_news(query):
    api_key = st.secrets.get("NEWS_API_KEY", "0ac47642d2d8408e9bf075473df6cbc7")
    newsapi = NewsApiClient(api_key=api_key)
    try:
        articles = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=100).get('articles', [])
        return articles
    except Exception as e:
        return {"error": str(e)}

# --- Main Dashboard UI ---
st.title("📈 TrendTrackr: AI-Powered Dashboard")

tab_news, tab_reviews, tab_research = st.tabs(["🧠 News Sentiment", "🛒 Amazon & G2 Reviews (DEMO)", "🔬 Research Projects"])

# --- News Sentiment Tab (Restored & Fixed) ---
with tab_news:
    st.header("Analyze Public Sentiment from News Headlines")
    
    providers = ["General", "AWS", "Azure", "Cloudflare", "Fastly", "Google Cloud"]
    selected_provider = st.selectbox("Choose a Provider (Optional)", providers, key='news_provider_select')
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
                df_sentiment = analyze_sentiment(df["text"].dropna())
                df = pd.concat([df.reset_index(drop=True), df_sentiment.reset_index(drop=True)], axis=1)
                st.session_state['news_df'] = df

    if 'news_df' in st.session_state:
        df = st.session_state['news_df']
        st.success(f"**Analysis Complete:** Found {len(df)} articles.")
        
        avg_score = df["compound"].mean()
        sentiment_label = "Positive" if avg_score >= 0.05 else "Negative" if avg_score <= -0.05 else "Neutral"
        col1, col2, col3 = st.columns(3)
        col1.metric("📰 Total Headlines", len(df))
        col2.metric("💬 Overall Sentiment", sentiment_label)
        col3.metric("📈 Avg. Score", f"{avg_score:.2f}")

        t1, t2, t3 = st.tabs(["📊 Distribution", "📈 Trend", "☁️ Word Cloud"])
        with t1:
            sentiment_counts = df["sentiment"].value_counts()
            fig_pie = px.pie(sentiment_counts, values=sentiment_counts.values, names=sentiment_counts.index,
                             color=sentiment_counts.index, color_discrete_map={'Positive': '#2ecc71', 'Negative': '#e74c3c', 'Neutral': '#95a5a6'})
            st.plotly_chart(fig_pie, use_container_width=True)
        with t2:
            df["publishedAt"] = pd.to_datetime(df["publishedAt"])
            df["date"] = df["publishedAt"].dt.date
            sentiment_by_day = df.groupby("date")["compound"].mean().reset_index()
            fig_line = px.line(sentiment_by_day, x="date", y="compound", markers=True, title='Sentiment Trend Over Time')
            st.plotly_chart(fig_line, use_container_width=True)
        with t3:
            wordcloud = generate_wordcloud(df['text'])
            if wordcloud:
                st.image(wordcloud.to_array(), caption='Most Frequent Words', use_container_width=True)
            else:
                st.write("Not enough data to generate a word cloud.")

# --- Amazon & G2 Reviews Tab (FIXED: Interactive Demo) ---
with tab_reviews:
    st.header("Analyze Product and Vendor Reviews")
    sub_tab_amazon, sub_tab_g2 = st.tabs(["📦 Amazon Product Reviews", "🏢 G2 Vendor Search"])

    with sub_tab_amazon:
        st.subheader("Demo: Sentiment Analysis of a Smartwatch")
        if st.button("Run Amazon Review Analysis", key='amazon_button'):
            mock_reviews = [
                "Absolutely love it! The battery life is incredible and it tracks my workouts perfectly.",
                "A total waste of money. The screen scratched on the first day and it constantly disconnects from my phone.",
                "It's an okay watch. Does the basics but nothing special. The interface is a bit clunky.",
                "Best tech purchase of the year! Seamless integration with all my apps.",
                "I had to return it. The heart rate monitor was wildly inaccurate.",
                "The design is sleek and I get a lot of compliments on it.",
                "The software is buggy and the updates are infrequent. Disappointed.",
                "Five stars! Finally a smartwatch that delivers on its promises.",
                "Terrible customer support when I had an issue with the charger.",
                "It works as advertised, no complaints from me."
            ]
            with st.spinner("Analyzing mock reviews..."):
                df_reviews = analyze_sentiment(mock_reviews)
                st.session_state['amazon_df'] = df_reviews

        if 'amazon_df' in st.session_state:
            df = st.session_state['amazon_df']
            st.subheader("Analysis Results for 'The Innovate Smartwatch Series X'")
            avg_score = df['compound'].mean()
            sentiment_label = "Positive" if avg_score >= 0.05 else "Negative" if avg_score <= -0.05 else "Neutral"
            col1, col2, col3 = st.columns(3)
            col1.metric("⭐ Overall Sentiment", sentiment_label)
            col2.metric("📊 Average Score", f"{avg_score:.2f}")
            col3.metric("💬 Reviews Analyzed", len(df))
            col_pie, col_wc = st.columns(2)
            with col_pie:
                st.markdown("**Sentiment Distribution**")
                sentiment_counts = df['sentiment'].value_counts()
                fig_pie = px.pie(sentiment_counts, values=sentiment_counts.values, names=sentiment_counts.index, color=sentiment_counts.index, color_discrete_map={'Positive': '#2ecc71', 'Negative': '#e74c3c', 'Neutral': '#95a5a6'})
                st.plotly_chart(fig_pie, use_container_width=True)
            with col_wc:
                st.markdown("**Positive vs. Negative Keywords**")
                pos_text = ' '.join(df[df['sentiment'] == 'Positive']['text'])
                neg_text = ' '.join(df[df['sentiment'] == 'Negative']['text'])
                if pos_text:
                    st.image(generate_wordcloud(pos_text, colormap='Greens').to_array(), caption='Positive Words', use_container_width=True)
                if neg_text:
                    st.image(generate_wordcloud(neg_text, colormap='Reds').to_array(), caption='Negative Words', use_container_width=True)
            st.markdown("**Detailed Review Analysis**")
            st.dataframe(df)

    with sub_tab_g2:
        st.subheader("Demo: G2 Vendor Search")
        if st.button("Run G2 Vendor Search", key='g2_button'):
            mock_vendors = [
                {"name": "ConnectSphere CRM", "category": "CRM", "score": 4.7, "description": "An all-in-one CRM platform for growing businesses.", "icon": "🌐"},
                {"name": "SalesLeap", "category": "Sales Intelligence", "score": 4.5, "description": "Provides actionable B2B contact and company data.", "icon": "🚀"},
                {"name": "Supportify Desk", "category": "Help Desk Software", "score": 4.6, "description": "Streamlines customer support with a unified inbox.", "icon": "🎧"}
            ]
            st.session_state['g2_vendors'] = mock_vendors

        if 'g2_vendors' in st.session_state:
            st.markdown("**Matching Vendors Found:**")
            for vendor in st.session_state['g2_vendors']:
                with st.container():
                    st.markdown(f"### {vendor['icon']} {vendor['name']}")
                    st.markdown(f"**Category:** {vendor['category']} | **G2 Score:** {vendor['score']}/5.0")
                    st.write(vendor['description'])
                    st.markdown("---")

# --- Research Projects Tab (Restored & Fixed) ---
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
