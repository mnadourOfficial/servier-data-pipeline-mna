# Dockerfile

# --- Dockerfile for Advanced, Container-Based Deployment ---
#
# This Dockerfile is provided as a blueprint for a more advanced, container-based
# deployment strategy.
#
# The intended workflow is to:
#   1. Build a Docker image from this file using Cloud Build.
#   2. Push the image to a container registry (e.g., Google Artifact Registry).
#   3. Use an Airflow `KubernetesPodOperator` to run this container as an isolated task.
#
# NOTE: Given the simplicity of the current project, the active CI/CD pipeline
# (`cloudbuild.yaml`) uses a more direct file-synchronization (`gsutil rsync`)
# method. This Dockerfile is therefore NOT USED in the current deployment setup
# but is kept here to document a potential future evolution of the project.
#
# ---
    
# Use an official lightweight Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy dependency files and install them
# This is done in a separate step to leverage Docker's layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# The command to run when the container starts will be provided by Airflow