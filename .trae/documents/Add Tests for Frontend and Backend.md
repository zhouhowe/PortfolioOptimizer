I will set up testing frameworks and add critical tests for both the backend (using `pytest`) and frontend (using `vitest`).

## Backend Testing (Pytest)
1.  **Setup**: Install `pytest` using `uv`.
2.  **Unit Tests (`backend/tests/`)**:
    -   `test_option_pricing.py`: Validate Black-Scholes formulas (Call/Put prices, Greeks) against known values.
    -   `test_simulator.py`: Verify `MarketSimulator` generates data with correct dimensions and statistical properties (drift/volatility).
    -   `test_backtest.py`: Test `LeapStrategyBacktester` initialization and core logic (e.g., rebalancing checks).

## Frontend Testing (Vitest + React Testing Library)
1.  **Setup**:
    -   Install `vitest`, `jsdom`, `@testing-library/react`, and `@testing-library/jest-dom`.
    -   Configure `vite.config.js` for the test environment.
    -   Create `frontend/src/setupTests.js` for global test configuration.
2.  **Component Tests (`frontend/src/components/`)**:
    -   `Dashboard.test.jsx`: Verify form rendering, input updates, and submission handling.
    -   `Results.test.jsx`: Ensure results and charts render correctly with sample data.
