import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import numpy as np

st.set_page_config(page_title="EPS Attack Matrix", layout="wide")
st.title("⚽ Tactical Attack Zones & Box Entries")

@st.cache_data
def load_data():
    df = pd.read_csv('EPS_Match_Data_Clean.csv')
    df.columns = df.columns.str.strip()
    df['Players'] = df['Players'].fillna('Unknown')
    return df

try:
    df = load_data()

    # 1. تعريف "دخول منطقة الجزاء"
    box_entries = df[
        (df['X_End'] >= 0.83) & (df['Y_End'] >= 0.22) & (df['Y_End'] <= 0.78) & (df['X_Start'] < 0.83)
    ].copy()

    # 2. تصنيف ذكي (ممرات + أنواع)
    def classify_entry(row):
        is_pass = 'Pass' in str(row['Event Name'])
        is_wing = row['Y_Start'] < 0.33 or row['Y_Start'] > 0.66
        if is_pass and is_wing: return "Wing Cross 🟡"
        elif is_pass and not is_wing: return "Central Through Pass 🔵"
        else: return "Dribble / Carry 🔴"

    if not box_entries.empty:
        box_entries['Entry_Class'] = box_entries.apply(classify_entry, axis=1)

    # --- العرض المرئي الرئيسي (The Image You Requested) ---
    st.subheader("📊 Visual Attack Matrix (EPS Entries)")
    
    col1, col2 = st.columns([2, 1])

    with col1:
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#efefef', stripe=True)
        fig, ax = pitch.draw(figsize=(10, 7))
        
        # ألوان محددة
        colors = {"Wing Cross 🟡": "yellow", "Central Through Pass 🔵": "#00bfff", "Dribble / Carry 🔴": "#ff00ff"}
        
        # رسم ممرات الهجوم (شمال، وسط، يمين)
        # ممر شمال (Y: 0-26)
        pitch.lines(0, 0, 120, 26, lw=4, color='#555555', alpha=0.3, ax=ax)
        # ممر وسط (Y: 26-54)
        pitch.lines(0, 54, 120, 80, lw=4, color='#555555', alpha=0.3, ax=ax)
        
        if not box_entries.empty:
            for _, row in box_entries.iterrows():
                pitch.arrows(row.X_Start*120, row.Y_Start*80, row.X_End*120, row.Y_End*80, 
                             color=colors.get(row['Entry_Class'], "white"), ax=ax, width=3, headwidth=8, alpha=0.8)
        
        st.pyplot(fig)
        st.write("🟢 Green: Target Box Zone | 🟢 Lines: Wing/Center Zones")

    with col2:
        st.subheader("📈 Entry Breakdown (Visualized)")
        # رسم بياني بالألوان المناسبة للخريطة
        if not box_entries.empty:
            type_counts = box_entries['Entry_Class'].value_counts()
            # استخدام الألوان المناسبة للخريطة في الرسم البياني
            custom_colors = {'Wing Cross 🟡': 'yellow', 'Central Through Pass 🔵': '#00bfff', 'Dribble / Carry 🔴': '#ff00ff'}
            color_list = [custom_colors.get(name, 'gray') for name in type_counts.index]
            
            fig_bar, ax_bar = plt.subplots(figsize=(6, 4))
            type_counts.plot(kind='bar', color=color_list, ax=ax_bar)
            plt.xticks(rotation=0)
            st.pyplot(fig_bar)
            
            st.write(f"إجمالي عدد محاولات الدخول: {len(box_entries)}")

    st.divider()
    st.subheader("📋 Detailed Raw Entries")
    st.dataframe(box_entries[['Players', 'Entry_Class', 'Event Name', 'Y_Start']])

except Exception as e:
    st.error(f"Error: {e}")
