from fastapi import APIRouter, HTTPException, Depends
from app.models import BacktestRequest, BacktestResult
from app.services.backtest import LeapStrategyBacktester
from app.services.monte_carlo import MonteCarloSimulator
from app.database import Strategy, init_db
from app.schemas import StrategyCreate, StrategyResponse
import traceback
import json

router = APIRouter()

# Ensure DB is initialized
init_db()

@router.post("/backtest/run", response_model=BacktestResult)
async def run_backtest(request: BacktestRequest):
    try:
        if request.use_simulation and request.simulation_runs > 1:
            simulator = MonteCarloSimulator(request)
            result = simulator.run_monte_carlo()
        else:
            backtester = LeapStrategyBacktester(request)
            result = backtester.run()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/strategies", response_model=list[StrategyResponse])
async def get_strategies():
    strategies = Strategy.select().order_by(Strategy.created_at.desc())
    return [
        StrategyResponse(
            id=s.id,
            name=s.name,
            description=s.description,
            parameters=json.loads(s.parameters),
            created_at=str(s.created_at)
        ) for s in strategies
    ]

@router.post("/strategies", response_model=StrategyResponse)
async def create_strategy(strategy: StrategyCreate):
    try:
        new_strategy = Strategy.create(
            name=strategy.name,
            description=strategy.description,
            parameters=json.dumps(strategy.parameters)
        )
        return StrategyResponse(
            id=new_strategy.id,
            name=new_strategy.name,
            description=new_strategy.description,
            parameters=strategy.parameters,
            created_at=str(new_strategy.created_at)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/strategies/{id}")
async def delete_strategy(id: int):
    try:
        query = Strategy.delete().where(Strategy.id == id)
        rows = query.execute()
        if rows == 0:
            raise HTTPException(status_code=404, detail="Strategy not found")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "ok"}
