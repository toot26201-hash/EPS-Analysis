import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mplsoccer import Pitch

st.set_page_config(page_title="EPS Tactical Zones", layout="wide")

@st.cache_data
def load_data():
    try:
        df = pd.read_excel('EPS_Match_Data.xlsx')
        df.columns = df.columns.str.strip()
        for col in ['X_Start', 'Y_Start', 'X_End', 'Y_End']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df.dropna(subset=['X_End', 'Y_End'])
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

df = load_data()
if not df.empty:
    all_names = df['Players'].str.split('|').explode().str.strip()
    selected_player = st.sidebar.selectbox("Select Player", sorted(all_names.unique()))
    p_df = df[df['Players'].str.contains(selected_player, na=False)].copy()

    # --- فلترة المناطق (Zone 14 & Half-spaces) ---
    # بنحول الإحداثيات لمقاس الملعب (120x80) مع ضبط القلبة اللي اتفقنا عليها
    p_df['x_end_plot'] = p_df['Y_End'] * 120
    p_df['y_end_plot'] = p_df['X_Start'] * 80 # تعديل بسيط للواقعية
    
    def classify_zone(x, y):
        if 80 <= x <= 102 and 30 <= y <= 50: return "Zone 14"
        if 80 <= x <= 102 and ((18 <= y <= 30) or (50 <= y <= 62)): return "Half-space"
        return "Other"

    p_df['Target_Zone'] = p_df.apply(lambda r: classify_zone(r['x_end_plot'], r['y_end_plot']), axis=1)
    tactical_passes = p_df[p_df['Target_Zone'] != "Other"].copy()

    st.title(f"🎯 Tactical Entry Map: {selected_player}")
    
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#1e293b', line_color='#777777')
    fig, ax = pitch.draw(figsize=(12, 8))

    # رسم المناطق يدوياً عشان نهرب من الـ AttributeError
    # Zone 14
    ax.add_patch(patches.Rectangle((80, 30), 22, 20, color='red', alpha=0.2, label='Zone 14'))
    # Half-spaces
    ax.add_patch(patches.Rectangle((80, 18), 22, 12, color='blue', alpha=0.1, label='Half-space'))
    ax.add_patch(patches.Rectangle((80, 50), 22, 12, color='blue', alpha=0.1))

    for _, row in tactical_passes.iterrows():
        color = "#ef4444" if row['Target_Zone'] == "Zone 14" else "#38bdf8"
        pitch.arrows(row['Y_Start']*120, row['X_Start']*80, 
                     row['x_end_plot'], row['y_end_plot'], 
                     color=color, ax=ax, width=2, headwidth=4, alpha=0.8)

    st.pyplot(fig)
    st.write("🔴 Zone 14 Entries | 🔵 Half-space Entries")
    st.dataframe(tactical_passes[['Event Name', 'Target_Zone']].head(10))
