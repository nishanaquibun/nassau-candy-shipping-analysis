
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# --------------------------------------------------
# 1. PATHS AND SETTINGS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "processed" / "nassau_candy_cleaned.csv"
LANE_FILE = BASE_DIR / "data" / "processed" / "geographic_lane_analysis.csv"

FIGURE_DIR = BASE_DIR / "reports" / "figures"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", context="notebook")

df = pd.read_csv(DATA_FILE, low_memory=False)
lanes = pd.read_csv(LANE_FILE, low_memory=False)

# --------------------------------------------------
# 2. FACTORY SALES
# --------------------------------------------------

factory = (
    df.groupby("Factory")
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Gross Profit", "sum")
    )
    .sort_values("Sales")
)

plt.figure(figsize=(11, 6))
sns.barplot(data=factory.reset_index(), x="Sales", y="Factory")
plt.title("Total Sales by Factory", fontsize=16)
plt.xlabel("Total Sales")
plt.ylabel("Factory")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "01_factory_sales.png", dpi=300)
plt.close()

# --------------------------------------------------
# 3. FACTORY GEOGRAPHIC COVERAGE
# --------------------------------------------------

factory_coverage = (
    lanes.groupby("Factory")
    .agg(
        Geographic_Lanes=("City", "size"),
        Shipments=("Provisional_Shipments", "sum")
    )
    .sort_values("Geographic_Lanes")
    .reset_index()
)

plt.figure(figsize=(11, 6))
sns.barplot(
    data=factory_coverage,
    x="Geographic_Lanes",
    y="Factory"
)
plt.title("Geographic Lane Coverage by Factory", fontsize=16)
plt.xlabel("Number of Unique Geographic Lanes")
plt.ylabel("Factory")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "02_factory_coverage.png", dpi=300)
plt.close()

# --------------------------------------------------
# 4. TOP 10 DESTINATION STATES BY SALES
# --------------------------------------------------

state = (
    df.groupby(["Country/Region", "State/Province"])
    ["Sales"]
    .sum()
    .reset_index()
)

state["Destination"] = (
    state["State/Province"] + ", " + state["Country/Region"]
)

top_states = state.nlargest(10, "Sales").sort_values("Sales")

plt.figure(figsize=(11, 7))
sns.barplot(data=top_states, x="Sales", y="Destination")
plt.title("Top 10 Destinations by Sales", fontsize=16)
plt.xlabel("Total Sales")
plt.ylabel("Destination")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "03_top_destinations.png", dpi=300)
plt.close()

# --------------------------------------------------
# 5. TOP 15 GEOGRAPHIC LANES BY SHIPMENT VOLUME
# --------------------------------------------------

lanes["Destination"] = (
    lanes["City"] + ", " + lanes["State/Province"]
)

lanes["Lane"] = (
    lanes["Factory"] + " → " + lanes["Destination"]
)

top_lanes = (
    lanes.nlargest(15, "Provisional_Shipments")
    .sort_values("Provisional_Shipments")
)

plt.figure(figsize=(13, 9))
sns.barplot(
    data=top_lanes,
    x="Provisional_Shipments",
    y="Lane"
)
plt.title("Top 15 Geographic Lanes by Shipment Volume", fontsize=16)
plt.xlabel("Provisional Shipment Combinations")
plt.ylabel("Factory → Destination")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "04_top_lanes.png", dpi=300)
plt.close()

# --------------------------------------------------
# 6. SHIP MODE ORDER VOLUME
# --------------------------------------------------

ship_mode = (
    df.groupby("Ship Mode")
    .agg(
        Order_Lines=("Row ID", "count"),
        Sales=("Sales", "sum"),
        Profit=("Gross Profit", "sum")
    )
    .reset_index()
    .sort_values("Order_Lines")
)

plt.figure(figsize=(10, 6))
sns.barplot(
    data=ship_mode,
    x="Order_Lines",
    y="Ship Mode"
)
plt.title("Order Line Volume by Ship Mode", fontsize=16)
plt.xlabel("Number of Order Lines")
plt.ylabel("Ship Mode")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "05_ship_mode_volume.png", dpi=300)
plt.close()

# --------------------------------------------------
# 7. DIVISION-WISE SALES
# --------------------------------------------------

division = (
    df.groupby("Division")
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Gross Profit", "sum")
    )
    .reset_index()
    .sort_values("Sales")
)

plt.figure(figsize=(10, 6))
sns.barplot(data=division, x="Sales", y="Division")
plt.title("Sales Contribution by Product Division", fontsize=16)
plt.xlabel("Total Sales")
plt.ylabel("Division")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "06_division_sales.png", dpi=300)
plt.close()

# --------------------------------------------------
# 8. COMPLETION
# --------------------------------------------------

print("\nVISUALIZATION COMPLETED SUCCESSFULLY!")

print("Charts saved in:")
print(FIGURE_DIR)

for file in sorted(FIGURE_DIR.glob("*.png")):
    print("-", file.name)
