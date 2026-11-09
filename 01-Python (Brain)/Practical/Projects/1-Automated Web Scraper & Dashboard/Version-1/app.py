import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Hacker News Scraper", page_icons=":newspaper:", layout="wide")

st.title(":newspaper: Live Hacker News Dashboard")
st.markdown("This dashboard scrapes the front page of the Hacker News in real-time, processes the data, and displays stats.")

# 2. Data Ingestion (The Scraper)
@st.cache_data(ttl=300) # Caches data for 5 minutes so you don't spam the site
def scrape_hacker_news():
    url = "https://news.ycombinator.com/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        articls = []

        # Find all article rows and subtext rows
        links = soup.select(".titleline > a")
        subtexts = soup.select(".subtext")

        for i in range(min(len(links), len(subtexts))):
            title = links[i].text
            url_link = links[i]["href"]

            # Extract score/upvotes safely
            score_element = subtexts[i].select_one(".score")
            upvotes = int(score_element.text.split()[0]) if score_element else 0

            articles.append({
                "Rank": i + 1,
                "Title": title,
                "Upvotes": upvotes,
                "URL": url_link,
                "Title_Length": len(title)
            })

        return pd.DataFrame(articles)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# 3. Fetch and Process Data
with st.spinner("Scraping Hacker News..."):
    df = scrape_hacker_news()

if not df.empty:
    # 4. Metrics Display
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Articles Scraped", len(df))
    with col2:
        st.metric("Highest Upvotes", int(df["Upvotes"].max()))
    with col3:
        st.metric("Average Title Length", f"{int(df['Title_Length'].mean())} chars")

    st.markdown("---")

    # 5. Interactive Layout
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.subheader("Top Articles by Upvotes")
        #Interactive slider to filter data dynamically
        min_votes = st.slider("Filter by Minimum Upvotes", 0, int(df["Upvotes"].max()), 50)
        filtered_df = df[df["Upvotes"] >= min_votes]

        # Display clickable links in a clean data editor
        st.data_editor(
            filtered_df[["Rank", "Title", "Upvotes", "URL"]],
            column_config={"URL": st.column_config.LinkColumn("Article Link")},
            use_Container_width=True,
            hide_index=True
        )

    with right_col:
        st.subheader("Distribution Of Upvotes")
        #Bar chart showing upvotes across top ranks
        st.bar_chart(data=df.set_index("Title")["Upvotes"], use_container_width=True)

        # Simple data download feature
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name="hacker_news_data.csv",
            mime="text/csv",
        )

        else:
            st.warning("NO data retrieved. Make sure you are connected to the internet.")
