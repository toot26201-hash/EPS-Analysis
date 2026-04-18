# --- حساب إحصائيات متقدمة ---
# 1. التمريرات داخل الثلث الأخير (Final Third Entries)
final_third_entries = filtered_df[
    (filtered_df['Event Name'].str.contains('Pass', na=False)) & 
    (filtered_df['X_Start'] < 0.66) & 
    (filtered_df['X_End'] >= 0.66)
]

# 2. دخول منطقة الجزاء (Penalty Box Entries)
# الصندوق بيبدأ تقريباً من X=0.83 ومن Y=0.22 لـ Y=0.78
box_entries = filtered_df[
    (filtered_df['X_End'] >= 0.83) & 
    (filtered_df['Y_End'] >= 0.22) & 
    (filtered_df['Y_End'] <= 0.78) &
    (filtered_df['X_Start'] < 0.83) # عشان نضمن إنه دخل الصندوق مش كان جواه
]

# --- عرض الإحصائيات الجديدة في الداشبورد ---
st.divider()
st.subheader("🚀 Advanced Tactical Metrics")
m1, m2, m3 = st.columns(3)

with m1:
    st.metric("Final Third Entries", len(final_third_entries))
    st.caption("الكرة انتقلت من وسط الملعب للثلث الأخير")

with m2:
    st.metric("Penalty Box Entries", len(box_entries))
    st.caption("دخول منطقة جزاء الخصم")

with m3:
    # نسبة نجاح التمريرات (لو عندك عمود للحالة)
    st.metric("Progressive Actions", len(final_third_entries) + len(box_entries))
