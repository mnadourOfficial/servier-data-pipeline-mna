# tests/unit/test_preprocess.py
import pandas as pd
from pandas.testing import assert_frame_equal
from src.pharma_graph_pipeline.pipeline.preprocess import clean_text, preprocess_data

def test_clean_text():
    # ... (this test function is unchanged)
    assert clean_text("  Some Title!  ") == "some title"
    assert clean_text("Another Title with <p>HTML</p>") == "another title with html"
    assert clean_text("Weird \\xc3\\x28 spacing") == "weird spacing"
    assert clean_text(None) == ""

def test_preprocess_data():
    """Tests the main preprocessing function."""
    # Input data
    raw_publications = pd.DataFrame({
        'id': [1, None],
        'scientific_title': ["A Study on Drug X", "Another Study"],
        'title': [None, "Redundant Title"],
        'date': ["01/01/2025", "invalid-date"],
        'journal': ["The Journal!", "The Journal!"],
        'source_type': ["pubmed", "clinical_trial"]
    })
    raw_data = {"publications": raw_publications, "drugs": pd.DataFrame()}

    # Expected clean output
    expected_publications = pd.DataFrame({
        'id': ['1'], 
        'title': ["a study on drug x"],
        'date': ["2025-01-01"],
        'journal': ["the journal"],
        'source_type': ["pubmed"],
    })
    
    # Run the function
    processed_data = preprocess_data(raw_data)
    
    # The comparison is done after dropping the surrogate_key from the actual result
    assert_frame_equal(
        processed_data["publications"].drop(columns=['surrogate_key']),
        expected_publications
    )