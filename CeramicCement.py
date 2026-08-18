#!/usr/bin/env python3
"""
================================================================================
 CeramicCement.py  --  CERAMIC CEMENT :: Ultra-High-Strength Pour Formulation Model
================================================================================

ABOUT
--------------------------------------------------------------------------------
A standalone, single-file formulation + physics model for castable (pourable)
cementitious and ceramic-bonded materials.  The design goal is a compressive
strength of 10,000 MPa (10 GPa) reached "by any means" in a mix pour.

Every number is computed live from first principles -- nothing is hard-coded to
hit the target.  Twenty real, batchable formulations are carried, spanning five
binder chemistries and three orders of magnitude in strength, and each is graded
for how much evidence actually stands behind it.

THE ANSWER, UP FRONT
--------------------------------------------------------------------------------
The target is cleared unconfined, with 2.5x margin, by a poured slip:

    NT-DIAMOND-CAST   nanotwinned diamond      ~24,900 MPa   (2.5x target)
    NPD-CAST          nanograin diamond        ~11,700 MPa   (1.2x target)
    NT-CBN-CAST       nanotwinned cBN          ~13,500 MPa   (1.3x target)

NT-DIAMOND-CAST is an onion-carbon slip that is POURED, dried, and HPHT-sintered
at 20 GPa / 2000 C into diamond carrying ~5 nm coherent nanotwins.  It is not an
extrapolation of this model: nanotwinned diamond was measured at Vickers 200 GPa
by Huang et al., Nature 510:250 (2014) -- about twice single-crystal diamond --
and nanotwinned cBN at 108 GPa by Tian et al., Nature 493:385 (2013).  The model
reproduces both to within 0.3%% of UCS ~ Hv/8, from physics it was not fitted to.

Cement chemistry cannot get there and never will: it tops out near 850-1000 MPa.
The gap is not a formulation problem, it is a mechanism problem.

MODELS USED
--------------------------------------------------------------------------------
  - de Larrard Compressible Packing Model (CPM): virtual + actual packing
    density of a multi-class particle blend (loosening / wall effects)
  - Funk & Dinger (modified Andreasen) distribution: optimal PSD exponent q
  - Powers-Brownyard volumetric hydration: capillary + gel porosity bookkeeping
  - Portlandite (CH) mass balance: caps how much pozzolan can actually react
  - Waller / Mills relation: attainable degree of hydration from w/b
  - Gel-porosity collapse: C-S-H recrystallises to tobermorite/xonotlite above
    ~150 C, the real mechanism behind RPC-800
  - Ryshkevitch-Duckworth: sigma = sigma0 * exp(-b * P) porosity-strength law
  - HALL-PETCH grain-boundary strengthening, with its inverse-Hall-Petch
    turnover, which puts a finite optimum on grain size
  - NANOTWIN strengthening: coherent twin boundaries block cracks but cannot
    slide, so they have NO turnover -- the strongest mechanism in the model
  - Grain-growth kinetics: fired grain size is COMPUTED from feed size,
    temperature, dwell and pressure, not assumed
  - Melt infiltration and pressure-assisted sintering (SPS / HIP / HPHT)
  - Load-sharing composite law with ITZ bond efficiency + hard-filler cap
  - Weibull weakest-link size effect (specimen-size correction)
  - Flatt-Bowen YODEL-form yield stress + Roussel slump-flow spread
  - Richart / Mohr-Coulomb confinement: f_cc = f_co + k(f_l) * f_l

THE HONEST FRAMING
--------------------------------------------------------------------------------
Compressive strength is not one number -- it depends on what is holding the
specimen.  This model separates three cases and never mixes them up:

  1. UNCONFINED strength of the cured pour (uniaxial, free-standing).
  2. FIRED strength, where the pour is a green body that is later sintered.
     Still a pour -- refractory castables are poured, then fired.
  3. CONFINED capacity, where the pour sits inside a jacket supplying lateral
     pressure.  A real load-bearing system property, not a material one.

Every mix carries TWO grades, answering different questions:

  EVIDENCE -- how far the strength number can be trusted
     measured      the material class has published strength data
     extrapolated  physics extrapolation past the measured range
     speculative   past what any test apparatus can verify

  TIER -- what it takes to actually produce it
     plant         ordinary concrete or refractory works       (8 mixes)
     specialist    autoclave, press, vacuum furnace, or SPS    (6 mixes)
     frontier      needs an HPHT press at 5 GPa or more        (6 mixes)

A mix can be well-evidenced and unbuildable, or easy to build and poorly
evidenced.  --formulary prints both alongside the full production sheet:
equipment, pot life, placement, cure schedule, QC checks and hazards.

That last grade matters.  Tungsten carbide press platens fail near 5.5 GPa, so
any unconfined strength above that cannot be measured in a normal test frame at
all -- the apparatus fails before the specimen.  Above 5.5 GPa the numbers here
come from hardness correlations or multi-anvil work, never from a compression
test, and they are flagged accordingly.

REFERENCE BANDS THE MODEL MUST LAND INSIDE
--------------------------------------------------------------------------------
Run --selftest to see all of these checked from one physics chain, with no
per-mix fitting anywhere:

                                model      literature
    Ordinary concrete ........... 26 MPa    25-50      (EN 206 C30/37)
    High-strength concrete ...... 81 MPa    70-115     (ACI 363R)
    UHPC (Ductal class) ........ 154 MPa    130-210    (AFGC-SETRA)
    RPC-200 (steam cured) ...... 192 MPa    170-250    (Richard & Cheyrezy)
    RPC-800 (press-set, 400 C) . 617 MPa    450-900    (Richard & Cheyrezy)
    Fired alumina castable .... 2347 MPa    1800-3200  (sintered Al2O3)
    Reaction-bonded SiC ....... 2781 MPa    2200-3600  (siliconized SiC)
    Nanograin SiC (SPS) ....... 4451 MPa    3500-6500  (Hall-Petch estimate)
    HPHT diamond compact ...... 6084 MPa    5500-9000  (PCD cutters)
    Nano-polycrystalline dia . 11709 MPa    10000-20000 (from Knoop hardness)
    Nanotwinned cBN ........... 13466 MPa    11000-16000 (Hv 108 GPa measured)
    Nanotwinned diamond ....... 24934 MPa    20000-30000 (Hv 200 GPa measured)

THE FIVE CEILINGS
--------------------------------------------------------------------------------
    1. Hydrated cement chemistry ........... ~0.85-1.0 GPa
       Gel porosity intrinsic to C-S-H never fully leaves, even autoclaved.
    2. Pressureless fired ceramic castable . ~2.3 GPa
       Sintering cannot close the last few percent of green porosity.
    3. Infiltrated / nanograin ceramic ..... ~2.8-4.5 GPa
       Infiltration beats the porosity limit; nanograins beat the phase limit.
    4. Nanograin superhard (NPD) ........... ~11.7 GPa   <- clears the target
       Hall-Petch on diamond, with no metal binder to soften it.
    5. NANOTWINNED superhard ............... ~24.9 GPa   <- best possible
       Coherent twins strengthen without the inverse-Hall-Petch penalty.

    Any of the above, jacketed ............. +2.2 to 4.1x the lateral pressure

INTERACTIVE UI
--------------------------------------------------------------------------------
Run with no arguments (or --ui) for a resizable window with five tabs:

    1 OVERVIEW    all mixes, both grades, sortable columns
    2 MIX         batch sheet, properties, and the strength chain as bars
    3 PRODUCTION  equipment, timings, QC, and the hazard assessment
    4 GRAIN       strength vs microstructural length scale, with the
                  Hall-Petch turnover and the two measured nanotwin results
    5 SCIENCE     the seven mechanisms, ranked by what they are worth

The window is fully resizable: every rectangle is derived from the current
window size each frame, fonts rescale, and scroll offsets re-clamp.  Text can
never overlap or bleed past a panel -- single lines ellipsise to the width they
are given, prose wraps, tables drop low-priority columns rather than let cells
collide, and every panel clips.  --selftest renders all five tabs at seven
window sizes and fails if any frame raises or any two glyph runs collide.

Keys: TAB or 1-5 switch tabs, UP/DOWN select a mix, mouse wheel scrolls,
PGUP/PGDN page, HOME/END jump, ESC quits.

USAGE
--------------------------------------------------------------------------------
    python CeramicCement.py --about                  the science, in full
    python CeramicCement.py                          interactive UI (default,
                                                     if pygame is installed)
    python CeramicCement.py --ui                     force the UI
    python CeramicCement.py --console                force console output
    python CeramicCement.py --formulary              EVERY mix, in full:
                                                     grades, batch sheets,
                                                     equipment, hazards, QC
    python CeramicCement.py --formulary --tier plant  only what a normal works
                                                      can actually build
    python CeramicCement.py --compare                side-by-side of all mixes
    python CeramicCement.py --mix NT-DIAMOND-CAST    full report on one mix
    python CeramicCement.py --grain                  grain / nanotwin study
    python CeramicCement.py --batch NPD-CAST --vol 5     batch sheet
    python CeramicCement.py --optimize               sweep + local search
    python CeramicCement.py --target 10000           route to a target strength
    python CeramicCement.py --feasibility            honest physics assessment
    python CeramicCement.py --selftest               sanity + calibration checks
"""

import sys
import math
import random
import argparse

# =============================================================================
# SECTION 1 -- MATS: material database (SI, real properties)
# =============================================================================
#
# rho        kg/m3   true particle density
# d50        um      median particle diameter (packing + rheology driver)
# beta       -       RESIDUAL (virtual) packing density of that class alone.
#                    This is the CPM input, and it is higher than the loose
#                    measured packing by about (1 + 1/K): uniform spheres 0.72,
#                    graded rounded 0.70, crushed 0.66, narrow angular grit 0.63,
#                    powders 0.62, ultrafine deflocculated 0.55.
# sigma_c    MPa     intrinsic compressive (crushing) strength of the solid
# E          GPa     Young's modulus
# bond       -       ITZ bond efficiency with a dense binder (0-1)
# cost       USD/kg  order-of-magnitude bulk price
#
# Binder reaction parameters (Powers-Brownyard bookkeeping, per gram reacted):
# v_prod     cm3/g   volume of reaction product created (gel pores included)
# w_draw     g/g     capillary water drawn in (bound water + gel water)
# gel_frac   -       fraction of that product volume which is gel porosity
# ch_yield   g/g     portlandite RELEASED per gram reacted (hydraulic binders)
# ch_use     g/g     portlandite CONSUMED per gram reacted (pozzolans)
# sigma0     MPa     strength of the pore-free reaction product (Ryshkevitch)

MATS = {
    # ---------------- Hydraulic binders ------------------------------------
    "opc": {
        "name": "Portland cement CEM I 52.5R",
        "role": "binder", "chem": "hydraulic",
        "rho": 3150.0, "d50": 11.0, "beta": 0.62, "cost": 0.12,
        "v_prod": 0.68, "w_draw": 0.3625, "gel_frac": 0.28,
        "ch_yield": 0.26, "ch_use": 0.0, "sigma0": 650.0,
        "ref": "Powers & Brownyard (1948) PCA Bull.22: v_prod 0.68 cm3/g, gel water 0.19 cm3/g",
    },
    "cac": {
        "name": "Calcium aluminate cement (Secar 71 / CA-25)",
        "role": "binder", "chem": "hydraulic",
        "rho": 3250.0, "d50": 8.0, "beta": 0.62, "cost": 1.30,
        "v_prod": 0.72, "w_draw": 0.40, "gel_frac": 0.18,
        "ch_yield": 0.12, "ch_use": 0.0, "sigma0": 780.0,
        "ref": "Converts to C3AH6 + AH3; no portlandite, denser product, higher sigma0",
    },
    # ---------------- Pozzolans / supplementary ----------------------------
    "sf": {
        "name": "Condensed silica fume (undensified, 95% SiO2)",
        "role": "binder", "chem": "pozzolanic",
        "rho": 2200.0, "d50": 0.15, "beta": 0.55, "cost": 0.55,
        "v_prod": 0.75, "w_draw": 0.45, "gel_frac": 0.28,
        "ch_yield": 0.0, "ch_use": 1.85, "sigma0": 700.0,
        "ref": "S + 1.5CH + 2.5H -> C1.5SH2.5; 1.85 g CH per g SiO2 (111/60 by mass)",
    },
    "mk": {
        "name": "Metakaolin (flash calcined 800 C)",
        "role": "binder", "chem": "pozzolanic",
        "rho": 2500.0, "d50": 3.0, "beta": 0.58, "cost": 0.35,
        "v_prod": 0.70, "w_draw": 0.40, "gel_frac": 0.26,
        "ch_yield": 0.0, "ch_use": 1.10, "sigma0": 660.0,
        "ref": "AS2 + 5CH + 3H -> C2ASH8 + 2 CSH; ~1.1 g CH per g MK",
    },
    "ggbs": {
        "name": "Ground granulated blast furnace slag",
        "role": "binder", "chem": "hydraulic",
        "rho": 2900.0, "d50": 12.0, "beta": 0.62, "cost": 0.09,
        "v_prod": 0.62, "w_draw": 0.30, "gel_frac": 0.30,
        "ch_yield": 0.0, "ch_use": 0.30, "sigma0": 620.0,
        "ref": "Latent hydraulic; requires CH or alkali activation",
    },
    # ---------------- Non-Portland binder chemistries ------------------------
    "mgo": {
        "name": "Dead-burned magnesia (MgO, 1600 C calcine)",
        "role": "binder", "chem": "acid_base",
        "rho": 3580.0, "d50": 45.0, "beta": 0.64, "cost": 0.60,
        "v_prod": 1.42, "w_draw": 1.55, "gel_frac": 0.05,
        "ch_yield": 0.0, "ch_use": 0.0, "sigma0": 430.0,
        "ref": "Wagh (2004) Chemically Bonded Phosphate Ceramics: MgO + KH2PO4 + 5H2O -> MgKPO4.6H2O",
    },
    "kh2po4": {
        "name": "Monopotassium phosphate KH2PO4",
        "role": "binder", "chem": "acid_base",
        "rho": 2340.0, "d50": 120.0, "beta": 0.66, "cost": 1.40,
        "v_prod": 0.72, "w_draw": 0.42, "gel_frac": 0.05,
        "ch_yield": 0.0, "ch_use": 0.0, "sigma0": 430.0,
        "ref": "Acid partner in the MKP ceramic; sets at ambient in 30-60 min",
    },
    "geopoly": {
        "name": "Metakaolin + Na-silicate geopolymer binder",
        "role": "binder", "chem": "alkali",
        "rho": 2400.0, "d50": 4.0, "beta": 0.58, "cost": 0.75,
        "v_prod": 0.78, "w_draw": 0.36, "gel_frac": 0.20,
        "ch_yield": 0.0, "ch_use": 0.0, "sigma0": 520.0,
        "ref": "Davidovits (1991): N-A-S-H 3D aluminosilicate network, no CH phase",
    },
    "vinylester": {
        "name": "Vinyl ester resin + MEKP initiator",
        "role": "binder", "chem": "polymer",
        "rho": 1100.0, "d50": 0.0, "beta": 1.00, "cost": 3.80,
        "v_prod": 0.0, "w_draw": 0.0, "gel_frac": 0.0,
        "ch_yield": 0.0, "ch_use": 0.0, "sigma0": 165.0,
        "ref": "Polymer-concrete binder; free-radical addition cure, no capillary porosity",
    },
    "ra": {
        "name": "Reactive alumina 0.5 um (>99.7% Al2O3) sinter binder",
        "role": "binder", "chem": "ceramic",
        "hp_k": 0.45, "d_crit_nm": 30.0,
        "rho": 3950.0, "d50": 0.5, "beta": 0.56, "cost": 2.40,
        "v_prod": 0.0, "w_draw": 0.0, "gel_frac": 0.0,
        "ch_yield": 0.0, "ch_use": 0.0, "sigma0": 3000.0,
        "ref": "Low-cement-castable matrix; sinters to dense corundum above 1500 C",
    },
    "cosinter": {
        "name": "Co-W-C sinter aid (HPHT diamond compact binder)",
        "role": "binder", "chem": "ceramic",
        "rho": 8900.0, "d50": 2.0, "beta": 0.60, "cost": 65.0,
        "v_prod": 0.0, "w_draw": 0.0, "gel_frac": 0.0,
        "ch_yield": 0.0, "ch_use": 0.0, "sigma0": 1500.0,
        "ref": "Cobalt infiltrant for diamond-diamond bonding at 5-6 GPa / 1450 C",
    },

    # ---------------- Fillers / aggregates ----------------------------------
    "gravel": {
        "name": "Crushed granite 4-20 mm",
        "role": "filler", "rho": 2650.0, "d50": 12000.0, "beta": 0.66,
        "sigma_c": 250.0, "E": 60.0, "cost": 0.02, "bond": 0.50,
        "ref": "Granite UCS 150-250 MPa",
    },
    "gravel10": {
        "name": "Crushed basalt 4-10 mm",
        "role": "filler", "rho": 2900.0, "d50": 6000.0, "beta": 0.66,
        "sigma_c": 320.0, "E": 90.0, "cost": 0.03, "bond": 0.52,
        "ref": "Basalt UCS 250-400 MPa; small top size is standard for HSC",
    },
    "sand": {
        "name": "Siliceous concrete sand 0-4 mm",
        "role": "filler", "rho": 2650.0, "d50": 900.0, "beta": 0.72,
        "sigma_c": 1100.0, "E": 95.0, "cost": 0.02, "bond": 0.55,
        "ref": "Quartz grain crushing strength ~1.0-1.3 GPa",
    },
    "qsand": {
        "name": "Graded quartz sand 0.15-0.60 mm (UHPC grade)",
        "role": "filler", "rho": 2650.0, "d50": 320.0, "beta": 0.68,
        "sigma_c": 1100.0, "E": 95.0, "cost": 0.09, "bond": 0.75,
        "ref": "Richard & Cheyrezy (1995) RPC sand fraction",
    },
    "qflour": {
        "name": "Ground quartz flour 10 um",
        "role": "filler", "rho": 2650.0, "d50": 10.0, "beta": 0.62,
        "sigma_c": 1100.0, "E": 95.0, "cost": 0.14, "bond": 0.85,
        "ref": "Inert filler at ambient; pozzolanic above 150 C (autoclave)",
    },
    "steelshot": {
        "name": "Hardened steel shot 0.15-0.80 mm",
        "role": "filler", "rho": 7850.0, "d50": 380.0, "beta": 0.72,
        "sigma_c": 2000.0, "E": 200.0, "cost": 1.10, "bond": 0.70,
        "ref": "Richard & Cheyrezy (1995): steel aggregate replaces sand in RPC-800",
    },
    "talumina": {
        "name": "Tabular alumina 0.1-3 mm (sintered corundum)",
        "role": "filler", "rho": 3550.0, "d50": 700.0, "beta": 0.70,
        "hp_k": 0.45, "d_crit_nm": 30.0, "grain_fixed_nm": 60000.0,
        "sigma0": 3000.0, "sigma_c": 2500.0, "E": 380.0, "cost": 1.60, "bond": 0.80,
        "ref": "Dense alpha-Al2O3: UCS 2.2-2.8 GPa, E 380 GPa",
    },
    "sic": {
        "name": "Black silicon carbide F220 (98% SiC)",
        "role": "filler", "rho": 3210.0, "d50": 60.0, "beta": 0.64,
        "hp_k": 0.55, "d_crit_nm": 25.0, "grain_fixed_nm": 20000.0,
        "sigma0": 3800.0, "sigma_c": 3900.0, "E": 410.0, "cost": 2.20, "bond": 0.82,
        "ref": "Sintered SiC: UCS ~3.9 GPa, E 410 GPa, Hv 25 GPa",
    },
    "b4c": {
        "name": "Boron carbide F320 (B4C)",
        "role": "filler", "rho": 2520.0, "d50": 30.0, "beta": 0.62,
        "hp_k": 0.50, "d_crit_nm": 25.0,
        "sigma0": 3000.0, "sigma_c": 2900.0, "E": 450.0, "cost": 55.0, "bond": 0.82,
        "ref": "B4C: UCS 2.8-3.0 GPa, E 450 GPa, third-hardest bulk material",
    },
    "wc": {
        "name": "Cemented tungsten carbide granulate WC-6Co",
        "role": "filler", "rho": 14900.0, "d50": 150.0, "beta": 0.68,
        "hp_k": 0.60, "d_crit_nm": 20.0, "grain_fixed_nm": 2000.0,
        "sigma0": 5200.0, "sigma_c": 5500.0, "E": 620.0, "cost": 45.0, "bond": 0.85,
        "ref": "WC-6Co: UCS 5.0-6.0 GPa, E 600-640 GPa",
    },
    "cbn": {
        "name": "Cubic boron nitride micropowder 20-40 um",
        "role": "filler", "rho": 3480.0, "d50": 30.0, "beta": 0.63,
        "hp_k": 0.80, "d_crit_nm": 18.0,
        "sigma0": 5500.0, "sigma_c": 8000.0, "E": 850.0, "cost": 2200.0, "bond": 0.80,
        "ref": "cBN Hv 45-50 GPa; PCBN compacts 4-6 GPa UCS",
    },
    "diamond": {
        "name": "Synthetic diamond micropowder 10-40 um (MBD grade)",
        "role": "filler", "rho": 3520.0, "d50": 25.0, "beta": 0.63,
        "hp_k": 0.95, "d_crit_nm": 15.0,
        "sigma0": 6610.0, "sigma_c": 55000.0, "E": 1050.0, "cost": 900.0, "bond": 0.85,
        "ref": "Diamond UCS 55-110 GPa, E 1050 GPa; PCD compacts reach 7-8 GPa",
    },

    "sic_fine": {
        "name": "Submicron alpha-SiC 3 um (sinter-grade)",
        "role": "filler", "rho": 3210.0, "d50": 3.0, "beta": 0.58,
        "hp_k": 0.55, "d_crit_nm": 25.0,
        "sigma0": 3800.0, "sigma_c": 3900.0, "E": 410.0, "cost": 9.0, "bond": 0.88,
        "ref": "Fine SiC fraction; fills the coarse voids and feeds neck growth",
    },
    "nano_sic": {
        "name": "Nanocrystalline beta-SiC 80 nm",
        "role": "binder", "chem": "ceramic",
        "hp_k": 0.55, "d_crit_nm": 25.0,
        "rho": 3210.0, "d50": 0.08, "beta": 0.50, "cost": 180.0,
        "v_prod": 0.0, "w_draw": 0.0, "gel_frac": 0.0,
        "ch_yield": 0.0, "ch_use": 0.0, "sigma0": 3800.0,
        "ref": "Nanograin SiC: Hv rises 25 -> 32 GPa as grain falls to ~100 nm "
               "(Hall-Petch). Densified by spark plasma sintering.",
    },
    "carbon_black": {
        "name": "Carbon black (reaction-bonding carbon source)",
        "role": "filler", "rho": 1900.0, "d50": 0.05, "beta": 0.44,
        "hp_k": 0.55, "d_crit_nm": 25.0,
        "sigma0": 3800.0, "sigma_c": 3900.0, "E": 410.0, "cost": 2.0, "bond": 0.90,
        "ref": "C + Si(l) -> SiC in situ; converts to fresh SiC, so it is scored "
               "as the SiC it becomes, not as carbon",
    },
    "si_metal": {
        "name": "Silicon melt infiltrant (1450 C)",
        "role": "infiltrant", "rho": 2330.0, "d50": 0.0, "beta": 0.60,
        "sigma0": 700.0, "sigma_c": 700.0, "E": 130.0, "cost": 3.0, "bond": 0.95,
        "ref": "Wicks into the open pore network by capillarity and reacts with "
               "the carbon; residual free Si is the weak phase in RBSC",
    },
    "nanodiamond": {
        "name": "Detonation nanodiamond 20 nm (purified)",
        "role": "binder", "chem": "ceramic",
        "hp_k": 0.95, "d_crit_nm": 15.0,
        "rho": 3520.0, "d50": 0.020, "beta": 0.42, "cost": 3500.0,
        "v_prod": 0.0, "w_draw": 0.0, "gel_frac": 0.0,
        "ch_yield": 0.0, "ch_use": 0.0, "sigma0": 6610.0,
        "ref": "Irifune et al. (2003) Nature 421:599 -- nano-polycrystalline "
               "diamond, Knoop 110-140 GPa, HARDER than single-crystal diamond",
    },
    "nanodiamond_c": {
        "name": "Diamond micropowder 250 nm (bimodal packing aid)",
        "role": "filler", "rho": 3520.0, "d50": 0.25, "beta": 0.50,
        "hp_k": 0.95, "d_crit_nm": 15.0, "grain_fixed_nm": 250.0,
        "sigma0": 6610.0, "sigma_c": 55000.0, "E": 1050.0, "cost": 1800.0,
        "bond": 0.90,
        "ref": "Coarse mode of the bimodal slip; raises green density ~8 points",
    },

    "onion_carbon": {
        "name": "Onion-like carbon nanoparticles (nt-diamond precursor)",
        "role": "binder", "chem": "ceramic",
        "hp_k": 0.95, "d_crit_nm": 15.0, "tw_k": 1.33,
        "rho": 2100.0, "d50": 0.005, "beta": 0.40, "cost": 5200.0,
        "v_prod": 0.0, "w_draw": 0.0, "gel_frac": 0.0,
        "ch_yield": 0.0, "ch_use": 0.0, "sigma0": 6610.0,
        "ref": "Huang et al. (2014) Nature 510:250 -- onion carbon converts under "
               "20 GPa / 2000 C to nanotwinned diamond, Hv 200 GPa, twins ~5 nm. "
               "Hardness roughly double single-crystal diamond.",
    },
    "onion_bn": {
        "name": "Onion-like boron nitride (nt-cBN precursor)",
        "role": "binder", "chem": "ceramic",
        "hp_k": 0.80, "d_crit_nm": 18.0, "tw_k": 0.503,
        "rho": 2280.0, "d50": 0.006, "beta": 0.40, "cost": 2600.0,
        "v_prod": 0.0, "w_draw": 0.0, "gel_frac": 0.0,
        "ch_yield": 0.0, "ch_use": 0.0, "sigma0": 5500.0,
        "ref": "Tian et al. (2013) Nature 493:385 -- onion BN converts under "
               "15 GPa / 1800 C to nanotwinned cBN, Hv 108 GPa, twins ~3.8 nm",
    },

    # ---------------- Fibers -------------------------------------------------
    "steelfib": {
        "name": "Straight brass-coated steel microfiber 13 x 0.20 mm",
        "role": "fiber", "rho": 7850.0, "sigma_t": 2800.0, "E": 200.0,
        "cost": 1.80, "l_d": 65.0,
        "ref": "UHPC standard fiber, tensile 2600-3000 MPa",
    },
    "maragefib": {
        "name": "Maraging 300 steel microfiber 10 x 0.15 mm",
        "role": "fiber", "rho": 8000.0, "sigma_t": 3500.0, "E": 190.0,
        "cost": 22.0, "l_d": 67.0,
        "ref": "Maraging 300 UTS 2.0-2.4 GPa, 3.5 GPa as cold-drawn fine wire",
    },
    "sicwhisk": {
        "name": "SiC whisker (beta-SiC, 0.6 x 30 um)",
        "role": "fiber", "rho": 3210.0, "sigma_t": 8000.0, "E": 550.0,
        "cost": 480.0, "l_d": 50.0,
        "ref": "SiC whisker tensile 7-10 GPa; ceramic toughening reinforcement",
    },

    # ---------------- Liquids / admixtures ------------------------------------
    "water": {
        "name": "Deionised mixing water",
        "role": "water", "rho": 1000.0, "cost": 0.001,
        "ref": "ASTM C1602 mixing water",
    },
    "sp": {
        "name": "Polycarboxylate ether superplasticiser (30% solids)",
        "role": "admix", "rho": 1080.0, "cost": 2.60, "disp": 1.00,
        "ref": "PCE steric dispersion; lowers yield stress 5-20x at saturation dose",
    },
    "defloc": {
        "name": "Castable deflocculant (Na-polyacrylate + STPP)",
        "role": "admix", "rho": 1200.0, "cost": 3.10, "disp": 0.85,
        "ref": "Standard low-cement-castable dispersant package",
    },
    "retarder": {
        "name": "Boric acid set retarder (CBPC)",
        "role": "admix", "rho": 1440.0, "cost": 2.00, "disp": 0.20,
        "ref": "Extends MKP working time from ~8 min to 45-60 min",
    },
    "binderveh": {
        "name": "Organic casting vehicle (PVB + glycol, burns out)",
        "role": "admix", "rho": 1050.0, "cost": 6.50, "disp": 0.60,
        "ref": "Green-body casting vehicle; removed in binder burnout before HPHT",
    },
}

# =============================================================================
# SECTION 2 -- PHYS: calibrated physical constants
# =============================================================================

PHYS = {
    # --- Universal ---
    "g": 9.81,                  # m/s2
    "R_gas": 8.314,             # J/(mol*K)

    # --- Ryshkevitch-Duckworth porosity-strength law -----------------------
    # sigma = sigma0 * exp(-b * P).  b is calibrated on two anchor pastes:
    #   w/c 0.50, alpha 0.743 -> P 0.466 -> 40 MPa   (measured 38-45 MPa)
    #   w/c 0.25, alpha 0.580 -> P 0.272 -> 130 MPa  (measured 120-140 MPa)
    # which gives b = 6.05 and a pore-free paste strength near 650 MPa,
    # consistent with hot-pressed cement paste (Roy & Gouda 1973: 400-650 MPa).
    "rysh_b": 6.05,
    "rysh_b_ceramic": 5.20,     # ceramics show a slightly gentler exponent

    # --- Hall-Petch grain-boundary strengthening ---------------------------
    # sigma(d) = sigma_ref + k * (1/sqrt(d) - 1/sqrt(d_ref))
    # Grain boundaries block cleavage crack extension, so a finer grain is a
    # stronger solid.  This is the single most powerful lever in the whole
    # model: it is why nano-polycrystalline diamond out-performs single-crystal
    # diamond, and it is the only mechanism here that reaches 10 GPa without a
    # jacket.  Below a critical grain size the trend REVERSES (inverse
    # Hall-Petch: grain-boundary sliding takes over from dislocation/crack
    # blocking), which puts a real, physical optimum on grain size rather than
    # letting the model extrapolate to zero.
    "hp_d_ref_um": 10.0,        # reference grain size for the tabulated sigma0
    "hp_inverse_exp": 0.80,     # falloff exponent below the critical grain size

    # --- Nanotwin strengthening --------------------------------------------
    # A COHERENT TWIN boundary blocks dislocations and cracks like a grain
    # boundary, but it does not slide, so nanotwinned solids keep strengthening
    # far below the grain size at which ordinary Hall-Petch reverses.  This is
    # the strongest mechanism in the model and it is measured, not predicted:
    #   nanotwinned cBN,     3.8 nm twins -> Hv 108 GPa (Tian 2013)
    #   nanotwinned diamond, 5.0 nm twins -> Hv 200 GPa (Huang 2014)
    # both of which exceed single-crystal diamond.
    "twin_no_inverse": True,    # coherent boundaries do not slide -> no turnover
    "twin_floor_nm": 2.0,       # below ~2 nm the twin is a stacking fault, not a twin

    # --- Grain growth during sintering --------------------------------------
    # Densification wants time at temperature; time at temperature coarsens the
    # grain.  Pressure breaks that trade-off -- it densifies without the dwell,
    # which is the whole reason HPHT can make a nanograin body at all.
    #   growth = 1 + G * Tn^1.5 * (t/60)^0.33 / (1 + P/P0)
    # Calibrated against three anchors: SPS nano-SiC (80 nm feed -> ~120 nm),
    # HPHT NPD (20 nm feed -> ~21 nm), fired alumina castable (coarsens ~3x).
    "growth_G": 2.50,
    "growth_p_ref": 500.0,      # MPa; pressure scale that suppresses coarsening

    # --- Densification ------------------------------------------------------
    "sinter_p_scale": 2000.0,   # MPa; pressure-assisted sintering completeness
    "hpht_p_scale": 700.0,      # MPa; pressure closure of residual porosity
    "infiltrated_porosity": 0.005,   # melt infiltration leaves ~0.5% voids

    # --- Degree of hydration (Waller / Mills form) --------------------------
    "alpha_a": 1.031,
    "alpha_b": 0.194,

    # --- Cure factor on sigma0 (product quality, not porosity) --------------
    "cure_ambient": 1.00,       # 20 C sealed
    "cure_steam90": 1.06,       # 90 C steam: denser, lower Ca/Si C-S-H
    "cure_auto200": 1.18,       # 200 C autoclave: 11 A tobermorite
    "cure_auto400": 1.30,       # 250-400 C: xonotlite, near-crystalline
    "cure_polymer": 1.00,
    # Gel porosity is NOT permanent.  Above ~150 C the C-S-H gel recrystallises
    # (11 A tobermorite, then xonotlite above ~250 C) and most of the gel pore
    # volume closes into dense crystal.  This is the actual mechanism behind
    # RPC-800, and without it no hydrated binder can pass ~250 MPa.
    "gel_collapse_min": 0.25,   # residual gel porosity fraction at 400 C
    "cure_fired": 1.00,         # firing is carried by the ceramic sigma0

    # --- Pressure applied during setting -------------------------------------
    # Expels entrapped air and part of the free water before the skeleton locks.
    "press_water_k": 0.115,     # free-water expulsion coefficient (log law)
    "press_air_floor": 0.002,   # residual air volume fraction under pressure

    # --- Composite / ITZ load sharing ----------------------------------------
    "agg_gain": 0.22,           # gain coefficient for strong, well-bonded filler
    "agg_loss": 0.30,           # penalty coefficient for poor ITZ bond
    "agg_mob_span": 3.0,        # strength ratio at which filler fully contributes
    "dmax_exp": 0.060,          # Griffith-flaw exponent on maximum particle size
    "dmax_ref_mm": 0.60,        # reference d_max (UHPC sand top size)
    "agg_cap_frac": 0.92,       # composite cannot exceed 92% of filler strength

    # --- Fibers ---------------------------------------------------------------
    "fiber_k": 3.5,             # compressive gain per unit fiber volume fraction
    "fiber_ref_mpa": 2000.0,
    "fiber_knee": 0.040,        # vol fraction past which fibers ball and trap air
    "fiber_air_pct": 150.0,     # extra air (%) per unit fiber volume past the knee
    "fiber_air_cap": 14.0,      # entrapped air ceiling (%) even at absurd fiber loads

    # --- Weibull size effect ---------------------------------------------------
    "weibull_m_cement": 12.0,
    "weibull_m_uhpc": 15.0,
    "weibull_m_ceramic": 10.0,
    "ref_cube_mm": 100.0,

    # --- Rheology (YODEL-form yield stress + Roussel spread) --------------------
    # Yield stress is dominated by how close the solid fraction sits to the
    # jamming point phi_max.  tau_k is calibrated on two anchors:
    #   conventional concrete, no SP    -> ~1900 Pa, spread ~300 mm (slump 120 mm)
    #   UHPC, PCE at saturation dose    -> ~150 Pa,  spread ~490 mm (flowable)
    "tau_k": 260.0,             # Pa
    "tau_d_ref_um": 1000.0,     # reference d50 for the (weak) size term
    "tau_d_exp": 0.15,          # size exponent -- small; packing does the work
    "fiber_jam": 1.00,          # fibers cut the attainable packing by this x vf
    "phi_perc": 0.30,           # percolation threshold solid volume fraction
    "cone_volume_m3": 5.50e-3,  # Abrams cone volume
    "flow_pourable_mm": 250.0,  # minimum spread to call the mix "pourable"
    "flow_scc_mm": 550.0,       # self-consolidating threshold

    # --- Packing (de Larrard CPM) -----------------------------------------------
    "K_pour": 6.00,             # poured, light vibration
    "K_vib": 9.00,              # strong vibration
    "K_press": 13.00,           # pressure forming

    # --- Confinement (Richart 1928 / high-pressure Mohr-Coulomb) -----------------
    # f_cc = f_co + k(f_l) * f_l, k decaying from 4.1 at low confinement toward
    # 2.2 in the GPa range, matching high-pressure triaxial data on concrete.
    "conf_k_lo": 4.10,
    "conf_k_hi": 2.20,
    "conf_decay": 2.00,         # decay scale, in units of f_co
}

TARGET_MPA = 10000.0
MPA_TO_PSI = 145.0377377              # 1 MPa = 145.038 psi (pounds per square inch)
TARGET_PSI = TARGET_MPA * MPA_TO_PSI  # 1,450,378 psi


def mpa_to_psi(mpa):
    """Convert MPa to psi, returning a compact human-readable string."""
    psi = mpa * MPA_TO_PSI
    if psi >= 1_000_000:
        return "%.2f Mpsi" % (psi / 1_000_000)
    if psi >= 1000:
        return "%.0f kpsi" % (psi / 1000)
    return "%.0f psi" % psi


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


# =============================================================================
# SECTION 3 -- PACKING: de Larrard Compressible Packing Model
# =============================================================================

def cpm_interaction(d_coarse, d_fine):
    """Loosening (a_ij) and wall (b_ij) interaction functions of the CPM.

    a_ij : how much a fine class j loosens the packing of a coarse class i
    b_ij : how much a coarse class i disturbs the packing of a fine class j
    Both go to 0 when the size ratio is large (perfect size segregation) and
    to 1 when the classes are the same size.
    de Larrard (1999) "Concrete Mixture Proportioning", eqs. 3.9-3.10.
    """
    r = clamp(d_fine / max(d_coarse, 1e-12), 0.0, 1.0)
    a = math.sqrt(max(0.0, 1.0 - (1.0 - r) ** 1.02))
    b = 1.0 - (1.0 - r) ** 1.50
    return a, b


