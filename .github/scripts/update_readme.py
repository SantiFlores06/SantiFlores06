"""Refresh the auto-generated "Latest activity" block in README.md from the
owner's public repositories. Standard library only."""
import json
import os
import re
import sys
import urllib.request

OWNER = "SantiFlores06"
MAX_ITEMS = 6
START, END = "<!-- AUTO-REPOS:START -->", "<!-- AUTO-REPOS:END -->"


def fetch_repos():
    req = urllib.request.Request(
        f"https://api.github.com/users/{OWNER}/repos?per_page=100&type=owner",
        headers={"Accept": "application/vnd.github+json"},
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def build_block(repos):
    own = [
        r for r in repos
        if not r["fork"] and not r["archived"] and r["name"].lower() != OWNER.lower()
    ]
    own.sort(key=lambda r: r["pushed_at"], reverse=True)
    lines = ["| Repository | Description | Language | Last push |", "|---|---|---|---|"]
    for r in own[:MAX_ITEMS]:
        desc = (r["description"] or "—").replace("|", "\\|")
        lang = r["language"] or "—"
        lines.append(f"| [{r['name']}]({r['html_url']}) | {desc} | {lang} | {r['pushed_at'][:10]} |")
    return "\n".join(lines)


def main():
    repos = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else fetch_repos()
    text = open("README.md", encoding="utf-8").read()
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        sys.exit("Markers not found in README.md")
    new = pattern.sub(lambda _: f"{START}\n{build_block(repos)}\n{END}", text)
    open("README.md", "w", encoding="utf-8").write(new)


if __name__ == "__main__":
    main()
