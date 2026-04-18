import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import os

st.set_page_config(page_title="EPS Analysis", layout="wide")
st.title("⚽ EPS Match Dashboard")

# اسم الملف اللي بنور عليه
FILE_NAME = 'EPS_Match_Data_Clean.csv'

if os.path.exists(FILE_NAME):
    df = pd.read_csv(FILE_NAME)
    
    # تنظيف أسماء الأعمدة من أي مسافات زايدة
    df.columns = df.columns.str.strip()
    
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📊 Match Summary")
        if 'Event Name' in df.columns:
            counts = df['Event Name'].str.split(' ').str[0].value_counts()
            st.bar_chart(counts)
        else:
            st.warning("Column 'Event Name' not found")

    with col2:
        st.subheader("🎯 Shot Map")
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
        fig, ax = pitch.draw(figsize=(8, 6))
        
        # محاولة رسم التسديدات لو الأعمدة موجودة
        if 'X_Start' in df.columns and 'Y_Start' in df.columns:
            shots = df[df['Event Name'].str.contains('Shot', na=False, case=False)]
            # تحويل الإحداثيات لمقياس Statsbomb (120x80) لو هي (0-1)
            pitch.scatter(shots['X_Start']*120, shots['Y_Start']*80, ax=ax, c='#ef4444', s=100)
        
        st.pyplot(fig)

    st.subheader("🔝 Top Players (Passes)")
    if 'Players' in df.columns:
        st.dataframe(df[df['Event Name'].str.contains('Pass', na=False)]['Players'].value_counts().head(10))

else:
    st.error(f"❌ الملف مش موجود في GitHub! اتأكد إنك رفعت ملف اسمه: {FILE_NAME}")
    st.info("الملفات اللي السيستم شايفها دلوقتي هي: " + str(os.listdir()))
