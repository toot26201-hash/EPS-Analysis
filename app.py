import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

st.title("🎯 EPS Box Entry Accuracy Check")

@st.cache_data
def load_data():
    df = pd.read_csv('EPS_Match_Data_Clean.csv')
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# فلترة دخول الصندوق
box_entries = df[(df['X_End'] >= 0.83) & (df['Y_End'] >= 0.22) & (df['Y_End'] <= 0.78) & (df['X_Start'] < 0.83)].copy()

# تصنيف شديد الدقة:
# العرضية (Cross) لازم تبدأ من المنطقة الميتة (أطراف الملعب تماماً)
def precise_classification(row):
    if 'Pass' in str(row['Event Name']):
        # لو التمريرة بدأت من برا منطقة الـ 25% يمين أو شمال تبقى عرضية
        if row['Y_Start'] < 0.20 or row['Y_Start'] > 0.80:
            return "Cross 🟡"
        else:
            return "Through Pass / Cut-back 🔵"
    return "Dribble / Carry 🔴"

box_entries['True_Method'] = box_entries.apply(precise_classification, axis=1)

# رسم الخريطة للتأكد بصرياً
pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#efefef')
fig, ax = pitch.draw()
colors = {"Cross 🟡": "yellow", "Through Pass / Cut-back 🔵": "#00bfff", "Dribble / Carry 🔴": "#ff00ff"}

for _, row in box_entries.iterrows():
    pitch.arrows(row.X_Start*120, row.Y_Start*80, row.X_End*120, row.Y_End*80, 
                 color=colors[row['True_Method']], ax=ax, width=3)
st.pyplot(fig)

# الجدول اللي هيحسم الجدل
st.subheader("🧐 مراجعة البيانات (تأكد بنفسك)")
st.write(box_entries[['Players', 'True_Method', 'Y_Start', 'Event Name']])
