# src/pharma_graph_pipeline/main.py

import yaml
import logging
from src.pharma_graph_pipeline.pipeline.extract import load_raw_data
from src.pharma_graph_pipeline.pipeline.preprocess import preprocess_data
from src.pharma_graph_pipeline.pipeline.transform import build_drug_graph
from src.pharma_graph_pipeline.pipeline.load import save_to_json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_pipeline(config_path="config.yaml"):
    """
    Executes the full data pipeline: Extract, Preprocess, Transform, Load.
    """
    # Load configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # 1. Extract raw data
    raw_data = load_raw_data(config)
    
    # 2. Preprocess and clean the data
    clean_data = preprocess_data(raw_data)
    
    # 3. Transform clean data to build the graph
    drug_graph = build_drug_graph(clean_data['drugs'], clean_data['publications'])
    
    # 4. Load the result into a JSON file
    save_to_json(drug_graph, config['output_path']['drug_graph'])

if __name__ == '__main__':
    logging.info("🚀 Starting data pipeline...")
    run_pipeline()
    logging.info("🏁 Pipeline finished.")