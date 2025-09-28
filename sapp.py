import streamlit as st
import pandas as pd
import plotly.express as px
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from newsapi import NewsApiClient

# --- Page Configuration ---
st.set_page_config(
    page_title="TrendTrackr - Sentiment Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- VADER Sentiment Setup ---
analyzer = SentimentIntensityAnalyzer()

# --- Caching ---
@st.cache_data(ttl=3600)
def fetch_news(query, api_key):
    newsapi = NewsApiClient(api_key=api_key)
    try:
        all_articles = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=100)
        articles = all_articles.get('articles', [])
        if not articles:
            return None
        return [{'title': a.get('title', ''), 'publishedAt': a.get('publishedAt', '')} for a in articles if a.get('title')]
    except Exception as e:
        raise RuntimeError(f"NewsAPI error: {e}")

@st.cache_data(ttl=3600)
def analyze_sentiment(df):
    df['sentiment_scores'] = df['title'].apply(lambda t: analyzer.polarity_scores(t))
    df['compound'] = df['sentiment_scores'].apply(lambda s: s['compound'])
    df['sentiment'] = df['compound'].apply(lambda c: 'Positive' if c >= 0.05 else 'Negative' if c <= -0.05 else 'Neutral')
    return df

def generate_wordcloud(text_series):
    text = ' '.join(text_series)
    if not text: return None
    wc = WordCloud(width=800, height=400, background_color='white', colormap='plasma').generate(text)
    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    fig.patch.set_alpha(0.0)
    return fig

def generate_html_table(df):
    colors = {'Positive': '#2ecc71', 'Negative': '#e74c3c', 'Neutral': '#95a5a6'}
    html = """<style>.styled-table{width:100%;border-collapse:collapse;font-family:Arial;}.styled-table th,.styled-table td{padding:10px;text-align:left;}.styled-table th{background-color:#34495e;color:#ecf0f1;}.styled-table tr{border-bottom:1px solid #bdc3c7;}</style><table class="styled-table"><thead><tr><th>Title</th><th>Sentiment</th></tr></thead><tbody>"""
    for _, row in df.iterrows():
        html += f"<tr><td>{row['title']}</td><td style='color:{colors[row['sentiment']]};font-weight:bold;'>{row['sentiment']}</td></tr>"
    html += "</tbody></table>"
    return html

# --- Sidebar ---
st.sidebar.header("📈 TrendTrackr")
st.sidebar.caption("Tracking trends, decoding sentiment.")
st.sidebar.markdown("---")
with st.sidebar.expander("ℹ️ About & Data Source", expanded=True):
    st.markdown("""
        - **About:** Analyze sentiment of recent news headlines for any topic.
        - **Data:** Real-time headlines from [NewsAPI.org](https://newsapi.org).
        - **Model:** VADER Sentiment Analysis.
    """)
if st.sidebar.button('Clear Cache'):
    st.cache_data.clear()
    st.success("Cache cleared!")

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

# --- Main Header ---
st.title("🧠 TrendTrackr: Real-Time Sentiment Dashboard")
st.markdown("Analyze public sentiment and track trends for any topic. Enter a query below to begin.")

# --- Provider Dropdown ---
providers = ["General", "AWS", "Azure", "Cloudflare", "Fastly", "Google Cloud"]
selected_provider = st.selectbox("Choose Provider", providers)
default_query = selected_provider if selected_provider != "General" else ""

# --- Search Form ---
with st.form(key='search_form'):
    search_query = st.text_input("Search Query", value=default_query, placeholder="e.g., Apple, Climate Change, The latest Marvel movie")
    submitted = st.form_submit_button("Analyze Sentiment")

# --- API Key Retrieval with Fallback ---
api_key = st.secrets.get("NEWS_API_KEY", "0ac47642d2d8408e9bf075473df6cbc7")
if api_key == "0ac47642d2d8408e9bf075473df6cbc7":
    st.warning("Using fallback API key. Consider configuring secrets for security.")

