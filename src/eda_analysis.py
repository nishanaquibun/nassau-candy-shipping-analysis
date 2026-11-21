
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "processed" / "nassau_candy_cleaned.csv"
REPORT_DIR = BASE_DIR / "reports"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

REPORT_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

# --------------------------------------------------
# 2. LOAD DATA
# --------------------------------------------------

df = pd.read_csv(DATA_FILE, low_memory=False)

print("Dataset loaded successfully!")
print("Rows:", len(df))
print("Columns:", len(df.columns))

# Convert numeric columns
numeric_columns = [
    "Sales",
    "Gross Profit",
    "Cost",
    "Units",
    "Order-to-Ship Lead Time"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# --------------------------------------------------
# 3. FACTORY PERFORMANCE
# --------------------------------------------------

factory_analysis = (
    df.groupby("Factory")
    .agg(
        Order_Lines=("Row ID", "count"),
        Unique_Base_Orders=("Base_Order_ID", "nunique"),
        Route_Combinations=("Route_Shipment_Key", "nunique"),
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Gross Profit", "sum"),
        Total_Cost=("Cost", "sum"),
        Total_Units=("Units", "sum"),
        Avg_Lead_Time=("Order-to-Ship Lead Time", "mean")
    )
    .reset_index()
    .sort_values("Route_Combinations", ascending=False)
)

factory_analysis.to_csv(
    PROCESSED_DIR / "factory_analysis.csv",
    index=False
)

# --------------------------------------------------
# 4. DESTINATION STATE ANALYSIS
# --------------------------------------------------

state_analysis = (
    df.groupby(["Country/Region", "State/Province"])
    .agg(
        Order_Lines=("Row ID", "count"),
        Unique_Base_Orders=("Base_Order_ID", "nunique"),
        Route_Combinations=("Route_Shipment_Key", "nunique"),
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Gross Profit", "sum"),
        Avg_Lead_Time=("Order-to-Ship Lead Time", "mean")
    )
    .reset_index()
    .sort_values("Route_Combinations", ascending=False)
)

state_analysis.to_csv(
    PROCESSED_DIR / "state_analysis.csv",
    index=False
)

# --------------------------------------------------
# 5. FACTORY-TO-DESTINATION ROUTE ANALYSIS
# --------------------------------------------------

route_analysis = (
    df.groupby([
        "Factory",
        "Country/Region",
        "State/Province",
        "City"
    ])
    .agg(
        Order_Lines=("Row ID", "count"),
        Unique_Base_Orders=("Base_Order_ID", "nunique"),
        Route_Combinations=("Route_Shipment_Key", "nunique"),
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Gross Profit", "sum"),
        Total_Units=("Units", "sum"),
        Avg_Lead_Time=("Order-to-Ship Lead Time", "mean"),
        Median_Lead_Time=("Order-to-Ship Lead Time", "median"),
        Max_Lead_Time=("Order-to-Ship Lead Time", "max")
    )
    .reset_index()
)

route_analysis = route_analysis.sort_values(
    "Avg_Lead_Time",
    ascending=False
)

route_analysis.to_csv(
    PROCESSED_DIR / "route_analysis.csv",
    index=False
)

# --------------------------------------------------
# 6. SHIP MODE ANALYSIS
# --------------------------------------------------

ship_mode_analysis = (
    df.groupby("Ship Mode")
    .agg(
        Order_Lines=("Row ID", "count"),
        Unique_Base_Orders=("Base_Order_ID", "nunique"),
        Route_Combinations=("Route_Shipment_Key", "nunique"),
        Avg_Lead_Time=("Order-to-Ship Lead Time", "mean"),
        Median_Lead_Time=("Order-to-Ship Lead Time", "median"),
        Min_Lead_Time=("Order-to-Ship Lead Time", "min"),
        Max_Lead_Time=("Order-to-Ship Lead Time", "max"),
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Gross Profit", "sum")
    )
    .reset_index()
    .sort_values("Avg_Lead_Time")
)

ship_mode_analysis.to_csv(
    PROCESSED_DIR / "ship_mode_analysis.csv",
    index=False
)

# --------------------------------------------------
# 7. YEAR-WISE ANALYSIS
# --------------------------------------------------

year_analysis = (
    df.groupby("Order_Year")
    .agg(
        Order_Lines=("Row ID", "count"),
        Unique_Base_Orders=("Base_Order_ID", "nunique"),
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Gross Profit", "sum"),
        Avg_Lead_Time=("Order-to-Ship Lead Time", "mean"),
        Median_Lead_Time=("Order-to-Ship Lead Time", "median")
    )
    .reset_index()
    .sort_values("Order_Year")
)

year_analysis.to_csv(
    PROCESSED_DIR / "year_analysis.csv",
    index=False
)

# --------------------------------------------------
# 8. OVERALL KPI SUMMARY
# --------------------------------------------------

kpis = {
    "Total Records": len(df),
    "Unique Full Order IDs": df["Order ID"].nunique(),
    "Unique Base Orders": df["Base_Order_ID"].nunique(),
    "Unique Factories": df["Factory"].nunique(),
    "Unique Destination States": df["State/Province"].nunique(),
    "Provisional Route Combinations": df["Route_Shipment_Key"].nunique(),
    "Total Sales": df["Sales"].sum(),
    "Total Gross Profit": df["Gross Profit"].sum(),
    "Total Cost": df["Cost"].sum(),
    "Total Units": df["Units"].sum(),
    "Average Order-to-Ship Lead Time": df["Order-to-Ship Lead Time"].mean(),
    "Median Order-to-Ship Lead Time": df["Order-to-Ship Lead Time"].median(),
    "Maximum Order-to-Ship Lead Time": df["Order-to-Ship Lead Time"].max(),
    "Records With Lead Time Above 365 Days":
        (df["Order-to-Ship Lead Time"] > 365).sum()
}

# --------------------------------------------------
# 9. SAVE EDA REPORT
# --------------------------------------------------

report = []

report.append("=" * 65)
report.append("NASSAU CANDY DISTRIBUTOR - EDA REPORT")
report.append("=" * 65)

report.append("\n1. OVERALL KPIs")
for key, value in kpis.items():
    if isinstance(value, float):
        report.append(f"{key}: {value:,.2f}")
    else:
        report.append(f"{key}: {value:,}")

report.append("\n2. FACTORY PERFORMANCE")
report.append(factory_analysis.to_string(index=False))

report.append("\n3. TOP 15 DESTINATION STATES")
report.append(state_analysis.head(15).to_string(index=False))

report.append("\n4. TOP 20 ROUTES BY AVERAGE LEAD TIME")
report.append(route_analysis.head(20).to_string(index=False))

report.append("\n5. SHIP MODE PERFORMANCE")
report.append(ship_mode_analysis.to_string(index=False))

report.append("\n6. YEAR-WISE PERFORMANCE")
report.append(year_analysis.to_string(index=False))

report.append("\n" + "=" * 65)
report.append("END OF EDA REPORT")
report.append("=" * 65)

report_file = REPORT_DIR / "eda_report.txt"

report_file.write_text(
    "\n".join(report),
    encoding="utf-8"
)

print("\nEDA ANALYSIS COMPLETED SUCCESSFULLY!")
print("Report saved:", report_file)

print("\nGenerated CSV files:")
print("- factory_analysis.csv")
print("- state_analysis.csv")
print("- route_analysis.csv")
print("- ship_mode_analysis.csv")
print("- year_analysis.csv")
