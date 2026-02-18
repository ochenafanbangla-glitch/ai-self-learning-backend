# PROJECT BLUEPRINT: AI MASTER PRO - Final Technical Brief

## Subject: Implementation of 12-Model Ensemble Logic & GitHub Automation

This document outlines the implementation details for the AI Master Pro project, focusing on the 12-model ensemble logic, GitHub integration, and data retention mechanisms as per the provided technical brief.

## 1. The "12-Model" Strategy (Smart Ensemble Logic)

The core of the AI Master Pro system is a sophisticated ensemble of 12 distinct AI models designed to provide robust and accurate predictions while managing computational resources efficiently. The implementation adheres to the "Champion Selection" logic, ensuring optimal performance by dynamically selecting the best-performing models.

### A. Background Training (The "Bench")

All 12 AI models are kept active on the server backend and are continuously trained in the background. Each time a game result is published, this new data is fed to all 12 models. This asynchronous training process allows the models to 
learn and update their weights without impacting real-time prediction latency. The models included are:

*   RandomForestClassifier
*   XGBClassifier
*   SVC (Support Vector Classifier)
*   KNeighborsClassifier
*   LogisticRegression
*   GradientBoostingClassifier
*   ExtraTreesClassifier
*   AdaBoostClassifier
*   RidgeClassifier
*   GaussianNB
*   DecisionTreeClassifier
*   MLP (represented by a RandomForestClassifier placeholder for now)

Training data is sourced from the `game_data.db` database, with the latest 100 rounds used for training. Features are prepared by encoding historical game outcomes into a numerical format.

### B. Real-Time Inference (The "Active Squad")

A "Selector Algorithm" is implemented within the `EnsembleManager` to constantly monitor and evaluate the performance of all 12 models. This algorithm identifies the Top 3 most accurate models based on their performance over the last 20 rounds.

**Prediction Logic:** When a user requests a prediction, only these Top 3 models are queried. The predictions from these models are then aggregated using a voting mechanism. For example, if two models predict "Red" and one predicts "Green", the final prediction will be "Red" with a confidence of 66%.

**Auto-Rotation:** The system is designed for dynamic auto-rotation. If a model within the "Top 3" begins to underperform (its accuracy drops below a certain threshold or is consistently outperformed by a model on the "Bench"), it is immediately swapped with a better-performing model from the remaining 9 models. This ensures that the "Active Squad" always consists of the most reliable predictors.

## 2. Data Retention & History (Auto-Reset)

To maintain database efficiency and relevance, a data retention policy has been implemented.

**7-Day Lifecycle:** Game data older than 7 days is automatically deleted or archived from the database. This cleanup is handled by a dedicated `cleanup.py` script, which is intended to be executed daily via a cron job. The `cleanup_old_data` method in `GameDatabase` and `EnsembleManager` handles the removal of old records from `game_results` and `model_performance` tables respectively.

**Live History:** The system is designed to support real-time updates for the "History/Results" table in the application. When a new game result is verified, it should appear instantly at the top of the list. While the backend implementation now handles the data updates, the frontend integration (using AJAX/WebSockets) would be required to achieve the real-time display without a full page reload.

## 3. GitHub Integration & Deployment (Crucial)

### Repository Update and Authentication

The existing repository, `ai-self-learning-backend`, under the `ochenafanbangla-glitch` GitHub organization, has been updated with the new code. Authentication for pushes was performed using the provided Personal Access Token (PAT).

### CI/CD Pipeline

A GitHub Actions workflow file (`.github/workflows/deploy.yml`) was initially created to set up a CI/CD pipeline for auto-deployment. This workflow was designed to:

*   Trigger on every `git push` to the `master` branch.
*   Set up a Python environment.
*   Install project dependencies, including the newly added machine learning libraries.
*   Include a placeholder for running tests.
*   Contain a step for deployment to Vercel.

**Note on PAT Scope:** Due to limitations with the provided PAT's scope, the workflow file could not be pushed directly to the repository. In a production environment, a PAT with `workflow` scope or a dedicated GitHub App would be used to enable the CI/CD pipeline. For this implementation, the workflow file was removed from the push to allow the core code changes to be committed. The user would need to manually configure the CI/CD on Vercel or PythonAnywhere to trigger on pushes to the `master` branch of the updated repository.

## Implementation Details

### `ensemble_models.py`

This new module encapsulates the 12 AI models, their training, performance tracking, and the champion selection logic. Key components include:

*   `EnsembleManager`: Manages the lifecycle of all 12 models, including initialization, training, performance tracking, and ensemble prediction.
*   `_initialize_models()`: Instantiates all 12 machine learning models.
*   `_load_performance()` and `_update_performance_from_db()`: Handles loading and updating model accuracy from the `model_performance` table in the database.
*   `prepare_features()`: Converts historical game data into a numerical format suitable for model training and prediction.
*   `train_all()`: Trains all 12 models on provided data and saves them to disk using `joblib`.
*   `get_top_3()`: Identifies and returns the names of the three best-performing models based on recent accuracy.
*   `predict_ensemble()`: Takes historical data, queries the Top 3 models, and returns a consolidated prediction with confidence.
*   `record_actual_outcome()`: Updates individual model performance in the database and triggers background training.
*   `_background_train()`: Fetches recent data from the database and retrains all models asynchronously.
*   `cleanup_old_data()`: Removes old model performance records.

### `main.py` Updates

*   **Integration of `EnsembleManager`**: The `EnsembleManager` is initialized and integrated into the FastAPI application.
*   **Hybrid Prediction Logic**: The `/predict` endpoint now incorporates a hybrid prediction strategy. It first attempts to use the ensemble's prediction if its confidence is sufficiently high (>= 66%). Otherwise, it falls back to the `AdvancedAIProcessor`'s prediction.
*   **Update Endpoint Enhancements**: The `/update` endpoint now includes calls to `ensemble_manager.record_actual_outcome()` to update all 12 models' performance and trigger background training. It also calls `ensemble_manager.cleanup_old_data()` to ensure data retention policies are applied.
*   **New `/stats` Endpoint**: An additional endpoint has been added to expose ensemble-related statistics, including the current Top 3 models and the performance of all models.

### `database.py` Updates

*   **`model_performance` Table**: A new table `model_performance` has been added to store the prediction outcomes and correctness for each of the 12 models, enabling the tracking of individual model accuracy.
*   **`cleanup_old_data()` Method**: A method `cleanup_old_data` has been added to remove game results older than 7 days.

### `requirements.txt` Updates

The `requirements.txt` file has been updated to include the necessary machine learning libraries:

*   `scikit-learn`
*   `xgboost`
*   `pandas`
*   `numpy`
*   `joblib`

### `cleanup.py`

A standalone Python script `cleanup.py` has been created to perform the daily data cleanup. This script initializes `GameDatabase` and `EnsembleManager` and calls their respective `cleanup_old_data` methods. This script is designed to be run as a daily cron job.

## Conclusion

The AI Master Pro system has been enhanced with a robust 12-model ensemble strategy, dynamic champion selection, and automated data retention. The GitHub repository has been updated with these changes, laying the groundwork for a fully automated CI/CD pipeline. Further steps would involve configuring the chosen hosting platform (Vercel or PythonAnywhere) to utilize the updated repository and trigger deployments on every push, and setting up the daily cron job for data cleanup.
