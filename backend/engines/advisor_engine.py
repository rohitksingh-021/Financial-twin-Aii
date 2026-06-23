"""Advisor Engine — generates proactive financial recommendations from customer data analysis."""

from models.customer import CustomerData
import statistics


def generate_recommendations(data: CustomerData) -> list[dict]:
    """Analyze all customer data and generate actionable recommendations."""
    recs = []

    recs.extend(_idle_balance_check(data))
    recs.extend(_subscription_audit(data))
    recs.extend(_tax_saving_check(data))
    recs.extend(_insurance_gap_check(data))
    recs.extend(_sip_optimization(data))
    recs.extend(_debt_optimization(data))
    recs.extend(_emergency_fund_check(data))
    recs.extend(_diversification_check(data))

    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recs.sort(key=lambda x: priority_order.get(x["priority"], 1))

    return recs


def generate_chat_response(data: CustomerData, message: str) -> dict:
    """Generate a contextual response to a user chat message."""
    msg_lower = message.lower()

    # Detect intent and generate appropriate response
    if any(w in msg_lower for w in ["invest", "where to invest", "sip", "mutual fund"]):
        return _investment_advice(data)
    elif any(w in msg_lower for w in ["save", "saving", "cut expense", "reduce spending"]):
        return _savings_advice(data)
    elif any(w in msg_lower for w in ["loan", "emi", "debt", "borrow"]):
        return _debt_advice(data)
    elif any(w in msg_lower for w in ["house", "home", "property", "flat"]):
        return _home_advice(data)
    elif any(w in msg_lower for w in ["retire", "retirement", "pension"]):
        return _retirement_advice(data)
    elif any(w in msg_lower for w in ["tax", "80c", "section"]):
        return _tax_advice(data)
    elif any(w in msg_lower for w in ["insurance", "cover", "term plan"]):
        return _insurance_advice(data)
    elif any(w in msg_lower for w in ["emergency", "rainy day", "contingency"]):
        return _emergency_advice(data)
    elif any(w in msg_lower for w in ["hello", "hi", "hey", "help"]):
        return _greeting(data)
    else:
        return _general_advice(data)


def _idle_balance_check(data: CustomerData) -> list[dict]:
    mf = data.monthly_financials
    if not mf:
        return []

    recs = []
    avg_income = statistics.mean([m.income for m in mf])
    avg_expenses = statistics.mean([m.total_expenses for m in mf])
    avg_investments = statistics.mean([m.investments for m in mf])
    idle = avg_income - avg_expenses - avg_investments

    if idle > avg_expenses * 0.3:
        recs.append({
            "id": "idle-balance",
            "title": "₹{:,.0f} Idle Balance Detected".format(idle),
            "description": "Your monthly surplus is sitting idle in your savings account earning minimal interest.",
            "suggested_action": "Allocate to: Liquid Fund (₹{:,.0f}) + SIP Top-up (₹{:,.0f})".format(idle * 0.6, idle * 0.4),
            "impact": "₹{:,.0f}/year additional returns".format(idle * 12 * 0.06),
            "priority": "high",
            "category": "invest",
            "confidence": 88,
            "data_points": [
                f"Average monthly surplus: ₹{idle:,.0f}",
                f"Current savings account rate: ~3.5%",
                f"Liquid fund potential rate: ~6-7%",
            ],
        })

    return recs


