"""
Comprehensive Data Structure Diagnostic
========================================
Scans all files in 01_Data_Raw and 02_Data_Intermediate folders
Shows columns, types, missing values, ranges, and samples

Usage: Run via VS Code (F5) or terminal: python 00_diagnose_all_files.py
Output: Terminal + log file in 05_Outputs/Logs/
"""

import pandas as pd
import numpy as np
import os
import glob
import logging
from datetime import datetime

# Setup logging
os.makedirs("05_Outputs/Logs", exist_ok=True)
log_file = f"05_Outputs/Logs/diagnose_all_files_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def log_separator(char="=", length=100):
    """Print separator line"""
    logging.info(char * length)

def diagnose_dataframe(df, file_name, description=""):
    """
    Comprehensive diagnostic for any dataframe
    Shows: dimensions, columns, types, missing, ranges, samples
    """
    log_separator("=")
    logging.info(f"FILE: {file_name}")
    if description:
        logging.info(f"DESCRIPTION: {description}")
    log_separator("=")
    
    # Basic dimensions
    logging.info(f"\nDIMENSIONS:")
    logging.info(f"   Total Rows:    {len(df):>15,}")
    logging.info(f"   Total Columns: {len(df.columns):>15,}")
    logging.info(f"   Memory Usage:  {df.memory_usage(deep=True).sum() / 1024**2:>15,.2f} MB")
    
    # Column-by-column breakdown
    logging.info(f"\nCOLUMN STRUCTURE:")
    header = f"{'#':<5} {'Column Name':<45} {'Type':<15} {'Non-Null':<12} {'Missing':<10} {'%Miss':<8} {'Unique'}"
    logging.info(header)
    log_separator("-")
    
    for i, col in enumerate(df.columns, 1):
        non_null = df[col].notna().sum()
        missing = df[col].isna().sum()
        pct_miss = (missing / len(df) * 100) if len(df) > 0 else 0
        unique = df[col].nunique()
        dtype = str(df[col].dtype)
        
        logging.info(
            f"{i:<5} {col:<45} {dtype:<15} {non_null:<12,} "
            f"{missing:<10,} {pct_miss:<7.1f}% {unique:,}"
        )
    
    # First and last rows
    logging.info(f"\nSAMPLE DATA (First 3 rows):")
    logging.info(df.head(3).to_string(max_colwidth=50))
    
    logging.info(f"\nSAMPLE DATA (Last 3 rows):")
    logging.info(df.tail(3).to_string(max_colwidth=50))
    
    # Numeric column analysis
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        logging.info(f"\nNUMERIC COLUMNS ANALYSIS ({len(numeric_cols)} columns):")
        for col in numeric_cols:
            if df[col].notna().sum() > 0:
                logging.info(f"\n   {col}:")
                logging.info(f"      Count:      {df[col].notna().sum():>15,}")
                logging.info(f"      Min:        {df[col].min():>15,.4f}")
                logging.info(f"      25%:        {df[col].quantile(0.25):>15,.4f}")
                logging.info(f"      Median:     {df[col].median():>15,.4f}")
                logging.info(f"      75%:        {df[col].quantile(0.75):>15,.4f}")
                logging.info(f"      Max:        {df[col].max():>15,.4f}")
                logging.info(f"      Mean:       {df[col].mean():>15,.4f}")
                logging.info(f"      Std Dev:    {df[col].std():>15,.4f}")
    
    # Categorical column analysis
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    if categorical_cols:
        logging.info(f"\nCATEGORICAL COLUMNS ANALYSIS ({len(categorical_cols)} columns):")
        for col in categorical_cols[:10]:
            unique_count = df[col].nunique()
            logging.info(f"\n   {col}: {unique_count:,} unique values")
            
            if unique_count <= 20:
                value_counts = df[col].value_counts()
                for val, count in value_counts.items():
                    logging.info(f"      '{val}': {count:,} ({count/len(df)*100:.1f}%)")
            else:
                logging.info(f"      (Showing top 10 most frequent)")
                top_values = df[col].value_counts().head(10)
                for val, count in top_values.items():
                    logging.info(f"      '{val}': {count:,} ({count/len(df)*100:.1f}%)")
    
    logging.info("\n")

