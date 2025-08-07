import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURATION ---
st.set_page_config(
    page_title="🌍 IMF WEO Economic Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- LOAD DATA ---
df = pd.read_csv(
    r"C:\Users\postgres\database\Data_World\Database_ET\WEO_IMF_Data\cleaned_WEO_data_FINAL.csv"
)

# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/IMF_logo.svg/1200px-IMF_logo.svg.png", width=120)
    st.title("🌍 Filter Options")
    
    countries = sorted(df['country_clean'].dropna().unique())
    selected_country = st.selectbox("Select a Country", countries, index=countries.index("Liberia") if "Liberia" in countries else 0)

    indicators = df[df['country_clean'] == selected_country]['indicator'].unique()
    selected_indicator = st.selectbox("Select an Indicator", sorted(indicators))

    # Optional year range filter
    year_min, year_max = int(df['year'].min()), int(df['year'].max())
    selected_years = st.slider("Select Year Range", year_min, year_max, (2000, year_max))

# --- FILTER DATA ---
filtered = df[
    (df['country_clean'] == selected_country) &
    (df['indicator'] == selected_indicator) &
    (df['year'].between(*selected_years))
].copy()

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

if chart_type == "Line Chart":
    st.line_chart(chart_data)
else:
    st.area_chart(chart_data)

# --- RAW DATA VIEW ---
with st.expander("📄 View Filtered Data"):
    st.dataframe(filtered[['year', 'value_scaled', 'unit', 'source', 'is_forecast']])

    # Download button
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=csv,
        file_name=f"{selected_country}_{selected_indicator}_WEO.csv",
        mime="text/csv"
    )

# --- OPTIONAL: Indicator Group Summary (Bottom)
with st.expander("📊 Indicator Details"):
    st.markdown(f"**Source:** {latest['source']}")
    st.markdown(f"**Group:** {latest['indicator_group']}")
    st.markdown(f"**Transformation:** {latest['transformation']} | **Derivation:** {latest['derivation_type']}")
