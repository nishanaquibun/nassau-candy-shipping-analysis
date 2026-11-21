
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Nassau Candy | Shipping Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "processed" / "nassau_candy_cleaned.csv"

NAVY = "#183153"
DARK_NAVY = "#10243A"
BLUE = "#3478C8"
LIGHT_BLUE = "#EAF2FB"
GREY = "#64748B"


# =====================================================
# 2. CORPORATE CSS
# =====================================================



st.markdown("""
<style>
    .stApp {
        background-color: #F3F6FA;
    }

    [data-testid="stSidebar"] {
        background-color: #142B49;
    }

    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Main title */
    .main-title {
        color: #183153;
        font-size: 30px;
        font-weight: 750;
        margin-bottom: 0;
    }

    /* Subheadings - dark charcoal */
    .sub-title {
        color: #303030 !important;
        font-size: 14px;
        margin-top: 4px;
    }

    /* Section headings - very dark */
    .section-title {
        color: #252525 !important;
        font-size: 21px;
        font-weight: 700;
        margin-top: 15px;
    }

    /* KPI cards - unchanged */
    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #DCE5EF;
        padding: 17px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.04);
    }

    /* KPI labels - dark charcoal */
    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] * {
        color: #303030 !important;
        font-weight: 600 !important;
    }

    /* KPI values - dark navy */
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] * {
        color: #142B49 !important;
    }

    /* Notice box - unchanged */
    .notice {
        background-color: #FFF4DF;
        border-left: 5px solid #E5A000;
        padding: 14px;
        border-radius: 6px;
        color: #674B0B;
        margin: 12px 0;
    }

    /* Footer - dark grey */
    .footer {
        color: #303030 !important;
        text-align: center;
        font-size: 12px;
        padding: 25px 0 10px 0;
    }

    /* Markdown headings - dark charcoal */
    .stMarkdown h1,
    .stMarkdown h2,
    .stMarkdown h3,
    .stMarkdown h4 {
        color: #252525 !important;
    }

    /* Supporting text - dark grey */
    .stMarkdown p,
    .stMarkdown li {
        color: #303030;
    }

</style>
""", unsafe_allow_html=True)



# =====================================================
# 3. LOAD DATA
# =====================================================

@st.cache_data
def load_data():
    data = pd.read_csv(DATA_FILE, low_memory=False)

    data["Sales"] = pd.to_numeric(data["Sales"], errors="coerce")
    data["Gross Profit"] = pd.to_numeric(
        data["Gross Profit"], errors="coerce"
    )
    data["Cost"] = pd.to_numeric(data["Cost"], errors="coerce")
    data["Units"] = pd.to_numeric(data["Units"], errors="coerce")

    for column in ["Order_Date_Parsed", "Ship_Date_Parsed"]:
        if column in data.columns:
            data[column] = pd.to_datetime(
                data[column], errors="coerce"
            )

    return data


try:
    df = load_data()
except Exception as error:
    st.error(f"Unable to load dataset: {error}")
    st.info(
        "Check that nassau_candy_cleaned.csv exists inside "
        "data/processed."
    )
    st.stop()


# =====================================================
# 4. SIDEBAR AND FILTERS
# =====================================================

st.sidebar.title("NASSAU CANDY")
st.sidebar.caption("SHIPPING ANALYTICS PLATFORM")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Executive Overview",
        "Factory Performance",
        "Geographic Route Analysis",
        "Destination Analysis",
        "Destination Performance",
        "Shipping Mode Analysis",
        "Data Quality"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("DATA FILTERS")

factories = sorted(df["Factory"].dropna().unique())
divisions = sorted(df["Division"].dropna().unique())
ship_modes = sorted(df["Ship Mode"].dropna().unique())
countries = sorted(df["Country/Region"].dropna().unique())

selected_factories = st.sidebar.multiselect(
    "Select Factory",
    factories,
    default=factories
)

selected_divisions = st.sidebar.multiselect(
    "Select Division",
    divisions,
    default=divisions
)