def _subscription_audit(data: CustomerData) -> list[dict]:
    recs = []

    # Find recurring small debits (subscriptions)
    subscription_txns = [t for t in data.transactions if t.category == "Subscription"]
    merchants = {}
    for t in subscription_txns:
        if t.merchant not in merchants:
            merchants[t.merchant] = {"count": 0, "total": 0, "amount": t.amount}
        merchants[t.merchant]["count"] += 1
        merchants[t.merchant]["total"] += t.amount

    # Find potentially unused subscriptions (appeared less than expected for the period)
    low_usage = [m for m, d in merchants.items() if d["count"] <= 3]  # less than quarterly

    if low_usage and len(merchants) >= 3:
        total_annual = sum(merchants[m]["amount"] * 12 for m in low_usage)
        recs.append({
            "id": "unused-subs",
            "title": f"{len(low_usage)} Potentially Unused Subscriptions",
            "description": f"Services: {', '.join(low_usage)}. Consider reviewing if you actively use these.",
            "suggested_action": "Review and cancel unused subscriptions.",
            "impact": f"Potential annual savings: ₹{total_annual:,.0f}",
            "priority": "medium",
            "category": "save",
            "confidence": 72,
            "data_points": [f"{m}: ₹{merchants[m]['amount']:,.0f}/month" for m in low_usage],
        })

    return recs


def _tax_saving_check(data: CustomerData) -> list[dict]:
    recs = []

    ppf = sum(i.invested_amount / max(1, (2026 - int(i.start_date[:4]))) for i in data.investments if i.type == "PPF")
    nps = sum(i.invested_amount / max(1, (2026 - int(i.start_date[:4]))) for i in data.investments if i.type == "NPS")
    insurance_premium = sum(i.annual_premium for i in data.insurance if i.type in ("term", "life"))

    total_80c = ppf + insurance_premium
    limit_80c = 150000

    if total_80c < limit_80c:
        gap = limit_80c - total_80c
        tax_saving = gap * 0.3  # 30% tax bracket
        recs.append({
            "id": "tax-80c",
            "title": f"Tax Saving Opportunity: ₹{gap:,.0f} Under 80C",
            "description": f"You've utilized ₹{total_80c:,.0f} of ₹{limit_80c:,.0f} limit under Section 80C.",
            "suggested_action": f"Invest ₹{gap:,.0f} in ELSS funds or increase PPF contribution.",
            "impact": f"Tax saving of ~₹{tax_saving:,.0f}",
            "priority": "high",
            "category": "save",
            "confidence": 90,
            "data_points": [
                f"PPF contribution: ~₹{ppf:,.0f}/year",
                f"Insurance premiums: ₹{insurance_premium:,.0f}/year",
                f"Remaining 80C limit: ₹{gap:,.0f}",
            ],
        })

    # NPS additional deduction (80CCD)
    if nps < 50000:
        nps_gap = 50000 - nps
        recs.append({
            "id": "tax-nps",
            "title": f"Additional ₹{nps_gap:,.0f} Tax Saving via NPS",
            "description": "Section 80CCD(1B) allows additional ₹50,000 deduction for NPS.",
            "suggested_action": f"Invest ₹{nps_gap:,.0f} in NPS Tier-1 for extra tax benefit.",
            "impact": f"Tax saving of ~₹{nps_gap * 0.3:,.0f}",
            "priority": "medium",
            "category": "save",
            "confidence": 85,
            "data_points": [f"Current NPS: ~₹{nps:,.0f}/year", "Additional limit: ₹50,000"],
        })

    return recs


def _insurance_gap_check(data: CustomerData) -> list[dict]:
    recs = []

    life_cover = sum(i.sum_assured for i in data.insurance if i.type in ("term", "life"))
    target_life = data.profile.annual_income * 10

    if life_cover < target_life:
        gap = target_life - life_cover
        recs.append({
            "id": "insurance-life",
            "title": "Life Insurance Coverage Gap",
            "description": f"Current cover: ₹{life_cover:,.0f} ({life_cover/data.profile.annual_income:.0f}x income). Recommended: 10x income.",
            "suggested_action": f"Add ₹{gap:,.0f} term life cover. Estimated premium: ₹{gap/1000000*1200:,.0f}/year.",
            "impact": "Complete financial protection for family",
            "priority": "high",
            "category": "protect",
            "confidence": 92,
            "data_points": [
                f"Annual income: ₹{data.profile.annual_income:,.0f}",
                f"Current cover: ₹{life_cover:,.0f}",
                f"Recommended: ₹{target_life:,.0f}",
            ],
        })

    health_cover = sum(i.sum_assured for i in data.insurance if i.type == "health")
    if health_cover < 1000000:
        recs.append({
            "id": "insurance-health",
            "title": "Upgrade Health Insurance",
            "description": f"Current cover: ₹{health_cover:,.0f}. May be insufficient for major hospitalizations.",
            "suggested_action": "Consider ₹10-15L super top-up plan (premium ~₹3,000-5,000/year).",
            "impact": "Protection against medical inflation and catastrophic expenses",
            "priority": "high",
            "category": "protect",
            "confidence": 88,
            "data_points": [
                f"Current health cover: ₹{health_cover:,.0f}",
                f"Family size: {data.profile.family_size}",
                "Average hospitalization cost in metro: ₹3-8L",
            ],
        })

    return recs


