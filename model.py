import pandas as pd
import joblib
import os
import re
import nltk
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# Download stopwords once
nltk.download('stopwords', quiet=True)
STOPWORDS = set(stopwords.words('english'))

def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 2]
    return ' '.join(tokens)

def train_models(csv_path="data/expenses_dataset.csv"):
    if not os.path.exists(csv_path):
        print(f"❌ Error: {csv_path} not found.")
        return
        
    df = pd.read_csv(csv_path)
    df['clean_desc'] = df['description'].apply(preprocess_text)
    
    # Filter out empty descriptions after cleaning
    df = df[df['clean_desc'] != ""]
    
    X = df['clean_desc']
    y = df['category']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Simple, high-accuracy pipeline
    model = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2))),
        ('clf', MultinomialNB(alpha=0.1))
    ])
    
    model.fit(X_train, y_train)
    joblib.dump(model, "models/expense_model.pkl")
    print(f"✅ Model saved with accuracy: {model.score(X_test, y_test):.2%}")

def predict_category(description):
    model_path = "models/expense_model.pkl"
    if not os.path.exists(model_path):
        return "Other", 0
    model = joblib.load(model_path)
    clean = preprocess_text(description)
    pred = model.predict([clean])[0]
    prob = max(model.predict_proba([clean])[0]) * 100
    return pred, round(prob, 1)