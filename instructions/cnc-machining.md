# CNC Machining — Requirement Extraction Instructions

## What to Extract from Client Documents

For each part, extract the following in Step 1:

### Part Information
- Part name / description
- Quantity required
- Product dimensions (L x W x H in mm)
- Estimated weight (g) — calculate from dimensions if not provided
- Tolerances (general and critical)
- Surface finish requirements
- Material requested by client (leave blank if not specified — decided in Step 2)

### Technical Requirements
- Machining type: 3-axis / 4-axis / 5-axis / turning / milling / drilling
- Thread specifications (size, depth, type)
- Hole specifications (diameter, depth, through/blind)
- Critical features (undercuts, thin walls, deep pockets)
- Reference files provided (drawing, STEP, IGES, STL, PDF)

### Delivery
- Required delivery date or lead time
- Shipping destination

## DFM Flags for CNC

Always check and flag:
- ❌ Thin walls < 0.8mm
- ❌ Deep pockets with aspect ratio > 6:1 (depth > 6x width)
- ❌ Sharp internal corners (need radius, specify minimum tool radius)
- ❌ Tolerances tighter than ±0.01mm (flag as precision machining — higher cost)
- ⚠️ No surface finish specified → assume as-machined Ra 3.2
- ⚠️ No tolerance specified → assume ±0.1mm general tolerance
- ⚠️ Material not specified → flag for Step 2 decision

## Confidence Scoring
- ✅ Confirmed — clearly in drawing/spec
- ⚠️ Assumed — state the assumption
- ❌ Missing — must be resolved before Step 2
