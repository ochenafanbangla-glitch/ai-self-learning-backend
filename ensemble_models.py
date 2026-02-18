import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier
import joblib
import os
import sqlite3
from datetime import datetime, timedelta

class EnsembleManager:
    def __init__(self, db_path="game_data.db", model_dir="models"):
        self.db_path = db_path
        self.model_dir = model_dir
        self.model_names = [
            "RandomForest", "XGBoost", "SVM", "KNN", 
            "LogisticRegression", "GradientBoosting", "ExtraTrees", 
            "AdaBoost", "Ridge", "GaussianNB", "DecisionTree", "MLPPlaceholder"
        ]
        self.models = {}
        self.performance = {name: {"accuracy": 0.5, "history": []} for name in self.model_names}
        
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
            
        self._initialize_models()
        self._load_performance()

    def _initialize_models(self):
        # Initialize the 12 models with default parameters
        self.models["RandomForest"] = RandomForestClassifier(n_estimators=100)
        self.models["XGBoost"] = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
        self.models["SVM"] = SVC(probability=True)
        self.models["KNN"] = KNeighborsClassifier()
        self.models["LogisticRegression"] = LogisticRegression()
        self.models["GradientBoosting"] = GradientBoostingClassifier()
        self.models["ExtraTrees"] = ExtraTreesClassifier()
        self.models["AdaBoost"] = AdaBoostClassifier()
        self.models["Ridge"] = RidgeClassifier() # Note: Ridge doesn't have predict_proba by default
        self.models["GaussianNB"] = GaussianNB()
        self.models["DecisionTree"] = DecisionTreeClassifier()
        self.models["MLPPlaceholder"] = RandomForestClassifier(n_estimators=50, max_depth=5) # Placeholder for MLP

    def _load_performance(self):
        # In a real app, this would load from a JSON or DB
        # For now, we'll initialize with dummy data or try to calculate from DB
        self._update_performance_from_db()

    def _update_performance_from_db(self):
        conn = sqlite3.connect(self.db_path)
        # We need a table to track individual model performance
        conn.execute('''
            CREATE TABLE IF NOT EXISTS model_performance (
                model_name TEXT,
                period TEXT,
                prediction TEXT,
                actual TEXT,
                is_correct INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        for name in self.model_names:
            cursor = conn.execute('''
                SELECT AVG(is_correct) FROM (
                    SELECT is_correct FROM model_performance 
                    WHERE model_name = ? 
                    ORDER BY timestamp DESC LIMIT 20
                )
            ''', (name,))
            row = cursor.fetchone()
            if row and row[0] is not None:
                self.performance[name]["accuracy"] = row[0]
        conn.close()

    def prepare_features(self, history):
        # Convert history (list of 'Red', 'Green', 'Violet') to numerical features
        # Simple encoding: Red=0, Green=1, Violet=2
        mapping = {'Red': 0, 'Green': 1, 'Violet': 2}
        encoded = [mapping.get(x, 0) for x in history]
        
        # Ensure we have enough data, pad if necessary
        if len(encoded) < 10:
            encoded = [0] * (10 - len(encoded)) + encoded
        
        return np.array(encoded[-10:]).reshape(1, -1)

    def train_all(self, X, y):
        # X is feature matrix, y is labels
        for name, model in self.models.items():
            try:
                model.fit(X, y)
                joblib.dump(model, os.path.join(self.model_dir, f"{name}.joblib"))
            except Exception as e:
                print(f"Error training {name}: {e}")

    def get_top_3(self):
        sorted_models = sorted(self.performance.items(), key=lambda x: x[1]["accuracy"], reverse=True)
        return [m[0] for m in sorted_models[:3]]

    def predict_ensemble(self, history):
        top_3_names = self.get_top_3()
        features = self.prepare_features(history)
        
        predictions = []
        for name in top_3_names:
            model = self.models[name]
            # Try to load from disk if not trained in memory
            model_path = os.path.join(self.model_dir, f"{name}.joblib")
            if os.path.exists(model_path):
                model = joblib.load(model_path)
            
            try:
                pred_idx = model.predict(features)[0]
                inv_mapping = {0: 'Red', 1: 'Green', 2: 'Violet'}
                predictions.append(inv_mapping[pred_idx])
            except:
                # Fallback if model not trained
                predictions.append("Red")
        
        # Voting logic
        from collections import Counter
        vote_counts = Counter(predictions)
        final_pred, count = vote_counts.most_common(1)[0]
        confidence = (count / len(predictions)) * 100
        
        return {
            "prediction": final_pred,
            "confidence": confidence,
            "models_used": top_3_names,
            "individual_preds": predictions
        }

    def record_actual_outcome(self, period, history, actual):
        # This is called when a result is published
        # 1. Update all 12 models' performance in DB
        features = self.prepare_features(history)
        mapping = {'Red': 0, 'Green': 1, 'Violet': 2}
        actual_idx = mapping.get(actual, 0)
        
        conn = sqlite3.connect(self.db_path)
        for name in self.model_names:
            model_path = os.path.join(self.model_dir, f"{name}.joblib")
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                try:
                    pred_idx = model.predict(features)[0]
                    is_correct = 1 if pred_idx == actual_idx else 0
                    inv_mapping = {0: 'Red', 1: 'Green', 2: 'Violet'}
                    conn.execute('''
                        INSERT INTO model_performance (model_name, period, prediction, actual, is_correct)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (name, period, inv_mapping[pred_idx], actual, is_correct))
                except:
                    pass
        conn.commit()
        conn.close()
        
        # 2. Trigger background training if we have enough data
        self._background_train()
        
        # 3. Refresh performance metrics
        self._update_performance_from_db()

    def _background_train(self):
        # Get last 100 rounds from DB to train
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT history, actual_outcome FROM game_results ORDER BY timestamp DESC LIMIT 100", conn)
        conn.close()
        
        if len(df) < 10:
            return
            
        X = []
        y = []
        mapping = {'Red': 0, 'Green': 1, 'Violet': 2}
        
        for _, row in df.iterrows():
            hist = row['history'].split(',')
            X.append(self.prepare_features(hist).flatten())
            y.append(mapping.get(row['actual_outcome'], 0))
            
        self.train_all(np.array(X), np.array(y))

    def cleanup_old_data(self, days=7):
        conn = sqlite3.connect(self.db_path)
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        conn.execute("DELETE FROM game_results WHERE timestamp < ?", (cutoff,))
        conn.execute("DELETE FROM model_performance WHERE timestamp < ?", (cutoff,))
        conn.commit()
        conn.close()
