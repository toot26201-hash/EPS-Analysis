import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns

st.set_page_config(page_title="EPS Pro Dashboard", layout="wide")
st.title("📊 EPS Performance Analysis - Pro Level")

@st.cache_data
def load_data():
    df = pd.read_csv('EPS_Match_Data_Clean.csv')
    df.columns = df.columns.str.strip()
    # تحويل أي خانة فاضية في الأسامي لكلمة 'Unknown' عشان الكود ميفصلش
    df['Players'] = df['Players'].fillna('Unknown')
    return df

try:
    df = load_data()

    # --- Sidebar ---
    st.sidebar.header("Filters")
    # استخراج الأسامي الفريدة وتصفية أي بيانات غير نصية
    player_list = sorted([str(p) for p in df['Players'].unique()])
    all_players = ["All Team"] + player_list
    selected_player = st.sidebar.selectbox("Select Player", all_players)

    if selected_player == "All Team":
        filtered_df = df
    else:
        filtered_df = df[df['Players'] == selected_player]

    # --- العرض ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"📍 Action Heatmap: {selected_player}")
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#efefef')
        fig, ax = pitch.draw(figsize=(8, 6))
        
        if not filtered_df.empty and len(filtered_df) > 1:
            sns.kdeplot(
                x=filtered_df['X_Start'] * 120,
                y=filtered_df['Y_Start'] * 80,
                fill=True, thresh=0.05, levels=100, cmap='hot', alpha=0.5, ax=ax
            )
        st.pyplot(fig)

    with col2:
        st.subheader(f"🎯 Shot Map: {selected_player}")
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#efefef')
        fig, ax = pitch.draw(figsize=(8, 6))
        
        shots = filtered_df[filtered_df['Event Name'].str.contains('Shot', na=False, case=False)]
        if not shots.empty:
            pitch.scatter(shots['X_Start']*120, shots['Y_Start']*80, ax=ax, c='#ef4444', s=150, edgecolors='white')
        st.pyplot(fig)

    # --- الإحصائيات ---
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Actions", len(filtered_df))
    m2.metric("Passes", len(filtered_df[filtered_df['Event Name'].str.contains('Pass', na=False)]))
    m3.metric("Shots", len(shots))

except Exception as e:
    st.error(f"حدث خطأ فني: {e}")
