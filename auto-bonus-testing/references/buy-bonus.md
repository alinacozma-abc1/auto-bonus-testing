# Buy Bonus (bonus type "Buy Bonus")

Read this **in addition to** the standard Display / Play / Settlement checks when the bonus definition's `type` is `Buy Bonus`. The player gets the game's bonus-buy feature for free: one (or `count`) buy(s) at a fixed stake (`value`), worth `value × feature.price_multiplier` (= `total_bonus_value`). The bought feature (usually a free-spins round) is played at that stake and the win goes to the real balance (`payout_to: cash`).

## Expected sheet additions
`value` (stake per spin in the bought round), `feature.id` (BUY_BONUS / other feature), `feature.price_multiplier`, `total_bonus_value` (= value × multiplier), `count` (number of buys), game(s), provider, `expiry_seconds`, `popup_displayed`. Awarded instance: `bondet_state` `_id` starts with `BB-`, `initial_amount` = count, `used`, `multiplier`, `value` (= total value), `state` new → complete, `total_won`.

## Scorecard rows (B-ids, shown under "3. Buy bonus" in the report)
| ID | Check | How |
|---|---|---|
| B1 | Card / panel show the bonus value = `total_bonus_value` (e.g. "Sumă disponibilă 4,000.00 RON") and the stake per spin from offer details | card + info panel vs config |
| B2 | On launch the game offers the free buy (provider popup / "free buy" banner) with the right value or stake; bet level is set to the configured stake | popup + bet display |
| B3 | Activating the buy costs nothing: real balance unchanged at activation; backend debit 0 with the `BB-…` free-spin id | header balance + gaming_ticker |
| B4 | The bought feature starts (free-spins round / respins) and every round in it is played at the configured stake | HUD + gaming_ticker stakes |
| B5 | Feature length matches the game's standard buy (e.g. number of free spins awarded) and no spins are lost or added | in-game counter |
| B6 | Leaving the game mid-feature and coming back resumes the same feature (same spins left, same win so far), no second free buy | leave + return |
| B7 | End-of-feature summary shows the total win; the win is credited once to the real balance (balance after − before = total_won), no wagering when `payout_to: cash` | end popup + balance + bondet_state |
| B8 | Only `count` buys are given: after use the game returns to plain real-money mode (normal buy prices, normal stake), no extra free buy offered | screenshot, don't buy or spin |
| B9 | Backend: `bondet_state` `used` = count, `state` complete / `status` empty, `total_won` = credited win; `gaming_ticker` all rounds finished, 0 rejected with wins | opensearch |

## Rules for playing
- Never press the game's own "buy" button with real money. Only accept the free buy offered by the bonus; if the game shows a buy price that would be charged (balance would drop), stop.
- Use autoplay/turbo only inside the bought feature if the game allows it; don't screenshot those settings.
- After the feature ends, don't spin or buy again: the game is in real-money mode.
- Settlement for a buy bonus should be immediate; if Istoric / `complete` lag, note it and recheck once after ~2–3 min.
