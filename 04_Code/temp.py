import subprocess
import pandas as pd

# This is what git checkout does -- reads the committed file content and writes it to disk
result = subprocess.run(
    ['git', 'show', 'f287cf5:02_Data_Intermediate/flood_exposure_panel.csv'],
    capture_output=True, cwd='e:/Climate-Migration-Bank-Fragility'
)
with open('02_Data_Intermediate/flood_exposure_panel.csv', 'wb') as f:
    f.write(result.stdout)

result2 = subprocess.run(
    ['git', 'show', 'f287cf5:02_Data_Intermediate/district_crosswalk_draft.csv'],
    capture_output=True, cwd='e:/Climate-Migration-Bank-Fragility'
)
with open('02_Data_Intermediate/district_crosswalk_draft.csv', 'wb') as f:
    f.write(result2.stdout)

# Verify immediately
flood = pd.read_csv('02_Data_Intermediate/flood_exposure_panel.csv')
cw = pd.read_csv('02_Data_Intermediate/district_crosswalk_draft.csv')
print("Crosswalk rows:", len(cw))
print("Flood Rule A events:", flood['flood_exposure_ruleA_qt'].sum())