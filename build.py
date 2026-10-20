#!/usr/bin/env python3
"""✦ Shiny Profile Builder ✦

照着《偶像大师 闪耀色彩》页游（シャニマス，界面用语取自汉化版）的真实界面，把 GitHub 数据画成「一整张」连续滚动的动画 SVG：

  主页        283 事务所（原生背景）：名牌 / 制作人档案 / 对话框 / Produce 按钮
  项目        横版项目卡：游戏菜单大字标题 + 完整简介（直接取 GitHub）+ 语言 / 最近更新
  培育        W.I.N.G. 培育主界面（原生背景、台历、马克杯、平板）：正在培育的项目 / 贡献日历 / 休息与贡献 / 语言排行
  制作人详情   档案照片 + Vo/Da/Vi/Me（语言占比）+ 技能（游戏技能一览样式的分类条 + 技术栈胶囊）
  任务        近 30 天贡献动态图表 + 连续贡献统计
  关于        帮助弹窗样式的自我介绍
  叶月        底部提示条

  python3 build.py            联网抓取最新数据（设置 GITHUB_TOKEN 后数据最完整）
  python3 build.py --offline  不联网，只用 data/stats.json 缓存
  python3 build.py --offline --watch  保存 config.json / projects.json 后自动重建
  python3 build.py --strict-refresh  自动任务使用：数据刷新失败时退出报错

素材：assets/game 保留游戏原生背景和道具（© Bandai Namco Entertainment；中文 UI 来自 ShinyGroup/SCTranslationData 汉化图集），
背景另有 AI 清晰度增强版，来源与处理记录见 assets/game/SOURCES.md；
培育页羽那 Coding 立绘为 AI 二创，见 assets/illustrations/SOURCES.md；
页签、圆形菜单按钮、气泡、平板、等级条、Vo/Da/Vi/Me 徽章等部件照游戏样式用矢量重绘；金币 / 羽钻仍用原生图；
字体为源样圆体（Resource Han Rounded，SIL OFL 1.1），构建时只保留用到的字，排版按它的真实字宽计算；
技术栈图标来自 Simple Icons（CC0），统计图标来自 Octicons（MIT）。
"""

import argparse
import base64
import datetime as dt
import hashlib
import html
import io
import json
import math
import os
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
GAME = ASSETS / "game"
FONTS = ASSETS / "fonts"
OUT = ASSETS / "shinycolors.svg"
CACHE = ROOT / "data" / "stats.json"
_ICONS = json.loads((ROOT / "data" / "icons.json").read_text(encoding="utf-8"))
ICON_DATA, OCTI = _ICONS["icons"], _ICONS["octicons"]
GIDX = json.loads((GAME / "index.json").read_text(encoding="utf-8"))
UA = {"User-Agent": "shiny-profile-builder"}
W = 1136  # 和游戏的逻辑宽度一致

# ───────────────────────── 配色（量自游戏运行时） ─────────────────────────

TEXT, TITLE, SUB = "#615365", "#4D4349", "#857A8A"  # 正文 / 标题 / 次要
LINE, FIELD, DOT = "#6B6A6F", "#A2A4B1", "#A1A1A1"  # 面板描边 / 输入框描边 / 点线
ROW, SIDE, PINK = "#F3F3F3", "#A59CAD", "#E8358D"
PARAM = {  # 键: (标签, 描边, 上色, 下色, 主色)
    "Vo": ("Vo.", "#E862A6", "#FFB0E6", "#F55FC0", "#F2559A"),
    "Da": ("Da.", "#6F8FD6", "#C2ECFF", "#5DB2FA", "#4C8DF0"),
    "Vi": ("Vi.", "#D9964F", "#FFEC9A", "#FBBE0A", "#F0A21A"),
    "Me": ("Me.", "#8E68C0", "#ECCBFF", "#9B5ED5", "#A57BE8"),
}
ORDER = ["Vo", "Da", "Vi", "Me"]
CARD = {  # 项目卡配色（取自偶像入口卡面）：大字上色, 大字下色, 大字外描边, 卡底色, 卡框
    "blue": ("#2B78EE", "#5CB9F8", "#6AA6F2", "#D3EBFF", "#7DB0EE"),
    "yellow": ("#EE4CA6", "#FF8ED2", "#F58BC6", "#FFF1B0", "#EDBF3A"),
    "orange": ("#FF7414", "#FFB320", "#FA9440", "#FFE0BE", "#F59E52"),
    "pink": ("#FF4B93", "#FF8E5A", "#FF7D97", "#FFD9E5", "#F48AA6"),
}
LANG_SLUG = {"Python": "python", "JavaScript": "javascript", "Java": "openjdk", "C++": "cplusplus", "C": "c",
             "Jupyter Notebook": "jupyter", "HTML": "html5", "CSS": "css3", "Dockerfile": "docker"}
INK = "#7B68B0"  # 技术栈 / 统计小图标统一用的单色（和档案卡统计图标同色）
LANG_C = {"TypeScript": "#3178C6", "Kotlin": "#A97BFF", "Shell": "#89E051", "Go": "#00ADD8", "Rust": "#DEA584",
          "QMake": "#41CD52", "Makefile": "#427819"}

# 字体：内嵌源样圆体可变字体（900 ≈ 游戏的 HummingStd-E，700 ≈ UD 角ゴ）；没装 fontTools 时退回系统字体
FALLBACK = "'PingFang SC','Hiragino Sans GB','Microsoft YaHei','Noto Sans CJK SC','Source Han Sans SC',sans-serif"

SPARK = "M0-1Q.13-.13 1 0Q.13.13 0 1Q-.13.13-1 0Q-.13-.13 0-1Z"
WEEK_CN = "一二三四五六日"

# ───────────────────────── 基础工具 ─────────────────────────


def esc(s):
    return html.escape(str(s), quote=True)


def n(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def _est(ch):
    """没有字体可读时的粗略字宽（em）。"""
    if ord(ch) > 0x2E80 or ch in "…—◇":
        return 1.0
    if ch in " il.,:;'|!·":
        return .32
    if ch in "()[]/\\-":
        return .42
    if ch.isupper() or ch in "@%&mw":
        return .72
    return .6 if ch.isdigit() else .57


_FONT, _ADV = {}, {}


def _glyphs(cls):
    """内嵌字体在对应字重下的字形表（h=900，u=700），用来精确量字宽。"""
    wt = 900 if cls == "h" else 700
    if wt not in _FONT:
        try:
            from fontTools.ttLib import TTFont
            if "f" not in _FONT:
                _FONT["f"] = TTFont(FONTS / "ResourceHanRoundedCN-VF.woff2")
            f = _FONT["f"]
            _FONT[wt] = (f.getBestCmap(), f.getGlyphSet(location={"wght": wt}), f["head"].unitsPerEm)
        except Exception:  # noqa: BLE001
            _FONT[wt] = None
    return _FONT[wt]


def tw(s, size, cls="h"):
    """文字宽度（px）：按内嵌字体的真实字宽累加（字体没有字间调整），读不到字体时粗估。"""
    w = 0.0
    for ch in str(s):
        k = (ch, cls)
        if k not in _ADV:
            g = _glyphs(cls)
            name = g[0].get(ord(ch)) if g else None
            _ADV[k] = g[1][name].width / g[2] if name else _est(ch)
        w += _ADV[k]
    return w * size


def fit(s, size, maxw, cls="h"):
    w = tw(s, size, cls)
    return size if w <= maxw else size * maxw / w


def plain(s):
    return re.sub(r"[\[\]]", "", s)


def wrap(s, size, maxw, lines=2, cls="u"):
    """按宽度折行（中文逐字、英文按词），超出行数时末尾加省略号。"""
    tokens = re.findall(r"[A-Za-z0-9_.+#'-]+|\s+|.", s.strip())
    out, cur = [], ""
    for t in tokens:
        if tw(cur + t, size, cls) <= maxw:
            cur += t
            continue
        out.append(cur.rstrip())
        cur = t.lstrip()
    if cur.strip():
        out.append(cur.rstrip())
    if len(out) > lines:
        last = out[lines - 1]
        while last and tw(last + "…", size, cls) > maxw:
            last = last[:-1]
        out = out[:lines - 1] + [last.rstrip("，。、 ") + "…"]
    return out


_uid = 0


def uid(p="u"):
    global _uid
    _uid += 1
    return f"{p}{_uid}"


DEFS = {}


def _stop(s):
    op = f' stop-opacity="{s[2]}"' if len(s) > 2 else ""
    return f'<stop offset="{s[0]}" stop-color="{s[1]}"{op}/>'


def lg(stops, x1=0, y1=0, x2=0, y2=1):
    """线性渐变（自动去重），返回 url(#id)。"""
    k = "l" + hashlib.md5(repr((stops, x1, y1, x2, y2)).encode()).hexdigest()[:7]
    if k not in DEFS:
        DEFS[k] = (f'<linearGradient id="{k}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">'
                   + "".join(_stop(s) for s in stops) + "</linearGradient>")
    return f"url(#{k})"


def rg(stops, cx=.5, cy=.5, r=.5):
    k = "r" + hashlib.md5(repr((stops, cx, cy, r)).encode()).hexdigest()[:7]
    if k not in DEFS:
        DEFS[k] = (f'<radialGradient id="{k}" cx="{cx}" cy="{cy}" r="{r}">'
                   + "".join(_stop(s) for s in stops) + "</radialGradient>")
    return f"url(#{k})"


# ── 动画：一律用缓动曲线，避免「一顿一顿」 ──
EASE = ".45 0 .55 1"
# 一组统一的节奏：操作提示、悬浮提示、环境呼吸、掠光。
MOTION = {"pulse": 3.2, "float": 4.2, "ambient": 5.6, "breath": 4.6, "shine": 6.4, "chart": 6.4}


def _kt(k):
    return ";".join("0" if i == 0 else "1" if i == k else f"{i / k:.3f}" for i in range(k + 1))


def anim(attr, values, dur, phase=0.0, kt=None, ease=True, extra=""):
    k = values.count(";")
    sp = f' calcMode="spline" keySplines="{";".join([EASE] * k)}"' if ease else ""
    return (f'<animate attributeName="{attr}" values="{values}" keyTimes="{kt or _kt(k)}"{sp} dur="{dur:g}s" '
            f'begin="{-phase:.2f}s" repeatCount="indefinite"{extra}/>')


def animT(typ, values, dur, phase=0.0, kt=None, ease=True, add=False):
    k = values.count(";")
    sp = f' calcMode="spline" keySplines="{";".join([EASE] * k)}"' if ease else ""
    a = ' additive="sum"' if add else ""
    return (f'<animateTransform attributeName="transform" type="{typ}" values="{values}" keyTimes="{kt or _kt(k)}"'
            f'{sp} dur="{dur:g}s" begin="{-phase:.2f}s" repeatCount="indefinite"{a}/>')


def grow(to, dur=1.4):
    """载入时宽度从 0 长到目标值（只播一次）。"""
    return (f'<animate attributeName="width" values="0;{n(to)}" keyTimes="0;1" calcMode="spline" '
            f'keySplines=".2 .8 .2 1" dur="{dur}s" fill="freeze"/>')


def once(attr, values, dur, kt=None):
    """内容只在初次载入时展开；之后保留，避免阅读时循环清空。"""
    return (f'<animate attributeName="{attr}" values="{values}" keyTimes="{kt or _kt(values.count(";"))}" '
            f'dur="{dur:g}s" fill="freeze"/>')


def enter(delay, dx=36, dur=.9):
    """载入时从右侧滑入并淡入（只播一次）。"""
    return (f'<animate attributeName="opacity" values="0;1" dur="{dur}s" begin="{delay}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" values="{dx} 0;0 0" calcMode="spline" '
            f'keySplines=".2 .8 .2 1" dur="{dur}s" begin="{delay}s" fill="freeze" additive="sum"/>')


def T(x, y, s, size, fill=TEXT, cls="u", anchor="start", extra="", w=None):
    if w:
        size = fit(s, size, w, cls)
        extra += f' data-w="{n(w)}"'
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (f'<text class="{cls}" x="{n(x)}" y="{n(y)}" font-size="{n(size)}" fill="{fill}"{a}{extra}>'
            f'{esc(s)}</text>')


def O(x, y, s, size, fill, stroke, sw, cls="h", anchor="start", extra="", w=None):
    """描边字（描边画在填充下面）。"""
    if w:
        k = fit(s, size, w, cls) / size
        size, sw = size * k, sw * k
        extra += f' data-w="{n(w)}"'
    return T(x, y, s, size, fill, cls, anchor,
             f' stroke="{stroke}" stroke-width="{n(sw)}" stroke-linejoin="round" paint-order="stroke"{extra}')


def RT(x, y, s, size, fill=TEXT, hi=PINK, cls="u", anchor="start", w=None):
    """带高亮的文字：方括号里的部分用粉色（游戏说明文里的强调色）。"""
    extra = ""
    if w:
        size = fit(plain(s), size, w, cls)
        extra = f' data-w="{n(w)}"'
    parts = [p for p in re.split(r"(\[[^\]]*\])", s) if p]
    inner = "".join(f'<tspan fill="{hi}">{esc(p[1:-1])}</tspan>' if p.startswith("[") else esc(p) for p in parts)
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return f'<text class="{cls}" x="{n(x)}" y="{n(y)}" font-size="{n(size)}" fill="{fill}"{a}{extra}>{inner}</text>'


def text_path(s, size, cls="h"):
    """按内嵌字体把文字转成路径（字体单位、整数坐标，基线在 y=0）：返回 (完整字形, 去掉字怀的外轮廓, 宽度 px, 缩放)，
    读不到字体时返回 None。
    粗描边直接描 <text> 会把字怀（A、e、g 的小洞）填一半，剩下零碎的小块；用外轮廓描边、字怀整块填白就干净了。"""
    g = _glyphs(cls)
    if not g:
        return None
    from fontTools.pens.recordingPen import RecordingPen
    cmap, gs, upm = g
    k = size / upm
    full, sil, x0 = [], [], 0.0

    def pt(p):
        return f"{round(x0 + p[0])} {round(-p[1])}"

    for ch in str(s):
        name = cmap.get(ord(ch))
        if not name:
            x0 += _est(ch) * upm
            continue
        rp = RecordingPen()
        gs[name].draw(rp)
        contours, cur = [], []
        for op, pts in rp.value:
            if op == "moveTo":
                cur = [(op, pts)]
            elif op in ("closePath", "endPath"):
                contours.append(cur)
                cur = []
            else:
                cur.append((op, pts))
        cmd = {"moveTo": "M", "lineTo": "L", "curveTo": "C", "qCurveTo": "Q"}
        ds, areas = [], []
        for c in contours:
            ds.append("".join(cmd[op] + " ".join(pt(q) for q in pts) for op, pts in c) + "Z")
            P = [q for _op, pts in c for q in pts]
            areas.append(sum(P[i][0] * P[i - 1][1] - P[i - 1][0] * P[i][1] for i in range(len(P))))
        if areas:
            outer = max(areas, key=abs) > 0  # 面积最大的一定是外轮廓，和它同向的都是外轮廓，反向的是字怀
            full += ds
            sil += [d for d, a in zip(ds, areas) if (a > 0) == outer]
        x0 += gs[name].width
    return "".join(full), "".join(sil), x0 * k, k


def outlined(x, y, s, size, layers, fill, anchor="start", w=None):
    """多层描边大字（layers 由外到内：(颜色, 描边总宽, 不透明度)），转成路径画，字怀填最内层颜色。"""
    if w:
        size = fit(s, size, w)
    tp = text_path(s, size)
    if not tp:  # 没装 fontTools：退回 <text> 描边
        return "".join(O(x, y, s, size, c, c, sw, "h", anchor, f' opacity="{op}"' if op < 1 else "")
                       for c, sw, op in layers) + T(x, y, s, size, fill, "h", anchor)
    full, sil, width, k = tp
    x0 = x - width / 2 if anchor == "middle" else x - width if anchor == "end" else x
    t = f' transform="translate({n(x0)} {n(y)}) scale({k:.5f})"'
    pid = "tp" + hashlib.md5(sil.encode()).hexdigest()[:7]  # 外轮廓只存一份，各层描边用 <use> 复用
    DEFS[pid] = f'<path id="{pid}" d="{sil}"/>'
    o = "".join(f'<use href="#{pid}"{t} fill="{c}" stroke="{c}" stroke-width="{sw / k:.0f}" stroke-linejoin="round"'
                + (f' opacity="{op}"' if op < 1 else "") + "/>" for c, sw, op in layers)
    return o + f'<path d="{full}"{t} fill="{fill}" data-t="{esc(s)}"' + (f' data-w="{n(w)}"' if w else "") + "/>"


def logo(x, y, s, size, grad, outer, anchor="middle", white=.38, out=.56, w=None):
    """游戏菜单大字：渐变填充 + 粗白边 + 外圈彩色描边。
    白边要够厚（约 0.19em）才能把 c、e、h 这类开口字怀整个填白；太薄时外圈颜色会在开口里留下一小截。"""
    if w:
        size = fit(s, size, w)
    return outlined(x, y, s, size, [(outer, size * out, 1), ("#fff", size * white, 1)], grad, anchor)


def R(x, y, w, h, r, fill, stroke=None, sw=1.0, extra=""):
    s = f' stroke="{stroke}" stroke-width="{n(sw)}"' if stroke else ""
    rr = f' rx="{n(r)}"' if r else ""
    return f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}"{rr} fill="{fill}"{s}{extra}/>'


