"""
Two-cluster validation summary: RAPID inferred age vs known cluster age.
Run from repo root:  python scripts\05_validation_summary.py
"""
import numpy as np, pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks"
FIGS  = ROOT / "figures"

CLUSTERS = {
    "pleiades": dict(age=125.0, age_err= 8.0, label="Pleiades",
                     jitter_halfwidth=35.0),
    "hyades":   dict(age=625.0, age_err=50.0, label="Hyades",
                     jitter_halfwidth=55.0),
}

fig, ax = plt.subplots(figsize=(9, 6.5))

# cluster age bands (vertical)
for cname, c in CLUSTERS.items():
    ax.axvspan(c["age"] - c["age_err"], c["age"] + c["age_err"],
               color="green", alpha=0.10, zorder=-2)
    ax.axvline(c["age"], color="green", lw=0.8, alpha=0.6, zorder=-1)
    ax.text(c["age"], 1040, c["label"], ha="center", va="bottom",
            color="darkgreen", fontsize=10, fontweight="bold")

# attractor band (horizontal)
ax.axhspan(250, 320, color="gold", alpha=0.18, zorder=-1)
ax.text(950, 285, "~250-300 Myr attractor", color="darkgoldenrod",
        fontsize=9, va="center", ha="right")

# loop over clusters and plot
all_handles = {"clean": None, "edge": None}
for cname, c in CLUSTERS.items():
    res = pd.read_csv(BENCH / f"{cname}_results.csv")
    res = res[res.Neff > 100].sort_values("age50").reset_index(drop=True)
    n = len(res)
    # spread x positions uniformly within a small window
    offsets = np.linspace(-c["jitter_halfwidth"], c["jitter_halfwidth"], n) if n > 1 else np.array([0.0])
    x  = c["age"] + offsets
    y  = res.age50.values
    ylo = (res.age50 - res.age16).values
    yhi = (res.age84 - res.age50).values
    edge = res.edge.values.astype(bool)

    for i in range(n):
        col = "crimson" if edge[i] else "steelblue"
        mk  = "s" if edge[i] else "o"
        h = ax.errorbar(x[i], y[i], yerr=[[ylo[i]], [yhi[i]]],
                        fmt=mk, color=col, ecolor="gray", capsize=2,
                        ms=7, elinewidth=0.9, alpha=0.95,
                        label=("grid-edge (edge=True)" if edge[i] else "clean A-dwarf (edge=False)")
                        if all_handles[("edge" if edge[i] else "clean")] is None else None)
        if all_handles["edge" if edge[i] else "clean"] is None:
            all_handles["edge" if edge[i] else "clean"] = h
        # label to the right, small font
        ax.annotate(res.name.iloc[i], (x[i], y[i]),
                    xytext=(7, 0), textcoords="offset points",
                    fontsize=7.5, color="black", alpha=0.85, va="center")

# 1:1 line
lim = 1100
xx = np.linspace(0, lim, 200)
ax.plot(xx, xx, "k--", lw=1, alpha=0.7, label="1:1 (perfect recovery)")

ax.set_xlabel("Independent cluster age (Myr)")
ax.set_ylabel("RAPID inferred age (Myr)")
ax.set_title("RAPID validation against open clusters")
ax.set_xlim(0, lim); ax.set_ylim(0, lim)
# dedupe legend entries
handles, labels = ax.get_legend_handles_labels()
seen = set(); h_uniq=[]; l_uniq=[]
for h, l in zip(handles, labels):
    if l not in seen:
        seen.add(l); h_uniq.append(h); l_uniq.append(l)
ax.legend(h_uniq, l_uniq, loc="upper right", fontsize=9)
fig.tight_layout()
out = FIGS / "05_validation_summary.png"
fig.savefig(out, dpi=160)
print(f"wrote {out}")

print("\nSummary of bias (RAPID - truth):")
for cname, c in CLUSTERS.items():
    res = pd.read_csv(BENCH / f"{cname}_results.csv")
    res = res[res.Neff > 100].sort_values("age50").reset_index(drop=True)
    print(f"\n  {cname.upper()} (truth = {c['age']:.0f} Myr)")
    for _, r in res.iterrows():
        bias = r.age50 - c["age"]
        flag = " (edge)" if r.edge else " (clean)"
        print(f"    {r['name']:24s}  RAPID={r.age50:5.0f}  bias={bias:+5.0f} Myr{flag}")
