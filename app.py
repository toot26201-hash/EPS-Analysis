import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

st.set_page_config(page_title="EPS Realistic Maps", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('EPS_Match_Data_Clean.csv')
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
    # تنظيف الأسماء
    all_names = df['Players'].str.split('|').explode().str.strip()
    player = st.sidebar.selectbox("Select Player", sorted(all_names.unique()))
    
    p_df = df[df['Players'].str.contains(player, na=False)].copy()

    # --- الملعب ---
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
    fig, ax = pitch.draw(figsize=(12, 8))

    if not p_df.empty:
        for _, row in p_df.iterrows():
            # تحويل الإحداثيات لواقعية الملعب (120x80)
            x_start, y_start = row['X_Start'] * 120, row['Y_Start'] * 80
            x_end, y_end = row['X_End'] * 120, row['Y_End'] * 80
            
            # فلترة التمريرات المستحيلة (لو المسافة أكبر من طول الملعب مثلاً)
            dist = ((x_end-x_start)**2 + (y_end-y_start)**2)**0.5
            if dist < 2: continue # شيل النقط اللي فوق بعضها (الزحمة الفاضية)

            # رسم السهم
            pitch.arrows(x_start, y_start, x_end, y_end, 
                         color='yellow' if y_start < 20 or y_start > 60 else '#00bfff',
                         ax=ax, width=1.2, headwidth=3, alpha=0.7)

    st.pyplot(fig)

    # مراجعة الأرقام للتأكد
    st.write("🔍 مراجعة عينة من إحداثيات اللاعب (X من 0-120 | Y من 0-80):")
    p_df['X_Real'] = p_df['X_Start'] * 120
    p_df['Y_Real'] = p_df['Y_Start'] * 80
    st.dataframe(p_df[['Event Name', 'X_Real', 'Y_Real']].head(10))

except Exception as e:
    st.error(f"Error: {e}")
