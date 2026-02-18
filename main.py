from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
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
from ensemble_models import EnsembleManager

app = FastAPI(title="Self-Learning AI Backend (Advanced)")

# Initialize components
pattern_matrix = PatternErrorMatrix()
dynamic_weighting = DynamicWeighting(["CID Sensor", "Dragon Logic", "Trend Sensor"])
recovery = MartingaleRecovery(confidence_threshold=85.0) # Threshold updated to match percentage
heatmap = MarketHeatmap(window_size=100)
db = GameDatabase()
ai_processor = AdvancedAIProcessor(pattern_matrix, dynamic_weighting)
ensemble_manager = EnsembleManager()

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

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("index.html", "r") as f:
        return f.read()

@app.get("/api/status")
def get_api_status():
    return {
        "status": "AI Backend is running", 
        "version": "3.0.0",
        "optimization": "12-Model Ensemble Strategy"
    }

@app.post("/predict")
def get_prediction(request: PredictionRequest):
    # 1. Get Ensemble Prediction (Top 3 Models)
    ensemble_result = ensemble_manager.predict_ensemble(request.history)
    
    # 2. Get Advanced AI Processor prediction
    ai_result = ai_processor.get_optimized_prediction(
        request.history, request.sensor_outputs
    )
    
    # Hybrid Logic: If ensemble has high confidence, use it. Otherwise fallback to AI processor.
    if ensemble_result["confidence"] >= 66:
        final_pred = ensemble_result["prediction"]
        optimized_conf = ensemble_result["confidence"]
        logic_used = f"Ensemble ({', '.join(ensemble_result['models_used'])})"
    else:
        final_pred = ai_result["prediction"]
        optimized_conf = ai_result["confidence"]
        logic_used = ai_result["logic_used"]
    
    is_inverted = ai_result["is_inverted"]
    warning_color = ai_result["warning_color"]
    
    # Check Recovery Mode (Using optimized confidence)
    bet_amount, should_signal = recovery.get_bet_strategy(optimized_conf)
    
    # Get Heatmap Data
    heatmap_data = heatmap.get_heatmap_data()
    
    return {
        "period": request.period,
        "prediction": final_pred,
        "confidence": round(optimized_conf, 2),
        "bet_amount": bet_amount,
        "should_signal": should_signal,
        "heatmap": heatmap_data,
        "is_inverted": is_inverted,
        "warning_color": warning_color,
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
    
    # 5. Update Ensemble Models & Performance
    ensemble_manager.record_actual_outcome(request.period, request.history, request.actual_outcome)
    
    # 6. Save to Database
    db.save_result(
        request.period, 
        request.history, 
        request.prediction, 
        request.actual_outcome, 
        request.confidence, 
        request.bet_amount
    )
    
    # 7. Daily Cleanup
    ensemble_manager.cleanup_old_data(days=7)
    
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
        },
        "ensemble_stats": {
            "top_3": ensemble_manager.get_top_3(),
            "all_performances": {name: round(perf["accuracy"], 4) for name, perf in ensemble_manager.performance.items()}
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
