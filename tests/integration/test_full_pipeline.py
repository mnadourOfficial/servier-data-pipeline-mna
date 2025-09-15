# tests/integration/test_full_pipeline.py
import yaml
import json
from pathlib import Path
import pytest
import traceback

# Import each pipeline function individually for step-by-step testing
from src.pharma_graph_pipeline.pipeline.extract import load_raw_data
from src.pharma_graph_pipeline.pipeline.preprocess import preprocess_data
from src.pharma_graph_pipeline.pipeline.transform import build_drug_graph
from src.pharma_graph_pipeline.pipeline.load import save_to_json

def test_full_pipeline_run(tmp_path):
    """
    Runs the entire pipeline step-by-step to pinpoint the exact point of failure.
    """
    # --- SETUP (unchanged) ---
    project_root = Path(__file__).parent.parent.parent
    test_fixtures_path = project_root / "tests" / "fixtures"
    output_file_path = tmp_path / "output.json"

    test_config = {
        'input_paths': {
            'raw_data_dir': str(test_fixtures_path / "sample_data")
        },
        'output_path': {
            'drug_graph': str(output_file_path)
        }
    }
    temp_config_path = tmp_path / "temp_config.yaml"
    with open(temp_config_path, 'w') as f:
        yaml.dump(test_config, f)

    # --- EXECUTION (Step-by-step with debugging) ---
    
    # Step 1: Extraction
    try:
        raw_data = load_raw_data(test_config)
    except Exception as e:
        pytest.fail(f"The pipeline FAILED at the EXTRACTION step.\nError: {e}\n{traceback.format_exc()}")

    # Step 2: Preprocessing
    try:
        clean_data = preprocess_data(raw_data)
    except Exception as e:
        pytest.fail(f"The pipeline FAILED at the PREPROCESSING step.\nError: {e}\n{traceback.format_exc()}")

    # Step 3: Transformation
    try:
        drug_graph = build_drug_graph(clean_data['drugs'], clean_data['publications'])
    except Exception as e:
        pytest.fail(f"The pipeline FAILED at the TRANSFORMATION step.\nError: {e}\n{traceback.format_exc()}")

    # Step 4: Loading (Saving)
    try:
        save_to_json(drug_graph, test_config['output_path']['drug_graph'])
    except Exception as e:
        pytest.fail(f"The pipeline FAILED at the LOADING step.\nError: {e}\n{traceback.format_exc()}")

    # --- VERIFICATION (unchanged) ---
    with open(test_fixtures_path / "expected_output.json", 'r') as f:
        expected_json = json.load(f)

    with open(output_file_path, 'r') as f:
        actual_json = json.load(f)

    assert actual_json == expected_json