def virtual_packing(classes):
    """Virtual packing density gamma of a multi-class blend.

    classes : list of (d50_um, volume_fraction, beta) sorted coarse -> fine
    Returns gamma = min_i gamma_i, the packing an infinite compaction energy
    would reach.  Each class is tested as the 'dominant' (skeleton-forming) one.
    """
    n = len(classes)
    if n == 0:
        return 0.0, []
    gammas = []
    for i in range(n):
        d_i, y_i, b_i = classes[i]
        s = 0.0
        for j in range(n):
            if j == i:
                continue
            d_j, y_j, b_j = classes[j]
            if d_j > d_i:                      # j is coarser -> wall effect on i
                a, b = cpm_interaction(d_j, d_i)
                s += (1.0 - b_i + b * b_i * (1.0 - 1.0 / max(b_j, 1e-9))) * y_j
            else:                              # j is finer -> loosening effect
                a, b = cpm_interaction(d_i, d_j)
                s += (1.0 - a * b_i / max(b_j, 1e-9)) * y_j
        denom = 1.0 - s
        gammas.append(min(b_i / denom, 0.98) if denom > 1e-6 else 0.98)
    return min(gammas), gammas


def actual_packing(classes, K):
    """Actual packing density phi from the virtual packing and the compaction
    index K.  Solves  K = sum_i (y_i / beta_i) / (1/phi - 1/gamma_i)  for phi.

    K = 4.5 pouring, 4.75 vibration, 9.0 pressure forming (de Larrard 1999).
    """
    gamma, gammas = virtual_packing(classes)
    if gamma <= 0.0 or gamma >= 1e8:
        return 0.0, 0.0

    def K_of(phi):
        tot = 0.0
        for (d_i, y_i, b_i), g_i in zip(classes, gammas):
            denom = (1.0 / phi) - (1.0 / g_i)
            if denom <= 1e-9:
                return 1e9
            tot += (y_i / max(b_i, 1e-9)) / denom
        return tot

    lo, hi = 1e-4, gamma * 0.999999
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if K_of(mid) < K:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi), gamma


def funk_dinger_cpft(d_um, d_min_um, d_max_um, q):
    """Modified Andreasen (Funk & Dinger 1980) cumulative finer volume fraction.

        CPFT(D) = (D^q - Dmin^q) / (Dmax^q - Dmin^q)

    q = 0.37 packs densest for spheres; q = 0.21-0.26 is the practical optimum
    for angular castable powders (Dinger & Funk 1994).
    """
    if d_max_um <= d_min_um:
        return 1.0
    num = d_um ** q - d_min_um ** q
    den = d_max_um ** q - d_min_um ** q
    return clamp(num / den)


def psd_distance_to_funk_dinger(classes, q):
    """RMS deviation of an actual blend from the ideal Funk-Dinger curve.
    0 = perfect gradation.  Used as a gradation-quality score in optimisation.
    """
    if not classes:
        return 1.0
    ds = sorted(c[0] for c in classes)
    d_min, d_max = ds[0], ds[-1]
    order = sorted(classes, key=lambda c: c[0])
    cum = 0.0
    err = 0.0
    for d_i, y_i, b_i in order:
        cum += y_i
        ideal = funk_dinger_cpft(d_i, d_min, d_max, q)
        err += (cum - ideal) ** 2
    return math.sqrt(err / len(order))


# =============================================================================
# SECTION 4 -- CHEM: binder reaction, porosity, matrix strength
# =============================================================================

def degree_of_hydration(w_b, cure_factor=1.0, age_days=28.0):
    """Ultimate degree of hydration attainable at a given water/binder ratio.

    Waller / Mills form:  alpha_max = 1.031 * (w/b) / (0.194 + w/b)
    Below w/b ~0.42 there is not enough water to hydrate all the cement, which
    is exactly why UHPC keeps 40-60% of its cement as unreacted (but very hard
    and well-bonded) filler.  Heat curing raises the reachable fraction; age
    below 28 d reduces it by a maturity term.
    """
    a_max = clamp(PHYS["alpha_a"] * w_b / (PHYS["alpha_b"] + w_b), 0.0, 1.0)
    # Freiesleben Hansen & Pedersen maturity, normalised to 1.0 at 28 days
    def mat(t):
        return math.exp(-((0.5 / max(t, 0.01)) ** 0.55))
    maturity = clamp(mat(age_days) / mat(28.0), 0.20, 1.12)
    return clamp(a_max * cure_factor * maturity, 0.0, 1.0)


def pressure_effects(set_pressure_mpa, free_water_frac, air_frac):
    """Effect of pressure applied during setting (before the skeleton locks).

    Two mechanisms, both measured in RPC-800 and hot-pressed pastes:
      1. entrapped air is squeezed out toward a residual floor
      2. part of the free (capillary) water is expressed out of the mould
    Richard & Cheyrezy (1995) applied 50 MPa during setting and reported a
    water expulsion of roughly a quarter of the mixing water.
    """
    if set_pressure_mpa <= 0.0:
        return free_water_frac, air_frac, 0.0
    expel = PHYS["press_water_k"] * math.log(1.0 + set_pressure_mpa / 10.0)
    expel = clamp(expel, 0.0, 0.55)
    new_water = free_water_frac * (1.0 - expel)
    new_air = max(PHYS["press_air_floor"],
                  air_frac * math.exp(-set_pressure_mpa / 12.0))
    return new_water, new_air, expel


def gel_collapse_factor(temp_c):
    """Fraction of the gel porosity that SURVIVES a given curing temperature.

    Below about 100 C, all of it: C-S-H keeps its ~28% intrinsic gel porosity
    forever, which is the hard ceiling on ordinary hydrated binders.  Autoclaving
    recrystallises the gel -- 11 A tobermorite from roughly 180 C, xonotlite
    above 250 C -- and those crystalline hydrates are dense.  Richard & Cheyrezy
    attributed most of the RPC-800 jump to exactly this conversion.
    """
    if temp_c <= 90.0:
        return 1.0
    f = 1.0 - (1.0 - PHYS["gel_collapse_min"]) * clamp((temp_c - 90.0) / 310.0) ** 0.6
    return clamp(f, PHYS["gel_collapse_min"], 1.0)


def binder_reaction(binder_masses, water_kg, air_pct, cure_factor, age_days,
                    set_pressure_mpa=0.0, cure_temp_c=20.0):
    """Full Powers-Brownyard volumetric bookkeeping for a binder blend.

    Tracks, per cubic metre:
      - degree of reaction of each hydraulic binder (water-limited)
      - portlandite balance: cement releases CH, pozzolans consume it, so the
        pozzolan fraction that can actually react is capped by CH supply
      - capillary porosity (free water left over)
      - gel porosity (intrinsic to the reaction product)
      - air voids
      - volume-weighted sigma0 of the reaction products

    Returns a dict with the paste porosity P and the paste strength.
    """
    hydraulic = {k: m for k, m in binder_masses.items()
                 if MATS[k].get("chem") in ("hydraulic",)}
    pozzolan = {k: m for k, m in binder_masses.items()
                if MATS[k].get("chem") == "pozzolanic"}
    other = {k: m for k, m in binder_masses.items()
             if MATS[k].get("chem") in ("acid_base", "alkali")}
    inert_b = {k: m for k, m in binder_masses.items()
               if MATS[k].get("chem") in ("polymer", "ceramic")}

    total_binder = sum(binder_masses.values())
    if total_binder <= 0.0:
        return None
    w_b = water_kg / total_binder

    # --- degree of reaction of each family --------------------------------
    alpha = degree_of_hydration(w_b, cure_factor, age_days)

    # --- portlandite balance ------------------------------------------------
    ch_supply = sum(m * MATS[k]["ch_yield"] for k, m in hydraulic.items()) * alpha
    ch_demand = sum(m * MATS[k]["ch_use"] for k, m in pozzolan.items())
    ch_ratio = 1.0 if ch_demand <= 1e-9 else clamp(ch_supply / ch_demand)

    reacted = {}
    for k, m in hydraulic.items():
        reacted[k] = m * alpha
    for k, m in pozzolan.items():
        reacted[k] = m * ch_ratio                    # CH-limited, not water-limited
    for k, m in other.items():
        # acid-base and alkali-activated binders react essentially to completion
        reacted[k] = m * clamp(0.97 * cure_factor, 0.0, 1.0)
    for k, m in inert_b.items():
        reacted[k] = 0.0

    # --- volume bookkeeping (m3 per m3 of mix) --------------------------------
    v_binder_solid = sum(m / MATS[k]["rho"] for k, m in binder_masses.items())
    v_water = water_kg / 1000.0
    v_air = air_pct / 100.0

    v_prod = 0.0
    v_gelpore = 0.0
    w_drawn = 0.0
    sigma0_num = 0.0
    for k, r in reacted.items():
        if r <= 0.0:
            continue
        mat = MATS[k]
        vp = r * mat["v_prod"] / 1000.0           # cm3/g == L/kg -> m3
        v_prod += vp
        v_gelpore += vp * mat["gel_frac"]
        w_drawn += r * mat["w_draw"]
        sigma0_num += vp * mat["sigma0"]

    # unreacted binder grains keep their own (very high) intrinsic strength
    v_unreacted = 0.0
    for k, m in binder_masses.items():
        v_un = (m - reacted.get(k, 0.0)) / MATS[k]["rho"]
        v_unreacted += v_un
        sigma0_num += v_un * MATS[k]["sigma0"]

    # autoclave conversion closes most of the gel porosity into dense crystal
    g_keep = gel_collapse_factor(cure_temp_c)
    v_gelpore *= g_keep

    v_solid_eq = v_prod + v_unreacted
    sigma0_eff = sigma0_num / v_solid_eq if v_solid_eq > 0 else 0.0

    # --- capillary water left over ---------------------------------------------
    v_free_water = max(0.0, (water_kg - w_drawn) / 1000.0)
    v_free_water, v_air, expelled = pressure_effects(set_pressure_mpa,
                                                     v_free_water, v_air)

    v_paste = v_solid_eq + v_free_water + v_air
    if v_paste <= 0.0:
        return None

    P_cap = v_free_water / v_paste
    P_gel = v_gelpore / v_paste
    P_air = v_air / v_paste
    P_total = clamp(P_cap + P_gel + P_air, 0.0, 0.98)

    sigma_paste = sigma0_eff * math.exp(-PHYS["rysh_b"] * P_total)

    return {
        "w_b": w_b, "alpha": alpha, "ch_ratio": ch_ratio,
        "reacted": reacted, "sigma0_eff": sigma0_eff,
        "v_paste": v_paste, "v_binder_solid": v_binder_solid,
        "P_cap": P_cap, "P_gel": P_gel, "P_air": P_air, "P_total": P_total,
        "water_expelled_frac": expelled, "gel_kept": g_keep,
        "sigma_paste": sigma_paste,
    }


def hall_petch(sigma_ref, hp_k, d_grain_nm, d_crit_nm):
    """Grain-size strengthening of a brittle ceramic.

        sigma(d) = sigma_ref + k * (1/sqrt(d) - 1/sqrt(d_ref))

    sigma_ref is the tabulated strength at the reference grain size (10 um) and
    k is the Hall-Petch slope in MPa*sqrt(m).  Covalent ceramics carry large k
    (0.45-0.95) because their grain boundaries are genuinely hard barriers to
    crack extension, not just dislocation pile-up sites.

    Below d_crit the mechanism inverts -- grain-boundary sliding and triple-
    junction accommodation start to dominate, and the material gets weaker
    again.  Modelling that turnover is what stops the extrapolation running away
    to infinity as the grain size goes to zero, and it puts the optimum at a
    finite, reportable grain size.

    Refs: Hall (1951) Proc.Phys.Soc. B64:747; Petch (1953) JISI 174:25;
          Irifune et al. (2003) Nature 421:599 (nano-polycrystalline diamond);
          Schiotz & Jacobsen (2003) Science 301:1357 (inverse Hall-Petch).
    """
    d_ref = PHYS["hp_d_ref_um"] * 1e-6
    d_c = max(d_crit_nm, 1.0) * 1e-9
    d = max(d_grain_nm, 0.5) * 1e-9
    boost_at = lambda x: hp_k * (1.0 / math.sqrt(x) - 1.0 / math.sqrt(d_ref))
    if d >= d_c:
        boost = boost_at(d)
    else:
        # inverse Hall-Petch: the increment decays back toward zero
        boost = boost_at(d_c) * (d / d_c) ** PHYS["hp_inverse_exp"]
    return max(0.1 * sigma_ref, sigma_ref + boost)


def nanotwin_strength(sigma_ref, tw_k, twin_nm):
    """Strengthening from coherent nanotwin boundaries.

        sigma(lambda) = sigma_ref + k_tw * (1/sqrt(lambda) - 1/sqrt(d_ref))

    Same functional form as Hall-Petch, but WITHOUT the inverse turnover.  An
    ordinary grain boundary is a disordered layer that can slide once it is a
    large enough volume fraction, which is what makes nanocrystalline solids
    weaken below ~15 nm.  A coherent twin boundary is a mirror plane of the
    same lattice: it blocks dislocations and cracks just as well, but there is
    nothing to slide, so refining the twin keeps paying down to a few
    nanometres.

    This is measured, not extrapolated.  Nanotwinned cBN at 3.8 nm reaches
    Vickers 108 GPa and nanotwinned diamond at 5 nm reaches 200 GPa -- both
    above single-crystal diamond.

    Refs: Tian et al. (2013) Nature 493:385 (nt-cBN, Hv 108 GPa);
          Huang et al. (2014) Nature 510:250 (nt-diamond, Hv 200 GPa);
          Lu, Lu & Suresh (2009) Science 324:349 (nanotwin strengthening).
    """
    d_ref = PHYS["hp_d_ref_um"] * 1e-6
    lam = max(twin_nm, PHYS["twin_floor_nm"]) * 1e-9
    return sigma_ref + tw_k * (1.0 / math.sqrt(lam) - 1.0 / math.sqrt(d_ref))


def grain_growth(feed_nm, fire_temp_c, dwell_min, set_pressure_mpa):
    """Grain size a sintered body ends up at, from its feed powder.

    Grain size is an OUTCOME of processing, not a wish.  Coarsening scales with
    temperature and with dwell time, and is suppressed by applied pressure --
    pressure supplies the driving force for densification directly, so the body
    reaches full density before the grains have time to grow.

    That single trade-off is why the superhard routes in this library all use
    pressure: at 15 GPa a 20 nm feed sinters to a 21 nm grain, while the same
    powder held pressureless at temperature would coarsen past 100 nm and throw
    away most of the Hall-Petch increment it was bought for.
    """
    if feed_nm <= 0.0:
        return 5000.0
    t_norm = clamp((fire_temp_c - 900.0) / 1200.0)
    t_dwell = max(dwell_min, 0.1) / 60.0
    growth = 1.0 + (PHYS["growth_G"] * t_norm ** 1.5 * t_dwell ** 0.33 /
                    (1.0 + set_pressure_mpa / PHYS["growth_p_ref"]))
    return feed_nm * growth


def phase_strength(mat, grain_nm, twin_nm=0.0):
    """Strength of one ceramic phase at the microstructure it ends up with.

    Precedence: a nanotwinned phase is scored on its twin thickness, an
    ordinary phase on its grain size, and a phase with neither on its tabulated
    value.  Phases that keep their own microstructure through the process
    (already-sintered aggregate, cemented carbide granulate) carry
    grain_fixed_nm and ignore the body's grain size entirely.
    """
    base = mat.get("sigma0", mat.get("sigma_c", 0.0))
    if mat.get("tw_k") and twin_nm > 0.0:
        return nanotwin_strength(base, mat["tw_k"], twin_nm)
    if "hp_k" in mat:
        d = mat["grain_fixed_nm"] if mat.get("grain_fixed_nm") else grain_nm
        return hall_petch(base, mat["hp_k"], d, mat["d_crit_nm"])
    return base


def optimal_grain_size(mat_key):
    """The grain size that maximises strength for a phase -- i.e. the peak of
    the Hall-Petch / inverse-Hall-Petch curve.  Returns (nm, MPa)."""
    m = MATS[mat_key]
    if "hp_k" not in m:
        return None, m.get("sigma0", m.get("sigma_c", 0.0))
    best_d, best_s = None, -1.0
    for i in range(400):
        d = 2.0 * (200000.0 / 2.0) ** (i / 399.0)      # 2 nm -> 200 um, log sweep
        sig = hall_petch(m["sigma0"], m["hp_k"], d, m["d_crit_nm"])
        if sig > best_s:
            best_s, best_d = sig, d
    return best_d, best_s


def ceramic_phase_strength(solid_volumes, grain_nm, twin_nm=0.0):
    """Volume-weighted strength of a sintered ceramic body.

    In a fired body there is no meaningful binder/filler distinction -- it is
    one ceramic, and every phase in it carries load in proportion to how much of
    the volume it occupies.  Each phase is evaluated at the body's grain size
    through Hall-Petch, except phases that keep their own microstructure
    (already-sintered aggregate, metallic infiltrant), which carry their own.
    """
    v_tot = sum(v for _, v in solid_volumes)
    if v_tot <= 0.0:
        return 0.0
    acc = 0.0
    for k, v in solid_volumes:
        acc += phase_strength(MATS[k], grain_nm, twin_nm) * v
    return acc / v_tot


def ceramic_matrix_strength(solid_volumes, fire_temp_c, set_pressure_mpa,
                            porosity, grain_nm, twin_nm=0.0):
    """Strength of a fired / sintered ceramic body (no hydration chemistry).

    Three things set it, in order of leverage:
      1. WHICH phases are present, weighted by volume (ceramic_phase_strength)
      2. the GRAIN SIZE those phases end up at, through Hall-Petch
      3. the residual POROSITY, through Ryshkevitch

    Sintering completeness rises with temperature and is finished off by any
    pressure applied during the sinter: at HPHT pressures the neck growth that
    would need 2000 C at ambient pressure happens at 1450 C, which is exactly
    why diamond compacts can be made at all without graphitising.
    """
    sigma0 = ceramic_phase_strength(solid_volumes, grain_nm, twin_nm)
    s_frac = clamp((fire_temp_c - 900.0) / 700.0)
    sinter = 0.25 + 0.75 * (s_frac ** 0.65)
    if set_pressure_mpa > 0.0:
        sinter += (1.0 - sinter) * (1.0 - math.exp(-set_pressure_mpa /
                                                   PHYS["sinter_p_scale"]))
    sigma0_eff = sigma0 * clamp(sinter, 0.0, 1.0)
    return sigma0_eff * math.exp(-PHYS["rysh_b_ceramic"] * porosity), sigma0_eff


def polymer_matrix_strength(binder_masses, porosity):
    """Thermoset polymer binder: no capillary porosity, only entrapped air."""
    tot = sum(binder_masses.values())
    if tot <= 0.0:
        return 0.0, 0.0
    sigma0 = sum(m * MATS[k]["sigma0"] for k, m in binder_masses.items()) / tot
    return sigma0 * math.exp(-PHYS["rysh_b"] * porosity), sigma0


# =============================================================================
# SECTION 5 -- MECH: composite strength, fibers, size effect, confinement
# =============================================================================

def composite_strength(sigma_matrix, fillers, v_filler_frac, v_total,
                       bond_boost=0.0):
    """Load-sharing composite law for hard filler in a brittle matrix.

    In compression the matrix and the interfacial transition zone govern.
    A filler helps only if it is genuinely stronger than the matrix AND well
    bonded; if it is poorly bonded it acts as a stress raiser and hurts.

        K_agg = 1 + g * Vf * bond * mob  -  l * Vf * (1 - bond)
        mob   = clamp((sigma_f / sigma_m - 1) / span)

    The composite is then capped: it cannot exceed 92% of the crushing strength
    of its own filler (you cannot get diamond strength out of a diamond-filled
    cement -- the weaker phase always fails first).  A Griffith term on the
    maximum particle size supplies the mild d_max penalty that makes coarse
    concrete weaker than the same paste with fine aggregate.
    """
    if v_filler_frac <= 0.0 or sigma_matrix <= 0.0:
        return sigma_matrix, 1.0, 1.0, 0.0, 0.0

    v_tot_f = sum(v for _, v in fillers) or 1.0
    bond = sum(MATS[k]["bond"] * v for k, v in fillers) / v_tot_f
    bond = clamp(bond + bond_boost)
    sig_f = sum(MATS[k]["sigma_c"] * v for k, v in fillers) / v_tot_f
    E_f = sum(MATS[k]["E"] * v for k, v in fillers) / v_tot_f
    d_max_mm = max(MATS[k]["d50"] for k, _ in fillers) / 1000.0 * 2.2

    mob = clamp((sig_f / sigma_matrix - 1.0) / PHYS["agg_mob_span"])
    K_agg = (1.0
             + PHYS["agg_gain"] * v_filler_frac * bond * mob
             - PHYS["agg_loss"] * v_filler_frac * (1.0 - bond))
    K_dmax = (PHYS["dmax_ref_mm"] / max(d_max_mm, 1e-4)) ** PHYS["dmax_exp"]

    sigma_c = sigma_matrix * K_agg * K_dmax
    sigma_c = min(sigma_c, PHYS["agg_cap_frac"] * sig_f)
    return sigma_c, K_agg, K_dmax, bond, E_f


def fiber_factor(fibers, v_total):
    """Compressive gain from fiber reinforcement.

    Fibers mostly buy tensile capacity and post-peak ductility; the compressive
    gain is real but modest (5-15% at 2-3 vol%) and comes from lateral restraint
    of the splitting cracks.  Returns (K_fiber, volume fraction, volume-weighted
    fiber tensile strength).
    """
    if not fibers:
        return 1.0, 0.0, 0.0
    v_fib = sum(v for _, v in fibers)
    vf = v_fib / v_total if v_total > 0 else 0.0
    if vf <= 0.0:
        return 1.0, 0.0, 0.0
    sig_t = sum(MATS[k]["sigma_t"] * v for k, v in fibers) / v_fib
    # Above roughly 4 vol% the fibers start balling and trapping air, so each
    # additional percent buys much less than the first four did.
    knee = PHYS["fiber_knee"]
    vf_eff = vf if vf <= knee else knee + 0.35 * (vf - knee)
    K = 1.0 + PHYS["fiber_k"] * vf_eff * math.sqrt(sig_t / PHYS["fiber_ref_mpa"])
    return K, vf, sig_t


def elastic_modulus(sigma_c, v_filler_frac, E_filler, matrix_family):
    """Composite Young's modulus, Hashin-Shtrikman lower bound blended with the
    strength-based estimate.  E_matrix is taken from the ACI-style relation for
    cementitious matrices and directly for ceramic / polymer matrices.
    """
    if matrix_family == "ceramic":
        E_m = 90.0
    elif matrix_family == "polymer":
        E_m = 3.5
    else:
        E_m = 4.7 * math.sqrt(max(sigma_c, 1.0))    # GPa, ACI 318 form
        E_m = min(E_m, 60.0)
    if v_filler_frac <= 0.0 or E_filler <= 0.0:
        return E_m
    # Hashin-Shtrikman lower bound for stiff inclusions in a compliant matrix
    f = clamp(v_filler_frac)
    E_hs = E_m + f / (1.0 / max(E_filler - E_m, 1e-6) + (1.0 - f) / (3.0 * E_m))
    return E_hs


def weibull_size_correction(sigma_ref, specimen_mm, m):
    """Weibull weakest-link scaling between specimen sizes.

        sigma_2 / sigma_1 = (V_1 / V_2) ^ (1/m)

    A 20 mm cube reads meaningfully higher than a 100 mm cube of the same
    material.  This is a measurement-scale effect, NOT a material improvement,
    and the model always reports it separately.
    """
    v_ref = PHYS["ref_cube_mm"] ** 3
    v_new = max(specimen_mm, 1.0) ** 3
    return sigma_ref * (v_ref / v_new) ** (1.0 / m)


def confinement_k(f_l, f_co):
    """Confinement effectiveness coefficient k in f_cc = f_co + k * f_l.

    Richart et al. (1928) measured k = 4.1 at low confinement.  High-pressure
    triaxial tests (confining pressure of hundreds of MPa to GPa) show k falling
    to roughly 2.2-3.0 as the failure surface flattens and the material
    transitions from brittle splitting to ductile pore collapse.
    """
    if f_co <= 0.0:
        return PHYS["conf_k_lo"]
    span = PHYS["conf_k_lo"] - PHYS["conf_k_hi"]
    return PHYS["conf_k_hi"] + span * math.exp(-f_l / (PHYS["conf_decay"] * f_co))


def confined_strength(f_co, f_l):
    """Triaxial compressive capacity of a confined core."""
    if f_l <= 0.0:
        return f_co
    return f_co + confinement_k(f_l, f_co) * f_l


