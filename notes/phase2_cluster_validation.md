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
- Sample size is small (two clean A-dwarfs plus two edge/comparison
  cases), so this is a diagnostic validation, not yet a publication-grade
  calibration. Need to expand.
- Luminosities for cluster A-stars were drawn from a mix of older
  sources (Stauffer+98, TIC v8.2) and should be re-derived uniformly
  from Gaia DR3 parallaxes + PySSED bolometric fluxes for a cleaner
  result.
- HD 23642's good agreement may be partly because its input Teff is
  already binary-corrected. Other Pleiades A-stars may have unrecognised
  companions; the inferred ages assume the catalog values already
  reflect the unresolved binary stage.
## Phase 2 Step 2: Hyades

### Sample yield
- 6 candidates -> 2 clean A-dwarfs (60 Tau, HD 28910), 1 near-turnoff
  star (theta^2 Tau, edge=True at upper bound), 3 low-mass edge.

### Headline finding
- 60 Tau (A3m, 1.80 M_sun): age 334 (-209, +243) Myr, ~290 Myr too young
- HD 28910 (A4V, 1.70 M_sun): age 225 (-152, +228) Myr, ~400 Myr too young
- theta^2 Tau (near MS turnoff): 563 (-46, +57) Myr, matches truth

## Phase 2 Step 3: Alpha Per

### Headline finding
- Four clean A-dwarfs in alpha Per (adopting 90 +/- 10 Myr from the
  Stauffer+99 LDB age) return RAPID-style median ages of 348, 379, 386,
  and 397 Myr.
- This independently repeats the young-cluster old-bias seen in the
  Pleiades, with a larger offset because alpha Per is younger.

### Combined three-cluster picture
Across all three clusters, the clean A-dwarfs collapse toward a
~250-400 Myr value regardless of true age:
- Alpha Per A-dwarfs (truth ~90 Myr): inferred ~350-400 Myr
- Pleiades A-dwarfs (truth 125 Myr): inferred ~300 Myr (+175 Myr bias)
- Hyades A-dwarfs   (truth 625 Myr): inferred ~280 Myr (-345 Myr bias)
The bias flips sign because the inference is collapsing toward the
prior-weighted mean A-star MS age, not respecting the true age.

Numerically, the eight clean A-dwarfs span 225-397 Myr in inferred age
(a factor of 1.8), with seven of eight lying in the 250-400 Myr band.

The two cases that recover the cluster age within uncertainties are:
- HD 23642 (Pleiades EB, binary-corrected input): tight grid of bin_*
  models maps Teff/L to the right age
- theta^2 Tau (Hyades near-turnoff): rapid evolution makes HR-diagram
  position a sharp age indicator

### Implication for the paper
The manuscript's claim of "~100 Myr intrinsic scatter" for A-star
isochrone ages dramatically UNDERSTATES the actual single-star
inference error. For mid-MS A-dwarfs away from the turnoff, the
(Teff, log L) likelihood is too broad to distinguish ages between
~100 Myr and ~1 Gyr, and the posterior collapses to the prior mean.

A user should therefore not infer individual ages for A-dwarfs from
RAPID without additional priors (vsini, [Fe/H], log g, asteroseismic
Dnu). The paper's RAPID examples (HD 250208, HD 56414, KELT-20)
should be re-examined in this light: are their RAPID ages real, or
are they all sitting near 200-300 Myr because that's where the prior
lives?
