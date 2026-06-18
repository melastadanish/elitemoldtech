# Injection Mould Tooling — Requirement Extraction Instructions

## What to Extract from Client Documents

For each mould, extract the following in Step 1:

### Part Information
- Part name / description
- Product dimensions (L x W x H in mm)
- Product weight (g)
- Number of cavities requested
- Runner system (cold runner / hot runner — if specified)
- Surface treatment / texture (if specified)
- Mould life requirement (shots)

### Mould Specifications
- Cavity & core steel preference (H13, P20, 718, S136 — if specified)
- Mould size estimate (derive from part size if not given)
- Mould weight estimate
- Injection machine tonnage (if specified by client)
- Gate type (if specified)
- Ejection system (if specified)

### Technical Requirements
- Draft angles present in design
- Undercuts (require sliders or lifters)
- Thin walls
- Texture/finish on cavity surface
- Insert requirements
- Reference files provided (drawing, STEP, IGES, STL, PDF)

### Delivery
- Required delivery date or lead time
- Shipping destination

## DFM Flags for Injection Mould

Always check and flag:
- ❌ No draft angle — minimum 0.5° required, 1-2° recommended
- ❌ Thin walls < 1mm — risk of short shot and warpage
- ❌ Undercuts without slider/lifter specification
- ❌ Wall thickness variation > 25% — risk of sink marks
- ❌ Sharp corners — stress concentration, add radius
- ⚠️ No cavity count specified → ask client
- ⚠️ No runner system specified → assume cold runner
- ⚠️ No mould life specified → assume 500,000 shots standard
- ⚠️ No steel grade specified → decided in Step 2 based on mould life

## Confidence Scoring
- ✅ Confirmed — clearly in drawing/spec
- ⚠️ Assumed — state the assumption
- ❌ Missing — must be resolved before Step 2
