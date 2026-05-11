"""
Cluster validation for RAPID. Run from repo root:
    python scripts\03_cluster_validation.py pleiades
    python scripts\03_cluster_validation.py hyades
"""
import argparse, numpy as np, pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

CLUSTERS = {
    "pleiades": dict(age=125.0, age_err= 8.0, csv="pleiades_seed.csv",
                     ref="Stauffer+98 (LDB)"),
    "hyades":   dict(age=625.0, age_err=50.0, csv="hyades_seed.csv",
                     ref="Perryman+98"),
}

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIGS = ROOT / "figures"
BENCH = ROOT / "benchmarks"

ap = argparse.ArgumentParser()
ap.add_argument("cluster", choices=list(CLUSTERS.keys()))
args = ap.parse_args()
C = CLUSTERS[args.cluster]

print(f"loading population...")
df = pd.read_feather(DATA / "full_zcorrected.feather")
teff_mod = df["bin_teff"].values
logl_mod = np.log10(df["bin_lum"].values)
age      = df["Myr"].values
mass     = df["m"].values
w_z      = df["w_Zprior"].values

def split_normal_logpdf(x, mu, sp, sm):
    sig = np.where(x >= mu, sp, sm)
    return -0.5 * ((x - mu) / sig) ** 2

def wquantile(v, w, q):
    idx = np.argsort(v); v, w = v[idx], w[idx]
    return np.interp(q, np.cumsum(w), v)

def infer(teff_obs, teff_err, lum_obs, lum_err):
    logl_obs  = np.log10(lum_obs)
    logl_errp = np.log10(lum_obs + lum_err) - logl_obs
    logl_errm = logl_obs - np.log10(max(lum_obs - lum_err, 1e-6))
    logw  = split_normal_logpdf(teff_mod, teff_obs, teff_err, teff_err)
    logw += split_normal_logpdf(logl_mod, logl_obs, logl_errp, logl_errm)
    w = np.exp(logw - logw.max()) * w_z
    if w.sum() == 0:
        return None
    w /= w.sum()
    return w

bench = pd.read_csv(BENCH / C["csv"])
results = []
print(f"\n{args.cluster.upper()}  (reference age {C['age']:.0f} +/- {C['age_err']:.0f} Myr, {C['ref']})\n")
for _, row in bench.iterrows():
    w = infer(row.teff_K, row.teff_err_K, row.lum_Lsun, row.lum_err_Lsun)
    if w is None:
        print(f"  {row['name']:20s}  no posterior (off-grid)")
        continue
    a16, a50, a84 = [wquantile(age, w, q) for q in (0.16, 0.50, 0.84)]
    m16, m50, m84 = [wquantile(mass, w, q) for q in (0.16, 0.50, 0.84)]
    Neff = 1.0 / np.sum(w**2)
    top = np.argsort(w)[-200:]
    edge = (mass[top].max() > 2.48) or (mass[top].min() < 1.42)
    print(f"  {row['name']:20s}  age = {a50:6.0f} (-{a50-a16:3.0f},+{a84-a50:3.0f}) Myr   "
          f"M = {m50:.2f} M_sun   N_eff = {Neff:7.0f}   edge={edge}")
    results.append(dict(name=row['name'], age16=a16, age50=a50, age84=a84,
                        m16=m16, m50=m50, m84=m84, Neff=Neff, edge=edge,
                        teff=row.teff_K, lum=row.lum_Lsun))

res = pd.DataFrame(results)
res.to_csv(BENCH / f"{args.cluster}_results.csv", index=False)

fig, ax = plt.subplots(figsize=(7, 5))
x = np.arange(len(res))
err_lo = res.age50 - res.age16
err_hi = res.age84 - res.age50
colors = ["crimson" if e else "steelblue" for e in res.edge]
ax.errorbar(x, res.age50, yerr=[err_lo, err_hi], fmt="o", color="black",
            ecolor="gray", capsize=3, zorder=2)
for xi, ai, c in zip(x, res.age50, colors):
    ax.scatter(xi, ai, c=c, s=60, zorder=3, edgecolor="k", linewidth=0.5)
ax.axhspan(C["age"] - C["age_err"], C["age"] + C["age_err"],
           color="green", alpha=0.18, label=f'{args.cluster.capitalize()} age ({C["ref"]})')
ax.axhline(C["age"], color="green", lw=1)
ax.set_xticks(x); ax.set_xticklabels(res.name, rotation=45, ha="right")
ax.set_ylabel("RAPID age (Myr)")
ax.set_title(f'{args.cluster.capitalize()} A-star ages -- RAPID vs cluster')
ax.legend()
fig.tight_layout()
out = FIGS / f"04_{args.cluster}_validation.png"
fig.savefig(out, dpi=150)
print(f"wrote {out}")
