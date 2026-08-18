# Ceramic Cement -- Technical Overview

## Architecture

CeramicCement.py is a single-file Python application (~5,965 lines) with no external dependencies beyond Pygame. It contains three layers:

### 1. Physics Model Layer (lines 170-2480)

All strength predictions are computed from first principles through a chain of physics functions. No per-mix fitting -- the same parameter set runs every formulation.

**Core evaluation pipeline (`evaluate_mix`):**

```
components (kg/m3)
    |
    v
split_components -> binder / filler / fiber / water / infiltrant
    |
    v
volume bookkeeping -> v_binder, v_filler, v_water, v_fiber, v_air, v_infiltrant
    |
    v
particle packing (CPM) -> phi_max, phi_solid, d50, q_best, classes
    |
    v
rheology (YODEL + Roussel) -> tau0, flow_mm, pour_class, pourable
    |
    v
binder reaction (family-dependent):
  hydraulic  -> Powers-Brownyard hydration -> alpha, P_cap, P_gel, P_air, P_total
  acid_base  -> reaction-to-completion -> P_total
  ceramic    -> sintering + Hall-Petch -> grain_nm, sigma_phase
  polymer    -> air porosity only -> P_total
    |
    v
matrix strength -> sigma0_eff, sigma_matrix (Ryshkevitch-Duckworth)
    |
    v
composite strength -> K_agg, K_dmax, bond, sigma_composite
    |
    v
fiber factor -> K_fib, sigma_unconfined
    |
    v
Weibull size correction -> sigma_specimen
    |
    v
confinement (if jacket) -> f_lateral, sigma_confined
    |
    v
derived: E_gpa, sigma_tensile, sigma_flexural, cost_m3
    |
    v
verdict: hits_target, hits_target_unconfined
```

### 2. 3D Model Layer (lines 3878-4023)

A custom software 3D rasterizer following the same architectural pattern as Vapourize (Scene/Mesh) and GmanCoat (EngineRenderer):

- **`_sphere_mesh(radius, color)`** -- generates a UV-sphere triangle mesh
- **`_cyl_mesh(length, radius, color)`** -- generates a cylinder triangle mesh
- **`Model3D` class** -- holds primitives, transforms, renders:
  - Painter's algorithm depth sort (back-to-front)
  - Lambertian shading from directional light
  - Cross-section cutting (skip faces above y=0)
  - Camera orbit via pitch/yaw angles (mouse drag)
  - Perspective projection with focal length scaling

Three model instances are maintained:
- `self.model_micro` -- microstructure (grains, pores, fibers)
- `self.model_pack` -- particle packing (size-class spheres)
- `self.model_chem` -- molecules (atoms + bonds)

### 3. UI Layer (lines 4025-5970)

An interactive Pygame front end with 8 tabs, fully resizable:

- **Layout system**: every rectangle derived from window size each frame
- **Font scaling**: fonts rescale with window height (base 11-17px)
- **Text safety**: `fit_text` ellipsises, `wrap_text` wraps, `_blit` tracks all glyph rects
- **Overlap detection**: self-test verifies no two visible glyph runs collide across 448 frames
- **Scroll system**: per-tab `Scroll` objects with wheel/page/home/end navigation
- **Column dropping**: overview table drops low-priority columns on narrow windows

---

## Formulation Detail

### Material Database (MATS)

35+ materials across 5 roles:

| Role | Materials |
|------|-----------|
| binder | opc, cac, sf (silica fume), mk (metakaolin), ggbs, mgo, kh2po4, geopoly, vinylester, ra (reactive alumina), cosinter, nano_sic, nanodiamond, onion_carbon, onion_bn |
| filler | gravel, gravel10, sand, qsand, qflour, steelshot, talumina, sic, b4c, wc, cbn, diamond, sic_fine, carbon_black |
| fiber | steelfib, maragefib, sicwhisk |
| liquid | water, sp (superplasticizer), defloc, retarder, binderveh |

Each material carries: name, density (kg/m3), E (GPa), sigma (MPa), role, and family-specific properties (e.g. hp_k, d_crit_nm for ceramics).

### Cure System

Each mix has a `cure` dict:

| Key | Type | Description |
|-----|------|-------------|
| family | str | hydraulic / acid_base / alkali / polymer / ceramic |
| temp_c | float | Curing temperature |
| age_days | int | Age at test |
| set_pressure | float | MPa during setting |
| fire_temp_c | float | Sintering temperature (ceramic) |
| dwell_min | int | Dwell time at fire temperature |
| K | float | CPM compaction index (4.5 poured, 4.75 vibrated, 9.0 pressed) |
| air_pct | float | Entrapped air percentage |
| infiltrated | bool | Melt infiltration applied |
| grain_nm | float | Explicit grain size override |
| twin_nm | float | Nanotwin spacing |

