"""生成 Credly 徽章统计卡（nord 配色，完全自建，不依赖任何第三方图床服务）。

为什么自建：
  第三方徽章服务（credly-readme-stats 之类）必须把 **Credly 用户名写进图片 URL**，
  公开主页上就等于把账号名（往往是真名拼音）贴出来了。自建卡片把数据取回来、
  把徽章 PNG 存进仓库、主页直接引用（SVG 卡片已弃用）：
    · 公开页面里没有任何第三方 URL / 用户名
    · 不依赖第三方服务的可用性（那些免费实例会冷启动、会限流，主页会变破图）
    · 配色与主页其它元素统一（nord）

用法：
    python tools/gen_credly_card.py                     # 用户名取环境变量 CREDLY_USER
    CREDLY_USER=someone python tools/gen_credly_card.py

输出：
    assets/credly-badges.svg

CI 里通过仓库 Secret `CREDLY_USER` 传入，Secret 不会出现在公开仓库里。
"""

from __future__ import annotations

import base64
import json
import os
import sys
import urllib.error
import re
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

NORD = {
    "bg": "#2E3440", "panel": "#3B4252", "panel2": "#434C5E",
    "text": "#ECEFF4", "muted": "#D8DEE9", "dim": "#81A1C1",
    "accent": "#88C0D0", "accent2": "#5E81AC", "green": "#A3BE8C", "yellow": "#EBCB8B",
    "red": "#BF616A",
}
FONT = "Segoe UI,Helvetica,Arial,sans-serif"
USER = os.environ.get("CREDLY_USER", "").strip()
TITLE = os.environ.get("CARD_TITLE", "Yata-Datacom")
OUT = Path(__file__).resolve().parent.parent / "assets" / "credly-badges.svg"
BADGE_DIR = Path(__file__).resolve().parent.parent / "assets" / "badges"
README = Path(__file__).resolve().parent.parent / "README.md"
UA = {"User-Agent": "Mozilla/5.0 (compatible; credly-card-generator)"}


