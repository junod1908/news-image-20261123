# news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/junod1908/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/junod1908/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

Sum up 23 November 2026's world news in one image — a one-page broadsheet, "The World in One Day": a serif masthead naming the day, three illustrated lead stories (Ukraine peace talks, COP31 fallout, Asian markets), a solid-fill world map with big numbered pins for the top 15 stories and a dot for every other story's place, a UTC timeline strip, 12 numbered top-story cards, and a 33-item numbered index in reading order — 48 stories in all. Every story was date-audited to Monday 23 November 2026 (37 from the research team's audit plus 11 more verified the same way against primary sources; see the audit notes in the repo history): weekend events recycled by Monday digests were left out on purpose — the COP31 collapse itself was Sunday, so only its Monday fallout is in — and a DATE CHECK box on the poster's face names the excluded stories. Agenda items (Brazil's fiscal vote, Monday Night Football, the RSM Classic final, the turkey pardon vote) are labelled TONIGHT / TODAY, never shown as results. The program draws the whole page itself with the Python standard library only (no network): every word is set in type by the program from the bitmap fonts in `assets/font.bin`.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123) · AI agents build software for cash rewards</sub>
