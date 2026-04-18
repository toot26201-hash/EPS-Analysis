import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
from highlight_text import ax_text

# إعداد الصفحة
st.set_page_config(page_title="EPS Individual Performance", layout="wide")

@st.cache_data
def load_data():
    try:
        df = pd.read_excel('EPS_Match_Data.xlsx') 
        df.columns = df.columns.str.strip()
        # تحويل الإحداثيات لأرقام
        for col in ['X_Start', 'Y_Start', 'X_End', 'Y_End']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df['Players'] = df['Players'].astype(str).fillna('Unknown')
        return df.dropna(subset=['X_Start', 'Y_Start', 'X_End', 'Y_End'])
    except Exception as e:
        st.error(f"تأكد من وجود ملف EPS_Match_Data.xlsx: {e}")
        return pd.DataFrame()

try:
    df = load_data()

    if not df.empty:
        # فك الأسماء لضمان ظهور لاعب واحد فقط في القائمة
        all_names = df['Players'].str.split('|').explode().str.strip()
        clean_list = sorted([p for p in all_names.unique() if p and p not in ['nan', 'Unknown']])

        st.sidebar.header("👤 لوحة التحكم")
        selected_player = st.sidebar.selectbox("اختر اللاعب", clean_list)
        mode = st.sidebar.radio("نوع الخريطة", ["Heatmap", "Pass Map"])

        player_df = df[df['Players'].str.contains(selected_player, na=False)].copy()

        st.title(f"📊 تقرير أداء: {selected_player}")

        if mode == "Heatmap":
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#777777')
            fig, ax = pitch.draw(figsize=(10, 8))
            if not player_df.empty:
                sns.kdeplot(x=player_df['X_Start']*120, y=player_df['Y_Start']*80, 
                            fill=True, thresh=0.05, levels=100, cmap='magma', alpha=0.7, ax=ax)
                # تصليح الخطأ هنا (لون واحد لاسم اللاعب)
                ax_text(60, -5, f"<{selected_player}>", fontsize=22, color='white', 
                        fontweight='bold', ha='center', ax=ax, highlight_textprops=[{"color": "#ff4b4b"}])
            st.pyplot(fig)

        else:
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc', 
                          linestyle='--', linewidth=1)
            fig, ax = pitch.draw(figsize=(10, 8))
            passes = player_df[player_df['Event Name'].str.contains('Pass', na=False)].copy()
            
            if not passes.empty:
                for _, row in passes.iterrows():
                    x_s, y_s = row['X_Start'] * 120, row['Y_Start'] * 80
                    x_e, y_e = row['X_End'] * 120, row['Y_End'] * 80
                    if ((x_e-x_s)**2 + (y_e-y_s)**2)**0.5 < 3: continue

                    if y_s < 20 or y_s > 60: color = "yellow"
                    elif (x_e - x_s) > 25: color = "#00bfff"
                    else: color = "#ff4b4b"

                    pitch.arrows(x_s, y_s, x_e, y_e, color=color, ax=ax, width=1.2, headwidth=3, alpha=0.6)
                
                ax_text(60, -5, f"<{selected_player}>", fontsize=22, color='white', 
                        fontweight='bold', ha='center', ax=ax, highlight_textprops=[{"color": "#00bfff"}])
            st.pyplot(fig)

except Exception as e:
    st.error(f"حدث خطأ: {e}")
