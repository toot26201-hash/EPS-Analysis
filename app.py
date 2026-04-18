import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import numpy as np

st.set_page_config(page_title="EPS Tactical Lab", layout="wide")
st.title("⚽ Advanced Final Third Entries & Pass Types")

@st.cache_data
def load_data():
    df = pd.read_csv('EPS_Match_Data_Clean.csv')
    df.columns = df.columns.str.strip()
    df['Players'] = df['Players'].fillna('Unknown')
    # حساب المسافة التقدمية (للتمييز بين الطولية والقصيرة)
    df['prog_dist'] = df['X_End'] - df['X_Start']
    return df

try:
    df = load_data()

    # 1. فلترة "التمريرات" اللي دخلت التلت الأخير
    f3_entries = df[
        (df['Event Name'].str.contains('Pass', na=False, case=False)) & 
        (df['X_End'] >= 0.66) & (df['X_Start'] < 0.66)
    ].copy()

    # 2. وظيفة تصنيف ذكية لأنواع التمريرات (حسب طلبك)
    def classify_pass_type(row):
        is_pass = 'Pass' in str(row['Event Name'])
        is_wing = row['Y_Start'] < 0.25 or row['Y_Start'] > 0.75
        dist_x = row['prog_dist']

        # العرضية: من الأطراف (Y) وبتدخل الصندوق أو قريبة منه
        if is_pass and is_wing and row['X_End'] > 0.75:
            return "Cross 🟡"
        # البينية/العمودية الطويلة: بتمشي مسافة طويلة للأمام (X)
        elif dist_x > 0.25:
            return "Vertical Long Pass 🔵"
        # البينية القصيرة: بتمشي مسافة قصيرة (اختراق ضيق)
        else:
            return "Short Vertical Pass 🔴"

    if not f3_entries.empty:
        f3_entries['Pass_Type'] = f3_entries.apply(classify_pass_type, axis=1)

    # --- العرض المرئي الرئيسي (The Image Format) ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🗺️ Entry Pass Map (Colored by Type)")
        
        # استخدام الملعب اللي طلبته (النجيلة، الخطوط البيضاء، والخطوط)
        pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white', stripe=True)
        fig, ax = pitch.draw(figsize=(10, 7))
        
        # ألوان محددة لكل نوع (كما في طلبك)
        custom_colors = {"Cross 🟡": "yellow", "Vertical Long Pass 🔵": "#00bfff", "Short Vertical Pass 🔴": "#ff1493"}
        
        # رسم كل نوع لون بلون مختلف
        for pass_type, color in custom_colors.items():
            passes = f3_entries[f3_entries['Pass_Type'] == pass_type]
            if not passes.empty:
                pitch
