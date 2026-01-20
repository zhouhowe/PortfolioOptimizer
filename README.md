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
- **Experimental Frontend**: Marimo Notebook.
- **Dependency Management**: uv.

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 16+
- uv (Python package manager)

### Backend Setup (using uv)
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Sync dependencies:
   ```bash
   uv sync
   ```
3. Run the server:
   ```bash
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   The API will be available at `http://localhost:8000`.

### Marimo Frontend (Lightweight)
For quick experimentation and interactive visualization:
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Run the Marimo notebook:
   ```bash
   uv run marimo edit notebooks/dashboard.py
   ```
   This will open a browser window with the interactive dashboard.

### React Frontend Setup
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
1. Open the frontend (React or Marimo) in your browser.
2. Configure your strategy parameters (Target Equity, Allocation, LEAP details, Rebalancing rules).
3. Click "Run Strategy Backtest" (or "Run Backtest" in Marimo).
4. Analyze the results (Return, CAGR, Drawdown, Trade History).
