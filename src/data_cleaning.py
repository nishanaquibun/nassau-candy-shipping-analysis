
import pandas as pd
import numpy as np
from pathlib import Path

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "raw" / "nassau_candy.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed"
REPORT_DIR = BASE_DIR / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 2. LOAD ORIGINAL DATA
# --------------------------------------------------

df = pd.read_csv(DATA_FILE, low_memory=False)

original_rows = len(df)

print("Original dataset loaded:", df.shape)

# --------------------------------------------------
# 3. PRODUCT-TO-FACTORY MAPPING
# --------------------------------------------------

factory_mapping = {
    "Wonka Bar - Nutty Crunch Surprise": "Lot's O' Nuts",
    "Wonka Bar - Fudge Mallows": "Lot's O' Nuts",
    "Wonka Bar -Scrumdiddlyumptious": "Lot's O' Nuts",
    "Wonka Bar - Milk Chocolate": "Wicked Choccy's",
    "Wonka Bar - Triple Dazzle Caramel": "Wicked Choccy's",
    "Laffy Taffy": "Sugar Shack",
    "SweeTARTS": "Sugar Shack",
    "Nerds": "Sugar Shack",
    "Fun Dip": "Sugar Shack",
    "Everlasting Gobstopper": "Secret Factory",
    "Fizzy Lifting Drinks": "Sugar Shack",
    "Lickable Wallpaper": "Secret Factory",
    "Wonka Gum": "Secret Factory",
    "Kazookles": "The Other Factory",
    "Hair Toffee": "The Other Factory"
}

df["Factory"] = df["Product Name"].map(factory_mapping)

# --------------------------------------------------
# 4. IDENTIFY BASE ORDER
# --------------------------------------------------

df["Base_Order_ID"] = df["Order ID"].str.extract(
    r"^([A-Z]{2}-\d{4}-\d+)"
)

# --------------------------------------------------
# 5. PARSE DATE COLUMNS
# --------------------------------------------------

df["Order_Date_Parsed"] = pd.to_datetime(
    df["Order Date"],
    dayfirst=True,
    errors="coerce"
)

df["Ship_Date_Parsed"] = pd.to_datetime(
    df["Ship Date"],
    dayfirst=True,
    errors="coerce"
)

# --------------------------------------------------
# 6. CALCULATE ORDER-TO-SHIP LEAD TIME
# --------------------------------------------------

df["Order-to-Ship Lead Time"] = (
    df["Ship_Date_Parsed"] - df["Order_Date_Parsed"]
).dt.days

df["Order_Year"] = df["Order_Date_Parsed"].dt.year

# --------------------------------------------------
# 7. DATA QUALITY FLAGS
# --------------------------------------------------

df["Data_Quality_Flag"] = "Valid"

df.loc[
    df["Order_Date_Parsed"].isna(),
    "Data_Quality_Flag"
] = "Invalid Order Date"

df.loc[
    df["Ship_Date_Parsed"].isna(),
    "Data_Quality_Flag"
] = "Invalid Ship Date"

df.loc[
    df["Order-to-Ship Lead Time"] < 0,
    "Data_Quality_Flag"
] = "Negative Lead Time"

df.loc[
    df["Order-to-Ship Lead Time"] > 365,
    "Data_Quality_Flag"
] = "Lead Time Above 365 Days - Review"

df.loc[
    df["Factory"].isna(),
    "Data_Quality_Flag"
] = "Missing Factory Mapping"

df.loc[
    df["Base_Order_ID"].isna(),
    "Data_Quality_Flag"
] = "Missing Base Order ID"

# --------------------------------------------------
# 8. IDENTIFY ROUTE SHIPMENT
# --------------------------------------------------

# Destination includes country, state and city.
# This prevents Canadian and US destinations from
# being accidentally grouped together.

route_columns = [
    "Base_Order_ID",
    "Factory",
    "Country/Region",
    "State/Province",
    "City"
]

df["Route_Shipment_Key"] = (
    df[route_columns]
    .fillna("UNKNOWN")
    .astype(str)
    .agg("|".join, axis=1)
)

# --------------------------------------------------
# 9. ROUTE SHIPMENT SUMMARY
# --------------------------------------------------

route_summary = (
    df.groupby("Route_Shipment_Key", as_index=False)
    .agg(
        Base_Order_ID=("Base_Order_ID", "first"),
        Factory=("Factory", "first"),
        Country=("Country/Region", "first"),
        State=("State/Province", "first"),
        City=("City", "first"),
        Order_Date=("Order_Date_Parsed", "first"),
        Ship_Date=("Ship_Date_Parsed", "first"),
        Lead_Time_Days=("Order-to-Ship Lead Time", "first"),
        Ship_Mode=("Ship Mode", "first"),
        Customer_ID=("Customer ID", "first"),
        Order_Lines=("Row ID", "count"),
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Gross Profit", "sum"),
        Total_Cost=("Cost", "sum"),
        Total_Units=("Units", "sum")
    )
)

# --------------------------------------------------
# 10. SAVE CLEANED DATA AND SUMMARIES
# --------------------------------------------------

cleaned_file = OUTPUT_DIR / "nassau_candy_cleaned.csv"
route_file = OUTPUT_DIR / "route_shipment_summary.csv"
quality_file = REPORT_DIR / "cleaning_summary.txt"

df.to_csv(cleaned_file, index=False)
route_summary.to_csv(route_file, index=False)

# --------------------------------------------------
# 11. GENERATE CLEANING REPORT
# --------------------------------------------------

report = []

report.append("NASSAU CANDY DATA CLEANING REPORT")
report.append("=" * 60)

report.append(f"Original rows: {original_rows}")
report.append(f"Cleaned rows: {len(df)}")
report.append(f"Unique Base Orders: {df['Base_Order_ID'].nunique()}")
report.append(f"Unique Route Shipments: {len(route_summary)}")

report.append(
    f"Missing Factory mappings: {df['Factory'].isna().sum()}"
)

report.append(
    f"Invalid Order Dates: {df['Order_Date_Parsed'].isna().sum()}"
)

report.append(
    f"Invalid Ship Dates: {df['Ship_Date_Parsed'].isna().sum()}"
)

report.append(
    f"Negative Lead Times: "
    f"{(df['Order-to-Ship Lead Time'] < 0).sum()}"
)

report.append(
    f"Lead Times Above 365 Days: "
    f"{(df['Order-to-Ship Lead Time'] > 365).sum()}"
)

report.append("\nData Quality Flag Distribution:")
report.append(df["Data_Quality_Flag"].value_counts().to_string())

report.append("\nFactory Distribution:")
report.append(df["Factory"].value_counts(dropna=False).to_string())

report.append("\nCountry Distribution:")
report.append(df["Country/Region"].value_counts().to_string())

report.append("\nAverage Lead Time:")
report.append(
    str(round(df["Order-to-Ship Lead Time"].mean(), 2))
)

with open(quality_file, "w", encoding="utf-8") as file:
    file.write("\n".join(report))

# --------------------------------------------------
# 12. FINAL OUTPUT
# --------------------------------------------------

print("\nDATA CLEANING COMPLETED SUCCESSFULLY!")

print("\nCleaned dataset:")
print(cleaned_file)

print("\nRoute shipment summary:")
print(route_file)

print("\nCleaning report:")
print(quality_file)

print("\nOriginal rows:", original_rows)
print("Cleaned rows:", len(df))
print("Unique Base Orders:", df["Base_Order_ID"].nunique())
print("Unique Route Shipments:", len(route_summary))
print("Missing factory mappings:", df["Factory"].isna().sum())
