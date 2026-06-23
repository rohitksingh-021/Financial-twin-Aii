from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class RiskAppetite(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class CustomerProfile(BaseModel):
    name: str = "Rahul Sharma"
    age: int = 32
    gender: str = "Male"
    occupation: str = "Software Engineer"
    employer: str = "TCS"
    annual_income: float = 1800000
    monthly_income: float = 150000
    city: str = "Mumbai"
    family_size: int = 3
    dependents: int = 1
    risk_appetite: RiskAppetite = RiskAppetite.MODERATE
    pan_number: str = "ABCPS1234K"
    account_number: str = "IDBI0012345678"


class Transaction(BaseModel):
    date: str
    amount: float
    category: str
    merchant: str = ""
    type: str  # "credit" or "debit"
    channel: str = "UPI"  # UPI, card, NEFT, IMPS, cash


class Investment(BaseModel):
    id: str = ""
    type: str  # MF, FD, stocks, PPF, NPS, gold
    name: str
    invested_amount: float
    current_value: float
    start_date: str
    expected_return: float  # annual % e.g. 12.0


class Loan(BaseModel):
    id: str = ""
    type: str  # home, personal, car, education
    principal: float
    outstanding: float
    emi: float
    tenure_remaining: int  # months
    interest_rate: float


class Insurance(BaseModel):
    id: str = ""
    type: str  # life, health, term, vehicle
    provider: str = ""
    sum_assured: float
    annual_premium: float
    expiry_date: str = ""


class Goal(BaseModel):
    id: str = ""
    name: str
    target_amount: float
    current_amount: float
    deadline: str  # YYYY-MM-DD
    priority: int = Field(default=3, ge=1, le=5)


class MonthlyFinancial(BaseModel):
    month: str  # YYYY-MM
    income: float
    rent: float = 0
    groceries: float = 0
    utilities: float = 0
    transport: float = 0
    entertainment: float = 0
    healthcare: float = 0
    education: float = 0
    shopping: float = 0
    emi_total: float = 0
    investments: float = 0
    other: float = 0

    @property
    def total_expenses(self) -> float:
        return (self.rent + self.groceries + self.utilities + self.transport +
                self.entertainment + self.healthcare + self.education +
                self.shopping + self.emi_total + self.other)

    @property
    def savings(self) -> float:
        return self.income - self.total_expenses - self.investments


class CustomerData(BaseModel):
    profile: CustomerProfile = Field(default_factory=CustomerProfile)
    transactions: list[Transaction] = Field(default_factory=list)
    investments: list[Investment] = Field(default_factory=list)
    loans: list[Loan] = Field(default_factory=list)
    insurance: list[Insurance] = Field(default_factory=list)
    goals: list[Goal] = Field(default_factory=list)
    monthly_financials: list[MonthlyFinancial] = Field(default_factory=list)
