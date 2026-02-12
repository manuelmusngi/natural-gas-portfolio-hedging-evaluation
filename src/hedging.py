from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


class HedgingError(ValueError):
    """Raised when hedge ratio estimation or application fails."""


def estimate_hedge_ratios_ols(
    spot_ret: pd.Series,
    futs_ret: pd.DataFrame,
    regime: pd.Series | None = None,
    add_intercept: bool = True,
) -> dict[str, pd.Series | float]:
    """
    Estimate static hedge ratios via OLS for each futures tenor.
    Optionally estimate per-regime (returns a time-aligned series with regime-mapped ratios).

    Returns
    -------
    dict mapping tenor_col -> hedge_ratio
      - if regime is None: float beta
      - else: pd.Series beta_t aligned to index (beta depends on regime label at t)
    """
    _check_series(spot_ret, "spot_ret")
    _check_frame(futs_ret, "futs_ret")

    idx = spot_ret.index.intersection(futs_ret.index)
    y = spot_ret.loc[idx].astype(float)
    X = futs_ret.loc[idx].astype(float)

    if regime is not None:
        reg = regime.loc[idx].astype("string")
    else:
        reg = None

    out: dict[str, pd.Series | float] = {}
    for col in X.columns:
        x = X[col]
        mask = y.notna() & x.notna()
        if mask.sum() < 10:
            raise HedgingError(f"Not enough observations to estimate OLS hedge ratio for {col}.")

        if reg is None:
            beta = _ols_beta(y[mask].values, x[mask].values, add_intercept=add_intercept)
            out[col] = float(beta)
        else:
            betas_by_regime: dict[str, float] = {}
            for rlab, sub in pd.DataFrame({"y": y, "x": x, "r": reg}).dropna().groupby("r"):
                if len(sub) < 10:
                    continue
                betas_by_regime[str(rlab)] = float(_ols_beta(sub["y"].values, sub["x"].values, add_intercept=add_intercept))

            if not betas_by_regime:
                raise HedgingError(f"Could not estimate any regime-specific hedge ratios for {col} (too few obs).")

            beta_t = reg.map(lambda rlab: betas_by_regime.get(str(rlab), np.nan)).astype(float)
            beta_t.name = f"beta_ols_{col}"
            out[col] = beta_t

    return out


def estimate_hedge_ratios_rolling_cov(
    spot_ret: pd.Series,
    futs_ret: pd.DataFrame,
    lookback: int,
    min_obs: int,
) -> dict[str, pd.Series]:
    """
    Dynamic hedge ratios via rolling covariance:
        h_t = Cov(spot, fut)/Var(fut) over trailing window.

    This is a pragmatic substitute for DCC when you want time variation without heavy deps.
    """
    if lookback <= 1:
        raise HedgingError("lookback must be > 1")
    if min_obs < 5:
        raise HedgingError("min_obs must be >= 5")

    _check_series(spot_ret, "spot_ret")
    _check_frame(futs_ret, "futs_ret")

    idx = spot_ret.index.intersection(futs_ret.index)
    y = spot_ret.loc[idx].astype(float)
    X = futs_ret.loc[idx].astype(float)

    out: dict[str, pd.Series] = {}
    for col in X.columns:
        x = X[col]

        cov = y.rolling(lookback, min_periods=min_obs).cov(x)
        var = x.rolling(lookback, min_periods=min_obs).var(ddof=1)
        h = (cov / var).replace([np.inf, -np.inf], np.nan)
        h.name = f"beta_rollcov_{col}"
        out[col] = h.reindex(spot_ret.index)

    return out


def apply_hedge(
    spot_ret: pd.Series,
    fut_ret: pd.Series,
    hedge_ratio: float | pd.Series,
    notional: float,
) -> pd.Series:
    """
    Apply a single-instrument hedge:
        pnl = notional * (spot_ret - h * fut_ret)

    hedge_ratio can be scalar or time series.
    """
    _check_series(spot_ret, "spot_ret")
    _check_series(fut_ret, "fut_ret")
    if notional <= 0:
        raise HedgingError("notional must be > 0")

    idx = spot_ret.index.intersection(fut_ret.index)
    s = spot_ret.loc[idx].astype(float)
    f = fut_ret.loc[idx].astype(float)

    if isinstance(hedge_ratio, pd.Series):
        h = hedge_ratio.reindex(idx).astype(float)
    else:
        h = float(hedge_ratio)
        h = pd.Series(h, index=idx)

    pnl = notional * (s - h * f)
    pnl.name = "hedged_pnl"
    return pnl


def apply_multi_tenor_hedge(
    spot_ret: pd.Series,
    futs_ret: pd.DataFrame,
    hedge_ratios: dict[str, float | pd.Series],
    weights: dict[str, float] | None,
    notional: float,
) -> pd.Series:
    """
    Multi-tenor hedge:
        pnl = notional * (spot_ret - sum_i w_i * h_i * fut_i)

    weights:
      - if None: equal weights across provided hedge_ratios keys
      - otherwise: must sum to 1.0 approximately
    """
    _check_series(spot_ret, "spot_ret")
    _check_frame(futs_ret, "futs_ret")
    if notional <= 0:
        raise HedgingError("notional must be > 0")

    idx = spot_ret.index.intersection(futs_ret.index)
    s = spot_ret.loc[idx].astype(float)
    X = futs_ret.loc[idx].astype(float)

    keys = list(hedge_ratios.keys())
    missing = [k for k in keys if k not in X.columns]
    if missing:
        raise HedgingError(f"hedge_ratios keys not found in futs_ret columns: {missing}")

    if weights is None:
        w = {k: 1.0 / len(keys) for k in keys}
    else:
        w = dict(weights)
        if set(w.keys()) != set(keys):
            raise HedgingError("weights keys must match hedge_ratios keys exactly.")
        ssum = sum(w.values())
        if not np.isfinite(ssum) or abs(ssum - 1.0) > 1e-6:
            raise HedgingError("weights must sum to 1.0.")

    hedge_term = pd.Series(0.0, index=idx)
    for k in keys:
        hr = hedge_ratios[k]
        if isinstance(hr, pd.Series):
            h = hr.reindex(idx).astype(float)
        else:
            h = pd.Series(float(hr), index=idx)
        hedge_term = hedge_term + w[k] * h * X[k]

    pnl = notional * (s - hedge_term)
    pnl.name = "multi_tenor_hedged_pnl"
    return pnl


def _ols_beta(y: np.ndarray, x: np.ndarray, add_intercept: bool) -> float:
    if add_intercept:
        X = np.column_stack([np.ones_like(x), x])
        beta = np.linalg.lstsq(X, y, rcond=None)[0][1]
    else:
        denom = float(np.dot(x, x))
        if denom == 0.0:
            return np.nan
        beta = float(np.dot(x, y) / denom)
    return float(beta)


def _check_series(x: pd.Series, name: str) -> None:
    if not isinstance(x, pd.Series):
        raise HedgingError(f"{name} must be a pandas Series.")
    if x.index.inferred_type not in {"datetime64", "datetime"}:
        raise HedgingError(f"{name} must have a datetime-like index.")


def _check_frame(x: pd.DataFrame, name: str) -> None:
    if not isinstance(x, pd.DataFrame):
        raise HedgingError(f"{name} must be a pandas DataFrame.")
    if x.index.inferred_type not in {"datetime64", "datetime"}:
        raise HedgingError(f"{name} must have a datetime-like index.")
