import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns

st.set_page_config(page_title="EPS Pro Dashboard", layout="wide")
st.title("⚽ EPS Tactical Analysis Dashboard")

@st.cache_data
def load_data():
    df = pd.read_csv('EPS_Match_Data_Clean.csv')
    df.columns = df.columns.str.strip()
    df['Players'] = df['Players'].fillna('Unknown')
    return df

try:
    df = load_data()

    # --- Sidebar Filters ---
    st.sidebar.header("Control Panel")
    player_list = sorted([str(p) for p in df['Players'].unique()])
    selected_player = st.sidebar.selectbox("Select Player", ["All Team"] + player_list)

    # فلترة البيانات
    if selected_player == "All Team":
        filtered_df = df
    else:
        filtered_df = df[df['Players'] == selected_player]

    # --- حساب الإحصائيات التكتيكية (بعد تعريف filtered_df) ---
    # دخول الثلث الأخير (X > 0.66)
    final_third = filtered_df[(filtered_df['X_End'] >= 0.66) & (filtered_df['X_Start'] < 0.66)]
    # دخول الصندوق (X > 0.83 و Y بين 0.22 و 0.78)
    box_entries = filtered_df[
        (filtered_df['X_End'] >= 0.83) & 
        (filtered_df['Y_End'] >= 0.22) & (filtered_df['Y_End'] <= 0.78) &
        (filtered_df['X_Start'] < 0.83)
    ]

    # --- العرض المرئي ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"📍 Action Heatmap: {selected_player}")
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#efefef')
        fig, ax = pitch.draw(figsize=(8, 6))
        if len(filtered_df) > 1:
            sns.kdeplot(x=filtered_df['X_Start']*120, y=filtered_df['Y_Start']*80, 
                        fill=True, thresh=0.05, levels=100, cmap='hot', alpha=0.5, ax=ax)
        st.pyplot(fig)

    with col2:
        st.subheader("🚀 Tactical Metrics")
        st.metric("Final Third Entries", len(final_third))
        st.metric("Penalty Box Entries", len(box_entries))
        st.progress(min(len(box_entries) * 10, 100)) # بار بيوضح الخطورة

    # --- جدول التمريرات ---
    st.divider()
    st.subheader("🔝 Top Action Types")
    st.bar_chart(filtered_df['Event Name'].value_counts().head(10))

except Exception as e:
    st.error(f"Error: {e}")
    st.info("تأكد أن ملف CSV يحتوي على أعمدة: X_Start, Y_Start, X_End, Y_End")
