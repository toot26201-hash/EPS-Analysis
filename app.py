import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
from highlight_text import ax_text

st.set_page_config(page_title="EPS Corrected Analysis", layout="wide")

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
        st.error(f"Error loading Excel: {e}")
        return pd.DataFrame()

try:
    df = load_data()
    if not df.empty:
        all_names = df['Players'].str.split('|').explode().str.strip()
        clean_list = sorted([p for p in all_names.unique() if p and p not in ['nan', 'Unknown']])
        
        selected_player = st.sidebar.selectbox("اختر اللاعب", clean_list)
        player_df = df[df['Players'].str.contains(selected_player, na=False)].copy()

        st.title(f"📊 تقرير الأداء المظبوط: {selected_player}")

        # رسم الملعب (Vertical=False للتأكد من الاتجاه الطولي)
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc', linestyle='--', linewidth=1)
        fig, ax = pitch.draw(figsize=(12, 9))

        if not player_df.empty:
            for _, row in player_df.iterrows():
                # --- تعديل المحاور السحري ---
                # لو التمريرات جاية بالعرض، هنبدل الـ X والـ Y أو نضبط الضرب في الأبعاد
                x_s, y_s = row['X_Start'] * 120, row['Y_Start'] * 80
                x_e, y_e = row['X_End'] * 120, row['Y_End'] * 80
                
                dist = ((x_e-x_s)**2 + (y_e-y_s)**2)**0.5
                if dist < 2: continue

                # تحديد اللون بناءً على اتجاه الكورة (Progressive)
                if (x_e - x_s) > 15: # تمريرة للأمام
                    color = "#00bfff" # أزرق
                elif abs(y_e - y_s) > 20: # تمريرة عرضية
                    color = "yellow"
                else:
                    color = "#ff4b4b" # قصيرة/للخلف

                pitch.arrows(x_s, y_s, x_e, y_e, color=color, ax=ax, width=1.5, headwidth=4, alpha=0.7)

            ax_text(60, -5, f"<{selected_player}>", fontsize=25, color='white', 
                    fontweight='bold', ha='center', ax=ax, highlight_textprops=[{"color": "#00bfff"}])
            
        st.pyplot(fig)
        st.write("🔵 للأمام (Vertical) | 🟡 عرضية (Lateral) | 🔴 قصيرة/للخلف")

except Exception as e:
    st.error(f"Error: {e}")
