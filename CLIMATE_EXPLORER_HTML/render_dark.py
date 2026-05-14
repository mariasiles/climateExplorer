"""
Re-renderiza los gráficos de fase2/fase3/fase4 con fondo transparente + texto/ejes
en tono claro. NO toca los colores intencionales (rojos, azules, verdes que las
fases asignan explícitamente). Solo cambia el "chrome" (fondos, ejes, ticks,
labels, títulos, leyendas, grids).

Salida: CLIMATE_EXPLORER_HTML/grafics_dark/

Uso:
    cd CLIMATE_EXPLORER_HTML
    py -3.12 render_dark.py
"""
from __future__ import annotations

import os
import sys
import runpy
import warnings

import matplotlib
matplotlib.use("Agg")  # no display

import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

warnings.filterwarnings("ignore")

# ── paths ───────────────────────────────────────────────────────────────
HERE   = os.path.dirname(os.path.abspath(__file__))
GLOBAL = os.path.normpath(os.path.join(HERE, "..", "GLOBAL"))
OUT    = os.path.join(HERE, "grafics_dark")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, GLOBAL)

# ── design tokens (must match style.css CarbonPlan tokens) ──────────────
FG       = "#ebebec"   # primary text
MUTED    = "#a9aaad"   # axes labels / ticks
DIM      = "#7a7c80"   # subtle elements
GRID     = "#3a3e45"   # grid lines
LEGEND_BG = (0.11, 0.13, 0.16, 0.55)  # rgba — translucent over page

# ── apply dark rcParams ─────────────────────────────────────────────────
DARK_RC = {
    "figure.facecolor":   "none",
    "figure.edgecolor":   "none",
    "axes.facecolor":     "none",
    "savefig.facecolor":  "none",
    "savefig.edgecolor":  "none",
    "savefig.transparent": True,

    "axes.edgecolor":     MUTED,
    "axes.labelcolor":    FG,
    "axes.titlecolor":    FG,
    "axes.spines.top":    False,
    "axes.spines.right":  False,

    "xtick.color":        MUTED,
    "ytick.color":        MUTED,
    "xtick.labelcolor":   MUTED,
    "ytick.labelcolor":   MUTED,

    "text.color":         FG,

    "grid.color":         GRID,
    "grid.alpha":         0.55,
    "grid.linewidth":     0.6,
    "grid.linestyle":     "-",

    "legend.facecolor":   "#1f2329",
    "legend.edgecolor":   GRID,
    "legend.labelcolor":  FG,
    "legend.frameon":     True,

    "figure.dpi":         130,
    "savefig.dpi":        160,
    "font.size":          11,
    "font.family":        "DejaVu Sans",
}
plt.rcParams.update(DARK_RC)

# seaborn often resets rcParams when set_theme is called inside fase scripts
# patch it to merge our DARK_RC after each call
_orig_set_theme = sns.set_theme
def _patched_set_theme(*args, **kwargs):
    _orig_set_theme(*args, **kwargs)
    plt.rcParams.update(DARK_RC)
sns.set_theme = _patched_set_theme

# also intercept any plt.style.use call
_orig_style_use = plt.style.use
def _patched_style_use(*args, **kwargs):
    _orig_style_use(*args, **kwargs)
    plt.rcParams.update(DARK_RC)
plt.style.use = _patched_style_use


