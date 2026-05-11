# Phase 2 Step 1: Pleiades validation

## Sample yield
- 12 candidates → 4 comparable stars after removing Be (off-grid above
  2.5 M_sun) and A7/F0 (off-grid below 1.4 M_sun).
- HD 23642 (EB, binary-corrected input): age 144 (-92, +117) Myr,
  consistent with Pleiades 125 +/- 8 Myr at <1 sigma.
- HD 23631 (A1V, clean): 294 (-163, +152) Myr, ~1 sigma high.
- HD 23289 (A2V, clean): 316 (-178, +184) Myr, ~1 sigma high.
- HII 1117 (A0V, edge): 273 (-146, +104) Myr, ~1 sigma high.

## Headline finding
RAPID exhibits a systematic ~150-170 Myr OLD bias for clean A0-A2 stars
near the Pleiades-age ZAMS. This is the same sign and approximate
magnitude as the bias predicted by the paper's own Fig. 10a (red/blue
regions near the ZAMS): the synthetic population has no models younger
than the youngest pre-MS hook contained in the grid, so random scatter
and binary effects can only inflate ages, not deflate them.

The Pleiades validation therefore CONFIRMS the paper's theoretical
prediction on a real cluster, while also quantifying that RAPID is not
yet a reliable age estimator for individual young (~100 Myr) A stars.

## Caveats / sample weaknesses
- Sample size of 4 clean A stars is too small for a publication-grade
  calibration. Need to expand.
- Luminosities for cluster A-stars were drawn from a mix of older
  sources (Stauffer+98, TIC v8.2) and should be re-derived uniformly
  from Gaia DR3 parallaxes + PySSED bolometric fluxes for a cleaner
  result.
- HD 23642's good agreement may be partly because its input Teff is
  already binary-corrected. Other Pleiades A-stars may have unrecognised
  companions; the inferred ages assume the catalog values already
  reflect the unresolved binary stage.