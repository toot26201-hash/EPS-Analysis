import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
from PIL import Image

# 1. إعدادات الصفحة والأسلوب (TootScouting Theme)
st.set_page_config(page_title="TootScouting | Tactical Lab", layout="wide")

# تخصيص واجهة المستخدم لتشبه المواقع الاحترافية
st.markdown("""
    <style>
    .reportview-container { background: #f8f9fa; }
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1 { color: #1e293b; font-weight: 800; font-size: 2.2rem !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f5f9;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 600;
        color: #475569;
    }
    .stTabs [aria-selected="true"] { background-color: #1e293b !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

def add_logo(ax):
    try:
        img = Image.open('image_deac96.png')
        ax.imshow(img, extent=[48, 72, 28, 52], alpha=0.12, zorder=0)
    except:
        pass

st.title("🔬 TootScouting Tactical Dashboard")

# --- الـ Sidebar الجانبي (بنفس فكرة ScoutLab) ---
st.sidebar.image("image_deac96.png", use_container_width=True) if Image.open('image_deac96.png') else st.sidebar.write("⚽ **TootScouting Pro**")
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader("📥 Upload Match CSV Data", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    if 'X start' in df.columns:
        df['x_scaled'] = df['X start'] * 120
        df['y_scaled'] = df['Y start'] * 80
        df['x_end_scaled'] = df['X end'] * 120
        df['y_end_scaled'] = df['Y end'] * 80

    df = df.dropna(subset=['Action', 'Team'])
    team_list = sorted(df['Team'].unique().tolist())
    selected_team = st.sidebar.selectbox("📋 Select Team", team_list)
    team_df = df[df['Team'] == selected_team].copy()

    # فلاتر التحكم التكتيكية في الـ Sidebar (منظمة داخل Expander)
    st.sidebar.markdown("### 🛠️ Tactical Control Unit")
    
    with st.sidebar.expander("🎯 Passing Filters", expanded=True):
        selected_passes = st.multiselect(
            "Choose Pass Types:",
            ["Normal Passes", "Crosses", "Through Balls", "Corners", "Free Kicks"],
            default=["Normal Passes", "Crosses"]
        )
        
    with st.sidebar.expander("🛡️ Defensive & Attack Filters", expanded=True):
        selected_defense = st.multiselect(
            "Choose Actions:",
            ["Tackles", "Clearances", "Ground Duels", "Aerial Duels", "Fouls", "Counterpress", "Goals"],
            default=["Tackles", "Ground Duels", "Goals"]
        )

    all_selected_layers = selected_passes + selected_defense

    # --- دليل الرموز الثابت والمنظم (Legend) ---
    def get_full_legend():
        return [
            mlines.Line2D([], [], color='#2ecc71', marker='>', linestyle='-', label='Pass Success', markersize=8),
            mlines.Line2D([], [], color='#e74c3c', marker='>', linestyle='-', label='Pass Failed', markersize=8),
            mlines.Line2D([], [], color='blue', marker='>', linestyle='-', label='Cross Success', markersize=8),
            mlines.Line2D([], [], color='red', marker='>', linestyle='--', label='Cross Failed', markersize=8),
            mlines.Line2D([], [], color='#FF69B4', marker='>', linestyle='-', label='Through Ball', markersize=8),
            mlines.Line2D([], [], color='blue', marker='x', label='Tackle (Blue X)', linestyle='None', markersize=10, markeredgewidth=2),
            mlines.Line2D([], [], color='purple', marker='d', label='Clearance', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#2ecc71', marker='s', label='Ground Duel Won', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='red', marker='s', label='Ground Duel Lost', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='#2ecc71', marker='^', label='Aerial Won', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='red', marker='^', label='Aerial Lost', linestyle='None', markersize=10),
            mlines.Line2D([], [], color='gold', marker='*', label='Goal', linestyle='None', markersize=12)
        ]

    # --- محرك الرسم التكتيكي ---
    def draw_actions(dataframe, ax, pitch_obj, layers):
        for i, row in dataframe.iterrows():
            act = str(row['Action']).lower()
            tag = str(row['Tags']).lower()
            is_success = 'success' in tag or 'ناجح' in tag
            
            # تمريرات
            if 'pass' in act or 'تمرير' in act:
                if 'cross' in tag and "Crosses" in layers:
                    pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='blue' if is_success else 'red', linestyle='solid' if is_success else 'dashed', ax=ax)
                elif 'through' in tag and "Through Balls" in layers:
                    pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#FF69B4', ax=ax)
                elif 'corner' in tag and "Corners" in layers:
                    pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='orange' if is_success else 'red', linestyle='solid' if is_success else 'dashed', ax=ax)
                elif "Normal Passes" in layers and not any(k in tag for k in ['cross', 'through', 'corner', 'free kick']):
                    pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#2ecc71' if is_success else '#e74c3c', ax=ax, alpha=0.5)

            # دفاعيات
            elif any(word in act for word in ['tackle', 'inter', 'تدخل', 'قطع']) and "Tackles" in layers:
                pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='x', s=220, color='blue', linewidth=2.5, ax=ax)
            elif 'clear' in act and "Clearances" in layers:
                pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='d', s=180, color='purple', ax=ax)
            elif 'aerial' in act and "Aerial Duels" in layers:
                pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='^', s=200, color='#2ecc71' if is_success else 'red', edgecolors='black', ax=ax)
            elif 'duel' in act and 'aerial' not in act and "Ground Duels" in layers:
                pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='s', s=180, color='#2ecc71' if is_success else 'red', ax=ax)
            
            if ('goal' in tag or 'هدف' in tag) and "Goals" in layers:
                pitch_obj.scatter(row.x_scaled, row.y_scaled, marker='*', s=600, color='gold', edgecolors='black', ax=ax, zorder=5)

    # --- التبويبات الرئيسية في الصفحة (Tabs) ---
    tab1, tab2 = st.tabs(["👤 Individual Player Lab", "👥 Team Tactical Lab"])

    with tab1:
        player_list = sorted(team_df['Player'].dropna().unique().tolist())
        sel_player = st.selectbox("🎯 Focus Player:", player_list)
        p_df = team_df[team_df['Player'] == sel_player].copy()
        
        # رسم ملعب الفردي مع الممرات الـ 5 المضيئة خفيف
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#1e293b', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
        fig, ax = pitch.draw(figsize=(12, 8.5))
        add_logo(ax)
        
        draw_actions(p_df, ax, pitch, all_selected_layers)
        ax.legend(handles=get_full_legend(), loc='upper left', bbox_to_anchor=(1.01, 1), fontsize='small', framealpha=1, facecolor='#ffffff')
        st.pyplot(fig)

    with tab2:
        st.subheader(f"Tactical Distribution: {selected_team}")
        
        # رسم ملعب الفريق الجماعي
        pitch_t = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#1e293b', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
        fig_t, ax_t = pitch_t.draw(figsize=(12.5, 9))
        add_logo(ax_t)
        
        draw_actions(team_df, ax_t, pitch_t, all_selected_layers)
        ax_t.legend(handles=get_full_legend(), loc='upper left', bbox_to_anchor=(1.01, 1), fontsize='small', framealpha=1, facecolor='#ffffff')
        st.pyplot(fig_t)

else:
    st.info("👋 Welcome to TootScouting Lab! Please upload a match CSV file on the left sidebar to generate the dynamic dashboard.")
