# FX Replay management simulation

Matched **55 / 55** closed trades. High-confidence exit-path matches: **36**. Calibrated timestamp offset: **UTC-3**. Median exit-path mismatch: **0.159R**.

Public XAUUSD tick data is not the exact OANDA feed. Each path is anchored to the public quote at the FX Replay entry time, and low-confidence mismatches are flagged.

| Scenario | Total R | Expectancy | Profit factor | Max DD | Losses saved | Winners reduced |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 41.93 | 0.762 | 2.16 | 11.88 | 0 | 0 |
| Partial 20%@3R | 37.47 | 0.681 | 2.09 | 10.13 | 0 | 6 |
| Partial 20%@5R | 36.74 | 0.668 | 2.02 | 10.93 | 0 | 5 |
| Partial 25%@3R | 36.35 | 0.661 | 2.07 | 9.93 | 2 | 6 |
| BE@1.5R | 36.03 | 0.655 | 2.24 | 9.96 | 7 | 3 |
| Partial 20%@2R | 35.56 | 0.647 | 2.04 | 9.70 | 0 | 7 |
| Partial 25%@5R | 35.44 | 0.644 | 1.98 | 10.93 | 0 | 5 |
| Partial 25%@2R | 33.97 | 0.618 | 2.01 | 9.20 | 0 | 7 |
| BE@2R | 32.14 | 0.584 | 1.97 | 10.96 | 3 | 2 |
| BE@3R | 31.21 | 0.567 | 1.91 | 10.88 | 2 | 1 |
| Partial 50%@3R | 30.78 | 0.560 | 1.90 | 9.93 | 2 | 6 |
| BE@5R | 29.24 | 0.532 | 1.81 | 11.88 | 0 | 1 |
| Partial 50%@5R | 28.94 | 0.526 | 1.80 | 10.93 | 0 | 5 |
| Partial 20%@3R + BE | 28.89 | 0.525 | 1.85 | 9.93 | 2 | 6 |
| Partial 25%@3R + BE | 28.31 | 0.515 | 1.83 | 9.93 | 2 | 6 |

Tested BE at **0.5R, 1R, 1.5R, 2R, 3R and 5R**. Tested **20%, 25% and 50% partials at 2R, 3R and 5R**, both partial-only and partial-plus-BE. Full results are in `scenario_summary.csv`; trade-level paths are in `trade_path_analysis.csv`.
