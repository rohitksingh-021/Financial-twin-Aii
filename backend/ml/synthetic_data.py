import pandas as pd
import numpy as np

def generate_life_events_data(n_samples=2000):
    np.random.seed(42)
    
    age = np.random.randint(22, 60, n_samples)
    income = np.random.randint(50000, 300000, n_samples)
    savings_rate = np.random.uniform(0.05, 0.4, n_samples)
    
    # Feature indicating if they made large purchases (furniture/jewelry)
    large_purchases = np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
    # Feature for property searches or related
    property_search = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
    # Feature for credit score checks
    credit_checks = np.random.choice([0, 1], n_samples, p=[0.85, 0.15])
    
    # Generate labels based on some rules + noise
    # Home Purchase is likely if property_search=1, credit_checks=1, and savings_rate > 0.2
    prob_home = 0.05 + 0.4 * property_search + 0.3 * credit_checks + 0.1 * (savings_rate > 0.2) + 0.05 * (age > 28)
    home_purchase = (np.random.rand(n_samples) < prob_home).astype(int)
    
    # Marriage is likely if age is 25-32 and large purchases
    prob_marriage = 0.02 + 0.5 * large_purchases + 0.3 * ((age >= 25) & (age <= 32))
    marriage = (np.random.rand(n_samples) < prob_marriage).astype(int)
    
    df = pd.DataFrame({
        'age': age,
        'income': income,
        'savings_rate': savings_rate,
        'large_purchases': large_purchases,
        'property_search': property_search,
        'credit_checks': credit_checks,
        'label_home_purchase': home_purchase,
        'label_marriage': marriage
    })
    return df

def generate_stress_data(n_samples=2000):
    np.random.seed(42)
    
    emi_to_income = np.random.uniform(0, 0.8, n_samples)
    months_emergency_fund = np.random.uniform(0, 12, n_samples)
    recent_income_drop = np.random.choice([0, 1], n_samples, p=[0.9, 0.1])
    missed_payments = np.random.choice([0, 1], n_samples, p=[0.95, 0.05])
    
    prob_stress = 0.05 + 0.4 * (emi_to_income > 0.5) + 0.3 * (months_emergency_fund < 2) + 0.5 * recent_income_drop + 0.8 * missed_payments
    prob_stress = np.clip(prob_stress, 0, 1)
    
    # Label 1 = High Stress Risk, 0 = Normal
    stress_risk = (np.random.rand(n_samples) < prob_stress).astype(int)
    
    df = pd.DataFrame({
        'emi_to_income': emi_to_income,
        'months_emergency_fund': months_emergency_fund,
        'recent_income_drop': recent_income_drop,
        'missed_payments': missed_payments,
        'label_stress': stress_risk
    })
    return df

if __name__ == "__main__":
    df_life = generate_life_events_data()
    print("Life Events Sample:\n", df_life.head())
    
    df_stress = generate_stress_data()
    print("Stress Sample:\n", df_stress.head())
