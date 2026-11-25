---
name: auto-bonus-testing
description: End-to-end QA of a casino bonus on production, from the PLAYER's point of view. Given a bonus id and a test account (customer id) logged in on the browser, it takes the market (country + brand → site and Slack channel) from Betler, then checks what the player sees (offer details, public name, T&C link, CTA) against the Betler configuration. It plays the bonus through and verifies that the win or conversion reached the real-money balance and that the bonus moved to history. Then it posts a status-per-check summary to the market's Slack channel, with screenshots on Drive. Supports Free Spins, Countdown Free Spins, Buy Bonus, Free Chips (live tables) and Wagering bonuses (played with the account's real balance first) on superbet.ro, napoleongames.ro, superbet.gr, superbet.pl, superbet.rs, napoleoncasino.be and napoleonsports.be. Use whenever the user says "test this bonus", "QA bonus <id>", "check the free spins / free chips / wagering bonus on account <id>", "verify the bonus works for the player", "test the offer on the test account", or hands you a bonus id + test user id, even if they don't say "skill". Sports bonuses are not covered yet.
---

# Auto bonus testing – player-perspective casino bonus test

## Before you start
Each tester needs, once:
- **Betler production MCP** (`mcp__betler-production-mcp__*`), signed in through their own Teleport session. Everything is read from production.
- **Claude in Chrome** connected to their own Chrome, where the test accounts are signed in.
- **Slack connector** (to post in the market channels below) and **Google Drive connector**, each signed in with their own account.
- **Membership of the "Automated Bonus Tests" team Shared Drive** with rights to upload and to move old folders to trash (see `references/storage.md`).
- **Their own test accounts** on each site they test (flagged `TEST_ACCOUNT` in Betler), signed in by the tester. For Wagering bonuses the account needs real balance; see `references/wagering.md`.
- **A Greek or Romanian IP when the provider needs it** (e.g. Pragmatic on superbet.gr, Greentube on superbet.ro).
- Python 3 (built into macOS). The contact-sheet script installs its image library into `~/.cache/auto-bonus-testing-venv` on first use.

If one of these is missing, say which one in one line and stop before playing; don't work around it.

You act as the player. The point is to catch two kinds of problems before real players do:
1. **Configuration misses** – what the player sees (or gets) differs from what was configured in Betler (wrong number of spins, wrong stake, wrong game, missing/incorrect T&C, dead CTA…).
2. **Experience misses** – the bonus can't be started, the popup is wrong/missing, spins don't match, the win isn't credited, the bonus never moves to history…

Report every miss, including small ones (typos, wrong language, broken link). A test that only says "all good" is worthless if you didn't actually compare numbers, so each check must carry the **expected** value, the **observed** value and a status.

## Inputs — only the two ids
The only inputs are the **bonus id(s)** and the **user id**. If either is missing from the request, ask for it in one short plain message. Don't ask for country, brand or environment:
- **Environment is always production.** This skill is never used for stage tests. Always query the production Betler MCP (`mcp__betler-production-mcp__*`) and never the stage, dev or QA ones.
- **Market comes from Betler.** Read `jurisdiction_domain` (country) and `jurisdiction_brand` (brand) from the bonus definition. Map them to the site and Slack channel with the Market rules table below.

| Input | Notes |
|---|---|
| User id | `customer_id` (UUID) of the test account the bonus was awarded to |
| Bonus id(s) | **One or more** bonus *definition* ids (and/or awarded instance ids). Accept a list separated by commas, spaces or new lines. All bonuses in one run share the same user and market; bonuses from different markets, or a different user, are separate runs. De-duplicate the list. |

State the result back in one line before starting, without waiting for confirmation, e.g. "Testing 3273eb93 on prod · RO · Superbet → superbet.ro, posting to #ro-automated-bonus-testing."

Stop and ask only when one of these happens:
- The bonus id isn't found on production. It is probably a typo or a stage id.
- Several bonuses resolve to different markets.
- The pair has no row in the Market rules table. In that case, ask for the site URL and the Slack channel.

**Market rules** — site to test on and Slack channel for the summary:
| Market | Site | Slack channel |
|---|---|---|
| Romania · Superbet | https://superbet.ro/ | #ro-automated-bonus-testing `C0CJB87LB47` |
| Romania · Napoleon | https://napoleongames.ro/casino | #ro-automated-bonus-testing `C0CJB87LB47` |
| Greece · Superbet | https://superbet.gr/ | #gr-automated-bonus-testing `C0CK8NZR5L1` |
| Belgium · Napoleon Casino (`be` / `napoleoncasino`) | https://napoleoncasino.be/fr-be/games | #be-automated-bonus-testing `C0CL3KC996J` |
| Belgium · Napoleon Sports (`be` / `maxbetsports`) | https://napoleonsports.be/ | #be-automated-bonus-testing `C0CL3KC996J` |
| Poland · Superbet | https://superbet.pl/ | #pl-automated-bonus-testing `C0CL3KE2GS2` |
| Serbia · Superbet | https://superbet.rs/ | #rs-automated-bonus-testing `C0CL09R1H2R` |

Belgium's Betler values: `jurisdiction_domain` = `be`; `jurisdiction_brand` = `napoleoncasino` (casino row) or `maxbetsports` (sports row, confirmed = napoleonsports.be). Any other Belgian brand value (e.g. a Napoleon Dice brand) isn't mapped, so ask. Poland and Serbia's exact values haven't been seen yet (expected `pl` / `rs` + `superbet`). On their first run, state what you found.

The market is taken from the bonus definition's `jurisdiction_domain` / `jurisdiction_brand`. For a pair not in the table, ask for the site URL and the Slack channel before starting. Also check that the customer record's `jurisdiction_domain` / `jurisdiction_brand` (in `customer_attributes`) match the bonus. A mismatch means the wrong user or the wrong bonus id: stop and tell the user.

The test account should be **logged in** in Chrome. Never type credentials, never press the site's log-in button (even when Chrome has autofilled a saved password), never log out, never change account settings — signing in is always done by a person.

**If the browser is logged out at the start:** don't fail the run. Open the site's sign-in form in the test tab (the header's log-in / "Intră în cont" button) so Chrome can autofill the saved username and password, take no further action on the form, and tell the user in one line: "The test account isn't logged in — I've opened the sign-in page on <site>; press Log in there and tell me when it's done." Wait for their reply, then run the Phase 0 identity check and continue. If a different account is logged in, say which username is shown and stop — don't log it out.

Browser: use the user's Chrome (`mcp__claude-in-chrome__*`, load via ToolSearch in one call: tabs_context_mcp, navigate, computer, read_page, find, get_page_text, tabs_create_mcp, tabs_close_mcp, read_console_messages, read_network_requests). Their session is the logged-in one; the built-in browser pane usually isn't.

## Safety rules (money is involved, even on test accounts)
- Only play **bonus mode**. If the game opens in real-money mode (no FS popup / no bonus indicator), **stop**, mark the play checks `BLOCKED`, and flag it – don't spin real balance.
- No deposits, withdrawals, payment pages, limit/responsible-gaming changes, or opt-ins other than the bonus under test.
- Don't accept other bonuses/offers that pop up; note them and dismiss.
- Record the real-money balance **before** the first spin; it's the baseline for the credit check.
- **Always mute the game sound**: every casino game in every bonus test, including slots, live tables (roulette, blackjack, game shows) and buy-bonus features. Mute on the first screen where the speaker icon is reachable, before any spin or bet, and check it shows as muted. **Pragmatic slots** (e.g. Wolf Gold): the small speaker icon doesn't mute reliably, so open ≡ → Settings and switch off both Ambient Music and Sound FX Muting is a tester setting, not a check, so it gets no screenshot.
- **Always use autoplay and the fastest speed** in every game that has them: autoplay / "Joc automat" / auto-spin, plus turbo / quick spin / fast play / "Joc rapid". Turn them on before the first bonus spin, together with muting (no screenshot of the setup). Keep autoplay from ever running into real money:
  - **Free Spins:** set the autoplay count to at most the spins left. Stop when the bonus counter reaches 0 or the end screen appears.
  - **Countdown:** stop autoplay before the last ~2 min of a long countdown (last ~10 s of one ≤ 2 min) and watch the end manually.
  - **Wagering:** use a high stake so the requirement is covered in about 5–15 spins. Set the count so that count × stake ≤ what's left of `wager_limit` (or spin manually if the autoplay minimum is too high), and recheck `wagered` between batches.
  - **Not available** (e.g. live tables, or a game without autoplay): play manually and say so once in the caveats.
- **Responsible-gaming reality check**: if a "Play paused" / session-time popup appears (e.g. "You are playing for 60 Min … Resume play / Logout"), press **Resume play** and carry on. Never press Logout, and never change limits or any other responsible-gaming setting. Mention the popup once in "Not tested / caveats"; it is not a finding.
- **Exception: Wagering bonuses** are played with the account's real balance by default, without asking. The rules are in `references/wagering.md`. Even then, no deposits, and no bets after `wager_limit` is reached.

## Shared storage and retention
Evidence is stored in a shared Google Drive folder, one subfolder per test named `<bonus name> · <site> · <timestamp>`, and anything older than 5 days is deleted at the start of each run. Read `references/storage.md` at the start of every run (cleanup) and at delivery (upload).

## Evidence screenshots
Every check that ends ✅ or ⚠️ (and ❌) needs a screenshot showing it, because the thread should let a reviewer see what you saw without re-running the test. One screen often proves several checks (e.g. the bonus card proves name + spins + game + expiry), so take one screenshot per screen/moment and map it to the check ids it covers. Take them as you go — the moment can't be re-created later (popup, end screen, balance before/after).
- Use `computer` `screenshot` / `zoom` with `save_to_disk: true`, then copy each file into `<working folder>/casino-bonus-test-<bonus_id>-<YYYY-MM-DD>/screenshots/` named `<NN>-<checks>-<what>.png` (e.g. `03-D2-D5-D7-D8-bonus-card.png`, `09-P3-fs-popup.png`, `22-S1-balance-after.png`).
- Keep it lean: one screenshot per screen, plus one per ⚠️/❌. Skip mid-play counter shots unless something looks off, and read text checks (names, offer details, T&C) with `get_page_text` instead of screenshotting them.
- Minimum set: balance before · bonus card · bonus panel · T&C page · CTA landing page · FS popup · first spin (counter + stake) · last spin · end popup · balance after · bonus gone from active · bonus in history. Add one for every ⚠️/❌ showing exactly the problem.
- Keep an index (file → checks covered) for the report.

## Testing several bonuses in one run
The user can give many bonus ids for the same user (all on production, same market). Do one run, not N: shared work happens once, per-bonus work happens per bonus.
- **Once per run:** input questions, storage cleanup, Phase 0 identity check, opening the site, the Drive run folder.
- **Per bonus:** expected sheet (Phase 1), display checks (Phase 2), play (Phase 3), settlement (Phase 4), check list and verdict. Keep one expected sheet and one result set per bonus id; never merge them.
- **Validate each id up front.** Pull all definitions first. A bonus that is not awarded to this customer, or whose `jurisdiction_domain`/`jurisdiction_brand` doesn't match the market, is marked `BLOCKED` with the reason and skipped; the others continue. Say which ones were skipped before starting to play.
- **Display (Phase 2) in one pass:** open the bonus area once and check every bonus card, panel, T&C link and CTA target in turn. Map each card to its bonus by public name + spins + game, never by position.
- **Play (Phase 3–4) strictly one bonus at a time**, in the order the user gave (or ask if the order matters). Take the real-money balance baseline **right before each bonus's first spin** and the "after" balance once that bonus has finished and settled; the previous bonus's win must already be credited, otherwise the credit check is ambiguous. Never run two bonuses in parallel tabs.
- **Make sure the right bonus is being played.** With several active bonuses, a CTA or game launch can offer a different one. Check that the FS popup (count, stake, game) belongs to the bonus under test; if another bonus's popup appears, dismiss it without playing, note it, and find the correct entry. Attribute backend evidence (`bondet_state`, `gaming_ticker`) to a bonus by its template/free-spin id, not by time alone.
- **A failure in one bonus doesn't stop the run.** Real-money mode or a blocked launch only blocks that bonus's play checks.
- **Evidence:** screenshots are named `<bonus tag>-<NN>-<checks>-<what>` where the bonus tag is the first 8 chars of the bonus id, and everything lives in one run folder (see `storage.md`).
- **Report:** **one separate Slack message per bonus**: each bonus gets its own parent post in the single-bonus format (headline, summary, Needs attention) with its own thread (check list, then screenshots link to that bonus's Drive subfolder). No combined run message.
- **Post each bonus as soon as it is finished, then move to the next.** Don't wait until all bonuses are tested. For each bonus, in the order given: play → settlement checks → write its section of the report → upload its screenshots to its Drive subfolder → post its parent message + check list + screenshots link to the channel → only then start the next bonus. Display checks may still be done in one pass up front, but the post for a bonus always goes out before the next bonus's play starts.

## Bonus type specifics
- **Countdown Free Spins** (`type` = "Countdown Free Spins", time-limited, no spin count): read `references/countdown-free-spins.md` and add its C-checks (pause/leave, return before and after expiry, reload, expiry, settlement). Play with autoplay + turbo, never into real money.

- **Buy Bonus** (`type` = "Buy Bonus", free bonus-buy feature worth `value × feature.price_multiplier`): read `references/buy-bonus.md` and add its B-checks (free buy offered, no real debit, feature at the configured stake, leave/return mid-feature, single use, win to real balance) as area "3. Buy bonus" in the scorecard.

- **Free Chips** (`type` = "Free Chips", `chips` list of value × amount, usually a live table): read `references/free-chips.md`. It uses the standard Free Spins checks with chips for spins, plus the live-table rules: seat first, one click per betting window, never double/split, stop after the last chip.

- **Bonus Funds** (`type` = "Bonus Funds", a bonus balance with no wagering): read `references/bonus-funds.md`. Bets come from the bonus first and wins go straight to cash. Play only the bonus balance, sizing the last bet to what's left, spin manually, and never deposit (press "Joacă oricum" on a deposit prompt).

- **Wagering** (`type` = "Wagering", bonus balance that converts to cash after `reward × wagering_multiplier` is bet): read `references/wagering.md`. Real-money play is the default here, as an exception to the safety rules. Wager with the account's real balance without asking. If the cash is less than the requirement, keep going on the bonus funds once cash hits 0. Ask only if cash is 0 at award: play on bonus funds only, or wait for the user to fund the account. Count wagering progress from `bondet_state.wagered` and `gaming_ticker`, not clicks, and stop as soon as the completion popup appears.

## Workflow

### Phase 0 – Preflight
0. **Check login and IP before anything else.** Open the site and confirm it's logged in. From the bonus definitions, list the providers; if a provider is known to geo-block outside its market (Pragmatic on GR needs a Greek IP; Greentube on RO needs a Romanian IP), ask the user once, at the start, to switch IP. Don't discover it mid-run.
1. Open/identify the tab. If the header shows a sign-in button instead of a username, follow "If the browser is logged out" above and wait for the user. Then confirm the logged-in account is the account for `customer_id`. A Betler UUID maps to exactly one username, so this is a hard check, not a caveat — don't report it as "indirect". Read the username shown in the site header, then in Betler read the customer record (`customer_search`, `_id` = customer_id: `username`, `flags` incl. `TEST_ACCOUNT`) and `customer_attributes` (`real_balance`). Confirm: (a) username matches — the MCP currently returns it **hashed (unsalted SHA-256 does not match; salt unknown)**, so if it's hashed fall back to (b); (b) the header's real balance equals `real_balance` in `customer_attributes` (exact to the cent, read before playing); (c) the account carries the `TEST_ACCOUNT` flag. (b)+(c) together confirm identity; any mismatch → stop and tell the user. Report the result as one line ("Account confirmed: username <shown username>, balance match, TEST_ACCOUNT").
2. Screenshot the starting state and note the real-money balance and bonus balance.

### Phase 1 – Expected values (source of truth = Betler)
(Repeat for every bonus id; build all expected sheets before touching the browser so mismatches in market/award are found first.)
Read `references/config-extraction.md`. Build an **expected sheet**: bonus type, provider/game(s), number of spins, stake per spin, total value, expiry, public/promo name, offer details, T&C URL/text, CTA text + deeplink, popup flag, wagering/redeem rules, and the awarded instance state (`bondet_state`: status, timestamps, template). If the bonus was never awarded to this customer, stop – nothing to test.
Keyed lookups have returned false empties before; use `opensearch_search` with `.keyword` term filters as the default and say when a value couldn't be found rather than guessing.

### Phase 2 – Front-end display
Read `references/test-checklist.md` § Display. Find the bonus in the player's bonus area (My Bonuses / Promotions / banner – wherever it is shown) and for each item compare with the expected sheet: public name, offer details text, FS count, stake, game, expiry, language. Then **click** the T&C link (loads? right content? right language? matches this promo?) and the CTA (lands on the intended game/page? matches the deeplink config?). Open links in a new tab and close it after.

### Phase 3 – Play the bonus
Read `references/test-checklist.md` § Play. Launch via the CTA/bonus entry; verify the FS popup (count, stake, game), click OK, verify the in-game FS counter and stake per spin. **Before the first spin, set the game to its maximum speed (turbo / quick-spin toggle next to the spin button) and mute the sound (speaker icon, bottom right of the game): it shortens the run and avoids noise.** **Don't screenshot these setup steps** (turbo / "Joc rapid", autoplay / "Joc automat" dialog, sound) and never put them in the evidence folder — they're tester settings, not product checks. Then spin until the free spins are exhausted, zooming on the counter/balance bar after each spin (shorter waits are fine on max speed). Don't change any other game setting. Track spin count, stake each spin (sample or every spin if cheap), and total win. Take a screenshot at popup, first spin, last spin, end screen. Console/network logs are **not** a check: read them (`read_console_messages`, `read_network_requests`) only when something visibly breaks — game won't load, popup missing, spin stuck, balance not updating — and add what they show to that finding as the likely cause. They can't see inside the provider's game frame, so an empty log proves nothing.

### Phase 4 – After play
Read `references/test-checklist.md` § Settlement. Check: win credited to the real-money balance (or to bonus/wagering balance if the config says wagering applies – compare with expected), bonus gone from active and present in history with the right status, and cross-check backend (`bondet_state`, `fsinfo_state`/updates, `gaming_ticker` incl. rejected rounds with real wins). Backend can lag a few minutes – retry once before failing.

### Phase 5 – Report
**Fast reporting: write the findings once, as `findings.json`, and let the scripts produce the rest.**
1. Write `<test folder>/findings.json` (schema in `references/report-template.md` → "findings.json"): title, ids, config, result, evidence, the check list per area with a status per check, "Needs attention" items, caveats. This is the only place findings are written by hand.
2. `scripts/contact_sheet.sh <test folder>/screenshots <test folder>/sheets` tiles the screenshots into 1–2 JPEG pages with captions (WARN/FAIL captions in red).
3. Upload to Drive only `sheets/sheet-*.jpg` + `report.md` (storage.md), not each screenshot. Put the folder link in `findings.json` (`drive_url`).
4. `python3 scripts/build_report.py <test folder>/findings.json` writes `report.md`, `slack_parent.md` and `slack_thread.md` (verdict and counts are computed). Post `slack_parent.md`, then `slack_thread.md` as **one** thread reply: it holds the check list, evidence, caveats and the Drive link together.
Re-run step 4 after adding `drive_url` so the report and thread carry the link.

Use `references/report-template.md`. Status per check: ✅ PASS · ❌ FAIL · ⚠️ WARN (works but off/cosmetic) · ⛔ BLOCKED (couldn't test, say why) · ➖ N/A. Each FAIL/WARN gets expected vs observed and a severity (Config miss / Experience miss) plus a screenshot reference. End with an overall verdict (PASS / PASS WITH WARNINGS / FAIL).

For several bonuses, give each its own verdict and add a run-level line (worst verdict wins).

Delivery standard: **summary post, then full details and screenshots in the thread.** Save the report and screenshots in the folder above and tell the user where they are. **Posting to Slack is part of every run:** when each bonus is finished (one bonus at a time in multi-bonus runs, see above), upload its evidence to Drive (storage.md) and post the summary + thread to **the market's channel from the Market rules table** (RO Superbet and RO Napoleon → #ro-automated-bonus-testing `C0CJB87LB47`; GR → #gr-automated-bonus-testing `C0CK8NZR5L1`) without waiting to be asked. A market not in the table has no default channel: ask before posting. Post only a finished bonus (all its checks done). For countdown bonuses, **don't wait the ~10 min for Istoric / `complete`**; do the rest of the settlement checks (balance credit, card gone from Bonusuri, rounds), mark history/backend-final as "known ~10 min delay, not re-checked" and post right away. Only wait if the user asks to re-verify. Only post somewhere else (a DM, another channel) or hold the post if the user says so in that run. If the Slack connector isn't available, say so and leave the report ready to paste. Structure on Slack (see `references/report-template.md`): the **first message holds the headline + summary** (market, ids, config, result, counts, "Needs attention"), and **one thread reply holds the details**: the full check list, evidence, caveats and the Drive link (generated as `slack_thread.md`). The Slack connector can't upload files: the evidence reaches Slack only as the Drive folder link, so never claim screenshots were posted to Slack.

Before listing findings, read `references/known-expected-behaviours.md` and leave out anything on it (owner-confirmed by design).

## Principles
- Compare, don't just look: every numeric/text item has expected vs observed.
- Judge against the **live** config in Betler, not memory or drafts.
- When something is ambiguous (e.g. a rounding display, a label), report it as WARN with evidence rather than silently passing or failing.
- Don't claim a check passed if you couldn't see it; use BLOCKED.
