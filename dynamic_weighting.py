import json
import os

class DynamicWeighting:
    def __init__(self, sensors, storage_path="sensor_weights.json"):
        self.storage_path = storage_path
        self.sensors = sensors
        self.data = self._load_data()
        self.round_counter = self.data.get("round_counter", 0)
        self.weights = self.data.get("weights", {sensor: 1.0 for sensor in self.sensors})
        self.temp_performance = self.data.get("temp_performance", {sensor: 0 for sensor in self.sensors})

    def _load_data(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return {
            "round_counter": 0, 
            "weights": {sensor: 1.0 for sensor in self.sensors}, 
            "temp_performance": {sensor: 0 for sensor in self.sensors}
        }

    def _save_data(self):
        data = {
            "round_counter": self.round_counter,
            "weights": self.weights,
            "temp_performance": self.temp_performance
        }
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=4)

    def get_weighted_prediction(self, sensor_outputs):
        """
        Returns final prediction and confidence level based on current weights.
        """
        score = 0
        total_weight = sum(self.weights.values())
        
        for sensor, prediction in sensor_outputs.items():
            weight = self.weights.get(sensor, 0)
            val = 1 if prediction == "Big" else -1
            score += val * weight
        
        final_pred = "Big" if score >= 0 else "Small"
        confidence = abs(score) / total_weight if total_weight > 0 else 0.5
        
        return final_pred, confidence

    def update_weights(self, sensor_outputs, actual_outcome):
        """Tracks performance and updates weights every 5 rounds."""
        self.round_counter += 1
        
        for sensor, prediction in sensor_outputs.items():
            if sensor not in self.temp_performance:
                self.temp_performance[sensor] = 0
            if prediction == actual_outcome:
                self.temp_performance[sensor] += 1
        
        if self.round_counter >= 5:
            self._apply_weight_updates()
            self.round_counter = 0
            self.temp_performance = {sensor: 0 for sensor in self.sensors}
            
        self._save_data()

    def _apply_weight_updates(self):
        """Adjusts weights based on performance in the last 5 rounds."""
        for sensor in self.sensors:
            wins = self.temp_performance.get(sensor, 0)
            # If sensor won more than 3/5 rounds, increase weight
            if wins >= 4:
                self.weights[sensor] *= 1.2
            elif wins <= 2:
                self.weights[sensor] *= 0.8
            
            # Keep weights within bounds
            self.weights[sensor] = max(0.1, min(self.weights[sensor], 5.0))
