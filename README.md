# Password Strength Analyzer Using Machine Learning

## Project Overview
This project is a **Password Strength Analyzer** that classifies passwords as **Weak, Medium, or Strong** using machine learning and feature extraction. Weak passwords are one of the biggest security risks, and this tool helps users understand and improve password security.

The system analyzes passwords **locally** (no data is uploaded online) using a **Logistic Regression model** trained on patterns from a balanced dataset inspired by `rockyou.txt`. The model evaluates features such as length, character diversity, digits, special characters, and common weak patterns.

---


---

## Features
- User enters password locally.
- ML-based prediction: **very Weak / weak / Strong**.
- Feature extraction:
  - Length
  - Uppercase letters
  - Lowercase letters
  - Digits
  - Special characters
  - Common weak patterns
- Clear color-coded feedback:
  - **very Weak** → Red  
  - **weak** → Orange  
  - **Strong** → Green
- Visualization of password patterns (optional).

---

## Tools & Technologies
- **Python 3.x**  
- **Streamlit** (Web Interface)  
- **Scikit-learn** (ML Model: Logistic Regression)  
- **Pandas & NumPy** (Data Processing)  
- **Matplotlib / Seaborn** (Visualization)  
- **Joblib** (Save/Load Model)  

---

## Folder Structure

