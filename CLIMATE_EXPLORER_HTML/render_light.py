"""
Re-renderiza los gráficos con fondo claro (#f7f7f7) — tema light.
Salida: CLIMATE_EXPLORER_HTML/grafics_light/

Uso:
    cd CLIMATE_EXPLORER_HTML
    py render_light.py
"""
from __future__ import annotations

import os
import sys
import runpy
import warnings

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

warnings.filterwarnings("ignore")

HERE   = os.path.dirname(os.path.abspath(__file__))
GLOBAL = os.path.normpath(os.path.join(HERE, "..", "..", "GLOBAL"))
OUT    = os.path.join(HERE, "grafics_light")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, GLOBAL)

BG     = "#fff8f2"
FG     = "#1a1a1a"
MUTED  = "#666666"
DIM    = "#aaaaaa"
GRID   = "#dedede"
LEGEND_BG = (0.97, 0.97, 0.97, 0.90)

LIGHT_RC = {
    "figure.facecolor":   BG,
    "figure.edgecolor":   "none",
    "axes.facecolor":     BG,
    "savefig.facecolor":  BG,
    "savefig.edgecolor":  "none",
    "savefig.transparent": False,

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
    "grid.alpha":         0.8,
    "grid.linewidth":     0.6,
    "grid.linestyle":     "-",

    "legend.facecolor":   "#f0f0f0",
    "legend.edgecolor":   GRID,
    "legend.labelcolor":  FG,
    "legend.frameon":     True,

    "figure.dpi":         130,
    "savefig.dpi":        160,
    "font.size":          11,
    "font.family":        "DejaVu Sans",
}
plt.rcParams.update(LIGHT_RC)

_orig_set_theme = sns.set_theme
def _patched_set_theme(*args, **kwargs):
    _orig_set_theme(*args, **kwargs)
    plt.rcParams.update(LIGHT_RC)
sns.set_theme = _patched_set_theme

_orig_style_use = plt.style.use
def _patched_style_use(*args, **kwargs):
    _orig_style_use(*args, **kwargs)
    plt.rcParams.update(LIGHT_RC)
plt.style.use = _patched_style_use


def _force_light_chrome(fig):
    fig.patch.set_facecolor(BG)
    fig.patch.set_edgecolor("none")

    for ax in fig.get_axes():
        ax.set_facecolor(BG)
        for spine in ax.spines.values():
            spine.set_edgecolor(MUTED)
            spine.set_linewidth(0.8)
        ax.tick_params(colors=MUTED, which="both")
        if ax.xaxis.label is not None:
            ax.xaxis.label.set_color(FG)
        if ax.yaxis.label is not None:
            ax.yaxis.label.set_color(FG)
        if ax.title is not None:
            ax.title.set_color(FG)

        ax.grid(True, color=GRID, alpha=0.7, linewidth=0.6)
        for gl in ax.get_xgridlines() + ax.get_ygridlines():
            gl.set_color(GRID)
            gl.set_alpha(0.7)

        leg = ax.get_legend()
        if leg is not None:
            fr = leg.get_frame()
            fr.set_facecolor("#f0f0f0")
            fr.set_edgecolor(GRID)
            fr.set_alpha(0.95)
            for txt in leg.get_texts():
                txt.set_color(FG)

        for txt in ax.texts:
            c = txt.get_color()
            if c in ("white", "w", "#ffffff", (1, 1, 1, 1), (1.0, 1.0, 1.0, 1.0)):
                txt.set_color(FG)
            bbox = txt.get_bbox_patch()
            if bbox is not None:
                fc = bbox.get_facecolor()
                if fc in ("black", "k", "#000000", "#1b1e23", (0, 0, 0, 1)):
                    bbox.set_facecolor((0.95, 0.95, 0.95, 0.85))
                    bbox.set_edgecolor(GRID)


_orig_savefig = plt.savefig

def _patched_savefig(fname, *args, **kwargs):
    fig = kwargs.pop("_fig", None) or plt.gcf()
    _force_light_chrome(fig)
    kwargs["facecolor"]    = BG
    kwargs["edgecolor"]    = "none"
    kwargs["transparent"]  = False
    if isinstance(fname, str):
        base = os.path.basename(fname)
        out_path = os.path.join(OUT, base)
        print(f"   -> {base}")
        return _orig_savefig(out_path, *args, **kwargs)
    return _orig_savefig(fname, *args, **kwargs)

plt.savefig = _patched_savefig

from matplotlib.figure import Figure
_orig_fig_savefig = Figure.savefig
def _patched_fig_savefig(self, fname, *args, **kwargs):
    _force_light_chrome(self)
    kwargs["facecolor"]   = BG
    kwargs["edgecolor"]   = "none"
    kwargs["transparent"] = False
    if isinstance(fname, str):
        base = os.path.basename(fname)
        out_path = os.path.join(OUT, base)
        print(f"   -> {base}")
        return _orig_fig_savefig(self, out_path, *args, **kwargs)
    return _orig_fig_savefig(self, fname, *args, **kwargs)
Figure.savefig = _patched_fig_savefig

plt.show = lambda *a, **k: None


def run_phase(name: str) -> None:
    path = os.path.join(GLOBAL, name)
    if not os.path.isfile(path):
        print(f"  !! {name} not found, skipping")
        return
    print(f"\n== running {name} ==")
    plt.rcParams.update(LIGHT_RC)
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
