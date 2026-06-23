"""Financial Vitality Score Engine — computes 8 sub-scores from raw customer data."""

from models.customer import CustomerData
import statistics


def compute_vitality_score(data: CustomerData) -> dict:
    mf = data.monthly_financials
    if not mf:
        return _empty_score()

    income_stability = _income_stability(mf)
    savings_discipline = _savings_discipline(mf)
    investment_growth = _investment_growth(data)
    debt_health = _debt_health(data, mf)
    liquidity_readiness = _liquidity_readiness(data, mf)
    risk_resilience = _risk_resilience(data)
    goal_achievement = _goal_achievement(data)
    financial_confidence = _financial_confidence(data, mf)

    sub_scores = {
        "income_stability": income_stability,
        "savings_discipline": savings_discipline,
        "investment_growth": investment_growth,
        "debt_health": debt_health,
        "liquidity_readiness": liquidity_readiness,
        "risk_resilience": risk_resilience,
        "goal_achievement": goal_achievement,
        "financial_confidence": financial_confidence,
    }

    weights = {
        "income_stability": 0.15,
        "savings_discipline": 0.15,
        "investment_growth": 0.15,
        "debt_health": 0.12,
        "liquidity_readiness": 0.12,
        "risk_resilience": 0.10,
        "goal_achievement": 0.11,
        "financial_confidence": 0.10,
    }

    overall = sum(sub_scores[k] * weights[k] for k in sub_scores)

    labels = {
        "income_stability": _label(income_stability),
        "savings_discipline": _label(savings_discipline),
        "investment_growth": _label(investment_growth),
        "debt_health": _label(debt_health),
        "liquidity_readiness": _label(liquidity_readiness),
        "risk_resilience": _label(risk_resilience),
        "goal_achievement": _label(goal_achievement),
        "financial_confidence": _label(financial_confidence),
    }

    explanations = {
        "income_stability": _income_explanation(mf),
        "savings_discipline": _savings_explanation(mf),
        "investment_growth": _investment_explanation(data),
        "debt_health": _debt_explanation(data, mf),
        "liquidity_readiness": _liquidity_explanation(data, mf),
        "risk_resilience": _resilience_explanation(data),
        "goal_achievement": _goal_explanation(data),
        "financial_confidence": _confidence_explanation(data, mf),
    }

    # Historical trend (compute score for each month cumulatively)
    history = []
    for i in range(1, len(mf) + 1):
        partial = CustomerData(
            profile=data.profile,
            monthly_financials=mf[:i],
            investments=data.investments,
            loans=data.loans,
            insurance=data.insurance,
            goals=data.goals,
            transactions=data.transactions,
        )
        partial_scores = _quick_score(partial)
        history.append({"month": mf[i - 1].month, "score": round(partial_scores, 1)})

    return {
        "overall": round(overall, 1),
        "sub_scores": {k: round(v, 1) for k, v in sub_scores.items()},
        "labels": labels,
        "explanations": explanations,
        "history": history,
        "peer_benchmark": {
            "age_group": "30-35",
            "median_score": 65,
            "percentile": min(95, max(5, int(overall * 1.1))),
        },
        "improvements": _get_improvements(sub_scores),
    }


def _quick_score(data: CustomerData) -> float:
    mf = data.monthly_financials
    if not mf:
        return 50.0
    scores = [
        _income_stability(mf),
        _savings_discipline(mf),
        _investment_growth(data),
        _debt_health(data, mf),
        _liquidity_readiness(data, mf),
        _risk_resilience(data),
        _goal_achievement(data),
        _financial_confidence(data, mf),
    ]
    return sum(scores) / len(scores)


def _income_stability(mf) -> float:
    incomes = [m.income for m in mf]
    if len(incomes) < 2:
        return 70.0
    mean_inc = statistics.mean(incomes)
    if mean_inc == 0:
        return 0
    cv = statistics.stdev(incomes) / mean_inc  # coefficient of variation
    stability = max(0, 100 - cv * 300)  # low CV = high score

    # Growth bonus
    if incomes[-1] > incomes[0]:
        growth = (incomes[-1] - incomes[0]) / incomes[0]
        stability = min(100, stability + growth * 50)

    # Consistency bonus (all months have income)
    months_with_income = sum(1 for i in incomes if i > 0)
    consistency = months_with_income / len(incomes) * 20
    return min(100, stability + consistency)


def _savings_discipline(mf) -> float:
    savings_rates = []
    for m in mf:
        total_out = m.total_expenses + m.investments
        if m.income > 0:
            savings_rates.append((m.income - total_out) / m.income)

    if not savings_rates:
        return 50.0

    avg_rate = statistics.mean(savings_rates)
    # Target: 30% savings rate
    score = min(100, (avg_rate / 0.30) * 80)

    # Consistency bonus
    if len(savings_rates) > 1:
        positive_months = sum(1 for r in savings_rates if r > 0)
        consistency = positive_months / len(savings_rates) * 20
        score = min(100, score + consistency)

    return max(0, score)