def spark(x, y, r, color="#fff", op=1.0):
    o = f' opacity="{op}"' if op < 1 else ""
    return f'<path d="{SPARK}" transform="translate({n(x)} {n(y)}) scale({n(r)})" fill="{color}"{o}/>'


def sparkle(x, y, r, color="#fff", dur=MOTION["ambient"], phase=0.0):
    """一闪一闪的四角星（放大时顺带转 45°）。"""
    return (f'<g transform="translate({n(x)} {n(y)})"><g transform="scale(0)">'
            + animT("scale", f"0;{n(r)};0;0", dur, phase, kt="0;.4;.8;1")
            + animT("rotate", "0;45;45;45", dur, phase, kt="0;.4;.8;1", add=True)
            + f'<path d="{SPARK}" fill="{color}"/></g></g>')


def shine(x, y, w, h, r, dur=MOTION["shine"], phase=0.0, op=.5, bw=26):
    """按钮/进度条上周期性划过的一道高光。"""
    cid = uid("s")
    return (f'<clipPath id="{cid}">{R(x, y, w, h, r, "#000")}</clipPath><g clip-path="url(#{cid})">'
            f'<g transform="translate({n(x)} {n(y)})"><rect x="{-bw * 2}" y="0" width="{bw}" height="{n(h)}" '
            f'fill="#fff" opacity="{op}" transform="skewX(-22)">'
            + anim("x", f"{-bw * 2};{n(w + h)};{n(w + h)}", dur, phase, kt="0;.35;1") + "</rect></g></g>")


def dotted(x1, x2, y, color=DOT, w=1.3):
    return (f'<path d="M{n(x1)} {n(y)}H{n(x2)}" stroke="{color}" stroke-width="{w}" '
            f'stroke-dasharray="1.6 2.6" stroke-linecap="round"/>')


# ───────────────────────── 素材：原生图片 / 图标 ─────────────────────────

USED = {}


def gimg(name, x, y, w=None, h=None, extra=""):
    """放一张 assets/game 里的原生素材（同一张图只内嵌一次）。"""
    # 背景的画面尺寸、放大比例照旧；只换用更高像素的增强版。
    logical_w, logical_h = GIDX[name][:2]
    if name + "_hd" in GIDX:
        name += "_hd"
    w0, h0 = GIDX[name][:2]
    if w is None and h is None:
        w, h = logical_w, logical_h
    elif h is None:
        h = h0 * w / w0
    elif w is None:
        w = w0 * h / h0
    USED[name] = True
    return (f'<use href="#g-{name}" transform="translate({n(x)} {n(y)}) scale({w / w0:.4f} {h / h0:.4f})"'
            f'{extra}/>')


def hana_coding(y, cfg):
    """透明立绘使用固定画布，整体上下平移，不改变人物比例。"""
    path = cfg.get("illustration", "assets/illustrations/hana-coding.webp")
    if path is None:
        return ""
    from PIL import Image
    with Image.open(ROOT / path) as source:
        source = source.convert("RGBA")
        source.thumbnail((1024, 1536), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (1024, 1536))
        canvas.alpha_composite(source, ((1024-source.width)//2, 1536-source.height))
        output = io.BytesIO()
        canvas.save(output, "WEBP", lossless=True)
    data = base64.b64encode(output.getvalue()).decode()
    DEFS["hanaArtwork"] = (f'<image id="hanaArtwork" width="1024" height="1536" '
                          f'href="data:image/webp;base64,{data}"/>')
    # 从电脑贴合桌沿的位置向下缓移，底部仍被前景桌面遮挡，避免露出悬空间隙。
    return (f'<g id="hana-coding" transform="translate(0 {y+543})"><g>'
            + animT("translate", "0 0;0 5;0 0", MOTION["breath"])
            + '<use href="#hanaArtwork" transform="translate(354 -467) scale(.419921875)"/></g></g>')


def mug_steam(x, y):
    """杯口三缕很淡的蒸汽，错相上升并消散。"""
    o = [f'<g id="mug-steam" transform="translate({x} {y})" fill="none" stroke="#fff" stroke-linecap="round">']
    for i in range(3):
        phase = i * MOTION["ambient"] / 3
        o.append('<g opacity="0">'
                 + animT("translate", "0 4;3 -16;0 -32", MOTION["ambient"], phase)
                 + anim("opacity", "0;.6;0", MOTION["ambient"], phase)
                 + f'<path d="M{i*12} 0q-8-9 0-18t0-18" stroke-width="2.4"/></g>')
    return "".join(o) + '</g>'


def octicon(name, cx, cy, s, color):
    return (f'<path d="{OCTI[name]}" transform="translate({n(cx - s / 2)} {n(cy - s / 2)}) scale({s / 24:.4f})" '
            f'fill="{color}"/>')


def _lum(hx):
    r, g, b = (int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return .299 * r + .587 * g + .114 * b


def brand(slug, x, y, s, color=INK):
    """技术栈 logo（Simple Icons 路径，以 x,y 为中心，边长 s）。默认统一画成单色，color=None 时用品牌色。"""
    if slug == "openjdk":  # Simple Icons 的 OpenJDK 是 Duke 剪影，小尺寸认不出来，换成咖啡杯
        t = f'transform="translate({n(x - s / 2)} {n(y - s / 2)}) scale({s / 24:.3f})"'
        cup, steam = (color, color) if color else ("#5382A1", "#E76F00")
        return (f'<path d="M4.6 10.6h11.6v4.6a4.9 4.9 0 0 1-4.9 4.9H9.5a4.9 4.9 0 0 1-4.9-4.9Z" fill="{cup}" {t}/>'
                f'<path d="M16.2 12h1.3a2.5 2.5 0 0 1 0 5h-1.9M3.4 21.8h14.4" fill="none" stroke="{cup}" '
                f'stroke-width="1.9" stroke-linecap="round" {t}/>'
                f'<path d="M8.4 2.4c-1.5 1.5 1.5 2.7 0 4.8M12.4 2.4c-1.5 1.5 1.5 2.7 0 4.8" fill="none" '
                f'stroke="{steam}" stroke-width="1.9" stroke-linecap="round" {t}/>')
    ic = ICON_DATA[slug]
    if color:
        return (f'<path d="{ic["path"]}" transform="translate({n(x - s / 2)} {n(y - s / 2)}) scale({s / 24:.3f})" '
                f'fill="{color}"/>')
    c = ic["hex"]
    o = ""
    if slug == "javascript":  # 黄底黑字
        o = R(x - s * .42, y - s * .42, s * .84, s * .84, 1, "#1B1B1F")
    elif _lum(c) > .62:
        c = "#5D7898"
    elif c == "#000000":
        c = "#3A3A46"
    return o + f'<path d="{ic["path"]}" transform="translate({n(x - s / 2)} {n(y - s / 2)}) scale({s / 24:.3f})" fill="{c}"/>'


def chevron(x, y, s, color, sw=2.4):
    return (f'<path d="M{n(x - s)} {n(y - s / 2)}l{n(s)} {n(s)} {n(s)}-{n(s)}" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')


# ───────────────────────── 矢量小部件（照游戏样式重绘，任意缩放都清晰） ─────────────────────────


def _gear(teeth=8, ro=10.6, ri=8.2, hole=3.3):
    pts = []
    for i in range(teeth):
        a = 2 * math.pi * i / teeth
        for da, r in ((-.3, ri), (-.17, ro), (.17, ro), (.3, ri)):
            pts.append(f"{12 + r * math.cos(a + da):.2f} {12 + r * math.sin(a + da):.2f}")
    return (f"M{'L'.join(pts)}Z"
            f"M{12 + hole} 12a{hole} {hole} 0 1 0 {-2 * hole} 0a{hole} {hole} 0 1 0 {2 * hole} 0Z")


GLYPH = {  # 24×24 格子里的实心小图形：填充路径, 描边路径, evenodd, 描边色（None=同填充色）
    "people": ("M9 4.4a3.3 3.3 0 1 1 0 6.6 3.3 3.3 0 0 1 0-6.6ZM16.5 4.2a2.8 2.8 0 1 1 0 5.6 2.8 2.8 0 0 1 0-5.6Z"
               "M3 20v-1.2C3 15.6 5.5 13 9 13s6 2.6 6 5.8V20ZM16.2 11.6c3.1 0 5.3 2.3 5.3 5.4V18.6h-5.1v-.2"
               "c0-2.4-.9-4.6-2.6-6.1.7-.4 1.5-.7 2.4-.7Z", None, False, None),
    "trophy": ("M6.5 3.5h11V9a5.5 5.5 0 0 1-11 0ZM10.8 14h2.4v3.6h-2.4ZM7.6 17.4h8.8a1.1 1.1 0 0 1 1.1 1.1v2H6.5v-2"
               "a1.1 1.1 0 0 1 1.1-1.1Z", "M6.6 5.4H4.2V7a3.7 3.7 0 0 0 3.5 3.7M17.4 5.4h2.4V7a3.7 3.7 0 0 1-3.5 3.7",
               False, None),
    "flame": ("M12.4 2.4c.7 3.1-1.7 4.8-3.4 6.8C7.2 11.2 6 13 6 15.4a6 6 0 0 0 12 0c0-2.5-1.2-4.6-2.6-5.9"
              ".1 1.7-.5 3-1.7 3.6.6-3.9-.5-7.8-1.3-10.7Z", None, False, None),
    "house": ("M12 3 2.4 11.2h2.9v9.4h5v-6h3.4v6h5v-9.4h2.9Z", None, False, None),
    "bag": ("M9 3.4h6a1.6 1.6 0 0 1 1.6 1.6v2H20a1.6 1.6 0 0 1 1.6 1.6v10A1.6 1.6 0 0 1 20 20.2H4a1.6 1.6 0 0 1-1.6-1.6"
            "v-10A1.6 1.6 0 0 1 4 7h3.4V5A1.6 1.6 0 0 1 9 3.4ZM9.4 5.2V7h5.2V5.2Z", None, True, None),
    "gear": (_gear(), None, True, None),
}


def glyph(name, cx, cy, s, color):
    """实心小图形（以 cx,cy 为中心，边长 s）。"""
    d, ds, eo, sc = GLYPH[name]
    t = f' transform="translate({n(cx - s / 2)} {n(cy - s / 2)}) scale({s / 24:.4f})"'
    rule = ' fill-rule="evenodd"' if eo else ""
    o = f'<path d="{d}" fill="{color}"{rule}{t}/>'
    if ds:
        o += (f'<path d="{ds}" fill="none" stroke="{sc or color}" stroke-width="{1.6 if sc else 1.9}" '
              f'stroke-linecap="round" stroke-linejoin="round"{t}/>')
    return o


BADGE = {  # 圆形图标：渐变色标, 是否斜向渐变, 外描边, 图形, 图形色（金币和羽石用原生图，见 item）
    "fan": ([(0, "#A8EB90"), (1, "#36AE47")], False, "#2A8638", "people", "#fff"),
    "trophy": ([(0, "#FFE27A"), (1, "#F09A16")], False, "#B5760A", "trophy", "#fff"),
    "flame": ([(0, "#FFC27A"), (1, "#FF5A8C")], False, "#D4456D", "flame", "#fff"),
}


def badge(kind, cx, cy, r):
    """统一风格的圆形图标：深色外圈 + 白圈 + 渐变底 + 白色图形（粉丝 / 奖杯 / 连续）。"""
    stops, diag, line, g, gc = BADGE[kind]
    fill = lg(stops, 0, 0, 1, 1) if diag else lg(stops)
    o = (f'<circle cx="{n(cx)}" cy="{n(cy + r * .1)}" r="{n(r)}" fill="#2E2236" opacity=".2"/>'
         f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{line}"/>'
         f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r * .9)}" fill="#fff"/>'
         f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r * .78)}" fill="{fill}"/>')
    o += (f'<ellipse cx="{n(cx)}" cy="{n(cy - r * .4)}" rx="{n(r * .46)}" ry="{n(r * .2)}" fill="#fff" opacity=".35"/>'
          + glyph(g, cx, cy + r * .02, r * (1.16 if g == "people" else 1.08), gc))
    return o


def item(name, cx, cy, s):
    """原生道具图（金币 / 羽石，从商店 148px 图标里抠出来的），以 cx,cy 为中心、高 s。"""
    w0, h0 = GIDX[name][:2]
    return gimg(name, cx - s * w0 / h0 / 2, cy - s / 2, h=s)


def pill(x, cy, label, slug=None, size=13, h=26):
    """技术栈 / 标签胶囊：浅紫底 + 单色 logo + 文字，返回 (svg, 宽度)。"""
    pad, ico, gap = h * .4, h * .58, h * .26
    tx = x + (pad + ico + gap if slug else h * .46)
    w = tx - x + tw(label, size, "u") + h * .46
    return (R(x, cy - h / 2, w, h, h / 2, "#F6F3FB", "#D6CDE6", 1.2)
            + (brand(slug, x + pad + ico / 2, cy, ico) if slug else "")
            + T(tx, cy + size * .36, label, size, TEXT, "u")), w


def ribbon(x, y, w, h, label, size=16):
    """技能列表的分类条（照游戏技能一览的灰紫斜纹条：两端四角星 + 居中白字）。"""
    cid = uid("rb")
    stripes = R(x, y, w, h, 0, "url(#stripes)", extra=' opacity=".16"')
    return (f'<clipPath id="{cid}">{R(x, y, w, h, h / 2, "#000")}</clipPath>'
            + R(x, y, w, h, h / 2, lg([(0, "#A898B0"), (1, "#8F8098")]))
            + f'<g clip-path="url(#{cid})">{stripes}</g>'
            + spark(x + 17, y + h / 2, 6.5, "#fff") + spark(x + w - 17, y + h / 2, 6.5, "#fff")
            + T(x + w / 2, y + h / 2 + size * .36, label, size, "#fff", "h", "middle", w=w - 80))


