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
Simultaneous analysis of front‑month, seasonal, and calendar futures

Tenor‑specific hedge ratios and portfolio‑level combinations

Insight into maturity‑dependent hedge effectiveness

#### 🔄 Market Regime Awareness
Volatility regimes derived from GARCH‑based estimates

Curve regimes based on contango/backwardation dynamics

Regime‑conditional hedge effectiveness metrics

#### ⚙️ Time‑Varying Hedge Ratios
Static OLS hedge ratios for benchmarking

Dynamic DCC‑GARCH hedge ratios aligned with academic best practices

Direct comparison of static vs adaptive hedging strategies

#### 📉 Risk‑Focused Performance Metrics
Variance reduction and classical hedge effectiveness

Tail‑risk metrics including CVaR and drawdowns

Distributional analysis of hedged vs unhedged P&L

#### License
This project is licensed under the [MIT License](https://github.com/manuelmusngi/regime_switching_models/edit/main/LICENSE).

