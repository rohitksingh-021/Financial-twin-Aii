"""Simulator Engine — runs what-if financial scenarios and computes impact across all dimensions."""

from models.customer import CustomerData
from engines.vitality_engine import compute_vitality_score
from engines.twin_engine import build_twin
import statistics
import copy


SCENARIO_CONFIGS = {
    "buy_car": {
        "label": "Buy a Car",
        "description": "Purchase a car with down payment and auto loan.",
        "default_params": {"amount": 2500000, "down_payment_pct": 20, "loan_tenure_months": 60, "interest_rate": 9.5},
    },
    "increase_sip": {
        "label": "Increase Monthly SIP",
        "description": "Increase your monthly systematic investment.",
        "default_params": {"additional_amount": 10000},
    },
    "job_loss": {
        "label": "Job Loss Scenario",
        "description": "Simulate income loss for a period.",
        "default_params": {"months_without_income": 6},
    },
    "early_retirement": {
        "label": "Early Retirement",
        "description": "Stop earning income at a specific age.",
        "default_params": {"retirement_age": 50},
    },
    "salary_hike": {
        "label": "Salary Hike",
        "description": "Simulate a salary increase.",
        "default_params": {"hike_percentage": 30},
    },
    "large_expense": {
        "label": "Large One-time Expense",
        "description": "A major unplanned expense.",
        "default_params": {"amount": 500000},
    },
    "inflation_change": {
        "label": "Inflation Scenario",
        "description": "What if inflation increases significantly?",
        "default_params": {"new_inflation_rate": 10},
    },
}


def run_simulation(data: CustomerData, scenario: str, params: dict) -> dict:
    """Run a what-if simulation and compute impact."""

    config = SCENARIO_CONFIGS.get(scenario, {})
    merged_params = {**config.get("default_params", {}), **params}

    # Compute baseline
    baseline_vitality = compute_vitality_score(data)
    baseline_twin = build_twin(data)

    # Create modified data
    modified_data = _apply_scenario(data, scenario, merged_params)

    # Compute modified state
    modified_vitality = compute_vitality_score(modified_data)
    modified_twin = build_twin(modified_data)

    # Compute deltas
    wealth_impact = _compute_wealth_impact(baseline_twin, modified_twin)
    goal_impact = _compute_goal_impact(data, modified_data)
    vitality_impact = _compute_vitality_impact(baseline_vitality, modified_vitality)

    # Generate 3 scenarios
    scenarios = _generate_three_scenarios(data, scenario, merged_params, baseline_twin)

    # AI verdict
    verdict = _generate_verdict(scenario, merged_params, wealth_impact, vitality_impact, goal_impact)

    return {
        "scenario": scenario,
        "label": config.get("label", scenario),
        "description": config.get("description", ""),
        "params": merged_params,
        "baseline": {
            "vitality_score": baseline_vitality["overall"],
            "net_worth": baseline_twin["current_state"]["net_worth"],
            "monthly_savings": baseline_twin["current_state"]["monthly_savings"],
            "net_worth_5yr": baseline_twin["projections"].get("5yr", {}).get("net_worth", 0),
        },
        "modified": {
            "vitality_score": modified_vitality["overall"],
            "net_worth": modified_twin["current_state"]["net_worth"],
            "monthly_savings": modified_twin["current_state"]["monthly_savings"],
            "net_worth_5yr": modified_twin["projections"].get("5yr", {}).get("net_worth", 0),
        },
        "impact": {
            "wealth": wealth_impact,
            "goals": goal_impact,
            "vitality": vitality_impact,
        },
        "scenarios": scenarios,
        "verdict": verdict,
    }


def get_available_scenarios() -> list[dict]:
    return [
        {"id": k, "label": v["label"], "description": v["description"], "default_params": v["default_params"]}
        for k, v in SCENARIO_CONFIGS.items()
    ]


