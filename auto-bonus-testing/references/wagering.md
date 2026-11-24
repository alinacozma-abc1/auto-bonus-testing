# Wagering bonus (bonus type "Wagering")

Read this **in addition to** the standard Display / Play / Settlement checks when the bonus definition's `type` is `Wagering`: a bonus balance that converts to real money once a wagering amount has been bet. First run: 3273eb93 "Bonus Special Casino" (100 RON, x1, cash_first) on 2026-11-19. Result: PASS WITH WARNINGS.

## Expected sheet
- Definition fields:
  - `reward_amount` and `reward_type`: fixed, or a percentage of the deposit.
  - `wagering_multiplier`: the wager requirement is the reward × the multiplier.
  - `wagering`: `cash_first` or `bonus_first`.
  - `game_product`, `game_category`, `game_select_type`.
  - `launchIds`: empty means no specific game, so the CTA goes to the lobby.
  - `promo_restricted`, `expiry` (days), `popup_displayed`, `public_names`, `offer_details`, `terms_and_conditions`.
- Awarded instance in `bondet_state` (its `_id` is a plain UUID):
  - `initial_amount`, `wager_limit` (the requirement), `wagered`, `uncommitted`, `total_won`, `payout_to`, `expires`.
  - `state` goes new → inprogress → complete. When it completes, `event` is `transfer_pot` and `empty_at` is set.

## Before playing: which balance to wager with (Alina, 2026-11-23)
With `wagering: cash_first`, every bet comes out of the **real balance** before the bonus balance. The T&C usually say so: "banii reali vor fi folosiți înaintea banilor bonus". For Wagering bonuses this is a standing exception to the "never bet real money" safety rule: **playing with the test account's real balance is the default.** Decide from the real balance (`customer_attributes.real_balance`, same as the header) when the run starts:
- **Real balance ≥ wagering requirement** (`wager_limit`): wager with real money. **Don't ask for confirmation.**
- **0 < real balance < requirement:** wager with real money until the cash runs out, then keep playing on the bonus funds until `wager_limit` is reached or the bonus balance is gone. Don't ask. Record the moment the in-game CASH reaches 0 and the bets switch to BONUS (screenshot + the first `gaming_ticker` debit with bonus funding), because that switch is a check worth seeing (P6).
- **Real balance is 0 when the bonus is awarded:** ask the user (AskUserQuestion), and wait for the answer:
  1. **Play bonus only.** Wager on the bonus funds alone, with cash at 0.
  2. **I'll fund the account.** The user deposits; never deposit for them. When they confirm, re-read the balance and apply the rules above.

Never deposit, withdraw, or go past `wager_limit`. Once the requirement is met, any further bet is plain real money.
Superseded on 2026-11-23: asking every run (display only / 0-cash account / allow real money), as on 19/11 and 23/11.

## Check mapping (same ids as test-checklist.md)
- **D5:** bonus amount, from the card's "Rulează … RON" and the panel's "Bonus rămas".
- **D6:** wagering requirement, from the progress bar "0.00 / <wager_limit> RON".
- **D7:** eligible games ("jocuri eligibile").
- **D10:** compare the T&C game restrictions with `game_category` and `game_product`. A T&C line like "ruletă, blackjack, video poker nu participă" next to `table_game` or `live_casino` in the config is a ⚠️ Config miss (seen on the first run).
- **P1:** the game shows CASH and BONUS separately (e.g. on Pragmatic).
- **P5:** in-game BONUS = the reward.
- **P6:** the wagering order matches the config. With cash_first, CASH drops by the stake and BONUS stays put. Confirm in `gaming_ticker`: debits have `funding_type: cash` and `bonus_amount_used` is 0. Once cash runs out (or cash was 0), BONUS should drop by the stake instead and `bonus_amount_used` should be greater than 0. Those bets must still count toward `wagered`.
- **P7:** `wagered` in `bondet_state` rises by exactly each stake. Re-check it once the first spin settles, before scaling up.
- **P8:** a completion popup ("Ai câștigat <X> RON – Ai rulat bonusul cu succes …") appears on the bet that reaches `wager_limit`.
- **S1:** the real balance rises by the bonus amount at completion. Compare the balance just before the last spin, plus that spin's win, with the balance after.
- **S2:** card gone from Bonusuri.
- **S3:** in Istoric as "Folosit" with the amount.
- **S4:** `bondet_state` shows complete / transfer_pot, `wagered` = `wager_limit`, and `uncommitted` 0.
- **S5:** rounds finished and none rejected.

