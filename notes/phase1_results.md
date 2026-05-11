# Phase 1: metallicity-prior importance reweighting

## What was wrong

- Manuscript Sec. 2.4.2 claims a Gaussian [Fe/H] prior with sigma = 0.15 dex.
- Implemented acceptance probability is erfc(n/sqrt(2)) per model.
- At 1 sigma: 31.7% accepted (Gaussian: 60.7%).
  At 2 sigma: 4.6% accepted (Gaussian: 13.5%).

## Fix without regenerating the population

- Importance weight per sample: w_Zprior = exp(-n^2/2) / erfc(n/sqrt(2)),
  capped at 20 for numerical safety.
- Added as a new column to both samples; saved as
  data/full_zcorrected.feather and data/no_binaries_zcorrected.feather.

## What the reweighting recovers

- [Fe/H] histogram peak: implemented ~10, reweighted ~6.6,
  intended Gaussian ~2.66.
- Reweighting closes about half the gap. The rest is unrecoverable because
  the population contains essentially zero surviving samples at
  |[Fe/H]| > 0.3. A full fix requires regenerating with proper Gaussian
  rejection over the Gautam tracks.

## Effect on single-star inference (KELT-20)

- Teff = 8980 K, log L = 1.27 (Talens+18, with 2% Teff floor)
- Age (no Z correction):   210 Myr (-132, +161), N_eff = 18,216
- Age (with Z correction): 213 Myr (-135, +178), N_eff = 17,011
- Shift in median: +3 Myr. Tails very slightly broader on the +1 sigma
  side. Posteriors visually nearly identical. N_eff drops only 7%,
  confirming the importance weights are well-conditioned.

## Interpretation

- The metallicity-prior bug has a large effect on the population-level
  [Fe/H] distribution, but only a small effect on individual-star
  posteriors, because the (Teff, log L) likelihood dominates and
  constrains Z implicitly through the evolutionary tracks regardless of
  the prior.
- Recommendation for the revision: fix the prior (or document the
  implemented one accurately) so the Fig. 10/11 population-level bias
  maps are sound, but note that single-star ages from RAPID are
  insensitive to this detail.
