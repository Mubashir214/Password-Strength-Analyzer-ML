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

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        text-align: center;
        font-size: 1.2rem;
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
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        text-align: center;
        margin: 2rem 0;
        border: none;
        transition: all 0.3s ease;
    }
    .weak-card {
        background: linear-gradient(135deg, #ff6b6b, #ee5a52);
        color: white;
    }
    .medium-card {
        background: linear-gradient(135deg, #ffd93d, #ffcd38);
        color: #2c3e50;
    }
    .strong-card {
        background: linear-gradient(135deg, #6bcf7f, #2ecc71);
        color: white;
    }
    .check-button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 15px 40px;
        font-size: 1.2rem;
        border-radius: 25px;
        cursor: pointer;
        width: 100%;
        margin: 1rem 0;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .check-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    .feature-item {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .tips-section {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        border-left: 5px solid #667eea;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 0.5rem;
    }
    .security-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    .progress-bar {
        height: 8px;
        border-radius: 10px;
        margin: 1rem 0;
        background: #e0e0e0;
    }
    .progress-fill {
        height: 100%;
        border-radius: 10px;
        transition: all 0.5s ease;
    }
</style>
""", unsafe_allow_html=True)

# Streamlit interface
st.markdown('<div class="main-header">🔒 Password Strength Analyzer</div>', unsafe_allow_html=True)
st.markdown("""
<div class="sub-header">
    Secure your digital life with stronger passwords • Real-time strength analysis
</div>
""", unsafe_allow_html=True)

# Main content area
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Password input section
    st.markdown("### 🔑 Enter Your Password")
    password_input = st.text_input(
        "", 
        type="password", 
        placeholder="Type your password here...",
        label_visibility="collapsed",
        help="We don't store or save your password anywhere - analysis happens locally"
    )
    
    # Analyze button
    if st.button("🚀 Analyze Password Strength", use_container_width=True):
        if not password_input.strip():
            st.warning("⚠️ Please enter a password to analyze!")
        else:
            with st.spinner("🔍 Analyzing your password security..."):
                # Simulate loading for better UX
                import time
                time.sleep(0.5)
                
                strength = predict_strength(password_input)
                features = extract_features(password_input)
                
                # Strength visualization
                st.markdown("### 📊 Analysis Result")
                
                # Progress bar based on strength
                strength_levels = {"Weak": 33, "Medium": 66, "Strong": 100}
                progress_color = {"Weak": "#ff6b6b", "Medium": "#ffd93d", "Strong": "#6bcf7f"}
                
                st.markdown(f"""
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {strength_levels[strength]}%; background: {progress_color[strength]};"></div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display result card
                if strength == "Weak":
                    st.markdown(f"""
                    <div class="strength-card weak-card">
                        <div class="security-icon">🔴</div>
                        <h2>WEAK PASSWORD</h2>
                        <p style='font-size: 1.3rem; font-weight: bold;'>High Security Risk</p>
                        <p>Your password needs immediate improvement to protect your accounts</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                elif strength == "Medium":
                    st.markdown(f"""
                    <div class="strength-card medium-card">
                        <div class="security-icon">🟡</div>
                        <h2>MEDIUM PASSWORD</h2>
                        <p style='font-size: 1.3rem; font-weight: bold;'>Moderate Security</p>
                        <p>Good foundation, but could be stronger with some improvements</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                else:
                    st.markdown(f"""
                    <div class="strength-card strong-card">
                        <div class="security-icon">🟢</div>
                        <h2>STRONG PASSWORD</h2>
                        <p style='font-size: 1.3rem; font-weight: bold;'>Excellent Security</p>
                        <p>Your password provides strong protection against attacks</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Password features breakdown
                st.markdown("### 📈 Password Composition")
                
                cols = st.columns(4)
                with cols[0]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>📏</h3>
                        <h4>{features['length']}</h4>
                        <p>Length</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[1]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>🔠</h3>
                        <h4>{features['upper']}</h4>
                        <p>Uppercase</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[2]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>🔢</h3>
                        <h4>{features['digits']}</h4>
                        <p>Digits</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[3]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>⭐</h3>
                        <h4>{features['special']}</h4>
                        <p>Special</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Security tips
                with st.expander("💡 **Security Recommendations**", expanded=True):
                    st.markdown("""
                    <div class="tips-section">
                        <h4>🔒 How to Create Strong Passwords:</h4>
                        <ul style="text-align: left;">
                            <li><b>Use at least 12 characters</b> - Longer is better</li>
                            <li><b>Mix character types</b> - Upper/lower case, numbers, symbols</li>
                            <li><b>Avoid common patterns</b> - Like "123", "password", "qwerty"</li>
                            <li><b>Don't use personal info</b> - Names, birthdays, etc.</li>
                            <li><b>Use unique passwords</b> - Different for each account</li>
                            <li><b>Consider passphrases</b> - "BlueDragon$FliesHigh42!"</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888; padding: 2rem;'>"
    "🔒 <b>Privacy First:</b> Your password is analyzed locally and never stored or transmitted. "
    "We believe in complete privacy and security."
    "</div>", 
    unsafe_allow_html=True
)

# Sidebar with additional info
with st.sidebar:
    st.markdown("## ℹ️ About")
    st.markdown("""
    This tool uses machine learning to analyze password strength based on:
    
    - **Length** and character diversity
    - **Pattern recognition**
    - **Common password databases**
    - **Security best practices**
    
    ### 🛡️ Why Password Strength Matters
    Strong passwords protect against:
    - Brute force attacks
    - Dictionary attacks
    - Credential stuffing
    - Data breaches
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Strength Criteria")
    st.markdown("""
    **🔴 Weak:** Short, common, or simple patterns
    **🟡 Medium:** Moderate length, some complexity  
    **🟢 Strong:** Long, diverse characters, no patterns
    """)
