# pyromod/utils/captcha.py
from pathlib import Path
import random, os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ASSETS_FONTS = list((Path(__file__).parent.parent / "assets/fonts").glob("*.ttf"))
CHAR_POOL      = "ABCDEFGHJKMNPQRTUVWXYZ23456789"
COLORS = [
    # Blues & Teals
    ( 30,  60, 150), ( 10, 100, 120), (  0,  80, 180),
    ( 20, 130, 160), ( 50,  50, 200), (  0, 150, 180),

    # Reds & Pinks
    (150,  20,  20), (180,  40,  60), (200,  10,  80),
    (140,  50,  30), (160,   0,  60), (120,  20,  50),

    # Greens
    ( 20, 110,  40), ( 10, 140,  70), ( 40, 160,  50),
    (  0, 120,  80), ( 60, 150,  30), ( 20, 100,  60),

    # Purples
    (100,  20, 130), (120,  10, 160), ( 80,  30, 150),
    (130,  40, 180), ( 70,   0, 120), (110,  50, 140),

    # Oranges & Browns
    (160,  80,   0), (180, 100,  10), (200,  70,  20),
    (140,  60,  20), (170,  90,  30), (150,  50,   0),

    # Cyans & Other
    ( 10, 100, 120), (  0, 130, 140), ( 30, 110, 150),
    ( 20, 140, 130), (  0, 160, 150), ( 40, 120, 140),
]
EMOJI_POOL = {
    "nature"   : ["🌸","🌺","🌻","🌹","🍀","🍁","🌴","🌵","🎋","🌾",
                   "🌿","🪴","🌲","🌳","🍄","🌊","🌈","⛅","🌙","❄️",
                   "🌑","🌟","💧","🌪","🏔️","🌋","🪨","🪵","🐚","🌏"],
    "animals"  : ["🐶","🐱","🐭","🐹","🐰","🦊","🐻","🐼","🐨","🐯",
                   "🦁","🐮","🐸","🐧","🐦","🦋","🐢","🦄","🐬","🦉",
                   "🦀","🐙","🦈","🐘","🦒","🦓","🦏","🐊","🦜","🐿️"],
    "food"     : ["🍎","🍌","🍇","🍉","🍓","🍒","🥝","🍍","🥑","🍔",
                   "🍕","🍣","🍜","🍩","🎂","🧁","🍦","🥐","🧇","🍟",
                   "🌮","🥗","🍱","🧆","🥟","🍛","🥩","🧀","🥨","🍿"],
    "sports"   : ["⚽","🏀","🏈","⚾","🎾","🏐","🏉","🎱","🥏","🏓",
                   "🏸","🥊","🎯","🏹","🛹","🎿","🏊","🚴","🤸","🧗",
                   "🤼","🏋️","⛷️","🤺","🥋","🏇","🧘","🪃","🎣","🤿"],
    "transport": ["🚗","🚕","🚙","🚌","🚎","🏎️","🚓","🚑","🚒","🚐",
                   "✈️","🚀","🛸","🚁","⛵","🛥️","🚂","🚲","🛵","🚜",
                   "🛺","🚠","🚡","🛤️","⛽","🚤","🛳️","🚟","🛶","🪂"],
}

