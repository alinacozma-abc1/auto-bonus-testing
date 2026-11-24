# Shared evidence storage (Google Drive)

The skill is shared across the team and tests run on many machines, so screenshots and reports must not live only on the tester's disk. Everything goes to **one shared Google Drive folder**, readable by the whole company, with a **5-day retention rule**. Decided by Alina, 2026-11-18.

## Where
- Root folder: **Bonus Test Evidence** — id `1MFbXCSDo-0ITXi3ZNYtLwav8LeXjsj8Z` (https://drive.google.com/drive/folders/1MFbXCSDo-0ITXi3ZNYtLwav8LeXjsj8Z), owned by alina.cozma@super.xyz.
- Uses the Google Drive connector (`create_file`, `search_files`, `trash_file`, `get_file_metadata`). If the connector isn't available on the tester's machine, keep the local folder, say so in the report, and skip the Drive steps.

## Access (one-time setup, done by the folder owner in the Drive UI)
- Readers: **whole company** — Share → General access → Superbet → Viewer. The connector's `share_file` cannot grant company-wide access (no domain audience id), so this can't be done from the skill. Subfolders inherit it.
- Editors: every teammate who runs the skill needs **Editor** on the root folder (or membership in a group that has it), otherwise uploads fail. If an upload returns a permission error, tell the user to ask the folder owner for edit access — don't work around it.
- Long term, moving the root into a team-owned Shared Drive is safer than a personal My Drive (it survives the owner leaving). Ask the owner before moving.

## Folder structure and naming
One subfolder per test, directly under the root:
`<bonus public name> · <site> · <YYYY-MM-DD HH-mm>` — e.g. `32 Rotiri Gratuite 5 Dazzling Hot · superbet.ro · 2026-11-18 10-27`
- Bonus name = the public name from Betler (`public_names`), falling back to the bonus id if it's missing.
- Timestamp = when the test started, in the tester's local time, 24h, with `-` between hour and minute (no `:` or `/` in folder names).
**Several bonuses in one run:** still one folder per run. Name it `Bonus test · <N> bonuses · <site> · <YYYY-MM-DD HH-mm>`, and inside create one subfolder per bonus named `<bonus public name> · <first 8 chars of bonus id>`; each subfolder holds that bonus's screenshots, the run folder holds one `report.md` covering all. Retention applies to the run folder (subfolders go with it). Each bonus's Slack message links its own subfolder, not the run folder. Shared screenshots (e.g. balance at start, bonus area overview) go in the run folder root.
Inside a single-bonus folder: `01-…jpg` … `NN-…jpg` (screenshots named `<NN>-<checks>-<what>.jpg`, with `FAIL`/`WARN` in the name for those) and `report.md`.

## Retention: delete after 5 days
Drive has no auto-delete, so the skill enforces it. **At the start of every run** (before creating the new folder):
1. `search_files` with `parentId = '<root id>' and mimeType = 'application/vnd.google-apps.folder' and createdTime < '<now minus 5 days, RFC 3339 UTC>'` (page through all results).
2. `trash_file` each result. Report how many were removed in one line.
3. Never touch anything outside the root folder, and never delete the root itself or a folder younger than 5 days.
Trashed items are purged by Drive after 30 days; the owner can empty the trash for an immediate hard delete. A daily sweep also runs the same query on Alina's machine (scheduled task `bonus-test-evidence-sweep`, every day ~07:14 local, runs while the Claude app is open, otherwise on next launch), so old folders go even when nobody runs the skill. It is a personal task: teammates don't get it by installing the skill, and it stops if Alina's app is off for days — the per-run cleanup is the real guarantee.

## Upload
1. `create_file` with `mimeType: application/vnd.google-apps.folder`, `parentId: <root id>`, `title:` the folder name above.
2. For each screenshot: `create_file` with `parentId: <new folder id>`, `contentMimeType: image/jpeg`, `disableConversionToGoogleType: true`, and `base64Content` set to the file reference `sha256:<64-hex>:<absolute path>` (get the hash with `shasum -a 256`). Each upload is approved by the user; send them in one parallel block.
3. Upload `report.md` (`text/markdown`, `disableConversionToGoogleType: true`).
4. The folder link is `https://drive.google.com/drive/folders/<new folder id>` — post it in the Slack thread.
