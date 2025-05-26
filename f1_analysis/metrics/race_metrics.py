import pandas as pd
import numpy as np


def get_position_changes(final_position, grid_position):
    position_change = grid_position-final_position
    return position_change


def convert_to_timedelta_column(times):
    # Try to parse the first valid (non-None) time as the leader's time
    for t in times:
        if isinstance(t, str) and not t.startswith('+'):
            try:
                leader_time = pd.to_timedelta("0:" + t)
                break
            except Exception:
                continue
    else:
        leader_time = pd.NaT  # No valid leader time found

    td_times = []
    for t in times:
        if t is None:
            td_times.append(pd.NaT)
        elif isinstance(t, str) and t.startswith('+'):
            try:
                offset = float(t[1:])
                td_times.append(leader_time + pd.Timedelta(seconds=offset))
            except ValueError:
                try:
                    offset = pd.to_timedelta("0:" + t[1:])
                    td_times.append(leader_time + offset)
                except Exception:
                    td_times.append(pd.NaT)
        else:
            try:
                td_times.append(pd.to_timedelta("0:" + t))
            except Exception:
                td_times.append(pd.NaT)

    return pd.Series(td_times)


def get_position_interval(time_series):
    return time_series.diff().dt.total_seconds()


def compute_gini_coefficient(values):
    """Compute Gini coefficient of a list of numeric values (e.g. counts).
        Higher values mean less diversity in the metrics"""
    array = np.array(values)
    if np.amin(array) < 0:
        raise ValueError("Negative values not allowed in Gini calculation.")
    array = np.sort(array)
    n = len(array)
    cum_diffs = np.abs(array[:, None] - array).sum()
    mean = array.mean()
    if mean == 0:
        return 0
    return 1 - (cum_diffs / (2 * n**2 * mean))