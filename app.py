import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mplsoccer import Pitch

st.set_page_config(page_title="EPS Team Tactical Analysis", layout="wide")

@st.cache_data
def load_data():
    try:
        # تأكد أن اسم الملف EPS_Match_Data.xlsx
        df = pd.read_excel('EPS_Match_Data.xlsx')
        df.columns = df.columns.str.strip()
        # تحويل الإحداثيات لأرقام
        for col in ['X_Start', 'Y_Start', 'X_End', 'Y_End']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df.dropna(subset=['X_Start', 'Y_Start', 'X_End', 'Y_End'])
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("🎯 EPS Team: Zone 14 & Half-space Entries")
    st.subheader("تحليل اختراقات الفريق للمناطق المؤثرة")

    # --- معالجة الإحداثيات للجماعي ---
    # ضبط المحاور (الـ Y في الإكسيل هو الـ X في الملعب)
    df['x_s_plot'] = df['Y_Start'] * 120
    df['y_s_plot'] = df['X_Start'] * 80
    df['x_e_plot'] = df['Y_End'] * 120
    df['y_e_plot'] = df['X_End'] * 80

    # تعريف المناطق تكتيكياً
    def classify_zone(x, y):
        # Zone 14 (80-102 طول، 30-50 عرض)
        if 80 <= x <= 102 and 30 <= y <= 50:
            return "Zone 14"
        # Half-spaces (80-102 طول، العرض 18-30 أو 50-62)
        elif 80 <= x <= 102 and ((18 <= y <= 30) or (50 <= y <= 62)):
            return "Half-space"
        return "Other"

    df['Target_Zone'] = df.apply(lambda r: classify_zone(r['x_e_plot'], r['y_e_plot']), axis=1)
    
    # فلترة التمريرات الجماعية اللي دخلت المناطق دي بس
    team_tactical = df[df['Target_Zone'] != "Other"].copy()

    # رسم الملعب
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#1e293b', line_color='#777777')
    fig, ax = pitch.draw(figsize=(13, 9))

    # رسم تظليل المناطق
    # Zone 14 (أحمر خفيف)
    ax.add_patch(patches.Rectangle((80, 30), 22, 20, color='red', alpha=0.1, label='Zone 14'))
    # Half-spaces (أزرق خفيف)
    ax.add_patch(patches.Rectangle((80, 18), 22, 12, color='blue', alpha=0.05, label='Half-space'))
    ax.add_patch(patches.Rectangle((80, 50), 22, 12, color='blue', alpha=0.05))

    # رسم التمريرات (كل نوع بلون)
    for _, row in team_tactical.iterrows():
        if row['Target_Zone'] == "Zone 14":
            color = "#ff4b4b" # أحمر للـ Zone 14
            label = "Zone 14"
        else:
            color = "#38bdf8" # أزرق للـ Half-space
            label = "Half-space"
            
        pitch.arrows(row['x_s_plot'], row['y_s_plot'], 
                     row['x_e_plot'], row['y_e_plot'], 
                     color=color, ax=ax, width=2, headwidth=4, alpha=0.7)

    st.pyplot(fig)

    # إحصائيات سريعة للمدرب
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Zone 14 Entries", len(team_tactical[team_tactical['Target_Zone']=="Zone 14"]))
    with col2:
        st.metric("Total Half-space Entries", len(team_tactical[team_tactical['Target_Zone']=="Half-space"]))

    st.write("🔴 Zone 14 Entries | 🔵 Half-space Entries")
    st.dataframe(team_tactical[['Players', 'Event Name', 'Target_Zone']].sort_values('Target_Zone'))

else:
    st.info("ارفع ملف الإكسيل EPS_Match_Data.xlsx عشان نشوف أداء الفريق.")
