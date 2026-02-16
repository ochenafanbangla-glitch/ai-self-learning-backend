import json
import os

class DynamicWeighting:
    def __init__(self, sensors, storage_path="sensor_weights.json"):
        self.storage_path = storage_path
        self.sensors = sensors # List of sensor names
        self.weights = self._load_weights()

    def _load_weights(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        # Initialize equal weights
        return {sensor: 1.0 for sensor in self.sensors}

    def _save_weights(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.weights, f)

    def get_weighted_prediction(self, sensor_outputs):
        """
        sensor_outputs: dict like {"CID Sensor": "Big", "Dragon Logic": "Small"}
        Returns final prediction and confidence level.
        """
        score = 0
        total_weight = sum(self.weights.values())
        
        for sensor, prediction in sensor_outputs.items():
            weight = self.weights.get(sensor, 0)
            val = 1 if prediction == "Big" else -1
            score += val * weight
        
        final_pred = "Big" if score >= 0 else "Small"
        confidence = abs(score) / total_weight
        
        return final_pred, confidence

    def update_weights(self, sensor_outputs, actual_outcome):
        """Increases weight for correct sensors, decreases for incorrect ones."""
        for sensor, prediction in sensor_outputs.items():
            if sensor not in self.weights:
                self.weights[sensor] = 1.0
                
            if prediction == actual_outcome:
                self.weights[sensor] *= 1.1 # Increase by 10%
            else:
                self.weights[sensor] *= 0.9 # Decrease by 10%
            
            # Keep weights within reasonable bounds
            self.weights[sensor] = max(0.1, min(self.weights[sensor], 5.0))
            
        self._save_weights()

# Example usage:
# dw = DynamicWeighting(["CID Sensor", "Dragon Logic"])
# outputs = {"CID Sensor": "Big", "Dragon Logic": "Big"}
# pred, conf = dw.get_weighted_prediction(outputs)
# dw.update_weights(outputs, "Small")
