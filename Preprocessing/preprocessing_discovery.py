import pandas as pd
from pathlib import Path

pd.set_option('display.max_columns', None)

script_dir = Path(__file__).resolve().parent
data_folder_path = script_dir / ".." / "Data"

injuries = pd.read_csv(data_folder_path / "injuries.csv")
#print(injuries['season'].value_counts()) -- goes back to 2009
#print(injuries.isnull().sum()) -- can drop nulls for this dataframe, if injury is null it doesn't really matter

injuries_raw = injuries[injuries['season'] == 2020].copy()
# Filter specifically for Christian McCaffrey to demonstrate the fix
cmc = injuries_raw[injuries_raw['gsis_id'] == '00-0033280'].copy()

# 2. De-duplicate at the weekly level so practice reports don't trigger false breaks
# Keep the most detailed record per week
cmc = cmc.sort_values(
    by=['season', 'week', 'report_primary_injury']
).drop_duplicates(subset=['gsis_id', 'season', 'week'], keep='last')

# Sort chronologically
cmc = cmc.sort_values(by=['gsis_id', 'season', 'week']).reset_index(drop=True)

# 3. Fill missing injury descriptions temporarily so shift operations don't fail
cmc['clean_injury'] = cmc['report_primary_injury'].fillna('Unspecified')

# 4. Calculate week gaps and injury switches
cmc['prev_week'] = cmc.groupby(['gsis_id', 'season'])['week'].shift(1)
cmc['prev_injury'] = cmc.groupby(['gsis_id', 'season'])['clean_injury'].shift(
    1
)

# A new spell starts if:
# - It's the player's first record (prev_week is NaN)
# - The injury type changed
# - There was a gap of more than 2 week between reports
cmc['is_new_spell'] = (
    cmc['prev_week'].isna()
    | (cmc['clean_injury'] != cmc['prev_injury'])
    | (cmc['week'] > (cmc['prev_week'] + 2))
)

# 5. Assign unique spell ID
cmc['spell_id'] = (
    cmc.groupby(['gsis_id', 'season'])['is_new_spell'].cumsum().astype(int)
)

# 6. Group by spell to get onset and duration
cmc_spells = (
    cmc.groupby(['gsis_id', 'full_name', 'season', 'spell_id', 'clean_injury'])
    .agg(injury_onset_week=('week', 'min'), weeks_on_report=('week', 'count'))
    .reset_index()
)

print(
    cmc_spells[
        [
            'full_name',
            'season',
            'spell_id',
            'clean_injury',
            'injury_onset_week',
            'weeks_on_report',
        ]
    ].to_string()
)

# DATA LIMITATION: Injured Reserve designations that happen before the mid-week practice reports will never show, 
# so we don't know what injury they had for severe things like this