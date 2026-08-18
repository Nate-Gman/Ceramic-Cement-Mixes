# Ceramic Cement

## Ultra-High-Strength Pour Formulation Model

A standalone, single-file Python/Pygame application that models, evaluates, and visually renders formulations for castable (pourable) cementitious and ceramic-bonded materials targeting **10,000 MPa (10 GPa / 1,450,378 psi)** compressive strength.

Every number is computed live from first principles -- nothing is hard-coded to hit the target. Twenty real, batchable formulations are carried, spanning five binder chemistries and three orders of magnitude in strength, each graded for evidence level and producibility tier.

---

## Quick Start

```bash
# Requirements: Python 3.10+, Pygame 2.x
pip install pygame

# Launch the interactive 3D UI (default)
python CeramicCement.py

# Run the full self-test (21 physics + UI checks)
python CeramicCement.py --selftest

# Console comparison of all 20 mixes
python CeramicCement.py --compare

# Full formulary: every mix with batch sheets, production, hazards
python CeramicCement.py --formulary

# Everything
python CeramicCement.py --all
```

---

## The Answer, Up Front

The 10 GPa target is cleared **unconfined**, with 2.5x margin, by a poured slip:

| Mix | Material | Strength | Margin |
|-----|----------|----------|--------|
| NT-DIAMOND-CAST | Nanotwinned diamond | ~24,934 MPa (3.62 Mpsi) | 2.5x target |
| NT-CBN-CAST | Nanotwinned cBN | ~13,466 MPa (1.95 Mpsi) | 1.3x target |
| NPD-CAST | Nanograin diamond | ~11,709 MPa (1.70 Mpsi) | 1.2x target |

Nanotwinned diamond was measured at Vickers 200 GPa by Huang et al. (Nature 510:250, 2014). Nanotwinned cBN at 108 GPa by Tian et al. (Nature 493:385, 2013). The model reproduces both to within 0.3% of UCS ~ Hv/8, from physics it was not fitted to.

Cement chemistry cannot get there and never will: it tops out near 850-1000 MPa. The gap is not a formulation problem -- it is a mechanism problem.

---

## The 8 UI Tabs

| Tab | Name | What It Shows |
|-----|------|---------------|
| 1 | OVERVIEW | All 20 mixes in a sortable table: MPa, PSI, flow, density, cost, evidence, tier |
| 2 | MIX | Batch sheet, mix proportions, particle packing, rheology, strength chain bars, confinement, verdict |
| 3 | PRODUCTION | Cure schedule, equipment, pot life, placement, QC checks, hazard assessment |
| 4 | GRAIN | Hall-Petch strength vs grain size chart with nanotwin markers and d_crit turnover |
| 5 | MICRO | **3D microstructure model** -- rotatable grains, pores, fibers with cross-section cut |
| 6 | PACKING | **3D particle packing** -- rotatable size-class spheres + Funk-Dinger grading curve |
| 7 | CHEMISTRY | **3D molecule model** -- rotatable atoms and bonds + reaction equation cards |
| 8 | SCIENCE | The seven mechanisms ranked by leverage, model contract, measurement honesty |

### 3D Model Controls

- **Mouse drag** -- rotate the 3D model (MICRO, PACKING, CHEMISTRY tabs)
- **X key** -- toggle cross-section cut to see interior
- **TAB / 1-8** -- switch tabs
- **UP/DOWN** -- select mix
- **Mouse wheel** -- scroll
- **PGUP/PGDN** -- page scroll
- **HOME/END** -- jump to top/bottom
- **ESC** -- quit

---

## The 20 Formulations

### Plant Tier (ordinary concrete/refractory works)

| ID | Name | Family | Unconfined | PSI | Evidence |
|----|------|--------|-----------|-----|----------|
| 1 | OPC-BASELINE | hydraulic | 26 MPa | 4 kpsi | measured |
| 2 | HSC-100 | hydraulic | 81 MPa | 12 kpsi | measured |
| 3 | UHPC-160 | hydraulic | 154 MPa | 22 kpsi | measured |
| 4 | RPC-200 | hydraulic | 192 MPa | 28 kpsi | measured |
| 7 | CBPC-ALUMINA | acid_base | 247 MPa | 36 kpsi | measured |
| 8 | GEO-CORUNDUM | alkali | 117 MPa | 17 kpsi | measured |
| 9 | POLY-SIC | polymer | 196 MPa | 28 kpsi | measured |
| 10 | LCC-ALUMINA-FIRED | ceramic | 2,347 MPa | 340 kpsi | measured |
| 11 | RBSC-CAST | ceramic | 2,781 MPa | 403 kpsi | measured |

