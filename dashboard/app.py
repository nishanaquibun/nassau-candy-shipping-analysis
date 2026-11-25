from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# NASSAU CANDY | STATIC AGGREGATE DASHBOARD
# No raw CSV or private dataset is required at runtime.
# The figures below are precomputed aggregate results.
# ============================================================

st.set_page_config(
    page_title="Nassau Candy | Shipping Analytics",
    page_icon="ðŸ“¦",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#142B49"
BLUE = "#3B82B8"
LIGHT_BG = "#F3F6FA"
DARK_GREY = "#343A40"
MID_GREY = "#667085"

st.markdown(
    f"""
    <style>
      .stApp {{ background: {LIGHT_BG}; color: {DARK_GREY}; }}
      [data-testid="stSidebar"] {{ background: {NAVY}; }}
      [data-testid="stSidebar"] * {{ color: #FFFFFF !important; }}
      [data-testid="stMetric"] {{
        background: #FFFFFF; padding: 17px 18px; border-radius: 10px;
        border: 1px solid #E1E6ED; box-shadow: 0 1px 3px rgba(20,43,73,.06);
      }}
      [data-testid="stMetricLabel"] {{ color: {MID_GREY}; }}
      h1, h2, h3 {{ color: {NAVY}; }}
      .page-subtitle {{ color: {MID_GREY}; font-size: 0.95rem; }}
      .note {{
        background: #FFFFFF; border-left: 4px solid {BLUE};
        padding: 12px 15px; border-radius: 5px; margin: 10px 0 18px 0;
      }}
      .warning {{
        background: #FFF8E7; border-left: 4px solid #D69E2E;
        padding: 12px 15px; border-radius: 5px; margin: 10px 0 18px 0;
      }}
      div[data-testid="stDataFrame"] {{ background: #FFFFFF; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------- Embedded aggregate data -----------------------

factories = pd.DataFrame([
    {"Factory": "Lot's O' Nuts", "Order_Lines": 5692, "Unique_Base_Orders": 3652,
     "Route_Combinations": 3652, "Total_Sales": 76340.15, "Total_Profit": 52771.05,
     "Total_Cost": 23569.10, "Total_Units": 21412, "Gross_Profit_Margin_%": 69.13,
     "Sales_Contribution_%": 53.84, "Profit_Contribution_%": 56.47,
     "Units_Contribution_%": 55.39, "Sales_Rank": 1, "Profit_Rank": 1,
     "Margin_Rank": 1, "Units_Rank": 1},
    {"Factory": "Wicked Choccy's", "Order_Lines": 4152, "Unique_Base_Orders": 2965,
     "Route_Combinations": 2967, "Total_Sales": 55352.75, "Total_Profit": 36053.57,
     "Total_Cost": 19299.18, "Total_Units": 15863, "Gross_Profit_Margin_%": 65.13,
     "Sales_Contribution_%": 39.04, "Profit_Contribution_%": 38.58,
     "Units_Contribution_%": 41.04, "Sales_Rank": 2, "Profit_Rank": 2,
     "Margin_Rank": 2, "Units_Rank": 2},
    {"Factory": "Secret Factory", "Order_Lines": 217, "Unique_Base_Orders": 211,
     "Route_Combinations": 211, "Total_Sales": 8587.50, "Total_Profit": 4344.70,
     "Total_Cost": 4242.80, "Total_Units": 884, "Gross_Profit_Margin_%": 50.59,
     "Sales_Contribution_%": 6.06, "Profit_Contribution_%": 4.65,
     "Units_Contribution_%": 2.29, "Sales_Rank": 3, "Profit_Rank": 3,
     "Margin_Rank": 4, "Units_Rank": 3},
    {"Factory": "The Other Factory", "Order_Lines": 100, "Unique_Base_Orders": 98,
     "Route_Combinations": 98, "Total_Sales": 1282.25, "Total_Profit": 152.25,
     "Total_Cost": 1130.00, "Total_Units": 388, "Gross_Profit_Margin_%": 11.87,
     "Sales_Contribution_%": 0.90, "Profit_Contribution_%": 0.16,
     "Units_Contribution_%": 1.00, "Sales_Rank": 4, "Profit_Rank": 4,
     "Margin_Rank": 5, "Units_Rank": 4},
    {"Factory": "Sugar Shack", "Order_Lines": 33, "Unique_Base_Orders": 32,
     "Route_Combinations": 32, "Total_Sales": 220.98, "Total_Profit": 121.23,
     "Total_Cost": 99.75, "Total_Units": 107, "Gross_Profit_Margin_%": 54.86,
     "Sales_Contribution_%": 0.16, "Profit_Contribution_%": 0.13,
     "Units_Contribution_%": 0.28, "Sales_Rank": 5, "Profit_Rank": 5,
     "Margin_Rank": 3, "Units_Rank": 5},
])

coverage = pd.DataFrame([
    {"Factory": "Lot's O' Nuts", "Geographic_Lanes": 568, "Provisional_Shipments": 3652,
     "Total_Sales": 76340.15, "Total_Profit": 52771.05, "Total_Units": 21412,
     "Sales_Contribution_Percent": 53.84, "Shipment_Contribution_Percent": 52.47},
    {"Factory": "Wicked Choccy's", "Geographic_Lanes": 524, "Provisional_Shipments": 2967,
     "Total_Sales": 55352.75, "Total_Profit": 36053.57, "Total_Units": 15863,
     "Sales_Contribution_Percent": 39.04, "Shipment_Contribution_Percent": 42.63},
    {"Factory": "Secret Factory", "Geographic_Lanes": 107, "Provisional_Shipments": 211,
     "Total_Sales": 8587.50, "Total_Profit": 4344.70, "Total_Units": 884,
     "Sales_Contribution_Percent": 6.06, "Shipment_Contribution_Percent": 3.03},
    {"Factory": "The Other Factory", "Geographic_Lanes": 58, "Provisional_Shipments": 98,
     "Total_Sales": 1282.25, "Total_Profit": 152.25, "Total_Units": 388,
     "Sales_Contribution_Percent": 0.90, "Shipment_Contribution_Percent": 1.41},
    {"Factory": "Sugar Shack", "Geographic_Lanes": 21, "Provisional_Shipments": 32,
     "Total_Sales": 220.98, "Total_Profit": 121.23, "Total_Units": 107,
     "Sales_Contribution_Percent": 0.16, "Shipment_Contribution_Percent": 0.46},
])

countries = pd.DataFrame([
    {"Country/Region": "United States", "Destinations": 49, "Order_Lines": 9994,
     "Unique_Base_Orders": 5009, "Route_Combinations": 6825, "Total_Sales": 138830.34,
     "Total_Profit": 91508.23, "Gross_Profit_Margin_Percent": 65.91,
     "Sales_Contribution_Percent": 97.92, "Profit_Contribution_Percent": 97.93},
    {"Country/Region": "Canada", "Destinations": 10, "Order_Lines": 200,
     "Unique_Base_Orders": 102, "Route_Combinations": 135, "Total_Sales": 2953.29,
     "Total_Profit": 1934.57, "Gross_Profit_Margin_Percent": 65.51,
     "Sales_Contribution_Percent": 2.08, "Profit_Contribution_Percent": 2.07},
])

ship_modes = pd.DataFrame([
    {"Ship Mode": "Standard Class", "Order_Lines": 6120, "Unique_Base_Orders": 3068,
     "Route_Combinations": 4164, "Total_Sales": 85490.35, "Total_Profit": 56424.46},
    {"Ship Mode": "Second Class", "Order_Lines": 1979, "Unique_Base_Orders": 982,
     "Route_Combinations": 1351, "Total_Sales": 27860.22, "Total_Profit": 18306.52},
    {"Ship Mode": "Same Day", "Order_Lines": 547, "Unique_Base_Orders": 266,
     "Route_Combinations": 358, "Total_Sales": 7113.67, "Total_Profit": 4700.73},
    {"Ship Mode": "First Class", "Order_Lines": 1548, "Unique_Base_Orders": 795,
     "Route_Combinations": 1087, "Total_Sales": 21319.39, "Total_Profit": 14011.09},
])

years = pd.DataFrame([
    {"Order_Year": 2024, "Order_Lines": 4181, "Unique_Base_Orders": 2048,
     "Total_Sales": 57956.20, "Total_Profit": 38151.43},
    {"Order_Year": 2025, "Order_Lines": 6013, "Unique_Base_Orders": 3063,
     "Total_Sales": 83827.43, "Total_Profit": 55291.37},
])

lanes = pd.DataFrame([
    {"Factory": "Lot's O' Nuts", "City": "New York City", "State": "New York",
     "Order_Lines": 533, "Total_Sales": 7184.18, "Total_Profit": 4965.68,
     "Total_Units": 2014, "Provisional_Shipments": 332, "Margin_%": 69.12},
    {"Factory": "Lot's O' Nuts", "City": "Los Angeles", "State": "California",
     "Order_Lines": 405, "Total_Sales": 5473.75, "Total_Profit": 3778.85,
     "Total_Units": 1535, "Provisional_Shipments": 264, "Margin_%": 69.04},
    {"Factory": "Wicked Choccy's", "City": "Los Angeles", "State": "California",
     "Order_Lines": 322, "Total_Sales": 4439.50, "Total_Profit": 2891.26,
     "Total_Units": 1276, "Provisional_Shipments": 229, "Margin_%": 65.13},
    {"Factory": "Wicked Choccy's", "City": "New York City", "State": "New York",
     "Order_Lines": 342, "Total_Sales": 4344.50, "Total_Profit": 2829.66,
     "Total_Units": 1246, "Provisional_Shipments": 241, "Margin_%": 65.13},
    {"Factory": "Lot's O' Nuts", "City": "Philadelphia", "State": "Pennsylvania",
     "Order_Lines": 301, "Total_Sales": 3948.79, "Total_Profit": 2726.29,
     "Total_Units": 1107, "Provisional_Shipments": 190, "Margin_%": 69.04},
    {"Factory": "Lot's O' Nuts", "City": "San Francisco", "State": "California",
     "Order_Lines": 284, "Total_Sales": 3764.61, "Total_Profit": 2603.11,
     "Total_Units": 1057, "Provisional_Shipments": 183, "Margin_%": 69.15},
    {"Factory": "Lot's O' Nuts", "City": "Seattle", "State": "Washington",
     "Order_Lines": 233, "Total_Sales": 3036.40, "Total_Profit": 2101.60,
     "Total_Units": 852, "Provisional_Shipments": 147, "Margin_%": 69.21},
    {"Factory": "Wicked Choccy's", "City": "San Francisco", "State": "California",
     "Order_Lines": 211, "Total_Sales": 2938.25, "Total_Profit": 1914.51,
     "Total_Units": 835, "Provisional_Shipments": 151, "Margin_%": 65.16},
    {"Factory": "Lot's O' Nuts", "City": "Houston", "State": "Texas",
     "Order_Lines": 215, "Total_Sales": 2881.41, "Total_Profit": 1989.01,
     "Total_Units": 808, "Provisional_Shipments": 134, "Margin_%": 69.03},
    {"Factory": "Wicked Choccy's", "City": "Philadelphia", "State": "Pennsylvania",
     "Order_Lines": 208, "Total_Sales": 2585.00, "Total_Profit": 1684.00,
     "Total_Units": 738, "Provisional_Shipments": 157, "Margin_%": 65.15},
])

destinations = pd.DataFrame([
    {"Destination": "California, United States", "Order_Lines": 2001,
     "Unique_Base_Orders": 1021, "Total_Sales": 27917.40, "Total_Profit": 18479.42,
     "Margin_%": 66.19, "Sales_Contribution_%": 19.69},
    {"Destination": "New York, United States", "Order_Lines": 1128,
     "Unique_Base_Orders": 562, "Total_Sales": 15541.03, "Total_Profit": 10222.44,
     "Margin_%": 65.78, "Sales_Contribution_%": 10.96},
    {"Destination": "Texas, United States", "Order_Lines": 985,
     "Unique_Base_Orders": 487, "Total_Sales": 13416.09, "Total_Profit": 8909.53,
     "Margin_%": 66.41, "Sales_Contribution_%": 9.46},
    {"Destination": "Pennsylvania, United States", "Order_Lines": 587,
     "Unique_Base_Orders": 288, "Total_Sales": 8027.03, "Total_Profit": 5225.47,
     "Margin_%": 65.10, "Sales_Contribution_%": 5.66},
    {"Destination": "Washington, United States", "Order_Lines": 506,
     "Unique_Base_Orders": 256, "Total_Sales": 6921.15, "Total_Profit": 4566.64,
     "Margin_%": 65.98, "Sales_Contribution_%": 4.88},
    {"Destination": "Illinois, United States", "Order_Lines": 492,
     "Unique_Base_Orders": 276, "Total_Sales": 6898.96, "Total_Profit": 4557.68,
     "Margin_%": 66.06, "Sales_Contribution_%": 4.87},
    {"Destination": "Ohio, United States", "Order_Lines": 469,
     "Unique_Base_Orders": 236, "Total_Sales": 6768.95, "Total_Profit": 4413.03,
     "Margin_%": 65.20, "Sales_Contribution_%": 4.77},
    {"Destination": "Florida, United States", "Order_Lines": 383,
     "Unique_Base_Orders": 200, "Total_Sales": 4804.02, "Total_Profit": 3207.11,
     "Margin_%": 66.76, "Sales_Contribution_%": 3.39},
    {"Destination": "Arizona, United States", "Order_Lines": 224,
     "Unique_Base_Orders": 108, "Total_Sales": 3587.55, "Total_Profit": 2290.11,
     "Margin_%": 63.83, "Sales_Contribution_%": 2.53},
    {"Destination": "North Carolina, United States", "Order_Lines": 249,
     "Unique_Base_Orders": 136, "Total_Sales": 3450.86, "Total_Profit": 2331.16,
     "Margin_%": 67.55, "Sales_Contribution_%": 2.43},
])

# ----------------------- Helpers -----------------------

def money(value: float) -> str:
    return f"${value:,.2f}"

def metric_row(items):
    cols = st.columns(len(items))
    for col, (label, value, help_text) in zip(cols, items):
        col.metric(label, value, help=help_text)

def section_intro(text: str):
    st.markdown(f'<p class="page-subtitle">{text}</p>', unsafe_allow_html=True)

# ----------------------- Sidebar -----------------------

st.sidebar.title("ðŸ“¦ Nassau Candy")
st.sidebar.caption("Shipping Route & Business Analytics")
page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Executive Overview",
        "Factory Performance",
        "Geographic Route Analysis",
        "Destination Analysis",
        "Destination Performance",
        "Shipping Mode Analysis",
        "Data Quality",
    ],
)
st.sidebar.markdown("---")
st.sidebar.caption("Analysis period: 2024â€“2025")
st.sidebar.caption("Dataset: 10,194 order lines")
st.sidebar.caption("Aggregate-only dashboard")

# ----------------------- Page 1 -----------------------

if page == "Executive Overview":
    st.title("Nassau Candy | Shipping Analytics")
    section_intro("Executive overview of factory performance, destination markets and shipping-mode activity.")
    metric_row([
        ("Total Sales", "$141,783.63", "Sum of recorded sales"),
        ("Gross Profit", "$93,442.80", "Sum of recorded gross profit"),
        ("Gross Profit Margin", "65.9%", "Gross profit divided by sales"),
        ("Order Lines", "10,194", "Rows in the source dataset"),
    ])
    st.markdown("")
    metric_row([
        ("Units Sold", "38,654", "Recorded units"),
        ("Factories", "5", "Manufacturing facilities"),
        ("Destinations", "59", "State/province destinations"),
        ("Countries", "2", "United States and Canada"),
    ])
    st.markdown("### Sales and profit by factory")
    fig = px.bar(
        factories.sort_values("Total_Sales", ascending=True),
        x="Total_Sales", y="Factory", orientation="h", color="Total_Profit",
        color_continuous_scale="Blues", text_auto=",.0f",
        labels={"Total_Sales": "Sales (USD)", "Factory": "", "Total_Profit": "Gross profit (USD)"},
    )
    fig.update_layout(height=390, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, width="stretch")
    left, right = st.columns(2)
    with left:
        st.markdown("### Sales by country")
        fig_country = px.pie(
            countries, names="Country/Region", values="Total_Sales", hole=0.55,
            color_discrete_sequence=[NAVY, BLUE],
        )
        fig_country.update_layout(height=330, margin=dict(t=10, b=10))
        st.plotly_chart(fig_country, width="stretch")
    with right:
        st.markdown("### Sales by order year")
        fig_year = px.bar(
            years, x="Order_Year", y="Total_Sales", text_auto=",.0f",
            color="Order_Year", color_continuous_scale="Blues",
            labels={"Order_Year": "Order year", "Total_Sales": "Sales (USD)"},
        )
        fig_year.update_layout(height=330, showlegend=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig_year, width="stretch")
    st.markdown(
        '<div class="note"><b>Key insight:</b> Lot\'s O\' Nuts contributes 53.84% of total sales '
        'and 56.47% of gross profit. The United States accounts for 97.92% of sales.</div>',
        unsafe_allow_html=True,
    )

# ----------------------- Page 2 -----------------------

elif page == "Factory Performance":
    st.title("Factory Performance")
    section_intro("Compare factory-level sales, gross profit, margin, units and geographic reach.")
    metric_row([
        ("Leading factory", "Lot's O' Nuts", "Highest sales and gross profit"),
        ("Leading sales share", "53.84%", "Lot's O' Nuts share of total sales"),
        ("Leading margin", "69.13%", "Lot's O' Nuts gross profit margin"),
    ])
    metric = st.selectbox("Rank factories by", ["Total_Sales", "Total_Profit", "Gross_Profit_Margin_%", "Total_Units"])
    chart_data = factories.sort_values(metric, ascending=True)
    fig = px.bar(
        chart_data, x=metric, y="Factory", orientation="h", text=metric,
        color=metric, color_continuous_scale="Blues",
        labels={metric: metric.replace("_", " "), "Factory": ""},
    )
    fig.update_layout(height=400, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, width="stretch")
    st.markdown("### Factory performance table")
    display = factories[[
        "Factory", "Order_Lines", "Total_Sales", "Total_Profit",
        "Gross_Profit_Margin_%", "Total_Units", "Sales_Contribution_%"
    ]].copy()
    display = display.rename(columns={
        "Order_Lines": "Order lines", "Total_Sales": "Sales (USD)",
        "Total_Profit": "Gross profit (USD)", "Gross_Profit_Margin_%": "Gross margin (%)",
        "Total_Units": "Units", "Sales_Contribution_%": "Sales share (%)"
    })
    st.dataframe(display, width="stretch", hide_index=True)
    st.markdown("### Geographic coverage by factory")
    cov_fig = px.bar(
        coverage.sort_values("Geographic_Lanes"), x="Geographic_Lanes", y="Factory",
        orientation="h", text="Geographic_Lanes", color="Geographic_Lanes",
        color_continuous_scale="Blues",
        labels={"Geographic_Lanes": "Factory-to-city combinations", "Factory": ""},
    )
    cov_fig.update_layout(height=350, margin=dict(l=10, r=10, t=15, b=10))
    st.plotly_chart(cov_fig, width="stretch")
    st.caption("Geographic lanes are distinct factory-to-city combinations, not verified carrier routes.")

# ----------------------- Page 3 -----------------------

elif page == "Geographic Route Analysis":
    st.title("Geographic Route Analysis")
    section_intro("Explore the highest-sales factory-to-city lanes and factory geographic coverage.")
    st.markdown(
        '<div class="warning"><b>Interpretation note:</b> A geographic lane represents a factory-to-city '
        'combination. Provisional shipment groupings are an analytical proxy, not verified physical shipments.</div>',
        unsafe_allow_html=True,
    )
    selected_factory = st.selectbox("Factory", ["All factories"] + factories["Factory"].tolist())
    lane_view = lanes.copy()
    if selected_factory != "All factories":
        lane_view = lane_view[lane_view["Factory"] == selected_factory]
    st.markdown("### Highest-sales lanes")
    fig = px.bar(
        lane_view.sort_values("Total_Sales"), x="Total_Sales",
        y="City", orientation="h", color="Factory", text_auto=",.0f",
        hover_data=["State", "Order_Lines", "Provisional_Shipments", "Total_Profit"],
        labels={"Total_Sales": "Sales (USD)", "City": "Destination city"},
    )
    fig.update_layout(height=430, margin=dict(l=10, r=10, t=15, b=10))
    st.plotly_chart(fig, width="stretch")
    st.dataframe(
        lane_view[["Factory", "City", "State", "Order_Lines", "Provisional_Shipments",
                   "Total_Sales", "Total_Profit"]],
        width="stretch", hide_index=True,
    )
    st.markdown("### Factory geographic coverage")
    st.dataframe(
        coverage[["Factory", "Geographic_Lanes", "Provisional_Shipments",
                  "Sales_Contribution_Percent"]],
        width="stretch", hide_index=True,
    )

# ----------------------- Page 4 -----------------------

elif page == "Destination Analysis":
    st.title("Destination Analysis")
    section_intro("Country-level distribution of order lines, sales, gross profit and destination coverage.")
    metric_row([
        ("United States sales share", "97.92%", "Share of total recorded sales"),
        ("US destinations", "49", "State/province destinations"),
        ("Canada destinations", "10", "State/province destinations"),
    ])
    fig = px.bar(
        countries, x="Country/Region", y="Total_Sales", color="Country/Region",
        text_auto=",.0f", color_discrete_sequence=[NAVY, BLUE],
        labels={"Total_Sales": "Sales (USD)", "Country/Region": ""},
    )
    fig.update_layout(height=350, showlegend=False, margin=dict(t=15, b=10))
    st.plotly_chart(fig, width="stretch")
    st.markdown("### Country performance")
    st.dataframe(countries.rename(columns={
        "Country/Region": "Country", "Destinations": "Destinations",
        "Order_Lines": "Order lines", "Unique_Base_Orders": "Unique base orders",
        "Total_Sales": "Sales (USD)", "Total_Profit": "Gross profit (USD)",
        "Gross_Profit_Margin_Percent": "Gross margin (%)",
        "Sales_Contribution_Percent": "Sales share (%)",
    })[["Country", "Destinations", "Order lines", "Unique base orders",
        "Sales (USD)", "Gross profit (USD)", "Gross margin (%)", "Sales share (%)"]],
        width="stretch", hide_index=True)
    st.caption("Country totals are based on the provided aggregate analysis.")

# ----------------------- Page 5 -----------------------

elif page == "Destination Performance":
    st.title("Destination Performance")
    section_intro("Rank the ten highest-sales state/province destinations in the provided summary.")
    sort_by = st.selectbox("Sort destinations by", ["Total_Sales", "Total_Profit", "Order_Lines", "Margin_%"])
    dest_view = destinations.sort_values(sort_by, ascending=False)
    fig = px.bar(
        dest_view.sort_values(sort_by), x=sort_by, y="Destination",
        orientation="h", color=sort_by, color_continuous_scale="Blues",
        text=sort_by, labels={sort_by: sort_by.replace("_", " "), "Destination": ""},
    )
    fig.update_layout(height=470, margin=dict(l=10, r=10, t=15, b=10))
    st.plotly_chart(fig, width="stretch")
    st.markdown("### Top 10 destination table")
    st.dataframe(
        dest_view.rename(columns={
            "Order_Lines": "Order lines", "Unique_Base_Orders": "Unique base orders",
            "Total_Sales": "Sales (USD)", "Total_Profit": "Gross profit (USD)",
            "Margin_%": "Gross margin (%)", "Sales_Contribution_%": "Sales share (%)",
        }),
        width="stretch", hide_index=True,
    )
    st.caption("This page displays the top 10 destinations by sales, not all 59 destinations.")

# ----------------------- Page 6 -----------------------

elif page == "Shipping Mode Analysis":
    st.title("Shipping Mode Analysis")
    section_intro("Compare recorded sales, gross profit and order-line activity across shipping modes.")
    fig = px.bar(
        ship_modes.sort_values("Total_Sales"), x="Total_Sales", y="Ship Mode",
        orientation="h", color="Total_Profit", color_continuous_scale="Blues",
        text_auto=",.0f",
        labels={"Total_Sales": "Sales (USD)", "Ship Mode": "", "Total_Profit": "Gross profit (USD)"},
    )
    fig.update_layout(height=400, margin=dict(l=10, r=10, t=15, b=10))
    st.plotly_chart(fig, width="stretch")
    st.markdown("### Shipping mode summary")
    st.dataframe(ship_modes.rename(columns={
        "Ship Mode": "Shipping mode", "Order_Lines": "Order lines",
        "Unique_Base_Orders": "Unique base orders", "Route_Combinations": "Route combinations",
        "Total_Sales": "Sales (USD)", "Total_Profit": "Gross profit (USD)",
    }), width="stretch", hide_index=True)
    st.markdown(
        '<div class="note">Standard Class has the highest recorded sales ($85,490.35) and gross profit '
        '($56,424.46) among the four shipping modes.</div>',
        unsafe_allow_html=True,
    )
    st.caption("No freight-cost field is available; product cost is not shipping cost.")

# ----------------------- Page 7 -----------------------

elif page == "Data Quality":
    st.title("Data Quality & Methodology")
    section_intro("Important validation results and interpretation limits for this analysis.")
    metric_row([
        ("Source rows", "10,194", "Original dataset row count"),
        ("Missing values", "0", "No missing values reported"),
        ("Duplicate rows", "0", "No complete duplicate rows reported"),
        ("Financial check", "Passed", "Sales = Gross Profit + Cost within $0.01"),
    ])
    st.markdown("### Validation summary")
    checks = pd.DataFrame([
        {"Check": "Missing values", "Result": "0 missing values", "Status": "Passed"},
        {"Check": "Complete duplicate rows", "Result": "0 duplicate rows", "Status": "Passed"},
        {"Check": "Row ID uniqueness", "Result": "No duplicate Row IDs", "Status": "Passed"},
        {"Check": "Factory mapping", "Result": "15 products mapped to 5 factories", "Status": "Passed"},
        {"Check": "Financial reconciliation", "Result": "Sales = Gross Profit + Cost within $0.01", "Status": "Passed"},
        {"Check": "Date interval review", "Result": "All 10,194 Order Date-to-Ship Date intervals exceed 365 days", "Status": "Warning"},
    ])
    st.dataframe(checks, width="stretch", hide_index=True)
    st.markdown("### Critical date anomaly")
    st.warning(
        "All 10,194 recorded Order Date-to-Ship Date intervals are greater than 365 days "
        "(range: 904â€“1,642 days). The cause is unknown. These values must not be interpreted "
        "as actual transit time, delivery delay or carrier performance."
    )
    st.markdown("### Scope and limitations")
    st.markdown("""
    - No actual delivery date is available.
    - No freight-cost field is available. Cost and gross profit are product financial measures, not shipping costs.
    - Provisional shipment groupings are derived analytical proxies, not verified physical shipment records.
    - Geographic lanes represent factory-to-city combinations, not actual carrier routes.
    - This dashboard uses precomputed aggregate results; it does not provide transaction-level filtering.
    - Some pages show top-10 summaries rather than the complete destination or lane population.
    """)
    st.markdown("### Recommended interpretation")
    st.info(
        "Use this dashboard to compare recorded sales, gross profit, factory contribution, "
        "destination concentration and shipping-mode activity. Do not use it to claim delivery "
        "speed, freight-cost efficiency or verified carrier-route performance."
    )

st.sidebar.markdown("---")
st.sidebar.caption("Prepared for academic/internship analysis")
st.sidebar.caption("Aggregate values only â€¢ No raw CSV loaded")

