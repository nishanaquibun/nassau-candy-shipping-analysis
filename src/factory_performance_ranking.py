
import pandas as pd
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "factory_analysis.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "factory_performance_ranking.csv"
REPORT_FILE = BASE_DIR / "reports" / "factory_performance_ranking_report.txt"

# Load factory analysis
df = pd.read_csv(INPUT_FILE)

# Calculate performance metrics
total_sales = df["Total_Sales"].sum()
total_profit = df["Total_Profit"].sum()
total_units = df["Total_Units"].sum()

df["Gross_Profit_Margin_%"] = (
    df["Total_Profit"] / df["Total_Sales"] * 100
)

df["Sales_Contribution_%"] = (
    df["Total_Sales"] / total_sales * 100
)

df["Profit_Contribution_%"] = (
    df["Total_Profit"] / total_profit * 100
)

df["Units_Contribution_%"] = (
    df["Total_Units"] / total_units * 100
)

# Separate performance rankings
df["Sales_Rank"] = df["Total_Sales"].rank(
    ascending=False, method="min"
).astype(int)

df["Profit_Rank"] = df["Total_Profit"].rank(
    ascending=False, method="min"
).astype(int)

df["Margin_Rank"] = df["Gross_Profit_Margin_%"].rank(
    ascending=False, method="min"
).astype(int)

df["Units_Rank"] = df["Total_Units"].rank(
    ascending=False, method="min"
).astype(int)

df["Route_Coverage_Rank"] = df["Route_Combinations"].rank(
    ascending=False, method="min"
).astype(int)

# Sort by sales performance
df = df.sort_values("Sales_Rank")

# Round calculated values
percentage_columns = [
    "Gross_Profit_Margin_%",
    "Sales_Contribution_%",
    "Profit_Contribution_%",
    "Units_Contribution_%"
]

df[percentage_columns] = df[percentage_columns].round(2)

# Save detailed ranking CSV
df.to_csv(OUTPUT_FILE, index=False)

# Generate text report
report = []

report.append("=" * 65)
report.append("FACTORY PERFORMANCE RANKING REPORT")
report.append("=" * 65)

report.append(f"\nTotal Factories: {len(df)}")
report.append(f"Total Sales: {total_sales:,.2f}")
report.append(f"Total Gross Profit: {total_profit:,.2f}")
report.append(f"Total Units Sold: {total_units:,}")

report.append("\n\n1. SALES RANKING")
report.append("-" * 65)

for _, row in df.sort_values("Sales_Rank").iterrows():
    report.append(
        f"{row['Sales_Rank']}. {row['Factory']} "
        f"| Sales: {row['Total_Sales']:,.2f} "
        f"| Contribution: {row['Sales_Contribution_%']:.2f}%"
    )

report.append("\n\n2. GROSS PROFIT RANKING")
report.append("-" * 65)

for _, row in df.sort_values("Profit_Rank").iterrows():
    report.append(
        f"{row['Profit_Rank']}. {row['Factory']} "
        f"| Profit: {row['Total_Profit']:,.2f} "
        f"| Contribution: {row['Profit_Contribution_%']:.2f}%"
    )

report.append("\n\n3. PROFIT MARGIN RANKING")
report.append("-" * 65)

for _, row in df.sort_values("Margin_Rank").iterrows():
    report.append(
        f"{row['Margin_Rank']}. {row['Factory']} "
        f"| Gross Profit Margin: {row['Gross_Profit_Margin_%']:.2f}%"
    )

report.append("\n\n4. UNITS SOLD RANKING")
report.append("-" * 65)

for _, row in df.sort_values("Units_Rank").iterrows():
    report.append(
        f"{row['Units_Rank']}. {row['Factory']} "
        f"| Units: {row['Total_Units']:,} "
        f"| Contribution: {row['Units_Contribution_%']:.2f}%"
    )

report.append("\n\n5. ROUTE COVERAGE RANKING")
report.append("-" * 65)

for _, row in df.sort_values("Route_Coverage_Rank").iterrows():
    report.append(
        f"{row['Route_Coverage_Rank']}. {row['Factory']} "
        f"| Geographic Route Combinations: {row['Route_Combinations']:,}"
    )

report.append("\n\n6. KEY BUSINESS FINDINGS")
report.append("-" * 65)

top_sales = df.loc[df["Sales_Rank"].idxmin()]
top_profit = df.loc[df["Profit_Rank"].idxmin()]
top_margin = df.loc[df["Margin_Rank"].idxmin()]

report.append(
    f"Highest sales: {top_sales['Factory']} "
    f"({top_sales['Total_Sales']:,.2f})"
)

report.append(
    f"Highest gross profit: {top_profit['Factory']} "
    f"({top_profit['Total_Profit']:,.2f})"
)

report.append(
    f"Highest gross profit margin: {top_margin['Factory']} "
    f"({top_margin['Gross_Profit_Margin_%']:.2f}%)"
)

report.append(
    "\nNote: Gross profit margin is based on product financials, "
    "not shipping costs."
)

report.append(
    "Route combinations represent geographic coverage, not "
    "verified physical shipping routes."
)

report.append(
    "Recorded Order-to-Ship intervals are not actual transit "
    "or delivery times."
)

report.append("\n" + "=" * 65)
report.append("REPORT COMPLETED")
report.append("=" * 65)

# Save report
REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
REPORT_FILE.write_text("\n".join(report), encoding="utf-8")

# Display results
print("\nFACTORY PERFORMANCE RANKING COMPLETED!")
print("\nSales, Profit, Margin, Units and Route Coverage Rankings:\n")

print(
    df[[
        "Factory",
        "Sales_Rank",
        "Profit_Rank",
        "Gross_Profit_Margin_%",
        "Margin_Rank",
        "Units_Rank",
        "Route_Coverage_Rank"
    ]].to_string(index=False)
)

print("\nFiles generated:")
print(OUTPUT_FILE)
print(REPORT_FILE)
