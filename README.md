1. Introduction

Weak passwords remain one of the biggest attack vectors in modern systems. Users often choose predictable passwords such as 123456, password, or short dictionary words.

This project builds a local, offline Password Strength Analyzer using Machine Learning (Logistic Regression) trained on a balanced password dataset inspired by RockYou.

2. Project Overview

The analyzer extracts features from a password such as:

Length

Uppercase / Lowercase letters

Digits

Special characters

Dictionary-like patterns

Common weak sequences (123, qwerty, password, abc)

Using these features, the ML model predicts:

very_weak

weak

strong

The system is 100% offline, lightweight, and streamlit-based.

3. Tools & Technologies

Python

Scikit-Learn (Logistic Regression Model)

Pandas

NumPy

Streamlit (GUI)

Matplotlib / Seaborn

Joblib

4. Features

✔ Offline and secure
✔ Machine-learning driven predictions
✔ Visual feedback
✔ Color-coded results
✔ Real-time Streamlit UI
✔ Dataset balanced: 100 very_weak / 100 weak / 100 strong
