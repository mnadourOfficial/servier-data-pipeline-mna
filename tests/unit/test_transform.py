# tests/unit/test_transform.py
import pandas as pd
from src.pharma_graph_pipeline.pipeline.transform import build_drug_graph
import re # import re

def test_build_drug_graph_journal_centric():
    """Tests the journal-centric JSON structure generation."""
    # Input clean data
    drugs = pd.DataFrame({
        "atccode": ["A01", "B02"],
        "drug": ["DRUG-X", "DRUG-Y"]
    })
    publications = pd.DataFrame({
        'id': ['1', 'NCT123', '3'],
        'title': ["A pubmed article about drug-x", "A trial of drug-x and drug-y", "Another article on drug-y"],
        'date': ["2025-01-01", "2025-02-01", "2025-03-01"],
        'journal': ["journal one", "journal one", "journal two"],
        'source_type': ["pubmed", "clinical_trial", "pubmed"]
    })

    # Expected output structure
    expected_output = {
        "journals": [
            {
                "title": "journal one",
                "references": {
                    "pubmed": [
                        {
                            "article_id": "1",
                            "article_title": "A pubmed article about drug-x",
                            "mention_date": "2025-01-01",
                            "mentioned_drug_id": "A01",
                            "mentioned_drug_name": "DRUG-X"
                        }
                    ],
                    "clinical_trials": [
                        {
                            "article_id": "NCT123",
                            "article_title": "A trial of drug-x and drug-y",
                            "mention_date": "2025-02-01",
                            "mentioned_drug_id": "A01",
                            "mentioned_drug_name": "DRUG-X"
                        },
                        {
                            "article_id": "NCT123",
                            "article_title": "A trial of drug-x and drug-y",
                            "mention_date": "2025-02-01",
                            "mentioned_drug_id": "B02",
                            "mentioned_drug_name": "DRUG-Y"
                        }
                    ]
                }
            },
            {
                "title": "journal two",
                "references": {
                    "pubmed": [
                        {
                            "article_id": "3",
                            "article_title": "Another article on drug-y",
                            "mention_date": "2025-03-01",
                            "mentioned_drug_id": "B02",
                            "mentioned_drug_name": "DRUG-Y"
                        }
                    ],
                    "clinical_trials": []
                }
            }
        ]
    }

    # Run the function
    actual_output = build_drug_graph(drugs, publications)

    # Compare
    assert actual_output == expected_output