def _apply_scenario(data: CustomerData, scenario: str, params: dict) -> CustomerData:
    """Create a modified copy of customer data based on the scenario."""
    modified = data.model_copy(deep=True)

    if scenario == "buy_car":
        amount = params.get("amount", 2500000)
        down_pct = params.get("down_payment_pct", 20) / 100
        tenure = params.get("loan_tenure_months", 60)
        rate = params.get("interest_rate", 9.5) / 100 / 12

        down_payment = amount * down_pct
        loan_amount = amount - down_payment
        emi = loan_amount * rate * ((1 + rate) ** tenure) / (((1 + rate) ** tenure) - 1)

        # Reduce investments by down payment
        total_inv = sum(inv.current_value for inv in modified.investments)
        if total_inv > 0:
            ratio = max(0, 1 - down_payment / total_inv)
            for inv in modified.investments:
                inv.current_value = round(inv.current_value * ratio)
                inv.invested_amount = round(inv.invested_amount * ratio)

        # Add car loan
        from models.customer import Loan
        modified.loans.append(Loan(
            id="sim-car", type="car", principal=loan_amount,
            outstanding=loan_amount, emi=round(emi),
            tenure_remaining=tenure, interest_rate=params.get("interest_rate", 9.5)
        ))

        # Update monthly financials (add EMI, reduce investments)
        for mf in modified.monthly_financials:
            mf.emi_total += round(emi)
            mf.investments = max(0, mf.investments - round(emi * 0.5))

    elif scenario == "increase_sip":
        additional = params.get("additional_amount", 10000)
        for mf in modified.monthly_financials:
            mf.investments += additional

    elif scenario == "job_loss":
        months = params.get("months_without_income", 6)
        # Zero out income for last N months of data
        for mf in modified.monthly_financials[-months:]:
            mf.income = 0

    elif scenario == "early_retirement":
        # Reduce projected income years
        ret_age = params.get("retirement_age", 50)
        years_left = ret_age - data.profile.age
        # Modify by reducing projected income (reflected in twin)
        # For simplicity, reduce all incomes by proportion
        factor = years_left / (60 - data.profile.age) if data.profile.age < 60 else 0.5
        for mf in modified.monthly_financials:
            mf.income = round(mf.income * max(0.3, factor))

    elif scenario == "salary_hike":
        hike = params.get("hike_percentage", 30) / 100
        for mf in modified.monthly_financials:
            mf.income = round(mf.income * (1 + hike))
        modified.profile.monthly_income = round(modified.profile.monthly_income * (1 + hike))
        modified.profile.annual_income = round(modified.profile.annual_income * (1 + hike))

    elif scenario == "large_expense":
        amount = params.get("amount", 500000)
        # Deduct from investments
        total_inv = sum(inv.current_value for inv in modified.investments)
        if total_inv > 0:
            ratio = max(0, 1 - amount / total_inv)
            for inv in modified.investments:
                inv.current_value = round(inv.current_value * ratio)

    elif scenario == "inflation_change":
        new_rate = params.get("new_inflation_rate", 10) / 100
        base_rate = 0.06
        multiplier = (1 + new_rate) / (1 + base_rate)
        for mf in modified.monthly_financials:
            mf.rent = round(mf.rent * multiplier)
            mf.groceries = round(mf.groceries * multiplier)
            mf.utilities = round(mf.utilities * multiplier)
            mf.transport = round(mf.transport * multiplier)
            mf.entertainment = round(mf.entertainment * multiplier)
            mf.healthcare = round(mf.healthcare * multiplier)
            mf.other = round(mf.other * multiplier)

    return modified


def _compute_wealth_impact(baseline, modified):
    b_nw = baseline["current_state"]["net_worth"]
    m_nw = modified["current_state"]["net_worth"]
    b_5yr = baseline["projections"].get("5yr", {}).get("net_worth", 0)
    m_5yr = modified["projections"].get("5yr", {}).get("net_worth", 0)

    return {
        "net_worth_change": round(m_nw - b_nw),
        "net_worth_change_pct": round((m_nw - b_nw) / b_nw * 100, 1) if b_nw != 0 else 0,
        "net_worth_5yr_change": round(m_5yr - b_5yr),
        "monthly_savings_change": round(
            modified["current_state"]["monthly_savings"] - baseline["current_state"]["monthly_savings"]
        ),
    }


def _compute_goal_impact(baseline_data, modified_data):
    from engines.gps_engine import compute_wealth_gps
    baseline_goals = compute_wealth_gps(baseline_data)
    modified_goals = compute_wealth_gps(modified_data)

    impacts = []
    for bg, mg in zip(baseline_goals, modified_goals):
        impacts.append({
            "goal": bg["name"],
            "baseline_probability": bg["probability"],
            "modified_probability": mg["probability"],
            "change": round(mg["probability"] - bg["probability"], 1),
            "baseline_eta": bg["eta"],
            "modified_eta": mg["eta"],
        })
    return impacts