def fetch(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def truncate(s: str, n: int) -> str:
    s = str(s).strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def wrap2(s: str, width: int = 22) -> list[str]:
    """把徽章名折成最多两行（按词折，超长单词硬切），避免长名字被截成 `xxx…`。"""
    words, lines, cur = str(s).split(), [], ""
    for w in words:
        while len(w) > width:                      # 超长单词硬切
            if cur:
                lines.append(cur); cur = ""
            lines.append(w[:width]); w = w[width:]
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= width:
            cur += " " + w
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    if len(lines) <= 2:
        return lines
    return [lines[0], truncate(" ".join(lines[1:]), width)]


def save_image(url: str, out: Path) -> str:
    """
    把徽章图片另存为仓库内的 PNG，**不**内嵌进 SVG。

    为什么：GitHub 对提交进仓库的 SVG 有安全清理（script / foreignObject / **内嵌 data-URI 图片** 都会被拒），
    内嵌后文件页会直接报 `Error rendering embedded code / Invalid image source`。
    所以卡片只画矢量图形与文字，徽章缩略图用独立 PNG，在 README 里并排展示。
    """
    try:
        if not url:
            return ""
        raw = fetch(url, timeout=45)
        if not raw or len(raw) > 400_000:
            return ""
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(raw)
        return out.name
    except Exception as e:
        print(f"  ⚠ 图片下载失败 {str(url)[:60]}: {e}")
        return ""


def collect(user: str) -> dict:
    d = json.loads(fetch(f"https://www.credly.com/users/{user}/badges.json"))
    badges = d.get("data", [])
    now = datetime.now(timezone.utc)
    issuers, skills, active, expiring = Counter(), Counter(), 0, 0
    items = []
    for b in badges:
        tpl = b.get("badge_template") or {}
        ents = ((tpl.get("issuer") or {}).get("entities") or [{}])
        issuer = (ents[0].get("entity") or {}).get("name") or "—"
        issuers[issuer] += 1
        for s in (tpl.get("skills") or []):
            if s.get("name"):
                skills[s["name"]] += 1
        exp = b.get("expires_at")
        expired = False
        if exp:
            try:
                expired = datetime.fromisoformat(exp.replace("Z", "+00:00")) < now
            except Exception:
                pass
        if not expired:
            active += 1
            if exp:
                try:
                    days = (datetime.fromisoformat(exp.replace("Z", "+00:00")) - now).days
                    if 0 <= days <= 90:
                        expiring += 1
                except Exception:
                    pass
        items.append({
            "name": tpl.get("name") or "—",
            "issuer": issuer,
            "img": save_image(b.get("image_url") or (tpl.get("image") or {}).get("url") or "",
                              BADGE_DIR / f"credly-{len(items) + 1}.png"),
            "issued": (b.get("issued_at") or "")[:10],
        })
    return {"total": len(badges), "issuers": issuers, "skills": skills, "active": active,
            "expiring": expiring, "items": items}


def short_name(name: str, issuer: str = "") -> str:
    """徽章名太长时去掉冗余前缀（发行方名字在缩略图角落已经有了），保证能完整显示。"""
    n = str(name).strip()
    for pre in ("Red Hat Certified ", "Red Hat ", "Microsoft Certified ", "AWS Certified "):
        if n.startswith(pre) and len(n) - len(pre) >= 8:
            n = n[len(pre):]
            break
    return n


def wrap2(s: str, width: int = 30) -> list[str]:
    """折成最多两行（按词折，超长单词硬切）。"""
    words, lines, cur = str(s).split(), [], ""
    for w in words:
        while len(w) > width:
            if cur:
                lines.append(cur); cur = ""
            lines.append(w[:width]); w = w[width:]
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= width:
            cur += " " + w
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines[:2] if lines else [""]


def stat(x: int, y: int, w: int, value: str, label: str, color: str) -> str:
    return (
        f'<g><rect x="{x}" y="{y}" width="{w}" height="62" rx="10" fill="{NORD["panel"]}"/>'
        f'<rect x="{x}" y="{y}" width="4" height="62" rx="2" fill="{color}"/>'
        f'<text x="{x + w / 2:.0f}" y="{y + 31}" fill="{NORD["text"]}" font-size="21" font-weight="700" '
        f'text-anchor="middle" font-family="{FONT}">{esc(value)}</text>'
        f'<text x="{x + w / 2:.0f}" y="{y + 49}" fill="{NORD["dim"]}" font-size="11" '
        f'text-anchor="middle" font-family="{FONT}">{esc(label)}</text></g>')


def render(d: dict) -> str:
    W, H = 660, 400
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">',
         f'<rect width="{W}" height="{H}" rx="14" fill="{NORD["bg"]}"/>',
         f'<rect width="{W}" height="50" rx="14" fill="{NORD["panel"]}"/>',
         f'<rect y="36" width="{W}" height="14" fill="{NORD["panel"]}"/>',
         f'<circle cx="26" cy="25" r="8" fill="{NORD["accent"]}"/>',
         f'<text x="42" y="30" fill="{NORD["text"]}" font-size="16" font-weight="700" font-family="{FONT}">'
         f'{esc(TITLE)}&#39;s Credly Stats</text>',
         f'<text x="{W - 22}" y="30" fill="{NORD["dim"]}" font-size="11" text-anchor="end" '
         f'font-family="{FONT}">auto-generated from public Credly data</text>']
    # ── 统计块（一排五个）──
    tiles = [(str(d["total"]), "Total Badges", NORD["accent"]),
             (str(len(d["issuers"])), "Unique Issuers", NORD["accent2"]),
             (str(len(d["skills"])), "Unique Skills", NORD["green"]),
             (str(d["active"]), "Active", NORD["yellow"]),
             (str(d["expiring"]), "Expiring ≤90d", NORD["red"])]
    gap, tw = 8, (W - 44 - 8 * 4) / 5
    for i2, (v, l, c) in enumerate(tiles):
        s.append(stat(22 + i2 * (tw + gap), 64, tw, v, l, c))
    # ── 一行式 Top Issuers / Top Skills ──
    y = 146
    iss = " · ".join(f"{truncate(n, 20)} ({c})" for n, c in d["issuers"].most_common(4)) or "—"
    s.append(f'<text x="22" y="{y}" fill="{NORD["muted"]}" font-size="12.5" font-family="{FONT}">'
             f'<tspan font-weight="700">Top Issuers</tspan>  {esc(iss)}</text>')
    y += 20
    sk = " · ".join(f"{truncate(n, 18)} ({c})" for n, c in d["skills"].most_common(5)) or "—"
    s.append(f'<text x="22" y="{y}" fill="{NORD["muted"]}" font-size="12.5" font-family="{FONT}">'
             f'<tspan font-weight="700">Top Skills</tspan>  {esc(sk)}</text>')
    # ── 徽章清单（纯文字；缩略图是仓库内独立 PNG，见 README）──
    y2 = 188
    s.append(f'<text x="22" y="{y2}" fill="{NORD["muted"]}" font-size="12.5" font-weight="700" '
             f'font-family="{FONT}">Badges ({d["total"]})</text>')
    y2 += 8
    for it in d["items"][:5]:
        y2 += 22
        s.append(f'<circle cx="28" cy="{y2 - 4}" r="4" fill="{NORD["accent"]}"/>')
        s.append(f'<text x="40" y="{y2}" fill="{NORD["text"]}" font-size="12" font-family="{FONT}">'
                 f'{esc(truncate(short_name(it["name"], it["issuer"]), 46))}</text>')
        s.append(f'<text x="{W - 22}" y="{y2}" fill="{NORD["dim"]}" font-size="11" text-anchor="end" '
                 f'font-family="{FONT}">{esc(it["issuer"])} · {esc(it["issued"])}</text>')
    s.append(f'<text x="22" y="{H - 14}" fill="{NORD["dim"]}" font-size="10.5" font-family="{FONT}">'
             f'数据来源：Credly 公开接口 · 由仓库内 GitHub Actions 自动刷新</text>')
    s.append("</svg>")
    return "\n".join(s)


