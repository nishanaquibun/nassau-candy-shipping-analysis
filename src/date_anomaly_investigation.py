
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

FILE = BASE_DIR / "data" / "processed" / "nassau_candy_cleaned.csv"
REPORT = BASE_DIR / "reports" / "date_anomaly_investigation.txt"

df = pd.read_csv(FILE, low_memory=False)

df["Order_Date_Parsed"] = pd.to_datetime(
    df["Order_Date_Parsed"], errors="coerce"
)

df["Ship_Date_Parsed"] = pd.to_datetime(
    df["Ship_Date_Parsed"], errors="coerce"
)

df["Lead_Time"] = (
    df["Ship_Date_Parsed"] - df["Order_Date_Parsed"]
).dt.days

# Extract year embedded in Order ID
df["Order_ID_Year"] = pd.to_numeric(
    df["Order ID"].str.extract(r"^[A-Z]{2}-(\d{4})")[0],
    errors="coerce"
)

df["Order_Date_Year"] = df["Order_Date_Parsed"].dt.year
df["Ship_Date_Year"] = df["Ship_Date_Parsed"].dt.year

report = []

def add(title, result):
    report.append("\n" + "=" * 65)
    report.append(title)
    report.append("=" * 65)
    report.append(str(result))

# 1. Compare ID year and actual order date year
id_vs_order = (
    df.groupby(["Order_ID_Year", "Order_Date_Year"])
    .size()
    .reset_index(name="Records")
)

add("1. ORDER ID YEAR VS ACTUAL ORDER DATE YEAR",
    id_vs_order.to_string(index=False))

# 2. Lead-time distribution
add("2. LEAD TIME DISTRIBUTION",
    df["Lead_Time"].describe(
        percentiles=[0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
    ).to_string())

# 3. Lead time frequency
add("3. LEAD TIME FREQUENCY",
    df["Lead_Time"].value_counts().head(20).to_string())

# 4. Date-year combinations
year_pairs = (
    df.groupby(["Order_Date_Year", "Ship_Date_Year"])
    .agg(
        Records=("Order ID", "size"),
        Minimum_Lead_Time=("Lead_Time", "min"),
        Average_Lead_Time=("Lead_Time", "mean"),
        Maximum_Lead_Time=("Lead_Time", "max")
    )
    .reset_index()
)

add("4. YEAR PAIR LEAD TIME ANALYSIS",
    year_pairs.to_string(index=False))

# 5. Check date consistency for base orders
base_consistency = (
    df.groupby("Base_Order_ID")
    .agg(
        Order_Date_Variations=("Order_Date_Parsed", "nunique"),
        Ship_Date_Variations=("Ship_Date_Parsed", "nunique")
    )
)

add("5. BASE ORDER DATE CONSISTENCY",
    f"Base orders with multiple order dates: "
    f"{(base_consistency['Order_Date_Variations'] > 1).sum()}\n"
    f"Base orders with multiple ship dates: "
    f"{(base_consistency['Ship_Date_Variations'] > 1).sum()}")

# 6. Show examples with shortest and longest lead times
columns = [
    "Order ID",
    "Order Date",
    "Ship Date",
    "Order_ID_Year",
    "Order_Date_Year",
    "Ship_Date_Year",
    "Lead_Time"
]

shortest = df.nsmallest(10, "Lead_Time")[columns]
longest = df.nlargest(10, "Lead_Time")[columns]

add("6. TEN SHORTEST RECORDED INTERVALS",
    shortest.to_string(index=False))

add("7. TEN LONGEST RECORDED INTERVALS",
    longest.to_string(index=False))

REPORT.write_text(
    "\n".join(report),
    encoding="utf-8"
)

print("DATE INVESTIGATION COMPLETED!")
print("Report saved:", REPORT)
