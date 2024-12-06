import streamlit as st
from bs4 import BeautifulSoup
import requests
from transformers import pipeline
import torch

# Initialize the summarization pipeline
device = "cuda" if torch.cuda.is_available() else "cpu"
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", device=0 if device == "cuda" else -1)

def summarize_text(text):
    try:
        summary = summarizer(text, max_length=150, min_length=40, do_sample=False)
        return summary[0]["summary_text"]
    except Exception as e:
        return f"Error in summarization: {e}"

# Define topics
topics = ["India", "World", "Business", "Tech", "Cricket", "Sports", "Entertainment", "Auto", "TV"]

st.title("News Summarizer")
st.subheader("Select a topic to fetch and summarize the latest news")

topic = st.selectbox("Choose a topic:", topics)

if st.button("Get News"):
    url = f"https://timesofindia.indiatimes.com/topic/{topic}"

    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        elements = soup.find_all(class_="uwU81")

        BASE_URL = "https://timesofindia.indiatimes.com"

        # Extract text and links from these elements
        scraped_data = []
        for element in elements_with_uwU81[:5]:
            text = element.get_text(strip=True)
            link = element.find('a')['href'] if element.find('a') else None
            if link:
                # Check if the link is already an absolute URL or needs the base URL
                full_link = link if link.startswith("http") else BASE_URL + link
                # Store for further scraping
                scraped_data.append({'text': text, 'link': full_link})

        for item in scraped_data:
            try:
                link_response = requests.get(item["link"])
                link_response.raise_for_status()

                link_soup = BeautifulSoup(link_response.content, "html.parser")
                article_text = link_soup.get_text(strip=True)

                summary = summarize_text(article_text[:2000])
                st.write(f"### News: {item['text']}")
                st.write(f"**Link**: [Read More]({item['link']})")
                st.write(f"**Summary**: {summary}")
                st.write("---")
            except Exception as e:
                st.error(f"Failed to process link {item['link']}: {e}")

    except Exception as e:
        st.error(f"Failed to retrieve the webpage: {e}")
