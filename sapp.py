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
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- VADER Sentiment Analysis Setup ---
analyzer = SentimentIntensityAnalyzer()

# --- HELPER FUNCTIONS ---
@st.cache_data(ttl=3600)
def fetch_news(query, api_key):
    if not api_key:
        return "Error: News API key is not configured in the app's secrets."
    try:
        newsapi = NewsApiClient(api_key=api_key)
        all_articles = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=100)
    except Exception as e:
        return f"Error fetching news. Please check the configured API key. Details: {e}"
    if not all_articles['articles']:
        return "No articles found for this query."
    return [{'title': article['title'], 'publishedAt': article['publishedAt']} for article in all_articles['articles']]

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

# --- UI Function for the Dashboard ---
def display_dashboard(df, search_query):
    """Takes a DataFrame and displays the full sentiment analysis dashboard."""
    
    st.success(f"Analysis complete! Found {len(df)} articles.")
    st.markdown("---")
    
    total_headlines = len(df)
    overall_sentiment_score = df['compound'].mean()
    sentiment_label = "Positive" if overall_sentiment_score >= 0.05 else "Negative" if overall_sentiment_score <= -0.05 else "Neutral"
    
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.markdown(f"<div style='text-align: center;'><span style='font-size: 1.2em; color: grey;'>📰 Total Headlines</span><br><b style='font-size: 2.5em;'>{total_headlines}</b></div>", unsafe_allow_html=True)
    with col2:
        with st.container(border=True):
            st.markdown(f"<div style='text-align: center;'><span style='font-size: 1.2em; color: grey;'>💬 Overall Sentiment</span><br><b style='font-size: 2.5em;'>{sentiment_label}</b></div>", unsafe_allow_html=True)
    with col3:
        with st.container(border=True):
            st.markdown(f"<div style='text-align: center;'><span style='font-size: 1.2em; color: grey;'>📈 Avg. Score</span><br><b style='font-size: 2.5em;'>{overall_sentiment_score:.2f}</b></div>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Sentiment Breakdown", "📈 Sentiment Over Time", "☁️ Word Clouds", "📰 Recent Mentions"])
    
    # --- THIS IS THE CORRECTED SECTION ---
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
            st.markdown("<h3 style='text-align: center;'>Positive Words</h3>", unsafe_allow_html=True)
            positive_text = df[df['sentiment'] == 'Positive']['title']
            fig_pos = generate_wordcloud(positive_text, "")
            if fig_pos: st.pyplot(fig_pos, use_container_width=True)
            else: st.write("No positive words found.")
        with col_wc2:
            st.markdown("<h3 style='text-align: center;'>Negative Words</h3>", unsafe_allow_html=True)
            negative_text = df[df['sentiment'] == 'Negative']['title']
            fig_neg = generate_wordcloud(negative_text, "")
            if fig_neg: st.pyplot(fig_neg, use_container_width=True)
            else: st.write("No negative words found.")

    with tab4:
        st.subheader("Analyzed Headlines")
        csv = df[['title', 'sentiment', 'compound']].to_csv(index=False).encode('utf-8')
        st.download_button(
           label="📥 Download Results as CSV",
           data=csv,
           file_name=f'sentiment_analysis_{search_query.replace(" ", "_")}.csv',
           mime='text/csv',
        )
        st.markdown("---")
        html_table = generate_html_table(df[['title', 'sentiment']])
        st.markdown(f'<div style="height: 400px; overflow-y: auto;">{html_table}</div>', unsafe_allow_html=True)

# --- Streamlit App Layout ---
st.sidebar.image("assets/logo.png", width=100)
st.sidebar.caption("Tracking trends, decoding sentiment.")
st.sidebar.header("📈 TrendTrackr")
st.sidebar.markdown("---")
with st.sidebar.expander("ℹ️ About & Data Source", expanded=True):
    st.markdown("""
        - **About:** This app analyzes the sentiment of recent news headlines for any topic.
        - **Data:** Real-time headlines from [NewsAPI.org](https://newsAPI.org/).
        - **Model:** Sentiment analysis by VADER.
    """)
if st.sidebar.button('Clear Cache'):
    st.cache_data.clear()
    st.success("Cache cleared!")
st.sidebar.markdown("---")
st.sidebar.write("Built with passion by Saikat.")

col1_main, col2_main = st.columns([0.1, 0.9])
with col1_main:
    st.image("assets/logo.png", width=80)
with col2_main:
    st.title("TrendTrackr: Real-Time Sentiment Dashboard")
st.markdown("Analyze public sentiment and track trends for any topic. Enter a query below to begin.")

with st.form(key='search_form'):
    search_query = st.text_input("Search Query", placeholder="e.g., Apple, Climate Change, The latest Marvel movie")
    submitted = st.form_submit_button("Analyze Sentiment")

if submitted:
    if not search_query:
        st.warning("Please enter a search query.")
    else:
        api_key = st.secrets.get("NEWS_API_KEY")
        if not api_key:
            st.error("News API key is not configured. Please contact the app administrator.")
        else:
            with st.spinner("Brewing insights... ☕ This may take a moment."):
                headlines_data = fetch_news(search_query, api_key)
                if isinstance(headlines_data, str):
                    st.error(headlines_data)
                else:
                    df = pd.DataFrame(headlines_data)
                    df = analyze_sentiment(df)
                    st.session_state['results_df'] = df
                    st.session_state['search_query'] = search_query

if 'results_df' in st.session_state:
    display_dashboard(st.session_state['results_df'], st.session_state['search_query'])
