
from pathlib import Path
import pandas as pd

# =====================================================
# 1. PROJECT PATHS
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = BASE_DIR / "data" / "raw" / "nassau_candy.csv"
CLEAN_FILE = BASE_DIR / "data" / "processed" / "nassau_candy_cleaned.csv"
DASHBOARD_FILE = BASE_DIR / "dashboard" / "app.py"

REPORT_DIR = BASE_DIR / "reports"
FIGURE_DIR = REPORT_DIR / "figures"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

REPORT_FILE = REPORT_DIR / "dashboard_validation_report.txt"

# =====================================================
# 2. VALIDATION TRACKER
# =====================================================

results = []

def record_check(name, passed, details=""):
    status = "PASS" if passed else "FAIL"
    results.append((name, status, details))

# =====================================================
# 3. CHECK REQUIRED FILES
# =====================================================

required_files = [
    RAW_FILE,
    CLEAN_FILE,
    DASHBOARD_FILE,
    BASE_DIR / "data" / "processed" / "factory_performance_ranking.csv",
    BASE_DIR / "data" / "processed" / "route_performance_ranking.csv",
    BASE_DIR / "data" / "processed" / "destination_performance_ranking.csv",
    BASE_DIR / "data" / "processed" / "geographic_lane_analysis.csv",
]

for file_path in required_files:
    record_check(
        f"File exists: {file_path.name}",
        file_path.exists(),
        str(file_path)
    )

# =====================================================
# 4. LOAD DATA
# =====================================================

raw = None
cleaned = None

if RAW_FILE.exists():
    raw = pd.read_csv(RAW_FILE)
    
if CLEAN_FILE.exists():
    cleaned = pd.read_csv(CLEAN_FILE)

# =====================================================
# 5. VALIDATE DATASET STRUCTURE
# =====================================================

if raw is not None:
    record_check(
        "Raw dataset has 10,194 records",
        len(raw) == 10194,
        f"Records: {len(raw):,}"
    )

    record_check(
        "Raw dataset has 18 original columns",
        len(raw.columns) == 18,
        f"Columns: {len(raw.columns)}"
    )

if cleaned is not None:
    record_check(
        "Cleaned dataset preserves all 10,194 records",
        len(cleaned) == 10194,
        f"Records: {len(cleaned):,}"
    )

    record_check(
        "Cleaned dataset has Factory column",
        "Factory" in cleaned.columns
    )

    record_check(
        "Cleaned dataset has Base_Order_ID column",
        "Base_Order_ID" in cleaned.columns
    )

# =====================================================
# 6. FINANCIAL RECONCILIATION
# =====================================================

if raw is not None and cleaned is not None:

    financial_columns = [
        "Sales",
        "Gross Profit",
        "Cost",
        "Units"
    ]

    for column in financial_columns:

        if column in raw.columns and column in cleaned.columns:

            raw_total = pd.to_numeric(
                raw[column], errors="coerce"
            ).sum()

            clean_total = pd.to_numeric(
                cleaned[column], errors="coerce"
            ).sum()

            difference = abs(raw_total - clean_total)

            record_check(
                f"{column} totals reconcile",
                difference < 0.01,
                (
                    f"Raw: {raw_total:,.2f} | "
                    f"Cleaned: {clean_total:,.2f} | "
                    f"Difference: {difference:.4f}"
                )
            )

# =====================================================
# 7. FACTORY MAPPING VALIDATION
# =====================================================

if cleaned is not None and "Factory" in cleaned.columns:

    factories = cleaned["Factory"].nunique()

    record_check(
        "Five factories represented",
        factories == 5,
        f"Unique factories: {factories}"
    )

    record_check(
        "No missing factory assignments",
        cleaned["Factory"].notna().all(),
        f"Missing: {cleaned['Factory'].isna().sum()}"
    )

# =====================================================
# 8. DASHBOARD PAGE VALIDATION
# =====================================================

if DASHBOARD_FILE.exists():

    dashboard_code = DASHBOARD_FILE.read_text(
        encoding="utf-8"
    )

    required_pages = [
        "Executive Overview",
        "Factory Performance",
        "Geographic Route Analysis",
        "Destination Analysis",
        "Destination Performance",
        "Shipping Mode Analysis",
        "Data Quality"
    ]

    for page in required_pages:

        record_check(
            f"Dashboard page: {page}",
            page in dashboard_code
        )

    record_check(
        "Deprecated use_container_width removed",
        "use_container_width" not in dashboard_code
    )

# =====================================================
# 9. VISUALIZATION VALIDATION
# =====================================================

required_charts = [
    "01_factory_sales.png",
    "02_factory_coverage.png",
    "03_top_destinations.png",
    "04_top_lanes.png",
    "05_ship_mode_volume.png",
    "06_division_sales.png"
]

for chart in required_charts:

    chart_path = FIGURE_DIR / chart

    record_check(
        f"Visualization: {chart}",
        chart_path.exists(),
        str(chart_path)
    )

# =====================================================
# 10. DATE DATA LIMITATION CHECK
# =====================================================

if cleaned is not None:

    date_warning_present = (
        "Order Date" in cleaned.columns
        and "Ship Date" in cleaned.columns
    )

    record_check(
        "Order and Ship Date fields available",
        date_warning_present
    )

# =====================================================
# 11. GENERATE FINAL REPORT
# =====================================================

passed = sum(1 for _, status, _ in results if status == "PASS")
failed = sum(1 for _, status, _ in results if status == "FAIL")

report_lines = [
    "=" * 65,
    "NASSAU CANDY - DASHBOARD VALIDATION REPORT",
    "=" * 65,
    "",
    f"Total checks: {len(results)}",
    f"Passed: {passed}",
    f"Failed: {failed}",
    "",
    "=" * 65,
    "VALIDATION DETAILS",
    "=" * 65,
    ""
]

for name, status, details in results:

    report_lines.append(f"[{status}] {name}")

    if details:
        report_lines.append(f"       {details}")

    report_lines.append("")

report_lines.extend([
    "=" * 65,
    "FINAL VALIDATION STATUS",
    "=" * 65,
    ""
])

if failed == 0:
    report_lines.append("ALL VALIDATION CHECKS PASSED.")
else:
    report_lines.append(
        f"{failed} CHECK(S) REQUIRE ATTENTION."
    )

report_lines.extend([
    "",
    "IMPORTANT ANALYTICAL LIMITATION:",
    "Order Date-to-Ship Date intervals are anomalously long.",
    "They must not be interpreted as actual transit or delivery time.",
    "Product gross profit is not shipping profit.",
    "Provisional shipment counts are analytical estimates.",
    "",
    "=" * 65
])

REPORT_FILE.write_text(
    "\n".join(report_lines),
    encoding="utf-8"
)

print("\nDASHBOARD VALIDATION COMPLETED")
print("=" * 50)
print(f"Total checks : {len(results)}")
print(f"Passed       : {passed}")
print(f"Failed       : {failed}")
print(f"\nReport saved at:\n{REPORT_FILE}")

if failed:
    print("\nPlease review the failed checks in the report.")
