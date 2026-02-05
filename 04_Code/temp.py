import os

# Files to delete (all based on contaminated deposit data)
contaminated_files = [
    '02_Data_Intermediate/master_panel_raw.csv',
    '03_Data_Clean/master_panel_analysis.csv',
    '03_Data_Clean/analysis_panel_final.csv',
    '03_Data_Clean/regression_panel_final.csv',
    '05_Outputs/Tables/01_descriptive_stats.csv',
    '05_Outputs/Tables/02_H1_first_stage.csv',
    '05_Outputs/Tables/03_H2_iv2sls.csv',
    '05_Outputs/Tables/04_H3_timing.csv',
    '05_Outputs/Tables/05_H4_heterogeneity.csv',
    '05_Outputs/Logs/25_descriptive_summary.txt',
    '05_Outputs/Logs/27_H1_regression_full.txt',
    '05_Outputs/Logs/28_H2_regression.txt',
    '05_Outputs/Logs/29_H3_timing.txt',
    '05_Outputs/Logs/30_H4_heterogeneity.txt'
]

print("="*70)
print("DELETING CONTAMINATED FILES")
print("="*70)

for filepath in contaminated_files:
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"✓ Deleted: {filepath}")
    else:
        print(f"  (Not found: {filepath})")

print("\nContaminated files removed. Ready for pipeline re-run.")