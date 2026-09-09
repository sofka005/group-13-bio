# Epidemiological Model Assignment — Parameter Exploration

**Course**: KEN3170 — Multi-scale modeling of biological systems
**Group number**: 13

**Group members**

| Name | Student ID |
|---|---|
| Sava Stoimenov | I6385825 |
| Ben Tickler | I6385539 |
| Barnabás Szaniszló | I6374623 |
| Sofia Tsankova | I6390332 |

---

## 1. Repository overview

- `assignment1.ipynb` — main notebook containing all required sections (Setup, Part 1–3, Conclusions)
- `requirements.txt` — Python dependencies (numpy, matplotlib, pandas, scipy, seaborn)
- `README.md` — this file

**How to run**

```bash
pip install -r requirements.txt
jupyter notebook assignment1.ipynb   # then run all cells top to bottom
```

The notebook is deterministic — no random seeds are involved — so every number and figure
below is reproduced exactly on re-execution.

**Model.** All results come from a four-compartment SIRD model, integrated with
`scipy.integrate.odeint` on a daily grid:

```
dS/dt = -β·S·I/N
dI/dt =  β·S·I/N − γ·I − μ·I
dR/dt =  γ·I
dD/dt =  μ·I
```

with `N = S + I + R + D` held constant (deaths remain counted in the population). Following
the assignment brief, R₀ is reported as β/γ. Note that the threshold implied by the equations
is β/(γ + μ), because death is a second route out of the infectious compartment — this
matters at low R₀ and is discussed in the notebook.

---

## 2. Part 1 — Parameter analysis function

**Function**: `run_gamma_sensitivity_analysis(gamma_values, beta, mu, S0, I0, R0_init, D0, days)`

**Approach.** For each recovery rate in `gamma_values` the function integrates the SIRD system
over `days + 1` daily time points, then extracts four summary metrics from the resulting
trajectory: the maximum of I(t), the day on which that maximum occurs, the cumulative deaths
D at the final time point, and R₀ = β/γ. The metrics are collected into a tidy DataFrame with
the required columns, and the infectious curves for all γ values are drawn on a single
publication-quality axis (viridis colour ramp, labelled axes, legend showing both γ and R₀,
top and right spines removed). The function returns the DataFrame and the figure object, so
callers can compose several runs into one comparison figure without re-solving the model —
this is what Part 2 does.

**Default run** (β = 0.3, μ = 0.01, S₀ = 990, I₀ = 10, 160 days):

| gamma | R0 | peak_infected | peak_day | total_deaths |
|---|---|---|---|---|
| 0.05 | 6.0 | 479.7 | 26.0 | 165.5 |
| 0.10 | 3.0 | 269.1 | 27.0 | 83.6 |
| 0.15 | 2.0 | 136.8 | 30.0 | 47.7 |
| 0.20 | 1.5 | 57.4 | 33.0 | 26.0 |
| 0.25 | 1.2 | 18.0 | 30.0 | 11.5 |

---

## 3. Part 2 — Scenario comparison

### Scenario A — high transmission (β = 0.4, μ = 0.02, N = 1000, I₀ = 5, 200 days)

| gamma | R0 | peak_infected | peak_day | total_deaths |
|---|---|---|---|---|
| 0.05 | 8.00 | 520.6 | 21.0 | 284.8 |
| 0.10 | 4.00 | 340.1 | 22.0 | 159.9 |
| 0.15 | 2.67 | 213.5 | 24.0 | 102.6 |
| 0.20 | 2.00 | 123.9 | 27.0 | 67.4 |
| 0.25 | 1.60 | 63.1 | 30.0 | 42.7 |

### Scenario B — low transmission (β = 0.2, μ = 0.005, N = 1000, I₀ = 5, 200 days)

| gamma | R0 | peak_infected | peak_day | total_deaths |
|---|---|---|---|---|
| 0.05 | 4.00 | 371.4 | 44.0 | 88.2 |
| 0.10 | 2.00 | 139.3 | 52.0 | 36.7 |
| 0.15 | 1.33 | 31.3 | 67.0 | 13.6 |
| 0.20 | 1.00 | 5.0 | 0.0 | 1.8 |
| 0.25 | 0.80 | 5.0 | 0.0 | 0.4 |

