import numpy as np
import pandas as pd


def compute_second_serve_metrics(df: pd.DataFrame, player: str) -> dict:
    """
    Compute second-serve metrics for a given player on a given dataframe slice.
    """
    df_w = df[df['winner_name'] == player]
    df_l = df[df['loser_name'] == player]

    matches_w = len(df_w)
    matches_l = len(df_l)
    matches_tot = matches_w + matches_l

    if matches_tot == 0:
        return None

    # Percent second serve won
    perc_2nd_w = df_w['w_2ndWon'].mean()
    perc_2nd_l = df_l['l_2ndWon'].mean()

    perc_2nd_overall = (
        perc_2nd_w * matches_w + perc_2nd_l * matches_l
    ) / matches_tot

    # Margin on second serve (won matches only, consistent with your logic)
    margin_2nd_w = (
        df_w['w_2ndWon'].mean() - df_w['l_2ndWon'].mean()
        if matches_w > 0 else np.nan
    )

    # Matches won thanks to second serve
    matches_2nd_w = len(
        df_w[
            (df_w['w_1stWon'] <= df_w['l_1stWon']) &
            (df_w['w_2ndWon'] > df_w['l_2ndWon'])
        ]
    )

    return {
        'matches_tot': matches_tot,
        'matches_w': matches_w,
        'perc_2nd_overall': perc_2nd_overall,
        'perc_2nd_w': perc_2nd_w,
        'margin_2nd_w': margin_2nd_w,
        'matches_2nd_w': matches_2nd_w
    }


def get_all_players(df: pd.DataFrame) -> set:
    """Return set of all players appearing in the dataframe."""
    return set(df['winner_name']).union(set(df['loser_name']))
