#### 🌐 Natural Gas Portfolio Hedging Evaluation

A research‑grade analytics framework for evaluating hedge effectiveness in natural gas portfolios using scenario‑based analysis, multi‑tenor futures, and market regime awareness.
The project is designed to bridge academic hedging theory and production‑ready risk analytics, enabling robust assessment of hedging strategies across volatility regimes, curve structures, and stress scenarios.

#### 🔍 Project Overview
This repository delivers an end‑to‑end Python workflow for quantifying how well futures‑based hedges mitigate risk in natural gas portfolios.
The framework emphasizes time‑varying hedge ratios, regime‑conditional performance, and tail‑risk protection, reflecting the unique volatility and seasonality of natural gas markets.

#### ✨ Highlights
#### 🧠 Scenario‑Based Hedging Analytics
- Historical, bootstrapped, and user‑defined stress scenarios
- Explicit evaluation of hedge performance during extreme market events
- Replay of regime‑specific shocks (e.g., high‑volatility or backwardation periods)

#### 📈 Multi‑Tenor Hedge Evaluation
- Simultaneous analysis of front‑month, seasonal, and calendar futures
- Tenor‑specific hedge ratios and portfolio‑level combinations
- Insight into maturity‑dependent hedge effectiveness

#### 🔄 Market Regime Awareness
- Volatility regimes derived from GARCH‑based estimates
- Curve regimes based on contango/backwardation dynamics
- Regime‑conditional hedge effectiveness metrics

#### ⚙️ Time‑Varying Hedge Ratios
- Static OLS hedge ratios for benchmarking
- Dynamic DCC‑GARCH hedge ratios aligned with academic best practices
- Direct comparison of static vs adaptive hedging strategies

#### 📉 Risk‑Focused Performance Metrics
- Variance reduction and classical hedge effectiveness
- Tail‑risk metrics including CVaR and drawdowns
- Distributional analysis of hedged vs unhedged P&L

#### 🧠 Key Takeaways
- Hedge effectiveness in natural gas is highly regime‑dependent, with materially different outcomes in high‑volatility and stressed markets.
- Dynamic hedge ratios consistently outperform static approaches, particularly during volatility spikes and structural curve shifts.
- Tenor selection matters: front‑month hedges may reduce variance efficiently, while longer‑dated tenors can offer superior tail‑risk protection.
- Scenario‑based evaluation reveals vulnerabilities that are invisible under unconditional, full‑sample metrics.
- A modular, research‑aligned architecture enables transparent validation, extension, and production deployment.

#### 🧩 Project Architecture

ngas-portfolio-hedging/\
├─ data/\
│  ├─ raw/\
│  │  ├─ ngas_spot.csv\
│  │  ├─ ngas_futures_curve.csv\
│  │  └─ cross_assets.csv          # optional: crude, power, etc.\
│  └─ processed/\
│     └─ ngas_merged.parquet\
├─ config/\
│  └─ [config.yaml](https://github.com/manuelmusngi/natural-gas-portfolio-hedging-evaluation/blob/main/config/config.yaml)      # tenors, regimes, scenario settings\
├─ src/\
│  ├─ __init__.py\
│  ├─ config_loader.py\
│  ├─ data_loader.py\
│  ├─ features.py                   # returns, curve slopes, spreads\
│  ├─ regimes.py                    # volatility & curve-shape regimes\
│  ├─ hedging.py                    # hedge ratios, portfolio P&L\
│  ├─ scenarios.py                  # scenario generation & application\
│  ├─ metrics.py                    # variance, CVaR, HE, etc.\
│  └─ plotting.py                   # diagnostic and reporting charts\
├─ notebooks/\
│  └─ 01_ngas_portfolio_hedging_evaluation.ipynb\
├─ docs/\
│  └─ README.md\
└─ requirements.txt


#### License
This project is licensed under the [MIT License](https://github.com/manuelmusngi/regime_switching_models/edit/main/LICENSE).

