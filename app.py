import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.patches import FancyBboxPatch
import json

# --- Page config ---
st.set_page_config(layout="wide")

# --- Load data ---
df = pd.read_csv('./data/full_user_profiles_with_persona.csv')

st.title("Kaggle Persona Analyzer 🔍")

# --- Intro section ---
with st.expander("📘 What is This App?"):
    st.markdown("""
    This tool analyzes Kaggle users by examining their public notebook activity.

    - 🧬 Assigns an AI-generated **persona** (e.g., 🤖 ML Practitioner, 📊 EDA-Focused)
    - 📈 Visualizes notebook engagement and topic preferences
    - 🧠 Suggests areas for exploration
    - 📥 Downloadable **Persona Card** (PNG) and user data (JSON)
    """)

# --- Select User ---
search_term = st.text_input("🔎 Search User ID")
filtered = df[df['AuthorUserId'].astype(str).str.contains(search_term, case=False)] if search_term else df.head(10)

user_id = st.selectbox("Select User ID", filtered['AuthorUserId'].unique())
user = filtered[filtered['AuthorUserId'] == user_id].iloc[0]

medals = {
    "🥇 Gold": user["GoldMedals"],
    "🥈 Silver": user["SilverMedals"],
    "🥉 Bronze": user["BronzeMedals"]
}


# --- Functions ---
def get_persona_badge(persona):
    color_map = {
        "🧠 Generalist": "#888888",
        "🗣️ NLP Specialist": "#FFB347",
        "📊 EDA-Focused": "#4CAF50",
        "👁️ CV Enthusiast": "#2196F3",
        "🤖 ML Practitioner": "#9C27B0",
        "🧬 DL Researcher": "#E91E63",
        "📈 Time-Series Analyst": "#FF5722"
    }
    for key, color in color_map.items():
        if persona.startswith(key[:2]):
            return f"<span style='background-color:{color}; color:white; padding:4px 8px; border-radius:8px;'>{persona}</span>"
    return f"<span style='background-color:#888; color:white; padding:4px 8px; border-radius:8px;'>{persona}</span>"


def create_persona_card(user):
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.set_facecolor('#0D0D0D')
    fig.patch.set_facecolor('#0D0D0D')
    ax.axis('off')

    # Neon border
    rect = FancyBboxPatch((0, 0), 1, 1,
                          boxstyle="round,pad=0.02",
                          linewidth=2,
                          edgecolor='#00FFFF',
                          facecolor='none',
                          transform=ax.transAxes,
                          zorder=10)
    ax.add_patch(rect)

    # Emoji-free version to avoid glyph warnings
    persona_clean = ''.join([c for c in user['Persona'] if c.isalnum() or c.isspace()])

    text = f"""
KAGGLE PERSONA CARD

USER ID: {user['AuthorUserId']}
PERSONA: {persona_clean}
TOP NOTEBOOK: {user['MostVotedNotebook']} ({user['MostVotes']} votes)
ACTIVE MONTH: {user['MostActiveMonth']}
AVG LENGTH: {user['AvgNotebookLength']:.2f} cells
NOTEBOOKS: {user['TotalNotebooks']}
VIEWS: {user['TotalViews']}
VOTES: {user['TotalVotes']}
"""

    ax.text(0.05, 0.95, text, fontsize=12, va='top', ha='left', color='white', family='monospace')
    plt.tight_layout(pad=2)

    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    buf.seek(0)
    return buf


# --- Persona Display ---
st.markdown(f"### 🎭 Persona: {get_persona_badge(user['Persona'])}", unsafe_allow_html=True)

persona_explainer = {
    "🧠 Generalist": "Contributes across multiple domains with balanced focus.",
    "🗣️ NLP Specialist": "Strong focus on text and language-related projects.",
    "📊 EDA-Focused": "Excels in data storytelling and visual exploration.",
    "👁️ CV Enthusiast": "Loves building computer vision models and image tasks.",
    "🤖 ML Practitioner": "Works across classic ML problems and solutions.",
    "🧬 DL Researcher": "Deep learning-focused notebooks and innovations.",
    "📈 Time-Series Analyst": "Specialist in trend-based time-driven datasets."
}

for key in persona_explainer:
    if user["Persona"].startswith(key[:2]):
        st.markdown(f"🧾 _{persona_explainer[key]}_")
        break

st.write(f"**Most Voted Notebook:** {user['MostVotedNotebook']} ({user['MostVotes']} votes)")
st.write(f"**Most Active Month:** {user['MostActiveMonth']}")
st.write(f"**Average Notebook Length:** {user['AvgNotebookLength']:.2f}")