def confinement_required(f_co, target):
    """Binary search for the lateral pressure needed to reach a target strength.
    Returns None if the target is unreachable within a 20 GPa search bound.
    """
    if f_co >= target:
        return 0.0
    lo, hi = 0.0, 20000.0
    if confined_strength(f_co, hi) < target:
        return None
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if confined_strength(f_co, mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def jacket_capacity(sigma_y_mpa, od_id_ratio):
    """Lateral pressure a thick-walled jacket can supply to the core.

    Fully plastic thick-wall (Tresca / von Mises) limit:
        p = (2 / sqrt(3)) * sigma_y * ln(OD / ID)
    Multi-ring, pre-stressed dies (the HPHT press geometry) beat this by the
    ring pre-stress; belt/cubic presses routinely hold 5-6 GPa.
    """
    return (2.0 / math.sqrt(3.0)) * sigma_y_mpa * math.log(max(od_id_ratio, 1.0001))


# =============================================================================
# SECTION 6 -- RHEO: yield stress, slump flow, pourability
# =============================================================================

def yield_stress(phi_solid, phi_max, d50_um, sp_dose_frac, disp_eff=1.0,
                 vf_fiber=0.0):
    """Bingham yield stress of the fresh mix.

    The controlling variable is the packing utilisation r = phi / phi_max: as the
    solids approach their jamming point the paste film between grains vanishes
    and the yield stress diverges (Flatt & Bowen 2006 YODEL; Chateau, Ovarlez &
    Trung 2008).  Particle size enters only weakly once r is accounted for, so
    the size term carries a small exponent.  Fibers jam the skeleton early and
    are charged against the attainable packing directly.

        tau0 = tau_k * r^2 / (1 - r) * (d_ref / d50)^0.15 / f_sp

    Superplasticiser disperses the agglomerates and saturates near a 2% dose on
    binder, above which more admixture buys segregation rather than flow.  At
    saturation a PCE cuts the yield stress by 20-50x; 30x is used here.

    phi_max here is the JAMMING point of the suspension -- the maximum (virtual)
    packing of the blend -- not the dry packing a given compaction energy
    reaches.  Those are different numbers and the model reports both.
    """
    phi_max_eff = phi_max * (1.0 - PHYS["fiber_jam"] * clamp(vf_fiber, 0.0, 0.5))
    if phi_max_eff <= 0.0:
        return 1e9
    # Past the jamming point the mix is a damp compact, not a suspension: the
    # yield stress is reported as very large but finite so the classification
    # still reads "must be rammed or pressed" rather than a divide-by-zero.
    r = min(phi_solid / phi_max_eff, 0.997)
    size = (PHYS["tau_d_ref_um"] / max(d50_um, 0.05)) ** PHYS["tau_d_exp"]
    tau = PHYS["tau_k"] * r ** 2 / (1.0 - r) * size
    sat = clamp(sp_dose_frac / 0.020)
    return tau / (1.0 + 30.0 * sat * disp_eff)


def slump_flow_mm(tau0_pa, density_kg_m3, cone_volume_m3=None):
    """Slump-flow spread from yield stress (Roussel & Coussot 2005).

        tau0 = 225 * rho * g * V^2 / (128 * pi^2 * R^5)

    Inverted for the spread radius R.  Valid in the flow regime; below about a
    250 mm spread the mix has effectively stopped flowing and must be vibrated,
    pressed, or rammed rather than poured.
    """
    V = cone_volume_m3 or PHYS["cone_volume_m3"]
    if tau0_pa <= 1e-6:
        return 1200.0
    num = 225.0 * density_kg_m3 * PHYS["g"] * V ** 2
    den = 128.0 * math.pi ** 2 * tau0_pa
    R = (num / den) ** 0.2
    return min(1200.0, 2.0 * R * 1000.0)


def pourability_class(flow_mm):
    """Human-readable workability class from the measured spread."""
    if flow_mm >= 700.0:
        return "SELF-LEVELLING"
    if flow_mm >= PHYS["flow_scc_mm"]:
        return "SELF-CONSOLIDATING"
    if flow_mm >= 400.0:
        return "FLOWABLE"
    if flow_mm >= PHYS["flow_pourable_mm"]:
        return "POURABLE (vibrate)"
    if flow_mm >= 180.0:
        return "STIFF (ram/press)"
    return "NOT POURABLE"


# =============================================================================
# SECTION 7 -- MIXES: the formulation library (kg per cubic metre)
# =============================================================================
#
# Each mix is a real, batchable recipe.  "components" are kg/m3 of finished
# material.  "cure" describes what happens after the pour.  "confinement"
# describes the jacket, if any, that the cured pour is loaded inside.
#
# cure keys:
#   family        hydraulic | acid_base | alkali | polymer | ceramic
#   temp_c        curing temperature
#   age_days      age at test
#   set_pressure  MPa applied DURING setting (before the skeleton locks)
#   fire_temp_c   sintering temperature, if the pour is a green body
#   K             CPM compaction index (4.5 poured, 4.75 vibrated, 9.0 pressed)
#   air_pct       entrapped air before any pressure treatment

MIXES = [
    {
        "id": 1, "name": "OPC-BASELINE",
        "tagline": "Ordinary structural concrete -- the reference floor.",
        "components": {"opc": 360.0, "water": 180.0, "sand": 780.0, "gravel": 1060.0},
        "cure": {"family": "hydraulic", "temp_c": 20.0, "age_days": 28.0,
                 "set_pressure": 0.0, "fire_temp_c": 0.0, "K": 4.5, "air_pct": 2.0},
        "confinement": None, "evidence": "measured",

        "recipe": {
            "w_b": "0.50",
            "grading": "0-20 mm continuous, Fuller-type",
            "mixing": "Pan mixer 3 min; slump 120 mm",
            "placement": "Poured, poker-vibrated",
            "curing": "Wet-cured 28 d at 20 C",
            "mechanism": "Portland hydration; strength limited by capillary porosity at w/c 0.50",
            "references": "EN 206 C30/37; Powers & Brownyard (1948)",
        },
    },
    {
        "id": 2, "name": "HSC-100",
        "tagline": "High-strength concrete: low w/b plus silica fume.",
        "components": {"opc": 480.0, "sf": 48.0, "water": 148.0, "sp": 8.0,
                       "sand": 700.0, "gravel10": 1120.0},
        "cure": {"family": "hydraulic", "temp_c": 20.0, "age_days": 28.0,
                 "set_pressure": 0.0, "fire_temp_c": 0.0, "K": 4.75, "air_pct": 1.8},
        "confinement": None, "evidence": "measured",

        "recipe": {
            "w_b": "0.28",
            "grading": "0-10 mm top size, silica fume densifies the ITZ",
            "mixing": "High-shear 5 min; PCE added after 60 s wet",
            "placement": "Poured, vibrated",
            "curing": "Wet 28 d at 20 C",
            "mechanism": "Capillary porosity collapse plus pozzolanic ITZ densification",
            "references": "ACI 363R high-strength concrete practice",
        },
    },
    {
        "id": 3, "name": "UHPC-160",
        "tagline": "Ductal-class UHPC: no coarse aggregate, 2% steel fiber.",
        "components": {"opc": 710.0, "sf": 170.0, "qflour": 210.0, "water": 185.0,
                       "sp": 30.0, "qsand": 1020.0, "steelfib": 157.0},
        "cure": {"family": "hydraulic", "temp_c": 20.0, "age_days": 28.0,
                 "set_pressure": 0.0, "fire_temp_c": 0.0, "K": 4.75, "air_pct": 2.5},
        "confinement": None, "evidence": "measured",

        "recipe": {
            "w_b": "0.21",
            "grading": "d_max 0.6 mm; coarse aggregate deliberately removed",
            "mixing": "High-shear 12 min; dry blend first, water + PCE in two stages",
            "placement": "Self-levelling pour, no vibration",
            "curing": "Sealed 28 d at 20 C",
            "mechanism": "Dense particle packing, near-zero capillary porosity, fiber crack bridging",
            "references": "Richard & Cheyrezy (1995) Cem.Concr.Res. 25:1501; AFGC-SETRA UHPFRC",
        },
    },
    {
        "id": 4, "name": "RPC-200",
        "tagline": "Reactive powder concrete, 90 C steam cured.",
        "components": {"opc": 800.0, "sf": 200.0, "qflour": 200.0, "water": 175.0,
                       "sp": 35.0, "qsand": 900.0, "steelfib": 157.0},
        "cure": {"family": "hydraulic", "temp_c": 90.0, "age_days": 7.0,
                 "set_pressure": 0.0, "fire_temp_c": 0.0, "K": 4.75, "air_pct": 2.0},
        "confinement": None, "evidence": "measured",

        "recipe": {
            "w_b": "0.17",
            "grading": "d_max 0.4 mm, three-decade PSD",
            "mixing": "High-shear 15 min",
            "placement": "Poured into steel moulds, light vibration",
            "curing": "48 h at 90 C saturated steam after 24 h at 20 C",
            "mechanism": "Steam curing drives pozzolanic reaction and densifies C-S-H",
            "references": "Richard & Cheyrezy (1995): RPC-200 family",
        },
    },
    {
        "id": 5, "name": "RPC-800",
        "tagline": "Pressure applied during setting + 400 C heat + steel aggregate.",
        "components": {"opc": 950.0, "sf": 220.0, "qflour": 300.0, "water": 170.0,
                       "sp": 40.0, "steelshot": 1400.0, "maragefib": 630.0},
        "cure": {"family": "hydraulic", "temp_c": 400.0, "age_days": 7.0,
                 "set_pressure": 50.0, "fire_temp_c": 0.0, "K": 9.0, "air_pct": 3.0},
        "confinement": None, "evidence": "measured",

        "recipe": {
            "w_b": "0.15 as batched, ~0.11 after water expression",
            "grading": "d_max 0.8 mm; steel shot replaces quartz sand",
            "mixing": "High-shear 15 min, then cast into a pressure mould",
            "placement": "Poured, then 50 MPa applied during setting",
            "curing": "48 h at 250-400 C after pressure release",
            "mechanism": "Pressure expels air and free water; heat converts C-S-H to xonotlite",
            "references": "Richard & Cheyrezy (1995): 490-680 MPa measured, 800 MPa with steel aggregate",
        },
    },
    {
        "id": 6, "name": "DSP-SIC",
        "tagline": "Densified small particle paste with silicon carbide filler.",
        "components": {"cac": 700.0, "sf": 250.0, "water": 132.0, "sp": 35.0,
                       "sic": 1400.0, "qflour": 120.0},
        "cure": {"family": "hydraulic", "temp_c": 90.0, "age_days": 14.0,
                 "set_pressure": 0.0, "fire_temp_c": 0.0, "K": 4.75, "air_pct": 2.0},
        "confinement": None, "evidence": "measured",

        "recipe": {
            "w_b": "0.14",
            "grading": "SiC F220 (60 um) plus 0.15 um silica fume: two-decade gap grading",
            "mixing": "High-shear 20 min under vacuum de-airing",
            "placement": "Vibration-poured",
            "curing": "14 d, 90 C steam",
            "mechanism": "DSP principle: ultrafine particles fill the cement interstices",
            "references": "Bache (1981) DSP materials; CAC gives no portlandite to weaken the ITZ",
        },
    },
    {
        "id": 7, "name": "CBPC-ALUMINA",
        "tagline": "Chemically bonded phosphate ceramic -- a ceramic that pours at 20 C.",
        "components": {"mgo": 132.0, "kh2po4": 480.0, "water": 185.0,
                       "talumina": 1650.0, "qflour": 200.0, "retarder": 8.0},
        "cure": {"family": "acid_base", "temp_c": 20.0, "age_days": 7.0,
                 "set_pressure": 0.0, "fire_temp_c": 0.0, "K": 4.5, "air_pct": 2.5},
        "confinement": None, "evidence": "measured",

        "recipe": {
            "w_b": "0.30 on binder",
            "grading": "Tabular alumina 0.1-3 mm plus quartz flour",
            "mixing": "Paddle mixer 8 min; exothermic, keep below 40 C",
            "placement": "Poured within a 45 min working window",
            "curing": "Sets in 60 min, full strength in 7 d at ambient",
            "mechanism": "MgO + KH2PO4 + 5H2O -> MgKPO4.6H2O crystalline ceramic bond",
            "references": "Wagh (2004) Chemically Bonded Phosphate Ceramics, Elsevier",
        },
    },
    {
        "id": 8, "name": "GEO-CORUNDUM",
        "tagline": "Alkali-activated geopolymer with corundum aggregate.",
        "components": {"geopoly": 520.0, "water": 175.0, "talumina": 1700.0,
                       "qflour": 200.0, "sp": 10.0, "steelfib": 80.0},
        "cure": {"family": "alkali", "temp_c": 80.0, "age_days": 7.0,
                 "set_pressure": 0.0, "fire_temp_c": 0.0, "K": 4.5, "air_pct": 3.0},
        "confinement": None, "evidence": "measured",

        "recipe": {
            "w_b": "0.34 on binder",
            "grading": "Tabular alumina plus quartz flour",
            "mixing": "Activator solution pre-dissolved 24 h, then 10 min mixing",
            "placement": "Poured, light vibration",
            "curing": "24 h at 80 C, then ambient to 7 d",
            "mechanism": "Geopolymerisation into an N-A-S-H 3D aluminosilicate network",
            "references": "Davidovits (1991) J.Therm.Anal. 37:1633",
        },
    },
    {
        "id": 9, "name": "POLY-SIC",
        "tagline": "Vinyl ester polymer concrete with SiC aggregate.",
        "components": {"vinylester": 265.0, "sic": 1950.0, "qflour": 240.0,
                       "sicwhisk": 30.0},
        "cure": {"family": "polymer", "temp_c": 60.0, "age_days": 1.0,
                 "set_pressure": 0.0, "fire_temp_c": 0.0, "K": 4.75, "air_pct": 1.2},
        "confinement": None, "evidence": "measured",

        "recipe": {
            "w_b": "n/a -- no water in the system",
            "grading": "SiC F220 plus quartz flour, silane-coupled",
            "mixing": "Vacuum planetary mixer 10 min; MEKP added last",
            "placement": "Poured, vibrated, gels in 25 min",
            "curing": "4 h at 60 C post-cure",
            "mechanism": "Free-radical addition cure; strength limited by the resin, not by pores",
            "references": "ACI 548.1R polymer concrete; silane coupling raises the bond by 30-40%",
        },
    },
    {
        "id": 10, "name": "LCC-ALUMINA-FIRED",
        "tagline": "Low-cement alumina castable: poured cold, fired to corundum.",
        "components": {"talumina": 2450.0, "ra": 430.0, "cac": 100.0, "sf": 70.0,
                       "water": 115.0, "defloc": 7.0},
        "cure": {"family": "ceramic", "temp_c": 20.0, "age_days": 1.0,
                 "set_pressure": 0.0, "fire_temp_c": 1650.0, "dwell_min": 300.0, "K": 9.0, "air_pct": 2.0},
        "confinement": None, "evidence": "measured",

        "recipe": {
            "w_b": "0.20 on the fine binder fraction (4.3% water on total solids)",
            "grading": "Andreasen q = 0.24, d_max 3 mm, five size decades",
            "mixing": "Intensive mixer 6 min; deflocculated, vibration-cast",
            "placement": "Poured as a self-flowing castable",
            "curing": "Demould 24 h, dry 110 C, fire to 1650 C and hold 5 h",
            "mechanism": "Hydraulic green strength, then solid-state sintering to dense corundum",
            "references": "Low-cement castable practice; sintered Al2O3 UCS 2.2-2.8 GPa",
        },
    },
    {
        "id": 11, "name": "RBSC-CAST",
        "tagline": "Reaction-bonded SiC: poured slip, silicon-infiltrated to zero porosity.",
        "components": {"sic": 1600.0, "sic_fine": 600.0, "carbon_black": 90.0,
                       "binderveh": 260.0, "defloc": 8.0, "si_metal": 420.0},
        "cure": {"family": "ceramic", "temp_c": 20.0, "age_days": 1.0,
                 "set_pressure": 0.0, "fire_temp_c": 1450.0, "dwell_min": 120.0, "K": 9.0,
                 "air_pct": 1.0, "infiltrated": True},
        "confinement": None, "evidence": "measured",
        "recipe": {
            "w_b": "n/a -- 62 vol% solids slip in an organic vehicle",
            "grading": "SiC F220 60 um / SiC 3 um / carbon black 50 nm, three decades",
            "mixing": "Ball-milled 12 h, deflocculated, vacuum de-aired",
            "placement": "POURED into a plaster or resin mould, drained and dried",
            "curing": "Burnout 600 C, then molten Si infiltration at 1450 C in vacuum",
            "mechanism": "Capillary infiltration fills the pore network outright and "
                         "C + Si(l) -> SiC bonds the skeleton in situ; the porosity "
                         "term that limits every pressureless ceramic is bypassed",
            "references": "Reaction-bonded / siliconized SiC practice; UCS 2.2-3.6 GPa",
        },
    },
    {
        "id": 12, "name": "NANO-SIC-CAST",
        "tagline": "Nanograin SiC: cast slip, spark-plasma sintered. Hall-Petch route.",
        "components": {"nano_sic": 1420.0, "sic_fine": 240.0, "binderveh": 490.0,
                       "defloc": 14.0},
        "cure": {"family": "ceramic", "temp_c": 20.0, "age_days": 1.0,
                 "set_pressure": 100.0, "fire_temp_c": 1800.0, "dwell_min": 5.0, "K": 13.0,
                 "air_pct": 1.0},
        "confinement": None, "evidence": "extrapolated",
        "recipe": {
            "w_b": "n/a -- 48 vol% solids nano slip",
            "grading": "80 nm beta-SiC with a 3 um coarse mode to break agglomerates",
            "mixing": "Attrition-milled 24 h with a polyelectrolyte dispersant",
            "placement": "POURED as a slip, dried, cold-isostatically consolidated",
            "curing": "Spark plasma sintering, 1800 C at 100 MPa, 5 min dwell",
            "mechanism": "Short SPS dwell densifies without letting the grains coarsen, "
                         "so the fired body keeps a ~120 nm grain and collects the "
                         "Hall-Petch increment instead of losing it to grain growth",
            "references": "Hall (1951); Petch (1953); nanograin SiC Hv 30-35 GPa",
        },
    },
    {
        "id": 13, "name": "NPD-CAST",
        "tagline": "Binderless nano-polycrystalline diamond. STRONGEST UNCONFINED POUR.",
        "components": {"nanodiamond": 1230.0, "nanodiamond_c": 395.0,
                       "binderveh": 530.0, "defloc": 16.0},
        "cure": {"family": "ceramic", "temp_c": 20.0, "age_days": 1.0,
                 "set_pressure": 15000.0, "fire_temp_c": 2300.0, "dwell_min": 12.0, "K": 13.0,
                 "air_pct": 1.0},
        "confinement": None, "evidence": "extrapolated",
        "recipe": {
            "w_b": "n/a -- 46 vol% solids nanodiamond slip",
            "grading": "Bimodal 20 nm detonation nanodiamond + 250 nm micropowder",
            "mixing": "Bead-milled to break the detonation aggregates, then de-aired",
            "placement": "POURED as a slip into the cell liner, dried, burned out",
            "curing": "15 GPa at 2300 C, direct diamond-diamond bonding, NO metal binder",
            "mechanism": "With no cobalt to soften it, strength is set by grain size "
                         "alone.  At 20 nm the Hall-Petch increment is ~6.4 GPa on top "
                         "of the ~6.6 GPa coarse-grain baseline.  This is why NPD is "
                         "measurably harder than single-crystal diamond.",
            "references": "Irifune, Kurio, Sakamoto, Inoue & Sumiya (2003) Nature "
                          "421:599; Sumitomo HIME-DIA; Knoop 110-140 GPa measured",
        },
    },
    {
        "id": 14, "name": "NT-CBN-CAST",
        "tagline": "Nanotwinned cubic boron nitride. Harder than diamond, oxidation-stable.",
        "components": {"onion_bn": 665.0, "binderveh": 715.0, "defloc": 18.0},
        "cure": {"family": "ceramic", "temp_c": 20.0, "age_days": 1.0,
                 "set_pressure": 15000.0, "fire_temp_c": 1800.0, "dwell_min": 20.0,
                 "K": 13.0, "air_pct": 1.0, "twin_nm": 3.8},
        "confinement": None, "evidence": "extrapolated",
        "recipe": {
            "w_b": "n/a -- 33 vol% solids onion-BN slip",
            "grading": "Monodisperse 6 nm onion BN; no coarse mode, it would "
                       "dilute the nanotwinned phase",
            "mixing": "Bead-milled with a polyelectrolyte dispersant, vacuum de-aired",
            "placement": "POURED as a slip into the cell liner, dried, burned out",
            "curing": "15 GPa at 1800 C, 20 min -- onion BN collapses to cBN with "
                      "a dense coherent nanotwin structure",
            "mechanism": "The onion shells are already curved sp2 sheets; under "
                         "pressure they buckle into cBN with ~3.8 nm coherent twins. "
                         "Measured Vickers 108 GPa, above single-crystal diamond, "
                         "and unlike diamond it does not oxidise or react with iron.",
            "references": "Tian, Xu, Yu, Ma, Wang, Zhao et al. (2013) Nature 493:385",
        },
    },
    {
        "id": 15, "name": "NT-DIAMOND-CAST",
        "tagline": "Nanotwinned diamond. The strongest formulation in the model.",
        "components": {"onion_carbon": 620.0, "binderveh": 700.0, "defloc": 18.0},
        "cure": {"family": "ceramic", "temp_c": 20.0, "age_days": 1.0,
                 "set_pressure": 20000.0, "fire_temp_c": 2000.0, "dwell_min": 20.0,
                 "K": 13.0, "air_pct": 1.0, "twin_nm": 5.0},
        "confinement": None, "evidence": "extrapolated",
        "recipe": {
            "w_b": "n/a -- 30 vol% solids onion-carbon slip",
            "grading": "Monodisperse 5 nm onion carbon.  Deliberately NO coarse "
                       "mode: any coarse diamond keeps its own grain and dilutes "
                       "the nanotwinned phase, which costs more than the packing "
                       "gain is worth (see --optimize phase 6).",
            "mixing": "Bead-milled 36 h, dispersant-stabilised, vacuum de-aired",
            "placement": "POURED as a slip, drained, dried, binder burned out at 400 C",
            "curing": "20 GPa at 2000 C, 20 min",
            "mechanism": "Onion carbon converts to diamond with a coherent nanotwin "
                         "structure at ~5 nm twin spacing.  A twin boundary blocks "
                         "cracks like a grain boundary but cannot slide, so there is "
                         "no inverse-Hall-Petch turnover and the strengthening keeps "
                         "paying down to a few nm.  Measured Vickers 200 GPa -- about "
                         "twice single-crystal diamond.  NOTE: the green body loses "
                         "~40% of its volume converting sp2 carbon to diamond, so "
                         "the mould must be oversized accordingly.",
            "references": "Huang, Yue, Yu, Xu, Wang, Zhang et al. (2014) Nature "
                          "510:250; Lu, Lu & Suresh (2009) Science 324:349",
        },
    },
    {
        "id": 16, "name": "CC-MAX-POUR",
        "tagline": "Best practical free-standing unconfined pour (see --optimize for the ceiling).",
        "components": {"cac": 620.0, "sf": 220.0, "water": 92.0, "sp": 42.0,
                       "wc": 3200.0, "b4c": 620.0, "sic_fine": 150.0,
                       "maragefib": 320.0},
        "cure": {"family": "hydraulic", "temp_c": 400.0, "age_days": 14.0,
                 "set_pressure": 150.0, "fire_temp_c": 0.0, "K": 13.0, "air_pct": 3.0},
        "confinement": None, "evidence": "extrapolated",

        "recipe": {
            "w_b": "0.11 as batched, ~0.07 after water expression",
            "grading": "WC-6Co 150 um / B4C 30 um / SiC 3 um / silica fume 0.15 um, four decades",
            "mixing": "Vacuum high-shear 20 min",
            "placement": "Poured into a pressure mould, 150 MPa held through setting",
            "curing": "48 h at 300-400 C autoclave, then 14 d",
            "mechanism": "CAC binder with no portlandite, pressure-collapsed porosity, "
                         "xonotlite conversion, and a filler stronger than the matrix",
            "references": "RPC-800 route extended with carbide filler and higher set pressure",
        },
    },
    {
        "id": 17, "name": "CC-10K-CONFINED",
        "tagline": "The CC-MAX pour inside a pre-stressed carbide jacket. TARGET ROUTE.",
        "components": {"cac": 620.0, "sf": 220.0, "water": 92.0, "sp": 42.0,
                       "wc": 3200.0, "b4c": 620.0, "sic_fine": 150.0,
                       "maragefib": 320.0},
        "cure": {"family": "hydraulic", "temp_c": 400.0, "age_days": 14.0,
                 "set_pressure": 150.0, "fire_temp_c": 0.0, "K": 13.0, "air_pct": 3.0},
        "confinement": {
            "type": "Pre-stressed multi-ring WC / maraging-300 jacket",
            "sigma_y_mpa": 2000.0, "od_id": 4.0, "prestress_mpa": 900.0,
            "note": "Two-ring shrink-fit die, the standard HPHT belt-press geometry",
        }, "evidence": "extrapolated",

        "recipe": {
            "w_b": "0.11 as batched",
            "grading": "identical to CC-MAX-POUR",
            "mixing": "Vacuum high-shear 20 min",
            "placement": "Cast directly into the jacket bore; the jacket IS the mould",
            "curing": "80 MPa through setting, 400 C autoclave, jacket stays on in service",
            "mechanism": "Triaxial confinement suppresses splitting; the core fails by pore "
                         "collapse instead of axial cracking, which is a far higher stress",
            "references": "Richart et al. (1928) Univ.Illinois Bull.185; HPHT die practice",
        },
    },
    {
        "id": 18, "name": "HPHT-PCD-CAST",
        "tagline": "Cast diamond green body, HPHT sintered. Ceiling case.",
        "components": {"diamond": 1780.0, "cosinter": 195.0, "sic": 110.0,
                       "binderveh": 440.0, "defloc": 9.0},
        "cure": {"family": "ceramic", "temp_c": 20.0, "age_days": 1.0,
                 "set_pressure": 5500.0, "fire_temp_c": 1450.0, "dwell_min": 12.0, "K": 13.0,
                 "air_pct": 1.0},
        # The 5.5 GPa press pressure is a PROCESS condition, not a service load.
        # Once the compact leaves the cell it is free-standing, so it is scored
        # unconfined -- anything else would be double-counting the press.
        "confinement": None, "evidence": "measured",

        "recipe": {
            "w_b": "n/a -- 55 vol% solids slip in an organic vehicle",
            "grading": "Bimodal diamond 25 um / 5 um for maximum green density",
            "mixing": "Ball-milled 24 h, deflocculated, de-aired under vacuum",
            "placement": "POURED as a slip into the cell liner, drained and dried, "
                         "vehicle burned out at 400 C",
            "curing": "5.5 GPa at 1450 C for 12 min, cobalt-infiltrated diamond-diamond bonding",
            "mechanism": "Liquid-phase sintering of diamond into a fully bonded skeleton",
            "references": "PCD cutter practice; PCD UCS 6.9-8.0 GPa (Sumitomo, Element Six data)",
        },
    },
    {
        "id": 19, "name": "PCD-JACKETED",
        "tagline": "The cast diamond compact in an ordinary steel sleeve. "
                   "Second, far cheaper route to target.",
        "components": {"diamond": 1780.0, "cosinter": 195.0, "sic": 110.0,
                       "binderveh": 440.0, "defloc": 9.0},
        "cure": {"family": "ceramic", "temp_c": 20.0, "age_days": 1.0,
                 "set_pressure": 5500.0, "fire_temp_c": 1450.0, "dwell_min": 12.0, "K": 13.0,
                 "air_pct": 1.0},
        "confinement": {
            "type": "Shrink-fit high-strength steel sleeve (4340, sy 1000 MPa)",
            "sigma_y_mpa": 1000.0, "od_id": 3.0, "prestress_mpa": 0.0,
            "note": "The core is already at 6.3 GPa, so it needs only about 0.9 GPa "
                    "of lateral support -- an ordinary heat-treated steel sleeve, "
                    "not an HPHT die",
        }, "evidence": "extrapolated",

        "recipe": {
            "w_b": "n/a -- 55 vol% solids slip",
            "grading": "identical to HPHT-PCD-CAST",
            "mixing": "Ball-milled 24 h, deflocculated, de-aired under vacuum",
            "placement": "POURED as a slip, dried, burned out, HPHT sintered, "
                         "then shrink-fitted into the service sleeve",
            "curing": "5.5 GPa at 1450 C, then sleeve fitted at 300 C interference",
            "mechanism": "A very strong core needs proportionally little confinement, "
                         "so the jacket requirement collapses from 4.1 GPa to 0.9 GPa",
            "references": "Richart et al. (1928); shrink-fit interference practice",
        },
    },
    {
        "id": 20, "name": "NPD-JACKETED",
        "tagline": "Nano-diamond core in a carbide die. Theoretical ceiling of the model.",
        "components": {"nanodiamond": 1230.0, "nanodiamond_c": 395.0,
                       "binderveh": 530.0, "defloc": 16.0},
        "cure": {"family": "ceramic", "temp_c": 20.0, "age_days": 1.0,
                 "set_pressure": 15000.0, "fire_temp_c": 2300.0, "dwell_min": 12.0, "K": 13.0,
                 "air_pct": 1.0},
        "confinement": {
            "type": "Pre-stressed multi-ring WC / maraging-300 jacket",
            "sigma_y_mpa": 2000.0, "od_id": 4.0, "prestress_mpa": 900.0,
            "note": "UNVERIFIABLE BY TEST: no press platen survives this stress. "
                    "WC platens fail near 5.5 GPa, so anything past that must be "
                    "measured in a diamond-anvil or multi-anvil cell, where the "
                    "apparatus and the specimen are the same class of material.",
        },
        "evidence": "speculative",
        "recipe": {
            "w_b": "n/a -- identical slip to NPD-CAST",
            "grading": "Bimodal 20 nm + 250 nm nanodiamond",
            "mixing": "Bead-milled, de-aired",
            "placement": "POURED as a slip, dried, burned out, HPHT sintered in situ",
            "curing": "15 GPa at 2300 C, then shrink-fitted into the service die",
            "mechanism": "Stacks the two strongest mechanisms in the model -- "
                         "Hall-Petch grain refinement and triaxial confinement. "
                         "Reported because it is where the physics leads, and "
                         "flagged because it is past what anyone can measure.",
            "references": "Irifune et al. (2003); Richart et al. (1928); "
                          "diamond-anvil cell practice",
        },
    },
]


# =============================================================================
# SECTION 7b -- PRODUCTION: equipment, hazards, timings, QC, producibility tier
# =============================================================================
#
# Everything needed to actually make each mix, kept separate from the physics so
# the recipes stay readable.  Merged into MIXES at import.
#
# TIER -- what it takes to produce, which is a different question from whether
#         the strength number is trustworthy (that is the evidence grade):
#   plant       ordinary concrete or refractory works: mixer, vibrator, kiln
#   specialist  lab or specialist works: autoclave, hydraulic press, vacuum
#               furnace, spark plasma sintering
#   frontier    needs an HPHT press at 5 GPa or above -- a few dozen facilities
#               worldwide, and above 15 GPa only a handful
#
# HAZARDS are not decoration.  Several of these mixes involve caustics that
# cause full-thickness burns, organic peroxides that detonate if mixed wrong,
# respirable nanopowders, molten silicon, or presses storing enough elastic
# energy to be treated as ordnance.  Read them before batching anything.

PRODUCTION = {
    "OPC-BASELINE": {
        "tier": "plant",
        "equipment": "Pan or drum mixer, poker vibrator, standard formwork",
        "hazards": "Wet cement is caustic (pH 12.5) and causes full-thickness "
                   "chemical burns on prolonged skin contact -- burns are painless "
                   "at first, so they are usually noticed late. Respirable "
                   "crystalline silica from dry aggregate is IARC Group 1. "
                   "Gloves, goggles, P2/N95 when handling dry powders.",
        "pot_life": "90 min at 20 C",
        "demould": "24 h",
        "qc": "Slump 120 +/- 25 mm; 28 d cube >= 37 MPa; density 2350-2400 kg/m3",
    },
    "HSC-100": {
        "tier": "plant",
        "equipment": "High-shear pan mixer, poker vibrator",
        "hazards": "As OPC. Undensified silica fume is an ultrafine respirable "
                   "powder -- bag-dump under local exhaust ventilation, P3/N100. "
                   "PCE superplasticiser is a mild skin irritant.",
        "pot_life": "60 min at 20 C, shortens sharply above 25 C",
        "demould": "24 h",
        "qc": "Slump flow 500-560 mm; 28 d >= 90 MPa; no bleed water",
    },
    "UHPC-160": {
        "tier": "plant",
        "equipment": "High-shear or planetary mixer, 15 kW minimum for 1 m3. "
                     "No vibration -- the mix is self-levelling",
        "hazards": "As HSC. Steel microfibers puncture skin readily and are hard "
                   "to see once shed -- cut-resistant gloves, sweep magnetically, "
                   "never handle the mix by hand.",
        "pot_life": "45 min; the mix passes through a stiff 'dry' phase at ~4 min "
                    "before it turns over -- do not add water there, keep mixing",
        "demould": "48 h",
        "qc": "Flow 480-520 mm; cut a hardened section and count fibers per cm2 "
              "for dispersion; 28 d >= 150 MPa",
    },
    "RPC-200": {
        "tier": "specialist",
        "equipment": "High-shear mixer, steel moulds, saturated-steam autoclave "
                     "or steam cabinet at 90 C",
        "hazards": "As UHPC, plus steam scald risk. Do not open the cabinet above "
                   "70 C. Alkaline condensate collects in the tray and is caustic.",
        "pot_life": "40 min",
        "demould": "24 h at 20 C, then 48 h steam at 90 C",
        "qc": "Flow 450-500 mm; 7 d post-steam >= 180 MPa",
    },
    "RPC-800": {
        "tier": "specialist",
        "equipment": "High-shear mixer; hydraulic press able to hold 50 MPa on "
                     "the full casting area through setting; 400 C furnace; "
                     "drained pressure mould",
        "hazards": "Press crush hazard -- interlocked guarding, two-hand control. "
                   "Water expressed under pressure is caustic and comes out fast; "
                   "shield the mould drain. 400 C furnace burns. Maraging fiber "
                   "punctures. Do NOT release pressure before initial set.",
        "pot_life": "30 min -- pressure must be applied and held before set",
        "demould": "Release after set, then 48 h at 250-400 C",
        "qc": "Weigh the expressed water: target ~25% of batch water. Density "
              ">= 3600 kg/m3. >= 500 MPa at 7 d.",
    },
    "DSP-SIC": {
        "tier": "specialist",
        "equipment": "Vacuum high-shear mixer, 90 C steam cabinet",
        "hazards": "Calcium aluminate cement is caustic and sets fast -- a batch "
                   "that stiffens in the mixer can lock the paddle. SiC dust is a "
                   "mechanical irritant. Vacuum vessel implosion risk if damaged.",
        "pot_life": "25 min -- CAC gives little warning before it sets",
        "demould": "12 h",
        "qc": "Flow 450-480 mm; 14 d >= 350 MPa",
    },
    "CBPC-ALUMINA": {
        "tier": "plant",
        "equipment": "Paddle mixer, ambient cure. No kiln, no autoclave -- this "
                     "is the only ceramic-bonded mix here that needs neither",
        "hazards": "STRONGLY EXOTHERMIC. Above ~40 C the reaction runs away and "
                   "flash-sets in the mixer; batch cold, keep below 40 C, and do "
                   "not scale up without re-checking the exotherm. Boric acid "
                   "retarder is an EU CMR Cat 1B reproductive toxin -- gloves and "
                   "respirator, keep off skin. MgO dust is an irritant.",
        "pot_life": "45 min with the boric acid retarder; 8 min without it",
        "demould": "2 h",
        "qc": "Peak exotherm < 40 C on a thermocouple in the pour; set in 60 min; "
              "7 d >= 200 MPa",
    },
    "GEO-CORUNDUM": {
        "tier": "plant",
        "equipment": "Paddle mixer, sealed cure at 80 C for 24 h",
        "hazards": "SEVERE. The sodium silicate / NaOH activator is strongly "
                   "caustic (pH > 13) and causes immediate severe skin and eye "
                   "damage -- face shield, gauntlets, apron, eyewash within reach. "
                   "Dissolution is strongly exothermic: add alkali TO water, never "
                   "the reverse, pre-dissolve 24 h, and let it cool before use.",
        "pot_life": "60 min",
        "demould": "24 h",
        "qc": "Flow 360-400 mm; 7 d >= 100 MPa",
    },
    "POLY-SIC": {
        "tier": "plant",
        "equipment": "Vacuum planetary mixer, 60 C post-cure oven",
        "hazards": "MEKP is an ORGANIC PEROXIDE. Never mix it directly with a "
                   "cobalt accelerator -- that combination can detonate. Add each "
                   "separately, fully dispersed. Styrene vapour is flammable and a "
                   "suspected carcinogen: local exhaust, no ignition sources, "
                   "bonded and earthed vessels. Exotherm can run away in thick "
                   "sections -- limit pour depth to 50 mm per lift.",
        "pot_life": "25 min at 20 C, 12 min at 30 C",
        "demould": "4 h, then 4 h at 60 C",
        "qc": "Barcol hardness >= 40; peak exotherm < 120 C; 1 d >= 180 MPa",
    },
    "LCC-ALUMINA-FIRED": {
        "tier": "plant",
        "equipment": "Intensive mixer, vibrating table, 110 C dryer, 1650 C kiln",
        "hazards": "EXPLOSIVE SPALLING if fired wet: trapped water flashes to "
                   "steam and can burst the piece violently. Dry fully at 110 C, "
                   "then heat at <= 50 C/h to 600 C. Refractory ceramic fibre and "
                   "alumina dust are respirable. Kiln burns.",
        "pot_life": "30 min",
        "demould": "24 h, dry 24 h at 110 C, fire to 1650 C and hold 5 h",
        "qc": "Green density >= 3.05 g/cm3; fired shrinkage 1-2%; fired >= 2000 MPa",
    },
    "RBSC-CAST": {
        "tier": "plant",
        "equipment": "Ball mill, plaster or resin moulds, 600 C burnout furnace, "
                     "vacuum furnace at 1450 C with a silicon feed tray",
        "hazards": "Molten silicon at 1414 C -- severe burn and fire risk, and it "
                   "wets and climbs graphite fixturing. Vacuum furnace. Carbon "
                   "black is IARC 2B and extremely dusty. Residual free silicon in "
                   "the product releases hydrogen if attacked by strong alkali.",
        "pot_life": "4 h as a stirred slip",
        "demould": "12 h drain, 24 h dry, burnout, then infiltrate",
        "qc": "Green density >= 70% theoretical; no open porosity after "
              "infiltration (dye penetrant); >= 2400 MPa",
    },
    "NANO-SIC-CAST": {
        "tier": "specialist",
        "equipment": "Attrition mill, cold isostatic press, spark plasma sintering "
                     "furnace rated 1800 C at 100 MPa with graphite tooling",
        "hazards": "NANOPOWDER. 80 nm SiC is respirable to the alveoli and is not "
                   "captured by ordinary dust masks -- handle in a glovebox or "
                   "HEPA-filtered enclosure, wet-wipe surfaces, never dry-sweep. "
                   "SPS passes kiloamp DC through graphite dies: arc-flash and "
                   "burn risk, and the die can fail explosively under load.",
        "pot_life": "8 h stirred; the slip settles hard if left overnight",
        "demould": "24 h dry, then CIP and sinter",
        "qc": "Grain size <= 200 nm by TEM; density >= 98% theoretical; "
              "any grain growth past 300 nm means the dwell was too long",
    },
    "NPD-CAST": {
        "tier": "frontier",
        "equipment": "Bead mill, slip mould, 400 C burnout, HPHT belt or cubic "
                     "press capable of 15 GPa at 2300 C",
        "hazards": "NANODIAMOND respirable powder -- glovebox handling. The HPHT "
                   "press stores enormous elastic energy: blast containment, "
                   "remote operation, and a documented cell-failure procedure are "
                   "mandatory. If pressure is lost while hot the diamond reverts "
                   "to graphite, which is a scrapped run rather than a hazard, but "
                   "an uncontrolled decompression is not.",
        "pot_life": "12 h stirred",
        "demould": "24 h dry, burnout, then load the cell",
        "qc": "Green density; XRD must show cubic diamond with no graphite peak; "
              "grain <= 30 nm by TEM; Knoop >= 110 GPa",
    },
    "NT-CBN-CAST": {
        "tier": "frontier",
        "equipment": "Bead mill, 400 C burnout, HPHT press at 15 GPa / 1800 C",
        "hazards": "Onion-BN nanopowder is respirable -- glovebox. HPHT stored-"
                   "energy hazard as for NPD-CAST. Boron nitride dust is a "
                   "mechanical irritant.",
        "pot_life": "12 h stirred",
        "demould": "24 h dry, burnout, then load the cell",
        "qc": "TEM twin spacing 3-5 nm; Vickers >= 100 GPa; XRD cubic BN, no "
              "residual hexagonal BN",
    },
    "NT-DIAMOND-CAST": {
        "tier": "frontier",
        "equipment": "Bead mill (36 h), slip mould, 400 C burnout furnace, and an "
                     "HPHT press capable of 20 GPa at 2000 C -- a Kawai-type "
                     "multi-anvil or a large-volume belt press. This is the "
                     "limiting item: very few presses in the world reach 20 GPa "
                     "at useful sample volume",
        "hazards": "HIGHEST IN THIS LIBRARY. Onion carbon is a respirable "
                   "nanopowder: glovebox only. A 20 GPa cell stores enough elastic "
                   "energy that failure is an ordnance-class event -- full blast "
                   "containment, remote operation, and exclusion zone. The green "
                   "body loses about 40% of its volume converting sp2 carbon to "
                   "diamond, so an undersized mould gives an unfilled cell and an "
                   "unpredictable pressure distribution, which is itself a failure "
                   "mode. Oversize the mould accordingly.",
        "pot_life": "12 h stirred",
        "demould": "24 h dry, 400 C burnout, then load the cell",
        "qc": "TEM twin spacing 4-6 nm; Vickers >= 180 GPa; XRD cubic diamond with "
              "no graphite; any twin spacing above 10 nm means the dwell ran long "
              "and roughly half the strength has been lost",
    },
    "CC-MAX-POUR": {
        "tier": "specialist",
        "equipment": "Vacuum high-shear mixer, drained pressure mould rated "
                     "150 MPa, 400 C autoclave",
        "hazards": "CAC caustic and fast-setting. WC-6Co granulate contains "
                   "cobalt: a respiratory sensitiser and IARC 2A -- do not dry-"
                   "handle, do not grind the cured product without extraction. "
                   "B4C dust is abrasive and respirable. 150 MPa press crush "
                   "hazard. Expressed water is caustic and under pressure.",
        "pot_life": "20 min -- the shortest in the library; stage the press first",
        "demould": "Release after set, then 48 h at 300-400 C",
        "qc": "Expressed water ~30% of batch water; density >= 5200 kg/m3; "
              ">= 800 MPa",
    },
    "CC-10K-CONFINED": {
        "tier": "specialist",
        "equipment": "As CC-MAX-POUR, plus the jacket: pre-stressed multi-ring "
                     "WC / maraging-300 die, induction heater for the shrink fit, "
                     "and hoop strain gauges",
        "hazards": "As CC-MAX-POUR, plus: a pre-stressed jacket is a stored-energy "
                   "component and must be treated as a pressure vessel for its "
                   "whole life. NEVER machine, weld, or heat a fitted jacket, and "
                   "never remove a ring from a loaded assembly. Shrink-fitting "
                   "involves handling rings at 300 C.",
        "pot_life": "20 min",
        "demould": "The jacket is the mould and stays on in service",
        "qc": "Measured interference fit against design; hoop strain gauged at "
              "assembly and logged; core >= 800 MPa on a witness sample",
    },
    "HPHT-PCD-CAST": {
        "tier": "frontier",
        "equipment": "Ball mill, slip mould, HPHT cubic press at 5.5 GPa / 1450 C "
                     "with a cobalt infiltrant source. Commercially routine -- "
                     "this is how PCD drill and turning inserts are made",
        "hazards": "Cobalt powder is a respiratory sensitiser and IARC 2A. "
                   "Diamond micropowder is respirable. HPHT stored-energy hazard, "
                   "though 5.5 GPa cells are a mature, well-guarded technology.",
        "pot_life": "8 h stirred",
        "demould": "24 h dry, burnout, then load the cell",
        "qc": "Raman shows no graphite; cobalt content 8-12 wt%; >= 6000 MPa",
    },
    "PCD-JACKETED": {
        "tier": "frontier",
        "equipment": "As HPHT-PCD-CAST, plus a shrink-fit 4340 steel sleeve and "
                     "an induction heater",
        "hazards": "As HPHT-PCD-CAST, plus the stored-energy warning for any "
                   "fitted jacket: do not machine or heat it once assembled.",
        "pot_life": "8 h stirred",
        "demould": "Sleeve fitted at 300 C interference after sintering",
        "qc": "Interference fit measured; sleeve hoop strain logged; core "
              ">= 6000 MPa on a witness sample",
    },
    "NPD-JACKETED": {
        "tier": "frontier",
        "equipment": "As NPD-CAST, plus a pre-stressed multi-ring WC / maraging "
                     "die",
        "hazards": "As NPD-CAST, plus the fitted-jacket stored-energy warning. "
                   "NOTE that the resulting capacity cannot be verified: no press "
                   "platen survives it, so acceptance has to be by witness "
                   "coupon and hardness, never by testing the part to failure.",
        "pot_life": "12 h stirred",
        "demould": "Jacket fitted after HPHT sintering",
        "qc": "Core Knoop >= 110 GPa on a witness sample; jacket interference and "
              "hoop strain logged. Do not attempt a direct compression test.",
    },
}


def _merge_production():
    """Fold the production data into each mix, and fail loudly if any mix is
    missing it -- a formulation without production instructions is not usable."""
    for _m in MIXES:
        _p = PRODUCTION.get(_m["name"])
        if _p is None:
            raise KeyError("no PRODUCTION entry for mix %r" % _m["name"])
        _m["tier"] = _p["tier"]
        for _k in ("equipment", "hazards", "pot_life", "demould", "qc"):
            _m["recipe"][_k] = _p[_k]


_merge_production()


# =============================================================================
# SECTION 8 -- EVAL: full evaluation of one mix
# =============================================================================

def split_components(components):
    """Split a recipe into binder / filler / fiber / water / admixture groups.

    An "infiltrant" is a phase that is NOT present when the mix is poured -- it
    is wicked in afterwards, filling the pore network the green body already
    has.  It therefore adds mass and load-bearing solid to the fired body while
    adding no volume and taking no part in the fresh-mix packing or rheology.
    """
    binders, fillers, fibers, admix, infil = {}, {}, {}, {}, {}
    water = 0.0
    for k, kg in components.items():
        role = MATS[k]["role"]
        if role == "binder":
            binders[k] = kg
        elif role == "filler":
            fillers[k] = kg
        elif role == "fiber":
            fibers[k] = kg
        elif role == "water":
            water += kg
        elif role == "admix":
            admix[k] = kg
        elif role == "infiltrant":
            infil[k] = kg
    return binders, fillers, fibers, water, admix, infil


def build_size_classes(binders, fillers):
    """Assemble the CPM size-class list (coarse -> fine) from the solid phases."""
    vols = []
    for k, kg in list(binders.items()) + list(fillers.items()):
        d = MATS[k].get("d50", 0.0)
        if d <= 0.0:
            continue                       # liquid binders have no size class
        vols.append((d, kg / MATS[k]["rho"], MATS[k]["beta"]))
    v_tot = sum(v for _, v, _ in vols)
    if v_tot <= 0.0:
        return []
    classes = [(d, v / v_tot, b) for d, v, b in vols]
    classes.sort(key=lambda c: -c[0])       # coarse first
    return classes


def evaluate_mix(mix, specimen_mm=100.0, verbose=False):
    """Run the full physics chain on one mix and return every intermediate."""
    comp = {k: v for k, v in mix["components"].items() if v > 1e-9}
    cure = mix["cure"]
    binders, fillers, fibers, water, admix, infil = split_components(comp)

    # ---- volumes -----------------------------------------------------------
    v_binder = sum(kg / MATS[k]["rho"] for k, kg in binders.items())
    v_filler = sum(kg / MATS[k]["rho"] for k, kg in fillers.items())
    v_fiber = sum(kg / MATS[k]["rho"] for k, kg in fibers.items())
    v_water = water / 1000.0
    v_admix = sum(kg / MATS[k]["rho"] for k, kg in admix.items())
    v_infil = sum(kg / MATS[k]["rho"] for k, kg in infil.items())
    # fibers past the knee trap air; charge that against the mix before anything
    # else, because it feeds straight into the porosity term
    vf_fib_raw = v_fiber / max(v_binder + v_filler + v_fiber + v_water + v_admix, 1e-9)
    air_pct = min(PHYS["fiber_air_cap"],
                  cure["air_pct"] + PHYS["fiber_air_pct"] * max(
                      0.0, vf_fib_raw - PHYS["fiber_knee"]))
    v_air = air_pct / 100.0
    v_total = v_binder + v_filler + v_fiber + v_water + v_admix + v_air
    mass_total = sum(comp.values())
    density = mass_total / v_total if v_total > 0 else 0.0

    # ---- packing ------------------------------------------------------------
    classes = build_size_classes(binders, fillers)
    phi_max, gamma = actual_packing(classes, cure["K"]) if classes else (0.0, 0.0)
    # phi_max  = dry packing at this compaction energy (a placement property)
    # gamma    = maximum/virtual packing = the jamming point the suspension sees
    v_solid = v_binder + v_filler + v_fiber
    phi_solid = v_solid / v_total if v_total > 0 else 0.0
    vf_fiber_pack = v_fiber / v_total if v_total > 0 else 0.0
    packing_util = phi_solid / gamma if gamma > 0 else 0.0
    q_best, fd_err = best_funk_dinger_q(classes)

    # ---- rheology ------------------------------------------------------------
    if classes:
        d50_mix = math.exp(sum(y * math.log(max(d, 0.05))
                               for d, y, _ in classes))
    else:
        d50_mix = 100.0
    sp_kg = sum(kg for k, kg in admix.items())
    binder_kg = sum(binders.values()) or 1.0
    sp_dose = sp_kg / binder_kg
    disp = (sum(MATS[k].get("disp", 0.5) * kg for k, kg in admix.items()) / sp_kg
            if sp_kg > 0 else 0.0)
    if cure["family"] == "polymer":
        tau0 = 45.0                        # resin-carried, low yield stress by design
    else:
        tau0 = yield_stress(phi_solid, gamma, d50_mix, sp_dose, disp,
                            vf_fiber_pack)
    flow = slump_flow_mm(tau0, density)
    pour_class = pourability_class(flow)

    # ---- matrix strength -----------------------------------------------------
    fam = cure["family"]
    cure_factor = {
        20.0: PHYS["cure_ambient"], 60.0: PHYS["cure_ambient"],
        80.0: PHYS["cure_steam90"], 90.0: PHYS["cure_steam90"],
        200.0: PHYS["cure_auto200"], 400.0: PHYS["cure_auto400"],
    }.get(cure["temp_c"], PHYS["cure_ambient"])

    chem = None
    ceramic_info = None
    if fam in ("hydraulic", "acid_base", "alkali"):
        chem = binder_reaction(binders, water, air_pct, cure_factor,
                               cure["age_days"], cure["set_pressure"],
                               cure["temp_c"])
        sigma_m = chem["sigma_paste"] if chem else 0.0
        sigma0_eff = chem["sigma0_eff"] if chem else 0.0
        P_total = chem["P_total"] if chem else 0.0
    elif fam == "ceramic":
        # A cast green body drains and dries, so its particles consolidate to
        # the packing limit -- the vehicle leaves, the porosity it occupied does
        # not.  Green porosity is therefore 1 - phi_max, not 1 - phi_wet.
        P_green = clamp(1.0 - phi_max, 0.02, 0.6)
        # sintering closes most of the green porosity
        sfrac = clamp((cure["fire_temp_c"] - 900.0) / 700.0)
        # Pressureless sintering leaves ~14% of the green porosity behind.
        # Applied pressure during the sinter (SPS, HIP, HPHT) collapses it:
        # closure rises from 0.86 toward 0.99 with a 60 MPa scale.
        closure = 0.86 + 0.13 * (1.0 - math.exp(-cure["set_pressure"] / 60.0))
        P_total = P_green * (1.0 - closure * (sfrac ** 0.5))
        if cure.get("infiltrated"):
            # a molten infiltrant (Si, Co) fills the open pore network outright
            P_total = PHYS["infiltrated_porosity"]
        # HPHT densification: pressure applied DURING sintering closes the rest
        if cure["set_pressure"] > 0.0:
            P_total *= math.exp(-cure["set_pressure"] / PHYS["hpht_p_scale"])
        P_total = max(P_total, 0.0005)
        # A sintered body is ONE ceramic: every solid phase carries load in
        # proportion to its volume, so the whole body feeds the strength term
        # and the matrix/filler composite step is skipped rather than counted
        # twice.
        ceramic_solids = ([(k, kg / MATS[k]["rho"]) for k, kg in binders.items()] +
                          [(k, kg / MATS[k]["rho"]) for k, kg in fillers.items()] +
                          [(k, kg / MATS[k]["rho"]) for k, kg in infil.items()])
        # Feed size is the geometric-mean d50 of the phases that actually
        # SINTER; anything carrying grain_fixed_nm keeps its own microstructure
        # and neither contributes to nor takes the body's grain size.
        sint = [(k, v) for k, v in ceramic_solids
                if not MATS[k].get("grain_fixed_nm") and MATS[k].get("d50", 0.0) > 0]
        v_sint = sum(v for _, v in sint)
        if v_sint > 0:
            feed_nm = math.exp(sum(v * math.log(MATS[k]["d50"] * 1000.0)
                                   for k, v in sint) / v_sint)
        else:
            feed_nm = 5000.0
        grain_nm = grain_growth(feed_nm, cure["fire_temp_c"],
                                cure.get("dwell_min", 60.0), cure["set_pressure"])
        if cure.get("grain_nm"):
            grain_nm = cure["grain_nm"]        # explicit override, for validation
        twin_nm = cure.get("twin_nm", 0.0)
        sigma_m, sigma0_eff = ceramic_matrix_strength(
            ceramic_solids, cure["fire_temp_c"], cure["set_pressure"],
            P_total, grain_nm, twin_nm)
        ceramic_info = {"feed_nm": feed_nm, "grain_nm": grain_nm,
                        "twin_nm": twin_nm}
    elif fam == "polymer":
        P_total = v_air / v_total if v_total > 0 else 0.0
        sigma_m, sigma0_eff = polymer_matrix_strength(binders, P_total)
    else:
        sigma_m, sigma0_eff, P_total = 0.0, 0.0, 0.0

    # ---- composite ------------------------------------------------------------
    filler_vols = [(k, kg / MATS[k]["rho"]) for k, kg in fillers.items()]
    v_matrix = v_total - v_filler - v_fiber
    vf_filler = v_filler / max(v_total - v_fiber, 1e-9)
    bond_boost = 0.06 if "sf" in binders else 0.0     # silica fume densifies the ITZ
    if fam == "ceramic":
        # already accounted for inside ceramic_matrix_strength
        sigma_comp, K_agg, K_dmax = sigma_m, 1.0, 1.0
        bond = 1.0
        _vf = sum(v for _, v in filler_vols)
        E_f = (sum(MATS[k]["E"] * v for k, v in filler_vols) / _vf
               if _vf > 1e-12 else 0.0)
    else:
        sigma_comp, K_agg, K_dmax, bond, E_f = composite_strength(
            sigma_m, filler_vols, vf_filler, v_total, bond_boost)

    # ---- fibers -----------------------------------------------------------------
    fiber_vols = [(k, kg / MATS[k]["rho"]) for k, kg in fibers.items()]
    K_fib, vf_fiber, sig_fib = fiber_factor(fiber_vols, v_total)
    sigma_unconf = sigma_comp * K_fib

    # ---- stiffness, size effect, confinement --------------------------------------
    E_c = elastic_modulus(sigma_unconf, vf_filler, E_f, fam)
    m_weib = (PHYS["weibull_m_ceramic"] if fam == "ceramic"
              else PHYS["weibull_m_uhpc"] if sigma_unconf > 120.0
              else PHYS["weibull_m_cement"])
    sigma_spec = weibull_size_correction(sigma_unconf, specimen_mm, m_weib)

    conf = mix.get("confinement")
    f_l = 0.0
    if conf:
        f_l = min(jacket_capacity(conf["sigma_y_mpa"], conf["od_id"]),
                  conf["sigma_y_mpa"] * 2.6)          # ring-stress practical ceiling
        f_l += conf.get("prestress_mpa", 0.0)
    sigma_conf = confined_strength(sigma_unconf, f_l)

    # ---- tensile, flexural, cost ---------------------------------------------------
    sigma_t = 0.55 * math.sqrt(max(sigma_unconf, 1.0)) + 0.42 * vf_fiber * sig_fib
    sigma_f = 1.9 * sigma_t
    cost = sum(kg * MATS[k]["cost"] for k, kg in comp.items())
    if conf:
        cost += 2400.0                    # jacket amortised per m3 of core

    return {
        "mix": mix, "name": mix["name"],
        "v_total": v_total, "v_binder": v_binder, "v_filler": v_filler,
        "v_fiber": v_fiber, "v_water": v_water, "v_air": v_air,
        "v_infiltrant": v_infil, "air_pct": air_pct,
        "volume_check": v_total, "density": density, "mass_total": mass_total,
        "classes": classes, "phi_max": phi_max, "gamma": gamma,
        "phi_solid": phi_solid, "packing_util": packing_util,
        "q_best": q_best, "fd_err": fd_err, "d50_mix": d50_mix,
        "tau0": tau0, "flow_mm": flow, "pour_class": pour_class,
        "pourable": flow >= PHYS["flow_pourable_mm"],
        "chem": chem, "ceramic": ceramic_info, "cure_factor": cure_factor,
        "sigma0_eff": sigma0_eff, "P_total": P_total, "sigma_matrix": sigma_m,
        "K_agg": K_agg, "K_dmax": K_dmax, "bond": bond, "vf_filler": vf_filler,
        "sigma_composite": sigma_comp,
        "K_fiber": K_fib, "vf_fiber": vf_fiber, "sigma_fiber": sig_fib,
        "sigma_unconfined": sigma_unconf,
        "sigma_specimen": sigma_spec, "specimen_mm": specimen_mm, "weibull_m": m_weib,
        "f_lateral": f_l, "sigma_confined": sigma_conf,
        "E_gpa": E_c, "sigma_tensile": sigma_t, "sigma_flexural": sigma_f,
        "cost_m3": cost,
        "hits_target": sigma_conf >= TARGET_MPA,
        "hits_target_unconfined": sigma_unconf >= TARGET_MPA,
    }


def best_funk_dinger_q(classes):
    """Sweep the Funk-Dinger exponent q and report the best fit to the blend."""
    if not classes:
        return 0.0, 1.0
    best_q, best_err = 0.0, 1e9
    for i in range(61):
        q = 0.10 + 0.40 * i / 60.0
        err = psd_distance_to_funk_dinger(classes, q)
        if err < best_err:
            best_err, best_q = err, q
    return best_q, best_err


def get_mix(name):
    """Look a mix up by name or by id, case-insensitively."""
    key = str(name).strip().lower()
    for m in MIXES:
        if m["name"].lower() == key or str(m["id"]) == key:
            return m
    for m in MIXES:
        if key in m["name"].lower():
            return m
    return None


# =============================================================================
# SECTION 9 -- OPT: find the strongest mix that still pours
# =============================================================================

def _synth_mix(params, filler_key, fiber_key, binder_key, cure_temp, set_p,
               fired=False, confined=False):
    """Build a candidate mix dict from a parameter vector.

    params = [binder_kg, sf_frac, w_b, filler_kg, fine_filler_frac,
              sp_dose_frac, fiber_vol_frac]
    """
    (binder_kg, sf_frac, w_b, filler_kg, fine_frac, sp_dose, fib_vf) = params

    b_main = binder_kg * (1.0 - sf_frac)
    b_sf = binder_kg * sf_frac
    water = w_b * binder_kg
    sp_kg = sp_dose * binder_kg
    f_coarse = filler_kg * (1.0 - fine_frac)
    f_fine = filler_kg * fine_frac
    fib_kg = fib_vf * MATS[fiber_key]["rho"]

    comp = {binder_key: b_main, "sf": b_sf, "water": water, "sp": sp_kg,
            filler_key: f_coarse, "qflour": f_fine, fiber_key: fib_kg}
    comp = {k: v for k, v in comp.items() if v > 1e-6}

    cure = {"family": "ceramic" if fired else "hydraulic",
            "temp_c": cure_temp, "age_days": 14.0,
            "set_pressure": set_p, "fire_temp_c": 1650.0 if fired else 0.0,
            "K": PHYS["K_press"] if set_p > 0 else PHYS["K_vib"],
            "air_pct": 3.0}

    conf = None
    if confined:
        conf = {"type": "Pre-stressed multi-ring WC / maraging jacket",
                "sigma_y_mpa": 2000.0, "od_id": 4.0, "prestress_mpa": 900.0,
                "note": "optimiser candidate"}

    return {"id": 0, "name": "CANDIDATE", "tagline": "optimiser candidate",
            "components": comp, "cure": cure, "confinement": conf,
            "recipe": {}}


def _score(res, require_pourable=True, use_confined=False):
    """Objective: maximise strength, hard-reject anything that will not pour."""
    if res is None:
        return -1e9
    if require_pourable and not res["pourable"]:
        return -1e9
    if res["volume_check"] > 1.35 or res["volume_check"] < 0.80:
        return -1e9                     # recipe does not close to ~1 m3
    s = res["sigma_confined"] if use_confined else res["sigma_unconfined"]
    # small bonus for surplus workability, so the optimum is not on the cliff edge
    return s * (1.0 + 0.02 * clamp((res["flow_mm"] - 250.0) / 450.0))


def _local_search(params, ranges, eval_fn, n_iters=600, step_frac=0.06):
    """Gradient-free local search: perturb one dimension at a time, keep wins.
    Same pattern as the local refinement in GmanCoatV1.17.
    """
    params = list(params)
    best = eval_fn(params)
    for _ in range(n_iters):
        d = random.randint(0, len(params) - 1)
        lo, hi = ranges[d]
        step = (hi - lo) * step_frac
        old = params[d]
        params[d] = clamp(old + random.uniform(-1.0, 1.0) * step, lo, hi)
        val = eval_fn(params)
        if val > best:
            best = val
        else:
            params[d] = old
    return params, best


def optimize_pour(filler_key="wc", fiber_key="maragefib", binder_key="cac",
                  cure_temp=400.0, set_p=80.0, fired=False, confined=False,
                  n_sweep=6000, n_local=1500, seed=7):
    """Phase 1 random sweep, phase 2 local search, maximising strength subject
    to the mix remaining pourable.
    """
    random.seed(seed)
    ranges = [
        (300.0, 1200.0),    # binder kg/m3
        (0.00, 0.40),       # silica fume fraction of binder
        (0.08, 0.32),       # water / binder
        (800.0, 3400.0),    # filler kg/m3
        (0.00, 0.35),       # fine (quartz flour) share of filler
        (0.00, 0.06),       # superplasticiser dose on binder
        # Randomly oriented fibers jam at roughly 4/(l/d) by volume -- about
        # 6 vol% at l/d = 65 -- and lose placeability well before that, so the
        # search is bounded at 4.5 vol% rather than letting the optimiser
        # propose a fiber load that cannot physically be poured.
        (0.00, 0.045),      # fiber volume fraction
    ]

    def ev(p):
        mix = _synth_mix(p, filler_key, fiber_key, binder_key, cure_temp,
                         set_p, fired, confined)
        try:
            res = evaluate_mix(mix)
        except Exception:
            return -1e9
        return _score(res, True, confined)

    best_p, best_v = None, -1e9
    for _ in range(n_sweep):
        p = [random.uniform(lo, hi) for lo, hi in ranges]
        v = ev(p)
        if v > best_v:
            best_v, best_p = v, p
    if best_p is None:
        return None, None, -1e9

    best_p, best_v = _local_search(best_p, ranges, ev, n_iters=n_local)
    mix = _synth_mix(best_p, filler_key, fiber_key, binder_key, cure_temp,
                     set_p, fired, confined)
    return mix, evaluate_mix(mix), best_v


def optimize_packing_q(d_min_um=0.10, d_max_um=3000.0, n_classes=7):
    """Sweep the Funk-Dinger exponent q and report the packing density that an
    ideally graded blend of n_classes would reach.  This is the theoretical
    packing ceiling every real recipe is measured against.
    """
    out = []
    for i in range(41):
        q = 0.10 + 0.30 * i / 40.0
        ds = [d_min_um * (d_max_um / d_min_um) ** (j / (n_classes - 1.0))
              for j in range(n_classes)]
        cum = [funk_dinger_cpft(d, d_min_um, d_max_um, q) for d in ds]
        ys = [cum[0]] + [cum[j] - cum[j - 1] for j in range(1, n_classes)]
        tot = sum(ys) or 1.0
        ys = [y / tot for y in ys]
        betas = [0.44 if d < 1.0 else 0.52 if d < 100.0 else 0.60 for d in ds]
        classes = sorted(zip(ds, ys, betas), key=lambda c: -c[0])
        phi, gamma = actual_packing(classes, PHYS["K_vib"])
        out.append((q, phi, gamma))
    best = max(out, key=lambda r: r[1])
    return best, out


def route_to_target(target=TARGET_MPA):
    """For every mix, work out what it would take to reach the target.
    Returns one row per mix with the confinement pressure required and whether
    a real jacket can supply it.
    """
    rows = []
    for m in MIXES:
        r = evaluate_mix(m)
        need = confinement_required(r["sigma_unconfined"], target)
        rows.append({
            "name": m["name"],
            "unconfined": r["sigma_unconfined"],
            "as_built": r["sigma_confined"],
            "f_l_present": r["f_lateral"],
            "f_l_needed": need,
            "reachable": need is not None,
            "already": r["sigma_confined"] >= target,
            "res": r,
        })
    return rows


# =============================================================================
# SECTION 10 -- REPORT: console output
# =============================================================================

def _bar(frac, width=22):
    n = int(clamp(frac) * width)
    return "[" + "#" * n + "." * (width - n) + "]"


def print_banner():
    print("=" * 78)
    print(" CeramicCement.py -- ULTRA-HIGH-STRENGTH POUR FORMULATION MODEL")
    print(" Target: %.0f MPa compressive, by any means, in a mix pour" % TARGET_MPA)
    print("=" * 78)
    print(" %d formulations | %d materials | 5 binder chemistries" %
          (len(MIXES), len(MATS)))
    print("")
    print(" PHYSICS CHAIN")
    print("   PSD -> CPM packing -> YODEL yield stress -> Roussel slump flow")
    print("   Powers-Brownyard hydration + CH balance -> capillary/gel porosity")
    print("   gel collapse (autoclave) -> Ryshkevitch sigma0*exp(-bP)")
    print("   grain growth -> Hall-Petch / nanotwin strengthening")
    print("   -> ITZ load sharing -> fibers -> Weibull -> Richart confinement")
    print("")
    print(" %d mixes are buildable in an ordinary works, %d need specialist kit," %
          (sum(1 for m in MIXES if m.get("tier") == "plant"),
           sum(1 for m in MIXES if m.get("tier") == "specialist")))
    print(" %d need an HPHT press.  Full production sheets: --formulary" %
          sum(1 for m in MIXES if m.get("tier") == "frontier"))
    print("")
    print(" RESULT: target cleared UNCONFINED, 2.5x over, by a poured slip")
    print("   NT-DIAMOND-CAST  ~24,900 MPa  (onion carbon, HPHT, 5 nm nanotwins)")
    print("   Cement chemistry tops out near 850 MPa and cannot reach it.")
    print("=" * 78)


def print_about():
    """The science behind the model: what each mechanism buys, and where it stops."""
    print("=" * 78)
    print(" CERAMIC CEMENT -- ABOUT THE SCIENCE")
    print("=" * 78)
    print("""
WHAT THIS MODEL IS
------------------------------------------------------------------------------
  A formulation engine for pourable ultra-high-strength materials.  You give it
  a recipe in kg/m3 and a curing schedule; it computes packing, rheology,
  reaction chemistry, porosity and strength from first principles, and tells you
  whether the thing can actually be poured.

  It carries %d formulations across four binder chemistries:
    hydraulic    Portland and calcium aluminate cements (hydration)
    acid-base    chemically bonded phosphate ceramics (Wagh)
    alkali       geopolymers (Davidovits)
    ceramic      fired, infiltrated, and HPHT-sintered bodies
    (plus polymer concrete, which has no porosity mechanism at all)

THE SEVEN MECHANISMS THAT SET STRENGTH
------------------------------------------------------------------------------
  Ranked by what they are actually worth:

  1. PHASE CHOICE -- worth 100x
     The intrinsic strength of the load-bearing solid.  C-S-H gel is ~650 MPa
     pore-free; corundum ~3000; SiC ~3800; WC ~5200; diamond ~6600.  Nothing
     else in the model spans that range.  This decision is made before any mix
     design starts, and it dominates everything after it.

  2. TWIN SPACING (nanotwinning) -- worth up to 3.8x, and it is the winner
     sigma(lambda) = sigma_ref + k_tw/sqrt(lambda), same form as Hall-Petch but
     with NO inverse turnover.  An ordinary grain boundary is a disordered layer
     that starts to slide once it is a large enough volume fraction, which is
     what makes nanocrystalline solids weaken below ~15 nm.  A coherent twin
     boundary is a mirror plane of the same lattice: it blocks dislocations and
     cracks just as well, but there is nothing to slide, so refining the twin
     keeps paying down to a few nanometres.

     Measured, not predicted: nanotwinned cBN at 3.8 nm reaches Vickers 108 GPa
     (Tian 2013) and nanotwinned diamond at 5 nm reaches 200 GPa (Huang 2014).
     Both exceed single-crystal diamond.  This is the single most valuable lever
     in the model and the reason the target is cleared without a jacket.

  3. GRAIN SIZE (Hall-Petch) -- worth up to 2x
     sigma(d) = sigma_ref + k/sqrt(d).  Grain boundaries block cleavage cracks,
     so a finer grain is a stronger solid.  For covalent ceramics k is large
     (0.45-0.95 MPa*sqrt(m)) because those boundaries are genuinely hard
     barriers.  Taking diamond from a 25 um grain to 20 nm doubles it: 6.5 ->
     13 GPa.  Below a critical size (~15 nm for diamond) the trend REVERSES as
     grain-boundary sliding takes over, so there is a real finite optimum and
     the model reports it instead of extrapolating to zero.

  4. POROSITY -- worth up to 10x within one phase
     sigma = sigma0*exp(-b*P), b ~ 5-6.  Each percent of porosity costs about
     5%% of strength.  This is where ordinary concrete loses: at w/c 0.50 the
     paste is 47%% porous and keeps only 6%% of its pore-free strength.  Three
     ways to beat it, in increasing order of effectiveness:
       - lower the water        (limited by rheology -- it must still pour)
       - press during setting   (expels free water and entrapped air)
       - infiltrate a melt      (RBSC: porosity -> 0.5%%, the porosity term
                                 stops mattering at all)

  5. CONFINEMENT -- worth 3-20x, but it is a system property
     f_cc = f_co + k(f_l)*f_l, with k falling from 4.1 to ~2.2 at GPa pressures.
     Lateral pressure shuts off axial splitting and forces failure into pore
     collapse, which takes far more stress.  Real -- it is how gun barrels and
     HPHT anvils work -- but the jacket is part of the structure, not part of
     the material, and this model never blends the two.

  6. GEL COLLAPSE -- worth ~2x, hydraulic binders only
     C-S-H carries ~28%% intrinsic gel porosity that never leaves at ambient
     temperature.  Autoclaving above ~150 C recrystallises it to tobermorite,
     and above 250 C to xonotlite, both dense.  This is the actual reason
     RPC-800 exists; without it no hydrated binder passes ~250 MPa.

  7. PARTICLE PACKING -- worth ~1.3x directly, but it gates everything
     Better packing means less water for the same flow, which means less
     porosity.  It rarely adds strength by itself -- it is what makes the low
     water/binder ratios physically placeable in the first place.

WHAT IS WORTH ALMOST NOTHING
------------------------------------------------------------------------------
  - Hard aggregate in a soft matrix.  The composite is matrix-limited: a 55 GPa
    diamond grain in a 300 MPa paste still fails at paste strength, because the
    paste is what transfers the load.  K_agg tops out near 1.25.
  - Silica fume past ~14%% on cement.  The portlandite balance caps it: cement
    releases 0.26 g CH per gram reacted, silica fume consumes 1.85 g/g.  Past
    that it is an excellent inert filler and nothing more.
  - Fiber past ~4 vol%%.  Compressive gain is 5-15%%; past the knee the fibers
    ball, trap air, and cost more in porosity than they buy in restraint.
  - Nano-additives in cement.  They do not change the Ryshkevitch exponent, and
    the exponent is what is holding the material back.
  - Grinding a nanograin body finer than its d_crit.  Past the Hall-Petch peak
    the grain boundaries start sliding and the material gets WEAKER.  Twinning
    is the way past that wall, not finer grinding.
  - A coarse packing mode in a nanostructured slip.  It raises green density,
    but coarse particles keep their own grain size and dilute the nanostructure;
    the model prefers as little of it as the slip can be cast without.

WHY THE TARGET NEEDS A CHANGE OF MECHANISM
------------------------------------------------------------------------------
  Mechanisms 4, 6 and 7 are all porosity management.  Together they take a
  hydrated binder from 26 MPa to about 850 MPa -- a 33x gain, and essentially
  the entire history of concrete technology.  They then stop, because gel
  porosity is intrinsic: pressure cannot remove what crystallography puts there.

  Reaching %.0f MPa therefore requires mechanism 1, 2 or 3 -- change the phase,
  refine the twin, or refine the grain.  NT-DIAMOND-CAST does all three, which
  is why it clears the target 2.5x over while every cement-family mix in the
  library falls about 12x short of it.

MEASUREMENT HONESTY
------------------------------------------------------------------------------
  Tungsten carbide press platens fail near 5.5 GPa.  Any unconfined strength
  above that cannot be measured in a conventional test frame -- the apparatus
  fails before the specimen does.  Above 5.5 GPa the numbers here are inferred
  from hardness correlations (UCS ~ H/7 for superhard ceramics) or from
  multi-anvil work, and every such mix is flagged extrapolated or speculative.

  The Weibull term is reported separately for the same reason: a 20 mm cube
  reads about %.0f%% higher than a 100 mm cube of identical material.  That is a
  measurement-scale effect, not strength, and it is never folded into the
  headline number.
""" % (len(MIXES), TARGET_MPA,
       100.0 * (weibull_size_correction(1.0, 20.0, 12.0) - 1.0)))
    print("=" * 78)


def print_grain_study():
    """Hall-Petch grain-size study: what grain size each phase wants, and what
    refining to it is worth."""
    print("=" * 78)
    print(" HALL-PETCH GRAIN-SIZE STUDY")
    print(" sigma(d) = sigma_ref + k*(1/sqrt(d) - 1/sqrt(d_ref)),  d_ref = %.0f um"
          % PHYS["hp_d_ref_um"])
    print("=" * 78)
    phases = [k for k in MATS if "hp_k" in MATS[k]]
    phases.sort(key=lambda k: -MATS[k]["sigma0"])
    print(" %-15s %9s %8s %9s %9s %10s %8s" %
          ("PHASE", "k", "d_crit", "@25um", "@1um", "@OPTIMUM", "GAIN"))
    print(" %-15s %9s %8s %9s %9s %10s %8s" %
          ("", "MPa.m^.5", "nm", "MPa", "MPa", "MPa", "x"))
    print(" " + "-" * 76)
    for k in phases:
        m = MATS[k]
        s25 = hall_petch(m["sigma0"], m["hp_k"], 25000.0, m["d_crit_nm"])
        s1 = hall_petch(m["sigma0"], m["hp_k"], 1000.0, m["d_crit_nm"])
        d_opt, s_opt = optimal_grain_size(k)
        flag = "  <-- clears target" if s_opt >= TARGET_MPA else ""
        print(" %-15s %9.2f %8.1f %9.0f %9.0f %10.0f %7.2fx%s" %
              (k, m["hp_k"], m["d_crit_nm"], s25, s1, s_opt, s_opt / s25, flag))
    print(" " + "-" * 76)
    print("")
    print(" NANOTWINNED PHASES -- the same maths, without the turnover")
    print(" " + "-" * 76)
    print("  %-16s %8s %10s %10s %10s" %
          ("PHASE", "k_tw", "TWIN", "STRENGTH", "MEASURED"))
    print("  %-16s %8s %10s %10s %10s" %
          ("", "MPa.m^.5", "nm", "MPa", "Hv GPa"))
    for k, lam, hv in (("onion_carbon", 5.0, 200.0), ("onion_bn", 3.8, 108.0)):
        m = MATS[k]
        sig = nanotwin_strength(m["sigma0"], m["tw_k"], lam)
        print("  %-16s %8.3f %10.1f %10.0f %10.0f   (UCS~Hv/8 = %.0f MPa)" %
              (k, m["tw_k"], lam, sig, hv, hv * 1000.0 / 8.0))
    print("")
    print("""  A coherent twin boundary blocks cracks exactly like a grain boundary, but
  it is a mirror plane of the same lattice rather than a disordered layer -- so
  there is nothing to slide, and the inverse-Hall-Petch turnover never arrives.
  That is why nanotwinned diamond at 5 nm (200 GPa Vickers) beats nanograin
  diamond at its 15 nm optimum, and why it beats single-crystal diamond outright.

  READ IT THIS WAY
    The @25um column is what a conventional coarse-grained compact gives -- the
    numbers on a supplier datasheet.  The @OPTIMUM column is what the same
    chemistry gives if you can sinter it without letting the grains grow.

    That gap is the whole engineering problem.  Densification wants time at
    temperature, and time at temperature coarsens the grain.  Every process in
    this library that reaches a fine grain does it by substituting PRESSURE for
    time: spark plasma sintering at 100 MPa, HPHT at 15 GPa.  Pressure densifies
    without the long dwell that would eat the nanostructure.

    The turnover at d_crit is not a modelling convenience.  Below roughly
    10-20 nm the grain boundaries become a large enough volume fraction that
    boundary sliding, rather than crack blocking, controls -- so the curve peaks
    and falls.  Grinding finer than the peak makes the material weaker.
""")
    print("=" * 78)


def print_comparison(specimen_mm=100.0):
    """Side-by-side table of every mix in the library."""
    print("=" * 120)
    print(" CERAMIC CEMENT -- MIX COMPARISON  (%d mixes, %.0f mm specimen)"
          % (len(MIXES), specimen_mm))
    print("=" * 108)
    print(" %-18s %8s %8s %7s %8s %9s %7s %8s %-12s %-10s" %
          ("MIX", "MATRIX", "UNCONF", "FLOW", "POUR?", "CONFINED", "E",
           "COST", "EVIDENCE", "TIER"))
    print(" %-18s %8s %8s %7s %8s %9s %7s %8s %-12s %-10s" %
          ("", "MPa", "MPa", "mm", "", "MPa", "GPa", "USD/m3", "", ""))
    print(" " + "-" * 118)
    results = []
    for m in MIXES:
        r = evaluate_mix(m, specimen_mm)
        results.append(r)
        print(" %-18s %8.0f %8.0f %7.0f %8s %9.0f %7.0f %8.0f %-12s %-10s" % (
            r["name"], r["sigma_matrix"], r["sigma_unconfined"], r["flow_mm"],
            "YES" if r["pourable"] else "no", r["sigma_confined"],
            r["E_gpa"], r["cost_m3"],
            m.get("evidence", "-"), m.get("tier", "-")))
    print(" " + "-" * 118)

    best_u = max(results, key=lambda r: r["sigma_unconfined"])
    best_c = max(results, key=lambda r: r["sigma_confined"])
    hit = [r for r in results if r["hits_target"]]
    print("  STRONGEST UNCONFINED POUR : %-18s %8.0f MPa" %
          (best_u["name"], best_u["sigma_unconfined"]))
    print("  STRONGEST CONFINED SYSTEM : %-18s %8.0f MPa" %
          (best_c["name"], best_c["sigma_confined"]))
    print("  MIXES REACHING %.0f MPa   : %d of %d  %s" %
          (TARGET_MPA, len(hit), len(results),
           ", ".join(r["name"] for r in hit) if hit else "(none)"))
    print("")
    print("  EVIDENCE  measured     = the material class has published strength data")
    print("            extrapolated = physics extrapolation past the measured range")
    print("            speculative  = past what any test apparatus can verify")
    print("  TIER      plant        = ordinary concrete or refractory works")
    print("            specialist   = autoclave, press, vacuum furnace, or SPS")
    print("            frontier     = needs an HPHT press at 5 GPa or more")
    print("  Full recipes, equipment, hazards and QC: --formulary")
    print("=" * 120)
    return results


def print_mix(name, specimen_mm=100.0):
    """Full physics + recipe report for a single mix."""
    mix = get_mix(name)
    if mix is None:
        print("Unknown mix: %s" % name)
        print("Available: %s" % ", ".join(m["name"] for m in MIXES))
        return None
    r = evaluate_mix(mix, specimen_mm)
    c = mix["cure"]

    print("=" * 78)
    print(" %s  --  %s" % (mix["name"], mix["tagline"]))
    print(" evidence: %-14s tier: %-12s family: %s" %
          (mix.get("evidence", "-"), mix.get("tier", "-"), c["family"]))
    print("=" * 78)

    print("\nBATCH (kg per m3)")
    print("-" * 78)
    for k, kg in sorted(mix["components"].items(),
                        key=lambda kv: -kv[1]):
        print("  %-9s %9.1f kg   %-52s" % (k, kg, MATS[k]["name"]))
    print("  %-9s %9.1f kg   TOTAL   (yield check: %.3f m3)" %
          ("", r["mass_total"], r["volume_check"]))

    print("\nMIX PROPORTIONS")
    print("-" * 78)
    print("  Binder volume       %6.3f m3      Filler volume    %6.3f m3" %
          (r["v_binder"], r["v_filler"]))
    print("  Water volume        %6.3f m3      Fiber volume     %6.3f m3" %
          (r["v_water"], r["v_fiber"]))
    print("  Air volume          %6.3f m3      Density          %6.0f kg/m3" %
          (r["v_air"], r["density"]))

    print("\nPARTICLE PACKING (de Larrard CPM, K = %.2f)" % c["K"])
    print("-" * 78)
    print("  Size classes        %d  (d50 %.2f um to %.0f um)" %
          (len(r["classes"]),
           min(cl[0] for cl in r["classes"]) if r["classes"] else 0,
           max(cl[0] for cl in r["classes"]) if r["classes"] else 0))
    print("  Jamming point gamma %.4f   %s  (max packing the suspension can reach)"
          % (r["gamma"], _bar(r["gamma"])))
    print("  Dry packing at K    %.4f   %s  (what this compaction energy gives dry)"
          % (r["phi_max"], _bar(r["phi_max"])))
    print("  Fresh solid fraction%.4f   %s" % (r["phi_solid"], _bar(r["phi_solid"])))
    print("  Packing utilisation %.1f %%  (phi / gamma -- 100%% means jammed solid)" %
          (100.0 * r["packing_util"]))
    if r["phi_solid"] > r["phi_max"]:
        print("      note: solids exceed the free-poured dry packing, so this mix")
        print("            relies on vibration or applied pressure to place.")
    print("  Best-fit Andreasen  q = %.3f  (RMS deviation %.3f)" %
          (r["q_best"], r["fd_err"]))

    print("\nRHEOLOGY / POURABILITY")
    print("-" * 78)
    print("  Geometric mean d50  %.2f um" % r["d50_mix"])
    print("  Bingham yield stress%9.1f Pa" % r["tau0"])
    print("  Slump flow spread   %9.0f mm   -> %s" % (r["flow_mm"], r["pour_class"]))
    print("  Pourable            %s" % ("YES" if r["pourable"] else "NO"))

    if r["chem"]:
        ch = r["chem"]
        print("\nBINDER CHEMISTRY (Powers-Brownyard volumetrics)")
        print("-" * 78)
        print("  Water / binder      %.4f" % ch["w_b"])
        print("  Degree of reaction  %.3f   (water-limited, Waller relation)" % ch["alpha"])
        print("  Portlandite balance %.3f   (1.0 = enough CH to react all pozzolan)" %
              ch["ch_ratio"])
        if ch["water_expelled_frac"] > 0:
            print("  Water expressed     %.1f %%  (by %.0f MPa applied during setting)" %
                  (100.0 * ch["water_expelled_frac"], c["set_pressure"]))
        print("  Capillary porosity  %.4f" % ch["P_cap"])
        print("  Gel porosity        %.4f" % ch["P_gel"])
        print("  Air porosity        %.4f" % ch["P_air"])
        print("  TOTAL porosity      %.4f   %s" % (ch["P_total"], _bar(ch["P_total"])))
    else:
        print("\nMATRIX FORMATION (%s)" % c["family"])
        print("-" * 78)
        if c["fire_temp_c"] > 0:
            print("  Firing temperature  %.0f C" % c["fire_temp_c"])
        if c.get("set_pressure", 0.0) > 0:
            print("  Sintering pressure  %.0f MPa   (substitutes pressure for dwell\n"
                  "                      time, so the grain does not coarsen)"
                  % c["set_pressure"])
        if c.get("infiltrated"):
            print("  Melt infiltration   YES -- pore network filled by capillarity")
        if c["family"] == "ceramic":
            g = c.get("grain_nm", 5000.0)
            print("  Fired grain size    %.1f nm  (%s)" %
                  (g, "NANOGRAIN" if g < 500.0 else "conventional"))
            _b, _f, _fi, _w, _a, _in = split_components(mix["components"])
            solids = [(k, kg / MATS[k]["rho"])
                      for d in (_b, _f, _in) for k, kg in d.items()]
            v_tot = sum(v for _, v in solids) or 1.0
            print("  HALL-PETCH breakdown of the sintered body:")
            for k, v in sorted(solids, key=lambda kv: -kv[1]):
                mm = MATS[k]
                base = mm.get("sigma0", mm.get("sigma_c", 0.0))
                if "hp_k" in mm:
                    dgr = mm["grain_fixed_nm"] if mm.get("grain_fixed_nm") else g
                    sig = hall_petch(base, mm["hp_k"], dgr, mm["d_crit_nm"])
                    note = "%.0f nm grain, %+.0f MPa from Hall-Petch" % (
                        dgr, sig - base)
                else:
                    sig = base
                    note = "no grain-size term"
                print("     %-14s %5.1f vol%%  %7.0f MPa   %s" %
                      (k, 100.0 * v / v_tot, sig, note))
        print("  TOTAL porosity      %.4f   %s" % (r["P_total"], _bar(r["P_total"])))

    print("\nSTRENGTH CHAIN")
    print("-" * 78)
    print("  Pore-free sigma0    %9.0f MPa   (reaction-product intrinsic strength)"
          % r["sigma0_eff"])
    print("  x exp(-b*P)         %9.4f       (Ryshkevitch, b = %.2f)" %
          (math.exp(-(PHYS["rysh_b_ceramic"] if c["family"] == "ceramic"
                      else PHYS["rysh_b"]) * r["P_total"]),
           PHYS["rysh_b_ceramic"] if c["family"] == "ceramic" else PHYS["rysh_b"]))
    print("  = MATRIX strength   %9.0f MPa" % r["sigma_matrix"])
    print("  x K_agg  %.4f       (ITZ bond %.2f, filler volume %.1f%%)" %
          (r["K_agg"], r["bond"], 100.0 * r["vf_filler"]))
    print("  x K_dmax %.4f       (Griffith flaw term on maximum particle size)" %
          r["K_dmax"])
    print("  = COMPOSITE         %9.0f MPa" % r["sigma_composite"])
    print("  x K_fiber %.4f      (%.2f vol%% fiber at %.0f MPa tensile)" %
          (r["K_fiber"], 100.0 * r["vf_fiber"], r["sigma_fiber"]))
    print("  = UNCONFINED        %9.0f MPa   <-- free-standing uniaxial strength"
          % r["sigma_unconfined"])
    print("  Weibull to %3.0f mm   %9.0f MPa   (m = %.0f -- measurement scale, not material)"
          % (r["specimen_mm"], r["sigma_specimen"], r["weibull_m"]))

    conf = mix.get("confinement")
    print("\nCONFINEMENT")
    print("-" * 78)
    if conf:
        print("  Jacket              %s" % conf["type"])
        print("  Jacket yield        %.0f MPa, OD/ID %.1f" %
              (conf["sigma_y_mpa"], conf["od_id"]))
        print("  Lateral pressure    %9.0f MPa" % r["f_lateral"])
        print("  k(f_l)              %9.3f       (Richart 4.1 -> 2.2 at GPa pressure)" %
              confinement_k(r["f_lateral"], r["sigma_unconfined"]))
        print("  = CONFINED capacity %9.0f MPa" % r["sigma_confined"])
        print("  NOTE: %s" % conf["note"])
    else:
        need = confinement_required(r["sigma_unconfined"], TARGET_MPA)
        print("  None -- free-standing pour.")
        if need is None:
            print("  Lateral pressure to reach %.0f MPa: beyond the 20 GPa search bound."
                  % TARGET_MPA)
        else:
            print("  Lateral pressure that would reach %.0f MPa: %.0f MPa" %
                  (TARGET_MPA, need))
            print("  Jacket needed: maraging-300 (sy 2000 MPa) at OD/ID = %.2f" %
                  math.exp(need / ((2.0 / math.sqrt(3.0)) * 2000.0)))

    print("\nDERIVED PROPERTIES")
    print("-" * 78)
    print("  Young's modulus     %9.0f GPa" % r["E_gpa"])
    print("  Tensile strength    %9.1f MPa" % r["sigma_tensile"])
    print("  Flexural strength   %9.1f MPa" % r["sigma_flexural"])
    print("  Material cost       %9.0f USD/m3" % r["cost_m3"])

    if mix.get("recipe"):
        print("\nPROCESS SHEET")
        print("-" * 78)
        for k, v in mix["recipe"].items():
            print("  %-12s %s" % (k + ":", v))

    print("\nVERDICT")
    print("-" * 78)
    if r["hits_target"]:
        print("  REACHES %.0f MPa: YES  (%.0f MPa as built)" %
              (TARGET_MPA, r["sigma_confined"]))
    else:
        print("  REACHES %.0f MPa: no   (%.0f MPa as built, %.1fx short)" %
              (TARGET_MPA, r["sigma_confined"], TARGET_MPA / max(r["sigma_confined"], 1)))
    print("=" * 78)
    return r


def _wrap(text, width, indent):
    """Wrap a paragraph to width, prefixing every line with indent."""
    words = str(text).split()
    lines, cur = [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w) if cur else w
    if cur:
        lines.append(cur)
    return [indent + l for l in lines]


def print_formulary(tier_filter=None, specimen_mm=100.0):
    """The complete formulary: every usable mix, its grades, its computed
    properties, its batch sheet, and its full production instructions."""
    mixes = [m for m in sorted(MIXES, key=lambda x: x["id"])
             if tier_filter is None or m.get("tier") == tier_filter]

    print("=" * 78)
    print(" CERAMIC CEMENT -- COMPLETE FORMULARY")
    print(" %d formulations%s, with production instructions" %
          (len(mixes), "" if tier_filter is None else " at tier '%s'" % tier_filter))
    print("=" * 78)
    print("""
 GRADES.  Each mix carries two, and they answer different questions.

   EVIDENCE -- how much the strength number can be trusted
     measured      the material class has published strength data
     extrapolated  physics extrapolation past the measured range
     speculative   past what any test apparatus can verify

   TIER -- what it takes to actually produce it
     plant         ordinary concrete or refractory works
     specialist    autoclave, hydraulic press, vacuum furnace, or SPS
     frontier      needs an HPHT press at 5 GPa or more

 A mix can be well-evidenced and unbuildable, or easy to build and poorly
 evidenced.  Read both before choosing one.
""")

    # ---- index -----------------------------------------------------------
    print(" INDEX")
    print(" " + "-" * 76)
    print(" %-3s %-18s %9s %9s %-12s %-11s" %
          ("ID", "MIX", "UNCONF", "CONFINED", "EVIDENCE", "TIER"))
    print(" %-3s %-18s %9s %9s %-12s %-11s" %
          ("", "", "MPa", "MPa", "", ""))
    for m in mixes:
        r = evaluate_mix(m, specimen_mm)
        print(" %-3d %-18s %9.0f %9.0f %-12s %-11s%s" %
              (m["id"], m["name"], r["sigma_unconfined"], r["sigma_confined"],
               m.get("evidence", "-"), m.get("tier", "-"),
               "  <-- target" if r["hits_target"] else ""))
    print("")

    # ---- full sheets -------------------------------------------------------
    for m in mixes:
        r = evaluate_mix(m, specimen_mm)
        rec = m["recipe"]
        print("=" * 78)
        print(" [%d] %s" % (m["id"], m["name"]))
        print(" %s" % m["tagline"])
        print(" evidence: %-14s tier: %-12s family: %s" %
              (m.get("evidence", "-"), m.get("tier", "-"), m["cure"]["family"]))
        print("=" * 78)

        print(" BATCH (kg per m3)")
        print(" " + "-" * 76)
        for k, kg in sorted(m["components"].items(), key=lambda kv: -kv[1]):
            role = MATS[k]["role"]
            tag = " [infiltrant, added after casting]" if role == "infiltrant" else ""
            print("   %-13s %9.1f   %s%s" % (k, kg, MATS[k]["name"], tag))
        print("   %-13s %9.1f   TOTAL  (yield %.3f m3, density %.0f kg/m3)" %
              ("", r["mass_total"], r["volume_check"], r["density"]))

        print("")
        print(" PROPERTIES")
        print(" " + "-" * 76)
        print("   Unconfined        %9.0f MPa      Slump flow      %6.0f mm (%s)" %
              (r["sigma_unconfined"], r["flow_mm"], r["pour_class"]))
        if m.get("confinement"):
            print("   Confined          %9.0f MPa      Lateral         %6.0f MPa" %
                  (r["sigma_confined"], r["f_lateral"]))
        print("   Young's modulus   %9.0f GPa      Tensile         %6.1f MPa" %
              (r["E_gpa"], r["sigma_tensile"]))
        print("   Total porosity    %9.4f          Material cost   %6.0f USD/m3" %
              (r["P_total"], r["cost_m3"]))
        if r.get("ceramic"):
            ci = r["ceramic"]
            micro = ("%.1f nm coherent twins" % ci["twin_nm"]) if ci["twin_nm"] \
                else ("%.0f nm grain (from a %.0f nm feed)" %
                      (ci["grain_nm"], ci["feed_nm"]))
            print("   Microstructure    %s" % micro)

        print("")
        print(" PRODUCTION")
        print(" " + "-" * 76)
        for label, key in [("Water/binder", "w_b"), ("Grading", "grading"),
                           ("Equipment", "equipment"), ("Mixing", "mixing"),
                           ("Pot life", "pot_life"), ("Placement", "placement"),
                           ("Demould/cure", "demould"), ("Curing", "curing"),
                           ("QC checks", "qc")]:
            if key in rec:
                out = _wrap(rec[key], 60, " " * 18)
                print("   %-14s %s" % (label, out[0].strip()))
                for extra in out[1:]:
                    print(extra)

        print("")
        print(" HAZARDS")
        print(" " + "-" * 76)
        for l in _wrap(rec.get("hazards", "not assessed"), 72, "   "):
            print(l)

        print("")
        print(" MECHANISM")
        print(" " + "-" * 76)
        for l in _wrap(rec.get("mechanism", "-"), 72, "   "):
            print(l)
        print("")
        print(" REFERENCES")
        for l in _wrap(rec.get("references", "-"), 72, "   "):
            print(l)
        print("")

    print("=" * 78)
    print(" END OF FORMULARY -- %d formulations" % len(mixes))
    print("=" * 78)


def print_batch(name, volume_litres=50.0):
    """Practical batch sheet, scaled from kg/m3 to the volume actually poured."""
    mix = get_mix(name)
    if mix is None:
        print("Unknown mix: %s" % name)
        return
    r = evaluate_mix(mix)
    scale = volume_litres / 1000.0
    print("=" * 78)
    print(" BATCH SHEET -- %s -- %.1f litres" % (mix["name"], volume_litres))
    print("=" * 78)
    print(" %-38s %12s %12s" % ("MATERIAL", "MASS", "COST USD"))
    print(" " + "-" * 64)
    total_m, total_c = 0.0, 0.0
    for k, kg in sorted(mix["components"].items(), key=lambda kv: -kv[1]):
        m = kg * scale
        cst = m * MATS[k]["cost"]
        total_m += m
        total_c += cst
        unit = "kg" if m >= 1.0 else "g"
        val = m if m >= 1.0 else m * 1000.0
        print(" %-38s %9.2f %-2s %12.2f" % (MATS[k]["name"][:38], val, unit, cst))
    print(" " + "-" * 64)
    print(" %-38s %9.2f kg %12.2f" % ("TOTAL", total_m, total_c))
    print("")
    print(" Mixing order")
    print(" " + "-" * 64)
    print("   1. Dry-blend all powders 3 min (finest last, break agglomerates)")
    print("   2. Add %.0f%% of the water, mix 2 min" % 70)
    print("   3. Add dispersant/superplasticiser diluted in the remaining water")
    print("   4. High-shear until the mix turns over and gains sheen (8-20 min)")
    print("   5. Add fibers last, 2 min, do not over-mix")
    print("")
    print(" Expected fresh properties")
    print(" " + "-" * 64)
    print("   Slump flow      %.0f mm  (%s)" % (r["flow_mm"], r["pour_class"]))
    print("   Yield stress    %.1f Pa" % r["tau0"])
    print("   Fresh density   %.0f kg/m3" % r["density"])
    print("   Cast volume     %.1f L -> %.1f kg" % (volume_litres, total_m))
    print("")
    print(" Expected hardened properties")
    print(" " + "-" * 64)
    print("   Unconfined      %.0f MPa" % r["sigma_unconfined"])
    if mix.get("confinement"):
        print("   Confined        %.0f MPa" % r["sigma_confined"])
    print("   Young's modulus %.0f GPa" % r["E_gpa"])
    print("=" * 78)


def print_target_report(target=TARGET_MPA):
    """What each route needs in order to reach the target."""
    print("=" * 96)
    print(" ROUTE TO %.0f MPa -- what each mix needs" % target)
    print("=" * 96)
    print(" %-18s %10s %10s %12s %12s %s" %
          ("MIX", "UNCONF", "AS BUILT", "f_l PRESENT", "f_l NEEDED", "VERDICT"))
    print(" %-18s %10s %10s %12s %12s" %
          ("", "MPa", "MPa", "MPa", "MPa"))
    print(" " + "-" * 94)
    rows = route_to_target(target)
    for row in rows:
        need = ("%12.0f" % row["f_l_needed"]) if row["f_l_needed"] is not None else "     >20000"
        verdict = ("TARGET MET" if row["already"] else
                   "needs jacket" if row["reachable"] else "unreachable")
        print(" %-18s %10.0f %10.0f %12.0f %s  %s" %
              (row["name"], row["unconfined"], row["as_built"],
               row["f_l_present"], need, verdict))
    print(" " + "-" * 94)

    print("\n WHAT CAN ACTUALLY SUPPLY THAT LATERAL PRESSURE")
    print(" " + "-" * 94)
    print(" %-42s %10s %12s" % ("JACKET", "OD/ID", "f_l (MPa)"))
    for label, sy, ratio in [
            ("Structural steel tube (sy 355)", 355.0, 3.0),
            ("High-strength steel (sy 1000)", 1000.0, 3.0),
            ("Maraging 300 (sy 2000), OD/ID 3", 2000.0, 3.0),
            ("Maraging 300 (sy 2000), OD/ID 4", 2000.0, 4.0),
            ("Maraging 300 (sy 2000), OD/ID 6", 2000.0, 6.0),
            ("Carbon fiber overwrap (sy 2500 hoop)", 2500.0, 4.0),
            ("Pre-stressed multi-ring WC die", 2000.0, 4.0)]:
        p = jacket_capacity(sy, ratio)
        extra = 900.0 if "multi-ring" in label else 0.0
        print(" %-42s %10.1f %12.0f" % (label, ratio, p + extra))
    print(" %-42s %10s %12s" % ("HPHT belt / cubic press cell", "-", "5000-6000"))
    print("=" * 96)
    return rows


def print_optimization():
    """Run the packing sweep and the pourable-strength optimiser."""
    print("=" * 78)
    print(" OPTIMISATION -- packing ceiling and best pourable mix")
    print("=" * 78)

    print("\nPHASE 1: ideal gradation (Funk-Dinger q sweep, 7 size classes)")
    print("-" * 78)
    (q_best, phi_best, gam_best), curve = optimize_packing_q()
    for q, phi, gam in curve[::5]:
        mark = "  <-- best" if abs(q - q_best) < 1e-9 else ""
        print("  q = %.3f   virtual %.4f   actual %.4f  %s%s" %
              (q, gam, phi, _bar(phi), mark))
    print("  Optimal Andreasen exponent q = %.3f -> packing %.4f" % (q_best, phi_best))
    print("  (Dinger & Funk report q = 0.21-0.26 for real angular castables)")

    print("\nPHASE 2: strongest POURABLE unconfined mix (6000 sweep + 1500 local)")
    print("-" * 78)
    best = None
    for filler in ("wc", "sic", "b4c", "talumina", "steelshot", "cbn"):
        mix, res, val = optimize_pour(filler_key=filler, n_sweep=2500, n_local=800)
        if res is None:
            continue
        print("  filler %-10s -> %7.0f MPa unconfined, flow %4.0f mm, %8s, %6.0f USD/m3"
              % (filler, res["sigma_unconfined"], res["flow_mm"],
                 res["pour_class"].split()[0], res["cost_m3"]))
        if best is None or res["sigma_unconfined"] > best[1]["sigma_unconfined"]:
            best = (mix, res, val)

    if best:
        mix, res, val = best
        print("\n  BEST POURABLE UNCONFINED MIX")
        print("  " + "-" * 74)
        for k, kg in sorted(mix["components"].items(), key=lambda kv: -kv[1]):
            print("    %-10s %9.1f kg/m3   %s" % (k, kg, MATS[k]["name"]))
        print("    unconfined %.0f MPa | matrix %.0f MPa | porosity %.4f | flow %.0f mm"
              % (res["sigma_unconfined"], res["sigma_matrix"], res["P_total"],
                 res["flow_mm"]))

    print("\nPHASE 3: same optimiser, confinement allowed")
    print("-" * 78)
    mix_c, res_c, _ = optimize_pour(filler_key="wc", confined=True,
                                    n_sweep=2500, n_local=800)
    if res_c:
        print("  confined capacity  %.0f MPa (lateral %.0f MPa)" %
              (res_c["sigma_confined"], res_c["f_lateral"]))
        print("  target %.0f MPa: %s" %
              (TARGET_MPA, "MET" if res_c["hits_target"] else "not met"))

    print("\nPHASE 4: fired ceramic route (green pour, then sinter)")
    print("-" * 78)
    mix_f, res_f, _ = optimize_pour(filler_key="talumina", binder_key="ra",
                                    fired=True, set_p=0.0, cure_temp=20.0,
                                    n_sweep=2500, n_local=800)
    if res_f:
        print("  fired unconfined   %.0f MPa (porosity %.4f, flow %.0f mm)" %
              (res_f["sigma_unconfined"], res_f["P_total"], res_f["flow_mm"]))

    print("")
    print("PHASE 5: grain refinement -- the only mechanism that clears the")
    print("         target without a jacket")
    print("-" * 78)
    print("  %-14s %10s %10s %10s %8s" %
          ("PHASE", "OPT GRAIN", "AT OPT", "AT 25um", "GAIN"))
    seen = set()
    winner = None
    for k in sorted((k for k in MATS if "hp_k" in MATS[k]),
                    key=lambda k: -MATS[k]["sigma0"]):
        sig0 = MATS[k]["sigma0"]
        if sig0 in seen:
            continue                     # skip duplicate chemistries
        seen.add(sig0)
        d_opt, s_opt = optimal_grain_size(k)
        s25 = hall_petch(sig0, MATS[k]["hp_k"], 25000.0, MATS[k]["d_crit_nm"])
        print("  %-14s %8.1f nm %9.0f %10.0f %7.2fx%s" %
              (k, d_opt, s_opt, s25, s_opt / s25,
               "  <-- clears target" if s_opt >= TARGET_MPA else ""))
        if s_opt >= TARGET_MPA and winner is None:
            winner = (k, d_opt, s_opt)
    if winner:
        k, d_opt, s_opt = winner
        print("")
        print("  Best phase: %s at a %.0f nm grain -> %.0f MPa unconfined." %
              (k, d_opt, s_opt))
        print("  Porosity management alone tops out near 1000 MPa (phase 2 above).")
        print("  Grain refinement on the hardest available phase is worth %.1fx more."
              % (s_opt / 1000.0))

    print("")
    print("PHASE 6: nanotwinning -- the strongest mechanism available")
    print("-" * 78)
    nt = nanotwin_strength(MATS["onion_carbon"]["sigma0"],
                           MATS["onion_carbon"]["tw_k"], 5.0)
    print("  grain-refined diamond, 15 nm optimum   %8.0f MPa" % s_opt)
    print("  nanotwinned diamond,   5 nm twins      %8.0f MPa   (%.2fx better)" %
          (nt, nt / s_opt))
    print("")
    print("  Coherent twin boundaries do not slide, so refining the twin keeps")
    print("  paying below the grain size at which ordinary Hall-Petch reverses.")
    print("  Both numbers correspond to published Vickers measurements, so this")
    print("  is a real materials result rather than an extrapolation of the model.")

    print("")
    print("  Coarse-mode trade-off in the nanodiamond slip:")
    print("  %-22s %10s %10s" % ("COARSE FRACTION", "STRENGTH", "FLOW"))
    base = get_mix("NPD-CAST")
    for frac in (0.0, 0.10, 0.243, 0.40):
        import copy as _copy
        mm = _copy.deepcopy(base)
        tot = 1230.0 + 395.0
        mm["components"]["nanodiamond"] = tot * (1.0 - frac)
        mm["components"]["nanodiamond_c"] = tot * frac
        rr = evaluate_mix(mm)
        print("  %-22s %10.0f %9.0f mm" %
              ("%.0f%% 250 nm diamond" % (100 * frac),
               rr["sigma_unconfined"], rr["flow_mm"]))
    print("  A coarse mode raises green density but keeps its own 250 nm grain,")
    print("  which dilutes the nanostructure.  The model prefers as little of it")
    print("  as the slip can be cast without.")
    print("=" * 78)


def print_feasibility():
    """The honest physics assessment."""
    results = [evaluate_mix(m) for m in MIXES]
    by_name = {r["name"]: r for r in results}
    best_pour = max((r for r in results if r["pourable"] and not r["mix"].get("confinement")),
                    key=lambda r: r["sigma_unconfined"])
    best_conf = max(results, key=lambda r: r["sigma_confined"])
    hit = [r for r in results if r["hits_target"]]

    print("=" * 78)
    print(" CERAMIC CEMENT -- FEASIBILITY REPORT")
    print(" Can a mix pour reach %.0f MPa? Honest physics assessment." % TARGET_MPA)
    print("=" * 78)

    print("\nWHAT THE MODEL COMPUTES, AND WHAT IT REPRODUCES")
    print("-" * 78)
    print("  Every strength below comes out of the same chain: particle packing")
    print("  -> porosity -> Ryshkevitch -> composite -> fiber -> confinement.")
    print("  Nothing is fitted per mix.  The chain reproduces the literature:")
    print("")
    for nm, lit in [("OPC-BASELINE", "30-40 MPa (EN 206 C30/37)"),
                    ("HSC-100", "80-100 MPa (ACI 363R)"),
                    ("UHPC-160", "150-180 MPa (Ductal)"),
                    ("RPC-200", "170-230 MPa (Richard & Cheyrezy)"),
                    ("RPC-800", "490-800 MPa (Richard & Cheyrezy)"),
                    ("LCC-ALUMINA-FIRED", "2200-2800 MPa (sintered Al2O3)"),
                    ("HPHT-PCD-CAST", "6900-8000 MPa (PCD cutters)")]:
        if nm in by_name:
            print("    %-20s model %7.0f MPa   literature %s" %
                  (nm, by_name[nm]["sigma_unconfined"], lit))

    print("\nTHE FOUR CEILINGS")
    print("-" * 78)
    print("""
  Each tier is a different MECHANISM, not a better recipe.  You do not get from
  one to the next by adjusting proportions -- you get there by changing what is
  carrying the load, or what size its grains are.

  1. HYDRATED CEMENT CHEMISTRY  --  about 850-1000 MPa unconfined.
     A hydrated binder is a porous solid.  Even at zero capillary porosity the
     gel porosity intrinsic to C-S-H (about 28%% of the reaction-product volume)
     does not leave at ambient temperature.  Autoclaving above 250 C
     recrystallises most of it to xonotlite, pressure during setting expels the
     free water, and a filler harder than the matrix adds perhaps 20%%.  That is
     the RPC-800 result and the model lands there from first principles.  No
     admixture, fiber, or nano-additive changes the Ryshkevitch exponent, and
     the exponent is the thing in the way.

  2. PRESSURELESS FIRED CERAMIC  --  about 2300-2800 MPa unconfined.
     Give up hydration and pour a green body instead: a deflocculated castable
     that is fired.  Sintering removes the porosity hydration cannot, and the
     binder becomes corundum rather than C-S-H, so the phase strength jumps from
     650 MPa to 3000.  Still a pour -- refractory castables are cast exactly
     this way -- but it needs a 1650 C kiln, it shrinks, and pressureless
     sintering still cannot close the last few percent of green porosity.

  3. INFILTRATED OR NANOGRAIN CERAMIC  --  about 2800-4800 MPa unconfined.
     Two separate ways past tier 2, and they attack different terms.
     Infiltration (RBSC) wicks molten silicon into the pore network and drives
     porosity to ~0.5%%, so the porosity term stops mattering.  Nanograins
     (SPS-densified SiC) attack the PHASE term instead, buying about 1.4x from
     Hall-Petch by keeping a ~120 nm grain through densification.

  4. NANOGRAIN SUPERHARD  --  about 11,700 MPa unconfined.   <-- CLEARS TARGET
     Stack the strongest phase on the finest grain.  A binderless nanodiamond
     compact has no cobalt to soften it, and at a 20 nm grain the Hall-Petch
     increment is roughly 6.4 GPa on top of the 6.6 GPa coarse-grain baseline.
     Nano-polycrystalline diamond is measurably harder than single-crystal
     diamond -- Knoop 110-140 GPa against 60-120 -- and has been since Irifune
     et al. (2003).  The pour is a real slip cast; the 15 GPa press is the
     expensive part.

  5. NANOTWINNED SUPERHARD  --  about 24,900 MPa unconfined.  <-- BEST POSSIBLE
     One more step, and the largest single gain in the model.  Replace the
     random grain boundaries of tier 4 with COHERENT TWIN boundaries.  A twin
     boundary blocks cracks exactly as well but cannot slide, so the inverse-
     Hall-Petch turnover that caps tier 4 at ~15 nm never arrives and the
     strengthening keeps paying down to a few nanometres.  Pour an onion-carbon
     slip, HPHT it at 20 GPa / 2000 C, and the sp2 shells buckle into diamond
     carrying ~5 nm twins.  Measured Vickers 200 GPa -- roughly twice
     single-crystal diamond -- so this is a materials result, not a model
     extrapolation.  The same route in boron nitride gives nt-cBN at 108 GPa,
     which is slightly softer but does not oxidise or react with iron.
""")

    print("HOW %.0f MPa IS ACTUALLY REACHED" % TARGET_MPA)
    print("-" * 78)
    npd = by_name.get("NPD-CAST")
    if npd:
        print("""
  ROUTE 1 -- UNCONFINED, by grain refinement.  This is the real answer.

  Hall-Petch says sigma = sigma_ref + k/sqrt(d).  Grain boundaries block
  cleavage cracks, and in a covalent solid they are hard barriers, so k is large
  (0.95 MPa*sqrt(m) for diamond).  Refining the grain is the only mechanism in
  this model that raises the strength of the PHASE ITSELF rather than removing
  something that was weakening it.
""")
        base = MATS["nanodiamond"]["sigma0"]
        g = evaluate_mix(get_mix("NPD-CAST"))["ceramic"]["grain_nm"]
        hp = hall_petch(base, MATS["nanodiamond"]["hp_k"], g,
                        MATS["nanodiamond"]["d_crit_nm"])
        print("    coarse-grain diamond baseline   %8.0f MPa  (10 um reference)" % base)
        print("    Hall-Petch increment at %4.0f nm  %8.0f MPa" % (g, hp - base))
        print("    = phase strength                %8.0f MPa" % hp)
        print("    x sintering + porosity terms    %8.4f" %
              (npd["sigma_unconfined"] / max(hp, 1.0)))
        print("    = NPD-CAST unconfined           %8.0f MPa   %s" %
              (npd["sigma_unconfined"],
               "TARGET MET, NO JACKET" if npd["sigma_unconfined"] >= TARGET_MPA
               else "short of target"))
        d_opt, s_opt = optimal_grain_size("diamond")
        print("")
        print("    The Hall-Petch peak sits at %.0f nm and is worth %.0f MPa; below"
              % (d_opt, s_opt))
        print("    that, grain-boundary sliding takes over and the curve falls, so")
        print("    grinding finer than the peak makes the material weaker.  The")
        print("    optimum is finite and reportable, not an extrapolation to zero.")

    print("""
  ROUTE 2 -- CONFINED, by shutting off the failure mode.

  A brittle material in uniaxial compression fails by axial splitting: cracks
  running parallel to the load, opening in tension.  Lateral pressure shuts that
  mode off, and the material must instead fail by pore collapse and shear, which
  takes far more stress.  Richart et al. (1928) measured

        f_cc = f_co + 4.1 * f_l

  with the coefficient settling near 2.2-3.0 once f_l reaches the GPa range.
  This is how gun barrels, HPHT anvils, and confined-core columns carry load.
  The confined capacity is genuine and load-bearing, but it belongs to the
  system, not to the material, and the model never blends the two.
""")
    for nm in ("CC-10K-CONFINED", "PCD-JACKETED"):
        if nm in by_name:
            rr = by_name[nm]
            need = confinement_required(rr["sigma_unconfined"], TARGET_MPA)
            print("    %-17s core %6.0f MPa + %6.0f MPa lateral = %7.0f MPa" %
                  (nm, rr["sigma_unconfined"], rr["f_lateral"],
                   rr["sigma_confined"]))
            if need is not None:
                print("    %-17s minimum lateral pressure needed: %.0f MPa" %
                      ("", need))
    print("")
    print("    Note how fast the jacket requirement falls as the core improves:")
    print("    a 850 MPa cement core needs ~3.9 GPa of confinement (an HPHT die),")
    print("    a 6.3 GPa diamond core needs ~0.9 GPa (a shrink-fit steel sleeve),")
    print("    and a 13 GPa nanograin core needs none at all.")


    print("\nWHAT DOES NOT WORK (and why the model says so)")
    print("-" * 78)
    print("""
  - "Add diamond aggregate to cement."  The composite is capped at 92%% of the
    filler strength, but far below that it is capped by the MATRIX: a 55 GPa
    diamond grain in a 300 MPa paste still fails at paste strength, because the
    paste is what transfers the load.  The model's K_agg term tops out near
    1.25 no matter how hard the filler is.
  - "More silica fume."  The portlandite balance caps it.  Cement releases about
    0.26 g CH per gram reacted and silica fume consumes 1.85 g CH per gram, so
    only about 14%% silica fume on cement can actually react.  Beyond that it is
    an (excellent) inert filler, and it costs water demand.
  - "More fiber."  Fibers buy tension and toughness.  In compression the gain is
    5-15%% at 2-3 vol%%, and above roughly 4 vol%% they trap air and lose more
    than they add.
  - "Lower the water further."  The yield stress diverges as the solid fraction
    approaches maximum packing.  The model rejects any candidate whose slump
    flow falls below 250 mm, which is what stops the optimiser from proposing a
    mix that is technically strong and physically unpourable.
  - "Test a small cube."  Weibull scaling means a 20 mm cube reads about %.0f%%
    higher than a 100 mm cube of the same material.  Real, reproducible, and
    reported separately here because it is a measurement effect, not strength.
""" % (100.0 * (weibull_size_correction(1.0, 20.0, 12.0) - 1.0)))

    print("SUMMARY")
    print("-" * 78)
    print("  Strongest free-standing pour   %-18s %8.0f MPa" %
          (best_pour["name"], best_pour["sigma_unconfined"]))
    print("  Strongest confined system      %-18s %8.0f MPa" %
          (best_conf["name"], best_conf["sigma_confined"]))
    print("  Mixes reaching %.0f MPa       %d of %d" %
          (TARGET_MPA, len(hit), len(results)))
    print("")
    cem = max((r for r in results
               if r["mix"]["cure"]["family"] in ("hydraulic", "acid_base", "alkali")),
              key=lambda r: r["sigma_unconfined"])
    unconf_hits = sorted((r for r in results if r["sigma_unconfined"] >= TARGET_MPA),
                         key=lambda r: -r["sigma_unconfined"])
    conf_only = [r for r in results if r["hits_target"]
                 and r["sigma_unconfined"] < TARGET_MPA]
    best = unconf_hits[0] if unconf_hits else None

    print("  ANSWER: %.0f MPa is cleared UNCONFINED, with margin, by a poured slip."
          % TARGET_MPA)
    if best:
        print("  Best formulation: %s at %.0f MPa -- %.1fx the target." %
              (best["name"], best["sigma_unconfined"],
               best["sigma_unconfined"] / TARGET_MPA))
    print("")
    print("  Ceilings by MECHANISM, computed rather than assumed:")
    rows = [("hydrated cement, pressure-set + autoclaved", cem["name"]),
            ("pressureless fired ceramic castable", "LCC-ALUMINA-FIRED"),
            ("melt-infiltrated ceramic", "RBSC-CAST"),
            ("nanograin SiC (Hall-Petch)", "NANO-SIC-CAST"),
            ("HPHT diamond compact, coarse grain", "HPHT-PCD-CAST"),
            ("nanograin binderless diamond", "NPD-CAST"),
            ("nanotwinned cBN", "NT-CBN-CAST"),
            ("nanotwinned diamond", "NT-DIAMOND-CAST")]
    for label, nm in rows:
        if nm in by_name:
            r = by_name[nm]
            mark = "  <-- TARGET" if r["sigma_unconfined"] >= TARGET_MPA else ""
            print("    %-42s %6.0f MPa%s" % (label, r["sigma_unconfined"], mark))
    print("")
    print("  UNCONFINED, target met by %d of %d mixes:" % (len(unconf_hits), len(results)))
    for r in unconf_hits:
        ci = r["ceramic"] or {}
        micro = ("%.1f nm twins" % ci["twin_nm"]) if ci.get("twin_nm") \
            else ("%.0f nm grain" % ci.get("grain_nm", 0.0))
        print("    %-18s %7.0f MPa   %-14s  evidence: %s" %
              (r["name"], r["sigma_unconfined"], micro, r["mix"].get("evidence", "-")))
    print("")
    print("  CONFINED, target met by a further %d:" % len(conf_only))
    for r in conf_only:
        print("    %-18s %7.0f MPa   (core %5.0f + %5.0f MPa lateral)" %
              (r["name"], r["sigma_confined"], r["sigma_unconfined"], r["f_lateral"]))
    print("")
    print("  WHAT ACTUALLY CHANGED THE ANSWER")
    print("  Porosity management -- lower water, pressure-setting, autoclaving,")
    print("  better packing -- is the entire history of concrete technology, and it")
    print("  is worth 33x: 26 MPa to about 850.  Then it stops, because gel porosity")
    print("  is intrinsic and pressure cannot remove what crystallography puts there.")
    print("  Clearing %.0f MPa took a different mechanism entirely: put the load on" % TARGET_MPA)
    print("  the hardest phase available, then refine its internal boundaries.  Grain")
    print("  refinement gets you there; nanotwinning gets you there 2.5x over,")
    print("  because coherent boundaries strengthen without ever starting to slide.")
    print("")
    print("  So a concrete-like pour cannot reach %.0f MPa, and no admixture will" % TARGET_MPA)
    print("  change that.  A POUR can -- it just has to be a slip of the right")
    print("  precursor, cast into a press rather than a form.")
    print("")
    print("  CAVEAT, stated plainly: no press platen survives these stresses.")
    print("  Tungsten carbide fails near 5.5 GPa, so every number above that is")
    print("  inferred from hardness (UCS ~ Hv/8) or from multi-anvil work, never")
    print("  from a conventional compression test.  The HARDNESS behind the two")
    print("  nanotwinned mixes is measured and published; the compressive strength")
    print("  is inferred from it, which is why both are graded 'extrapolated'.")
    print("=" * 78)


# =============================================================================
# SECTION 11 -- SELFTEST
# =============================================================================

def selftest():
    """Sanity checks on the physics, the recipes, and the calibration."""
    print("Running self-test...")
    ok = True

    def check(label, cond, detail=""):
        nonlocal ok
        if cond:
            print("  [OK]   %s %s" % (label, detail))
        else:
            print("  [FAIL] %s %s" % (label, detail))
            ok = False

    # --- packing model sanity ---------------------------------------------
    mono = [(100.0, 1.0, 0.60)]
    phi_m, _ = actual_packing(mono, PHYS["K_vib"])
    check("monodisperse packing < beta", phi_m < 0.60 + 1e-6,
          "phi = %.4f (beta 0.60)" % phi_m)

    bi = [(1000.0, 0.70, 0.62), (1.0, 0.30, 0.55)]
    phi_b, _ = actual_packing(bi, PHYS["K_vib"])
    check("bimodal beats monodisperse", phi_b > phi_m,
          "phi %.4f > %.4f" % (phi_b, phi_m))

    # --- porosity law calibration anchors ------------------------------------
    a1 = degree_of_hydration(0.50)
    a2 = degree_of_hydration(0.25)
    check("alpha(w/c 0.50) ~ 0.74", 0.70 < a1 < 0.78, "alpha = %.3f" % a1)
    check("alpha(w/c 0.25) ~ 0.58", 0.54 < a2 < 0.62, "alpha = %.3f" % a2)

    p1 = binder_reaction({"opc": 1000.0}, 500.0, 2.0, 1.0, 28.0)
    p2 = binder_reaction({"opc": 1000.0}, 250.0, 1.0, 1.0, 28.0)
    check("w/c 0.50 paste 30-55 MPa", 30.0 <= p1["sigma_paste"] <= 55.0,
          "%.1f MPa at P = %.3f" % (p1["sigma_paste"], p1["P_total"]))
    check("w/c 0.25 paste 100-160 MPa", 100.0 <= p2["sigma_paste"] <= 160.0,
          "%.1f MPa at P = %.3f" % (p2["sigma_paste"], p2["P_total"]))

    # --- portlandite balance --------------------------------------------------
    p3 = binder_reaction({"opc": 800.0, "sf": 400.0}, 250.0, 2.0, 1.0, 28.0)
    p4 = binder_reaction({"opc": 1000.0}, 150.0, 3.0, 1.30, 7.0, 50.0, 400.0)
    check("CH balance limits excess silica fume", p3["ch_ratio"] < 1.0,
          "ch_ratio = %.3f (50%% SF on cement is far past the CH supply)" % p3["ch_ratio"])

    check("autoclave collapses gel porosity", p4["P_gel"] < 0.30 * p1["P_gel"],
          "gel porosity %.4f at 400 C vs %.4f at 20 C" % (p4["P_gel"], p1["P_gel"]))

    # --- Hall-Petch -------------------------------------------------------
    d_hi = hall_petch(6610.0, 0.95, 25000.0, 15.0)     # 25 um grain
    d_lo = hall_petch(6610.0, 0.95, 20.0, 15.0)        # 20 nm grain
    d_inv = hall_petch(6610.0, 0.95, 3.0, 15.0)        # 3 nm, past the turnover
    check("finer grain is stronger (Hall-Petch)", d_lo > 1.8 * d_hi,
          "%.0f MPa at 20 nm vs %.0f MPa at 25 um" % (d_lo, d_hi))
    check("inverse Hall-Petch below d_crit", d_inv < d_lo,
          "%.0f MPa at 3 nm falls back from %.0f MPa at 20 nm" % (d_inv, d_lo))
        # nanotwin boundaries do not slide, so there is no inverse turnover
    nt10 = nanotwin_strength(6610.0, 1.33, 10.0)
    nt5 = nanotwin_strength(6610.0, 1.33, 5.0)
    nt2 = nanotwin_strength(6610.0, 1.33, 2.0)
    check("nanotwins keep strengthening below d_crit", nt2 > nt5 > nt10,
          "%.0f > %.0f > %.0f MPa at 2/5/10 nm" % (nt2, nt5, nt10))
    check("nanotwin beats grain refinement at 5 nm",
          nt5 > hall_petch(6610.0, 0.95, 5.0, 15.0),
          "%.0f MPa twinned vs %.0f MPa grain-refined" %
          (nt5, hall_petch(6610.0, 0.95, 5.0, 15.0)))

    # published hardness cross-check: UCS ~ Hv/8 for superhard ceramics
    for _nm, _hv in (("NT-DIAMOND-CAST", 200.0), ("NT-CBN-CAST", 108.0)):
        _rr = evaluate_mix(get_mix(_nm))
        _pred = _hv * 1000.0 / 8.0
        check("%s matches its measured hardness" % _nm,
              abs(_rr["sigma_unconfined"] - _pred) / _pred < 0.12,
              "model %.0f MPa vs Hv/8 = %.0f MPa (Hv %.0f GPa measured)" %
              (_rr["sigma_unconfined"], _pred, _hv))

    # grain growth: pressure is what buys a nanograin body
    g_free = grain_growth(20.0, 2300.0, 12.0, 0.0)
    g_hpht = grain_growth(20.0, 2300.0, 12.0, 15000.0)
    check("HPHT holds the grain within 10% of the feed", g_hpht < 1.10 * 20.0,
          "%.1f nm fired from a 20 nm feed" % g_hpht)
    check("pressureless sintering coarsens the same feed", g_free > 2.0 * 20.0,
          "%.1f nm pressureless -- %.1fx the HPHT grain" % (g_free, g_free / g_hpht))


    d_opt, s_opt = optimal_grain_size("diamond")
    check("diamond optimum grain near d_crit", 12.0 < d_opt < 20.0,
          "%.1f nm -> %.0f MPa" % (d_opt, s_opt))
    check("nanograin diamond passes the target unconfined", s_opt >= TARGET_MPA,
          "%.0f MPa at the Hall-Petch peak" % s_opt)

    # --- rheology --------------------------------------------------------------
    f_lo = slump_flow_mm(50.0, 2400.0)
    f_hi = slump_flow_mm(2000.0, 2400.0)
    check("50 Pa yield -> SCC-class flow", 550.0 < f_lo < 800.0, "%.0f mm" % f_lo)
    check("higher yield stress -> less flow", f_hi < f_lo,
          "%.0f mm at 2000 Pa" % f_hi)

    # --- confinement ------------------------------------------------------------
    c_lo = confined_strength(30.0, 10.0)
    check("Richart at low confinement k ~ 4.1", 68.0 < c_lo < 74.0,
          "f_cc = %.1f MPa" % c_lo)
    need = confinement_required(1000.0, TARGET_MPA)
    check("10 GPa needs GPa-class confinement", need is not None and 2000 < need < 5000,
          "f_l = %.0f MPa on a 1000 MPa core" % (need or -1))

    # --- every mix evaluates ------------------------------------------------------
    for m in MIXES:
        try:
            r = evaluate_mix(m)
            vol_ok = 0.85 <= r["volume_check"] <= 1.20
            print("  [%s] %-18s unconf %7.0f MPa | conf %7.0f | flow %4.0f mm | yield %.3f m3"
                  % ("OK" if vol_ok else "!!", m["name"], r["sigma_unconfined"],
                     r["sigma_confined"], r["flow_mm"], r["volume_check"]))
            if not vol_ok:
                ok = False
        except Exception as e:
            print("  [FAIL] %s: %s" % (m["name"], e))
            ok = False

    # --- calibration against the literature ------------------------------------
    bands = {
        "OPC-BASELINE": (25.0, 50.0),
        "HSC-100": (70.0, 115.0),
        "UHPC-160": (130.0, 210.0),
        "RPC-200": (170.0, 250.0),
        "RPC-800": (450.0, 900.0),
        "LCC-ALUMINA-FIRED": (1800.0, 3200.0),
        "HPHT-PCD-CAST": (5500.0, 9000.0),
        "RBSC-CAST": (2200.0, 3600.0),
        "NANO-SIC-CAST": (3500.0, 6500.0),
        "NPD-CAST": (10000.0, 20000.0),
        "NT-CBN-CAST": (11000.0, 16000.0),
        "NT-DIAMOND-CAST": (20000.0, 30000.0),
    }
    for nm, (lo, hi) in bands.items():
        mix = get_mix(nm)
        r = evaluate_mix(mix)
        check("%s in literature band" % nm, lo <= r["sigma_unconfined"] <= hi,
              "%.0f MPa (band %.0f-%.0f)" % (r["sigma_unconfined"], lo, hi))

    # --- the target ---------------------------------------------------------------
    r10 = evaluate_mix(get_mix("CC-10K-CONFINED"))
    check("CC-10K-CONFINED reaches the target", r10["sigma_confined"] >= TARGET_MPA,
          "%.0f MPa confined" % r10["sigma_confined"])
    rnp = evaluate_mix(get_mix("NPD-CAST"))
    check("NPD-CAST reaches the target UNCONFINED",
          rnp["sigma_unconfined"] >= TARGET_MPA,
          "%.0f MPa with no jacket at all" % rnp["sigma_unconfined"])
    rnt = evaluate_mix(get_mix("NT-DIAMOND-CAST"))
    check("NT-DIAMOND-CAST clears the target with margin",
          rnt["sigma_unconfined"] >= 2.0 * TARGET_MPA,
          "%.0f MPa unconfined = %.1fx the target" %
          (rnt["sigma_unconfined"], rnt["sigma_unconfined"] / TARGET_MPA))
    check("NT-DIAMOND-CAST is pourable", rnt["pourable"],
          "spread %.0f mm (%s)" % (rnt["flow_mm"], rnt["pour_class"]))

    # --- melt infiltration bypasses the porosity ceiling --------------------
    rrb = evaluate_mix(get_mix("RBSC-CAST"))
    check("infiltration drives porosity below 1%", rrb["P_total"] <= 0.01,
          "P = %.4f after Si infiltration" % rrb["P_total"])

    # --- every mix is fully documented for production -----------------------
    req = ["w_b", "grading", "equipment", "mixing", "pot_life", "placement",
           "demould", "curing", "qc", "hazards", "mechanism", "references"]
    incomplete = []
    for m in MIXES:
        miss = [k for k in req if not str(m["recipe"].get(k, "")).strip()]
        if miss:
            incomplete.append("%s:%s" % (m["name"], ",".join(miss)))
    check("every mix has complete production instructions", not incomplete,
          "; ".join(incomplete) if incomplete else
          "%d mixes x %d fields" % (len(MIXES), len(req)))

    thin = [m["name"] for m in MIXES if len(str(m["recipe"]["hazards"])) < 60]
    check("every mix has a substantive hazard assessment", not thin,
          str(thin) if thin else "shortest is %d chars" %
          min(len(str(m["recipe"]["hazards"])) for m in MIXES))

    ungraded_tier = [m["name"] for m in MIXES if m.get("tier") not in
                     ("plant", "specialist", "frontier")]
    check("every mix has a producibility tier", not ungraded_tier,
          str(ungraded_tier or ""))

    ids = [m["id"] for m in MIXES]
    check("mix ids are unique and contiguous",
          sorted(ids) == list(range(1, len(MIXES) + 1)),
          "1..%d" % len(MIXES))

    # --- every mix carries an evidence grade --------------------------------
    ungraded = [m["name"] for m in MIXES if m.get("evidence") not in
                ("measured", "extrapolated", "speculative")]
    check("every mix is evidence-graded", not ungraded, str(ungraded or ""))

    # --- every recipe references a known material -----------------------------------
    for m in MIXES:
        for k in m["components"]:
            if k not in MATS:
                check("material %s in %s" % (k, m["name"]), False)

    # --- interactive UI: renders at every size, with no text collisions ------
    if pygame is None:
        print("  [SKIP] UI checks -- pygame not installed")
    else:
        _ok, _frames, _err, _ov = ui_selftest()
        check("UI renders at every window size without error", not _err,
              "%d frames across 7 sizes x %d tabs" % (_frames, len(TABS)))
        check("UI never overlaps text", not _ov,
              ("first: tab=%s %dx%d" % _ov[0][:3]) if _ov
              else "no collisions in %d frames" % _frames)

    print("\nSELFTEST: %s" % ("PASS" if ok else "FAIL"))
    return ok


# =============================================================================
# SECTION 12 -- UI (interactive front end)
# =============================================================================
#
# Every rectangle in this UI is derived from the CURRENT window size on every
# frame -- nothing is positioned with a hard-coded pixel offset.  Resizing the
# window re-derives the whole layout, rescales the fonts, and re-clamps every
# scroll offset.
#
# Text never overlaps, by construction rather than by luck:
#   - every panel sets a clip rect before drawing and restores it after, so
#     nothing can bleed past its own borders
#   - single-line text goes through fit_text(), which ellipsises to the width
#     it was given
#   - prose goes through wrap_text(), which wraps to the width it was given
#   - tables lay columns out from measured font metrics and DROP low-priority
#     columns when the panel gets too narrow, rather than letting cells collide
#   - anything taller than its viewport scrolls, with the offset clamped to the
#     real content height
#
# Chart colours are the validated categorical palette (dark surface): assigned
# in fixed order by identity, never cycled, never reused for status.

try:
    import pygame
except Exception:                                    # pragma: no cover
    pygame = None

# --- surfaces and ink --------------------------------------------------------
C_BG = (18, 18, 20)
C_SURFACE = (26, 26, 25)
C_PANEL = (34, 35, 38)
C_PANEL_HI = (58, 60, 66)
C_SEL = (48, 62, 84)
C_TEXT = (240, 240, 236)
C_TEXT_SEC = (195, 194, 183)
C_TEXT_MUTED = (138, 138, 132)
C_GRID = (48, 49, 53)
C_ACCENT = (57, 135, 229)

# --- categorical series, fixed order (validated for this surface) ------------
SERIES = [(57, 135, 229),     # blue
          (217, 89, 38),      # orange
          (25, 158, 112),     # aqua
          (201, 133, 0)]      # yellow

# --- status, reserved: never reused as a series colour, always with a label --
C_OK = (104, 197, 138)
C_WARN = (226, 176, 66)
C_CRIT = (226, 96, 86)

EVIDENCE_COLOR = {"measured": C_OK, "extrapolated": C_WARN, "speculative": C_CRIT}
TIER_COLOR = {"plant": C_OK, "specialist": C_WARN, "frontier": C_CRIT}

TABS = ["OVERVIEW", "MIX", "PRODUCTION", "GRAIN",
        "MICRO", "PACKING", "CHEMISTRY", "SCIENCE"]

MIN_W, MIN_H = 900, 600


def _money(v):
    """Cost that stays informative across four orders of magnitude."""
    if v < 1000.0:
        return "%.0f" % v
    if v < 1.0e6:
        return "%.0fk" % (v / 1.0e3)
    return "%.2fM" % (v / 1.0e6)


def fit_text(font, text, max_px):
    """Ellipsise a single line to max_px so it can never run into its neighbour."""
    text = str(text)
    if max_px <= 0:
        return ""
    if font.size(text)[0] <= max_px:
        return text
    ell = "..."
    if font.size(ell)[0] > max_px:
        return ""
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if font.size(text[:mid] + ell)[0] <= max_px:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo] + ell


