import pandas as pd
import os

print("="*70)
print("RBI DISTRICT DEPOSIT DATA INSPECTION - PHASE 3c")
print("="*70)

# Check folder structure
print("\n[0] CHECKING FOLDER STRUCTURE")
raw_data_path = "01_Data_Raw"
if os.path.exists(raw_data_path):
    folders = os.listdir(raw_data_path)
    print(f"    Folders in 01_Data_Raw: {folders}")

# Find the file
possible_paths = [
    "01_Data_Raw/RBI_Bank_Data/RBI_Deposits_2023_2024.xlsx",
    "01_Data_Raw/RBI_Bank_Data/RBI_Deposits_2023_2024.xls",
    "01_Data_Raw/RBIBankData/RBI_Deposits_2023_2024.xlsx",
    "01_Data_Raw/RBIBankData/RBI_Deposits_2023_2024.xls"
]

file_path = None
for path in possible_paths:
    if os.path.exists(path):
        file_path = path
        print(f"    ✓ Found file at: {path}")
        break

if file_path is None:
    print("\n    ERROR: Could not find RBI file.")
    exit()

# Load Excel file
excel_file = pd.ExcelFile(file_path)
print(f"\n[1] EXCEL FILE STRUCTURE")
print(f"    File: {file_path}")
print(f"    Sheet names: {excel_file.sheet_names}")
print(f"    Number of sheets: {len(excel_file.sheet_names)}")

# Load the first sheet with header row 5
sheet_name = excel_file.sheet_names[0]
print(f"\n[2] LOADING SHEET: {sheet_name}")
df = pd.read_excel(file_path, sheet_name=sheet_name, header=5)

print(f"    Shape: {df.shape[0]} rows × {df.shape[1]} columns")

# Display column names - CORRECTED INDICES
print(f"\n[3] COLUMN STRUCTURE (First 15 columns)")
for i, col in enumerate(df.columns[:15]):
    print(f"    [{i}] {col}")

# CORRECTED: Identify key columns using proper indices
print(f"\n[4] KEY COLUMNS IDENTIFIED")
print(f"    Column 0 (Empty): {df.columns[0]}")
print(f"    Column 1 (REGION): {df.columns[1]}")
print(f"    Column 2 (STATE): {df.columns[2]}")
print(f"    Column 3 (DISTRICT): {df.columns[3]}")  # CORRECTED - index 3
print(f"    Column 4 (POP GROUP): {df.columns[4]}")  # CORRECTED - index 4

# Extract ACTUAL district column (column index 3, not 2)
district_col = df.columns[3]
print(f"\n[5] DISTRICT NAME ANALYSIS")
print(f"    District column name: '{district_col}'")
print(f"    Total rows: {len(df)}")
print(f"    Unique districts: {df[district_col].nunique()}")
print(f"    Missing district names: {df[district_col].isna().sum()}")

# Sample district names (first 30 unique)
print(f"\n[6] SAMPLE DISTRICT NAMES (First 30 unique)")
sample_districts = df[district_col].dropna().unique()[:30]
for i, district in enumerate(sample_districts, 1):
    print(f"    {i:2d}. {district}")

# CORRECTED: Identify deposit columns by searching all column names
print(f"\n[7] DEPOSIT VALUE COLUMNS - DETAILED SEARCH")
print(f"    Searching through all {len(df.columns)} columns...")

# Look for columns with numbers (deposit values)
# Dates appear as 2025-09-30, deposit amounts are in sub-headers
# We need to look at the actual data to find deposit columns

# Check what's in columns 5-15 (where deposit data should be)
print(f"\n    Sample column 7 name: {df.columns[7]}")
print(f"    Sample column 10 name: {df.columns[10]}")
print(f"    Sample values from column 7 (first 5 rows):")
print(f"    {df.iloc[:5, 7].tolist()}")

# Get column indices where column names contain specific patterns
date_cols = [i for i, col in enumerate(df.columns) if '2023' in str(col) or '2024' in str(col) or '2025' in str(col)]
print(f"\n    Columns with dates (2023-2025): {len(date_cols)} found")
print(f"    Date column indices: {date_cols[:5]}...")  # Show first 5

# Pattern: Every 3rd column after each date is "Deposit Amount"
# Dates are at columns 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35
# Deposit amounts are at columns 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37
deposit_col_indices = list(range(7, 38, 3))  # Start at 7, increment by 3
print(f"    Estimated deposit column indices: {deposit_col_indices}")

# Check population group categories
pop_group_col = df.columns[4]  # CORRECTED - index 4
print(f"\n[8] POPULATION GROUP CATEGORIES")
pop_groups = df[pop_group_col].value_counts()
print(pop_groups)

# Display first 5 data rows - CORRECTED indices
print(f"\n[9] FIRST 5 DATA ROWS (Key columns only)")
key_cols = [df.columns[i] for i in [2, 3, 4]]  # STATE, DISTRICT, POP_GROUP (CORRECTED)
print(df[key_cols].head())

# Sample deposit values from the first deposit column
first_deposit_col_idx = 7
print(f"\n[10] SAMPLE DEPOSIT VALUES (Column {first_deposit_col_idx})")
print(f"     Column name: {df.columns[first_deposit_col_idx]}")
print(df.iloc[:10, first_deposit_col_idx])

# Summary for merge feasibility
print(f"\n{'='*70}")
print("MERGE FEASIBILITY ASSESSMENT")
print(f"{'='*70}")
print(f"✓ District column found: Column {3} = '{district_col}'")
print(f"✓ Number of unique districts: {df[district_col].nunique()}")
print(f"✓ District name format: ALL UPPERCASE with hyphens for compound names")
print(f"✓ Estimated deposit columns: {len(deposit_col_indices)} quarterly snapshots")
print(f"\n⚠ CRITICAL: Each district has multiple rows (Rural/Semi-urban/Urban/Metropolitan)")
print(f"   → Must aggregate by district to get total deposits")
print(f"\n⚠ DATE RANGE: This file covers 2023-2025 only")
print(f"   → Need to inspect RBI_Deposits_2017_2022.xlsx next")
print(f"{'='*70}")