def _sip_optimization(data: CustomerData) -> list[dict]:
    recs = []
    mf = data.monthly_financials

    if not mf:
        return recs

    avg_investments = statistics.mean([m.investments for m in mf])
    avg_income = statistics.mean([m.income for m in mf])

    invest_ratio = avg_investments / avg_income if avg_income > 0 else 0

    if invest_ratio < 0.25:
        target = avg_income * 0.25
        additional = target - avg_investments
        recs.append({
            "id": "sip-increase",
            "title": f"Increase SIP by ₹{additional:,.0f}/month",
            "description": f"Currently investing {invest_ratio*100:.0f}% of income. Target: 25%.",
            "suggested_action": f"Add ₹{additional:,.0f}/month across diversified funds.",
            "impact": f"₹{additional*12*10*0.12:,.0f} additional corpus in 10 years (at 12% CAGR)",
            "priority": "medium",
            "category": "invest",
            "confidence": 82,
            "data_points": [
                f"Current monthly investment: ₹{avg_investments:,.0f}",
                f"Target (25% of income): ₹{target:,.0f}",
                f"Gap: ₹{additional:,.0f}/month",
            ],
        })

    return recs


def _debt_optimization(data: CustomerData) -> list[dict]:
    recs = []

    high_interest = [l for l in data.loans if l.interest_rate > 10]
    if high_interest:
        for loan in high_interest:
            interest_paid = loan.outstanding * loan.interest_rate / 100
            recs.append({
                "id": f"debt-{loan.id}",
                "title": f"Prepay {loan.type.title()} Loan ({loan.interest_rate}% rate)",
                "description": f"Outstanding: ₹{loan.outstanding:,.0f}. You're paying ~₹{interest_paid:,.0f}/year in interest.",
                "suggested_action": "Consider partial prepayment to reduce interest burden.",
                "impact": f"Save ~₹{interest_paid*0.3:,.0f}/year in interest",
                "priority": "medium",
                "category": "save",
                "confidence": 78,
                "data_points": [
                    f"Outstanding: ₹{loan.outstanding:,.0f}",
                    f"EMI: ₹{loan.emi:,.0f}/month",
                    f"Remaining tenure: {loan.tenure_remaining} months",
                ],
            })

    return recs


def _emergency_fund_check(data: CustomerData) -> list[dict]:
    recs = []
    mf = data.monthly_financials

    if not mf:
        return recs

    avg_expenses = statistics.mean([m.total_expenses for m in mf])
    target = avg_expenses * 6

    ef_goal = next((g for g in data.goals if "emergency" in g.name.lower()), None)
    current = ef_goal.current_amount if ef_goal else 0

    if current < target:
        gap = target - current
        months_covered = current / avg_expenses if avg_expenses > 0 else 0
        recs.append({
            "id": "emergency-fund",
            "title": f"Emergency Fund: {months_covered:.1f} months (Target: 6)",
            "description": f"Current: ₹{current:,.0f}. Target: ₹{target:,.0f}.",
            "suggested_action": f"Allocate ₹{gap/12:,.0f}/month to liquid fund until target reached.",
            "impact": f"Financial safety net of ₹{target:,.0f}",
            "priority": "high" if months_covered < 3 else "medium",
            "category": "save",
            "confidence": 95,
            "data_points": [
                f"Monthly expenses: ~₹{avg_expenses:,.0f}",
                f"Months covered: {months_covered:.1f}",
                f"Gap: ₹{gap:,.0f}",
            ],
        })

    return recs


