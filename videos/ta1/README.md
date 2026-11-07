# Technical Analysis of the Financial Markets: Part 1 video pipeline

Animated summary of John J. Murphy's book, chapters 1 to 8 (about 64 minutes).
Everything is generated in code: narration (Kokoro TTS), animation (cairocffi), music (numpy).

## Files
- `script_p1.py`: narration in our own words, with `{n}` beat markers that sync visuals to speech
- `speech.py`: turns numbers, years, money and acronyms into words for the voice
- `tts.py`: Kokoro voice `am_michael`, speed 0.97, one chunk per beat, measures real durations
- `timeline.py`: scene and beat timing built from the measured audio
- `engine.py`: paper style, typography, chapter title card, header, key-idea banner, avatars, icons, chart tools
- `scenes/`: one custom animated diagram per lesson (`s_open.py`, `s_c1.py` ... `s_c8.py`)
- `render.py`: previews (`preview`) and parallel per-scene MP4 rendering (`video`)
- `music.py`: original lo-fi bed (FM e-piano, bass, soft kick, swung hats)
- `audio.py`: voice + music at -11 dB, loudness to -15 LUFS with a peak limiter, captions, chapters
- `tools/`: TradingView export, contact sheets, thumbnail, YouTube upload info

## Rebuild
```
python tools/grab_ohlcv.py data            # after fetching OHLCV with the TradingView connector
python tts.py BUILD MODELS
python music.py BUILD/music.wav SECONDS
python render.py BUILD preview --t=end      # check every final frame
python render.py BUILD video --workers=3
python audio.py BUILD deliverables
```
Market data: TradingView (NSE:NIFTY, BITSTAMP:BTCUSD). Educational content, not financial advice.
Unofficial summary written in our own words, not affiliated with the author or publisher.
