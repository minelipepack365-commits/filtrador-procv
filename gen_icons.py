# Gera os icones PNG do PWA (sem dependencias externas).
#
# Desenha o mesmo selo do icone PROCV: fundo azul (#2F81F7 -> #1f6feb),
# "X" do Excel e uma mini grade de tabela, ambos em branco.
#
# Uso:  python gen_icons.py

import math
import os
import struct
import zlib

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, 'icons')

C_TOP = (0x3d, 0x8b, 0xfd)     # azul claro do topo
C_BOT = (0x1c, 0x63, 0xd6)     # azul escuro da base

# Conteudo em espaco normalizado [0,1].
BARS = [
    (0.17, 0.22, 0.52, 0.57, 0.090),   # X - diagonal 1
    (0.52, 0.22, 0.17, 0.57, 0.090),   # X - diagonal 2
    (0.59, 0.33, 0.87, 0.33, 0.042),   # grade - topo
    (0.59, 0.62, 0.87, 0.62, 0.042),   # grade - base
    (0.59, 0.33, 0.59, 0.62, 0.042),   # grade - esquerda
    (0.73, 0.33, 0.73, 0.62, 0.042),   # grade - meio
    (0.87, 0.33, 0.87, 0.62, 0.042),   # grade - direita
]
CX, CY = 0.515, 0.46                  # centro do conteudo


def png_bytes(w, h, rgba):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += rgba[y * w * 4:(y + 1) * w * 4]

    def chunk(tag, data):
        return (struct.pack('>I', len(data)) + tag + data +
                struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff))

    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
            + chunk(b'IEND', b''))


def sd_round_rect(px, py, cx, cy, hw, hh, r):
    qx = abs(px - cx) - (hw - r)
    qy = abs(py - cy) - (hh - r)
    return math.hypot(max(qx, 0.0), max(qy, 0.0)) + min(max(qx, qy), 0.0) - r


def sd_segment(px, py, x1, y1, x2, y2, w):
    dx, dy = x2 - x1, y2 - y1
    ll = dx * dx + dy * dy
    t = 0.0 if ll == 0 else max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / ll))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy)) - w / 2.0


def render(size, radius_frac, content_scale=1.0, ss=3):
    """radius_frac=0 -> quadrado cheio (maskable / iOS)."""
    px = bytearray(size * size * 4)
    r = radius_frac * size
    hw = hh = size / 2.0

    for y in range(size):
        fy = y + 0.5
        for x in range(size):
            fx = x + 0.5
            acc_bg = 0
            acc_fg = 0
            for sy in range(ss):
                for sx in range(ss):
                    sfx = fx + (sx + 0.5) / ss - 0.5
                    sfy = fy + (sy + 0.5) / ss - 0.5
                    if sd_round_rect(sfx, sfy, hw, hh, hw, hh, r) <= 0:
                        acc_bg += 1
                        u = 0.5 + (sfx / size - CX) * content_scale
                        v = 0.5 + (sfy / size - CY) * content_scale
                        for x1, y1, x2, y2, w in BARS:
                            if sd_segment(u, v, x1, y1, x2, y2, w) <= 0:
                                acc_fg += 1
                                break

            total = ss * ss
            ab = acc_bg / total
            af = (acc_fg / total) * ab
            if ab <= 0:
                continue

            # fundo com gradiente vertical
            t = fy / size
            br = round(C_TOP[0] + (C_BOT[0] - C_TOP[0]) * t)
            bg = round(C_TOP[1] + (C_BOT[1] - C_TOP[1]) * t)
            bb = round(C_TOP[2] + (C_BOT[2] - C_TOP[2]) * t)

            a = ab * (1 - af)
            i = (y * size + x) * 4
            px[i] = round(br * (1 - af) + 255 * af)
            px[i + 1] = round(bg * (1 - af) + 255 * af)
            px[i + 2] = round(bb * (1 - af) + 255 * af)
            px[i + 3] = round(255 * a)

    return png_bytes(size, size, px)


def main():
    os.makedirs(OUT, exist_ok=True)

    targets = [
        ('icon-192.png',        192, 0.22, 1.0),
        ('icon-512.png',        512, 0.22, 1.0),
        ('maskable-512.png',    512, 0.0,  0.76),
        ('apple-touch-icon.png', 180, 0.0,  1.0),
        ('favicon-32.png',       32, 0.22, 1.0),
    ]

    for name, size, rad, scale in targets:
        dest = os.path.join(OUT, name)
        with open(dest, 'wb') as f:
            f.write(render(size, rad, scale))
        print('OK  icons/%-22s %4dpx  %5.1f KB' % (name, size, os.path.getsize(dest) / 1024))

    shutil_favicon()


def shutil_favicon():
    src = os.path.join(OUT, 'favicon-32.png')
    with open(src, 'rb') as f:
        data = f.read()
    for dest in (os.path.join(BASE, 'favicon.png'),):
        with open(dest, 'wb') as f:
            f.write(data)
        print('OK  %-29s %5.1f KB' % ('favicon.png', os.path.getsize(dest) / 1024))


if __name__ == '__main__':
    main()