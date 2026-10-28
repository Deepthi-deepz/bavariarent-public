"""Validated historical Bavaria rental analytics shared by UI and future modules."""
from pathlib import Path
import numpy as np
import pandas as pd

REQUIRED = {"regio1", "regio2", "baseRent", "livingSpace", "base_rent_per_sqm"}


def load_bavaria(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Bavaria CSV missing: {path}. Run Notebook 03 first.")
    df = pd.read_csv(path)
    missing = REQUIRED.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if df.empty or not df["regio1"].eq("Bayern").all():
        raise ValueError("Expected nonempty data containing only Bayern observations.")
    for field in ("baseRent", "livingSpace", "base_rent_per_sqm"):
        df[field] = pd.to_numeric(df[field], errors="coerce")
        if not np.isfinite(df[field]).all() or not df[field].gt(0).all():
            raise ValueError(f"Invalid or missing positive values in {field}")
    if not np.allclose(df["base_rent_per_sqm"], df["baseRent"] / df["livingSpace"], rtol=1e-4, atol=1e-4):
        raise ValueError("base_rent_per_sqm differs from baseRent / livingSpace")
    return df


def regional_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (df.dropna(subset=["regio2"])
            .groupby("regio2", as_index=False)
            .agg(listings=("baseRent", "size"),
                 median_cold_rent=("baseRent", "median"),
                 median_cold_rent_sqm=("base_rent_per_sqm", "median"))
            .sort_values("median_cold_rent_sqm", ascending=False))


def size_summary(df: pd.DataFrame) -> pd.DataFrame:
    bands = pd.cut(df["livingSpace"], [0, 30, 50, 70, 90, 120, np.inf],
                   labels=["≤30", "30–50", "50–70", "70–90", "90–120", ">120"],
                   include_lowest=True)
    return (df.assign(size_band=bands)
            .groupby("size_band", observed=True)
            .agg(listings=("baseRent", "size"), median_sqm=("base_rent_per_sqm", "median"))
            .reset_index())


def observation_summary(df: pd.DataFrame) -> pd.DataFrame:
    if "date" not in df.columns:
        return pd.DataFrame(columns=["period", "listings", "median_sqm"])
    dates = pd.to_datetime(df["date"], errors="coerce")
    valid = df.loc[dates.notna()].copy()
    valid["period"] = dates.loc[dates.notna()].dt.to_period("M").astype(str).to_numpy()
    return (valid.groupby("period", as_index=False)
            .agg(listings=("baseRent", "size"), median_sqm=("base_rent_per_sqm", "median"))
            .sort_values("period"))
