import streamlit as st
import pandas as pd
from mplsoccer import Pitch
import matplotlib.pyplot as plt

st.set_page_config(page_title="EPS Tactical Zones", layout="wide")

@st.cache_data
def load_data():
    try:
        df = pd.read_excel('EPS_Match_Data.xlsx')
        df.columns = df.columns.str.strip()
        for col in ['X_Start', 'Y_Start', 'X_End', 'Y_End']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df.dropna(subset=['X_End', 'Y_End'])
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

def get_zone(x, y):
    # تعريف Zone 14 (StatsBomb coords: X 80-102, Y 30-50)
    if 80 <= x <= 102 and 30 <= y <= 50:
        return "Zone 14"
    # تعريف الـ Half-spaces (StatsBomb coords: Y 18-30 or 50-62)
    elif 80 <= x <= 102 and ((18 <= y <= 30) or (50 <= y <= 62)):
        return "Half-space"
    return "Other"

df = load_data()
if not df.empty:
    # فك الأسماء
    all_names = df['Players'].str.split('|').explode().str.strip()
    selected_player = st.sidebar.selectbox("Select Player", sorted(all_names.unique()))
    
    p_df = df[df['Players'].str.contains(selected_player, na=False)].copy()

    # حساب المنطقة والنوع (تبديل المحاور لضبط الاتجاه اللي اتفقنا عليه)
    p_df['Real_X_End'] = p_df['Y_End'] * 120
    p_df['Real_Y_End'] = p_df['X_End'] * 80
    p_df['Target_Zone'] = p_df.apply(lambda row: get_zone(row['Real_X_End'], row['Real_Y_End']), axis=1)

    # فلترة التمريرات اللي دخلت المناطق دي بس
    tactical_passes = p_df[p_df['Target_Zone'] != "Other"].copy()

    st.title(f"🎯 Tactical Entry Map: {selected_player}")
    
    col1, col2 = st.columns([3, 1])

    with col1:
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1e293b', line_color='#777777')
        fig, ax = pitch.draw(figsize=(10, 7))
        
        # رسم المناطق تظليلياً للفهم
        # Zone 14
        pitch.box(80, 30, 102, 50, ax=ax, color='red', alpha=0.1, label='Zone 14')
        # Half-spaces
        pitch.box(80, 18, 102, 30, ax=ax, color='blue', alpha=0.1)
        pitch.box(80, 50, 102, 62, ax=ax, color='blue', alpha=0.1)

        for _, row in tactical_passes.iterrows():
            color = "#ff4b4b" if row['Target_Zone'] == "Zone 14" else "#38bdf8"
            pitch.arrows(row['Y_Start']*120, row['X_Start']*80, 
                         row['Real_X_End'], row['Real_Y_End'], 
                         color=color, ax=ax, width=2, headwidth=4)
        st.pyplot(fig)

    with col2:
        st.subheader("📊 Summary")
        st.write(f"Total Tactical Entries: {len(tactical_passes)}")
        st.dataframe(tactical_passes[['Event Name', 'Target_Zone']])

else:
    st.info("ارفع ملف الإكسيل عشان نبدأ التحليل.")
