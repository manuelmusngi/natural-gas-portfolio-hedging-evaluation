from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


class RegimeError(ValueError):
    """Raised when regime estimation inputs are invalid."""


def realized_volatility(returns: pd.Series, lookback: int) -> pd.Series:
    """
    Rolling realized volatility proxy: rolling std dev of returns.

    Returns a series aligned to input index.
    """
    if lookback <= 1:
        raise RegimeError("lookback must be > 1")
    r = _to_series(returns, name="returns").dropna()
    vol = r.rolling(lookback).std(ddof=1)
    return vol.reindex(returns.index)


def estimate_volatility_garch_optional(returns: pd.Series, p: int = 1, q: int = 1) -> pd.Series:
    """
    Optional GARCH( p, q ) sigma estimate.

    If `arch` is not installed, raises ImportError.

    Notes
    -----
    This is intentionally minimal; for production research, tune distributions,
    mean model, and diagnostics explicitly.
    """
    r = _to_series(returns, name="returns").dropna()

    try:
        from arch import arch_model  # type: ignore
    except Exception as e:  # pragma: no cover
        raise ImportError("Optional dependency 'arch' is required for GARCH. Install: pip install arch") from e

    am = arch_model(r * 100.0, mean="Zero", vol="GARCH", p=p, q=q, rescale=False)
    res = am.fit(disp="off")
    sigma = (res.conditional_volatility / 100.0).rename("garch_sigma")
    return sigma.reindex(returns.index)


def label_volatility_regimes(vol: pd.Series, config: dict[str, Any]) -> pd.Series:
    """
    Label volatility regimes using a quantile threshold.

    config example:
      lookback: 20
      high_quantile: 0.7
      labels: {low: "LOW_VOL", high: "HIGH_VOL"}  # optional
    """
    v = _to_series(vol, name="vol").dropna()
    q = float(config["high_quantile"])
    if not (0.0 < q < 1.0):
        raise RegimeError("high_quantile must be in (0,1).")

    thr = v.quantile(q)
    labels = config.get("labels", {"low": "LOW_VOL", "high": "HIGH_VOL"})
    out = pd.Series(np.where(v >= thr, labels["high"], labels["low"]), index=v.index, name="vol_regime")
    return out.reindex(vol.index)


def label_curve_regimes(curve_slope: pd.Series, config: dict[str, Any]) -> pd.Series:
    """
    Label curve regimes based on slope thresholds.

    curve_slope is typically (front - back).
    - Positive slope => backwardation (front > back)
    - Negative slope => contango (front < back)

    config example:
      contango_threshold: -0.05
      backwardation_threshold: 0.05
      labels: {contango:"CONTANGO", backwardation:"BACKWARDATION", flat:"FLAT"}
    """
    s = _to_series(curve_slope, name="curve_slope").dropna()
    cont_thr = float(config["contango_threshold"])
    back_thr = float(config["backwardation_threshold"])
    labels = config.get("labels", {"contango": "CONTANGO", "backwardation": "BACKWARDATION", "flat": "FLAT"})

    regime = np.full(len(s), labels["flat"], dtype=object)
    regime[s <= cont_thr] = labels["contango"]
    regime[s >= back_thr] = labels["backwardation"]

    out = pd.Series(regime, index=s.index, name="curve_regime")
    return out.reindex(curve_slope.index)


def combine_regimes(*regimes: pd.Series, sep: str = "|") -> pd.Series:
    """
    Combine multiple regime labels into a single joint regime label.
    """
    if not regimes:
        raise RegimeError("At least one regime series required.")
    aligned = [r.astype("string") for r in regimes]
    df = pd.concat(aligned, axis=1)
    combined = df.apply(lambda row: sep.join([str(x) for x in row.values]), axis=1)
    combined.name = "joint_regime"
    return combined


def _to_series(x: pd.Series, name: str) -> pd.Series:
    if not isinstance(x, pd.Series):
        raise RegimeError(f"{name} must be a pandas Series.")
    if x.name is None:
        x = x.rename(name)
    return x
