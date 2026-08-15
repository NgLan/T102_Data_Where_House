#!/usr/bin/env python3
"""
Codex CLI log scanner — extracts exact user-typed prompts from local Codex session files.

Source of truth:
    ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl

Each rollout file is JSON Lines containing turn_context, event_msg, and response_item.
We emit one log entry per user message where `payload.type == "user_message"`.
If the user message references pasted attachments in ~/.codex/attachments/..., we extract
the text from the attachment file.

Conversation -> repo mapping:
---------------------------
Each turn_context entry contains `cwd` and `workspace_roots`. We map a session to the
current repo when its cwd matches (equals, is ancestor, or descendant of) the current repo root.

Usage:
  python scripts/log_codex.py --auto            # default: last 24h
  python scripts/log_codex.py --hours 72
  python scripts/log_codex.py --all             # every session, no cutoff
  python scripts/log_codex.py --dry-run         # preview only

Env overrides:
  CODEX_SESSIONS_DIR  point at a different sessions/ directory
  AI_LOG_DIR          where session.jsonl is written (default: .ai-log)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Fix Windows console encoding so VN diacritics in prompts print cleanly.
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

VN_TZ = timezone(timedelta(hours=7))
CODEX_HOME = Path.home() / ".codex"
SESSIONS_DIR = CODEX_HOME / "sessions"

PASTED_TXT_RE = re.compile(r"([A-Za-z]:\\[^\n:]+pasted-text\.txt|/[^\n:]+pasted-text\.txt)")


def git(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd.split(), shell=False, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def get_sessions_dir() -> Path | None:
    env = os.environ.get("CODEX_SESSIONS_DIR")
    if env:
        p = Path(env)
        return p if p.exists() else None
    return SESSIONS_DIR if SESSIONS_DIR.exists() else None


def _normalize(p: str) -> str:
    if not p:
        return ""
    return p.strip().lower().replace("/", "\\").rstrip("\\")


def _cwd_matches_repo(cwd: str, repo_root_n: str) -> bool:
    if not repo_root_n or not cwd:
        return False
    cwd_n = _normalize(cwd)
    if cwd_n == repo_root_n:
        return True
    if cwd_n.startswith(repo_root_n + "\\"):
        return True
    if repo_root_n.startswith(cwd_n + "\\"):
        return True
    return False


def clean_prompt_text(raw_text: str) -> str:
    if not raw_text:
        return ""
    # If the text mentions a pasted-text file attachment, try reading it
    m = PASTED_TXT_RE.search(raw_text)
    if m:
        att_path = Path(m.group(1))
        if att_path.exists():
            try:
                attached_content = att_path.read_text(encoding="utf-8", errors="replace").strip()
                if len(attached_content) > 1:
                    return attached_content
            except Exception:
                pass

    # Strip standard wrapper text if present
    lines = raw_text.splitlines()
    filtered_lines = []
    skip_mode = False
    for line in lines:
        if line.startswith("# Files pasted by the user:") or line.startswith("# Files mentioned by the user:"):
            skip_mode = True
            continue
        if line.startswith("## My request:"):
            skip_mode = False
            continue
        if skip_mode and (line.startswith("## ") or line.startswith("Pasted text contains")):
            continue
        if not skip_mode:
            filtered_lines.append(line)

    result = "\n".join(filtered_lines).strip()
    return result if result else raw_text.strip()


def get_logged_entry_ids(log_file: Path) -> set[str]:
    logged: set[str] = set()
    if not log_file.exists():
        return logged
    with open(log_file, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            eid = entry.get("entry_id", "")
            if eid:
                logged.add(eid)
    return logged


def iter_codex_prompts(sessions_dir: Path, cutoff: datetime | None, repo_root_n: str):
    """Yield dicts for every user prompt found in matching Codex session files."""
    for root, _, files in os.walk(sessions_dir):
        for file in sorted(files):
            if not (file.startswith("rollout-") and file.endswith(".jsonl")):
                continue
            filepath = Path(root) / file
            session_id = file.replace("rollout-", "").replace(".jsonl", "").split("-")[-1]

            cwd = ""
            model = ""
            turn_id = ""
            step_idx = 0

            with open(filepath, encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    t = data.get("type")
                    if t == "turn_context":
                        payload = data.get("payload", {})
                        cwd = payload.get("cwd", "")
                        model = payload.get("model", "")
                        turn_id = payload.get("turn_id", "")
                    elif t == "event_msg":
                        payload = data.get("payload", {})
                        msg_type = payload.get("type")
                        if msg_type == "user_message":
                            raw_msg = payload.get("message", "")
                            # Skip internal agent auto-review system messages
                            if (
                                "[codex-auto-review]" in raw_msg
                                or "The following is the Codex agent history" in raw_msg
                                or "Continue the same review conversation" in raw_msg
                            ):
                                continue

                            ts_str = data.get("timestamp", "")
                            if cutoff and ts_str:
                                try:
                                    ts_dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                                    if ts_dt < cutoff:
                                        continue
                                except ValueError:
                                    pass

                            if repo_root_n and not _cwd_matches_repo(cwd, repo_root_n):
                                continue

                            text = clean_prompt_text(raw_msg)
                            if len(text) < 2:
                                continue

                            step_idx += 1
                            suffix = turn_id if turn_id else f"{step_idx:03d}"
                            entry_id = f"codex-{session_id}-{suffix}"

                            yield {
                                "session_id": session_id,
                                "turn_id": turn_id,
                                "entry_id": entry_id,
                                "timestamp": ts_str,
                                "model": model,
                                "text": text,
                                "cwd": cwd,
                            }


def build_entry(msg: dict, repo: str, branch: str, commit: str, student: str) -> dict:
    ts = msg["timestamp"]
    if ts and ts.endswith("Z"):
        try:
            ts = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(VN_TZ).isoformat()
        except ValueError:
            pass

    return {
        "ts": ts or datetime.now(VN_TZ).isoformat(),
        "tool": "codex",
        "event": "UserPrompt",
        "entry_id": msg["entry_id"],
        "session_id": msg["session_id"],
        "model": msg["model"] or "codex",
        "repo": repo,
        "branch": branch,
        "commit": commit,
        "student": student,
        "prompt": msg["text"],
        "response_summary": "",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract user prompts from Codex CLI transcripts into .ai-log/session.jsonl."
    )
    parser.add_argument("--auto", action="store_true", help="Default mode: scan recent sessions.")
    parser.add_argument("--hours", type=int, default=24, help="Window in hours when scanning (default: 24).")
    parser.add_argument("--all", action="store_true", help="Ignore time window; scan everything.")
    parser.add_argument("--no-repo-filter", action="store_true", help="Don't filter sessions by current repo.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be logged, don't write.")
    args = parser.parse_args()

    sessions_dir = get_sessions_dir()
    if not sessions_dir:
        print(f"[codex-log] No Codex sessions directory found at {SESSIONS_DIR}.", file=sys.stderr)
        sys.exit(0)

    log_dir = Path(os.environ.get("AI_LOG_DIR", ".ai-log"))
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "session.jsonl"
    logged_ids = get_logged_entry_ids(log_file)

    cutoff = None
    if not args.all:
        cutoff = datetime.now(tz=VN_TZ) - timedelta(hours=args.hours)

    repo_root_n = "" if args.no_repo_filter else _normalize(str(Path.cwd()))

    repo = git("git remote get-url origin").split("/")[-1].replace(".git", "")
    branch = git("git rev-parse --abbrev-ref HEAD")
    commit = git("git rev-parse --short HEAD")
    student = git("git config user.email") or os.environ.get("USERNAME", os.environ.get("USER", "unknown"))

    new_entries = []
    for msg in iter_codex_prompts(sessions_dir, cutoff, repo_root_n):
        entry = build_entry(msg, repo or Path.cwd().name, branch, commit, student)
        if entry["entry_id"] in logged_ids:
            continue
        new_entries.append(entry)
        logged_ids.add(entry["entry_id"])

    if not new_entries:
        scope = "all" if args.all else f"{args.hours}h"
        repo_note = "any repo" if args.no_repo_filter else f"repo={repo_root_n or '(unknown)'}"
        print(f"[codex-log] No new prompts ({repo_note}, window={scope}).", file=sys.stderr)
        sys.exit(0)

    if args.dry_run:
        print(f"\n[codex-log] DRY RUN — would log {len(new_entries)} entries:\n")
        for e in new_entries:
            preview = e["prompt"].replace("\n", " ")[:120]
            print(f"  [{e['ts'][:19]}] {preview}")
        sys.exit(0)

    with open(log_file, "a", encoding="utf-8") as f:
        for e in new_entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

    print(f"[codex-log] Logged {len(new_entries)} prompt(s) from Codex CLI.", file=sys.stderr)


if __name__ == "__main__":
    main()
