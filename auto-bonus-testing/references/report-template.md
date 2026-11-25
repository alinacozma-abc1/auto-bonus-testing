# Report template (Slack-ready, light, threaded)

**Standard (Alina, 2026-11-18): summary post, then the full details and the screenshots in the thread.** Every Slack delivery of a test follows it, in a channel or a DM. **Default destination: the market's channel, posted automatically at the end of every run** — Romania (Superbet and Napoleon) → #ro-automated-bonus-testing `C0CJB87LB47`, Greece → #gr-automated-bonus-testing `C0CK8NZR5L1`, Belgium (Napoleon Casino and Sports) → #be-automated-bonus-testing `C0CL3KC996J`, Poland → #pl-automated-bonus-testing `C0CL3KE2GS2`, Serbia → #rs-automated-bonus-testing `C0CL09R1H2R` (Market rules table in SKILL.md); post the parent message, then the check-list reply(ies), then the screenshots reply, in that order.

Goal: readable in 10 seconds, with all detail one click away. The channel shows the **headline + summary** as the first message; the full check list and the screenshots live in the thread.

Save the full report to `casino-bonus-test-<bonus_id>-<YYYY-MM-DD>/report.md` (same folder as `screenshots/`). Slack tool takes standard markdown (`**bold**`, `` `code` ``, `_italic_`, `-` bullets, `1.` numbers).

## Parent message (channel / DM) — headline + summary (keep under ~20 lines)
The summary is what people read, so it is the **first message itself**, not a thread reply. One message, headline line then the block below:
```
🎰 **<bonus public name>** · <market, e.g. superbet.ro> · <✅ PASS | ⚠️ PASS WITH WARNINGS | ❌ FAIL | ⏸ INCOMPLETE>

**Market:** <site> (<country> · <brand>) · **Env:** <env> · <date>
**Bonus id:** `<bonus_id>` · **User id:** `<customer_id>`

**Config:** <N> spins × <stake> · <game> · <expiry>
**Result:** <one sentence: what the player got, e.g. "won 26.00 RON, credited to real balance, bonus moved to history">

Display ✅ 9 · ⚠️ 1   |   Play ✅ 9   |   Settlement ✅ 5

**Needs attention**
1. ⚠️ <short title> — expected <…>, seen <…> _(Config miss | Experience miss | Cosmetic)_
2. ❌ …
```
If nothing needs attention write `**Needs attention:** nothing 🎉`. Leave out anything listed in `known-expected-behaviours.md`.

