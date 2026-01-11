import pandas as pd

# Load data
df = pd.read_csv('02_Data_Intermediate/flood_exposure_panel.csv')
emdat = pd.read_csv('02_Data_Intermediate/emdat_districts_parsed.csv')

print("="*70)
print("MANUAL VALIDATION: 3 FLOOD EVENTS")
print("="*70)

# Event 1: 2019-0331-IND (Bihar/Assam floods, long district list)
print("\n[Event 1] 2019-0331-IND (July 2019 Bihar/Assam floods)")
print("-"*70)
event1 = emdat[emdat['DisNo.'] == '2019-0331-IND'].iloc[0]
print(f"Date: {event1['Start Year']}-{int(event1['Start Month'])}")
print(f"Quarter: 2019Q3")
print(f"Districts in EM-DAT (first 200 chars): {str(event1['districts_final_str'])[:200]}...")

# Check exposure
exposed_2019q3 = df[(df['quarter'] == '2019Q3') & 
                     ((df['flood_exposure_ruleA_qt'] == 1) | 
                      (df['flood_exposure_ruleB_qt'] == 1))]
print(f"\nDistricts exposed in 2019Q3:")
print(f"  Rule A: {exposed_2019q3['flood_exposure_ruleA_qt'].sum()} districts")
print(f"  Rule B: {exposed_2019q3['flood_exposure_ruleB_qt'].sum()} districts")

# Show specific Rule B districts
ruleB_dists = exposed_2019q3[exposed_2019q3['flood_exposure_ruleB_qt']==1]['district_gadm'].unique().tolist()
print(f"  Rule B districts (first 15): {ruleB_dists[:15]}")

# Event 2: 2023-0428-IND (State-only: HP, Uttarakhand, Delhi, etc.)
print("\n[Event 2] 2023-0428-IND (June 2023 multi-state floods - STATE ONLY)")
print("-"*70)
event2 = emdat[emdat['DisNo.'] == '2023-0428-IND'].iloc[0]
print(f"Date: {event2['Start Year']}-{int(event2['Start Month'])}")
print(f"Quarter: 2023Q2")
print(f"Location string: {event2['districts_final_str']}")

exposed_2023q2 = df[(df['quarter'] == '2023Q2') & 
                     ((df['flood_exposure_ruleA_qt'] == 1) | 
                      (df['flood_exposure_ruleB_qt'] == 1))]
print(f"\nDistricts exposed in 2023Q2:")
print(f"  Rule A: {exposed_2023q2['flood_exposure_ruleA_qt'].sum()} districts")
print(f"  Rule B: {exposed_2023q2['flood_exposure_ruleB_qt'].sum()} districts")

# Check if Himachal Pradesh districts got coded (Rule A only)
hp_districts_2023q2 = exposed_2023q2[(exposed_2023q2['state_gadm'] == 'Himachal Pradesh') & 
                                      (exposed_2023q2['flood_exposure_ruleA_qt'] == 1)]
print(f"  HP districts coded (Rule A): {len(hp_districts_2023q2)}")
print(f"  Sample HP districts: {hp_districts_2023q2['district_gadm'].head(5).tolist()}")

# Check Delhi (should now work with alias)
delhi_districts_2023q2 = exposed_2023q2[(exposed_2023q2['state_gadm'] == 'NCT of Delhi') & 
                                         (exposed_2023q2['flood_exposure_ruleA_qt'] == 1)]
print(f"  Delhi districts coded (Rule A): {len(delhi_districts_2023q2)}")

# Event 3: 2015-0504-IND (Specific districts in AP + TN)
print("\n[Event 3] 2015-0504-IND (Nov 2015 Andhra Pradesh/Tamil Nadu)")
print("-"*70)
event3 = emdat[emdat['DisNo.'] == '2015-0504-IND'].iloc[0]
print(f"Date: {event3['Start Year']}-{int(event3['Start Month'])}")
print(f"Quarter: 2015Q4")
print(f"Districts: {event3['districts_final_str']}")

exposed_2015q4 = df[(df['quarter'] == '2015Q4') & 
                     (df['flood_exposure_ruleB_qt'] == 1)]
print(f"\nRule B exposed districts in 2015Q4: {len(exposed_2015q4)}")

# Expected: Chittoor, Cuddapah(Kadapa), Nellore, Prakasam (AP)
#           Chennai, Cuddalore, Kancheepuram, Nagapattinam, Thiruvallur, Villupuram (TN)
print(f"\n  Expected districts (AP): Chittoor, Nellore, Prakasam")
ap_check = exposed_2015q4[exposed_2015q4['state_gadm'] == 'Andhra Pradesh']
print(f"    AP districts found: {ap_check['district_gadm'].tolist()}")

print(f"\n  Expected districts (TN): Chennai, Cuddalore, Kancheepuram")
tn_check = exposed_2015q4[exposed_2015q4['state_gadm'] == 'Tamil Nadu']
print(f"    TN districts found: {tn_check['district_gadm'].tolist()}")

print("\n" + "="*70)
print("VALIDATION COMPLETE")
print("="*70)
print("\n✓ If Event 1 shows multiple Rule B districts: Multi-district coding works")
print("✓ If Event 2 shows Rule A > 0, Rule B = 0: State fallback works")
print("✓ If Event 3 shows specific AP/TN districts: District-level matching works")