"""Simulator route."""

from fastapi import APIRouter
from pydantic import BaseModel
from store.data_store import store
from engines.simulator_engine import run_simulation, get_available_scenarios

router = APIRouter()


class SimulationRequest(BaseModel):
    scenario: str
    params: dict = {}


@router.post("/simulator")
def simulate(req: SimulationRequest):
    data = store.get_customer()
    return run_simulation(data, req.scenario, req.params)


@router.get("/simulator/scenarios")
def list_scenarios():
    return get_available_scenarios()
