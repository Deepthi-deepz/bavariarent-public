"""BavariaRent: transparent historical rental-market dashboard for Bavaria."""
from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bavariarent.analytics import (  # noqa: E402
    load_bavaria,
    observation_summary,
    regional_summary,
    size_summary,
)

DATA_PATH = ROOT / "data" / "processed" / "immo_data_bavaria.csv"
DEMO_PATH = ROOT / "data" / "sample" / "synthetic_bavaria_demo.csv"

st.set_page_config(page_title="BavariaRent | Historical Market", page_icon="🏠", layout="wide")
st.title("🏠 BavariaRent")
st.subheader("Historical rental market intelligence | Bavaria")



@st.cache_data(show_spinner="Loading Bavaria rental data…")
def read_data(path: str, modified_at_ns: int) -> pd.DataFrame:
    """Cache the validated CSV, invalidating when its modification timestamp changes."""
    return load_bavaria(path)


with st.sidebar:
    mode = st.radio(
        "Data source",
        ["Synthetic demonstration", "Local historical CSV"],
        help="Demo values are entirely fictional. Local mode requires a separately obtained CSV.",
    )

demo_mode = mode == "Synthetic demonstration"
active_path = DEMO_PATH if demo_mode else DATA_PATH
if demo_mode:
    st.error(
        "DEMONSTRATION MODE — All records, prices, locations, dates and charts "
        "are synthetic examples. They do not describe the real Bavarian rental market."
    )
else:
    st.warning(
        "LOCAL HISTORICAL DATA — Advertised cold rents from an older listing sample, "
        "not current rental prices, official Mietspiegel figures or live listings. "
        "Check dataset permissions before sharing results."
    )

try:
    data = read_data(str(active_path), active_path.stat().st_mtime_ns)
except (FileNotFoundError, ValueError, pd.errors.ParserError, OSError) as exc:
    st.error(f"Cannot load selected data: {exc}")
    if demo_mode:
        st.info("Run: python scripts/create_demo_data.py")
    else:
        st.info("For local historical mode, place a permitted CSV at data/processed/immo_data_bavaria.csv.")
    st.stop()

regions = sorted(data["regio2"].dropna().astype(str).unique().tolist())

with st.sidebar:
    st.header("Explore the data")
    if st.button("Reset filters", width="stretch"):
        for key in ("regions", "area", "min_count", "ranking"):
            st.session_state.pop(key, None)
        st.rerun()
    selected = st.multiselect(
        "Geographic groups (regio2)", regions, key="regions",
        help="These source labels may mix administrative levels and need verification.",
    )
    min_area, max_area = float(data["livingSpace"].min()), float(data["livingSpace"].max())
    if min_area < max_area:
        area = st.slider(
            "Living area (m²)", min_value=min_area, max_value=max_area,
            value=(min_area, max_area), key="area",
        )
    else:
        area = (min_area, max_area)
        st.caption(f"All records have {min_area:g} m² living area.")
    min_region_n = st.number_input(
        "Minimum records per geographic group", min_value=1, max_value=10000,
        value=100, step=25, key="min_count",
    )
    ranking = st.radio("Regional ranking", ["Highest rent", "Lowest rent"], key="ranking")
    st.caption("A minimum count is a descriptive threshold, not proof of representativeness.")

filtered = data.loc[data["livingSpace"].between(*area)].copy()
if selected:
    filtered = filtered.loc[filtered["regio2"].astype(str).isin(selected)]
if filtered.empty:
    st.warning("No observations match these filters. Widen the living-area range or region selection.")
    st.stop()

st.caption(f"Displaying {len(filtered):,} of {len(data):,} {'synthetic demo' if demo_mode else 'historical'} records. All metrics are recalculated after filtering.")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Observations", f"{len(filtered):,}")
c2.metric("Median cold rent", f"€{filtered['baseRent'].median():,.0f}")
c3.metric("Median cold rent / m²", f"€{filtered['base_rent_per_sqm'].median():,.2f}")
c4.metric("Median living area", f"{filtered['livingSpace'].median():,.0f} m²")

