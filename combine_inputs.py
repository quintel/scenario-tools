"""
Combines 14 KM scenario input CSVs with the reference metadata CSV
into a single wide-format CSV.

Usage: pipenv run python combine_inputs.py
"""

import csv
import re
from pathlib import Path

OUTPUT_DIR = Path('data/output')
REFERENCE_CSV = OUTPUT_DIR / 'inputs-dordrecht-2040.csv'
OUTPUT_FILE = OUTPUT_DIR / 'input_reg-km_stable_drechtsteden.csv'

SCENARIOS_40 = [
    'KM_stable_Alblasserdam_40',
    'KM_stable_Dordrecht_40',
    'KM_stable_Hardinxveld-Giessendam_40',
    'KM_stable_Hendrik-Ido-Ambacht_40',
    'KM_stable_Papendrecht_40',
    'KM_stable_Sliedrecht_40',
    'KM_stable_Zwijndrecht_40',
]

SCENARIOS_50 = [
    'KM_stable_Alblasserdam_50',
    'KM_stable_Dordrecht_50',
    'KM_stable_Hardinxveld-Giessendam_50',
    'KM_stable_Hendrik-Ido-Ambacht_50',
    'KM_stable_Papendrecht_50',
    'KM_stable_Sliedrecht_50',
    'KM_stable_Zwijndrecht_50',
]

ALL_SCENARIOS = SCENARIOS_40 + SCENARIOS_50


def parse_inputs_csv(filepath):
    """
    Parse the mangled JSON-as-CSV format produced when pd.read_csv() is called
    on the ETM API's JSON /inputs response, then saved with df.to_csv().

    Returns a dict of {slider_key: user_value_or_None}.
    """
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # single header row, no data rows

    cols = header

    # Group columns: each new group starts with a col containing key:{"min":
    groups = []
    current = []
    for col in cols:
        if re.search(r'\w+:\{"min":', col):
            if current:
                groups.append(current)
            current = [col]
        else:
            current.append(col)
    if current:
        groups.append(current)

    results = {}
    for group in groups:
        # First column: [{ key:{"min":value  (leading { optional)
        key_match = re.search(r'(\w+):\{"min":([-\d.]+)', group[0])
        if not key_match:
            continue
        key = key_match.group(1)

        # Find user value among group columns; pandas appends .N to de-duplicate
        user_val = None
        for col in group:
            user_match = re.match(r'user:([-\d.]+(?:\.\d+)?)', col)
            if user_match:
                raw = user_match.group(1)
                try:
                    user_val = float(raw)
                except ValueError:
                    # Strip trailing pandas dedup suffix (.N)
                    stripped = re.sub(r'\.\d+$', '', raw)
                    user_val = float(stripped)
                break

        results[key] = user_val

    return results


def load_reference(filepath):
    """Load reference CSV, return list of row dicts with clean column names."""
    with open(filepath, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def main():
    # Load metadata from reference file
    print(f'Loading reference: {REFERENCE_CSV}')
    ref_rows = load_reference(REFERENCE_CSV)
    print(f'  {len(ref_rows)} sliders in reference')

    # Parse all scenario input CSVs
    scenario_data = {}
    for scenario in ALL_SCENARIOS:
        csv_path = OUTPUT_DIR / scenario / f'{scenario}_inputs.csv'
        print(f'Parsing {csv_path.name} ...')
        scenario_data[scenario] = parse_inputs_csv(csv_path)
        n_user = sum(1 for v in scenario_data[scenario].values() if v is not None)
        print(f'  {len(scenario_data[scenario])} keys, {n_user} with user values')

    # Build output rows
    meta_cols = ['Sidebar', 'Sectie', 'Slide', 'Naam', 'Key',
                 'Minimumwaarde', 'Maximumwaarde', 'Standaardwaarde', 'Eenheid']
    out_cols = meta_cols + ALL_SCENARIOS

    out_rows = []
    for row in ref_rows:
        key = row['Key']
        out_row = {
            'Sidebar': row['Sidebar'],
            'Sectie': row['Sectie'],
            'Slide': row['Slide'],
            'Naam': row['Naam'],
            'Key': key,
            'Minimumwaarde': row['Minimumwaarde'],
            'Maximumwaarde': row['Maximumwaarde'],
            'Standaardwaarde': row['Standaardwaarde'],
            'Eenheid': row['Eenheid'],
        }
        for scenario in ALL_SCENARIOS:
            val = scenario_data[scenario].get(key)
            out_row[scenario] = '' if val is None else val
        out_rows.append(out_row)

    # Write output
    print(f'\nWriting {OUTPUT_FILE} ...')
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=out_cols)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f'Done. {len(out_rows)} rows, {len(out_cols)} columns.')


if __name__ == '__main__':
    main()
