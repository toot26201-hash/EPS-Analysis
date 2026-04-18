import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
from highlight_text import ax_text

st.set_page_config(page_title="EPS Pro Analytics", layout="wide")

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
        selected_player = st.sidebar.selectbox("اختر اللاعب", clean_list)
        player_df = df[df['Players'].str.contains(selected_player, na=False)].copy()

        st.title(f"📊 تقرير الأداء الواقعي: {selected_player}")

        # رسم الملعب
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1e293b', line_color='#777777', linestyle='--', linewidth=1)
        fig, ax = pitch.draw(figsize=(12, 9))

        if not player_df.empty:
            for _, row in player_df.iterrows():
                # --- التعديل الجوهري لضبط الاتجاه المعكوس ---
                # بنبدل الـ X والـ Y عشان نعدل التمريرات اللي طالعة بالعرض
                # وبنعكس الـ X عشان الهجمة تمشي لليمين
                x_s, y_s = (1 - row['Y_Start']) * 120, row['X_Start'] * 80
                x_e, y_e = (1 - row['Y_End']) * 120, row['X_End'] * 80
                
                if ((x_e-x_s)**2 + (y_e-y_s)**2)**0.5 < 2: continue

                # تلوين حسب النوع
                if (x_e - x_s) > 15: color = "#38bdf8" # للأمام
                elif abs(y_e - y_s) > 20: color = "#fbbf24" # عرضية
                else: color = "#ef4444" # قصيرة

                pitch.arrows(x_s, y_s, x_e, y_e, color=color, ax=ax, width=1.5, headwidth=4, alpha=0.8)

            # كتابة اسم اللاعب
            ax_text(60, -5, f"<{selected_player}>", fontsize=25, color='white', 
                    fontweight='bold', ha='center', ax=ax, highlight_textprops=[{"color": "#38bdf8"}])
            
        st.pyplot(fig)
        st.write("🔵 تمريرات هجومية | 🟡 عرضيات | 🔴 تمريرات تحضيرية")

except Exception as e:
    st.error(f"Error: {e}")
