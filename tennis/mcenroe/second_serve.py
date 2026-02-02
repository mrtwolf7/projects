import pandas as pd
import numpy as np
import glob
from second_serve_helpers import compute_second_serve_metrics, get_all_players

# --- CONFIG ---
INPUT_PATH = '../input_data/'
OUTPUT_PATH = 'output_data/'
START_YEAR = 1991


# --- LOAD ALL FILES ---
def load_all_years(start_year: int):
    files = sorted(glob.glob(f"{INPUT_PATH}atp_matches_*.csv"))
    year_files = []

    for f in files:
        year = int(f.split('_')[-1].split('.')[0])
        if year >= start_year:
            year_files.append((year, f))

    return year_files


# --- PROCESS ONE YEAR ---
def process_year(year: int, file: str):
    df = pd.read_csv(file)

    overall_rows = []
    surface_rows = []

    players = get_all_players(df)

    for player in players:
        # --- OVERALL ---
        metrics = compute_second_serve_metrics(df, player)
        if metrics is None:
            continue

        overall_rows.append({
            'year': year,
            'player': player,
            **metrics
        })

        # --- BY SURFACE ---
        for surface, df_surface in df.groupby('surface'):
            metrics_surface = compute_second_serve_metrics(df_surface, player)
            if metrics_surface is None:
                continue

            surface_rows.append({
                'year': year,
                'player': player,
                'surface': surface,
                **metrics_surface
            })

    return (
        pd.DataFrame(overall_rows),
        pd.DataFrame(surface_rows)
    )


# --- MULTI-YEAR WRAPPER ---
def process_all_years(start_year: int):
    overall_all = []
    surface_all = []

    year_files = load_all_years(start_year)

    for year, file in year_files:
        print(f"Processing {year}...")
        overall_df, surface_df = process_year(year, file)

        overall_all.append(overall_df)
        surface_all.append(surface_df)

    return (
        pd.concat(overall_all, ignore_index=True),
        pd.concat(surface_all, ignore_index=True)
    )


# --- MAIN ---
def main():
    overall_df, surface_df = process_all_years(START_YEAR)

    overall_df.to_csv(
        OUTPUT_PATH + 'second_serve_overall.csv',
        index=False
    )

    surface_df.to_csv(
        OUTPUT_PATH + 'second_serve_by_surface.csv',
        index=False
    )

    print("\n✅ Output files created:")
    print(f"  {OUTPUT_PATH}second_serve_overall.csv")
    print(f"  {OUTPUT_PATH}second_serve_by_surface.csv")


if __name__ == "__main__":
    main()
