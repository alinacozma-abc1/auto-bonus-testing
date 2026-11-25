# Countdown Free Spins (bonus type "Countdown Free Spins")

Read this **in addition to** the standard Display / Play / Settlement checks when the bonus definition's `type` is `Countdown Free Spins`. The player gets unlimited spins at a fixed stake for a fixed time (`countdown_time`, seconds); the clock starts on the **first spin**, keeps running even if the player leaves, and the win is paid when the countdown ends. Added 2026-11-18, from the UAT of "3 Minute Rotiri Gratuite Gates of Olympus Super Scatter" (8 cases) plus the first full run on superbet.ro.

## Expected sheet additions
`countdown_time` (s → minutes), stake per spin (`value`), `expiry_seconds` (how long the player has to START it), game(s), provider, `popup_displayed`. There is **no spin count** — don't report "spins" checks (D5/P5/P7 become C-checks below). Backend: `bondet_state` carries `first_spin_timestamp`, `countdown_time`, `state` (new → inprogress → complete), `total_won`; **end of countdown = first_spin_timestamp + countdown_time**.

## Rules for playing
- **Play with autoplay ("Joc automat") and turbo ("Joc rapid") on**. Turbo is the "Joc rapid" switch inside the autoplay dialog for Pragmatic games, not in Settings. Pick the max autoplay count and restart it when it ends.
- **Autoplay must never run through the end of the countdown into real money.** Stop autoplay before the last ~2 minutes, then watch the end manually. If the game shows no bonus HUD (timer/stake), stop — real money.
- Take a `date -u` stamp at the first spin, at every leave/return, and at expiry; the clock checks compare in-game timer vs wall clock vs `first_spin_timestamp`.
- The clock is real time, so a full run is `countdown_time` long (60 min for a 60-minute bonus). Do the pause/return tests while it runs, then wait for expiry. Use a background `sleep` to wait; don't poll.

