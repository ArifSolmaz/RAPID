"""
Phase 1 (cont'd): KELT-20 age posterior with and without the metallicity
importance correction. Run from repo root:
    python scripts\02_kelt20_zcorr.py
"""
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIGS = ROOT / "figures"

# --- KELT-20 observables.
# Talens et al. 2018: Teff = 8980 +/- 90 K, after the paper's 2% Teff floor.
# Luminosity: derive from R = 1.78 R_sun, Teff = 8980 K (Talens+18 vals).
# If applet.py has explicit defaults, override these with those numbers.
TEFF, TEFF_SIGP, TEFF_SIGM = 8980.0, 180.0, 180.0      # 2% floor
R_SUN, T_SUN, L_SUN = 6.957e10, 5772.0, 3.828e33       # cgs
R_KELT = 1.78          # R_sun, Talens+18
L = (R_KELT)**2 * (TEFF / T_SUN)**4                    # in L_sun
LOGL = np.log10(L)
# crude +/- 10% on L for the demo; tighten later
LOGL_SIGP = np.log10(L * 1.10) - LOGL
LOGL_SIGM = LOGL - np.log10(L * 0.90)
print(f"KELT-20: Teff = {TEFF} K, log L = {LOGL:.3f}")

# --- load the corrected population
df = pd.read_feather(DATA / "full_zcorrected.feather")
print("loaded:", df.shape, "cols:", df.columns.tolist())

# !!! TODO from your applet.py audit: which columns hold the 'binary'-stage
# Teff and log L?  Replace the next two lines with the right names.
TEFF_COL = "bin_teff"
LUM_COL  = "bin_lum"   # linear L in L_sun, not log

teff_mod = df[TEFF_COL].values
logl_mod = np.log10(df[LUM_COL].values)
age      = df["Myr"].values

def split_normal_logpdf(x, mu, sp, sm):
    sig = np.where(x >= mu, sp, sm)
    return -0.5 * ((x - mu) / sig) ** 2

logw  = split_normal_logpdf(teff_mod, TEFF, TEFF_SIGP, TEFF_SIGM)
logw += split_normal_logpdf(logl_mod, LOGL, LOGL_SIGP, LOGL_SIGM)
w_off = np.exp(logw - logw.max())
w_off /= w_off.sum()
w_on  = w_off * df["w_Zprior"].values
w_on /= w_on.sum()

def wquantile(v, w, q):
    idx = np.argsort(v); v, w = v[idx], w[idx]
    return np.interp(q, np.cumsum(w), v)

for name, w in [("no Z correction", w_off), ("with Z correction", w_on)]:
    med = wquantile(age, w, 0.5)
    lo  = wquantile(age, w, 0.16)
    hi  = wquantile(age, w, 0.84)
    Neff = 1.0 / np.sum(w**2)
    print(f"  {name:20s}  age = {med:6.0f}  -{med-lo:5.0f} +{hi-med:5.0f} Myr   N_eff = {Neff:7.0f}")

bins = np.linspace(0, 1500, 80)
fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(age, bins=bins, weights=w_off, density=True, histtype="step", lw=2,
        label="no Z correction")
ax.hist(age, bins=bins, weights=w_on,  density=True, histtype="step", lw=2,
        label="with Z correction")
ax.set_xlabel("Age (Myr)"); ax.set_ylabel("posterior density")
ax.set_title("KELT-20 age posterior — effect of metallicity-prior fix")
ax.legend()
fig.tight_layout()
fig.savefig(FIGS / "03_kelt20_zcorr.png", dpi=150)
print("wrote", FIGS / "03_kelt20_zcorr.png")