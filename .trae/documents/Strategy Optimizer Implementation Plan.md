# Implementation Plan: Completing Strategy Optimizer & P1 Features

Based on the review of the requirements and PRD, I have identified the following missing functionalities. The plan is prioritized by **Importance** (value to the user) and **Ease of Implementation** (speed to deliver).

## Missing Functionalities Summary

1. **Benchmark Comparison (P0)**: The PRD requires comparing the strategy performance against a benchmark (e.g., Buy & Hold of the target equity). Currently, we only show the portfolio value.
2. **Strategy Library & Persistence (P0/App Core)**: The PRD lists a "Strategy Library" to save, load, and compare strategies. Currently, the app is stateless; configurations are lost on refresh.
3. **Advanced Risk Analytics (P0)**: The PRD mentions tracking "Option Greeks exposure". Currently, we calculate Delta for pricing but do not visualize or track Greeks over time.
4. **Export Results (P0)**: The PRD requires exporting results to CSV.
5. **Wheel Strategy (P1)**: Selling Puts/Calls based on MA signals.
6. **Market Simulator (P1)**: Generating synthetic scenarios (Bear/Bull markets) using Random Walk models.

***

## Implementation Plan

### Phase 1: High-Value Visualizations (Quick Wins)

**Goal:** Provide immediate context to the backtest results.

1. **Implement Benchmark Comparison**

   * *Backend*: Calculate "Buy & Hold" performance series for the underlying equity in `LeapStrategyBacktester`.

   * *Frontend*: Overlay the Benchmark curve on the main Performance Chart in `Results.jsx`.
2. **Add Export Functionality**

   * *Frontend*: Add a "Download CSV" button to the Results page that converts the trade history and performance data to a CSV file.

### Phase 2: App Persistence (Strategy Library)

**Goal:** Transform the tool into a full application where users can save their work.
*Note: To keep the local setup simple without requiring external database credentials (Supabase), I will use* ***SQLite*** *for local persistence.*

1. **Backend Persistence Layer**

   * Set up SQLite database .

   * Create API endpoints: `GET /strategies`, `POST /strategies`, `DELETE /strategies/{id}`.
2. **Frontend Strategy Library**

   * Add "Save Strategy" button on Dashboard/Results.

   * Create a new "Strategy Library" page to list saved configurations.

   * Allow loading a saved strategy back into the Dashboard.

### Phase 3: P1 Features (Core Logic Expansion)

**Goal:** Implement the "Wheel Strategy" and "Simulator" requirements.

1. **Implement Wheel Strategy Logic**

   * Add Moving Average (MA) calculation indicators.

   * Implement logic to Sell Puts (when bullish/neutral) and Sell Calls (Covered Calls).

   * Integrate into the main backtest engine.
2. **Implement Market Simulator**

   * Create a `MarketSimulator` service using Geometric Brownian Motion (GBM).

   * Add a "Simulation Mode" toggle in the Dashboard to use synthetic data instead of `yfinance`.

### Phase 4: Advanced Analytics (Polish)

**Goal:** Deepen the financial analysis capabilities.

1. **Track & Visualize Greeks**

   * Log Delta, Gamma, Theta, and Vega in the `PortfolioSnapshot`.

   * Add a secondary chart in Results to show "Greeks Exposure over Time".

***

**Recommendation:** I suggest we start with **Phase 1 (Benchmark & Export)** as it provides immediate analytical value, followed by **Phase 2 (Persistence)** to solidify the app structure.
