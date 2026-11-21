# Factory-to-Customer Shipping Route Efficiency Analysis

### Nassau Candy Distributor | Data Analytics Project

## 1. Project Overview

This project analyzes historical order and shipment records of Nassau Candy Distributor to understand factory performance, geographic distribution, destination demand, and shipping route patterns.

The analysis focuses on identifying high-volume factory-to-customer lanes, evaluating product sales and gross profit across destinations, comparing shipping modes, and developing an interactive dashboard to support data-driven business decisions.

The project uses Python for data cleaning, exploratory data analysis, statistical summaries, route-level analysis, and visualization. A Streamlit dashboard provides an interactive interface for exploring the results.

## 2. Project Objectives

- Analyze historical order and shipment records.
- Evaluate the performance of five manufacturing factories.
- Identify high-volume factory-to-destination lanes.
- Analyze sales and gross profit across customer destinations.
- Compare shipping modes based on recorded order-to-ship intervals.
- Examine geographic coverage across the United States and Canada.
- Identify data quality issues and investigate date inconsistencies.
- Develop an interactive dashboard for business insights.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Data analysis and processing |
| Pandas | Data cleaning and manipulation |
| NumPy | Numerical operations |
| Matplotlib | Data visualization |
| Seaborn | Statistical visualization |
| Plotly | Interactive charts |
| Streamlit | Interactive dashboard |
| OpenPyXL | Spreadsheet support |
| VS Code | Development environment |

## 4. Dataset Description

The dataset contains **10,194 records and 18 original columns**.

Important fields include:

- Order ID
- Order Date
- Ship Date
- Ship Mode
- Customer ID
- City
- State/Province
- Country/Region
- Division
- Product Name
- Sales
- Units
- Gross Profit
- Cost

The analysis covers customer destinations in the United States and Canada.

### Factory Locations

The dataset contains five factories:

1. Lot's O' Nuts
2. Wicked Choccy's
3. Sugar Shack
4. Secret Factory
5. The Other Factory

Factory assignments were created using the supplied product-to-factory mapping.

## 5. Project Workflow

The project follows these major stages:

1. **Data Inspection:** Examined dataset dimensions, column types, unique values, and distributions.
2. **Data Quality Assessment:** Checked missing values, duplicates, inconsistent records, and invalid values.
3. **Data Cleaning:** Standardized fields, parsed dates, mapped products to factories, and created analytical features.
4. **Feature Engineering:** Created base order identifiers, factory assignments, and recorded order-to-ship interval metrics.
5. **Exploratory Data Analysis:** Analyzed factory, destination, geographic lane, financial, and shipping mode patterns.
6. **Route Performance Analysis:** Ranked factory-to-city lanes by provisional shipment volume, sales, and gross profit.
7. **Destination Analysis:** Evaluated customer demand and financial contribution by state or province.
8. **Visualization:** Generated charts to communicate key patterns.
9. **Dashboard Development:** Built an interactive Streamlit dashboard.
10. **Validation:** Checked data reconciliation, required files, dashboard source structure, and chart availability.

## 6. Key Findings

### Overall Financial Performance

| Metric | Value |
|---|---:|
| Total Sales | $141,783.63 |
| Total Gross Profit | $93,442.80 |
| Total Product Cost | $48,340.83 |
| Total Units | 38,654 |
| Gross Profit Margin | Approximately 65.9% |

### Factory Performance

- **Lot's O' Nuts** recorded the highest sales, gross profit, units, and geographic coverage.
- **Wicked Choccy's** ranked second across major sales and volume measures.
- **Sugar Shack** contributed a small proportion of total sales but recorded a gross profit margin of approximately 54.86%.
- **The Other Factory** recorded the lowest gross profit margin among the five factories.

### Geographic Destination Analysis

- California was the highest-sales destination, with approximately $27,917.40 in sales.
- New York ranked second, followed by Texas.
- The United States contributed approximately 97.92% of total sales.
- Canada contributed approximately 2.08% of total sales.

### Geographic Lane Analysis

- The analysis identified 1,278 factory-to-city geographic lanes.
- The busiest lane was Lot's O' Nuts to New York City, with 332 provisional shipments.
- Lot's O' Nuts to New York City also recorded the highest lane sales, approximately $7,184.18.
- Lot's O' Nuts and Wicked Choccy's accounted for most of the recorded geographic activity.

## 7. Interactive Dashboard

The project includes a Streamlit dashboard with seven analytical sections:

1. **Executive Overview:** Overall business KPIs and financial summary.
2. **Factory Performance:** Factory-level sales, profit, and performance comparisons.
3. **Geographic Route Analysis:** Factory-to-destination lane analysis.
4. **Destination Analysis:** Geographic distribution and destination patterns.
5. **Destination Performance:** State/province-level financial and order comparisons.
6. **Shipping Mode Analysis:** Comparison of recorded order-to-ship intervals by shipping mode.
7. **Data Quality:** Data validation results and identified limitations.

The dashboard includes interactive filters for:

