# CNC Machining — Pricing Rules

## Stock Size Multipliers
Applied to raw material cost to account for stock sizing waste:

| Part Size (longest dimension) | Multiplier |
|-------------------------------|------------|
| Small: < 50mm | × 1.5 |
| Medium: 50mm – 200mm | × 1.1 |
| Large: > 200mm | × 1.05 |

**How to apply:**
```
Raw material cost = (part volume × material rate per cm³) × size multiplier
```

## Materials & Rates
[TO BE FILLED — add material name, cost per kg, and machining rate per hour]

Example format:
```
| Material | Cost/kg (USD) | Machine Rate/hr (USD) | Notes |
|----------|--------------|----------------------|-------|
| Aluminum 6061 | [price] | [rate] | Most common |
| Stainless 316 | [price] | [rate] | 1.8x harder |
| Brass C360 | [price] | [rate] | |
```

## Machine Hourly Rates
[TO BE FILLED]
```
3-axis milling:  $[rate]/hr
4-axis milling:  $[rate]/hr
5-axis milling:  $[rate]/hr
CNC turning:     $[rate]/hr
Setup fee:       $[amount] flat per job
```

## Surface Finishing
[TO BE FILLED]
```
As-machined (Ra 3.2):  included
Anodizing:             $[price]/part
Powder coat:           $[price]/part
Polishing:             $[price]/hr
```

## Quantity Discounts
[TO BE FILLED]
```
1-9 pcs:    no discount
10-49 pcs:  [x]% discount
50-99 pcs:  [x]% discount
100+ pcs:   [x]% discount
```

## Notes
- Prices in USD
- All prices FOB Shenzhen
- Minimum order: [TO BE FILLED]
