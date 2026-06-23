"""Life Event Prediction Engine — predicts major life events from transaction patterns and financial behavior."""

from models.customer import CustomerData
from collections import defaultdict
import statistics


def predict_life_events(data: CustomerData) -> list[dict]:
    """Analyze transaction patterns and financial behavior to predict life events."""
    predictions = []

    predictions.append(_detect_home_purchase(data))
    predictions.append(_detect_marriage(data))
    predictions.append(_detect_child_planning(data))
    predictions.append(_detect_job_change(data))
    predictions.append(_detect_business_expansion(data))
    predictions.append(_detect_vacation(data))
    predictions.append(_detect_education(data))

    # Filter out very low probability events
    predictions = [p for p in predictions if p["probability"] > 15]

    # Sort by probability descending
    predictions.sort(key=lambda x: x["probability"], reverse=True)

    return predictions


def _detect_home_purchase(data: CustomerData) -> dict:
    signals = []
    score = 0

    # Check for furniture purchases
    furniture_txns = [t for t in data.transactions if t.category in ("Furniture", "Shopping") and
                      any(m in t.merchant.lower() for m in ["ikea", "pepperfry", "urban ladder", "godrej", "furniture"])]
    if len(furniture_txns) >= 2:
        signals.append(f"{len(furniture_txns)} furniture-related purchases detected")
        score += 15

    # Check for property portal subscriptions
    property_txns = [t for t in data.transactions if
                     any(m in t.merchant.lower() for m in ["magicbricks", "99acres", "housing.com", "nobroker", "property"])]
    if property_txns:
        signals.append(f"Property portal activity: {', '.join(set(t.merchant for t in property_txns))}")
        score += 20

    # Check for security deposits
    deposit_txns = [t for t in data.transactions if "security" in t.category.lower() or "deposit" in t.category.lower()]
    if deposit_txns:
        signals.append(f"Security deposit payment of ₹{sum(t.amount for t in deposit_txns):,.0f}")
        score += 15

    # Check for CIBIL/credit score checks
    credit_txns = [t for t in data.transactions if "cibil" in t.merchant.lower() or "credit" in t.category.lower()]
    if credit_txns:
        signals.append("Credit score inquiry detected")
        score += 10

    # Check for increased savings trend
    mf = data.monthly_financials
    if len(mf) >= 6:
        early_savings = statistics.mean([m.investments for m in mf[:3]])
        recent_savings = statistics.mean([m.investments for m in mf[-3:]])
        if recent_savings > early_savings * 1.15:
            signals.append(f"Savings increased by {((recent_savings/early_savings)-1)*100:.0f}% in recent months")
            score += 12

    # Check for home-related goals
    home_goals = [g for g in data.goals if any(w in g.name.lower() for w in ["house", "home", "flat", "apartment", "property"])]
    if home_goals:
        signals.append(f"Active goal: {home_goals[0].name}")
        score += 15

    # Cap at 95
    probability = min(95, score)

    timeline = "within 6 months" if probability > 70 else "within 12 months" if probability > 40 else "within 18-24 months"

    return {
        "event": "Home Purchase",
        "icon": "🏠",
        "probability": probability,
        "timeline": timeline,
        "signals": signals,
        "recommendations": [
            "Build emergency fund to 6 months before down payment",
            "Check home loan eligibility with current income and credit score",
            "Compare fixed vs floating rate options across banks",
            "Ensure down payment of 20-25% to avoid higher interest rates",
            "Factor in registration, stamp duty, and furnishing costs (add 10-15% to property cost)",
        ] if probability > 30 else [],
    }


def _detect_marriage(data: CustomerData) -> dict:
    signals = []
    score = 0

    # Jewelry purchases
    jewelry = [t for t in data.transactions if any(m in t.merchant.lower() for m in ["jewel", "tanishq", "kalyan", "gold"])]
    if jewelry:
        signals.append(f"Jewelry purchases: {len(jewelry)} transactions")
        score += 20

    # Venue/event bookings
    venue = [t for t in data.transactions if any(m in t.merchant.lower() for m in ["venue", "banquet", "hotel", "event", "wedding"])]
    if venue:
        signals.append("Event/venue bookings detected")
        score += 25

    # Large cash withdrawals
    cash = [t for t in data.transactions if t.channel == "cash" and t.amount > 50000]
    if len(cash) >= 2:
        signals.append(f"{len(cash)} large cash withdrawals")
        score += 10

    # Age-based probability boost (25-35 age range)
    if 25 <= data.profile.age <= 35:
        score += 5

    probability = min(95, score)
    timeline = "within 6 months" if probability > 60 else "within 12 months"

    return {
        "event": "Marriage",
        "icon": "💒",
        "probability": probability,
        "timeline": timeline,
        "signals": signals,
        "recommendations": [
            "Start a dedicated wedding fund SIP",
            "Review and increase life insurance coverage",
            "Plan for combined financial goals post-marriage",
        ] if probability > 30 else [],
    }


