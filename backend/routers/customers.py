"""Customer data CRUD routes — used by Judge Mode data input panel."""

from fastapi import APIRouter
from models.customer import CustomerData
from store.data_store import store

router = APIRouter()


@router.get("/customer")
def get_customer():
    """Get current customer data."""
    data = store.get_customer()
    return data.model_dump()


@router.post("/customer")
def set_customer(data: CustomerData):
    """Set complete customer data (from Judge Mode input)."""
    store.set_customer(data)
    return {"status": "success", "message": f"Financial Twin built for {data.profile.name}"}


@router.post("/customer/reset")
def reset_customer():
    """Reset to default Rahul Sharma data."""
    store.reset()
    data = store.get_customer()
    return {"status": "success", "message": "Reset to Rahul Sharma", "name": data.profile.name}


@router.get("/customer/template")
def get_template():
    """Get an empty customer data template with field descriptions."""
    return {
        "profile": {
            "name": "", "age": 30, "gender": "Male",
            "occupation": "", "employer": "",
            "annual_income": 0, "monthly_income": 0,
            "city": "", "family_size": 1, "dependents": 0,
            "risk_appetite": "moderate",
            "pan_number": "", "account_number": "",
        },
        "monthly_financials": [],
        "investments": [],
        "loans": [],
        "insurance": [],
        "goals": [],
        "transactions": [],
    }
