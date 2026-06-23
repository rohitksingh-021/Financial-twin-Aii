"""Stress Analysis Engine — detects financial stress signals and predicts future stress levels."""

from models.customer import CustomerData
import statistics


def analyze_stress(data: CustomerData) -> dict:
    mf = data.monthly_financials
    if not mf:
        return _empty_stress()

    signals = _detect_signals(data)
    current_level = _compute_stress_level(signals)
    projections = _project_stress(data, current_level)
    actions = _generate_actions(signals, data)

    # Historical trend
    history = []
    for i in range(max(1, len(mf) - 5), len(mf) + 1):
        partial_mf = mf[:i]
        partial_data = CustomerData(
            profile=data.profile,
            monthly_financials=partial_mf,
            investments=data.investments,
            loans=data.loans,
            insurance=data.insurance,
            goals=data.goals,
            transactions=data.transactions,
        )
        partial_signals = _detect_signals(partial_data)
        level = _compute_stress_level(partial_signals)
        history.append({"month": partial_mf[-1].month, "level": round(level, 1)})

    return {
        "current_level": round(current_level, 1),
        "status": _stress_status(current_level),
        "projections": projections,
        "signals": signals,
        "preventive_actions": actions,
        "history": history,
    }


def _detect_signals(data: CustomerData) -> list[dict]:
    signals = []
    mf = data.monthly_financials

    if len(mf) < 2:
        return signals

    # 1. Income trend
    incomes = [m.income for m in mf]
    if len(incomes) >= 3:
        recent = statistics.mean(incomes[-3:])
        earlier = statistics.mean(incomes[:3])
        if recent < earlier * 0.9:
            signals.append({
                "type": "income_decline",
                "severity": "high",
                "title": "Declining Income",
                "description": f"Income dropped {((earlier-recent)/earlier)*100:.0f}% from ₹{earlier:,.0f} to ₹{recent:,.0f}.",
                "weight": 25,
            })
        elif recent < earlier:
            signals.append({
                "type": "income_stagnation",
                "severity": "medium",
                "title": "Income Stagnation",
                "description": "Income has not grown in recent months.",
                "weight": 10,
            })

    # 2. Expense-to-income ratio
    recent_mf = mf[-3:]
    avg_income = statistics.mean([m.income for m in recent_mf])
    avg_expenses = statistics.mean([m.total_expenses for m in recent_mf])
    if avg_income > 0:
        expense_ratio = avg_expenses / avg_income
        if expense_ratio > 0.75:
            signals.append({
                "type": "high_expense_ratio",
                "severity": "high",
                "title": "High Expense-to-Income Ratio",
                "description": f"Expenses are {expense_ratio*100:.0f}% of income. Very little room for savings.",
                "weight": 20,
            })
        elif expense_ratio > 0.60:
            signals.append({
                "type": "moderate_expense_ratio",
                "severity": "medium",
                "title": "Rising Expense Ratio",
                "description": f"Expenses are {expense_ratio*100:.0f}% of income.",
                "weight": 10,
            })

    # 3. EMI utilization
    total_emi = sum(l.emi for l in data.loans)
    if avg_income > 0 and total_emi > 0:
        emi_ratio = total_emi / avg_income
        if emi_ratio > 0.40:
            signals.append({
                "type": "high_emi",
                "severity": "high",
                "title": "Critical EMI Burden",
                "description": f"EMIs consume {emi_ratio*100:.0f}% of income.",
                "weight": 25,
            })
        elif emi_ratio > 0.25:
            signals.append({
                "type": "moderate_emi",
                "severity": "medium",
                "title": "Moderate EMI Burden",
                "description": f"EMIs are {emi_ratio*100:.0f}% of income.",
                "weight": 12,
            })

    # 4. Savings depletion
    savings_trend = []
    for m in mf:
        s = m.income - m.total_expenses - m.investments
        savings_trend.append(s)
    if len(savings_trend) >= 3:
        recent_savings = savings_trend[-3:]
        if all(s < 0 for s in recent_savings):
            signals.append({
                "type": "negative_savings",
                "severity": "high",
                "title": "Negative Savings",
                "description": "Spending exceeds income for 3+ months.",
                "weight": 30,
            })
        elif statistics.mean(recent_savings) < statistics.mean(savings_trend) * 0.5:
            signals.append({
                "type": "declining_savings",
                "severity": "medium",
                "title": "Declining Savings",
                "description": "Savings have dropped significantly in recent months.",
                "weight": 15,
            })

    # 5. Emergency fund check
    ef_goal = next((g for g in data.goals if "emergency" in g.name.lower()), None)
    if ef_goal:
        months_covered = ef_goal.current_amount / avg_expenses if avg_expenses > 0 else 0
        if months_covered < 2:
            signals.append({
                "type": "low_emergency_fund",
                "severity": "high",
                "title": "Critically Low Emergency Fund",
                "description": f"Only {months_covered:.1f} months of expenses covered.",
                "weight": 20,
            })
        elif months_covered < 4:
            signals.append({
                "type": "moderate_emergency_fund",
                "severity": "medium",
                "title": "Emergency Fund Below Target",
                "description": f"{months_covered:.1f} months covered, target is 6 months.",
                "weight": 10,
            })

    # 6. Unusual spending spikes
    if len(mf) >= 4:
        expense_list = [m.total_expenses for m in mf]
        avg_exp = statistics.mean(expense_list[:-1])
        last_exp = expense_list[-1]
        if last_exp > avg_exp * 1.3:
            signals.append({
                "type": "spending_spike",
                "severity": "medium",
                "title": "Spending Spike Detected",
                "description": f"Last month expenses ₹{last_exp:,.0f} vs average ₹{avg_exp:,.0f}.",
                "weight": 8,
            })

    return signals


