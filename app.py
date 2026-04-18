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
    
    # 1. فلترة التمريرات اللي دخلت التلت الأخير
    f3_passes = df[
        (df['Event Name'].str.contains('Pass', na=False, case=False)) & 
        (df['X_End'] >= 0.66) & (df['X_Start'] < 0.66)
    ].copy()

    # 2. وظيفة لتصنيف نوع التمريرة بناءً على طولها أو مكانها
    def classify_pass(row):
        dist_x = row['X_End'] - row['X_Start']
        # إذا كانت التمريرة عرضية (بتتحرك بالعرض أكتر ما بتتحرك للطول في منطقة الأطراف)
        if abs(row['Y_End'] - row['Y_Start']) > 0.3 and row['X_End'] > 0.7:
            return "Cross"
        elif dist_x > 0.2:
            return "Long Vertical Pass"
        else:
            return "Short/Normal Pass"

    # 3. تحديد الجانب (Zone)
    def get_side(y):
        if y < 0.30: return "Left Wing"
        elif y > 0.70: return "Right Wing"
        else: return "Central"

    if not f3_passes.empty:
        f3_passes['Pass Type'] = f3_passes.apply(classify_pass, axis=1)
        f3_passes['Side'] = f3_passes['Y_Start'].apply(get_side)

    # --- العرض ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🗺️ Entry Passes Map")
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#efefef', stripe=True)
        fig, ax = pitch.draw(figsize=(10, 7))
        
        if not f3_passes.empty:
            # رسم التمريرات بألوان مختلفة حسب النوع
            for _, row in f3_passes.iterrows():
                color = "#adff2f" if row['Pass Type'] == "Cross" else "#00bfff"
                pitch.arrows(row.X_Start*120, row.Y_Start*80, 
                             row.X_End*120, row.Y_End*80, 
                             width=2, color=color, ax=ax)
            st.write("🟢 Green: Crosses | 🔵 Blue: Vertical Passes")
        st.pyplot(fig)

    with col2:
        st.subheader("📊 Statistics")
        
        st.write("**Entries by Side:**")
        st.bar_chart(f3_passes['Side'].value_counts())
        
        st.write("**Pass Types into Final Third:**")
        st.bar_chart(f3_passes['Pass Type'].value_counts())

    st.divider()
    st.subheader("📋 Final Third Entry Details")
    st.dataframe(f3_passes[['Players', 'Pass Type', 'Side', 'Event Name']])

except Exception as e:
    st.error(f"Error: {e}")
