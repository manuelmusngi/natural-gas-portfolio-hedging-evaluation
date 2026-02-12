from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


class MetricsError(ValueError):
    """Raised when metric computation fails."""


def annualized_vol(pnl_or_ret: pd.Series, periods_per_year: int = 252) -> float:
    x = _clean_series(pnl_or_ret)
    return float(x.std(ddof=1) * np.sqrt(periods_per_year))


def max_drawdown(pnl_or_ret: pd.Series) -> float:
    """
    Max drawdown on cumulative P&L (treat series as incremental P&L or returns).
    """
    x = _clean_series(pnl_or_ret)
    cum = x.cumsum()
    peak = cum.cummax()
    dd = cum - peak
    return float(dd.min())


def cvar(pnl_or_ret: pd.Series, alpha: float = 0.95) -> float:
    """
    CVaR (Expected Shortfall) on the left tail (loss tail).

    Returns the mean of observations <= VaR_{1-alpha}.
    """
    if not (0.0 < alpha < 1.0):
        raise MetricsError("alpha must be in (0,1).")
    x = _clean_series(pnl_or_ret)
    var_level = np.quantile(x, 1.0 - alpha)
    tail = x[x <= var_level]
    if tail.empty:
        return float("nan")
    return float(tail.mean())


def hedge_effectiveness_variance(unhedged_pnl: pd.Series, hedged_pnl: pd.Series) -> float:
    """
    Classic variance reduction hedge effectiveness:
      HE = 1 - Var(hedged) / Var(unhedged)
    """
    u = _align(unhedged_pnl, hedged_pnl)[0]
    h = _align(unhedged_pnl, hedged_pnl)[1]
    vu = float(u.var(ddof=1))
    vh = float(h.var(ddof=1))
    if vu == 0.0:
        return float("nan")
    return float(1.0 - vh / vu)


def hedge_effectiveness_cvar(unhedged_pnl: pd.Series, hedged_pnl: pd.Series, alpha: float = 0.95) -> float:
    """
    Tail-risk hedge effectiveness:
      HE_CVaR = 1 - CVaR(hedged)/CVaR(unhedged)

    Note: CVaR values are typically negative for P&L (loss tail).
    This ratio is meaningful as long as both CVaRs share sign and scaling.
    """
    u, h = _align(unhedged_pnl, hedged_pnl)
    cu = cvar(u, alpha=alpha)
    ch = cvar(h, alpha=alpha)
    if not np.isfinite(cu) or cu == 0.0:
        return float("nan")
    return float(1.0 - ch / cu)


def portfolio_risk_metrics(pnl_or_ret: pd.Series, alpha: float = 0.95, periods_per_year: int = 252) -> dict[str, float]:
    x = _clean_series(pnl_or_ret)
    return {
        "ann_vol": annualized_vol(x, periods_per_year=periods_per_year),
        "cvar": cvar(x, alpha=alpha),
        "max_drawdown": max_drawdown(x),
        "mean": float(x.mean()),
    }


def _clean_series(x: pd.Series) -> pd.Series:
    if not isinstance(x, pd.Series):
        raise MetricsError("Input must be a pandas Series.")
    s = x.astype(float).replace([np.inf, -np.inf], np.nan).dropna()
    if s.empty:
        raise MetricsError("Series is empty after cleaning.")
    return s


def _align(a: pd.Series, b: pd.Series) -> tuple[pd.Series, pd.Series]:
    idx = a.index.intersection(b.index)
    if len(idx) < 5:
        raise MetricsError("Not enough overlapping observations to compute metric.")
    return a.loc[idx].astype(float), b.loc[idx].astype(float)