### Specialist Tier (autoclave, press, vacuum furnace, SPS)

| ID | Name | Family | Unconfined | PSI | Evidence |
|----|------|--------|-----------|-----|----------|
| 5 | RPC-800 | hydraulic | 617 MPa | 89 kpsi | measured |
| 6 | DSP-SIC | hydraulic | 395 MPa | 57 kpsi | measured |
| 12 | NANO-SIC-CAST | ceramic | 4,451 MPa | 645 kpsi | extrapolated |
| 16 | CC-MAX-POUR | hydraulic | 850 MPa | 123 kpsi | extrapolated |
| 17 | CC-10K-CONFINED | hydraulic | 850 MPa (10,572 confined) | 1.53 Mpsi | extrapolated |

### Frontier Tier (HPHT press at 5+ GPa)

| ID | Name | Family | Unconfined | PSI | Evidence |
|----|------|--------|-----------|-----|----------|
| 13 | NPD-CAST | ceramic | 11,709 MPa | 1.70 Mpsi | extrapolated |
| 14 | NT-CBN-CAST | ceramic | 13,466 MPa | 1.95 Mpsi | extrapolated |
| 15 | NT-DIAMOND-CAST | ceramic | 24,934 MPa | 3.62 Mpsi | extrapolated |
| 18 | HPHT-PCD-CAST | ceramic | 6,084 MPa | 883 kpsi | measured |
| 19 | PCD-JACKETED | ceramic | 6,084 MPa (11,047 confined) | 1.60 Mpsi | extrapolated |
| 20 | NPD-JACKETED | ceramic | 11,709 MPa (27,273 confined) | 3.96 Mpsi | speculative |

---

## Physics Models Used

- **de Larrard Compressible Packing Model (CPM)** -- virtual + actual packing density with loosening/wall effects
- **Funk & Dinger (modified Andreasen) distribution** -- optimal particle size distribution exponent q
- **Powers-Brownyard volumetric hydration** -- capillary + gel porosity bookkeeping
- **Portlandite (CH) mass balance** -- caps how much pozzolan can actually react
- **Waller / Mills relation** -- attainable degree of hydration from water-binder ratio
- **Gel-porosity collapse** -- C-S-H recrystallises to tobermorite/xonotlite above 150 C
- **Ryshkevitch-Duckworth** -- sigma = sigma0 * exp(-b * P) porosity-strength law
- **Hall-Petch grain-boundary strengthening** -- with inverse-Hall-Petch turnover at d_crit
- **Nanotwin strengthening** -- coherent twin boundaries with NO turnover (strongest mechanism)
- **Grain-growth kinetics** -- fired grain size computed from feed size, temperature, dwell, pressure
- **Melt infiltration and pressure-assisted sintering** (SPS / HIP / HPHT)
- **Load-sharing composite law** with ITZ bond efficiency + hard-filler cap
- **Weibull weakest-link size effect** -- specimen-size correction
- **Flatt-Bowen YODEL-form yield stress** + Roussel slump-flow spread
- **Richart / Mohr-Coulomb confinement** -- f_cc = f_co + k(f_l) * f_l

---

## CLI Commands

```bash
python CeramicCement.py                          # interactive UI (default)
python CeramicCement.py --ui                     # force the UI
python CeramicCement.py --console                # force console output
python CeramicCement.py --about                  # the science, in full
python CeramicCement.py --grain                  # Hall-Petch grain-size study
python CeramicCement.py --compare                # side-by-side table of all mixes
python CeramicCement.py --formulary              # EVERY mix: grades, batches, production, hazards
python CeramicCement.py --formulary --tier plant # only what a normal works can build
python CeramicCement.py --mix NT-DIAMOND-CAST    # full report on one mix
python CeramicCement.py --batch NPD-CAST --vol 5 # batch sheet at 5 litres
python CeramicCement.py --optimize               # packing sweep + pourable-strength optimisation
python CeramicCement.py --target 10000           # route to a target strength
python CeramicCement.py --feasibility            # honest physics assessment
python CeramicCement.py --selftest               # 21 sanity + calibration checks
python CeramicCement.py --all                    # everything
```

