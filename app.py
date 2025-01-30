import pandas as pd
import requests
import streamlit as st
import os
from dotenv import load_dotenv
import time
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud

nltk.download('vader_lexicon')

load_dotenv()

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

    return reviews

def show_wordcloud(data, colormap="Blues"):
    wordcloud = WordCloud(
        background_color=None,
        mode="RGBA",
        max_words=50,
        max_font_size=50,
        # width=width,
        # height=height,
        scale=2,
        random_state=42,
        colormap=colormap
    ).generate(str(data))
    
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    return fig

def display_star_rating(avg_rating):
    """Display star rating using image icons."""
    full_star = "https://static-00.iconduck.com/assets.00/star-emoji-512x488-phxasgjk.png"
    empty_star = "https://www.iconpacks.net/icons/1/free-star-icon-984-thumb.png"

    full_count = int(avg_rating)  # Full stars
    empty_count = 5 - full_count  # Empty stars

    stars = [full_star] * full_count + [empty_star] * empty_count
    st.image(stars, width=20)  # Display stars

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
                st.subheader("Company Details:")
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

            # if not details.empty:
            #     st.dataframe(details)
            # else:
            #     st.write("No details found.")

            st.write("")
            
            st.write("")

            if not reviews.empty:
                st.subheader("Reviews:")
                st.dataframe(reviews)

                with st.container():
                    cols = st.columns([1, 1])

                    # Display career opportunities average rating
                    with cols[0]:
                        career_rating = reviews['careerOpportunitiesRating'].mean().reset_index(name='Average')
                        career_rating = career_rating['Average'].iloc[0]
                        st.write(f"Average Career Opportunities Rating: {career_rating}")
                        display_star_rating(career_rating)
                    
                    # Display work life balance average rating
                    with cols[1]:
                        balance_rating = reviews['workLifeBalanceRating'].mean().reset_index(name='Average')
                        balance_rating = balance_rating['Average'].iloc[0]
                        st.write(f"Average Work Life Balance Rating: {balance_rating}")
                        display_star_rating(balance_rating)

            else:
                st.write("No reviews found.")

            if not sentiment.empty:
                st.subheader("Sentiment Analysis:")
                st.dataframe(sentiment)

                with st.container():
                    cols = st.columns([1, 1, 1])

                    with cols[0]:
                        # Group sentiment data
                        sentiment_chart = sentiment.groupby('sentiment_label').size().reset_index(name='Count')
                        # Create Donut Chart
                        fig1 = px.pie(sentiment_chart, values="Count", names="sentiment_label", hole=0.4, color="sentiment_label",
                                    color_discrete_map={"Positive": "green", "Neutral": "gray", "Negative": "red"})
                        # Display in Streamlit
                        st.write("Sentiment Label Distribution")
                        st.plotly_chart(fig1)

                    with cols[1]:
                        # Group outlook data
                        outlook_chart = sentiment.groupby('ratingBusinessOutlook').size().reset_index(name='Count')
                        # Create Donut Chart
                        fig2 = px.pie(outlook_chart, values="Count", names="ratingBusinessOutlook", hole=0.4, color="ratingBusinessOutlook",
                                    color_discrete_map={"Positive": "green", "Neutral": "gray", "Negative": "red"})
                        # Display in Streamlit
                        st.write("Business Outlook Distribution")
                        st.plotly_chart(fig2)   
                    
                    with cols[2]:
                        # Group reviews by positions
                        reviews['jobTitle'] = reviews['jobTitle'].apply(lambda x: x["text"] if isinstance(x, dict) else x)
                        position_chart = reviews.groupby('jobTitle').size().reset_index(name='Count')
                        # Create Treemap
                        fig5 = px.treemap(position_chart, path = ["jobTitle"], values = "Count", color = "Count", color_continuous_scale="Blues")
                        # Display Treemap
                        st.write("Position Distribution")
                        st.plotly_chart(fig5)

                # Group Positive Reviews
                positive_reviews = sentiment[sentiment['sentiment_label'] == 'Positive']
                # Group Negative Reviews
                negative_reviews = sentiment[sentiment['sentiment_label'] == 'Negative']
                #Display Word Cloud
                if not positive_reviews.empty:
                    st.write("")
                    with st.container():
                        cols = st.columns([1, 1])

                        with cols[0]:
                            fig3 = show_wordcloud(positive_reviews["summary"], colormap="Greens")
                            st.write("Positive Word Cloud")
                            st.pyplot(fig3)
                        
                        with cols[1]:
                            fig4 = show_wordcloud(negative_reviews["summary"], colormap="Reds")
                            st.write("Negative Word Cloud")
                            st.pyplot(fig4)
                else:
                    st.warning("No reviews found.")        
            else:
                st.write("No sentiment analysis found.")
        else:
            st.write("Company not found.")
    else:
        st.write("Please enter a company name.")