import streamlit as st
import pandas as pd
import joblib
import re
import numpy as np

# ----------------------------
# Load Model & Scaler
# ----------------------------
model = joblib.load("password_model.pkl")
scaler = joblib.load("password_scaler.pkl")

# ----------------------------
# Feature Extraction Function
# ----------------------------
def extract_features(password):
    features = {}
    features['length'] = len(password)
    features['upper'] = sum(1 for c in password if c.isupper())
    features['lower'] = sum(1 for c in password if c.islower())
    features['digits'] = sum(1 for c in password if c.isdigit())
    features['special'] = sum(1 for c in password if not c.isalnum())
    
    features['digit_ratio'] = features['digits'] / max(1, features['length'])
    features['special_ratio'] = features['special'] / max(1, features['length'])
    features['upper_ratio'] = features['upper'] / max(1, features['length'])
    features['lower_ratio'] = features['lower'] / max(1, features['length'])
    
    # Common weak patterns
    features['common_pattern'] = int(bool(re.search(r"123|password|qwerty|abc", password.lower())))
    
    return features

# ----------------------------
# PURE ML Prediction
# ----------------------------
def predict_strength(password):
    f = extract_features(password)
    df_f = pd.DataFrame([f])
    scaled = scaler.transform(df_f)
    
    pred = model.predict(scaled)[0]
    probs = model.predict_proba(scaled)[0]
    
    # Return label + class probabilities as dict
    prob_dict = dict(zip(model.classes_, probs))
    return pred, prob_dict

# ----------------------------
# Color Function
# ----------------------------
def get_color(label):
    if label == "very_weak":
        return "🔴 Very Weak Password"
    elif label == "weak":
        return "🟠 Weak Password"
    else:
        return "🟢 Strong Password"

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="Password Strength Analyzer", page_icon="🔐", layout="centered")

st.title("🔐 Password Strength Analyzer")
st.write("This tool analyzes your password using **Machine Learning only** (no manual rules).")

password = st.text_input("Enter a Password:", type="password")

if st.button("Analyze Password"):
    if password.strip() == "":
        st.warning("⚠ Please enter a password.")
    else:
        pred_label, probs = predict_strength(password)
        st.markdown(f"### {get_color(pred_label)}")

        # Show probabilities
        st.subheader("📊 Prediction Probabilities")
        prob_df = pd.DataFrame.from_dict(probs, orient='index', columns=['Probability'])
        prob_df['Probability'] = prob_df['Probability'].apply(lambda x: f"{x*100:.2f}%")
        st.table(prob_df)

        # Detailed Feedback
        st.subheader("🔎 Security Suggestions")
        if pred_label == "very_weak":
            st.error("Your password is extremely weak! Avoid common patterns and increase complexity.")
        elif pred_label == "weak":
            st.warning("Your password is weak. Add more digits, special characters, and uppercase letters.")
        else:
            st.success("Your password is strong! Good job 👍")

        # Show extracted features
        st.subheader("🧠 Feature Analysis")
        f = extract_features(password)
        st.json(f)

# Footer
st.markdown("---")
st.caption("Developed by Mubashir & Taha — Information Security Project 2025")
