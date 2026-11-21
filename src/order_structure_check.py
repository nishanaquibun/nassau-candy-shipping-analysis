
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "nassau_candy.csv"
REPORT_DIR = BASE_DIR / "reports"

df = pd.read_csv(DATA_FILE, low_memory=False)

# Extract the likely underlying order number
df["Base_Order_ID"] = df["Order ID"].str.extract(
    r"^([A-Z]{2}-\d{4}-\d+)"
)

# Product-to-factory mapping from the project brief
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

report = []

def section(title):
    report.append("\n" + "=" * 65)
    report.append(title)
    report.append("=" * 65)

section("1. ORDER IDENTIFIER INVESTIGATION")

report.append(
    f"Unique full Order IDs: {df['Order ID'].nunique()}"
)
report.append(
    f"Unique Base Order IDs: {df['Base_Order_ID'].nunique()}"
)
report.append(
    f"Rows without extracted Base Order ID: "
    f"{df['Base_Order_ID'].isna().sum()}"
)

base_summary = df.groupby("Base_Order_ID").agg(
    Rows=("Row ID", "count"),
    Distinct_Order_IDs=("Order ID", "nunique"),
    Distinct_Products=("Product Name", "nunique"),
    Distinct_Factories=("Factory", "nunique")
)

report.append("\nRows per Base Order ID:")
report.append(
    base_summary["Rows"].value_counts().sort_index().to_string()
)

report.append(
    "\nBase orders containing multiple products: "
    + str((base_summary["Distinct_Products"] > 1).sum())
)

report.append(
    "\nBase orders containing multiple factories: "
    + str((base_summary["Distinct_Factories"] > 1).sum())
)

report.append("\nFirst 20 Base Order IDs:")
report.append(base_summary.head(20).to_string())

section("2. PRODUCT-TO-FACTORY MAPPING VALIDATION")

report.append(
    "\nRows with missing Factory mapping: "
    + str(df["Factory"].isna().sum())
)

report.append("\nProduct and assigned Factory:")
report.append(
    df[["Product Name", "Factory"]]
    .drop_duplicates()
    .sort_values(["Factory", "Product Name"])
    .to_string(index=False)
)

section("3. BASE ORDER EXAMPLES")

example_ids = (
    base_summary[base_summary["Rows"] > 1]
    .head(5)
    .index
)

for order_id in example_ids:
    report.append(f"\nBase Order: {order_id}")
    report.append(
        df.loc[
            df["Base_Order_ID"] == order_id,
            [
                "Order ID",
                "Product Name",
                "Factory",
                "City",
                "State/Province",
                "Ship Date"
            ]
        ].to_string(index=False)
    )

report_path = REPORT_DIR / "order_structure_report.txt"

with open(report_path, "w", encoding="utf-8") as file:
    file.write("\n".join(report))

print("ORDER STRUCTURE INVESTIGATION COMPLETED!")
print("Report saved at:")
print(report_path)
print("\nUnique full Order IDs:", df["Order ID"].nunique())
print("Unique Base Order IDs:", df["Base_Order_ID"].nunique())
print("Missing factory mappings:", df["Factory"].isna().sum())
print(
    "Base orders with multiple products:",
    (base_summary["Distinct_Products"] > 1).sum()
)
print(
    "Base orders with multiple factories:",
    (base_summary["Distinct_Factories"] > 1).sum()
)
