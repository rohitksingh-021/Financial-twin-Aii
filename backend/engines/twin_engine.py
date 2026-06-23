"""Financial Twin Engine — builds financial projections and trajectory analysis."""

from models.customer import CustomerData
import statistics
import math


def build_twin(data: CustomerData) -> dict:
    mf = data.monthly_financials
    if not mf:
        return _empty_twin()

    current = _current_state(data)
    projections = _build_projections(data)
    trajectory = _build_trajectory(data)
    data_sources = _get_data_sources(data)

    return {
        "current_state": current,
        "projections": projections,
        "trajectory": trajectory,
        "data_sources": data_sources,
        "opportunities": _detect_opportunities(data),
    }


def _current_state(data: CustomerData) -> dict:
    mf = data.monthly_financials
    total_investments = sum(inv.current_value for inv in data.investments)
    total_debt = sum(loan.outstanding for loan in data.loans)
    avg_income = statistics.mean([m.income for m in mf]) if mf else 0
    avg_expenses = statistics.mean([m.total_expenses for m in mf]) if mf else 0
    avg_savings = avg_income - avg_expenses - (statistics.mean([m.investments for m in mf]) if mf else 0)
    avg_investments_monthly = statistics.mean([m.investments for m in mf]) if mf else 0

    net_worth = total_investments - total_debt + max(0, avg_savings * 3)  # approx liquid cash

    return {
        "net_worth": round(net_worth),
        "total_investments": round(total_investments),
        "total_debt": round(total_debt),
        "monthly_income": round(avg_income),
        "monthly_expenses": round(avg_expenses),
        "monthly_savings": round(avg_savings),
        "monthly_investments": round(avg_investments_monthly),
        "savings_rate": round((avg_savings + avg_investments_monthly) / avg_income * 100, 1) if avg_income > 0 else 0,
        "debt_to_income": round(total_debt / (avg_income * 12) * 100, 1) if avg_income > 0 else 0,
        "investment_portfolio": [
            {"type": inv.type, "name": inv.name, "value": inv.current_value, "return": inv.expected_return}
            for inv in data.investments
        ],
    }


def _build_projections(data: CustomerData) -> dict:
    """Project financial state at 1yr, 3yr, 5yr, 10yr."""
    mf = data.monthly_financials
    if not mf:
        return {}

    avg_income = statistics.mean([m.income for m in mf])
    avg_expenses = statistics.mean([m.total_expenses for m in mf])
    avg_investments = statistics.mean([m.investments for m in mf])
    total_inv_value = sum(inv.current_value for inv in data.investments)
    total_debt = sum(loan.outstanding for loan in data.loans)

    # Growth assumptions
    income_growth = 0.08  # 8% annual
    expense_inflation = 0.06  # 6% annual
    investment_return = 0.11  # 11% annual (blended)

    # Calculate weighted average return from portfolio
    if data.investments:
        total_invested = sum(inv.current_value for inv in data.investments)
        if total_invested > 0:
            investment_return = sum(inv.current_value * inv.expected_return / 100 for inv in data.investments) / total_invested

    projections = {}
    for years in [1, 3, 5, 10]:
        future_income = avg_income * ((1 + income_growth) ** years)
        future_expenses = avg_expenses * ((1 + expense_inflation) ** years)
        future_monthly_invest = avg_investments * ((1 + income_growth) ** years) * 0.9

        # Investment corpus growth (existing + new monthly)
        existing_growth = total_inv_value * ((1 + investment_return) ** years)
        # Future value of SIP (monthly annuity)
        monthly_rate = investment_return / 12
        months = years * 12
        if monthly_rate > 0:
            sip_fv = avg_investments * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
        else:
            sip_fv = avg_investments * months

        total_future_investments = existing_growth + sip_fv

        # Debt repayment
        remaining_debt = 0
        for loan in data.loans:
            months_left = loan.tenure_remaining - (years * 12)
            if months_left > 0:
                remaining_debt += loan.emi * months_left * 0.5  # rough outstanding
            # else: loan fully paid off

        future_net_worth = total_future_investments - remaining_debt

        projections[f"{years}yr"] = {
            "net_worth": round(future_net_worth),
            "monthly_income": round(future_income),
            "monthly_expenses": round(future_expenses),
            "total_investments": round(total_future_investments),
            "total_debt": round(remaining_debt),
            "monthly_savings": round(future_income - future_expenses - future_monthly_invest),
            "savings_rate": round((future_income - future_expenses) / future_income * 100, 1) if future_income > 0 else 0,
        }

    return projections


