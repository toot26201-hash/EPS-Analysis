import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

st.set_page_config(page_title="EPS Analysis", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv('EPS_Match_Data_Clean.csv')

try:
    df = load_data()
    st.title("⚽ EPS Match Dashboard")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Match Events")
        counts = df['Event Name'].str.split(' ').str[0].value_counts()
        st.bar_chart(counts)

    with col2:
        st.subheader("Shot Map")
        # فلترة ذكية للتسديدات
        shots = df[df['Event Name'].str.contains('Shot', case=False, na=False)]
        
        # رسم الملعب بنظام مرن
        pitch = Pitch(pitch_type='custom', pitch_length=100, pitch_width=100)
        fig, ax = pitch.draw()
        
        if not shots.empty:
            # ضرب الإحداثيات في 100 لأن مكتبة الرسم بتفهم الأرقام الكبيرة أحسن
            plt.scatter(shots['X_Start'] * 100, shots['Y_Start'] * 100, c='red', s=100, edgecolors='black')
        
        st.pyplot(fig)

    st.subheader("Top Players (Passes)")
    st.dataframe(df[df['Event Name'].str.contains('Pass', na=False)]['Players'].value_counts().head(10))

except Exception as e:
    st.error(f"Error loading dashboard: {e}")
