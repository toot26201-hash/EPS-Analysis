import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

st.set_page_config(page_title="EPS Tactical Lab", layout="wide")
st.title("⚽ Advanced Penalty Box Entries")

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

    # 2. وظيفة تصنيف "ذكية" للدخول
    def get_entry_method(row):
        # لو هي تمريرة
        if 'Pass' in str(row['Event Name']):
            # العرضية لازم تبدأ من "طرف الملعب" (Y < 0.25 أو Y > 0.75)
            if row['Y_Start'] < 0.25 or row['Y_Start'] > 0.75:
                return "Cross"
            else:
                return "Through Pass / Cut-back"
        # لو مش تمريرة يبقى جري بالكورة
        return "Dribble / Carry"

    if not box_entries.empty:
        box_entries['Method'] = box_entries.apply(get_entry_method, axis=1)

    # --- العرض المرئي ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🎯 Penalty Box Entry Map")
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#efefef', stripe=True)
        fig, ax = pitch.draw(figsize=(10, 7))
        
        # ألوان محددة لكل نوع
        colors = {"Cross": "yellow", "Through Pass / Cut-back": "#00bfff", "Dribble / Carry": "#ff00ff"}
        
        for _, row in box_entries.iterrows():
            pitch.arrows(row.X_Start*120, row.Y_Start*80, row.X_End*120, row.Y_End*80, 
                         color=colors.get(row['Method'], "white"), ax=ax, width=3, headwidth=8)
        
        st.pyplot(fig)
        st.write("🟡 **Yellow: Crosses** (From Wings) | 🔵 **Blue: Central Passes** | 🔴 **Pink: Dribbles**")

    with col2:
        st.subheader("📊 Entry Stats")
        method_counts = box_entries['Method'].value_counts()
        st.bar_chart(method_counts)
        
        st.write("**Top Players entering the box:**")
        st.table(box_entries['Players'].value_counts().head(5))

    st.divider()
    st.subheader("📋 Raw Data (Box Entries Only)")
    st.dataframe(box_entries[['Players', 'Event Name', 'Method', 'X_Start', 'Y_Start']])

except Exception as e:
    st.error(f"Error: {e}")
