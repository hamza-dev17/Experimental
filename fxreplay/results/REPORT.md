# FX Replay management simulation

Matched **55 / 55** closed trades. High-confidence exit-path matches: **48**. Global timestamp offset: **UTC-3**; monthly offsets were used trade-by-trade. Median exit-path mismatch: **0.096R**.

Public XAUUSD tick data is not the exact OANDA feed. Each path is anchored to the public quote at the FX Replay entry time, and low-confidence mismatches are flagged.

| Scenario | Total R | Expectancy | Profit factor | Max DD | Losses saved | Winners reduced |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 41.93 | 0.762 | 2.16 | 11.88 | 0 | 0 |
| BE@1.5R | 37.03 | 0.673 | 2.32 | 9.96 | 8 | 3 |
| Partial 20%@5R | 36.44 | 0.663 | 2.01 | 10.93 | 0 | 6 |
| Partial 20%@3R | 36.36 | 0.661 | 2.05 | 10.13 | 0 | 8 |
| Partial 25%@5R | 35.06 | 0.638 | 1.97 | 10.93 | 0 | 6 |
| Partial 25%@3R | 34.97 | 0.636 | 2.03 | 9.93 | 2 | 8 |
| Partial 20%@2R | 34.95 | 0.635 | 2.02 | 9.70 | 0 | 8 |
| Partial 25%@2R | 33.20 | 0.604 | 1.98 | 9.20 | 0 | 8 |
| BE@2R | 32.14 | 0.584 | 1.97 | 10.96 | 3 | 2 |
| BE@3R | 31.21 | 0.567 | 1.91 | 10.88 | 2 | 1 |
| BE@5R | 29.24 | 0.532 | 1.81 | 11.88 | 0 | 1 |
| Partial 50%@5R | 28.20 | 0.513 | 1.78 | 10.93 | 0 | 6 |
| Partial 50%@3R | 28.01 | 0.509 | 1.82 | 9.93 | 2 | 8 |
| Partial 20%@3R + BE | 27.79 | 0.505 | 1.81 | 9.93 | 2 | 8 |
| Partial 20%@2R + BE | 27.12 | 0.493 | 1.82 | 9.37 | 3 | 8 |

Tested BE at **0.5R, 1R, 1.5R, 2R, 3R and 5R**. Tested **20%, 25% and 50% partials at 2R, 3R and 5R**, both partial-only and partial-plus-BE. Full results are in `scenario_summary.csv`; trade-level paths are in `trade_path_analysis.csv`.
