# Free Chips (bonus type "Free Chips")

Read this **in addition to** the standard Display / Play / Settlement checks when the bonus definition's `type` is `Free Chips`. The checks are the Free Spins ones, read with "chip" for "spin" (Alina, 2026-11-19). First run: 36725b86 (2 × 25 RON on Exclusive Superbet Blackjack 1, Pragmatic Live).

## Expected sheet
`chips` (list of `{value, amount}`: e.g. 2 chips of 25), `total_bonus_value` (= Σ value × amount), game(s) (usually a **live table**, `game_type: live_casino`), provider, `expiry_seconds`, `popup_displayed`. Awarded instance: `bondet_state` `_id` starts with `FC-`, `initial_amount` = total value, `chips`, `used`, `total_spent`, `uncommitted`, `state` new → inprogress → complete, `total_won`.

## Check mapping (same ids as test-checklist.md)
- D5 / P5 = number of chips · D6 / P6 = chip value (stake per hand) · P7 = chip counter decrements by one per hand · P8 = end popup ("Nu mai sunt jetoane gratuite", Câștig Total).
- S4 = `bondet_state` `complete`/`empty`, `used` = all chips, `uncommitted` 0. S5 = `gaming_ticker` rounds `finished`, debit `amount` 0 with `free_play_info.free_chip.id` = the FC id and `totals.free_chip` = chip value.
- Win paid is the **net** win (stake not returned): a won 25 hand at 1:1 pays 25.

## Playing a live table (Pragmatic blackjack)
- After the popup's "Joacă", **take a free seat** (seat icon). Clicking an occupied seat places a bet-behind; check "Pariu total" after every click.
- The seat is released if you skip rounds. Betting windows are short (~10 s) and screenshots lag ~5 s, so you mostly see the timer at 2. Poll with small screenshots and click the seat once as soon as the chip tray appears. Keep it to **one click per window**: once the chips run out, the next click is real money.
- The gold free chip is first in the tray and preselected. After it's placed, the real chips go grey. Verify the balance is unchanged and "Pariu total" = chip value.
- Decisions: stand or hit only. **Never Dublu / Despărțire** (they can draw on real balance) and decline insurance (disabled for free chips anyway).
- After the last chip's hand, don't press "Continuați să jucați" and don't touch the table. Navigate the tab away.
- Pragmatic news popups (new features, "Superbet Bonus Cards") can cover the chips popup. Close them without opting in.

## Seen on the first run (2026-11-19, 36725b86)
After both chips were played and the win credited, the bonus **stayed active**: the card showed "Sumă disponibilă 50.00 RON" and "0.00 / 50.00", it was missing from Istoric, and `bondet_state` stayed `inprogress`/`active` with `used 0`, `total_spent 0`, `uncommitted 50`. Reported as FAIL (not confirmed as expected behaviour). Re-check this on every Free Chips run.

## Evolution Free Chips (first run 2026-11-23, 38724018 on superbet.gr: PASS WITH WARNINGS)
- **Setup:** the instance's `type` is `external_token` with `free_chip_strategy: summary`. The configured chips (e.g. 5,000 × €0.01) behave as one reward balance ("REWARD GAME €50"), which can be used in parts across several rounds; the table minimum still applies (€0.20). No chip count is shown anywhere, so mark D5/D6 ⚠️ Cosmetic.
- **Launch:** CTA → OneLink → table → reward screen ("You are entering … with €50 worth of Reward Game · Max winnings €1,000") → PLAY NOW.
- **Screen name (Alina, 2026-11-23):** Evolution may ask for a screen name before the first bet. Enter it yourself, without asking. Use a generic first name for the market plus numbers (e.g. "Nikos2311"). Never use "test", "qa" or anything from the account's personal data. Change it later under ⚙ Settings → General → Screen name.
- **Roulette play:** mute with the speaker icon (top right). Use even-money outside bets (red/black). Select the chip first (the tray appears only while betting is open), then click the spot.
  - Screenshots lag about 10 s behind the stream, so time clicks blind after "Next game soon". Never place more clicks than the remaining reward can cover.
  - At REWARD GAME €0 the chips grey out. Stop there.
- **End screen:** "Congratulations · You have completed your Reward Game · You have won: €X". Don't press "Play real money"; navigate away.
- **Backend:** one summary `gaming_ticker` round (debit 0 + `free_chip` stake = total, credit = win as cash). `bondet_state` goes complete / `status: empty` with `used` = total and `uncommitted` 0. The Pragmatic "stays active" bug from 19/11 did **not** happen on Evolution.
- **Payout is gross (confirmed expected, Alina 2026-11-23):** a winning bet returns stake + win (€25 at 1:1 → €50). Check that the credit equals the gross return; don't report it as a finding.

## Pragmatic live roulette (2026-11-23, d26d1551 on superbet.gr: PASS WITH WARNINGS)
- **Geo-block:** Pragmatic blocks GR games on a non-GR IP ("Games Unavailable … location Romania"). Stop and ask the tester to switch to a Greek IP. Never try to bypass the block yourself. Evolution did not geo-block.
- **Launch:** the popup shows "Chips N · Value €X · Max Bet · ends in …" and "Play Now". The chip stack sits top left ("N Free Chips · 6d"). Pragmatic assigns a nickname itself, so there's no screen-name prompt.
- **Placing chips:** the gold free chip is first in the tray. While free chips are on the table, the real chips are greyed out. Each click on a spot places one chip.
  - Betting windows are about 15 s, every 80–95 s, and screenshots lag about 10 s. Spread bursts across a cycle (select chip, click spot ×2, wait 3 s, repeat).
  - **Never send more clicks in one batch than the chips left.** Re-read the stack counter (or `bondet_state.uncommitted ÷ chip value`) before every batch.
  - Extra clicks in the same round after the last chip just show "Insufficient funds".
- **Payout:** net, credited per round as cash (the stake is not returned). Confirmed expected for Pragmatic (Alina, 2026-11-23); a Pragmatic gross payout would be a finding. The end popup reads "Free Chips Completed · Total Win €X".
- **Backend:** `free_chip_strategy: standard`. Each round is its own `gaming_ticker` entry (debit 0 + `free_chip` stake). `bondet_state.used`/`total_spent` update after every round and the bonus goes complete / empty at the last chip.
  - The RO "stays inprogress" bug (36725b86) did **not** reproduce on GR Pragmatic, so keep checking S4 on every Pragmatic run.

## Faster chip placement on live tables (Alina, 2026-11-23)
On the 23/11 Pragmatic run, 50 chips took 10 rounds (~17 min) because of small capped batches and ~10 s lag. Use this instead:
1. **Find the window:** take a zoom of the bet area. Act as soon as the chip tray is visible or the timer shows ≥ 10 s.
2. **Fire one fast burst inside that round:** select the free chip, then click the spot once for **every remaining chip**, with no waits. The whole burst must finish within about 3–4 s.
   - Clicks after the last chip in the same round are harmless: they only show "Insufficient funds" and the real chips stay greyed out.
3. **Never let clicks spill into the next round.** Don't add waits inside the burst, and don't queue a second burst until the round has settled. Once the free chips are gone, a click in a new round is a real-money bet.
4. **Recount before each burst:** after each round, read the chips left from `bondet_state` (`uncommitted ÷ chip value`). Use the in-game stack only as a cross-check.
5. **Close out:** stop when the end popup appears ("Free Chips Completed" or Evolution's "Congratulations"). Don't press continue / play real money.
