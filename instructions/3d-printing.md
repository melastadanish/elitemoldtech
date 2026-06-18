# 3D Printing — Requirement Extraction Instructions

## Technologies Offered
- FDM (Fused Deposition Modeling)
- SLA (Stereolithography)
- SLS (Selective Laser Sintering)
- MJF (Multi Jet Fusion)

## What to Extract from Client Documents

### Part Information
- Part name / description
- Quantity required
- Product dimensions (L x W x H in mm)
- Estimated volume (cm³) — calculate from dimensions if not provided
- Estimated weight (g)
- Surface finish requirements
- Color requirements
- Technology preference (if specified by client)
- Material preference (if specified)

### Technical Requirements
- Functional or prototype use
- Mechanical strength requirements
- Temperature resistance requirements
- Tolerances required
- Post-processing needed (painting, sanding, assembly)
- Reference files provided (STL, STEP, OBJ, 3MF)

### Delivery
- Required delivery date or lead time
- Shipping destination

## DFM Flags for 3D Printing

### FDM
- ❌ Overhangs > 45° without support specification
- ⚠️ Fine details < 1mm — may not print accurately
- ⚠️ No layer orientation specified — affects strength

### SLA
- ❌ Walls < 0.5mm
- ⚠️ Large hollow parts need drainage holes
- ⚠️ Resin is brittle — flag for functional parts

### SLS / MJF
- ⚠️ Minimum wall 0.7mm
- ✅ Best for functional parts, no support needed
- ⚠️ Surface is slightly rough — flag if smooth finish needed

### General
- ⚠️ Technology not specified → recommend based on use case
- ⚠️ Material not specified → decided in Step 2
- ❌ File format not supported → request STL or STEP

## Confidence Scoring
- ✅ Confirmed — clearly in drawing/spec
- ⚠️ Assumed — state the assumption
- ❌ Missing — must be resolved before Step 2
