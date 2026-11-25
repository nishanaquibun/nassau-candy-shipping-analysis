
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

# Light chart theme so chart text/backgrounds are readable
px.defaults.template = "plotly_white"

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

    /* Top header bar (Deploy / menu) */
    [data-testid="stHeader"] {
        background-color: #F3F6FA !important;
    }
    [data-testid="stHeader"] * {
        color: #252525 !important;
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

    /* KPI cards */
    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #DCE5EF;
        padding: 17px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.04);
    }

    /* KPI labels - dark charcoal */
    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] *,
    [data-testid="stMetric"] label,
    [data-testid="stMetric"] label * {
        color: #303030 !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }

    /* KPI values - dark navy */
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] * {
        color: #142B49 !important;
        opacity: 1 !important;
    }

    /* KPI delta (if used) keeps its own colour */

    /* Notice box */
    .notice {
        background-color: #FFF4DF;
        border-left: 5px solid #E5A000;
        padding: 14px;
        border-radius: 6px;
        color: #674B0B !important;
        margin: 12px 0;
    }
    .notice * {
        color: #674B0B !important;
    }

    /* Footer - dark grey */
    .footer {
        color: #303030 !important;
        text-align: center;
        font-size: 12px;
        padding: 25px 0 10px 0;
    }

    /* ALL headings in the main area (st.subheader, st.header, markdown) */
    [data-testid="stMain"] h1,
    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3,
    [data-testid="stMain"] h4,
    [data-testid="stMain"] h5,
    [data-testid="stMain"] h6,
    [data-testid="stHeading"],
    [data-testid="stHeading"] *,
    .stMarkdown h1,
    .stMarkdown h2,
    .stMarkdown h3,
    .stMarkdown h4 {
        color: #252525 !important;
    }

    /* Supporting text - dark grey (st.write, markdown, captions) */
    [data-testid="stMain"] .stMarkdown p,
    [data-testid="stMain"] .stMarkdown li,
    [data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stMain"] [data-testid="stCaptionContainer"],
    [data-testid="stMain"] [data-testid="stCaptionContainer"] * {
        color: #303030 !important;
    }

    /* Download button */
    [data-testid="stDownloadButton"] button {
        background-color: #183153;
        border: 1px solid #183153;
    }
    [data-testid="stDownloadButton"] button,
    [data-testid="stDownloadButton"] button * {
        color: white !important;
    }

    /* Alerts (warning / info / error) keep readable dark text */
    [data-testid="stAlert"] * {
        color: #252525 !important;
    }


    /* Extra-strong KPI label + heading rules */
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] div,
    [data-testid="stMetricLabel"] span {
        color: #303030 !important;
        opacity: 1 !important;
    }
    [data-testid="stMain"] h1 *,
    [data-testid="stMain"] h2 *,
    [data-testid="stMain"] h3 * {
        color: #252525 !important;
    }
    [data-testid="stMain"] [data-testid="stWidgetLabel"] * {
        color: #252525 !important;
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


def show_table(data, **kwargs):
    """Render a table with white background and dark text,
    regardless of the Streamlit theme."""
    styled = data.style.set_properties(**{
        "background-color": "#FFFFFF",
        "color": "#1F1F1F",
    })
    st.dataframe(styled, **kwargs)


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
    left.plotly_chart(fig1, width="stretch", theme=None)

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
    right.plotly_chart(fig2, width="stretch", theme=None)

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
    st.plotly_chart(fig3, width="stretch", theme=None)


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
    left.plotly_chart(fig1, width="stretch", theme=None)

    fig2 = px.bar(
        factory.sort_values("Profit", ascending=False),
        x="Factory",
        y="Profit",
        title="Factory-wise Gross Profit",
        color="Profit",
        color_continuous_scale="Teal"
    )
    right.plotly_chart(fig2, width="stretch", theme=None)

    fig3 = px.bar(
        factory.sort_values("Geographic_Lanes"),
        x="Geographic_Lanes",
        y="Factory",
        orientation="h",
        title="Geographic Coverage by Factory"
    )
    st.plotly_chart(fig3, width="stretch", theme=None)

    st.subheader("Factory Performance Table")
    show_table(
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
        "Explore factory-to-destination geographic lanes"
    )

    if filtered.empty:
        show_empty()
        st.stop()

    lanes = make_lane_data(filtered)

    c1, c2, c3 = st.columns(3)
    c1.metric("Geographic Lanes", f"{len(lanes):,}")
    c2.metric(
        "Provisional Shipments",
        f"{lanes['Provisional_Shipments'].sum():,}"
    )
    c3.metric("Factories", lanes["Factory"].nunique())

    st.markdown(
        '<div class="notice"><b>Interpretation note:</b> '
        'Shipment counts are provisional combinations based on '
        'Base Order ID, factory and destination. They are not '
        'verified physical shipment records.</div>',
        unsafe_allow_html=True
    )

    top_lanes = (
        lanes.nlargest(15, "Provisional_Shipments")
        .sort_values("Provisional_Shipments")
    )

    fig = px.bar(
        top_lanes,
        x="Provisional_Shipments",
        y="Lane",
        orientation="h",
        title="Top 15 Geographic Lanes by Provisional Shipment Volume",
        color="Provisional_Shipments",
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig, width="stretch", theme=None)

    st.subheader("Geographic Lane Details")

    show_table(
        lanes.sort_values(
            "Provisional_Shipments",
            ascending=False
        ),
        width="stretch",
        hide_index=True
    )

    csv = lanes.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Geographic Lane Data",
        data=csv,
        file_name="geographic_lane_analysis.csv",
        mime="text/csv"
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

    st.plotly_chart(fig, width="stretch", theme=None)

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

    st.plotly_chart(fig2, width="stretch", theme=None)

    st.subheader("Destination Performance Table")
    show_table(
        state.sort_values("Sales", ascending=False),
        width="stretch",
        hide_index=True
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
    left.plotly_chart(fig1, width="stretch", theme=None)

    fig2 = px.bar(
        mode.sort_values("Sales"),
        x="Sales",
        y="Ship Mode",
        orientation="h",
        title="Sales by Ship Mode",
        color="Sales",
        color_continuous_scale="Blues"
    )
    right.plotly_chart(fig2, width="stretch", theme=None)

    fig3 = px.bar(
        mode,
        x="Ship Mode",
        y="Profit",
        title="Gross Profit by Ship Mode"
    )
    st.plotly_chart(fig3, width="stretch", theme=None)

    st.subheader("Shipping Mode Details")
    show_table(
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

    st.plotly_chart(fig, width="stretch", theme=None)

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

    show_table(
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