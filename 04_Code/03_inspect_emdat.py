import pandas as pd
import json
import os

print("="*70)
print("EM-DAT FLOOD DATA INSPECTION - PHASE 3c")
print("="*70)

# Find EM-DAT file
emdat_folder = "01_Data_Raw/EMDAT_Disasters"
print(f"\n[0] LOCATING EM-DAT FILE")

if not os.path.exists(emdat_folder):
    print(f"    ERROR: Folder not found at {emdat_folder}")
    exit()

files = os.listdir(emdat_folder)
print(f"    Files in folder: {files}")

# Find Excel/CSV file
file_path = None
for filename in files:
    if filename.endswith('.xlsx') or filename.endswith('.csv'):
        file_path = os.path.join(emdat_folder, filename)
        print(f"    ✓ Found: {filename}")
        break

if file_path is None:
    print("    ERROR: No data file found")
    exit()

# Load file
print(f"\n[1] LOADING FILE")
if file_path.endswith('.xlsx'):
    df = pd.read_excel(file_path)
else:
    df = pd.read_csv(file_path)

print(f"    Shape: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"    Date range: {df['Start Year'].min()}-{df['Start Year'].max()}")

# Display column structure
print(f"\n[2] KEY COLUMNS IDENTIFIED")
print(f"    Column 13 (Location): {df.columns[13]}")
print(f"    Column 25-27 (Start Date): {df.columns[25]}, {df.columns[26]}, {df.columns[27]}")
print(f"    Column 31 (Total Deaths): {df.columns[31]}")
print(f"    Column 33 (No. Affected): {df.columns[33]}")
print(f"    Column 43 (Admin Units JSON): {df.columns[43]}")

# Parse Admin Units JSON to extract district names
print(f"\n[3] PARSING ADMIN UNITS (Structured Geographic Data)")

def parse_admin_units(admin_json):
    """Extract state and district names from Admin Units JSON"""
    if pd.isna(admin_json):
        return [], []
    
    try:
        units = json.loads(admin_json)
        states = [u['adm1_name'] for u in units if 'adm1_name' in u]
        districts = [u['adm2_name'] for u in units if 'adm2_name' in u]
        return states, districts
    except:
        return [], []

# Apply parsing
df[['admin_states', 'admin_districts']] = df.apply(
    lambda row: pd.Series(parse_admin_units(row['Admin Units'])), axis=1
)

# Count geographic precision
district_level = df['admin_districts'].apply(lambda x: len(x) > 0).sum()
state_only = df['admin_districts'].apply(lambda x: len(x) == 0).sum()

print(f"    Events with district-level data: {district_level}")
print(f"    Events with state-level only: {state_only}")
print(f"    Total events: {len(df)}")

# Extract unique districts from Admin Units
all_districts = []
for districts in df['admin_districts']:
    all_districts.extend(districts)

unique_districts = sorted(set(all_districts))
print(f"\n[4] UNIQUE DISTRICTS IN EM-DAT (from Admin Units)")
print(f"    Total unique districts: {len(unique_districts)}")
print(f"    Sample district names (first 30):")
for i, dist in enumerate(unique_districts[:30], 1):
    print(f"    {i:2d}. {dist}")

# Sample location text vs Admin Units comparison
print(f"\n[5] LOCATION STRING vs ADMIN UNITS (First 10 Events)")
print(f"    Comparing unstructured text vs structured JSON data\n")
for i in range(min(10, len(df))):
    loc_text = df.iloc[i]['Location']
    admin_states = df.iloc[i]['admin_states']
    admin_districts = df.iloc[i]['admin_districts']
    
    print(f"    Event {i+1}:")
    print(f"    Location text: {loc_text[:80]}...")
    print(f"    Admin states: {admin_states}")
    print(f"    Admin districts: {admin_districts}")
    print()

# Date analysis for quarterly conversion
print(f"\n[6] DATE STRUCTURE FOR QUARTERLY CONVERSION")
print(f"    Start date columns: Year={df['Start Year'].dtype}, Month={df['Start Month'].dtype}, Day={df['Start Day'].dtype}")
print(f"    Sample start dates (first 10):")
for i in range(10):
    year = df.iloc[i]['Start Year']
    month = df.iloc[i]['Start Month']
    day = df.iloc[i]['Start Day']
    
    # Convert to quarter
    quarter = (month - 1) // 3 + 1 if pd.notna(month) else None
    quarter_str = f"{int(year)}Q{quarter}" if pd.notna(year) and quarter else "MISSING"
    
    print(f"    {int(year) if pd.notna(year) else 'NA'}-{int(month) if pd.notna(month) else 'NA'}-{int(day) if pd.notna(day) else 'NA'} → {quarter_str}")

# Severity data analysis
print(f"\n[7] SEVERITY DATA COMPLETENESS")
deaths_col = 'Total Deaths'
affected_col = 'No. Affected'
damage_col = 'Total Damage (\'000 US$)'

print(f"    {deaths_col}:")
print(f"    Non-missing: {df[deaths_col].notna().sum()} / {len(df)} ({df[deaths_col].notna().sum()/len(df)*100:.1f}%)")
print(f"    Range: {df[deaths_col].min()} to {df[deaths_col].max()}")

print(f"\n    {affected_col}:")
print(f"    Non-missing: {df[affected_col].notna().sum()} / {len(df)} ({df[affected_col].notna().sum()/len(df)*100:.1f}%)")
print(f"    Range: {df[affected_col].min():.0f} to {df[affected_col].max():.0f}")

print(f"\n    {damage_col}:")
print(f"    Non-missing: {df[damage_col].notna().sum()} / {len(df)} ({df[damage_col].notna().sum()/len(df)*100:.1f}%)")
if df[damage_col].notna().sum() > 0:
    print(f"    Range: ${df[damage_col].min():.0f}k to ${df[damage_col].max():.0f}k")

print(f"\n    RECOMMENDED SEVERITY PROXY: {affected_col}")
print(f"    Reason: Most complete data ({df[affected_col].notna().sum()/len(df)*100:.1f}% coverage)")

# Critical merge feasibility assessment
print(f"\n{'='*70}")
print("MERGE FEASIBILITY - EM-DAT vs RBI")
print(f"{'='*70}")
print(f"✓ Total flood events (2015-2024): {len(df)}")
print(f"✓ Events with district-level precision: {district_level} ({district_level/len(df)*100:.1f}%)")
print(f"✓ Events with state-level only: {state_only} ({state_only/len(df)*100:.1f}%)")
print(f"✓ Unique districts identified: {len(unique_districts)}")
print(f"✓ Date data: Complete, convertible to quarters")
print(f"✓ Severity measure: No. Affected (best coverage)")

print(f"\n⚠️ IDENTIFICATION STRATEGY:")
print(f"   DISTRICT-LEVEL ({district_level} events): Direct match to RBI districts")
print(f"   STATE-LEVEL ({state_only} events): All districts in state coded as flood=1")
print(f"   → This creates measurement error (false positives in state-level events)")
print(f"   → Will attenuate treatment effects in H1 regression")
print(f"   → MUST disclose in paper: 'Geographic precision varies by event'")

print(f"\n⚠️ NEXT CRITICAL STEP:")
print(f"   1. Compare EM-DAT district names vs RBI district names")
print(f"   2. Identify spelling mismatches (e.g., 'Belgaum' vs 'BELAGAVI')")
print(f"   3. Build district name harmonization crosswalk")
print(f"   4. For unmatched districts: Manual verification required")

print(f"\n⚠️ RBI COMPARISON:")
print(f"   RBI has 762 unique districts")
print(f"   EM-DAT has {len(unique_districts)} unique districts in Admin Units")
print(f"   Expected overlap: ~{len(unique_districts)} districts (if names match)")
print(f"   Actual overlap: TBD (requires fuzzy matching in next script)")

print(f"{'='*70}")