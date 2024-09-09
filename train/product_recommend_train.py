import os
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging
from sqlalchemy import create_engine
from django.conf import settings
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Centralize the MODEL_PATH definition
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, 'model')
MODEL_PATH = os.path.join(MODEL_DIR, 'recommender_model.pkl')

def ensure_model_directory_exists():
    """Ensure the model directory exists."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    logging.info(f"Model directory ensured at: {MODEL_DIR}")

def fetch_data_from_postgres():
    """Fetch data from PostgreSQL database."""
    db_settings = settings.DATABASES['default']
    db_url = f"postgresql://{db_settings['USER']}:{db_settings['PASSWORD']}@{db_settings['HOST']}:{db_settings['PORT']}/{db_settings['NAME']}"
    engine = create_engine(db_url)
    
    query = "SELECT * FROM products"
    df = pd.read_sql_query(query, engine)
    
    if df.empty:
        raise ValueError("No products found in the database")
    
    # Process the data
    df['categories'] = df['categories'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
    df['category_names'] = df['categories'].apply(lambda x: ' '.join([cat['category_name'] for cat in x]) if isinstance(x, list) else '')
    
    df['tags'] = df['tags'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
    df['tags_str'] = df['tags'].apply(lambda x: ' '.join(x) if isinstance(x, list) else '')
    
    return df

def train_model(df):
    """Train the model using the provided DataFrame."""
    df['combined_features'] = (
        df['name'] + ' ' + 
        df['description'] + ' ' + 
        df['brand'] + ' ' + 
        df['country_of_origin'] + ' ' + 
        df['category_names'] + ' ' + 
        df['tags_str']
    )
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['combined_features'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    return df, cosine_sim

def save_model(df, cosine_sim):
    """Save the model to the specified path."""
    ensure_model_directory_exists()
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump((df, cosine_sim), f)
    logging.info(f"Model saved successfully at: {MODEL_PATH}")
    print(f"Model file saved at: {MODEL_PATH}")  # Print the actual path

def update_and_train_product_recommend():
    """Update and train the product recommendation model."""
    try:
        df = fetch_data_from_postgres()
        df, cosine_sim = train_model(df)
        save_model(df, cosine_sim)
        return "Data fetched, model trained and saved successfully"
    except Exception as e:
        logging.error(f"Error in update_and_train_product_recommend: {str(e)}")
        raise

def verify_model_file():
    """Verify that the model file exists and can be loaded."""
    if os.path.exists(MODEL_PATH):
        try:
            with open(MODEL_PATH, 'rb') as f:
                df, cosine_sim = pickle.load(f)
            logging.info("Model file verified successfully.")
            return True
        except Exception as e:
            logging.error(f"Error loading model file: {str(e)}")
            return False
    else:
        logging.error(f"Model file not found at: {MODEL_PATH}")
        return False

if __name__ == "__main__":
    try:
        result = update_and_train_product_recommend()
        print(result)
        if verify_model_file():
            print("Model file created and verified successfully.")
        else:
            print("Failed to create or verify the model file.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")