# ============================================================================
# MAIN DIAGNOSTIC EXECUTION
# ============================================================================

logging.info("\n")
log_separator("#")
logging.info("COMPREHENSIVE DATA STRUCTURE DIAGNOSTIC - ALL RAW AND INTERMEDIATE FILES")
logging.info(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log_separator("#")

# ============================================================================
# PART 1: RAW DATA FILES (01_Data_Raw)
# ============================================================================

logging.info("\n\n")
log_separator("#")
logging.info("PART 1: RAW DATA FILES (01_Data_Raw)")
log_separator("#")

raw_folders = ["01_Data_Raw/RBI_Bank_Data", "01_Data_Raw/EMDAT_Disasters", "01_Data_Raw/District_Boundaries"]

for folder in raw_folders:
    if os.path.exists(folder):
        logging.info(f"\n\nScanning folder: {folder}")
        log_separator("-")
        
        # Scan for Excel files
        excel_files = glob.glob(f"{folder}/*.xls") + glob.glob(f"{folder}/*.xlsx")
        for file_path in excel_files:
            try:
                logging.info(f"\nLoading Excel: {file_path}")
                # Try common sheet names and header rows
                try:
                    df = pd.read_excel(file_path, sheet_name='Report 1', header=5)
                except:
                    try:
                        df = pd.read_excel(file_path, header=0)
                    except:
                        df = pd.read_excel(file_path)
                
                file_name = os.path.basename(file_path)
                diagnose_dataframe(df, file_path, f"Raw Excel file from {folder}")
            except Exception as e:
                logging.error(f"ERROR loading {file_path}: {str(e)}")
        
        # Scan for CSV files
        csv_files = glob.glob(f"{folder}/*.csv")
        for file_path in csv_files:
            try:
                logging.info(f"\nLoading CSV: {file_path}")
                df = pd.read_csv(file_path)
                diagnose_dataframe(df, file_path, f"Raw CSV file from {folder}")
            except Exception as e:
                logging.error(f"ERROR loading {file_path}: {str(e)}")
    else:
        logging.warning(f"FOLDER NOT FOUND: {folder}")

# ============================================================================
# PART 2: INTERMEDIATE FILES (02_Data_Intermediate)
# ============================================================================

logging.info("\n\n")
log_separator("#")
logging.info("PART 2: INTERMEDIATE FILES (02_Data_Intermediate)")
log_separator("#")

intermediate_folder = "02_Data_Intermediate"

if os.path.exists(intermediate_folder):
    # Scan for all CSV files
    csv_files = glob.glob(f"{intermediate_folder}/*.csv")
    
    if csv_files:
        logging.info(f"\nFound {len(csv_files)} CSV file(s) in {intermediate_folder}")
        
        for file_path in csv_files:
            try:
                logging.info(f"\nLoading: {file_path}")
                df = pd.read_csv(file_path)
                
                # Add context based on filename
                file_name = os.path.basename(file_path)
                if "emdat" in file_name.lower():
                    desc = "EM-DAT flood events with parsed districts"
                elif "panel" in file_name.lower() and "master" not in file_name.lower():
                    desc = "RBI deposits panel - district-quarter format"
                elif "master" in file_name.lower():
                    desc = "Master analysis panel with flood exposure"
                elif "crosswalk" in file_name.lower():
                    desc = "District name harmonization crosswalk"
                else:
                    desc = "Intermediate processed data"
                
                diagnose_dataframe(df, file_path, desc)
            except Exception as e:
                logging.error(f"ERROR loading {file_path}: {str(e)}")
    else:
        logging.warning(f"No CSV files found in {intermediate_folder}")
else:
    logging.error(f"FOLDER NOT FOUND: {intermediate_folder}")

# ============================================================================
# SUMMARY
# ============================================================================

logging.info("\n\n")
log_separator("#")
logging.info("DIAGNOSTIC COMPLETE")
logging.info(f"Log saved to: {log_file}")
log_separator("#")
logging.info("\n")