selected_modes = st.sidebar.multiselect(
    "Select Ship Mode",
    ship_modes,
    default=ship_modes
)

selected_countries = st.sidebar.multiselect(
    "Select Country",
    countries,
    default=countries
)

filtered = df[
    df["Factory"].isin(selected_factories)
    & df["Division"].isin(selected_divisions)
    & df["Ship Mode"].isin(selected_modes)
    & df["Country/Region"].isin(selected_countries)
].copy()


# =====================================================
# 5. HELPER FUNCTIONS
# =====================================================

def money(value):
    return f"${value:,.2f}"


def make_header(title, subtitle):
    st.markdown(
        f'<div class="main-title">{title}</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="sub-title">{subtitle}</div>',
        unsafe_allow_html=True
    )
    st.markdown("---")


def make_lane_data(data):
    """
    Build geographic lanes and provisional shipment counts.

    A provisional shipment is identified by:
    Base Order + Factory + Country + State + City.

    This is an analytical proxy, not a verified physical shipment.
    """

    group_columns = [
        "Factory",
        "Country/Region",
        "State/Province",
        "City"
    ]

    lanes = (
        data.groupby(group_columns, dropna=False)
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Gross Profit", "sum"),
            Units=("Units", "sum"),
            Order_Lines=("Row ID", "count"),
            Provisional_Shipments=("Base_Order_ID", "nunique")
        )
        .reset_index()
    )

    lanes["Destination"] = (
        lanes["City"].astype(str)
        + ", "
        + lanes["State/Province"].astype(str)
    )

    lanes["Lane"] = (
        lanes["Factory"].astype(str)
        + " → "
        + lanes["Destination"]
    )

    return lanes


def show_empty():
    st.warning(
        "No records match the selected filters. "
        "Please change your sidebar selections."
    )


# =====================================================
# 6. EXECUTIVE OVERVIEW
# =====================================================

if page == "Executive Overview":

    make_header(
        "Executive Overview",
        "Factory-to-Customer Shipping Route Efficiency Analysis"
    )

    if filtered.empty:
        show_empty()
        st.stop()

    total_sales = filtered["Sales"].sum()
    total_profit = filtered["Gross Profit"].sum()
    total_units = filtered["Units"].sum()
    total_records = len(filtered)

    margin = (
        total_profit / total_sales * 100
        if total_sales else 0
    )

    lanes = make_lane_data(filtered)

    # KPI CARDS
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Sales", money(total_sales))
    c2.metric("Gross Profit", money(total_profit))
    c3.metric("Order Lines", f"{total_records:,}")
    c4.metric("Geographic Lanes", f"{len(lanes):,}")

    c5, c6, c7, c8 = st.columns(4)

    c5.metric("Total Units", f"{total_units:,.0f}")
    c6.metric("Factories", filtered["Factory"].nunique())
    c7.metric("Destinations", filtered["State/Province"].nunique())
    c8.metric("Gross Profit Margin", f"{margin:.1f}%")

    st.markdown(
        '<div class="section-title">Business Performance</div>',
        unsafe_allow_html=True
    )

    left, right = st.columns(2)

    factory_sales = (
        filtered.groupby("Factory")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending=False)
    )

    fig1 = px.bar(
        factory_sales,
        x="Factory",
        y="Sales",
        title="Sales Contribution by Factory",
        color="Sales",
        color_continuous_scale="Blues"
    )
    fig1.update_layout(showlegend=False)
    left.plotly_chart(fig1, width="stretch")

    mode_sales = (
        filtered.groupby("Ship Mode")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending=False)
    )

    fig2 = px.pie(
        mode_sales,
        names="Ship Mode",
        values="Sales",
        title="Sales Distribution by Ship Mode",
        hole=0.45
    )
    right.plotly_chart(fig2, width="stretch")

    st.markdown(
        '<div class="section-title">Top Destinations</div>',
        unsafe_allow_html=True
    )

    destinations = (
        filtered.groupby(["State/Province", "Country/Region"])
        ["Sales"]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending=False)
        .head(10)
    )

    destinations["Destination"] = (
        destinations["State/Province"]
        + ", "
        + destinations["Country/Region"]
    )

    fig3 = px.bar(
        destinations.sort_values("Sales"),
        x="Sales",
        y="Destination",
        orientation="h",
        title="Top 10 Destinations by Sales",
        color="Sales",
        color_continuous_scale="Blues"
    )
    fig3.update_layout(showlegend=False)
    st.plotly_chart(fig3, width="stretch")


