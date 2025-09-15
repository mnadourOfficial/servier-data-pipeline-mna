# src/pharma_graph_pipeline/pipeline/extract.py

import pandas as pd
from typing import Dict
from pathlib import Path
import logging
import re
from io import StringIO

def load_raw_data(config: Dict) -> Dict[str, pd.DataFrame]:
    """
    Scans a directory, identifies data files, and loads them into DataFrames.
    Adds a source_type for each publication.
    Handles malformed JSON files (e.g., trailing comma).
    """
    logging.info("🚀 Starting dynamic data extraction from directory...")
    
    raw_dir = Path(config['input_paths']['raw_data_dir'])
    if not raw_dir.is_dir():
        raise FileNotFoundError(f"Directory not found: {raw_dir}")

    temp_dataframes = {"drugs": [], "publications": []}

    for file_path in raw_dir.iterdir():
        if not file_path.is_file(): continue

        filename = file_path.name.lower()
        df = None

        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif filename.endswith('.json'):
                logging.info(f"Preprocessing JSON file: {file_path.name}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                content_fixed = re.sub(r',\s*\]', ']', content)
                df = pd.read_json(StringIO(content_fixed))
            else:
                continue
            
            # Identify the nature of the file
            if 'drug' in filename:
                temp_dataframes['drugs'].append(df)
                logging.info(f"Drug file loaded: {file_path.name}")
            elif 'pubmed' in filename or 'clinical' in filename:
                # Add a column to identify the source type
                if 'pubmed' in filename:
                    df['source_type'] = 'pubmed'
                elif 'clinical' in filename:
                    df['source_type'] = 'clinical_trial'
                
                temp_dataframes['publications'].append(df)
                logging.info(f"Publication file loaded: {file_path.name}")
            else:
                logging.warning(f"File ignored (unrecognized name): {file_path.name}")

        except Exception as e:
            logging.error(f"Error reading file {file_path.name}: {e}")
            continue
            
    # Final concatenation
    final_dataframes = {}
    if temp_dataframes['drugs']:
        final_dataframes['drugs'] = pd.concat(temp_dataframes['drugs'], ignore_index=True)
    else:
        raise ValueError("No drug files found.")
        
    if temp_dataframes['publications']:
        final_dataframes['publications'] = pd.concat(temp_dataframes['publications'], ignore_index=True)
    else:
        raise ValueError("No publication files found.")

    logging.info("✅ Raw data extraction complete.")
    return final_dataframes