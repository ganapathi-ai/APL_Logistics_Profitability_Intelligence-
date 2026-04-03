# APL Logistics — Profitability Intelligence Dashboard

**From Revenue to Profitability: A Data-Driven Framework for Customer, Product, and Margin Performance Analysis in Global Logistics Operations**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Dataset: Git LFS](https://img.shields.io/badge/Dataset-Git%20LFS-F05032?logo=git&logoColor=white)](https://git-lfs.github.com/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-5.18+-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/)

---

## Overview

This repository contains the full implementation of a profitability intelligence platform developed for APL Logistics (KWE Group). The system transforms raw transactional supply chain data — 180,519 order records spanning five global markets — into actionable margin insights across customers, products, and geographic regions.

The work addresses a critical gap in logistics analytics: revenue-centric reporting that obscures profitability signals. By engineering 43 derived features and applying a five-tier profitability classification framework, the platform enables data-driven decisions on discount policy, customer segmentation, and market strategy.

This repository accompanies the research paper listed in the [Citation](#citation) section below.

---

## Research Context

| Field | Detail |
|---|---|
| Title | From Revenue to Profitability: A Data-Driven Framework for Customer, Product, and Margin Performance Analysis in Global Logistics Operations |
| Journal | ..... |
| Volume / Issue | .... |
| Dataset Size | 180,519 transaction records |
| Engineered Features | 43 |
| Markets Covered | Pacific Asia, USCA, Europe, LATAM, Africa |
| Framework | Customer–Product–Market (CPM) Profitability Model |

---

## Key Findings

| Metric | Value |
|---|---|
| Total Revenue | $36.78 M |
| Total Profit | $4.58 M |
| Overall Net Margin | 12.45% |
| Loss-Making Orders | 18.7% (33,784 orders) |
| Late Delivery Rate | 57.28% |
| Average Discount Rate | 10.17% |
| Critical Discount Threshold | 10% (margin inflection point) |
| Highest-Margin Market | USCA — 12.72% |
| Highest-Margin Category | Fishing — 13.99% |

---

## Repository Structure

```
APL_Logistics_Profitability_Intelligence/
│
├── app.py                            # Streamlit dashboard — 6 analytical modules
├── data_transformation.py            # Data pipeline — cleaning + 43 feature derivations
├── requirements.txt                  # Python dependencies (pinned versions)
├── LICENSE                           # MIT License
│
├── APL_Logistics_Transformed.csv     # Processed analytical dataset (stored via Git LFS)
├── APL_Logistics_Research_Paper.docx # Full research paper (manuscript)
│
└── README.md
```

---

## Dashboard Modules

The Streamlit application (`app.py`) provides six interactive analytical tabs:

| Module | Description |
|---|---|
| Revenue & Profit Overview | Portfolio-level KPIs, market revenue/profit comparison, profitability class distribution by segment and shipping mode |
| Customer Value Analysis | Top/bottom customer rankings by profit, value-tier segmentation (Premium → Loss Customer), segment contribution summary |
| Product & Category Intelligence | Product margin rankings, category profitability heatmap by customer segment, revenue treemap coloured by margin |
| Discount Impact Analyzer | Discount-band margin degradation, discount rate vs. profit ratio scatter, what-if discount simulator, margin erosion heatmap |
| Market & Regional Intelligence | Market-level revenue/margin comparison, regional profit margin bar chart, region revenue treemap |
| Shipping Performance Analytics | Late delivery rates by mode, delivery status distribution, delay distributions, profit before/after shipping cost |

---

## Data Transformation Pipeline

`data_transformation.py` executes a six-stage pipeline:

1. **Data Loading** — Reads raw CSV (`APL_Logistics.csv`) with latin-1 encoding
2. **Column Standardisation** — Renames all fields to snake_case
3. **Data Cleaning** — Missing value imputation, string normalisation, removal of zero-sales records, profit outlier capping at ±3 standard deviations
4. **Feature Engineering** — 43 derived features across six categories:
   - Core financial metrics: gross margin %, effective unit price, unit profit, revenue after discount
   - Shipping performance: delay days, late delivery flag, shipping efficiency ratio
   - Discount impact: erosion flag, net margin after discount, discount band classification
   - Profitability classification: five-tier label (Loss-Making / Break-Even / Low-Margin / Moderate-Margin / High-Margin)
   - Aggregated profiles: customer-level, product-level, market-level, and category-level summary statistics
   - Risk scoring: composite margin erosion risk score (0–100)
5. **PII Removal** — Drops street address, coordinates, and raw name fields
6. **Export** — Writes `APL_Logistics_Transformed.csv`

---

## Setup and Installation

### Prerequisites

- Python 3.10 or higher
- pip
- Git with Git LFS ([install Git LFS](https://git-lfs.github.com/))

### Clone and Install

```bash
git lfs install
git clone https://github.com/ganapathi-ai/APL_Logistics_Profitability_Intelligence-.git
cd APL_Logistics_Profitability_Intelligence-
pip install -r requirements.txt
```

> Git LFS is required to download `APL_Logistics_Transformed.csv` (≈100 MB). Without it, the file will appear as a text pointer.

### Run the Dashboard

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

### Regenerate the Dataset (Optional)

If you have the raw source file `APL_Logistics.csv`:

```bash
python data_transformation.py
```

---

## Deployment on Streamlit Cloud

1. Fork this repository to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in
3. Click **New app** → select your fork → set main file to `app.py`
4. Click **Deploy**

Streamlit Cloud installs dependencies from `requirements.txt` automatically. Ensure Git LFS is enabled on your fork so the CSV is accessible.

---

## Dependencies

```
streamlit>=1.32.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
```

---

## Dataset

The transformed dataset (`APL_Logistics_Transformed.csv`) is stored in this repository using **Git Large File Storage (Git LFS)** due to its size (≈100 MB). It is a standard comma-separated values file with 180,519 rows and 73 columns.

To verify the file downloaded correctly (not as an LFS pointer):

```bash
head -n 2 APL_Logistics_Transformed.csv
```

The first line should be a comma-separated header row beginning with `payment_type,shipping_days_actual,...`

---

## Citation

If you use this codebase, dataset, or dashboard in academic work, please cite:

```bibtex
@article{apllogistics2024profitability,
  title     = {From Revenue to Profitability: A Data-Driven Framework for Customer,
               Product, and Margin Performance Analysis in Global Logistics Operations},
  journal   = {...},
  volume    = {..},
  number    = {..},
  year      = {2026},
  publisher = {..},
  url       = {https://github.com/ganapathi-ai/APL_Logistics_Profitability_Intelligence-}
}
```

---

## License

This project is released under the **MIT License**. See [LICENSE](LICENSE) for the full terms.

The dataset (`APL_Logistics_Transformed.csv`) is derived from supply chain transaction data and is provided for research and educational purposes only.

---

## Contact

Ganapathi Kakarla| Independent Researcher | April 2026
Repository: [github.com/ganapathi-ai/APL_Logistics_Profitability_Intelligence-](https://github.com/ganapathi-ai/APL_Logistics_Profitability_Intelligence-)

---

*APL Logistics Profitability Intelligence Platform — © 2024 KWE Group. Released under the MIT License.*
