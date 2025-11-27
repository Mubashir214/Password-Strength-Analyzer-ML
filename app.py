import streamlit as st
import pandas as pd
import joblib
import re

# Load model and scaler
model = joblib.load("password_model.pkl")
scaler = joblib.load("password_scaler.pkl")

# Feature extraction function
def extract_features(password):
    features = {}
    features['length'] = len(password)
    features['upper'] = sum(1 for c in password if c.isupper())
    features['lower'] = sum(1 for c in password if c.islower())
    features['digits'] = sum(1 for c in password if c.isdigit())
    features['special'] = sum(1 for c in password if not c.isalnum())
    
    # Ratios
    features['digit_ratio'] = features['digits'] / max(1, features['length'])
    features['special_ratio'] = features['special'] / max(1, features['length'])
    features['upper_ratio'] = features['upper'] / max(1, features['length'])
    features['lower_ratio'] = features['lower'] / max(1, features['length'])
    
    # Common weak pattern
    features['common_pattern'] = int(bool(re.search(r'123|password|qwerty|abc', password.lower())))
    
    return features

# Prediction function
def predict_strength(password):
    f = extract_features(password)
    
    # Rule 1: Very short password
    if f['length'] < 6:
        return "Weak"
    
    # Rule 2: Exact common weak passwords
    common_weak = ['password', '12345', 'qwerty', 'abc123']
    if password.lower() in common_weak:
        return "Weak"
    
    # ML Prediction
    df_f = pd.DataFrame([f])
    scaled = scaler.transform(df_f)
    pred = model.predict(scaled)[0]
    
    # Rule 3: Strong override
    if f['length'] >= 12 and f['digits'] >= 2 and f['special'] >= 1 and f['upper'] >= 1 and f['lower'] >= 1:
        return "Strong"
    
    return pred

# Streamlit interface
st.title("🔒 Password Strength Analyzer")
st.write("Enter a password to check its strength (Weak / Medium / Strong)")

password_input = st.text_input("Enter your password", type="password")

if st.button("Check Strength"):
    if password_input.strip() == "":
        st.warning("Please enter a password!")
    else:
        strength = predict_strength(password_input)
        if strength == "Weak":
            st.error(f"Password Strength: {strength}")
        elif strength == "Medium":
            st.warning(f"Password Strength: {strength}")
        else:
            st.success(f"Password Strength: {strength}")
