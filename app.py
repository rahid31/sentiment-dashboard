import pandas as pd
import requests
import streamlit as st
import os
import time
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

nltk.download('vader_lexicon')

# Load API credentials
BASE_URL = os.getenv("baseUrl")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

# Headers for the API request
HEADERS = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST
}

def get_company_id(company_name):
    """Fetch company ID by name."""
    search_url = f"{BASE_URL}/search"
    params = {"query": company_name}
    response = requests.get(search_url, headers=HEADERS, params=params)
    
    if response.status_code == 200:
        data = response.json().get('data', {}).get('employerResults', [])
        if data and len(data) > 0:
            return data[0].get('employer', {}).get('id')
    return None

def get_company_details(company_id):
    """Fetch details using company ID."""
    reviews_url = f"{BASE_URL}/overview-details"
    params = {"companyId": company_id}
    response = requests.get(reviews_url, headers=HEADERS, params=params)
            
    if response.status_code == 200:
        data = response.json().get('data', {})

        if isinstance(data, dict):  # Ensure data is a dictionary, not a list
            return pd.DataFrame([data])  # Convert dictionary to a DataFrame with one row

    return pd.DataFrame()

def get_reviews(company_id):
    """Fetch reviews using company ID."""
    reviews_url = f"{BASE_URL}/reviews"
    params = {"companyId": company_id, "page": 1}
    response = requests.get(reviews_url, headers=HEADERS, params=params)
            
    if response.status_code == 200:
        data = response.json().get('data', []).get('employerReviewsRG', []).get('reviews', [])
        reviews = data
        return pd.DataFrame(reviews) if reviews else pd.DataFrame()
    return pd.DataFrame()

def calculate_sentiment(reviews):
    reviews = reviews.dropna(subset=['summary'])
    reviews['summary'] = reviews['summary'].astype(str)
    # Initialize SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()
    # Calculate sentiment score for each review
    reviews['sentiment_score'] = reviews['summary'].apply(lambda x: sia.polarity_scores(x)['compound'])
    # Assign sentiment label based on sentiment score
    reviews['sentiment_label'] = reviews['sentiment_score'].apply(
        lambda x: 'Positive' if x >= 0.2 else 'Negative' if x <= -0.2 else 'Neutral'
    )
    # Count the number of positive, negative, and neutral reviews
    sentiment_counts = reviews['sentiment_label'].value_counts()
    # Add the sentiment count as a new column
    reviews['sentiment_count'] = reviews['sentiment_label'].map(sentiment_counts)

    for sentiment, count in sentiment_counts.items():
        print(f"{sentiment}: {count} reviews")

    return reviews

# Streamlit UI
st.title("Company Reviews Sentiment Analysis")

company_name = st.text_input("Enter company name:")

if st.button("Search"):
    if company_name:
        with st.spinner("Searching for company ID..."):
            time.sleep(1)
            company_id = get_company_id(company_name)
        
        if company_id:
            st.success("Company found in the database")
            with st.spinner("Fetching company info..."):
                time.sleep(3)
                details = get_company_details(company_id)
                reviews = get_reviews(company_id)
                sentiment = calculate_sentiment(reviews)

            if not details.empty:
                st.write("Company Details:")
                mission = details["overview"].apply(lambda x: x.get("mission", "No mission available.") if isinstance(x, dict) else "No mission available.")
                description = details["overview"].apply(lambda x: x.get("description", "No description available.") if isinstance(x, dict) else "No description available.")
                industry = details["primaryIndustry"].apply(lambda x: x.get("industryName", "No name available.") if isinstance(x, dict) else "No name available.")

                with st.container():
                    cols = st.columns([1, 1])

                    with cols[0]:
                        st.image(details['squareLogoUrl'].iloc[0], caption="Company Logo")

                        st.write("")

                        st.write(f"**Company Name:** {details['name'].iloc[0]}")

                        st.write("")

                        st.write(f"**Year Founded:** {details['yearFounded'].iloc[0]}")

                        st.write("")

                        st.write(f"**Industry:** {industry.iloc[0]}")

                        st.write("")
                        
                        st.write(f"**Company Headquarters:** {details['headquarters'].iloc[0]}")

                        st.write("")

                        st.write(f"**Company Size:** {details['size'].iloc[0]}")

                        st.write("")

                        st.write(f"**Website:** {details['website'].iloc[0]}")

                    with cols[1]:
                        st.write(f"**Company Description:** {description.iloc[0]}")
                        st.write("")
                        st.write(f"**Company Mission:** {mission.iloc[0]}")
            else:
                st.write("No details found.")

            if not details.empty:
                st.dataframe(details)
            else:
                st.write("No details found.")

            st.write("")
            
            st.write("")

            if not reviews.empty:
                st.write("Reviews:")
                st.dataframe(reviews)
            else:
                st.write("No reviews found.")

            if not sentiment.empty:
                st.write("Sentiment Analysis:")
                st.dataframe(sentiment)
            else:
                st.write("No sentiment analysis found.")
        else:
            st.write("Company not found.")
    else:
        st.write("Please enter a company name.")