# =====================================================
# 7. FACTORY PERFORMANCE
# =====================================================

elif page == "Factory Performance":

    make_header(
        "Factory Performance",
        "Compare sales, profitability and geographic coverage"
    )

    if filtered.empty:
        show_empty()
        st.stop()

    factory = (
        filtered.groupby("Factory")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Gross Profit", "sum"),
            Cost=("Cost", "sum"),
            Units=("Units", "sum"),
            Order_Lines=("Row ID", "count"),
            Base_Orders=("Base_Order_ID", "nunique")
        )
        .reset_index()
    )

    factory["Profit_Margin"] = (
        factory["Profit"] / factory["Sales"] * 100
    )

    lanes = make_lane_data(filtered)

    coverage = (
        lanes.groupby("Factory")
        .size()
        .reset_index(name="Geographic_Lanes")
    )

    factory = factory.merge(coverage, on="Factory", how="left")

    left, right = st.columns(2)

    fig1 = px.bar(
        factory.sort_values("Sales", ascending=False),
        x="Factory",
        y="Sales",
        title="Factory-wise Sales",
        color="Sales",
        color_continuous_scale="Blues"
    )
    left.plotly_chart(fig1, width="stretch")

    fig2 = px.bar(
        factory.sort_values("Profit", ascending=False),
        x="Factory",
        y="Profit",
        title="Factory-wise Gross Profit",
        color="Profit",
        color_continuous_scale="Teal"
    )
    right.plotly_chart(fig2, width="stretch")

    fig3 = px.bar(
        factory.sort_values("Geographic_Lanes"),
        x="Geographic_Lanes",
        y="Factory",
        orientation="h",
        title="Geographic Coverage by Factory"
    )
    st.plotly_chart(fig3, width="stretch")

    st.subheader("Factory Performance Table")
    st.dataframe(
        factory.sort_values("Sales", ascending=False),
        width="stretch",
        hide_index=True
    )




# =====================================================
# 8. GEOGRAPHIC ROUTE ANALYSIS
# =====================================================