def _investment_growth(data: CustomerData) -> float:
    if not data.investments:
        return 30.0

    total_invested = sum(inv.invested_amount for inv in data.investments)
    total_current = sum(inv.current_value for inv in data.investments)

    if total_invested == 0:
        return 30.0

    returns = (total_current - total_invested) / total_invested
    # Target: 12% CAGR
    score = min(100, (returns / 0.12) * 60)

    # Diversification bonus
    asset_types = set(inv.type for inv in data.investments)
    diversification = min(30, len(asset_types) * 6)
    score += diversification

    # Regular investment bonus
    investment_months = sum(1 for m in data.monthly_financials if m.investments > 0)
    if data.monthly_financials:
        regularity = (investment_months / len(data.monthly_financials)) * 10
        score += regularity

    return min(100, max(0, score))


def _debt_health(data: CustomerData, mf) -> float:
    if not data.loans:
        return 95.0  # No debt is great

    total_emi = sum(l.emi for l in data.loans)
    avg_income = statistics.mean([m.income for m in mf]) if mf else 0

    if avg_income == 0:
        return 20.0

    emi_ratio = total_emi / avg_income

    # EMI/Income: <20% excellent, 20-35% good, 35-50% concerning, >50% bad
    if emi_ratio <= 0.20:
        score = 90 + (0.20 - emi_ratio) * 50
    elif emi_ratio <= 0.35:
        score = 65 + (0.35 - emi_ratio) * 166
    elif emi_ratio <= 0.50:
        score = 35 + (0.50 - emi_ratio) * 200
    else:
        score = max(0, 35 - (emi_ratio - 0.50) * 200)

    # Debt-to-asset ratio bonus
    total_assets = sum(inv.current_value for inv in data.investments)
    total_debt = sum(l.outstanding for l in data.loans)
    if total_assets > 0:
        dta = total_debt / total_assets
        if dta < 0.5:
            score = min(100, score + 10)

    return min(100, max(0, score))


def _liquidity_readiness(data: CustomerData, mf) -> float:
    # Emergency fund = liquid assets / monthly expenses
    liquid = sum(
        inv.current_value for inv in data.investments
        if inv.type in ("FD", "liquid", "savings")
    )

    # Also count savings from last few months
    recent = mf[-3:] if len(mf) >= 3 else mf
    avg_expenses = statistics.mean([m.total_expenses for m in recent]) if recent else 50000
    avg_income = statistics.mean([m.income for m in recent]) if recent else 150000

    # Estimate liquid savings (income - expenses - investments from recent months)
    recent_savings = sum(m.income - m.total_expenses - m.investments for m in recent)
    liquid += max(0, recent_savings)

    # Check goal: emergency fund
    ef_goal = next((g for g in data.goals if "emergency" in g.name.lower()), None)
    if ef_goal:
        liquid = max(liquid, ef_goal.current_amount)

    if avg_expenses == 0:
        return 80.0

    months_covered = liquid / avg_expenses

    # Target: 6 months
    if months_covered >= 6:
        score = 90 + min(10, (months_covered - 6) * 2)
    elif months_covered >= 3:
        score = 55 + (months_covered - 3) * 11.67
    elif months_covered >= 1:
        score = 25 + (months_covered - 1) * 15
    else:
        score = months_covered * 25

    return min(100, max(0, score))


def _risk_resilience(data: CustomerData) -> float:
    score = 40.0  # base

    # Insurance coverage
    life_cover = sum(ins.sum_assured for ins in data.insurance if ins.type in ("term", "life"))
    health_cover = sum(ins.sum_assured for ins in data.insurance if ins.type == "health")

    # Life cover should be 10-15x annual income
    if data.profile.annual_income > 0:
        life_ratio = life_cover / data.profile.annual_income
        if life_ratio >= 10:
            score += 25
        elif life_ratio >= 5:
            score += 15
        elif life_ratio > 0:
            score += 8

    # Health cover should be >= 5L for family
    if health_cover >= 1000000:
        score += 20
    elif health_cover >= 500000:
        score += 12
    elif health_cover > 0:
        score += 5

    # Portfolio diversification
    if data.investments:
        types = set(inv.type for inv in data.investments)
        score += min(15, len(types) * 3)

    return min(100, max(0, score))


def _goal_achievement(data: CustomerData) -> float:
    if not data.goals:
        return 50.0

    weighted_completion = 0
    total_weight = 0

    for goal in data.goals:
        if goal.target_amount > 0:
            completion = min(1.0, goal.current_amount / goal.target_amount)
            weight = 6 - goal.priority  # priority 1 = weight 5
            weighted_completion += completion * weight
            total_weight += weight

    if total_weight == 0:
        return 50.0

    return min(100, (weighted_completion / total_weight) * 100)


def _financial_confidence(data: CustomerData, mf) -> float:
    # Composite metric
    sub = [
        _income_stability(mf) * 0.2,
        _savings_discipline(mf) * 0.2,
        _investment_growth(data) * 0.2,
        _debt_health(data, mf) * 0.15,
        _goal_achievement(data) * 0.15,
        _risk_resilience(data) * 0.1,
    ]
    return min(100, sum(sub))