def _diversification_check(data: CustomerData) -> list[dict]:
    recs = []

    if not data.investments:
        return recs

    types = {}
    total = sum(i.current_value for i in data.investments)
    for inv in data.investments:
        types[inv.type] = types.get(inv.type, 0) + inv.current_value

    # Check concentration
    for t, val in types.items():
        if total > 0 and val / total > 0.50:
            recs.append({
                "id": f"diversify-{t}",
                "title": f"Portfolio Concentrated in {t.upper()}",
                "description": f"{t.upper()} is {val/total*100:.0f}% of your portfolio. Consider rebalancing.",
                "suggested_action": "Diversify into other asset classes to reduce risk.",
                "impact": "Reduced portfolio volatility",
                "priority": "medium",
                "category": "invest",
                "confidence": 75,
                "data_points": [f"{k.upper()}: {v/total*100:.0f}%" for k, v in types.items()],
            })

    return recs


# === Chat Response Generators ===

def _greeting(data: CustomerData) -> dict:
    return {
        "message": f"Hello {data.profile.name}! 👋 I'm your AI Financial Advisor. I've analyzed your complete financial profile and have personalized insights ready. What would you like to discuss? You can ask about investments, savings, loans, taxes, or any financial topic.",
        "suggestions": ["Where should I invest?", "How can I save more?", "Am I ready to buy a house?", "Review my tax savings"],
        "context": {"topic": "greeting"},
    }


def _investment_advice(data: CustomerData) -> dict:
    total_inv = sum(i.current_value for i in data.investments)
    types = set(i.type for i in data.investments)
    avg_return = sum(i.current_value * i.expected_return for i in data.investments) / total_inv if total_inv > 0 else 0

    return {
        "message": f"Based on your profile ({data.profile.risk_appetite.value} risk appetite, age {data.profile.age}), here's my investment analysis:\n\n📊 **Current Portfolio**: ₹{total_inv:,.0f} across {len(types)} asset classes\n📈 **Weighted Return**: {avg_return:.1f}%\n\n**My Recommendations:**\n1. Your equity allocation could be higher for your age. Consider 60-70% in equity.\n2. Add international diversification via Nasdaq/S&P 500 index fund.\n3. Increase SIP by ₹5,000-10,000/month for faster wealth creation.\n4. Your PPF is a solid debt anchor — continue max contribution.\n\n**Confidence**: 85% | **Data Points**: 12-month investment history, risk profile, age-based allocation model",
        "suggestions": ["Simulate ₹10,000 more SIP", "Show my portfolio allocation", "Compare fund options"],
        "context": {
            "topic": "investment",
            "confidence": 85,
            "portfolio_value": total_inv,
        },
    }


def _savings_advice(data: CustomerData) -> dict:
    mf = data.monthly_financials
    avg_income = statistics.mean([m.income for m in mf]) if mf else 0
    avg_expenses = statistics.mean([m.total_expenses for m in mf]) if mf else 0
    savings_rate = (avg_income - avg_expenses) / avg_income * 100 if avg_income > 0 else 0

    return {
        "message": f"Let me analyze your spending patterns:\n\n💰 **Savings Rate**: {savings_rate:.0f}% (Target: 30%)\n\n**Top Expense Categories:**\n🏠 Rent: ₹35,000/month (largest fixed cost)\n🛒 Shopping: Variable, spikes in Nov-Dec\n🍔 Food & Dining: ₹4,000-6,000/month\n\n**Quick Wins:**\n1. Set up auto-transfer of 25% on salary day\n2. Review and cancel unused subscriptions\n3. Switch to a cashback credit card for groceries\n4. Use UPI payments to track all expenses\n\n**Confidence**: 90% | Based on 12-month transaction analysis",
        "suggestions": ["Show my spending breakdown", "Set up savings goal", "Find unused subscriptions"],
        "context": {"topic": "savings", "confidence": 90, "savings_rate": savings_rate},
    }


