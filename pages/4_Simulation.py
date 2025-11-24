import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import plotly.express as px

st.set_page_config(layout="wide", page_title="Simulation - Customer Churn")

TITLE = "🎲 Simulation: Customer Churn After Allocation"
TARGET_DEFAULT = 2_000_000.0

# Fixed simulation parameters (intentionally strict to highlight sensitivity)
SIM_SEED = 123
CHURN_SENSITIVITY = 1.6
BURDEN_FOCUS = 0.8  # closer to 1 => income-driven churn
BASE_CHURN = 0.12
INCOME_THRESHOLD = 0.05  # lower threshold => higher sensitivity
PATRIMOINE_THRESHOLD = 0.01


@st.cache_data(show_spinner=False)
def load_map():
    map_df = gpd.read_file("./arrondissements_municipaux/arrondissements_municipaux-20180711.shp")
    map_df = map_df[map_df["insee"].isin(
        [
            "75101",
            "75102",
            "75103",
            "75104",
            "75105",
            "75106",
            "75107",
            "75108",
            "75109",
            "75110",
            "75111",
            "75112",
            "75113",
            "75114",
            "75115",
            "75116",
            "75117",
            "75118",
            "75119",
            "75120",
        ]
    )]
    return map_df


def ensure_data_loaded():
    """Make sure base data is available in session state."""
    if "data" not in st.session_state or "customers" not in st.session_state:
        map_df = load_map()

        city_exposure = pd.read_csv("city_exposure.csv")
        city_exposure["COM"] = city_exposure["COM"].astype(str)

        customers = pd.read_csv("customers.csv")
        customers["COM"] = customers["COM"].astype(str)
        st.session_state.customers = customers

        filosofi_filtered = pd.read_csv("filosofi_filtered.csv")
        filosofi_filtered["insee"] = filosofi_filtered["COM"].astype(str)
        filosofi_filtered = filosofi_filtered.drop(columns=["COM"])

        map_data = map_df.merge(city_exposure, left_on="insee", right_on="COM", how="left")
        map_data = map_data.merge(filosofi_filtered, on="insee", how="left")
        st.session_state.data = map_data


ensure_data_loaded()
customers = st.session_state.customers.copy()
map_data = st.session_state.data.copy()
customers["COM"] = customers["COM"].astype(str)
map_data["insee"] = map_data["insee"].astype(str)

arrondissements = (
    map_data.groupby(["insee", "nom"])
    .first()
    .reset_index()[["insee", "nom"]]
    .sort_values("insee")
)
arrondissements_list = arrondissements["insee"].tolist()
arrondissements_names = dict(zip(arrondissements["insee"], arrondissements["nom"]))

target = st.session_state.get("target_profit_costs", TARGET_DEFAULT)

if "simulation_allocations" not in st.session_state:
    st.session_state.simulation_allocations = {arr: 0.0 for arr in arrondissements_list}


st.title(TITLE)
st.write(
    """
Simulate how customers might react (churn or stay) when premiums increase per arrondissement.
Churn probability is calibrated on the burden of the new premium compared with the local
median revenues and the insured patrimoine.
"""
)

st.markdown("### 1. Configure Allocation (fixed target: €{:,.0f})".format(target))


def apply_allocation_from_series(series):
    total_series = series.sum()
    if total_series <= 0:
        return
    for arr in arrondissements_list:
        st.session_state.simulation_allocations[arr] = float(
            target * (series.get(arr, 0.0) / total_series)
        )


allocation_mode = st.radio(
    "Auto-fill allocation strategy",
    (
        "Manual",
        "Equal Distribution",
        "Proportional to Exposure",
        "Proportional to Risk",
    ),
    horizontal=True,
)

if allocation_mode == "Equal Distribution":
    equal = target / len(arrondissements_list)
    for arr in arrondissements_list:
        st.session_state.simulation_allocations[arr] = equal
elif allocation_mode == "Proportional to Exposure":
    exposure = (
        customers.groupby("COM")["patrimoine"]
        .sum()
        .reindex(arrondissements_list)
        .fillna(0.0)
    )
    if exposure.sum() > 0:
        apply_allocation_from_series(exposure)
    else:
        st.warning("Exposure data not available to auto-fill.")
elif allocation_mode == "Proportional to Risk":
    customers["expected_loss"] = customers["patrimoine"] * customers["prob"]
    risk = (
        customers.groupby("COM")["expected_loss"]
        .sum()
        .reindex(arrondissements_list)
        .fillna(0.0)
    )
    if risk.sum() > 0:
        apply_allocation_from_series(risk)
    else:
        st.warning("Risk data not available to auto-fill.")