st.divider()
st.header("Cold rent per m² distribution")
view = st.radio("Chart range", ["Full range", "1st–99th percentile (chart only)"], horizontal=True)
chart_df = filtered.dropna(subset=["base_rent_per_sqm"])
if view.startswith("1st") and not chart_df.empty:
    low, high = chart_df["base_rent_per_sqm"].quantile([0.01, 0.99])
    chart_df = chart_df.loc[chart_df["base_rent_per_sqm"].between(low, high)]
if not chart_df.empty:
    fig = px.histogram(
        chart_df, x="base_rent_per_sqm", nbins=65,
        labels={"base_rent_per_sqm": "Advertised cold rent (€/m²)"},
        title="Historical distribution of advertised cold rent per m²",
    )
    fig.update_layout(yaxis_title="Observations")
    st.plotly_chart(fig, width="stretch")
    st.caption(f"Chart uses {len(chart_df):,} observations; summary metrics use all {len(filtered):,} filtered records.")
else:
    st.info("No valid rent-per-m² observations are available for this chart.")

st.header("Compare geographic groups")
regional = regional_summary(filtered)
eligible = regional.loc[
    (regional["listings"] >= min_region_n) & regional["median_cold_rent_sqm"].notna()
]
if eligible.empty:
    st.info("No geographic groups meet the selected sample-size threshold. Try lowering it.")
else:
    # The analytics function sorts descending, but explicitly sort again for both ranking modes.
    top = eligible.sort_values(
        "median_cold_rent_sqm", ascending=(ranking == "Lowest rent")
    ).head(15).sort_values("median_cold_rent_sqm")
    fig = px.bar(
        top, x="median_cold_rent_sqm", y="regio2", orientation="h",
        hover_data=["listings", "median_cold_rent"],
        labels={"regio2": "Source geographic group", "median_cold_rent_sqm": "Median cold rent (€/m²)"},
        title=f"{ranking} groups with at least {min_region_n:,} observations",
    )
    st.plotly_chart(fig, width="stretch")
    st.caption("Geographic labels are sourced from regio2 and may not all refer to equivalent administrative units.")
st.dataframe(regional, width="stretch", hide_index=True)
st.download_button(
    "Download regional summary (synthetic CSV)" if demo_mode else "Download regional summary (CSV)",
    data=regional.to_csv(index=False).encode("utf-8-sig"),
    file_name="bavaria_regional_SYNTHETIC_DEMO.csv" if demo_mode else "bavaria_regional_historical.csv", mime="text/csv",
)

st.header("Apartment-size comparison")
size = size_summary(filtered)
if not size.empty:
    fig = px.bar(
        size, x="size_band", y="median_sqm", text="listings",
        hover_data=["listings"],
        labels={"size_band": "Living area (m²)", "median_sqm": "Median cold rent (€/m²)"},
        title="Historical median cold rent per m² by living-area band",
    )
    st.plotly_chart(fig, width="stretch")
    st.caption("Numbers above bars are observation counts, not available listings.")
else:
    st.info("No apartment-size groups are available.")

st.header("Historical observations")
period = observation_summary(filtered)
if not period.empty:
    fig = px.bar(
        period, x="period", y="median_sqm", text="listings",
        hover_data=["listings"],
        labels={"period": "Observed year–month", "median_sqm": "Median cold rent (€/m²)"},
        title="Observed months only — not a continuous trend",
    )
    fig.update_xaxes(type="category")
    st.plotly_chart(fig, width="stretch")
    st.caption("Observation months are sparse; changes may reflect differences in listing composition rather than rent growth.")
else:
    st.info("No valid observation dates are available for this selection.")

with st.expander("Methodology, sources and limitations"):
    st.markdown(
        "**Price definition:** Kaltmiete is advertised monthly cold rent, excluding charges. "
        "It is not Warmmiete, Bestandsmiete, a legal rent assessment, or a live listing.\n\n"
        "**Metric:** Each record's cold rent per m² is `baseRent / livingSpace`; "
        "the displayed median is the median of those record-level ratios.\n\n"
        "**Coverage:** Historical listing samples may be non-representative. "
        "The source `regio2` labels require geographic harmonization. "
        "Filtering can create small or compositionally different subsamples. "
        "No current availability or legal compliance is asserted."
    )

if demo_mode:
    st.caption("DEMO DATA ONLY — Generated deterministically by scripts/create_demo_data.py; never use for market conclusions.")
