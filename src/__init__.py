"""
ngas-portfolio-hedging

Lightweight, research-oriented toolkit for multi-tenor natural gas hedge evaluation:
- Data ingest (spot, curve, optional cross-assets)
- Feature engineering (returns, curve spreads)
- Regime labeling (volatility + curve shape)
- Hedge ratio estimation (static OLS + rolling covariance dynamic)
- Scenario generation (historical windows + block bootstrap)
- Risk + hedge effectiveness metrics
- Matplotlib diagnostics
"""

from __future__ import annotations

__all__ = [
    "config_loader",
    "data_loader",
    "features",
    "regimes",
    "hedging",
    "scenarios",
    "metrics",
    "plotting",
]
