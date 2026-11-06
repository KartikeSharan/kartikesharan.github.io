"""Draw a timing diagram (SVG) from the RISC16 testbench's VCD dump.

Usage: python3 tools/wave.py cpu.vcd out.svg [end_ns]
The colours come from the page's CSS (classes wv-*), so the figure follows
the solder mask colour picked on the site.
"""
import sys

def load(path):
    ids, ch, t = {}, {}, 0
    for l in open(path).read().split('\n'):
        l = l.strip()
        if l.startswith('$var'):
            p = l.split(); ids[p[3]] = p[4]
        elif l.startswith('#'):
            t = int(l[1:])
        elif l.startswith('b'):
            v, c = l[1:].split(); ch.setdefault(ids[c], []).append((t, v))
        elif l and l[0] in '01xz' and l[1:] in ids:
            ch.setdefault(ids[l[1:]], []).append((t, l[0]))
    return ch

MNEMONIC = {0x0035: 'MOV R0,53', 0x040F: 'MOV R1,15', 0x1900: 'MOV R2,R1', 0x2821: 'ADD R2,33',
            0x3100: 'ADD R0,R1', 0x5200: 'SUB R0,R2', 0x600C: 'AND R0,12', 0x0CA5: 'MOV R3,165',
            0x7D00: 'AND R3,R1', 0x9C00: 'OR R3,R0', 0xBC00: 'SHL R3', 0xC400: 'SHR R1',
            0x5600: 'SUB R1,R2', 0xF000: '(undefined)', 0xA00E: 'JMP 14'}
STATE = {1: 'F', 2: 'D', 3: 'E', 4: 'E', 5: 'E', 6: 'E', 7: 'E', 8: 'E', 9: 'W', 10: 'E', 11: 'E'}

def draw(ch, t0, t1, px_per_ns, title):
    PX = px_per_ns / 1000.0
    LEFT, ROWH = 64, 30
    W = LEFT + (t1 - t0) * PX + 8
    x = lambda t: LEFT + (max(min(t, t1), t0) - t0) * PX
    rows = [('clk', 'clk'), ('state', 'state'), ('PC', 'addr'), ('IR', 'ir'),
            ('R0', 'q0'), ('R1', 'q1'), ('R2', 'q2'), ('R3', 'q3')]
    H = ROWH * len(rows) + 34
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H}" class="wave" role="img"><title>{title}</title>']
    for tt in range(t0 + 5000, t1, 50000):
        o.append(f'<line class="wv-grid" x1="{x(tt):.1f}" y1="4" x2="{x(tt):.1f}" y2="{H-24}"/>')
    def segs(name):
        c, out = ch[name], []
        for i, (tt, v) in enumerate(c):
            te = c[i + 1][0] if i + 1 < len(c) else t1
            if te <= t0 or tt >= t1:
                continue
            out.append((max(tt, t0), min(te, t1), None if 'x' in v else int(v, 2)))
        return out
    for r, (lab, name) in enumerate(rows):
        y0 = 8 + r * ROWH; yh, yl, ym = y0 + 4, y0 + 20, y0 + 12
        o.append(f'<text class="wv-name" x="4" y="{ym+4}">{lab}</text>')
        if name == 'clk':
            d, c = [], ch['clk']
            for i, (tt, v) in enumerate(c):
                if tt < t0 or tt >= t1:
                    continue
                yy = yh if v == '1' else yl
                d.append(f'M{x(tt):.1f},{yy}' if not d else f'V{yy}')
                te = c[i + 1][0] if i + 1 < len(c) else t1
                d.append(f'H{x(te):.1f}')
            o.append(f'<path class="wv-clk" d="{" ".join(d)}"/>')
            continue
        for a, b, v in segs(name):
            xa, xb = x(a), x(b)
            if xb - xa < 1:
                continue
            o.append(f'<path class="wv-bus" d="M{xa+2:.1f},{yh} H{xb-2:.1f} L{xb:.1f},{ym} L{xb-2:.1f},{yl} H{xa+2:.1f} L{xa:.1f},{ym} Z"/>')
            if v is None:
                continue
            if name == 'state': txt = STATE.get(v, '')
            elif name == 'ir': txt = MNEMONIC.get(v, f'{v:04X}') if v else ''
            elif name == 'addr': txt = str(v)
            else: txt = str(v - 65536 if v >= 32768 else v)
            if txt and xb - xa > len(txt) * 5.6 + 4:
                o.append(f'<text class="wv-val" x="{(xa+xb)/2:.1f}" y="{ym+3.5}" text-anchor="middle">{txt}</text>')
    for tt in range(t0 + 5000, t1, 100000):
        o.append(f'<text class="wv-axis" x="{x(tt):.1f}" y="{H-8}" text-anchor="middle">{(tt-t0-5000)//1000} ns</text>')
    o.append('</svg>')
    return '\n'.join(o)

if __name__ == '__main__':
    vcd, out = sys.argv[1], sys.argv[2]
    end_ns = int(sys.argv[3]) if len(sys.argv) > 3 else 850
    ch = load(vcd)
    px = 1.25 if end_ns > 500 else 2.6
    title = ('Simulation of the revised RISC16 processor running its test program: '
             'control state, program counter, instruction register and the four registers')
    open(out, 'w').write(draw(ch, 125000, end_ns * 1000, px, title))
