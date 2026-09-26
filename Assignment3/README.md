## Most dangerous mutation

Basin size actually ties A, B and C together. All three push the cancer-like fraction from
3.1% (8/256) up to the max possible, 50% (128/256). D barely moves, still sitting at 3.1%. So
going off basin size alone, there's no way to rank A, B and C against each other.

The MDM2 inhibitor is what actually splits them apart:

| network | untreated | + inhibitor | rescued? |
|---|---|---|---|
| A: p53 knockout | 50.0% | 50.0% | no |
| B: MYC amplification | 50.0% | 0.0% | yes |
| C: MDM2 overexpression | 50.0% | 0.0% | yes |
| D: p21 knockout | 3.1% | 0.0% | yes |

Block MDM2 in B or C and p53 comes back online, apoptosis fully returns to 0% cancer. Do the
same thing to A and nothing changes; 50% before, 50% after, because p53 isn't just being
suppressed there, it's gone. There's no signal left for the drug to bring back. A is also
faster than the other two: 4 steps to cancer under stress vs. 7 for B and C. Same numbers as
B and C on paper, but untreatable and quicker to get there. That's the case for A being the
most dangerous.

## Feedback loops (MYC → MDM2 → p53)

p53 blocks MYC, MYC turns on MDM2, MDM2 blocks p53. Multiply those three signs and you get a
net positive loop, which means bistability instead of one resting value. The system settles
either high-p53/low-MYC or high-MYC/low-p53, nothing in between.

This is basically why A, B and C converge on the same result even though they hit three
different genes. Each mutation just pins one node inside that same loop, and pinning any
single node is enough to drag the whole thing onto the growth side. D sidesteps this because
p21 sits downstream of the loop rather than inside it, so p53 can still do its job — the
basin ends up looking just like normal.

## Limitations

Updates happen synchronously, every node at once, which isn't how real cells work. Reactions
run at different speeds with no shared clock. Those two limit cycles that only show up in D
could easily be a side effect of that synchronous assumption rather than actual biology.

Every node is strictly on or off, so the inhibitor gets modeled as a full block rather than a
partial dose. There's no way to ask how much drug would actually be needed, or what a
half-effective treatment would look like.

Eight nodes is also a pretty big simplification of the real network, no DNA repair pathway,
no other tumor suppressors or oncogenes, no cell-to-cell variability. A real mutation
probably wouldn't behave this deterministically once all of that is put back in.
