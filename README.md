# BavariaRent

**Historical Rental Market Intelligence for Bavaria, Germany**

BavariaRent is a Python and Streamlit application for exploring historical advertised rental prices across Bavaria.

## Current Features

- Interactive geographic and apartment-size filters
- Historical cold-rent statistics
- Rental-price distributions
- Regional comparisons
- Interactive Plotly visualizations
- CSV downloads of aggregated regional statistics
- Automated validation tests

## Technology

Python, Pandas, NumPy, Plotly, Streamlit, and Pytest.

## Data Requirements

The application currently expects:

`data/processed/immo_data_bavaria.csv`

The original historical rental dataset was obtained from Kaggle and is labeled **Data files © Original Authors**.

The dataset is not distributed with this public repository because redistribution permissions have not been established.

The application cannot display its rental statistics without a compatible dataset.

## Run Locally

Create and activate a Python virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start the application:

```powershell
python -m streamlit run app/Home.py
```

## Tests

Install Pytest:

```powershell
python -m pip install pytest
```

Run:

```powershell
python -m pytest tests/ -v
```

## Limitations

The original analysis covers historical advertised listings from 2018–2020. It does not represent current rental prices, verified available properties, official Mietspiegel benchmarks, or legal rental assessments.

## Development Status

The historical market intelligence dashboard is implemented locally.

A publicly deployed dashboard with appropriately licensed data, rental-price predictions, accommodation discovery, and personalized recommendations remain future work.

## License

The application code's license will be selected separately from the rental dataset's licensing conditions.

## Live Demonstration

Explore the BavariaRent dashboard:

https://bavariarent-public-exrqhcqdemjr6bngnwovjz.streamlit.app/

The public application uses synthetic demonstration
data. Its prices and statistics are fictional and
must not be interpreted as real Bavarian rental
market measurements.