def scallop(cx, cy, r, k=12):
    """花边圆（Vo/Da/Vi/Me 徽章的外形），r 为凸起处半径。"""
    rv = r / (math.cos(math.pi / k) + .5366 * math.sin(math.pi / k))  # 凸起弧半径取弦长的 0.6 倍
    b = 2 * rv * math.sin(math.pi / k) * .6
    pts = [(cx + rv * math.cos(2 * math.pi * (i + .5) / k), cy + rv * math.sin(2 * math.pi * (i + .5) / k))
           for i in range(k + 1)]
    return (f"M{n(pts[0][0])} {n(pts[0][1])}"
            + "".join(f"A{n(b)} {n(b)} 0 0 1 {n(px)} {n(py)}" for px, py in pts[1:]) + "Z")


def param_badge(key, cx, cy, r):
    """属性徽章：花边圆 + 「Vo.」字样（照培育画面的属性图标重绘）。"""
    lab, bd, top, bot, _m = PARAM[key]
    d = scallop(cx, cy, r)
    size = r * .84
    return (f'<path d="{d}" fill="{bd}" stroke="{bd}" stroke-width="{n(r * .18)}" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="{lg([(0, top), (1, bot)])}" stroke="#fff" stroke-width="{n(r * .1)}"/>'
            + O(cx, cy + size * .36, lab, size, "#fff", bd, size * .3, "h", "middle", w=r * 1.66))


TAB = {  # 页签：上色, 下色, 外框, 字色, 字描边
    "pink": ("#FFFBFF", "#FFD2EE", "#EE6CB0", "#F0529C", "#fff"),
    "lav": ("#FFFFFF", "#D8DAF8", "#5E5462", TITLE, "#fff"),
    "yellow": ("#FFFEF2", "#FFE892", "#5E5462", TITLE, "#fff"),
    "magenta": ("#E3418F", "#F86BB2", "#5C3450", "#fff", "#B02E72"),
}


def tab(x, y, w, h, label, kind, size=22, r=8):
    """游戏里的页签按钮（选中态粉色描边 / 未选中态深色描边）。"""
    top, bot, line, tc, ts = TAB[kind]
    return (R(x, y + 2.5, w, h, r, "#3C3442", extra=' opacity=".18"') + R(x, y, w, h, r, line)
            + R(x + 2, y + 2, w - 4, h - 4, r - 2, lg([(0, top), (1, bot)]))
            + R(x + 3.6, y + 3.6, w - 7.2, h - 7.2, max(1, r - 3.6), "none", "#fff", 1.2, ' opacity=".8"')
            + spark(x + w - 14, y + 13, 5, "#fff", .95) + spark(x + w - 24, y + 20, 2.8, "#fff", .85)
            + O(x + w / 2, y + h / 2 + size * .36, label, size, tc, ts, size * .24, "h", "middle", w=w - 26))


def round_btn(cx, cy, label, g, r=37):
    """培育画面两侧的圆形菜单按钮（图标 + 压在下沿的白边字）。"""
    return (f'<circle cx="{n(cx)}" cy="{n(cy + 3)}" r="{n(r + 3)}" fill="#2E2236" opacity=".2"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r + 3)}" fill="#6E6475"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r + 1.4)}" fill="#fff"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r - 1.4)}" fill="{lg([(0, "#FFFFFF"), (1, "#CBC5EA")])}"/>'
            + glyph(g, cx, cy - r * .16, r * 1.02, "#6B5A80")
            + O(cx, cy + r * .82, label, 15, TITLE, "#fff", 4.6, "h", "middle", w=r * 2.7))


def new_tag(x, y, size=19):
    """「NEW!!」角标（左下角为 x,y）。"""
    return (f'<g transform="translate({n(x)} {n(y)}) skewX(-8)">'
            + O(0, 0, "NEW!!", size, "#5B3A06", "#5B3A06", size * .42, "h")
            + O(0, 0, "NEW!!", size, lg([(0, "#FFF9BF"), (.55, "#FFD43A"), (1, "#F4A600")]), "#FFF4C2", size * .08,
                "h") + "</g>")


# ───────────────────────── 游戏 UI 组件 ─────────────────────────

BTN = {  # 外描边, 竖向渐变, 斜切色, 斜切透明度, 字色, 字描边
    "lav": ("#5E5462", [(0, "#FFFFFF"), (1, "#E2E3FA")], "#CFCFF6", .55, TEXT, None),
    "pink": ("#6E4A70", [(0, "#FFC6DB"), (.46, "#FF96C6"), (.5, "#FF6BB7"), (1, "#EE3F9F")], "#E8399A", .25,
             "#fff", "#BC2B74"),
}


def button(x, y, w, h, kind="lav", label="", size=22, r=9):
    """游戏按钮：深色外框 + 渐变 + 右下斜切暗面 + 内高光。"""
    line, stops, cut, cut_op, tc, ts = BTN[kind]
    cid = uid("c")
    o = [R(x, y + 3, w, h, r, "#3C3442", extra=' opacity=".22"'),
         R(x, y, w, h, r, line),
         f'<clipPath id="{cid}">{R(x + 2, y + 2, w - 4, h - 4, r - 2, "#000")}</clipPath>',
         R(x + 2, y + 2, w - 4, h - 4, r - 2, lg(stops)),
         f'<path clip-path="url(#{cid})" d="M{n(x + w * .46)} {n(y + h)}L{n(x + w)} {n(y + h * .1)}V{n(y + h)}Z" '
         f'fill="{cut}" opacity="{cut_op}"/>',
         R(x + 3.5, y + 3.5, w - 7, h - 7, max(1, r - 3.5), "none", "#fff", 1.3, ' opacity=".8"'),
         spark(x + w - 16, y + 12, 4.5, "#fff", .9) + spark(x + w - 27, y + 19, 2.6, "#fff", .8)]
    if label:
        ty = y + h / 2 + fit(label, size, w - 18) * .36
        o.append(O(x + w / 2, ty, label, size, tc, ts, size * .2, "h", "middle", w=w - 18) if ts
                 else T(x + w / 2, ty, label, size, tc, "h", "middle", w=w - 18))
    return "".join(o)


def chip(x, y, w, h=34):
    """主页顶部的半透明深色数值条。"""
    return (R(x, y, w, h, h / 2, "#1C1830", extra=' opacity=".62"')
            + R(x + .5, y + .5, w - 1, h - 1, h / 2, "none", "#fff", 1, ' opacity=".28"'))


def red_badge(cx, cy, num, r=13):
    w = max(r * 2, tw(num, r * 1.1, "u") + 14)
    return (R(cx - w / 2, cy - r, w, r * 2, r, lg([(0, "#FF6E93"), (1, "#E5305F")]), "#fff", 2.2)
            + T(cx, cy + r * .42, num, r * 1.1, "#fff", "u", "middle"))


def header(y, title):
    """按原生标题条重画细边框，避免 56px 高图集在高分屏上模糊。"""
    return (R(-27, y+3, 398, 54, 27, "#7B727F", extra=' opacity=".15"')
            + R(-27, y, 398, 54, 27, "#fff", "#948C9A", 1.4)
            + R(-24, y+3, 392, 48, 24, "none", "#DBD5E2", 1.4)
            + f'<circle cx="23" cy="{y+27}" r="20" fill="#fff" stroke="#B5A3D5" stroke-width="1.3"/>'
            + f'<circle cx="23" cy="{y+27}" r="16.5" fill="{lg([(0, "#AD91EF"), (1, "#F7A0D1")])}"/>'
            + gimg("swan", 9, y+14, 28, 26) + sparkle(344, y+28, 9, "#D9C4F0", MOTION["pulse"])
            + T(54, y + 37, title, 24, TITLE, "h"))


def home_action(kind, size, repos=0):
    """Produce / 任务按钮的原生双圆环、图形与大字，全部用矢量重画。"""
    pink = kind == "produce"
    colors = [(0, "#FFD4F1"), (.52, "#F975D0"), (1, "#E539AE")] if pink else [(0, "#E9E5FA"), (1, "#AEB3DC")]
    o = [f'<g transform="scale({size/154:.5f})">',
         '<circle cy="3" r="75" fill="#463E4C" opacity=".25"/>',
         '<circle r="75" fill="#FFF" stroke="#746978" stroke-width="2"/>',
         f'<circle r="71" fill="{lg(colors)}" stroke="#D6CCDF" stroke-width="1.2"/>',
         '<circle r="67" fill="none" stroke="#fff" stroke-width="1.5"/>',
         '<path d="M-57-35Q0-89 57-35Q0-45-57-35Z" fill="#fff" opacity=".25"/>']
    for sx, sy, r in [(-48, -12, 8), (49, 3, 10), (39, -39, 6), (-24, -49, 5)]:
        o.append(spark(sx, sy, r, "#fff", .42))
    if pink:
        o.append('<g stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none">'
                 '<path d="M-30 4V-49L27-45V5M27-45L38-50V5M-34-38H-25M-34-23H-25M-34-8H-25M19-35H25M19-25H25M19-15H25"/>'
                 '<path d="M-20-55L37-50" opacity=".7"/></g>'
                 + gimg("swan", -19, -32, 34, 31)
                 + O(0, 29, "Produce", 24, "#fff", "#DC2F9D", 3.4, "h", "middle")
                 + R(-48, 38, 96, 20, 10, "#BE006E", "#FFF", 1.2)
                 + T(0, 52.5, f"公开仓库 {repos}", 12.5, "#fff", "h", "middle", w=86))
    else:
        o.append('<g stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none">'
                 '<rect x="-26" y="-48" width="52" height="65" rx="5"/><path d="M-11-48V-44Q-11-41-8-41H8Q11-41 11-44V-48"/>'
                 '<path d="M-18-29l3 3 6-7M-18-13l3 3 6-7M-18 3l3 3 6-7M-3-29H17M-3-13H17M-3 3H17"/></g>'
                 + O(0, 48, "任务", 26, "#6C6D8C", "#fff", 4.2, "h", "middle"))
    return "".join(o)+'</g>'


def panel(x, y, w, h, r=10, fill="#fff", op=1.0):
    o = f' fill-opacity="{op}"' if op < 1 else ""
    return (R(x, y + 3, w, h, r, "#3C3442", extra=' opacity=".12"')
            + R(x, y, w, h, r, fill, LINE, 1.3, o))


def balloon(kind, x, y, w, text, size=18, stroke="#fff", tip=None):
    """按原生气泡轮廓重画：文字和边框都保持矢量，尺寸不受图集像素限制。"""
    colors = {"bal_blue": ("#49DAFF", "#00A9ED", "#1479AF"),
              "bal_green": ("#52EC70", "#04C932", "#158634"),
              "bal_yellow": ("#FFF8AC", "#F7D849", "#9D7E29"),
              "bal_orange": ("#FFD948", "#FF9D12", "#B86B14")}
    top, bot, edge = colors[kind]
    h, r = size + 18, (size + 18) / 2
    tail = f'H{w*.58+7}l3 8-13-8'
    if tip is not None:
        tx, ty = tip[0] - x, tip[1] - y
        stem = min(max(tx, r + 8), w - r - 8)
        tail = f'H{n(stem+7)}L{n(tx)} {n(ty)}L{n(stem-7)} {n(h)}'
    path = (f'M{r} 0H{w-r}a{r} {r} 0 0 1 0 {h}{tail}H{r}'
            f'a{r} {r} 0 0 1 0-{h}Z')
    return (f'<g transform="translate({n(x)} {n(y)})">'
            f'<path d="{path}" transform="translate(0 2)" fill="#433C48" opacity=".2"/>'
            f'<path d="{path}" fill="{lg([(0, top), (1, bot)])}" stroke="#69616D" stroke-width="4"/>'
            f'<path d="{path}" fill="none" stroke="{stroke}" stroke-width="2.4"/>'
            + O(w/2, h/2 + size*.36, text, size, "#fff", edge, 2.4, "h", "middle", w=w-18) + '</g>')


def avatar_photo(x, y, size, rotation=0):
    """把方形头像作为档案照片使用；保留完整图像，不再用圆形羽化模拟立绘。"""
    cid = uid("photo")
    return (f'<g transform="rotate({rotation} {n(x+size/2)} {n(y+size/2)})">'
            + R(x-7, y-3, size+14, size+14, 11, "#493C5B", extra=' opacity=".18"')
            + R(x-7, y-7, size+14, size+14, 11, "#fff", "#B2A3C5", 1.5)
            + f'<clipPath id="{cid}">{R(x, y, size, size, 5, "#fff")}</clipPath>'
            + f'<g clip-path="url(#{cid})"><use href="#av" transform="translate({n(x)} {n(y)}) scale({size/240:.5f})"/></g>'
            + R(x, y, size, size, 5, "none", "#D4CCDF", 1) + '</g>')


def action_title(cx, baseline, label, color, size=36, w=None):
    return outlined(cx, baseline, label, size,
                    [("#746573", 10, .22), (color, 8, 1), ("#fff", 5, 1)], color, "middle", w=w)


# ───────────────────────── 抓取 GitHub 数据 ─────────────────────────


def api(url, token=None, payload=None):
    headers = dict(UA, Accept="application/vnd.github+json")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(payload).encode() if payload is not None else None
    with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers), timeout=30) as r:
        return json.loads(r.read().decode())


def gql(query, token):
    res = api("https://api.github.com/graphql", token, {"query": query})
    if res.get("errors"):
        raise RuntimeError(res["errors"][0].get("message"))
    return res["data"]["user"]


def hd_avatar(raw):
    """保留 GitHub 原图；插值放大不能补回细节，还会引入二次 JPEG 压缩。"""
    mime = "image/png" if raw.startswith(b"\x89PNG") else "image/webp" if raw[8:12] == b"WEBP" else "image/jpeg"
    return raw, mime


REPO_FIELDS = ('nodes{name defaultBranchRef{name target{... on Commit{oid messageHeadline committedDate url}}} '
               'languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}} '
               'pageInfo{hasNextPage endCursor}')


def fetch_repo_commits_rest(login, repos, token):
    """无 GraphQL 凭据时，直接读取各项目默认分支头提交，不依赖有延迟的事件流。"""
    commits = {}
    for repo in repos:
        if repo['name'].casefold() == login.casefold() or not repo.get('default_branch'):
            continue
        branch = urllib.parse.quote(repo['default_branch'], safe='')
        try:
            rows = api(f"https://api.github.com/repos/{login}/{repo['name']}/commits?sha={branch}&per_page=1", token)
        except urllib.error.HTTPError as e:
            if e.code == 409:  # 空仓库没有提交。
                continue
            raise
        if rows:
            row = rows[0]
            commits[repo['name']] = {'sha': row['sha'], 'at': row['commit']['committer']['date'],
                                    'message': row['commit']['message'].splitlines()[0],
                                    'url': row['html_url'], 'branch': repo['default_branch']}
    return commits


