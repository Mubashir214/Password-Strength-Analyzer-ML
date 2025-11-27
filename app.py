import streamlit as st
import pandas as pd
import numpy as np
import joblib
import re
import os

# ----------------------------
# Load Model & Scaler with Debug Info
# ----------------------------
def load_models():
    """Load models with proper error handling and debug info"""
    try:
        model = joblib.load("password_model.pkl")
        scaler = joblib.load("password_scaler.pkl")
        
        # Debug: Print model info
        st.sidebar.success("✅ Model loaded successfully!")
        st.sidebar.info(f"Model type: {type(model)}")
        
        # Try to get feature names if available
        try:
            if hasattr(model, 'feature_names_in_'):
                st.sidebar.info(f"Features expected: {list(model.feature_names_in_)}")
        except:
            pass
            
        return model, scaler, True
        
    except FileNotFoundError:
        st.sidebar.error("❌ Model files not found.")
        return None, None, False
    except Exception as e:
        st.sidebar.error(f"❌ Error loading models: {str(e)}")
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
    features['common_pattern_any'] = int(bool(re.search(r"123|password|qwerty|abc|admin|welcome|123456|letmein", password.lower())))

    return features

# ----------------------------
# Rule-based Prediction (Fallback)
# ----------------------------
def rule_based_predict(features, password):
    """Advanced rule-based password strength prediction"""
    pw_lower = password.lower()
    
    # Very weak conditions
    very_weak_patterns = ["password", "12345", "123456", "12345678", "123456789", 
                         "qwerty", "abc123", "admin", "welcome", "letmein", "monkey",
                         "password1", "1234", "123", "qwerty123", "iloveyou", "sunshine"]
    
    if (features['length'] <= 4 or
        pw_lower in very_weak_patterns or
        features['common_pattern_any'] == 1):
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
# ML Prediction with Robust Output Handling
# ----------------------------
def ml_predict(features):
    """ML prediction with robust output handling"""
    try:
        # Expected feature names based on common patterns
        expected_features = [
            'length', 'upper', 'lower', 'digits', 'special',
            'digit_ratio', 'special_ratio', 'upper_ratio', 'lower_ratio', 
            'common_pattern_any'
        ]
        
        # Create feature row in correct order
        feature_row = [features[feature] for feature in expected_features]
        df_f = pd.DataFrame([feature_row], columns=expected_features)
        
        # Scale features
        scaled = scaler.transform(df_f)
        
        # Predict and handle different output types
        raw_pred = model.predict(scaled)
        
        # Debug the raw prediction
        st.sidebar.info(f"Raw prediction: {raw_pred} (type: {type(raw_pred)})")
        
        # Handle different prediction output formats
        if hasattr(raw_pred, '__len__') and len(raw_pred) > 0:
            pred_value = raw_pred[0]
        else:
            pred_value = raw_pred
            
        # Convert prediction to our strength scale
        return convert_ml_prediction(pred_value)
        
    except Exception as e:
        st.sidebar.warning(f"⚠️ ML prediction failed: {str(e)}")
        return None

def convert_ml_prediction(pred_value):
    """Convert ML prediction to our strength categories"""
    # Debug the prediction value
    st.sidebar.info(f"Prediction value: {pred_value} (type: {type(pred_value)})")
    
    # Handle numeric predictions (0-1 scale or class probabilities)
    if isinstance(pred_value, (int, float, np.number)):
        if pred_value <= 0.33:
            return "very_weak"
        elif pred_value <= 0.66:
            return "weak"
        else:
            return "strong"
    
    # Handle string predictions
    elif isinstance(pred_value, str):
        pred_lower = pred_value.lower()
        if 'very_weak' in pred_lower or 'weak' in pred_lower or pred_lower == '0':
            return "very_weak"
        elif 'strong' in pred_lower or pred_lower == '2':
            return "strong"
        elif 'medium' in pred_lower or pred_lower == '1':
            return "weak"
        else:
            # Default for unknown strings
            return "weak"
    
    # Default fallback
    return "weak"

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
    common_weak_list = ["password", "12345", "123456", "qwerty", "abc123", "admin", "welcome", "letmein"]
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
            st.sidebar.success(f"🤖 ML Prediction: {ml_pred}")
            return ml_pred

    # Fallback to rule-based prediction
    rule_pred = rule_based_predict(f, password)
    st.sidebar.success(f"⚡ Rule-Based Prediction: {rule_pred}")
    return rule_pred

