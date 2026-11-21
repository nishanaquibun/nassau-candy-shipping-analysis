
import pandas as pd
from pathlib import Path

# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "geographic_lane_analysis.csv"

OUTPUT_DIR = BASE_DIR / "data" / "processed"
REPORT_DIR = BASE_DIR / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

RANKING_FILE = OUTPUT_DIR / "route_performance_ranking.csv"
TOP_SHIPMENTS_FILE = OUTPUT_DIR / "top_10_lanes_by_shipments.csv"
TOP_SALES_FILE = OUTPUT_DIR / "top_10_lanes_by_sales.csv"
TOP_PROFIT_FILE = OUTPUT_DIR / "top_10_lanes_by_profit.csv"
LOW_VOLUME_FILE = OUTPUT_DIR / "lowest_10_lanes_by_volume.csv"
FACTORY_COVERAGE_FILE = OUTPUT_DIR / "factory_geographic_coverage.csv"

REPORT_FILE = REPORT_DIR / "route_performance_ranking_report.txt"


# ==========================================
# 2. LOAD DATA
# ==========================================

df = pd.read_csv(INPUT_FILE)

print("Geographic lane dataset loaded!")
print("Total geographic lanes:", len(df))


# ==========================================
# 3. DATA VALIDATION
# ==========================================

