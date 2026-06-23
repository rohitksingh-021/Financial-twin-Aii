"""Complete seed data for demo user Rahul Sharma.
All data is realistic for a 32-year-old IT professional in Mumbai earning ₹18L/year.
Transaction patterns include signals that suggest home purchase intent."""

from models.customer import (
    CustomerData, CustomerProfile, Transaction, Investment,
    Loan, Insurance, Goal, MonthlyFinancial, RiskAppetite
)


def get_seed_data() -> CustomerData:
    profile = CustomerProfile(
        name="Rahul Sharma",
        age=32,
        gender="Male",
        occupation="Senior Software Engineer",
        employer="Tata Consultancy Services",
        annual_income=1800000,
        monthly_income=150000,
        city="Mumbai",
        family_size=3,
        dependents=1,
        risk_appetite=RiskAppetite.MODERATE,
        pan_number="ABCPS1234K",
        account_number="IDBI0012345678",
    )

    monthly_financials = [
        MonthlyFinancial(month="2025-07", income=150000, rent=35000, groceries=12000, utilities=5000, transport=6000, entertainment=4000, healthcare=2000, education=0, shopping=8000, emi_total=15000, investments=25000, other=5000),
        MonthlyFinancial(month="2025-08", income=150000, rent=35000, groceries=11500, utilities=5200, transport=5500, entertainment=5000, healthcare=1500, education=0, shopping=7000, emi_total=15000, investments=25000, other=4500),
        MonthlyFinancial(month="2025-09", income=150000, rent=35000, groceries=12500, utilities=4800, transport=6200, entertainment=3500, healthcare=3000, education=0, shopping=6500, emi_total=15000, investments=25000, other=5500),
        MonthlyFinancial(month="2025-10", income=150000, rent=35000, groceries=11000, utilities=5100, transport=5800, entertainment=4500, healthcare=2500, education=0, shopping=9000, emi_total=15000, investments=28000, other=4000),
        MonthlyFinancial(month="2025-11", income=150000, rent=35000, groceries=13000, utilities=5500, transport=6500, entertainment=6000, healthcare=1800, education=0, shopping=12000, emi_total=15000, investments=25000, other=6000),
        MonthlyFinancial(month="2025-12", income=175000, rent=35000, groceries=14000, utilities=5300, transport=7000, entertainment=8000, healthcare=2200, education=0, shopping=15000, emi_total=15000, investments=30000, other=8000),
        MonthlyFinancial(month="2026-01", income=155000, rent=35000, groceries=12000, utilities=5000, transport=5500, entertainment=4000, healthcare=2000, education=0, shopping=7500, emi_total=15000, investments=30000, other=5000),
        MonthlyFinancial(month="2026-02", income=155000, rent=35000, groceries=11500, utilities=4800, transport=6000, entertainment=3500, healthcare=8000, education=0, shopping=6000, emi_total=15000, investments=30000, other=4500),
        MonthlyFinancial(month="2026-03", income=155000, rent=35000, groceries=12500, utilities=5200, transport=6500, entertainment=4000, healthcare=2500, education=0, shopping=18000, emi_total=15000, investments=30000, other=5000),
        MonthlyFinancial(month="2026-04", income=155000, rent=35000, groceries=13000, utilities=5000, transport=5800, entertainment=3000, healthcare=2000, education=0, shopping=22000, emi_total=15000, investments=32000, other=4500),
        MonthlyFinancial(month="2026-05", income=155000, rent=35000, groceries=12000, utilities=4900, transport=6200, entertainment=3500, healthcare=2200, education=0, shopping=15000, emi_total=15000, investments=32000, other=5000),
        MonthlyFinancial(month="2026-06", income=155000, rent=35000, groceries=12500, utilities=5100, transport=6000, entertainment=4000, healthcare=2000, education=0, shopping=8000, emi_total=15000, investments=32000, other=4500),
    ]

    investments = [
        Investment(id="inv-1", type="MF", name="HDFC Mid-Cap Opportunities Fund", invested_amount=350000, current_value=420000, start_date="2023-06-15", expected_return=14.0),
        Investment(id="inv-2", type="MF", name="SBI Blue Chip Fund (SIP ₹10,000/mo)", invested_amount=240000, current_value=275000, start_date="2024-01-10", expected_return=12.0),
        Investment(id="inv-3", type="FD", name="IDBI Bank FD — 7.1%", invested_amount=200000, current_value=214200, start_date="2024-06-01", expected_return=7.1),
        Investment(id="inv-4", type="PPF", name="Public Provident Fund", invested_amount=300000, current_value=332000, start_date="2021-04-01", expected_return=7.1),
        Investment(id="inv-5", type="stocks", name="Direct Equity (NIFTY 50 stocks)", invested_amount=150000, current_value=182000, start_date="2023-09-01", expected_return=15.0),
        Investment(id="inv-6", type="NPS", name="National Pension System — Tier 1", invested_amount=120000, current_value=138000, start_date="2022-01-01", expected_return=10.0),
        Investment(id="inv-7", type="gold", name="Sovereign Gold Bonds", invested_amount=100000, current_value=128000, start_date="2023-03-01", expected_return=8.0),
    ]

    loans = [
        Loan(id="loan-1", type="personal", principal=500000, outstanding=320000, emi=15000, tenure_remaining=24, interest_rate=11.5),
    ]

    insurance_policies = [
        Insurance(id="ins-1", type="term", provider="ICICI Prudential", sum_assured=10000000, annual_premium=12000, expiry_date="2053-06-15"),
        Insurance(id="ins-2", type="health", provider="Star Health", sum_assured=500000, annual_premium=15000, expiry_date="2027-03-01"),
    ]

    goals = [
        Goal(id="goal-1", name="Buy a House (₹80L)", target_amount=8000000, current_amount=1200000, deadline="2028-06-30", priority=1),
        Goal(id="goal-2", name="Emergency Fund (6 months)", target_amount=600000, current_amount=410000, deadline="2027-03-31", priority=2),
        Goal(id="goal-3", name="Retirement Corpus (₹5Cr)", target_amount=50000000, current_amount=1689200, deadline="2048-12-31", priority=3),
        Goal(id="goal-4", name="Goa Vacation", target_amount=150000, current_amount=128000, deadline="2026-12-31", priority=4),
    ]

    transactions = _generate_transactions()

    return CustomerData(
        profile=profile,
        monthly_financials=monthly_financials,
        investments=investments,
        loans=loans,
        insurance=insurance_policies,
        goals=goals,
        transactions=transactions,
    )


