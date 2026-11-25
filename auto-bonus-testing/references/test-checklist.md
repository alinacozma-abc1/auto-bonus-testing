# Test checklist (Free Spins – first version)

Each line = one row in the report. Record expected, observed, status.

## Display (before playing)
| ID | Check |
|---|---|
| D1 | Bonus visible to the player in the bonus area / promo placement for this account |
| D2 | Public bonus name matches config (and language is right for the account's locale) |
| D3 | Promo public name / title matches config |
| D4 | Offer details text matches config (number of spins, stake per spin, game, validity) – no placeholder/raw keys like `{{spins}}`, no truncation, no typos |
| D5 | Number of spins shown = configured |
| D6 | Stake per spin shown = configured |
| D7 | Game shown = a configured game |
| D8 | Expiry shown ≈ awarded_at + configured expiry |
| D9 | T&C link present; click → loads (no 404/blank), opens the right document for THIS promo, right language |
| D10 | T&C content consistent with config (spins, stake, expiry, game restrictions) |
| D11 | CTA label matches config; click → goes to the configured destination (game page/deeplink); lands logged-in on the right game |
| D12 | Images/layout render (no broken image, overflow, overlapped text) – WARN level |

## Play
| ID | Check |
|---|---|
| P1 | Game launches **in bonus mode** (else STOP – see safety rules) |
| P2 | FS popup appears on launch (if `popup displayed` = Yes) – no popup when config says No |
| P3 | Popup content: number of spins, stake, game = config; text/language correct; no raw keys |
| P4 | Popup OK/Continue button works and closes the popup |
| P4b | Speed set to max and sound muted before spinning (setup step, not a pass/fail on the product; no screenshot, never in the evidence folder) |
| P5 | In-game free-spin counter = configured number of spins |
| P6 | Stake per spin during FS = configured stake (check the bet display; real balance must not decrease while spinning) |
| P7 | Counter decrements by one per spin and the spin total matches (no lost or extra spins) |
| P8 | FS round ends with the game's end/summary screen showing total win |

(No console/network check: logs are only read to diagnose a visible failure, never reported as a check row or as Blocked.)

## Settlement
| ID | Check |
|---|---|
| S1 | Win shown at end of FS = amount credited: real-money balance after − before = total win (if wagering applies, check the bonus balance / wagering progress instead and compare with config) |
| S2 | Bonus no longer in the active list |
| S3 | Bonus present in history with correct name and a final status (Used / Completed), correct amount/spins |
| S4 | Backend: `bondet_state` status final, `fsinfo_state` used = configured spins and remaining = 0 |
| S5 | Backend: `gaming_ticker` shows no rejected rounds carrying a win that never got credited |

Retry backend reads once after ~2–3 minutes before marking S4/S5 as FAIL; if still inconsistent, FAIL with the raw values.

## Severity
- **Config miss** – player-visible value differs from what Betler says should be configured (D2–D11, P3, P5, P6).
- **Experience miss** – behavior is broken even though config is right (D1, D9/D11 link failures, P1–P2, P4, P7–P8, S1–S5).
- **Cosmetic** – D12 and typos → WARN.

## Adding other bonus types later
Cash bonus, free chips, countdown FS, wagering, buy bonus, cashback: add `references/<type>.md` with the type-specific D/P/S rows and point to it from SKILL.md. Sports bonuses get their own skill or reference with the player's bet-slip flow.

## Provider notes (Free Spins)
- **EGT Digital** (e.g. 5 Crown Hot Clover Chance): the popup says "YOU HAVE RECEIVED 10 GIFT SPINS!" with no stake (the €0.05 shows in the bet box under the reels; likely provider-side, not a finding). Autoplay offers 10/20/50/100/∞ and there is a turbo (">>>") button under the spin button. After the last spin the "You have completed your Gift Spins! TOTAL WIN" popup has only CONTINUE: the last round stays open in Betler (used 9/10) until CONTINUE is pressed. Press it (it only dismisses the popup and places no bet), check the game shows the normal bet selector, and don't spin.
- **Amusnet / EGT** (e.g. El Dogiachi 1000): popup "CONGRATULATIONS! You get 10 FREE SPINS x 0.05 EUR" with PLAY NOW / PLAY LATER. Autoplay 10/20/50/100/∞, no turbo. The end popup's OK returns the game to the normal bet selector.
