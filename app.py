import streamlit as st
from bs4 import BeautifulSoup
import requests
from transformers import pipeline

# Initialize the summarization pipeline
summarizer = pipeline("summarization")

def summarize_text(text):
    try:
        # Summarize the text
        summary = summarizer(text, max_length=150, min_length=40, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"Error in summarization: {e}"

# Define topics
topics = ["India", "World", "Business", "Tech", "Cricket", "Sports", "Entertainment", "Auto", "TV"]

# Streamlit UI
st.title("News Summarizer")
st.subheader("Select a topic to fetch the latest news and get summaries")

topic = st.selectbox("Choose a topic:", topics)

if st.button("Get News"):
    # URL to scrape
    url = f"https://timesofindia.indiatimes.com/topic/{topic}"

    # Send a request to the website
    response = requests.get(url)
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all elements with the class 'uwU81'
        elements_with_uwU81 = soup.find_all(class_='uwU81')

        # Extract text and links from these elements
        scraped_data = []
        for element in elements_with_uwU81[:5]:
            text = element.get_text(strip=True)
            link = element.find('a')['href'] if element.find('a') else None
            if link:
                full_link = f"https://timesofindia.indiatimes.com{link}"
                # Store for further scraping
                scraped_data.append({'text': text, 'link': full_link})

        # Display summaries
        for item in scraped_data:
            link_response = requests.get(item['link'])
            if link_response.status_code == 200:
                link_soup = BeautifulSoup(link_response.content, 'html.parser')
                # Extract the main content of the article (adjust selector as needed)
                article_text = link_soup.get_text(strip=True)
                # Summarize the article content
                summary = summarize_text(article_text[:2000])  # Limit to 2000 characters for efficiency
                summary = summary.split("|")[0]
                st.write(f"### News: {item['text']}")
                st.write(f"**Link**: [Read More]({item['link']})")
                st.write(f"**Summary**: {summary}")
                st.write("---")
            else:
                st.write(f"Failed to scrape link: {item['link']} with status code {link_response.status_code}")
    else:
        st.error(f"Failed to retrieve the webpage. Status code: {response.status_code}")
