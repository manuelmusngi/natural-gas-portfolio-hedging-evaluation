#### 🌐 Natural Gas Portfolio Hedging Evaluation

Scenario‑Based Analytics Across a Forward‑Curve‑Spanning Natural Gas Portfolio

This project delivers a complete, research‑grounded framework for evaluating hedge effectiveness in a forward‑curve‑spanning natural gas portfolio. It integrates quantitative finance, energy market structure, and risk analytics into a modular workflow suitable for both exploratory research and production‑grade modeling.

The notebook implements a forward‑curve‑spanning, regime‑aware hedging engine that supports static and dynamic hedge ratios, scenario‑based stress testing, and tail‑risk evaluation using VaR/CVaR. It is designed for quantitative researchers, energy analysts, and risk teams who require transparent, reproducible analytics for hedging decisions.

#### 📁 Project Alignment

#### 00. Overview & Assumptions
#### 🧭 High‑level description of the modeling framework, assumptions, and intended use cases.

#### 01. Configuration
#### ⚙️ Centralized configuration for calendar settings, tenor universe, scenario parameters, and risk metrics.

#### 02. Data Layer
#### 🗄️ Adapters for CSV/database ingestion plus a synthetic curve generator with regime‑dependent volatility.

#### 03. Curve & Alignment
#### 📈 Forward curve construction, normalization, return computation, and hooks for roll logic.

#### 04. Portfolio Specification
#### 📊 Forward curve level exposures (DV01‑like sensitivities) and portfolio return construction.

#### 05. Hedge Instruments
#### 🔧 Futures, strips, and spread hedges represented as linear exposure vectors across the curve.

#### 06. Regime Detection
#### 🌗 Proxy high/low volatility regimes with extensibility to HMM, MS‑GARCH, or fundamentals‑based regimes.

#### 07. Scenario Engine
#### 🎲 Historical block bootstrap, regime‑conditioned sampling, and deterministic stress shocks.

#### 08. Hedge Optimization
#### 🧮 Static OLS, rolling OLS, EWMA covariance hedging, and hooks for DCC‑GARCH extensions.

#### 09. Backtest & Evaluation
#### 📉 Variance reduction, VaR/CVaR improvements, drawdown metrics, and hedged vs. unhedged performance.

#### 10. Reporting
#### 📑 Summary tables, time‑series plots, scenario distributions, and hedge‑weight stability charts.

#### License
This project is licensed under the [MIT License](https://github.com/manuelmusngi/regime_switching_models/edit/main/LICENSE).

