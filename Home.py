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
st.sidebar.caption("An Agentic AI-Powered Dashboard")
st.sidebar.markdown("---")
with st.sidebar.expander("ℹ️ About & Data Source", expanded=True):
    st.markdown("""
        - **News Sentiment:** Headlines from [NewsAPI.org](https://newsapi.org)
        - **Amazon Reviews:** Product data via RapidAPI
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

# --- AGENT TOOLS (MCP) ---
# These functions act as our specialized 'tools' in the Multi-Component Pipeline.

@st.cache_data(ttl=3600)
def tool_fetch_news(query):
    """Agent Tool: Fetches news from NewsAPI."""
    newsapi = NewsApiClient(api_key=st.secrets.get("NEWS_API_KEY", "0ac47642d2d8408e9bf075473df6cbc7"))
    try:
        articles = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=100).get('articles', [])
        return [{'title': a.get('title', ''), 'publishedAt': a.get('publishedAt', '')} for a in articles if a.get('title')]
    except Exception as e:
        return {"error": str(e)}

@st.cache_data(ttl=3600)
def tool_fetch_amazon_product(asin, country="US"):
    """Agent Tool: Fetches product details from Amazon via RapidAPI."""
    url = "https://real-time-amazon-data.p.rapidapi.com/product-details"
    headers = {"x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com", "x-rapidapi-key": st.secrets.get("RAPIDAPI_KEY")}
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

@st.cache_data(ttl=3600)
def tool_analyze_sentiment(texts):
    """Agent Tool: Analyzes sentiment using VADER."""
    analyzer = SentimentIntensityAnalyzer()
    df = pd.DataFrame(texts, columns=["text"])
    df["compound"] = df["text"].apply(lambda t: analyzer.polarity_scores(t)["compound"])
    df["sentiment"] = df["compound"].apply(lambda c: "Positive" if c >= 0.05 else "Negative" if c <= -0.05 else "Neutral")
    return df

@st.cache_data(ttl=3600)
def tool_generate_wordcloud(text_series):
    """Agent Tool: Generates a word cloud image."""
    text = ' '.join(text_series)
    if not text: return None
    wc = WordCloud(width=800, height=400, background_color='white', colormap='plasma').generate(text)
    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    return fig

# --- Main Dashboard UI ---
st.title("📈 TrendTrackr: An Agentic AI-Powered Dashboard")

tab_news, tab_reviews, tab_research = st.tabs(["🧠 News Sentiment", "🛒 Amazon Reviews", "🔬 Research Projects"])

# --- News Sentiment Tab --- 
with tab_news:
    st.header("Analyze Public Sentiment from News Headlines")
    
    with st.form(key='news_search_form'):
        search_query = st.text_input("Search Query", placeholder="e.g., Apple, Climate Change", key='news_query_input')
        submitted = st.form_submit_button("🚀 Run Agentic Workflow")

    if submitted:
        with st.status("🤖 **Orchestrator:** Running News Analysis Pipeline...", expanded=True) as status:
            st.write("🔍 **API Agent:** Fetching headlines from NewsAPI...")
            articles = tool_fetch_news(search_query)
            time.sleep(1)

            if isinstance(articles, dict) and "error" in articles:
                status.update(label="Workflow Failed!", state="error", expanded=True)
                st.error(articles["error"])
            elif not articles:
                status.update(label="Workflow Complete!", state="complete", expanded=False)
                st.warning("No articles found.")
            else:
                df = pd.DataFrame(articles)
                df["text"] = df["title"]
                
                st.write("🧠 **Sentiment Agent:** Analyzing sentiment of headlines...")
                df_sentiment = tool_analyze_sentiment(df[["text"]])
                df = pd.concat([df.reset_index(drop=True), df_sentiment.reset_index(drop=True)], axis=1)
                st.session_state['news_df'] = df
                time.sleep(1)

                status.update(label="Workflow Complete!", state="complete", expanded=False)

    if 'news_df' in st.session_state:
        df = st.session_state['news_df']
        st.success(f"**Analysis Complete:** Found {len(df)} articles.")
        # ... (UI for displaying results remains the same)

# --- Amazon Reviews Tab ---
with tab_reviews:
    st.header("Analyze Amazon Product Reviews")
    asin = st.text_input("Enter Amazon ASIN", value="B07ZPKBL9V", key='amazon_asin_input')
    
    if st.button("🚀 Run Agentic Workflow", key='amazon_button'):
        with st.status("🤖 **Orchestrator:** Running Amazon Review Pipeline...", expanded=True) as status:
            st.write("🔍 **API Agent:** Fetching product data from Amazon...")
            product = tool_fetch_amazon_product(asin)
            time.sleep(1)

            if "error" in product:
                status.update(label="Workflow Failed!", state="error", expanded=True)
                st.error(product["error"])
            elif not product['reviews']:
                status.update(label="Workflow Complete!", state="complete", expanded=False)
                st.info("No reviews available for this product.")
            else:
                st.write(f"**Found Product:** {product['title']}")
                st.write("🧠 **Sentiment Agent:** Analyzing review sentiment...")
                df_reviews = tool_analyze_sentiment(product['reviews'])
                time.sleep(1)

                st.write("☁️ **Visualization Agent:** Generating word cloud...")
                fig_wc = tool_generate_wordcloud(df_reviews['text'])
                time.sleep(1)

                status.update(label="Workflow Complete!", state="complete", expanded=False)

                st.dataframe(df_reviews)
                if fig_wc: st.pyplot(fig_wc)

# --- Research Projects Tab ---
with tab_research:
    # ... (RDMA and CDN simulation code remains the same)
    st.header("Research Projects & Simulations")
    sub_tab_rdma, sub_tab_cdn = st.tabs(["RDMA for AI Training", "CDN Paywall Analysis"])

    with sub_tab_rdma:
        st.subheader("Interactive Simulation: TCP/IP vs. RDMA")
        gradient_size_mb = st.slider("Gradient Size (MB)", 16, 1024, 128, key='rdma_slider')
        if st.button("▶️ Run Simulation", key='rdma_button'):
            # ... (simulation logic)
            pass

    with sub_tab_cdn:
        st.subheader("Simulating Cloudflare's 'Pay Per Crawl'")
        # ... (simulation logic)
        pass

# --- Footer ---
st.markdown("---")
st.markdown("<div style='text-align:center; font-size:0.85em; color:grey;'>© 2025 TrendTrackr | Created by <b>Shivakant Dubey</b> | <a href='https://www.linkedin.com/in/shivapunit/' target='_blank'>Connect on LinkedIn</a></div>", unsafe_allow_html=True)