def fetch(login, token, timezone_offset=8):
    u = api(f"https://api.github.com/users/{login}", token)
    repos, page = [], 1
    while True:
        batch = api(f"https://api.github.com/users/{login}/repos?per_page=100&type=owner&page={page}", token)
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    own = [r for r in repos if not r["fork"]]
    # 主页仓库每天被机器人推送，不能算作「最近活动」
    pushes = [r["pushed_at"] for r in repos if r.get("pushed_at") and r["name"].lower() != login.lower()]
    st = {"github": login, "profile_name": u.get("name") or login,
          "followers": u["followers"], "repos": u["public_repos"], "created": u["created_at"],
          "stars": sum(r["stargazers_count"] for r in own), "last_push": max(pushes, default=None),
          "repo_meta": {r["name"]: [r["stargazers_count"], r["language"], r["description"] or "", r["pushed_at"]]
                        for r in own if r["name"].lower() != login.lower()}}
    # 「正在培育」：最近一次推送提交的仓库（公开事件，只算自己的非 fork 仓库，跳过主页仓库），每次构建都重新取
    names = {r["name"].lower(): r["name"] for r in own if r["name"].lower() != login.lower()}
    try:
        ev = api(f"https://api.github.com/users/{login}/events/public?per_page=100", token)
        pushes = [(x["created_at"], x["repo"]["name"].split("/", 1)[1]) for x in ev
                  if x.get("type") == "PushEvent" and x["repo"]["name"].split("/", 1)[0].lower() == login.lower()
                  and x["repo"]["name"].split("/", 1)[1].lower() in names]
        if pushes:
            at, repo = max(pushes)
            st["last_commit"] = {"repo": names[repo.lower()], "at": at}
    except Exception as e:  # noqa: BLE001
        print("  ! 最近提交读取失败：", e)
    langs = {}
    st['repo_commits'] = {}
    if token:
        d = gql('{user(login:"%s"){pullRequests{totalCount} issues{totalCount} '
                'repositoriesContributedTo(contributionTypes:[COMMIT,ISSUE,PULL_REQUEST,REPOSITORY]){totalCount} '
                'contributionsCollection{contributionYears totalCommitContributions '
                'contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}} '
                'repositories(first:100,ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC){%s}}}'
                % (login, REPO_FIELDS), token)
        cc = d["contributionsCollection"]
        days = [[x["date"], x["contributionCount"]] for w in cc["contributionCalendar"]["weeks"]
                for x in w["contributionDays"]]
        tz = dt.timezone(dt.timedelta(hours=timezone_offset))
        now = dt.datetime.now(tz).replace(microsecond=0)
        # 首页保留滚动近一年；带年份的页面单独读取该自然年，跨年时也查询新年零值。
        year_numbers = sorted(set(cc["contributionYears"]) | {now.year})
        years = " ".join(
            f'y{y}:contributionsCollection(from:"{dt.datetime(y, 1, 1, tzinfo=tz).isoformat()}",'
            f'to:"{(now if y == now.year else dt.datetime(y+1, 1, 1, tzinfo=tz) - dt.timedelta(microseconds=1)).isoformat()}")'
            f'{{contributionCalendar{{totalContributions}}}}' for y in year_numbers)
        allc = gql('{user(login:"%s"){%s}}' % (login, years), token)
        st.update(commits=cc["totalCommitContributions"],
                  contrib_rolling_year=cc["contributionCalendar"]["totalContributions"],
                  contrib_year=allc[f"y{now.year}"]["contributionCalendar"]["totalContributions"],
                  contribution_year=now.year,
                  contrib_all=sum(v["contributionCalendar"]["totalContributions"] for v in allc.values()),
                  prs=d["pullRequests"]["totalCount"], issues=d["issues"]["totalCount"],
                  contributed=d["repositoriesContributedTo"]["totalCount"], days=days, langs_source="graphql")
        connection = d['repositories']
        nodes = list(connection['nodes'])
        while connection['pageInfo']['hasNextPage']:
            cursor = json.dumps(connection['pageInfo']['endCursor'])
            connection = gql('{user(login:"%s"){repositories(first:100,after:%s,ownerAffiliations:OWNER,'
                             'isFork:false,privacy:PUBLIC){%s}}}' % (login, cursor, REPO_FIELDS), token)['repositories']
            nodes.extend(connection['nodes'])
        for nd in nodes:
            branch = nd.get('defaultBranchRef')
            target = (branch or {}).get('target') or {}
            if nd['name'] in st['repo_meta'] and target.get('oid') and target.get('committedDate'):
                st['repo_commits'][nd['name']] = {
                    'sha': target['oid'], 'at': target['committedDate'], 'message': target.get('messageHeadline') or '',
                    'url': target.get('url') or '', 'branch': branch['name']}
            for e in nd["languages"]["edges"]:
                v = langs.setdefault(e["node"]["name"], [0, 0])
                v[0] += e["size"]
                v[1] += 1
    else:  # 没有 token：用每个仓库的主语言和仓库体积粗略估计
        st['repo_commits'] = fetch_repo_commits_rest(login, own, token)
        for r in own:
            if r["language"]:
                v = langs.setdefault(r["language"], [0, 0])
                v[0] += max(r["size"], 1) * 1024
                v[1] += 1
        st["langs_source"] = "rest"
    st["langs"] = langs
    try:
        with urllib.request.urlopen(urllib.request.Request(u["avatar_url"], headers=UA), timeout=30) as r:
            raw, mime = hd_avatar(r.read())
        st["avatar"] = f"data:{mime};base64," + base64.b64encode(raw).decode()
    except Exception as e:  # noqa: BLE001
        print("  ! 头像下载失败：", e)
    return st


def load_stats(cfg, offline, strict=False):
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    # A copied or renamed repository must never inherit somebody else's data.
    if cache.get("github", "").casefold() != cfg["github"].casefold():
        cache = {}
    if offline:
        if not cache:
            raise ValueError("没有当前账号的缓存；先联网构建，或用 --demo 查看离线示例")
        return cache
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise ValueError("联网构建需要 GITHUB_TOKEN（Actions 自动提供）；离线体验请用 --demo")
    try:
        fresh = fetch(cfg["github"], token, cfg.get("timezone_offset", 8))
    except Exception as e:  # noqa: BLE001
        if strict or "--strict-refresh" in sys.argv or not cache:
            raise RuntimeError("GitHub 数据刷新失败，保留已有缓存与页面") from e
        print("  ! 抓取失败，改用缓存：", e)
        return cache
    if fresh.get("langs_source") != "graphql" and cache.get("langs_source") == "graphql":
        fresh["langs"] = cache["langs"]  # 别用粗略数据覆盖精确数据
        fresh["langs_source"] = "graphql"
    keep = {"followers", "repos", "created", "stars", "last_push", "commits", "contrib_year", "contrib_all",
            "contrib_rolling_year", "contribution_year",
            "prs", "issues", "contributed", "days", "langs_source", "langs", "avatar", "repo_meta",
            "last_commit", "repo_commits", "github", "profile_name"}
    st = {k: v for k, v in fresh.items() if k in keep}
    CACHE.parent.mkdir(exist_ok=True)
    write_atomic(CACHE, json.dumps(st, ensure_ascii=False, indent=1))
    return st


# ───────────────────────── 把数据翻译成「游戏数值」 ─────────────────────────

RANKS = ["D", "C", "C+", "B", "B+", "A", "A+", "S", "SS"]
RANK_AT = [0, 50, 120, 250, 500, 900, 1500, 2500, 6000]


def next_goal(v, steps):
    return next((s for s in steps if s > v), steps[-1])


def streaks(days):
    cur = 0
    for i, (_d, k) in enumerate(reversed(days)):
        if k:
            cur += 1
        elif i:  # 今天还没提交不算断
            break
    best = run = 0
    for _d, k in days:
        run = run + 1 if k else 0
        best = max(best, run)
    return cur, best


def load_config(path=None):
    """读取项目页清单；首页最新项目独立来自 GitHub 提交数据。"""
    path = Path(path or ROOT / "config.json")
    cfg = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(cfg, dict):
        raise ValueError("config.json 必须是对象")
    if "projects_file" in cfg and not isinstance(cfg["projects_file"], str):
        raise ValueError("config.json: projects_file 必须是文件路径文字")
    if cfg.get("projects_file"):
        cfg["projects"] = json.loads((path.parent / cfg["projects_file"]).read_text(encoding="utf-8"))
    offset = cfg.get("timezone_offset", 8)
    if isinstance(offset, bool) or not isinstance(offset, (int, float)) or not -12 <= offset <= 14:
        raise ValueError("timezone_offset 必须是 -12 到 14 之间的小时数")
    for section, background in cfg.get("backgrounds", {}).items():
        if f"bg_{background}" not in GIDX:
            raise ValueError(f"backgrounds.{section}: 未知背景 {background}")
    for skill in cfg.get("skills", []):
        if skill.get("param") not in ORDER:
            raise ValueError("skills.param 必须是 Vo、Da、Vi、Me 之一")
        for icon in skill.get("icons", []):
            if icon not in ICON_DATA:
                raise ValueError(f"skills.icons: 未知图标 {icon}，可运行 --list-icons")
    for item in cfg.get("about", []):
        if item.get("icon") not in ICON_DATA and item.get("icon") not in OCTI:
            raise ValueError(f"about.icon: 未知图标 {item.get('icon')}，可运行 --list-icons")
    return cfg


def resolve_identity(cfg, username=None, demo=False):
    cfg = dict(cfg)
    login = username or cfg.get("github") or "auto"
    if demo:
        login = "demo-producer"
    elif login == "auto":
        login = os.environ.get("GITHUB_REPOSITORY_OWNER", "")
    if not isinstance(login, str) or not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", login):
        raise ValueError("请在 config.json 设置 github 用户名，或传入 --username；Actions 会自动识别仓库所有者")
    cfg["github"] = login
    return cfg


def demo_stats():
    """Synthetic data, including a generated avatar; never saved as a live cache."""
    from PIL import Image, ImageDraw
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date()
    rng = random.Random(283)
    days = [[(today-dt.timedelta(days=364-i)).isoformat(), rng.choice([0, 0, 1, 2, 3, 5, 8])]
            for i in range(365)]
    image = Image.new("RGB", (240, 240), "#f2eafa")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((24, 24, 216, 216), radius=42, fill="#b99bdc")
    draw.polygon([(120, 44), (140, 100), (196, 120), (140, 140),
                  (120, 196), (100, 140), (44, 120), (100, 100)], fill="#fff7df")
    output = io.BytesIO()
    image.save(output, "PNG")
    meta, commits = {}, {}
    for i, (name, language, description) in enumerate([
        ("starlight-notes", "Python", "把灵感记下来，慢慢做成喜欢的作品。"),
        ("tiny-garden", "TypeScript", "一个照顾日常、记录成长的小工具。"),
        ("paper-plane", "JavaScript", "探索界面、交互和有趣的小实验。"),
        ("after-school", "Go", "写给自己的自动化工具箱。"),
    ]):
        at = f"{today-dt.timedelta(days=i*2)}T03:00:00Z"
        meta[name] = [24-i*5, language, description, at]
        commits[name] = {"sha": str(i+1)*40, "at": at, "message": "Example commit", "branch": "main"}
    annual = sum(k for date, k in days if date.startswith(str(today.year)))
    return {"github": "demo-producer", "profile_name": "Your Name", "followers": 28, "repos": 12,
            "created": "2020-01-01T00:00:00Z", "stars": 66, "commits": 372,
            "contrib_year": annual, "contrib_rolling_year": sum(k for _, k in days),
            "contrib_all": 1283, "contribution_year": today.year, "prs": 18, "issues": 9,
            "days": days, "langs_source": "graphql",
            "langs": {"Python": [42000, 5], "TypeScript": [31000, 3], "JavaScript": [14000, 2], "Go": [9000, 1]},
            "repo_meta": meta, "repo_commits": commits,
            "avatar": "data:image/png;base64," + base64.b64encode(output.getvalue()).decode()}


def resolve_projects(cfg, meta, now, ago):
    settings = cfg.get("projects")
    if settings is None:  # 兼容已有 config.json 的 featured 字段。
        picks = cfg.get("featured", [{"repo": k} for k, _ in sorted(meta.items(), key=lambda kv: -kv[1][0])[:4]])
        settings = {"items": picks}
    if not isinstance(settings, dict):
        raise ValueError("projects.json 必须是对象")
    picks = settings.get("items")
    if picks is None:
        limit = settings.get("limit", 4)
        if type(limit) is not int or not 1 <= limit <= 20:
            raise ValueError("projects.json: limit 必须是 1 到 20 的整数")
        picks = [{"repo": k} for k, _ in sorted(meta.items(), key=lambda kv: (kv[1][3] or "", kv[0]), reverse=True)[:limit]]
    if not isinstance(picks, list):
        raise ValueError("projects.json: items 必须是项目数组或 null（自动选择）")
    catalog = {}
    for i, item in enumerate(picks):
        if not isinstance(item, dict) or not isinstance(item.get("repo"), str) or not item["repo"].strip():
            raise ValueError(f"projects.json: items[{i}].repo 必须是仓库名")
        repo = item["repo"].strip()
        if repo.casefold() in {key.casefold() for key in catalog}:
            raise ValueError(f"projects.json: 仓库 {repo} 重复")
        color = item.get("color", list(CARD)[i % len(CARD)])
        if not isinstance(color, str) or color not in CARD:
            raise ValueError(f"projects.json: {repo}.color 必须是 {', '.join(CARD)}")
        visible = item.get("show_on_projects", True)
        if not isinstance(visible, bool):
            raise ValueError(f"projects.json: {repo}.show_on_projects 必须为 true 或 false")
        for field in ("title", "description", "language"):
            if item.get(field) is not None and not isinstance(item[field], str):
                raise ValueError(f"projects.json: {repo}.{field} 必须是文字或 null")
        key = next((key for key in meta if key.casefold() == repo.casefold()), None)
        stars, lang, desc, pushed = (list(meta[key]) + [None])[:4] if key else (None, None, "", None)
        if key is None:
            print(f"  ! {repo} 暂无 GitHub 数据，使用配置内容；联网构建后可补全统计")
        fresh = bool(pushed) and (now - dt.datetime.fromisoformat(pushed.replace("Z", "+00:00"))).days < 7
        catalog[repo] = {"repo": repo, "name": item.get("title") or repo,
                         "stars": stars, "lang": item["language"] if item.get("language") is not None else lang,
                         "color": color, "desc": item["description"] if item.get("description") is not None else item.get("desc", desc),
                         "fresh": fresh, "ago": ago(pushed), "show_on_projects": visible}
    # 旧 home_recommendation 字段不再参与生成，也不能阻止 items 修改生效。
    return [item for item in catalog.values() if item["show_on_projects"]]