# ════════════════════════════════════════════════════════
# TEXT IMAGE CAPTCHA
# ════════════════════════════════════════════════════════
def _get_system_fonts():
    
    candidates = [
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
        # Windows
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/verdanab.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
        "C:/Windows/Fonts/trebucbd.ttf",
        # macOS
        "/Library/Fonts/Arial Bold.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    exists = []
    for p in candidates:
        if os.path.exists(p):
            exists.append(p)
            
    win_fonts = "C:/Windows/Fonts"
    if os.path.isdir(win_fonts):
        list_dir = os.listdir(win_fonts)
        random.shuffle(list_dir)
        list_dir = [f for f in list_dir[:100] if f.lower().endswith(".ttf")]  
        for f in list_dir:
            exists.append(os.path.join(win_fonts, f))
 
    if not exists:
        raise FileNotFoundError("Tidak ada font TTF yang ditemukan. Install font atau set path manual.")
    
    return exists

def _render_char_layer(char, font, font_size, clarity, color, opacity=255):
    font  = ImageFont.truetype(font, font_size)
    color = color if color is not None else random.choice(COLORS)

    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    bb    = probe.textbbox((0, 0), char, font=font)
    tw    = bb[2] - bb[0]
    th    = bb[3] - bb[1]

    side   = int(math.sqrt(tw**2 + th**2)) + 4
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    d      = ImageDraw.Draw(canvas)

    tx = (side - tw) // 2 - bb[0]
    ty = (side - th) // 2 - bb[1]

    # Shadow ikut opacity
    shadow_alpha = max(40, int((180 - clarity * 25) * opacity / 255))
    off = max(1, font_size // 35)
    d.text((tx + off, ty + off), char, font=font, fill=(*color, shadow_alpha))
    d.text((tx, ty), char, font=font, fill=(*color, opacity))

    max_angle = max(2, 16 - clarity * 2)
    angle     = random.uniform(-max_angle, max_angle)
    rotated   = canvas.rotate(angle, expand=False, resample=Image.BICUBIC)

    bbox = rotated.getbbox()
    return rotated.crop(bbox) if bbox else rotated

def generate_captcha_text(
    path, n_choices=6, lenght=5,
    clarity=1, font_size=48, opacity=150, spacing=-10, 
    color=None, width=240, height=80,
):
    system_fonts = _get_system_fonts()
    
    if color is not None:
        color = tuple(max(0, min(255, c)) for c in color[:3])
        
    clarity = max(1, min(5, clarity))
    opacity = max(0, min(255, opacity))
    
    answer = "".join(random.choices(CHAR_POOL, k=lenght))
    choices = set()
    while len(choices) < n_choices - 1:
        c = "".join(random.choices(CHAR_POOL, k=lenght))
        if c != answer:
            choices.add(c)  
    choices = list(choices) + [answer]
    random.shuffle(choices)
    

    base = random.choice([
        (245, 248, 255), (255, 248, 238), (242, 255, 242),
        (255, 242, 255), (245, 255, 252),
    ])
    img  = Image.new("RGB", (width, height), base)
    draw = ImageDraw.Draw(img)

    # Noise dots — makin banyak jika clarity rendah
    dot_count = int(60 + (5 - clarity) * 120)   # clarity5=50, clarity1=530
    for _ in range(dot_count):
        x, y = random.randint(0, width), random.randint(0, height)
        c = tuple(max(0, b - random.randint(15, 60)) for b in base)
        draw.point((x, y), fill=c)

    # Garis latar — makin banyak jika clarity rendah
    line_count = max(0, 9 - clarity * 2)         # clarity5=0, clarity1=7 (bg lines)
    for _ in range(line_count):
        col = tuple(random.randint(150, 210) for _ in range(3))
        draw.line([
            (random.randint(0, width), random.randint(0, height)),
            (random.randint(0, width), random.randint(0, height)),
        ], fill=col, width=1)

    # Karakter palsu kecil — makin banyak jika clarity rendah
    fp = random.choice(system_fonts)
    font_sm  = ImageFont.truetype(fp, max(7, font_size // 5))
    fake_count = max(0, 8 - clarity)             # clarity5=3, clarity1=7
    for _ in range(fake_count):
        col = tuple(random.randint(180, 220) for _ in range(3))
        draw.text(
            (random.randint(0, width - 20), random.randint(0, height - 20)),
            random.choice(CHAR_POOL), font=font_sm, fill=col
        )
    
    # Render karakter
    chars   = [
        _render_char_layer(c, random.choice(ASSETS_FONTS), font_size, clarity, color, opacity) for c in answer
    ]
    total_w = sum(c.width for c in chars)

    # Gap default + spacing offset dari user
    default_gap = max(2, (width - total_w - 20) // max(len(answer) - 1, 1))
    default_gap = min(default_gap, 25)
    gap = default_gap + spacing                  # spacing negatif = menimpa

    x = max(6, (width - (total_w + gap * (len(answer) - 1))) // 2)

    for ch_img in chars:
        jitter = max(0, 8 - clarity)
        y = (height - ch_img.height) // 2 + random.randint(-jitter, jitter)
        y = max(0, min(height - ch_img.height, y))
        img.paste(ch_img, (x, y), ch_img)
        x += ch_img.width + gap

    # Garis silang — makin banyak dan tebal jika clarity rendah
    cross_count = max(1, 4 - clarity)            # clarity5=1, clarity1=3 garis
    for _ in range(cross_count):
        y1  = random.randint(height // 4, 3 * height // 4)
        col = tuple(random.randint(60, 150) for _ in range(3))
        lw  = max(1, 3 - clarity // 2)
        draw.line([(0, y1), (width, y1 + random.randint(-12, 12))], fill=col, width=lw)

    # Blur — lebih kuat jika clarity rendah
    blur_r = max(0.0, 0.8 - clarity * 0.1)
    if blur_r > 0:
        img = img.filter(ImageFilter.GaussianBlur(radius=blur_r))

    img.save(path)
    
    return {
        "answer"  : answer,
        "choices" : choices,
        "path"    : path,
    }

# ════════════════════════════════════════════════════════
# EMOJI CAPTCHA
# ════════════════════════════════════════════════════════
def generate_captcha_emoji(n_choices: int = 6) -> dict:
    category = random.choice(list(EMOJI_POOL.keys()))
    pool     = EMOJI_POOL[category]
    n        = min(n_choices, len(pool))
    choices  = random.sample(pool, n)
    answer   = random.choice(choices)
    random.shuffle(choices)
 
    return {
        "answer"  : answer,
        "choices" : choices,
    }
 
 
# ════════════════════════════════════════════════════════
# MATH CAPTCHA
# ════════════════════════════════════════════════════════
def generate_captcha_math(n_choices: int = 5, difficulty: int = 1) -> dict:
    difficulty = max(1, min(3, difficulty))
    
    if difficulty == 1:
        ops = ["+", "-"]
    elif difficulty == 2:
        ops = ["+", "-", "×"]
    else:
        ops = ["+", "-", "×", "÷"]
 
    op = random.choice(ops)
 
    if op == "+":
        lim  = {1: 20, 2: 30, 3: 50}[difficulty]
        a, b = random.randint(1, lim), random.randint(1, lim)
        answer = a + b
 
    elif op == "-":
        lim  = {1: 20, 2: 30, 3: 50}[difficulty]
        a    = random.randint(5, lim)
        b    = random.randint(1, a)
        answer = a - b
 
    elif op == "×":
        lim  = {1: 5, 2: 9, 3: 12}[difficulty]
        a, b = random.randint(2, lim), random.randint(2, lim)
        answer = a * b
 
    else:  # ÷
        b      = random.randint(2, 9)
        answer = random.randint(2, 10)
        a      = b * answer   # pastikan hasil bulat
 
    question = f"{a} {op} {b} = ?"
 
    # Jawaban salah yang masuk akal (dekat dengan jawaban benar)
    wrong: set = set()
    attempts   = 0
    while len(wrong) < n_choices - 1 and attempts < 100:
        attempts += 1
        noise = random.choice([-3, -2, -1, 1, 2, 3, 5, -5])
        w     = answer + noise
        if w != answer and w > 0:
            wrong.add(w)
 
    choices = [str(w) for w in wrong] + [str(answer)]
    random.shuffle(choices)
 
    return {
        "question": question,
        "answer"  : str(answer),
        "choices" : choices,
    }

