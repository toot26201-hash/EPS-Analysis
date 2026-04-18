import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
from highlight_text import ax_text

st.set_page_config(page_title="EPS Pro Analysis", layout="wide")

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

        st.title(f"📊 تقرير الأداء المظبوط: {selected_player}")

        # ضبط الملعب ليكون أفقي (طول 120 وعرض 80)
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1e293b', line_color='#777777', linestyle='--', linewidth=1)
        fig, ax = pitch.draw(figsize=(12, 9))

        if not player_df.empty:
            for _, row in player_df.iterrows():
                # --- تعديل المحاور لضبط الاتجاه ---
                # بنخلي الـ X هي اللي بتعبر عن التقدم للمرمى (الطول) والـ Y هي العرض
                # لو لقيت الاتجاه لسه غلط، جرب نبدل x_s بـ y_s في السطرين اللي جايين
                x_s, y_s = row['X_Start'] * 120, row['Y_Start'] * 80
                x_e, y_e = row['X_End'] * 120, row['Y_End'] * 80
                
                # حساب المسافة (تجنب النقط الميتة)
                if ((x_e-x_s)**2 + (y_e-y_s)**2)**0.5 < 2: continue

                # تلوين ذكي حسب الاتجاه
                if (x_e - x_s) > 10: # تمريرة تقدمية للأمام
                    color = "#38bdf8" # أزرق فاتح
                elif abs(y_e - y_s) > 20: # تمريرة عرضية صريحة
                    color = "#fbbf24" # أصفر
                else:
                    color = "#ef4444" # تمريرة قصيرة أو للخلف

                pitch.arrows(x_s, y_s, x_e, y_e, color=color, ax=ax, width=1.5, headwidth=4, alpha=0.8)

            # كتابة الاسم بوضوح
            ax_text(60, -5, f"<{selected_player}>", fontsize=25, color='white', 
                    fontweight='bold', ha='center', ax=ax, highlight_textprops=[{"color": "#38bdf8"}])
            
        st.pyplot(fig)
        st.write("🔵 تمريرات للأمام | 🟡 عرضيات | 🔴 تمريرات خلفية/قصيرة")

except Exception as e:
    st.error(f"Error: {e}")
