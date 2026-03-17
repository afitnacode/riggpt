#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
waterfall_image.py -- IC-7610 Voice Agent v2.10.17
Encodes an image into audio that appears as a picture on an SDR waterfall display.

How it works:
  - Image is resized to (width x height) pixels
  - Each ROW of pixels -> one short audio frame
  - Each COLUMN (pixel) -> one sine wave frequency bin
  - Pixel brightness (0-255) -> sine wave amplitude
  - All sine waves for a row are summed -> one audio frame
  - Frames concatenated -> WAV -> played via SSB -> appears on SDR waterfall

Image processing pipeline (v2.10.15):
  Resize -> grayscale -> histogram eq -> brightness/contrast
  -> sharpen -> dither -> invert -> black/white point
  -> tone curve (linear/gamma/srgb/log/power/s_curve) -> noise floor -> encode
"""

import numpy as np
import wave, tempfile, os, math, logging
from PIL import Image, ImageFilter, ImageEnhance, ImageOps

logger    = logging.getLogger('ic7610.waterfall')
SAMPLE_RATE = 44100


# -- Canned test images --------------------------------------------------------

def make_smiley(size=(128, 64)):
    from PIL import ImageDraw
    W, H = size
    img = Image.new('L', size, 0)
    d   = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2
    r = min(W, H) // 2 - 4
    # Face outline
    d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=255, width=max(2, r//10))
    # Eyes
    er = max(2, r // 7); ex = r // 3; ey = r // 4
    d.ellipse([cx-ex-er, cy-ey-er, cx-ex+er, cy-ey+er], fill=255)
    d.ellipse([cx+ex-er, cy-ey-er, cx+ex+er, cy-ey+er], fill=255)
    # Smile arc
    sr = r // 2
    for angle in range(10, 171, 3):
        rad = math.radians(angle)
        x = int(cx + sr * math.cos(rad))
        y = int(cy + int(sr * 0.65 * math.sin(rad)) + r // 7)
        w = max(2, r // 14)
        d.ellipse([x-w, y-w, x+w, y+w], fill=220)
    return img


def make_moon(size=(128, 64)):
    from PIL import ImageDraw
    W, H = size
    cx, cy = W // 2, H // 2
    r = min(W, H) // 2 - 4
    disk  = Image.new('L', size, 0)
    dd    = ImageDraw.Draw(disk)
    dd.ellipse([cx-r, cy-r, cx+r, cy+r], fill=240)
    bite  = Image.new('L', size, 0)
    db    = ImageDraw.Draw(bite)
    off   = r // 3
    db.ellipse([cx-r+off, cy-r, cx+r+off, cy+r], fill=255)
    arr = np.array(disk, dtype=np.float32)
    msk = np.array(bite, dtype=np.float32) / 255.0
    arr = arr * (1.0 - msk * 0.96)
    rng = np.random.default_rng(42)
    for _ in range(14):
        sx = rng.integers(4, W-4); sy = rng.integers(4, H-4)
        arr[sy, sx] = 200
        for dy,dx in [(-1,0),(1,0),(0,-1),(0,1)]:
            ny,nx = sy+dy, sx+dx
            if 0<=ny<H and 0<=nx<W: arr[ny,nx] = max(arr[ny,nx], 130)
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8),'L')


def make_flower(size=(128, 64)):
    from PIL import ImageDraw
    W, H = size
    img = Image.new('L', size, 0)
    cx, cy = W // 2, H // 2
    r  = min(W, H) // 2 - 6
    pr = r * 0.55; pw = r * 0.22
    for i in range(6):
        angle = math.radians(360/6*i)
        petal = Image.new('L', size, 0)
        dp    = ImageDraw.Draw(petal)
        for t in np.linspace(0.1, 1.0, 30):
            ex = int(cx + t * pr * math.cos(angle))
            ey = int(cy + t * pr * math.sin(angle))
            ew = max(2, int(pw * math.sin(math.pi * t)))
            bright = int(160 + 80*t)
            dp.ellipse([ex-ew, ey-ew, ex+ew, ey+ew], fill=bright)
        arr_p = np.array(petal); arr_i = np.array(img)
        img = Image.fromarray(np.maximum(arr_i, arr_p), 'L')
    d = ImageDraw.Draw(img)
    cr = max(4, r//5)
    d.ellipse([cx-cr, cy-cr, cx+cr, cy+cr], fill=255)
    return img


def make_diamond(size=(128, 64)):
    from PIL import ImageDraw
    W, H = size
    img = Image.new('L', size, 0)
    d   = ImageDraw.Draw(img)
    cx, cy = W//2, H//2
    rw, rh = W//2-6, H//2-4
    d.polygon([(cx,cy-rh),(cx+rw,cy),(cx,cy+rh),(cx-rw,cy)], outline=255, fill=140)
    rw2,rh2 = rw//2, rh//2
    d.polygon([(cx,cy-rh2),(cx+rw2,cy),(cx,cy+rh2),(cx-rw2,cy)], fill=230)
    d.ellipse([cx-3, cy-rh-2, cx+3, cy-rh+4], fill=255)
    return img


def make_plasma(size=(128, 64)):
    """Interference plasma -- classic demoscene effect."""
    W, H = size
    x = np.linspace(0, 4*np.pi, W)
    y = np.linspace(0, 4*np.pi, H)
    X, Y = np.meshgrid(x, y)
    Z  = np.sin(X) + np.sin(Y) + np.sin((X+Y)/2)
    Z += np.sin(np.sqrt(X**2 + Y**2))
    Z  = (Z - Z.min()) / (Z.max() - Z.min())
    return Image.fromarray((Z * 255).astype(np.uint8), 'L')


def make_lissajous(size=(128, 64), a=3, b=4, delta=np.pi/4):
    """Lissajous figure -- parametric math curves."""
    from PIL import ImageDraw
    W, H = size
    img = Image.new('L', size, 0)
    d   = ImageDraw.Draw(img)
    cx, cy = W//2, H//2
    rx, ry = W//2 - 4, H//2 - 4
    pts = []
    for t in np.linspace(0, 2*np.pi, 2000):
        px = int(cx + rx * np.sin(a*t + delta))
        py = int(cy + ry * np.sin(b*t))
        pts.append((px, py))
    # Draw with varying brightness using multiple passes
    arr = np.zeros((H, W), dtype=np.float32)
    for i in range(len(pts)-1):
        x0,y0 = pts[i]; x1,y1 = pts[i+1]
        if 0<=x0<W and 0<=y0<H: arr[y0,x0] += 12
        if 0<=x1<W and 0<=y1<H: arr[y1,x1] += 8
    arr = np.clip(arr, 0, 255)
    # Blur slightly
    from PIL import ImageFilter
    img2 = Image.fromarray(arr.astype(np.uint8), 'L')
    img2 = img2.filter(ImageFilter.GaussianBlur(1))
    return img2


def make_spiral(size=(128, 64)):
    """Archimedean spiral with glow."""
    W, H = size
    arr = np.zeros((H, W), dtype=np.float32)
    cx, cy = W/2, H/2
    max_r  = min(W, H)/2 - 2
    # Draw spiral as a dense set of points
    for t in np.linspace(0, 6*np.pi, 8000):
        r  = max_r * t / (6*np.pi)
        px = cx + r * np.cos(t)
        py = cy + r * np.sin(t) * (H/W)  # aspect correction
        ix, iy = int(px), int(py)
        if 0<=ix<W and 0<=iy<H:
            brightness = 100 + 155 * (t/(6*np.pi))
            arr[iy, ix] = max(arr[iy,ix], brightness)
            # Glow neighbours
            for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx,ny = ix+dx, iy+dy
                if 0<=nx<W and 0<=ny<H:
                    arr[ny,nx] = max(arr[ny,nx], brightness*0.4)
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8), 'L')


def make_mandelbrot(size=(128, 64)):
    """Mandelbrot set slice -- zoomed into the interesting boundary."""
    W, H = size
    # Zoom into the seahorse valley
    x = np.linspace(-0.76, -0.74, W)
    y = np.linspace(0.08,   0.12, H)
    X, Y = np.meshgrid(x, y)
    C    = X + 1j*Y
    Z    = np.zeros_like(C)
    M    = np.zeros((H, W), dtype=np.float32)
    MAX_ITER = 80
    for i in range(MAX_ITER):
        mask = np.abs(Z) <= 2
        Z[mask] = Z[mask]**2 + C[mask]
        M[mask] += 1
    M = M / MAX_ITER
    # Gamma + invert so boundary is bright
    M = 1.0 - np.power(M, 0.5)
    return Image.fromarray((M * 255).astype(np.uint8), 'L')


def make_dna_helix(size=(128, 64)):
    """DNA double helix backbone."""
    from PIL import ImageDraw
    W, H = size
    img = Image.new('L', size, 0)
    d   = ImageDraw.Draw(img)
    cx  = H // 2
    # Two sine waves offset by pi (the two strands)
    amp  = H//2 - 4
    freq = 3  # number of full turns
    prev1 = prev2 = None
    for col in range(W):
        t  = col / W * freq * 2 * np.pi
        y1 = int(cx + amp * np.sin(t))
        y2 = int(cx + amp * np.sin(t + np.pi))
        # Draw rungs (base pairs) at every 1/8 turn
        if int(t * 8 / np.pi) != int((t - 2*np.pi/W) * 8 / np.pi):
            d.line([(col, min(y1,y2)), (col, max(y1,y2))], fill=80, width=1)
        # Draw backbone
        if prev1: d.line([prev1, (col, y1)], fill=255, width=2)
        if prev2: d.line([prev2, (col, y2)], fill=200, width=2)
        prev1, prev2 = (col, y1), (col, y2)
    return img


def make_static_burst(size=(128, 64)):
    """TV static / noise that brightens from center outward."""
    W, H = size
    rng = np.random.default_rng(1337)
    # Base noise
    noise = rng.random((H, W)).astype(np.float32)
    # Radial gradient -- bright in centre, dark at edges
    cx, cy = W/2, H/2
    x = np.arange(W); y = np.arange(H)
    X, Y = np.meshgrid(x, y)
    dist = np.sqrt(((X-cx)/(W/2))**2 + ((Y-cy)/(H/2))**2)
    radial = np.clip(1.0 - dist, 0, 1) ** 0.5
    result = noise * radial * 0.7 + radial * 0.3
    result = np.clip(result, 0, 1)
    return Image.fromarray((result*255).astype(np.uint8), 'L')


def make_sine_stack(size=(128, 64)):
    """Multiple overlapping sine waves at different frequencies -- standing wave look."""
    W, H = size
    arr = np.zeros((H, W), dtype=np.float32)
    cx  = H / 2
    freqs_amps = [(1,0.9),(2,0.6),(3,0.4),(5,0.25),(7,0.15),(11,0.08),(13,0.05)]
    x   = np.arange(W)
    for freq, amp in freqs_amps:
        y_float = cx + (H/2 - 2) * amp * np.sin(2*np.pi*freq*x/W)
        for col in range(W):
            iy = int(np.clip(y_float[col], 0, H-1))
            brightness = 255 * amp / 0.9
            arr[iy, col] = max(arr[iy, col], brightness)
            # Vertical blur / glow
            for dy in range(-2, 3):
                ny = iy + dy
                if 0<=ny<H:
                    arr[ny, col] = max(arr[ny, col], brightness * np.exp(-abs(dy)*0.8))
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8), 'L')


def make_radial_burst(size=(128, 64)):
    """Starburst / radial rays from centre."""
    W, H = size
    x  = np.arange(W) - W/2
    y  = (np.arange(H) - H/2)[:, np.newaxis]
    # Scale y for aspect ratio
    y  = y * (W/H)
    angle = np.arctan2(y, x)  # -pi..pi
    dist  = np.sqrt(x**2 + y**2) / (W/2)
    # 12 rays with soft edges
    n_rays = 12
    ray    = np.abs(np.sin(n_rays/2 * angle))
    # Fade toward edges
    result = ray * np.clip(1.0 - dist*0.7, 0, 1)
    result = np.power(result, 0.5)
    return Image.fromarray((result*255).astype(np.uint8), 'L')


def make_checkerboard_warp(size=(128, 64)):
    """Warped checkerboard -- pinch/bulge distortion."""
    W, H = size
    cx, cy = W/2, H/2
    arr = np.zeros((H, W), dtype=np.float32)
    for iy in range(H):
        for ix in range(W):
            # Polar coords
            dx = (ix - cx) / cx
            dy = (iy - cy) / cy * (W/H)
            r  = np.sqrt(dx**2 + dy**2)
            # Barrel distortion
            r2 = r * (1 + 0.4*r**2)
            # Map back
            scale = r2/max(r, 1e-9)
            sx = int(cx + dx*cx*scale)
            sy = int(cy + dy*cy/(W/H)*scale)
            if 0<=sx<W and 0<=sy<H:
                check = ((sx//8) + (sy//8)) % 2
                arr[iy, ix] = 220 if check else 30
            else:
                arr[iy, ix] = 0
    return Image.fromarray(arr.astype(np.uint8), 'L')


def make_interference(size=(128, 64)):
    """Two-source interference rings -- like a ripple tank."""
    W, H = size
    x = np.linspace(0, W, W)
    y = np.linspace(0, H, H)[:, np.newaxis]
    # Two point sources
    s1x, s1y = W*0.35, H*0.5
    s2x, s2y = W*0.65, H*0.5
    d1 = np.sqrt((x-s1x)**2 + (y-s1y)**2)
    d2 = np.sqrt((x-s2x)**2 + (y-s2y)**2)
    k  = 0.35  # spatial frequency
    wave = np.sin(k*d1) + np.sin(k*d2)
    wave = (wave - wave.min()) / (wave.max() - wave.min())
    return Image.fromarray((wave*255).astype(np.uint8), 'L')


def make_vortex(size=(128, 64)):
    """Logarithmic spiral vortex -- galaxy arm look."""
    W, H = size
    x  = np.linspace(-1, 1, W)
    y  = np.linspace(-1, 1, H)[:, np.newaxis] * (H/W)
    r  = np.sqrt(x**2 + y**2)
    th = np.arctan2(y, x)
    # Vortex: rotate angle proportional to 1/r
    twist = th + 3.0 / (r + 0.15)
    # Arms: bright on multiples of pi/2
    arms = np.cos(3 * twist) ** 2
    # Fade toward edge and at centre
    fade = np.exp(-r*2.5) * np.clip(1-np.exp(-r*8), 0, 1)
    result = arms * fade
    result = (result - result.min()) / (result.max()-result.min()+1e-9)
    return Image.fromarray((result**0.6*255).astype(np.uint8), 'L')


def make_qrish(size=(128, 64)):
    """QR-code-like random block pattern -- maximises high-frequency content."""
    W, H = size
    rng   = np.random.default_rng(2024)
    block = 8
    cols_b = W // block; rows_b = H // block
    arr = rng.choice([0, 255], size=(rows_b, cols_b)).astype(np.uint8)
    # Upscale with NEAREST
    img = Image.fromarray(arr, 'L').resize((W, H), Image.NEAREST)
    return img


def make_callsign(text='DE HAM', size=(128, 64)):
    """Render text as a waterfall image -- callsign or CQ call."""
    from PIL import ImageDraw, ImageFont
    W, H = size
    img = Image.new('L', size, 0)
    d   = ImageDraw.Draw(img)
    font_size = max(8, H // 2)
    font = None
    for path in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                 '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf']:
        try:
            font = ImageFont.truetype(path, font_size); break
        except Exception:
            pass
    if font is None:
        font = ImageFont.load_default()
    try:
        bbox = d.textbbox((0,0), text, font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    except AttributeError:
        tw, th = d.textsize(text, font=font)
    d.text(((W-tw)//2, (H-th)//2), text, fill=255, font=font)
    arr  = np.array(img, dtype=np.float32)
    glow = np.array(img.filter(ImageFilter.MaxFilter(3)), dtype=np.float32)*0.35
    return Image.fromarray(np.clip(arr+glow, 0,255).astype(np.uint8),'L')


def make_chevron(size=(128, 64)):
    """Right-pointing chevron/arrow -- tests directionality."""
    from PIL import ImageDraw
    W, H = size
    img = Image.new('L', size, 0)
    d   = ImageDraw.Draw(img)
    mg  = 6
    for offset, bright in [(0,255), (-W//7, 170)]:
        tip_x = W - mg + offset
        left_x = mg + offset
        mid_y = H // 2
        notch_x = left_x + W // 4
        pts = [(left_x, mg), (tip_x - W//4, mg), (tip_x, mid_y),
               (tip_x - W//4, H-mg), (left_x, H-mg), (notch_x, mid_y)]
        d.polygon(pts, outline=bright, fill=bright//2)
    return img


def make_skull(size=(128, 64)):
    """Skull / crossbones — spooky waterfall silhouette."""
    from PIL import ImageDraw
    W, H = size
    img = Image.new('L', size, 0)
    d   = ImageDraw.Draw(img)
    cx, cy = W//2, H//3
    # Cranium
    rx, ry = W//5, H//4
    d.ellipse([cx-rx, cy-ry, cx+rx, cy+ry], fill=200)
    # Jaw
    jw, jh = rx*2//3, H//6
    d.rectangle([cx-jw, cy+ry-4, cx+jw, cy+ry+jh], fill=160)
    # Eyes
    ew = rx//3
    d.ellipse([cx-rx//2-ew, cy-ry//3, cx-rx//2+ew, cy+ry//4], fill=0)
    d.ellipse([cx+rx//2-ew, cy-ry//3, cx+rx//2+ew, cy+ry//4], fill=0)
    # Nose
    d.polygon([(cx-3, cy+ry//6), (cx+3, cy+ry//6), (cx, cy+ry//2)], fill=0)
    # Crossbones
    bw = W//3
    by = cy+ry+jh+4
    d.line([cx-bw, by, cx+bw, by+H//5], fill=180, width=3)
    d.line([cx+bw, by, cx-bw, by+H//5], fill=180, width=3)
    return img


def make_radioactive(size=(128, 64)):
    """Radioactive trefoil symbol."""
    from PIL import ImageDraw
    W, H = size
    img = Image.new('L', size, 0)
    d   = ImageDraw.Draw(img)
    cx, cy = W//2, H//2
    r = min(W, H)//2 - 4
    # Three blades
    for angle in [0, 120, 240]:
        a_rad = np.radians(angle)
        a2 = np.radians(angle + 60)
        pts = [(cx, cy)]
        for t in np.linspace(a_rad, a2, 30):
            pts.append((int(cx + r*np.cos(t)), int(cy + r*np.sin(t))))
        pts.append((cx, cy))
        d.polygon(pts, fill=220)
    # Center hole
    d.ellipse([cx-r//4, cy-r//4, cx+r//4, cy+r//4], fill=0)
    return img


def make_eye(size=(128, 64)):
    """All-seeing eye — Illuminati vibes on the waterfall."""
    from PIL import ImageDraw
    W, H = size
    img = Image.new('L', size, 0)
    d   = ImageDraw.Draw(img)
    cx, cy = W//2, H//2
    # Outer eye shape (two arcs)
    pts_top = [(int(cx + W//2.5*np.cos(t)), int(cy - H//3*np.sin(t)))
               for t in np.linspace(0, np.pi, 60)]
    pts_bot = [(int(cx + W//2.5*np.cos(t)), int(cy + H//3*np.sin(t)))
               for t in np.linspace(np.pi, 0, 60)]
    d.polygon(pts_top + pts_bot, outline=200, fill=80)
    # Iris
    ir = min(W, H)//6
    d.ellipse([cx-ir, cy-ir, cx+ir, cy+ir], outline=255, fill=160)
    # Pupil
    pr = ir//2
    d.ellipse([cx-pr, cy-pr, cx+pr, cy+pr], fill=0)
    # Light reflection
    d.ellipse([cx-pr+2, cy-pr+2, cx-pr+5, cy-pr+5], fill=255)
    return img


def make_barcode(size=(128, 64)):
    """Random barcode / scanner lines — mysterious data on the waterfall."""
    import random
    W, H = size
    arr = np.zeros((H, W), dtype=np.uint8)
    x = 4
    while x < W - 4:
        bw = random.choice([1, 1, 2, 2, 3])
        bright = random.choice([180, 200, 220, 240, 255])
        arr[:, x:min(x+bw, W)] = bright
        x += bw + random.choice([1, 2, 3])
    return Image.fromarray(arr, 'L')


def make_heartbeat(size=(128, 64)):
    """ECG / heartbeat trace — flatline with periodic QRS spikes."""
    from PIL import ImageDraw, ImageFilter
    W, H = size
    img = Image.new('L', size, 0)
    d   = ImageDraw.Draw(img)
    mid = H // 2
    # Draw flatline
    d.line([(0, mid), (W, mid)], fill=100, width=1)
    # QRS complexes every ~30px
    for bx in range(20, W-10, 32):
        pts = [(bx, mid), (bx+3, mid-2), (bx+5, mid+H//6),
               (bx+7, mid-H//3), (bx+9, mid+H//5), (bx+12, mid-1), (bx+15, mid)]
        d.line(pts, fill=255, width=2)
    img = img.filter(ImageFilter.GaussianBlur(0.8))
    return img


def make_alien_face(size=(128, 64)):
    """Grey alien face — big eyes, small mouth."""
    from PIL import ImageDraw
    W, H = size
    img = Image.new('L', size, 0)
    d   = ImageDraw.Draw(img)
    cx, cy = W//2, H//2
    # Head (inverted triangle-ish)
    hw, hh = W//3, H//2-2
    d.ellipse([cx-hw, cy-hh, cx+hw, cy+hh+4], fill=120)
    # Chin
    d.polygon([(cx-hw//2, cy+hh//2), (cx, cy+hh+4), (cx+hw//2, cy+hh//2)], fill=120)
    # Eyes — big, black, almond-shaped
    ew, eh = hw//2+4, hh//3+2
    d.ellipse([cx-hw//2-ew//2, cy-eh, cx-hw//2+ew//2, cy+eh//2], fill=255)
    d.ellipse([cx+hw//2-ew//2, cy-eh, cx+hw//2+ew//2, cy+eh//2], fill=255)
    # Pupils
    d.ellipse([cx-hw//2-3, cy-3, cx-hw//2+3, cy+3], fill=0)
    d.ellipse([cx+hw//2-3, cy-3, cx+hw//2+3, cy+3], fill=0)
    # Mouth — small line
    d.line([(cx-6, cy+hh//2+2), (cx+6, cy+hh//2+2)], fill=60, width=1)
    return img


def make_sos_morse(size=(128, 64)):
    """SOS in Morse code as visual pattern: ... --- ..."""
    W, H = size
    arr = np.zeros((H, W), dtype=np.uint8)
    mid_y = H // 2
    bar_h = max(H // 3, 6)
    x = 8
    dot_w, dash_w, gap, letter_gap = 3, 9, 3, 8
    pattern = [  # S=...  O=---  S=...
        dot_w, gap, dot_w, gap, dot_w, letter_gap,
        dash_w, gap, dash_w, gap, dash_w, letter_gap,
        dot_w, gap, dot_w, gap, dot_w,
    ]
    for i, pw in enumerate(pattern):
        if i % 2 == 0:  # signal element
            arr[mid_y-bar_h//2:mid_y+bar_h//2, x:min(x+pw, W)] = 240
        x += pw
        if x >= W:
            break
    # Repeat pattern across width
    segment_w = x
    if segment_w > 0 and segment_w < W:
        tile = arr[:, :segment_w].copy()
        for ox in range(segment_w + 12, W - segment_w, segment_w + 12):
            end = min(ox + segment_w, W)
            arr[:, ox:end] = tile[:, :end-ox]
    return Image.fromarray(arr, 'L')


def make_fractal_tree(size=(128, 64)):
    """Recursive fractal tree."""
    from PIL import ImageDraw
    W, H = size
    img = Image.new('L', size, 0)
    d   = ImageDraw.Draw(img)
    def _branch(x, y, length, angle, depth):
        if depth <= 0 or length < 2:
            return
        x2 = x + int(length * np.cos(angle))
        y2 = y - int(length * np.sin(angle))
        bright = min(255, 80 + depth * 30)
        d.line([(x, y), (x2, y2)], fill=bright, width=max(1, depth//2))
        _branch(x2, y2, length * 0.67, angle + 0.45, depth - 1)
        _branch(x2, y2, length * 0.67, angle - 0.45, depth - 1)
    _branch(W//2, H-2, H//3, np.pi/2, 7)
    return img


def make_wave_collapse(size=(128, 64)):
    """Collapsing sine waves — multiple frequencies decaying to center."""
    W, H = size
    x = np.linspace(0, 8*np.pi, W)
    arr = np.zeros((H, W), dtype=np.float32)
    for row in range(H):
        decay = 1.0 - abs(row - H/2) / (H/2)
        freq = 1.0 + 3.0 * (row / H)
        arr[row] = decay * (0.5 + 0.5 * np.sin(freq * x + row * 0.3))
    arr = (arr / arr.max() * 255).astype(np.uint8)
    return Image.fromarray(arr, 'L')


# ── Feld-Hellschreiber Encoder ────────────────────────────────────────────────
# Classic Feld-Hell: 7-pixel tall bitmap font, each column is one audio frame.
# Text scrolls horizontally across the waterfall. Each row = one frequency.
# Lit pixels produce sine tones; dark pixels are silence.
# Column rate: ~8.6 columns/sec (122.5ms per column) for standard Feld-Hell,
# but we allow tuning to match SDR scroll speed.

# 5x7 bitmap font — each char is a list of 5 column bytes (bit 0 = top row)
_HELL_FONT = {
    'A': [0x7E,0x09,0x09,0x09,0x7E], 'B': [0x7F,0x49,0x49,0x49,0x36],
    'C': [0x3E,0x41,0x41,0x41,0x22], 'D': [0x7F,0x41,0x41,0x41,0x3E],
    'E': [0x7F,0x49,0x49,0x49,0x41], 'F': [0x7F,0x09,0x09,0x09,0x01],
    'G': [0x3E,0x41,0x49,0x49,0x3A], 'H': [0x7F,0x08,0x08,0x08,0x7F],
    'I': [0x41,0x41,0x7F,0x41,0x41], 'J': [0x20,0x40,0x40,0x40,0x3F],
    'K': [0x7F,0x08,0x14,0x22,0x41], 'L': [0x7F,0x40,0x40,0x40,0x40],
    'M': [0x7F,0x02,0x0C,0x02,0x7F], 'N': [0x7F,0x02,0x04,0x08,0x7F],
    'O': [0x3E,0x41,0x41,0x41,0x3E], 'P': [0x7F,0x09,0x09,0x09,0x06],
    'Q': [0x3E,0x41,0x51,0x21,0x5E], 'R': [0x7F,0x09,0x19,0x29,0x46],
    'S': [0x26,0x49,0x49,0x49,0x32], 'T': [0x01,0x01,0x7F,0x01,0x01],
    'U': [0x3F,0x40,0x40,0x40,0x3F], 'V': [0x0F,0x30,0x40,0x30,0x0F],
    'W': [0x3F,0x40,0x30,0x40,0x3F], 'X': [0x63,0x14,0x08,0x14,0x63],
    'Y': [0x03,0x04,0x78,0x04,0x03], 'Z': [0x61,0x51,0x49,0x45,0x43],
    '0': [0x3E,0x51,0x49,0x45,0x3E], '1': [0x00,0x42,0x7F,0x40,0x00],
    '2': [0x62,0x51,0x49,0x49,0x46], '3': [0x22,0x41,0x49,0x49,0x36],
    '4': [0x18,0x14,0x12,0x7F,0x10], '5': [0x27,0x45,0x45,0x45,0x39],
    '6': [0x3E,0x49,0x49,0x49,0x32], '7': [0x01,0x71,0x09,0x05,0x03],
    '8': [0x36,0x49,0x49,0x49,0x36], '9': [0x26,0x49,0x49,0x49,0x3E],
    ' ': [0x00,0x00,0x00,0x00,0x00], '.': [0x00,0x60,0x60,0x00,0x00],
    ',': [0x00,0x80,0x60,0x00,0x00], '!': [0x00,0x00,0x5F,0x00,0x00],
    '?': [0x02,0x01,0x59,0x09,0x06], '-': [0x08,0x08,0x08,0x08,0x08],
    '/': [0x40,0x20,0x10,0x08,0x04], ':': [0x00,0x36,0x36,0x00,0x00],
    '=': [0x14,0x14,0x14,0x14,0x14], '+': [0x08,0x08,0x3E,0x08,0x08],
    '(': [0x00,0x1C,0x22,0x41,0x00], ')': [0x00,0x41,0x22,0x1C,0x00],
    '@': [0x3E,0x41,0x5D,0x55,0x0E], '#': [0x14,0x7F,0x14,0x7F,0x14],
    '$': [0x24,0x2A,0x7F,0x2A,0x12], '%': [0x23,0x13,0x08,0x64,0x62],
}


def hellschreiber_encode(text, bandwidth=2400.0, base_freq=200.0,
                         col_duration=0.1225, repeat=2, sample_rate=44100):
    """
    Encode text as Feld-Hellschreiber audio for SDR waterfall display.
    
    Each character is 5 columns × 7 rows. Each column becomes one audio frame.
    Each row maps to a frequency within the bandwidth. Lit pixels produce tones.
    Text is transmitted `repeat` times (standard Hell repeats 2x for readability).
    
    Returns: numpy array of audio samples (float, -1 to 1)
    """
    text = text.upper()
    
    # Build column data: list of 7-bit columns
    columns = []
    for ch in text:
        glyph = _HELL_FONT.get(ch, _HELL_FONT.get(' '))
        for col_byte in glyph:
            columns.append(col_byte)
        columns.append(0x00)  # 1-column gap between characters
    
    # 7 frequency rows spanning the bandwidth
    n_rows = 7
    # Spread rows across 70% of bandwidth (centered) for better visibility
    freqs = np.linspace(base_freq + bandwidth * 0.15,
                        base_freq + bandwidth * 0.85, n_rows)
    
    samples_per_col = int(sample_rate * col_duration)
    t = np.linspace(0, col_duration, samples_per_col, endpoint=False)
    
    # Each tone includes fundamental + slight spread for wider waterfall dots
    freq_spread = bandwidth / (n_rows * 4)  # spread each dot slightly
    sine_basis = np.array([
        np.sin(2.0 * np.pi * f * t) * 0.7 +
        np.sin(2.0 * np.pi * (f - freq_spread) * t) * 0.15 +
        np.sin(2.0 * np.pi * (f + freq_spread) * t) * 0.15
        for f in freqs
    ])
    
    all_frames = []
    for _ in range(repeat):
        for col_byte in columns:
            frame = np.zeros(samples_per_col)
            for bit in range(n_rows):
                if col_byte & (1 << bit):
                    frame += sine_basis[bit]
            # Normalize this frame
            peak = np.max(np.abs(frame))
            if peak > 0:
                frame = frame / peak * 0.7
            # Fade edges to prevent clicks
            fl = min(int(sample_rate * 0.003), samples_per_col // 4)
            frame[:fl] *= np.linspace(0, 1, fl)
            frame[-fl:] *= np.linspace(1, 0, fl)
            all_frames.append(frame)
        # Gap between repeats
        all_frames.append(np.zeros(int(sample_rate * 0.5)))
    
    audio = np.concatenate(all_frames)
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio * (0.8 / peak)
    return audio


def hellschreiber_to_wav(text, output_wav=None, **kwargs):
    """Encode Hellschreiber text to WAV file. Returns path."""
    if output_wav is None:
        output_wav = tempfile.mktemp(suffix='_hell.wav')
    audio = hellschreiber_encode(text, **kwargs)
    audio_i16 = (audio * 32767).astype(np.int16)
    with wave.open(output_wav, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(kwargs.get('sample_rate', SAMPLE_RATE))
        wf.writeframes(audio_i16.tobytes())
    dur = len(audio) / kwargs.get('sample_rate', SAMPLE_RATE)
    logger.info(f'Hellschreiber: "{text}" -> {os.path.getsize(output_wav)//1024}KB, {dur:.1f}s')
    return output_wav


CANNED_IMAGES = {
    # Standard shapes
    'smiley':   (make_smiley,   'Smiley Face'),
    'moon':     (make_moon,     'Crescent Moon'),
    'flower':   (make_flower,   'Flower'),
    'diamond':  (make_diamond,  'Diamond'),
    'callsign': (make_callsign, 'Callsign / CQ'),
    'chevron':  (make_chevron,  'Chevron / Arrow'),
    # Trippy / generative
    'plasma':         (make_plasma,           'Plasma / Interference'),
    'lissajous':      (make_lissajous,        'Lissajous Figure'),
    'spiral':         (make_spiral,           'Archimedean Spiral'),
    'mandelbrot':     (make_mandelbrot,        'Mandelbrot Slice'),
    'dna':            (make_dna_helix,         'DNA Double Helix'),
    'static':         (make_static_burst,      'Static Burst'),
    'sine_stack':     (make_sine_stack,        'Sine Wave Stack'),
    'radial':         (make_radial_burst,      'Radial Starburst'),
    'checkerboard':   (make_checkerboard_warp, 'Warped Checkerboard'),
    'interference':   (make_interference,      'Wave Interference'),
    'vortex':         (make_vortex,            'Galaxy Vortex'),
    'qrish':          (make_qrish,             'QR-ish Blocks'),
    # Bizarre / HF weirdness
    'skull':          (make_skull,             '☠ Skull & Crossbones'),
    'radioactive':    (make_radioactive,       '☢ Radioactive Trefoil'),
    'eye':            (make_eye,               '👁 All-Seeing Eye'),
    'barcode':        (make_barcode,           '▮ Mysterious Barcode'),
    'heartbeat':      (make_heartbeat,         '♡ ECG Heartbeat'),
    'alien_face':     (make_alien_face,        '👽 Grey Alien'),
    'sos_morse':      (make_sos_morse,         '🆘 SOS Morse Visual'),
    'fractal_tree':   (make_fractal_tree,      '🌳 Fractal Tree'),
    'wave_collapse':  (make_wave_collapse,     '🌊 Wave Collapse'),
}


# -- Image processing pipeline -------------------------------------------------

def _apply_tone_curve(arr, curve, gamma):
    """Map [0,1]->[0,1] amplitude through chosen tone curve."""
    g = max(0.05, gamma)
    if curve == 'linear':
        return arr
    elif curve == 'gamma':
        return np.power(np.clip(arr, 0, 1), g)
    elif curve == 'srgb':
        mask = arr <= 0.04045
        lin  = np.where(mask, arr/12.92, np.power((arr+0.055)/1.055, 2.4))
        return np.power(np.clip(lin, 0, 1), g)
    elif curve == 'log':
        return np.log1p(arr * 9.0) / math.log1p(9.0)
    elif curve == 'power':
        return np.power(np.clip(arr, 0, 1), 1.0/g)
    elif curve == 's_curve':
        k   = max(1.0, g * 7.0)
        out = 1.0 / (1.0 + np.exp(-k*(arr-0.5)))
        lo  = 1.0 / (1.0 + np.exp(k*0.5))
        hi  = 1.0 / (1.0 + np.exp(-k*0.5))
        return np.clip((out-lo)/(hi-lo), 0, 1)
    else:
        return np.power(np.clip(arr, 0, 1), g)


def process_image(
    img, target_w, target_h, *,
    brightness=1.0, contrast=1.5, gamma=0.7,
    sharpen=0.0, equalize=False, dither=False, invert=False,
    tone_curve='gamma', noise_floor=0.03,
    black_point=0, white_point=255,
    flip_v=False, flip_h=False,
):
    """Full processing pipeline. Returns float32 array (h,w) in [0,1]."""
    img = img.convert('L').resize((target_w, target_h), Image.LANCZOS)
    if equalize:
        img = ImageOps.equalize(img)
    if abs(brightness - 1.0) > 0.01:
        img = ImageEnhance.Brightness(img).enhance(brightness)
    if abs(contrast - 1.0) > 0.01:
        img = ImageEnhance.Contrast(img).enhance(contrast)
    if sharpen > 0.01:
        img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=int(sharpen*300), threshold=3))
    if dither:
        img = img.convert('1', dither=Image.Dither.FLOYDSTEINBERG).convert('L')
    if invert:
        img = ImageOps.invert(img)
    if black_point > 0 or white_point < 255:
        span = max(1, white_point - black_point)
        lut  = [0 if i <= black_point else
                255 if i >= white_point else
                int((i - black_point) / span * 255)
                for i in range(256)]
        img = img.point(lut)
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = _apply_tone_curve(arr, tone_curve, gamma)
    if noise_floor > 0:
        arr = arr * (1.0 - noise_floor) + noise_floor * (arr > 0).astype(np.float32)
    if flip_v:
        arr = arr[::-1, :]   # flip rows (fixes upside-down waterfall)
    if flip_h:
        arr = arr[:, ::-1]   # mirror horizontally
    return arr


def get_histogram(arr):
    """64-bucket histogram of float [0,1] array."""
    counts, _ = np.histogram(arr.flatten(), bins=64, range=(0.0,1.0))
    return counts.tolist()


def get_processed_preview(
    img, target_w, target_h, scale=4, **proc_kwargs
):
    """
    Process image and return:
    - PIL Image for preview (upscaled)
    - histogram bucket list (64 values)
    - stats dict (min, max, mean, std)
    """
    arr = process_image(img, target_w, target_h, **proc_kwargs)
    hist = get_histogram(arr)
    stats = {
        'min':  float(np.min(arr)),
        'max':  float(np.max(arr)),
        'mean': float(np.mean(arr)),
        'std':  float(np.std(arr)),
    }
    # Upscale for display
    preview_arr = np.clip(arr * 255, 0, 255).astype(np.uint8)
    preview_img = Image.fromarray(preview_arr, 'L')
    pw = min(target_w * scale, 640)
    ph = min(target_h * scale, 320)
    preview_img = preview_img.resize((pw, ph), Image.NEAREST)
    return preview_img, hist, stats


# -- Main encoder --------------------------------------------------------------

def image_to_waterfall_wav(
    image_path, output_wav=None, *,
    image_width=128, image_height=64,
    base_freq=200.0, bandwidth=2400.0, frame_duration=0.08,
    invert=False, normalize=True, add_markers=True,
    brightness=1.0, contrast=2.0, gamma=1.0,
    sharpen=0.3, equalize=True, dither=False,
    tone_curve='gamma', noise_floor=0.03,
    black_point=0, white_point=255,
    flip_v=False, flip_h=False,
    add_header_tone=None, add_footer_tone=None,
):
    if add_header_tone is not None or add_footer_tone is not None:
        add_markers = bool(add_header_tone) or bool(add_footer_tone)
    if output_wav is None:
        output_wav = tempfile.mktemp(suffix='_waterfall.wav')

    img    = Image.open(image_path)
    pixels = process_image(
        img, image_width, image_height,
        brightness=brightness, contrast=contrast, gamma=gamma,
        sharpen=sharpen, equalize=equalize, dither=dither, invert=invert,
        tone_curve=tone_curve, noise_floor=noise_floor,
        black_point=black_point, white_point=white_point,
        flip_v=flip_v, flip_h=flip_h,
    )

    logger.info(f"Waterfall encode: {image_width}x{image_height} curve={tone_curve} gamma={gamma:.2f} contrast={contrast:.2f}")

    freqs             = np.linspace(base_freq, base_freq+bandwidth, image_width)
    samples_per_frame = int(SAMPLE_RATE * frame_duration)
    t                 = np.linspace(0, frame_duration, samples_per_frame, endpoint=False)
    sine_basis        = np.sin(2.0 * np.pi * freqs[:,np.newaxis] * t[np.newaxis,:])

    all_frames = []
    if add_markers:
        md  = 0.25
        mt  = np.linspace(0, md, int(SAMPLE_RATE*md), endpoint=False)
        ins = np.cumsum(np.linspace(base_freq, base_freq+bandwidth, len(mt))) / SAMPLE_RATE
        pip = 0.55 * np.sin(2*np.pi*ins)
        fl  = int(SAMPLE_RATE*0.015)
        pip[:fl] *= np.linspace(0,1,fl); pip[-fl:] *= np.linspace(1,0,fl)
        all_frames += [pip, np.zeros(int(SAMPLE_RATE*0.1))]

    # Amplitude boost: SDR waterfalls use log/power color maps, so linear
    # pixel→amplitude mapping makes mid-tones nearly invisible.
    # Applying sqrt (power 0.5) to amplitudes boosts mid-tones significantly.
    boosted = np.power(np.clip(pixels, 0, 1), 0.5)

    for row_idx in range(image_height):
        row_amps = boosted[row_idx]
        # Per-row peak normalization — ensures each row uses full amplitude range
        row_peak = np.max(row_amps)
        if row_peak > 0.05:
            row_amps = row_amps / row_peak
        frame = np.dot(row_amps, sine_basis)
        fl    = min(int(SAMPLE_RATE*0.005), samples_per_frame//4)
        frame[:fl] *= np.linspace(0,1,fl); frame[-fl:] *= np.linspace(1,0,fl)
        all_frames.append(frame)

    if add_markers:
        pd  = 0.25
        pt  = np.linspace(0, pd, int(SAMPLE_RATE*pd), endpoint=False)
        pip = 0.45 * np.sin(2*np.pi*(base_freq+bandwidth*0.5)*pt)
        fl  = int(SAMPLE_RATE*0.015)
        pip[:fl] *= np.linspace(0,1,fl); pip[-fl:] *= np.linspace(1,0,fl)
        all_frames += [np.zeros(int(SAMPLE_RATE*0.1)), pip]

    audio = np.concatenate(all_frames)
    if normalize:
        peak = np.max(np.abs(audio))
        if peak > 0: audio = audio * (0.82 / peak)

    audio_i16 = (audio * 32767).astype(np.int16)
    with wave.open(output_wav, 'w') as wf:
        wf.setnchannels(1); wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE); wf.writeframes(audio_i16.tobytes())

    logger.info(f"WAV: {os.path.getsize(output_wav)//1024}KB, {len(audio)/SAMPLE_RATE:.1f}s")
    return output_wav


def get_transmission_info(image_width, image_height, base_freq, bandwidth, frame_duration):
    total = image_height * frame_duration
    return {
        'image_size':        f'{image_width}x{image_height} px',
        'frequency_range':   f'{base_freq:.0f}-{base_freq+bandwidth:.0f} Hz',
        'bandwidth':         f'{bandwidth:.0f} Hz',
        'freq_resolution':   f'{bandwidth/image_width:.1f} Hz/pixel',
        'frame_duration_ms': f'{frame_duration*1000:.0f} ms',
        'total_duration_s':  f'{total:.1f} s',
        'recommended_fft':   '2048' if bandwidth<=1000 else '4096' if bandwidth<=2000 else '8192',
    }
