# Self-Learning AI Backend (Optimized)

This is an optimized and enhanced Self-Learning AI Backend designed for advanced game prediction, now migrated to FastAPI for improved performance and real-time data processing. It incorporates sophisticated self-correction mechanisms, dynamic sensor weighting, a safe recovery strategy, and live market trend visualization.

## Features

### 1. Pattern Error Matrix (Self-Correction with 3-Loss Inversion)
The system intelligently tracks prediction patterns. If a specific pattern leads to **three consecutive incorrect predictions**, the AI automatically activates an **inversion logic** for that pattern. This means for future occurrences of that pattern, the system will intentionally reverse its prediction, effectively learning from its persistent errors and adapting to game algorithm changes.

### 2. Dynamic Weighting (Sensor Control with 5-Round Update)
This feature dynamically adjusts the influence of different prediction "sensors" (e.g., CID Sensor, Dragon Logic, Trend Sensor) based on their real-time performance. Sensor weights are updated every **five rounds**, giving more prominence to sensors that are currently demonstrating higher accuracy. This ensures the final prediction is always driven by the most successful data sources.

### 3. Martingale-Safe Recovery Logic
Designed to manage and recover from losses, this system only triggers a recovery bet when the AI's confidence score, derived from the Dynamic Weighting system, is **above 85%**. This critical safety threshold prevents aggressive recovery attempts during uncertain market conditions, promoting a more secure and strategic approach to recouping losses.

### 4. Live Market Heatmap and Status API
The backend provides a `/stats` API endpoint that delivers real-time data for a **Live Market Heatmap**. This visual tool allows users to graphically observe the trend of 'Big' versus 'Small' outcomes over the last 100 rounds, enhancing transparency and user trust by providing immediate insights into market dynamics.

### 5. FastAPI Optimization
The entire backend has been migrated from Flask to **FastAPI**. This transition significantly improves data processing speed, reduces latency, and provides a more robust and scalable foundation for real-time game data analysis and prediction.

## API Endpoints

- `POST /predict`: Receives current game history and sensor outputs, returning the AI's next prediction, confidence level, suggested bet amount (if recovery is active and confidence is high), heatmap data, and inversion status.
- `POST /update`: Used to feed the actual outcome of a game back into the system. This endpoint triggers updates for the Pattern Error Matrix, Dynamic Weighting, Martingale-Safe Recovery, and Live Market Heatmap, facilitating continuous learning and adaptation.
- `GET /stats`: Provides comprehensive statistics including current sensor weights, live heatmap data, recovery mode status (current step, total loss, active status), and learning statistics (round counter, number of patterns learned).

## Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/ochenafanbangla-glitch/ai-self-learning-backend.git
   cd ai-self-learning-backend
   ```
2. **Install dependencies:**
   ```bash
   pip install fastapi uvicorn pydantic
   ```
3. **Run the server:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## Database
The system uses SQLite for persistent storage of game results and learning data. The `game_data.db`, `pattern_data.json`, and `sensor_weights.json` files are automatically created and managed by the application.

## Contributing
Feel free to fork the repository, submit pull requests, or report issues. Your contributions are welcome!
