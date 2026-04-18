import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
from highlight_text import ax_text

st.set_page_config(page_title="EPS Excel Analytics", layout="wide")

@st.cache_data
def load_data():
    # التعديل هنا: بنقرأ ملف .xlsx بدل .csv
    # تأكد إن اسم الملف في GitHub هو EPS_Match_Data.xlsx
    df = pd.read_excel('EPS_Match_Data.xlsx') 
    df.columns = df.columns.str.strip()
    
    # تحويل الإحداثيات لأرقام
    for col in ['X_Start', 'Y_Start', 'X_End', 'Y_End']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['Players'] = df['Players'].astype(str).fillna('Unknown')
    return df.dropna(subset=['X_Start', 'Y_Start', 'X_End', 'Y_End'])

try:
    df = load_data()
    
    all_names = df['Players'].str.split('|').explode().str.strip()
    clean_list = sorted([p for p in all_names.unique() if p and p not in ['nan', 'Unknown']])
    
    selected_player = st.sidebar.selectbox("اختر لاعب EPS", clean_list)
    p_df = df[df['Players'].str.contains(selected_player, na=False)].copy()

    st.title(f"📍 Pass Map: {selected_player}")

    pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#777777',
                  linestyle='--', linewidth=1, goal_linestyle='-')
    fig, ax = pitch.draw(figsize=(12, 9))
    fig.set_facecolor('#1a1a1a')

    if not p_df.empty:
        for _, row in p_df.iterrows():
            x_s, y_s = row['X_Start'] * 120, row['Y_Start'] * 80
            x_e, y_e = row['X_End'] * 120, row['Y_End'] * 80
            
            dist = ((x_e-x_s)**2 + (y_e-y_s)**2)**0.5
            if dist < 3: continue 

            if y_s < 20 or y_s > 60: color = "yellow"
            elif (x_e - x_s) > 25: color = "#00bfff"
            else: color = "#ff4b4b"

            pitch.arrows(x_s, y_s, x_e, y_e, color=color, ax=ax, 
                         width=1.2, headwidth=3, alpha=0.6)

        ax_text(60, -5, f"<{selected_player}> | <EPS Tactical Analysis>", 
                fontsize=20, color='white', fontweight='bold', ha='center', ax=ax,
                highlight_textprops=[{"color": "#00bfff"}, {"color": "yellow"}])
        
        st.pyplot(fig)
    else:
        st.warning("لا توجد بيانات لهذا اللاعب في ملف الإكسيل.")

except Exception as e:
    st.error(f"Error: {e}")