### Production System

Each mix has a `recipe` dict with:

- **equipment** -- required machinery (mixer type, press, furnace, etc.)
- **mixing** -- mixing procedure (dry mix, wet mix, order, time)
- **placement** -- placement method (pour, vibrate, pump, press)
- **demould** -- time before demoulding
- **curing** -- cure schedule steps
- **qc** -- quality control checks (slump, density, strength, porosity)
- **mechanism** -- physics explanation of why this mix works
- **hazards** -- safety assessment
- **references** -- literature citations

---

## Strength Chain Detail

The strength chain in the MIX tab shows how each stage transforms the strength:

| Stage | Formula | Color |
|-------|---------|-------|
| pore-free sigma0 | sigma0_eff (intrinsic paste strength) | gray |
| matrix (x porosity) | sigma0 * exp(-b * P_total) | aqua |
| composite (x K_agg) | sigma_matrix * K_agg * K_dmax | orange |
| unconfined (x fiber) | sigma_composite * K_fib | blue |
| confined (x jacket) | sigma_unconfined + k(f_l) * f_l | green |

Each bar carries a red target tick at the 10 GPa position. Value text turns green when a stage reaches the target.

---

## Key Physical Constants (PHYS dict)

| Category | Parameter | Value |
|----------|-----------|-------|
| Ryshkevitch | rysh_b (cement) | 6.05 |
| Ryshkevitch | rysh_b_ceramic | 5.20 |
| Hall-Petch | hp_d_ref_um | 10.0 |
| Hall-Petch | hp_inverse_exp | 0.80 |
| Nanotwin | twin_floor_nm | 2.0 |
| Grain growth | growth_G | 2.50 |
| Densification | sinter_p_scale | 2000.0 |
| Densification | hpht_p_scale | 700.0 |
| Densification | infiltrated_porosity | 0.005 |
| Hydration | alpha_a | 1.031 |
| Hydration | alpha_b | 0.194 |
| Cure | cure_ambient | 1.00 |
| Cure | cure_steam90 | 1.06 |
| Cure | cure_auto200 | 1.18 |
| Cure | cure_auto400 | 1.30 |
| Composite | agg_gain | 0.22 |
| Composite | agg_cap_frac | 0.92 |
| Fibers | fiber_k | 3.5 |
| Weibull | weibull_m_cement | 12.0 |
| Weibull | weibull_m_uhpc | 15.0 |
| Weibull | weibull_m_ceramic | 10.0 |
| Rheology | tau_k | 260.0 |
| Rheology | flow_pourable_mm | 250.0 |
| Rheology | flow_scc_mm | 550.0 |
| Packing | K_pour | 6.00 |
| Packing | K_vib | 9.00 |
| Packing | K_press | 13.00 |
| Confinement | conf_k_lo | 4.10 |
| Confinement | conf_k_hi | 2.20 |

---

## Literature Calibration Bands

The self-test verifies that every material class lands within its published literature band:

| Material | Model (MPa) | Literature Band | Source |
|----------|-------------|-----------------|--------|
| Ordinary concrete | 26 | 25-50 | EN 206 C30/37 |
| High-strength concrete | 81 | 70-115 | ACI 363R |
| UHPC (Ductal) | 154 | 130-210 | AFGC-SETRA |
| RPC-200 (steam) | 192 | 170-250 | Richard & Cheyrezy |
| RPC-800 (400 C) | 617 | 450-900 | Richard & Cheyrezy |
| Fired alumina | 2,347 | 1,800-3,200 | sintered Al2O3 |
| RBSC | 2,781 | 2,200-3,600 | siliconized SiC |
| Nanograin SiC (SPS) | 4,451 | 3,500-6,500 | Hall-Petch estimate |
| HPHT diamond compact | 6,084 | 5,500-9,000 | PCD cutters |
| NPD | 11,709 | 10,000-20,000 | Knoop hardness |
| Nanotwinned cBN | 13,466 | 11,000-16,000 | Hv 108 GPa |
| Nanotwinned diamond | 24,934 | 20,000-30,000 | Hv 200 GPa |

---

## Model Contract

### Input (mix dict)

```
{
  id: int,
  name: str,
  tagline: str,
  tier: "plant" | "specialist" | "frontier",
  evidence: "measured" | "extrapolated" | "speculative",
  components: {material_key: kg_per_m3, ...},
  cure: {family, temp_c, age_days, set_pressure, K, air_pct,
         fire_temp_c, dwell_min, infiltrated, grain_nm, twin_nm},
  confinement: {type, sigma_y_mpa, od_id, prestress_mpa, note}  # optional
  recipe: {equipment, mixing, placement, demould, curing, qc,
           mechanism, hazards, references}
}
```

### Output (evaluate_mix return dict)

