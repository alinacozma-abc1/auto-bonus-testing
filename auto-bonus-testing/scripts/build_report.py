#!/usr/bin/env python3
"""Build report.md + the Slack summary + the Slack thread reply from one findings.json.

Usage: python3 build_report.py findings.json [out_dir]
Writes report.md, slack_parent.md, slack_thread.md into out_dir (default: next to findings.json).
Standard library only. Schema: see references/report-template.md ("findings.json").
"""
import json, os, sys

EMOJI = {"pass": "✅", "warn": "⚠️", "fail": "❌", "blocked": "⛔"}
WORD = {"pass": "Passed", "warn": "Warning", "fail": "Failed", "blocked": "Blocked"}
ORDER = ["pass", "warn", "fail", "blocked"]


def verdict(f):
    sts = [c["status"] for a in f["areas"] for c in a["checks"]]
    if "fail" in sts:
        return "❌ FAIL"
    if f.get("core_blocked"):
        return "⏸ INCOMPLETE"
    if "warn" in sts or any(n.get("status") == "warn" for n in f.get("needs_attention", [])):
        return "⚠️ PASS WITH WARNINGS"
    return "✅ PASS"


def counts(area):
    out = []
    for s in ORDER:
        n = sum(1 for c in area["checks"] if c["status"] == s)
        if n:
            out.append(f"{EMOJI[s]} {n}")
    return f"{area['name']} " + " · ".join(out)


def needs_lines(f, md_bold=True):
    items = f.get("needs_attention", [])
    if not items:
        return ["**Needs attention:** nothing 🎉"]
    lines = ["**Needs attention**"]
    for i, n in enumerate(items, 1):
        sev = f" _({n['severity']})_" if n.get("severity") else ""
        lines.append(f"{i}. {EMOJI.get(n.get('status', 'warn'), '⚠️')} **{n['title']}** {n['text']}{sev}")
    return lines


def slack_parent(f, v):
    head = f"🎰 **{f['title']}** · {f['site']} · {v}"
    ids = f"**Bonus id:** `{f['bonus_id']}` · **User id:** `{f['user_id']}`"
    lines = [head, "",
             f"**Market:** {f['site']} ({f['market']}) · **Env:** prod · {f['date']}",
             ids, "",
             f"**Config:** {f['config']}",
             f"**Result:** {f['result']}", "",
             "   |   ".join(counts(a) for a in f["areas"]), ""]
    lines += needs_lines(f)
    return "\n".join(lines) + "\n"


def slack_thread(f):
    lines = []
    for i, a in enumerate(f["areas"], 1):
        lines.append(f"**{i}. {a['name']}**")
        first = True
        for s in ORDER:
            names = [c["name"] for c in a["checks"] if c["status"] == s]
            if not names:
                continue
            if not first:
                lines.append("")  # blank line before every status line after a list
            lines.append(f"{WORD[s]} {EMOJI[s]}")
            lines += [f"- {n}" for n in names]
            first = False
        lines.append("")
    lines.append(f"**Evidence:** {f['evidence']}")
    lines.append(f"**Account:** {f['account']}")
    cav = f.get("caveats", [])
    if cav:
        lines.append("**Not tested / caveats:**")
        lines += [f"- {c}" for c in cav]
    if f.get("drive_url"):
        n = f.get("screenshots")
        lines += ["", f"**Screenshots**{f' ({n})' if n else ''}, in the shared Drive folder, kept 5 days: {f['drive_url']}"]
    return "\n".join(lines) + "\n"


def report_md(f, v):
    lines = [f"# {f['title']} · {f['site']} · {f['date']}", "",
             f"Market: {f['site']} ({f['market']}) · Env: prod",
             f"Bonus id: {f['bonus_id']}" + (f" (instance {f['instance_id']})" if f.get("instance_id") else "") + f" · User id: {f['user_id']}",
             f"Account: {f['account']}",
             f"Type: {f.get('config_detail', f['config'])}"]
    if f.get("timeline"):
        lines.append("Timeline (UTC): " + " · ".join(f["timeline"]))
    lines += ["", f"Result: {f['result']}", f"Evidence: {f['evidence']}", "",
              f"## Verdict: {v.split(' ', 1)[1]}", "",
              "| Area | Passed | Warning | Failed | Blocked |", "|---|---|---|---|---|"]
    for a in f["areas"]:
        c = [sum(1 for x in a["checks"] if x["status"] == s) for s in ORDER]
        lines.append(f"| {a['name']} | " + " | ".join(map(str, c)) + " |")
    lines += [""] + [l.replace("**Needs attention**", "## Needs attention") for l in needs_lines(f)] + [""]
    for a in f["areas"]:
        lines.append(f"## {a['name']}")
        for c in a["checks"]:
            d = f": {c['detail']}" if c.get("detail") else ""
            lines.append(f"- {EMOJI[c['status']]} {c['name']}{d}")
        lines.append("")
    if f.get("caveats"):
        lines.append("## Not tested / caveats")
        lines += [f"- {c}" for c in f["caveats"]] + [""]
    lines += ["## Evidence", f"{f.get('screenshots', '')} screenshots in `screenshots/` (contact sheets in `sheets/`)." if f.get("screenshots") else "See `screenshots/`."]
    return "\n".join(lines) + "\n"


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(src))
    f = json.load(open(src))
    v = verdict(f)
    for name, text in [("report.md", report_md(f, v)), ("slack_parent.md", slack_parent(f, v)), ("slack_thread.md", slack_thread(f))]:
        with open(os.path.join(out, name), "w") as fh:
            fh.write(text)
    print(f"{v} · wrote report.md, slack_parent.md, slack_thread.md to {out}")


if __name__ == "__main__":
    main()
