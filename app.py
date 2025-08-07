import streamlit as st
import pandas as pd
import numpy as np
import os

# --- CONFIG ---
st.set_page_config(
    page_title="🌍 IMF WEO Economic Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- LOAD DATA ---
df = pd.read_csv("cleaned_WEO_data_FINAL.csv")

# --- SIDEBAR FILTERS ---
with st.sidebar:
    # Safely display the image
    img_path = os.path.join("images", "logo.png")
    if os.path.exists(img_path):
        st.image(img_path, width=120)

    st.title("🌍 Filter Options")

    countries = sorted(df['country_clean'].dropna().unique())
    selected_country = st.selectbox("Select a Country", countries, index=countries.index("Liberia") if "Liberia" in countries else 0)

    indicators = df[df['country_clean'] == selected_country]['indicator'].dropna().unique()
    if len(indicators) == 0:
        st.error("No indicators found for selected country.")
        st.stop()
    selected_indicator = st.selectbox("Select an Indicator", sorted(indicators))

    # Year slider
    year_min, year_max = int(df['year'].min()), int(df['year'].max())
    selected_years = st.slider("Select Year Range", year_min, year_max, (2000, year_max))

# --- FILTER DATA ---
filtered = df[
    (df['country_clean'] == selected_country) &
    (df['indicator'] == selected_indicator) &
    (df['year'].between(*selected_years))
].copy()

if filtered.empty:
    st.warning("No data available for this selection.")
    st.stop()

# --- KPI METRICS ---
latest = filtered.sort_values("year").iloc[-1]
prev = filtered.sort_values("year").iloc[-2] if len(filtered) > 1 else latest

col1, col2, col3 = st.columns(3)
col1.metric("📍 Latest Value", f"{latest['value_scaled']:.2f} {latest['unit']}")
col2.metric("📊 YoY Change", f"{latest['value_diff']:.2f}", delta=f"{latest['value_pct_diff']*100:.2f}%", delta_color="inverse")
col3.metric("🔮 Forecast?", "Yes" if latest["is_forecast"] == 1 else "No")

# --- CHART DISPLAY ---
st.subheader(f"📈 {selected_indicator} in {selected_country}")
chart_type = st.radio("Choose Chart Type:", ["Line Chart", "Area Chart"], horizontal=True)

chart_data = filtered.set_index("year")["value_scaled"]

if chart_data.empty:
    st.warning("No chart data available.")
else:
    if chart_type == "Line Chart":
        st.line_chart(chart_data)
    else:
        st.area_chart(chart_data)

# --- RAW DATA ---
with st.expander("📄 View Filtered Data"):
    st.dataframe(filtered[['year', 'value_scaled', 'unit', 'source', 'is_forecast']])

    # Download filtered data
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=csv,
        file_name=f"{selected_country}_{selected_indicator}_WEO.csv",
        mime="text/csv"
    )

# --- Indicator Details ---
with st.expander("📊 Indicator Details"):
    st.markdown(f"**Source:** {latest['source']}")
    st.markdown(f"**Group:** {latest['indicator_group']}")
    st.markdown(f"**Transformation:** {latest['transformation']} | **Derivation:** {latest['derivation_type']}")
