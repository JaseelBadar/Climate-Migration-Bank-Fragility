import pandas as pd
import os

print("="*70)
print("RBI DEPOSITS EXTRACTION - PHASE 3d")
print("="*70)

# Input files
rbi_files = [
    '01_Data_Raw/RBI_Bank_Data/RBI_Deposits_2023_2024.xlsx',
    '01_Data_Raw/RBI_Bank_Data/RBI_Deposits_2017_2022.xlsx',
    '01_Data_Raw/RBI_Bank_Data/RBI_Deposits_2004_2017.xlsx'
]

# Load crosswalk
crosswalk = pd.read_csv('02_Data_Intermediate/district_crosswalk_draft.csv')
print(f"\n[1] Crosswalk loaded: {len(crosswalk)} rows")
print(f"    RBI→GADM matches: {crosswalk['matched_rbi_gadm'].sum()}")

# Storage for all quarters
all_data = []

for file_idx, filepath in enumerate(rbi_files, 1):
    print(f"\n[2.{file_idx}] Processing: {os.path.basename(filepath)}")
    
    if not os.path.exists(filepath):
        print(f"    ⚠ File not found, skipping")
        continue
    
    # Load Excel (header at row 5, 0-indexed)
    df = pd.read_excel(filepath, sheet_name=0, header=5)
    print(f"    Loaded: {df.shape[0]} rows × {df.shape[1]} cols")
    
    # Identify key columns
    state_col = df.columns[2]
    district_col = df.columns[3]
    
    # Detect file format
    has_fiscal_quarters = any(':Q' in str(col) for col in df.columns[:20])
    
    if has_fiscal_quarters:
        # Historical format: column names like "2022-23:Q3"
        print(f"    Format: Historical (fiscal quarters in column names)")
        
        # Find all columns with fiscal quarter pattern
        deposit_cols = [i for i, col in enumerate(df.columns) if ':Q' in str(col)]
        print(f"    Deposit columns found: {len(deposit_cols)}")
        
        for dep_idx in deposit_cols:
            col_name = str(df.columns[dep_idx])
            
            try:
                # Parse "2022-23:Q3" format
                year_part, q_part = col_name.split(':Q')
                year_start = int(year_part.split('-')[0])
                fiscal_q = int(q_part)
                
                # Convert Indian fiscal year to calendar year
                # Fiscal year starts April 1
                # Fiscal Q1 (Apr-Jun) = Calendar Q2
                # Fiscal Q2 (Jul-Sep) = Calendar Q3
                # Fiscal Q3 (Oct-Dec) = Calendar Q4
                # Fiscal Q4 (Jan-Mar) = Calendar Q1 of NEXT calendar year
                
                if fiscal_q == 4:
                    calendar_year = year_start + 1
                    calendar_q = 1
                else:
                    calendar_year = year_start
                    calendar_q = fiscal_q + 1
                
                quarter_str = f"{calendar_year}Q{calendar_q}"
                
            except Exception as e:
                print(f"    ⚠ Skipping column '{col_name}': {e}")
                continue
            
            # Extract data
            temp = df[[state_col, district_col, df.columns[dep_idx]]].copy()
            temp.columns = ['state_rbi', 'district_rbi', 'deposits']
            temp['quarter'] = quarter_str
            temp['year'] = calendar_year
            temp['q'] = calendar_q
            
            # Drop missing values
            temp = temp.dropna(subset=['district_rbi', 'deposits'])
            
            # Aggregate by district-quarter (sum across population groups)
            temp_agg = temp.groupby(
                ['state_rbi', 'district_rbi', 'quarter', 'year', 'q'], 
                as_index=False
            )['deposits'].sum()
            
            all_data.append(temp_agg)
    
    else:
        # Current format: dates in separate columns
        print(f"    Format: Current (calendar dates as timestamps)")
        
        # Deposit columns at every 3rd position starting from 7
        deposit_indices = list(range(7, len(df.columns), 3))
        print(f"    Deposit columns found: {len(deposit_indices)}")
        
        for dep_idx in deposit_indices:
            if dep_idx >= len(df.columns):
                break
            
            # Date is 2 columns before deposit
            date_idx = dep_idx - 2
            quarter_date = df.columns[date_idx]
            
            try:
                dt = pd.to_datetime(quarter_date)
                calendar_year = dt.year
                calendar_q = (dt.month - 1) // 3 + 1
                quarter_str = f"{calendar_year}Q{calendar_q}"
            except:
                continue
            
            # Extract data
            temp = df[[state_col, district_col, df.columns[dep_idx]]].copy()
            temp.columns = ['state_rbi', 'district_rbi', 'deposits']
            temp['quarter'] = quarter_str
            temp['year'] = calendar_year
            temp['q'] = calendar_q
            
            # Drop missing values
            temp = temp.dropna(subset=['district_rbi', 'deposits'])
            
            # Aggregate by district-quarter
            temp_agg = temp.groupby(
                ['state_rbi', 'district_rbi', 'quarter', 'year', 'q'], 
                as_index=False
            )['deposits'].sum()
            
            all_data.append(temp_agg)