def derive(cfg, st):
    tz = dt.timezone(dt.timedelta(hours=cfg.get("timezone_offset", 8)))
    now = dt.datetime.now(tz)

    lc = cfg.get("languages", {})
    ex = set(lc.get("exclude", []))
    sw, cw = lc.get("size_weight", .5), lc.get("count_weight", .5)
    scores = {k: (v[0] ** sw) * (v[1] ** cw) for k, v in st.get("langs", {}).items() if k not in ex and v[0] > 0}
    total = sum(scores.values()) or 1
    langs = [{"name": k, "pct": s / total * 100, "key": ORDER[i]}
             for i, (k, s) in enumerate(sorted(scores.items(), key=lambda kv: -kv[1])[:4])]

    c = st.get("contrib_all") or st.get("contrib_year") or 0
    lv = max(1, math.isqrt(c))
    score = c + st.get("stars", 0) * 15 + st.get("followers", 0) * 10
    ri = max(i for i, t in enumerate(RANK_AT) if score >= t)

    days = st.get("days") or []
    cur, best = streaks(days)
    d30 = days[-30:]
    last_active = next((dd for dd, k in reversed(days) if k), None)
    week_start = (now.date() - dt.timedelta(days=now.weekday())).isoformat()
    week_total = sum(k for dd, k in days if week_start <= dd <= now.date().isoformat())

    excluded = {cfg.get("github", "").casefold()}
    repository = os.environ.get("GITHUB_REPOSITORY", "").split("/", 1)
    if len(repository) == 2 and repository[0].casefold() == cfg.get("github", "").casefold():
        excluded.add(repository[1].casefold())
    meta = {k: v for k, v in (st.get("repo_meta") or {}).items() if k.casefold() not in excluded}

    def ago(iso):
        if not iso:
            return "—"
        t = dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(tz)
        k = (now.date() - t.date()).days
        return "今天" if k <= 0 else "昨天" if k == 1 else f"{k} 天前" if k < 60 else t.strftime("%Y/%m/%d")

    featured = resolve_projects(cfg, meta, now, ago)
    latest_project = None
    commits = [(name, c) for name, c in (st.get('repo_commits') or {}).items()
               if name in meta and name.casefold() != cfg.get('github', '').casefold() and c.get('at') and c.get('sha')]
    if commits:
        name, commit = max(commits, key=lambda pair: (dt.datetime.fromisoformat(pair[1]['at'].replace('Z', '+00:00')), pair[0]))
        at = dt.datetime.fromisoformat(commit['at'].replace('Z', '+00:00')).astimezone(tz)
        latest_project = {'repo': name, 'name': name, 'stars': meta[name][0], 'lang': meta[name][1],
                          'fresh': (now - at).days < 7,
                          'commit_sha': commit['sha'], 'commit_message': ' '.join((commit.get('message') or '').split()),
                          'commit_url': commit.get('url') or '', 'commit_at': commit['at'],
                          'commit_time': f"{ago(commit['at'])} {at:%H:%M}"}
    # 「正在培育」：最近一次提交的仓库（取不到推送事件时，退回最近推送的仓库）
    lc = st.get("last_commit") or {}
    if lc.get("repo") in meta:
        act_name, act_at = lc["repo"], lc["at"]
    else:
        act_name, act_at = max(((k, v[3]) for k, v in meta.items()), key=lambda kv: kv[1] or "", default=(None, None))
    active = None
    if act_name:
        t_ = dt.datetime.fromisoformat(act_at.replace("Z", "+00:00")).astimezone(tz) if act_at else None
        active = {"name": act_name, "stars": meta[act_name][0], "lang": meta[act_name][1], "ago": ago(act_at),
                  "md": f"{t_.month}/{t_.day}" if t_ else ""}

    vals30 = [k for _d, k in d30]
    return {
        "date": now.strftime("%Y/%m/%d"), "year": st.get("contribution_year", now.year),
        "langs": langs, "contrib": c, "level": lv, "lv_prog": max(0, (c - lv * lv) / ((lv + 1) ** 2 - lv * lv)),
        "next_lv": (lv + 1) ** 2 - c, "score": score, "rank": RANKS[ri],
        "streak": cur, "best": best, "d30": d30, "sum30": sum(vals30), "max30": max(vals30 + [0]),
        "rest30": sum(1 for k in vals30 if not k), "week_total": week_total,
        "last_md": f"{int(last_active[5:7])}/{int(last_active[8:10])}" if last_active else "—",
        "cal": days[-35:], "featured": featured, "latest_project": latest_project, "active": active,
    }


# ───────────────────────── ① 主页（283 事务所） ─────────────────────────


def home(cfg, st, d):
    nick = cfg["nickname"]
    H = 680
    bgk = cfg.get("backgrounds", {}).get("home", "003")
    k = 1.22
    bw, bh = W * k, 640 * k
    o = [f'<g mask="url(#homeFade)"><g>{animT("translate", "0 0;-44 -16;0 0", 48)}'
         + gimg(f"bg_{bgk}", -(bw - W) / 2, -(bh - H) / 2 - 16, bw, bh) + "</g>"
         + R(0, 0, W, 130, 0, lg([(0, "#120E2A", .55), (1, "#120E2A", 0)]))
         + R(0, 430, W, 250, 0, lg([(0, "#1A1433", 0), (1, "#1A1433", .45)])) + "</g>"]
    for sx, sy, sr, sd in [(800, 110, 11, 0), (1112, 92, 8, 1.2), (744, 300, 7, 2.1), (948, 462, 9, .6),
                           (500, 90, 6, 1.7)]:
        o.append(sparkle(sx, sy, sr, "#FFF6D6", MOTION["ambient"], sd))

    # ── 顶部：名牌 + 数值条 + 等级 ──
    o.append(R(10, 12, 300, 46, 23, "#000", extra=' opacity=".22"') + R(10, 10, 300, 46, 23, "#fff", "#75697A", 2)
             + R(14, 14, 292, 38, 19, "none", "#E2DEE8", 1.2)
             + f'<circle cx="35" cy="33" r="19" fill="{lg([(0, "#A98BFF"), (1, "#FF8FC8")], 0, 0, 1, 1)}" '
             f'stroke="#fff" stroke-width="2"/>' + gimg("swan", 21, 20, 28, 26)
             + T(64, 27, "制作人", 13, SUB, "u") + T(64, 51, nick, 22, TITLE, "h", w=190)
             + T(64 + min(190, tw(nick, 22)) + 6, 51, "P", 16, SUB, "h"))
    # 数值条：统一的圆形图标压在深色条左端，数字右对齐、垂直居中
    stats = [("coin", st.get("stars", 0), 120), ("jewel", d["contrib"], 140), ("fan", st.get("followers", 0), 112)]
    x = 322
    for ico, val, w in stats:
        o.append(chip(x + 8, 16, w - 8) + (badge(ico, x + 17, 33, 17) if ico == "fan" else item(ico, x + 17, 33, 36))
                 + T(x + w - 14, 33 + 19 * .36, f"{val:,}", 19, "#fff", "u", "end", w=w - 54))
        x += w + 10
    lx, lw = 744, 380
    gx = lx + lw - 254
    o.append(chip(lx + 8, 16, lw - 8) + badge("trophy", lx + 17, 33, 17)
             + T(lx + 42, 33 + 20 * .36, f"Lv.{d['level']}", 20, "#fff", "h", w=gx - lx - 52)
             + R(gx, 20, 242, 26, 13, "#403545", "#776A7C", 1.1)
             + R(gx+2, 22, 238, 22, 11, "#5D4B68")
             + f'<clipPath id="lvClip"><rect x="{gx + 1}" y="21" width="{n(240 * d["lv_prog"])}" height="24">'
             f'{grow(240 * d["lv_prog"], 1.8)}</rect></clipPath>'
             + f'<g clip-path="url(#lvClip)">{R(gx+1, 21, 240, 24, 12, lg([(0, "#FFB30B"), (1, "#FF7D00")]))}</g>'
             + O(gx + 121, 33 + 14 * .36, f"下一级还差 {d['next_lv']}", 14, "#fff", "#4A3F4D", 3.2, "u", "middle",
                 w=220))

    # ── 左：制作人档案卡 ──
    cx0, cy0, cw, chh = 20, 78, 452, 338
    cid = uid("pc")
    o.append(R(cx0, cy0 + 4, cw, chh, 14, "#1A1433", extra=' opacity=".28"')
             + f'<clipPath id="{cid}">{R(cx0, cy0, cw, chh, 14, "#000")}</clipPath><g clip-path="url(#{cid})">'
             + R(cx0, cy0, cw, chh, 0, "#fff", extra=' opacity=".95"')
             + R(cx0, cy0, cw, 34, 0, lg([(0, "#B9A6F2"), (1, "#F4A6D7")], 0, 0, 1, 0)) + "</g>"
             + R(cx0, cy0, cw, chh, 14, "none", "#8E84A0", 1.5)
             + T(cx0 + 18, cy0 + 23, "制作人档案", 15, "#fff", "h")
             + gimg("swan", cx0 + cw - 44, cy0 + 4, 30, 27.5))
    ax, ay, asz = cx0 + 16, cy0 + 48, 146
    o.append(f'<clipPath id="pcAv">{R(ax, ay, asz, asz, 12, "#000")}</clipPath>'
             + R(ax - 3, ay - 3, asz + 6, asz + 6, 14, "#fff", "#B7AACB", 1.2)
             + f'<g clip-path="url(#pcAv)"><use href="#av" transform="translate({ax} {ay}) scale({asz / 240:.4f})"/></g>'
             + shine(ax, ay, asz, asz, 12, MOTION["shine"], 0, .25, 40))
    tx = ax + asz + 18
    tags = cfg.get("tags", [])
    o.append(T(tx, cy0 + 70, cfg.get("card_title", "闪耀编码者"), 15, PINK, "h", w=cx0 + cw - tx - 16)
             + T(tx - 2, cy0 + 122, nick, 44, TITLE, "h", w=cx0 + cw - tx - 14)
             + dotted(tx, cx0 + cw - 16, cy0 + 140)
             + T(tx, cy0 + 166, " ◇ ".join(tags), 15, TEXT, "u", w=cx0 + cw - tx - 16))
    # 语言胶囊（和技能页同一套胶囊），宽度按真实字宽算，放不下就整体缩字
    langs = d["langs"][:4]
    # pill() 接收中心 y；头像框底边是 cy0+197，标签顶边保留 16px。
    lx0, ly = cx0 + 16, cy0 + 228
    ls = 14
    while ls > 11 and sum(pill(0, 0, g["name"], LANG_SLUG.get(g["name"]), ls, 30)[1] for g in langs) \
            + 8 * (len(langs) - 1) > cw - 32:
        ls -= .5
    for lang in langs:
        svg_, lwid = pill(lx0, ly, lang["name"], LANG_SLUG.get(lang["name"]), ls, 30)
        o.append(svg_)
        lx0 += lwid + 8
    o.append(dotted(cx0 + 16, cx0 + cw - 16, cy0 + 256))
    cols = [("git-commit", "年提交", st.get("commits", 0)), ("git-pull-request", "PR", st.get("prs", 0)),
            ("issue-opened", "Issue", st.get("issues", 0)), ("repo", "仓库", st.get("repos", 0))]
    colw = (cw - 32) / len(cols)
    for i, (ic, lab, val) in enumerate(cols):
        x0 = cx0 + 16 + i * colw
        o.append(f'<circle cx="{n(x0 + 22)}" cy="{cy0 + 295}" r="17" fill="#F1ECFB" stroke="#CBBEE6" stroke-width="1.2"/>'
                 + octicon(ic, x0 + 22, cy0 + 295, 20, "#7B68B0")
                 + T(x0 + 46, cy0 + 296, f"{val:,}", 22, TITLE, "h", w=colw - 50)
                 + T(x0 + 46, cy0 + 314, lab, 13, SUB, "u"))
        if i:
            o.append(f'<path d="M{n(x0 - 2)} {cy0 + 274}V{cy0 + 318}" stroke="#D8D0E4" stroke-width="1.2"/>')

    # ── 左下：对话框（打字机效果） ──
    dx, dy, dw, dh = 16, 560, 684, 106
    lines = cfg.get("greeting", ["把喜欢的事，", "一点一点变成作品。"])[:2]
    o.append(R(dx, dy + 3, dw, dh, 14, "#1A1433", extra=' opacity=".25"')
             + R(dx, dy, dw, dh, 14, "#fff", extra=' opacity=".93"') + R(dx, dy, dw, dh, 14, "none", "#B8B2C6", 1.2))
    o.append('<clipPath id="twHome">'
             f'<rect x="{dx + 16}" y="{dy + 8}" width="640" height="32">{once("width", "0;640", 1.6)}</rect>'
             f'<rect x="{dx + 16}" y="{dy + 40}" width="640" height="32">{once("width", "0;0;640", 3.2, kt="0;.5;1")}</rect>'
             '</clipPath><g clip-path="url(#twHome)">'
             + "".join(T(dx + 26, dy + 33 + i * 31, ln, 22, "#4A4352", "u", w=620) for i, ln in enumerate(lines)) + "</g>")
    o.append(dotted(dx + 18, dx + dw - 18, dy + 80, "#8E879A", 1.4) + T(dx + 26, dy + 99, nick, 15, "#4A4352", "u")
             + f'<g>{animT("translate", "0 0;0 3;0 0", MOTION["float"])}{chevron(dx + dw - 30, dy + 62, 6, PINK)}</g>')

    # ── 右：标语（载入时依次滑入） ──
    for i, ln in enumerate(cfg.get("tagline", ["Code.", "Create.", "Cherish."])[:3]):
        tx_ = 828 + i * 22
        o.append(f'<g opacity="0">{enter(.3 + i * .28)}<g transform="translate({tx_} {146 + i * 74}) skewX(-10)">'
                 + outlined(0, 0, ln, 56, [("#fff", 14, .6), ("#7B55D6", 8, 1)], lg([(0, "#FFFFFF"), (1, "#F3E9FF")]),
                            w=W - 24 - tx_)
                 + "</g></g>")

    # ── 右中：最新项目与默认分支最新提交（独立于 items） ──
    top = d["latest_project"]
    if top:
        fx, fy, fw, fh = 772, 340, 350, 100
        o.append('<g id="latest-project"><title>' + esc(f"{top['name']} · 最近提交 {top['commit_time']}") + '</title>'
                 + R(fx, fy + 4, fw, fh, 12, "#1A1433", extra=' opacity=".28"') + R(fx, fy, fw, fh, 12, "#fff", "#8E84A0", 1.5)
                 + R(fx + 16, fy - 13, 108, 28, 14, lg([(0, "#FF8FC8"), (1, "#F2559A")]), "#fff", 2)
                 + T(fx + 70, fy + 6, "最新项目", 15, "#fff", "h", "middle")
                 + T(fx + 20, fy + 53, top["name"], 32, TITLE, "h", w=fw - 40)
                 + T(fx + 20, fy + 83, f"最近提交 · {top['commit_time']}", 13, SUB, 'u', w=fw - 115)
                 + item('coin', fx + fw - 65, fy + 78, 24)
                 + T(fx + fw - 20, fy + 83, f"× {top['stars'] if top['stars'] is not None else '—'}", 14, TEXT, 'u', 'end', w=32)
                 + (new_tag(fx + fw - 82, fy + 4, 20) if top['fresh'] else '') + '</g>')

    # ── 右下：原生 Produce 按钮 + 任务按钮（按原图尺寸显示，避免放大发糊） ──
    pcx, pcy, ps = 1032, 576, 148
    o.append(R(pcx - 86, 452, 172, 30, 15, lg([(0, "#FF8FC8"), (1, "#EE3F9F")]), "#fff", 2)
             + T(pcx, 472.5, cfg.get("produce_label", "个人创作 · 作品"), 15, "#fff", "h", "middle", w=150)
             + f'<path d="M{pcx - 7} 481L{pcx} 489L{pcx + 7} 481Z" fill="#EE3F9F"/>')
    o.append(f'<g transform="translate({pcx} {pcy})"><g>{animT("scale", "1;1.03;1", MOTION["pulse"])}'
             + home_action("produce", ps, st.get('repos', 0))
             + "</g></g>")
    o.append(f'<g transform="translate(882 600)"><g>{animT("scale", "1;1.025;1", MOTION["pulse"], 1.2)}'
             + home_action("mission", 112) + "</g></g>"
             + f'<g>{animT("translate", "0 0;0 -4.5;0 0", MOTION["float"])}'
             + red_badge(911, 553, f"本周 {d['week_total']}") + '</g>')
    return "".join(o), H


# ───────────────────────── ② 项目（偶像入口卡片） ─────────────────────────


DESC = 15.5  # 项目简介字号


