from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class PlottingError(ValueError):
    """Raised when plotting inputs are invalid."""


def plot_regimes(
    df: pd.DataFrame,
    vol_col: str,
    vol_regime_col: str,
    curve_regime_col: str | None = None,
    title: str = "Volatility and regimes",
) -> None:
    _require_cols(df, [vol_col, vol_regime_col])

    fig, ax = plt.subplots(figsize=(12, 4))
    df[vol_col].plot(ax=ax, color="black", linewidth=1.2, label=vol_col)

    # shade high vol periods if label exists
    high_mask = df[vol_regime_col].astype(str).str.contains("HIGH", case=False, na=False)
    ax.fill_between(df.index, df[vol_col].min(), df[vol_col].max(), where=high_mask, alpha=0.15, label="high vol")

    ax.set_title(title)
    ax.set_ylabel("Vol proxy")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.show()

    if curve_regime_col is not None and curve_regime_col in df.columns:
        fig, ax = plt.subplots(figsize=(12, 1.8))
        y = df[curve_regime_col].astype(str)
        ax.plot(df.index, np.zeros(len(df)), alpha=0)  # anchor
        ax.set_title("Curve regime (labels)")
        ax.set_yticks([])
        ax.grid(True, axis="x", alpha=0.15)
        # annotate sparse points
        step = max(1, len(df) // 12)
        for i in range(0, len(df), step):
            ax.text(df.index[i], 0, y.iloc[i], rotation=45, ha="right", va="center", fontsize=9)
        plt.tight_layout()
        plt.show()


def plot_hedge_ratios(hedge_ratios: dict[str, float | pd.Series], title: str = "Hedge ratios") -> None:
    fig, ax = plt.subplots(figsize=(12, 4))

    any_series = False
    for k, v in hedge_ratios.items():
        if isinstance(v, pd.Series):
            any_series = True
            v.plot(ax=ax, label=k, linewidth=1.0)
        else:
            ax.axhline(float(v), linestyle="--", linewidth=1.2, label=f"{k} (const)")

    ax.set_title(title)
    ax.set_ylabel("hedge ratio")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    plt.tight_layout()
    plt.show()


def plot_pnl_distributions(unhedged_pnl: pd.Series, hedged_pnls: pd.DataFrame, title: str = "P&L distributions") -> None:
    if not isinstance(hedged_pnls, pd.DataFrame):
        raise PlottingError("hedged_pnls must be a DataFrame.")

    fig, ax = plt.subplots(figsize=(12, 4))
    u = unhedged_pnl.dropna().astype(float)
    ax.hist(u.values, bins=60, alpha=0.35, density=True, label="unhedged")

    # overlay up to 5 hedged series to keep readable
    cols = list(hedged_pnls.columns)[:5]
    for c in cols:
        x = hedged_pnls[c].dropna().astype(float)
        ax.hist(x.values, bins=60, alpha=0.25, density=True, label=c)

    ax.set_title(title)
    ax.set_xlabel("incremental P&L")
    ax.set_ylabel("density")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    plt.tight_layout()
    plt.show()


def _require_cols(df: pd.DataFrame, cols: list[str]) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise PlottingError(f"Missing required columns: {missing}")
