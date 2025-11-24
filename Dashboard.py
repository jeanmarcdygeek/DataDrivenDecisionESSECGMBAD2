import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Dashboard - Insurance Pricing")

METRIC_COLUMNS = {
    "Ensured Amount": "patrimoine",
    "Model Premium": "model_premium",
    "Median Revenues": "DISP_MED18",
    "Census": "index"
}

if "data" not in st.session_state or "customers" not in st.session_state:
    map_df = gpd.read_file("./arrondissements_municipaux/arrondissements_municipaux-20180711.shp")
    map_df = map_df[map_df['insee'].isin(['75101','75102','75103','75104','75105','75106',
                '75107','75108','75109','75110','75111','75112','75113',
                '75114','75115','75116','75117','75118','75119','75120'])]
    

    city_exposure = pd.read_csv("city_exposure.csv")
    city_exposure["COM"] = city_exposure["COM"].astype(str)

    customers = pd.read_csv("customers.csv")
    customers["COM"] = customers["COM"].astype(str)  # Ensure COM is string for matching
    st.session_state.customers = customers
    
    filosofi_filtered = pd.read_csv("filosofi_filtered.csv")
    filosofi_filtered["insee"] = filosofi_filtered["COM"].astype(str)
    filosofi_filtered = filosofi_filtered.drop(columns=["COM"])

    map_data = map_df.merge(city_exposure, left_on="insee", right_on="COM", how="left")
    map_data = map_data.merge(filosofi_filtered, on="insee", how="left")

    st.session_state.data = map_data


st.title("Insurance Policy Increase")
st.write("This is a dashboard to analyze the insurance policy increase in Paris.")

# Initialize allocation state
if "target_profit_costs" not in st.session_state:
    st.session_state.target_profit_costs = 2000000.0  # Default target: 2 million euros
if "allocation_dict" not in st.session_state:
    st.session_state.allocation_dict = {}

metric = st.selectbox("Select the metric to display", list(METRIC_COLUMNS.keys()))

# Create two columns for table and map
col1, col2 = st.columns(2)

with col1:
    st.subheader("Selected Metrics by Arrondissement")
    # Create a summary table with metrics by arrondissement
    summary_data = st.session_state.data.groupby(['insee', 'nom']).agg({
        'patrimoine': 'sum',
        'model_premium': 'mean',
        'DISP_MED18': 'mean',
        'index': 'sum'
    }).reset_index()
    summary_data.columns = ['Arrondissement Code', 'Arrondissement', 'Ensured Amount', 
                           'Model Premium', 'Median Revenues', 'Census']
    summary_data = summary_data.round(2)
    st.dataframe(summary_data, use_container_width=True, hide_index=True)

with col2:
    st.subheader("Map Visualization")
    fig = px.choropleth(st.session_state.data, geojson=st.session_state.data.geometry, 
                       locations=st.session_state.data.index, 
                       color=METRIC_COLUMNS[metric], 
                       projection="mercator",
                       labels={METRIC_COLUMNS[metric]: metric})
    fig.update_geos(fitbounds="locations", visible=True)
    st.plotly_chart(fig, use_container_width=True)

# Customer characteristics section
st.subheader("Customer Characteristics")
customer_cols = st.columns(4)

with customer_cols[0]:
    st.metric("Total Customers", f"{len(st.session_state.customers):,}")

with customer_cols[1]:
    avg_patrimoine = st.session_state.customers['patrimoine'].mean()
    st.metric("Average Ensured Amount", f"€{avg_patrimoine:,.2f}")

with customer_cols[2]:
    avg_premium = st.session_state.customers['model_premium'].mean()
    st.metric("Average Model Premium", f"€{avg_premium:,.2f}")

with customer_cols[3]:
    total_patrimoine = st.session_state.customers['patrimoine'].sum()
    st.metric("Total Ensured Amount", f"€{total_patrimoine:,.0f}")

# Portfolio metrics section
st.subheader("Portfolio Metrics")
portfolio_cols = st.columns(4)

# Calculate portfolio-level metrics
total_expected_loss = (st.session_state.customers['patrimoine'] * st.session_state.customers['prob']).sum()
total_premium = st.session_state.customers['model_premium'].sum()
avg_prob = st.session_state.customers['prob'].mean()
total_census = st.session_state.data['index'].sum() if 'index' in st.session_state.data.columns else 0

with portfolio_cols[0]:
    st.metric("Total Expected Loss", f"€{total_expected_loss:,.2f}")

with portfolio_cols[1]:
    st.metric("Total Premium", f"€{total_premium:,.2f}")