def _compute_vitality_impact(baseline, modified):
    return {
        "overall_change": round(modified["overall"] - baseline["overall"], 1),
        "sub_score_changes": {
            k: round(modified["sub_scores"][k] - baseline["sub_scores"][k], 1)
            for k in baseline["sub_scores"]
        },
    }


def _generate_three_scenarios(data, scenario, params, baseline_twin):
    b_nw_5yr = baseline_twin["projections"].get("5yr", {}).get("net_worth", 0)

    # Optimistic: better returns, income growth
    optimistic_nw = b_nw_5yr * 1.15
    # Realistic: baseline impact
    realistic_nw = b_nw_5yr * 0.95
    # Pessimistic: worse returns, expenses up
    pessimistic_nw = b_nw_5yr * 0.75

    if scenario in ("increase_sip", "salary_hike"):
        optimistic_nw = b_nw_5yr * 1.35
        realistic_nw = b_nw_5yr * 1.20
        pessimistic_nw = b_nw_5yr * 1.05
    elif scenario in ("buy_car", "large_expense"):
        optimistic_nw = b_nw_5yr * 0.92
        realistic_nw = b_nw_5yr * 0.82
        pessimistic_nw = b_nw_5yr * 0.68
    elif scenario == "job_loss":
        optimistic_nw = b_nw_5yr * 0.85
        realistic_nw = b_nw_5yr * 0.70
        pessimistic_nw = b_nw_5yr * 0.50

    return {
        "optimistic": {
            "label": "Best Case",
            "net_worth_5yr": round(optimistic_nw),
            "description": _scenario_desc(scenario, "optimistic"),
        },
        "realistic": {
            "label": "Most Likely",
            "net_worth_5yr": round(realistic_nw),
            "description": _scenario_desc(scenario, "realistic"),
        },
        "pessimistic": {
            "label": "Worst Case",
            "net_worth_5yr": round(pessimistic_nw),
            "description": _scenario_desc(scenario, "pessimistic"),
        },
    }


def _scenario_desc(scenario, variant):
    descs = {
        "buy_car": {
            "optimistic": "Car purchased, income grows well, investments recover quickly.",
            "realistic": "Car EMI impacts savings moderately, goals delayed 6-12 months.",
            "pessimistic": "High EMI strain, emergency fund depleted, multiple goals at risk.",
        },
        "increase_sip": {
            "optimistic": "Higher investments compound well, goals reached ahead of schedule.",
            "realistic": "Steady growth, improved goal completion by 15-20%.",
            "pessimistic": "Market underperforms, but disciplined investing still adds value.",
        },
        "job_loss": {
            "optimistic": "Quick re-employment within 2 months, minimal impact.",
            "realistic": "4-6 month gap, emergency fund depleted, goals delayed 1-2 years.",
            "pessimistic": "Extended unemployment, forced liquidation of investments.",
        },
        "salary_hike": {
            "optimistic": "Higher savings rate maintained, accelerated wealth building.",
            "realistic": "Lifestyle inflation absorbs 50% of hike, net positive.",
            "pessimistic": "Lifestyle inflation absorbs most of hike, minimal improvement.",
        },
    }
    return descs.get(scenario, {}).get(variant, "Scenario outcome based on market conditions and personal behavior.")


def _generate_verdict(scenario, params, wealth_impact, vitality_impact, goal_impact):
    # Determine recommendation
    nw_change = wealth_impact["net_worth_change"]
    vitality_change = vitality_impact["overall_change"]

    if vitality_change >= 5:
        recommendation = "Strongly Recommended"
        confidence = 85
        reasoning = "This action significantly improves your financial health."
    elif vitality_change >= 0:
        recommendation = "Recommended with Caution"
        confidence = 70
        reasoning = "Positive overall impact, but monitor cash flow closely."
    elif vitality_change >= -5:
        recommendation = "Proceed Carefully"
        confidence = 60
        reasoning = "Minor negative impact on financial health. Ensure adequate emergency fund."
    else:
        recommendation = "Not Recommended Currently"
        confidence = 75
        reasoning = "Significant negative impact on financial trajectory. Consider delaying or scaling down."

    # Check goal impacts
    goals_at_risk = [g for g in goal_impact if g["change"] < -10]
    if goals_at_risk:
        reasoning += f" {len(goals_at_risk)} goal(s) would be significantly delayed."

    return {
        "recommendation": recommendation,
        "confidence": confidence,
        "reasoning": reasoning,
        "vitality_change": vitality_change,
        "wealth_change_5yr": wealth_impact["net_worth_5yr_change"],
        "goals_at_risk": len(goals_at_risk),
    }