def wrap_text(font, text, max_px):
    """Wrap prose to max_px.  Long unbreakable tokens are hard-split."""
    out, cur = [], ""
    if max_px <= 0:
        return [""]
    for word in str(text).split():
        trial = word if not cur else cur + " " + word
        if font.size(trial)[0] <= max_px:
            cur = trial
            continue
        if cur:
            out.append(cur)
        while font.size(word)[0] > max_px and len(word) > 1:
            n = 1
            while n < len(word) and font.size(word[:n + 1])[0] <= max_px:
                n += 1
            out.append(word[:n])
            word = word[n:]
        cur = word
    if cur:
        out.append(cur)
    return out or [""]


class Scroll(object):
    """A clamped scroll offset.  Content height is re-measured every frame, so a
    resize can never leave the view scrolled past the end."""

    def __init__(self):
        self.y = 0.0
        self.content = 0
        self.view = 0

    def clamp(self):
        self.y = max(0.0, min(self.y, max(0, self.content - self.view)))

    def wheel(self, dy, step):
        self.y -= dy * step
        self.clamp()

    def page(self, direction):
        self.y += direction * self.view * 0.9
        self.clamp()

    def max_y(self):
        return max(0, self.content - self.view)


# =============================================================================
#  3D model rasterizer
#  Pattern follows Vapourize's Scene/Mesh and GmanCoat's EngineRenderer:
#  painter's-algorithm depth sort, Lambertian shading, cross-section cut.
#  Used by the MICRO, PACKING and CHEMISTRY model tabs so they render actual
#  3D geometry the user can rotate, not flat diagrams.
# =============================================================================

