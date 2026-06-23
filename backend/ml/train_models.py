import os
import pickle
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from synthetic_data import generate_life_events_data, generate_stress_data

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'saved_models')

def train_and_save():
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # 1. Life Events Models
    print("Training Life Events Models...")
    df_life = generate_life_events_data()
    X_life = df_life[['age', 'income', 'savings_rate', 'large_purchases', 'property_search', 'credit_checks']]
    
    # Home Purchase Model
    y_home = df_life['label_home_purchase']
    X_train, X_test, y_train, y_test = train_test_split(X_life, y_home, test_size=0.2, random_state=42)
    model_home = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    model_home.fit(X_train, y_train)
    acc = accuracy_score(y_test, model_home.predict(X_test))
    print(f"Home Purchase Model Accuracy: {acc:.2f}")
    with open(os.path.join(MODEL_DIR, 'home_purchase.pkl'), 'wb') as f:
        pickle.dump(model_home, f)
        
    # Marriage Model
    y_mar = df_life['label_marriage']
    X_train, X_test, y_train, y_test = train_test_split(X_life, y_mar, test_size=0.2, random_state=42)
    model_mar = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    model_mar.fit(X_train, y_train)
    acc = accuracy_score(y_test, model_mar.predict(X_test))
    print(f"Marriage Model Accuracy: {acc:.2f}")
    with open(os.path.join(MODEL_DIR, 'marriage.pkl'), 'wb') as f:
        pickle.dump(model_mar, f)

    # 2. Stress Model
    print("\nTraining Stress Model...")
    df_stress = generate_stress_data()
    X_stress = df_stress[['emi_to_income', 'months_emergency_fund', 'recent_income_drop', 'missed_payments']]
    y_stress = df_stress['label_stress']
    
    X_train, X_test, y_train, y_test = train_test_split(X_stress, y_stress, test_size=0.2, random_state=42)
    model_stress = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    model_stress.fit(X_train, y_train)
    acc = accuracy_score(y_test, model_stress.predict(X_test))
    print(f"Stress Model Accuracy: {acc:.2f}")
    with open(os.path.join(MODEL_DIR, 'stress.pkl'), 'wb') as f:
        pickle.dump(model_stress, f)

if __name__ == "__main__":
    train_and_save()
    print("All models trained and saved to", MODEL_DIR)
