
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "processed" / "nassau_candy_cleaned.csv"
REPORT_FILE = BASE_DIR / "reports" / "eda_refinement_report.txt"
LANE_FILE = BASE_DIR / "data" / "processed" / "geographic_lane_analysis.csv"

df = pd.read_csv(DATA_FILE, low_memory=False)

# Parse dates
df["Order_Date_Parsed"] = pd.to_datetime(
    df["Order_Date_Parsed"], errors="coerce"
)
df["Ship_Date_Parsed"] = pd.to_datetime(
    df["Ship_Date_Parsed"], errors="coerce"
)

df["Order-to-Ship Lead Time"] = pd.to_numeric(
    df["Order-to-Ship Lead Time"], errors="coerce"
)

# --------------------------------------------------
# 1. CREATE ONE RECORD PER PROVISIONAL SHIPMENT
# --------------------------------------------------

shipment_level = (
    df.sort_values("Row ID")
    .drop_duplicates("Route_Shipment_Key")
    .copy()
)

# --------------------------------------------------
# 2. GEOGRAPHIC LANE ANALYSIS
# --------------------------------------------------

lane_columns = [
    "Factory",
    "Country/Region",
    "State/Province",
    "City"
]

# Financial and volume measures from all line items
lane_financials = (
    df.groupby(lane_columns)
    .agg(
        Order_Lines=("Row ID", "count"),
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Gross Profit", "sum"),
        Total_Cost=("Cost", "sum"),
        Total_Units=("Units", "sum")
    )
    .reset_index()
)

# Shipment count and lead-time statistics:
# one observation per provisional shipment
lane_lead_times = (
    shipment_level.groupby(lane_columns)
    .agg(
        Provisional_Shipments=("Route_Shipment_Key", "nunique"),
        Avg_Lead_Time=("Order-to-Ship Lead Time", "mean"),
        Median_Lead_Time=("Order-to-Ship Lead Time", "median"),
        Min_Lead_Time=("Order-to-Ship Lead Time", "min"),
        Max_Lead_Time=("Order-to-Ship Lead Time", "max")
    )
    .reset_index()
)

lane_analysis = lane_financials.merge(
    lane_lead_times,
    on=lane_columns,
    how="left"
)

lane_analysis["Gross_Profit_Margin_Percent"] = (
    lane_analysis["Total_Profit"] /
    lane_analysis["Total_Sales"] * 100
)

lane_analysis.to_csv(LANE_FILE, index=False)

# Lanes with at least 10 provisional shipments
reliable_volume_lanes = (
    lane_analysis[
        lane_analysis["Provisional_Shipments"] >= 10
    ]
    .sort_values("Avg_Lead_Time", ascending=False)
)

# --------------------------------------------------
# 3. GEOGRAPHIC LANE COUNTS BY FACTORY
# --------------------------------------------------

factory_lanes = (
    lane_analysis.groupby("Factory")
    .agg(
        Geographic_Lanes=("City", "size"),
        Provisional_Shipments=("Provisional_Shipments", "sum"),
        Total_Sales=("Total_Sales", "sum"),
        Total_Profit=("Total_Profit", "sum")
    )
    .reset_index()
    .sort_values("Geographic_Lanes", ascending=False)
)

# --------------------------------------------------
# 4. DATE PATTERN INVESTIGATION
# --------------------------------------------------

df["Order_Date_Year"] = df["Order_Date_Parsed"].dt.year
df["Ship_Date_Year"] = df["Ship_Date_Parsed"].dt.year

date_year_comparison = (
    df.groupby(["Order_Date_Year", "Ship_Date_Year"])
    .size()
    .reset_index(name="Records")
)

order_year_stats = (
    df.groupby("Order_Date_Year")["Order-to-Ship Lead Time"]
    .agg(["count", "min", "median", "mean", "max"])
    .reset_index()
)

date_examples = df[
    [
        "Order ID",
        "Order Date",
        "Ship Date",
        "Order_Date_Parsed",
        "Ship_Date_Parsed",
        "Order-to-Ship Lead Time"
    ]
].head(15)

# --------------------------------------------------
# 5. BUILD REPORT
# --------------------------------------------------

report = []

def add(title, content):
    report.append("\n" + "=" * 65)
    report.append(title)
    report.append("=" * 65)
    report.append(str(content))

add(
    "1. GEOGRAPHIC LANES BY FACTORY",
    factory_lanes.to_string(index=False)
)

add(
    "2. TOP 20 LANES BY PROVISIONAL SHIPMENT VOLUME",
    lane_analysis.sort_values(
        "Provisional_Shipments", ascending=False
    ).head(20).to_string(index=False)
)

add(
    "3. HIGHEST LEAD-TIME LANES WITH AT LEAST 10 SHIPMENTS",
    reliable_volume_lanes.head(20).to_string(index=False)
)

add(
    "4. LOWEST LEAD-TIME LANES WITH AT LEAST 10 SHIPMENTS",
    reliable_volume_lanes.tail(20).sort_values(
        "Avg_Lead_Time"
    ).to_string(index=False)
)

add(
    "5. ORDER YEAR VS SHIP YEAR",
    date_year_comparison.to_string(index=False)
)

add(
    "6. LEAD-TIME STATISTICS BY ORDER YEAR",
    order_year_stats.to_string(index=False)
)

add(
    "7. SAMPLE DATE RECORDS",
    date_examples.to_string(index=False)
)

add(
    "8. SHIPMENT-LEVEL VALIDATION",
    f"Raw line-item rows: {len(df)}\n"
    f"Provisional shipment records: {len(shipment_level)}\n"
    f"Unique geographic lanes: {len(lane_analysis)}\n"
    f"Lanes with at least 10 shipments: "
    f"{len(reliable_volume_lanes)}"
)

REPORT_FILE.write_text(
    "\n".join(report),
    encoding="utf-8"
)

print("EDA REFINEMENT COMPLETED!")
print("Report:", REPORT_FILE)
print("Geographic lane CSV:", LANE_FILE)
print("Unique geographic lanes:", len(lane_analysis))
print("Lanes with at least 10 shipments:", len(reliable_volume_lanes))
