import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns

st.set_page_config(page_title="EPS Player Heatmaps", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('EPS_Match_Data_Clean.csv')
    df.columns = df.columns.str.strip()
    df['Players'] = df['Players'].fillna('Unknown')
    return df

try:
    df = load_data()
    
    # --- القائمة الجانبية لاختيار اللاعب ---
    st.sidebar.header("Filter by Player")
    player_list = sorted([str(p) for p in df['Players'].unique()])
    selected_player = st.sidebar.selectbox("Choose Player", player_list)

    # فلترة البيانات للاعب المختار فقط
    player_df = df[df['Players'] == selected_player]

    st.title(f"🔥 Heatmap: {selected_player}")

    # --- رسم الخريطة الحرارية ---
    # استخدمنا ملعب الـ Grass اللي طلبته
    pitch = Pitch(pitch_color='grass', line_color='white', stripe=True)
    fig, ax = pitch.draw(figsize=(10, 7))

    if not player_df.empty:
        # رسم الخريطة الحرارية باستخدام Seaborn
        # ملحوظة: بنضرب في 120 و 80 عشان يتناسب مع أبعاد الملعب
        sns.kdeplot(
            x=player_df['X_Start'] * 120,
            y=player_df['Y_Start'] * 80,
            fill=True,
            thresh=0.05,
            levels=100,
            cmap='hot', # لون النار للخريطة الحرارية
            alpha=0.6,
            ax=ax
        )
        
    st.pyplot(fig)

    # --- إحصائيات سريعة للاعب أسفل الخريطة ---
    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Actions", len(player_df))
    col2.metric("Passes", len(player_df[player_df['Event Name'].str.contains('Pass', na=False)]))
    col3.metric("Shots", len(player_df[player_df['Event Name'].str.contains('Shot', na=False)]))

except Exception as e:
    st.error(f"Error: {e}")