def _compute_stress_level(signals) -> float:
    if not signals:
        return 10.0  # baseline low stress

    total_weight = sum(s["weight"] for s in signals)
    # Normalize: 100 weight points = 100% stress
    return min(95, 10 + total_weight)


def _stress_status(level: float) -> str:
    if level <= 20:
        return "Low"
    elif level <= 40:
        return "Moderate"
    elif level <= 60:
        return "Elevated"
    elif level <= 80:
        return "High"
    else:
        return "Critical"


def _project_stress(data: CustomerData, current: float) -> dict:
    mf = data.monthly_financials
    if not mf:
        return {"30_day": current, "90_day": current, "365_day": current}

    # Simple projection based on trends
    income_trend = 0
    expense_trend = 0

    if len(mf) >= 4:
        incomes = [m.income for m in mf]
        expenses = [m.total_expenses for m in mf]
        income_trend = (incomes[-1] - incomes[0]) / max(1, incomes[0])
        expense_trend = (expenses[-1] - expenses[0]) / max(1, expenses[0])

    # If expenses growing faster than income, stress increases
    trend_delta = expense_trend - income_trend

    day_30 = min(95, max(5, current + trend_delta * 10))
    day_90 = min(95, max(5, current + trend_delta * 25))
    day_365 = min(95, max(5, current + trend_delta * 60))

    return {
        "30_day": round(day_30, 1),
        "90_day": round(day_90, 1),
        "365_day": round(day_365, 1),
    }


def _generate_actions(signals, data: CustomerData) -> list[dict]:
    actions = []

    signal_types = {s["type"] for s in signals}

    if "high_emi" in signal_types or "moderate_emi" in signal_types:
        actions.append({
            "title": "Reduce EMI Burden",
            "description": "Consider prepaying high-interest loans or consolidating debt.",
            "priority": "high",
            "impact": "Could free up ₹5,000-15,000/month",
            "category": "debt",
        })

    if "high_expense_ratio" in signal_types:
        actions.append({
            "title": "Review Monthly Expenses",
            "description": "Identify and cut non-essential spending. Focus on subscriptions, dining, and shopping.",
            "priority": "high",
            "impact": "Target reducing expenses by 10-15%",
            "category": "expense",
        })

    if "low_emergency_fund" in signal_types or "moderate_emergency_fund" in signal_types:
        actions.append({
            "title": "Build Emergency Fund",
            "description": "Prioritize building 6 months of expenses in a liquid fund.",
            "priority": "high",
            "impact": "Financial safety net against unexpected events",
            "category": "savings",
        })

    if "negative_savings" in signal_types or "declining_savings" in signal_types:
        actions.append({
            "title": "Reverse Savings Decline",
            "description": "Automate savings via standing instruction. Move at least 20% to savings immediately on salary day.",
            "priority": "high",
            "impact": "Rebuild financial buffer",
            "category": "savings",
        })

    if "income_decline" in signal_types:
        actions.append({
            "title": "Diversify Income",
            "description": "Explore freelancing, consulting, or passive income sources to supplement primary income.",
            "priority": "medium",
            "impact": "Reduce dependency on single income source",
            "category": "income",
        })

    # Always add general advice
    actions.append({
        "title": "Review Insurance Coverage",
        "description": "Ensure adequate life and health insurance to protect against unexpected events.",
        "priority": "medium",
        "impact": "Risk mitigation for family",
        "category": "protection",
    })

    return actions


def _empty_stress() -> dict:
    return {
        "current_level": 0,
        "status": "No Data",
        "projections": {"30_day": 0, "90_day": 0, "365_day": 0},
        "signals": [],
        "preventive_actions": [],
        "history": [],
    }
