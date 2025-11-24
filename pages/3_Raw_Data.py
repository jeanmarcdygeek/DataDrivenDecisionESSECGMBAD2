import streamlit as st
import pandas as pd
import geopandas as gpd

st.set_page_config(layout="wide", page_title="Raw Data")

st.title("📊 Raw Data")

st.write("This page displays the raw dataframes used in the dashboard.")

# Load data if not in session state
if "data" not in st.session_state or "customers" not in st.session_state:
    st.info("Loading data... Please go to the Dashboard page first to load the data.")
    
    # Load data
    map_df = gpd.read_file("./arrondissements_municipaux/arrondissements_municipaux-20180711.shp")
    map_df = map_df[map_df['insee'].isin(['75101','75102','75103','75104','75105','75106',
                '75107','75108','75109','75110','75111','75112','75113',
                '75114','75115','75116','75117','75118','75119','75120'])]
    
    city_exposure = pd.read_csv("city_exposure.csv")
    city_exposure["COM"] = city_exposure["COM"].astype(str)
    
    customers = pd.read_csv("customers.csv")
    customers["COM"] = customers["COM"].astype(str)
    
    filosofi_filtered = pd.read_csv("filosofi_filtered.csv")
    filosofi_filtered["insee"] = filosofi_filtered["COM"].astype(str)
    filosofi_filtered = filosofi_filtered.drop(columns=["COM"])
    
    map_data = map_df.merge(city_exposure, left_on="insee", right_on="COM", how="left")
    map_data = map_data.merge(filosofi_filtered, on="insee", how="left")
    
    st.session_state.data = map_data
    st.session_state.customers = customers

# Display Customers Data
st.header("👥 Customers Data")
st.write(f"**Total rows:** {len(st.session_state.customers):,}")
st.write(f"**Columns:** {', '.join(st.session_state.customers.columns.tolist())}")
st.dataframe(st.session_state.customers, use_container_width=True, height=400)

# Display Map Data (without geometry column for display)
st.header("🗺️ Map Data (Geographic + Exposure + Filosofi)")
st.write(f"**Total rows:** {len(st.session_state.data):,}")
st.write(f"**Columns:** {', '.join([col for col in st.session_state.data.columns if col != 'geometry'])}")

# Create a copy without geometry for display
map_data_display = st.session_state.data.drop(columns=['geometry']) if 'geometry' in st.session_state.data.columns else st.session_state.data.copy()
st.dataframe(map_data_display, use_container_width=True, height=400)

# Display City Exposure Data
st.header("🏙️ City Exposure Data")
try:
    city_exposure = pd.read_csv("city_exposure.csv")
    st.write(f"**Total rows:** {len(city_exposure):,}")
    st.write(f"**Columns:** {', '.join(city_exposure.columns.tolist())}")
    st.dataframe(city_exposure, use_container_width=True, height=400)
except Exception as e:
    st.error(f"Error loading city_exposure.csv: {e}")

# Display Filosofi Filtered Data
st.header("💰 Filosofi Filtered Data")
try:
    filosofi_filtered = pd.read_csv("filosofi_filtered.csv")
    st.write(f"**Total rows:** {len(filosofi_filtered):,}")
    st.write(f"**Columns:** {', '.join(filosofi_filtered.columns.tolist())}")
    st.dataframe(filosofi_filtered, use_container_width=True, height=400)
except Exception as e:
    st.error(f"Error loading filosofi_filtered.csv: {e}")

# Data Summary
st.header("📈 Data Summary")
summary_col1, summary_col2 = st.columns(2)

with summary_col1:
    st.subheader("Customers Data Summary")
    st.write(f"- Total customers: {len(st.session_state.customers):,}")
    if 'COM' in st.session_state.customers.columns:
        st.write(f"- Unique arrondissements: {st.session_state.customers['COM'].nunique()}")
    if 'patrimoine' in st.session_state.customers.columns:
        st.write(f"- Total insured amount: €{st.session_state.customers['patrimoine'].sum():,.2f}")
    if 'model_premium' in st.session_state.customers.columns:
        st.write(f"- Total premiums: €{st.session_state.customers['model_premium'].sum():,.2f}")

with summary_col2:
    st.subheader("Map Data Summary")
    st.write(f"- Total geographic features: {len(st.session_state.data):,}")
    if 'insee' in st.session_state.data.columns:
        st.write(f"- Unique arrondissements: {st.session_state.data['insee'].nunique()}")
    if 'patrimoine' in st.session_state.data.columns:
        st.write(f"- Total exposure: €{st.session_state.data['patrimoine'].sum():,.2f}")