- Factory
- Division
- Ship Mode
- Country

It also provides interactive charts and downloadable analytical data.

## 8. How to Run the Project

### Prerequisites

- Python 3.10 or later
- Visual Studio Code
- Required Python libraries

### Step 1: Clone the Repository

```bash
git clone <your-github-repository-url>
cd Nassau_Candy_Analysis
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 3: Activate the Environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 4: Install Dependencies

```bash
pip install pandas numpy matplotlib seaborn plotly streamlit openpyxl
```

### Step 5: Run the Dashboard

```bash
streamlit run dashboard/app.py
```

Open the local URL displayed in the terminal, usually:

```text
http://localhost:8501
```

## 9. Project Structure

```text
Nassau_Candy_Analysis/
│
├── data/
│   ├── raw/
│   │   └── nassau_candy.csv
│   │
│   └── processed/
│       ├── nassau_candy_cleaned.csv
│       ├── route_shipment_summary.csv
│       ├── factory_analysis.csv
│       ├── state_analysis.csv
│       ├── route_analysis.csv
│       ├── ship_mode_analysis.csv
│       ├── year_analysis.csv
│       ├── geographic_lane_analysis.csv
│       ├── route_performance_ranking.csv
│       └── destination_performance_ranking.csv
│
├── notebooks/
│
├── src/
│   ├── data_inspection.py
│   ├── data_quality_check.py
│   ├── order_structure_check.py
│   ├── final_validation.py
│   ├── data_cleaning.py
│   ├── aggregation_validation.py
│   ├── eda_analysis.py
│   ├── eda_refinement.py
│   ├── date_anomaly_investigation.py
│   ├── visualization.py
│   ├── visualization_validation.py
│   ├── factory_performance_ranking.py
│   ├── route_performance_ranking.py
│   ├── destination_performance_analysis.py
│   └── dashboard_validation.py
│
├── dashboard/
│   └── app.py
│
├── reports/
│   ├── figures/
│   ├── inspection_report.txt
│   ├── data_quality_report.txt
│   ├── order_structure_report.txt
│   ├── final_validation_report.txt
│   ├── cleaning_summary.txt
│   ├── eda_report.txt
│   ├── eda_refinement_report.txt
│   ├── route_performance_ranking_report.txt
│   ├── destination_performance_report.txt
│   └── dashboard_validation_report.txt
│
└── README.md
```

*Note: The structure above highlights major project files and outputs; it is not an exhaustive listing of every generated file.*

## 10. Data Quality and Analytical Limitations

Several important limitations were identified during validation.

### Date Anomaly

All 10,194 records have an Order-to-Ship interval greater than 365 days. The recorded intervals range from 904 to 1,642 days.

The dataset does not contain an actual delivery date. Therefore, these intervals represent the recorded difference between Order Date and Ship Date, not actual transportation time or delivery delay.

The date anomaly should be investigated with the original data provider before drawing conclusions about shipping speed or delivery performance.

### Provisional Shipment Definition

Shipment counts are estimated using a grouping of base order, factory, and destination information. They should be treated as provisional shipment counts rather than verified physical shipment records.

### Shipping Cost Limitation

The available Cost and Gross Profit fields represent product financial values. Actual freight or transportation costs are not available.

Consequently, the project does not claim to calculate actual shipping cost efficiency.

### Geographic Route Limitation

Factory-to-city combinations are treated as geographic lanes for analysis. They do not represent verified carrier paths or actual road transportation routes.

## 11. Validation Results

The project includes automated validation checks covering:

- Dataset dimensions and required fields
- Preservation of original records
- Financial reconciliation
- Factory mapping completeness
- Dashboard page presence
- Chart file availability
- Date field availability
- Deprecated Streamlit parameter checks

**Latest dashboard validation result:**

- Total checks: 33
- Passed: 33
- Failed: 0

This validates the specified files, data checks, and dashboard source conditions. It is not a complete browser-based end-to-end test.

## 12. Business Value

This project demonstrates how historical business data can be transformed into actionable analytical insights.

The analysis can help stakeholders:

- Understand factory-level business contribution.
- Identify high-volume customer destinations.
- Compare geographic sales patterns.
- Examine product financial performance.
- Explore shipping mode patterns.
- Improve visibility through interactive reporting.
- Identify data quality issues before operational decisions.

## 13. Conclusion

The Factory-to-Customer Shipping Route Efficiency Analysis project provides a structured analytical view of Nassau Candy Distributor's factory performance, geographic distribution, destination demand, and shipping records.

Through Python-based data analysis and an interactive Streamlit dashboard, the project demonstrates practical applications of data cleaning, exploratory data analysis, feature engineering, performance ranking, data validation, and business intelligence.

The findings also highlight the importance of data quality and clearly defined operational metrics when evaluating shipping performance.

---

**Project Domain:** Data Analytics | Supply Chain Analytics | Business Intelligence

**Organization:** Unified Mentor

**Tools:** Python, Pandas, NumPy, Matplotlib, Seaborn, Plotly, Streamlit