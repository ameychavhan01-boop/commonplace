# Market Wizards — Style Sample 01
## "The Arithmetic of Survival" (opening + concept lesson)

**Purpose:** a style test to set the series look before production. It contains no trader research.
Every figure is a hypothetical example calculated in `render.py`.

**Runtime:** 2:01  ·  **Format:** 1920×1080, 30 fps, H.264 + AAC
**Narration pace:** about 140–150 words per minute (the subtitle timings assume this)

---

| Time | Visual | Narration (voice-over) |
|---|---|---|
| 0:00–0:02 | **JSR sting.** Black screen. The round JSR logo rises from below with a soft gold glow, holds for a moment, then lifts away and disappears. A low "hit" sound plays. | — |
| 0:02–0:13 | **Cold open.** Charcoal with a vignette. A faint gold price line traces across a dim grid. | Every trader in this series has lost money. Some lost fortunes. / What set them apart was not avoiding losses. It was surviving them. |
| 0:13–0:19 | **Series title.** MARKET WIZARDS in light, widely spaced letters. A gold rule draws out from the centre. Tagline: *The Traders · The Methods · The Lessons* | — |
| 0:19–0:24 | **Chapter card.** Gold vertical bar. CHAPTER ONE / *The Arithmetic of Survival* / *Why risk per trade decides who is still trading tomorrow* | — |
| 0:25–0:55 | **One losing streak, two outcomes.** An equity chart from $100k down to $0, with two trader cards. The lines draw trade by trade and the counters step to exact balances. End values: A **$34,868**, B **$90,438**. A bracket shows the **$55,570** difference. | Imagine two hypothetical traders, each starting with one hundred thousand dollars. / Trader A risks ten percent of the account per trade. Trader B risks one percent. / Now give them both the same bad luck: ten losing trades in a row. / Trader A is left with about thirty-five thousand dollars. Trader B still has about ninety. / Same market. Same losing streak. The only difference was how much they risked. |
| 0:56–1:21 | **The gain required to break even.** Paired bars, grey for the loss and gold for the gain needed: −10% → +11.1%, −25% → +33.3%, −50% → +100%, −65.1% → +186.8% (Trader A). | And losses are harder to recover from than they look. / A ten percent loss needs an eleven percent gain to recover. A twenty-five percent loss needs thirty-three. / Lose half, and you must double what remains just to break even. / Trader A lost sixty-five percent. Recovering requires a gain of nearly one hundred and ninety percent. |
| 1:21–1:52 | **Sizing a position from risk.** Synthetic daily candles: an uptrend, a base above $48.30, then a breakout to $50. The entry line ($50) and dashed stop line ($48) mark a shaded risk zone. A numbered calculation panel fills in step by step: account → 1% risk → $2.00 risk per share → **500 shares** → maximum planned loss. A caveat about gaps and slippage appears. | That is why position size is often set by risk, not by conviction. / First, choose the most you will lose on one trade: one percent, or one thousand dollars. / You buy at fifty dollars, with a stop at forty-eight. Each share risks two dollars. / One thousand dollars, divided by two dollars per share: five hundred shares. / If the stop is hit, the loss is planned, though gaps and slippage can make it larger. |
| 1:52–2:01 | **Outro and end card.** The gold line returns, then the MARKET WIZARDS end card: *Episode One · Coming soon*. A disclaimer runs along the bottom. | Every trader in this series found their own answer to this problem. |

---

### Calculation check (hypothetical)
- Trader A: 100,000 × 0.90¹⁰ = **34,867.84**
- Trader B: 100,000 × 0.99¹⁰ = **90,438.21**
- Difference: **55,570**
- Gain needed to recover a loss L = L ÷ (1 − L): 10% → 11.1%; 25% → 33.3%; 50% → 100%; 65.13% → 186.8%
- Position size = $1,000 risk ÷ ($50 − $48) = **500 shares**

### Placeholders in this sample
- **Logo:** a placeholder round "JSR" monogram. Put the real logo at `assets/jsr_logo.png` and re-render.
- **Music:** an original ambient pad synthesized in code. It's a temporary bed, not the final score.
- **Voice:** subtitles only. A recorded narration would replace or accompany them.
