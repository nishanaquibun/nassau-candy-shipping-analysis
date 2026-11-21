
import pandas as pd
from pathlib import Path

# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "state_analysis.csv"

OUTPUT_DIR = BASE_DIR / "data" / "processed"
REPORT_DIR = BASE_DIR / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

RANKING_FILE = OUTPUT_DIR / "destination_performance_ranking.csv"
TOP_SALES_FILE = OUTPUT_DIR / "top_10_destinations_by_sales.csv"
TOP_PROFIT_FILE = OUTPUT_DIR / "top_10_destinations_by_profit.csv"
TOP_ORDERS_FILE = OUTPUT_DIR / "top_10_destinations_by_orders.csv"
LOW_SALES_FILE = OUTPUT_DIR / "lowest_10_destinations_by_sales.csv"
COUNTRY_FILE = OUTPUT_DIR / "country_performance_analysis.csv"

REPORT_FILE = REPORT_DIR / "destination_performance_report.txt"


# ==========================================
# 2. LOAD DATA
# ==========================================

df = pd.read_csv(INPUT_FILE)

print("Destination dataset loaded successfully!")
print("Total destination records:", len(df))


# ==========================================
# 3. VALIDATE DATA
# ==========================================

required_columns = [
    "Country/Region",
    "State/Province",
    "Order_Lines",
    "Unique_Base_Orders",
    "Route_Combinations",
    "Total_Sales",
    "Total_Profit"
]

missing = [col for col in required_columns if col not in df.columns]

if missing:
    raise ValueError(f"Missing columns: {missing}")

numeric_columns = [
    "Order_Lines",
    "Unique_Base_Orders",
    "Route_Combinations",
    "Total_Sales",
    "Total_Profit"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="raise")

if df[numeric_columns].isnull().any().any():
    raise ValueError("Missing values found in numeric columns.")

if df.duplicated(
    subset=["Country/Region", "State/Province"]
).any():
    raise ValueError("Duplicate country-state combinations found.")

if (df["Total_Sales"] <= 0).any():
    raise ValueError("Non-positive sales found.")

if (df["Total_Profit"] < 0).any():
    raise ValueError("Negative gross profit found.")


# ==========================================
# 4. CREATE DESTINATION LABEL
# ==========================================

df["Destination"] = (
    df["State/Province"].astype(str)
    + ", "
    + df["Country/Region"].astype(str)
)


# ==========================================
# 5. CALCULATE CONTRIBUTIONS
# ==========================================

total_sales = df["Total_Sales"].sum()
total_profit = df["Total_Profit"].sum()
total_orders = df["Unique_Base_Orders"].sum()
total_lines = df["Order_Lines"].sum()

df["Gross_Profit_Margin_Percent"] = (
    df["Total_Profit"] / df["Total_Sales"] * 100
)

df["Sales_Contribution_Percent"] = (
    df["Total_Sales"] / total_sales * 100
)

df["Profit_Contribution_Percent"] = (
    df["Total_Profit"] / total_profit * 100
)

df["Order_Contribution_Percent"] = (
    df["Unique_Base_Orders"] / total_orders * 100
)


# ==========================================
# 6. CREATE DESTINATION RANKINGS
# ==========================================

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

df["Order_Volume_Rank"] = (
    df["Unique_Base_Orders"]
    .rank(ascending=False, method="min")
    .astype(int)
)

df["Margin_Rank"] = (
    df["Gross_Profit_Margin_Percent"]
    .rank(ascending=False, method="min")
    .astype(int)
)


# ==========================================
# 7. SELECT TOP AND LOW DESTINATIONS
# ==========================================

top_sales = df.sort_values(
    "Total_Sales", ascending=False
).head(10).copy()

top_profit = df.sort_values(
    "Total_Profit", ascending=False
).head(10).copy()

top_orders = df.sort_values(
    "Unique_Base_Orders", ascending=False
).head(10).copy()

low_sales = df.sort_values(
    "Total_Sales", ascending=True
).head(10).copy()


# ==========================================
# 8. COUNTRY-WISE ANALYSIS
# ==========================================

country_analysis = (
    df.groupby("Country/Region")
    .agg(
        Destinations=("State/Province", "nunique"),
        Order_Lines=("Order_Lines", "sum"),
        Unique_Base_Orders=("Unique_Base_Orders", "sum"),
        Route_Combinations=("Route_Combinations", "sum"),
        Total_Sales=("Total_Sales", "sum"),
        Total_Profit=("Total_Profit", "sum")
    )
    .reset_index()
)

country_analysis["Gross_Profit_Margin_Percent"] = (
    country_analysis["Total_Profit"]
    / country_analysis["Total_Sales"] * 100
)

country_analysis["Sales_Contribution_Percent"] = (
    country_analysis["Total_Sales"] / total_sales * 100
)

country_analysis["Profit_Contribution_Percent"] = (
    country_analysis["Total_Profit"] / total_profit * 100
)

country_analysis = country_analysis.sort_values(
    "Total_Sales", ascending=False
)


# ==========================================
# 9. ROUND PERCENTAGES
# ==========================================

percentage_columns = [
    "Gross_Profit_Margin_Percent",
    "Sales_Contribution_Percent",
    "Profit_Contribution_Percent",
    "Order_Contribution_Percent"
]

for col in percentage_columns:
    df[col] = df[col].round(2)

