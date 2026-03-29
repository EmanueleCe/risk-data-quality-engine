### Completeness Overview

![Completeness Heatmap](images/completeness_heatmap.png)

# Risk Monitoring & Data Quality Engine

This project focuses on building a simple data quality monitoring framework using multi-asset market data. The idea is to replicate, in a simplified way, how data quality checks are typically handled.

The workflow starts from basic data preparation, where market data is cleaned and enriched with additional fields such as bid, ask, spread, and source. Once the dataset is structured, completeness checks are performed to assess data availability at asset level, taking into account where specific fields are expected.

Validation rules are then applied to ensure that the available data is consistent, for example checking that prices are positive and that bid/ask relationships make sense. In parallel, outliers are identified using log returns and simple statistical thresholds, highlighting unusually large movements that may require further attention.

In the final step, all these signals are combined into a single summary table. For each asset, the table reports the number of missing values, invalid observations, and outliers, providing a compact and practical view of data quality issues.

The project is not meant to be a quantitative model, but rather a practical example of how data quality can be monitored and summarized in a structured and business-oriented way.

*Note: the completeness values shown in the heatmap are based on a controlled dataset where data quality issues were intentionally introduced to simulate realistic scenarios.*