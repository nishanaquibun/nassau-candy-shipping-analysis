
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "processed" / "nassau_candy_cleaned.csv"
LANE_FILE = BASE_DIR / "data" / "processed" / "geographic_lane_analysis.csv"
FIGURE_DIR = BASE_DIR / "reports" / "figures"

df = pd.read_csv(DATA_FILE)
lanes = pd.read_csv(LANE_FILE)

print("\n========== DATA VALIDATION ==========")

print("Total records:", len(df))
print("Unique factories:", df["Factory"].nunique())
print("Unique destinations:", df["State/Province"].nunique())
print("Total sales:", round(df["Sales"].sum(), 2))
print("Total gross profit:", round(df["Gross Profit"].sum(), 2))
print("Total units:", df["Units"].sum())
print("Total geographic lanes:", len(lanes))
print("Total provisional shipments:", lanes["Provisional_Shipments"].sum())

print("\n========== CHART FILE VALIDATION ==========")

expected_files = [
    "01_factory_sales.png",
    "02_factory_coverage.png",
    "03_top_destinations.png",
    "04_top_lanes.png",
    "05_ship_mode_volume.png",
    "06_division_sales.png"
]

for filename in expected_files:
    path = FIGURE_DIR / filename

    if path.exists():
        print(f"OK: {filename} | {path.stat().st_size:,} bytes")
    else:
        print(f"MISSING: {filename}")

print("\n========== SHIP MODE VALIDATION ==========")

print(
    df.groupby("Ship Mode")
    .size()
    .sort_values(ascending=False)
    .to_string()
)

print("\n========== FACTORY SALES VALIDATION ==========")

print(
    df.groupby("Factory")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .round(2)
    .to_string()
)

print("\n========== VALIDATION COMPLETED ==========")
