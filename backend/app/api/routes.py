from fastapi import APIRouter, HTTPException
from app.models import BacktestRequest, BacktestResult
from app.services.backtest import LeapStrategyBacktester
import traceback

router = APIRouter()

@router.post("/backtest/run", response_model=BacktestResult)
async def run_backtest(request: BacktestRequest):
    try:
        backtester = LeapStrategyBacktester(request)
        result = backtester.run()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/health")
async def health_check():
    return {"status": "ok"}
