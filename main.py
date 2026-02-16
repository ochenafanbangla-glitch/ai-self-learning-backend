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
from advanced_logic import AdvancedAIProcessor

app = FastAPI(title="Self-Learning AI Backend (Advanced)")

# Initialize components
pattern_matrix = PatternErrorMatrix()
dynamic_weighting = DynamicWeighting(["CID Sensor", "Dragon Logic", "Trend Sensor"])
recovery = MartingaleRecovery(confidence_threshold=85.0) # Threshold updated to match percentage
heatmap = MarketHeatmap(window_size=100)
db = GameDatabase()
ai_processor = AdvancedAIProcessor(pattern_matrix, dynamic_weighting)

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
        "version": "2.2.0",
        "optimization": "Force Prediction & Alternative Logic Search"
    }

@app.post("/predict")
def get_prediction(request: PredictionRequest):
    # Use Advanced AI Processor for optimized prediction and confidence
    # UPDATED: Now returns a dict with more info including warning_color
    result = ai_processor.get_optimized_prediction(
        request.history, request.sensor_outputs
    )
    
    final_pred = result["prediction"]
    optimized_conf = result["confidence"]
    is_inverted = result["is_inverted"]
    warning_color = result["warning_color"]
    logic_used = result["logic_used"]
    
    # Check Recovery Mode (Using optimized confidence)
    # UPDATED: should_signal is now always True (No "Wait" mode)
    bet_amount, should_signal = recovery.get_bet_strategy(optimized_conf)
    
    # Get Heatmap Data
    heatmap_data = heatmap.get_heatmap_data()
    
    return {
        "period": request.period,
        "prediction": final_pred,
        "confidence": round(optimized_conf, 2),
        "bet_amount": bet_amount,
        "should_signal": should_signal, # Always True now
        "heatmap": heatmap_data,
        "is_inverted": is_inverted,
        "warning_color": warning_color, # New: Orange for high risk, Green for low risk
        "logic_used": logic_used,
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