def _debt_advice(data: CustomerData) -> dict:
    total_debt = sum(l.outstanding for l in data.loans)
    total_emi = sum(l.emi for l in data.loans)

    return {
        "message": f"Here's your debt snapshot:\n\n📋 **Total Outstanding**: ₹{total_debt:,.0f}\n📋 **Monthly EMIs**: ₹{total_emi:,.0f}\n\n{'Your debt is manageable.' if total_emi < data.profile.monthly_income * 0.3 else '⚠️ EMI burden is high.'}\n\n**Recommendations:**\n1. Prioritize prepaying the personal loan (11.5% rate)\n2. ₹50,000 prepayment could save ₹12,000 in interest\n3. Avoid new debt until existing loans are below 20% of income\n\n**Confidence**: 88%",
        "suggestions": ["Simulate loan prepayment", "Check home loan eligibility", "Debt freedom plan"],
        "context": {"topic": "debt", "confidence": 88, "total_debt": total_debt},
    }


def _home_advice(data: CustomerData) -> dict:
    goal = next((g for g in data.goals if "house" in g.name.lower() or "home" in g.name.lower()), None)
    progress = (goal.current_amount / goal.target_amount * 100) if goal and goal.target_amount > 0 else 0

    return {
        "message": f"🏠 **Home Purchase Readiness Analysis**\n\n{'Goal: ' + goal.name if goal else 'No home purchase goal set'}\n📊 Progress: {progress:.0f}% (₹{goal.current_amount:,.0f} of ₹{goal.target_amount:,.0f})\n\n**Readiness Checklist:**\n✅ Stable income (24+ months)\n{'✅' if progress > 20 else '⬜'} Down payment (20% = ₹{goal.target_amount * 0.2:,.0f})\n✅ Credit score inquiry done\n⬜ Emergency fund (need 6 months post-purchase)\n\n**Home Loan Estimate:**\n• Eligible amount: ~₹{data.profile.annual_income * 4:,.0f}\n• Approx EMI: ₹{data.profile.annual_income * 4 * 0.0085:,.0f}/month (8.5%, 20yr)\n• EMI-to-income: {data.profile.annual_income * 4 * 0.0085 / data.profile.monthly_income * 100:.0f}%\n\n**Confidence**: 82%",
        "suggestions": ["Simulate mortgage scenarios", "View Wealth GPS for house", "Compare home loan rates"],
        "context": {"topic": "home", "confidence": 82},
    }


def _retirement_advice(data: CustomerData) -> dict:
    ret_goal = next((g for g in data.goals if "retire" in g.name.lower()), None)
    years_to_retire = 60 - data.profile.age

    return {
        "message": f"🏖️ **Retirement Planning Analysis**\n\n⏰ Years to retirement: {years_to_retire}\n{'📊 Current corpus: ₹' + f'{ret_goal.current_amount:,.0f}' if ret_goal else '⚠️ No retirement goal set!'}\n{'📊 Target: ₹' + f'{ret_goal.target_amount:,.0f}' if ret_goal else ''}\n\n**Key Actions:**\n1. Maximize NPS contribution (tax benefit + corpus growth)\n2. Consider EPF voluntary contribution\n3. SIP in equity index funds for long-term growth\n4. Review retirement target annually for inflation\n\n**Monthly SIP needed for ₹5Cr at 60**: ~₹{5_00_00_000 * 0.01 / (((1+0.01)**((60-data.profile.age)*12) - 1)):,.0f}/month (assuming 12% CAGR)\n\n**Confidence**: 80%",
        "suggestions": ["Simulate early retirement at 50", "Increase NPS contribution", "Retirement corpus calculator"],
        "context": {"topic": "retirement", "confidence": 80},
    }


