import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

st.set_page_config(page_title="EPS Tactical Analysis", layout="wide")
st.title("⚽ Final Third Entry Analysis")

@st.cache_data
def load_data():
    df = pd.read_csv('EPS_Match_Data_Clean.csv')
    df.columns = df.columns.str.strip()
    df['Players'] = df['Players'].fillna('Unknown')
    return df

try:
    df = load_data()
    
    # فلترة التمريرات التي دخلت الثلث الأخير (X_End >= 0.66) وكانت بدأت قبل الخط ده
    f3_passes = df[
        (df['Event Name'].str.contains('Pass', na=False, case=False)) & 
        (df['X_End'] >= 0.66) & (df['X_Start'] < 0.66)
    ].copy()

    # تحديد الجانب (Zones) بناءً على عرض الملعب Y
    # تقسيم الملعب لـ 3 ممرات: Left (0-0.33), Center (0.33-0.66), Right (0.66-1)
    def get_side(y):
        if y < 0.33: return "Left Wing"
        elif y > 0.66: return "Right Wing"
        else: return "Central"

    f3_passes['Side'] = f3_passes['Y_Start'].apply(get_side)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🗺️ Final Third Passes Map")
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#efefef', stripe=True)
        fig, ax = pitch.draw(figsize=(10, 7))
        
        if not f3_passes.empty:
            # رسم الأسهم: من البداية للنهاية
            pitch.arrows(f3_passes.X_Start*120, f3_passes.Y_Start*80, 
                         f3_passes.X_End*120, f3_passes.Y_End*80, 
                         width=2, headwidth=10, headlength=10, color='#adff2f', ax=ax, label='Entry Pass')
        st.pyplot(fig)

    with col2:
        st.subheader("📊 Entries by Side")
        side_counts = f3_passes['Side'].value_counts()
        st.bar_chart(side_counts)
        
        st.subheader("📋 Pass Types")
        type_counts = f3_passes['Event Name'].value_counts()
        st.write(type_counts)

    st.divider()
    st.subheader("Detailed Entries Table")
    st.dataframe(f3_passes[['Players', 'Event Name', 'Side', 'X_Start', 'X_End']])

except Exception as e:
    st.error(f"Error: {e}")
