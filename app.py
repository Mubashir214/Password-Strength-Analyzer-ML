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
    .strength-unknown { background-color: #cccccc; padding: 10px; border-radius: 5px; color: black; font-weight: bold; }
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

# Enhanced prediction function with better error handling
def predict_strength(password, model, scaler):
    if not password:
        return "very_weak"
    
    try:
        f = extract_features(password)
        pw_lower = password.lower()
        
        # RULE 1: Very short passwords → very_weak
        if f['length'] < 6:
            return "very_weak"
        
        # RULE 2: Exact common weak passwords → very_weak
        common_weak = ['password', '12345', 'qwerty', 'abc123', '123456', '12345678', '123456789']
        if pw_lower in common_weak:
            return "very_weak"
        
        # Check if model and scaler are available
        if model is None or scaler is None:
            # Fallback to rule-based prediction
            if (f['length'] >= 12 and f['digits'] >= 2 and f['special'] >= 1 and 
                f['upper'] >= 1 and f['lower'] >= 1):
                return "strong"
            elif (f['length'] >= 8 and f['digits'] >= 1 and 
                  (f['upper'] >= 1 or f['special'] >= 1)):
                return "medium"
            else:
                return "weak"
        
        # Scale features for ML
        df_f = pd.DataFrame([f])
        scaled = scaler.transform(df_f)
        pred = model.predict(scaled)[0]
        
        # Ensure the prediction is a string and handle case variations
        pred = str(pred).lower()
        
        # Map predictions to consistent labels
        if pred in ['very_weak', 'very weak']:
            return "very_weak"
        elif pred in ['weak', 'weak']:
            return "weak"
        elif pred in ['medium', 'moderate']:
            return "medium"
        elif pred in ['strong', 'good']:
            return "strong"
        
        # RULE 3: Strong override for complex passwords
        if (f['length'] >= 12 and f['digits'] >= 2 and 
            f['special'] >= 1 and f['upper'] >= 1 and f['lower'] >= 1):
            return "strong"
        
        return pred if pred in ["very_weak", "weak", "medium", "strong"] else "weak"
        
    except Exception as e:
        st.error(f"Error in prediction: {e}")
        return "unknown"

# Load model and scaler with better error handling
@st.cache_resource
def load_model():
    try:
        # Try to load the model files
        model = joblib.load("password_model_vw.pkl")
        scaler = joblib.load("password_scaler_vw.pkl")
        st.sidebar.success("✅ Model loaded successfully!")
        return model, scaler
    except FileNotFoundError:
        st.sidebar.warning("⚠️ Model files not found. Using rule-based analysis only.")
        return None, None
    except Exception as e:
        st.sidebar.error(f"❌ Error loading model: {e}")
        return None, None

# Initialize model and scaler
model, scaler = load_model()

# Strength labels with comprehensive coverage
strength_labels = {
    "very_weak": "🔴 Very Weak",
    "weak": "🟠 Weak", 
    "medium": "🟡 Medium",
    "strong": "🟢 Strong",
    "unknown": "⚪ Unknown"
}

# Sidebar for navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox("Choose Mode", 
    ["Single Password Check", "Batch Analysis", "Dataset Insights", "About"])

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
                
                # Safe display of strength with fallback
                display_strength = strength_labels.get(strength, "⚪ Unknown")
                css_class = f"strength-{strength}" if strength in strength_labels else "strength-unknown"
                
                st.markdown(f'<div class="{css_class}">{display_strength}</div>', 
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
                
                # Progress bars for ratios
                st.subheader("📈 Character Ratios")
                col_ratio1, col_ratio2 = st.columns(2)
                
                with col_ratio1:
                    st.progress(features['digit_ratio'], text=f"Digit Ratio: {features['digit_ratio']:.1%}")
                    st.progress(features['special_ratio'], text=f"Special Char Ratio: {features['special_ratio']:.1%}")
                
                with col_ratio2:
                    st.progress(features['upper_ratio'], text=f"Uppercase Ratio: {features['upper_ratio']:.1%}")
                    st.progress(features['lower_ratio'], text=f"Lowercase Ratio: {features['lower_ratio']:.1%}")
    
    with col2:
        st.subheader("💡 Tips for Strong Passwords")
        st.markdown("""
        - Use **12+ characters**
        - Mix **upper** and **lowercase**
        - Include **numbers** and **symbols**
        - Avoid common words/patterns
        - Don't reuse passwords
        """)
        
        # Quick test examples
        st.subheader("🚀 Test Examples")
        test_passwords = ["password", "12345", "Hello123", "MyPass123!", "Secure@Pass2024!"]
        for test_pw in test_passwords:
            if st.button(f"Test: {test_pw}", key=test_pw):
                st.session_state.test_password = test_pw

elif app_mode == "Batch Analysis":
    st.header("📁 Batch Password Analysis")
    
    uploaded_file = st.file_uploader("Upload CSV/Excel file with passwords", 
                                   type=['csv', 'xlsx', 'txt'])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            else:  # txt file
                passwords = uploaded_file.getvalue().decode().splitlines()
                df = pd.DataFrame(passwords, columns=['password'])
            
            st.success(f"Successfully loaded {len(df)} records")
            
            # Find password column
            password_cols = [col for col in df.columns if 'pass' in col.lower() or col.lower() in ['password', 'pwd', 'pass']]
            if password_cols:
                password_col = st.selectbox("Select password column", password_cols)
            else:
                password_col = st.selectbox("Select password column", df.columns)
            
            if st.button("Analyze All Passwords"):
                with st.spinner("Analyzing passwords..."):
                    results = []
                    features_list = []
                    
                    for pw in df[password_col]:
                        pw_str = str(pw)
                        strength = predict_strength(pw_str, model, scaler)
                        features = extract_features(pw_str)
                        
                        results.append(strength)
                        features_list.append(features)
                    
                    df_results = df.copy()
                    df_results['predicted_strength'] = results
                    df_features = pd.DataFrame(features_list)
                    df_results = pd.concat([df_results, df_features], axis=1)
                    
                    # Display results
                    st.subheader("Analysis Results")
                    st.dataframe(df_results.head(50))  # Show first 50 results
                    
                    # Summary statistics
                    st.subheader("📊 Summary Statistics")
                    strength_counts = df_results['predicted_strength'].value_counts()
                    col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
                    
                    for strength, count in strength_counts.items():
                        display_name = strength_labels.get(strength, strength.title())
                        if strength == "very_weak":
                            col_sum1.metric("Very Weak", count)
                        elif strength == "weak":
                            col_sum2.metric("Weak", count)
                        elif strength == "medium":
                            col_sum3.metric("Medium", count)
                        elif strength == "strong":
                            col_sum4.metric("Strong", count)
                    
                    # Download results
                    csv = df_results.to_csv(index=False)
                    st.download_button(
                        label="Download Results as CSV",
                        data=csv,
                        file_name="password_analysis_results.csv",
                        mime="text/csv"
                    )
                    
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

elif app_mode == "Dataset Insights":
    st.header("📈 Dataset Insights")
    
    uploaded_insights = st.file_uploader("Upload your balanced rockyou Excel file for insights", 
                                       type=['xlsx', 'csv'])
    
    if uploaded_insights is not None:
        try:
            if uploaded_insights.name.endswith('.csv'):
                df = pd.read_csv(uploaded_insights)
            else:
                df = pd.read_excel(uploaded_insights)
                
            st.success(f"Dataset loaded: {len(df)} passwords")
            
            # Check if label column exists
            if 'label' not in df.columns:
                st.warning("No 'label' column found. Please upload a file with password strength labels.")
            else:
                # Extract features
                with st.spinner("Extracting features..."):
                    X = [extract_features(str(pw)) for pw in df['password']]
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
                    plt.xticks(rotation=45)
                    st.pyplot(fig)
                
                with col2:
                    st.subheader("Common Patterns")
                    pattern_counts = df_features.groupby('common_pattern')['common_pattern'].count()
                    if len(pattern_counts) > 0:
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
                
                # Normalize label names
                label_mapping = {
                    'very_weak': 'Very Weak', 'very weak': 'Very Weak',
                    'weak': 'Weak', 
                    'medium': 'Medium', 'moderate': 'Medium',
                    'strong': 'Strong', 'good': 'Strong'
                }
                
                df_features['label_normalized'] = df_features['label'].map(
                    lambda x: label_mapping.get(str(x).lower(), str(x).title())
                )
                
                colors = {'Very Weak': 'red', 'Weak': 'orange', 'Medium': 'yellow', 'Strong': 'green'}
                
                for label in df_features['label_normalized'].unique():
                    subset = df_features[df_features['label_normalized'] == label]
                    color = colors.get(label, 'blue')
                    ax.hist(subset['length'], bins=15, alpha=0.6, label=label, color=color)
                
                ax.set_title("Password Length Distribution by Strength")
                ax.set_xlabel("Password Length")
                ax.set_ylabel("Number of Passwords")
                ax.legend()
                st.pyplot(fig)
            
        except Exception as e:
            st.error(f"Error analyzing dataset: {str(e)}")

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

# Handle test password from quick examples
if 'test_password' in st.session_state:
    st.experimental_set_query_params(test=st.session_state.test_password)
    del st.session_state.test_password
