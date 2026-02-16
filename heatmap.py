import collections

class MarketHeatmap:
    def __init__(self, window_size=100):
        self.window_size = window_size
        self.history = collections.deque(maxlen=window_size)

    def add_result(self, result):
        """result should be 'Big' or 'Small'"""
        self.history.append(result)

    def get_heatmap_data(self):
        """Returns the percentage distribution of Big and Small."""
        if not self.history:
            return {"Big": 50, "Small": 50}
        
        counts = collections.Counter(self.history)
        total = len(self.history)
        
        big_percent = (counts.get("Big", 0) / total) * 100
        small_percent = (counts.get("Small", 0) / total) * 100
        
        return {
            "Big": round(big_percent, 2),
            "Small": round(small_percent, 2),
            "trend": "Big" if big_percent > small_percent else "Small",
            "sample_size": total
        }

# Example usage:
# heatmap = MarketHeatmap()
# heatmap.add_result("Big")
# print(heatmap.get_heatmap_data())
