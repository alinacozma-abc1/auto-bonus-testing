# Wagering bonus (bonus type "Wagering")

Read this **in addition to** the standard Display / Play / Settlement checks when the bonus definition's `type` is `Wagering`: a bonus balance that converts to real money once a wagering amount has been bet.

## Expected sheet
- Definition fields:
  - `reward_amount` and `reward_type`: fixed, or a percentage of the deposit.
  - `wagering_multiplier`: the wager requirement is the reward × the multiplier.
  - `wagering`: `cash_first` or `bonus_first`.
  - `game_product`, `game_category`, `game_select_type`, `excluded_games`.
  - `launchIds`: empty means no specific game, so the CTA goes to the lobby.
  - `promo_restricted`, `expiry` (days), `popup_displayed`, `public_names`, `offer_details`, `terms_and_conditions`.
- Awarded instance in `bondet_state` (its `_id` is a plain UUID):
  - `initial_amount`, `wager_limit` (the requirement), `wagered`, `uncommitted`, `total_won`, `payout_to`, `expires`.
  - `state` goes new → inprogress → complete. When it completes, `event` is `transfer_pot` and `empty_at` is set.

## Before playing: which balance to wager with
With `wagering: cash_first`, every bet comes out of the **real balance** before the bonus balance (the T&C usually say so, e.g. "banii reali vor fi folosiți înaintea banilor bonus"). For Wagering bonuses this is a standing exception to the "never bet real money" safety rule: **playing with the test account's real balance is the default.** Decide from the real balance (`customer_attributes.real_balance`, same as the header) when the run starts:
- **Real balance ≥ wagering requirement** (`wager_limit`): wager with real money. **Don't ask for confirmation.**
- **0 < real balance < requirement:** wager with real money until the cash runs out, then keep playing on the bonus funds until `wager_limit` is reached or the bonus balance is gone. Don't ask. Record the moment the in-game CASH reaches 0 and the bets switch to BONUS (screenshot + the first `gaming_ticker` debit with bonus funding).
- **Real balance is 0 when the bonus is awarded:** ask the user (AskUserQuestion), and wait for the answer:
  1. **Play bonus only.** Wager on the bonus funds alone, with cash at 0.
  2. **I'll fund the account.** The user deposits; never deposit for them. When they confirm, re-read the balance and apply the rules above.

Never deposit, withdraw, or go past `wager_limit`. Once the requirement is met, any further bet is plain real money.

## Checks (same ids as test-checklist.md)
- **D5 amount and requirement on the card:** compare the card with the panel. The card's "Play a total of / Rulează" amount must equal `wager_limit`, not the bonus amount. With x1 they're equal, so the mistake only shows when the multiplier is above 1.
- **D6 requirement in the panel:** "Play a total of <wager_limit>" and the progress bar "0.00 / <wager_limit>".
- **D7:** eligible games ("jocuri eligibile" / games tab).
- **D10:** compare the T&C game restrictions with `game_category`, `game_product` and `excluded_games`. A T&C line like "ruletă, blackjack, video poker nu participă" next to `table_game` or `live_casino` in the config, or a T&C list of excluded games while `excluded_games` is empty, is a ⚠️ Config miss.
- **P1:** the game shows the bonus funds (CASH and BONUS separately on some Pragmatic and Napoleon games; one combined CREDIT on others, e.g. Wolf Gold on superbet.gr).
- **P5:** in-game bonus amount = the reward.
- **P6:** the wagering order matches the config. With cash_first, CASH drops by the stake and BONUS stays put. Confirm in `gaming_ticker`: debits have `funding_type: cash` and `bonus_amount_used` is 0. Once cash runs out (or cash was 0), BONUS drops instead and `bonus_amount_used` > 0, and those bets must still count toward `wagered`.
- **P7:** `wagered` in `bondet_state` rises by exactly each stake.
- **P7b, one mid-play card check:** at roughly 40% of `wager_limit`, open the bonus area in a second tab (leave the game open). Screenshot the card (progress bar + amount) and the panel ("x / wager_limit") and compare with `wagered` at that moment. The bar must track `wager_limit`. Once per wagering test.
- **P8:** a completion popup ("Ai câștigat <X> RON – Ai rulat bonusul cu succes …") appears on the bet that reaches `wager_limit`. If nothing appears (seen when `popup_displayed` is false), check Notifications too and report ⚠️ "no completion message" for the owner to confirm.
- **S1:** cash rises by the bonus amount at completion. Reconcile from `gaming_ticker`: cash before the last bet − its stake + its win + `initial_amount` = the header balance after. When the game shows one combined credit, it doesn't jump at completion, so use this calculation, not the game's number. `customer_attributes.real_balance` can lag; trust the header and `gaming_ticker`.
- **S2:** card gone from the bonus area.
- **S3:** in Istoric as "Folosit" / Used with the amount.
- **S4:** `bondet_state` complete / transfer_pot, `wagered` = `wager_limit`, `uncommitted` 0.
- **S5:** rounds finished and none rejected.

With cash-first x1, a player who has cash converts the bonus just by betting the same amount of their own money, and the bonus balance is never touched. That matches the T&C: note it as a caveat, not a finding.

## Playing
1. **Pick a game that counts.** Use a plain, eligible slot. Games flagged `promo_restricted: true` in `gaming_ticker` (e.g. Amusnet El Dogiachi 1000 on superbet.gr) don't move `wagered`. Pragmatic Wolf Gold counted. If the bonus has `launchIds`, use that game.
2. **Probe once.** Place one spin at the default stake, then check `bondet_state.wagered`. If it didn't move, stop and report: cash bets may not count, or the game is excluded.
3. **Then go to a high stake to finish fast.** Aim to cover what's left of `wager_limit` in about 5–15 spins (a €250 requirement took 66 spins and ~12 min at €2.50–€5, but 13 spins and ~4 min at €20).
   - Stake ≈ what's left ÷ 10, at the nearest stake the game offers. Never more than what's left: only the final, completing bet may cross the limit.
   - Keep each stake ≤ the current cash balance. If cash runs out mid-way, carry on with the bonus funds per the funding rules above.
   - Prefer games with a wide bet range and low-to-medium volatility, so one stake doesn't wipe the balance before the requirement is met. Know the game's maximum (Wolf Gold: €20).
   - Recheck `wagered` after the first high-stake spin, around the mid-play card check, and before the last few spins; lower the stake for the final spin(s) to land on or just over the limit.
4. **Autoplay only when its count fits.** Pragmatic's autoplay slider starts at 30 spins, so use it only when 30 × stake ≤ what's left; otherwise spin manually (5–15 manual spins are faster than a long low-stake autoplay). After autoplay ends, the Pragmatic settings box can reopen by itself: close it with its X.
5. **Count from `wagered` / `gaming_ticker`, not from clicks.** A click during a win or tumble animation, or the second click of a quick double click (a slam-stop), doesn't start a spin.
6. **Stop as soon as the requirement is reached** (completion popup, or `wagered` = `wager_limit`). Never spin past it, because any further bet is plain real money.
