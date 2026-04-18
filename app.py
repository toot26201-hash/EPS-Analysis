import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
from highlight_text import ax_text

st.set_page_config(page_title="EPS Pro Tactical", layout="wide")

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
        # فك الأسامي لظهور لاعب واحد فقط
        all_names = df['Players'].str.split('|').explode().str.strip()
        clean_list = sorted([p for p in all_names.unique() if p and p not in ['nan', 'Unknown']])
        selected_player = st.sidebar.selectbox("Select Player", clean_list)
        player_df = df[df['Players'].str.contains(selected_player, na=False)].copy()

        st.title(f"📊 تقرير الأداء الواقعي: {selected_player}")

        # رسم ملعب StatsBomb (120x80)
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1e293b', line_color='#777777', linestyle='--', linewidth=1)
        fig, ax = pitch.draw(figsize=(12, 9))

        if not player_df.empty:
            for _, row in player_df.iterrows():
                # --- التعديل السحري لضبط الاتجاه المقلوب ---
                # البيانات الأصلية (Y) هي اللي بتعبر عن التقدم للمرمى في ملفك
                # بنخلي الـ Y تترسم على محور الـ X والـ X تترسم على محور الـ Y
                x_s, y_s = row['Y_Start'] * 120, row['X_Start'] * 80
                x_e, y_e = row['Y_End'] * 120, row['X_End'] * 80
                
                # حساب المسافة (لو أقل من 2 متر متترسمش عشان الزحمة)
                if ((x_e-x_s)**2 + (y_e-y_s)**2)**0.5 < 2: continue

                # تلوين تكتيكي حسب اتجاه السهم الجديد
                if (x_e - x_s) > 10: color = "#38bdf8" # للأمام (هجومية)
                elif abs(y_e - y_s) > 20: color = "#fbbf24" # عرضية صريحة
                else: color = "#ef4444" # قصيرة أو للخلف

                pitch.arrows(x_s, y_s, x_e, y_e, color=color, ax=ax, width=1.8, headwidth=4, alpha=0.8)

            # كتابة الاسم بوضوح داخل الصورة
            ax_text(60, -5, f"<{selected_player}>", fontsize=25, color='white', 
                    fontweight='bold', ha='center', ax=ax, highlight_textprops=[{"color": "#38bdf8"}])
            
        st.pyplot(fig)
        st.write("🔵 تمريرات للأمام | 🟡 عرضيات | 🔴 تمريرات خلفية/قصيرة")

except Exception as e:
    st.error(f"Error: {e}")
