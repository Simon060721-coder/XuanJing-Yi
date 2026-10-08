# -*- coding: utf-8 -*-
"""生成玄镜易配色候选预览图（决策辅助用，非项目代码）。"""
from PIL import Image, ImageDraw, ImageFont

W = 1680
CARD_H = 268
GAP = 20
TOP = 132
N = 4
H = TOP + N * CARD_H + (N - 1) * GAP + 36

F_KAI = "C:/Windows/Fonts/STKAITI.TTF"
F_SONG = "C:/Windows/Fonts/STSONG.TTF"
F_BODY = "C:/Windows/Fonts/msyh.ttc"
F_BOLD = "C:/Windows/Fonts/msyhbd.ttc"


def font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception:
        return ImageFont.truetype(F_BODY, size)


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def blend(fg_rgb, alpha, bg_rgb):
    return tuple(round(fg_rgb[i] * alpha + bg_rgb[i] * (1 - alpha)) for i in range(3))


def lum(rgb):
    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def readable_on(bg_rgb):
    return (20, 18, 16) if lum(bg_rgb) > 0.45 else (250, 248, 244)


PALETTES = [
    dict(
        key="A", name="玄墨金", tag="冷黑 · 暗金 · 庄重",
        desc="故宫拓片气质：对比强、气度沉，适合强调典籍与权威。",
        use="适合：想突出「认真、专业、有传承」的项目调性",
        bg="#0E0F12", bg2="#14161B", surf=(255, 255, 255, 0.045), bord=(255, 255, 255, 0.10),
        accent="#C6A567", accent_hover="#D8BC85", seal="#9E3B32",
        text="#ECE7DD", text2="#A5A099", muted="#6E6A64",
    ),
    dict(
        key="B", name="宣纸青", tag="浅色 · 竹青 · 清雅",
        desc="宣纸底色配竹青，水墨书卷气；明亮通透，长文阅读最舒适。",
        use="适合：想让解读文案像「文章」而非「仪表盘」",
        bg="#F5F2EA", bg2="#EFEBE1", surf=(255, 255, 255, 0.75), bord=(43, 38, 32, 0.12),
        accent="#3D6B5B", accent_hover="#2F5648", seal="#A9432F",
        text="#24211C", text2="#5F5A51", muted="#8C867C",
    ),
    dict(
        key="C", name="靛青月白", tag="深靛 · 月白 · 神秘",
        desc="星空罗盘感，冷调未来古典，最呼应「数字化」这条叙事线。",
        use="适合：想强调「算法推演」的神秘与精确感",
        bg="#0D1420", bg2="#131C2B", surf=(255, 255, 255, 0.05), bord=(255, 255, 255, 0.11),
        accent="#7FA8C9", accent_hover="#9CC0DC", seal="#B04A3C",
        text="#E6EDF3", text2="#9FB0C0", muted="#6B7A8A",
    ),
    dict(
        key="D", name="紫檀朱", tag="暖褐 · 檀木 · 亲和",
        desc="精修当前线上配色：保留暖褐基调，收紧色彩、拉开层次。",
        use="适合：改动量最小、风险最低的稳妥路线",
        bg="#1F1512", bg2="#2A1D18", surf=(245, 232, 211, 0.06), bord=(245, 232, 211, 0.12),
        accent="#C08A56", accent_hover="#D6A26C", seal="#A33A2A",
        text="#F3E8D3", text2="#B9A490", muted="#8A7A6C",
    ),
]

img = Image.new("RGB", (W, H), hx("#FBFBF9"))
d = ImageDraw.Draw(img)

f_title = font(F_SONG, 40)
f_sub = font(F_BODY, 17)
f_name = font(F_SONG, 34)
f_tag = font(F_BODY, 15)
f_desc = font(F_BODY, 14)
f_use = font(F_BODY, 13)
f_h1 = font(F_KAI, 38)
f_h2 = font(F_KAI, 20)
f_body = font(F_BODY, 14)
f_btn = font(F_BODY, 16, )
f_chip = font(F_BODY, 12)
f_hex = font(F_BODY, 11)
f_dot = font(F_BODY, 11)

d.text((48, 44), "玄镜易 · 配色候选", font=f_title, fill=hx("#24211C"))
d.text((50, 94), "每套含：背景 / 卡片面 / 强调色 / 朱砂 / 三级文字。右侧为令牌色值。", font=f_sub, fill=hx("#8C867C"))

