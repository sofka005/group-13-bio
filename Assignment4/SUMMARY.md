# Assignment 4: what was done (short summary)

## The idea in one paragraph
We have brain scans (fMRI) of one person's STG, a hearing area of the brain, taken while they listened to 288 sounds. We also have several AI models that recognise sounds. For every model layer, and for the brain, we build a table of how *different* each pair of sounds looks. This table is called an RDM, and the method is called RSA. If a model's table looks like the brain's table, the model "thinks about" sounds the way the brain does. We check which models, and which layers inside them, match the brain best.

## What was added on top of the groupmate's work (Part I)
Your groupmate's notebook already built the tables, compared them and made t-SNE plots. We added:
1. **Fairer baseline.** Untrained models are now 5 random copies instead of 1. One copy can be lucky or unlucky.
2. **Error bars everywhere.** Every result is shown with a 95% confidence interval: "we're 95% sure the true value is in this range".
3. **Significance tests.** These check whether a difference is real or just noise, corrected because we run many tests at once. Two kinds:
   - across the 5 trained copies of each model;
   - across the sounds, by resampling the 288 sounds 1000 times.
4. **Other ways to measure similarity.** We tried 6 combinations to see whether the conclusions depend on that choice. Some do.
5. **Plots of match vs. layer depth** for every model, plus the big pretrained model YAMNet.
6. **Simple baselines.** How well does the raw sound itself (spectrogram) match the brain, with no model at all?
7. **A number for "how clustered are the categories"** (silhouette score). This backs up the t-SNE pictures, which are only visual.
8. **A bug fix.** Layers used to be sorted alphabetically, so the output layer was shown first. They now go in input-to-output order.

## Our own model (Part II, the bonus)
`AuditoryPathwayModel` copies the route sound takes through the brain. Each part of the network is named after a brain area: inferior colliculus → thalamus (MGB) → primary auditory cortex (A1) → belt → STG. We trained it 5 times on the ESC-50 dataset. It was the most accurate small model (44.7%) and matched the brain about as well as the best provided model.

## Main takeaways
- Models that listen to **spectrograms** match the brain much better than the one that listens to the raw waveform.
- **Does training help?** It depends on how you measure similarity. With one measure it helps everywhere; with the other it hurts the last layers.
- The **middle-to-late layers** match the brain best. For YAMNet it's layer 12 of 15, not the very last layer.
- With only one person's brain data, most differences between the good models are **not statistically certain**.

## Deliverables (where things are)
| What | Where |
| --- | --- |
| Report (LaTeX, ~1,350 words, 5 pages) | `report/report.tex` + `report/figures/`, compiled to `report/report.pdf` |
| Notebook with all analysis (fully re-run, outputs included) | `assignment4.ipynb`. Our new part is **Section 4** |
| Our own model | `AuditoryPathwayModel` in `models.py`, registered in `core.py` |
| Result tables (CSV) and key numbers (JSON) | `results/` |
| Figures | `img/` (not in git) and copies in `report/figures/` |

## Where the explanatory text is
- **Notebook, Section 4**: every sub-step (4.1–4.8) starts with a short text cell explaining what it does and why.
- **`models.py`**: the docstring of `AuditoryPathwayModel` explains which layer stands for which brain area.
- **`report/report.tex`**: the full write-up (introduction, methods, results, discussion, future work).
- **This file**: the short version.

## To re-run
```bash
conda activate ken3170
jupyter nbconvert --to notebook --execute assignment4.ipynb --inplace
```
Data (`data/`, `models/`) comes from the filesender link in the README; ESC-50 from GitHub.
