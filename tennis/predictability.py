import pandas as pd
import numpy as np
from helpers import get_games_differences, get_games_sums, get_winner_games

# --- CONFIG ---
path = 'input_data/'
output_path = 'output_data/'
tournament_types = ['G', 'M']
tournament_rounds = ['R16', 'QF', 'SF', 'F']


# --- LOAD DATASET ---
def load_dataset(year: int) -> pd.DataFrame:
    """Load ATP matches for the given year, filtered to Grand Slams and Masters 1000."""
    df = pd.read_csv(path + f'atp_matches_{year}.csv')
    df_filtered = df.loc[df['tourney_level'].isin(tournament_types)]
    return df_filtered


# --- COMPUTE ROUND METRICS ---
def compute_indicators(df: pd.DataFrame):
    """Compute base indicators for a tournament or round."""
    if df.empty:
        return 0, np.nan, np.nan, np.nan, np.nan

    df = df.copy()
    df['sets_count'] = df['score'].str.count('-')
    df['differences'] = df['score'].apply(get_games_differences)
    df['tot_games'] = df['score'].apply(get_games_sums)
    df['winner_games'] = df['score'].apply(get_winner_games)

    avg_sets = df['sets_count'].mean()
    avg_diff_games = df['differences'].mean()
    avg_tot_games = df['tot_games'].mean()
    avg_rank = df['winner_rank'].mean()
    fave_ratio = (df['winner_rank'] < df['loser_rank']).mean()

    return avg_sets, avg_diff_games, avg_tot_games, avg_rank, fave_ratio


# --- TOURNAMENT METRICS (overall + per round) ---
def get_tournament_metrics(df: pd.DataFrame):
    """Compute overall and per-round metrics for a tournament."""
    round_metrics = {}

    overall_metrics_keys = [
        'avg_sets',
        'avg_diff_games',
        'avg_tot_games',
        'avg_rank',
        'fave_ratio'
    ]

    overall_values = compute_indicators(df)
    overall_metrics = dict(zip(overall_metrics_keys, overall_values))

    for rnd in tournament_rounds:
        r_metrics = compute_indicators(df[df['round'] == rnd])
        round_metrics.update({
            f'{k}_{rnd}': v
            for k, v in zip(overall_metrics_keys, r_metrics)
        })

    return overall_metrics, round_metrics


# --- PREDICTABILITY METRICS ---
def compute_predictability(metrics: dict):
    avg_winner_rank = np.nanmean([
        metrics.get('avg_rank_R16'),
        metrics.get('avg_rank_QF'),
        metrics.get('avg_rank_SF'),
        metrics.get('avg_rank_F')
    ])

    rank_drop = (
        (metrics.get('avg_rank_F') - metrics.get('avg_rank_R16'))
        / metrics.get('avg_rank_R16')
        if metrics.get('avg_rank_R16') else np.nan
    )

    avg_fave_ratio = np.nanmean([
        metrics.get('fave_ratio_R16'),
        metrics.get('fave_ratio_QF'),
        metrics.get('fave_ratio_SF'),
        metrics.get('fave_ratio_F')
    ])

    return avg_winner_rank, rank_drop, avg_fave_ratio


# --- COMPETITIVENESS METRICS ---
def compute_competitiveness(metrics: dict):
    tourney_level = metrics.get('tourney_level', 'G')
    n_sets = 5 if tourney_level == 'G' else 3
    max_games = 13 * n_sets

    match_tightness = np.nanmean([
        metrics.get('avg_tot_games_R16') / max_games,
        metrics.get('avg_tot_games_QF') / max_games,
        metrics.get('avg_tot_games_SF') / max_games,
        metrics.get('avg_tot_games_F') / max_games
    ])

    match_balance = 1 - np.nanmean([
        metrics.get('avg_diff_games_R16') / metrics.get('avg_tot_games_R16'),
        metrics.get('avg_diff_games_QF') / metrics.get('avg_tot_games_QF'),
        metrics.get('avg_diff_games_SF') / metrics.get('avg_tot_games_SF'),
        metrics.get('avg_diff_games_F') / metrics.get('avg_tot_games_F')
    ])

    return match_tightness, match_balance


# --- AGGREGATE TOURNAMENT SCORE ---
def get_tournament_scores(metrics: dict):
    avg_winner_rank, rank_drop, avg_fave_ratio = compute_predictability(metrics)
    match_tightness, match_balance = compute_competitiveness(metrics)

    return {
        'avg_winner_rank': avg_winner_rank,
        'rank_drop': rank_drop,
        'avg_fave_ratio': avg_fave_ratio,
        'match_tightness': match_tightness,
        'match_balance': match_balance
    }


# --- PROCESS ONE YEAR ---
def process_year(year: int):
    df_year = load_dataset(year)

    overall_results = []
    round_results = []

    for tourney_id, df_tournament in df_year.groupby('tourney_id'):
        tourney_name = df_tournament['tourney_name'].iloc[0]
        tourney_level = df_tournament['tourney_level'].iloc[0]
        surface = df_tournament['surface'].iloc[0]

        df_tournament = df_tournament.copy()
        df_tournament['winner_games'] = df_tournament['score'].apply(get_winner_games)

        avg_winner_games = df_tournament['winner_games'].mean()

        final_match = df_tournament[df_tournament['round'] == 'F']
        final_winner_rank = (
            final_match['winner_rank'].iloc[0]
            if not final_match.empty
            else np.nan
        )

        overall_metrics, round_metrics = get_tournament_metrics(df_tournament)

        metrics = {
            **overall_metrics,
            **round_metrics,
            'tourney_level': tourney_level
        }

        scores = get_tournament_scores(metrics)

        overall_results.append({
            'year': year,
            'tournament': tourney_name,
            'surface': surface,
            'tourney_level': tourney_level,
            **overall_metrics,
            **scores,
            'avg_winner_games': avg_winner_games,
            'final_winner_rank': final_winner_rank
        })

        round_results.append({
            'year': year,
            'tournament': tourney_name,
            'surface': surface,
            'tourney_level': tourney_level,
            **round_metrics
        })

    return pd.DataFrame(overall_results), pd.DataFrame(round_results)


# --- MULTI-YEAR WRAPPER ---
def process_multiple_years(years: list):
    all_overall = []
    all_rounds = []

    for year in years:
        print(f"Processing {year}...")
        overall_df, rounds_df = process_year(year)
        all_overall.append(overall_df)
        all_rounds.append(rounds_df)

    return (
        pd.concat(all_overall, ignore_index=True),
        pd.concat(all_rounds, ignore_index=True)
    )


# --- MAIN ---
def main():
    years = list(range(1968, 2025))
    # years = [2024]

    overall_df, rounds_df = process_multiple_years(years)

    overall_df.to_csv(
        output_path + 'tournaments_overall_all_years.csv',
        index=False
    )

    rounds_df.to_csv(
        output_path + 'tournaments_rounds_all_years.csv',
        index=False
    )

    print("\n✅ Saved:")
    print(f"  {output_path}tournaments_overall_all_years.csv")
    print(f"  {output_path}tournaments_rounds_all_years.csv")


if __name__ == "__main__":
    main()
