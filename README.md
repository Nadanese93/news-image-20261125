# The World — 25 November 2026

[![bounty](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/Nadanese93/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/Nadanese93/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A newspaper front page that sums up the world news of **Wednesday, 25 November 2026** in one image. The program draws the whole 1024×1024 page with Python 3.13 standard library only — its own PNG encoder, its own 5×7 bitmap font, and all artwork drawn programmatically with shapes. No network, no external fonts or images, fully deterministic (two runs write byte-identical files).

## The stories

1. **Four tankers hit mines in Hormuz** — Iran says a fourth oil tanker exploded and caught fire after striking a naval mine in the Strait of Hormuz, the fourth in two days, despite a US military escort. Sources: IRGC Navy via IRNA/Tasnim, Reuters, UKMTO (which has not verified the mine claims).
2. **Ukraine sank a warship off Libya** — Zelenskiy confirms Ukraine struck two Russian vessels off the Libyan coast, sinking one warship in Benghazi harbour; Kyiv's strikes now reach beyond Europe. Source: Reuters.
3. **Baghdad seizes Kurd oilfields** — Iraq's prime minister orders the federal oil ministry to take over oilfields and all border crossings in Kurdish-controlled areas; the Kurdistan government calls it unacceptable. Sources: INA, Financial Times.
4. **Senegal win AFCON back** — the Court of Arbitration for Sport reinstates Senegal as 2025 Africa Cup of Nations champions, setting aside the CAF decision that gave the title to Morocco; Morocco vows to appeal. Source: Reuters.
5. **Car bomb wounds 23 in Colombia** — a bomb outside regional government offices in Villavicencio injures 23 on the eve of the 10th anniversary of the FARC peace deal; the president blames FARC dissidents. Source: AP.
6. **Sarkozy and Bruni face trial** — French officials order former president Nicolas Sarkozy and his wife Carla Bruni to stand trial in the Libya corruption case; a pre-trial hearing is set for 1 April 2027. Source: Reuters.

Note on dates: the contest opened at 00:00 UTC on 25 November and this entry was built at about 01:30 UTC, when the 25 November UTC day had barely begun. The six stories above are the freshest of the 25 November news cycle, first reported late on 24 November or overnight into 25 November across time zones.

## How to run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024×1024 PNG, under 1 MiB). Run it twice and the files are byte-identical.
