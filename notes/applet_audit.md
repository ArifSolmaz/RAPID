# applet.py audit

783 lines, a single `InteractiveHRD` class (lines 18-747) plus a `__main__`
block (lines 757-782). All inference, plotting and event handling live on
that class.

## File structure (cheat sheet)

| Lines | Block |
|-------|-------|
| 1-9 | Imports: numpy, matplotlib (widgets, patheffects), scipy, corner |
| 10-15 | matplotlib rcParams |
| 18-110 | __init__: state, figure, axes, controls, initial draw |
| 111-127 | compute_positions, update_fields |
| 128-174 | update_plot, plot_tracks |
| 175-237 | validate_position, pan_if_needed |
| 238-285 | update_mahalanobis_fill (background paint) |
| 286-303 | compute_weights (distance -> weight) |
| 304-357 | event handlers |
| 358-496 | init_controls (widgets) |
| 497-536 | reset, log toggles, weight-function radio |
| 537-562 | **compute** <- real inference entry point |
| 563-660 | **_draw_hist** <- KDE + median/16/84 for mass and age |
| 661-693 | **plot_corner** <- weighted corner.corner |
| 695-731 | small submit callbacks |
| 732-756 | background_scatter, toggle_binaries |
| 757-782 | __main__: load feathers, instantiate, plt.show() |

## The inference pipeline

1. **Distance** -- compute() line 547:
   dist = sqrt((dTeff/sigma_teff)^2 + (dlum/sigma_lum)^2)  (linear, not d^2).
   Asymmetric errors via np.where(dx>=0, ex_p, ex_m).

2. **Weight** -- compute_weights(dist, max_distance=10) line 286:
   - Exponential: W = exp(-0.5 * D2**2). Variable named D2 but holds
     d here (because compute passes linear distance), so effective
     formula is exp(-d^2/2) -- the Gaussian weight the paper claims.
     Naming bug, math correct.
   - Inverse-square: W = 0.25/d^2 for d > 0.5, capped at W = 1.0 for
     d <= 0.5. Paper footnote 9 says cap at d=0.5 giving W=4 with norm
     1/4. The code appears to implement the normalised form directly, so
     this is a documentation/notation point rather than a science bug.

3. **Truncation**:
   - KDE for mass and age uses all samples with d <= 10 (comment line
     565: "minimise edge effects on the KDE").
   - Corner plot and CSV export use the d <= 3 cut (self.result).
   - The paper's Sec. 3.4 says "all simulated points with d <= 3 when
     calculating stellar properties" -- inconsistent with the code's
     d <= 10 used for the printed median/16/84.

4. **KDE** -- _draw_hist calls scipy.stats.gaussian_kde(data_col,
   weights=weights[mask], bw_method=...). Mass bandwidth is
   user-adjustable; age bandwidth is hardcoded to Scott's rule.

5. **Quantiles**:
   - Single-number mass/age in the main GUI: KDE-CDF root-finding via
     fsolve on integrate_box_1d (lines 591-595).
   - Corner-plot titles: corner.quantile(..., weights=weights.values)
     on raw weighted samples (line 686). This is the cleanest path.

## Data columns used

From full.feather (binaries on):
- inputs: bin_teff, bin_lum (L in linear L_sun, not log).
- outputs / posteriors: m, z, Myr, v_rot, sini, P_rot, R_p, R_eq, rho,
  new_Dnu, p1, p5.
- diagnostics: binary, q_bin.

From no_binaries.feather:
- toggle_binaries (lines 743-752) swaps to inc_teff, inc_lum because
  bin_* is absent in this sample. Consistent with paper Fig. 1.

## Things that look fragile or wrong

1. update_mahalanobis_fill (background-paint) builds dist = d^2 then
   calls compute_weights, which squares again -> background uses
   exp(-d^4/2), not exp(-d^2/2). Cosmetic only; quoted posteriors via
   compute() are correct (its dist is linear).

2. compute() ignores metallicity, vsini, logg, or any other measured
   prior. Even if a user knows [Fe/H]_obs, RAPID can't condition on it.
   The w_Zprior column added in Phase 1 is a clean place to attach an
   optional [Fe/H]_obs likelihood later.

3. KDE uses d <= 10 while paper says d <= 3. Either paper or code wrong.

4. No N_eff diagnostic. No edge-of-grid warning.

5. Mass-KDE bandwidth exposed; age-KDE bandwidth is not.

6. default_state = {"Teff": 8980, "Lum": 15.0, ...} are KELT-20's
   startup values from Sec. 3.6.

## Functions to lift into rapid_core.py for Phase 4

- compute -- refactor to return weighted DataFrame; drop plot side-effects.
- compute_weights -- replace with a proper Gaussian likelihood.
- The KDE/quantile block inside _draw_hist -- make KDE display-only and
  use corner.quantile (the corner-plot path) as the canonical estimator.

## Open questions for Simon

- Can the inverse-square footnote explicitly state that the code uses the
  normalised 0.25/d^2 form capped at W=1.0?
- Was the d <= 10 window for mass/age KDEs deliberate, or is the
  paper's d <= 3 the intended cut?
- Why does update_mahalanobis_fill paint with exp(-d^4/2) while the
  inference uses exp(-d^2/2)?
