# Self-Learning AI Backend

This is a high-performance AI backend designed for game prediction with self-learning capabilities.

## Features

### 1. Pattern Error Matrix (Self-Learning)
The system tracks patterns and their outcomes. If the AI detects that a specific pattern frequently leads to a wrong prediction, it automatically **inverts** its logic for that pattern to stay ahead of the game's algorithm.

### 2. Dynamic Weighting (Sensor Control)
Multiple sensors (CID, Dragon, Trend) are evaluated in real-time. Sensors that perform well gain more influence, while underperforming ones lose weight. The final prediction is a weighted consensus.

### 3. Martingale-Safe Recovery
A smart recovery system that calculates the necessary bet to recover losses. It only issues a signal when the AI's confidence level is above **85%**, ensuring a safer recovery process.

### 4. Live Market Heatmap
Provides a visual statistical distribution of 'Big' vs 'Small' outcomes over a sliding window, helping users understand market trends.

## API Endpoints

- `POST /predict`: Get the next prediction based on history and sensor data.
- `POST /update`: Feed the actual outcome back into the system for learning.
- `GET /stats`: View current sensor weights and market heatmap.

## Setup
1. Install dependencies: `pip install fastapi uvicorn`
2. Run the server: `python main.py`
