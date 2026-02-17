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

    def get_alternative_prediction(self, history):
        """
        Secondary Logic: Last 3 Period Calculation (Simple Trend Analysis)
        If Trend Analysis fails, this acts as the fallback.
        """
        if not history or len(history) < 3:
            return "Big" # Default fallback
        
        # Count Big/Small in last 3 periods
        last_3 = history[-3:]
        big_count = last_3.count("Big")
        small_count = last_3.count("Small")
        
        # Predict the majority (Simple Trend Following)
        return "Big" if big_count >= small_count else "Small"

    def get_optimized_prediction(self, history, sensor_outputs):
        # 1. Primary Logic: Weighted Sensors
        base_pred, base_conf = self.dynamic_weighting.get_weighted_prediction(sensor_outputs)
        
        # 2. Force Prediction: No more "Wait" logic.
        # Even if confidence is low, we pick the best available.
        final_pred = base_pred
        is_alternative_used = False
        
        # If base confidence is very low, we still use it but mark it.
        # Client requested: Algorithm যাকেই এগিয়ে দেখবে সেটিকেই রেজাল্ট হিসেবে দেখাবে।
        if base_conf < 0.5:
            # If sensors are split or weak, check alternative logic
            alt_pred = self.get_alternative_prediction(history)
            final_pred = alt_pred
            is_alternative_used = True
        
        # 3. Apply pattern matrix inversion logic (Final Safety Layer)
        final_pred = self.pattern_matrix.predict(history, final_pred)
        
        # 4. Calculate boosted confidence
        optimized_conf = self.calculate_boosted_confidence(history, base_pred, base_conf * 100)
        
        # 5. Color Coding System (Traffic Light Logic):
        # Green: Confidence > 80% (Safe)
        # Yellow: Confidence 60% - 79% (Medium Risk)
        # Red: Confidence < 60% (High Risk, but show result)
        if optimized_conf >= 80.0:
            warning_color = "Green"
        elif 60.0 <= optimized_conf < 80.0:
            warning_color = "Yellow"
        else:
            warning_color = "Red"
        
        return {
            "prediction": final_pred,
            "confidence": optimized_conf,
            "is_inverted": (final_pred != base_pred),
            "warning_color": warning_color,
            "logic_used": "Alternative" if is_alternative_used else "Primary"
        }