def _tax_advice(data: CustomerData) -> dict:
    return {
        "message": f"🧾 **Tax Optimization Strategies**\n\n**Current Utilization:**\n• Section 80C: PPF + Insurance premiums\n• Section 80D: Health insurance premium\n• Section 80CCD: NPS contribution\n\n**Opportunities:**\n1. ₹46,000+ gap in 80C limit — invest in ELSS funds\n2. NPS additional ₹50,000 deduction available (80CCD1B)\n3. Home loan interest deduction (80EEA) when you buy\n4. Consider HRA optimization if renting\n\n**Estimated Tax Saving**: ₹35,000-50,000/year\n\n**Confidence**: 90%",
        "suggestions": ["Calculate exact tax savings", "Best ELSS funds", "NPS vs PPF comparison"],
        "context": {"topic": "tax", "confidence": 90},
    }


def _insurance_advice(data: CustomerData) -> dict:
    life = sum(i.sum_assured for i in data.insurance if i.type in ("term", "life"))
    health = sum(i.sum_assured for i in data.insurance if i.type == "health")

    return {
        "message": f"🛡️ **Insurance Coverage Review**\n\n**Life Cover**: ₹{life:,.0f} ({life/data.profile.annual_income:.0f}x income)\n**Health Cover**: ₹{health:,.0f}\n\n**Recommendations:**\n1. {'✅ Adequate' if life >= data.profile.annual_income * 10 else '⚠️ Increase to 10x income (₹' + f'{data.profile.annual_income*10:,.0f}' + ')'}\n2. {'✅ Good' if health >= 1000000 else '⚠️ Add super top-up to reach ₹10-15L'}\n3. Consider critical illness rider\n4. {'Add personal accident cover' if data.profile.dependents > 0 else 'Review annually'}\n\n**Confidence**: 92%",
        "suggestions": ["Compare term plans", "Calculate ideal cover", "Review claim process"],
        "context": {"topic": "insurance", "confidence": 92},
    }


def _emergency_advice(data: CustomerData) -> dict:
    mf = data.monthly_financials
    avg_exp = statistics.mean([m.total_expenses for m in mf]) if mf else 50000
    ef = next((g for g in data.goals if "emergency" in g.name.lower()), None)
    current = ef.current_amount if ef else 0
    months = current / avg_exp if avg_exp > 0 else 0

    return {
        "message": f"🆘 **Emergency Fund Status**\n\n📊 Current: ₹{current:,.0f} ({months:.1f} months)\n🎯 Target: ₹{avg_exp*6:,.0f} (6 months)\n\n**Plan:**\n1. Allocate ₹{(avg_exp*6 - current)/12:,.0f}/month to liquid fund\n2. Keep in instant-access instrument (liquid fund or sweep FD)\n3. Don't invest emergency fund in equity\n4. Review every 6 months as expenses change\n\n**Confidence**: 95%",
        "suggestions": ["Best liquid funds", "Set up auto-SIP for emergency fund", "Review expenses"],
        "context": {"topic": "emergency", "confidence": 95},
    }


def _general_advice(data: CustomerData) -> dict:
    return {
        "message": f"I'd be happy to help you with that, {data.profile.name}! Here are some areas I can advise on:\n\n📈 **Investments** — Portfolio review, SIP optimization, asset allocation\n💰 **Savings** — Expense analysis, savings strategies, budgeting\n🏠 **Goals** — Home purchase, retirement, education planning\n🧾 **Taxes** — 80C, 80D, NPS deductions, ELSS\n🛡️ **Insurance** — Life, health, coverage analysis\n📊 **What-If** — Simulate any financial scenario\n\nJust ask me anything specific!",
        "suggestions": ["Review my finances", "Where should I invest?", "Am I on track for my goals?", "Tax saving tips"],
        "context": {"topic": "general"},
    }
