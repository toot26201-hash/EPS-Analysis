import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

st.set_page_config(page_title="EPS Tactical Analysis", layout="wide")
st.title("⚽ Final Third Entries & Pass Types")

@st.cache_data
def load_data():
    df = pd.read_csv('EPS_Match_Data_Clean.csv')
    df.columns = df.columns.str.strip()
    df['Players'] = df['Players'].fillna('Unknown')
    return df

try:
    df = load_data()
    
    # 1. فلترة التمريرات التي دخلت الثلث الأخير
    f3_entries = df[
        (df['Event Name'].str.contains('Pass', na=False, case=False)) & 
        (df['X_End'] >= 0.66) & (df['X_Start'] < 0.66)
    ].copy()

    # 2. تصنيف أنواع التمريرات بدقة (بالأرقام اللي شفناها في الجدول)
    def classify_pass(row):
        # لو بدأت من الطرف (Y قريبة من 0 أو 1)
        if row['Y_Start'] < 0.25 or row['Y_Start'] > 0.75:
            return "Cross 🟡"
        # لو مشيت مسافة طويلة للأمام
        elif (row['X_End'] - row['X_Start']) > 0.20:
            return "Long Pass 🔵"
        else:
            return "Short Pass 🔴"

    if not f3_entries.empty:
        f3_entries['Type'] = f3_entries.apply(classify_pass, axis=1)

    # --- العرض المرئي ---
    col1, col2 = st.columns([2, 1])

    with col1:
        # الملعب اللي طلبته بالظبط
        pitch = Pitch(pitch_color='grass', line_color='white', stripe=True)
        fig, ax = pitch.draw(figsize=(10, 7))
        
        # رسم التمريرات ملونة
        colors = {"Cross 🟡": "yellow", "Long Pass 🔵": "#00bfff", "Short Pass 🔴": "#ff4b4b"}
        
        for p_type, color in colors.items():
            subset = f3_entries[f3_entries['Type'] == p_type]
            if not subset.empty:
                pitch.arrows(subset.X_Start*120, subset.Y_Start*80, 
                             subset.X_End*120, subset.Y_End*80, 
                             color=color, ax=ax, width=3, headwidth=8, label=p_type)
        
        st.pyplot(fig)
        st.write("🟡 **Yellow: Crosses** | 🔵 **Blue: Long Vertical** | 🔴 **Red: Short/Inner**")

    with col2:
        st.subheader("📊 Entries Stats")
        if not f3_entries.empty:
            st.bar_chart(f3_entries['Type'].value_counts())
            st.write("**Top Players:**")
            st.write(f3_entries['Players'].value_counts().head(5))

except Exception as e:
    st.error(f"Error in execution: {e}")