elif page == "Geographic Route Analysis":

    make_header(
        "Geographic Route Analysis",
        "Analyze factory-to-customer geographic lanes and route performance"
    )

    if filtered.empty:
        show_empty()
        st.stop()

    # 1. PREPARE ROUTE DATA
    lanes = make_lane_data(filtered)

    if lanes.empty:
        st.info("No geographic route data available.")
        st.stop()

    lanes = lanes.copy()

    lanes["Gross_Profit_Margin"] = (
        lanes["Profit"] / lanes["Sales"] * 100
    ).where(lanes["Sales"] != 0, 0)

    total_lanes = len(lanes)
    total_shipments = lanes["Provisional_Shipments"].sum()
    total_sales = lanes["Sales"].sum()
    total_profit = lanes["Profit"].sum()

    # 2. KPI CARDS
    st.markdown(
        '<div class="section-title">Route Performance Overview</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Geographic Lanes", f"{total_lanes:,}")
    c2.metric("Provisional Shipments", f"{total_shipments:,.0f}")
    c3.metric("Total Sales", money(total_sales))
    c4.metric("Gross Profit", money(total_profit))

    st.markdown(
        '<div class="notice"><b>Important:</b> '
        'Shipment counts are provisional combinations based on '
        'Base Order ID, factory and destination. They are not '
        'verified physical shipment records. Gross profit represents '
        'product-level financial performance, not shipping profit.</div>',
        unsafe_allow_html=True
    )

    # 3. TOP 10 BUSIEST ROUTES
    st.markdown(
        '<div class="section-title">Highest-Volume Geographic Lanes</div>',
        unsafe_allow_html=True
    )

    top_volume = (
        lanes.nlargest(10, "Provisional_Shipments")
        .sort_values("Provisional_Shipments")
    )

    fig1 = px.bar(
        top_volume,
        x="Provisional_Shipments",
        y="Lane",
        orientation="h",
        title="Top 10 Lanes by Provisional Shipment Volume",
        color="Provisional_Shipments",
        color_continuous_scale="Blues",
        text="Provisional_Shipments"
    )

    st.plotly_chart(fig1, width="stretch")

    # 4. TOP 10 ROUTES BY SALES
    st.markdown(
        '<div class="section-title">Revenue Contribution by Route</div>',
        unsafe_allow_html=True
    )

    top_sales = (
        lanes.nlargest(10, "Sales")
        .sort_values("Sales")
    )

    fig2 = px.bar(
        top_sales,
        x="Sales",
        y="Lane",
        orientation="h",
        title="Top 10 Lanes by Total Sales",
        color="Sales",
        color_continuous_scale="Teal",
        text_auto=".2s"
    )

    st.plotly_chart(fig2, width="stretch")

    # 5. FACTORY-WISE GEOGRAPHIC COVERAGE
    st.markdown(
        '<div class="section-title">Factory Geographic Coverage</div>',
        unsafe_allow_html=True
    )

    factory_coverage = (
        lanes.groupby("Factory")
        .agg(
            Geographic_Lanes=("Lane", "count"),
            Provisional_Shipments=("Provisional_Shipments", "sum"),
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Profit", "sum")
        )
        .reset_index()
        .sort_values("Geographic_Lanes", ascending=False)
    )

    left, right = st.columns(2)

    fig3 = px.bar(
        factory_coverage,
        x="Factory",
        y="Geographic_Lanes",
        title="Number of Geographic Lanes Served",
        color="Geographic_Lanes",
        color_continuous_scale="Blues",
        text="Geographic_Lanes"
    )

    left.plotly_chart(fig3, width="stretch")

    fig4 = px.bar(
        factory_coverage.sort_values("Provisional_Shipments"),
        x="Provisional_Shipments",
        y="Factory",
        orientation="h",
        title="Provisional Shipments by Factory",
        color="Provisional_Shipments",
        color_continuous_scale="Teal",
        text="Provisional_Shipments"
    )

    right.plotly_chart(fig4, width="stretch")

    st.subheader("Factory Coverage Details")

    st.dataframe(
        factory_coverage,
        width="stretch",
        hide_index=True
    )

    # 6. SALES VS GROSS PROFIT
    st.markdown(
        '<div class="section-title">Route Financial Comparison</div>',
        unsafe_allow_html=True
    )

    fig5 = px.scatter(
        lanes,
        x="Sales",
        y="Profit",
        size="Provisional_Shipments",
        color="Factory",
        hover_name="Lane",
        hover_data=[
            "Units",
            "Gross_Profit_Margin",
            "Provisional_Shipments"
        ],
        title="Geographic Lane Sales vs Gross Profit"
    )

    st.plotly_chart(fig5, width="stretch")

    # 7. LOW-VOLUME ROUTES
    st.markdown(
        '<div class="section-title">Low-Volume Geographic Lanes</div>',
        unsafe_allow_html=True
    )

    low_volume = (
        lanes.nsmallest(10, "Provisional_Shipments")
        .sort_values("Provisional_Shipments")
    )

    st.dataframe(
        low_volume[
            [
                "Factory",
                "Lane",
                "Provisional_Shipments",
                "Sales",
                "Profit"
            ]
        ],
        width="stretch",
        hide_index=True
    )

    st.caption(
        "Low shipment volume alone does not indicate poor route "
        "performance. Demand, product availability and market size "
        "may also influence route volume."
    )

    # 8. COMPLETE ROUTE PERFORMANCE TABLE
    st.markdown(
        '<div class="section-title">Complete Geographic Lane Report</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        lanes.sort_values(
            "Provisional_Shipments",
            ascending=False
        ),
        width="stretch",
        hide_index=True
    )

    csv = lanes.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Route Performance Report",
        data=csv,
        file_name="route_performance_dashboard.csv",
        mime="text/csv"
    )

    # 9. DATE DATA LIMITATION
    st.markdown(
        '<div class="notice"><b>Date limitation:</b> '
        'Recorded Order Date-to-Ship Date intervals are anomalously '
        'long and have not been verified as actual transit times. '
        'This page does not rank routes by delivery speed or claim '
        'actual delivery delays.</div>',
        unsafe_allow_html=True
    )