def _detect_child_planning(data: CustomerData) -> dict:
    signals = []
    score = 0

    # Hospital/medical visits spike
    medical = [t for t in data.transactions if t.category == "Healthcare" and t.amount > 3000]
    if len(medical) >= 3:
        signals.append(f"Increased healthcare spending ({len(medical)} significant transactions)")
        score += 15

    # Life insurance purchase
    life_ins = [t for t in data.transactions if "insurance" in t.category.lower() and "life" in t.merchant.lower()]
    if life_ins:
        signals.append("Recent life insurance activity")
        score += 10

    # Age and family size
    if 28 <= data.profile.age <= 40 and data.profile.dependents <= 1:
        score += 8

    # Education-related goal creation
    edu_goals = [g for g in data.goals if "child" in g.name.lower() or "education" in g.name.lower()]
    if edu_goals:
        signals.append("Child education goal detected")
        score += 15

    probability = min(95, score)
    timeline = "within 12-18 months"

    return {
        "event": "Child Planning",
        "icon": "👶",
        "probability": probability,
        "timeline": timeline,
        "signals": signals,
        "recommendations": [
            "Start child education SIP (₹5,000-10,000/month)",
            "Increase health insurance coverage",
            "Build emergency fund to 8-12 months of expenses",
        ] if probability > 30 else [],
    }


def _detect_job_change(data: CustomerData) -> dict:
    signals = []
    score = 0

    # Salary irregularity
    mf = data.monthly_financials
    if len(mf) >= 3:
        incomes = [m.income for m in mf]
        if any(i == 0 for i in incomes[-3:]):
            signals.append("Missing salary credits detected")
            score += 30

        # Sudden salary change
        if len(incomes) >= 2 and incomes[-1] != incomes[-2]:
            change = abs(incomes[-1] - incomes[-2]) / incomes[-2] * 100
            if change > 15:
                signals.append(f"Salary changed by {change:.0f}%")
                score += 15

    # Professional networking/LinkedIn premium
    prof = [t for t in data.transactions if any(m in t.merchant.lower() for m in ["linkedin", "naukri", "glassdoor"])]
    if prof:
        signals.append("Professional networking platform activity")
        score += 15

    probability = min(95, score)
    timeline = "within 3-6 months"

    return {
        "event": "Job Change",
        "icon": "💼",
        "probability": probability,
        "timeline": timeline,
        "signals": signals,
        "recommendations": [
            "Ensure 6+ months emergency fund before switching",
            "Evaluate new employer's benefits (insurance, PF contribution)",
            "Plan for potential notice period gap in income",
        ] if probability > 30 else [],
    }


def _detect_business_expansion(data: CustomerData) -> dict:
    signals = []
    score = 0

    # GST-related transactions
    gst = [t for t in data.transactions if "gst" in t.category.lower() or "gst" in t.merchant.lower()]
    if gst:
        signals.append("GST payment activity detected")
        score += 20

    # Equipment purchases
    equip = [t for t in data.transactions if any(m in t.merchant.lower() for m in ["equipment", "machinery", "commercial"])]
    if equip:
        signals.append("Business equipment purchases")
        score += 15

    probability = min(95, score)
    timeline = "within 6-12 months"

    return {
        "event": "Business Expansion",
        "icon": "🏢",
        "probability": probability,
        "timeline": timeline,
        "signals": signals,
        "recommendations": [
            "Explore business loans with competitive rates",
            "Consider separating personal and business finances",
        ] if probability > 30 else [],
    }


def _detect_vacation(data: CustomerData) -> dict:
    signals = []
    score = 0

    # Travel bookings
    travel = [t for t in data.transactions if any(m in t.merchant.lower() for m in ["makemytrip", "irctc", "goibibo", "booking", "airbnb", "airline"])]
    if travel:
        signals.append(f"Travel booking activity ({len(travel)} transactions)")
        score += 20

    # Vacation goal
    vac_goals = [g for g in data.goals if any(w in g.name.lower() for w in ["vacation", "travel", "trip", "goa", "holiday"])]
    if vac_goals:
        completion = vac_goals[0].current_amount / vac_goals[0].target_amount * 100 if vac_goals[0].target_amount > 0 else 0
        signals.append(f"Vacation goal {completion:.0f}% funded")
        if completion > 70:
            score += 25
        elif completion > 40:
            score += 15
        else:
            score += 8

    # Passport/visa activity
    passport = [t for t in data.transactions if any(m in t.merchant.lower() for m in ["passport", "visa", "embassy"])]
    if passport:
        signals.append("Passport/visa related activity")
        score += 15

    probability = min(95, score)
    timeline = "within 3-6 months" if probability > 50 else "within 6-12 months"

    return {
        "event": "Vacation / Travel",
        "icon": "✈️",
        "probability": probability,
        "timeline": timeline,
        "signals": signals,
        "recommendations": [
            "Consider a travel SIP for regular vacations",
            "Look into travel insurance for international trips",
            "Use credit card travel rewards for savings",
        ] if probability > 30 else [],
    }


def _detect_education(data: CustomerData) -> dict:
    signals = []
    score = 0

    # Education transactions
    edu = [t for t in data.transactions if any(m in t.merchant.lower() for m in ["coursera", "udemy", "upgrad", "university", "college", "school"])]
    if edu:
        signals.append(f"Education platform transactions ({len(edu)})")
        score += 15

    # Education goal
    edu_goals = [g for g in data.goals if "education" in g.name.lower()]
    if edu_goals:
        signals.append(f"Education fund goal active")
        score += 15

    probability = min(95, score)
    timeline = "within 12-18 months"

    return {
        "event": "Education Investment",
        "icon": "🎓",
        "probability": probability,
        "timeline": timeline,
        "signals": signals,
        "recommendations": [
            "Explore education loans with tax benefits",
            "Start an education SIP in equity funds for long-term goals",
        ] if probability > 30 else [],
    }
