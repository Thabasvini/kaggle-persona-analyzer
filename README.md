# Kaggle Persona Analyzer

This is a Streamlit-based application built for the **Meta Kaggle Hackathon 2025**. It analyzes Kaggle user behavior to generate unique AI personas using notebook activity data.

## Features

- 📊 Analyzes notebook-level data from Meta-Kaggle
- 🧬 Assigns personas like "EDA Specialist", "CV Enthusiast", etc.
- 📈 Visualizes user activity trends over time
- 🖼️ Generates elegant, downloadable persona cards
- Built with Python, Pandas, Matplotlib, and Streamlit

## Files

- `app.py` – Main Streamlit app
- `data/full_user_profiles_with_persona.csv` – Merged user-level data with persona
- `data/user_timeline.csv` – Notebook activity timeline
- `explore_users.ipynb` – (Optional) Notebook used for EDA and feature engineering

## 📦 Requirements

Install all dependencies:

```bash
pip install -r requirements.txt

Run the App

streamlit run app.py

```

Watch the youtube demo here: https://youtu.be/uY3kN7t9Ie4
