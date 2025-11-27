import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import io

# Page configuration
st.set_page_config(
    page_title="Password Strength Analyzer",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .strength-very_weak { background-color: #ff4d4d; padding: 10px; border-radius: 5px; color: white; font-weight: bold; }
    .strength-weak { background-color: #ff9999; padding: 10px; border-radius: 5px; color: white; font-weight: bold; }
    .strength-medium { background-color: #ffcc00; padding: 10px; border-radius: 5px; color: black; font-weight: bold; }
    .strength-strong { background-color: #66cc66; padding: 10px; border-radius: 5px; color: white; font-weight: bold; }
    .feature-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin: 10px 0; }
    .metric-card { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<h1 class="main-header">🔒 Password Strength Analyzer</h1>', unsafe_allow_html=True)
st.markdown("""
This tool analyzes password strength using machine learning and rule-based checks. 
Upload your dataset or test individual passwords to see their strength classification.
""")

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
    
    # Common weak pattern anywhere
    features['common_pattern'] = int(bool(re.search(r'123|password|qwerty|abc', password.lower())))
    
    return features

# Prediction function
def predict_strength(password, model, scaler):
    if not password:
        return "very_weak"
    
    f = extract_features(password)
    pw_lower = password.lower()
    
    # RULE 1: Very short passwords → very_weak
    if f['length'] < 6:
        return "very_weak"
    
    # RULE 2: Exact common weak passwords → very_weak
    common_weak = ['password', '12345', 'qwerty', 'abc123']
    if pw_lower in common_weak:
        return "very_weak"
    
    # Scale features for ML
    df_f = pd.DataFrame([f])
    scaled = scaler.transform(df_f)
    pred = model.predict(scaled)[0]
    
    # Convert ML label: if ML predicts 'medium' → 'weak'
    if pred == "weak":
        pred = "weak"
    
    # RULE 3: Strong override for complex passwords
    if (
        f['length'] >= 12 and
        f['digits'] >= 2 and
        f['special'] >= 1 and
        f['upper'] >= 1 and
        f['lower'] >= 1
    ):
        return "strong"
    
    return pred

# Sidebar for navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox("Choose Mode", 
    ["Single Password Check", "Batch Analysis", "Dataset Insights", "About"])

# Load model and scaler (you'll need to upload these files)
@st.cache_resource
def load_model():
    try:
        model = joblib.load("password_model_vw.pkl")
        scaler = joblib.load("password_scaler_vw.pkl")
        return model, scaler
    except:
        st.warning("Model files not found. Please train the model first.")
        return None, None

model, scaler = load_model()

if app_mode == "Single Password Check":
    st.header("🔍 Single Password Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        password = st.text_input("Enter password to analyze:", type="password", 
                               placeholder="Type your password here...")
        
        if password:
            with st.spinner("Analyzing password..."):
                strength = predict_strength(password, model, scaler)
                features = extract_features(password)
                
                # Display strength with colored box
                strength_labels = {
                    "very_weak": "🔴 Very Weak",
                    "weak": "🟠 Weak", 
                    "medium": "🟡 Medium",
                    "strong": "🟢 Strong"
                }
                
                st.markdown(f'<div class="strength-{strength}">{strength_labels[strength]}</div>', 
                          unsafe_allow_html=True)
                
                # Feature breakdown
                st.subheader("📊 Password Features")
                feat_col1, feat_col2, feat_col3 = st.columns(3)
                
                with feat_col1:
                    st.metric("Length", features['length'])
                    st.metric("Uppercase", features['upper'])
                
                with feat_col2:
                    st.metric("Digits", features['digits'])
                    st.metric("Lowercase", features['lower'])
                
                with feat_col3:
                    st.metric("Special Chars", features['special'])
                    st.metric("Common Pattern", "Yes" if features['common_pattern'] else "No")
    
    with col2:
        st.subheader("💡 Tips for Strong Passwords")
        st.markdown("""
        - Use **12+ characters**
        - Mix **upper** and **lowercase**
        - Include **numbers** and **symbols**
        - Avoid common words/patterns
        - Don't reuse passwords
        """)

elif app_mode == "Batch Analysis":
    st.header("📁 Batch Password Analysis")
    
    uploaded_file = st.file_uploader("Upload CSV/Excel file with passwords", 
                                   type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"Successfully loaded {len(df)} records")
            
            # Assume password column is named 'password'
            password_col = st.selectbox("Select password column", df.columns)
            
            if st.button("Analyze All Passwords"):
                with st.spinner("Analyzing passwords..."):
                    results = []
                    for pw in df[password_col]:
                        strength = predict_strength(str(pw), model, scaler)
                        results.append(strength)
                    
                    df_results = df.copy()
                    df_results['predicted_strength'] = results
                    
                    # Display results
                    st.subheader("Analysis Results")
                    st.dataframe(df_results)
                    
                    # Download results
                    csv = df_results.to_csv(index=False)
                    st.download_button(
                        label="Download Results as CSV",
                        data=csv,
                        file_name="password_analysis_results.csv",
                        mime="text/csv"
                    )
                    
        except Exception as e:
            st.error(f"Error processing file: {e}")

elif app_mode == "Dataset Insights":
    st.header("📈 Dataset Insights")
    
    uploaded_insights = st.file_uploader("Upload your balanced rockyou Excel file for insights", 
                                       type=['xlsx'])
    
    if uploaded_insights is not None:
        try:
            df = pd.read_excel(uploaded_insights)
            st.success(f"Dataset loaded: {len(df)} passwords")
            
            # Extract features
            with st.spinner("Extracting features..."):
                X = [extract_features(pw) for pw in df['password']]
                df_features = pd.DataFrame(X)
                df_features['label'] = df['label']
            
            # Display insights
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Class Distribution")
                fig, ax = plt.subplots()
                df['label'].value_counts().plot(kind='bar', ax=ax, color=['red', 'orange', 'green'])
                ax.set_title("Password Strength Distribution")
                ax.set_ylabel("Count")
                st.pyplot(fig)
            
            with col2:
                st.subheader("Common Patterns")
                pattern_counts = df_features.groupby('common_pattern')['common_pattern'].count()
                pattern_counts.index = ["No Common Pattern", "Has Common Pattern"]
                
                fig, ax = plt.subplots()
                pattern_percent = (pattern_counts / pattern_counts.sum()) * 100
                bars = ax.bar(pattern_percent.index, pattern_percent.values, 
                            color=['green', 'red'], alpha=0.8)
                ax.set_title("Common Patterns in Passwords")
                ax.set_ylabel("Percentage (%)")
                
                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2.0, height + 1, 
                           f'{height:.1f}%', ha='center', fontsize=11)
                
                st.pyplot(fig)
            
            # Length distribution
            st.subheader("Password Length by Strength")
            fig, ax = plt.subplots(figsize=(10, 6))
            for label, color in zip(["Very Weak", "Weak", "Strong"], ['red', 'orange', 'green']):
                subset = df_features[df_features['label'] == label]
                ax.hist(subset['length'], bins=10, alpha=0.6, label=label, color=color)
            
            ax.set_title("Password Length Distribution by Strength")
            ax.set_xlabel("Password Length")
            ax.set_ylabel("Number of Passwords")
            ax.legend()
            st.pyplot(fig)
            
        except Exception as e:
            st.error(f"Error analyzing dataset: {e}")

else:  # About page
    st.header("ℹ️ About This Tool")
    
    st.markdown("""
    ## Password Strength Analyzer
    
    This application uses machine learning and rule-based analysis to evaluate password strength.
    
    ### Features:
    - **Single Password Analysis**: Check individual password strength with detailed feature breakdown
    - **Batch Analysis**: Upload files to analyze multiple passwords at once
    - **Dataset Insights**: Visualize password patterns and distributions
    
    ### Methodology:
    1. **Feature Extraction**: Length, character types, ratios, common patterns
    2. **Machine Learning**: Logistic Regression model trained on labeled password data
    3. **Rule-based Checks**: Additional security rules for common weak patterns
    
    ### Strength Levels:
    - 🔴 **Very Weak**: Too short or common passwords
    - 🟠 **Weak**: Basic passwords with minimal complexity
    - 🟡 **Medium**: Moderate complexity but room for improvement
    - 🟢 **Strong**: Complex, secure passwords
    
    ### Technical Stack:
    - Python, Scikit-learn, Pandas
    - Streamlit for web interface
    - Matplotlib/Seaborn for visualization
    """)

# Footer
st.markdown("---")
st.markdown("🔒 *Built with Streamlit - Password Security Tool*")