---

## The Five Ceilings

| Ceiling | Strength | Mechanism |
|---------|----------|-----------|
| 1. Hydrated cement chemistry | ~0.85-1.0 GPa | Gel porosity intrinsic to C-S-H |
| 2. Pressureless fired ceramic | ~2.3 GPa | Sintering cannot close last few % porosity |
| 3. Infiltrated / nanograin ceramic | ~2.8-4.5 GPa | Infiltration beats porosity; nanograins beat phase |
| 4. Nanograin superhard (NPD) | ~11.7 GPa | Hall-Petch on diamond, no metal binder |
| 5. Nanotwinned superhard | ~24.9 GPa | Coherent twins, no inverse-Hall-Petch penalty |
| Any of the above, jacketed | +2.2 to 4.1x lateral | Richart triaxial confinement |

---

## Evidence and Tier Grading

### Evidence Levels
- **measured** -- the material class has published strength data
- **extrapolated** -- physics extrapolation past the measured range
- **speculative** -- past what any test apparatus can verify

### Producibility Tiers
- **plant** -- ordinary concrete or refractory works (9 mixes)
- **specialist** -- autoclave, press, vacuum furnace, or SPS (5 mixes)
- **frontier** -- needs an HPHT press at 5 GPa or more (6 mixes)

A mix can be well-evidenced and unbuildable, or easy to build and poorly evidenced. Both grades are shown side by side.

---

## Self-Test

The self-test verifies 21 checks across the full physics chain with no per-mix fitting:

1. Packing model sanity (monodisperse < beta, bimodal beats monodisperse)
2. Porosity law calibration (w/c 0.50 and 0.25 pastes in literature bands)
3. Portlandite balance limits excess silica fume
4. Autoclave gel collapse at 400 C
5. Hall-Petch: finer grain stronger, inverse below d_crit
6. Nanotwins keep strengthening below d_crit, beat grain refinement
7. Hardness cross-check: NT-DIAMOND and NT-CBN match measured Hv/8
8. Grain growth: HPHT holds grain, pressureless coarsens
9. Diamond optimum near d_crit, passes target unconfined
10. Rheology: 50 Pa yield -> SCC flow, higher yield -> less flow
11. Confinement: Richart k ~ 4.1, 10 GPa needs GPa-class confinement
12. All 20 mixes evaluate without error
13. All 12 literature reference bands matched
14. Target verification (CC-10K-CONFINED, NPD-CAST, NT-DIAMOND-CAST)
15. Infiltration drives porosity below 1%
16. Every mix has complete production instructions (20 x 12 fields)
17. Every mix has substantive hazard assessment
18. Every mix has valid tier and evidence grade
19. Mix IDs unique and contiguous 1..20
20. UI renders at 7 window sizes x 8 tabs = 448 frames, 0 errors
21. UI never overlaps text: 0 collisions in 448 frames

---

## Technical Stack

- **Python 3.10+**
- **Pygame 2.6.1** (SDL 2.28.4) for the interactive UI
- **No external dependencies** beyond Pygame -- all physics is computed in-file
- **Single file**: ~5,965 lines, fully self-contained
- **Headless rendering**: SDL dummy video driver for CI/self-test

---

## File Structure

```
Ceramic Cement/
  CeramicCement.py     # the entire application (model + UI + CLI)
  infornmational.md    # original science notes on the 10 GPa goal
  README.md            # this file
  OVERVIEW.md          # technical architecture and formulation detail
  INFORMATIONAL.md     # product value appraisal and projected earnings
```

---

## License

Proprietary. All rights reserved. This model and its formulations are the intellectual property of the author. See INFORMATIONAL.md for the full value appraisal and licensing terms.