if 'RecommendedTopics' in user and pd.notna(user['RecommendedTopics']):
    st.markdown("### 🔍 Suggested Topics to Explore Next")
    st.info(user['RecommendedTopics'])

# --- Stats Metrics ---
st.markdown("### 📊 Activity Overview")
col1, col2, col3 = st.columns(3)
col1.metric("📘 Total Notebooks", int(user['TotalNotebooks']))
col2.metric("👀 Total Views", int(user['TotalViews']))
col3.metric("👍 Total Votes", int(user['TotalVotes']))

# --- Radar Chart ---
topic_cols = ['cv', 'dl', 'eda', 'ml', 'nlp', 'other', 'time_series']
topic_values = [user[col] for col in topic_cols]
total = sum(topic_values)
percentages = [round((v / total) * 100, 2) if total > 0 else 0 for v in topic_values]

fig = go.Figure()
fig.add_trace(go.Scatterpolar(r=percentages, theta=topic_cols, fill='toself', name='Topic Strength'))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False,
                  title=dict(text="📊 Topic Strength Radar Chart", x=0.5))

# --- Medal Bar Chart ---
medal_fig = px.bar(x=list(medals.keys()), y=list(medals.values()),
                   labels={'x': 'Medal Type', 'y': 'Count'},
                   title="🏅 Medal Distribution")

col1, col2 = st.columns(2)
col1.plotly_chart(fig, use_container_width=True)
col2.plotly_chart(medal_fig, use_container_width=True)

# --- Timeline Chart ---
try:
    timeline_df = pd.read_csv('./data/user_timeline.csv')
    user_timeline = timeline_df[timeline_df['AuthorUserId'] == user_id]
    if not user_timeline.empty:
        timeline_fig = px.bar(user_timeline, x='Month', y='Count', title="🗓️ Notebook Activity Over Time")
        st.plotly_chart(timeline_fig, use_container_width=True)
    else:
        st.info("No timeline data available for this user.")
except FileNotFoundError:
    st.warning("Timeline data not found. Please generate 'user_timeline.csv'.")

# --- Futuristic UI Card Display (HTML/CSS) ---
persona = user['Persona']
notebook = user['MostVotedNotebook']
votes = user['MostVotes']
month = user['MostActiveMonth']
avg_len = f"{user['AvgNotebookLength']:.2f}"

st.markdown(f"""
    <style>
        .card {{
            background: rgba(30, 30, 30, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 15px;
            padding: 25px;
            color: #fff;
            font-family: 'Segoe UI', sans-serif;
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.4);
            backdrop-filter: blur(10px);
            margin-top: 40px;
        }}
        .card h2 {{
            font-size: 26px;
            background: linear-gradient(to right, #00fff0, #00d2ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        .card p {{
            font-size: 17px;
            margin: 6px 0;
        }}
        .badge {{
            display: inline-block;
            background: linear-gradient(to right, #ff00cc, #3333ff);
            padding: 6px 12px;
            border-radius: 12px;
            font-weight: bold;
            color: white;
            box-shadow: 0 0 10px rgba(255, 0, 255, 0.6);
            margin-bottom: 12px;
        }}
    </style>

    <div class="card">
        <h2>🧬 Kaggle Persona Card</h2>
        <div class="badge">{persona}</div>
        <p><b>📘 Most Voted Notebook:</b> {notebook} ({votes} votes)</p>
        <p><b>📅 Most Active Month:</b> {month}</p>
        <p><b>✍️ Avg. Notebook Length:</b> {avg_len}</p>
    </div>
""", unsafe_allow_html=True)

# --- Download Buttons ---
if st.button("📥 Download PNG Persona Card"):
    card = create_persona_card(user)
    st.download_button(
        label="Download as PNG",
        data=card,
        file_name=f"persona_card_{user['AuthorUserId']}.png",
        mime="image/png"
    )

if st.button("📤 Export Full User Stats as JSON"):
    export_data = user.to_dict()
    st.download_button(
        label="Download as JSON",
        data=json.dumps(export_data, indent=2),
        file_name=f"{user['AuthorUserId']}_persona_data.json",
        mime="application/json"
    )

# --- Footer ---
st.markdown("---")
st.markdown("<center>🚀 Built by Thabasvini K & Team for the Meta Kaggle Hackathon 2025</center>", unsafe_allow_html=True)