with portfolio_cols[2]:
    st.metric("Average Probability", f"{avg_prob:.4f}")

with portfolio_cols[3]:
    st.metric("Total Census", f"{total_census:,}")

# Additional customer distribution by arrondissement
st.subheader("Customer Distribution by Arrondissement")
if 'COM' in st.session_state.customers.columns:
    customer_dist = st.session_state.customers.groupby('COM').agg({
        'patrimoine': ['count', 'sum', 'mean'],
        'model_premium': 'mean'
    }).reset_index()
    customer_dist.columns = ['Arrondissement', 'Number of Customers', 'Total Ensured Amount', 
                            'Avg Ensured Amount', 'Avg Premium']
    customer_dist = customer_dist.sort_values('Number of Customers', ascending=False)
    st.dataframe(customer_dist, use_container_width=True, hide_index=True)

# Pricing Allocation Section
st.markdown("---")
st.header("💰 Pricing Allocation")

# Get arrondissement list from data
arrondissements = st.session_state.data.groupby(['insee', 'nom']).first().reset_index()[['insee', 'nom']].sort_values('insee')
# Ensure insee codes are strings for consistent matching
arrondissements['insee'] = arrondissements['insee'].astype(str)
arrondissements_list = arrondissements['insee'].tolist()
arrondissements_names = dict(zip(arrondissements['insee'], arrondissements['nom']))

# Target display (fixed, not modifiable)
target = st.session_state.target_profit_costs  # Fixed at 2 million euros

col_target1, col_target2 = st.columns([2, 1])
with col_target1:
    st.metric(
        "Target Profit + Operating Costs (€)",
        f"€{target:,.2f}",
        help="Fixed target for the entire portfolio: €2,000,000"
    )
    st.caption("⚠️ This target is fixed and cannot be modified")

with col_target2:
    st.write("")
    st.write("")
    current_total_premium = st.session_state.customers['model_premium'].sum()
    current_expected_loss = (st.session_state.customers['patrimoine'] * st.session_state.customers['prob']).sum()
    current_profit = current_total_premium - current_expected_loss
    st.metric("Current Profit", f"€{current_profit:,.2f}")

# Allocation method selection
allocation_method = st.radio(
    "Allocation Method",
    ["Manual Entry", "Proportional to Exposure", "Proportional to Risk", "Equal Distribution"],
    horizontal=True
)

# Calculate allocation based on method
if allocation_method == "Equal Distribution":
    num_arr = len(arrondissements_list)
    equal_amount = target / num_arr if num_arr > 0 else 0
    for arr in arrondissements_list:
        st.session_state.allocation_dict[arr] = equal_amount
    # Display the calculated allocations
    st.info(f"✅ Allocated equally across {num_arr} arrondissements. Each receives: €{equal_amount:,.2f}")
elif allocation_method == "Proportional to Exposure":
    # Calculate total exposure by arrondissement
    exposure_by_arr = st.session_state.customers.groupby('COM').agg({'patrimoine': 'sum'}).reset_index()
    total_exposure = exposure_by_arr['patrimoine'].sum()
    if total_exposure > 0:
        for arr in arrondissements_list:
            arr_str = str(arr)
            exposure_match = exposure_by_arr[exposure_by_arr['COM'].astype(str) == arr_str]['patrimoine']
            exposure = exposure_match.values[0] if len(exposure_match) > 0 else 0
            st.session_state.allocation_dict[arr] = (exposure / total_exposure) * target
    else:
        for arr in arrondissements_list:
            st.session_state.allocation_dict[arr] = 0
    # Display the calculated allocations
    st.info(f"✅ Allocated proportionally based on insured amounts (exposure). Total exposure: €{total_exposure:,.2f}")
elif allocation_method == "Proportional to Risk":
    # Calculate total expected loss by arrondissement
    st.session_state.customers['expected_loss'] = st.session_state.customers['patrimoine'] * st.session_state.customers['prob']
    risk_by_arr = st.session_state.customers.groupby('COM').agg({'expected_loss': 'sum'}).reset_index()
    total_risk = risk_by_arr['expected_loss'].sum()
    if total_risk > 0:
        for arr in arrondissements_list:
            arr_str = str(arr)
            risk_match = risk_by_arr[risk_by_arr['COM'].astype(str) == arr_str]['expected_loss']
            risk = risk_match.values[0] if len(risk_match) > 0 else 0
            st.session_state.allocation_dict[arr] = (risk / total_risk) * target
    else:
        for arr in arrondissements_list:
            st.session_state.allocation_dict[arr] = 0
    # Display the calculated allocations
    st.info(f"✅ Allocated proportionally based on expected losses (risk). Total expected loss: €{total_risk:,.2f}")