# =====================================================
# 9. DESTINATION ANALYSIS
# =====================================================

elif page == "Destination Analysis":

    make_header(
        "Destination Analysis",
        "Understand customer demand across destination states"
    )

    if filtered.empty:
        show_empty()
        st.stop()

    state = (
        filtered.groupby(["Country/Region", "State/Province"])
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Gross Profit", "sum"),
            Units=("Units", "sum"),
            Order_Lines=("Row ID", "count"),
            Customers=("Customer ID", "nunique")
        )
        .reset_index()
    )

    state["Destination"] = (
        state["State/Province"]
        + ", "
        + state["Country/Region"]
    )

    top_states = (
        state.nlargest(15, "Sales")
        .sort_values("Sales")
    )

    fig = px.bar(
        top_states,
        x="Sales",
        y="Destination",
        orientation="h",
        title="Top 15 Destinations by Sales",
        color="Sales",
        color_continuous_scale="Blues"
    )

    st.plotly_chart(fig, width="stretch")

    fig2 = px.scatter(
        state,
        x="Sales",
        y="Profit",
        size="Units",
        hover_name="Destination",
        title="Destination Sales vs Gross Profit",
        color="Sales",
        color_continuous_scale="Blues"
    )

    st.plotly_chart(fig2, width="stretch")

    st.subheader("Destination Performance Table")
    st.dataframe(
        state.sort_values("Sales", ascending=False),
        width="stretch",
        hide_index=True
    )


# =====================================================
# 10. DESTINATION PERFORMANCE
# =====================================================

