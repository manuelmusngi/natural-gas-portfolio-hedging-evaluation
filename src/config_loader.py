from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml


class ConfigError(ValueError):
    """Raised when configuration is missing required keys or is malformed."""


def load_config(path: str | Path) -> dict[str, Any]:
    """
    Load YAML config into a dict.

    Parameters
    ----------
    path:
        Path to config.yaml

    Returns
    -------
    dict
        Parsed configuration.

    Raises
    ------
    FileNotFoundError, ConfigError
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    if not isinstance(cfg, dict):
        raise ConfigError("Config root must be a mapping/dict.")

    _validate_config(cfg)
    return cfg


def _require(cfg: Mapping[str, Any], key: str) -> Any:
    if key not in cfg:
        raise ConfigError(f"Missing required config key: '{key}'")
    return cfg[key]


def _validate_config(cfg: Mapping[str, Any]) -> None:
    data = _require(cfg, "data")
    _require(data, "spot_file")
    _require(data, "futures_file")
    # cross_assets_file is optional

    curve = _require(cfg, "curve")
    _require(curve, "tenors")
    if not isinstance(curve["tenors"], list) or not curve["tenors"]:
        raise ConfigError("config.curve.tenors must be a non-empty list (e.g., ['M1','M2','Q1']).")

    _require(cfg, "portfolio")
    _require(cfg["portfolio"], "base_notional")

    returns = _require(cfg, "returns")
    _require(returns, "method")
    if returns["method"] not in {"log", "simple"}:
        raise ConfigError("config.returns.method must be one of: 'log', 'simple'.")

    regimes = _require(cfg, "regimes")
    _require(regimes, "volatility")
    _require(regimes["volatility"], "lookback")
    _require(regimes["volatility"], "high_quantile")

    _require(regimes, "curve")
    _require(regimes["curve"], "slope_definition")  # e.g. {"front":"M1","back":"M3"}
    _require(regimes["curve"], "contango_threshold")
    _require(regimes["curve"], "backwardation_threshold")

    scenarios = _require(cfg, "scenarios")
    _require(scenarios, "historical")
    _require(scenarios["historical"], "window")
    _require(scenarios, "bootstrap")
    _require(scenarios["bootstrap"], "block_size")
    _require(scenarios["bootstrap"], "n_paths")

    hedging = _require(cfg, "hedging")
    _require(hedging, "ols")
    _require(hedging, "rolling")
    _require(hedging["rolling"], "lookback")
    _require(hedging["rolling"], "min_obs")

    metrics = _require(cfg, "metrics")
    _require(metrics, "cvar_alpha")
