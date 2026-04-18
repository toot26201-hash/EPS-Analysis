import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch, VerticalPitch
import seaborn as sns

st.set_page_config(page_title="EPS Pro Dashboard", layout="wide")
st.title("📊 EPS Performance Analysis - Pro Level")

@st.cache_data
def load_data():
    df = pd.read_csv('EPS_Match_Data_Clean.csv')
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# --- Sidebar: قائمة اختيار اللاعب ---
st.sidebar.header("Filters")
all_players = ["All Team"] + sorted(df['Players'].unique().tolist())
selected_player = st.sidebar.selectbox("Select Player", all_players)

# فلترة البيانات بناءً على الاختيار
if selected_player == "All Team":
    filtered_df = df
else:
    filtered_df = df[df['Players'] == selected_player]

# --- توزيع الصفحة ---
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"📍 Action Heatmap: {selected_player}")
    pitch = Pitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#22312b', line_color='#efefef')
    fig, ax = pitch.draw(figsize=(8, 6))
    
    # رسم الخريطة الحرارية
    if not filtered_df.empty:
        kde = sns.kdeplot(
            x=filtered_df['X_Start'] * 120,
            y=filtered_df['Y_Start'] * 80,
            fill=True,
            thresh=0.05,
            levels=100,
            cmap='hot',
            alpha=0.5,
            ax=ax
        )
    st.pyplot(fig)

with col2:
    st.subheader(f"🎯 Shot Map: {selected_player}")
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#efefef')
    fig, ax = pitch.draw(figsize=(8, 6))
    
    shots = filtered_df[filtered_df['Event Name'].str.contains('Shot', na=False, case=False)]
    if not shots.empty:
        pitch.scatter(shots['X_Start']*120, shots['Y_Start']*80, ax=ax, c='#ef4444', s=150, edgecolors='white', label='Shots')
    st.pyplot(fig)

# --- جدول الإحصائيات أسفل الملعب ---
st.divider()
st.subheader(f"📈 Performance Stats: {selected_player}")
stats_col1, stats_col2, stats_col3 = st.columns(3)

with stats_col1:
    total_actions = len(filtered_df)
    st.metric("Total Actions", total_actions)

with stats_col2:
    passes_count = len(filtered_df[filtered_df['Event Name'].str.contains('Pass', na=False)])
    st.metric("Total Passes", passes_count)

with stats_col3:
    shots_count = len(filtered_df[filtered_df['Event Name'].str.contains('Shot', na=False)])
    st.metric("Total Shots", shots_count)
