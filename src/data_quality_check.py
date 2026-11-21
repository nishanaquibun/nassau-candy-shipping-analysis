
import pandas as pd
import numpy as np
from pathlib import Path

# ==========================================
# 1. PATHS AND DATA LOADING
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "raw" / "nassau_candy.csv"
REPORT_DIR = BASE_DIR / "reports"

df = pd.read_csv(DATA_FILE, low_memory=False)

report = []

def section(title):
    report.append("\n" + "=" * 65)
    report.append(title)
    report.append("=" * 65)

# ==========================================
# 2. DATE PATTERN INVESTIGATION
# ==========================================

section("1. DATE PATTERN INVESTIGATION")

df["Order_Date_Parsed"] = pd.to_datetime(
    df["Order Date"], dayfirst=True, errors="coerce"
)

df["Ship_Date_Parsed"] = pd.to_datetime(
    df["Ship Date"], dayfirst=True, errors="coerce"
)

df["Lead_Time_Days"] = (
    df["Ship_Date_Parsed"] - df["Order_Date_Parsed"]
).dt.days

report.append("\nLead time by Ship Mode:")
report.append(
    df.groupby("Ship Mode")["Lead_Time_Days"]
    .agg(["count", "min", "median", "mean", "max"])
    .round(2).to_string()
)

report.append("\nLead time by Order Year:")
report.append(
    df.groupby(df["Order_Date_Parsed"].dt.year)["Lead_Time_Days"]
    .agg(["count", "min", "median", "mean", "max"])
    .round(2).to_string()
)

report.append("\nFirst 20 date records:")
report.append(
    df[[
        "Order ID", "Order Date", "Ship Date",
        "Ship Mode", "Lead_Time_Days"
    ]].head(20).to_string(index=False)
)

# ==========================================
# 3. ORDER ID YEAR INVESTIGATION
# ==========================================

section("2. ORDER ID YEAR INVESTIGATION")

df["Order_ID_Year"] = (
    df["Order ID"].str.extract(r"US-(\d{4})")[0]
)

report.append("\nOrder ID year distribution:")
report.append(
    df["Order_ID_Year"].value_counts(dropna=False)
    .sort_index().to_string()
)

report.append("\nOrder ID year vs actual Order Date year:")
report.append(
    pd.crosstab(
        df["Order_ID_Year"],
        df["Order_Date_Parsed"].dt.year,
        dropna=False
    ).to_string()
)

# ==========================================
# 4. GEOGRAPHY FIELD INVESTIGATION
# ==========================================

section("3. GEOGRAPHY FIELD INVESTIGATION")

geo_columns = [
    "City", "State/Province", "Postal Code",
    "Country/Region", "Region"
]

for col in geo_columns:

    report.append(f"\n{col}:")

    values = df[col].astype("string")

    report.append(
        f"Blank or whitespace-only values: "
        f"{(values.str.strip() == '').sum()}"
    )

    report.append(
        f"Leading/trailing whitespace: "
        f"{(values != values.str.strip()).sum()}"
    )

report.append("\nFirst 15 geography records (exact values):")

for _, row in df.head(15).iterrows():
    report.append(
        repr({
            "City": row["City"],
            "State": row["State/Province"],
            "Postal Code": row["Postal Code"],
            "Country": row["Country/Region"]
        })
    )

# ==========================================
# 5. FINANCIAL VALIDATION
# ==========================================

section("4. FINANCIAL VALIDATION")

for col in ["Sales", "Gross Profit", "Cost", "Units"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["Financial_Difference"] = (
    df["Sales"] - df["Gross Profit"] - df["Cost"]
)

report.append(
    "\nSales - Gross Profit - Cost difference statistics:"
)

report.append(
    df["Financial_Difference"].describe().to_string()
)

report.append(
    "\nRows where Sales != Gross Profit + Cost "
    "(tolerance 0.01): "
    + str((df["Financial_Difference"].abs() > 0.01).sum())
)

report.append(
    "\nRows with non-positive Sales: "
    + str((df["Sales"] <= 0).sum())
)

report.append(
    "\nRows with non-positive Units: "
    + str((df["Units"] <= 0).sum())
)

# ==========================================
# 6. PRODUCT AND DIVISION VALIDATION
# ==========================================

section("5. PRODUCT AND DIVISION VALIDATION")

report.append("\nProduct Name and Division combinations:")

report.append(
    df.groupby(["Product Name", "Division"])
    .size().to_string()
)

# ==========================================
# 7. ORDER LINE STRUCTURE
# ==========================================

section("6. ORDER STRUCTURE")

report.append(
    "\nNumber of rows per Order ID distribution:"
)

report.append(
    df.groupby("Order ID").size()
    .value_counts().sort_index().to_string()
)

report.append(
    "\nOrders containing more than one distinct product:"
)

products_per_order = df.groupby("Order ID")["Product ID"].nunique()

report.append(
    str((products_per_order > 1).sum())
)

# ==========================================
# 8. SAVE REPORT
# ==========================================

report_path = REPORT_DIR / "data_quality_report.txt"

with open(report_path, "w", encoding="utf-8") as file:
    file.write("\n".join(report))

print("\nDATA QUALITY INVESTIGATION COMPLETED!")
print("Report saved at:")
print(report_path)

print("\nIMPORTANT SUMMARY")
print("Total rows:", len(df))
print("Average lead time:", round(df["Lead_Time_Days"].mean(), 2))
print(
    "Financial mismatches:",
    (df["Financial_Difference"].abs() > 0.01).sum()
)
