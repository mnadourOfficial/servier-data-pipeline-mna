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
└── pyproject.toml           # Python project dependencies
└── poetry.lock              # Python project dependencies
└── dockerfile               # Docker image builder
```

---
## 4. Local Setup and Execution

### Prerequisites

* Python 3.10+
* Git

### Installation

1.  **Clone the repository and install Poetry** (if not already installed).

2.  **Navigate to the project directory and install dependencies:**
    Poetry will automatically create a virtual environment and install the dependencies listed in `pyproject.toml` and `poetry.lock`.
    ```bash
    poetry install
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
To run scripts, use `poetry run`. This ensures the script runs inside the virtual environment managed by Poetry.
```bash
poetry run python -m src.pharma_graph_pipeline.main
```
But first you have to Place your raw data files (`drugs.csv`, `pubmed.csv`, etc.) in the `data/raw/` directory.

The output will be generated in the `outputs/drug_graph.json` file.

### Running Tests

To ensure everything is working as expected, run the full test suite from the **project root directory**:
```bash 
poetry run pytest -v
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

### Deployment Workflow
* Merge Requests (MRs) are the key to this process. When an MR is accepted and merged into a branch, it automatically kicks off a deployment to its corresponding environment.

* Automated testing is a critical part of each stage, ensuring that code is stable and bug-free before moving forward.

* Manual validation gates are used between environments to provide a final, human review. This is an important step before promoting code from staging to production.

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


# Going Further

To handle very large data volumes (terabytes of files), our current code, based on **Pandas**, won't work because it's limited by the memory of a single machine. We need to switch to a **distributed computing architecture**.

Here are two modern and robust approaches to achieve this.

---

### Option 1: The ETL Approach with Spark (PySpark)

This approach uses a cluster of machines to transform data in memory *before* loading the final result.

* **Main Idea**: We rewrite our Python logic in **PySpark** (the Python version of Spark) and execute it on a managed cluster like **Google Cloud Dataproc**.
* **How It Works**:
    1.  Raw data is stored on **Google Cloud Storage (GCS)** in the optimized **Parquet** format.
    2.  Our **Airflow** DAG launches a job on the Dataproc cluster.
    3.  The Spark job reads the data from GCS and performs transformations (mention lookup, aggregation) in parallel across all cluster machines.
    4.  The results are then written to GCS (or another destination).
* **Ideal for**: Complex transformations that are easier to write in Python than in SQL, and for teams already familiar with the Spark ecosystem.

---

### Option 2: The ELT Approach with BigQuery & dbt (or Dataform) (Modern and Serverless)

This approach involves loading the raw data first and then using the power of the data warehouse to transform it.

* **Main Idea**: Files are received in GCS, and we load the raw data directly into **BigQuery**. Then, we use **SQL** queries, orchestrated by the **dbt (or Dataform)** tool, to transform the data directly within BigQuery (staging / intermediate / mart).
* **How It Works**:
    1.  A **Cloud Run** service automatically loads files from GCS into raw tables in BigQuery.
    2.  We launch dbt transformations, which consist of a series of SQL models. These models perform the necessary joins to denormalize source tables and aggregate information, building the final data marts ready for analysis. The result is a new, "clean" table in BigQuery.
* **Ideal for**: Teams who are very comfortable with **SQL** and want a **"serverless"** solution without having to manage clusters.

---

**In summary, the choice depends on your preferences and skills**: **Spark** if you prefer Python logic and fine-grained control over execution, **BigQuery/dbt** if you prefer a SQL approach and the simplicity of a serverless solution.
