# Strategy Optimizer (P0)

A web application to back-test LEAP options strategies combined with equity positions.

## Features (P0)
- **LEAP Strategy Backtesting**: Test strategies with LEAP calls + Equity + Cash.
- **Rebalancing**: Automated rebalancing based on allocation drift and price movements.
- **Profit/Loss Management**: Configurable rules for closing positions based on P/L and time to expiry.
- **Visualizations**: Interactive charts for portfolio performance and drawdown.
- **Trade History**: Detailed log of all trades executed during the backtest.

## Tech Stack
- **Backend**: Python, FastAPI, Pandas, NumPy, SciPy (Black-Scholes Model), yfinance.
- **Frontend**: React, Vite, Tailwind CSS, Chart.js.

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:5173`.

## Usage
1. Open the frontend in your browser.
2. Configure your strategy parameters (Target Equity, Allocation, LEAP details, Rebalancing rules).
3. Click "Run Strategy Backtest".
4. Analyze the results (Return, CAGR, Drawdown, Trade History).