# --- Sentiment Analysis ---
if submitted:
    if not search_query:
        st.warning("Please enter a search query.")
    else:
        with st.spinner("Brewing insights... ☕"):
            try:
                articles = fetch_news(search_query, api_key)
                if not articles:
                    st.warning("No articles found for this query. Try a different topic.")
                else:
                    df = pd.DataFrame(articles)
                    df = analyze_sentiment(df)
                    st.session_state['results_df'] = df
                    st.session_state['search_query'] = search_query
            except Exception as e:
                st.error(str(e))

# --- Dashboard Display ---
if 'results_df' in st.session_state:
    df = st.session_state['results_df']
    search_query = st.session_state['search_query']

    st.success(f"Analysis complete! Found {len(df)} articles.")
    st.markdown("---")

    # --- Key Metrics ---
    avg_score = df['compound'].mean()
    sentiment_label = "Positive" if avg_score >= 0.05 else "Negative" if avg_score <= -0.05 else "Neutral"
    col1, col2, col3 = st.columns(3)
    col1.metric("📰 Total Headlines", len(df))
    col2.metric("💬 Overall Sentiment", sentiment_label)
    col3.metric("📈 Avg. Score", f"{avg_score:.2f}")

    # --- Tabs ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Sentiment Breakdown", "📈 Sentiment Over Time", "☁️ Word Clouds",
        "📥 Download & Mentions", "📉 Confidence Histogram"
    ])

    with tab1:
        st.subheader("Sentiment Distribution")
        sentiment_counts = df['sentiment'].value_counts()
        fig_pie = px.pie(sentiment_counts, values=sentiment_counts.values, names=sentiment_counts.index,
                         color=sentiment_counts.index,
                         color_discrete_map={'Positive': '#2ecc71', 'Negative': '#e74c3c', 'Neutral': '#95a5a6'})
        fig_pie.update_layout(paper_bgcolor='white', plot_bgcolor='white')
        st.plotly_chart(fig_pie, use_container_width=True)

    with tab2:
        st.subheader("Sentiment Trend")
        df['date'] = pd.to_datetime(df['publishedAt']).dt.date
        sentiment_by_day = df.groupby('date')['compound'].mean().reset_index()
        fig_line = px.line(sentiment_by_day, x='date', y='compound', markers=True)
        fig_line.update_layout(xaxis_title='Date', yaxis_title='Avg. Sentiment Score',
                               paper_bgcolor='white', plot_bgcolor='white')
        st.plotly_chart(fig_line, use_container_width=True)

    with tab3:
        st.subheader("Most Frequent Words")
        col_wc1, col_wc2 = st.columns(2)
        with col_wc1:
            st.markdown("**Positive Words**")
            fig_pos = generate_wordcloud(df[df['sentiment'] == 'Positive']['title'])
            if fig_pos: st.pyplot(fig_pos, use_container_width=True)
            else: st.write("No positive words found.")
        with col_wc2:
            st.markdown("**Negative Words**")
            fig_neg = generate_wordcloud(df[df['sentiment'] == 'Negative']['title'])
            if fig_neg: st.pyplot(fig_neg, use_container_width=True)
            else: st.write("No negative words found.")

    with tab4:
        st.subheader("Analyzed Headlines")
        csv = df[['title', 'sentiment', 'compound']].to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", data=csv, file_name=f"{search_query}_sentiment.csv", mime='text/csv')
        html_table = generate_html_table(df[['title', 'sentiment']])
        st.markdown(f'<div style="height: 400px; overflow-y: auto;">{html_table}</div>', unsafe_allow_html=True)

    with tab5:
        st.subheader("Sentiment Confidence Histogram")
        fig_hist = px.histogram(df, x='compound', nbins=20, title='Distribution of Sentiment Scores')
        fig_hist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_hist, use_container_width=True)