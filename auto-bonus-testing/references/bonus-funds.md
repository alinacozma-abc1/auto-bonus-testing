# Bonus Funds (bonus type "Bonus Funds")

Read this **in addition to** the standard Display / Play / Settlement checks when the bonus definition's `type` is `Bonus Funds`.

## What it is
A bonus balance with **no wagering requirement**: `reward_amount` (or `reward_type: dynamic` with `reward_amount_percentage` / `max_reward_amount`), `expiry` (days), `game_product` (e.g. casino + live_casino), `game_select_type`, `games` / `launchIds` when limited to a list, `payout_to` cash. There's no `wagering_multiplier` and no `wager_limit` in `bondet_state`. Often no `offer_details`, `terms_and_conditions` or CTA deeplink.

## Expected behaviour
- **Bets come from the bonus balance first**, even when there is cash. Games that show CASH and BONUS separately show BONUS dropping; `gaming_ticker` debits have `funding_type: bonus`.
- **Winnings go straight to cash** per round. CASH rises and `bondet_state.total_won` adds up.
- **It completes when the bonus balance reaches 0:** `bondet_state` complete, `total_spent` = reward, `uncommitted` 0.
- **End popup:** with a win, "AI CÂȘTIGAT X RON · Ai rulat bonusul cu succes <public name> și ai câștigat X RON"; with no win, "ÎNCEARCĂ-ȚI NOROCUL DATA VIITOARE! · <public name> a fost rulat în totalitate, dar nu ai câștigat".
- **A game's balance includes only the bonuses eligible for that game.** With two Bonus Funds active, each eligible game shows cash + only its own bonus.
- T&C may describe the bonus as "rulaj 1x … convertit în bani reali". The player outcome is the same as wins-straight-to-cash, so this wording is not a finding.

## How to play it
- No real money is needed: play only the bonus balance.
- **Stake:** pick one that divides the bonus exactly (e.g. 20 → 2 × 10 or 2.50 × 8; 320 → 30 × 10 + 20) and size the **last bet to exactly the bonus left**, so no cash is ever bet.
- **Spin manually, no autoplay.** Once winnings sit in cash, autoplay would keep betting them as real money, and many autoplay minimums (Amusnet 10, Pragmatic 30) overshoot the bonus.
- **Several Bonus Funds active, with overlapping game lists:** play each bonus on a game that is in its list only, and attribute bets by `bondet_state.total_spent` per instance.
- **"DEPOZIT NECESAR … Depune acum / Joacă oricum"** can appear when launching a game with 0 cash. Press **Joacă oricum** (never deposit) and report the popup as ⚠️ Experience miss: the bonus needs no deposit.
- **Geo-blocks:** some providers block a non-local IP (e.g. Greentube Sizzling Hot Deluxe on superbet.ro: "Jocul ales nu este disponibil în țara dvs."). Use another eligible game, or ask the tester to switch IP.
- **Provider popups:** Playson shows tournament popups on launch (Turbo Races → REFUZĂ → DA, REFUZ; Grand Race → X). Don't join them.

## Checks specific to this type
- **Visible in the bonus area:** check the casino home page, the sports home page and Promoții și Bonusuri → Bonusuri. A Bonus Funds bonus may show only as a home page card ("XX LEI BONUS", Folosește recompensa / Vezi detalii), or nowhere after the award popup. Card only on the home page and missing from Bonusuri = ⚠️; not shown anywhere = ❌, and the card checks (name, amount, T&C link, CTA button) are ⛔ BLOCKED. In that case check the T&C URL and the CTA deeplink by opening them directly from the config.
- **Public name:** the card and panel may say "XX LEI BONUS" instead of the public name, which then only shows in the completion popup (⚠️ Cosmetic).
- **"Vezi detaliile recompensei"** opens the general Promoții page when no T&C is configured. Note it; not a finding.
- **History:** Bonus Funds may not appear in Istoric after use. Report ⚠️ if missing.
- **Settlement:** total won = popup = `total_won` = cash gained from the bonus rounds. Exclude any deposit the tester makes meanwhile (check `last_deposit_ts`).