allocation_df = pd.DataFrame(
    {
        "Arrondissement Code": arrondissements_list,
        "Arrondissement": [arrondissements_names.get(arr, arr) for arr in arrondissements_list],
        "Allocation (€)": [
            st.session_state.simulation_allocations.get(arr, 0.0) for arr in arrondissements_list
        ],
    }
)

edited_alloc_df = st.data_editor(
    allocation_df,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "Allocation (€)": st.column_config.NumberColumn(format="€%.2f", step=1000.0, min_value=0.0)
    },
    key="allocation_editor",
)

for _, row in edited_alloc_df.iterrows():
    st.session_state.simulation_allocations[row["Arrondissement Code"]] = float(row["Allocation (€)"])

total_allocated = sum(st.session_state.simulation_allocations.values())

summary_col1, summary_col2, summary_col3 = st.columns(3)
with summary_col1:
    st.metric("Target", f"€{target:,.0f}")
with summary_col2:
    st.metric("Total Allocated", f"€{total_allocated:,.0f}")
with summary_col3:
    diff = target - total_allocated
    st.metric("Difference", f"€{diff:,.0f}")
if abs(target - total_allocated) > 1:
    st.warning("Allocation total must match the €{:,.0f} target before running the simulation.".format(target))

st.markdown("### 2. Simulation Parameters (locked for workshop)")
st.info(
    f"""
    The churn model uses fixed parameters to make customer reactions noticeable:
    - Random seed: {SIM_SEED}
    - Churn sensitivity: {CHURN_SENSITIVITY}
    - Income vs patrimoine weight: {BURDEN_FOCUS:.2f}
    - Base churn: {BASE_CHURN:.0%}
    - Burden thresholds: income {INCOME_THRESHOLD:.2%}, patrimoine {PATRIMOINE_THRESHOLD:.2%}
    """
)

run_simulation = st.button("Run Churn Simulation", type="primary", disabled=abs(target - total_allocated) > 1)