A peak of 5.0 on day 0 means no outbreak occurred: the initial seed of five infectious
individuals is never exceeded and the infection dies out.

**Which scenario is worse, and why.** Scenario A, at every recovery rate tested.

The primary reason is simultaneity rather than the total case count. A higher transmission
rate raises R₀ at every γ, so more people are infectious at the same moment, and the strain on
a health system is set by the peak rather than by the cumulative total. At γ = 0.10 Scenario A
peaks at 340.1 infectious individuals against Scenario B's 139.3, and it reaches that peak on
day 22 rather than day 52 — roughly two and a half times the concurrent caseload, arriving in
less than half the time. Beds, staff and available treatment all fall short under that kind of
compression. When the same infections are spread out over a longer period, as in Scenario B,
shortages of hospital capacity are far rarer even though many people still get sick.

The death toll points the same way: 159.9 deaths against 36.7 at γ = 0.10, 4.4 times as many.
Two independent factors compound here. The higher β doubles R₀ at every γ, so a larger share of
the population is ever infected (95.9% vs 77.1%). The four-times higher μ then raises the case
fatality ratio, μ/(γ + μ), from 4.8% to 16.7% at the same γ.

Scenario B also has a reachable control target — it stops producing epidemics entirely once
γ ≥ 0.20 — whereas Scenario A remains above threshold even at γ = 0.25 (β/(γ + μ) = 1.48).

---

## 4. Part 3 — Policy recommendations

### 4.1 Parameter impact analysis

Increasing the recovery rate improves every outcome except epidemic duration.

**Peak infections** fall faster than proportionally: in Scenario A a fivefold increase in γ
(0.05 → 0.25) cuts the peak from 520.6 to 63.1, an 88% reduction. The proportional benefit of
each additional step in γ grows as R₀ approaches 1, because peak prevalence collapses towards
zero at the threshold. Scenario B shows the endpoint — between γ = 0.15 and γ = 0.20 the peak
falls from 31.3 to nothing at all.

**Total deaths** fall because γ shrinks two multiplicative factors at once. Deaths equal the
number ever infected times the case fatality ratio, and in this model the CFR has the closed
form μ/(γ + μ). In Scenario A, γ = 0.05 gives a 28.6% CFR applied to 996.7 infections
(284.8 deaths); γ = 0.25 gives a 7.4% CFR applied to 576.4 infections (42.7 deaths). The 85%
reduction is the product of a 74% cut in CFR and a 42% cut in infections.

**Epidemic duration is not monotonic.** Defining the epidemic as over when I(t) first falls
below 1 after the peak, Scenario A ends on days 118, 86, 77, 78 and 84 for γ = 0.05 … 0.25.
Faster recovery shortens the outbreak while R₀ is comfortably above 1, but as R₀ approaches 1
the epidemic grows slowly and leaves a long flat tail, so duration lengthens again. Duration
is therefore a poor policy target — the mildest epidemic in Scenario A is not the shortest.

### 4.2 Intervention analysis

Baseline: Scenario A at γ = 0.10 (R₀ = 4). An intervention raising the recovery rate by 50%
moves γ to 0.15.

| | Baseline γ = 0.10 | Treated γ = 0.15 | Change |
|---|---|---|---|
| CFR = μ/(γ+μ) | 16.7% | 11.8% | ×0.71 |
| Ever infected | 959.4 | 872.2 | ×0.91 |
| **Total deaths** | **159.9** | **102.6** | **−57.3 (−35.8%)** |
| Peak infectious | 340.1 | 213.5 | −37.2% |

0.71 × 0.91 = 0.64, so roughly three-quarters of the benefit comes from patients surviving
infections they would otherwise have died from, and one-quarter from infections prevented.

Applying the same +50% intervention at every baseline recovery rate shows the benefit is
strongly dependent on the starting point:

