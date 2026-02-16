from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import uvicorn

from pattern_matrix import PatternErrorMatrix
from dynamic_weighting import DynamicWeighting
from recovery_mode import MartingaleRecovery
from heatmap import MarketHeatmap

app = FastAPI(title="Self-Learning AI Backend")

# Initialize components
pattern_matrix = PatternErrorMatrix()
dynamic_weighting = DynamicWeighting(["CID Sensor", "Dragon Logic", "Trend Sensor"])
recovery = MartingaleRecovery()
heatmap = MarketHeatmap()

class PredictionRequest(BaseModel):
    history: List[str]
    sensor_outputs: Dict[str, str]

class UpdateRequest(BaseModel):
    history: List[str]
    sensor_outputs: Dict[str, str]
    prediction: str
    actual_outcome: str
    bet_amount: float

@app.get("/")
def read_root():
    return {"status": "AI Backend is running", "features": ["Pattern Error Matrix", "Dynamic Weighting", "Martingale Recovery", "Heatmap"]}

@app.post("/predict")
def get_prediction(request: PredictionRequest):
    # 1. Get weighted prediction from sensors
    base_pred, confidence = dynamic_weighting.get_weighted_prediction(request.sensor_outputs)
    
    # 2. Apply Pattern Error Matrix (Self-Learning)
    final_pred = pattern_matrix.predict(request.history, base_pred)
    
    # 3. Check Recovery Mode
    bet_amount, should_signal = recovery.get_bet_strategy(confidence)
    
    # 4. Get Heatmap Data
    heatmap_data = heatmap.get_heatmap_data()
    
    return {
        "prediction": final_pred,
        "confidence": round(confidence * 100, 2),
        "bet_amount": bet_amount,
        "should_signal": should_signal,
        "heatmap": heatmap_data,
        "is_inverted": final_pred != base_pred
    }

@app.post("/update")
def update_system(request: UpdateRequest):
    # 1. Update Pattern Matrix
    pattern_matrix.update(request.history, request.prediction, request.actual_outcome)
    
    # 2. Update Sensor Weights
    dynamic_weighting.update_weights(request.sensor_outputs, request.actual_outcome)
    
    # 3. Update Recovery State
    won = request.prediction == request.actual_outcome
    recovery.update_result(won, request.bet_amount)
    
    # 4. Update Heatmap
    heatmap.add_result(request.actual_outcome)
    
    return {"status": "success", "message": "System updated with latest data"}

@app.get("/stats")
def get_stats():
    return {
        "sensor_weights": dynamic_weighting.weights,
        "heatmap": heatmap.get_heatmap_data(),
        "recovery_status": {
            "current_step": recovery.current_step,
            "total_loss": recovery.total_loss
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