## Multi-bonus runs (several bonus ids, same user and market)
**One separate Slack message per bonus (Alina, 2026-11-18), posted as soon as that bonus is finished, before the next bonus is played (Alina, 2026-11-24).** Don't post a combined run message and don't hold posts until the whole list is done. For each bonus, in the order given:
1. Parent message in the single-bonus format above (headline with that bonus's verdict, market/env/ids, config, result, counts, Needs attention).
2. Thread reply: that bonus's full check list (format below).
3. Thread reply: screenshots link to that bonus's own Drive subfolder (see `storage.md`).
A bonus skipped as BLOCKED (not awarded, wrong market) still gets its own short message: headline with ⛔ BLOCKED and one line with the reason. Single-bonus runs ignore this section.

## findings.json (input to scripts/build_report.py)
```json
{
  "title": "public name", "site": "superbet.gr", "market": "Greece · Superbet", "date": "YYYY-MM-DD",
  "bonus_id": "...", "instance_id": "...", "user_id": "...",
  "account": "confirmed (how)",
  "config": "one line for Slack", "config_detail": "longer line for report.md (optional)",
  "result": "one sentence: what the player got",
  "timeline": ["awarded 11:54", "first spin 11:59", "complete 11:59"],
  "evidence": "balance before → after · rounds · Betler state",
  "core_blocked": false,
  "areas": [{"name": "Display", "checks": [{"name": "Public name", "status": "pass|warn|fail|blocked", "detail": "optional, report.md only"}]}],
  "needs_attention": [{"status": "warn|fail", "title": "Short title.", "text": "Plain-words sentence (what happens → what Betler expects → player effect).", "severity": "Config miss|Experience miss|Cosmetic"}],
  "caveats": ["..."],
  "drive_url": "https://drive.google.com/drive/folders/...", "screenshots": 12
}
```
Verdict: any `fail` → FAIL; else `core_blocked` → INCOMPLETE; else any `warn` → PASS WITH WARNINGS; else PASS. Check names are plain words, never ids. Leave N/A checks out.

## Thread reply – full check list + screenshots link (ONE reply per bonus, Alina 2026-11-25)
Areas are **numbered** (1. Display, 2. Play, 3. Settlement; 3. Countdown + 4. Settlement for countdown bonuses). Within an area, each status that has checks gets a line with the status word **and** emoji (Passed ✅ · Warning ⚠️ · Failed ❌ · Blocked ⛔), and the check **names** (plain words, not ids) are **bullets** under it, one per line. Skip statuses with no checks.
**Leave an empty line before every status line** (Passed / Warning / Failed / Blocked) that follows a bullet list (Alina, 2026-11-19): Slack otherwise treats the status line as part of the last bullet and indents it.
**Never show Not applicable (➖) on Slack** (Alina, 2026-11-18): no ➖ section in the thread check list and no ➖ count in the summary line. Checks that don't apply are simply left out; if something was skipped on purpose (e.g. no spin after the end, history not re-checked), say it once in "Not tested / caveats".
```
**1. Display**
Passed ✅
- Visible to player
- …

Warning ⚠️
- Stake per spin

**2. Play**
Passed ✅
- Bonus mode
- …

**3. Settlement**
Passed ✅
- Win credited to real balance
- …

**Evidence:** balance <before> → <after> · <N>/<N> rounds finished at <stake>, <N> rejected · Betler: <state, used N/N, won X, payout>
**Account:** confirmed (<how>)
**Not tested / caveats:** <BLOCKED items, anything skipped>
```
Only expand a check into its own line with expected vs observed when it is not ✅ (that goes in "Needs attention" in reply 1).

## Screenshots (now inside the single thread reply)
The Drive link goes at the end of the single thread reply (build_report.py adds it from `drive_url`). The older guidance below still describes the gallery-page option.
The Slack connector can't upload files. First upload everything to the shared Drive folder (see `storage.md`) and post that **Drive folder link** in the thread — it is the primary link because the whole company can open it and it follows the 5-day retention rule. The per-person **gallery page** below is an optional extra (private to its publisher, so keep it second):
1. Generate a single HTML page with the screenshots embedded as data URIs (one card per screenshot: image, number, caption, status badge Passed/Warning/Failed, the checks it covers). Keep it light/dark themed and mobile friendly; title it "Bonus Test Evidence". Python script pattern: read `screenshots/*.jpg`, base64-embed, write HTML to the scratchpad (a reusable generator was used on 2026-11-18; rewrite it if it's gone).
2. Publish it with the Artifact tool (private by default) and post the URL in the thread, noting that the link is private: only the owner and people it is shared with can open it. If the thread's readers aren't the owner, say they need sharing access.
3. Also hand the raw files to the user (SendUserFile, one call listing each file — a folder path is rejected) and keep them in the test folder.
If publishing isn't possible, fall back to a text index of the screenshots by check name:
```
**Screenshots** (one per confirmed point / warning)
1. Bonus card — Visible to player, Public name, Spins, Game, Expiry · `03-D2-D5-D7-D8-bonus-card.png`
2. FS popup — Popup content · `09-P3-fs-popup.png`
3. ⚠️ Bonus panel — Stake per spin not shown · `05-D6-bonus-panel.png`
…
```
Warnings/failures get their own screenshot, marked with the status emoji.

## Rules
- **Write findings in plain words** (Alina, 2026-11-24). Name the exact on-screen element and where it is (e.g. "the green PLAY NOW button on the game's Countdown Free Spins popup", "the Time left timer under the reels"). No jargon: no "HUD", no check ids (C1/C2) in the sentence, no field names unless they're needed as evidence.
  - Shape: what happens → what Betler expects → the effect on the player, with the number.
  - Example: "The game's own Time left timer starts as soon as the player presses PLAY NOW on that popup, even before the first spin. Betler only starts its 60 seconds at the first spin. The game therefore ends the free spins earlier than Betler expects, here about 17 seconds early."
  - Put timestamps and field values on an Evidence line after the sentence, not inside it.
- Counts must equal the number of check rows; findings that are not check rows (e.g. config-vs-T&C mismatches) go under "Needs attention" but are not added to the check counts. State both numbers when they differ ("23 checks passed · 4 findings").
- Never write ✅ for something not directly observed — use ⛔ BLOCKED.
- Verdict: any ❌ → FAIL; no ❌ but any ⚠️ → PASS WITH WARNINGS; else PASS. ⛔ on a core check (P1–P5, S1) → INCOMPLETE.
- Order "Needs attention" by severity: ❌ first, then Config miss, Experience miss, Cosmetic.
- Every ✅/⚠️/❌ must map to at least one screenshot.
- Don't include personal data beyond the customer id.