elif page == "Destination Performance":

    make_header(
        "Destination Performance",
        "Evaluate destination markets by sales, profit and customer demand"
    )

    if filtered.empty:
        show_empty()
        st.stop()

    # -------------------------------------------------
    # 1. DESTINATION-LEVEL AGGREGATION
    # -------------------------------------------------

    destination = (
        filtered.groupby(["Country/Region", "State/Province"])
        .agg(
            Order_Lines=("Row ID", "count"),
            Unique_Base_Orders=("Base_Order_ID", "nunique"),
            Customers=("Customer ID", "nunique"),
            Factories=("Factory", "nunique"),
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Gross Profit", "sum"),
            Total_Units=("Units", "sum")
        )
        .reset_index()
    )

    destination["Destination"] = (
        destination["State/Province"]
        + ", "
        + destination["Country/Region"]
    )

    destination["Gross_Profit_Margin"] = (
        destination["Total_Profit"]
        / destination["Total_Sales"] * 100
    )

    total_sales = destination["Total_Sales"].sum()
    total_profit = destination["Total_Profit"].sum()
    total_orders = filtered["Base_Order_ID"].nunique()

    destination["Sales_Contribution"] = (
        destination["Total_Sales"] / total_sales * 100
    )

    destination["Profit_Contribution"] = (
        destination["Total_Profit"] / total_profit * 100
    )

    destination["Sales_Rank"] = (
        destination["Total_Sales"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    destination["Profit_Rank"] = (
        destination["Total_Profit"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    destination["Order_Rank"] = (
        destination["Unique_Base_Orders"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    # -------------------------------------------------
    # 2. KPI CARDS
    # -------------------------------------------------

    best_sales = destination.loc[
        destination["Total_Sales"].idxmax()
    ]

    best_profit = destination.loc[
        destination["Total_Profit"].idxmax()
    ]

    best_orders = destination.loc[
        destination["Unique_Base_Orders"].idxmax()
    ]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Destinations",
        f"{len(destination):,}"
    )

    c2.metric(
        "Filtered Sales",
        f"${total_sales:,.2f}"
    )

    c3.metric(
        "Filtered Gross Profit",
        f"${total_profit:,.2f}"
    )

    c4.metric(
        "Unique Base Orders",
        f"{total_orders:,}"
    )

    st.markdown("---")

    # -------------------------------------------------
    # 3. TOP DESTINATIONS
    # -------------------------------------------------

    st.subheader("Top Destination Markets")

    top_sales = destination.nlargest(
        10, "Total_Sales"
    ).sort_values("Total_Sales")

    top_profit = destination.nlargest(
        10, "Total_Profit"
    ).sort_values("Total_Profit")

    top_orders = destination.nlargest(
        10, "Unique_Base_Orders"
    ).sort_values("Unique_Base_Orders")

    left, right = st.columns(2)

    with left:

        fig_sales = px.bar(
            top_sales,
            x="Total_Sales",
            y="Destination",
            orientation="h",
            title="Top 10 Destinations by Sales",
            color="Total_Sales",
            color_continuous_scale="Blues",
            labels={
                "Total_Sales": "Sales",
                "Destination": "Destination"
            }
        )

        st.plotly_chart(
            fig_sales,
            width="stretch",
        )

    with right:

        fig_profit = px.bar(
            top_profit,
            x="Total_Profit",
            y="Destination",
            orientation="h",
            title="Top 10 Destinations by Gross Profit",
            color="Total_Profit",
            color_continuous_scale="Teal",
            labels={
                "Total_Profit": "Gross Profit",
                "Destination": "Destination"
            }
        )

        st.plotly_chart(
            fig_profit,
            width="stretch",
        )

    # -------------------------------------------------
    # 4. ORDER VOLUME ANALYSIS
    # -------------------------------------------------

    st.subheader("Customer Demand by Destination")

    fig_orders = px.bar(
        top_orders,
        x="Unique_Base_Orders",
        y="Destination",
        orientation="h",
        title="Top 10 Destinations by Unique Base Orders",
        color="Unique_Base_Orders",
        color_continuous_scale="Blues",
        labels={
            "Unique_Base_Orders": "Unique Base Orders",
            "Destination": "Destination"
        }
    )

    st.plotly_chart(
        fig_orders,
        width="stretch",
    )

    # -------------------------------------------------
    # 5. COUNTRY-WISE PERFORMANCE
    # -------------------------------------------------

    st.markdown("---")
    st.subheader("Country-wise Performance")

    country = (
        destination.groupby("Country/Region")
        .agg(
            Destinations=("State/Province", "nunique"),
            Unique_Base_Orders=("Unique_Base_Orders", "sum"),
            Total_Sales=("Total_Sales", "sum"),
            Total_Profit=("Total_Profit", "sum"),
            Total_Units=("Total_Units", "sum")
        )
        .reset_index()
    )

    country["Sales_Contribution"] = (
        country["Total_Sales"] / total_sales * 100
    )

    country["Gross_Profit_Margin"] = (
        country["Total_Profit"]
        / country["Total_Sales"] * 100
    )

    left, right = st.columns(2)

    with left:

        fig_country = px.bar(
            country.sort_values("Total_Sales"),
            x="Total_Sales",
            y="Country/Region",
            orientation="h",
            title="Sales by Country",
            color="Total_Sales",
            color_continuous_scale="Blues"
        )

        st.plotly_chart(
            fig_country,
            width="stretch",
        )

    with right:

        fig_share = px.pie(
            country,
            names="Country/Region",
            values="Total_Sales",
            title="Country-wise Sales Contribution",
            hole=0.45
        )

        st.plotly_chart(
            fig_share,
            width="stretch",
        )

    st.dataframe(
        country.round(2),
        width="stretch",
        hide_index=True
    )

    # -------------------------------------------------
    # 6. SALES VS PROFIT ANALYSIS
    # -------------------------------------------------

    st.markdown("---")
    st.subheader("Destination Sales vs Profit")

    fig_scatter = px.scatter(
        destination,
        x="Total_Sales",
        y="Total_Profit",
        size="Unique_Base_Orders",
        color="Gross_Profit_Margin",
        hover_name="Destination",
        color_continuous_scale="Blues",
        title="Sales, Gross Profit and Order Volume by Destination",
        labels={
            "Total_Sales": "Total Sales",
            "Total_Profit": "Gross Profit",
            "Gross_Profit_Margin": "Gross Profit Margin (%)",
            "Unique_Base_Orders": "Unique Base Orders"
        }
    )

    st.plotly_chart(
        fig_scatter,
        width="stretch",
    )

    # -------------------------------------------------
    # 7. LOWEST SALES DESTINATIONS
    # -------------------------------------------------

    st.markdown("---")
    st.subheader("Lowest 10 Destinations by Sales")

    lowest = destination.nsmallest(
        10, "Total_Sales"
    )

    st.dataframe(
        lowest[
            [
                "Destination",
                "Unique_Base_Orders",
                "Total_Sales",
                "Total_Profit",
                "Gross_Profit_Margin"
            ]
        ].round(2),
        width="stretch",
        hide_index=True
    )

    # -------------------------------------------------
    # 8. COMPLETE DESTINATION RANKING
    # -------------------------------------------------

    st.markdown("---")
    st.subheader("Complete Destination Performance Ranking")

    display_columns = [
        "Sales_Rank",
        "Profit_Rank",
        "Order_Rank",
        "Destination",
        "Unique_Base_Orders",
        "Order_Lines",
        "Customers",
        "Factories",
        "Total_Sales",
        "Total_Profit",
        "Gross_Profit_Margin",
        "Sales_Contribution",
        "Profit_Contribution"
    ]

    ranking = destination.sort_values(
        "Total_Sales",
        ascending=False
    )[display_columns].copy()

    ranking = ranking.rename(
        columns={
            "Sales_Rank": "Sales Rank",
            "Profit_Rank": "Profit Rank",
            "Order_Rank": "Order Rank",
            "Unique_Base_Orders": "Unique Base Orders",
            "Order_Lines": "Order Lines",
            "Gross_Profit_Margin": "Gross Profit Margin (%)",
            "Sales_Contribution": "Sales Contribution (%)",
            "Profit_Contribution": "Profit Contribution (%)",
            "Total_Sales": "Total Sales",
            "Total_Profit": "Total Gross Profit"
        }
    )

    st.dataframe(
        ranking.round(2),
        width="stretch",
        hide_index=True
    )

    # -------------------------------------------------
    # 9. DOWNLOAD DESTINATION REPORT
    # -------------------------------------------------

    csv = ranking.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "Download Destination Performance Data",
        data=csv,
        file_name="destination_performance_dashboard.csv",
        mime="text/csv"
    )

    # -------------------------------------------------
    # 10. INTERPRETATION NOTICE
    # -------------------------------------------------

    st.markdown(
        '<div class="notice"><b>Analysis note:</b> '
        'Destination rankings use recorded sales, gross profit '
        'and unique base orders. Gross profit is a product '
        'financial measure, not shipping profit. Low sales '
        'alone do not establish poor market performance. '
        'Order-to-Ship intervals are not treated as actual '
        'delivery or transit times.</div>',
        unsafe_allow_html=True
    )

# =====================================================
# 10. SHIPPING MODE ANALYSIS
# =====================================================

elif page == "Shipping Mode Analysis":

    make_header(
        "Shipping Mode Analysis",
        "Compare order volume and financial contribution"
    )

    if filtered.empty:
        show_empty()
        st.stop()

    mode = (
        filtered.groupby("Ship Mode")
        .agg(
            Order_Lines=("Row ID", "count"),
            Sales=("Sales", "sum"),
            Profit=("Gross Profit", "sum"),
            Units=("Units", "sum"),
            Base_Orders=("Base_Order_ID", "nunique")
        )
        .reset_index()
    )

    left, right = st.columns(2)

    fig1 = px.bar(
        mode.sort_values("Order_Lines"),
        x="Order_Lines",
        y="Ship Mode",
        orientation="h",
        title="Order Line Volume by Ship Mode"
    )
    left.plotly_chart(fig1, width="stretch")

    fig2 = px.bar(
        mode.sort_values("Sales"),
        x="Sales",
        y="Ship Mode",
        orientation="h",
        title="Sales by Ship Mode",
        color="Sales",
        color_continuous_scale="Blues"
    )
    right.plotly_chart(fig2, width="stretch")

    fig3 = px.bar(
        mode,
        x="Ship Mode",
        y="Profit",
        title="Gross Profit by Ship Mode"
    )
    st.plotly_chart(fig3, width="stretch")

    st.subheader("Shipping Mode Details")
    st.dataframe(
        mode.sort_values("Sales", ascending=False),
        width="stretch",
        hide_index=True
    )

    st.markdown(
        '<div class="notice"><b>Important:</b> '
        'This page compares recorded order volume and financial '
        'contribution. The available dates do not establish actual '
        'transit or delivery performance, so no shipping-speed '
        'ranking is presented.</div>',
        unsafe_allow_html=True
    )


# =====================================================
# 11. DATA QUALITY
# =====================================================

elif page == "Data Quality":

    make_header(
        "Data Quality & Validation",
        "Review dataset reliability and date-related limitations"
    )

    total_rows = len(df)
    missing = int(df.isnull().sum().sum())
    duplicates = int(df.duplicated().sum())

    if "Order-to-Ship Lead Time" in df.columns:
        lead = pd.to_numeric(
            df["Order-to-Ship Lead Time"],
            errors="coerce"
        )
    else:
        lead = (
            df["Ship_Date_Parsed"] - df["Order_Date_Parsed"]
        ).dt.days

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Records", f"{total_rows:,}")
    c2.metric("Missing Values", f"{missing:,}")
    c3.metric("Duplicate Rows", f"{duplicates:,}")
    c4.metric(
        "Intervals Over 365 Days",
        f"{int((lead > 365).sum()):,}"
    )

    st.subheader("Recorded Order-to-Ship Interval")

    st.write(
        "This is the difference between Order Date and Ship Date. "
        "It is not verified delivery or transit time."
    )

    fig = px.histogram(
        x=lead.dropna(),
        nbins=40,
        title="Distribution of Recorded Order-to-Ship Intervals",
        labels={"x": "Days", "y": "Number of Records"}
    )

    st.plotly_chart(fig, width="stretch")

    st.subheader("Date Data Limitations")

    st.markdown("""
    <div class="notice">
        <b>Major data limitation identified</b><br><br>
        All 10,194 records have recorded Order-to-Ship intervals
        greater than 365 days.<br><br>
        Minimum interval: 904 days<br>
        Median interval: 1,274 days<br>
        Maximum interval: 1,642 days<br><br>
        The date pattern is highly unusual and its cause has not
        been established. These values must not be interpreted as
        actual shipping delays or delivery durations.
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Validation Summary")

    validation = pd.DataFrame({
        "Validation": [
            "Missing values",
            "Complete duplicate rows",
            "Duplicate Row IDs",
            "Financial reconciliation",
            "Product-to-factory mapping",
            "Date anomaly"
        ],
        "Result": [
            "0",
            "0",
            "0",
            "Sales = Gross Profit + Cost",
            "All 15 products mapped",
            "Requires source clarification"
        ]
    })

    st.dataframe(
        validation,
        width="stretch",
        hide_index=True
    )


# =====================================================
# 12. FOOTER
# =====================================================

st.markdown("---")

st.markdown(
    '<div class="footer">'
    'Nassau Candy Shipping Analytics | Data Analytics Project'
    '<br>Developed using Python, Pandas, Plotly and Streamlit'
    '</div>',
    unsafe_allow_html=True
)
