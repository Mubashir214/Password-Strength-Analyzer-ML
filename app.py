import streamlit as st
import pandas as pd
import numpy as np
import joblib
import re
import os

# ----------------------------
# Load Model & Scaler with Error Handling
# ----------------------------
def load_models():
    """Load models with proper error handling"""
    try:
        model = joblib.load("password_model.pkl")
        scaler = joblib.load("password_scaler.pkl")
        return model, scaler, True
    except FileNotFoundError:
        st.error("❌ Model files not found. Please ensure 'password_model.pkl' and 'password_scaler.pkl' are in the app directory.")
        return None, None, False
    except Exception as e:
        st.error(f"❌ Error loading models: {str(e)}")
        return None, None, False

model, scaler, models_loaded = load_models()

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

    # Common Weak Patterns
    features['common_pattern'] = int(bool(re.search(r"123|password|qwerty|abc", password.lower())))

    return features

# ----------------------------
# Rule-based Prediction (Fallback)
# ----------------------------
def rule_based_predict(features, password):
    """Advanced rule-based password strength prediction"""
    pw_lower = password.lower()
    
    # Very weak conditions
    very_weak_patterns = ["password", "12345", "123456", "12345678", "123456789", 
                         "qwerty", "abc123", "admin", "welcome", "letmein", "monkey"]
    
    if (features['length'] <= 4 or
        pw_lower in very_weak_patterns or
        features['common_pattern'] == 1):
        return "very_weak"
    
    # Weak conditions
    if (features['length'] <= 6 or
        features['digits'] == 0 or
        features['upper'] == 0 or
        features['special'] == 0):
        return "weak"
    
    # Strong conditions
    if (features['length'] >= 12 and
        features['digits'] >= 2 and
        features['special'] >= 2 and
        features['upper'] >= 2 and
        features['lower'] >= 3):
        return "strong"
    
    # Medium to Strong conditions
    if (features['length'] >= 10 and
        features['digits'] >= 1 and
        features['special'] >= 1 and
        features['upper'] >= 1 and
        features['lower'] >= 4):
        return "strong"
    
    return "weak"

# ----------------------------
# ML Prediction with Feature Alignment
# ----------------------------
def ml_predict(features):
    """ML prediction with proper feature alignment"""
    try:
        # Create DataFrame with expected feature names
        expected_features = [
            'length', 'upper', 'lower', 'digits', 'special',
            'digit_ratio', 'special_ratio', 'upper_ratio', 'lower_ratio', 
            'common_pattern'
        ]
        
        # Ensure all expected features are present
        feature_row = [features.get(feature, 0) for feature in expected_features]
        df_f = pd.DataFrame([feature_row], columns=expected_features)
        
        # Scale features
        scaled = scaler.transform(df_f)
        
        # Predict
        pred = model.predict(scaled)[0]
        return pred
        
    except Exception as e:
        st.sidebar.warning(f"⚠️ ML prediction failed: {str(e)}. Using rule-based method.")
        return None

