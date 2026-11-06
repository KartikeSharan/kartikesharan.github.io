"""Plot the Sentaurus I-V results (DF-ISE .plt) as a theme-aware SVG.

Usage: python3 tools/tcad_plot.py <dir with n8_des.plt and n10_des.plt> assets/fig/tcad-iv.svg
Colours are placeholders swapped for the site's CSS variables afterwards.
"""
import re, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

SUP = str.maketrans('-0123456789', '⁻⁰¹²³⁴⁵⁶⁷⁸⁹')

def load(path):
    t = open(path).read()
    v = np.array([float(x) for x in t.split('Data {')[1].split('}')[0].split()]).reshape(-1, 17)
    V, I = v[:, 9], v[:, 15]                 # p_contact OuterVoltage, p_contact TotalCurrent
    k = int(np.argmin(V))                    # the sweep goes 0 -> -1 V, then -1 -> +0.6 V
    V, I = V[k:], np.abs(I[k:])
    keep = (np.abs(V) > 0.03) & (I > 0)     # skip the zero crossing, where log|I| is noise
    return V[keep], I[keep]

def main(src, out):
    plt.rcParams.update({'svg.fonttype': 'none', 'font.family': 'sans-serif', 'font.size': 10})
    SILK, PAD, HI, GRID, MUTED, LINK = '#010101', '#020202', '#030303', '#040404', '#050505', '#060606'
    fig, ax = plt.subplots(figsize=(8, 4.4))
    for f, c, lab, ls in [('n10_des.plt', PAD, 'SRH recombination in the neutral regions', '-'),
                          ('n8_des.plt', HI, 'No recombination model', '--')]:
        V, I = load(f'{src}/{f}')
        neg, pos = V < 0, V > 0
        ax.semilogy(V[neg], I[neg], ls, color=c, lw=2.2, label=lab)
        ax.semilogy(V[pos], I[pos], ls, color=c, lw=2.2)
    ax.set_xlabel('Voltage on the p contact (V)', color=SILK)
    ax.set_ylabel('Current (A/µm)', color=SILK)
    ax.set_xlim(-1.02, 0.62); ax.set_ylim(1e-19, 1e-7)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '10' + str(int(round(np.log10(y)))).translate(SUP)))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.1f}'.replace('-', '−')))
    ax.grid(True, which='major', color=GRID, lw=0.6)
    for s in ax.spines.values(): s.set_color(MUTED)
    ax.tick_params(colors=SILK, which='both')
    ax.annotate('6.3 × 10⁻¹⁷ A/µm at −1 V', xy=(-1, 6.35e-17), xytext=(-0.9, 2e-15), color=LINK,
                arrowprops=dict(arrowstyle='-', color=LINK, lw=1))
    ax.annotate('1.6 × 10⁻¹⁸ A/µm', xy=(-1, 1.64e-18), xytext=(-0.9, 1.6e-19 * 2.2), color=HI,
                arrowprops=dict(arrowstyle='-', color=HI, lw=1))
    ax.annotate('about 60 mV per decade', xy=(0.45, 2.5e-11), xytext=(0.0, 3e-9), color=SILK,
                arrowprops=dict(arrowstyle='-', color=SILK, lw=1))
    leg = ax.legend(loc='upper left', frameon=False)
    for t in leg.get_texts(): t.set_color(SILK)
    fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    fig.tight_layout()
    fig.savefig(out, transparent=True)
    s = open(out).read()
    for k, v in {SILK: 'var(--silk)', PAD: 'var(--pad)', HI: 'var(--trace-hi)', GRID: 'var(--grid)', MUTED: 'var(--muted)', LINK: 'var(--link)'}.items():
        s = s.replace(k, v)
    s = re.sub(r'<\?xml[^>]*>\s*', '', s)
    s = re.sub(r'<!DOCTYPE[^>]*>\s*', '', s)
    s = re.sub(r'<metadata>.*?</metadata>\s*', '', s, flags=re.S)
    s = s.replace('font-family:', 'font-family: var(--font-body),')
    s = s.replace('<svg ', '<svg role="img" aria-label="Current against voltage for the two simulation runs, on a log scale" ', 1)
    open(out, 'w').write(s)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
