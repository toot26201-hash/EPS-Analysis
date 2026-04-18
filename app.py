import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
from highlight_text import ax_text

st.set_page_config(page_title="EPS Player Pass Maps", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('EPS_Match_Data_Clean.csv')
    df.columns = df.columns.str.strip()
    df['Players'] = df['Players'].astype(str).fillna('Unknown')
    return df

try:
    df = load_data()
    
    # تنظيف الأسماء وفك التمريرات المركبة (حسب الصور السابقة)
    all_names_raw = df['Players'].str.split('|').explode().str.strip()
    clean_player_list = sorted([p for p in all_names_raw.unique() if p and p not in ['nan', 'Unknown']])

    st.sidebar.header("📋 إعدادات الخريطة")
    selected_player = st.sidebar.selectbox("اختر اللاعب", clean_player_list)

    # فلترة التمريرات فقط للاعب المختار
    player_passes = df[
        (df['Players'].str.contains(selected_player, na=False)) & 
        (df['Event Name'].str.contains('Pass', na=False, case=False))
    ].copy()

    st.title(f"📍 Pass Map: {selected_player}")

    # --- إعداد الملعب حسب طلبك بالظبط ---
    pitch = Pitch(
        pitch_type='statsbomb', 
        pitch_color='#22312b', 
        line_color='#c7d5cc',
        linestyle='--', 
        linewidth=1, 
        goal_linestyle='-'
    )
    fig, ax = pitch.draw(figsize=(12, 9))
    fig.set_facecolor('#22312b')

    if not player_passes.empty:
        # تصنيف التمريرات للتلوين
        def get_color(row):
            # عرضية: تبدأ من الأطراف
            if row['Y_Start'] < 0.20 or row['Y_Start'] > 0.80:
                return "yellow"
            # طولية: مسافة التقدم في الملعب كبيرة
            elif (row['X_End'] - row['X_Start']) > 0.30:
                return "#00bfff" # أزرق سماوي
            # تمريرة عادية
            else:
                return "#ff4b4b" # أحمر

        for _, row in player_passes.iterrows():
            color = get_color(row)
            pitch.arrows(
                row.X_Start*120, row.Y_Start*80, 
                row.X_End*120, row.Y_End*80, 
                color=color, ax=ax, width=2, headwidth=5, alpha=0.7
            )

        # إضافة اسم اللاعب وعنوان الخريطة داخل الصورة
        ax_text(60, -5, f"<{selected_player}> | <Pass Map Analysis>", 
                fontsize=20, color='white', fontweight='bold', ha='center', ax=ax,
                highlight_textprops=[{"color": "#00bfff"}, {"color": "yellow"}])
        
        st.pyplot(fig)
        
        # مفتاح الألوان
        st.write("🟡 **Yellow:** Crosses | 🔵 **Blue:** Long/Vertical Passes | 🔴 **Red:** Short/Other Passes")
    else:
        st.warning(f"لا توجد بيانات تمريرات مسجلة للاعب {selected_player} في هذا الملف.")

except Exception as e:
    st.error(f"حدث خطأ أثناء التشغيل: {e}")