```
{
  # Volumes
  v_total, v_binder, v_filler, v_fiber, v_water, v_air, v_infiltrant,
  volume_check, density, mass_total,

  # Packing
  classes: [(d_um, y_frac, beta), ...],
  phi_max, gamma, phi_solid, packing_util, q_best, fd_err, d50_mix,

  # Rheology
  tau0, flow_mm, pour_class, pourable,

  # Matrix (family-dependent)
  chem: {w_b, alpha, ch_ratio, P_cap, P_gel, P_air, P_total,
         water_expelled_frac, sigma0_eff, sigma_paste} | None,
  ceramic: {grain_nm, feed_nm, twin_nm, sigma_phase} | None,

  # Strength chain
  sigma0_eff, P_total, sigma_matrix,
  K_agg, K_dmax, bond, vf_filler, sigma_composite,
  K_fiber, vf_fiber, sigma_fiber,
  sigma_unconfined, sigma_specimen, specimen_mm, weibull_m,
  f_lateral, sigma_confined,

  # Derived
  E_gpa, sigma_tensile, sigma_flexural, cost_m3,

  # Verdict
  hits_target, hits_target_unconfined
}
```

### Family Handling

| Family | Binder Chemistry | Porosity Source | Strength Mechanism |
|--------|-----------------|-----------------|-------------------|
| hydraulic | Powers-Brownyard hydration | gel + capillary + air | Ryshkevitch on paste sigma0 |
| acid_base | reaction-to-completion | unreacted + air | Ryshkevitch on product sigma0 |
| alkali | geopolymer condensation | gel + air | Ryshkevitch on gel sigma0 |
| ceramic | none (sintering) | green + sintered residual | Hall-Petch + porosity |
| polymer | none (cross-linking) | air only | polymer matrix + filler |

All families converge to the same downstream chain: matrix -> composite -> fiber -> Weibull -> confinement.

---

## 3D Model System Detail

### Model3D Class

```
Model3D
  |-- prims: list of (verts, faces, offset)
  |-- ax, ay: camera rotation angles (pitch, yaw)
  |-- zoom: float
  |-- cut: 0 (off) or 1 (cross-section at y=0)
  |-- light: directional light vector
  |
  |-- add_sphere(cx, cy, cz, r, color)
  |-- add_cyl(cx, cy, cz, length, r, color)
  |-- render(surf, rect)
```

### Rendering Pipeline

1. For each primitive: transform vertices by yaw then pitch, translate by offset
2. For each face: compute centroid, skip if cross-section cut and centroid y > 0
3. Compute average depth for sorting
4. Project to screen with perspective division
5. Compute Lambertian shade from face normal x light direction
6. Sort all faces back-to-front by depth
7. Draw filled polygons with shaded color

### Per-Tab Models

**MICRO tab:**
- Grains: spheres sized by d50 (log-scaled), colored by family
- Pores: small dark spheres, count proportional to P_total
- Fibers: cylinders, count proportional to vf_fiber
- Rebuilt when mix selection changes

**PACKING tab:**
- Size-class spheres: coarse (orange), medium (blue), fine (green)
- Scaled by d_max, placed with 3D collision avoidance
- Rebuilt when mix selection changes
- Right panel: 2D Funk-Dinger grading curve with mix classes overlaid

**CHEMISTRY tab:**
- Atoms: spheres colored by element (Ca=blue, Si=orange, O=green, H=purple)
- Bonds: thin cylinders between atom centers
- Family-specific molecules: C-S-H (hydraulic), SiC lattice (ceramic), polymer chain (polymer)
- Rebuilt when mix selection or family changes
- Bottom panel: reaction equation cards with actual model values

---

## Self-Test Architecture

The self-test runs 21 checks in sequence:

1. **Physics checks** (1-11): packing, porosity, CH balance, gel collapse, Hall-Petch, nanotwins, hardness cross-check, grain growth, diamond optimum, rheology, confinement
2. **Integration checks** (12-15): all 20 mixes evaluate, literature bands, target verification, infiltration
3. **Documentation checks** (16-19): production instructions, hazards, tiers, evidence grades
4. **UI checks** (20-21): 448 frames across 7 sizes x 8 tabs, 0 text collisions

The UI self-test (`ui_selftest`) uses a `_Probe` subclass that wraps `_blit` to record every glyph rect, then checks for intersections after each frame. Clipped scrolling outside the content area is acceptable; visible glyph intersections are bugs.

---

## Code Statistics

| Metric | Value |
|--------|-------|
| Total lines | ~5,965 |
| Physics functions | 30+ |
| Material definitions | 35+ |
| Mix formulations | 20 |
| UI tabs | 8 |
| 3D model tabs | 3 |
| Self-test checks | 21 |
| UI self-test frames | 448 (7 sizes x 8 tabs) |
| CLI commands | 12 |
| External dependencies | 1 (Pygame) |
