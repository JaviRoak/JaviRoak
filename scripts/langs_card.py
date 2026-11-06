"""Genera koi/langs.svg: tarjeta de lenguajes por número de repos (estilo del perfil).

Uso: python3 scripts/langs_card.py <usuario> <salida.svg>
Lee GITHUB_TOKEN del entorno (opcional, evita límites de la API).
"""
import json, os, sys, urllib.request
from html import escape

USER = sys.argv[1] if len(sys.argv) > 1 else "javiroak"
OUT = sys.argv[2] if len(sys.argv) > 2 else "koi/langs.svg"
TOP = 6

COLORS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
    "C#": "#178600", "C++": "#f34b7d", "C": "#555555", "Java": "#b07219",
    "Lua": "#4a5bd4", "Luau": "#00A2FF", "HTML": "#e34c26", "CSS": "#663399",
    "SCSS": "#c6538c", "Rust": "#dea584", "Go": "#00ADD8", "PHP": "#4F5D95",
    "Ruby": "#701516", "Shell": "#89e051", "PowerShell": "#012456",
    "Kotlin": "#A97BFF", "Swift": "#F05138", "Dart": "#00B4AB",
    "Vue": "#41b883", "Svelte": "#ff3e00", "Jupyter Notebook": "#DA5B0B",
    "GDScript": "#355570", "ShaderLab": "#222c37", "HLSL": "#aace60",
    "Dockerfile": "#384d54", "Makefile": "#427819", "Batchfile": "#C1F12E",
    "Visual Basic .NET": "#945db7", "SQL": "#e38c00", "TSQL": "#e38c00",
}
OTHER = "#6e7681"


def fetch_counts(user):
    counts, page = {}, 1
    token = os.environ.get("GITHUB_TOKEN")
    while True:
        req = urllib.request.Request(
            f"https://api.github.com/users/{user}/repos?per_page=100&type=owner&page={page}",
            headers={"Accept": "application/vnd.github+json", "User-Agent": "langs-card"},
        )
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        repos = json.load(urllib.request.urlopen(req))
        if not repos:
            break
        for r in repos:
            if r.get("fork") or not r.get("language"):
                continue
            counts[r["language"]] = counts.get(r["language"], 0) + 1
        page += 1
    return counts


def render(counts):
    total = sum(counts.values()) or 1
    items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    if len(items) > TOP:
        rest = sum(n for _, n in items[TOP - 1:])
        items = items[:TOP - 1] + [("Other", rest)]

    W, H, PAD = 360, 256, 22
    bar_y, bar_w, bar_h = 64, W - 2 * PAD, 10
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        '<style>text{font-family:"Segoe UI",Ubuntu,"Helvetica Neue",Arial,sans-serif}</style>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="#141414" stroke="#222222"/>',
        f'<text x="{PAD}" y="42" font-size="18" font-weight="600" fill="#F0A020">Languages</text>',
        f'<text x="{W-PAD}" y="42" font-size="12" fill="#666666" text-anchor="end">by repo count</text>',
        f'<clipPath id="b"><rect x="{PAD}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="5"/></clipPath>',
        '<g clip-path="url(#b)">',
    ]
    x = PAD
    for i, (name, n) in enumerate(items):
        w = bar_w * n / total if i < len(items) - 1 else PAD + bar_w - x
        col = COLORS.get(name, OTHER)
        out.append(f'<rect x="{x:.2f}" y="{bar_y}" width="{w + 0.5:.2f}" height="{bar_h}" fill="{col}"/>')
        x += w
    out.append("</g>")

    col_x = [PAD, PAD + bar_w / 2 + 6]
    for i, (name, n) in enumerate(items):
        cx, cy = col_x[i % 2], 108 + (i // 2) * 44
        pct = 100 * n / total
        out += [
            f'<circle cx="{cx + 6}" cy="{cy - 4}" r="6" fill="{COLORS.get(name, OTHER)}"/>',
            f'<text x="{cx + 20}" y="{cy}" font-size="14" fill="#ffffff">{escape(name)}</text>',
            f'<text x="{cx + 20}" y="{cy + 18}" font-size="12" fill="#cccccc">{pct:.0f}% · {n} repo{"s" if n != 1 else ""}</text>',
        ]
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    counts = json.loads(os.environ["DEMO_COUNTS"]) if os.environ.get("DEMO_COUNTS") else fetch_counts(USER)
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(counts))
    print(f"{OUT}: {counts}")