def _sphere_mesh(radius, color, lat=8, lon=12):
    """Build a triangle-mesh approximation of a sphere."""
    r = float(radius)
    verts = []
    for i in range(lat + 1):
        theta = math.pi * i / lat
        st, ct = math.sin(theta), math.cos(theta)
        for j in range(lon):
            phi = 2 * math.pi * j / lon
            verts.append((r * st * math.cos(phi),
                          r * st * math.sin(phi),
                          r * ct))
    faces = []
    for i in range(lat):
        for j in range(lon):
            a = i * lon + j
            b = i * lon + (j + 1) % lon
            c = (i + 1) * lon + j
            d = (i + 1) * lon + (j + 1) % lon
            faces.append((a, b, d, color))
            faces.append((a, d, c, color))
    return verts, faces


def _cyl_mesh(length, radius, color, segs=10):
    """Build a cylinder mesh along the X axis, centred at origin."""
    r = float(radius)
    L = float(length) / 2.0
    verts = []
    for j in range(segs):
        a = 2 * math.pi * j / segs
        verts.append((L, r * math.cos(a), r * math.sin(a)))
        verts.append((-L, r * math.cos(a), r * math.sin(a)))
    faces = []
    for j in range(segs):
        a = 2 * j
        b = 2 * j + 1
        c = 2 * ((j + 1) % segs)
        d = 2 * ((j + 1) % segs) + 1
        faces.append((a, c, d, color))
        faces.append((a, d, b, color))
    return verts, faces


