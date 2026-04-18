import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
from highlight_text import ax_text

st.set_page_config(page_title="EPS Calibration Tool", layout="wide")

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
        # فك الأسماء
        all_names = df['Players'].str.split('|').explode().str.strip()
        clean_list = sorted([p for p in all_names.unique() if p and p not in ['nan', 'Unknown']])
        
        st.sidebar.header("⚙️ إعدادات المعايرة")
        selected_player = st.sidebar.selectbox("اختر اللاعب", clean_list)
        
        # --- السحر هنا: أزرار لضبط الاتجاه لو طلع غلط ---
        flip_axes = st.sidebar.checkbox("تبديل الطول بالعرض (Swap X/Y)")
        invert_x = st.sidebar.checkbox("عكس اتجاه الهجوم (Invert X)")

        player_df = df[df['Players'].str.contains(selected_player, na=False)].copy()

        st.title(f"📊 Pass Map: {selected_player}")

        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1e293b', line_color='#777777', linestyle='--', linewidth=1)
        fig, ax = pitch.draw(figsize=(12, 9))

        for _, row in player_df.iterrows():
            # ضبط الإحداثيات بناءً على اختياراتك في الـ Sidebar
            if flip_axes:
                xs, ys = row['Y_Start'], row['X_Start']
                xe, ye = row['Y_End'], row['X_End']
            else:
                xs, ys = row['X_Start'], row['Y_Start']
                xe, ye = row['X_End'], row['Y_End']
            
            if invert_x:
                xs, xe = 1 - xs, 1 - xe

            # التحويل النهائي لمقاس الملعب
            x_s, y_s = xs * 120, ys * 80
            x_e, y_e = xe * 120, ye * 80
            
            if ((x_e-x_s)**2 + (y_e-y_s)**2)**0.5 < 4: continue

            # تلوين ذكي
            color = "#38bdf8" if (x_e - x_s) > 10 else "#ef4444"
            pitch.arrows(x_s, y_s, x_e, y_e, color=color, ax=ax, width=2, headwidth=4, alpha=0.7)

        ax_text(60, -5, f"<{selected_player}>", fontsize=25, color='white', fontweight='bold', ha='center', ax=ax, highlight_textprops=[{"color": "#38bdf8"}])
        st.pyplot(fig)

except Exception as e:
    st.error(f"Error: {e}")
