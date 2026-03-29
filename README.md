# Risk Monitoring & Data Quality Engine

This project presents a simple data quality monitoring framework built on multi-asset market data. The objective is to show how core data quality checks can be structured in a practical and business-oriented way, with a focus on monitoring rather than pure modelling.

The workflow starts from data preparation, where market data is cleaned and enriched with additional fields such as bid, ask, spread, and source. It then moves to completeness checks, field-level validation rules, and outlier detection based on log returns. In the final step, these signals are brought together into a compact issues summary at asset level.

The validation and outlier analysis are performed on the main market dataset. The completeness heatmap shown below is based on a controlled dataset where data quality issues were intentionally introduced to better illustrate the behaviour of the checks.

## Completeness Overview

![Completeness Heatmap](images/completeness_heatmap.png)

This project is not intended as a quantitative pricing or forecasting model. It is a practical example of how data quality can be monitored, summarized, and presented in a structured way within a risk or market data environment.