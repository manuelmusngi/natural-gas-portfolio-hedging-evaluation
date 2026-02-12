from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import numpy as np
import pandas as pd


class ScenarioError(ValueError):
    """Raised when scenario generation or application fails."""


def build_historical_scenarios(
    returns_df: pd.DataFrame,
    window: int,
    step: int = 1,
    start: str | None = None,
    end: str | None = None,
) -> dict[str, pd.DataFrame]:
    """
    Create overlapping historical window scenarios from returns_df.

    Returns a dict:
      scenario_id -> DataFrame slice of length=window
    """
    if window <= 1:
        raise ScenarioError("window must be > 1.")
    if step <= 0:
        raise ScenarioError("step must be > 0.")

    df = returns_df.sort_index()
    if start is not None:
        df = df.loc[pd.to_datetime(start) :]
    if end is not None:
        df = df.loc[: pd.to_datetime(end)]

    if len(df) < window:
        raise ScenarioError("Not enough data for requested historical scenario window.")

    scenarios: dict[str, pd.DataFrame] = {}
    for i in range(0, len(df) - window + 1, step):
        sl = df.iloc[i : i + window]
        sid = f"hist_{sl.index[0].date()}_{sl.index[-1].date()}"
        scenarios[sid] = sl

    return scenarios


def build_block_bootstrap_scenarios(
    returns_df: pd.DataFrame,
    block_size: int,
    n_paths: int,
    path_length: int | None = None,
    seed: int | None = None,
) -> dict[str, pd.DataFrame]:
    """
    Block bootstrap scenarios to preserve autocorrelation.

    Parameters
    ----------
    returns_df:
        DataFrame of returns (rows=dates, cols=return series)
    block_size:
        Length of each block
    n_paths:
        Number of simulated paths
    path_length:
        Desired length of each path; default len(returns_df)
    seed:
        RNG seed

    Returns
    -------
    dict of scenario_id -> DataFrame path (index is integer step)
    """
    if block_size <= 0:
        raise ScenarioError("block_size must be > 0.")
    if n_paths <= 0:
        raise ScenarioError("n_paths must be > 0.")

    df = returns_df.dropna().copy()
    if df.empty:
        raise ScenarioError("returns_df is empty after dropna().")

    T = int(path_length) if path_length is not None else len(df)
    if T <= 1:
        raise ScenarioError("path_length must be > 1.")
    if len(df) < block_size:
        raise ScenarioError("Not enough rows to form a single block.")

    rng = np.random.default_rng(seed)
    starts = np.arange(0, len(df) - block_size + 1)

    scenarios: dict[str, pd.DataFrame] = {}
    for p in range(n_paths):
        pieces = []
        while sum(len(x) for x in pieces) < T:
            st = int(rng.choice(starts))
            pieces.append(df.iloc[st : st + block_size])
        path = pd.concat(pieces, axis=0).iloc[:T].reset_index(drop=True)
        path.index.name = "t"
        scenarios[f"boot_{p:04d}"] = path

    return scenarios


def apply_scenario_single_hedge(
    scenario_returns: pd.DataFrame,
    spot_ret_col: str,
    fut_ret_col: str,
    hedge_ratio: float | pd.Series,
    notional: float,
) -> pd.Series:
    """
    Apply a single-instrument hedge to a scenario return path.

    scenario_returns:
      DataFrame containing the relevant return columns. Index can be datetime or step integer.
    """
    if spot_ret_col not in scenario_returns.columns:
        raise ScenarioError(f"Missing spot_ret_col '{spot_ret_col}' in scenario returns.")
    if fut_ret_col not in scenario_returns.columns:
        raise ScenarioError(f"Missing fut_ret_col '{fut_ret_col}' in scenario returns.")
    if notional <= 0:
        raise ScenarioError("notional must be > 0.")

    s = scenario_returns[spot_ret_col].astype(float)
    f = scenario_returns[fut_ret_col].astype(float)

    if isinstance(hedge_ratio, pd.Series):
        h = hedge_ratio.reindex(s.index).astype(float)
        if h.isna().all():
            raise ScenarioError("hedge_ratio series does not align with scenario index (all NaN after reindex).")
    else:
        h = pd.Series(float(hedge_ratio), index=s.index)

    pnl = notional * (s - h * f)
    pnl.name = "scenario_hedged_pnl"
    return pnl
