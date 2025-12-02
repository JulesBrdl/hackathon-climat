# Script to extract manually down loaded zipfiles into csv

import zipfile
import os
import pandas as pd

from io import TextIOWrapper

# --- SETTINGS ---
input_folder = "data/incendies/"        # folder containing .zip files
merged_output = "data/incendies/incendies.csv"      # final merged csv path
# -----------------

def read_csv_from_zip(zip_path):
    """Reads one CSV from a ZIP and returns a dataframe with correct header skipping."""
    
    with zipfile.ZipFile(zip_path, "r") as z:
        # find the CSV file inside the zip
        csv_inside = [f for f in z.namelist() if f.lower().endswith(".csv")][0]
        
        # open the CSV as text stream
        with z.open(csv_inside, "r") as raw:
            text = TextIOWrapper(raw, encoding="utf-8", errors="replace")
            lines = text.readlines()

    # detect header row
    header_idx = None
    for i, line in enumerate(lines):
        if line.startswith("Année;"):
            header_idx = i
            break
    
    if header_idx is None:
        raise ValueError(f"No header found in ZIP: {zip_path}")

    # read CSV from memory
    df = pd.read_csv(
        pd.io.common.StringIO("".join(lines)),
        sep=";",
        skiprows=header_idx,
        dtype=str,
        engine="c",
    )
    return df

# --- PROCESS ALL ZIP FILES ---
dfs = []

for file in os.listdir(input_folder):
    if file.lower().endswith(".zip"):
        zip_path = os.path.join(input_folder, file)
        print(f"Loading {zip_path}...")
        df = read_csv_from_zip(zip_path)
        dfs.append(df)

# --- MERGE ---
merged_df = pd.concat(dfs, ignore_index=True)

# --- SAVE ---
merged_df.to_csv(merged_output, index=False)

print(f"Merged CSV saved to: {merged_output}")