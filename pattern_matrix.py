import json
import os

class PatternErrorMatrix:
    def __init__(self, storage_path="pattern_data.json"):
        self.storage_path = storage_path
        self.matrix = self._load_data()

    def _load_data(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        return {}

    def _save_data(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.matrix, f)

    def get_pattern_key(self, history):
        """Converts last N results into a string key."""
        return ",".join(map(str, history))

    def predict(self, history, base_prediction):
        """
        Adjusts base prediction based on historical errors for this pattern.
        If the pattern has a high error rate, it flips the prediction.
        """
        key = self.get_pattern_key(history)
        if key in self.matrix:
            error_count = self.matrix[key].get("errors", 0)
            success_count = self.matrix[key].get("success", 0)
            
            # If errors are significantly higher than successes, flip the logic
            if error_count > success_count:
                return "Small" if base_prediction == "Big" else "Big"
        
        return base_prediction

    def update(self, history, prediction, actual_outcome):
        """Updates the matrix based on the result."""
        key = self.get_pattern_key(history)
        if key not in self.matrix:
            self.matrix[key] = {"errors": 0, "success": 0}
        
        if prediction == actual_outcome:
            self.matrix[key]["success"] += 1
        else:
            self.matrix[key]["errors"] += 1
        
        self._save_data()

# Example usage:
# matrix = PatternErrorMatrix()
# history = ["Big", "Small", "Big"]
# pred = matrix.predict(history, "Big")
# matrix.update(history, pred, "Small")
