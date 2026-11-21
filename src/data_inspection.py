
import pandas as pd
import numpy as np
from pathlib import Path

# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "raw" / "nassau_candy.csv"
REPORT_DIR = BASE_DIR / "reports"

REPORT_DIR.mkdir(exist_ok=True)

# ==========================================
# 2. LOAD DATASET
# ==========================================

print("\nLoading Nassau Candy Dataset...")

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found at: {DATA_FILE}\n"
        "Check your CSV filename and folder."
    )

df = pd.read_csv(DATA_FILE, low_memory=False)

print("Dataset loaded successfully!")

# ==========================================
# 3. BASIC INFORMATION
# ==========================================

print("\n" + "=" * 55)
print("1. DATASET OVERVIEW")
print("=" * 55)

print("Total Rows:", df.shape[0])
print("Total Columns:", df.shape[1])
print("\nColumn Names:")
print(df.columns.tolist())

print("\nFirst 5 Records:")
print(df.head().to_string())

print("\nLast 5 Records:")
print(df.tail().to_string())

print("\nData Types:")
print(df.dtypes)

# ==========================================
# 4. MISSING VALUE ANALYSIS
# ==========================================

print("\n" + "=" * 55)
print("2. MISSING VALUE ANALYSIS")
print("=" * 55)

missing_data = pd.DataFrame({
    "Missing Count": df.isnull().sum(),
    "Missing Percentage": (
        df.isnull().mean() * 100
    ).round(2)
})

print(missing_data.to_string())

# ==========================================
# 5. DUPLICATE ANALYSIS
# ==========================================

print("\n" + "=" * 55)
print("3. DUPLICATE ANALYSIS")
print("=" * 55)

print("Complete Duplicate Rows:", df.duplicated().sum())

if "Row ID" in df.columns:
    print(
        "Duplicate Row IDs:",
        df["Row ID"].duplicated().sum()
    )

if "Order ID" in df.columns:
    print(
        "Unique Orders:",
        df["Order ID"].nunique()
    )

# ==========================================
# 6. DATE ANALYSIS
# ==========================================

print("\n" + "=" * 55)
print("4. DATE ANALYSIS")
print("=" * 55)

date_columns = ["Order Date", "Ship Date"]
parsed_dates = {}

for col in date_columns:

    if col in df.columns:

        parsed_dates[col] = pd.to_datetime(
            df[col],
            dayfirst=True,
            errors="coerce"
        )

        print(f"\n{col}")
        print("Minimum:", parsed_dates[col].min())
        print("Maximum:", parsed_dates[col].max())
        print(
            "Invalid/Missing:",
            parsed_dates[col].isna().sum()
        )

        print("Sample original values:")
        print(df[col].head(10).tolist())

# ==========================================
# 7. SHIPPING LEAD TIME
# ==========================================

print("\n" + "=" * 55)
print("5. SHIPPING LEAD TIME ANALYSIS")
print("=" * 55)

if all(col in parsed_dates for col in date_columns):

    lead_time = (
        parsed_dates["Ship Date"] -
        parsed_dates["Order Date"]
    ).dt.days

    print("\nLead Time Statistics:")
    print(lead_time.describe())

    print("\nNegative Lead Times:", (lead_time < 0).sum())
    print("Zero-Day Lead Times:", (lead_time == 0).sum())
    print("Above 30 Days:", (lead_time > 30).sum())
    print("Above 365 Days:", (lead_time > 365).sum())
    print("Missing Lead Times:", lead_time.isna().sum())

# ==========================================
# 8. CATEGORY ANALYSIS
# ==========================================

print("\n" + "=" * 55)
print("6. CATEGORY ANALYSIS")
print("=" * 55)

category_columns = [
    "Ship Mode",
    "Country/Region",
    "Division",
    "Region",
    "State/Province"
]

for col in category_columns:

    if col in df.columns:

        print(f"\n{col} - Unique Values:")
        print("Total:", df[col].nunique())

        print(df[col].value_counts(dropna=False).head(20))

# ==========================================
# 9. FINANCIAL ANALYSIS
# ==========================================

print("\n" + "=" * 55)
print("7. FINANCIAL ANALYSIS")
print("=" * 55)

financial_columns = [
    "Sales",
    "Gross Profit",
    "Cost",
    "Units"
]

for col in financial_columns:

    if col in df.columns:

        numeric_values = pd.to_numeric(
            df[col],
            errors="coerce"
        )

        print(f"\n{col} Statistics:")
        print(numeric_values.describe())

        print("Negative Values:", (numeric_values < 0).sum())
        print("Missing/Invalid:", numeric_values.isna().sum())

# ==========================================
# 10. PRODUCT ANALYSIS
# ==========================================

print("\n" + "=" * 55)
print("8. PRODUCT ANALYSIS")
print("=" * 55)

if "Product Name" in df.columns:

    print("Unique Products:", df["Product Name"].nunique())

    print("\nTop 15 Products by Record Count:")
    print(df["Product Name"].value_counts().head(15))

# ==========================================
# 11. SHIP MODE ANALYSIS
# ==========================================

print("\n" + "=" * 55)
print("9. SHIP MODE DISTRIBUTION")
print("=" * 55)

if "Ship Mode" in df.columns:
    print(df["Ship Mode"].value_counts(dropna=False))

# ==========================================
# 12. SAVE INSPECTION REPORT
# ==========================================

report_path = REPORT_DIR / "inspection_report.txt"

with open(report_path, "w", encoding="utf-8") as file:

    file.write("NASSAU CANDY DATASET INSPECTION REPORT\n")
    file.write("=" * 55 + "\n")

    file.write(f"\nDataset Shape: {df.shape}\n")
    file.write(f"\nColumns:\n{df.columns.tolist()}\n")

    file.write("\n\nDATA TYPES\n")
    file.write(df.dtypes.to_string())

    file.write("\n\nMISSING VALUES\n")
    file.write(missing_data.to_string())

    file.write("\n\nDUPLICATE ROWS\n")
    file.write(str(df.duplicated().sum()))

    if "Row ID" in df.columns:
        file.write(
            "\n\nDUPLICATE ROW IDs\n" +
            str(df["Row ID"].duplicated().sum())
        )

    if "Order ID" in df.columns:
        file.write(
            "\n\nUNIQUE ORDERS\n" +
            str(df["Order ID"].nunique())
        )

    if all(col in parsed_dates for col in date_columns):

        file.write("\n\nLEAD TIME STATISTICS\n")
        file.write(lead_time.describe().to_string())

        file.write(
            "\n\nNEGATIVE LEAD TIMES: " +
            str((lead_time < 0).sum())
        )

        file.write(
            "\nLEAD TIMES ABOVE 365 DAYS: " +
            str((lead_time > 365).sum())
        )

print("\n" + "=" * 55)
print("DATASET INSPECTION COMPLETED!")
print("=" * 55)

print("\nReport saved at:")
print(report_path)
