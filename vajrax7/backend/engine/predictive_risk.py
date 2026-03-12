# 4.3 Phase 3 – Predictive Supplier Risk Modeling
from models import RiskFeatureInputs

# Weights for the scoring model (w1 to w5)
# In a real scenario these might come from a trained ML model. For demo, we split 1.0 equally or reasonably.
DEFAULT_WEIGHTS = {
    "flood": 0.20,
    "earthquake": 0.20,
    "political": 0.20,
    "transportation": 0.25,
    "infrastructure": 0.15
}

def calculate_supplier_risk_probability(inputs: RiskFeatureInputs, weights: dict = DEFAULT_WEIGHTS) -> float:
    """
    SRP = w₁F + w₂E + w₃P + w₄T + w₅R
    """
    srp = (
        weights["flood"] * inputs.flood_severity +
        weights["earthquake"] * inputs.earthquake_risk +
        weights["political"] * inputs.political_instability +
        weights["transportation"] * inputs.transportation_disruption +
        weights["infrastructure"] * inputs.regional_infrastructure_risk
    )
    return srp

import os
import joblib

def predict_with_ml_model(inputs: RiskFeatureInputs) -> float:
    """
    B. Machine Learning Model (Optional Advanced Layer)
    Loads the trained Logistic Regression model from risk_model.pkl
    and outputs the probability of supplier disruption.
    """
    model_path = os.path.join(os.path.dirname(__file__), 'risk_model.pkl')
    
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            # The model expects a 2D array representing the 5 features
            feature_array = [[
                inputs.flood_severity,
                inputs.earthquake_risk,
                inputs.political_instability,
                inputs.transportation_disruption,
                inputs.regional_infrastructure_risk
            ]]
            # predict_proba returns [[P(class=0), P(class=1)]]
            # We want the probability of disruption (class=1)
            disruption_prob = model.predict_proba(feature_array)[0][1]
            return float(disruption_prob)
        except Exception as e:
            print(f"Error loading ML model from {model_path}: {e}")
            # Fallback to the static calculation if ML fails
            return calculate_supplier_risk_probability(inputs)
    else:
        print(f"ML Model not found at {model_path}. Falling back to formula.")
        return calculate_supplier_risk_probability(inputs)

def classify_risk(srp: float) -> str:
    """
    SRP > 0.7 → HIGH
    0.4–0.7 → MEDIUM
    < 0.4 → LOW
    """
    if srp > 0.7:
        return "HIGH"
    elif srp >= 0.4:  # Using >= 0.4 to handle the exact 0.4 bound cleanly based on spec "0.4-0.7"
        return "MEDIUM"
    else:
        return "LOW"

def run_phase3(inputs: RiskFeatureInputs, use_ml: bool = False) -> dict:
    if use_ml:
        srp = predict_with_ml_model(inputs)
    else:
        srp = calculate_supplier_risk_probability(inputs)
        
    # The model weights may average down an extreme single risk.
    # To correctly capture acute threats like a severe flood alone, 
    # we take the max of the individual feature risks if it is exceptionally high.
    max_single_risk = max([
        inputs.flood_severity,
        inputs.earthquake_risk,
        inputs.political_instability,
        inputs.transportation_disruption,
        inputs.regional_infrastructure_risk
    ])
    
    # If any individual risk is >= 0.7, ensure SRP reflects that severity
    if max_single_risk >= 0.7:
        srp = max(srp, max_single_risk)
        
    classification = classify_risk(srp)
    
    return {
        "supplier_risk_probability": round(srp, 2),
        "risk_classification": classification
    }