if run_simulation:
    st.markdown("### 3. Simulation Results")

    arr_counts = customers.groupby("COM").size().reindex(arrondissements_list).fillna(0).to_dict()
    allocation_share_per_customer = {}
    for arr in arrondissements_list:
        count = arr_counts.get(arr, 0)
        allocation_share_per_customer[arr] = (
            st.session_state.simulation_allocations.get(arr, 0.0) / count if count > 0 else 0.0
        )

    customers["allocation_share"] = customers["COM"].map(allocation_share_per_customer).fillna(0.0)
    customers["new_premium"] = customers["model_premium"] + customers["allocation_share"]

    income_map = (
        map_data.groupby("insee")["DISP_MED18"]
        .mean()
        .reindex(arrondissements_list)
        .fillna(map_data["DISP_MED18"].mean())
        .to_dict()
    )

    customers["median_income"] = customers["COM"].map(income_map).fillna(map_data["DISP_MED18"].mean())
    customers["premium_income_ratio"] = customers["new_premium"] / customers["median_income"].replace(0, np.nan)
    customers["premium_income_ratio"] = customers["premium_income_ratio"].fillna(
        customers["new_premium"] / (customers["median_income"].replace(0, np.nan) + 1)
    )

    customers["premium_patrimoine_ratio"] = customers["new_premium"] / customers["patrimoine"].replace(0, np.nan)
    customers["premium_patrimoine_ratio"] = customers["premium_patrimoine_ratio"].fillna(
        customers["premium_income_ratio"] * 0.1
    )

    burden_income = np.clip(customers["premium_income_ratio"] / INCOME_THRESHOLD, 0, 3)
    burden_patrimoine = np.clip(customers["premium_patrimoine_ratio"] / PATRIMOINE_THRESHOLD, 0, 3)

    churn_prob = np.clip(
        (
            BASE_CHURN
            + BURDEN_FOCUS * 0.35 * burden_income
            + (1 - BURDEN_FOCUS) * 0.25 * burden_patrimoine
        )
        * CHURN_SENSITIVITY,
        0,
        0.95,
    )

    rng = np.random.default_rng(SIM_SEED)
    customers["stayed"] = rng.random(len(customers)) > churn_prob

    stayed_rate = customers["stayed"].mean()
    churn_rate = 1 - stayed_rate

    metric_col1, metric_col2 = st.columns(2)
    with metric_col1:
        st.metric("Customers Staying", f"{stayed_rate * 100:.1f}%", delta=f"{(stayed_rate - 0.5) * 100:.1f} pp")
    with metric_col2:
        st.metric("Customers Churning", f"{churn_rate * 100:.1f}%")

    stay_summary = (
        customers.groupby("COM")
        .agg(
            original_customers=("stayed", "count"),
            customers_staying=("stayed", "sum"),
        )
        .reset_index()
    )
    stay_summary["customers_churned"] = stay_summary["original_customers"] - stay_summary["customers_staying"]
    stay_summary["stay_rate_%"] = (
        stay_summary["customers_staying"] / stay_summary["original_customers"]
    ).replace(np.nan, 0) * 100
    stay_summary["old_share_%"] = (
        stay_summary["original_customers"] / stay_summary["original_customers"].sum()
    ) * 100
    stay_summary["new_share_%"] = (
        stay_summary["customers_staying"] / stay_summary["customers_staying"].sum()
    ).replace(np.nan, 0) * 100
    stay_summary["Arrondissement"] = stay_summary["COM"].map(arrondissements_names)

    st.subheader("Geographic Distribution Shift (Maps)")
    if "geometry" in map_data.columns:
        map_geo = map_data.copy()
        old_share_map = stay_summary.set_index("COM")["old_share_%"].to_dict()
        new_share_map = stay_summary.set_index("COM")["new_share_%"].to_dict()

        map_geo["old_share"] = map_geo["insee"].map(old_share_map).fillna(0.0)
        map_geo["new_share"] = map_geo["insee"].map(new_share_map).fillna(0.0)
        map_geo["share_diff"] = map_geo["new_share"] - map_geo["old_share"]

        map_col1, map_col2 = st.columns(2)
        with map_col1:
            fig_old = px.choropleth(
                map_geo,
                geojson=map_geo.geometry,
                locations=map_geo.index,
                color="old_share",
                projection="mercator",
                labels={"old_share": "Old Share (%)"},
                title="Before Churn",
                color_continuous_scale="Blues",
            )
            fig_old.update_geos(fitbounds="locations", visible=True)
            st.plotly_chart(fig_old, use_container_width=True)

        with map_col2:
            fig_new = px.choropleth(
                map_geo,
                geojson=map_geo.geometry,
                locations=map_geo.index,
                color="new_share",
                projection="mercator",
                labels={"new_share": "New Share (%)"},
                title="After Churn",
                color_continuous_scale="Greens",
            )
            fig_new.update_geos(fitbounds="locations", visible=True)
            st.plotly_chart(fig_new, use_container_width=True)

        max_abs_diff = float(map_geo["share_diff"].abs().max())
        diff_range = max_abs_diff if max_abs_diff > 0 else 1.0

        fig_diff = px.choropleth(
            map_geo,
            geojson=map_geo.geometry,
            locations=map_geo.index,
            color="share_diff",
            projection="mercator",
            labels={"share_diff": "Δ Share (pp)"},
            title="Difference (After - Before)",
            color_continuous_scale="RdBu",
            range_color=(-diff_range, diff_range),
        )
        fig_diff.update_geos(fitbounds="locations", visible=True)
        st.plotly_chart(fig_diff, use_container_width=True)
    else:
        st.warning("No geometry available to draw the geographic maps.")

    dist_col1, dist_col2 = st.columns(2)
    with dist_col1:
        st.caption("Original Geographic Distribution")
        st.bar_chart(
            stay_summary.set_index("Arrondissement")["old_share_%"],
            height=300,
        )
    with dist_col2:
        st.caption("New Distribution After Churn")
        st.bar_chart(
            stay_summary.set_index("Arrondissement")["new_share_%"],
            height=300,
        )

    st.subheader("Customer Loss by Arrondissement")
    loss_table = stay_summary[
        [
            "COM",
            "Arrondissement",
            "original_customers",
            "customers_staying",
            "customers_churned",
            "stay_rate_%",
            "old_share_%",
            "new_share_%",
        ]
    ].round(2)
    st.dataframe(loss_table.rename(columns={"COM": "Arrondissement Code"}), use_container_width=True, hide_index=True)

    st.subheader("Real Profit After Churn")
    staying_mask = customers["stayed"]
    premium_staying = customers.loc[staying_mask, "new_premium"].sum()
    expected_loss_staying = (
        customers.loc[staying_mask, "patrimoine"] * customers.loc[staying_mask, "prob"]
    ).sum()
    realized_profit = premium_staying - expected_loss_staying

    profit_cols = st.columns(3)
    with profit_cols[0]:
        st.metric("Premium Collected (Post-Churn)", f"€{premium_staying:,.0f}")
    with profit_cols[1]:
        st.metric("Expected Loss (Remaining Portfolio)", f"€{expected_loss_staying:,.0f}")
    with profit_cols[2]:
        st.metric("Realized Profit", f"€{realized_profit:,.0f}")

    st.info(
        "The simulation uses stochastic churn draws. "
        "Adjust the parameters or the allocation and re-run to explore different scenarios."
    )
else:
    st.info("Configure the allocation and parameters, then click **Run Churn Simulation**.")