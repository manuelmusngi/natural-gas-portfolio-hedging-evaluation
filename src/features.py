from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


class FeatureError(ValueError):
    """Raised when required columns are missing for feature engineering."""


def compute_returns(prices: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    """
    Compute returns for all columns in the input price frame.

    Parameters
    ----------
    prices:
        DataFrame of price series (spot + futures + optional assets)
    config:
        includes config['returns']['method'] in {'log','simple'}

    Returns
    -------
    DataFrame of returns with suffix '_ret' for each input column name.
    """
    method = config["returns"]["method"]
    if method not in {"log", "simple"}:
        raise FeatureError(f"Unknown return method: {method}")

    df = prices.copy()
    if df.index.inferred_type not in {"datetime64", "datetime"}:
        raise FeatureError("prices index must be datetime-like.")

    if method == "log":
        rets = np.log(df).diff()
    else:
        rets = df.pct_change()

    rets = rets.replace([np.inf, -np.inf], np.nan).dropna(how="all")
    rets.columns = [f"{c}_ret" for c in rets.columns]
    return rets


def build_curve_features(futs_wide_prices: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    """
    Build curve features from wide futures price columns (fut_<TENOR>).

    Features
    --------
    - slope: fut_front - fut_back (config.regimes.curve.slope_definition)
    - generic spreads: for each pair in config.curve.get('spreads', [])

    Returns
    -------
    DataFrame with feature columns.
    """
    df = futs_wide_prices.copy()
    slope_def = config["regimes"]["curve"]["slope_definition"]
    front = slope_def["front"]
    back = slope_def["back"]

    front_col = f"fut_{front}"
    back_col = f"fut_{back}"

    _require_cols(df, [front_col, back_col])
    out = pd.DataFrame(index=df.index)

    out["curve_slope"] = df[front_col] - df[back_col]

    spreads = config["curve"].get("spreads", [])
    for sp in spreads:
        # allow either ["M1","M3"] or {"name":"M1_M3","front":"M1","back":"M3"}
        if isinstance(sp, list) and len(sp) == 2:
            a, b = sp
            name = f"spread_{a}_{b}"
            a_col, b_col = f"fut_{a}", f"fut_{b}"
        elif isinstance(sp, dict):
            name = sp.get("name") or f"spread_{sp['front']}_{sp['back']}"
            a_col, b_col = f"fut_{sp['front']}", f"fut_{sp['back']}"
        else:
            raise FeatureError("config.curve.spreads must contain 2-lists or dict specs.")

        _require_cols(df, [a_col, b_col])
        out[name] = df[a_col] - df[b_col]

    return out


def _require_cols(df: pd.DataFrame, cols: list[str]) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise FeatureError(f"Missing required columns: {missing}")
