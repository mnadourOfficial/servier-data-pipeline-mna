# src/pharma_graph_pipeline/adhoc/analysis.py

import json
from collections import defaultdict
import yaml
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_top_journals(graph_file_path: str) -> str:
    """
    Analyzes the journal-centric JSON to find the journal(s) that mention the
    most *different* drugs. Handles ties by listing all winners.

    Args:
        graph_file_path (str): Path to the output JSON file.

    Returns:
        str: A formatted string announcing the top journal(s).
    """
    try:
        with open(graph_file_path, 'r', encoding='utf-8') as f:
            # The loaded data is a dictionary: {"journals": [...]}
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error reading JSON file: {e}"

    # Use defaultdict(set) to count unique drugs per journal
    journal_drug_counts = defaultdict(set)
    
    # Get the list of journals from the top-level dictionary
    journal_list = data.get('journals', [])

    # 1. Loop through the list of journals
    for journal_data in journal_list:
        journal_name = journal_data.get('title')
        if not journal_name:
            continue
        
        references = journal_data.get('references', {})
        
        # 2. Loop through pubmed publications for that journal
        for pubmed_ref in references.get('pubmed', []):
            drug_name = pubmed_ref.get('mentioned_drug_name')
            if drug_name:
                journal_drug_counts[journal_name].add(drug_name)

        # 3. Loop through clinical trials for that journal
        for trial_ref in references.get('clinical_trials', []):
            drug_name = trial_ref.get('mentioned_drug_name')
            if drug_name:
                journal_drug_counts[journal_name].add(drug_name)

    if not journal_drug_counts:
        return "No journals found in the data."

    # Find the maximum score
    max_count = max(len(drugs) for drugs in journal_drug_counts.values())

    if max_count == 0:
        return "No drug mentions found in any journal."

    # List all journals that achieved this maximum score
    top_journals = [
        journal for journal, drugs in journal_drug_counts.items() 
        if len(drugs) == max_count
    ]

    # Format the output message
    if len(top_journals) == 1:
        return f"The journal that mentions the most different drugs is: {top_journals[0]} (with {max_count} drugs)."
    else:
        journal_list_str = ", ".join(top_journals)
        return f"There are {len(top_journals)} journals tied for the top spot, each mentioning {max_count} different drugs: {journal_list_str}."


if __name__ == '__main__':
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        graph_path = config['output_path']['drug_graph']
        
        logging.info("🔎 Running ad-hoc analysis: Finding the top journal(s)...")
        result = find_top_journals(graph_path)
        logging.info(f"🏆 Analysis result: {result}")

    except FileNotFoundError:
        logging.error("Error: 'config.yaml' not found. Make sure you are running the script from the project root.")
    except KeyError:
        logging.error("Error: Key 'output_path.drug_graph' not found in 'config.yaml'.")