| Baseline γ | Treated γ | Deaths before | Deaths after | Reduction |
|---|---|---|---|---|
| 0.05 | 0.075 | 284.8 | 207.2 | 27.2% |
| 0.10 | 0.150 | 159.9 | 102.6 | 35.8% |
| 0.15 | 0.225 | 102.6 | 54.1 | 47.3% |
| 0.20 | 0.300 | 67.4 | 24.1 | 64.3% |
| 0.25 | 0.375 | 42.7 | 5.5 | 87.1% |

The proportional benefit more than triples across the range for an identical intervention,
because at high baseline γ the boost pushes β/(γ + μ) close to 1. Treatment and transmission
control are complementary, not additive.

**Coverage matters as much as efficacy.** If treatment reaches only a fraction *c* of
infections the population-average rate becomes γ(1 + 0.5c). At 30% coverage the model gives
139.0 deaths rather than 159.9 — a 13.1% reduction, about a third of the idealised benefit.

### 4.3 Real-world application

**Remdesivir for hospitalised COVID-19.** Remdesivir is a nucleoside analogue prodrug whose
active triphosphate form is accepted by the SARS-CoV-2 RNA-dependent RNA polymerase in place
of ATP and incorporated into the growing viral RNA, causing delayed chain termination a few
nucleotides later. Replication slows, viral load falls, and the patient clears the infection
sooner — in SIRD terms, a direct increase in γ, with μ unchanged, so a larger share of
infectious individuals exit through R rather than D.

**Realistic effectiveness.** In ACTT-1 (Beigel et al., *NEJM* 2020, 1062 hospitalised
patients) median time to recovery was 10 days on remdesivir versus 15 on placebo. Reading the
infectious period as 1/γ, that is γ rising from 0.067 to 0.100 — a 50% increase, matching the
magnitude modelled in 4.2. Day-29 mortality was 11% versus 15%, a difference the trial could
not distinguish from chance.

**Limits.** The WHO Solidarity trial (~11,000 patients) found no significant effect on
mortality or hospital duration, so 50% is an optimistic reading of contested evidence. The
model's γ is the rate of losing infectiousness, whereas the trial measured clinical recovery,
and hospitalised patients are typically past peak viral shedding — so the transmission benefit
transfers less faithfully than the mortality benefit. Coverage is the binding constraint:
remdesivir is an intravenous hospital drug, so treating the roughly 5% of infections that
reach hospital raises the population-average γ by about 2.5%, not 50%. For a
community-treated pathogen, oseltamivir for influenza is the closer analogue — a 10–20%
increase in γ, but deliverable to a far larger share of cases.

---

## 5. Conclusions

The recovery rate is the strongest lever in this model because it acts through two channels
simultaneously: it reduces how many people are ever infected and, independently, reduces the
share of those infections that end in death via the CFR μ/(γ + μ). A fivefold increase in γ
cuts Scenario A's deaths by 85% (284.8 → 42.7) and its peak by 88% (520.6 → 63.1).

Scenario A is worse for public health than Scenario B at every recovery rate, by roughly a
factor of four in deaths, with contributions from both the higher transmission rate and the
higher mortality rate.

Epidemic duration is the one outcome that does not improve monotonically with γ, so policy
should be judged on deaths and peak burden rather than on how quickly an outbreak ends.

A treatment raising recovery rates by 50% averts 57.3 deaths per 1000 at the γ = 0.10
baseline, but the same intervention removes 87% of deaths when applied to an epidemic already
pushed near threshold. The practical conclusion is that treatment programmes are worth most in
combination with transmission control, and that their real-world value is governed as much by
the share of infections they reach as by their efficacy in treated patients.

---

## 6. Generative AI disclaimer

Claude Opus 5 was used for writing checks, code debugging and documentation. The
interpretation of the results and the ideas behind them and the code are the students' own.

---

## References

- Beigel, J. H. et al. (2020). Remdesivir for the Treatment of Covid-19 — Final Report.
  *New England Journal of Medicine*, 383:1813–1826.
- WHO Solidarity Trial Consortium (2021). Repurposed Antiviral Drugs for Covid-19 — Interim
  WHO Solidarity Trial Results. *New England Journal of Medicine*, 384:497–511.
