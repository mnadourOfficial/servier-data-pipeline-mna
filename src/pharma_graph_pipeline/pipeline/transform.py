# src/pharma_graph_pipeline/pipeline/transform.py

import pandas as pd
from typing import Dict, List
import logging
import re

def build_drug_graph(drugs_df: pd.DataFrame, publications_df: pd.DataFrame) -> Dict[str, List]:
    """
    Builds a journal-centric graph. The output is a dictionary containing a list of journals.
    Each journal contains a breakdown of its publications (PubMed, Clinical Trials)
    that mention any of the specified drugs.
    """
    logging.info("🚀 Starting journal-centric graph transformation...")

    # --- Step 1: Find all drug mentions across all publications ---
    all_mentions = []
    # Ensure drug names are lowercase for matching
    drugs_df['drug_lower'] = drugs_df['drug'].str.lower()

    for _, pub_row in publications_df.iterrows():
        pub_title_lower = pub_row['title'].lower()
        
        # For each publication, check against every drug
        for _, drug_row in drugs_df.iterrows():
            # Use regex to match whole words to avoid partial matches (e.g., 'on' in 'betamethasone')
            if re.search(fr'\b{re.escape(drug_row["drug_lower"])}\b', pub_title_lower):
                # If a drug is mentioned, create a detailed record of the mention
                mention_record = {
                    'journal': pub_row['journal'],
                    'source_type': pub_row['source_type'],
                    'article_id': pub_row['id'],
                    'article_title': pub_row['title'],
                    'mention_date': pub_row['date'],
                    'mentioned_drug_id': drug_row['atccode'],
                    'mentioned_drug_name': drug_row['drug']
                }
                all_mentions.append(mention_record)

    if not all_mentions:
        logging.warning("No drug mentions were found in any publication.")
        return {"journals": []}

    # Convert the list of mentions into a DataFrame for easy grouping
    mentions_df = pd.DataFrame(all_mentions)

    # --- Step 2: Group the mentions to build the final JSON structure ---
    final_journal_list = []
    # Group all mentions by the journal they appeared in
    for journal_name, journal_group in mentions_df.groupby('journal'):
        
        # Separate mentions into pubmed and clinical trials
        pubmed_mentions = journal_group[journal_group['source_type'] == 'pubmed']
        trials_mentions = journal_group[journal_group['source_type'] == 'clinical_trial']

        # Format the references for this journal
        journal_references = {
            "pubmed": pubmed_mentions.drop(columns=['journal', 'source_type']).to_dict('records'),
            "clinical_trials": trials_mentions.drop(columns=['journal', 'source_type']).to_dict('records')
        }
        
        # Build the final object for this journal
        final_journal_list.append({
            "title": journal_name,
            "references": journal_references
        })
        
    logging.info("✅ Journal-centric graph transformation complete.")
    return {"journals": final_journal_list}