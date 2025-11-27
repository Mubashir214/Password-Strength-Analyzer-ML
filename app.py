import streamlit as st
import pandas as pd
import numpy as np
import joblib
import re

# ----------------------------
# Load ML Model & Scaler
# ----------------------------
model = joblib.load("password_model.pkl")
scaler = joblib.load("password_scaler.pkl")

# ----------------------------
# Feature Extraction
# ----------------------------
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

    features['common_pattern'] = int(bool(re.search(r"123|password|qwerty|abc", password.lower())))
    return features

# ----------------------------
# ML-only Prediction
# ----------------------------
def predict_strength(password):
    f = extract_features(password)
    df_f = pd.DataFrame([f])
    scaled = scaler.transform(df_f)

    # Predict class and probabilities
    pred_class = model.predict(scaled)[0]
    prob_array = model.predict_proba(scaled)[0]
    prob_dict = dict(zip(model.classes_, prob_array))

    return pred_class, prob_dict

# ----------------------------
# UI Colors
# ----------------------------
def get_color(label):
    if label == "very_weak":
        return "🔴 Very Weak"
    elif label == "weak":
        return "🟠 Weak"
    else:
        return "🟢 Strong"

# ----------------------------
# Streamlit App UI
# ----------------------------
st.set_page_config(page_title="Password Strength Analyzer", page_icon="🔐", layout="centered")
st.title("🔐 Password Strength Analyzer (ML Only)")
st.write("This tool analyzes your password **using the trained ML model only** (no manual rules).")

password = st.text_input("Enter a Password:", type="password")

if st.button("Analyze Password"):
    if password.strip() == "":
        st.warning("⚠ Please enter a password.")
    else:
        pred, probs = predict_strength(password)
        st.markdown(f"### Password Strength: {get_color(pred)}")

        # Show probabilities
        st.subheader("Prediction Probabilities")
        for k, v in probs.items():
            st.write(f"{k}: {v:.4f}")

        # Feature Analysis
        st.subheader("Feature Analysis")
        f = extract_features(password)
        st.json(f)

st.markdown("---")
st.caption("Developed by Mubashir & Taha — Information Security Project 2025")