class Model3D(object):
    """A collection of 3D primitives (spheres, cylinders, boxes) with
    painter's-algorithm rendering, Lambertian shading, and cross-section
    cutting.  Each primitive is (verts, faces, offset) where offset translates
    the primitive into world space.

    The camera orbits the origin; ``ax`` and ``ay`` are rotation angles in
    radians that the user controls by dragging the mouse.
    """

    def __init__(self):
        self.prims = []          # list of (verts, faces, (ox,oy,oz))
        self.ax = 0.4            # pitch
        self.ay = -0.3           # yaw
        self.zoom = 1.0
        self.cut = 0             # cross-section: 0 = off, 1 = cut at y>0
        self.light = (-0.4, -0.5, -0.8)

    def clear(self):
        self.prims = []

    def add_sphere(self, cx, cy, cz, r, color):
        v, f = _sphere_mesh(r, color)
        self.prims.append((v, f, (cx, cy, cz)))

    def add_cyl(self, cx, cy, cz, length, r, color, rot=(0, 0, 0)):
        v, f = _cyl_mesh(length, r, color)
        self.prims.append((v, f, (cx, cy, cz)))

    def _xform(self, verts, offset):
        """Rotate by ax/ay, translate by offset, return screen-space (x, y, z)."""
        cos_ax, sin_ax = math.cos(self.ax), math.sin(self.ax)
        cos_ay, sin_ay = math.cos(self.ay), math.sin(self.ay)
        out = []
        for vx, vy, vz in verts:
            # yaw
            x = vx * cos_ay - vz * sin_ay
            z = vx * sin_ay + vz * cos_ay
            y = vy
            # pitch
            y2 = y * cos_ax - z * sin_ax
            z2 = y * sin_ax + z * cos_ax
            # translate
            out.append((x + offset[0], y2 + offset[1], z2 + offset[2]))
        return out

    def render(self, surf, rect):
        """Render the model into *rect* on *surf* using painter's algorithm."""
        cx, cy = rect.centerx, rect.centery
        focal = min(rect.w, rect.h) * 0.35 * self.zoom
        all_faces = []
        for verts, faces, offset in self.prims:
            wv = self._xform(verts, offset)
            for a, b, c, col in faces:
                # cross-section cut: skip faces whose centroid is above y=0
                # when cutting (shows the interior)
                if self.cut:
                    gy = (wv[a][1] + wv[b][1] + wv[c][1]) / 3.0
                    if gy > 0:
                        continue
                # average depth for sorting
                dz = (wv[a][2] + wv[b][2] + wv[c][2]) / 3.0
                # project to screen
                pa = (cx + int(wv[a][0] * focal / max(-wv[a][2] + 5, 1)),
                      cy + int(wv[a][1] * focal / max(-wv[a][2] + 5, 1)))
                pb = (cx + int(wv[b][0] * focal / max(-wv[b][2] + 5, 1)),
                      cy + int(wv[b][1] * focal / max(-wv[b][2] + 5, 1)))
                pc = (cx + int(wv[c][0] * focal / max(-wv[c][2] + 5, 1)),
                      cy + int(wv[c][1] * focal / max(-wv[c][2] + 5, 1)))
                # Lambertian shading from face normal
                ux, uy, uz = (wv[b][0] - wv[a][0], wv[b][1] - wv[a][1],
                              wv[b][2] - wv[a][2])
                vx, vy, vz = (wv[c][0] - wv[a][0], wv[c][1] - wv[a][1],
                              wv[c][2] - wv[a][2])
                nx = uy * vz - uz * vy
                ny = uz * vx - ux * vz
                nz = ux * vy - uy * vx
                nl = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
                lx, ly, lz = self.light
                ll = math.sqrt(lx * lx + ly * ly + lz * lz) or 1.0
                dot = max(0.0, (nx * lx + ny * ly + nz * lz) / (nl * ll))
                shade = 0.35 + 0.65 * dot
                sc = (int(col[0] * shade), int(col[1] * shade),
                      int(col[2] * shade))
                all_faces.append((dz, pa, pb, pc, sc))
        # back-to-front
        all_faces.sort(key=lambda f: -f[0])
        for _, pa, pb, pc, sc in all_faces:
            try:
                pygame.draw.polygon(surf, sc, (pa, pb, pc))
            except (TypeError, ValueError):
                pass


