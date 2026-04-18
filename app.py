import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mplsoccer import Pitch

st.set_page_config(page_title="EPS Team Analysis", layout="wide")

@st.cache_data
def load_data():
    try:
        # تأكد أن اسم الملف EPS_Match_Data.xlsx
        df = pd.read_excel('EPS_Match_Data.xlsx')
        df.columns = df.columns.str.strip()
        for col in ['X_Start', 'Y_Start', 'X_End', 'Y_End']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df.dropna(subset=['X_Start', 'Y_Start', 'X_End', 'Y_End'])
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("🎯 EPS Team: Zone 14 & Half-space Arrows")

    # --- ضبط الإحداثيات (قلبة المحاور لضبط الاتجاه) ---
    df['x_s'] = df['Y_Start'] * 120
    df['y_s'] = df['X_Start'] * 80
    df['x_e'] = df['Y_End'] * 120
    df['y_e'] = df['X_End'] * 80

    # تعريف المناطق بدقة
    def classify_zone(x, y):
        # Zone 14
        if 80 <= x <= 102 and 30 <= y <= 50:
            return "Zone 14"
        # Half-spaces
        elif 80 <= x <= 102 and ((18 <= y <= 30) or (50 <= y <= 62)):
            return "Half-space"
        return "Other"

    df['Target_Zone'] = df.apply(lambda r: classify_zone(r['x_e'], r['y_e']), axis=1)
    
    # فلترة التمريرات اللي دخلت الأهداف التكتيكية
    team_passes = df[df['Target_Zone'] != "Other"].copy()

    # رسم الملعب
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#1e293b', line_color='#777777')
    fig, ax = pitch.draw(figsize=(13, 9))

    # 1. رسم التظليل أولاً (عشان يكون تحت الأسهم)
    ax.add_patch(patches.Rectangle((80, 30), 22, 20, color='red', alpha=0.15)) # Zone 14
    ax.add_patch(patches.Rectangle((80, 18), 22, 12, color='blue', alpha=0.1)) # Half-space Top
    ax.add_patch(patches.Rectangle((80, 50), 22, 12, color='blue', alpha=0.1)) # Half-space Bottom

    # 2. رسم الأسهم فوق التظليل
    if not team_passes.empty:
        for _, row in team_passes.iterrows():
            color = "#ff4b4b" if row['Target_Zone'] == "Zone 14" else "#38bdf8"
            # رسم السهم
            pitch.arrows(row['x_s'], row['y_s'], row['x_e'], row['y_e'], 
                         color=color, ax=ax, width=2.5, headwidth=4, alpha=0.9, zorder=3)
        
        st.pyplot(fig)
        
        # ملخص الأرقام
        c1, c2 = st.columns(2)
        c1.metric("Zone 14 Entries 🔴", len(team_passes[team_passes['Target_Zone']=="Zone 14"]))
        c2.metric("Half-space Entries 🔵", len(team_passes[team_passes['Target_Zone']=="Half-space"]))
    else:
        st.warning("لم يتم العثور على تمريرات دخلت هذه المناطق. تأكد من دقة الإحداثيات في ملف الإكسيل.")
        st.pyplot(fig)

else:
    st.info("ارفع ملف الإكسيل EPS_Match_Data.xlsx")
