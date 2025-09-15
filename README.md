# Pharmaceutical Data Pipeline 💊

## 1. Overview

This project implements a complete and robust data pipeline for processing pharmaceutical publications. Its main goal is to identify mentions of drugs (from `drugs.csv`) within various scientific publications (PubMed articles and clinical trials), and to generate a structured JSON output grouping these mentions by journal.

The entire process is designed to be automated, tested, and deployed on Google Cloud Platform (GCP) following modern DataOps best practices.

---
## 2. Features

* **Dynamic Data Ingestion**: Automatically scans and loads all `.csv` and `.json` files from the `data/raw/` directory.
* **Robust Preprocessing**: A dedicated step for cleaning, standardizing, and unifying data, including:
    * Standardization of date formats to `YYYY-MM-DD`.
    * Merging of title columns.
    * filtering out irrelevant data.
    * Cleaning of text data (lowercase, punctuation, encoding artifacts).
    * Systematic generation of a unique surrogate key for each record.
* **Journal-Centric Output**: Generates a structured JSON file grouped by journal, detailing every drug mention found.
* **Comprehensive Testing**: Includes a full suite of unit and integration tests using `pytest` to ensure code quality and prevent regressions.
* **Automated CI/CD**: A complete Continuous Integration/Continuous Deployment pipeline using **Cloud Build** for automated testing and deployment.
* **Orchestration**: An **Airflow DAG** to orchestrate the pipeline execution in a production environment (Cloud Composer).

---
## 3. Project Structure
```
pharma_graph_pipeline/
├── dags/                    # Airflow DAG definitions
│   └── pharma_pipeline_dag.py
├── data/
│   ├── raw/                 # Input raw data files
├── outputs/                 # Generated output files (ignored by Git)
├── src/                     # Main application source code
│   ├── pharma_graph_pipeline/
│   │   ├── main.py
│   │   ├── pipeline/        # Core ETL (Extract, Preprocess, Transform, Load) modules
│   │       └── extract.py
│   │       └── load.py
│   │       └── transform.py
│   │       └── preprocess.py
│   │   ├── adhoc/           # Ad-hoc analysis scripts
│   │       └── __init__.py
│   │       └── analysis.py
├── tests/                   # All tests for the project
│   ├── fixtures/           # Test data (sample inputs and expected outputs)
│   │   └── sample_data/    # Containing some input data to test
│   │   └── expected_output.json
│   ├── unit/               # Tests for individual functions
│   │   └── test_preprocess.py
│   │   └── test_transform.py
│   └── integration/        # End-to-end pipeline tests
│   │   └── test_full_pipeline.py
│   │   └── __init__.py
├── .gitignore               # Specifies files to be ignored by Git
├── cloudbuild.yaml          # CI/CD configuration for Google Cloud Build
├── config.yaml              # Configuration file (paths, etc.)
├── pytest.ini               # Configuration for Pytest (path setup)
└── requirements.txt         # Python project dependencies
```

---
## 4. Local Setup and Execution

### Prerequisites

* Python 3.10+
* Git

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/VOTRE_NOM/NOM_DU_REPO.git](https://github.com/VOTRE_NOM/NOM_DU_REPO.git)
    cd NOM_DU_REPO
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    # On Windows, use: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Pipeline Locally

1.  Place your raw data files (`drugs.csv`, `pubmed.csv`, etc.) in the `data/raw/` directory.
2.  Execute the main script from the **project root directory**:
    ```bash
    python -m src.pharma_graph_pipeline.main
    ```
3.  The output will be generated in the `outputs/drug_graph.json` file.

### Running Tests

To ensure everything is working as expected, run the full test suite from the **project root directory**:
```bash 
pytest -v
```

## 5. Ad-Hoc Analysis
This project includes a separate script for performing analysis on the generated output.

### Find Top Journal
The script located at src/pharma_graph_pipeline/adhoc/analysis.py analyzes the outputs/drug_graph.json file to find the journal (or journals, in case of a tie) that mentions the most different drugs.

**Prerequisite**: You must run the main pipeline at least once before running this analysis, as it depends on the JSON output file.

### How to Run
From the project root directory, run the following command:

```bash
python -m src.pharma_graph_pipeline.adhoc.analysis
```

The result will be displayed as a log message in the terminal.

## 6. Deployment and Orchestration on GCP (DataOps)

This project is designed for automated deployment and execution on Google Cloud Platform.

### Overview of the Workflow

1.  A developer pushes code changes to the `main` branch on **GitHub**.
2.  A **Cloud Build** trigger automatically starts a new build.
3.  Cloud Build installs dependencies and runs `pytest`. If any test fails, the process stops.
4.  If tests pass, Cloud Build deploys the application code and the DAG file to the **Cloud Composer** GCS bucket.
5.  **Cloud Composer (Airflow)** automatically detects the new DAG and schedules it for execution.

### Step-by-Step Deployment Setup

1.  **GCP Prerequisites**:
    * A GCP project with billing enabled.
    * A **Cloud Composer 2** environment created. Note its GCS bucket name.
    * The **Cloud Build** API enabled.

2.  **Push your project to GitHub**: Ensure all your code, including the `cloudbuild.yaml` and `dags` folder, is on your GitHub repository.

3.  **Connect Cloud Build to GitHub**:
    * In the GCP Console, navigate to `Cloud Build` > `Triggers`.
    * Connect your GitHub repository.
    * Create a new trigger that watches your `main` branch.

4.  **Configure the Trigger**:
    * In the trigger settings, under "Configuration", select "Cloud Build configuration file". The location is `/cloudbuild.yaml`.
    * Under "Advanced" > **"Substitution variables"**, you **must** add the following variable. This tells Cloud Build where to deploy your files.
        * **Variable**: `_COMPOSER_BUCKET`
        * **Value**: The name of your Cloud Composer GCS bucket.

5.  **Configure Airflow**:
    * Access your Airflow UI via the Cloud Composer page.
    * Navigate to `Admin` > `Variables`.
    * Create a new variable required by the DAG:
        * **Key**: `pharma_project_dir`
        * **Val**: `/home/airflow/gcs/data/pharma_graph_pipeline`

Once these steps are completed, every `git push` to your main branch will trigger this automated, tested, and secure deployment process.
