# Bonus Funds (bonus type "Bonus Funds")

First run: 2019577f "Bonus Casino" (320 RON, napoleongames.ro, 2026-11-24). Result: PASS WITH WARNINGS.

## What it is
A bonus balance with **no wagering requirement**: `reward_amount`, `expiry` (days), `game_product` (e.g. casino + live_casino), `game_select_type`, `payout_to` cash. There's no `wagering_multiplier` and no `wager_limit` in `bondet_state`. Often no `offer_details`, `terms_and_conditions` or CTA deeplink.

## Observed behaviour (expected rules)
- **Bets come from the bonus balance first**, even when there is cash. The game shows CASH and BONUS separately (Pragmatic), and `gaming_ticker` debits have `funding_type: bonus`.
- **Winnings go straight to cash** per round. The game's CASH rises, and `bondet_state.total_won` adds up.
- **Completes when the bonus balance reaches 0:** `bondet_state` complete, `total_spent` = reward, `uncommitted` 0. Completion popup: "AI CÂȘTIGAT X RON · Ai rulat bonusul cu succes <public name> și ai câștigat X RON".

## How to play it
- No real money is needed. Play only the bonus balance: high stakes (about reward ÷ 10), and size the **last bet to exactly the bonus left**, so no cash is ever bet.
- **Spin manually, no autoplay.** Once winnings sit in cash, autoplay would keep betting them as real money.
- Launching a game with 0 cash may show "DEPOZIT NECESAR … Depune acum / Joacă oricum". Press **Joacă oricum** (never deposit) and report the popup as ⚠️ Experience miss.

## Checks specific to this type
- Display: where it shows. On Napoleon RO it showed **only** as a card on the casino home page ("320.00 LEI BONUS", Folosește recompensa / Vezi detalii). It was **not** in Promoții și Bonusuri → Bonusuri, and **not** in Istoric after use. Reported as ⚠️.
- The card and panel title showed "320.00 LEI BONUS", not the public name. The name only appeared in the completion popup (⚠️ Cosmetic).
- "Vezi detaliile recompensei" opens the general Promoții page when no T&C is configured. Note it, not a finding.
- Settlement: total won = popup = `total_won` = cash gained from the bonus rounds (exclude any deposit the tester makes meanwhile; check `last_deposit_ts`).

## Seen on superbet.ro (2026-11-24, ceb06037 + 7754419d "Provocarea din SuperSocial", 20 RON each)
- **Not shown anywhere after the award popup.** There was no card on the casino or sports home page, Bonusuri said "NU AI BONUSURI ACTIVE", and nothing appeared in Istoric after use. Reported as ❌ (visible in bonus area). The card checks (name, amount, T&C link, CTA button) were ⛔ BLOCKED. Check the T&C URL and the CTA deeplink by opening them directly from the config.
- **The game balance includes only the bonuses eligible for that game.** With two Bonus Funds active, Shining Crown showed cash + 20 (ceb06037 only), and Coin Strike showed cash + 20 (7754419d only). Choose a game unique to the bonus under test when game lists overlap, and attribute bets with `bondet_state.total_spent`.
- **End popup with no win:** "ÎNCEARCĂ-ȚI NOROCUL DATA VIITOARE! · <public name> a fost rulat în totalitate, dar nu ai câștigat". With a win: "AI CÂȘTIGAT X RON" (Napoleon).
- **Sizing:** pick a stake that divides the bonus exactly (2 RON × 10, or 2.50 RON × 8) and spin manually. Amusnet's autoplay minimum is 10, which would run into cash.
- **Geo-blocks:** some providers (e.g. Greentube Sizzling Hot Deluxe) block a non-RO IP ("Jocul ales nu este disponibil în țara dvs."). Use another eligible game, or ask the tester to switch IP.
- **Playson** shows tournament popups on launch (Turbo Races → REFUZĂ → DA, REFUZ; Grand Race → X). Don't join them.
