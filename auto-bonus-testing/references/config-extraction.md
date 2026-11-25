# Phase 1 – Extracting the expected values from Betler

Goal: one "expected sheet" before touching the front end, so the browser steps are pure comparison.

## Which MCP
Always `betler-production-mcp` (load via ToolSearch). The skill is production-only, so never use the stage, dev or QA MCPs.

## What to pull
| Need | Source | Notes |
|---|---|---|
| Bonus definition (type, provider, games, spins, stake, expiry, names, offer details, T&C, CTA, popup flag, wagering) | `bonus_definitions` topic/index | Try `lookup(topic="bonus_definitions", kafka_key=<bonus_id>)`; if empty, `opensearch_search` on the index. Use `latest` / the running revision only – never an older draft. |
| Awarded instance for the test account | `bondet_state` | `opensearch_search`, index `bondet_state`, term `customer_id.keyword` (+ bonus/template id). Gives status, awarded_at, expiry, `campaign_template` (manual vs campaign). |
| FS usage | `fsinfo_state` / `fsinfo_updates` | `used` / `remaining` counters |
| Spin-level truth | `gaming_ticker` | includes `status: rejected` rounds that may carry a calculated win. Query the day index `gaming_ticker-YYYY.MM.DD` with `bool.must` [term `customer_id.keyword`, range on `kafire_timestamp`]; a range on `timestamp` returns 0 hits (2026-11-19) |

Index/field names can differ per environment — if a term query returns suspiciously nothing, check `opensearch_mappings` (ID fields are `text` with a `.keyword` subfield) and widen the date window (daily rollovers happen ~21:00 UTC). Keyed `messages` / `check_topic_message` calls have silently returned `count: 0` before; don't treat their empties as fact.

If the definition's name fields are PII-redacted by the MCP, fall back to `PROD.DWH` Snowflake tables if authenticated, otherwise report public names as "not retrievable – verify manually against the Betler UI".

## Expected sheet (fill every row; write "n/a" when it truly doesn't apply)
```
Bonus id / instance id:
Type: Free Spins (Fixed | Dynamic) | other
Provider:           Game(s):
Number of spins:    Stake per spin (currency):   Total value:
Expiry (days/h/min) → expected expiry timestamp:
Public bonus name (per language):
Promo public name:
Offer details text:
T&C link / text:
CTA text:           CTA deeplink:
Popup displayed (flag):
Wagering / redeem / max-win rules:
Instance status at start:  awarded_at:
```
Dynamic FS (percentage of deposit, capped) → compute the expected spins from the configured percentages and the triggering deposit; if you can't, mark spins "dynamic – verify consistency between popup, in-game counter and `bondet_state`" rather than inventing a number.
