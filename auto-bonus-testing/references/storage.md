# Shared evidence storage (Google Drive)

Screenshots and reports must not live only on the tester's disk, because tests run on many machines. Everything goes to **one team Shared Drive folder** with a **5-day retention rule**.

## Where
- Root folder: **Automated Bonus Tests** (team Shared Drive), id `1FiKRXzJEqRiuw14374IGedd09i4gDZWQ`, https://drive.google.com/drive/folders/1FiKRXzJEqRiuw14374IGedd09i4gDZWQ
- Uses the Google Drive connector (`create_file`, `search_files`, `trash_file`, `get_file_metadata`). If the connector isn't available on the tester's machine, keep the local folder, say so in the report, and skip the Drive steps.

## Access
- The folder lives in a team Shared Drive, so it doesn't depend on one person's account. Anyone who runs the skill must be a member of that Shared Drive with at least **Contributor** (to upload) and **Content manager** (to move old test folders to trash) rights. Readers of the Slack posts need at least Viewer.
- If an upload or a cleanup returns a permission error, tell the user to ask a Shared Drive manager for access. Don't work around it, and don't fall back to a personal My Drive folder.

## Folder structure and naming
One subfolder per test, directly under the root:
`<bonus public name> · <site> · <YYYY-MM-DD HH-mm>`, e.g. `32 Rotiri Gratuite 5 Dazzling Hot · superbet.ro · 2026-11-18 10-27`
- Bonus name = the public name from Betler (`public_names`), falling back to the bonus id if it's missing.
- Timestamp = when the test started, in the tester's local time, 24h, with `-` between hour and minute (no `:` or `/` in folder names).

**Several bonuses in one run:** one folder per run, named `Bonus test · <N> bonuses · <site> · <YYYY-MM-DD HH-mm>`, with one subfolder per bonus named `<bonus public name> · <first 8 chars of bonus id>`. Shared evidence (balance at start, award popups, bonus area overview) goes in the run folder root. Each bonus's Slack thread links its own subfolder. Retention applies to the run folder (subfolders go with it).

A single-bonus folder holds the contact sheets (`sheet-1.jpg`, …) and `report.md`.

## Retention: delete after 5 days
Drive has no auto-delete, so the skill enforces it. **At the start of every run**, before creating the new folder:
1. `search_files` with `parentId = '<root id>' and mimeType = 'application/vnd.google-apps.folder' and createdTime < '<now minus 5 days, RFC 3339 UTC>'` (page through all results).
2. `trash_file` each result. Report how many were removed in one line.
3. Never touch anything outside the root folder, and never delete the root itself or a folder younger than 5 days.

Trashed items in a Shared Drive are purged by Drive after 30 days. A Shared Drive manager can empty the trash sooner.

## Upload
1. `create_file` with `contentMimeType: application/vnd.google-apps.folder`, `parentId: <root id>`, `title:` the folder name above.
2. **Upload the contact sheets, not every screenshot:** run `scripts/contact_sheet.sh <test folder>/screenshots <test folder>/sheets` and upload each `sheets/sheet-N.jpg`. Keep the individual screenshots locally; upload one separately only if a reviewer needs it full size. If the contact-sheet script fails (it reports an error), upload the individual screenshots instead and say so once in the caveats. Upload method for each file: `create_file` with `parentId: <new folder id>`, `contentMimeType: image/jpeg` (or `image/png`), `disableConversionToGoogleType: true`, and `base64Content` set to the file reference `sha256:<64-hex>:<absolute path>` (get the hash with `shasum -a 256`). Send the uploads in one parallel block.
3. Upload `report.md` (`text/markdown`, `disableConversionToGoogleType: true`).
4. The folder link is `https://drive.google.com/drive/folders/<new folder id>`; put it in `findings.json` (`drive_url`) so it lands in the Slack thread.