def tile(x, y, w, h, f, idx, first=False):
    """横版项目卡：游戏菜单大字标题 + 完整简介 + 语言 / 最近更新。"""
    lt, lb, lo, bg, line = CARD[f["color"]]
    cid = uid("pj")
    star = OCTI["star-fill"]
    o = ['<g>',
         R(x + 4, y + 6, w - 8, h, 16, "#4B3F55", extra=' opacity=".14"') + R(x, y, w, h, 16, line),
         f'<clipPath id="{cid}">{R(x + 2.5, y + 2.5, w - 5, h - 5, 13.5, "#000")}</clipPath><g clip-path="url(#{cid})">'
         + R(x, y, w, h, 0, lg([(0, bg), (.62, "#FFFFFF")]))
         + R(x, y, w, h, 0, "url(#stripes)", extra=' opacity=".3"')
         + f'<path d="{star}" transform="translate({n(x + w - 150)} {n(y - 34)}) rotate(14) scale(4.8)" fill="#fff" opacity=".6"/>'
         + f'<path d="{star}" transform="translate({n(x + w - 232)} {n(y + 14)}) rotate(-12) scale(2.3)" fill="#fff" opacity=".5"/>'
         + "</g>" + R(x + 5, y + 5, w - 10, h - 10, 11, "none", "#fff", 1.6, ' opacity=".9"'),
         sparkle(x + w - 178, y + 30, 9, "#fff", MOTION["ambient"], idx * 1.6) + sparkle(x + w - 34, y + 62, 7, "#fff", MOTION["ambient"], idx * 1.6 + 2.4)]
    o.append(shine(x+6, y+6, w-12, 62, 10, MOTION["shine"], idx*1.6, .35, 46))
    o.append(logo(x + 26, y + 58, f["name"], 38, lg([(0, lt), (1, lb)]), lo, "start", w=w - 170))
    if f["stars"]:  # 金币角标
        sx_, sy_ = x + w - 84, y + 36
        o.append(R(sx_, sy_ - 14, 62, 28, 14, "#fff", line, 1.5) + item("coin", sx_ + 2, sy_, 30)
                 + T(sx_ + 40, sy_ + 17 * .36, str(f["stars"]), 17, TITLE, "h", "middle", w=30))
    # 简介面板：整段简介尽量完整显示，底部一行放语言和最近更新
    lines = f["_lines"]
    px, py, pw, ph = x + 14, y + 78, w - 28, h - 78 - 14
    o.append(R(px, py, pw, ph, 10, "#fff", extra=' opacity=".93"') + R(px, py, pw, ph, 10, "none", line, 1.2, ' opacity=".55"'))
    for i, ln in enumerate(lines):
        o.append(T(px + 18, py + 28 + i * 24, ln, DESC, "#4F4452", "u"))
    fy = py + ph - 16
    o.append(dotted(px + 16, px + pw - 16, fy - 18, "#DCD3E8"))
    if f.get("lang"):
        slug = LANG_SLUG.get(f["lang"])
        o.append((brand(slug, px + 26, fy - 4, 16) if slug else "")
                 + T(px + (40 if slug else 18), fy - 4 + 13 * .36, f["lang"], 13, TEXT, "u"))
    o.append(T(px + pw - 18, fy - 4 + 13 * .36, f"最近更新 · {f['ago']}", 13, SUB, "u", "end"))
    o.append("</g>")
    if first:
        bw = 160
        o.append(f'<g>{animT("translate", "0 0;0 -4.5;0 0", MOTION["float"])}'
                 + balloon("bal_orange", x + w - 84 - bw + 30, y - 48, bw, "人气上升中！", 16) + "</g>")
    return "".join(o)


