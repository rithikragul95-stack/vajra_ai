import os
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

def train_and_save_model():
    print("Generating synthetic supply chain risk data...")
    # Features: [Flood, Earthquake, Political, Transportation, Infrastructure]
    # We will generate synthetic data where high values generally lead to higher risk (label=1)
    
    np.random.seed(42)
    X = np.random.rand(1000, 5)
    
    # Let's say risk probability is roughly based on the existing formula:
    # SRP = w1*F + w2*E + w3*P + w4*T + w5*R
    # with weights: 0.2, 0.2, 0.2, 0.25, 0.15
    weights = np.array([0.20, 0.20, 0.20, 0.25, 0.15])
    
    y_prob = np.dot(X, weights)
    
    # Add a little noise
    y_prob += np.random.normal(0, 0.05, 1000)
    
    # Convert probabilities to a binary target for classification training
    # For a logistic regression model predicting probability, we need 0/1 targets.
    # We'll consider anything above 0.5 as "disrupted" (1).
    # Critical Fix: Also enforce that if ANY single risk factor is very high (>=0.7), it must be disrupted
    max_risk = np.max(X, axis=1)
    y = ((y_prob > 0.5) | (max_risk >= 0.7)).astype(int)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Logistic Regression Model...")
    model = LogisticRegression()
    model.fit(X_train, y_train)
    
    # Evaluate
    score = model.score(X_test, y_test)
    print(f"Model Accuracy on Test Set: {score:.4f}")
    
    # Save the model
    model_path = os.path.join(os.path.dirname(__file__), 'risk_model.pkl')
    print(f"Saving model to {model_path}...")
    joblib.dump(model, model_path)
    
    print("Model training and saving complete.")

if __name__ == "__main__":
    train_and_save_model()
