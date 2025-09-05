📈 TrendTrackr: Real-Time Sentiment Analysis Dashboard
A web-based dashboard that fetches recent news headlines for any user-provided query, performs sentiment analysis, and visualizes the results and historical trends in a clean, interactive, and mobile-friendly interface.

Live Demo GIF
(Replace this text and the image link below with a GIF of your running application. Use a free tool like LICEcap or ScreenToGif.)

✨ Features
Dynamic Data Fetching: Utilizes the NewsAPI to pull the latest 100 headlines for any topic.

Advanced Sentiment Analysis: Employs the VADER model to classify headlines as Positive, Negative, or Neutral.

Time-Series Analysis: Plots the average sentiment score per day on an interactive line chart to reveal trends over time.

Efficient Caching: Implemented @st.cache_data to cache API results for one hour, with a manual "Clear Cache" button for data freshness.

Interactive Dashboard: A polished UI with a custom theme (light/dark mode supported), organized into clear tabs for an intuitive user experience.

Rich Visualizations:

Key performance metrics (Total Headlines, Overall Sentiment, Average Score).

An interactive pie chart for sentiment distribution.

Insightful word clouds for positive and negative keywords.

A custom-styled, scrollable HTML table for detailed results.

User-Friendly Interface: Includes a professional header, placeholder examples, and responds to the "Enter" key for submission.

🛠️ Tech Stack
Framework: Streamlit

Data Source: NewsAPI.org

Sentiment Analysis: VADER (Valence Aware Dictionary and sEntiment Reasoner)

Visualizations: Plotly Express, WordCloud, Matplotlib

Core Libraries: Pandas

🧠 Challenges & Solutions
Developing this application presented a significant environmental challenge that required deep troubleshooting and creative problem-solving.

The Problem: A persistent and critical ImportError: DLL load failed originating from the pyarrow library. This error crashed the application whenever a DataFrame was displayed.

The Solution:

Initial Troubleshooting: Standard debugging steps, such as reinstalling libraries and creating a new virtual environment, were unsuccessful.

System-Level Fixes: The investigation led to installing system-wide dependencies like the Microsoft C++ Redistributable.

Python Versioning: To rule out version conflicts, the entire project was migrated from Python 3.12 to the more stable Python 3.11 in a completely new, isolated environment.

The Final Workaround: When the error surprisingly persisted, it confirmed a deep, unusual incompatibility with the local system. I engineered a robust solution by creating a custom HTML table renderer. This function dynamically generates a styled HTML table from the pandas DataFrame and displays it within a scrollable div. This creative workaround completely bypassed the problematic pyarrow dependency, restoring full functionality and a polished look to the dashboard.

This experience was a valuable lesson in debugging complex environment issues and the importance of having alternative implementation strategies to ensure project delivery.

## 💡 Known Limitations & Future Improvements
Relevance Filtering:
The current version uses a keyword-based search via the NewsAPI. This can sometimes lead to irrelevant results (e.g., searching for "Apple" the company may return articles about the fruit).

To create a truly state-of-the-art relevance filter, the next step would be to implement a sentence embedding model (like Sentence-BERT). This advanced process would involve:

Fetching a broad set of articles from the API.

Generating vector embeddings for the user's query and for each headline.

Calculating the cosine similarity between the query and each headline.

Displaying only the top results with the highest similarity scores, ensuring a much higher degree of contextual relevance.

This feature was scoped out of the current project to focus on the core dashboard requirements but represents a clear path for future enhancement.

🚀 Local Setup and Execution
Clone the Repository

git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
cd YOUR_REPOSITORY_NAME

Create and Activate a Virtual Environment
We recommend using Python 3.11 for maximum compatibility.

py -3.11 -m venv venv
venv\Scripts\activate

Install Dependencies

pip install -r requirements.txt

Set Up Your API Key

Get a free API key from newsapi.org.

This project is designed to be deployed on Streamlit Community Cloud, where the API key should be stored in the Secrets manager.

Run the Application

streamlit run sapp.py

The application will now be running and accessible at http://localhost:8501.