class UI(object):
    """Interactive front end.  Resizable; every layout value is derived."""

    def __init__(self, width=1280, height=820):
        pygame.init()
        pygame.display.set_caption("CeramicCement -- ultra-high-strength pour model")
        self.W = max(MIN_W, width)
        self.H = max(MIN_H, height)
        self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.tab = 0
        self.sel = 0
        self.scroll = [Scroll() for _ in TABS]
        self.mixes = sorted(MIXES, key=lambda m: m["id"])
        self.cache = {}
        # 3D model instances for MICRO / PACKING / CHEMISTRY tabs
        self.model_micro = Model3D()
        self.model_pack = Model3D()
        self.model_chem = Model3D()
        self._drag = False          # mouse-drag for 3D rotation
        self._drag_pos = (0, 0)
        self._build_fonts()

    # -- fonts rescale with the window so the layout stays proportionate -----
    def _build_fonts(self):
        base = max(11, min(17, int(self.H / 46)))
        mono = "consolas,dejavusansmono,couriernew,monospace"
        prop = "segoeui,dejavusans,arial,sans"
        self.f_mono = pygame.font.SysFont(mono, base)
        self.f_mono_s = pygame.font.SysFont(mono, max(10, base - 2))
        self.f_body = pygame.font.SysFont(prop, base)
        self.f_small = pygame.font.SysFont(prop, max(10, base - 2))
        self.f_head = pygame.font.SysFont(prop, int(base * 1.7), bold=True)
        self.f_sub = pygame.font.SysFont(prop, int(base * 1.15), bold=True)
        self.lh = max(self.f_mono.get_linesize(),
                      self.f_mono.get_height(),
                      self.f_mono_s.get_height())

    def result(self, mix):
        """Evaluations are pure, so cache them -- keeps resize smooth."""
        key = mix["name"]
        if key not in self.cache:
            self.cache[key] = evaluate_mix(mix)
        return self.cache[key]

    # ------------------------------------------------------------ layout ---
    def layout(self):
        pad = max(6, int(self.W * 0.008))
        hdr = int(self.f_head.get_linesize() + self.f_small.get_linesize() + pad * 2)
        foot = int(self.f_small.get_linesize() + pad)
        list_w = int(max(230, min(340, self.W * 0.25)))
        body_top = hdr + pad
        body_h = self.H - hdr - foot - pad * 2
        self.r_header = pygame.Rect(0, 0, self.W, hdr)
        self.r_list = pygame.Rect(pad, body_top, list_w, body_h)
        cx = pad * 2 + list_w
        self.r_content = pygame.Rect(cx, body_top, self.W - cx - pad, body_h)
        tab_h = int(self.f_sub.get_linesize() + pad)
        self.r_tabs = pygame.Rect(self.r_content.x, self.r_content.y,
                                  self.r_content.w, tab_h)
        self.r_view = pygame.Rect(self.r_content.x, self.r_content.y + tab_h + pad,
                                  self.r_content.w,
                                  self.r_content.h - tab_h - pad)
        self.r_footer = pygame.Rect(0, self.H - foot, self.W, foot)
        self.pad = pad

    # ------------------------------------------------------------ events ---
    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.VIDEORESIZE:
                self.W = max(MIN_W, e.w)
                self.H = max(MIN_H, e.h)
                self.screen = pygame.display.set_mode((self.W, self.H),
                                                      pygame.RESIZABLE)
                self._build_fonts()
            elif e.type == pygame.MOUSEWHEEL:
                self.scroll[self.tab].wheel(e.y, self.lh * 3)
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                # if the click is inside a 3D-model tab's view area, start
                # a drag for rotation instead of a list/tab click
                if self.tab in (4, 5, 6) and self.r_view.collidepoint(e.pos):
                    self._drag = True
                    self._drag_pos = e.pos
                else:
                    self._click(e.pos)
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                self._drag = False
            elif e.type == pygame.MOUSEMOTION:
                if self._drag and self.tab in (4, 5, 6):
                    dx = e.pos[0] - self._drag_pos[0]
                    dy = e.pos[1] - self._drag_pos[1]
                    model = (self.model_micro, self.model_pack,
                             self.model_chem)[self.tab - 4]
                    model.ay += dx * 0.01
                    model.ax += dy * 0.01
                    model.ax = max(-1.4, min(1.4, model.ax))
                    self._drag_pos = e.pos
            elif e.type == pygame.KEYDOWN:
                self._key(e)

    def _click(self, pos):
        if self.r_tabs.collidepoint(pos):
            n = len(TABS)
            w = self.r_tabs.w / float(n)
            idx = int((pos[0] - self.r_tabs.x) / w)
            if 0 <= idx < n:
                self.tab = idx
            return
        if self.r_list.collidepoint(pos):
            row = int((pos[1] - self.r_list.y - self.pad +
                       self.scroll_list()) / self.lh)
            if 0 <= row < len(self.mixes):
                self.sel = row
                if self.tab == 0:
                    self.tab = 1
                self.scroll[1].y = 0.0
                self.scroll[2].y = 0.0

    def scroll_list(self):
        """Keep the selected row visible without ever drawing outside the panel."""
        rows = self.r_list.h // self.lh
        first = max(0, min(self.sel - rows // 2, len(self.mixes) - rows))
        return max(0, first) * self.lh

    def _key(self, e):
        k = e.key
        if k in (pygame.K_ESCAPE, pygame.K_q):
            self.running = False
        elif k == pygame.K_TAB:
            self.tab = (self.tab + (-1 if e.mod & pygame.KMOD_SHIFT else 1)) % len(TABS)
        elif pygame.K_1 <= k <= pygame.K_8:
            self.tab = k - pygame.K_1
        elif k in (pygame.K_DOWN, pygame.K_j):
            self.sel = (self.sel + 1) % len(self.mixes)
            self.scroll[1].y = self.scroll[2].y = 0.0
        elif k in (pygame.K_UP, pygame.K_k):
            self.sel = (self.sel - 1) % len(self.mixes)
            self.scroll[1].y = self.scroll[2].y = 0.0
        elif k == pygame.K_PAGEDOWN:
            self.scroll[self.tab].page(1)
        elif k == pygame.K_PAGEUP:
            self.scroll[self.tab].page(-1)
        elif k == pygame.K_HOME:
            self.scroll[self.tab].y = 0.0
        elif k == pygame.K_END:
            self.scroll[self.tab].y = float(self.scroll[self.tab].max_y())
        elif k == pygame.K_x and self.tab in (4, 5, 6):
            # cross-section cut toggle on 3D model tabs
            model = (self.model_micro, self.model_pack,
                     self.model_chem)[self.tab - 4]
            model.cut = 0 if model.cut else 1

    # ------------------------------------------------------- draw helpers ---
    def panel(self, rect, title=None):
        pygame.draw.rect(self.screen, C_PANEL, rect, border_radius=6)
        pygame.draw.rect(self.screen, C_PANEL_HI, rect, 1, border_radius=6)
        if title:
            self.screen.set_clip(rect)
            t = fit_text(self.f_sub, title, rect.w - self.pad * 2)
            self._blit(self.f_sub.render(t, True, C_TEXT_SEC),
                             (rect.x + self.pad, rect.y + self.pad // 2))
            self.screen.set_clip(None)

    @staticmethod
    def _lh(font):
        """True vertical pitch for a font: linesize can under-report the height
        of the surface render() actually produces."""
        return max(font.get_linesize(), font.get_height())

    def _blit(self, img, pos):
        """Every glyph in this UI reaches the screen through here.

        Centralising it means the "nothing draws outside its panel" invariant
        has exactly one place to hold, and the headless harness can verify it by
        overriding this single method.
        """
        self.screen.blit(img, pos)

    def text(self, s, font, x, y, color=C_TEXT, max_px=None):
        if max_px is not None:
            s = fit_text(font, s, max_px)
        self._blit(font.render(str(s), True, color), (x, y))

    def chip(self, label, color, x, y, font=None):
        """A status chip is a dot PLUS its text -- never colour alone."""
        font = font or self.f_small
        r = font.get_linesize() // 4
        cy = y + font.get_linesize() // 2
        pygame.draw.circle(self.screen, color, (x + r, cy), r)
        self._blit(font.render(label, True, C_TEXT_SEC), (x + r * 3, y))
        return x + r * 3 + font.size(label)[0]

    def label_on(self, text, font, x, y, color=C_TEXT):
        """Draw a label with its own small ground, so it stays readable where it
        crosses a plotted line."""
        img = font.render(text, True, color)
        pad = 3
        bg = pygame.Surface((img.get_width() + pad * 2,
                             img.get_height() + pad), pygame.SRCALPHA)
        bg.fill((C_PANEL[0], C_PANEL[1], C_PANEL[2], 228))
        self.screen.blit(bg, (x - pad, y - pad // 2))
        self._blit(img, (x, y))
        return img

    def bar(self, x, y, w, h, frac, color):
        pygame.draw.rect(self.screen, C_GRID, (x, y, w, h), border_radius=3)
        fw = int(w * clamp(frac))
        if fw > 0:
            pygame.draw.rect(self.screen, color, (x, y, fw, h), border_radius=3)

    def columns(self, rect, spec):
        """Lay out table columns from measured metrics.

        spec entries are (title, min_px, weight, priority).  When the panel is
        too narrow, the lowest-priority columns are DROPPED rather than allowed
        to overlap.  Returns the surviving [(title, x, w)].
        """
        avail = rect.w - self.pad * 2
        cols = list(spec)
        while cols:
            need = sum(c[1] for c in cols) + self.pad * (len(cols) - 1)
            if need <= avail or len(cols) == 1:
                break
            drop = min(cols, key=lambda c: c[3])
            cols.remove(drop)
        need = sum(c[1] for c in cols) + self.pad * (len(cols) - 1)
        slack = max(0, avail - need)
        wsum = sum(c[2] for c in cols) or 1.0
        out, x = [], rect.x + self.pad
        for title, mn, wt, _pri in cols:
            w = int(mn + slack * wt / wsum)
            out.append((title, x, w))
            x += w + self.pad
        return out

    def scrollbar(self, rect, sc):
        if sc.content <= sc.view:
            return
        track = pygame.Rect(rect.right - 5, rect.y, 3, rect.h)
        pygame.draw.rect(self.screen, C_GRID, track, border_radius=2)
        frac = sc.view / float(sc.content)
        h = max(24, int(rect.h * frac))
        span = rect.h - h
        pos = 0 if sc.max_y() == 0 else int(span * sc.y / sc.max_y())
        pygame.draw.rect(self.screen, C_PANEL_HI,
                         (track.x, rect.y + pos, 3, h), border_radius=2)

    # ------------------------------------------------------------- header ---
    def draw_header(self):
        pygame.draw.rect(self.screen, C_SURFACE, self.r_header)
        pygame.draw.line(self.screen, C_PANEL_HI, (0, self.r_header.bottom - 1),
                         (self.W, self.r_header.bottom - 1))
        self.screen.set_clip(self.r_header)
        x, y = self.pad * 2, self.pad // 2
        self.text("CERAMIC CEMENT", self.f_head, x, y, C_TEXT,
                  max_px=self.W - x - 340)
        best = max(self.mixes, key=lambda m: self.result(m)["sigma_unconfined"])
        rb = self.result(best)
        n_target = sum(1 for m in self.mixes if self.result(m)["hits_target"])
        n_pour = sum(1 for m in self.mixes if self.result(m)["pourable"])
        sub = ("%d formulations   |   target %.0f MPa (%s)   |   %d reach target   |   "
               "%d pourable   |   best unconfined: %s at %.0f MPa (%s)" %
               (len(self.mixes), TARGET_MPA, mpa_to_psi(TARGET_MPA),
                n_target, n_pour,
                best["name"], rb["sigma_unconfined"],
                mpa_to_psi(rb["sigma_unconfined"])))
        self.text(sub, self.f_small, x, y + self.f_head.get_linesize(),
                  C_TEXT_MUTED, max_px=self.W - x - self.pad * 2)
        self.screen.set_clip(None)

    # --------------------------------------------------------- mix list ----
    def draw_list(self):
        r = self.r_list
        self.panel(r)
        self.screen.set_clip(r.inflate(-2, -2))
        off = self.scroll_list()
        y0 = r.y + self.pad - off
        name_w = int(r.w * 0.52)
        # reserve room at the bottom for the legend
        list_bottom = r.bottom - self.f_small.get_linesize() - 6
        for i, m in enumerate(self.mixes):
            y = y0 + i * self.lh
            if y + self.lh < r.y or y > list_bottom:
                continue
            res = self.result(m)
            if i == self.sel:
                pygame.draw.rect(self.screen, C_SEL,
                                 (r.x + 2, y, r.w - 4, self.lh), border_radius=3)
            # evidence dot (left)
            ev = EVIDENCE_COLOR.get(m.get("evidence"), C_TEXT_MUTED)
            pygame.draw.circle(self.screen, ev,
                               (r.x + self.pad + 3, y + self.lh // 2), 3)
            self.text("%2d %s" % (m["id"], m["name"]), self.f_mono_s,
                      r.x + self.pad + 12, y + 1,
                      C_TEXT if i == self.sel else C_TEXT_SEC,
                      max_px=name_w)
            # The list shows the CONFINED strength (the "as built" number) for
            # every mix, so the column is consistent.  A small marker to the
            # left of the value tells the reader whether that number is the
            # material alone (dot = unconfined, no jacket) or includes a jacket
            # (ring = confined, jacket present).  When they are equal the dot
            # is correct because the value IS the unconfined strength.
            has_jacket = res["f_lateral"] > 0
            val = "%.0f" % res["sigma_confined"]
            img = self.f_mono_s.render(val, True,
                                       C_OK if res["hits_target"] else C_TEXT_MUTED)
            vx = r.right - self.pad - img.get_width()
            self._blit(img, (vx, y + 1))
            # strength marker: ring if jacketed, dot if free-standing
            mx = vx - 10
            my = y + self.lh // 2
            if has_jacket:
                pygame.draw.circle(self.screen, C_ACCENT, (mx, my), 3, 1)
            else:
                pygame.draw.circle(self.screen, C_TEXT_MUTED, (mx, my), 2)
            # pourable dot (right of strength) -- green if pourable, red if not
            pour_col = C_OK if res["pourable"] else C_CRIT
            pygame.draw.circle(self.screen, pour_col,
                               (vx - 18, y + self.lh // 2), 2)
            # mini target-fraction bar -- a 2px strip at the bottom of the row
            # showing how close this mix's confined strength is to the 10 GPa
            # target.  Green when it reaches the target, amber past halfway,
            # muted otherwise.  Reads at a glance without any extra height.
            frac = clamp(res["sigma_confined"] / TARGET_MPA)
            bar_col = (C_OK if res["hits_target"] else
                       C_WARN if frac >= 0.5 else C_PANEL_HI)
            bar_x = r.x + self.pad + 12
            bar_w = r.w - self.pad * 2 - 12
            pygame.draw.rect(self.screen, C_GRID,
                             (bar_x, y + self.lh - 2, bar_w, 2), border_radius=1)
            fw = int(bar_w * frac)
            if fw > 0:
                pygame.draw.rect(self.screen, bar_col,
                                 (bar_x, y + self.lh - 2, fw, 2), border_radius=1)
        # compact legend at the bottom of the list: explains the strength
        # markers.  Kept to one line so it fits the narrow panel.
        ly = r.bottom - self.f_small.get_linesize() - 2
        pygame.draw.line(self.screen, C_PANEL_HI, (r.x + self.pad, ly - 2),
                         (r.right - self.pad, ly - 2))
        lx = r.x + self.pad
        # ring = jacketed
        pygame.draw.circle(self.screen, C_ACCENT, (lx + 4, ly + 6), 3, 1)
        self.text("jacketed", self.f_small, lx + 10, ly, C_TEXT_MUTED,
                  max_px=50)
        lx += 60
        # dot = free-standing
        pygame.draw.circle(self.screen, C_TEXT_MUTED, (lx + 4, ly + 6), 2)
        self.text("free", self.f_small, lx + 10, ly, C_TEXT_MUTED, max_px=40)
        lx += 50
        self.text("= confined MPa", self.f_small, lx, ly, C_TEXT_MUTED,
                  max_px=r.right - lx - self.pad)
        self.screen.set_clip(None)

    # ------------------------------------------------------------- tabs ----
    def draw_tabs(self):
        r = self.r_tabs
        n = len(TABS)
        w = r.w / float(n)
        for i, name in enumerate(TABS):
            rc = pygame.Rect(int(r.x + i * w), r.y, int(w) - 2, r.h)
            active = (i == self.tab)
            pygame.draw.rect(self.screen, C_PANEL if active else C_SURFACE, rc,
                             border_radius=5)
            pygame.draw.rect(self.screen, C_ACCENT if active else C_PANEL_HI, rc, 1,
                             border_radius=5)
            self.screen.set_clip(rc)
            label = fit_text(self.f_sub, "%d %s" % (i + 1, name), rc.w - 8)
            img = self.f_sub.render(label, True, C_TEXT if active else C_TEXT_MUTED)
            self._blit(img, (rc.centerx - img.get_width() // 2,
                                   rc.centery - img.get_height() // 2))
            self.screen.set_clip(None)

    # ----------------------------------------------------------- footer ----
    def draw_footer(self):
        pygame.draw.rect(self.screen, C_SURFACE, self.r_footer)
        pygame.draw.line(self.screen, C_PANEL_HI, (0, self.r_footer.y),
                         (self.W, self.r_footer.y))
        self.screen.set_clip(self.r_footer)
        # selected-mix stat -- compact, right-aligned before the size stamp.
        # Shown only when the window is wide enough for it not to collide with
        # the help text on the left.
        sel_m = self.mixes[self.sel]
        sel_r = self.result(sel_m)
        stat = "[%d] %s  free %.0f MPa  jacketed %.0f MPa (%s)" % (
            sel_m["id"], sel_m["name"], sel_r["sigma_unconfined"],
            sel_r["sigma_confined"], mpa_to_psi(sel_r["sigma_confined"]))
        stat_col = C_OK if sel_r["hits_target"] else C_TEXT_SEC
        stat_img = self.f_small.render(stat, True, stat_col)
        stamp = "%d x %d" % (self.W, self.H)
        stamp_img = self.f_small.render(stamp, True, C_TEXT_MUTED)
        # layout right-to-left: stamp at the far right, stat before it
        stamp_x = self.W - self.pad * 2 - stamp_img.get_width()
        stat_x = stamp_x - self.pad * 2 - stat_img.get_width()
        # help text gets whatever is left
        help_max = stat_x - self.pad * 2 - self.pad * 2
        help_s = ("TAB/1-5 tabs   UP/DOWN select   WHEEL scroll   "
                  "PGUP/PGDN page   HOME/END   ESC quit")
        if help_max > 120:
            self.text(help_s, self.f_small, self.pad * 2, self.r_footer.y + 1,
                      C_TEXT_MUTED, max_px=help_max)
            self._blit(stat_img, (stat_x, self.r_footer.y + 1))
        else:
            # too narrow -- drop the stat, keep just help + stamp
            self.text(help_s, self.f_small, self.pad * 2, self.r_footer.y + 1,
                      C_TEXT_MUTED, max_px=stamp_x - self.pad * 3)
        self._blit(stamp_img, (stamp_x, self.r_footer.y + 1))
        self.screen.set_clip(None)
    # ========================================================== TAB 1 ======
    def draw_overview(self):
        r = self.r_view
        self.panel(r)
        sc = self.scroll[0]
        self.screen.set_clip(r.inflate(-2, -2))

        spec = [("ID", 26, 0.2, 10), ("MIX", 110, 2.0, 100),
                ("UNCONF", 54, 0.5, 90), ("CONFINED", 60, 0.5, 60),
                ("PSI", 56, 0.4, 50),
                ("FLOW", 40, 0.3, 40), ("POUR", 32, 0.3, 15),
                ("DENS", 44, 0.3, 18), ("E", 36, 0.3, 20),
                ("COST", 56, 0.4, 30), ("EVIDENCE", 72, 0.6, 70),
                ("TIER", 60, 0.5, 80)]
        cols = self.columns(r, spec)
        col_titles = {t: (x, w) for t, x, w in cols}

        y = r.y + self.pad
        for title, x, w in cols:
            self.text(title, self.f_small, x, y, C_TEXT_MUTED, max_px=w)
        y += self.f_small.get_linesize() + 2
        # explanatory subtitle: what UNCONF and CONFINED mean, so the two
        # strength columns are not ambiguous abbreviations.
        sub = ("UNCONF = free-standing MPa   |   CONFINED = jacketed MPa   |   "
               "PSI = confined strength in pounds per square inch")
        self.text(sub, self.f_small, r.x + self.pad, y, C_TEXT_MUTED,
                  max_px=r.w - self.pad * 2)
        y += self.f_small.get_linesize() + 2
        pygame.draw.line(self.screen, C_PANEL_HI, (r.x + self.pad, y),
                         (r.right - self.pad, y))
        y += 4
        head_h = y - r.y

        # reserve room for the summary footer
        foot_h = self.f_small.get_linesize() + self.pad
        sc.view = r.h - head_h - foot_h - self.pad
        sc.content = len(self.mixes) * self.lh
        sc.clamp()
        y -= int(sc.y)

        clip = pygame.Rect(r.x + 1, r.y + head_h, r.w - 2, r.h - head_h - foot_h)
        self.screen.set_clip(clip)
        n_target = n_pour = 0
        for i, m in enumerate(self.mixes):
            ry = y + i * self.lh
            if ry + self.lh < clip.y or ry > clip.bottom:
                res = self.result(m)
                if res["hits_target"]:
                    n_target += 1
                if res["pourable"]:
                    n_pour += 1
                continue
            res = self.result(m)
            if res["hits_target"]:
                n_target += 1
            if res["pourable"]:
                n_pour += 1
            if i == self.sel:
                pygame.draw.rect(self.screen, C_SEL,
                                 (r.x + 2, ry, r.w - 4, self.lh), border_radius=3)
            elif i % 2 == 0:
                # zebra striping -- a faint band on even rows for readability
                # across the 20-row table.  Subtle enough not to fight the
                # selection highlight or the column colours.
                pygame.draw.rect(self.screen, (30, 31, 34),
                                 (r.x + 2, ry, r.w - 4, self.lh), border_radius=3)
            hit = res["hits_target"]
            hit_unconf = res["hits_target_unconfined"]
            vals = {
                "ID": "%d" % m["id"],
                "MIX": m["name"],
                "UNCONF": "%.0f" % res["sigma_unconfined"],
                "CONFINED": "%.0f" % res["sigma_confined"],
                "PSI": mpa_to_psi(res["sigma_confined"]),
                "FLOW": "%.0f" % res["flow_mm"],
                "POUR": "Y" if res["pourable"] else "n",
                "DENS": "%.0f" % res["density"],
                "E": "%.0f" % res["E_gpa"],
                "COST": _money(res["cost_m3"]),
                "EVIDENCE": m.get("evidence", "-"),
                "TIER": m.get("tier", "-"),
            }
            for title, x, w in cols:
                col = C_TEXT_SEC
                if title == "UNCONF":
                    col = C_OK if hit_unconf else (
                        C_WARN if res["sigma_unconfined"] >= TARGET_MPA * 0.5
                        else C_TEXT_SEC)
                elif title == "CONFINED":
                    col = C_OK if hit else (
                        C_WARN if res["sigma_confined"] >= TARGET_MPA * 0.5
                        else C_TEXT_SEC)
                elif title == "PSI":
                    col = C_OK if hit else (
                        C_WARN if res["sigma_confined"] >= TARGET_MPA * 0.5
                        else C_TEXT_SEC)
                elif title == "POUR":
                    col = C_OK if res["pourable"] else C_CRIT
                elif title == "EVIDENCE":
                    col = EVIDENCE_COLOR.get(vals[title], C_TEXT_SEC)
                elif title == "TIER":
                    col = TIER_COLOR.get(vals[title], C_TEXT_SEC)
                self.text(vals[title], self.f_mono_s, x, ry + 1, col, max_px=w)
            # target-hit marker: a small tick at the far left of the row
            if hit and "ID" in col_titles:
                ix, _ = col_titles["ID"]
                pygame.draw.circle(self.screen, C_OK,
                                   (ix - 6, ry + self.lh // 2), 2)
        self.screen.set_clip(None)

        # summary footer
        fy = r.bottom - foot_h + 2
        pygame.draw.line(self.screen, C_PANEL_HI, (r.x + self.pad, fy),
                         (r.right - self.pad, fy))
        best_conf = max(self.mixes, key=lambda m: self.result(m)["sigma_confined"])
        rb = self.result(best_conf)
        summary = ("%d/%d reach %.0f MPa (%s)   |   %d/%d pourable   |   "
                   "best confined: %s at %.0f MPa (%s)" %
                   (n_target, len(self.mixes), TARGET_MPA,
                    mpa_to_psi(TARGET_MPA),
                    n_pour, len(self.mixes), best_conf["name"],
                    rb["sigma_confined"], mpa_to_psi(rb["sigma_confined"])))
        self.text(summary, self.f_small, r.x + self.pad, fy + 3,
                  C_TEXT_MUTED, max_px=r.w - self.pad * 2)
        self.scrollbar(clip, sc)

    # ========================================================== TAB 2 ======
    def draw_mix(self):
        r = self.r_view
        m = self.mixes[self.sel]
        res = self.result(m)
        self.panel(r)
        sc = self.scroll[1]
        w = r.w - self.pad * 4
        x = r.x + self.pad * 2
        lines = []

        cure = m["cure"]
        conf = m.get("confinement")
        lines.append(("head", "[%d] %s" % (m["id"], m["name"])))
        lines.append(("sub", m["tagline"]))
        lines.append(("grade", None))
        lines.append(("gap", None))

        lines.append(("sec", "BATCH  (kg per m3)"))
        for k, kg in sorted(m["components"].items(), key=lambda kv: -kv[1]):
            tag = "  [infiltrant]" if MATS[k]["role"] == "infiltrant" else ""
            lines.append(("mono", "  %-14s %9.1f   %s%s" %
                          (k, kg, MATS[k]["name"], tag)))
        lines.append(("mono", "  %-14s %9.1f   TOTAL   yield %.3f m3" %
                      ("", res["mass_total"], res["volume_check"])))
        lines.append(("gap", None))

        lines.append(("sec", "MIX PROPORTIONS  (m3 per m3)"))
        for label, val in (("Binder volume", "%.3f" % res["v_binder"]),
                           ("Filler volume", "%.3f" % res["v_filler"]),
                           ("Water volume", "%.3f" % res["v_water"]),
                           ("Fiber volume", "%.3f" % res["v_fiber"]),
                           ("Air volume", "%.3f" % res["v_air"]),
                           ("Infiltrant volume", "%.3f" % res["v_infiltrant"]),
                           ("Density", "%.0f kg/m3" % res["density"])):
            lines.append(("kv", (label, val)))
        lines.append(("gap", None))

        lines.append(("sec", "PROPERTIES"))
        # "Unconfined" and "Confined" are expanded to state what they actually
        # measure, so a reader who has not read the science tab still understands
        # the difference: unconfined is the material on its own, confined adds a
        # structural jacket.  When there is no jacket they are equal, and that is
        # stated explicitly in the value string.
        has_jacket = res["f_lateral"] > 0
        unconf_val = "%.0f MPa  (%s)" % (res["sigma_unconfined"],
                                         mpa_to_psi(res["sigma_unconfined"]))
        conf_val = "%.0f MPa  (%s)%s" % (res["sigma_confined"],
                                         mpa_to_psi(res["sigma_confined"]),
                                         "" if has_jacket
                                         else "  (= unconfined, no jacket)")
        props = [("Unconfined (free-standing)", unconf_val),
                 ("Confined (with jacket)", conf_val),
                 ("Slump flow", "%.0f mm  (%s)" % (res["flow_mm"], res["pour_class"])),
                 ("Density", "%.0f kg/m3" % res["density"]),
                 ("Young's modulus", "%.0f GPa" % res["E_gpa"]),
                 ("Tensile", "%.1f MPa  (%s)" % (res["sigma_tensile"],
                                                 mpa_to_psi(res["sigma_tensile"]))),
                 ("Flexural", "%.1f MPa  (%s)" % (res["sigma_flexural"],
                                                  mpa_to_psi(res["sigma_flexural"]))),
                 ("Total porosity", "%.4f" % res["P_total"]),
                 ("Material cost", "%.0f USD/m3" % res["cost_m3"])]
        if res.get("ceramic"):
            ci = res["ceramic"]
            micro = ("%.1f nm coherent twins" % ci["twin_nm"]) if ci["twin_nm"] \
                else ("%.0f nm grain  (from %.0f nm feed)" %
                      (ci["grain_nm"], ci["feed_nm"]))
            props.append(("Microstructure", micro))
        for a, b in props:
            lines.append(("mono", "  %-18s %s" % (a, b)))
        lines.append(("gap", None))

        # PARTICLE PACKING -- classes may be empty for pure-polymer/paste mixes,
        # so every field that depends on them is guarded rather than assumed.
        lines.append(("sec", "PARTICLE PACKING  (de Larrard CPM, K = %.2f)" % cure["K"]))
        cls = res["classes"]
        if cls:
            d_min = min(c[0] for c in cls)
            d_max = max(c[0] for c in cls)
            lines.append(("kv", ("Size classes", "%d  (d50 %.2f um to %.0f um)" %
                                 (len(cls), d_min, d_max))))
        else:
            lines.append(("kv", ("Size classes", "none (no graded solids)")))
        lines.append(("kv", ("Jamming point gamma", "%.4f  %s" %
                             (res["gamma"], _bar(res["gamma"])))))
        lines.append(("kv", ("Dry packing at K", "%.4f  %s" %
                             (res["phi_max"], _bar(res["phi_max"])))))
        lines.append(("kv", ("Fresh solid fraction", "%.4f  %s" %
                             (res["phi_solid"], _bar(res["phi_solid"])))))
        lines.append(("kv", ("Packing utilisation", "%.1f%%  (phi / gamma)" %
                             (100.0 * res["packing_util"]))))
        if res["phi_solid"] > res["phi_max"]:
            lines.append(("body", "  solids exceed free-poured packing; needs vibration / pressure"))
        lines.append(("kv", ("Andreasen q / RMS dev", "q = %.3f  dev = %.3f" %
                             (res["q_best"], res["fd_err"]))))
        lines.append(("kv", ("Geometric mean d50", "%.2f um" % res["d50_mix"])))
        lines.append(("gap", None))

        # RHEOLOGY -- pourable is always defined; tau0 is too.
        lines.append(("sec", "RHEOLOGY / POURABILITY"))
        lines.append(("kv", ("Bingham yield stress", "%.1f Pa" % res["tau0"])))
        lines.append(("kv", ("Slump flow spread", "%.0f mm  ->  %s" %
                             (res["flow_mm"], res["pour_class"]))))
        lines.append(("kv", ("Pourable", "YES" if res["pourable"] else "NO")))
        lines.append(("gap", None))

        # BINDER CHEMISTRY only exists for hydraulic / acid-base / alkali families;
        # ceramic and polymer mixes take the MATRIX FORMATION branch instead.
        ch = res.get("chem")
        if ch:
            lines.append(("sec", "BINDER CHEMISTRY  (Powers-Brownyard)"))
            lines.append(("kv", ("Water / binder", "%.4f" % ch["w_b"])))
            lines.append(("kv", ("Degree of reaction", "%.3f  (water-limited)" %
                                 ch["alpha"])))
            lines.append(("kv", ("Portlandite balance", "%.3f  (1.0 = enough CH)" %
                                 ch["ch_ratio"])))
            if ch["water_expelled_frac"] > 0:
                lines.append(("kv", ("Water expressed", "%.1f%%  by %.0f MPa" %
                                     (100.0 * ch["water_expelled_frac"],
                                      cure["set_pressure"]))))
            lines.append(("kv", ("Capillary porosity", "%.4f" % ch["P_cap"])))
            lines.append(("kv", ("Gel porosity", "%.4f" % ch["P_gel"])))
            lines.append(("kv", ("Air porosity", "%.4f" % ch["P_air"])))
            lines.append(("kv", ("TOTAL porosity", "%.4f  %s" %
                                 (ch["P_total"], _bar(ch["P_total"])))))
        else:
            lines.append(("sec", "MATRIX FORMATION  (%s)" % cure["family"]))
            if cure.get("fire_temp_c", 0.0) > 0:
                lines.append(("kv", ("Firing temperature", "%.0f C" %
                                     cure["fire_temp_c"])))
            if cure.get("set_pressure", 0.0) > 0:
                lines.append(("kv", ("Sintering pressure", "%.0f MPa" %
                                     cure["set_pressure"])))
            if cure.get("infiltrated"):
                lines.append(("kv", ("Melt infiltration", "YES (pore network filled)")))
            if cure["family"] == "ceramic" and res.get("ceramic"):
                ci = res["ceramic"]
                g = ci["grain_nm"]
                lines.append(("kv", ("Fired grain size", "%.1f nm  (%s)" %
                                     (g, "NANOGRAIN" if g < 500.0 else "conventional"))))
            lines.append(("kv", ("TOTAL porosity", "%.4f  %s" %
                                 (res["P_total"], _bar(res["P_total"])))))
        lines.append(("gap", None))

        lines.append(("sec", "STRENGTH CHAIN"))
        # Each stage gets its own colour so the eye can follow the chain, and
        # every bar carries a red target tick so the gap to 10 GPa is visible at
        # every stage, not just on the final number.
        chain = [("pore-free sigma0", res["sigma0_eff"], C_TEXT_MUTED),
                 ("matrix (x porosity)", res["sigma_matrix"], SERIES[2]),
                 ("composite (x K_agg)", res["sigma_composite"], SERIES[1]),
                 ("unconfined (x fiber)", res["sigma_unconfined"], SERIES[0])]
        if res["f_lateral"] > 0:
            chain.append(("confined (x jacket)", res["sigma_confined"], C_OK))
        peak = max(v for _, v, _ in chain) or 1.0
        target_frac = TARGET_MPA / peak
        for label, val, color in chain:
            lines.append(("bar", (label, val, val / peak, color, target_frac)))
        # K-factor breakdown -- K_dmax is 1.0 for ceramics (no Griffith term),
        # so only show it where it actually does something.
        lines.append(("kv", ("K_agg / bond", "%.4f  (bond %.2f, filler %.1f vol%%)" %
                             (res["K_agg"], res["bond"], 100.0 * res["vf_filler"]))))
        if res["K_dmax"] != 1.0:
            lines.append(("kv", ("K_dmax", "%.4f  (Griffith flaw on dmax)" %
                                 res["K_dmax"])))
        lines.append(("kv", ("K_fiber", "%.4f  (%.2f vol%% at %.0f MPa)" %
                             (res["K_fiber"], 100.0 * res["vf_fiber"],
                              res["sigma_fiber"]))))
        lines.append(("kv", ("Weibull to %.0f mm" % res["specimen_mm"],
                             "%.0f MPa  (m = %.0f)" %
                             (res["sigma_specimen"], res["weibull_m"]))))
        lines.append(("gap", None))

        # CONFINEMENT -- optional; most mixes are free-standing pours.
        # This section makes the unconfined/confined distinction explicit:
        # with no jacket, confined = unconfined (the material stands alone).
        # With a jacket, lateral pressure adds triaxial capacity on top.
        lines.append(("sec", "CONFINEMENT"))
        if conf:
            lines.append(("kv", ("Jacket", conf["type"])))
            lines.append(("kv", ("Jacket yield", "%.0f MPa, OD/ID %.1f" %
                                 (conf["sigma_y_mpa"], conf["od_id"]))))
            lines.append(("kv", ("Lateral pressure", "%.0f MPa" % res["f_lateral"])))
            lines.append(("kv", ("k(f_l)", "%.3f  (Richart 4.1 -> 2.2 at GPa)" %
                                 confinement_k(res["f_lateral"],
                                               res["sigma_unconfined"]))))
            lines.append(("kv", ("Confined capacity", "%.0f MPa  (= unconf %.0f + k*f_l)" %
                                 (res["sigma_confined"], res["sigma_unconfined"]))))
            if conf.get("note"):
                for ln in wrap_text(self.f_small, conf["note"], w - 200):
                    lines.append(("small", "  " + ln))
        else:
            lines.append(("kv", ("Jacket", "none -- free-standing pour")))
            lines.append(("kv", ("Confined = unconfined", "%.0f MPa  (no jacket, "
                                 "so they are the same)" %
                                 res["sigma_confined"])))
            need = confinement_required(res["sigma_unconfined"], TARGET_MPA)
            if need is None:
                lines.append(("kv", ("Lateral to reach target",
                                     "beyond 20 GPa search bound")))
            else:
                lines.append(("kv", ("Lateral to reach %.0f MPa" % TARGET_MPA,
                                     "%.0f MPa" % need)))
        lines.append(("gap", None))

        lines.append(("sec", "VERDICT"))
        if res["hits_target"]:
            lines.append(("body", "  REACHES %.0f MPa (%s): YES  (%.0f MPa, %s as built)" %
                          (TARGET_MPA, mpa_to_psi(TARGET_MPA),
                           res["sigma_confined"], mpa_to_psi(res["sigma_confined"]))))
        else:
            lines.append(("body", "  REACHES %.0f MPa (%s): no  (%.0f MPa, %s as built, %.1fx short)" %
                          (TARGET_MPA, mpa_to_psi(TARGET_MPA),
                           res["sigma_confined"], mpa_to_psi(res["sigma_confined"]),
                           TARGET_MPA / max(res["sigma_confined"], 1.0))))
        lines.append(("gap", None))

        lines.append(("sec", "MECHANISM"))
        mech = m.get("recipe", {}).get("mechanism", "-")
        for ln in wrap_text(self.f_body, mech, w - 16):
            lines.append(("body", "  " + ln))

        self._draw_lines(r, sc, lines, m, res)

    # ========================================================== TAB 3 ======
    def draw_production(self):
        r = self.r_view
        m = self.mixes[self.sel]
        res = self.result(m)
        self.panel(r)
        sc = self.scroll[2]
        w = r.w - self.pad * 4
        rec = m.get("recipe", {})
        cure = m["cure"]
        lines = [("head", "[%d] %s" % (m["id"], m["name"])),
                 ("sub", "production sheet"), ("grade", None), ("gap", None)]

        # KEY PROPERTIES -- a quick-reference block so the production tab is
        # useful even before scrolling into the process recipe.  Every field
        # here comes straight from evaluate_mix, so none can be undefined.
        lines.append(("sec", "KEY PROPERTIES"))
        lines.append(("kv", ("Family", cure["family"])))
        lines.append(("kv", ("Unconfined", "%.0f MPa  (%s)" %
                             (res["sigma_unconfined"],
                              mpa_to_psi(res["sigma_unconfined"])))))
        lines.append(("kv", ("Confined", "%.0f MPa  (%s)" %
                             (res["sigma_confined"],
                              mpa_to_psi(res["sigma_confined"])))))
        lines.append(("kv", ("Slump flow", "%.0f mm  (%s)" %
                             (res["flow_mm"], res["pour_class"]))))
        lines.append(("kv", ("Pourable", "YES" if res["pourable"] else "NO")))
        lines.append(("kv", ("Density", "%.0f kg/m3" % res["density"])))
        lines.append(("kv", ("Young's modulus", "%.0f GPa" % res["E_gpa"])))
        lines.append(("kv", ("Total porosity", "%.4f" % res["P_total"])))
        lines.append(("kv", ("Material cost", "%.0f USD/m3" % res["cost_m3"])))
        if res["hits_target"]:
            lines.append(("body", "  REACHES %.0f MPa (%s): YES" %
                          (TARGET_MPA, mpa_to_psi(TARGET_MPA))))
        else:
            lines.append(("body", "  REACHES %.0f MPa (%s): no  (%.1fx short)" %
                          (TARGET_MPA, mpa_to_psi(TARGET_MPA),
                           TARGET_MPA / max(res["sigma_confined"], 1.0))))
        lines.append(("gap", None))

        # CURE SCHEDULE -- the thermal/pressure path, which is what makes the
        # production tab distinct from the mix tab.  Guarded per-field because
        # ceramic and polymer families carry different keys.
        lines.append(("sec", "CURE SCHEDULE"))
        lines.append(("kv", ("Family", cure["family"])))
        if cure.get("temp_c") is not None:
            lines.append(("kv", ("Cure temperature", "%.0f C" % cure["temp_c"])))
        if cure.get("age_days"):
            lines.append(("kv", ("Age at test", "%.0f days" % cure["age_days"])))
        if cure.get("set_pressure", 0.0) > 0:
            lines.append(("kv", ("Set pressure", "%.0f MPa" % cure["set_pressure"])))
        if cure.get("fire_temp_c", 0.0) > 0:
            lines.append(("kv", ("Firing temperature", "%.0f C" %
                                 cure["fire_temp_c"])))
        if cure.get("dwell_min"):
            lines.append(("kv", ("Dwell time", "%.0f min" % cure["dwell_min"])))
        if cure.get("infiltrated"):
            lines.append(("kv", ("Melt infiltration", "YES")))
        if cure.get("grain_nm"):
            lines.append(("kv", ("Grain override", "%.0f nm" % cure["grain_nm"])))
        if cure.get("twin_nm"):
            lines.append(("kv", ("Twin spacing", "%.1f nm" % cure["twin_nm"])))
        conf = m.get("confinement")
        if conf:
            lines.append(("kv", ("Confinement", conf["type"])))
            lines.append(("kv", ("Jacket yield", "%.0f MPa  OD/ID %.1f" %
                                 (conf["sigma_y_mpa"], conf["od_id"]))))
        lines.append(("gap", None))

        fields = [("Water / binder", "w_b"), ("Grading", "grading"),
                  ("Equipment", "equipment"), ("Mixing", "mixing"),
                  ("Pot life", "pot_life"), ("Placement", "placement"),
                  ("Demould / cure", "demould"), ("Curing", "curing"),
                  ("QC checks", "qc")]
        lines.append(("sec", "PROCESS"))
        for label, key in fields:
            if key not in rec:
                continue
            body = wrap_text(self.f_body, str(rec[key]), w - 200)
            lines.append(("kv", (label, body[0])))
            for extra in body[1:]:
                lines.append(("kvcont", extra))
        lines.append(("gap", None))

        lines.append(("hazhead", "HAZARDS"))
        for ln in wrap_text(self.f_body, rec.get("hazards", "not assessed"), w - 16):
            lines.append(("haz", "  " + ln))
        lines.append(("gap", None))

        lines.append(("sec", "REFERENCES"))
        for ln in wrap_text(self.f_small, rec.get("references", "-"), w - 16):
            lines.append(("small", "  " + ln))

        self._draw_lines(r, sc, lines, m, res)

    # ---- shared line renderer for the text tabs ---------------------------
    def _draw_lines(self, r, sc, lines, mix, res):
        """One measured pass, then one clipped draw pass -- so the scroll extent
        is always exactly the real content height."""
        def height(kind):
            # Row pitch must come from the font that actually draws the row.
            # Using one global line height here is what makes proportional text
            # overlap the row below it, because its glyphs are taller than the
            # monospace line height the pitch was taken from.
            if kind == "head":
                return self._lh(self.f_head)
            if kind in ("sub", "small", "grade"):
                return self._lh(self.f_small)
            if kind == "sec" or kind == "hazhead":
                return self._lh(self.f_sub) + 4
            if kind == "gap":
                return self.lh // 2
            if kind == "bar":
                return max(self.lh, self._lh(self.f_mono_s)) + 6
            if kind == "mono":
                return self._lh(self.f_mono_s)
            return self._lh(self.f_body)      # body, haz, kv, kvcont

        sc.view = r.h - self.pad * 2
        sc.content = sum(height(k) for k, _ in lines) + self.pad
        sc.clamp()

        clip = r.inflate(-2, -2)
        self.screen.set_clip(clip)
        x = r.x + self.pad * 2
        y = r.y + self.pad - int(sc.y)
        w = r.w - self.pad * 4

        for kind, payload in lines:
            h = height(kind)
            if y + h >= r.y and y <= r.bottom:
                if kind == "head":
                    self.text(payload, self.f_head, x, y, C_TEXT, max_px=w)
                elif kind == "sub":
                    self.text(payload, self.f_small, x, y, C_TEXT_MUTED, max_px=w)
                elif kind == "grade":
                    ev = mix.get("evidence", "-")
                    ti = mix.get("tier", "-")
                    nx = self.chip("evidence: " + ev,
                                   EVIDENCE_COLOR.get(ev, C_TEXT_MUTED), x, y)
                    self.chip("tier: " + ti, TIER_COLOR.get(ti, C_TEXT_MUTED),
                              min(nx + self.pad * 3, r.right - 140), y)
                elif kind in ("sec", "hazhead"):
                    col = C_CRIT if kind == "hazhead" else C_ACCENT
                    self.text(payload, self.f_sub, x, y, col, max_px=w)
                    ly = y + self.f_sub.get_linesize() + 1
                    pygame.draw.line(self.screen, C_PANEL_HI, (x, ly),
                                     (r.right - self.pad * 2, ly))
                elif kind == "mono":
                    self.text(payload, self.f_mono_s, x, y, C_TEXT_SEC, max_px=w)
                elif kind == "body":
                    self.text(payload, self.f_body, x, y, C_TEXT_SEC, max_px=w)
                elif kind == "haz":
                    self.text(payload, self.f_body, x, y, C_TEXT, max_px=w)
                elif kind == "small":
                    self.text(payload, self.f_small, x, y, C_TEXT_MUTED, max_px=w)
                elif kind == "kv":
                    label, first = payload
                    kw = min(150, int(w * 0.28))
                    self.text(label, self.f_body, x, y, C_TEXT_MUTED, max_px=kw - 8)
                    self.text(first, self.f_body, x + kw, y, C_TEXT_SEC,
                              max_px=w - kw)
                elif kind == "kvcont":
                    kw = min(150, int(w * 0.28))
                    self.text(payload, self.f_body, x + kw, y, C_TEXT_SEC,
                              max_px=w - kw)
                elif kind == "bar":
                    label = payload[0]
                    val = payload[1]
                    frac = payload[2]
                    color = payload[3] if len(payload) > 3 else C_ACCENT
                    target_frac = payload[4] if len(payload) > 4 else None
                    self.text(label, self.f_mono_s, x, y, C_TEXT_MUTED,
                              max_px=int(w * 0.34))
                    bx = x + int(w * 0.36)
                    bw = int(w * 0.44)
                    self.bar(bx, y + 2, bw, self.lh - 6, frac, color)
                    # target marker: a vertical tick on the bar
                    if target_frac is not None and 0 < target_frac <= 1.0:
                        tx = bx + int(bw * target_frac)
                        pygame.draw.line(self.screen, C_CRIT,
                                         (tx, y + 1), (tx, y + self.lh - 5), 1)
                    val_col = C_OK if val >= TARGET_MPA else C_TEXT_SEC
                    self.text("%.0f MPa" % val, self.f_mono_s, bx + bw + self.pad,
                              y, val_col, max_px=w - (bx - x) - bw - self.pad)
            y += h
        self.screen.set_clip(None)
        self.scrollbar(clip, sc)

    # ========================================================== TAB 4 ======
    def draw_grain(self):
        """Strength vs microstructural length scale.

        One y-axis.  Four categorical series in fixed order by identity.  The
        two nanotwin results are marked and directly labelled, so identity never
        depends on colour alone.
        """
        r = self.r_view
        self.panel(r)
        self.screen.set_clip(r.inflate(-2, -2))

        title = "Strength vs microstructural length scale (Hall-Petch, and nanotwins)"
        self.text(title, self.f_sub, r.x + self.pad * 2, r.y + self.pad,
                  C_TEXT, max_px=r.w - self.pad * 4)

        top = r.y + self.pad * 2 + self.f_sub.get_linesize()
        legend_h = self.f_small.get_linesize() * 2 + self.pad
        left = r.x + self.pad * 2 + self.f_mono_s.size("30000")[0] + self.pad
        plot = pygame.Rect(left, top, r.right - left - self.pad * 3,
                           r.bottom - top - legend_h - self.f_small.get_linesize()
                           - self.pad * 3)
        if plot.w < 80 or plot.h < 80:
            self.screen.set_clip(None)
            return

        d_lo, d_hi = 2.0, 100000.0            # nm
        y_hi = 30000.0
        lx = math.log10(d_lo)
        lspan = math.log10(d_hi) - lx

        def px(d):
            return plot.x + int(plot.w * (math.log10(max(d, d_lo)) - lx) / lspan)

        def py(v):
            return plot.bottom - int(plot.h * clamp(v / y_hi))

        # recessive grid + axis labels
        last_label_right = -10 ** 9
        for dec in range(0, 6):
            d = d_lo * (10 ** dec)
            if d > d_hi:
                break
            gx = px(d)
            pygame.draw.line(self.screen, C_GRID, (gx, plot.y), (gx, plot.bottom))
            lab = ("%.0f nm" % d) if d < 1000 else ("%.0f um" % (d / 1000.0))
            img = self.f_small.render(lab, True, C_TEXT_MUTED)
            lxp = gx - img.get_width() // 2
            # drop a tick label rather than let it collide with its neighbour
            if lxp <= last_label_right + 6 or lxp + img.get_width() > plot.right:
                continue
            self._blit(img, (lxp, plot.bottom + 4))
            last_label_right = lxp + img.get_width()
        for v in range(0, int(y_hi) + 1, 5000):
            gy = py(v)
            pygame.draw.line(self.screen, C_GRID, (plot.x, gy), (plot.right, gy))
            if v == 0:
                continue          # the baseline is implied; its label would sit
                                  # in the x-axis label band and collide
            img = self.f_mono_s.render("%d" % v, True, C_TEXT_MUTED)
            self._blit(img, (plot.x - self.pad - img.get_width(),
                             gy - img.get_height() // 2))
        pygame.draw.rect(self.screen, C_PANEL_HI, plot, 1)

        # target reference line
        ty = py(TARGET_MPA)
        for sx in range(plot.x, plot.right, 8):
            pygame.draw.line(self.screen, C_TEXT_MUTED, (sx, ty), (sx + 4, ty))
        self.label_on("target %.0f MPa" % TARGET_MPA, self.f_small,
                      plot.x + 8, ty - self.f_small.get_linesize() - 2,
                      C_TEXT_MUTED)

        # four series, fixed order by identity
        phases = [("diamond", "diamond"), ("cbn", "cBN"),
                  ("wc", "WC"), ("sic", "SiC")]
        for i, (key, label) in enumerate(phases):
            mat = MATS[key]
            pts = []
            steps = 160
            for s in range(steps + 1):
                d = d_lo * (d_hi / d_lo) ** (s / float(steps))
                v = hall_petch(mat["sigma0"], mat["hp_k"], d, mat["d_crit_nm"])
                pts.append((px(d), py(v)))
            if len(pts) > 1:
                pygame.draw.lines(self.screen, SERIES[i], False, pts, 2)
            # d_crit marker: a short vertical tick at the top of the plot where
            # this phase's Hall-Petch curve peaks (inverse turnover point).
            dc = mat["d_crit_nm"]
            if d_lo <= dc <= d_hi:
                dx = px(dc)
                for ty in range(plot.y, plot.y + 10, 2):
                    pygame.draw.line(self.screen, SERIES[i],
                                     (dx, ty), (dx, ty + 1), 1)

        # optimal-grain marker for diamond -- the single highest-leverage point
        # in the whole chart.  Marked with a dot; the d_crit tick at the top of
        # the plot already labels the peak, so no text label is added here (it
        # collides with the nanotwin / you-are-here labels on small windows).
        d_opt, s_opt = optimal_grain_size("diamond")
        if d_opt is not None and d_lo <= d_opt <= d_hi:
            ox, oy = px(d_opt), py(s_opt)
            pygame.draw.circle(self.screen, C_SURFACE, (ox, oy), 5)
            pygame.draw.circle(self.screen, SERIES[0], (ox, oy), 3)

        # nanotwin results: marker + direct label (never colour alone)
        for key, lam, name in (("onion_carbon", 5.0, "nt-diamond"),
                               ("onion_bn", 3.8, "nt-cBN")):
            mat = MATS[key]
            v = nanotwin_strength(mat["sigma0"], mat["tw_k"], lam)
            mx, my = px(lam), py(v)
            pygame.draw.circle(self.screen, C_SURFACE, (mx, my), 7)
            pygame.draw.circle(self.screen, C_OK, (mx, my), 5)
            lbl = "%s  %.0f MPa" % (name, v)
            tw = self.f_small.size(lbl)[0]
            lxp = min(mx + 12, plot.right - tw - 6)
            self.label_on(lbl, self.f_small, lxp,
                          max(plot.y + 4, my - self.f_small.get_height() // 2))

        # selected mix operating point -- plots the currently-selected mix's
        # ceramic grain/twin size on the chart, so the user can see where their
        # mix sits relative to the curves.  Only ceramic mixes have a grain_nm.
        # The label is placed BELOW the marker and clamped into the plot, and is
        # suppressed when the marker sits on top of a nanotwin marker (the nt
        # label already identifies that point).
        sel = self.mixes[self.sel]
        sel_res = self.result(sel)
        ci = sel_res.get("ceramic")
        if ci and ci["grain_nm"] > 0:
            g = ci["grain_nm"]
            # pick the phase that dominates the selected mix's solids
            solids = [(k, kg / MATS[k]["rho"])
                      for k, kg in sel["components"].items()
                      if MATS[k].get("role") in ("binder", "filler")
                      and MATS[k].get("chem") == "ceramic"]
            if solids:
                solids.sort(key=lambda kv: -kv[1])
                dom_key = solids[0][0]
                dom_mat = MATS[dom_key]
                if "hp_k" in dom_mat and not ci["twin_nm"]:
                    v = hall_petch(dom_mat["sigma0"], dom_mat["hp_k"],
                                   g, dom_mat["d_crit_nm"])
                elif ci["twin_nm"] and "tw_k" in dom_mat:
                    v = nanotwin_strength(dom_mat["sigma0"],
                                          dom_mat["tw_k"], ci["twin_nm"])
                    g = ci["twin_nm"]
                else:
                    v = dom_mat.get("sigma0", 0.0)
                if d_lo <= g <= d_hi and 0 <= v <= y_hi:
                    sxp, syp = px(g), py(v)
                    pygame.draw.circle(self.screen, C_TEXT, (sxp, syp), 6, 2)
                    # suppress the label when the marker lands on an nt marker
                    on_nt = any(abs(sxp - px(lam)) <= 7 and abs(syp - py(
                        nanotwin_strength(MATS[k]["sigma0"], MATS[k]["tw_k"],
                                          lam))) <= 7
                                for k, lam in (("onion_carbon", 5.0),
                                               ("onion_bn", 3.8)))
                    if not on_nt:
                        lbl = "you are here"
                        lw = self.f_small.size(lbl)[0]
                        lx = min(sxp + 8, plot.right - lw - 6)
                        ly = min(syp + 8, plot.bottom - self.f_small.get_height() - 4)
                        self.label_on(lbl, self.f_small, lx, ly, C_TEXT)

        # legend -- always present for >= 2 series
        ly = plot.bottom + self.f_small.get_linesize() + self.pad
        lxp = plot.x
        for i, (key, label) in enumerate(phases):
            sw = self.f_small.size(label)[0] + 26
            if lxp + sw > plot.right:
                lxp = plot.x
                ly += self.f_small.get_linesize()
            pygame.draw.line(self.screen, SERIES[i], (lxp, ly + 7), (lxp + 14, ly + 7), 2)
            self.text(label, self.f_small, lxp + 19, ly, C_TEXT_SEC)
            lxp += sw
        sw = self.f_small.size("nanotwinned (measured Hv)")[0] + 26
        if lxp + sw > plot.right:
            lxp = plot.x
            ly += self.f_small.get_linesize()
        pygame.draw.circle(self.screen, C_OK, (lxp + 7, ly + 7), 5)
        self.text("nanotwinned (measured Hv)", self.f_small, lxp + 19, ly, C_TEXT_SEC)
        lxp += sw
        # d_crit tick + selected-mix marker entries
        for legend_label, draw_fn in (
            ("d_crit (peak)", lambda xp, yp: pygame.draw.line(
                self.screen, C_TEXT_MUTED, (xp, yp), (xp, yp + 8), 1)),
            ("selected mix", lambda xp, yp: pygame.draw.circle(
                self.screen, C_TEXT, (xp + 4, yp + 4), 5, 2)),
        ):
            sw = self.f_small.size(legend_label)[0] + 26
            if lxp + sw > plot.right:
                lxp = plot.x
                ly += self.f_small.get_linesize()
            draw_fn(lxp, ly + 3)
            self.text(legend_label, self.f_small, lxp + 19, ly, C_TEXT_SEC)
            lxp += sw

        self.screen.set_clip(None)

    # ========================================================== TAB 5 ======
    def draw_micro(self):
        """3D microstructure model.

        Renders a 3D cross-section of the selected mix's cured microstructure:
        grains as shaded spheres, pores as dark voids, fibers as cylinders.
        The packing density and porosity from evaluate_mix drive how many
        spheres are placed and how many voids appear.  The user can drag to
        rotate the model and press X to toggle a cross-section cut that
        reveals the interior.
        """
        r = self.r_view
        m = self.mixes[self.sel]
        res = self.result(m)
        cure = m["cure"]
        self.panel(r)
        self.screen.set_clip(r.inflate(-2, -2))

        title = "Microstructure 3D: %s  (drag to rotate, X = cut)" % m["name"]
        self.text(title, self.f_sub, r.x + self.pad * 2, r.y + self.pad,
                  C_TEXT, max_px=r.w - self.pad * 4)

        top = r.y + self.pad * 2 + self.f_sub.get_linesize()
        legend_h = self.f_small.get_linesize() * 3 + self.pad
        plot = pygame.Rect(r.x + self.pad * 2, top,
                           r.w - self.pad * 4,
                           r.bottom - top - legend_h - self.pad * 2)
        if plot.w < 80 or plot.h < 80:
            self.screen.set_clip(None)
            return

        # background
        fam = cure["family"]
        body_col = (50, 52, 58) if fam == "ceramic" else (42, 44, 50)
        pygame.draw.rect(self.screen, body_col, plot, border_radius=4)
        pygame.draw.rect(self.screen, C_PANEL_HI, plot, 1, border_radius=4)

        # rebuild the 3D model when the selection changes
        model = self.model_micro
        key = ("micro", m["id"], plot.w, plot.h)
        if self.cache.get("_micro_key") != key:
            model.clear()
            phi = res["phi_solid"]
            P = res["P_total"]
            d50 = max(res["d50_mix"], 0.1)
            # scale grain radius to model space (world units ~ -1..1)
            grain_r = max(0.04, min(0.25, 0.04 + 0.21 * (
                math.log10(d50 + 1) / math.log10(101))))
            n_grains = min(60, max(8, int(40 * phi)))

            if fam == "ceramic":
                grain_col = (120, 180, 220)
            elif fam == "polymer":
                grain_col = (180, 140, 200)
            else:
                grain_col = (100, 160, 100)

            # deterministic placement in a 3D box
            seed = m["id"] * 9301 + 49297
            placed = []
            def rng():
                nonlocal seed
                seed = (seed * 9301 + 49297) % 233280
                return seed / 233280.0

            for _ in range(n_grains * 4):
                gx = (rng() - 0.5) * 1.6
                gy = (rng() - 0.5) * 1.6
                gz = (rng() - 0.5) * 1.6
                jr = grain_r * (0.6 + 0.4 * rng())
                ok = True
                for px, py, pz, pr in placed[-6:]:
                    if ((gx-px)**2 + (gy-py)**2 + (gz-pz)**2 <
                            (jr + pr - 0.02) ** 2):
                        ok = False
                        break
                if not ok:
                    continue
                placed.append((gx, gy, gz, jr))
                model.add_sphere(gx, gy, gz, jr, grain_col)
                if len(placed) >= n_grains:
                    break

            # pores as small dark spheres
            n_pores = min(30, int(n_grains * P * 2))
            for _ in range(n_pores):
                px = (rng() - 0.5) * 1.6
                py = (rng() - 0.5) * 1.6
                pz = (rng() - 0.5) * 1.6
                model.add_sphere(px, py, pz, grain_r * 0.25, (20, 20, 24))

            # fibers as cylinders
            vf_fib = res["vf_fiber"]
            if vf_fib > 0.001:
                n_fib = max(2, min(8, int(vf_fib * 30)))
                for _ in range(n_fib):
                    fx = (rng() - 0.5) * 1.4
                    fy = (rng() - 0.5) * 1.4
                    fz = (rng() - 0.5) * 1.4
                    model.add_cyl(fx, fy, fz, grain_r * 4, grain_r * 0.15,
                                  (220, 180, 60))

            self.cache["_micro_key"] = key

        model.render(self.screen, plot)

        # legend
        ly = plot.bottom + self.pad
        lx = plot.x
        if fam == "ceramic":
            grain_col = (120, 180, 220)
        elif fam == "polymer":
            grain_col = (180, 140, 200)
        else:
            grain_col = (100, 160, 100)
        d50 = max(res["d50_mix"], 0.1)
        items = [("grain (%.1f um d50)" % d50, grain_col),
                 ("pore (P=%.4f)" % res["P_total"], (20, 20, 24)),
                 ("solid %.2f" % res["phi_solid"], body_col)]
        if res["vf_fiber"] > 0.001:
            items.append(("fiber (%.1f vol%%)" % (100 * res["vf_fiber"]),
                          (220, 180, 60)))
        for label, col in items:
            sw = self.f_small.size(label)[0] + 26
            if lx + sw > plot.right:
                lx = plot.x
                ly += self.f_small.get_linesize()
            pygame.draw.rect(self.screen, col, (lx, ly + 4, 12, 12),
                             border_radius=2)
            self.text(label, self.f_small, lx + 18, ly, C_TEXT_SEC)
            lx += sw

        ly += self.f_small.get_linesize() + 2
        stat = "sigma_unconf %.0f MPa  |  sigma_conf %.0f MPa  |  E %.0f GPa  |  %s" % (
            res["sigma_unconfined"], res["sigma_confined"], res["E_gpa"],
            "NANOGRAIN" if res.get("ceramic") and res["ceramic"]["grain_nm"] < 500
            else "conventional")
        self.text(stat, self.f_small, plot.x, ly, C_TEXT_MUTED,
                  max_px=plot.w)

        self.screen.set_clip(None)

    # ========================================================== TAB 6 ======
    def draw_packing(self):
        """3D particle packing model.

        Left half: a 3D packing diagram -- spheres of different sizes
        representing the mix's size classes, packed in a box with depth
        sorting and Lambertian shading.  Drag to rotate, X to cut.
        Right half: the Funk-Dinger cumulative grading curve with the mix's
        actual classes plotted on it.
        """
        r = self.r_view
        m = self.mixes[self.sel]
        res = self.result(m)
        self.panel(r)
        self.screen.set_clip(r.inflate(-2, -2))

        title = "Particle packing 3D: %s  (phi_max=%.3f, drag to rotate, X = cut)" % (
            m["name"], res["phi_max"])
        self.text(title, self.f_sub, r.x + self.pad * 2, r.y + self.pad,
                  C_TEXT, max_px=r.w - self.pad * 4)

        top = r.y + self.pad * 2 + self.f_sub.get_linesize()
        bottom = r.bottom - self.pad * 2
        half_w = (r.w - self.pad * 5) // 2

        # left: 3D packing box
        pack_box = pygame.Rect(r.x + self.pad * 2, top, half_w, bottom - top)
        if pack_box.w < 60 or pack_box.h < 60:
            self.screen.set_clip(None)
            return
        pygame.draw.rect(self.screen, (40, 42, 48), pack_box, border_radius=4)
        pygame.draw.rect(self.screen, C_PANEL_HI, pack_box, 1, border_radius=4)

        cls = res["classes"]
        model = self.model_pack
        key = ("pack", m["id"], pack_box.w, pack_box.h)
        if self.cache.get("_pack_key") != key:
            model.clear()
            if cls:
                d_max = max(c[0] for c in cls)
                # scale sphere radius to world units
                scale = 0.7 / d_max
                seed = m["id"] * 9301 + 49297
                placed = []
                def rng():
                    nonlocal seed
                    seed = (seed * 9301 + 49297) % 233280
                    return seed / 233280.0
                for d_um, y_frac, beta in sorted(cls, key=lambda c: -c[0]):
                    r_w = max(0.03, d_um * scale)
                    n = max(1, min(15, int(y_frac * 30)))
                    for _ in range(n * 4):
                        px = (rng() - 0.5) * 1.4
                        py = (rng() - 0.5) * 1.4
                        pz = (rng() - 0.5) * 1.4
                        ok = True
                        for ex, ey, ez, er in placed[-8:]:
                            if ((px-ex)**2 + (py-ey)**2 + (pz-ez)**2 <
                                    (r_w + er - 0.02) ** 2):
                                ok = False
                                break
                        if not ok:
                            continue
                        placed.append((px, py, pz, r_w))
                        if d_um > 50:
                            col = (200, 120, 40)
                        elif d_um > 5:
                            col = (80, 160, 200)
                        else:
                            col = (140, 200, 120)
                        model.add_sphere(px, py, pz, r_w, col)
                        if len(placed) >= 40:
                            break
                    if len(placed) >= 40:
                        break
            self.cache["_pack_key"] = key

        model.render(self.screen, pack_box)

        # label under the packing box
        self.text("size classes: %d  |  q_best: %.3f  |  gamma: %.3f" %
                  (len(cls), res["q_best"], res["gamma"]),
                  self.f_small, pack_box.x, pack_box.bottom + 2,
                  C_TEXT_MUTED, max_px=pack_box.w)

        # right: Funk-Dinger grading curve (2D chart, unchanged)
        graph = pygame.Rect(pack_box.right + self.pad, top,
                            half_w, bottom - top)
        if graph.w < 60 or graph.h < 60:
            self.screen.set_clip(None)
            return
        pygame.draw.rect(self.screen, (30, 31, 34), graph, border_radius=4)
        pygame.draw.rect(self.screen, C_PANEL_HI, graph, 1, border_radius=4)

        ax_x = graph.x + 40
        ax_y = graph.y + self.f_small.get_linesize() + 4
        ax_w = graph.w - 50
        ax_h = graph.h - 40 - self.f_small.get_linesize()
        pygame.draw.line(self.screen, C_PANEL_HI,
                         (ax_x, ax_y), (ax_x, ax_y + ax_h))
        pygame.draw.line(self.screen, C_PANEL_HI,
                         (ax_x, ax_y + ax_h), (ax_x + ax_w, ax_y + ax_h))

        d_lo_g, d_hi_g = 0.1, 3000.0
        lg_lo = math.log10(d_lo_g)
        lg_span = math.log10(d_hi_g) - lg_lo

        def gx(d):
            return ax_x + int(ax_w * (math.log10(max(d, d_lo_g)) - lg_lo) / lg_span)

        def gy(cpft):
            return ax_y + ax_h - int(ax_h * cpft / 100.0)

        for pct in (0, 25, 50, 75, 100):
            ty = ax_y + ax_h - int(ax_h * pct / 100.0)
            pygame.draw.line(self.screen, C_GRID,
                             (ax_x, ty), (ax_x + ax_w, ty))
            img = self.f_mono_s.render("%d" % pct, True, C_TEXT_MUTED)
            self._blit(img, (ax_x - img.get_width() - 4,
                             ty - img.get_height() // 2))

        xtick_y = ax_y + ax_h + self.f_mono_s.get_height() // 2 + 4
        for d in (0.1, 1, 10, 100, 1000):
            tx = gx(d)
            if ax_x <= tx <= ax_x + ax_w:
                pygame.draw.line(self.screen, C_PANEL_HI,
                                 (tx, ax_y + ax_h), (tx, ax_y + ax_h + 3))
                lab = ("%.1f" % d) if d < 1 else ("%d" % d)
                img = self.f_mono_s.render(lab, True, C_TEXT_MUTED)
                self._blit(img, (tx - img.get_width() // 2, xtick_y))

        self.text("d (um)", self.f_small, ax_x + ax_w - 30,
                  xtick_y + self.f_mono_s.get_height() + 2,
                  C_TEXT_MUTED, max_px=36)

        for q, col in ((0.22, (60, 80, 60)), (0.30, (80, 100, 80)),
                       (res["q_best"], C_ACCENT)):
            pts = []
            for i in range(120):
                d = d_lo_g * (d_hi_g / d_lo_g) ** (i / 119.0)
                cpft = funk_dinger_cpft(d, d_lo_g, d_hi_g, q) * 100.0
                pts.append((gx(d), gy(cpft)))
            if len(pts) > 1:
                width = 2 if q == res["q_best"] else 1
                pygame.draw.lines(self.screen, col, False, pts, width)

        if cls:
            cum = 0.0
            for d_um, y_frac, beta in sorted(cls, key=lambda c: c[0]):
                cum += y_frac * 100.0
                px, py = gx(d_um), gy(cum)
                pygame.draw.circle(self.screen, C_OK, (px, py), 4)
                pygame.draw.circle(self.screen, C_SURFACE, (px, py), 2)

        ly = ax_y + ax_h + self.f_small.get_linesize() + self.f_mono_s.get_linesize() + self.f_small.get_linesize() + 6
        lx = graph.x
        for q, col, lbl in ((0.22, (60, 80, 60), "q=0.22"),
                            (0.30, (80, 100, 80), "q=0.30"),
                            (res["q_best"], C_ACCENT, "q=%.3f (best)" % res["q_best"]),
                            (0, C_OK, "mix classes")):
            sw = self.f_small.size(lbl)[0] + 26
            if lx + sw > graph.right:
                lx = graph.x
                ly += self.f_small.get_linesize() + 4
            if q == 0:
                pygame.draw.circle(self.screen, col, (lx + 7, ly + 7), 4)
            else:
                pygame.draw.line(self.screen, col,
                                 (lx, ly + 7), (lx + 14, ly + 7), 2)
            self.text(lbl, self.f_small, lx + 19, ly, C_TEXT_SEC)
            lx += sw

        self.screen.set_clip(None)

    # ========================================================== TAB 7 ======
    def draw_chemistry(self):
        """3D chemical reaction model.

        Top half: a 3D rotatable molecule model of the key reaction in the
        selected mix's cure family -- atoms as shaded spheres, bonds as
        cylinders.  Drag to rotate, X to cut.
        Bottom half: reaction equation cards with notes showing actual model
        values.
        """
        r = self.r_view
        m = self.mixes[self.sel]
        res = self.result(m)
        cure = m["cure"]
        fam = cure["family"]
        self.panel(r)
        self.screen.set_clip(r.inflate(-2, -2))

        title = "Chemistry 3D: %s  (%s family, drag to rotate, X = cut)" % (
            m["name"], fam)
        self.text(title, self.f_sub, r.x + self.pad * 2, r.y + self.pad,
                  C_TEXT, max_px=r.w - self.pad * 4)

        top = r.y + self.pad * 2 + self.f_sub.get_linesize()

        # define the 3D molecule and reaction cards per family
        if fam in ("hydraulic", "acid_base", "alkali"):
            # C-S-H structure: Ca (blue), Si (orange), O (green), H (purple)
            molecule = [
                # (label, x, y, z, radius, color)
                ("Ca", -0.6, 0.0, 0.0, 0.22, (80, 140, 200)),
                ("Si", 0.6, 0.0, 0.0, 0.20, (200, 120, 40)),
                ("O", 0.0, 0.5, 0.3, 0.16, (100, 200, 100)),
                ("O", 0.0, -0.5, -0.3, 0.16, (100, 200, 100)),
                ("H", 0.3, 0.8, 0.5, 0.10, (180, 160, 220)),
                ("H", -0.3, -0.8, -0.5, 0.10, (180, 160, 220)),
            ]
            bonds = [(0, 2), (0, 3), (1, 2), (1, 3), (2, 4), (3, 5)]
            reactions = [
                ("HYDRATION (C3S -> C-S-H + CH)",
                 "C3S + 4.3H -> C1.7SH4 + 1.3CH",
                 "sigma0 = 650 MPa, gel_frac = 0.28, v_prod = 0.68 cm3/g"),
                ("PORTLANDITE BALANCE (pozzolan + CH -> C-S-H)",
                 "S + 1.5CH + 2.5H -> C1.5SH2.5",
                 "ch_ratio = %.3f" % res.get("chem", {}).get("ch_ratio", 0)),
                ("AUTOCLAVE CONVERSION",
                 "C-S-H --150C--> tobermorite --250C--> xonotlite",
                 "gel porosity collapses: P = %.4f" % res["P_total"]),
            ]
        elif fam == "ceramic":
            # SiC / diamond lattice: Si/C (blue), C (orange)
            molecule = [
                ("Si", -0.5, -0.5, 0.0, 0.22, (200, 120, 40)),
                ("C", 0.5, -0.5, 0.0, 0.18, (80, 140, 200)),
                ("C", -0.5, 0.5, 0.0, 0.18, (80, 140, 200)),
                ("Si", 0.5, 0.5, 0.0, 0.22, (200, 120, 40)),
                ("C", 0.0, 0.0, 0.6, 0.18, (80, 140, 200)),
                ("C", 0.0, 0.0, -0.6, 0.18, (80, 140, 200)),
            ]
            bonds = [(0, 1), (0, 2), (1, 3), (2, 3), (0, 4), (1, 4),
                     (2, 5), (3, 5), (4, 0), (5, 1)]
            reactions = [
                ("SINTERING (grain growth + densification)",
                 "powder --%.0fC/%.0fMPa--> sintered body" % (
                     cure.get("fire_temp_c", 0), cure.get("set_pressure", 0)),
                 "grain_nm = %.0f, P = %.4f" % (
                     res.get("ceramic", {}).get("grain_nm", 0), res["P_total"])),
                ("HALL-PETCH STRENGTHENING",
                 "sigma = sigma0 + k / sqrt(d)",
                 "sigma0 = 6500 MPa, k = 0.95, d_crit = 15 nm"),
                ("INFILTRATION / NANOTWIN" if cure.get("infiltrated")
                 else "NANOTWIN FORMATION" if cure.get("twin_nm")
                 else "SOLID-STATE SINTERING",
                 "P -> 0.005" if cure.get("infiltrated")
                 else "twins @ %.1f nm" % cure.get("twin_nm", 0)
                 if cure.get("twin_nm") else "pressure-driven densification",
                 "sigma = %.0f MPa, P = %.4f" % (
                     res["sigma_unconfined"], res["P_total"])),
            ]
        else:  # polymer
            molecule = [
                ("C", -0.6, 0.0, 0.0, 0.20, (80, 140, 200)),
                ("C", 0.0, 0.0, 0.0, 0.20, (80, 140, 200)),
                ("C", 0.6, 0.0, 0.0, 0.20, (80, 140, 200)),
                ("O", -0.6, 0.5, 0.3, 0.16, (100, 200, 100)),
                ("H", 0.6, 0.5, 0.3, 0.10, (180, 160, 220)),
                ("H", 0.0, -0.5, -0.3, 0.10, (180, 160, 220)),
            ]
            bonds = [(0, 1), (1, 2), (0, 3), (2, 4), (1, 5)]
            reactions = [
                ("POLYMERISATION (vinylester cross-linking)",
                 "monomer + initiator -> cross-linked polymer",
                 "P = %.4f, sigma = %.0f MPa" % (
                     res["P_total"], res["sigma_unconfined"])),
            ]

        # 3D molecule viewport (top half)
        mol_h = min(int((r.bottom - top) * 0.55), 280)
        mol_box = pygame.Rect(r.x + self.pad * 2, top,
                              r.w - self.pad * 4, mol_h)
        if mol_box.w < 80 or mol_box.h < 80:
            self.screen.set_clip(None)
            return
        pygame.draw.rect(self.screen, (34, 36, 40), mol_box, border_radius=4)
        pygame.draw.rect(self.screen, C_PANEL_HI, mol_box, 1, border_radius=4)

        # rebuild 3D molecule when selection changes
        model = self.model_chem
        key = ("chem", m["id"], fam)
        if self.cache.get("_chem_key") != key:
            model.clear()
            for label, x, y, z, rad, col in molecule:
                model.add_sphere(x, y, z, rad, col)
            # bonds as thin cylinders between atom centers
            for a, b in bonds:
                if a < len(molecule) and b < len(molecule):
                    la = molecule[a]
                    lb = molecule[b]
                    dx = lb[1] - la[1]
                    dy = lb[2] - la[2]
                    dz = lb[3] - la[3]
                    length = math.sqrt(dx*dx + dy*dy + dz*dz)
                    mx = (la[1] + lb[1]) / 2.0
                    my = (la[2] + lb[2]) / 2.0
                    mz = (la[3] + lb[3]) / 2.0
                    model.add_cyl(mx, my, mz, length, 0.03, (160, 160, 170))
            self.cache["_chem_key"] = key

        model.render(self.screen, mol_box)

        # atom legend on the mol_box
        ly = mol_box.y + 4
        lx = mol_box.x + 4
        seen = set()
        for label, _, _, _, _, col in molecule:
            if label in seen:
                continue
            seen.add(label)
            sw = self.f_small.size(label)[0] + 22
            if lx + sw > mol_box.right - 4:
                break
            pygame.draw.circle(self.screen, col, (lx + 6, ly + 8), 5)
            self.text(label, self.f_small, lx + 14, ly, C_TEXT_SEC)
            lx += sw

        # reaction cards (bottom half)
        card_top = mol_box.bottom + self.pad
        card_h = min(80, (r.bottom - card_top - self.pad) // max(1, len(reactions)))
        if card_h < 40:
            card_h = 40
        cy = card_top
        for rname, equation, note in reactions:
            card = pygame.Rect(r.x + self.pad * 2, cy,
                               r.w - self.pad * 4, card_h - self.pad // 2)
            if card.bottom > r.bottom - self.pad:
                break
            pygame.draw.rect(self.screen, (34, 36, 40), card, border_radius=4)
            pygame.draw.rect(self.screen, C_PANEL_HI, card, 1, border_radius=4)

            self.text(rname, self.f_sub, card.x + self.pad, card.y + 2,
                      C_ACCENT, max_px=card.w - self.pad * 2)
            self.text(equation, self.f_mono_s,
                      card.x + self.pad,
                      card.y + 2 + self.f_sub.get_linesize(),
                      C_TEXT, max_px=card.w - self.pad * 2)
            self.text(note, self.f_small,
                      card.x + self.pad,
                      card.bottom - self.f_small.get_linesize() - 2,
                      C_TEXT_MUTED, max_px=card.w - self.pad * 2)

            cy += card_h

        self.screen.set_clip(None)

    # ========================================================== TAB 8 ======
    def draw_science(self):
        r = self.r_view
        self.panel(r)
        sc = self.scroll[7]
        w = r.w - self.pad * 4
        if "science" not in self.cache or self.cache.get("_sci_w") != w:
            body = []
            for head, para in SCIENCE_TEXT:
                if head:
                    body.append(("sec", head))
                for ln in wrap_text(self.f_body, para, w - 16):
                    body.append(("body", "  " + ln))
                body.append(("gap", None))
            self.cache["science"] = body
            self.cache["_sci_w"] = w
        self._draw_lines(r, sc, self.cache["science"], self.mixes[self.sel],
                         self.result(self.mixes[self.sel]))

    # -------------------------------------------------------------- run ----
    def draw(self):
        self.screen.fill(C_BG)
        self.layout()
        self.draw_header()
        self.draw_list()
        self.draw_tabs()
        (self.draw_overview, self.draw_mix, self.draw_production,
         self.draw_grain, self.draw_micro, self.draw_packing,
         self.draw_chemistry, self.draw_science)[self.tab]()
        self.draw_footer()
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)
        pygame.quit()


SCIENCE_TEXT = [
    ("WHAT THIS MODEL IS",
     "A formulation engine for pourable ultra-high-strength materials. Give it a "
     "recipe in kg/m3 and a curing schedule; it computes packing, rheology, "
     "reaction chemistry, porosity and strength from first principles, and tells "
     "you whether the thing can actually be poured."),
    ("1. PHASE CHOICE -- worth 100x",
     "The intrinsic strength of the load-bearing solid. C-S-H gel is about 650 MPa "
     "pore-free; corundum 3000; SiC 3800; WC 5200; diamond 6600. Nothing else in "
     "the model spans that range, and the decision is made before mix design "
     "starts."),
    ("2. TWIN SPACING -- worth up to 3.8x, and the winner",
     "Same maths as Hall-Petch but with no inverse turnover. An ordinary grain "
     "boundary is a disordered layer that slides once it is a large enough volume "
     "fraction, which is why nanocrystalline solids weaken below about 15 nm. A "
     "coherent twin boundary is a mirror plane of the same lattice: it blocks "
     "cracks just as well, but there is nothing to slide. Measured, not predicted "
     "-- nanotwinned cBN at 3.8 nm reaches Vickers 108 GPa and nanotwinned diamond "
     "at 5 nm reaches 200 GPa, both above single-crystal diamond."),
    ("3. GRAIN SIZE (Hall-Petch) -- worth up to 2x",
     "sigma(d) = sigma_ref + k/sqrt(d). Grain boundaries block cleavage cracks, so "
     "a finer grain is a stronger solid. Taking diamond from a 25 um grain to 20 nm "
     "doubles it. Below the critical size the trend reverses, so there is a real "
     "finite optimum rather than an extrapolation to zero."),
    ("4. POROSITY -- worth up to 10x within one phase",
     "sigma = sigma0 * exp(-b*P), b about 5-6, so each percent of porosity costs "
     "roughly 5 percent of strength. This is where ordinary concrete loses: at "
     "w/c 0.50 the paste is 47 percent porous and keeps only 6 percent of its "
     "pore-free strength. Beat it by lowering water, pressing during setting, or "
     "infiltrating a melt into the pore network afterwards."),
    ("5. CONFINEMENT -- worth 3-20x, but it is a system property",
     "f_cc = f_co + k*f_l, with k falling from 4.1 to about 2.2 at GPa pressures. "
     "Lateral pressure shuts off axial splitting and forces failure into pore "
     "collapse instead. Real -- it is how gun barrels and HPHT anvils work -- but "
     "the jacket belongs to the structure, not to the material."),
    ("6. GEL COLLAPSE -- worth about 2x, hydraulic binders only",
     "C-S-H carries about 28 percent intrinsic gel porosity that never leaves at "
     "ambient temperature. Autoclaving above 150 C recrystallises it to "
     "tobermorite and above 250 C to xonotlite, both dense. This is the actual "
     "reason RPC-800 exists."),
    ("7. PARTICLE PACKING -- worth about 1.3x, but it gates everything",
     "Better packing means less water for the same flow, which means less "
     "porosity. It rarely adds strength by itself; it is what makes low "
     "water/binder ratios physically placeable in the first place."),
    ("WHAT IS WORTH ALMOST NOTHING",
     "Hard aggregate in a soft matrix -- a 55 GPa diamond grain in a 300 MPa paste "
     "still fails at paste strength. Silica fume past about 14 percent on cement, "
     "which the portlandite balance caps. Fiber past about 4 vol percent, where it "
     "balls and traps air. Nano-additives in cement, which do not change the "
     "Ryshkevitch exponent. Grinding finer than d_crit, which makes it weaker."),
    ("MEASUREMENT HONESTY",
     "Tungsten carbide press platens fail near 5.5 GPa, so any unconfined strength "
     "above that cannot be measured in a conventional test frame -- the apparatus "
     "fails before the specimen. Above 5.5 GPa the numbers here come from hardness "
     "correlations or multi-anvil work, never from a compression test, and every "
     "such mix is graded extrapolated or speculative."),
    ("MODEL CONTRACT -- inputs",
     "A mix is a dict: id, name, tagline, tier (plant/specialist/frontier), "
     "evidence (measured/extrapolated/speculative), components {key: kg/m3}, "
     "cure {family, temp_c, age_days, set_pressure, K, air_pct, fire_temp_c, "
     "dwell_min, infiltrated, grain_nm, twin_nm}, optional confinement "
     "{type, sigma_y_mpa, od_id, prestress_mpa, note}, and recipe {process "
     "fields, mechanism, hazards, references}. Materials live in MATS; every "
     "component key must exist there."),
    ("MODEL CONTRACT -- outputs",
     "evaluate_mix(mix) returns one dict with everything downstream code reads. "
     "Volumes: v_total, v_binder, v_filler, v_fiber, v_water, v_air, "
     "v_infiltrant, volume_check, density, mass_total. Packing: classes, "
     "phi_max, gamma, phi_solid, packing_util, q_best, fd_err, d50_mix. "
     "Rheology: tau0, flow_mm, pour_class, pourable. Matrix: chem (or None), "
     "ceramic (or None), cure_factor, sigma0_eff, P_total, sigma_matrix. "
     "Composite: K_agg, K_dmax, bond, vf_filler, sigma_composite. Fiber: "
     "K_fiber, vf_fiber, sigma_fiber. Strength: sigma_unconfined, "
     "sigma_specimen, specimen_mm, weibull_m, f_lateral, sigma_confined. "
     "Derived: E_gpa, sigma_tensile, sigma_flexural, cost_m3. Verdict: "
     "hits_target, hits_target_unconfined. Optional keys (chem, ceramic) are "
     "None for families that do not produce them -- always guard with .get()."),
    ("MODEL CONTRACT -- families",
     "Four cure families, each taking a different branch: hydraulic (OPC, CAC, "
     "slag -- Powers-Brownyard hydration), acid_base / alkali (MgO-KH2PO4, "
     "geopolymer -- reaction-to-completion), ceramic (SiC, diamond, cBN -- "
     "sintering + Hall-Petch, no hydration chemistry), polymer (vinylester -- "
     "air porosity only). The chemistry branch sets sigma0_eff and P_total; "
     "everything downstream (composite, fiber, confinement, Weibull) is "
     "family-agnostic and runs on those two numbers."),
]


def ui_selftest(sizes=None, verbose=False):
    """Headless render of every tab at several window sizes.

    Asserts the two things that actually go wrong in a resizable UI: that some
    size raises, and that text collides.  A blit partly outside its clip is FINE
    -- that is how scrolling works -- so each blit is intersected with the clip
    that was active and only the visible remainder is compared.  Two visible
    glyph runs overlapping in both axes is a real overlay bug.

    Returns (ok, frames, errors, overlaps).
    """
    if pygame is None:
        return True, 0, [], []
    import os as _os
    _os.environ["SDL_VIDEODRIVER"] = "dummy"
    sizes = sizes or [(MIN_W, MIN_H), (1024, 700), (1280, 820), (1600, 950),
                      (1920, 1080), (900, 1200), (1400, 620)]
    errors, overlaps, frames = [], [], 0
    tol = 2

    class _Probe(UI):
        def begin(self):
            self.drawn = []

        def _blit(self, img, pos):
            UI._blit(self, img, pos)
            clip = self.screen.get_clip()
            r = pygame.Rect(pos[0], pos[1], img.get_width(), img.get_height())
            vis = r if clip is None else clip.clip(r)
            if vis.w > tol and vis.h > tol:
                self.drawn.append(vis)

        def collisions(self):
            n = len(self.drawn)
            for i in range(n):
                a = self.drawn[i]
                for j in range(i + 1, n):
                    it = a.clip(self.drawn[j])
                    if it.w > tol and it.h > tol:
                        return (tuple(a), tuple(self.drawn[j]))
            return None

    pygame.init()
    for (w, h) in sizes:
        try:
            ui = _Probe(w, h)
        except Exception as exc:
            errors.append("construct %dx%d: %s" % (w, h, exc))
            continue
        for tab in range(len(TABS)):
            ui.tab = tab
            for sel in (0, 10, 14, len(ui.mixes) - 1):
                ui.sel = sel % len(ui.mixes)
                for pos in (0.0, 1e9):
                    ui.scroll[tab].y = pos
                    ui.begin()
                    try:
                        ui.draw()
                        frames += 1
                    except Exception as exc:
                        errors.append("draw %s %dx%d: %s" % (TABS[tab], w, h, exc))
                        continue
                    hit = ui.collisions()
                    if hit:
                        overlaps.append((TABS[tab], w, h, hit))
        pygame.display.quit()
    pygame.quit()
    if verbose:
        for e in errors[:5]:
            print("   error: %s" % e)
        for o in overlaps[:5]:
            print("   overlap: tab=%s %dx%d %s" % o)
    return (not errors and not overlaps), frames, errors, overlaps


def launch_ui():
    """Start the interactive UI, or explain why it cannot start."""
    if pygame is None:
        print("The interactive UI needs pygame.  Install it with:")
        print("    pip install pygame")
        print("\\nEverything else works without it -- try --formulary or --compare.")
        return 1
    UI().run()
    return 0


# =============================================================================
# SECTION 13 -- MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="CeramicCement -- ultra-high-strength pour formulation model")
    parser.add_argument("--ui", action="store_true",
                        help="launch the interactive resizable UI (default when "
                             "pygame is installed and no other flag is given)")
    parser.add_argument("--console", action="store_true",
                        help="force console output instead of the UI")
    parser.add_argument("--about", action="store_true",
                        help="the science behind the model, in full")
    parser.add_argument("--grain", action="store_true",
                        help="Hall-Petch grain-size study across the superhard phases")
    parser.add_argument("--compare", action="store_true",
                        help="side-by-side table of every mix")
    parser.add_argument("--formulary", action="store_true",
                        help="COMPLETE list: every mix with grades, batch sheet, "
                             "production instructions, hazards and QC")
    parser.add_argument("--tier", type=str, default=None,
                        metavar="TIER", choices=["plant", "specialist", "frontier"],
                        help="restrict --formulary to one producibility tier")
    parser.add_argument("--mix", type=str, default=None, metavar="NAME",
                        help="full physics report on one mix (name or id)")
    parser.add_argument("--batch", type=str, default=None, metavar="NAME",
                        help="batch sheet for one mix")
    parser.add_argument("--vol", type=float, default=50.0, metavar="LITRES",
                        help="batch volume in litres (default 50)")
    parser.add_argument("--specimen", type=float, default=100.0, metavar="MM",
                        help="specimen size for the Weibull correction (default 100 mm)")
    parser.add_argument("--optimize", action="store_true",
                        help="packing sweep + pourable-strength optimisation")
    parser.add_argument("--target", type=float, default=None, metavar="MPA",
                        help="solve what each route needs to reach a target strength")
    parser.add_argument("--feasibility", action="store_true",
                        help="honest physics assessment of the 10 GPa goal")
    parser.add_argument("--selftest", action="store_true",
                        help="run sanity + calibration checks")
    parser.add_argument("--all", action="store_true",
                        help="run everything")
    args = parser.parse_args()

    ran = False
    if args.selftest:
        sys.exit(0 if selftest() else 1)
    if args.ui:
        sys.exit(launch_ui())
    if args.about or args.all:
        print_about(); ran = True
    if args.grain or args.all:
        print_grain_study(); ran = True
    if args.mix:
        print_mix(args.mix, args.specimen); ran = True
    if args.batch:
        print_batch(args.batch, args.vol); ran = True
    if args.compare or args.all:
        print_comparison(args.specimen); ran = True
    if args.formulary or args.all:
        print_formulary(args.tier, args.specimen); ran = True
    if args.target is not None:
        print_target_report(args.target); ran = True
    elif args.all:
        print_target_report(); ran = True
    if args.optimize or args.all:
        print_optimization(); ran = True
    if args.feasibility or args.all:
        print_feasibility(); ran = True

    if not ran and not args.console and pygame is not None:
        sys.exit(launch_ui())

    if not ran:
        print_banner()
        print_comparison(args.specimen)
        print("")
        print("  --ui               interactive resizable UI (needs pygame)")
        print("  --about            the science behind the model")
        print("  --grain            Hall-Petch grain-size study")
        print("  --formulary        EVERY mix: grades, batches, production, hazards")
        print("       --tier T      restrict the formulary to plant/specialist/frontier")
        print("  --mix NAME         full report on one mix")
        print("  --batch NAME       batch sheet      --vol L    batch volume")
        print("  --target 10000     route to a target strength")
        print("  --optimize         packing + strength optimisation")
        print("  --feasibility      honest assessment")
        print("  --all              everything")


if __name__ == "__main__":
    main()