# Display calculated allocations in a table for all methods
if allocation_method != "Manual Entry":
    st.subheader("Calculated Allocations")
    alloc_display_list = []
    for arr in arrondissements_list:
        alloc_display_list.append({
            'Arrondissement Code': arr,
            'Arrondissement': arrondissements_names.get(arr, f"Arr {arr}"),
            'Allocation (€)': st.session_state.allocation_dict.get(arr, 0.0)
        })
    alloc_display_df = pd.DataFrame(alloc_display_list)
    alloc_display_df = alloc_display_df.round(2)
    st.dataframe(alloc_display_df, use_container_width=True, hide_index=True)

# Manual entry interface
if allocation_method == "Manual Entry" or st.checkbox("Adjust allocations manually"):
    st.subheader("Allocate Target Across Arrondissements")
    
    # Create columns for input
    num_cols = 4
    cols = st.columns(num_cols)
    
    for idx, arr in enumerate(arrondissements_list):
        col_idx = idx % num_cols
        with cols[col_idx]:
            arr_name = arrondissements_names.get(arr, f"Arr {arr}")
            current_val = st.session_state.allocation_dict.get(arr, 0.0)
            new_val = st.number_input(
                f"{arr_name} ({arr})",
                min_value=0.0,
                value=float(current_val),
                step=1000.0,
                format="%.2f",
                key=f"alloc_{arr}"
            )
            st.session_state.allocation_dict[arr] = new_val

# Calculate total allocation
total_allocated = sum(st.session_state.allocation_dict.values())
allocation_diff = target - total_allocated

# Display allocation summary
alloc_col1, alloc_col2, alloc_col3 = st.columns(3)
with alloc_col1:
    st.metric("Target", f"€{target:,.2f}")
with alloc_col2:
    st.metric("Total Allocated", f"€{total_allocated:,.2f}")
with alloc_col3:
    color = "normal" if abs(allocation_diff) < 0.01 else "off"
    st.metric("Difference", f"€{allocation_diff:,.2f}", delta=None if abs(allocation_diff) < 0.01 else f"{allocation_diff:,.2f}")

if abs(allocation_diff) > 0.01:
    st.warning(f"⚠️ Allocation does not match target. Difference: €{allocation_diff:,.2f}")