## Playing
- Use a plain slot in an eligible category. Mute it and leave the speed at default (Pragmatic slots have no turbo toggle in the bar).
- Place one spin at the default stake first, then check `bondet_state.wagered`.
  - If it moved, **go to a high stake to finish fast (Alina, 2026-11-24).** Aim to cover what's left of `wager_limit` in about 5–15 spins, not 60+. On e5bd8a70 (€250) it took 66 spins at €2.50–€5 and ~12 minutes; at €25 it would be ~10 spins.
    - Stake ≈ what's left ÷ 10, rounded to the nearest stake the game offers, and never more than what's left (only the final, completing bet may cross the limit).
    - Keep each stake ≤ the current cash balance. If cash runs out mid-way, carry on with the bonus funds per the funding rules above (that's fine, not a reason to stop).
    - Pick a slot with a wide bet range (Pragmatic slots usually go to €100+). Avoid very high-volatility games, so one stake doesn't wipe the balance before the requirement is met.
    - Recheck `wagered` after the first high-stake spin and before the last few, and lower the stake for the final spin(s) to land on or just over the limit.
    - If a single high stake would need autoplay counts the game doesn't allow (e.g. Pragmatic's 30-spin minimum), spin manually: 5–15 manual spins is faster than a long autoplay at a low stake.
  - If it didn't move, stop: cash bets may not count, or the game may be excluded. Report what you saw.
- **Count from `gaming_ticker`, not from clicks.** A click during a win or tumble animation doesn't start a spin. On the first run, 2 of 9 clicks were lost that way. Before the final spins, recompute what's left from `wagered`.
- Stop as soon as the completion popup appears. Never spin past `wager_limit`, because any further bet is plain real money.

## Seen on the first run (2026-11-19, 3273eb93)
- The whole bonus worked end to end.
- I reported the Istoric expiry-date label as ⚠️ Cosmetic by mistake. It is already in `known-expected-behaviours.md` (raised to product as an improvement), so read that file before listing findings.
- With cash-first x1, a player who has cash converts the bonus just by betting the same amount of their own money, and the bonus balance is never touched. That matches the T&C, so note it as a caveat, not a finding.

## Seen on the GR run (2026-11-24, e5bd8a70 "Casino Bonus 25 euro", €25 x10, cash_first, slot)
- **Pick a game that counts.** Amusnet/EGT games such as El Dogiachi 1000 carry `promo_restricted: true` in `gaming_ticker`, and their bets did not move `wagered`. Pragmatic Wolf Gold (low volatility, €2–€10 steps: 2.00, 2.25, 2.50, 3.75, 5.00…) counted. Always probe one spin and check `wagered` first.
- **Pragmatic autoplay:** the slider's minimum is 30 spins, so plan batches as 30 × stake ≤ what's left, then finish with manual spins. After autoplay ends, the settings box can reopen by itself: close it with its X. The second click of a quick double click is a slam-stop, not a new spin, so count from `wagered`, not clicks.
- **Game credit is combined:** Wolf Gold shows one CREDIT = cash + bonus (no separate BONUS line), so at completion the credit doesn't jump. Reconcile S1 from `gaming_ticker` (cash before the last spin − its stake + `initial_amount`) against the site header.
- **The card can show the wrong amount:** the Rewards card's "Play a total of" showed the bonus amount (25.00 EUR) instead of the requirement (250.00 EUR). The panel was correct. Always compare the card with the panel (it only looked right on RO because x1 makes them equal).
- **No completion message** appeared with `popup_displayed` false: no popup in the game or on the site, and nothing in Notifications. Reported as ⚠️ pending owner confirmation.
- `customer_attributes.real_balance` lagged or was off after completion, so trust the header plus `gaming_ticker`.
- **Re-test at high stakes (same day, instance 3e80e314):** Wolf Gold's maximum bet is €20. 12 × €20 + 1 × €10 finished €250 in about 4 minutes of manual spins (vs about 12 min at €2.50–€5).
- **One mid-play card check (Alina, 2026-11-24):** at roughly 40% of `wager_limit`, open Rewards in a second tab, leaving the game open. Screenshot the card (bar + amount) and the panel ("x / wager_limit EUR") against `wagered` at that moment. Done once per wagering test. Result on e5bd8a70: the card bar tracks the real requirement, and only the card's amount label is wrong.
