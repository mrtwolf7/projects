import pandas as pd
import numpy as np
import re


def get_games_differences(score_string):
    if pd.isna(score_string) or 'W/O' in score_string or 'RET' in score_string or 'DEF' in score_string:
        return 0
    sets = score_string.split()
    diffs = []
    for s in sets:
        s_clean = re.sub(r'\([^)]*\)', '', s)
        if '-' in s_clean:
            a, b = s_clean.split('-')
            diffs.append(int(a) - int(b))
    return sum(diffs)


def get_games_sums(score_string):
    if pd.isna(score_string) or 'W/O' in score_string or 'RET' in score_string or 'DEF' in score_string:
        return 0
    sets = score_string.split()
    sums = []
    for s in sets:
        s_clean = re.sub(r'\([^)]*\)', '', s)
        if '-' in s_clean:
            a, b = s_clean.split('-')
            sums.append(int(a) + int(b))
    return sum(sums)


def get_winner_games(score: str) -> float:
    """
    Compute total games won by the match winner from score string.
    Example: '6-4 6-4 6-4' -> 18
    """
    if not isinstance(score, str):
        return np.nan

    total = 0
    for s in score.split():
        try:
            w, _ = s.split('-')
            total += int(w)
        except ValueError:
            continue
    return total