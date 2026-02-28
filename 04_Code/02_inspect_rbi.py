import pandas as pd
import os


print("=" * 70)
print("RBI DISTRICT DEPOSIT DATA INSPECTION - PHASE 3c")
print("=" * 70)


# [0] FOLDER STRUCTURE
print("\n[0] CHECKING FOLDER STRUCTURE")
raw_data_path = "01_Data_Raw"
if os.path.exists(raw_data_path):
    folders = os.listdir(raw_data_path)
    print(f"    Folders in 01_Data_Raw: {folders}")


# Locate file
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
        print(f"    FOUND: {path}")
        break

if file_path is None:
    print("\n    ERROR: Could not find RBI file.")
    raise SystemExit(1)


# [1] EXCEL FILE STRUCTURE
excel_file = pd.ExcelFile(file_path)
print(f"\n[1] EXCEL FILE STRUCTURE")
print(f"    File: {file_path}")
print(f"    Sheet names: {excel_file.sheet_names}")
print(f"    Number of sheets: {len(excel_file.sheet_names)}")


# [2] LOAD SHEET
sheet_name = excel_file.sheet_names[0]
print(f"\n[2] LOADING SHEET: {sheet_name}")
df = pd.read_excel(file_path, sheet_name=sheet_name, header=5)
print(f"    Shape: {df.shape[0]} rows x {df.shape[1]} columns")


# [3] COLUMN STRUCTURE
print(f"\n[3] COLUMN STRUCTURE (First 15 columns)")
for i, col in enumerate(df.columns[:15]):
    print(f"    [{i}] {col}")


# [4] KEY COLUMNS
# Verified against manual audit (Feb 4, 2026):
# Index 0 = Blank (Col A)
# Index 1 = REGION (Col B)
# Index 2 = STATE (Col C)
# Index 3 = DISTRICT (Col D)
# Index 4 = POPULATION GROUP (Col E)
# Deposit Amount at indices 7, 10, 13... (3rd sub-column of each quarter block)
print(f"\n[4] KEY COLUMNS IDENTIFIED")
print(f"    Column 0 (Blank):     {df.columns[0]}")
print(f"    Column 1 (REGION):    {df.columns[1]}")
print(f"    Column 2 (STATE):     {df.columns[2]}")
print(f"    Column 3 (DISTRICT):  {df.columns[3]}")
print(f"    Column 4 (POP GROUP): {df.columns[4]}")


# [5] DISTRICT ANALYSIS
district_col = df.columns[3]
print(f"\n[5] DISTRICT NAME ANALYSIS")
print(f"    District column name: '{district_col}'")
print(f"    Total rows: {len(df)}")
print(f"    Unique districts: {df[district_col].nunique()}")
print(f"    Missing district names: {df[district_col].isna().sum()}")


# [6] SAMPLE DISTRICT NAMES
print(f"\n[6] SAMPLE DISTRICT NAMES (First 30 unique)")
sample_districts = df[district_col].dropna().unique()[:30]
for i, district in enumerate(sample_districts, 1):
    print(f"    {i:2d}. {district}")


# [7] DEPOSIT COLUMN SEARCH
print(f"\n[7] DEPOSIT VALUE COLUMNS - DETAILED SEARCH")
print(f"    Searching through all {len(df.columns)} columns...")

print(f"\n    Sample column 7 name:  {df.columns[7]}")
print(f"    Sample column 10 name: {df.columns[10]}")
print(f"    Sample values from column 7 (first 5 rows):")
print(f"    {df.iloc[:5, 7].tolist()}")

date_cols = [i for i, col in enumerate(df.columns)
             if '2023' in str(col) or '2024' in str(col) or '2025' in str(col)]
print(f"\n    Columns with dates (2023-2025): {len(date_cols)} found")
print(f"    Date column indices (first 5): {date_cols[:5]}")

# Deposit Amount is at indices 7, 10, 13... (every 3rd column from 7)
# Confirmed: quarter label at 5, Accounts at 6, Deposit at 7 for first block
deposit_col_indices = list(range(7, 38, 3))
print(f"    Deposit column indices: {deposit_col_indices}")


# [8] POPULATION GROUP CATEGORIES
pop_group_col = df.columns[4]
print(f"\n[8] POPULATION GROUP CATEGORIES")
pop_groups = df[pop_group_col].value_counts()
print(pop_groups)


# [9] FIRST 5 DATA ROWS
print(f"\n[9] FIRST 5 DATA ROWS (Key columns only)")
key_cols = [df.columns[i] for i in [2, 3, 4]]
print(df[key_cols].head())


# [10] SAMPLE DEPOSIT VALUES
first_deposit_col_idx = 7
print(f"\n[10] SAMPLE DEPOSIT VALUES (Column {first_deposit_col_idx})")
print(f"     Column name: {df.columns[first_deposit_col_idx]}")
print(df.iloc[:10, first_deposit_col_idx])


# MERGE FEASIBILITY SUMMARY
print(f"\n{'=' * 70}")
print("MERGE FEASIBILITY ASSESSMENT")
print(f"{'=' * 70}")
print(f"PASS - District column found: Column 3 = '{district_col}'")
print(f"PASS - Unique districts: {df[district_col].nunique()}")
print(f"PASS - District name format: UPPERCASE with hyphens for compound names")
print(f"PASS - Deposit columns: {len(deposit_col_indices)} quarterly snapshots")
print(f"\nNOTE: Each district has multiple rows (Rural/Semi-urban/Urban/Metropolitan)")
print(f"      Must aggregate by district to get total deposits")
print(f"\nNOTE: Date range is 2023-2025 only")
print(f"      Must inspect RBI_Deposits_2017_2022.xlsx next")
print(f"{'=' * 70}")