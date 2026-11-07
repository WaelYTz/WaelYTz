"""Playable profile encounter: a visitor clicks FIGHT / ACT / ITEM / MERCY in the README, which opens an issue titled
"encounter|<action>". This script (run by the cards workflow on `issues: opened`) counts the action in
data/encounter.json, replies in Undertale style and closes the issue. The cards step then redraws the encounter box.

Only issues whose title is exactly "encounter|fight|act|item|mercy" are handled; anything else is left untouched.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import urllib.request
from pathlib import Path

STATE = Path("data/encounter.json")
REPLIES = {
    "fight": "* You attacked WAEL.\n* ...\n* But WAEL's SOUL refused to shatter.\n\n> Technoblade never dies.",
    "act": "* You checked WAEL.\n* WAEL - AT 99 DF 99\n* Trains ML models. Builds AI agents. Stays determined.",
    "item": "* You offered WAEL a cup of coffee.\n* WAEL's productivity went up!",
    "mercy": "* You spared WAEL. ❤\n* WAEL won't forget your kindness.",
}


def api(method: str, url: str, payload: dict) -> None:
    req = urllib.request.Request(url, method=method, data=json.dumps(payload).encode(),
                                 headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
                                          "Accept": "application/vnd.github+json", "User-Agent": "profile-encounter"})
    with urllib.request.urlopen(req, timeout=30):
        pass


def load() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"fight": 0, "act": 0, "item": 0, "mercy": 0, "last": None, "recent": []}


def main() -> None:
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    issue = event.get("issue") or {}
    title = (issue.get("title") or "").strip().lower()
    if not title.startswith("encounter|"):
        print("not an encounter issue; nothing to do")
        return
    action = title.split("|", 1)[1].strip()
    if action not in REPLIES:
        print(f"unknown action {action!r}; ignored")
        return
    user = issue["user"]["login"]
    st = load()
    st[action] = st.get(action, 0) + 1
    entry = {"user": user, "action": action, "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    st["last"] = entry
    st["recent"] = ([entry] + st.get("recent", []))[:8]
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(st, indent=2) + "\n", encoding="utf-8")

    repo, num = os.environ["GITHUB_REPOSITORY"], issue["number"]
    tally = f"FIGHT {st['fight']} · ACT {st['act']} · ITEM {st['item']} · MERCY {st['mercy']}"
    body = (f"```\n{REPLIES[action]}\n```\n\n<sub>{tally} · the profile updates in about a minute. "
            f"Thanks for playing, @{user}!</sub>")
    api("POST", f"https://api.github.com/repos/{repo}/issues/{num}/comments", {"body": body})
    api("PATCH", f"https://api.github.com/repos/{repo}/issues/{num}", {"state": "closed", "state_reason": "completed"})
    print(f"{user} chose {action}; {tally}")


if __name__ == "__main__":
    main()
