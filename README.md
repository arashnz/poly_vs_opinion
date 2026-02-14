# Opinion vs Polymarket ARB monitor

This bot uses **exchange APIs only** (no web-page scraping):

- Opinion API: `GET {base_url}{orderbook_path}?topicId=...&outcomeId=...`
- Polymarket CLOB API: `GET https://clob.polymarket.com/book?token_id=...`

It checks both sides for arbitrage:
- if `Opinion best bid > Polymarket best ask` => BOOM
- if `Polymarket best bid > Opinion best ask` => BOOM

Alerts are sent to:
- Telegram
- local dashboard (`http://localhost:8080`)

## Setup

```bash
export TELEGRAM_BOT_TOKEN='8331830301:AAFUCwAEyQwVZsCdzelOSQ3008QQeVvg6Gw'
export TELEGRAM_CHAT_ID='6645079982'
export OPINION_API_KEY='...'
python app.py --config config.json
```

## Important config fields

- `pairs[].opinion.topic_id` (already set to `332`)
- `pairs[].opinion.outcome_id` (must be exact outcome in Opinion market)
- `pairs[].polymarket.token_id` (must be exact CLOB token id for that Polymarket outcome)

## Extending later (Predict.fun, more markets)

Add additional objects under `pairs`. The engine is pair-based and reuses the same arb + alert pipeline.

## WS vs REST

Polymarket config includes `ws_url` and `use_ws` for future live stream mode.
Current default is REST polling for reliability.
