import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
from highlight_text import ax_text

st.set_page_config(page_title="EPS Pro Heatmaps", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('EPS_Match_Data_Clean.csv')
    df.columns = df.columns.str.strip()
    df['Players'] = df['Players'].astype(str).fillna('Unknown')
    return df

try:
    df = load_data()
    
    # تنظيف قائمة اللاعبين من الـ "|"
    all_names_raw = df['Players'].str.split('|').explode().str.strip()
    clean_player_list = sorted([p for p in all_names_raw.unique() if p and p not in ['nan', 'Unknown']])

    st.sidebar.header("🎨 Heatmap Settings")
    selected_player = st.sidebar.selectbox("Select Player", clean_player_list)

    # فلترة بيانات اللاعب
    player_df = df[df['Players'].str.contains(selected_player, na=False)].copy()

    st.title(f"📍 Visual Performance Report")

    # --- إعداد الرسم الاحترافي ---
    # بنستخدم Pitch بلون غامق عشان الـ Heatmap ينطق
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#777777', stripe=False)
    fig, ax = pitch.draw(figsize=(10, 8))
    fig.set_facecolor('#1a1a1a')

    if not player_df.empty and len(player_df) > 1:
        # رسم الـ Heatmap
        sns.kdeplot(
            x=player_df['X_Start'] * 120, y=player_df['Y_Start'] * 80,
            fill=True, thresh=0.05, levels=100, cmap='magma', alpha=0.7, ax=ax
        )
        
        # إضافة اسم اللاعب داخل الصورة (عشان لما تعمل Save Image الاسم يفضل موجود)
        ax_text(60, -5, f"<{selected_player}>", fontsize=25, color='white', 
                fontweight='bold', ha='center', va='center', ax=ax,
                highlight_textprops=[{"color": "#ff4b4b"}])
        
        ax_text(60, 85, "<EPS Performance Analysis>", fontsize=12, color='#aaaaaa',
                style='italic', ha='center', va='center', ax=ax)

    st.pyplot(fig)

    # زرار تحميل الصورة (اختياري لو عايز تحفظها مباشرة)
    st.info("💡 نصيحة: اضغط كليك يمين على الصورة واختار 'Save Image As' لتحميلها باسم اللاعب.")

except Exception as e:
    st.error(f"Error: {e}")
