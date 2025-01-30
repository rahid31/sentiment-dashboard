## **Sentiment Analysis Dashboard** 🚀
A **Streamlit-based dashboard** that fetches company details and reviews using an API, then applies **sentiment analysis** using the **NLTK** library.

---

## **Features** ✨
✅ Search for a company by name  
✅ Fetch company details and reviews via API  
✅ Perform **sentiment analysis** (Positive, Negative, Neutral) using **NLTK**  
✅ Interactive **Streamlit UI** with loading animations  
✅ Display company details, reviews, sentiment insights, and company logo  

---

## **Installation** ⚙️  

### **1️⃣ Clone the Repository**  
```sh
git clone https://github.com/your-repo/sentiment-dashboard.git
cd sentiment-dashboard
```

### **2️⃣ Create a Virtual Environment (Optional but Recommended)**  
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **3️⃣ Install Dependencies**  
```sh
pip install -r requirements.txt
```

---

## **Usage** ▶️  

### **Run the Streamlit Dashboard**  
```sh
streamlit run app.py
```

Enter a **company name** in the search box, and the dashboard will:  
1️⃣ Fetch company details & reviews  
2️⃣ Perform sentiment analysis  
3️⃣ Display insights dynamically  

---

## **Requirements** 📦  
Ensure you have the following **Python libraries** installed:  

```txt
streamlit
requests
pandas
nltk
os
time
```

You can install them all using:  
```sh
pip install -r requirements.txt
```

---

## **Environment Variables** 🌍  
Create a `.env` file or set the following **API credentials** in your environment:  

```sh
baseUrl=YOUR_API_BASE_URL
RAPIDAPI_KEY=YOUR_RAPIDAPI_KEY
RAPIDAPI_HOST=YOUR_RAPIDAPI_HOST
```

---

<!-- ## **Screenshots** 📸  
| Company Search | Sentiment Analysis |
|---------------|------------------|
| ![Search]() | ![Sentiment]() | -->

---