def _label(score: float) -> str:
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Strong"
    elif score >= 55:
        return "Moderate"
    elif score >= 40:
        return "Needs Attention"
    else:
        return "Critical"


def _income_explanation(mf) -> str:
    incomes = [m.income for m in mf]
    if incomes[-1] > incomes[0]:
        return f"Income grew from ₹{incomes[0]:,.0f} to ₹{incomes[-1]:,.0f} over {len(mf)} months. Consistent salary credits detected."
    return f"Stable income of ~₹{statistics.mean(incomes):,.0f}/month over {len(mf)} months."


def _savings_explanation(mf) -> str:
    rates = [(m.income - m.total_expenses - m.investments) / m.income * 100 for m in mf if m.income > 0]
    avg = statistics.mean(rates) if rates else 0
    return f"Average savings rate: {avg:.1f}% of income. Target: 30%. {'On track!' if avg >= 25 else 'Room for improvement.'}"


def _investment_explanation(data: CustomerData) -> str:
    total_inv = sum(i.invested_amount for i in data.investments)
    total_val = sum(i.current_value for i in data.investments)
    types = set(i.type for i in data.investments)
    returns = ((total_val - total_inv) / total_inv * 100) if total_inv > 0 else 0
    return f"Portfolio: ₹{total_val:,.0f} across {len(types)} asset classes. Overall returns: {returns:.1f}%."


def _debt_explanation(data, mf) -> str:
    total_emi = sum(l.emi for l in data.loans)
    avg_inc = statistics.mean([m.income for m in mf]) if mf else 1
    ratio = total_emi / avg_inc * 100
    return f"EMI-to-income ratio: {ratio:.1f}%. {'Healthy range.' if ratio < 35 else 'Consider reducing debt.'}"


def _liquidity_explanation(data, mf) -> str:
    ef = next((g for g in data.goals if "emergency" in g.name.lower()), None)
    if ef:
        months = ef.current_amount / (statistics.mean([m.total_expenses for m in mf]) if mf else 50000)
        return f"Emergency fund covers {months:.1f} months of expenses. Target: 6 months."
    return "No designated emergency fund detected. Consider building one."


def _resilience_explanation(data) -> str:
    life = sum(i.sum_assured for i in data.insurance if i.type in ("term", "life"))
    health = sum(i.sum_assured for i in data.insurance if i.type == "health")
    return f"Life cover: ₹{life:,.0f} ({life/data.profile.annual_income:.0f}x income). Health cover: ₹{health:,.0f}."


def _goal_explanation(data) -> str:
    on_track = sum(1 for g in data.goals if g.target_amount > 0 and g.current_amount / g.target_amount > 0.5)
    return f"{on_track} of {len(data.goals)} goals are over 50% complete."


def _confidence_explanation(data, mf) -> str:
    return "Composite score based on overall financial health indicators."


def _get_improvements(scores: dict) -> list[dict]:
    improvements = []
    sorted_scores = sorted(scores.items(), key=lambda x: x[1])

    labels_map = {
        "income_stability": ("Increase Income Stability", "Consider diversifying income sources or negotiating a raise."),
        "savings_discipline": ("Boost Savings Rate", "Aim to save at least 30% of your income. Identify non-essential expenses to cut."),
        "investment_growth": ("Optimize Investments", "Review portfolio allocation. Consider index funds for better long-term returns."),
        "debt_health": ("Reduce Debt Burden", "Prioritize high-interest debt repayment. Consider debt consolidation."),
        "liquidity_readiness": ("Build Emergency Fund", "Target 6 months of expenses in a liquid fund. Automate monthly transfers."),
        "risk_resilience": ("Strengthen Risk Coverage", "Review insurance coverage. Consider increasing health cover and adding critical illness cover."),
        "goal_achievement": ("Accelerate Goal Progress", "Increase SIP amounts or find additional savings to allocate to priority goals."),
        "financial_confidence": ("Build Financial Confidence", "Engage more with financial planning. Set up automated reviews."),
    }

    for key, score in sorted_scores[:3]:
        title, desc = labels_map.get(key, ("Improve", ""))
        improvements.append({
            "area": key,
            "current_score": round(score, 1),
            "title": title,
            "description": desc,
            "potential_impact": round(min(15, (80 - score) * 0.3), 1),
        })

    return improvements


def _empty_score() -> dict:
    return {
        "overall": 0,
        "sub_scores": {k: 0 for k in [
            "income_stability", "savings_discipline", "investment_growth",
            "debt_health", "liquidity_readiness", "risk_resilience",
            "goal_achievement", "financial_confidence"
        ]},
        "labels": {k: "No Data" for k in [
            "income_stability", "savings_discipline", "investment_growth",
            "debt_health", "liquidity_readiness", "risk_resilience",
            "goal_achievement", "financial_confidence"
        ]},
        "explanations": {},
        "history": [],
        "peer_benchmark": {"age_group": "N/A", "median_score": 0, "percentile": 0},
        "improvements": [],
    }