## Countdown checks (C-ids)
| ID | Check | How |
|---|---|---|
| C1 | Before the first spin the clock shows the full time and does NOT run (launch, popup, intro screens don't start it) | screenshot HUD after popup, wait ~10 s, still full |
| C2 | Clock starts at the first spin; `bondet_state.first_spin_timestamp` ≈ moment of the first spin | compare stamps |
| C3 | In-game timer decrements 1:1 with wall clock (no drift) at ≥2 checkpoints | timer vs `date -u` since first spin |
| C4 | Popup states the correct duration, stake, claim-until date; unit consistent with name/card (minutes vs seconds) | popup text vs config |
| C5 | Card in Bonusuri shows the same remaining time as the game and keeps ticking while the player is **away** | card timer vs game vs wall clock |
| C6 | **Leave mid-countdown** (navigate away / close game tab): clock keeps running, card shows reduced time, balance unchanged | leave ~1–2 min |
| C7 | **Return before expiry** (CTA on card / game URL): lands in the game in bonus mode, remaining time matches wall clock (±2 s), stake unchanged, bonus popup not shown again (or shown consistently), spins work | compare HUD vs wall clock right after load |
| C8 | **Reload / second tab / fresh launch** mid-countdown: same remaining time, no duplicate bonus, no second countdown | F5, open game in another tab |
| C9 | Win counter in the bonus HUD accumulates; balance behaviour mid-run matches T&C (paid at end vs per spin) | HUD win vs real balance |
| C10 | **At expiry**: spins stop or game leaves bonus mode cleanly; end screen/popup (if any) shows total win; no real-money spin possible by accident | observe last 10 s |
| C11 | **Return AFTER expiry** (reopen game / card CTA): no active bonus, no stale timer, plain real-money game (not auto-spinning), no error popup | reopen after end |
| C12 | Total win credited to **real balance** exactly = `total_won` (and HUD win); T&C "if not credited, reopen the game" case: note whether it needed reopening | balance after − before |
| C13 | Card leaves the active list; appears in Istoric with the right name/status/amount. **Known: Istoric and `complete` arrive ~10 min after the end (confirmed 2026-11-18) — don't wait for it; leave it out of the check list and mention "not re-checked, known delay" in the caveats** | Bonusuri + Istoric |
| C14 | Backend: `bondet_state` state `complete` (≈ end + 10 min), `total_won` = HUD, `first_spin_timestamp` + `countdown_time` ≈ end observed; `gaming_ticker`: no spin after the end time, no rejected rounds with wins | opensearch |
| C15 | Spin after expiry (only if the game still allows a click): must be a real-money prompt/blocked, never silently a bonus spin; do NOT spin real money — observe only | screenshot, no click |
| C16 | Start-of-claim window: bonus can be started until `awarded + expiry_seconds`; popup "claim until" date matches | popup vs `expires` |

Severity: C2, C3, C6, C7, C10–C14 failures are **Experience miss**; wrong durations/texts (C4, C16) are **Config miss**; unit/wording are **Cosmetic**.

## Known game quirks seen (not product defects unless stated)
- Pragmatic games open on an intro screen with a round "play" arrow (gorilla logo) — press it to start the game (the UAT recorded this as game-load freezes).
- Pragmatic shows its own bonus popup on first load even when `popup_displayed` is false in Betler.
- Popups state the countdown in seconds while the card/T&C use minutes — expected (see known-expected-behaviours.md).
- Report as ⚠️ (not confirmed as expected): the in-game timer lags the server clock in a background tab (4 min after 22 min); a fresh load re-syncs. Opening a second tab/page drops the game session. Wins are credited to the real balance during play although the T&C say after the minutes finish.
- Pragmatic's own features (bird-catch pick screen, in-game free spins) can stall autoplay until clicked.
- Istoric / `complete` come ~10 min after the end (known delay). **Don't wait for it**: check the other settlement points immediately, leave S3/S4 out of the check list and add "history / final backend state not re-checked (known ~10 min delay)" to the caveats, then post at once; wait and re-verify only if the user asks.

## EGT / Amusnet countdown
- **Popup:** "COUNTDOWN FREE SPINS · UNLIMITED FREE SPINS x €X · FOR: 1 MIN : 00 SEC" with PLAY LATER / PLAY NOW. The bar under the reels shows BET · TIME LEFT · TOTAL WIN. The spin button is the large circular arrow on the right; mute with the speaker icon at bottom right.
- **Known gap, not a failure:** the game's Time left timer starts at PLAY NOW, but Betler's `first_spin_timestamp` and the card timer start at the first spin (typically 15–20 s apart). It's in known-expected-behaviours.md, being addressed with product. Don't fail C1/C2 or the card-vs-game timer check for it; note the measured difference once in the caveats. To keep the run efficient, start autoplay right after PLAY NOW.
- **Wins:** credited to the real balance per winning spin, with no end-of-run batch.
- **End:** popup "has ended! YOU HAVE WON €X · You are playing with real money!", then the normal bet selector. Never spin after it.
- **Short countdowns (≤ 2 min):** skip C6–C8 (leave / return / reload) and say so in the caveats. Use autoplay + turbo if the game has them (rule in SKILL.md), stopping in the last ~10 s; manual clicks during a spin animation are ignored.
- **EGT controls:**
  - Autoplay is the small circular-arrow button above the spin button. It offers 10 / 20 / 50 / 100 / ∞. Pick a fixed count (never ∞) that ends well before the countdown does.
  - There's no turbo / quick-spin option, and the menu doesn't open during autoplay.
  - An "Amusnet Tournament" popup appears on every launch. Close it with its X, never "Join tournament".
- **EGT end of countdown:** if the last spin wins, the game stops at 0:00 and offers two buttons: **x2** (double-or-nothing gamble) and **collect** (the download-arrow icon).
  - Press **collect**, never x2. The last win reaches the balance, and the "has ended! YOU HAVE WON …" popup appears, only after collect.
  - Likely provider-side, so mention it in the caveats, not as a finding.


## Use the countdown wait
While a countdown runs on autoplay, don't sit idle. Between the in-game checks, draft `findings.json` (display, play and countdown checks seen so far), build the contact sheet from the screenshots already taken, and create the Drive folder. After the end, add only the final checks, re-run the scripts and post. Never let this delay the end-of-countdown checks (watch the last ~2 min live).