def _build_trajectory(data: CustomerData) -> dict:
    """Build monthly trajectory for 10 years in 3 scenarios."""
    mf = data.monthly_financials
    if not mf:
        return {"optimistic": [], "realistic": [], "pessimistic": []}

    avg_income = statistics.mean([m.income for m in mf])
    avg_investments = statistics.mean([m.investments for m in mf])
    total_inv = sum(inv.current_value for inv in data.investments)

    scenarios = {
        "optimistic": {"income_growth": 0.12, "return": 0.14, "expense_inflation": 0.05},
        "realistic": {"income_growth": 0.08, "return": 0.11, "expense_inflation": 0.06},
        "pessimistic": {"income_growth": 0.04, "return": 0.07, "expense_inflation": 0.08},
    }

    result = {}
    for scenario_name, params in scenarios.items():
        points = []
        corpus = total_inv
        monthly_invest = avg_investments

        for month in range(0, 121, 3):  # every 3 months for 10 years
            year_frac = month / 12
            monthly_return = params["return"] / 12
            corpus = corpus * (1 + monthly_return * 3)
            monthly_invest *= (1 + params["income_growth"] / 12 * 3)
            corpus += monthly_invest * 3

            points.append({
                "month": month,
                "year": round(year_frac, 1),
                "net_worth": round(corpus),
            })

        result[scenario_name] = points

    return result


def _get_data_sources(data: CustomerData) -> list[dict]:
    sources = [
        {"name": "Bank Transactions", "status": "active", "records": len(data.transactions)},
        {"name": "Salary Data", "status": "active", "records": len([t for t in data.transactions if t.category == "Salary"])},
        {"name": "Investment Portfolio", "status": "active", "records": len(data.investments)},
        {"name": "Loan Records", "status": "active", "records": len(data.loans)},
        {"name": "Insurance Data", "status": "active", "records": len(data.insurance)},
        {"name": "UPI Activity", "status": "active", "records": len([t for t in data.transactions if t.channel == "UPI"])},
        {"name": "Monthly Financials", "status": "active", "records": len(data.monthly_financials)},
        {"name": "Goal Preferences", "status": "active", "records": len(data.goals)},
    ]
    return sources


def _detect_opportunities(data: CustomerData) -> list[dict]:
    opportunities = []
    mf = data.monthly_financials

    if not mf:
        return opportunities

    avg_income = statistics.mean([m.income for m in mf])
    avg_expenses = statistics.mean([m.total_expenses for m in mf])
    avg_investments = statistics.mean([m.investments for m in mf])
    free_cash = avg_income - avg_expenses - avg_investments

    # Idle balance opportunity
    if free_cash > avg_expenses * 0.3:
        opportunities.append({
            "title": "Idle Balance Optimization",
            "description": f"₹{free_cash:,.0f}/month in idle savings could earn more in a liquid fund or FD.",
            "impact": f"₹{free_cash * 12 * 0.07:,.0f}/year potential earnings",
            "priority": "high",
            "category": "invest",
        })

    # Investment diversification
    inv_types = set(inv.type for inv in data.investments)
    if "gold" not in inv_types and len(data.investments) > 0:
        opportunities.append({
            "title": "Add Gold Allocation",
            "description": "Portfolio lacks gold exposure. Consider 5-10% allocation for diversification.",
            "impact": "Reduced portfolio volatility by ~8%",
            "priority": "medium",
            "category": "invest",
        })

    # Insurance gap
    life_cover = sum(i.sum_assured for i in data.insurance if i.type in ("term", "life"))
    if life_cover < data.profile.annual_income * 10:
        gap = data.profile.annual_income * 10 - life_cover
        opportunities.append({
            "title": "Increase Life Cover",
            "description": f"Current cover is {life_cover/data.profile.annual_income:.0f}x income. Recommend 10x. Gap: ₹{gap:,.0f}.",
            "impact": "Complete family financial protection",
            "priority": "high",
            "category": "protect",
        })

    health_cover = sum(i.sum_assured for i in data.insurance if i.type == "health")
    if health_cover < 1000000:
        opportunities.append({
            "title": "Upgrade Health Insurance",
            "description": f"Current health cover ₹{health_cover:,.0f} may be insufficient. Consider ₹10-15L super top-up.",
            "impact": "Protection against medical inflation",
            "priority": "high",
            "category": "protect",
        })

    # Tax saving
    ppf_inv = sum(i.invested_amount for i in data.investments if i.type == "PPF")
    nps_inv = sum(i.invested_amount for i in data.investments if i.type == "NPS")
    total_80c = ppf_inv + nps_inv + sum(i.annual_premium for i in data.insurance if i.type in ("term", "life"))
    if total_80c < 150000:
        gap = 150000 - total_80c
        opportunities.append({
            "title": "Tax Saving Opportunity (80C)",
            "description": f"₹{gap:,.0f} remaining in 80C limit. Consider ELSS funds or additional PPF contribution.",
            "impact": f"Tax saving of ~₹{gap * 0.3:,.0f} (30% bracket)",
            "priority": "medium",
            "category": "save",
        })

    return opportunities


def _empty_twin() -> dict:
    return {
        "current_state": {
            "net_worth": 0, "total_investments": 0, "total_debt": 0,
            "monthly_income": 0, "monthly_expenses": 0, "monthly_savings": 0,
            "monthly_investments": 0, "savings_rate": 0, "debt_to_income": 0,
            "investment_portfolio": [],
        },
        "projections": {},
        "trajectory": {"optimistic": [], "realistic": [], "pessimistic": []},
        "data_sources": [],
        "opportunities": [],
    }
