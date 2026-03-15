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
    brightness=1.0, contrast=1.5, gamma=0.7,
    sharpen=0.0, equalize=False, dither=False,
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

    for row_idx in range(image_height):
        frame = np.dot(pixels[row_idx], sine_basis)
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
