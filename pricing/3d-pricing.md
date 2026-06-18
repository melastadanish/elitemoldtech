# 3D Printing — Pricing Rules

## Pricing Model
3D printing is priced by **volume (cm³)** + **technology rate** + **post-processing**

```
Part cost = (volume cm³ × material rate) × technology multiplier + post-processing
```

## Technology Base Rates
[TO BE FILLED]
```
| Technology | Base Rate ($/cm³) | Notes |
|------------|------------------|-------|
| FDM | $[rate] | Cheapest, visible layer lines |
| SLA | $[rate] | Smooth surface, brittle |
| SLS | $[rate] | Strong, functional parts |
| MJF | $[rate] | Best accuracy, functional parts |
```

## Material Multipliers
[TO BE FILLED]
```
FDM:
  PLA:       × 1.0
  ABS:       × 1.1
  PETG:      × 1.1
  TPU:       × 1.3
  Nylon:     × 1.4

SLA:
  Standard resin:  × 1.0
  Engineering:     × 1.5
  Flexible:        × 1.4

SLS/MJF:
  Nylon PA12:  × 1.0
  Glass-fill:  × 1.3
```

## Stock Size Multipliers
Same as CNC — applied to account for build plate usage:

| Part Size (longest dimension) | Multiplier |
|-------------------------------|------------|
| Small: < 50mm | × 1.5 |
| Medium: 50mm – 200mm | × 1.1 |
| Large: > 200mm | × 1.05 |

## Post-Processing
[TO BE FILLED]
```
Support removal:     included
Sanding (basic):     + $[amount]
Painting:            + $[amount]
Primer + paint:      + $[amount]
Assembly:            + $[amount]/hr
```

## Quantity Discounts
[TO BE FILLED]
```
1-9 pcs:    no discount
10-49 pcs:  [x]% discount
50+ pcs:    [x]% discount
```

## Notes
- Prices in USD
- FOB Shenzhen
- Minimum order: [TO BE FILLED]
- File format required: STL or STEP
