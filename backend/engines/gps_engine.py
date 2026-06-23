"""Wealth GPS Engine — calculates goal routes, ETAs, waypoints, and alternative strategies."""

from models.customer import CustomerData
import statistics
from datetime import datetime, date
import math


def compute_wealth_gps(data: CustomerData) -> list[dict]:
    """Compute GPS route for all goals."""
    goals = []
    for goal in data.goals:
        goals.append(_compute_goal_route(goal, data))
    return goals


def _compute_goal_route(goal, data: CustomerData) -> dict:
    mf = data.monthly_financials
    avg_income = statistics.mean([m.income for m in mf]) if mf else 0
    avg_savings = statistics.mean([m.income - m.total_expenses - m.investments for m in mf]) if mf else 0
    avg_investments = statistics.mean([m.investments for m in mf]) if mf else 0

    target = goal.target_amount
    current = goal.current_amount
    remaining = max(0, target - current)
    completion_pct = (current / target * 100) if target > 0 else 0

    # Parse deadline
    try:
        deadline = datetime.strptime(goal.deadline, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        deadline = date(2028, 12, 31)

    today = date.today()
    months_left = max(1, (deadline.year - today.year) * 12 + (deadline.month - today.month))

    # Monthly requirement
    monthly_required = remaining / months_left if months_left > 0 else remaining

    # Estimate current monthly contribution to this goal
    # Distribute savings proportionally by priority
    total_priority = sum(6 - g.priority for g in data.goals) or 1
    goal_weight = (6 - goal.priority) / total_priority
    monthly_contribution = (avg_savings + avg_investments) * goal_weight * 0.4  # conservative estimate

    gap = max(0, monthly_required - monthly_contribution)

    # ETA calculation with compound growth
    annual_return = 0.10  # assume 10% blended return
    monthly_return = annual_return / 12

    if monthly_contribution > 0 and monthly_return > 0:
        # FV formula: FV = PV*(1+r)^n + PMT*((1+r)^n - 1)/r
        # Solve for n when FV = target
        # Using iterative approach
        months_to_goal = _estimate_months_to_goal(current, monthly_contribution, monthly_return, target)
        eta_date = _add_months(today, months_to_goal)
    else:
        months_to_goal = months_left * 3  # very far
        eta_date = _add_months(today, months_to_goal)

    on_track = months_to_goal <= months_left

    # Goal completion probability (simple estimate)
    if on_track:
        probability = min(95, 70 + (months_left - months_to_goal) / max(1, months_left) * 25)
    else:
        probability = max(10, 70 - (months_to_goal - months_left) / max(1, months_left) * 40)

    # Optimized probability (if gap is closed)
    optimized_months = _estimate_months_to_goal(current, monthly_contribution + gap, monthly_return, target)
    optimized_probability = min(95, probability + 20) if gap > 0 else probability

    # Waypoints
    waypoints = []
    for pct in [25, 50, 75, 100]:
        wp_amount = target * pct / 100
        if wp_amount <= current:
            wp_status = "completed"
        elif pct / 100 <= completion_pct / 100 + 0.1:
            wp_status = "upcoming"
        else:
            wp_status = "pending"
        waypoints.append({
            "percentage": pct,
            "amount": round(wp_amount),
            "status": wp_status,
            "label": f"{pct}% — ₹{wp_amount:,.0f}" if pct < 100 else f"🎯 Goal — ₹{target:,.0f}",
        })

    # Alternative routes
    alternatives = _generate_alternatives(goal, data, monthly_contribution, monthly_required, gap, months_left)

    # Risk factors
    risks = _assess_risks(goal, data, monthly_contribution, gap)

    return {
        "id": goal.id,
        "name": goal.name,
        "target_amount": target,
        "current_amount": current,
        "remaining": round(remaining),
        "completion_pct": round(completion_pct, 1),
        "deadline": goal.deadline,
        "priority": goal.priority,
        "monthly_required": round(monthly_required),
        "monthly_contribution": round(monthly_contribution),
        "gap": round(gap),
        "months_to_goal": months_to_goal,
        "eta": eta_date.isoformat(),
        "on_track": on_track,
        "probability": round(probability, 1),
        "optimized_probability": round(optimized_probability, 1),
        "waypoints": waypoints,
        "alternatives": alternatives,
        "risks": risks,
    }


def _estimate_months_to_goal(current, monthly, rate, target):
    """Estimate months to reach target with monthly SIP and compound growth."""
    if monthly <= 0:
        return 999
    corpus = current
    for month in range(1, 600):
        corpus = corpus * (1 + rate) + monthly
        if corpus >= target:
            return month
    return 999


def _add_months(d, months):
    month = d.month + months
    year = d.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    try:
        return date(min(year, 2099), month, min(d.day, 28))
    except ValueError:
        return date(min(year, 2099), month, 28)


def _generate_alternatives(goal, data, current_monthly, required, gap, months_left):
    alternatives = []

    # Route 1: Increase SIP
    if gap > 0:
        alternatives.append({
            "name": "Increase Monthly Investment",
            "description": f"Add ₹{gap:,.0f}/month to reach goal on time.",
            "monthly_amount": round(current_monthly + gap),
            "eta_months": months_left,
            "feasibility": "Medium" if gap < data.profile.monthly_income * 0.1 else "Challenging",
        })

    # Route 2: Extend timeline
    extended_months = _estimate_months_to_goal(
        goal.current_amount, current_monthly,
        0.10 / 12, goal.target_amount
    )
    if extended_months < 999:
        alternatives.append({
            "name": "Extend Timeline",
            "description": f"Keep current investment, reach goal in {extended_months} months instead.",
            "monthly_amount": round(current_monthly),
            "eta_months": extended_months,
            "feasibility": "Easy",
        })

    # Route 3: Adjust target
    adjusted_target = goal.current_amount + current_monthly * months_left * 1.5  # rough estimate with growth
    if adjusted_target < goal.target_amount * 0.95:
        alternatives.append({
            "name": "Adjust Target",
            "description": f"Reduce target to ₹{adjusted_target:,.0f} to stay comfortable.",
            "monthly_amount": round(current_monthly),
            "eta_months": months_left,
            "feasibility": "Easy",
        })

    # Route 4: High-growth strategy
    alternatives.append({
        "name": "Aggressive Growth Strategy",
        "description": "Shift to equity-heavy portfolio (80:20) for potentially higher returns.",
        "monthly_amount": round(current_monthly),
        "eta_months": max(months_left - 6, int(months_left * 0.85)),
        "feasibility": "High Risk",
    })

    return alternatives


def _assess_risks(goal, data, monthly, gap):
    risks = []

    if gap > data.profile.monthly_income * 0.1:
        risks.append({
            "factor": "Large Funding Gap",
            "severity": "high",
            "description": f"Monthly gap of ₹{gap:,.0f} is over 10% of income.",
            "mitigation": "Consider additional income sources or target adjustment.",
        })

    total_emi = sum(l.emi for l in data.loans)
    if total_emi > data.profile.monthly_income * 0.3:
        risks.append({
            "factor": "High EMI Burden",
            "severity": "high",
            "description": "Existing EMIs consume >30% of income, limiting savings capacity.",
            "mitigation": "Prioritize debt repayment to free up cash flow.",
        })

    risks.append({
        "factor": "Inflation Risk",
        "severity": "medium",
        "description": "Target amount may need upward revision due to inflation.",
        "mitigation": "Review target annually and adjust investments accordingly.",
    })

    risks.append({
        "factor": "Market Volatility",
        "severity": "medium",
        "description": "Equity investments may underperform in short term.",
        "mitigation": "Maintain diversified portfolio with debt component.",
    })

    return risks
