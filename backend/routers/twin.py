"""Financial Twin route."""

from fastapi import APIRouter
from store.data_store import store
from engines.twin_engine import build_twin

router = APIRouter()


@router.get("/twin")
def get_twin():
    data = store.get_customer()
    return build_twin(data)
