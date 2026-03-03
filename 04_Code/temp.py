print("\n[DIAGNOSTIC] Comparing merge key values...")
print("VIIRS sample (after rename):")
print(viirs_quarterly[['district_gadm', 'state_gadm']].head(5).to_string(index=False))
print("\nMaster panel sample:")
print(valid_districts.head(5).to_string(index=False))

# Check overlap manually
viirs_keys  = set(zip(viirs_quarterly['district_gadm'], viirs_quarterly['state_gadm']))
master_keys = set(zip(valid_districts['district_gadm'], valid_districts['state_gadm']))
overlap     = viirs_keys & master_keys
print(f"\nOverlapping keys: {len(overlap)}")
print(f"VIIRS only: {len(viirs_keys - master_keys)}")
print(f"Master only: {len(master_keys - viirs_keys)}")