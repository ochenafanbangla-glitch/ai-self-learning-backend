from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import os

from pattern_matrix import PatternErrorMatrix
from dynamic_weighting import DynamicWeighting
from recovery_mode import MartingaleRecovery
from heatmap import MarketHeatmap
from database import GameDatabase

app = FastAPI(title="Self-Learning AI Backend (Optimized)")

# Initialize components
pattern_matrix = PatternErrorMatrix()
dynamic_weighting = DynamicWeighting(["CID Sensor", "Dragon Logic", "Trend Sensor"])
recovery = MartingaleRecovery(confidence_threshold=0.85) # 85% threshold as requested
heatmap = MarketHeatmap(window_size=100)
db = GameDatabase()

# Load existing data into heatmap from DB
recent_outcomes = db.get_recent_results(100)
for outcome in reversed(recent_outcomes):
    heatmap.add_result(outcome)

class PredictionRequest(BaseModel):
    period: str
    history: List[str]
    sensor_outputs: Dict[str, str]

class UpdateRequest(BaseModel):
    period: str
    history: List[str]
    sensor_outputs: Dict[str, str]
    prediction: str
    actual_outcome: str
    bet_amount: float
    confidence: float

@app.get("/")
def read_root():
    return {
        "status": "AI Backend is running", 
        "version": "2.0.0",
        "features": [
            "Pattern Error Matrix (3-Loss Inversion)", 
            "Dynamic Weighting (5-Round Update)", 
            "Martingale-Safe Recovery (>85% Confidence)", 
            "Live Market Heatmap"
        ]
    }

@app.post("/predict")
def get_prediction(request: PredictionRequest):
    # 1. Get weighted prediction from sensors
    base_pred, confidence = dynamic_weighting.get_weighted_prediction(request.sensor_outputs)
    
    # 2. Apply Pattern Error Matrix (Self-Learning with 3-loss inversion)
    final_pred = pattern_matrix.predict(request.history, base_pred)
    
    # 3. Check Recovery Mode (Only if confidence > 85%)
    bet_amount, should_signal = recovery.get_bet_strategy(confidence)
    
    # 4. Get Heatmap Data
    heatmap_data = heatmap.get_heatmap_data()
    
    return {
        "period": request.period,
        "prediction": final_pred,
        "confidence": round(confidence * 100, 2),
        "bet_amount": bet_amount,
        "should_signal": should_signal,
        "heatmap": heatmap_data,
        "is_inverted": final_pred != base_pred,
        "recovery_mode": recovery.total_loss > 0
    }

@app.post("/update")
def update_system(request: UpdateRequest):
    # 1. Update Pattern Matrix
    pattern_matrix.update(request.history, request.prediction, request.actual_outcome)
    
    # 2. Update Sensor Weights (Every 5 rounds)
    dynamic_weighting.update_weights(request.sensor_outputs, request.actual_outcome)
    
    # 3. Update Recovery State
    won = request.prediction == request.actual_outcome
    recovery.update_result(won, request.bet_amount)
    
    # 4. Update Heatmap
    heatmap.add_result(request.actual_outcome)
    
    # 5. Save to Database
    db.save_result(
        request.period, 
        request.history, 
        request.prediction, 
        request.actual_outcome, 
        request.confidence, 
        request.bet_amount
    )
    
    return {"status": "success", "message": f"System updated for period {request.period}"}

@app.get("/stats")
def get_stats():
    return {
        "sensor_weights": dynamic_weighting.weights,
        "heatmap": heatmap.get_heatmap_data(),
        "recovery_status": {
            "current_step": recovery.current_step,
            "total_loss": recovery.total_loss,
            "is_active": recovery.total_loss > 0
        },
        "learning_stats": {
            "round_counter": dynamic_weighting.round_counter,
            "patterns_learned": len(pattern_matrix.matrix)
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