required_columns = [
    "Factory",
    "Country/Region",
    "State/Province",
    "City",
    "Order_Lines",
    "Total_Sales",
    "Total_Profit",
    "Total_Cost",
    "Total_Units",
    "Provisional_Shipments",
    "Gross_Profit_Margin_Percent"
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

numeric_columns = [
    "Order_Lines",
    "Total_Sales",
    "Total_Profit",
    "Total_Cost",
    "Total_Units",
    "Provisional_Shipments",
    "Gross_Profit_Margin_Percent"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="raise")

if df[numeric_columns].isnull().any().any():
    raise ValueError("Missing values found in required numeric columns.")

if (df["Total_Sales"] <= 0).any():
    raise ValueError("Non-positive sales found.")

if (df["Provisional_Shipments"] < 0).any():
    raise ValueError("Negative shipment count found.")

if df.duplicated(
    subset=["Factory", "Country/Region", "State/Province", "City"]
).any():
    raise ValueError("Duplicate geographic lane combinations found.")


# ==========================================
# 4. CREATE LANE IDENTIFICATION
# ==========================================

df["Lane"] = (
    df["Factory"].astype(str)
    + " -> "
    + df["City"].astype(str)
    + ", "
    + df["State/Province"].astype(str)
    + ", "
    + df["Country/Region"].astype(str)
)


# ==========================================
# 5. CALCULATE BUSINESS CONTRIBUTIONS
# ==========================================

total_sales = df["Total_Sales"].sum()
total_profit = df["Total_Profit"].sum()
total_shipments = df["Provisional_Shipments"].sum()
total_units = df["Total_Units"].sum()

df["Sales_Contribution_Percent"] = (
    df["Total_Sales"] / total_sales * 100
)

df["Profit_Contribution_Percent"] = (
    df["Total_Profit"] / total_profit * 100
)

df["Shipment_Contribution_Percent"] = (
    df["Provisional_Shipments"] / total_shipments * 100
)

# Recalculate margin from financial totals
df["Gross_Profit_Margin_Percent"] = (
    df["Total_Profit"] / df["Total_Sales"] * 100
)


# ==========================================
# 6. CREATE SEPARATE RANKINGS
# ==========================================

df["Shipment_Volume_Rank"] = (
    df["Provisional_Shipments"]
    .rank(ascending=False, method="min")
    .astype(int)
)

df["Sales_Rank"] = (
    df["Total_Sales"]
    .rank(ascending=False, method="min")
    .astype(int)
)

df["Profit_Rank"] = (
    df["Total_Profit"]
    .rank(ascending=False, method="min")
    .astype(int)
)

df["Profit_Margin_Rank"] = (
    df["Gross_Profit_Margin_Percent"]
    .rank(ascending=False, method="min")
    .astype(int)
)


# ==========================================
# 7. SELECT TOP AND LOW-VOLUME LANES
# ==========================================

top_shipments = df.sort_values(
    ["Provisional_Shipments", "Total_Sales"],
    ascending=[False, False]
).head(10).copy()

top_sales = df.sort_values(
    "Total_Sales",
    ascending=False
).head(10).copy()

top_profit = df.sort_values(
    "Total_Profit",
    ascending=False
).head(10).copy()

low_volume = df.sort_values(
    ["Provisional_Shipments", "Total_Sales"],
    ascending=[True, True]
).head(10).copy()


# ==========================================
# 8. FACTORY GEOGRAPHIC COVERAGE
# ==========================================

factory_coverage = (
    df.groupby("Factory")
    .agg(
        Geographic_Lanes=("City", "count"),
        Provisional_Shipments=("Provisional_Shipments", "sum"),
        Total_Sales=("Total_Sales", "sum"),
        Total_Profit=("Total_Profit", "sum"),
        Total_Units=("Total_Units", "sum")
    )
    .reset_index()
)

factory_coverage["Sales_Contribution_Percent"] = (
    factory_coverage["Total_Sales"] / total_sales * 100
)

factory_coverage["Shipment_Contribution_Percent"] = (
    factory_coverage["Provisional_Shipments"] / total_shipments * 100
)

factory_coverage = factory_coverage.sort_values(
    "Geographic_Lanes",
    ascending=False
)


# ==========================================
# 9. SAVE CSV OUTPUTS
# ==========================================

# Round percentage and financial fields for readability
percentage_columns = [
    "Gross_Profit_Margin_Percent",
    "Sales_Contribution_Percent",
    "Profit_Contribution_Percent",
    "Shipment_Contribution_Percent"
]

for col in percentage_columns:
    df[col] = df[col].round(2)

df.to_csv(RANKING_FILE, index=False)
top_shipments.to_csv(TOP_SHIPMENTS_FILE, index=False)
top_sales.to_csv(TOP_SALES_FILE, index=False)
top_profit.to_csv(TOP_PROFIT_FILE, index=False)
low_volume.to_csv(LOW_VOLUME_FILE, index=False)

factory_coverage["Sales_Contribution_Percent"] = (
    factory_coverage["Sales_Contribution_Percent"].round(2)
)

factory_coverage["Shipment_Contribution_Percent"] = (
    factory_coverage["Shipment_Contribution_Percent"].round(2)
)

factory_coverage.to_csv(FACTORY_COVERAGE_FILE, index=False)


# ==========================================
# 10. GENERATE REPORT
# ==========================================

report = []

report.append("=" * 75)
report.append("GEOGRAPHIC ROUTE PERFORMANCE RANKING REPORT")
report.append("=" * 75)

report.append(f"\nTotal Geographic Lanes: {len(df):,}")
report.append(f"Total Provisional Shipments: {total_shipments:,.0f}")
report.append(f"Total Sales: {total_sales:,.2f}")
report.append(f"Total Gross Profit: {total_profit:,.2f}")
report.append(f"Total Units: {total_units:,.0f}")


def add_lane_section(title, data, metric):
    report.append("\n\n" + title)
    report.append("-" * 75)

    for i, (_, row) in enumerate(data.iterrows(), start=1):
        report.append(
            f"{i}. {row['Lane']}\n"
            f"   Shipments: {row['Provisional_Shipments']:,.0f} | "
            f"Sales: {row['Total_Sales']:,.2f} | "
            f"Profit: {row['Total_Profit']:,.2f} | "
            f"Margin: {row['Gross_Profit_Margin_Percent']:.2f}%"
        )


add_lane_section(
    "1. TOP 10 LANES BY PROVISIONAL SHIPMENT VOLUME",
    top_shipments,
    "Provisional_Shipments"
)

add_lane_section(
    "2. TOP 10 LANES BY SALES",
    top_sales,
    "Total_Sales"
)

add_lane_section(
    "3. TOP 10 LANES BY GROSS PROFIT",
    top_profit,
    "Total_Profit"
)

add_lane_section(
    "4. LOWEST 10 LANES BY PROVISIONAL SHIPMENT VOLUME",
    low_volume,
    "Provisional_Shipments"
)


report.append("\n\n5. FACTORY GEOGRAPHIC COVERAGE")
report.append("-" * 75)

for _, row in factory_coverage.iterrows():
    report.append(
        f"{row['Factory']} | "
        f"Lanes: {row['Geographic_Lanes']} | "
        f"Shipments: {row['Provisional_Shipments']:,.0f} | "
        f"Sales: {row['Total_Sales']:,.2f}"
    )


report.append("\n\n6. KEY BUSINESS FINDINGS")
report.append("-" * 75)

best_sales_lane = top_sales.iloc[0]
best_profit_lane = top_profit.iloc[0]
busiest_lane = top_shipments.iloc[0]

report.append(
    f"Highest sales lane: {best_sales_lane['Lane']} "
    f"({best_sales_lane['Total_Sales']:,.2f})"
)

report.append(
    f"Highest profit lane: {best_profit_lane['Lane']} "
    f"({best_profit_lane['Total_Profit']:,.2f})"
)

report.append(
    f"Busiest lane: {busiest_lane['Lane']} "
    f"({busiest_lane['Provisional_Shipments']:,.0f} provisional shipments)"
)

report.append(
    "\nInterpretation notes:"
)

report.append(
    "- Provisional shipment counts are based on the existing "
    "Base_Order_ID and factory/destination grouping."
)

report.append(
    "- Geographic lanes represent factory-to-city combinations, "
    "not verified physical transport routes."
)

report.append(
    "- Low volume does not automatically mean poor performance; "
    "customer demand and product mix may affect volume."
)

report.append(
    "- Sales and gross profit are product financial measures, "
    "not shipping revenue or shipping cost."
)

report.append(
    "- Order-to-Ship intervals are not actual transit or delivery times."
)

report.append("\n" + "=" * 75)
report.append("ROUTE PERFORMANCE ANALYSIS COMPLETED")
report.append("=" * 75)

REPORT_FILE.write_text(
    "\n".join(report),
    encoding="utf-8"
)


# ==========================================
# 11. DISPLAY SUMMARY
# ==========================================

print("\nROUTE PERFORMANCE ANALYSIS COMPLETED!")

print("\nTOP 10 LANES BY PROVISIONAL SHIPMENTS")

print(
    top_shipments[
        ["Lane", "Provisional_Shipments", "Total_Sales", "Total_Profit"]
    ].to_string(index=False)
)

print("\nTOP 10 LANES BY SALES")

print(
    top_sales[
        ["Lane", "Total_Sales", "Total_Profit", "Provisional_Shipments"]
    ].to_string(index=False)
)

print("\nTOP 10 LANES BY GROSS PROFIT")

print(
    top_profit[
        ["Lane", "Total_Profit", "Total_Sales", "Provisional_Shipments"]
    ].to_string(index=False)
)

print("\nFACTORY GEOGRAPHIC COVERAGE")

print(factory_coverage.to_string(index=False))

print("\nGenerated files:")
print(RANKING_FILE)
print(TOP_SHIPMENTS_FILE)
print(TOP_SALES_FILE)
print(TOP_PROFIT_FILE)
print(LOW_VOLUME_FILE)
print(FACTORY_COVERAGE_FILE)
print(REPORT_FILE)
