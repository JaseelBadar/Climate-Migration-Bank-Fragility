import pandas as pd
import numpy as np
import os
from datetime import datetime

log_path = '05_Outputs/Logs/31_winsorize_log.txt'
os.makedirs(os.path.dirname(log_path), exist_ok=True)

df = pd.read_csv('03_Data_Clean/regression_panel_final.csv')
print(f'Loaded {len(df)} obs')

pre_outliers = df['deposit_change_qt'].describe()
print('Pre-winsorize descriptives:', pre_outliers)

# Winsorize 1%/99%
lower = df['deposit_change_qt'].quantile(0.01)
upper = df['deposit_change_qt'].quantile(0.99)
df['deposit_change_qt_winsor'] = np.clip(df['deposit_change_qt'], lower, upper)

post_outliers = df['deposit_change_qt_winsor'].describe()
print('Post-winsorize descriptives:', post_outliers)

outlier_pct = ((df['deposit_change_qt'] < lower) | (df['deposit_change_qt'] > upper)).mean() * 100
print(f'Outliers clipped: {outlier_pct:.1f}%')

df.to_csv('03_Data_Clean/regression_panel_final_winsor.csv', index=False)
with open(log_path, 'w') as f:
    f.write(f'2026-01-28: Winsorized deposit_change_qt 1%/99%. Clipped {outlier_pct:.1f}%. Lower: {lower:.3f}, Upper: {upper:.3f}\n')
print('Output: 03_Data_Clean/regression_panel_final_winsor.csv')
print('Log: 05_Outputs/Logs/31_winsorize_log.txt')