def update_readme_badges(items: list[dict]) -> None:
    """把徽章缩略图（独立 PNG）写进 README 的标记块，徽章增减时自动同步。"""
    if not README.exists():
        return
    md = README.read_text(encoding="utf-8")
    start, end = "<!-- credly-badges:start -->", "<!-- credly-badges:end -->"
    if start not in md or end not in md:
        print("  ⚠ README 里没有 credly-badges 标记块，跳过缩略图更新")
        return
    imgs = "\n".join(
        f'<img src="./assets/badges/{esc(it["img"])}" height="110" '
        f'alt="{esc(short_name(it["name"], it["issuer"]))}" title="{esc(it["name"])} · {esc(it["issuer"])}" />'
        for it in items)
    new = f"{start}\n{imgs}\n{end}"
    md = re.sub(re.escape(start) + r".*?" + re.escape(end), new, md, flags=re.S)
    README.write_text(md, encoding="utf-8")
    print(f"  ✓ README 徽章缩略图已更新（{len(items)} 张）")


def main() -> int:
    if not USER:
        print("✗ 缺少用户名：请设置环境变量 CREDLY_USER（CI 里用仓库 Secret 传入）", file=sys.stderr)
        return 2
    d = collect(USER)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # 主页现在直接贴 PNG 缩略图（GitHub 对仓库内 SVG 卡片的渲染不可靠，用户端加载不出来）。
    # 需要留一份矢量卡片时设 CREDLY_SVG=1。
    if os.environ.get("CREDLY_SVG") == "1":
        svg = render(d)
        OUT.write_text(svg, encoding="utf-8")
        print(f"✓ 已生成 {OUT}  ({len(svg) / 1024:.0f} KB)")
    update_readme_badges([i for i in d["items"] if i["img"]])
    print(f"✓ 已生成 {OUT}  ({len(svg) / 1024:.0f} KB)")
    print(f"  徽章 {d['total']} 枚 · 发行方 {len(d['issuers'])} · 技能 {len(d['skills'])} · 有效 {d['active']}")
    print(f"  内嵌图片 {sum(1 for i in d['items'] if i['img'])}/{len(d['items'])} 张")
    return 0


if __name__ == "__main__":
    sys.exit(main())
