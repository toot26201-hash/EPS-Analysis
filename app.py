import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch, VerticalPitch
import numpy as np

st.set_page_config(page_title="EPS Elite Dashboard", layout="wide")
st.title("🚀 EPS Elite Tactical Analytics")

@st.cache_data
def load_data():
    df = pd.read_csv('EPS_Match_Data_Clean.csv')
    df.columns = df.columns.str.strip()
    df['Players'] = df['Players'].fillna('Unknown')
    # حساب المسافة التقدمية (كم متر الكورة قربت للمرمى)
    df['prog_dist'] = df['X_End'] - df['X_Start']
    return df

try:
    df = load_data()
    
    # القائمة الجانبية
    st.sidebar.header("Elite Analytics")
    analysis_type = st.sidebar.selectbox("Select Analysis", ["Progressive Actions", "Pass Network", "Field Tilt"])
    selected_player = st.sidebar.selectbox("Filter by Player", ["All Team"] + sorted(df['Players'].unique().tolist()))

    if selected_player != "All Team":
        df_filtered = df[df['Players'] == selected_player]
    else:
        df_filtered = df

    # 1. تحليل التمريرات التقدمية (Progressive Passes)
    if analysis_type == "Progressive Actions":
        st.subheader("🎯 Progressive Passes & Carries")
        # تعريف التمريرة التقدمية: هي اللي بتمشي 10 متر لقدام على الأقل في اتجاه الخصم
        prog_df = df_filtered[(df_filtered['Event Name'].str.contains('Pass', na=False)) & (df_filtered['prog_dist'] > 0.25)]
        
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#c7d5cc')
        fig, ax = pitch.draw(figsize=(12, 8))
        pitch.arrows(prog_df.X_Start*120, prog_df.Y_Start*80, prog_df.X_End*120, prog_df.Y_End*80, 
                     color='#39FF14', width=2, headwidth=10, ax=ax)
        st.pyplot(fig)
        st.info(f"عدد التمريرات التقدمية: {len(prog_df)} - وهي التمريرات التي تكسر الخطوط وتدفع الفريق للأمام.")

    # 2. شبكة التمرير (Pass Network - Simplified)
    elif analysis_type == "Pass Network":
        st.subheader("🕸️ Player Connections (Simplified)")
        # حساب متوسط مراكز اللاعبين وعدد التمريرات بينهم
        avg_locations = df.groupby('Players').agg({'X_Start': 'mean', 'Y_Start': 'mean'}).reset_index()
        
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#555555')
        fig, ax = pitch.draw(figsize=(10, 7))
        
        # رسم اللاعبين كدوائر في أماكنهم المتوسطة
        pitch.scatter(avg_locations.X_Start*120, avg_locations.Y_Start*80, s=300, color='#00bfff', edgecolors='white', ax=ax)
        for i, row in avg_locations.iterrows():
            pitch.annotate(row.Players, (row.X_Start*120, row.Y_Start*80-2), ax=ax, color='white', fontsize=8, ha='center')
        st.pyplot(fig)
        st.write("هذا الشكل يوضح متوسط تمركز اللاعبين وشكل الـ Structure الخاص بالفريق.")

    # 3. الـ Field Tilt (الضغط العالي)
    elif analysis_type == "Field Tilt":
        st.subheader("🔥 Field Tilt & Territory Control")
        # تقسيم الملعب لـ 5 مناطق طولية
        df['zone'] = pd.cut(df['X_Start'], bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0], labels=['Own 1st', 'Own 2nd', 'Middle', 'Final 3rd', 'Deep Box'])
        zone_counts = df['zone'].value_counts().sort_index()
        st.bar_chart(zone_counts)
        st.write("يوضح الرسم البياني في أي منطقة من الملعب يمتلك الفريق أكبر عدد من الأفعال (Actions).")

except Exception as e:
    st.error(f"Error: {e}")
