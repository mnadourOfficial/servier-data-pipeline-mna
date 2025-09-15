# src/pharma_graph_pipeline/pipeline/load.py

import json
import logging
from typing import Dict, List

# The top-level data structure is now a Dictionary
def save_to_json(data: Dict[str, List], path: str):
    """
    Saves the final data structure to a JSON file.

    Args:
        data (Dict[str, List]): The final dictionary to save.
        path (str): The output file path.
    """
    with open(path, 'w', encoding='utf-8') as f:
        # indent=4 for human-readable output
        json.dump(data, f, indent=4, ensure_ascii=False)
    logging.info(f"✅ Output successfully saved to {path}")