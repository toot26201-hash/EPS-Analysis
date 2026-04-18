import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns

# إعدادات الصفحة
st.set_page_config(page_title="EPS Elite Analytics", layout="wide")

@st.cache_data
def load_data():
    # تحميل البيانات وتنظيفها
    df = pd.read_csv('EPS_Match_Data_Clean.csv')
    df.columns = df.columns.str.strip()
    df['Players'] = df['Players'].astype(str).fillna('Unknown')
    return df

try:
    df = load_data()

    # --- 1. تنظيف قائمة اللاعبين (حل مشكلة الأسماء المزدوجة) ---
    all_names_raw = df['Players'].str.split('|').explode().str.strip()
    clean_player_list = sorted([p for p in all_names_raw.unique() if p and p not in ['nan', 'Unknown', 'None']])

    # --- 2. القائمة الجانبية (Sidebar) ---
    st.sidebar.header("🎯 Dashboard Control")
    selected_player = st.sidebar.selectbox("Select Player for Analysis", clean_player_list)
    
    # فلترة البيانات للاعب المختار
    player_df = df[df['Players'].str.contains(selected_player, na=False)].copy()

    # --- 3. تصميم الصفوف في الصفحة ---
    st.title(f"📊 Performance Report: {selected_player}")
    
    tab1, tab2 = st.tabs(["🔥 Player Heatmap", "🚀 Final Third Entries"])

    # --- Tab 1: الخريطة الحرارية لكل لاعب ---
    with tab1:
        st.subheader(f"Movement Intensity - {selected_player}")
        pitch_h = Pitch(pitch_color='grass', line_color='white', stripe=True)
        fig_h, ax_h = pitch_h.draw(figsize=(10, 7))
        
        if not player_df.empty and len(player_df) > 1:
            sns.kdeplot(
                x=player_df['X_Start'] * 120, y=player_df['Y_Start'] * 80,
                fill=True, thresh=0.05, levels=100, cmap='hot', alpha=0.6, ax=ax_h
            )
        st.pyplot(fig_h)
        
        # إحصائيات سريعة تحت الخريطة
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total Actions", len(player_df))
        col_m2.metric("Passes", len(player_df[player_df['Event Name'].str.contains('Pass', na=False)]))
        col_m3.metric("Shots", len(player_df[player_df['Event Name'].str.contains('Shot', na=False)]))

    # --- Tab 2: تحليل دخول الثلث الأخير للاعب ---
    with tab2:
        st.subheader(f"How {selected_player} enters the Final Third")
        
        # فلترة تمريرات اللاعب للثلث الأخير
        p_f3 = player_df[
            (player_df['Event Name'].str.contains('Pass', na=False)) & 
            (player_df['X_End'] >= 0.66) & (player_df['X_Start'] < 0.66)
        ].copy()

        def classify_entry(row):
            if row['Y_Start'] < 0.25 or row['Y_Start'] > 0.75: return "Cross 🟡"
            elif (row['X_End'] - row['X_Start']) > 0.20: return "Long Pass 🔵"
            else: return "Short Pass 🔴"

        pitch_e = Pitch(pitch_color='grass', line_color='white', stripe=True)
        fig_e, ax_e = pitch_e.draw(figsize=(10, 7))

        if not p_f3.empty:
            p_f3['Type'] = p_f3.apply(classify_entry, axis=1)
            colors = {"Cross 🟡": "yellow", "Long Pass 🔵": "#00bfff", "Short Pass 🔴": "#ff4b4b"}
            
            for t, c in colors.items():
                subset = p_f3[p_f3['Type'] == t]
                pitch_e.arrows(subset.X_Start*120, subset.Y_Start*80, 
                             subset.X_End*120, subset.Y_End*80, 
                             color=c, ax=ax_e, width=3, headwidth=8, label=t)
            
            st.pyplot(fig_e)
            st.write("🟡 Crosses | 🔵 Vertical Long | 🔴 Short/Internal")
        else:
            st.warning("No Final Third entries found for this player in this match.")

except Exception as e:
    st.error(f"Something went wrong: {e}")
