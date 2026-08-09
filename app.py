import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
from mplsoccer import Pitch

# 1. Basic Page Configurations
st.set_page_config(
    page_title="TootScouting - Performance Lab",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ TootScouting - Performance Lab")
st.write("---")

# 2. Sidebar Controls - Data Loading
st.sidebar.header("📁 DATA LOADING")
uploaded_file = st.sidebar.file_uploader("Upload Match Data (Excel or CSV)", type=["csv", "xlsx"])

# Default pitch layout initialization
pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#7c7c7c')

# 3. Data Processing Pipeline
if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        try:
            xls = pd.ExcelFile(uploaded_file, engine='openpyxl')
            sheet_to_read = xls.sheet_names[0]
            for sheet in xls.sheet_names:
                if any(k in sheet.lower() for k in ['action', 'event', 'حدث', 'كل', 'data', 'events']):
                    sheet_to_read = sheet
                    break
            df = pd.read_excel(uploaded_file, sheet_name=sheet_to_read, engine='openpyxl')
        except:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            
    df.columns = df.columns.astype(str).str.strip()
    
    # 🚨 Extract actual text Action column
    act_series = None
    for col in df.columns:
        c_clean = col.lower().strip()
        if c_clean in ['action', 'الأكشن', 'حدث', 'event', 'event type'] or (c_clean.startswith('action') and not c_clean.endswith('name')):
            col_data = df[col]
            if isinstance(col_data, pd.DataFrame):
                col_data = col_data.iloc[:, 0]
            if not pd.to_numeric(col_data, errors='coerce').notna().all():
                act_series = col_data
                break
                
    if act_series is None:
        for col in df.columns:
            if col.strip() not in ['#', 'id', 'ID', 'no', 'No']:
                col_data = df[col]
                if col_data.dtype == 'object' and not pd.to_numeric(col_data, errors='coerce').notna().all():
                    act_series = col_data
                    break

    if act_series is not None:
        df['Action_Clean'] = act_series.fillna('Other').astype(str).str.strip()
    else:
        df['Action_Clean'] = 'Other'

    # Smart prioritization mapping for coordinate columns
    rename_dict = {}
    for col in df.columns:
        c_low = col.lower().strip()
        if 'start x (0-1)' in c_low or 'x start (0-1)' in c_low or c_low == 'x1': rename_dict[col] = 'x1'
        elif 'start y (0-1)' in c_low or 'y start (0-1)' in c_low or c_low == 'y1': rename_dict[col] = 'y1'
        elif 'end x (0-1)' in c_low or 'x end (0-1)' in c_low or c_low == 'x2': rename_dict[col] = 'x2'
        elif 'end y (0-1)' in c_low or 'y end (0-1)' in c_low or c_low == 'y2': rename_dict[col] = 'y2'
        
        elif 'x1' not in rename_dict.values() and any(k == c_low or k in c_low for k in ['x start', 'x_start', 'start x', 'pos x', 'x_coord']): rename_dict[col] = 'x1'
        elif 'y1' not in rename_dict.values() and any(k == c_low or k in c_low for k in ['y start', 'y_start', 'start y', 'pos y', 'y_coord']): rename_dict[col] = 'y1'
        elif 'x2' not in rename_dict.values() and any(k == c_low or k in c_low for k in ['x end', 'x_end', 'end x', 'pos x2', 'x_end_coord']): rename_dict[col] = 'x2'
        elif 'y2' not in rename_dict.values() and any(k == c_low or k in c_low for k in ['y end', 'y_end', 'end y', 'pos y2', 'y_end_coord']): rename_dict[col] = 'y2'
        
        elif c_low in ['player', 'اللاعب', 'لاعب', 'player name', 'name']: rename_dict[col] = 'Player'

    df = df.rename(columns=rename_dict)

    if 'x1' in df.columns and 'y1' in df.columns:
        st.sidebar.success("Data loaded successfully!")
        
        for col in ['x1', 'y1', 'x2', 'y2']:
            if col in df.columns:
                if isinstance(df[col], pd.DataFrame):
                    df[col] = df[col].iloc[:, 0]
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Advanced Smart Scaling
        if df['x1'].max() <= 1.0 and df['y1'].max() <= 1.0:
            df['x_scaled'] = df['x1'] * 120
            df['y_scaled'] = df['y1'] * 80
            df['x2_scaled'] = df['x2'] * 120 if 'x2' in df.columns else np.nan
            df['y2_scaled'] = df['y2'] * 80 if 'y2' in df.columns else np.nan
        else:
            df['x_scaled'], df['y_scaled'] = df['x1'], df['y1']
            df['x2_scaled'] = df['x2'] if 'x2' in df.columns else np.nan
            df['y2_scaled'] = df['y2'] if 'y2' in df.columns else np.nan

        # Clean numbers out of string actions
        def classify_action(val):
            v = str(val).lower().strip()
            v_alpha = ''.join([i for i in v if not i.isdigit()]).strip()
            
            if any(k in v_alpha for k in ['pass', 'تمرير', 'p/a', 'pas', 'cross', 'عرضية', 'corner', 'throw', 'progressive run']): return "Pass"
            if any(k in v_alpha for k in ['shot', 'sh/a', 'تسديد', 'sh', 'so', 'goal', 'هدف']): return "Shot"
            if any(k in v_alpha for k in ['tackle', 'تدخل', 'pressing', 'counter pressing', 'ضغط', 'counter', 'press', 'tck', 'challenge']): return "Defensive Action"
            if any(k in v_alpha for k in ['clearance', 'تشتيت', 'تخليص', 'clr', 'clear']): return "Clearance"
            if any(k in v_alpha for k in ['extraction', 'interception', 'قطع', 'intercept', 'int', 'recovery', 'استعادة']): return "Interception"
            if any(k in v_alpha for k in ['aerial', 'هوائي', 'air', 'head duel', 'كرة هوائية']): return "Aerial Duel"
            if any(k in v_alpha for k in ['ground', 'أرضي', 'duel', 'صراع', '1v1']): return "Ground Duel"
            if any(k in v_alpha for k in ['dribble', 'مراوغة', 'takeon', 'take on', 'ترقيص', 'drb']): return "Dribble"
            if any(k in v_alpha for k in ['miscontrol', 'فقد', 'lost', 'turnover', 'bad touch']): return "Miscontrol"
            if any(k in v_alpha for k in ['foul', 'fouls', 'خطأ', 'fouled', 'yellow', 'card']): return "Foul"
            if any(k in v_alpha for k in ['kick-off', 'بداية', 'kick off']): return "Kick-off"
            
            cleaned_title = ''.join([i for i in str(val) if not i.isdigit()]).strip().title()
            return cleaned_title if len(cleaned_title) > 0 and cleaned_title.lower() != 'other' else "Other Actions"

        df['Event_Type'] = df['Action_Clean'].apply(classify_action)

        # 4. Interactive Filtration Interface
        st.sidebar.write("---")
        st.sidebar.header("🔍 PITCH VISUAL FILTERS")
        
        map_type = st.sidebar.radio("Select Display Type:", ["Event Map", "Heatmap"])
        
        if 'Player' in df.columns:
            if isinstance(df['Player'], pd.DataFrame):
                df['Player'] = df['Player'].iloc[:, 0]
            players = ["All Players (Team)"] + sorted(df['Player'].dropna().astype(str).unique().tolist())
        else:
            players = ["All Players (Team)"]
            
        selected_player = st.sidebar.selectbox("Select Player or Squad:", players)
        
        available_events = sorted(df['Event_Type'].unique().tolist())
        selected_events = st.sidebar.multiselect("Select Actions to Include:", options=available_events, default=available_events)
        
        # Option to toggle arrows or dots for passes to prevent screen clutter
        draw_pass_arrows = st.sidebar.checkbox("Show Pass Arrows (Disable for cleaner Team view)", value=(selected_player != "All Players (Team)"))

        filtered_df = df
        if selected_player != "All Players (Team)" and 'Player' in df.columns:
            filtered_df = df[df['Player'].astype(str) == selected_player]
            
        filtered_df = filtered_df[filtered_df['Event_Type'].isin(selected_events)].dropna(subset=['x_scaled', 'y_scaled'])
        
        st.write("---")
        st.subheader(f"📊 Dashboard Presentation: {map_type}")

        col_stats, col_pitch = st.columns([1, 2.5])

        with col_stats:
            st.markdown("### 📈 Tactical Analytics")
            st.metric(label="Total Filtered Events", value=len(filtered_df))
            st.write("---")
            if not filtered_df.empty:
                st.markdown("**Event Distribution:**")
                event_counts = filtered_df['Event_Type'].value_counts()
                st.write(event_counts)

        with col_pitch:
            fig, ax = plt.subplots(figsize=(12, 10))
            pitch.draw(ax=ax)
            fig.patch.set_facecolor('#1a1a1a')
            
            display_title = "TEAM HEATMAP" if selected_player == "All Players (Team)" else f"{selected_player.upper()} - HEATMAP"
            if map_type == "Event Map":
                display_title = display_title.replace("HEATMAP", "EVENT MAP")
                
            ax.set_title(display_title, color='#D4AF37', fontsize=24, fontweight='bold', pad=20, ha='center')

            # 🔘 Visual State One: Heatmap Rendering Mode
            if map_type == "Heatmap":
                if len(filtered_df) > 2:
                    sns.kdeplot(
                        x=filtered_df['x_scaled'], 
                        y=filtered_df['y_scaled'], 
                        ax=ax, 
                        fill=True, 
                        cmap="hot", 
                        alpha=0.6, 
                        thresh=0.05, 
                        levels=100,
                        zorder=2
                    )
                else:
                    st.warning("⚠️ Insufficient data coordinates available to calculate a kernel density model.")
            
            # 🔘 Visual State Two: Event Map Mode
            else:
                event_configs = {
                    "Pass": {"color": "#00ffcc", "marker": "o"},
                    "Shot": {"color": "#00ff00", "marker": "*"},
                    "Defensive Action": {"color": "#ff00ff", "marker": "X"},
                    "Interception": {"color": "#FFFF00", "marker": "o"},
                    "Clearance": {"color": "#ffffff", "marker": "s"},
                    "Aerial Duel": {"color": "#3399ff", "marker": "^"},
                    "Ground Duel": {"color": "#8B4513", "marker": "v"},
                    "Dribble": {"color": "#ff9900", "marker": "P"},
                    "Miscontrol": {"color": "#ff3333", "marker": "h"},
                    "Foul": {"color": "#ccff00", "marker": "d"},
                    "Kick-off": {"color": "#9933ff", "marker": "p"}
                }

                legend_elements = []
                for event in selected_events:
                    cfg = event_configs.get(event, {"color": "#e6b800", "marker": "o"})
                    subset = filtered_df[filtered_df['Event_Type'] == event]
                    
                    if subset.empty: continue
                    
                    if event == "Pass" and draw_pass_arrows:
                        arrow_df = subset.dropna(subset=['x2_scaled', 'y2_scaled'])
                        if not arrow_df.empty:
                            pitch.arrows(arrow_df['x_scaled'], arrow_df['y_scaled'], 
                                         arrow_df['x2_scaled'], arrow_df['y2_scaled'], 
                                         color=cfg['color'], width=1.5, headwidth=3, ax=ax, zorder=3, alpha=0.6)
                            legend_elements.append(Line2D([0], [0], color=cfg['color'], lw=2, label=event))
                    else:
                        pitch.scatter(subset['x_scaled'], subset['y_scaled'], 
                                      color=cfg['color'], marker=cfg['marker'], s=100, ax=ax, zorder=3, alpha=0.8)
                        legend_elements.append(Line2D([0], [0], marker=cfg['marker'], color='none', 
                                                      markerfacecolor=cfg['color'], markeredgecolor=cfg['color'], 
                                                      label=event, markersize=8))

                if legend_elements:
                    ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), 
                              ncol=4, facecolor='#222222', labelcolor='white', fontsize=11)
            
            st.pyplot(fig)
            plt.close(fig)
        
        # 6. Detailed Data Table Feed
        st.write("---")
        st.subheader("📋 Filtered Dataset Record Stream")
        team_col = 'Player Team' if 'Player Team' in df.columns else ('Team' if 'Team' in df.columns else ('Team Tag' if 'Team Tag' in df.columns else 'Action_Clean'))
        start_col = 'Start' if 'Start' in df.columns else ('Time' if 'Time' in df.columns else ('Start (mm:ss)' if 'Start (mm:ss)' in df.columns else 'Action_Clean'))
        
        show_cols = ['Action_Clean', 'Event_Type', 'Player']
        if team_col in df.columns: show_cols.append(team_col)
        if start_col in df.columns: show_cols.append(start_col)
        
        st.dataframe(filtered_df[show_cols].reset_index(drop=True), use_container_width=True)
        
    else:
        st.error("⚠️ Spatial Matrix Error: Unable to detect structural x1/y1 spatial data column names.")
else:
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch.draw(ax=ax)
    fig.patch.set_facecolor('#1a1a1a')
    st.pyplot(fig)
    plt.close(fig)
    st.info("💡 Laboratory Environment Idle. Awaiting performance coordinate uploads from the sidebar controller.")
