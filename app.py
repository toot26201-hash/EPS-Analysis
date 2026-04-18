import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns

st.set_page_config(page_title="EPS Tactical Lab", layout="wide")
st.title("⚽ Final Third & Penalty Box Analysis")

@st.cache_data
def load_data():
    df = pd.read_csv('EPS_Match_Data_Clean.csv')
    df.columns = df.columns.str.strip()
    df['Players'] = df['Players'].fillna('Unknown')
    return df

try:
    df = load_data()

    # --- 1. فلترة اختراقات الثلث الأخير ---
    f3_entries = df[(df['X_End'] >= 0.66) & (df['X_Start'] < 0.66)].copy()
    
    # --- 2. فلترة دخول منطقة الجزاء ---
    box_entries = df[
        (df['X_End'] >= 0.83) & (df['Y_End'] >= 0.22) & (df['Y_End'] <= 0.78) & (df['X_Start'] < 0.83)
    ].copy()

    # تصنيف طريقة دخول الصندوق
    def entry_method(row):
        if 'Pass' in str(row['Event Name']):
            if abs(row['Y_End'] - row['Y_Start']) > 0.3: return "Cross"
            else: return "Through Pass"
        return "Dribble/Carry"

    if not box_entries.empty:
        box_entries['Method'] = box_entries.apply(entry_method, axis=1)

    # --- العرض ---
    tab1, tab2 = st.tabs(["Final Third Entries", "Penalty Box Detail"])

    with tab1:
        st.subheader("🗺️ How we enter the Final Third")
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#efefef')
        fig, ax = pitch.draw(figsize=(10, 7))
        # رسم أسهم الدخول للثلث الأخير
        pitch.arrows(f3_entries.X_Start*120, f3_entries.Y_Start*80, 
                     f3_entries.X_End*120, f3_entries.Y_End*80, color='#adff2f', ax=ax, width=2)
        st.pyplot(fig)
        st.write(f"إجمالي عدد مرات دخول الثلث الأخير: {len(f3_entries)}")

    with tab2:
        st.subheader("🎯 Penalty Box Entry Methods")
        col_m1, col_m2 = st.columns([2, 1])
        
        with col_m1:
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#efefef')
            fig, ax = pitch.draw(figsize=(10, 7))
            # تلوين الدخول حسب الطريقة
            for _, row in box_entries.iterrows():
                color = "cyan" if row['Method'] == "Through Pass" else "yellow" if row['Method'] == "Cross" else "magenta"
                pitch.arrows(row.X_Start*120, row.Y_Start*80, row.X_End*120, row.Y_End*80, color=color, ax=ax, width=3)
            st.pyplot(fig)
            st.write("🔵 Through Pass | 🟡 Cross | 🔴 Dribble")

        with col_m2:
            if not box_entries.empty:
                st.write("**Entry Stats:**")
                st.bar_chart(box_entries['Method'].value_counts())
                st.write("**Top Players entering the box:**")
                st.write(box_entries['Players'].value_counts().head(5))

except Exception as e:
    st.error(f"Error: {e}")