# ----------------------------
# UI Configuration
# ----------------------------
st.set_page_config(
    page_title="Password Strength Analyzer", 
    page_icon="🔐", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
    .strength-card {
        padding: 2.5rem;
        border-radius: 25px;
        box-shadow: 0 12px 35px rgba(0,0,0,0.15);
        text-align: center;
        margin: 2rem 0;
        border: none;
        transition: all 0.3s ease;
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
    }
    .metric-card {
        background: white;
        padding: 1.8rem;
        border-radius: 18px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        margin: 0.8rem;
    }
    .security-icon {
        font-size: 3rem;
        margin-bottom: 1.5rem;
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
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Main UI
# ----------------------------
st.markdown('<div class="main-header">🔐 Password Strength Analyzer</div>', unsafe_allow_html=True)
st.markdown("""
<div class="sub-header">
    Advanced Security Analysis • Protect your digital identity
</div>
""", unsafe_allow_html=True)

# Main content
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("### 🔑 Enter Your Password")
    password = st.text_input(
        "", 
        type="password", 
        placeholder="Type your password here...",
        label_visibility="collapsed"
    )
    
    if st.button("🚀 Analyze Password Security", use_container_width=True):
        if not password:
            st.warning("⚠️ Please enter a password to analyze!")
        else:
            with st.spinner("🔍 Analyzing password strength..."):
                try:
                    strength = predict_strength(password)
                    features = extract_features(password)
                    
                    # Display results
                    st.markdown("### 📊 Security Analysis Result")
                    
                    # Progress bar
                    progress_data = {
                        "very_weak": {"width": 20, "color": "#ff4757"},
                        "weak": {"width": 50, "color": "#ffa502"}, 
                        "strong": {"width": 95, "color": "#2ed573"}
                    }
                    
                    progress = progress_data.get(strength, progress_data["weak"])
                    
                    st.markdown(f"""
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {progress['width']}%; background: {progress['color']};"></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Result card
                    if strength == "very_weak":
                        st.markdown("""
                        <div class="strength-card very-weak-card">
                            <div class="security-icon">🚨</div>
                            <h1>CRITICAL RISK</h1>
                            <p style='font-size: 1.4rem;'>Very Weak Password</p>
                            <p>Immediate security threat detected!</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.error("**🚨 Immediate Action Required:** This password can be cracked instantly!")
                        
                    elif strength == "weak":
                        st.markdown("""
                        <div class="strength-card weak-card">
                            <div class="security-icon">⚠️</div>
                            <h1>MODERATE RISK</h1>
                            <p style='font-size: 1.4rem;'>Weak Password</p>
                            <p>Needs significant improvement</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.warning("**⚠️ Security Improvement Needed:** This password is vulnerable to attacks!")
                        
                    else:  # strong
                        st.markdown("""
                        <div class="strength-card strong-card">
                            <div class="security-icon">🎉</div>
                            <h1>EXCELLENT SECURITY</h1>
                            <p style='font-size: 1.4rem;'>Strong Password</p>
                            <p>Robust protection achieved</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                        st.success("### ✅ Perfect! Your password is highly secure!")
                    
                    # Features breakdown
                    st.markdown("### 🧩 Password Composition")
                    cols = st.columns(4)
                    metrics = [
                        {"icon": "📏", "value": features['length'], "label": "Length"},
                        {"icon": "🔠", "value": features['upper'], "label": "Uppercase"},
                        {"icon": "🔢", "value": features['digits'], "label": "Digits"}, 
                        {"icon": "⭐", "value": features['special'], "label": "Special"}
                    ]
                    
                    for i, metric in enumerate(metrics):
                        with cols[i]:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h2>{metric['icon']}</h2>
                                <h3>{metric['value']}</h3>
                                <p>{metric['label']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                except Exception as e:
                    st.error(f"❌ Analysis error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    🔒 <b>Privacy First:</b> All analysis happens locally. We never store your passwords.
</div>
""", unsafe_allow_html=True)