def _generate_transactions() -> list[Transaction]:
    """Generate 12 months of realistic transactions for Rahul Sharma.
    Includes signals that suggest home purchase intent (furniture, security deposits, etc.)"""
    txns = []

    # Helper to add bulk recurring transactions per month
    months = [
        "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12",
        "2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06",
    ]

    for i, m in enumerate(months):
        base_income = 150000 if i < 5 else (175000 if i == 5 else 155000)

        # Salary credit
        txns.append(Transaction(date=f"{m}-01", amount=base_income, category="Salary", merchant="TCS", type="credit", channel="NEFT"))

        # Rent
        txns.append(Transaction(date=f"{m}-05", amount=35000, category="Rent", merchant="Landlord", type="debit", channel="NEFT"))

        # EMI
        txns.append(Transaction(date=f"{m}-10", amount=15000, category="Loan EMI", merchant="IDBI Bank", type="debit", channel="NEFT"))

        # SIP investments
        sip_amount = 25000 if i < 3 else (28000 if i == 3 else (25000 if i == 4 else 30000 if i == 5 else 32000))
        txns.append(Transaction(date=f"{m}-15", amount=sip_amount, category="Investment", merchant="SBI MF / HDFC MF", type="debit", channel="NEFT"))

        # Groceries (multiple)
        txns.append(Transaction(date=f"{m}-03", amount=4000, category="Groceries", merchant="BigBasket", type="debit", channel="UPI"))
        txns.append(Transaction(date=f"{m}-12", amount=3500, category="Groceries", merchant="DMart", type="debit", channel="card"))
        txns.append(Transaction(date=f"{m}-22", amount=4500, category="Groceries", merchant="Zepto", type="debit", channel="UPI"))

        # Utilities
        txns.append(Transaction(date=f"{m}-08", amount=2200, category="Utility", merchant="BEST Electricity", type="debit", channel="UPI"))
        txns.append(Transaction(date=f"{m}-09", amount=1500, category="Utility", merchant="Jio Fiber", type="debit", channel="UPI"))
        txns.append(Transaction(date=f"{m}-10", amount=1300, category="Utility", merchant="Mahanagar Gas", type="debit", channel="UPI"))

        # Transport
        txns.append(Transaction(date=f"{m}-04", amount=2500, category="Transport", merchant="Uber", type="debit", channel="UPI"))
        txns.append(Transaction(date=f"{m}-18", amount=2000, category="Transport", merchant="Ola", type="debit", channel="UPI"))
        txns.append(Transaction(date=f"{m}-25", amount=1500, category="Transport", merchant="IRCTC", type="debit", channel="card"))

        # Entertainment
        txns.append(Transaction(date=f"{m}-06", amount=499, category="Subscription", merchant="Netflix", type="debit", channel="card"))
        txns.append(Transaction(date=f"{m}-06", amount=299, category="Subscription", merchant="Spotify", type="debit", channel="card"))
        txns.append(Transaction(date=f"{m}-14", amount=1200, category="Entertainment", merchant="PVR Cinemas", type="debit", channel="UPI"))

        # Food/Dining
        txns.append(Transaction(date=f"{m}-07", amount=800, category="Restaurant", merchant="Swiggy", type="debit", channel="UPI"))
        txns.append(Transaction(date=f"{m}-16", amount=1200, category="Restaurant", merchant="Zomato", type="debit", channel="UPI"))
        txns.append(Transaction(date=f"{m}-24", amount=2000, category="Restaurant", merchant="Barbeque Nation", type="debit", channel="card"))

        # Insurance premium (quarterly)
        if m in ["2025-09", "2025-12", "2026-03", "2026-06"]:
            txns.append(Transaction(date=f"{m}-20", amount=3000, category="Insurance", merchant="ICICI Prudential", type="debit", channel="NEFT"))
            txns.append(Transaction(date=f"{m}-20", amount=3750, category="Insurance", merchant="Star Health", type="debit", channel="NEFT"))

    # === HOME PURCHASE INTENT SIGNALS (recent months) ===

    # Furniture browsing/purchases (March-June 2026)
    txns.append(Transaction(date="2026-03-15", amount=8500, category="Shopping", merchant="Pepperfry", type="debit", channel="card"))
    txns.append(Transaction(date="2026-04-02", amount=12000, category="Shopping", merchant="IKEA", type="debit", channel="card"))
    txns.append(Transaction(date="2026-04-20", amount=6500, category="Shopping", merchant="Urban Ladder", type="debit", channel="UPI"))
    txns.append(Transaction(date="2026-05-10", amount=15000, category="Furniture", merchant="Godrej Interio", type="debit", channel="card"))

    # Property portal activity
    txns.append(Transaction(date="2026-03-08", amount=999, category="Subscription", merchant="MagicBricks Premium", type="debit", channel="card"))
    txns.append(Transaction(date="2026-04-12", amount=1499, category="Subscription", merchant="99acres Pro", type="debit", channel="card"))

    # Security deposit (large transfer — possibly flat advance)
    txns.append(Transaction(date="2026-05-22", amount=50000, category="Security Deposit", merchant="Property Advance", type="debit", channel="NEFT"))

    # Increased savings (visible in monthly financials)
    # Home loan inquiry signal
    txns.append(Transaction(date="2026-04-28", amount=500, category="Financial Services", merchant="CIBIL Score Check", type="debit", channel="card"))

    # Additional shopping in Nov-Dec (Diwali)
    txns.append(Transaction(date="2025-11-10", amount=8000, category="Shopping", merchant="Amazon", type="debit", channel="card"))
    txns.append(Transaction(date="2025-11-12", amount=4000, category="Shopping", merchant="Myntra", type="debit", channel="UPI"))
    txns.append(Transaction(date="2025-12-20", amount=6000, category="Shopping", merchant="Flipkart", type="debit", channel="card"))
    txns.append(Transaction(date="2025-12-25", amount=9000, category="Shopping", merchant="Croma", type="debit", channel="card"))

    # Healthcare spike in Feb (annual checkup)
    txns.append(Transaction(date="2026-02-05", amount=5000, category="Healthcare", merchant="Apollo Hospital", type="debit", channel="card"))
    txns.append(Transaction(date="2026-02-12", amount=3000, category="Healthcare", merchant="MedPlus Pharmacy", type="debit", channel="UPI"))

    return txns