y = TOP
for p in PALETTES:
    bg = hx(p["bg"])
    bg2 = hx(p["bg2"])
    text = hx(p["text"])
    text2 = hx(p["text2"])
    muted = hx(p["muted"])
    accent = hx(p["accent"])
    seal = hx(p["seal"])
    surface = blend((255, 255, 255) if p["surf"][0] == 255 else (245, 232, 211), p["surf"][3], bg)
    bd = blend((255, 255, 255) if p["bord"][0] == 255 else (43, 38, 32), p["bord"][3], bg)

    # 卡片外框
    d.rounded_rectangle([24, y, W - 24, y + CARD_H], radius=18, fill=hx("#FFFFFF"), outline=hx("#E6E2D9"), width=1)

    # 左栏：名称与说明
    lx = 52
    d.rounded_rectangle([lx, y + 28, lx + 34, y + 62], radius=8, fill=accent)
    d.text((lx + 11, y + 33), p["key"], font=font(F_BOLD, 20), fill=readable_on(accent))
    d.text((lx + 48, y + 28), p["name"], font=f_name, fill=hx("#24211C"))
    d.text((lx + 48, y + 72), p["tag"], font=f_tag, fill=hx("#9A948A"))
    d.text((lx, y + 108), p["desc"], font=f_desc, fill=hx("#5F5A51"))
    d.text((lx, y + 132), p["use"], font=f_use, fill=hx("#9A948A"))

    # 预览区
    px0, px1 = 460, 1180
    py0, py1 = y + 24, y + CARD_H - 24
    d.rounded_rectangle([px0, py0, px1, py1], radius=14, fill=bg)
    d.rounded_rectangle([px0, py0, px1, py1], radius=14, outline=bd, width=1)

    # 顶部渐变感：上半叠一层 bg2
    ov = Image.new("RGB", (px1 - px0 - 2, 90), bg2)
    img.paste(ov, (px0 + 1, py0 + 1))

    d.text((px0 + 26, py0 + 22), "玄镜易", font=f_h1, fill=text)
    d.text((px0 + 26, py0 + 72), "一扇通往东方古智的数字之门", font=f_h2, fill=accent)

    # 内层卡片
    cx0, cy0, cx1, cy1 = px0 + 26, py0 + 112, px1 - 26, py1 - 22
    d.rounded_rectangle([cx0, cy0, cx1, cy1], radius=10, fill=surface, outline=bd, width=1)
    d.text((cx0 + 18, cy0 + 16), "将千年易学转化为精确的算法", font=f_body, fill=text)
    d.text((cx0 + 18, cy0 + 40), "卦象 · 评分 · 多维解读", font=f_body, fill=text2)

    # 按钮
    bx0, by0 = cx0 + 18, cy0 + 72
    bw, bh = 138, 40
    d.rounded_rectangle([bx0, by0, bx0 + bw, by0 + bh], radius=10, fill=accent)
    d.text((bx0 + 30, by0 + 10), "开始占卜", font=f_btn, fill=readable_on(accent))
    # 次级按钮
    d.rounded_rectangle([bx0 + bw + 14, by0, bx0 + bw + 14 + 110, by0 + bh], radius=10,
                        fill=surface, outline=bd, width=1)
    d.text((bx0 + bw + 44, by0 + 10), "了解更多", font=f_btn, fill=text2)

    # 朱砂标签
    sx0 = bx0 + bw + 14 + 110 + 18
    seal_bg = blend(seal, 0.18, surface)
    d.rounded_rectangle([sx0, by0 + 5, sx0 + 76, by0 + 35], radius=15, fill=seal_bg)
    d.text((sx0 + 16, by0 + 13), "大吉 · 92", font=f_chip, fill=seal)

    # 右侧色令牌
    chips = [
        ("背景", p["bg"]), ("次背景", p["bg2"]), ("强调", p["accent"]), ("强调悬停", p["accent_hover"]),
        ("朱砂", p["seal"]), ("主文字", p["text"]), ("次文字", p["text2"]), ("弱文字", p["muted"]),
    ]
    for i, (label, val) in enumerate(chips):
        col = hx(val)
        cxx = 1220 + (i % 2) * 224
        cyy = y + 40 + (i // 2) * 52
        d.rounded_rectangle([cxx, cyy, cxx + 34, cyy + 34], radius=8, fill=col, outline=hx("#DCD7CD"), width=1)
        d.text((cxx + 44, cyy + 1), label, font=f_chip, fill=hx("#5F5A51"))
        d.text((cxx + 44, cyy + 18), val.upper(), font=f_hex, fill=hx("#9A948A"))

    y += CARD_H + GAP

d.text((50, H - 30), "朱砂色用于吉凶标签与警示；强调悬停色用于交互反馈。实际落地时全部收敛为设计令牌，不再出现硬编码色值。",
       font=f_use, fill=hx("#9A948A"))

out = "E:/Projects/玄镜易/palette-candidates.png"
img.save(out, "PNG")
print("saved:", out, img.size)
