# 📈 Real-Time Sentiment Analysis Dashboard: Agentic AI

[![Streamlit App](https://sentiment-analysis-agent-vfwc6va3wnvgqquitfkp5s.streamlit.app/)

A web-based dashboard that fetches recent news headlines for any user-provided query, performs sentiment analysis, and visualizes the results and historical trends in a clean, interactive, and mobile-friendly interface.

---

### **Live Demo**

![Image](https://github.com/user-attachments/assets/d223b94f-ca05-45e2-a12e-5001a5257f5e)

---

## ✨ Features

-   **Multi-Page Application**: Structured for easy navigation between different analysis modules (e.g., Real-Time News Sentiment, Amazon/G2 Reviews).
-   **Dynamic Data Fetching**: Utilizes the NewsAPI to pull the latest 100 headlines for any topic.
-   **Advanced Sentiment Analysis**: Employs the VADER model to classify headlines as Positive, Negative, or Neutral.
-   **Time-Series Analysis**: Plots the average sentiment score per day on an interactive line chart to reveal trends over time.
-   **Efficient Caching**: Implemented `@st.cache_data` to cache API results for one hour, with a manual "Clear Cache" button for data freshness.
-   **Interactive Dashboard**: A polished UI with a custom theme (light/dark mode supported), organized into clear tabs for an intuitive user experience.
-   **Data Export**: Allows users to download the full analysis results as a CSV file.
-   **Rich Visualizations**:
    -   Custom-styled metric cards for key insights (Total Headlines, Overall Sentiment, Average Score).
    -   An interactive pie chart for sentiment distribution.
    -   Insightful word clouds for positive and negative keywords.
    -   A custom-styled, scrollable HTML table for detailed results.
-   **User-Friendly Interface**: Includes a professional header with a logo, placeholder examples, and responds to the "Enter" key for submission.

---

## 🛠️ Tech Stack

-   **Framework**: Streamlit
-   **Data Source**: NewsAPI.org
-   **Sentiment Analysis**: VADER (Valence Aware Dictionary and sEntiment Reasoner)
-   **Visualizations**: Plotly Express, WordCloud, Matplotlib
-   **Core Libraries**: Pandas

---

## 🧠 Challenges & Solutions

Developing this application presented a significant environmental challenge that required deep troubleshooting and creative problem-solving.

**The Problem:** A persistent and critical `ImportError: DLL load failed` originating from the `pyarrow` library. This error crashed the application whenever a DataFrame was displayed.

**The Solution:**
1.  **Initial Troubleshooting:** Standard debugging steps, such as reinstalling libraries and creating a new virtual environment, were unsuccessful.
2.  **System-Level Fixes:** The investigation led to installing system-wide dependencies like the Microsoft C++ Redistributable.
3.  **Python Versioning:** To rule out version conflicts, the entire project was migrated from Python 3.12 to the more stable Python 3.11 in a completely new, isolated environment.
4.  **The Final Workaround:** When the error surprisingly persisted, it confirmed a deep, unusual incompatibility with the local system. I engineered a robust solution by creating a **custom HTML table renderer**. This function dynamically generates a styled HTML table from the pandas DataFrame and displays it within a scrollable `div`. This creative workaround completely bypassed the problematic `pyarrow` dependency, restoring full functionality and a polished look to the dashboard.

This experience was a valuable lesson in debugging complex environment issues and the importance of having alternative implementation strategies to ensure project delivery.

---

### ## 💡 Known Limitations & Future Improvements

**Relevance Filtering:**
The current version uses a keyword-based search via the NewsAPI. This can sometimes lead to irrelevant results (e.g., searching for "Apple" the company may return articles about the fruit).

To create a truly state-of-the-art relevance filter, the next step would be to implement a **sentence embedding model** (like Sentence-BERT). This advanced process would involve:
1.  Fetching a broad set of articles from the API.
2.  Generating vector embeddings for the user's query and for each headline.
3.  Calculating the cosine similarity between the query and each headline.
4.  Displaying only the top results with the highest similarity scores, ensuring a much higher degree of contextual relevance.

This feature was scoped out of the current project to focus on the core dashboard requirements but represents a clear path for future enhancement.

---

## 🚀 Local Setup and Execution

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/CoderSaikat345/sentiment-analysis-dashboard.git](https://github.com/CoderSaikat345/sentiment-analysis-dashboard.git)
    cd sentiment-analysis-dashboard
    ```

2.  **Create and Activate a Virtual Environment**
    *We recommend using Python 3.11 for maximum compatibility.*
    ```bash
    py -3.11 -m venv venv
    venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Your API Key**
    - Get a free API key from [newsapi.org](https://newsapi.org/).
    - This project is designed to be deployed on Streamlit Community Cloud, where the API key should be stored in the Secrets manager.
    - For local development, create a `.streamlit/secrets.toml` file in your project root and add your API key:
      ```toml
      NEWS_API_KEY = "your_news_api_key_here"
      ```

5.  **Run the Application**
    ```bash
    streamlit run Home.py
    ```
The application will now be running and accessible at `http://localhost:8501`.

---

## 👨‍💻 About the Creator

This project was developed by **Shivakant Dubey**.

Feel free to connect with me and follow my work:
🔗 [LinkedIn Profile](https://www.linkedin.com/in/shivapunit/)

---
