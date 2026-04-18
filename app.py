import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
from highlight_text import ax_text

# إعداد الصفحة
st.set_page_config(page_title="EPS Elite Analytics", layout="wide")

@st.cache_data
def load_data():
    # تأكد أن ملفك اسمه EPS_Match_Data.xlsx على GitHub
    try:
        df = pd.read_excel('EPS_Match_Data.xlsx') 
        df.columns = df.columns.str.strip()
        
        # تحويل الإحداثيات لأرقام لضمان الدقة والواقعية
        for col in ['X_Start', 'Y_Start', 'X_End', 'Y_End']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df['Players'] = df['Players'].astype(str).fillna('Unknown')
        return df.dropna(subset=['X_Start', 'Y_Start', 'X_End', 'Y_End'])
    except Exception as e:
        st.error(f"تأكد من رفع ملف الإكسيل باسم EPS_Match_Data.xlsx: {e}")
        return pd.DataFrame()

try:
    df = load_data()

    if not df.empty:
        # --- تنظيف قائمة اللاعبين (إظهار لاعب واحد فقط في كل اختيار) ---
        all_names_series = df['Players'].str.split('|').explode().str.strip()
        clean_player_list = sorted([p for p in all_names_series.unique() if p and p not in ['nan', 'Unknown']])

        # --- القائمة الجانبية ---
        st.sidebar.header("👤 اختيار المحلل")
        selected_player = st.sidebar.selectbox("اختر لاعب واحد من EPS", clean_player_list)
        analysis_type = st.sidebar.radio("نوع التحليل", ["Heatmap (خريطة حرارية)", "Pass Map (خريطة تمريرات)"])

        # فلترة البيانات للاعب المختار فقط
        player_df = df[df['Players'].str.contains(selected_player, na=False)].copy()

        st.title(f"📊 تقرير الأداء: {selected_player}")

        if analysis_type == "Heatmap (خريطة حرارية)":
            # --- الخريطة الحرارية الاحترافية ---
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#777777')
            fig, ax = pitch.draw(figsize=(10, 8))
            fig.set_facecolor('#1a1a1a')

            if not player_df.empty:
                sns.kdeplot(x=player_df['X_Start']*120, y=player_df['Y_Start']*80, 
                            fill=True, thresh=0.05, levels=100, cmap='magma', alpha=0.7, ax=ax)
                
                # كتابة اسم اللاعب داخل الصورة
                ax_text(60, -5, f"<{selected_player}> | <EPS Heatmap>", fontsize=22, 
                        color='white', fontweight='bold', ha='center', ax=ax, 
                        highlight_textprops=[{"color": "#ff4b4b"}])
            st.pyplot(fig)

        else:
            # --- خريطة التمريرات الواقعية ---
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc',
                          linestyle='--', linewidth=1, goal_linestyle='-')
            fig, ax = pitch.draw(figsize=(10, 8))
            fig.set_facecolor('#22312b')

            passes = player_df[player_df['Event Name'].str.contains('Pass', na=False)].copy()

            if not passes.empty:
                for _, row in passes.iterrows():
                    x_s, y_s = row['X_Start'] * 120, row['Y_Start'] * 80
                    x_e, y_e = row['X_End'] * 120, row['Y_End'] * 80
                    
                    # فلترة التمريرات الوهمية (المسافات القصيرة جداً)
                    if ((x_e-x_s)**2 + (y_e-y_s)**2)**0.5 < 3: continue

                    # تلوين تكتيكي: عرضية (أصفر) | طولية (أزرق) | قصيرة (أحمر)
                    if y_s < 20 or y_s > 60: color = "yellow"
                    elif (x_e - x_s) > 25: color = "#00bfff"
                    else: color = "#ff4b4b"

                    pitch.arrows(x_s, y_s, x_e, y_e, color=color, ax=ax, 
                                 width=1.2, headwidth=3, alpha=0.6)

                ax_text(60, -5, f"<{selected_player}> | <EPS Pass Map>", fontsize=22, 
                        color='white', fontweight='bold', ha='center', ax=ax,
                        highlight_textprops=[{"color": "#00bfff"}])
                
            st.pyplot(fig)
            st.write("🟡 عرضيات | 🔵 تمريرات تقدمية | 🔴 تمريرات قصيرة")

except Exception as e:
    st.error(f"حدث خطأ: {e}")