# Calculate and display resulting metrics
if total_allocated > 0:
    st.markdown("---")
    st.header("📊 Resulting Metrics After Allocation")
    
    # Calculate metrics by arrondissement
    results_list = []
    total_new_premium = 0
    total_expected_loss_portfolio = 0
    
    for arr in arrondissements_list:
        arr_str = str(arr)
        arr_customers = st.session_state.customers[st.session_state.customers['COM'].astype(str) == arr_str]
        
        if len(arr_customers) > 0:
            arr_expected_loss = (arr_customers['patrimoine'] * arr_customers['prob']).sum()
            arr_current_premium = arr_customers['model_premium'].sum()
            arr_avg_current_premium = arr_customers['model_premium'].mean()
            arr_allocation = st.session_state.allocation_dict.get(arr, 0.0)
            
            # Calculate new premium: current premium + allocation
            arr_new_premium = arr_current_premium + arr_allocation
            # Calculate average new premium: average current premium + (allocation / number of customers)
            arr_avg_new_premium = arr_avg_current_premium + (arr_allocation / len(arr_customers)) if len(arr_customers) > 0 else arr_avg_current_premium
            arr_profit = arr_new_premium - arr_expected_loss
            arr_profit_margin = (arr_profit / arr_new_premium * 100) if arr_new_premium > 0 else 0
            
            total_new_premium += arr_new_premium
            total_expected_loss_portfolio += arr_expected_loss
            
            results_list.append({
                'Arrondissement Code': arr,
                'Arrondissement': arrondissements_names.get(arr, f"Arr {arr}"),
                'Allocation (€)': arr_allocation,
                'Current Premium (€)': arr_current_premium,
                'Avg Current Premium (€)': arr_avg_current_premium,
                'New Premium (€)': arr_new_premium,
                'Avg New Premium (€)': arr_avg_new_premium,
                'Expected Loss (€)': arr_expected_loss,
                'Profit (€)': arr_profit,
                'Profit Margin (%)': arr_profit_margin,
                'Customers': len(arr_customers)
            })
    
    results_df = pd.DataFrame(results_list)
    
    # Display results table only if we have data
    if len(results_df) > 0:
        results_df = results_df.round(2)
        st.subheader("Metrics by Arrondissement")
        st.dataframe(results_df, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ No customer data found for the selected arrondissements. Please check your data.")
        results_df = pd.DataFrame()  # Ensure it's an empty dataframe with proper structure
    
    # Portfolio-level results
    st.subheader("Portfolio-Level Results")
    portfolio_results_cols = st.columns(4)
    
    total_profit = total_new_premium - total_expected_loss_portfolio
    total_profit_margin = (total_profit / total_new_premium * 100) if total_new_premium > 0 else 0
    premium_increase = total_new_premium - current_total_premium
    premium_increase_pct = (premium_increase / current_total_premium * 100) if current_total_premium > 0 else 0
    
    with portfolio_results_cols[0]:
        st.metric("Total New Premium", f"€{total_new_premium:,.2f}", 
                 delta=f"{premium_increase_pct:.2f}%")
    with portfolio_results_cols[1]:
        st.metric("Total Expected Loss", f"€{total_expected_loss_portfolio:,.2f}")
    with portfolio_results_cols[2]:
        st.metric("Total Profit", f"€{total_profit:,.2f}")
    with portfolio_results_cols[3]:
        st.metric("Profit Margin", f"{total_profit_margin:.2f}%")
    
    # Visualization of allocation
    st.subheader("Allocation Visualization")
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        # Bar chart of allocation
        alloc_df = pd.DataFrame({
            'Arrondissement': [arrondissements_names.get(arr, f"Arr {arr}") for arr in arrondissements_list],
            'Allocation (€)': [st.session_state.allocation_dict.get(arr, 0.0) for arr in arrondissements_list]
        })
        fig_alloc = px.bar(alloc_df, x='Arrondissement', y='Allocation (€)', 
                          title="Allocation by Arrondissement")
        fig_alloc.update_xaxes(tickangle=45)
        st.plotly_chart(fig_alloc, use_container_width=True)
    
    with viz_col2:
        # Profit margin by arrondissement
        if len(results_df) > 0:
            fig_margin = px.bar(results_df, x='Arrondissement', y='Profit Margin (%)',
                               title="Profit Margin by Arrondissement")
            fig_margin.update_xaxes(tickangle=45)
            st.plotly_chart(fig_margin, use_container_width=True)
    
    # Map visualization with old and new average premiums
    st.subheader("Map: Average Premiums Comparison")
    if ('insee' in st.session_state.data.columns and 
        len(results_df) > 0 and 
        'Arrondissement Code' in results_df.columns and 
        'Avg Current Premium (€)' in results_df.columns and
        'Avg New Premium (€)' in results_df.columns):
        # Merge results with map data
        map_results = st.session_state.data.copy()
        
        # Create mappings for average premiums
        avg_current_premium_mapping = dict(zip(results_df['Arrondissement Code'], results_df['Avg Current Premium (€)']))
        avg_new_premium_mapping = dict(zip(results_df['Arrondissement Code'], results_df['Avg New Premium (€)']))
        
        map_results['avg_current_premium'] = map_results['insee'].map(avg_current_premium_mapping)
        map_results['avg_current_premium'] = map_results['avg_current_premium'].fillna(0)
        
        map_results['avg_new_premium'] = map_results['insee'].map(avg_new_premium_mapping)
        map_results['avg_new_premium'] = map_results['avg_new_premium'].fillna(0)
        
        # Create two maps side by side
        map_col1, map_col2 = st.columns(2)
        
        with map_col1:
            fig_map_old = px.choropleth(
                map_results, 
                geojson=map_results.geometry, 
                locations=map_results.index, 
                color='avg_current_premium',
                projection="mercator",
                labels={'avg_current_premium': 'Average Premium (€)'},
                title="Current Average Premiums (Modeled)",
                color_continuous_scale="Blues"
            )
            fig_map_old.update_geos(fitbounds="locations", visible=True)
            st.plotly_chart(fig_map_old, use_container_width=True)
        
        with map_col2:
            fig_map_new = px.choropleth(
                map_results, 
                geojson=map_results.geometry, 
                locations=map_results.index, 
                color='avg_new_premium',
                projection="mercator",
                labels={'avg_new_premium': 'Average Premium (€)'},
                title="New Average Premiums (After Allocation)",
                color_continuous_scale="Greens"
            )
            fig_map_new.update_geos(fitbounds="locations", visible=True)
            st.plotly_chart(fig_map_new, use_container_width=True)


