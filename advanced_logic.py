import math

class AdvancedAIProcessor:
    def __init__(self, pattern_matrix, dynamic_weighting):
        self.pattern_matrix = pattern_matrix
        self.dynamic_weighting = dynamic_weighting

    def calculate_boosted_confidence(self, history, base_pred, base_confidence):
        """
        Normalizes and boosts confidence based on pattern reliability.
        """
        key = self.pattern_matrix.get_pattern_key(history)
        pattern_data = self.pattern_matrix.matrix.get(key, {})
        
        success = pattern_data.get("success", 0)
        errors = pattern_data.get("errors", 0)
        consecutive_errors = pattern_data.get("consecutive_errors", 0)
        
        # 1. Normalization: Ensure base confidence isn't too low if sensors agree
        # If confidence is < 20% but sensors agree, it's likely a calculation artifact
        normalized_conf = max(base_confidence, 30.0) if base_confidence > 0 else 50.0
        
        # 2. Pattern Boosting: If a pattern has high success, boost confidence
        total_pattern_rounds = success + errors
        if total_pattern_rounds > 5:
            win_rate = success / total_pattern_rounds
            if win_rate > 0.7:
                normalized_conf += 15.0
            elif win_rate < 0.3:
                # If pattern is failing, and we are inverting, boost confidence in the inversion
                if consecutive_errors >= 3:
                    normalized_conf += 20.0
        
        # 3. Penalty for high consecutive errors without inversion
        if consecutive_errors > 0 and consecutive_errors < 3:
            normalized_conf -= (consecutive_errors * 10.0)
            
        # Cap confidence between 5% and 99%
        return max(5.0, min(99.0, normalized_conf))

    def get_optimized_prediction(self, history, sensor_outputs):
        # Get base prediction and confidence from dynamic weighting
        base_pred, base_conf = self.dynamic_weighting.get_weighted_prediction(sensor_outputs)
        
        # Apply pattern matrix inversion logic
        final_pred = self.pattern_matrix.predict(history, base_pred)
        
        # Calculate boosted confidence
        optimized_conf = self.calculate_boosted_confidence(history, base_pred, base_conf * 100)
        
        return final_pred, optimized_conf, (final_pred != base_pred)
