"""生成 assets/langs.svg —— 主页那张深色数据卡。

数据全部来自 GitHub 公开 API（仓库列表 / 语言字节数 / 用户信息），
由 .github/workflows/langs.yml 每 6 小时跑一次，删库加库都会自动更新。
本地手动跑：GITHUB_TOKEN=xxx python tools/build_langs.py
"""

import json
import os
import urllib.request
from datetime import datetime, timezone

USER = "liubaibuliuyan"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "langs.svg")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

COLORS = {
    "Astro": "#ff5d01", "CSS": "#663399", "HTML": "#e34c26", "Python": "#3572a5",
    "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "C": "#555555", "C++": "#f34b7d",
    "C#": "#178600", "Vue": "#41b883", "Shell": "#89e051", "Java": "#b07219",
    "Go": "#00add8", "Rust": "#dea584", "Jupyter Notebook": "#da5b0b", "SCSS": "#c6538c",
    "Makefile": "#427819", "CMake": "#da3434", "Assembly": "#6e4c13", "Batchfile": "#c1f12e",
}
FALLBACK = ["#7d8792", "#9aa4ae", "#5c6772", "#b3bcc5", "#6e7b88", "#8b959e"]


def get(url):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "liubaibuliuyan-profile-card",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def collect():
    user = get(f"https://api.github.com/users/{USER}")

    repos, page = [], 1
    while True:
        batch = get(f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}&sort=updated")
        if not batch:
            break
        repos += [r for r in batch if not r.get("fork") and not r.get("archived")]
        if len(batch) < 100:
            break
        page += 1

    langs = {}
    for repo in repos:
        try:
            for name, size in get(repo["url"] + "/languages").items():
                langs[name] = langs.get(name, 0) + size
        except Exception:
            continue
    return user, repos, langs


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render(user, repos, langs):
    stars = sum(r.get("stargazers_count", 0) for r in repos)
    since = (user.get("created_at") or "2025")[:4]
    today = datetime.now(timezone.utc).strftime("%Y.%m.%d")

    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:5]
    pct = {k: v / total * 100 for k, v in top}

    # 语言细条：总宽 734，段间留 2px
    bar, cursor, gap = [], 48, 2
    avail = 734 - gap * max(0, len(top) - 1)
    for i, (name, _) in enumerate(top):
        w = max(6, round(pct[name] / 100 * avail))
        bar.append(f'      <rect x="{cursor}" y="176" width="{w}" height="6" rx="3" fill="{COLORS.get(name, FALLBACK[i % 6])}"/>')
        cursor += w + gap
    bar = "\n".join(bar) or '      <rect x="48" y="176" width="734" height="6" rx="3" fill="#2a333c"/>'

    legend = " · ".join(f"{esc(n)} {pct[n]:.1f}%" for n, _ in top[:3]) or "还没有公开代码"

    def stat(x, value, label):
        return (f'      <text x="{x}" y="112" font-family="\'Segoe UI\',Inter,Arial,sans-serif" '
                f'font-size="32" font-weight="600" fill="#e6edf3">{value}</text>\n'
                f'      <text x="{x}" y="134" font-family="ui-monospace,Consolas,monospace" '
                f'font-size="10" letter-spacing="2.2" fill="#6e7b88">{label}</text>')

    stats = "\n".join([
        stat(48, len(repos), "REPOSITORIES"),
        stat(246, stars, "STARS"),
        stat(444, user.get("followers", 0), "FOLLOWERS"),
        stat(642, since, "SINCE"),
    ])

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="830" height="230" viewBox="0 0 830 230" role="img" aria-label="GitHub overview">
  <defs>
    <linearGradient id="bg2" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0b0f14"/>
      <stop offset="100%" stop-color="#141c24"/>
    </linearGradient>
    <pattern id="grid2" width="22" height="22" patternUnits="userSpaceOnUse">
      <path d="M22 0H0V22" fill="none" stroke="#ffffff" stroke-width="1" opacity="0.03"/>
    </pattern>
    <clipPath id="card2"><rect width="830" height="230" rx="14"/></clipPath>
  </defs>

  <g clip-path="url(#card2)">
    <rect width="830" height="230" fill="url(#bg2)"/>
    <rect width="830" height="230" fill="url(#grid2)"/>

    <text x="48" y="52" font-family="ui-monospace,Consolas,Menlo,monospace" font-size="10.5" letter-spacing="3" fill="#6e7b88">GITHUB OVERVIEW</text>

{stats}

    <line x1="48" y1="158" x2="782" y2="158" stroke="#ffffff" stroke-width="1" opacity="0.07"/>
{bar}

    <text x="48" y="212" font-family="'Segoe UI',Inter,Arial,sans-serif" font-size="12.5" fill="#8b959e">{legend}</text>
    <text x="782" y="212" text-anchor="end" font-family="ui-monospace,Consolas,Menlo,monospace" font-size="9.5" letter-spacing="1.6" fill="#4b5563">UPDATED {today}</text>
  </g>
</svg>
'''


def main():
    user, repos, langs = collect()
    svg = render(user, repos, langs)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print("written", OUT, "|", len(repos), "repos |", len(langs), "languages")


if __name__ == "__main__":
    main()
