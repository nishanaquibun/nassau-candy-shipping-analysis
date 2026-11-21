
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = BASE_DIR / "data" / "raw" / "nassau_candy.csv"
CLEAN_FILE = BASE_DIR / "data" / "processed" / "nassau_candy_cleaned.csv"
ROUTE_FILE = BASE_DIR / "data" / "processed" / "route_shipment_summary.csv"
REPORT_FILE = BASE_DIR / "reports" / "aggregation_validation.txt"

raw = pd.read_csv(RAW_FILE, low_memory=False)
clean = pd.read_csv(CLEAN_FILE, low_memory=False)
routes = pd.read_csv(ROUTE_FILE, low_memory=False)

report = []

def add(title, value):
    report.append(f"\n{title}")
    report.append(str(value))

# 1. Repeated full Order IDs
order_counts = raw.groupby("Order ID").size()

add("1. REPEATED FULL ORDER IDs",
    f"Unique Order IDs: {raw['Order ID'].nunique()}\n"
    f"IDs appearing more than once: {(order_counts > 1).sum()}\n"
    f"Maximum rows for one Order ID: {order_counts.max()}")

# 2. Check repeated records for financial variation
financial_columns = [
    "Sales", "Gross Profit", "Cost", "Units"
]

financial_variation = (
    raw.groupby("Order ID")[financial_columns]
    .nunique()
)

repeated_ids = order_counts[order_counts > 1].index
repeated_variation = financial_variation.loc[repeated_ids]

add("2. FINANCIAL VARIATION WITHIN REPEATED ORDER IDs",
    repeated_variation.gt(1).sum().to_string())

# 3. Inspect examples of repeated Order IDs
examples = order_counts[order_counts > 1].head(10).index

add("3. EXAMPLE REPEATED ORDER RECORDS",
    raw.loc[
        raw["Order ID"].isin(examples),
        [
            "Row ID", "Order ID", "Product Name",
            "Sales", "Gross Profit", "Cost", "Units"
        ]
    ].to_string(index=False))

# 4. Verify financial totals are preserved in route aggregation
for col in ["Sales", "Gross Profit", "Cost", "Units"]:
    raw_total = pd.to_numeric(raw[col], errors="coerce").sum()

    route_col = {
        "Sales": "Total_Sales",
        "Gross Profit": "Total_Profit",
        "Cost": "Total_Cost",
        "Units": "Total_Units"
    }[col]

    route_total = routes[route_col].sum()

    add(
        f"4. TOTAL {col.upper()}",
        f"Raw total: {raw_total:.4f}\n"
        f"Route summary total: {route_total:.4f}\n"
        f"Difference: {raw_total - route_total:.8f}"
    )

# 5. Check route summary consistency
add("5. ROUTE SUMMARY",
    f"Cleaned records: {len(clean)}\n"
    f"Route summary rows: {len(routes)}\n"
    f"Unique route keys in cleaned data: "
    f"{clean['Route_Shipment_Key'].nunique()}")

# 6. Check whether every route has one consistent lead time
lead_variation = (
    clean.groupby("Route_Shipment_Key")[
        "Order-to-Ship Lead Time"
    ].nunique(dropna=False)
)

add("6. ROUTE LEAD-TIME CONSISTENCY",
    f"Routes with multiple lead-time values: "
    f"{(lead_variation > 1).sum()}")

REPORT_FILE.write_text("\n".join(report), encoding="utf-8")

print("AGGREGATION VALIDATION COMPLETED!")
print("Report saved at:", REPORT_FILE)
print("\nRepeated Order IDs:", (order_counts > 1).sum())
print("Routes:", len(routes))
print("Routes with inconsistent lead times:", (lead_variation > 1).sum())
