
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "nassau_candy.csv"
REPORT_DIR = BASE_DIR / "reports"

df = pd.read_csv(DATA_FILE, low_memory=False)

# Extract underlying order identifier
df["Base_Order_ID"] = df["Order ID"].str.extract(
    r"^([A-Z]{2}-\d{4}-\d+)"
)

report = []

def section(title):
    report.append("\n" + "=" * 65)
    report.append(title)
    report.append("=" * 65)

# Fields expected to remain consistent within a base order
consistency_columns = [
    "Order Date",
    "Ship Date",
    "Ship Mode",
    "Customer ID",
    "City",
    "State/Province",
    "Country/Region"
]

section("1. BASE ORDER CONSISTENCY")

for col in consistency_columns:
    counts = df.groupby("Base_Order_ID")[col].nunique(dropna=False)
    inconsistent = counts[counts > 1]

    report.append(f"\n{col}")
    report.append(
        f"Base orders with conflicting values: {len(inconsistent)}"
    )

    if len(inconsistent) > 0:
        report.append("First 10 affected Base Order IDs:")
        report.append(inconsistent.head(10).to_string())

section("2. REPEATED FULL ORDER ID INVESTIGATION")

full_order_summary = df.groupby("Order ID").agg(
    Rows=("Row ID", "count"),
    Products=("Product Name", "nunique"),
    Factories=("Product Name", "nunique"),
    Customers=("Customer ID", "nunique"),
    Ship_Dates=("Ship Date", "nunique"),
    Destinations=("City", "nunique")
)

repeated_ids = full_order_summary[
    full_order_summary["Rows"] > 1
]

report.append(
    f"\nFull Order IDs appearing more than once: {len(repeated_ids)}"
)
report.append(
    f"Repeated IDs with multiple ship dates: "
    f"{(repeated_ids['Ship_Dates'] > 1).sum()}"
)
report.append(
    f"Repeated IDs with multiple customers: "
    f"{(repeated_ids['Customers'] > 1).sum()}"
)
report.append(
    f"Repeated IDs with multiple cities: "
    f"{(repeated_ids['Destinations'] > 1).sum()}"
)

report.append("\nFirst 15 repeated full Order IDs:")
report.append(repeated_ids.head(15).to_string())

section("3. FACTORY-DESTINATION SHIPMENT KEY")

# This is the proposed route shipment key.
df["Route_Shipment_Key"] = (
    df["Base_Order_ID"].astype(str)
    + "|"
    + df["Product Name"].map({
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
    }).astype(str)
    + "|"
    + df["Country/Region"].astype(str)
    + "|"
    + df["State/Province"].astype(str)
    + "|"
    + df["City"].astype(str)
)

report.append(
    "\nUnique Base Order + Factory + Destination combinations: "
    + str(df["Route_Shipment_Key"].nunique())
)

report.append(
    "\nTotal dataset rows: " + str(len(df))
)

report_path = REPORT_DIR / "final_validation_report.txt"

with open(report_path, "w", encoding="utf-8") as file:
    file.write("\n".join(report))

print("FINAL VALIDATION COMPLETED!")
print("Report saved at:")
print(report_path)
print("\nBase order consistency results:")

for col in consistency_columns:
    counts = df.groupby("Base_Order_ID")[col].nunique(dropna=False)
    print(f"{col}: {(counts > 1).sum()} conflicting base orders")

print("\nRepeated full Order IDs:", len(repeated_ids))
print(
    "Proposed unique route shipment combinations:",
    df["Route_Shipment_Key"].nunique()
)
