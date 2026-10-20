import pandas as pd
import numpy as np
import os

data_dir = r"d:\Data_Cleaning_Visualization_System\data"
os.makedirs(data_dir, exist_ok=True)

# 1. Sample Sales Data (CSV)
np.random.seed(42)
n_rows = 150

sales_data = {
    " Order_ID ": [f"ORD-{1000 + i}" for i in range(n_rows - 10)] + [f"ORD-{1000 + i}" for i in range(10)], # 10 duplicates
    "Customer Name": [np.random.choice([" Alice Smith ", "BOB JOHNSON", "Charlie Brown", "Diana Prince", " Evan Wright ", None]) for _ in range(n_rows)],
    "Product Category": [np.random.choice(["Electronics", " electronics ", "Clothing", "Home & Kitchen", "Books", np.nan]) for _ in range(n_rows)],
    " Unit Price ($) ": [np.random.choice([15.5, 45.0, 120.0, 499.99, 1200.0, np.nan, 9999.0]) for _ in range(n_rows)], # Outlier 9999.0
    "Quantity Ordered": [np.random.choice([1, 2, 3, 5, 10, -5, 50, np.nan]) for _ in range(n_rows)], # Invalid -5, outlier 50
    "Discount Rate": [np.random.choice([0.0, 0.05, 0.1, 0.15, 0.2, 1.5, np.nan]) for _ in range(n_rows)], # Invalid 1.5 (150%)
    "Payment Method": [np.random.choice(["Credit Card", "PayPal", "Debit Card", " Cash ", np.nan]) for _ in range(n_rows)],
    "Order Date": [np.random.choice(["2023-01-15", "2023-02-20", "2023-03-12", "invalid_date", "2023-05-18", np.nan]) for _ in range(n_rows)],
    "Customer Rating": [np.random.choice([1, 2, 3, 4, 5, np.nan]) for _ in range(n_rows)],
    "Shipping Region": [np.random.choice(["North", "South", "East", "West", " north ", np.nan]) for _ in range(n_rows)]
}

df_sales = pd.DataFrame(sales_data)
# Add a few completely duplicate rows
df_sales = pd.concat([df_sales, df_sales.iloc[0:5]], ignore_index=True)
sales_csv_path = os.path.join(data_dir, "sample_sales_data.csv")
df_sales.to_csv(sales_csv_path, index=False)
print(f"Created {sales_csv_path} with shape {df_sales.shape}")

# 2. Sample Employee Data (Excel)
emp_data = {
    "Emp_ID": [f"EMP-{500 + i}" for i in range(120)],
    "Full Name": [np.random.choice([" John Doe ", "Jane Smith", "Michael Jordan", " Sarah Connor ", "David Miller", np.nan]) for _ in range(120)],
    "Department": [np.random.choice(["Engineering", "engineering", " Sales ", "Marketing", "HR", " Human Resources ", np.nan]) for _ in range(120)],
    " Salary ": [np.random.choice([45000, 60000, 75000, 95000, 120000, 500000, np.nan]) for _ in range(120)], # Outlier 500k
    "Years of Experience": [np.random.choice([1, 3, 5, 8, 12, 25, -2, np.nan]) for _ in range(120)], # Invalid -2
    "Age": [np.random.choice([22, 28, 35, 42, 55, 150, np.nan]) for _ in range(120)], # Outlier 150
    "Performance Rating": [np.random.choice(["Exceeds", "Meets", "Needs Improvement", " EXCEEDS ", np.nan]) for _ in range(120)],
    "Is Active": [np.random.choice(["True", "False", "TRUE", "yes", np.nan]) for _ in range(120)]
}

df_emp = pd.DataFrame(emp_data)
df_emp = pd.concat([df_emp, df_emp.iloc[10:18]], ignore_index=True) # duplicates
emp_xlsx_path = os.path.join(data_dir, "sample_employee_data.xlsx")
df_emp.to_excel(emp_xlsx_path, index=False, engine='openpyxl')
print(f"Created {emp_xlsx_path} with shape {df_emp.shape}")

# 3. Sample Medical Patient Data (CSV)
med_data = {
    "Patient ID": [f"PAT-{7000 + i}" for i in range(100)],
    "Patient Age": [np.random.choice([18, 25, 34, 45, 62, 78, 200, np.nan]) for _ in range(100)],
    "Gender": [np.random.choice(["Male", "Female", " M ", " F ", np.nan]) for _ in range(100)],
    "Systolic BP": [np.random.choice([110, 120, 130, 140, 160, 300, np.nan]) for _ in range(100)], # Outlier 300
    "Cholesterol (mg/dL)": [np.random.choice([180, 200, 220, 240, 310, np.nan]) for _ in range(100)],
    "Smoker Status": [np.random.choice(["Yes", "No", "yes", "no", np.nan]) for _ in range(100)],
    "BMI": [np.random.choice([18.5, 22.1, 26.4, 31.2, 45.0, 99.9, np.nan]) for _ in range(100)],
    "Outcome": [np.random.choice(["Low Risk", "Medium Risk", "High Risk", np.nan]) for _ in range(100)]
}

df_med = pd.DataFrame(med_data)
df_med = pd.concat([df_med, df_med.iloc[0:4]], ignore_index=True) # duplicates
med_csv_path = os.path.join(data_dir, "sample_medical_data.csv")
df_med.to_csv(med_csv_path, index=False)
print(f"Created {med_csv_path} with shape {df_med.shape}")