# ----------------------------
# Main Prediction Logic
# ----------------------------
def predict_strength(password):
    f = extract_features(password)
    pw_lower = password.lower()

    # RULE 1: Very short passwords → very_weak
    if f['length'] <= 4:
        return "very_weak"

    # RULE 2: Common weak passwords
    common_weak_list = ["password", "12345", "123456", "qwerty", "abc123", "admin", "welcome"]
    if pw_lower in common_weak_list:
        return "very_weak"

    # RULE 3: Very strong override (applies regardless of ML)
    if (f['length'] >= 12 and f['digits'] >= 2 and 
        f['special'] >= 2 and f['upper'] >= 2 and f['lower'] >= 4):
        return "strong"

    # Use ML if available and working
    if models_loaded and model is not None and scaler is not None:
        ml_pred = ml_predict(f)
        if ml_pred is not None:
            return ml_pred

    # Fallback to rule-based prediction
    return rule_based_predict(f, password)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .sub-header {
        text-align: center;
        font-size: 1.3rem;
        color: #666;
        margin-bottom: 3rem;
    }
    .password-input {
        border-radius: 15px;
        padding: 15px;
        border: 2px solid #e0e0e0;
        font-size: 1.1rem;
        width: 100%;
    }
    .strength-card {
        padding: 2.5rem;
        border-radius: 25px;
        box-shadow: 0 12px 35px rgba(0,0,0,0.15);
        text-align: center;
        margin: 2rem 0;
        border: none;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    .very-weak-card {
        background: linear-gradient(135deg, #ff4757, #ff3838);
        color: white;
        animation: pulse 2s infinite;
    }
    .weak-card {
        background: linear-gradient(135deg, #ff9f43, #ffa502);
        color: white;
    }
    .strong-card {
        background: linear-gradient(135deg, #2ed573, #1dd1a1);
        color: white;
        animation: celebrate 1s ease;
    }
    .check-button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 16px 45px;
        font-size: 1.3rem;
        border-radius: 30px;
        cursor: pointer;
        width: 100%;
        margin: 1.5rem 0;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    .check-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    .metric-card {
        background: white;
        padding: 1.8rem;
        border-radius: 18px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        margin: 0.8rem;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: scale(1.05);
    }
    .security-icon {
        font-size: 3rem;
        margin-bottom: 1.5rem;
        animation: bounce 2s infinite;
    }
    .progress-bar {
        height: 12px;
        border-radius: 15px;
        margin: 1.5rem 0;
        background: #e0e0e0;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        border-radius: 15px;
        transition: all 0.8s ease;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    @keyframes celebrate {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    .success-animation {
        animation: celebrate 1s ease;
    }
    .warning-section {
        background: linear-gradient(135deg, #fff9e6, #ffeaa7);
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        border-left: 5px solid #fdcb6e;
    }
    .critical-section {
        background: linear-gradient(135deg, #ffe6e6, #ff7675);
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        border-left: 5px solid #ff4757;
        animation: pulse 2s infinite;
    }
    .info-box {
        background: linear-gradient(135deg, #d6e4ff, #84a9ff);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #4d7cfe;
    }
    .model-status {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="Password Strength Analyzer", page_icon="🔐", layout="centered")

st.markdown('<div class="main-header">🔐 Password Strength Analyzer</div>', unsafe_allow_html=True)
st.markdown("""
<div class="sub-header">
    Advanced Security Analysis • Protect your digital identity
</div>
""", unsafe_allow_html=True)

# Display model status
if models_loaded:
    st.markdown("""
    <div class="info-box">
        <strong>🤖 AI-Powered Analysis:</strong> Using Machine Learning model for advanced password strength prediction
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="info-box">
        <strong>⚡ Rule-Based Analysis:</strong> Using advanced security rules for password strength evaluation
    </div>
    """, unsafe_allow_html=True)

# Main content
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Password input section
    st.markdown("### 🔑 Enter Your Password")
    password = st.text_input(
        "", 
        type="password", 
        placeholder="Type your password here for security analysis...",
        label_visibility="collapsed",
        help="🔒 Your password is analyzed locally and never stored"
    )
    
    # Analyze button
    if st.button("🚀 Analyze Password Security", use_container_width=True):
        if password.strip() == "":
            st.warning("⚠️ Please enter a password to analyze!")
        else:
            with st.spinner("🔍 Analyzing password strength..."):
                import time
                time.sleep(0.5)
                
                strength = predict_strength(password)
                features = extract_features(password)
                
                # Progress bar visualization
                st.markdown("### 📊 Security Level Analysis")
                
                strength_progress = {
                    "very_weak": {"width": 15, "color": "#ff4757", "emoji": "🔴"},
                    "weak": {"width": 40, "color": "#ffa502", "emoji": "🟠"}, 
                    "strong": {"width": 90, "color": "#2ed573", "emoji": "🟢"}
                }
                
                progress_info = strength_progress[strength]
                
                st.markdown(f"""
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {progress_info['width']}%; background: {progress_info['color']};"></div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display beautiful result card
                if strength == "very_weak":
                    st.markdown(f"""
                    <div class="strength-card very-weak-card">
                        <div class="security-icon">🚨</div>
                        <h1 style='font-size: 2.5rem; margin: 0;'>CRITICAL RISK</h1>
                        <p style='font-size: 1.4rem; font-weight: bold;'>Very Weak Password</p>
                        <p style='font-size: 1.1rem;'>Your password poses immediate security threats</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="critical-section">
                        <h3>🚨 IMMEDIATE ACTION REQUIRED</h3>
                        <p><b>This password can be cracked in seconds!</b> Avoid common patterns, 
                        increase length, and add character variety immediately.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                elif strength == "weak":
                    st.markdown(f"""
                    <div class="strength-card weak-card">
                        <div class="security-icon">⚠️</div>
                        <h1 style='font-size: 2.2rem; margin: 0;'>MODERATE RISK</h1>
                        <p style='font-size: 1.4rem; font-weight: bold;'>Weak Password</p>
                        <p style='font-size: 1.1rem;'>Your password needs significant improvement</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="warning-section">
                        <h3>⚠️ SECURITY IMPROVEMENT NEEDED</h3>
                        <p><b>This password is vulnerable to attacks!</b> Add more digits, 
                        special characters, uppercase letters, and increase length.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                else:
                    st.markdown(f"""
                    <div class="strength-card strong-card success-animation">
                        <div class="security-icon">🎉</div>
                        <h1 style='font-size: 2.5rem; margin: 0;'>EXCELLENT SECURITY</h1>
                        <p style='font-size: 1.4rem; font-weight: bold;'>Strong Password</p>
                        <p style='font-size: 1.1rem;'>Your password provides robust protection</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.balloons()
                    st.success("### ✅ Perfect! Your password meets high security standards!")
                
                # Password composition analysis
                st.markdown("### 🧩 Password Composition")
                
                cols = st.columns(4)
                metrics_data = [
                    {"icon": "📏", "value": features['length'], "label": "Length"},
                    {"icon": "🔠", "value": features['upper'], "label": "Uppercase"},
                    {"icon": "🔢", "value": features['digits'], "label": "Digits"}, 
                    {"icon": "⭐", "value": features['special'], "label": "Special"}
                ]
                
                for i, metric in enumerate(metrics_data):
                    with cols[i]:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h2 style='font-size: 2rem; margin: 0;'>{metric['icon']}</h2>
                            <h3 style='font-size: 2rem; margin: 0.5rem 0; color: #2c3e50;'>{metric['value']}</h3>
                            <p style='margin: 0; font-weight: bold; color: #666;'>{metric['label']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Security recommendations
                with st.expander("💡 **Security Recommendations & Best Practices**", expanded=True):
                    st.markdown("""
                    <div style="background: #f8f9fa; padding: 2rem; border-radius: 15px;">
                        <h4>🎯 How to Create Strong Passwords:</h4>
                        <ul style="text-align: left; font-size: 1.1rem;">
                            <li><b>Use 12+ characters</b> - Longer passwords are exponentially stronger</li>
                            <li><b>Mix character types</b> - Upper/lower case, numbers, symbols</li>
                            <li><b>Avoid dictionary words</b> - Use random combinations</li>
                            <li><b>No personal information</b> - Names, birthdays, pet names</li>
                            <li><b>Unique for each account</b> - Prevent credential stuffing</li>
                            <li><b>Consider passphrases</b> - "PurpleDragon$FliesHigh42!"</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888; padding: 2rem; font-size: 1.1rem;'>"
    "🔒 <b>Privacy First:</b> All analysis happens locally in your browser. "
    "We never store, transmit, or save your passwords. Your security is our priority."
    "</div>", 
    unsafe_allow_html=True
)

# Sidebar
with st.sidebar:
    st.markdown("## ℹ️ About This Tool")
    
    # Model status
    if models_loaded:
        st.success("### 🤖 ML Model: ✅ Loaded")
    else:
        st.warning("### ⚡ ML Model: Using Rule-Based")
        st.markdown("""
        *To use ML model, upload:*
        - `password_model.pkl`
        - `password_scaler.pkl`
        """)
    
    st.markdown("""
    ### 🛡️ Security Levels:
    **🔴 Very Weak:** Immediate risk, easily crackable  
    **🟠 Weak:** Vulnerable to basic attacks  
    **🟢 Strong:** Robust protection
    
    ---
    ### 👨‍💻 Developed By
    **Mubashir & Taha**  
    Information Security Project 2025
    """)
