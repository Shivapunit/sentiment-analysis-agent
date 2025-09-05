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
    page_icon="📈", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- VADER Sentiment Analysis Setup ---
analyzer = SentimentIntensityAnalyzer()

# --- HELPER FUNCTIONS ---
@st.cache_data(ttl=3600)
def fetch_news(query, api_key):
    """Fetches news using the NewsAPI.org service and caches the results."""
    if not api_key: # <-- Check if the API key exists
        return "Error: News API key is not configured in the app's secrets."
    try:
        newsapi = NewsApiClient(api_key=api_key)
        all_articles = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=100)
    except Exception as e:
        return f"Error fetching news. Please check the configured API key. Details: {e}"
    if not all_articles['articles']:
        return "No articles found for this query."
    return [{'title': article['title'], 'publishedAt': article['publishedAt']} for article in all_articles['articles']]

# (All other helper functions like analyze_sentiment, generate_wordcloud, etc. stay the same)
def analyze_sentiment(df):
    df['sentiment_scores'] = df['title'].apply(lambda title: analyzer.polarity_scores(title))
    df['compound'] = df['sentiment_scores'].apply(lambda score_dict: score_dict['compound'])
    def classify_sentiment(compound_score):
        if compound_score >= 0.05: return 'Positive'
        elif compound_score <= -0.05: return 'Negative'
        else: return 'Neutral'
    df['sentiment'] = df['compound'].apply(classify_sentiment)
    return df
def generate_wordcloud(text_series, title):
    text = ' '.join(text for text in text_series)
    if not text: return None
    wordcloud = WordCloud(width=800, height=400, background_color=None, mode="RGBA", colormap='viridis').generate(text)
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.set_title(title, fontsize=20, color='white')
    ax.axis('off')
    fig.patch.set_alpha(0.0)
    return fig
def generate_html_table(df):
    sentiment_colors = {'Positive': '#28a745', 'Negative': '#dc3545', 'Neutral': 'grey'}
    html = """<style>.styled-table{width:100%;border-collapse:collapse;}.styled-table th,.styled-table td{padding:12px 15px;text-align:left;}.styled-table th{background-color:#1C355A;color:#FFFFFF;border-bottom:2px solid #61dafb;}.styled-table tr{border-bottom:1px solid #1C355A;}</style><table class="styled-table"><thead><tr><th>Title</th><th>Sentiment</th></tr></thead><tbody>"""
    for _, row in df.iterrows():
        title = row['title']
        sentiment = row['sentiment']
        color = sentiment_colors.get(sentiment, '#FFFFFF')
        html += f"<tr><td>{title}</td><td style='color: {color}; font-weight: bold;'>{sentiment}</td></tr>"
    html += "</tbody></table>"
    return html

# --- Streamlit App Layout ---

# --- Sidebar ---
st.sidebar.image("https://i.imgur.com/8Go2i0s.png", width=100) # <-- Added a simple logo
st.sidebar.header("📈 TrendTrackr")
st.sidebar.markdown("---")
st.sidebar.subheader("How It Works")
st.sidebar.info(
    "This dashboard performs real-time sentiment analysis. It fetches news headlines, analyzes each one using the VADER model, and visualizes the aggregated sentiment, including trends over time."
)
if st.sidebar.button('Clear Cache'):
    st.cache_data.clear()
    st.success("Cache cleared!")
st.sidebar.markdown("---")
st.sidebar.write("Built with passion by Saikat Mondal.")

# --- Main Page ---
st.title("📈 TrendTrackr: Real-Time Sentiment Dashboard")
st.markdown("Analyze public sentiment and track trends for any topic. Enter a query to begin.")

# --- Input Section ---
with st.container(border=True):
    search_query = st.text_input("Enter a brand, topic, or keyword", "India")
    if st.button("Analyze Sentiment", type="primary"):
        # <-- REMOVED the API key input field ---
        if not search_query:
            st.warning("Please enter a search query.")
        else:
            with st.spinner(f"Fetching and analyzing news for '{search_query}'..."):
                # --- THIS IS THE KEY CHANGE ---
                # It now gets the key from Streamlit's secure secrets storage
                api_key = st.secrets.get("NEWS_API_KEY")
                
                headlines_data = fetch_news(search_query, api_key)
                
                if isinstance(headlines_data, str):
                    st.error(headlines_data)
                else:
                    df = pd.DataFrame(headlines_data)
                    df = analyze_sentiment(df)
                    st.success(f"Analysis complete! Found {len(df)} articles.")
                    st.markdown("---")
                    
                    # (The rest of the dashboard display code is the same)
                    total_headlines = len(df)
                    overall_sentiment_score = df['compound'].mean()
                    sentiment_label = "Positive" if overall_sentiment_score >= 0.05 else "Negative" if overall_sentiment_score <= -0.05 else "Neutral"
                    col1, col2, col3 = st.columns(3)
                    col1.metric("📰 Total Headlines", f"{total_headlines}")
                    col2.metric("🧠 Overall Sentiment", sentiment_label)
                    col3.metric("📈 Avg. Score", f"{overall_sentiment_score:.2f}")
                    tab1, tab2, tab3, tab4 = st.tabs(["📊 Sentiment Breakdown", "📈 Sentiment Over Time", "☁️ Word Clouds", "📰 Recent Mentions"])
                    with tab1:
                        st.subheader("Sentiment Distribution")
                        sentiment_counts = df['sentiment'].value_counts()
                        fig_pie = px.pie(sentiment_counts, values=sentiment_counts.values, names=sentiment_counts.index, color=sentiment_counts.index, color_discrete_map={'Positive':'#28a745', 'Negative':'#dc3545', 'Neutral':'#6c757d'})
                        fig_pie.update_layout(legend_title_text='Sentiment', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
                        st.plotly_chart(fig_pie, use_container_width=True)
                    with tab2:
                        st.subheader("Sentiment Trend")
                        df['date'] = pd.to_datetime(df['publishedAt']).dt.date
                        sentiment_by_day = df.groupby('date')['compound'].mean().reset_index()
                        fig_line = px.line(sentiment_by_day, x='date', y='compound', title='Average Sentiment Score Per Day', markers=True)
                        fig_line.update_layout(xaxis_title='Date', yaxis_title='Average Sentiment Score', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
                        st.plotly_chart(fig_line, use_container_width=True)
                    with tab3:
                        st.subheader("Most Frequent Words")
                        col_wc1, col_wc2 = st.columns(2)
                        with col_wc1:
                            positive_text = df[df['sentiment'] == 'Positive']['title']
                            fig_pos = generate_wordcloud(positive_text, "Positive Words")
                            if fig_pos: st.pyplot(fig_pos, use_container_width=True)
                            else: st.write("No positive words found.")
                        with col_wc2:
                            negative_text = df[df['sentiment'] == 'Negative']['title']
                            fig_neg = generate_wordcloud(negative_text, "Negative Words")
                            if fig_neg: st.pyplot(fig_neg, use_container_width=True)
                            else: st.write("No negative words found.")
                    with tab4:
                        st.subheader("Analyzed Headlines")
                        html_table = generate_html_table(df[['title', 'sentiment']])
                        st.markdown(f'<div style="height: 400px; overflow-y: auto;">{html_table}</div>', unsafe_allow_html=True)
