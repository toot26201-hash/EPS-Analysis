import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
from highlight_text import ax_text

st.set_page_config(page_title="EPS Elite Analytics", layout="wide")

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

    # --- القائمة الجانبية ---
    st.sidebar.header("🎨 Analysis Settings")
    selected_player = st.sidebar.selectbox("Select Player", clean_player_list)
    analysis_mode = st.sidebar.radio("View Mode", ["Heatmap", "Final Third Entries"])

    # فلترة بيانات اللاعب
    player_df = df[df['Players'].str.contains(selected_player, na=False)].copy()

    st.title(f"📊 {selected_player} Analysis Report")

    if analysis_mode == "Heatmap":
        # شكل الهيت ماب الاحترافي اللي طلبته
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#777777')
        fig, ax = pitch.draw(figsize=(10, 8))
        fig.set_facecolor('#1a1a1a')

        if not player_df.empty:
            sns.kdeplot(x=player_df['X_Start']*120, y=player_df['Y_Start']*80, 
                        fill=True, thresh=0.05, levels=100, cmap='magma', alpha=0.7, ax=ax)
            
            # إضافة اسم اللاعب داخل الصورة للتحميل
            ax_text(60, -5, f"<{selected_player}>", fontsize=22, color='white', 
                    fontweight='bold', ha='center', ax=ax, highlight_textprops=[{"color": "#ff4b4b"}])
        st.pyplot(fig)

    else:
        # ملعب النجيلة وتحليل التمريرات بالألوان
        st.subheader("🚀 Final Third Entry Passes")
        pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white', stripe=True)
        fig, ax = pitch.draw(figsize=(10, 8))
        
        f3_passes = player_df[(player_df['Event Name'].str.contains('Pass', na=False)) & 
                              (player_df['X_End'] >= 0.66) & (player_df['X_Start'] < 0.66)].copy()

        if not f3_passes.empty:
            # تصنيف وتلوين التمريرات
            for _, row in f3_passes.iterrows():
                # عرضية (من الطرف)
                if row['Y_Start'] < 0.25 or row['Y_Start'] > 0.75:
                    color = "yellow"
                # طولية (مسافة كبيرة)
                elif (row['X_End'] - row['X_Start']) > 0.20:
                    color = "#00bfff"
                # قصيرة
                else:
                    color = "#ff1493"
                
                pitch.arrows(row.X_Start*120, row.Y_Start*80, row.X_End*120, row.Y_End*80, 
                             color=color, ax=ax, width=3, headwidth=8)
            
            st.write("🟡 Yellow: Crosses | 🔵 Blue: Long Vertical | 🔴 Pink: Short Entries")
        st.pyplot(fig)

except Exception as e:
    st.error(f"Error: {e}")
