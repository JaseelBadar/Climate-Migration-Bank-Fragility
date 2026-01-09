"""
Script: 06_parse_emdat_locations.py
Purpose: Extract district names from EM-DAT flood events
- Parse Admin Units JSON (adm2_name = district level)
- Parse Location text field (fallback for missing Admin Units)
- Flag ambiguous cases for manual review

Input:  01_Data_Raw/EMDAT_Disasters/public_emdat_custom_request_2026-01-02_c149ea93-8fbf-4f6e-a8f6-3b41cc622ed0.xlsx
Output: 02_Data_Intermediate/emdat_districts_parsed.csv
Log:    05_Outputs/Logs/06_parse_emdat_log.txt
"""

import pandas as pd
import re
import os
from datetime import datetime

# ===== SETUP =====
start_time = datetime.now()
print(f"Script started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

# File paths
INPUT_FILE = '01_Data_Raw/EMDAT_Disasters/public_emdat_custom_request_2026-01-02_c149ea93-8fbf-4f6e-a8f6-3b41cc622ed0.xlsx'
OUTPUT_FILE = '02_Data_Intermediate/emdat_districts_parsed.csv'
LOG_FILE = '05_Outputs/Logs/06_parse_emdat_log.txt'

# Create folders
os.makedirs('02_Data_Intermediate', exist_ok=True)
os.makedirs('05_Outputs/Logs', exist_ok=True)

# Initialize log
log_lines = []
log_lines.append(f"EM-DAT Location Parsing Log - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
log_lines.append("="*60)

# ===== LOAD DATA =====
print(f"\nInput: {INPUT_FILE}")
emdat = pd.read_excel(INPUT_FILE)
print(f"Total rows loaded: {len(emdat)}")
log_lines.append(f"Input file: {INPUT_FILE}")
log_lines.append(f"Rows loaded: {len(emdat)}")

# ===== FUNCTION 1: Extract from Admin Units =====
def extract_admin_units(admin_str):
    """
    Parse Admin Units column.
    Structure: [{"adm1_code":1487, "adm1_name":"Assam"}, {"adm2_code":123, "adm2_name":"District"}]
    Returns list of district names (adm2_name) and state names (adm1_name if no districts)
    """
    if pd.isna(admin_str) or admin_str == '':
        return []
    
    try:
        if isinstance(admin_str, str):
            data = eval(admin_str)
            
            if isinstance(data, list):
                districts = []
                states = []
                
                for item in data:
                    if isinstance(item, dict):
                        # Priority: adm2_name (district level)
                        if 'adm2_name' in item and item['adm2_name']:
                            districts.append(item['adm2_name'])
                        # Fallback: adm1_name (state level)
                        elif 'adm1_name' in item and item['adm1_name']:
                            states.append(item['adm1_name'])
                
                # Return districts if available, else states
                return districts if districts else states
        return []
    except Exception as e:
        return []

# Apply extraction
emdat['districts_from_admin'] = emdat['Admin Units'].apply(extract_admin_units)

# Count coverage
has_admin = emdat[emdat['districts_from_admin'].apply(len) > 0]
missing_admin = emdat[emdat['districts_from_admin'].apply(len) == 0]

print(f"\nEvents with Admin Units: {len(has_admin)} ({len(has_admin)/len(emdat)*100:.1f}%)")
print(f"Events missing Admin Units: {len(missing_admin)} ({len(missing_admin)/len(emdat)*100:.1f}%)")

log_lines.append(f"\nAdmin Units coverage:")
log_lines.append(f"  - Events WITH Admin Units: {len(has_admin)}")
log_lines.append(f"  - Events MISSING Admin Units: {len(missing_admin)}")

# ===== FUNCTION 2: Parse Location text =====
def parse_location_text(loc_text):
    """Extract district names from free-text Location field."""
    if pd.isna(loc_text):
        return []
    
    districts = []
    text = str(loc_text)
    
    # Remove parentheses
    text_clean = re.sub(r'\([^)]*\)', '', text)
    
    # Split by delimiters
    parts = re.split(r'[,:;]|\sand\s', text_clean)
    
    # Stopwords
    stopwords = {'District', 'Districts', 'Region', 'State', 'River', 'Valley', 
                 'Area', 'Zone', 'Village', 'City', 'Towns', 'Parts', 'North',
                 'South', 'East', 'West', 'Central', 'Coastal', 'Upper', 'Lower'}
    
    for part in parts:
        part = part.strip()
        if part and len(part) > 3 and part[0].isupper() and part not in stopwords:
            districts.append(part)
    
    return districts

# ===== MANUAL REVIEW OUTPUT =====
print("\n" + "="*60)
print("EVENTS NEEDING MANUAL REVIEW (No Admin Units)")
print("="*60)
print(f"{'DisNo.':<15} {'Location (first 40 chars)':<42} {'Parsed'}")
print("-"*60)

log_lines.append("\n" + "="*60)
log_lines.append("Events requiring manual review:")
log_lines.append("-"*60)

for idx, row in missing_admin.iterrows():
    dis_no = row['DisNo.']
    location = str(row['Location'])[:40]
    parsed = parse_location_text(row['Location'])
    
    print(f"{dis_no:<15} {location:<42} {len(parsed)} items")
    log_lines.append(f"{dis_no} | {row['Location']} | {parsed}")

print("="*60)

# ===== COMBINE AND SAVE =====
emdat['districts_final'] = emdat.apply(
    lambda row: row['districts_from_admin'] if len(row['districts_from_admin']) > 0 
                else parse_location_text(row['Location']),
    axis=1
)

# Convert list to semicolon-separated string
emdat['districts_final_str'] = emdat['districts_final'].apply(lambda x: ';'.join(x) if len(x) > 0 else '')

# Count districts per source
districts_from_admin_count = len(emdat[emdat['districts_from_admin'].apply(len) > 0])
districts_from_location_count = len(emdat[(emdat['districts_from_admin'].apply(len) == 0) & 
                                           (emdat['districts_final_str'] != '')])

print(f"\nDistrict extraction summary:")
print(f"  - From Admin Units: {districts_from_admin_count} events")
print(f"  - From Location text: {districts_from_location_count} events")
print(f"  - Total with districts: {len(emdat[emdat['districts_final_str'] != ''])}")

log_lines.append(f"\nExtraction summary:")
log_lines.append(f"  From Admin Units: {districts_from_admin_count}")
log_lines.append(f"  From Location text: {districts_from_location_count}")

# Select output columns (use correct column names)
output_cols = [
    'DisNo.',
    'Start Year', 
    'Start Month', 
    'Start Day',
    'Location',
    'Admin Units',
    'districts_final_str'
]

emdat_output = emdat[output_cols].copy()
emdat_output.to_csv(OUTPUT_FILE, index=False)

print(f"\nOutput saved: {OUTPUT_FILE}")
log_lines.append(f"\nOutput file: {OUTPUT_FILE}")

# ===== SAVE LOG =====
end_time = datetime.now()
duration = (end_time - start_time).total_seconds()

log_lines.append(f"\nCompleted: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
log_lines.append(f"Duration: {duration:.1f} seconds")

with open(LOG_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log_lines))

print(f"Log saved: {LOG_FILE}")
print(f"\nScript completed in {duration:.1f} seconds")