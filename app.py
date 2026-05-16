import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import matplotlib.lines as mlines
from PIL import Image

# 1. إعدادات الصفحة والتصميم العام (TootScouting Theme)
st.set_page_config(page_title="TootScouting | Tactical Lab", layout="wide")

# تصميم الكارت الاحترافي باستخدام CSS
st.markdown("""
    <style>
    .reportview-container { background: #f8f9fa; }
    .main .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
    
    /* تصميم كارت اللاعب */
    .player-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
        font-family: 'Source Sans Pro', sans-serif;
    }
    .card-header {
        display: flex;
        align-items: center;
        gap: 15px;
        border-bottom: 1px solid #334155;
        padding-bottom: 12px;
        margin-bottom: 15px;
    }
    .player-icon {
        font-size: 40px;
        background: #334155;
        padding: 10px;
        border-radius: 50%;
    }
    .player-info h3 {
        margin: 0;
        color: #f8fafc;
        font-size: 1.4rem;
        font-weight: 700;
    }
    .player-info p {
        margin: 2px 0 0 0;
        color: #94a3b8;
        font-size: 0.9rem;
    }
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        text-align: center;
    }
    .stat-box {
        background: #1e293b;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    .stat-value {
        font-size: 1.2rem;
        font-weight: bold;
        color: #38bdf8;
    }
    .stat-label {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 4px;
    }
    </style>
""", unsafe_allow_html=True)

def add_logo(ax):
    try:
        img = Image.open('image_deac96.png')
        ax.imshow(img, extent=[48, 72, 28, 52], alpha=0.12, zorder=0)
    except:
        pass

st.title("🔬 TootScouting Tactical Dashboard")
st.sidebar.markdown("## 🛠️ Tactical Control Unit")

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

    # فلاتر التحكم التكتيكية في الـ Sidebar
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

    def draw_actions(dataframe, ax, pitch_obj, layers):
        for i, row in dataframe.iterrows():
            act = str(row['Action']).lower()
            tag = str(row['Tags']).lower()
            is_success = 'success' in tag or 'ناجح' in tag
            
            if 'pass' in act or 'تمرير' in act:
                if 'cross' in tag and "Crosses" in layers:
                    pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='blue' if is_success else 'red', linestyle='solid' if is_success else 'dashed', ax=ax)
                elif 'through' in tag and "Through Balls" in layers:
                    pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#FF69B4', ax=ax)
                elif 'corner' in tag and "Corners" in layers:
                    pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='orange' if is_success else 'red', linestyle='solid' if is_success else 'dashed', ax=ax)
                elif "Normal Passes" in layers and not any(k in tag for k in ['cross', 'through', 'corner', 'free kick']):
                    pitch_obj.arrows(row.x_scaled, row.y_scaled, row.x_end_scaled, row.y_end_scaled, width=2, color='#2ecc71' if is_success else '#e74c3c', ax=ax, alpha=0.5)

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

    tab1, tab2 = st.tabs(["👤 Individual Player Lab", "👥 Team Strategy Lab"])

    with tab1:
        player_list = sorted(team_df['Player'].dropna().unique().tolist())
        sel_player = st.selectbox("🎯 Focus Player:", player_list)
        p_df = team_df[team_df['Player'] == sel_player].copy()
        
        # --- حساب الـ Stats تلقائياً للكارت من واقع الداتا ---
        total_passes = len(p_df[p_df['Action'].str.lower().str.contains('pass', na=False)])
        succ_passes = len(p_df[(p_df['Action'].str.lower().str.contains('pass', na=False)) & (p_df['Tags'].str.lower().str.contains('success', na=False))])
        pass_acc = f"{(succ_passes/total_passes)*100:.0f}%" if total_passes > 0 else "0%"
        
        total_tackles = len(p_df[p_df['Action'].str.lower().str.contains('tackle|inter', na=False)])
        total_duels = len(p_df[p_df['Action'].str.lower().str.contains('duel', na=False)])
        
        # --- إنشاء كارت اللاعب بالـ HTML المخصص للمشروع ---
        st.markdown(f"""
            <div class="player-card">
                <div class="card-header">
                    <div class="player-icon">🏃‍♂️</div>
                    <div class="player-info">
                        <h3>{sel_player}</h3>
                        <p>Team: {selected_team} | Tactical Profile</p>
                    </div>
                </div>
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-value">{total_passes}</div>
                        <div class="stat-label">Total Passes</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{pass_acc}</div>
                        <div class="stat-label">Pass Acc.</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{total_tackles}</div>
                        <div class="stat-label">Def. Actions</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#1e293b', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
        fig, ax = pitch.draw(figsize=(12, 8.5))
        add_logo(ax)
        
        draw_actions(p_df, ax, pitch, all_selected_layers)
        ax.legend(handles=get_full_legend(), loc='upper left', bbox_to_anchor=(1.01, 1), fontsize='small', framealpha=1, facecolor='#ffffff')
        st.pyplot(fig)

    with tab2:
        st.subheader(f"Tactical Distribution: {selected_team}")
        pitch_t = Pitch(pitch_type='statsbomb', pitch_color='#ffffff', line_color='#1e293b', linestyle='--', positional=True, positional_color='#e2e8f0', linewidth=1.2)
        fig_t, ax_t = pitch_t.draw(figsize=(12.5, 9))
        add_logo(ax_t)
        
        draw_actions(team_df, ax_t, pitch_t, all_selected_layers)
        ax_t.legend(handles=get_full_legend(), loc='upper left', bbox_to_anchor=(1.01, 1), fontsize='small', framealpha=1, facecolor='#ffffff')
        st.pyplot(fig_t)

else:
    st.info("👋 Welcome to TootScouting Lab! Please upload a match CSV file on the left sidebar to generate the dynamic dashboard.")