def projects(y, d):
    o = [header(y, "项目")]
    fs = [dict(item) for item in d["featured"]]
    if not fs:
        return "".join(o), 70
    w, gap = 541, 18
    x0 = (W - (2 * w + gap)) / 2
    for f in fs:
        f["_lines"] = wrap(f["desc"] or "（暂无简介）", DESC, w - 28 - 36, 3)
    nl = max(len(f["_lines"]) for f in fs)
    h = 78 + 28 + (nl - 1) * 24 + 14 + 34 + 14
    top = max(range(len(fs)), key=lambda i: fs[i]["stars"] or 0)
    y0 = y + 108
    for i, f in enumerate(fs):
        o.append(tile(x0 + (i % 2) * (w + gap), y0 + (i // 2) * (h + 22), w, h, f, i, i == top and bool(fs[i]["stars"])))
    rows = (len(fs) + 1) // 2
    return "".join(o), 108 + rows * h + (rows - 1) * 22


# ───────────────────────── ③ 培育（W.I.N.G. 培育主界面） ─────────────────────────


def calendar_heat(d, x, y, s):
    """在原生台历的格子区画贡献热力（透视用仿射变换贴合）。"""
    o = [f'<g transform="translate({n(x)} {n(y)}) scale({s})">',
         '<path d="M139 34L237 26L249 150L151 158Z" fill="#fff"/>']
    cols, rows = 7, 5
    mt = "matrix(13 -1.05 2.3 21.6 142 39)"
    o.append(f'<g transform="{mt}">'
             f'<rect x="0" y="0" width="7" height=".42" fill="#F7A8CF"/>')
    days = d["cal"]
    if days:
        off = dt.date.fromisoformat(days[0][0]).weekday()
        for i, (_date, k) in enumerate(days):
            j = i + off
            c, r = j % cols, j // cols
            if r >= rows:
                break
            col = ("#FCEAF3" if k == 0 else "#F8C1DA" if k == 1 else "#F28DBB" if k <= 3 else "#EC5E9E" if k <= 7
                   else "#D93583")
            cell = (f'<rect x="{c + .07}" y="{.52 + r * 1.0 + .06:.2f}" width=".86" height=".86" rx=".12" fill="{col}"')
            if i == len(days) - 1:
                cell += f' stroke="{PINK}" stroke-width=".12">{anim("stroke-opacity", "1;.3;1", MOTION["pulse"])}</rect>'
            else:
                cell += "/>"
            o.append(cell)
    o.append("</g></g>")
    return "".join(o)


TABLET_SCREEN = [(54, 17), (235, 55), (204, 184), (22, 146)]  # 原生屏幕边缘，顺时针


def project_quad(q, w, h):
    """矩形到屏幕四角的单应变换。所有排行条、字形、徽章共享同一个平面。"""
    (ax, ay), (bx, by), (cx, cy), (dx, dy) = q
    dx1, dy1, dx2, dy2 = bx-cx, by-cy, dx-cx, dy-cy
    dx3, dy3 = ax-bx+cx-dx, ay-by+cy-dy
    det = dx1*dy2-dx2*dy1
    if abs(det) < 1e-9:
        raise ValueError("平板屏幕的四角不能退化为直线")
    g, hh = (dx3*dy2-dx2*dy3)/det, (dx1*dy3-dx3*dy1)/det
    a, b, d, e = bx-ax+g*bx, dx-ax+hh*dx, by-ay+g*by, dy-ay+hh*dy

    def at(x, y):
        u, v = x/w, y/h
        z = g*u+hh*v+1
        return ((a*u+b*v+ax)/z, (d*u+e*v+ay)/z)
    return at


def project_path(path, at, x=0, y=0, scale=1):
    """将曲线细分后投影成矢量路径，避免 SVG 的二维矩阵丢失透视。"""
    from fontTools.pens.basePen import BasePen
    from fontTools.svgLib.path import parse_path

    class Pen(BasePen):
        def __init__(self):
            super().__init__(None)
            self.parts = []

        def point(self, p):
            px, py = at(x+p[0]*scale, y+p[1]*scale)
            return f"{px:.2f} {py:.2f}"

        def _moveTo(self, p):
            self.parts.append("M"+self.point(p))

        def _lineTo(self, p):
            self.parts.append("L"+self.point(p))

        def _curveToOne(self, p1, p2, p3):
            p0 = self._getCurrentPoint()
            for i in range(1, 13):
                t, s = i/12, 1-i/12
                self._lineTo(tuple(s**3*p0[k]+3*s*s*t*p1[k]+3*s*t*t*p2[k]+t**3*p3[k] for k in (0, 1)))

        def _qCurveToOne(self, p1, p2):
            p0 = self._getCurrentPoint()
            for i in range(1, 9):
                t, s = i/8, 1-i/8
                self._lineTo(tuple(s*s*p0[k]+2*s*t*p1[k]+t*t*p2[k] for k in (0, 1)))

        def _closePath(self):
            self.parts.append("Z")

        def _endPath(self):
            pass
    pen = Pen()
    parse_path(path, pen)
    return "".join(pen.parts)


def trend_tablet(d, x, y):
    """照原生平板重画外壳，排行和文字使用同一个透视投影，始终不越出屏幕。"""
    at = project_quad(TABLET_SCREEN, 200, 150)
    screen = 'M54 17L235 55L204 184L22 146Z'
    cid = uid("screen")
    o = [f'<g transform="translate({x} {y})">',
         '<path d="M216 139L257 211Q258 216 251 219L215 231L196 195Z" fill="#26262C" stroke="#54545B" stroke-width="2"/>',
         '<path d="M43 3Q45-1 52 1L251 42Q259 44 256 53L220 201Q219 207 211 205L8 162Q1 160 3 152Z" '
         f'fill="{lg([(0, "#505056"), (1, "#2B2B30")])}" stroke="#64646B" stroke-width="2"/>',
         f'<path d="{screen}" fill="{lg([(0, "#FFF8FF"), (1, "#E6DDF9")])}" stroke="#15151A" stroke-width="1.5"/>',
         '<path d="M29 86L25 104" stroke="#8E8E96" stroke-width="2.4" stroke-linecap="round"/>',
         f'<clipPath id="{cid}"><path d="{screen}"/></clipPath><g clip-path="url(#{cid})">']

    def shape(path, fill, ox=0, oy=0, scale=1, stroke=None, sw=1):
        extra = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        return f'<path d="{project_path(path, at, ox, oy, scale)}" fill="{fill}"{extra}/>'

    def label(text, px, py, size, fill, maxw):
        tp = text_path(text, fit(text, size, maxw))
        if not tp:
            raise RuntimeError("平板排行需要 fonttools 和 brotli：pip install fonttools brotli")
        return shape(tp[0], fill, px, py, tp[3])

    medals = ["#CA971F", "#8C8E9D", "#B17841"]
    for i, lang in enumerate(d["langs"][:3]):
        ry = 12+i*44
        _lab, bd, top, bot, main = PARAM[lang["key"]]
        row = 'M10 0H176Q184 0 184 8V26Q184 34 176 34H10Q2 34 2 26V8Q2 0 10 0Z'
        medal = 'M0-12A12 12 0 1 1 0 12A12 12 0 1 1 0-12Z'
        o.append('<g>'+shape(row, lg([(0, top), (1, main)]), 6, ry, stroke="#fff", sw=1.2)
                 + shape(medal, medals[i], 25, ry+17, stroke="#fff", sw=1.4)
                 + label(str(i+1), 20, ry+23, 17, "#fff", 12)
                 + label(lang["name"], 46, ry+23, 16, "#fff", 100)
                 + label(PARAM[lang["key"]][0], 155, ry+24, 19, "#fff", 32) + '</g>')
    o.append('</g></g>')
    return "".join(o)


def producing_bar(x, y, h, d, right=False):
    """培育页顶栏：正在培育的项目（最近一次提交的仓库）+ 最近提交时间，照游戏表头样式（白底深框 + 左上深色页签）。"""
    a = d.get("active")
    if not a:
        return ""
    slug = LANG_SLUG.get(a["lang"] or "")
    nx = x + (48 if slug else 18)
    nw = min(tw(a["name"], 24), 230)
    s1 = nx + nw + (44 + tw(str(a["stars"]), 16) if a["stars"] else 18)  # 分隔线
    w = s1 + 150 - x
    if right:
        shift = W - 18 - (x+w)
        x, nx, s1 = x+shift, nx+shift, s1+shift
    o = [R(x, y + 3, w, h, 10, "#2E2236", extra=' opacity=".22"'), R(x, y, w, h, 10, "#4F4757"),
         R(x + 2, y + 2, w - 4, h - 4, 8, lg([(0, "#FFFFFF"), (1, "#ECE9F3")])),
         f'<path d="M{n(x + 2)} {n(y + 10)}a8 8 0 0 1 8-8H{n(x + 132)}L{n(x + 116)} {n(y + 24)}H{n(x + 2)}Z" fill="#4F4757"/>',
         T(x + 13, y + 18.5, "正在培育", 13, "#fff", "h"), shine(x + 2, y + 2, w - 4, h - 4, 8, MOTION["shine"], 2.4, .25, 40),
         f'<path d="M{n(s1)} {y + 12}V{y + h - 12}" stroke="#B3ACBC" stroke-width="1.4" stroke-dasharray="1.5 3.5" '
         f'stroke-linecap="round"/>']
    if slug:
        o.append(brand(slug, x + 30, y + 44, 22))
    o.append(T(nx, y + 44 + 24 * .36, a["name"], 24, TITLE, "h", w=230))
    if a["stars"]:
        o.append(item("coin", nx + nw + 20, y + 44, 24) + T(nx + nw + 36, y + 44 + 16 * .36, str(a["stars"]), 16, TITLE, "h"))
    o.append(T(s1 + 18, y + 28, f"最近提交 · {a['md']}" if a["md"] else "最近提交", 13, SUB, "h")
             + T(s1 + 18, y + 54, a["ago"], 22, PINK, "h", w=w - (s1 - x) - 34))
    return "".join(o)


def produce(y, cfg, st, d):
    H = 640
    bgk = cfg.get("backgrounds", {}).get("produce", "001")
    k = 1.3
    DEFS["prFade"] = (f'<mask id="prFade"><rect y="{y}" width="{W}" height="{H}" '
                      f'fill="{lg([(0, "#000"), (.06, "#fff"), (1, "#fff")])}"/></mask>')
    o = [f'<clipPath id="prClip"><rect y="{y}" width="{W}" height="{H}"/></clipPath>'
         f'<g clip-path="url(#prClip)"><g mask="url(#prFade)"><g>{animT("translate", "0 0;-32 -8;0 0", 44)}'
         + gimg(f"bg_{bgk}", -160, y - 66, W * k, 640 * k) + "</g></g>"]
    # 人物位于桌后，桌沿遮住下半身；电脑底边落在桌沿，不再放独立相框。
    for sx, sy, sr, phase in [(280, 170, 4, 0), (832, 290, 5, 2.4), (300, 330, 3, 4.8)]:
        o.append(sparkle(sx, y+sy, sr, "#FFF8DC", MOTION["ambient"], phase))
    o.append(hana_coding(y, cfg) + gimg("desk", 0, y + 543, W, 97) + "</g>")

    # 顶部：标题 + 「正在培育」信息条（最近一次推送的仓库：名字 / 简介 / 最近更新）
    o.append(header(y + 8, "培育"))
    o.append(producing_bar(0, y + 10, 64, d, right=True))

    # 左右：圆形菜单按钮（矢量重绘，原图上的字放大后发糊）
    o.append(round_btn(66, y + 130, "确认队伍", "people") + round_btn(66, y + 238, "道具", "bag")
             + round_btn(1070, y + 136, "返回主界面", "house") + round_btn(1070, y + 244, "设置", "gear"))

    # 桌上：台历（贡献日历）/ 马克杯 / 资料 / 平板（语言排行）
    cs = .92
    o.append(gimg("calendar", 22, y + 400, 259 * cs, 211 * cs) + calendar_heat(d, 22, y + 400, cs))
    o.append(gimg("mug", 314, y + 462, 139, 151)
             + gimg("papers_plain", 624, y + 535, 267.3, 83.7)
             + trend_tablet(d, 858, y + 392))
    o.append(mug_steam(350, y+483))
    # 提示直接写明时间与数值，和相应道具绑定；去掉散落在按钮上下的灰色小字。
    o.append(f'<g>{animT("translate", "0 0;0 -4.5;0 0", MOTION["float"])}'
             + balloon("bal_blue", 278, y+398, 158, f"近30天 · {d['rest30']} 天", 16) + '</g>')
    o.append(f'<g>{animT("translate", "0 0;0 -4.5;0 0", MOTION["float"], 1.2)}'
             + balloon("bal_green", 675, y+524, 164, f"近30天 · {d['sum30']} 次", 16) + '</g>')
    for cx, label, color, width in [(143, "培育", "#EF50AF", 200), (383, "休息", "#16AEEC", 138),
                                     (758, "回顾", "#AF52EC", 168), (988, "确认流行", "#6DBF28", 240)]:
        o.append(action_title(cx, y+609, label, color, 36 if len(label)==2 else 30, width))
    summary = f"{d['year']} 年贡献 {st.get('contrib_year', 0):,} 次"
    o.append(R(23, y+618, 240, 20, 10, lg([(0, "#FF8BC2"), (1, "#E8358D")]), "#fff", 1.3)
             + T(143, y+632, summary, 12.5, "#fff", "h", "middle", w=222))
    return "".join(o), H


# ───────────────────────── ④ 制作人详情 ─────────────────────────


def detail(y, cfg, st, d):
    nick = cfg["nickname"]
    o = [header(y, "制作人详情")]
    P = y + 66
    # 左：制作人档案卡 + 语言（Vo/Da/Vi/Me）
    o.append(panel(14, P, 566, 392))
    fx, fy, fw, fh = 24, P + 10, 546, 270
    o.append(f'<clipPath id="illust">{R(fx, fy, fw, fh, 6, "#000")}</clipPath><g clip-path="url(#illust)">'
             + gimg("bg_035", fx - 6, fy - 12, fw + 12, (fw + 12) * 640 / 1136))
    o.append(R(fx, fy, fw, fh, 0, lg([(0, "#FFFFFF", .55), (1, "#FFFFFF", 0)], 0, 0, 1, 0))
             + T(fx+26, fy+36, "PRODUCER CARD", 13, "#997EAF", "h")
             + gimg("swan", fx+28, fy+53, 51, 47)
             + avatar_photo(fx+fw-208, fy+39, 178, -3)
             + R(fx+fw-214, fy+224, 194, 25, 12.5, "#fff", "#C8B6DF", 1)
             + T(fx+fw-117, fy+241, "制作人 · P", 13, "#8E6EB2", "h", "middle"))
    for sx, sy, r, dl in [(fx + 276, fy + 56, 9, 0), (fx + 287, fy + 226, 7, 1.2), (fx + 235, fy + 96, 6, 2)]:
        o.append(sparkle(sx, sy, r, "#fff", MOTION["ambient"], dl))
    o.append(O(fx + 26, fy + 135, cfg.get("card_title", "闪耀编码者"), 17, "#fff", "#9562C4", 4.4, "h")
             + logo(fx + 24, fy + 190, nick, 40, lg([(0, "#FFFFFF"), (.5, "#FFD4EF"), (1, "#C1E6FF")]),
                    "#8962C7", "start", w=274)
             + T(fx+26, fy+225, "@"+cfg["github"], 16, "#8A739B", "u", w=274) + "</g>"
             + shine(fx, fy, fw, fh, 6, MOTION["shine"], 1.2, .32, 80)
             + R(fx, fy, fw, fh, 6, "none", "#fff", 3) + R(fx - 1.5, fy - 1.5, fw + 3, fh + 3, 7, "none", "#8E84A0", 1))
    # 档案照片下方两行语言（卡面止于 P+280，面板止于 P+392）。
    for i, lang in enumerate(d["langs"][:4]):
        cx_ = 34 if i % 2 == 0 else 304
        cy_ = P + 309 + (i // 2) * 42
        slug = LANG_SLUG.get(lang["name"])
        o.append(param_badge(lang["key"], cx_ + 16, cy_, 16)
                 + (brand(slug, cx_ + 52, cy_, 18, PARAM[lang["key"]][4]) if slug else "")
                 + T(cx_ + 68, cy_ + 16 * .36, lang["name"], 16, TEXT, "u", w=110)
                 + T(cx_ + 254, cy_ + 22 * .36, f"{lang['pct']:.0f}%", 22, TITLE, "h", "end", w=56)
                 + dotted(cx_, cx_ + 254, cy_ + 20, "#C9B9DF"))

    # 右：技能（技术栈）
    o.append(panel(592, P, 530, 392))
    o.append(tab(604, P + 12, 104, 42, "技能", "magenta", 19) + tab(714, P + 12, 120, 42, "资料", "lav", 19))
    # 每个分类：游戏技能一览样式的分类条 + 一行技术栈胶囊（单色 logo + 名字，标签同款无 logo）
    for i, sk in enumerate(cfg.get("skills", [])[:4]):
        ry = P + 66 + i * 80
        o.append(ribbon(604, ry, 506, 28, sk["name"], 16))
        items = [(ICON_DATA[g]["name"], g) for g in sk.get("icons", []) if g in ICON_DATA]
        items += [(t, None) for t in sk.get("tags", [])]
        ps = 13.5
        while ps > 11 and sum(pill(0, 0, lab, g, ps, 28)[1] for lab, g in items) + 8 * (len(items) - 1) > 506:
            ps -= .5
        ix = 604
        for lab, g in items:
            svg_, w_ = pill(ix, ry + 52, lab, g, ps, 28)
            o.append(svg_)
            ix += w_ + 8
    return "".join(o), 66 + 392


# ───────────────────────── ⑤ 任务（贡献动态） ─────────────────────────


def contrib_chart(d, x, y, w, h):
    """底图始终完整可读；描线强调循环播放，晚滚动到这里也能看到。"""
    pts = d["d30"] or [["", 0]]
    mx = max(d["max30"], 1)
    top = mx + (2 if mx < 6 else mx // 4)
    x0, x1, base, ytop = x + 40, x + w - 16, y + h - 30, y + 28
    xy = [(x0 + (x1 - x0) * i / max(1, len(pts) - 1), base - (base - ytop) * k / top) for i, (_d, k) in enumerate(pts)]
    o = []
    for v in sorted({0, top // 2, top}):
        gy = base - (base - ytop) * v / top
        dash = "" if v == 0 else ' stroke-dasharray="4 4"'
        o.append(f'<path d="M{n(x0)} {n(gy)}H{n(x1)}" stroke="#E6E0EE" stroke-width="1.2"{dash}/>'
                 + T(x0 - 10, gy + 4.5, str(v), 13, SUB, "u", "end"))
    for i, (dd, _k) in enumerate(pts):
        if dd and (i % 5 == 0 or i == len(pts) - 1):
            o.append(T(xy[i][0], base + 22, f"{int(dd[5:7])}/{int(dd[8:10])}", 13, SUB, "u", "middle"))
    line = "M" + "L".join(f"{n(px)} {n(py)}" for px, py in xy)
    cycle = MOTION["chart"]
    o.append(f'<path d="{line}L{n(x1)} {n(base)}L{n(x0)} {n(base)}Z" '
             f'fill="{lg([(0, "#FF8CC6", .5), (1, "#FF8CC6", .04)])}"/>'
             f'<path id="contrib-line-base" d="{line}" fill="none" stroke="#F2559A" stroke-width="3" '
             'stroke-linejoin="round" stroke-linecap="round"/>')
    # 只有上层强调线会重置，底线、面积和数据点从不清空。
    # 先淡出再重置 dashoffset，避免循环交界出现倒着擦除的闪烁。
    o.append(f'<path id="contrib-line-replay" d="{line}" fill="none" stroke="#D91D7A" stroke-width="3.8" '
             'stroke-linejoin="round" stroke-linecap="round" pathLength="1" '
             'stroke-dasharray="1" stroke-dashoffset="1" opacity="0">'
             + anim("stroke-dashoffset", "1;0;0;1;1", cycle, kt="0;.5;.84;.85;1", ease=False)
             + anim("opacity", "0;1;1;0;0", cycle, kt="0;.04;.7;.84;1") + '</path>')
    for (px, py), (_d, k) in zip(xy, pts):
        if not k:
            continue
        o.append(f'<circle cx="{n(px)}" cy="{n(py)}" r="4" fill="#fff" stroke="#F2559A" stroke-width="2.2"/>')
    o.append('<circle r="4" fill="#fff" stroke="#D91D7A" stroke-width="1.8">'
             f'<animateMotion path="{line}" dur="{cycle:g}s" repeatCount="indefinite" '
             'calcMode="linear" keyPoints="0;1;1" keyTimes="0;.5;1"/>'
             + anim("opacity", "0;1;1;0;0", cycle, kt="0;.04;.47;.52;1") + '</circle>')
    if d["max30"]:
        i = max(range(len(pts)), key=lambda j: (pts[j][1], j))
        px, py = xy[i]
        bx = min(max(px - 58, x0), x1 - 116)
        # 气泡整体保持轻微浮动；尖角横向对齐最高点，靠边时只调整本体位置。
        o.append('<g id="contrib-peak-label">'
                 + animT("translate", "0 0;0 -4.5;0 0", MOTION["float"])
                 + balloon("bal_yellow", bx, py - 54, 116, f"最高 {d['max30']} 次", 16,
                           tip=(px, py - 6)) + "</g>")
    px, py = xy[-1]
    o.append(f'<circle cx="{n(px)}" cy="{n(py)}" r="6" fill="none" stroke="{PINK}" stroke-width="2">'
             + anim("r", "5;10;5", MOTION["pulse"]) + anim("opacity", ".6;0;.6", MOTION["pulse"]) + "</circle>")
    return "".join(o)


def mission(y, st, d):
    o = [header(y, "任务")]
    C = y + 66
    ch = 300
    total = ch + 14 + 120
    o.append(R(0, C - 8, 178, total + 16, 0, SIDE) + R(178, C - 8, 3, total + 16, 0, "#fff")
             + R(181, C - 8, 1.2, total + 16, 0, "#C4C1CA"))
    o.append(tab(15, C + 10, 148, 56, "每日任务", "pink", 24) + tab(15, C + 80, 148, 56, "每周任务", "lav", 24)
             + tab(15, C + 150, 148, 56, "特别任务", "yellow", 24)
             + red_badge(160, C + 12, str(d["streak"]) if d["streak"] else "0", 12))
    o.append(panel(194, C, 928, ch))
    avg = d["sum30"] / max(1, len(d["d30"]))
    o.append(f'<circle cx="222" cy="{C + 30}" r="16" fill="#FDE3F0" stroke="#F4A6CB" stroke-width="1.2"/>'
             + octicon("graph", 222, C + 30, 18, PINK)
             + T(248, C + 37, "近 30 天贡献", 20, TITLE, "h")
             + T(1102, C + 36, f"共 {d['sum30']} 次 · 日均 {avg:.1f} 次", 16, TEXT, "u", "end", w=300)
             + dotted(210, 1106, C + 54))
    o.append(contrib_chart(d, 206, C + 70, 904, ch - 82))
    ry = C + ch + 14
    # 黄色任务行矢量化；三格里的图标中心与两行文字的整体中心同高。
    o.append(panel(194, ry, 928, 120, 11, lg([(0, "#FFFAC8"), (.5, "#FFFFEC"), (1, "#FFF5BF")])))
    for sx, sy, sr in [(218, ry+27, 14), (474, ry+80, 10), (738, ry+28, 11), (1094, ry+83, 17)]:
        o.append(spark(sx, sy, sr, "#F5D270", .24))
    cells = [("flame", "当前连续", f"{d['streak']} 天"), ("trophy", "最长连续", f"{d['best']} 天"),
             ("jewel", f"{d['year']} 年贡献", f"{st.get('contrib_year', 0):,} 次")]
    cw = 928 / 3
    my = ry + 58
    for i, (ico, lab, val) in enumerate(cells):
        cx = 194 + i * cw
        if ico == "flame":
            o.append(f'<g transform="translate({n(cx + 62)} {my})"><g>{animT("scale", "1;1.045;1", MOTION["pulse"])}'
                     + badge(ico, 0, 0, 27) + "</g></g>")
        elif ico == "jewel":  # 原生羽石
            o.append(item("jewel", cx + 62, my, 56))
        else:
            o.append(badge(ico, cx + 62, my, 27))
        o.append(T(cx + 104, my - 11, lab, 15, SUB, "h") + T(cx + 104, my + 22, val, 30, TITLE, "h", w=cw - 122))
        if i:
            o.append(f'<path d="M{n(cx)} {ry + 24}V{ry + 94}" stroke="#D8C9A0" stroke-width="1.4" stroke-dasharray="2 4"/>')
    return "".join(o), 66 + total + 8


# ───────────────────────── ⑥ 关于（帮助弹窗） ─────────────────────────


def about(y, cfg):
    nick = cfg["nickname"]
    lines = cfg.get("about", [])
    x, w = 64, W - 128
    band_h = len(lines) * 40 + 20
    body = 78 + band_h + 50 + 96
    H = 66 + body
    o = [R(x, y + 4, w, H, 6, "#3C3442", extra=' opacity=".2"'), R(x, y, w, H, 6, "#fff", "#6B6670", 2)]
    o.append(f'<clipPath id="hdClip">{R(x + 1, y + 1, w - 2, 66, 5, "#000")}</clipPath><g clip-path="url(#hdClip)">'
             + R(x, y, w, 66, 0, lg([(0, "#8DEB80"), (1, "#4CC94A")]))
             + "".join(f'<g transform="translate({x + 300 + k * 150} {y + 30 + (k % 2) * 14})"><g>'
                       + animT("rotate", "0;360", 32 + k * 6.4, k * 6.4, ease=False)
                       + f'<path d="{SPARK}" transform="scale({20 + (k % 3) * 8})" fill="#fff" opacity=".2"/></g></g>'
                       for k in range(5)) + "</g>")
    o.append(f'<clipPath id="abAv"><circle cx="{x + 52}" cy="{y + 28}" r="34"/></clipPath>'
             f'<circle cx="{x + 52}" cy="{y + 28}" r="37" fill="#fff" stroke="#6B6670" stroke-width="1.5"/>'
             f'<g clip-path="url(#abAv)"><use href="#av" transform="translate({x + 18} {y - 6}) scale({68 / 240:.4f})"/></g>'
             + sparkle(x + 98, y + 18, 9, "#fff", MOTION["ambient"], 0))
    ttl = f"关于 {nick}"
    o.append(outlined(x + 122, y + 45, ttl, 29, [("#fff", 12, 1), ("#2F9A37", 7, 1)], "#fff", w=700))
    o.append(O(x + w - 26, y + 47, "1/1", 30, "#fff", "#2F9A37", 6, "h", "end"))
    B = y + 66
    o.append(R(x + 10, B + 10, w - 20, body - 20, 6, "none", "#E4E3EA", 2))
    o.append(RT(W / 2, B + 52, cfg.get("about_title", "用代码，创造[闪耀]的每一天"), 26, TITLE, cls="h", anchor="middle",
                w=w - 80))
    o.append(R(x + 16, B + 74, w - 32, band_h, 0, "#F1F0F4"))
    cols = ["#F2559A", "#4C8DF0", "#F0A21A", "#A57BE8", "#4CC15A"]
    for i, ln in enumerate(lines):
        ly = B + 74 + 10 + 27 + i * 40
        ic = ln.get("icon", "star")
        o.append(f'<circle cx="{x + 58}" cy="{ly - 7}" r="16" fill="#fff" stroke="{cols[i % 5]}" stroke-width="2"/>'
                 + (brand(ic, x + 58, ly - 7, 19, cols[i % 5]) if ic in ICON_DATA else
                    octicon(ic, x + 58, ly - 7, 18, cols[i % 5]) if ic in OCTI else "")
                 + RT(x + 86, ly, ln["text"], 18.5, "#4F4452", w=w - 124))
    if cfg.get("speaks"):
        o.append(T(W / 2, B + 74 + band_h + 36, cfg["speaks"], 19, TEXT, "h", "middle"))
    by = B + body - 92
    for bx, dirx in ((W / 2 - 250, -1), (W / 2 + 172, 1)):  # 翻页箭头和「关闭」用同一套按钮样式
        acx, acy = bx + 39, by + 33
        o.append(button(bx, by, 78, 66, "lav", r=10)
                 + f'<path d="M{n(acx - 5 * dirx)} {n(acy - 11)}L{n(acx + 6 * dirx)} {n(acy)}L{n(acx - 5 * dirx)} '
                 f'{n(acy + 11)}" fill="none" stroke="{TITLE}" stroke-width="4.2" stroke-linecap="round" '
                 f'stroke-linejoin="round"/>')
    o.append(button(W / 2 - 92, by, 184, 66, "lav", "关闭", 25, r=10))
    for sx, sy, r, c, dl in [(x + 40, B + body - 40, 22, "#E8E6EE", 0), (x + 76, B + body - 70, 9, "#F5B8D6", 1),
                             (x + w - 44, B + 40, 20, "#E8E6EE", .5), (x + w - 70, B + 90, 8, "#9FD6FF", 1.5),
                             (x + w - 40, B + body - 50, 12, "#FFD978", 2)]:
        o.append(sparkle(sx, sy, r, c, MOTION["ambient"], dl))
    return "".join(o), H


# ───────────────────────── ⑦ 叶月的提示条 ─────────────────────────


def footer(y, d):
    """提示条本体用矢量画（任意宽度都清晰），左端叠原图里的叶月（1:1 显示，右缘渐隐接进条里）。"""
    bw, bh = 720, 86
    gx = (W - (52 + bw)) / 2
    bx = gx + 52  # 原图里条从 x=52 开始
    lines = ["制作人，今天也辛苦了！", f"数据每天自动更新 · 最后更新 {d['date']}"]
    DEFS["hzFade"] = (f'<mask id="hzFade"><rect x="{n(gx)}" y="{y}" width="108" height="108" '
                      f'fill="{lg([(0, "#fff"), (.86, "#fff"), (1, "#000")], 0, 0, 1, 0)}"/></mask>')
    tx = gx + 126
    o = [R(bx, y + 2, bw, bh, 8, "#2E3A1E", extra=' opacity=".08"'),
         R(bx, y, bw, bh, 8, lg([(0, "#F6FFEA"), (.5, "#F6FFEA"), (1, "#FAFFED")])),
         f'<g mask="url(#hzFade)">{gimg("hazuki", gx, y)}</g>',
         f'<clipPath id="twFoot"><rect x="{n(tx - 2)}" y="{y + 8}" width="580" height="36">'
         + once("width", "0;580", 1.6) + "</rect>"
         f'<rect x="{n(tx - 2)}" y="{y + 46}" width="580" height="36">'
         + once("width", "0;0;580", 3.2, kt="0;.5;1") + "</rect></clipPath>",
         '<g clip-path="url(#twFoot)">' + T(tx, y + 37, lines[0], 21, "#4F5A3E", "h", w=560)
         + T(tx, y + 70, lines[1], 17, "#6C7A58", "u", w=560) + "</g>"]
    return "".join(o), 108


# ───────────────────────── 字体（按用到的字裁剪后内嵌） ─────────────────────────


def font_css(body):
    """把源样圆体（可变字体）裁到页面实际用到的字后内嵌：标题用 900，正文用 700。"""
    try:
        from fontTools import subset
        from fontTools.ttLib import TTFont
    except ImportError:
        print("  ! 没装 fontTools，改用系统字体")
        return ""
    used = set()
    for inner in re.findall(r'<text class="[hu]"[^>]*>(.*?)</text>', body, re.S):
        used |= set(html.unescape(re.sub(r"<[^>]+>", "", inner)))
    f = TTFont(FONTS / "ResourceHanRoundedCN-VF.woff2")
    opts = subset.Options()
    opts.flavor, opts.layout_features, opts.name_IDs, opts.notdef_outline = "woff2", [], ["*"], True
    sub = subset.Subsetter(opts)
    sub.populate(text="".join(sorted(used)))
    sub.subset(f)
    buf = io.BytesIO()
    f.flavor = "woff2"
    f.save(buf)
    return ("@font-face{font-family:SCR;font-weight:200 900;"
            f"src:url(data:font/woff2;base64,{base64.b64encode(buf.getvalue()).decode()}) format('woff2')}}")


# ───────────────────────── 拼成一整张 ─────────────────────────


def compose(cfg, st, d):
    global _uid
    _uid = 0
    DEFS.clear()
    USED.clear()
    svg, h = home(cfg, st, d)
    parts, y = [svg], h + 10
    for fn in (lambda y_: projects(y_, d), lambda y_: produce(y_, cfg, st, d), lambda y_: detail(y_, cfg, st, d),
               lambda y_: mission(y_, st, d), lambda y_: about(y_, cfg)):
        svg, h = fn(y)
        parts.append(svg)
        y += h + 54
    svg, h = footer(y, d)
    parts.append(svg)
    H = int(y + h + 24)

    # 共用背景：浅彩虹渐变 + 白色斜纹 + 淡淡的棱镜徽章
    bg = [R(0, 0, W, H, 0, lg([(0, "#FFF4F3"), (.3, "#F8F1FF"), (.65, "#EEF4FF"), (1, "#FFF3F9")])),
          R(0, 0, W, H, 0, "url(#stripes)", extra=' opacity=".7"')]
    for ex, ey, er in [(980, 900, 230), (140, 1600, 260), (1000, 2450, 240), (180, 3200, 220)]:
        if ey < H:
            bg.append(f'<g opacity=".5" fill="none" stroke="#E6DDF6"><circle cx="{ex}" cy="{ey}" r="{er}" stroke-width="22"/>'
                      f'<circle cx="{ex}" cy="{ey}" r="{er * .7:.0f}" stroke-width="6"/>'
                      f'<path d="{SPARK}" transform="translate({ex} {ey}) scale({er * .45:.0f})" fill="#EFE8FA" stroke="none"/></g>')
    body = "".join(parts)
    imgs = "".join(f'<image id="g-{k}" width="{GIDX[k][0]}" height="{GIDX[k][1]}" '
                   f'href="data:image/webp;base64,{base64.b64encode((GAME / f"{k}.webp").read_bytes()).decode()}"/>'
                   for k in USED)
    defs = (f'<style>{font_css(body)}.h{{font-family:SCR,{FALLBACK};font-weight:900}}'
            f'.u{{font-family:SCR,{FALLBACK};font-weight:700}}</style>'
            f'<image id="av" width="240" height="240" preserveAspectRatio="xMidYMid slice" href="{st.get("avatar", "")}"/>'
            + imgs +
            '<pattern id="stripes" width="34" height="34" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)">'
            '<rect width="17" height="34" fill="#fff"/></pattern>'
            f'<mask id="homeFade"><rect width="{W}" height="690" fill="{lg([(0, "#fff"), (.86, "#fff"), (1, "#000")])}"/></mask>'
            + "".join(DEFS.values()))
    return defs, "".join(bg), body, H


def render(cfg, st, d):
    defs, bg, body, H = compose(cfg, st, d)
    alt = f"{cfg['nickname']} · Lv.{d['level']} · 连续贡献 {d['streak']} 天"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'role="img" aria-label="{esc(alt)}"><title>{esc(alt)}</title><defs>{defs}</defs>'
            f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>'
            f'<g clip-path="url(#frame)">{bg}{body}</g>'
            f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="17.5" fill="none" stroke="#CFC6DE" '
            f'stroke-width="1.5"/></svg>')


# ───────────────────────── README & 本地预览 ─────────────────────────


def readme(cfg, d, revision):
    alt = f"{cfg['nickname']} 的闪耀色彩风格主页 · Lv.{d['level']} · 连续贡献 {d['streak']} 天"
    return f'''<!-- ✦ 本文件由 build.py 生成：配置 config.json / projects.json；python3 build.py 或 --offline --watch ✦ -->
<p align="center"><img src="assets/{OUT.name}?v={revision}" width="100%" alt="{esc(alt)}"/></p>
'''


PREVIEW_START = "<!-- SHINY:START -->"
PREVIEW_END = "<!-- SHINY:END -->"


def update_readme(existing, profile, mode="auto"):
    if mode == "auto":
        repository = os.environ.get("GITHUB_REPOSITORY", "").split("/", 1)
        is_profile = len(repository) == 2 and repository[0].casefold() == repository[1].casefold()
        mode = "profile" if is_profile or not existing else "preserve"
    if mode == "profile":
        return profile
    if mode != "preserve":
        raise ValueError("readme mode 必须是 auto、preserve 或 profile")
    block = f"{PREVIEW_START}\n{profile}{PREVIEW_END}"
    if PREVIEW_START in existing or PREVIEW_END in existing:
        if existing.count(PREVIEW_START) != 1 or existing.count(PREVIEW_END) != 1:
            raise ValueError("README.md 必须恰好包含一对 SHINY:START / SHINY:END 标记")
        start, end = existing.index(PREVIEW_START), existing.index(PREVIEW_END)
        if start > end:
            raise ValueError("README.md 的 SHINY 标记顺序错误")
        return existing[:start] + block + existing[end+len(PREVIEW_END):]
    # Generated profile READMEs from previous runs have no marker.
    if existing.startswith("<!-- ✦ 本文件由 build.py 生成"):
        return profile
    return existing.rstrip() + "\n\n" + block + "\n"


def preview(cfg, st, body):
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Profile Preview</title>
<style>
:root{{--bg:#fff;--fg:#1f2328;--muted:#59636e;--line:#d1d9e0}}
:root[data-theme=dark]{{--bg:#0d1117;--fg:#f0f6fc;--muted:#9198a1;--line:#3d444d}}
body{{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif}}
.bar{{display:flex;justify-content:flex-end;padding:12px 24px;border-bottom:1px solid var(--line)}}
.bar button{{background:none;border:1px solid var(--line);color:var(--fg);border-radius:6px;padding:4px 12px;cursor:pointer}}
.wrap{{max-width:1280px;margin:24px auto;padding:0 32px;display:flex;gap:24px;box-sizing:border-box}}
.side{{width:296px;flex:none}} .side img{{width:100%;border-radius:50%;border:1px solid var(--line)}}
.side h1{{margin:16px 0 0;font-size:24px}}
.main{{flex:1;min-width:0}} .box{{border:1px solid var(--line);border-radius:6px;padding:24px}}
.box img{{max-width:100%}} .box p{{margin:0}}
@media(max-width:768px){{.wrap{{display:block;padding:0 16px}}.side{{width:auto;margin-bottom:16px}}.side img{{width:96px}}}}
</style></head><body>
<div class="bar"><button onclick="document.documentElement.dataset.theme=document.documentElement.dataset.theme==='dark'?'light':'dark'">切换深色 / 浅色</button></div>
<div class="wrap"><div class="side"><img src="{st.get("avatar", "")}" alt=""><h1>{esc(cfg["nickname"])}</h1></div>
<div class="main"><div class="box">
{body}
</div></div></div></body></html>
'''


def write_atomic(path, text):
    pending = path.with_name(path.name + ".tmp")
    pending.write_text(text, encoding="utf-8")
    pending.replace(path)


def build_once(offline=False, *, demo=False, username=None, readme_mode="auto", strict=False):
    cfg = resolve_identity(load_config(), username, demo)
    print("✦ 读取数据…")
    st = demo_stats() if demo else load_stats(cfg, offline, strict=strict)
    if not cfg.get("nickname") or cfg["nickname"] == "auto":
        cfg["nickname"] = st.get("profile_name") or cfg["github"]
    d = derive(cfg, st)
    ASSETS.mkdir(exist_ok=True)
    svg = render(cfg, st, d)
    profile = readme(cfg, d, hashlib.sha256(svg.encode()).hexdigest()[:12])
    readme_path = ROOT / "README.md"
    existing = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    md = update_readme(existing, profile, readme_mode)
    write_atomic(OUT, svg)
    print(f"  ✓ assets/{OUT.name}  ({len(svg.encode()) / 1024:.1f} KB，图像素材 {len(USED)} 张)")
    write_atomic(readme_path, md)
    write_atomic(ROOT / "PROFILE.md", profile)
    write_atomic(ROOT / "preview.html", preview(cfg, st, profile))
    print(f"  ✓ README.md   Lv.{d['level']} · 正在培育 {(d['active'] or {}).get('name', '—')} · 连续 {d['streak']} 天（最长 {d['best']}）"
          f" · 近 30 天 {d['sum30']} 次")


def watch_signature():
    config = ROOT / "config.json"
    raw = {}
    try:
        raw = json.loads(config.read_text(encoding="utf-8"))
        projects_file = raw.get("projects_file", "projects.json") if isinstance(raw, dict) else "projects.json"
        if not isinstance(projects_file, str):
            projects_file = "projects.json"
    except (OSError, ValueError):
        projects_file = "projects.json"
    illustration = raw.get("illustration", "assets/illustrations/hana-coding.webp") if isinstance(raw, dict) else None
    paths = [config, ROOT / projects_file]
    if isinstance(illustration, str):
        paths.append(ROOT / illustration)
    return tuple((str(p), p.stat().st_mtime_ns if p.exists() else None) for p in paths)


def main():
    parser = argparse.ArgumentParser(description="Shiny Colors 风格 GitHub Profile SVG 生成器")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--offline", action="store_true", help="使用当前账号的缓存，不联网")
    source.add_argument("--demo", action="store_true", help="使用虚构数据和示例头像，不联网、不写统计缓存")
    parser.add_argument("--username", help="覆盖 config.json 的 GitHub 用户名")
    parser.add_argument("--readme-mode", choices=("auto", "preserve", "profile"), default="auto",
                        help="auto: 同名个人仓库生成主页，普通仓库保留说明；preserve: 仅更新标记区域")
    parser.add_argument("--strict-refresh", action="store_true", help="联网失败时退出，不使用旧缓存")
    parser.add_argument("--watch", action="store_true", help="配置和立绘变化后重新构建")
    parser.add_argument("--list-icons", action="store_true", help="列出可用于配置的内置图标")
    args = parser.parse_args()
    if args.list_icons:
        print("技术图标（skills / about）:\n" + ", ".join(sorted(ICON_DATA)))
        print("\n统计图标（about）:\n" + ", ".join(sorted(OCTI)))
        return
    kwargs = dict(offline=args.offline, demo=args.demo, username=args.username,
                  readme_mode=args.readme_mode, strict=args.strict_refresh)
    if not args.watch:
        build_once(**kwargs)
        return
    print("✦ 自动构建已启动：保存 config.json / projects.json 后重建；Ctrl+C 退出", flush=True)
    previous = None
    try:
        while True:
            signature = watch_signature()
            if signature != previous:
                previous = signature
                try:
                    build_once(**kwargs)
                except (OSError, ValueError, RuntimeError) as e:
                    print(f"  ! 配置尚未有效，保留已有页面，等待下次保存：{e}", flush=True)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n✦ 自动构建已停止")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError) as error:
        print(f"✗ {error}", file=sys.stderr)
        if error.__cause__:
            print(f"  {error.__cause__}", file=sys.stderr)
        sys.exit(1)
