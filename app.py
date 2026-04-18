import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
from highlight_text import ax_text

st.set_page_config(page_title="EPS Pro Elite Analysis", layout="wide")

@st.cache_data
def load_data():
    try:
        df = pd.read_excel('EPS_Match_Data.xlsx') 
        df.columns = df.columns.str.strip()
        for col in ['X_Start', 'Y_Start', 'X_End', 'Y_End']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df['Players'] = df['Players'].astype(str).fillna('Unknown')
        return df.dropna(subset=['X_Start', 'Y_Start', 'X_End', 'Y_End'])
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

try:
    df = load_data()
    if not df.empty:
        all_names = df['Players'].str.split('|').explode().str.strip()
        clean_list = sorted([p for p in all_names.unique() if p and p not in ['nan', 'Unknown']])
        selected_player = st.sidebar.selectbox("Select Player", clean_list)
        player_df = df[df['Players'].str.contains(selected_player, na=False)].copy()

        st.title(f"📊 Tactical Report: {selected_player}")

        # رسم الملعب
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1e293b', line_color='#777777', linestyle='--', linewidth=1)
        fig, ax = pitch.draw(figsize=(12, 9))

        if not player_df.empty:
            for _, row in player_df.iterrows():
                # --- الفلترة والضبط النهائي ---
                # تبديل X و Y عشان نعدل الاتجاه المائل
                x_s, y_s = row['Y_Start'] * 120, row['X_Start'] * 80
                x_e, y_e = row['Y_End'] * 120, row['X_End'] * 80
                
                # حساب المسافة (لو التمريرة أقل من 4 متر شيلها لأنها بتعمل زحمة)
                dist = ((x_e-x_s)**2 + (y_e-y_s)**2)**0.5
                if dist < 4: continue

                # تحديد اللون بناءً على التقدم للأمام فقط
                if (x_e - x_s) > 10: 
                    color = "#38bdf8" # تمريرة للأمام (مفيدة)
                    alpha = 0.8
                elif abs(y_e - y_s) > 20:
                    color = "#fbbf24" # عرضية
                    alpha = 0.6
                else:
                    color = "#ef4444" # للخلف أو عرضية قصيرة
                    alpha = 0.4

                pitch.arrows(x_s, y_s, x_e, y_e, color=color, ax=ax, width=1.8, headwidth=4, alpha=alpha)

            # إضافة اسم اللاعب
            ax_text(60, -5, f"<{selected_player}>", fontsize=25, color='white', 
                    fontweight='bold', ha='center', ax=ax, highlight_textprops=[{"color": "#38bdf8"}])
            
        st.pyplot(fig)
        st.write("🔵 تمريرات هجومية | 🟡 عرضيات | 🔴 تمريرات تحضيرية")

except Exception as e:
    st.error(f"Error: {e}")
