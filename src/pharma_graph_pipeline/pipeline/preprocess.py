# src/pharma_graph_pipeline/pipeline/preprocess.py

import pandas as pd
from typing import Dict
import logging
import re
import hashlib

# ... (clean_text and generate_surrogate_key functions are unchanged) ...
def clean_text(text: str) -> str:
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'\\x[0-9a-f]{2}', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'[^\w\sÀ-ÿ-]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def generate_surrogate_key(row):
    unique_string = f"{row['title']}-{row['date']}-{row['journal']}"
    return hashlib.sha256(unique_string.encode('utf-8')).hexdigest()

def preprocess_data(raw_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    # ... (code for setup, id standardization, title merge, etc. is unchanged) ...
    logging.info("🚀 Starting data preprocessing...")

    publications_df = raw_data['publications']

    # Standardize ID column name
    if 'Id' in publications_df.columns:
        publications_df.rename(columns={'Id': 'id'}, inplace=True)
    elif 'publication_id' in publications_df.columns:
        publications_df.rename(columns={'publication_id': 'id'}, inplace=True)
    
    if 'id' not in publications_df.columns:
        raise KeyError("ID column not found after standardization attempts.")

    # Merge title columns
    if 'scientific_title' in publications_df.columns and 'title' in publications_df.columns:
        logging.info("Merging 'scientific_title' and 'title' columns.")
        publications_df['title'] = publications_df['scientific_title'].combine_first(publications_df['title'])
        publications_df.drop(columns=['scientific_title'], inplace=True)
    
    # Standardize date format
    publications_df['date'] = pd.to_datetime(
        publications_df['date'], dayfirst=True, format="mixed", errors="coerce"
    )
    
    # Drop rows with invalid dates or missing titles
    publications_df.dropna(subset=['date', 'title'], inplace=True)

    # Format valid dates to YYYY-MM-DD string
    publications_df['date'] = publications_df['date'].dt.strftime('%Y-%m-%d')
    
    # Apply text cleaning
    logging.info("Cleaning titles...")
    publications_df['title'] = publications_df['title'].apply(clean_text)
    logging.info("Cleaning journal names...")
    publications_df['journal'] = publications_df['journal'].apply(clean_text)

    # Systematically generate a surrogate key for every row
    logging.info("Generating surrogate key for all rows...")
    publications_df['surrogate_key'] = publications_df.apply(generate_surrogate_key, axis=1)

    # Remove rows where title or journal became empty after cleaning
    publications_df = publications_df[publications_df['title'] != '']
    publications_df = publications_df[publications_df['journal'] != '']

    # Replace NaN/None with an empty string before conversion
    publications_df['id'] = publications_df['id'].fillna('')

    # Define a function to convert id to string
    def format_id(x):
        try:
            # Try to convert to a whole number, then to string
            return str(int(float(x)))
        except (ValueError, TypeError):
            # If it fails, it's already a string (like 'NCT123') or empty
            return str(x)

    # Apply the function to the id column
    publications_df['id'] = publications_df['id'].apply(format_id)
    
    logging.info("✅ Preprocessing complete.")

    return {
        "drugs": raw_data['drugs'],
        "publications": publications_df
    }