# Combine all quarters
print(f"\n[3] Combining all files...")
rbi_panel = pd.concat(all_data, ignore_index=True)
print(f"    Total rows before crosswalk: {len(rbi_panel)}")
print(f"    Unique districts: {rbi_panel['district_rbi'].nunique()}")
print(f"    Quarters range: {rbi_panel['quarter'].min()} to {rbi_panel['quarter'].max()}")

# Map RBI districts to GADM using crosswalk
print(f"\n[4] Mapping RBI → GADM districts...")
rbi_panel = rbi_panel.merge(
    crosswalk[['district_rbi', 'district_gadm', 'state_gadm', 'matched_rbi_gadm']],
    on='district_rbi',
    how='left'
)

matched_count = rbi_panel['matched_rbi_gadm'].sum()
total_count = len(rbi_panel)
print(f"    Matched: {matched_count}/{total_count} ({matched_count/total_count*100:.1f}%)")

# Drop unmatched RBI districts
rbi_panel = rbi_panel[rbi_panel['matched_rbi_gadm'] == True].copy()
rbi_panel = rbi_panel.drop(columns=['matched_rbi_gadm'])

print(f"    After dropping unmatched: {len(rbi_panel)} rows")
print(f"    Unique GADM districts: {rbi_panel['district_gadm'].nunique()}")

# Add quarter_num (sequential index)
rbi_panel = rbi_panel.sort_values(['district_gadm', 'year', 'q'])
quarter_map = {q: i+1 for i, q in enumerate(sorted(rbi_panel['quarter'].unique()))}
rbi_panel['quarter_num'] = rbi_panel['quarter'].map(quarter_map)

# Aggregate to GADM level (handle duplicate crosswalk matches)
print(f"\n[4b] Aggregating to unique GADM district-state-quarters...")
print(f"    Before aggregation: {len(rbi_panel)} rows")

rbi_panel = rbi_panel.groupby(
    ['district_gadm', 'state_gadm', 'quarter', 'year', 'q', 'quarter_num'],
    as_index=False
).agg({
    'deposits': 'sum',
    'district_rbi': lambda x: '; '.join(sorted(set(x))),
    'state_rbi': 'first'
})

print(f"    After aggregation: {len(rbi_panel)} rows")
print(f"    Unique GADM districts: {rbi_panel['district_gadm'].nunique()}")

# Reorder columns
rbi_panel = rbi_panel[[
    'district_gadm', 'state_gadm', 'quarter', 'year', 'q', 'quarter_num',
    'deposits', 'district_rbi', 'state_rbi'
]]

# Save
output_path = '02_Data_Intermediate/rbi_deposits_panel.csv'
rbi_panel.to_csv(output_path, index=False)

print(f"\n[5] OUTPUT SAVED")
print(f"    File: {output_path}")
print(f"    Rows: {len(rbi_panel)}")
print(f"    Columns: {rbi_panel.columns.tolist()}")

# Summary stats
print(f"\n[6] SUMMARY STATISTICS")
print(f"    Districts: {rbi_panel['district_gadm'].nunique()}")
print(f"    Quarters: {rbi_panel['quarter'].nunique()}")
print(f"    Date range: {rbi_panel['year'].min()}-{rbi_panel['year'].max()}")
print(f"    Total deposits (₹ Crores): {rbi_panel['deposits'].sum():,.0f}")
print(f"    Mean deposits per district-quarter: {rbi_panel['deposits'].mean():,.0f}")

# Check for missing quarters
print(f"\n[7] TEMPORAL COVERAGE CHECK")
all_years = sorted(rbi_panel['year'].unique())
for year in all_years:
    quarters_present = sorted(rbi_panel[rbi_panel['year']==year]['q'].unique())
    print(f"    {year}: Q{quarters_present}")

print("="*70)
print("RBI EXTRACTION COMPLETE")
print("="*70)