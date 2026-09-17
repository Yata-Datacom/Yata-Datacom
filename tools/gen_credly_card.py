"""生成 Credly 徽章统计卡（nord 配色，完全自建，不依赖任何第三方图床服务）。

为什么自建：
  第三方徽章服务（credly-readme-stats 之类）必须把 **Credly 用户名写进图片 URL**，
  公开主页上就等于把账号名（往往是真名拼音）贴出来了。自建卡片把数据取回来、
  渲染成 SVG 提交到仓库，主页只引用 `./assets/credly-badges.svg`：
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


def data_uri(url: str, limit: int = 120_000) -> str:
    """把徽章图片内嵌成 data URI（SVG 作为 <img> 渲染时无法加载外链资源）。"""
    try:
        raw = fetch(url, timeout=45)
        if len(raw) > limit:
            return ""
        mime = "image/png" if raw[:4] == b"\x89PNG" else ("image/jpeg" if raw[:2] == b"\xff\xd8" else "image/svg+xml")
        return f"data:{mime};base64,{base64.b64encode(raw).decode()}"
    except Exception as e:
        print(f"  ⚠ 图片下载失败 {url[:60]}: {e}")
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
            "img": data_uri(b.get("image_url") or (tpl.get("image") or {}).get("url") or ""),
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
    # ── 徽章：整排三个（图 + 两行名称）──
    items = d["items"][:4]
    n_b = max(1, len(items))
    cell = (W - 44) / n_b
    img = 84
    for i3, it in enumerate(items):
        cx = 22 + i3 * cell + cell / 2
        top = 196
        s.append(f'<rect x="{cx - (img + 18) / 2:.0f}" y="{top}" width="{img + 18}" height="{img + 18}" rx="10" '
                 f'fill="{NORD["panel"]}"/>')
        if it["img"]:
            s.append(f'<image x="{cx - img / 2:.0f}" y="{top + 9}" width="{img}" height="{img}" '
                     f'preserveAspectRatio="xMidYMid meet" href="{it["img"]}"/>')
        else:
            s.append(f'<text x="{cx:.0f}" y="{top + 50}" fill="{NORD["dim"]}" font-size="11" text-anchor="middle" '
                     f'font-family="{FONT}">badge image</text>')
        for li, line in enumerate(wrap2(short_name(it["name"], it["issuer"]), 30)):
            s.append(f'<text x="{cx:.0f}" y="{top + img + 34 + li * 13}" fill="{NORD["muted"]}" font-size="10.5" '
                     f'text-anchor="middle" font-family="{FONT}">{esc(line)}</text>')
        s.append(f'<text x="{cx:.0f}" y="{top + img + 34 + 26}" fill="{NORD["dim"]}" font-size="9.5" '
                 f'text-anchor="middle" font-family="{FONT}">{esc(it["issuer"])} · {esc(it["issued"])}</text>')
    s.append(f'<text x="22" y="{H - 14}" fill="{NORD["dim"]}" font-size="10.5" font-family="{FONT}">'
             f'数据来源：Credly 公开接口 · 由仓库内 GitHub Actions 自动刷新</text>')
    s.append("</svg>")
    return "\n".join(s)


def main() -> int:
    if not USER:
        print("✗ 缺少用户名：请设置环境变量 CREDLY_USER（CI 里用仓库 Secret 传入）", file=sys.stderr)
        return 2
    d = collect(USER)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    svg = render(d)
    OUT.write_text(svg, encoding="utf-8")
    print(f"✓ 已生成 {OUT}  ({len(svg) / 1024:.0f} KB)")
    print(f"  徽章 {d['total']} 枚 · 发行方 {len(d['issuers'])} · 技能 {len(d['skills'])} · 有效 {d['active']}")
    print(f"  内嵌图片 {sum(1 for i in d['items'] if i['img'])}/{len(d['items'])} 张")
    return 0


if __name__ == "__main__":
    sys.exit(main())