country_percentage_columns = [
    "Gross_Profit_Margin_Percent",
    "Sales_Contribution_Percent",
    "Profit_Contribution_Percent"
]

for col in country_percentage_columns:
    country_analysis[col] = country_analysis[col].round(2)


# ==========================================
# 10. SAVE CSV FILES
# ==========================================

df.to_csv(RANKING_FILE, index=False)
top_sales.to_csv(TOP_SALES_FILE, index=False)
top_profit.to_csv(TOP_PROFIT_FILE, index=False)
top_orders.to_csv(TOP_ORDERS_FILE, index=False)
low_sales.to_csv(LOW_SALES_FILE, index=False)
country_analysis.to_csv(COUNTRY_FILE, index=False)


# ==========================================
# 11. GENERATE TEXT REPORT
# ==========================================

report = []

report.append("=" * 75)
report.append("DESTINATION PERFORMANCE ANALYSIS REPORT")
report.append("=" * 75)

report.append(f"\nTotal Destinations: {len(df)}")
report.append(f"Total Sales: {total_sales:,.2f}")
report.append(f"Total Gross Profit: {total_profit:,.2f}")
report.append(f"Total Unique Base Orders (summed): {total_orders:,}")
report.append(f"Total Order Lines: {total_lines:,}")


def add_section(title, data, metric):
    report.append("\n\n" + title)
    report.append("-" * 75)

    for i, (_, row) in enumerate(data.iterrows(), start=1):
        report.append(
            f"{i}. {row['Destination']}\n"
            f"   {metric}: {row[metric]:,.2f} | "
            f"Sales: {row['Total_Sales']:,.2f} | "
            f"Profit: {row['Total_Profit']:,.2f} | "
            f"Orders: {row['Unique_Base_Orders']:,}"
        )


add_section(
    "1. TOP 10 DESTINATIONS BY SALES",
    top_sales,
    "Total_Sales"
)

add_section(
    "2. TOP 10 DESTINATIONS BY GROSS PROFIT",
    top_profit,
    "Total_Profit"
)

add_section(
    "3. TOP 10 DESTINATIONS BY UNIQUE BASE ORDERS",
    top_orders,
    "Unique_Base_Orders"
)

add_section(
    "4. LOWEST 10 DESTINATIONS BY SALES",
    low_sales,
    "Total_Sales"
)


report.append("\n\n5. COUNTRY-WISE PERFORMANCE")
report.append("-" * 75)

for _, row in country_analysis.iterrows():
    report.append(
        f"{row['Country/Region']} | "
        f"Destinations: {row['Destinations']} | "
        f"Sales: {row['Total_Sales']:,.2f} | "
        f"Profit: {row['Total_Profit']:,.2f} | "
        f"Sales Contribution: {row['Sales_Contribution_Percent']:.2f}%"
    )


report.append("\n\n6. KEY BUSINESS FINDINGS")
report.append("-" * 75)

best_sales = top_sales.iloc[0]
best_profit = top_profit.iloc[0]
best_orders = top_orders.iloc[0]

report.append(
    f"Highest sales destination: {best_sales['Destination']} "
    f"({best_sales['Total_Sales']:,.2f})"
)

report.append(
    f"Highest profit destination: {best_profit['Destination']} "
    f"({best_profit['Total_Profit']:,.2f})"
)

report.append(
    f"Highest order-volume destination: {best_orders['Destination']} "
    f"({best_orders['Unique_Base_Orders']:,} unique base orders)"
)

report.append("\nInterpretation notes:")

report.append(
    "- Unique Base Orders are summed across destinations. "
    "Each base order is expected to belong to one destination."
)

report.append(
    "- Route Combinations measure geographic factory/city coverage, "
    "not shipment volume."
)

report.append(
    "- Low sales do not automatically indicate poor performance."
)

report.append(
    "- Gross profit and sales are product financial measures, "
    "not shipping revenue or shipping cost."
)

report.append(
    "- Recorded Order-to-Ship intervals are not actual transit "
    "or delivery times and are not used for destination rankings."
)

report.append("\n" + "=" * 75)
report.append("DESTINATION ANALYSIS COMPLETED")
report.append("=" * 75)

REPORT_FILE.write_text(
    "\n".join(report),
    encoding="utf-8"
)


# ==========================================
# 12. DISPLAY RESULTS
# ==========================================

print("\nDESTINATION PERFORMANCE ANALYSIS COMPLETED!")

print("\nTOP 10 DESTINATIONS BY SALES")

print(
    top_sales[
        ["Destination", "Total_Sales", "Total_Profit"]
    ].to_string(index=False)
)

print("\nTOP 10 DESTINATIONS BY GROSS PROFIT")

print(
    top_profit[
        ["Destination", "Total_Profit", "Total_Sales"]
    ].to_string(index=False)
)

print("\nTOP 10 DESTINATIONS BY UNIQUE BASE ORDERS")

print(
    top_orders[
        ["Destination", "Unique_Base_Orders", "Order_Lines"]
    ].to_string(index=False)
)

print("\nCOUNTRY-WISE PERFORMANCE")

print(country_analysis.to_string(index=False))

print("\nGenerated files:")
print(RANKING_FILE)
print(TOP_SALES_FILE)
print(TOP_PROFIT_FILE)
print(TOP_ORDERS_FILE)
print(LOW_SALES_FILE)
print(COUNTRY_FILE)
print(REPORT_FILE)