# ── force-recolor every drawn element before saving ─────────────────────
def _force_dark_chrome(fig):
    """
    Walk every Axes in the figure and force chrome elements (bg, axes,
    ticks, labels, titles, legends, grid, bbox annotations) to dark palette.
    Does NOT touch line/fill/marker colors that the script set explicitly.
    """
    fig.patch.set_facecolor("none")
    fig.patch.set_edgecolor("none")

    for ax in fig.get_axes():
        # bg
        ax.set_facecolor("none")
        # spines
        for spine in ax.spines.values():
            spine.set_edgecolor(MUTED)
            spine.set_linewidth(0.8)
        # ticks
        ax.tick_params(colors=MUTED, which="both")
        # axis labels & title
        if ax.xaxis.label is not None:
            ax.xaxis.label.set_color(FG)
        if ax.yaxis.label is not None:
            ax.yaxis.label.set_color(FG)
        if ax.title is not None:
            ax.title.set_color(FG)

        # grids
        ax.grid(True, color=GRID, alpha=0.45, linewidth=0.6)
        for gl in ax.get_xgridlines() + ax.get_ygridlines():
            gl.set_color(GRID)
            gl.set_alpha(0.45)

        # legend
        leg = ax.get_legend()
        if leg is not None:
            fr = leg.get_frame()
            fr.set_facecolor("#1f2329")
            fr.set_edgecolor(GRID)
            fr.set_alpha(0.85)
            for txt in leg.get_texts():
                txt.set_color(FG)

        # free-floating text — only recolor if it's pure black (the default
        # matplotlib draws) — preserves colored annotations
        for txt in ax.texts:
            c = txt.get_color()
            if c in ("black", "k", "#000000", (0, 0, 0, 1), (0.0, 0.0, 0.0, 1.0)):
                txt.set_color(FG)
            # bbox background — if white, swap to translucent dark
            bbox = txt.get_bbox_patch()
            if bbox is not None:
                fc = bbox.get_facecolor()
                if fc in ("white", "w", "#ffffff", (1, 1, 1, 1), (1.0, 1.0, 1.0, 1.0)):
                    bbox.set_facecolor((0.11, 0.13, 0.16, 0.7))
                    bbox.set_edgecolor(GRID)


# ── patch plt.savefig: redirect output + force dark chrome + transparent  ─
_orig_savefig = plt.savefig

def _patched_savefig(fname, *args, **kwargs):
    fig = kwargs.pop("_fig", None) or plt.gcf()
    _force_dark_chrome(fig)
    # always transparent
    kwargs["facecolor"]   = "none"
    kwargs["edgecolor"]   = "none"
    kwargs["transparent"] = True
    # redirect path
    if isinstance(fname, str):
        base = os.path.basename(fname)
        out_path = os.path.join(OUT, base)
        print(f"   -> {base}")
        return _orig_savefig.__wrapped__(out_path, *args, **kwargs) if hasattr(_orig_savefig, "__wrapped__") else _orig_savefig(out_path, *args, **kwargs)
    return _orig_savefig(fname, *args, **kwargs)

plt.savefig = _patched_savefig

# also override Figure.savefig (since some scripts call fig.savefig directly)
from matplotlib.figure import Figure
_orig_fig_savefig = Figure.savefig
def _patched_fig_savefig(self, fname, *args, **kwargs):
    _force_dark_chrome(self)
    kwargs["facecolor"]   = "none"
    kwargs["edgecolor"]   = "none"
    kwargs["transparent"] = True
    if isinstance(fname, str):
        base = os.path.basename(fname)
        out_path = os.path.join(OUT, base)
        print(f"   -> {base}")
        return _orig_fig_savefig(self, out_path, *args, **kwargs)
    return _orig_fig_savefig(self, fname, *args, **kwargs)
Figure.savefig = _patched_fig_savefig

# disable plt.show
plt.show = lambda *a, **k: None


# ── run each fase script ────────────────────────────────────────────────
def run_phase(name: str) -> None:
    path = os.path.join(GLOBAL, name)
    if not os.path.isfile(path):
        print(f"  !! {name} not found, skipping")
        return
    print(f"\n══ running {name} ══")
    # re-apply our rcParams (in case prior phase imported a module that reset them)
    plt.rcParams.update(DARK_RC)
    # restore seaborn patch
    sns.set_theme = _patched_set_theme
    try:
        runpy.run_path(path, run_name="__main__")
    except SystemExit:
        pass
    finally:
        plt.close("all")


if __name__ == "__main__":
    print(f"Output -> {OUT}")
    for phase in [
        "fase2_analisi_descriptiva.py",
        "fase3_correlacions.py",
        "fase4_ia_regressio_conclusions.py",
    ]:
        run_phase(phase)
    print("\nDone.")
