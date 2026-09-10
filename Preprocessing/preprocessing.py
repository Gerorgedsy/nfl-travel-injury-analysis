import pandas as pd
from pathlib import Path

def preprocess_injuries():
    """
    This function preprocesses the injuries dataset by performing the following steps:
    1. Load the injuries dataset from a CSV file
    2. De-duplicate records at the weekly level to avoid false breaks in injury spells
    3. Fill missing injury descriptions to ensure shift operations do not fail
    4. Calculate week gaps and injury switches to identify new injury spells
    5. Assign unique spell IDs to each injury spell
    6. Save the preprocessed dataset to a new CSV file
    7. Create another CSV with just the first week of each spell for easier analysis
    """

    # Step 1
    script_dir = Path(__file__).resolve().parent
    data_folder_path = script_dir / ".." / "Data"

    injuries = pd.read_csv(data_folder_path / "injuries.csv")

    # Step 2
    injuries = injuries.sort_values(
        by=['season', 'week', 'report_primary_injury']
    ).drop_duplicates(subset=['gsis_id', 'season', 'week'], keep='last')

    # Step 3
    injuries = injuries.sort_values(by=['gsis_id', 'season', 'week']).reset_index(drop=True)

    injuries['clean_injury'] = injuries['report_primary_injury'].fillna('Unspecified')

    # Step 4
    injuries['prev_week'] = injuries.groupby(['gsis_id', 'season'])['week'].shift(1)
    injuries['prev_injury'] = injuries.groupby(['gsis_id', 'season'])['clean_injury'].shift(1)

    injuries['is_new_spell'] = (
        injuries['prev_week'].isna()
        | (injuries['clean_injury'] != injuries['prev_injury'])
        | (injuries['week'] > (injuries['prev_week'] + 2))
    )

    # Step 5
    injuries['spell_id'] = (
        injuries.groupby(['gsis_id', 'season'])['is_new_spell'].cumsum().astype(int)
    )

    print(injuries.head())

    # Step 6
    injuries.to_csv(data_folder_path / "injuries_preprocessed.csv", index=False)

    # Step 7
    injuries_spells = (
        injuries.groupby(['gsis_id', 'full_name', 'season', 'spell_id', 'clean_injury'])
        .agg(injury_onset_week=('week', 'min'), weeks_on_report=('week', 'count'))
        .reset_index()
    )

    injuries_spells.to_csv(data_folder_path / "injuries_spells.csv", index=False)

if __name__ == "__main__":
    preprocess_injuries()