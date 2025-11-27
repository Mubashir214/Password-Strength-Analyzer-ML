import streamlit as st
import pandas as pd
import joblib
import re
from streamlit_lottie import st_lottie
import requests
import json

# Load model and scaler
model = joblib.load("password_model.pkl")
scaler = joblib.load("password_scaler.pkl")

# Load Lottie animations
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Lottie animations for different strength levels
lottie_weak = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_kdxqc1ms.json")
lottie_medium = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_u8ojfU.json")
lottie_strong = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_ukgjvscx.json")
lottie_lock = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_mDnmhAgZkb.json")

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

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .password-input {
        border-radius: 15px;
        padding: 15px;
        border: 2px solid #e0e0e0;
        font-size: 1.1rem;
    }
    .strength-card {
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        margin: 2rem 0;
    }
    .weak-card {
        background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
        color: white;
    }
    .medium-card {
        background: linear-gradient(135deg, #ffd93d, #ffed4e);
        color: #333;
    }
    .strong-card {
        background: linear-gradient(135deg, #6bcf7f, #4cd964);
        color: white;
    }
    .check-button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 12px 30px;
        font-size: 1.1rem;
        border-radius: 25px;
        cursor: pointer;
        width: 100%;
        margin-top: 1rem;
    }
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin-top: 2rem;
    }
    .feature-item {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .tips-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 15px;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Streamlit interface
st.markdown('<div class="main-header">🔒 Password Strength Analyzer</div>', unsafe_allow_html=True)

# Header with animation
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if lottie_lock:
        st_lottie(lottie_lock, height=200, key="lock")

st.markdown("""
<div style='text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;'>
    Enter your password below to analyze its security strength and get instant feedback
</div>
""", unsafe_allow_html=True)

# Password input section
with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password_input = st.text_input(
            "🔑 Enter your password", 
            type="password", 
            placeholder="Type your password here...",
            help="We don't store or save your password anywhere"
        )

        if st.button("🔍 Analyze Password Strength", use_container_width=True):
            if not password_input.strip():
                st.warning("⚠️ Please enter a password to analyze!")
            else:
                with st.spinner("🔐 Analyzing your password..."):
                    strength = predict_strength(password_input)
                    
                    # Display result with animation and styling
                    features = extract_features(password_input)
                    
                    if strength == "Weak":
                        st.markdown(f"""
                        <div class="strength-card weak-card">
                            <h2>⚠️ WEAK PASSWORD</h2>
                            <p style='font-size: 1.2rem;'>Your password needs significant improvement</p>
                        </div>
                        """, unsafe_allow_html=True)
                        if lottie_weak:
                            st_lottie(lottie_weak, height=150, key="weak")
                            
                    elif strength == "Medium":
                        st.markdown(f"""
                        <div class="strength-card medium-card">
                            <h2>🔄 MEDIUM PASSWORD</h2>
                            <p style='font-size: 1.2rem;'>Good start, but could be stronger</p>
                        </div>
                        """, unsafe_allow_html=True)
                        if lottie_medium:
                            st_lottie(lottie_medium, height=150, key="medium")
                            
                    else:
                        st.markdown(f"""
                        <div class="strength-card strong-card">
                            <h2>✅ STRONG PASSWORD</h2>
                            <p style='font-size: 1.2rem;'>Excellent! Your password is very secure</p>
                        </div>
                        """, unsafe_allow_html=True)
                        if lottie_strong:
                            st_lottie(lottie_strong, height=150, key="strong")
                    
                    # Password features breakdown
                    st.subheader("📊 Password Analysis")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Length", features['length'])
                    with col2:
                        st.metric("Uppercase", features['upper'])
                    with col3:
                        st.metric("Digits", features['digits'])
                    with col4:
                        st.metric("Special", features['special'])
                    
                    # Password tips
                    with st.expander("💡 Tips to Improve Your Password"):
                        st.markdown("""
                        - **Use at least 12 characters**
                        - **Mix uppercase and lowercase letters**
                        - **Include numbers and special characters**
                        - **Avoid common words and patterns**
                        - **Don't use personal information**
                        - **Consider using a passphrase**
                        - **Use unique passwords for different accounts**
                        """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888;'>"
    "🔒 Your password security is our priority. We never store or transmit your passwords."
    "</div>", 
    unsafe_allow_html=True
)
