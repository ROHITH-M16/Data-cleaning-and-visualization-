# Data Cleaning & Visualization System
> **An Enterprise-Grade Web Application for Automated Data Quality Audit, Data Cleaning, Exploratory Data Analysis & Interactive Plotly Visualization.**

![Python Version](https://img.shields.io/badge/Python-3.11-blue.svg)
![Framework](https://img.shields.io/badge/Streamlit-1.30+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Project Level](https://img.shields.io/badge/Academic-M.Sc%20Computer%20Science-purple.svg)

---

## 📌 Executive Summary

The **Data Cleaning & Visualization System** is a professional web-based analytics platform designed to streamline dataset preprocessing, data quality auditing, exploratory data analysis (EDA), and interactive visualization generation.

Built with **Python**, **Streamlit**, **Pandas**, **NumPy**, **Plotly**, and **Scikit-Learn**, this application provides both interactive step-by-step cleaning tools and a **1-Click Auto-Clean Pipeline** that automatically detects and resolves data health issues.

---

## ✨ Key Features

### 1. 📁 Dataset Upload & Inspection
- Supports **CSV (`.csv`)** and **Excel (`.xlsx`, `.xls`)** files.
- Includes **3 Pre-loaded Sample Datasets** (Retail Sales, Employee HR, Patient Medical Data) for instant 1-click testing.
- Displays metadata metrics: Row count, Column count, Missing cell count & %, Duplicate row count & %, Memory usage (MB).
- Previews first 10 rows (head), last 5 rows (tail), random sample rows, and data types breakdown.

### 2. 🧹 Interactive Data Cleaning Engine
- **Standardize Column Names**: Convert messy headers to `snake_case`, `UPPER_CASE`, `Title Case`, or clean whitespace.
- **Strip Whitespace**: Trims leading/trailing spaces across text columns.
- **Missing Values Handling**: Drop missing rows, drop high-missingness columns (> threshold %), or impute using Mean, Median, Mode, Zero, or Constant value.
- **Duplicate Records Removal**: Deduplicate rows based on all or subset of columns.
- **Data Type Conversion**: Cast features to Integer, Float, String, Categorical, Datetime, or Boolean.
- **Outlier Detection & Capping (IQR Method)**: Detects outliers using Interquartile Range ($Q1 - 1.5 \times IQR$, $Q3 + 1.5 \times IQR$) and allows Winsorizing (capping), row dropping, or median substitution.
- **Text Formatting & Cleanup**: Change casing (lower, UPPER, Title) and strip special characters or numbers.

### 3. 📊 Data Quality & Health Audit
- **Data Quality Index Gauge**: Interactive Plotly gauge meter calculating overall data health score (0 - 100%).
- **Column Health Diagnostic Table**: Detailed breakdown per column (Null count/%, Unique count/%, Data type, Min, Mean, Max, Skewness, Outliers count, Sample values).
- **Before vs After Cleaning Comparison**: Side-by-side metric diffs (Quality score, rows, missing cells, duplicates, memory).

### 4. 📈 Exploratory Data Analysis (EDA)
- **Automatic Column Classification**: Separates numerical, categorical, and datetime variables.
- **Numerical Descriptive Statistics**: Count, Mean, Median, Mode, Std Dev, Variance, Min, 25% Q1, 75% Q3, Max, Range, Skewness, Kurtosis.
- **Categorical Descriptive Statistics**: Count, Unique count, Most frequent category (Mode), Mode Frequency, Mode Share %.
- **Correlation Matrix**: Interactive correlation matrix table (Pearson / Spearman) with an annotated Plotly Heatmap.

### 5. 🎨 Interactive Data Visualizations
Generate customized Plotly interactive charts:
- **Bar Chart**: Grouped, stacked, aggregated (Sum, Mean, Median, Count), custom color scales.
- **Line Chart**: Continuous trend analysis over time or sequence.
- **Pie / Donut Chart**: Categorical distribution proportions.
- **Histogram**: Distribution view with bin adjustment sliders and density plots.
- **Scatter Plot**: 2D scatter plots with size dimension, color dimension, and OLS trendlines.
- **Box Plot**: Outlier distribution visualization across category groupings.
- **Missing Values Matrix Heatmap**: Visual map highlighting missing cell locations.

### 6. 💡 Automated Insights & Storytelling Engine
Generates natural language data storytelling across 6 pillars:
- Health & Completeness warnings
- Dominant categorical insights
- Numerical metrics & extreme skewness alerts
- Strong feature correlations ($|r| \ge 0.5$)
- Outlier presence alerts per column
- Actionable recommendations

### 7. ⚡ 1-Click Auto-Clean & Export Pipeline
- **Auto Clean Dataset**: One-click end-to-end automated cleaning pipeline.
- **Auto-Generated Recommended Visualizations**: Instant category bar chart and numerical scatter/box plot creation.
- **Multi-Format Downloads**:
  - Download Cleaned CSV (`.csv`)
  - Download Cleaned Excel (`.xlsx`)
  - Download Executive HTML Quality Audit Report (`.html`)
  - Download Plain Text Summary Report (`.txt`)

---

## 🛠️ Project Structure

```
d:\Data_Cleaning_Visualization_System\
├── app.py                         # Streamlit Main App Entrypoint
├── config.py                      # Theme colors, App constants & Plotly settings
├── requirements.txt               # Required Python packages
├── generate_samples.py            # Sample datasets generator script
├── test_system.py                 # Automated test & verification script
├── README.md                      # Comprehensive project documentation
├── modules/
│   ├── __init__.py
│   ├── data_loader.py             # CSV / Excel dataset loading & format validation
│   ├── data_cleaner.py            # Missing values, duplicates, outliers (IQR), type conversion, text formatting
│   ├── data_analyzer.py           # Descriptive stats, correlation, data quality score, health matrix
│   ├── visualizer.py              # Plotly interactive visualizers (Bar, Line, Pie, Hist, Scatter, Box, Heatmap)
│   ├── insights_generator.py      # Automated data insights & storytelling engine
│   └── report_generator.py        # Executive HTML and Plain Text report generation
├── utils/
│   ├── __init__.py
│   ├── ui_components.py           # Custom HTML/CSS cards, metric badges, UI widgets
│   └── helpers.py                 # Download helpers, session state management
├── data/
│   ├── sample_sales_data.csv      # Sample messy dataset 1 (Retail Sales)
│   ├── sample_employee_data.xlsx  # Sample messy dataset 2 (HR Employee Records)
│   └── sample_medical_data.csv    # Sample messy dataset 3 (Medical Patient Data)
└── docs/
    └── ARCHITECTURE.md            # Technical Architecture & System Design Document
```

---

## 🚀 Installation & Local Execution

### Prerequisites
- **Python 3.10+** installed on your system.

### Step 1: Clone or Navigate to Directory
```bash
cd d:\Data_Cleaning_Visualization_System
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
streamlit run app.py
```

The application will open automatically in your web browser at `http://localhost:8501`.

---

## 🧪 Verification & Testing

To run the automated verification suite across all sample datasets:
```bash
python test_system.py
```

---

## 🎓 Academic Project Information

- **Project Name**: Data Cleaning & Visualization System
- **Target Degree**: M.Sc Computer Science / Data Science / Big Data Analytics
- **Technologies Used**: Python 3.11, Pandas, NumPy, Matplotlib, Seaborn, Plotly, Scikit-Learn, Streamlit, HTML5/CSS3.
