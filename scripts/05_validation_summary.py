"""
Three-cluster validation summary: RAPID inferred age vs known cluster age.
Run from repo root:  python scripts\05_validation_summary.py
"""
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks"
FIGS = ROOT / "figures"

CLUSTERS = {
    "alphaper": dict(age=90.0, age_err=10.0, label=r"$\alpha$ Per",
                     offsets=[-0.18, -0.06, 0.06, 0.18]),
    "pleiades": dict(age=125.0, age_err=8.0, label="Pleiades",
                     offsets=[-0.12, 0.0, 0.12]),
    "hyades": dict(age=625.0, age_err=50.0, label="Hyades",
                   offsets=[-0.12, 0.0, 0.12]),
}

ANCHORS = {"HD 23642", "theta2 Tau (HD 28319)"}

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 8,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 7.5,
    "axes.linewidth": 0.8,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
})

fig, ax = plt.subplots(figsize=(6.7, 4.2))

cluster_names = list(CLUSTERS)
x_centres = np.arange(len(cluster_names), dtype=float)

ax.axhspan(250, 400, color="#E6B450", alpha=0.16, zorder=-5, lw=0)
ax.text(-0.45, 388, "prior-attractor band", color="#9A6200",
        fontsize=8, va="top", ha="left")

for x0, cname in zip(x_centres, cluster_names):
    c = CLUSTERS[cname]
    rect = Rectangle((x0 - 0.34, c["age"] - c["age_err"]),
                     0.68, 2 * c["age_err"],
                     facecolor="#5AA469", edgecolor="none",
                     alpha=0.16, zorder=-3)
    ax.add_patch(rect)
    ax.hlines(c["age"], x0 - 0.34, x0 + 0.34,
              color="#3F8E4D", lw=1.0, zorder=-2)

plotted = []
for x0, cname in zip(x_centres, cluster_names):
    c = CLUSTERS[cname]
    res = pd.read_csv(BENCH / f"{cname}_results.csv")
    res = res[res.Neff > 100].copy()
    res = res[(res.edge == False) | (res.name.isin(ANCHORS))]
    res = res.sort_values("age50").reset_index(drop=True)
    offsets = np.array(c["offsets"][:len(res)], dtype=float)

    for i, row in res.iterrows():
        is_anchor = row["name"] in ANCHORS
        x = x0 + offsets[i]
        y = row.age50
        yerr = [[row.age50 - row.age16], [row.age84 - row.age50]]
        if is_anchor:
            color, marker, size = "#C95B2C", "D", 4.8
        else:
            color, marker, size = "#2F6F9F", "o", 4.8

        ax.errorbar(
            x, y, yerr=yerr, fmt=marker, color=color,
            markeredgecolor="white", markeredgewidth=0.55,
            ecolor="0.55", elinewidth=0.8, capsize=2.0,
            ms=size, alpha=0.98, zorder=3,
        )
        plotted.append((row["name"], x, y))

for name, x, y in plotted:
    if name == "HD 23642":
        ax.annotate(
            "HD 23642\n(binary-corrected)",
            xy=(x, y), xytext=(0.38, 92), textcoords="data",
            ha="left", va="center", fontsize=7.5,
            arrowprops=dict(arrowstyle="-", color="0.35", lw=0.7,
                            shrinkA=2, shrinkB=3),
        )
    elif name == "theta2 Tau (HD 28319)":
        ax.annotate(
            r"$\theta^2$ Tau" "\n(turnoff)",
            xy=(x, y), xytext=(1.55, 610), textcoords="data",
            ha="left", va="center", fontsize=7.5,
            arrowprops=dict(arrowstyle="-", color="0.35", lw=0.7,
                            shrinkA=2, shrinkB=3),
        )

ax.set_ylabel("RAPID-style inferred age (Myr)")
ax.set_xlim(-0.55, len(cluster_names) - 0.45)
ax.set_ylim(0, 700)
ax.set_xticks(x_centres)
ax.set_xticklabels([
    f"{CLUSTERS[name]['label']}\n{CLUSTERS[name]['age']:.0f} ± {CLUSTERS[name]['age_err']:.0f} Myr"
    for name in cluster_names
])
ax.set_yticks(np.arange(0, 701, 100))
ax.grid(axis="y", color="0.90", lw=0.6, zorder=-6)

legend_handles = [
    Patch(facecolor="#5AA469", edgecolor="none", alpha=0.22,
          label="independent cluster age"),
    Patch(facecolor="#E6B450", edgecolor="none", alpha=0.22,
          label="250-400 Myr attractor band"),
    Line2D([0], [0], marker="o", color="none", markerfacecolor="#2F6F9F",
           markeredgecolor="white", markeredgewidth=0.55, markersize=5.5,
           label="clean mid-MS A dwarf"),
    Line2D([0], [0], marker="D", color="none", markerfacecolor="#C95B2C",
           markeredgecolor="white", markeredgewidth=0.55, markersize=5.5,
           label="turnoff / binary-corrected case"),
]
ax.legend(handles=legend_handles, loc="lower center", bbox_to_anchor=(0.5, 1.02),
          ncol=2, frameon=False, columnspacing=1.8, handletextpad=0.7)

fig.tight_layout()
out = FIGS / "05_validation_summary.png"
fig.savefig(out, dpi=300, bbox_inches="tight")
fig.savefig(FIGS / "05_validation_summary.pdf", bbox_inches="tight")
print(f"wrote {out}")

print("\nSummary of bias (RAPID - truth):")
for cname in cluster_names:
    c = CLUSTERS[cname]
    res = pd.read_csv(BENCH / f"{cname}_results.csv")
    res = res[res.Neff > 100].copy()
    res = res[(res.edge == False) | (res.name.isin(ANCHORS))]
    res = res.sort_values("age50").reset_index(drop=True)
    print(f"\n  {cname.upper()} (truth = {c['age']:.0f} Myr)")
    for _, r in res.iterrows():
        bias = r.age50 - c["age"]
        flag = " (anchor)" if r["name"] in ANCHORS else " (clean)"
        print(f"    {r['name']:24s}  RAPID={r.age50:5.0f}  "
              f"bias={bias:+5.0f} Myr{flag}")
