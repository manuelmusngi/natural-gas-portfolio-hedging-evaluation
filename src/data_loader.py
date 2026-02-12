from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


class DataError(ValueError):
    """Raised when input data is missing required fields or cannot be aligned."""


def load_ngas_data(raw_dir: str | Path, config: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame | None]:
    """
    Load spot, futures curve, and optional cross-assets data.

    Expected input formats
    ----------------------
    spot CSV:
        columns: date, spot

    futures curve CSV:
        columns: date, tenor, price
        tenor values should include those in config['curve']['tenors']

    cross assets CSV (optional):
        columns: date, <asset1>, <asset2>, ...

    Returns
    -------
    spot_df:
        index: DatetimeIndex, column: spot
    futs_wide_df:
        index: DatetimeIndex, columns: fut_<TENOR> (prices)
    xasset_df:
        index: DatetimeIndex, columns: asset prices (as provided), or None
    """
    raw_dir = Path(raw_dir)
    spot_path = raw_dir / config["data"]["spot_file"]
    futs_path = raw_dir / config["data"]["futures_file"]
    xasset_file = config["data"].get("cross_assets_file")

    spot_df = _load_spot(spot_path)
    futs_wide_df = _load_futures_curve_wide(futs_path, tenors=config["curve"]["tenors"])

    xasset_df = None
    if xasset_file:
        xasset_path = raw_dir / xasset_file
        if xasset_path.exists():
            xasset_df = _load_cross_assets(xasset_path)

    return spot_df, futs_wide_df, xasset_df


def _load_spot(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Spot file not found: {path}")

    df = pd.read_csv(path)
    _require_cols(df, ["date", "spot"], f"spot file {path.name}")

    df["date"] = pd.to_datetime(df["date"], utc=False)
    df = df.sort_values("date").set_index("date")

    df = df[["spot"]].astype(float)
    return df


def _load_futures_curve_wide(path: Path, tenors: list[str]) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Futures curve file not found: {path}")

    df = pd.read_csv(path)
    _require_cols(df, ["date", "tenor", "price"], f"futures curve file {path.name}")

    df["date"] = pd.to_datetime(df["date"], utc=False)
    df["tenor"] = df["tenor"].astype(str)
    df["price"] = df["price"].astype(float)

    missing = sorted(set(tenors) - set(df["tenor"].unique()))
    if missing:
        raise DataError(
            "Futures curve file is missing required tenors from config.curve.tenors. "
            f"Missing: {missing}. Found: {sorted(df['tenor'].unique().tolist())[:20]}..."
        )

    wide = (
        df.pivot_table(index="date", columns="tenor", values="price", aggfunc="last")
          .sort_index()
    )

    # keep only configured tenors, and rename
    wide = wide[tenors].rename(columns={t: f"fut_{t}" for t in tenors})
    return wide


def _load_cross_assets(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    _require_cols(df, ["date"], f"cross assets file {path.name}")
    df["date"] = pd.to_datetime(df["date"], utc=False)
    df = df.sort_values("date").set_index("date")

    # everything except date is treated as a numeric asset price series
    cols = [c for c in df.columns if c != "date"]
    if not cols:
        raise DataError(f"Cross assets file {path.name} has no asset columns beyond 'date'.")
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    return df[cols]


def _require_cols(df: pd.DataFrame, cols: list[str], label: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise DataError(f"Missing required columns in {label}: {missing}")
