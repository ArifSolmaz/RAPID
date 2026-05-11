"""
Phase 1: metallicity-prior importance reweighting.
Run from the repo root:  python scripts\01_zprior_demo.py
"""
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from scipy.special import erfc

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIGS = ROOT / "figures"
FIGS.mkdir(exist_ok=True)

Z_SUN = 0.0142
MU_FEH = 0.0
SIG_FEH = 0.15

print("loading full.feather ...")
df_full = pd.read_feather(DATA / "full.feather")
print("  shape:", df_full.shape)
print("  cols :", df_full.columns.tolist())

# ---- 1. visualise the as-implemented [Fe/H] distribution
feh = np.log10(df_full["z"].values / Z_SUN)
fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(feh, bins=80, density=True, alpha=0.6,
        label="RAPID population (implemented)")
xx = np.linspace(-1.2, 0.5, 400)
gauss = np.exp(-((xx - MU_FEH) / SIG_FEH) ** 2 / 2) / (SIG_FEH * np.sqrt(2 * np.pi))
ax.plot(xx, gauss, "k--", label="intended N(0, 0.15)")
ax.set_xlabel("[Fe/H]"); ax.set_ylabel("density"); ax.legend()
fig.tight_layout()
fig.savefig(FIGS / "01_feh_implemented.png", dpi=150)
print("wrote", FIGS / "01_feh_implemented.png")

# ---- 2. compute the importance correction
def zprior_weight(z_values, mu_feh=0.0, sig_feh=0.15, z_sun=Z_SUN, cap=20.0):
    feh = np.log10(np.asarray(z_values) / z_sun)
    n = np.abs(feh - mu_feh) / sig_feh
    num = np.exp(-0.5 * n ** 2)
    den = np.clip(erfc(n / np.sqrt(2)), 1e-300, None)
    return np.minimum(num / den, cap)

df_full["w_Zprior"] = zprior_weight(df_full["z"].values)
print("w_Zprior stats:")
print(df_full["w_Zprior"].describe())

# ---- 3. verify the corrected histogram is Gaussian
fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(feh, bins=80, density=True, alpha=0.5, label="implemented (unweighted)")
ax.hist(feh, bins=80, density=True, alpha=0.5,
        weights=df_full["w_Zprior"], label="reweighted")
ax.plot(xx, gauss, "k--", label="intended N(0, 0.15)")
ax.set_xlabel("[Fe/H]"); ax.set_ylabel("density"); ax.legend()
fig.tight_layout()
fig.savefig(FIGS / "02_feh_corrected.png", dpi=150)
print("wrote", FIGS / "02_feh_corrected.png")

# ---- 4. save corrected dataset
out = DATA / "full_zcorrected.feather"
df_full.to_feather(out)
print(f"wrote {out}  ({out.stat().st_size / 1e6:.1f} MB)")

# ---- repeat for no_binaries
print("\nloading no_binaries.feather ...")
df_no = pd.read_feather(DATA / "no_binaries.feather")
df_no["w_Zprior"] = zprior_weight(df_no["z"].values)
out2 = DATA / "no_binaries_zcorrected.feather"
df_no.to_feather(out2)
print(f"wrote {out2}  ({out2.stat().st_size / 1e6:.1f} MB)")

print("\nDone. Open the two PNGs in figures/ and confirm the reweighted "
      "histogram lies on top of the dashed Gaussian.")