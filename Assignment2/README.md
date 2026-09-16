# Metabolic Modeling Assignment - FBA on the E. coli Core Model

**Course**: KEN3170 - Multi-scale modeling of biological systems
**Group 13**: Sava Stoimenov (I6385825), Ben Tickler (I6385539), Barnabás Szaniszló (I6374623), Sofia Tsankova (I6390332)

## Files

- `assignment2.ipynb` – the notebook (Setup + Tasks 1–4)
- `e_coli_core.json` – the E. coli core model (BiGG)
- `KEN3170_Assignment_2026_e_coli_core_expression.csv` – measured max reaction activities
- `escher_max_activity.html` / `.svg` – Escher map from Task 1
- `task4_growth_vs_glucose.png` – Task 4 figure
- `requirements.txt`, `README.md`

## Running it

```bash
pip install -r requirements.txt
jupyter notebook assignment2.ipynb
```

Run top to bottom, keep the two data files next to the notebook. Escher pulls its map/model
from escher.github.io the first time you run Task 1, so you'll need internet for that once.
No randomness anywhere, so results come out the same every run.

The model has 95 reactions, 72 metabolites, 137 genes; 65 reactions have measured activity
values, the rest keep default bounds.

## Task 1 - Escher map

Built in-notebook with `escher` using the activity data (arrow thickness/colour = max
activity, grey = zero or missing).

- Glycolysis capacities don't line up neighbour-to-neighbour (PGI 11.1, PFK 13.1, FBA 30.4,
  TPI 70 …), because these are enzyme capacities, not fluxes - nothing forces them to match
  the way mass balance would. Pathway flux is set by whichever enzyme has the least capacity.
- Grey arrows come in two flavours: 12 reactions measured at exactly 0 (really blocked, e.g.
  PFL, LDH_D), and 30 with no data at all (exchanges, transporters, ATPM, biomass - not
  enzyme reactions, so no expression value; they just keep default bounds).

## Task 2 - Turning activity data into flux bounds

`apply_activity_constraints(model, activity)`: reversible reactions get (−v, v), irreversible
get (0, v), reactions with no data keep their defaults. Two exceptions: glucose exchange gets
reset to the wide default bound (−1000, 1000) since that's an environmental limit rather than
an enzyme one, and ATPM (no data) is left untouched. Reactions measured at 0 end up locked at
(0, 0) - effectively knocked out.

## Task 3 - FBA

With only the expression bounds and glucose unrestricted, max growth is **0.873/h** at a
glucose uptake of ~10.6 mmol/gDW/h - the cell just takes as much glucose as its enzymes can
handle. Respiration (CYTBD) and acetate export (ACKr) both sit at their caps, so leftover
carbon gets dumped as acetate.

Adding a glucose bound of ≤5 mmol/gDW/h on top drops growth to **0.416/h**, roughly half,
since carbon uptake also roughly halved. Acetate secretion stops entirely, since respiration
now has spare capacity for everything coming in.

The distinction: the glucose bound is about the environment (how much substrate is around),
the expression bounds are about the cell (how much flux each enzyme can carry).

## Task 4 - Growth vs. glucose availability

Sweeping the glucose bound from 1 to 15 mmol/gDW/h (step 0.1) shows growth rising, then
flattening - it can't increase forever, since once glucose supply exceeds the smallest enzyme
capacity in the pathway, that enzyme becomes the bottleneck instead.

The curve bends at two points, ~9.3–9.4 and ~10.6–10.7 mmol/gDW/h. At 9.5, only CYTBD sits at
its cap (41.1), so the first bend is where respiration saturates and acetate overflow
(EX_ac_e) kicks in - growth keeps climbing but slower, until that overflow pathway saturates
too around the second bend.

## Generative AI disclaimer

Claude helped with writing checks and code debugging. The results,
interpretation, and the code are our own.
