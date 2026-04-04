# Statistics Reference

## Default stance

- do not treat point estimates as enough for claim-facing comparisons
- use multi-seed runs whenever the method or training is stochastic
- use paired comparisons when the same seeds or splits are available
- keep metric direction explicit for every comparison

## Recommended reporting block

For every claim-facing result, report:
- method
- dataset
- metric
- mean
- uncertainty interval
- seed count or repeated-trial count
- direction of improvement
- config identifier or git sha for the evaluated run

## Intervals and tests

Use these defaults unless the field or venue expects something else:
- bootstrap confidence intervals for per-method means and paired deltas
- sign test or another declared paired test when shared seeds exist
- Holm correction when many candidates are compared against one baseline

## Effect sizes

When comparisons are paired, include:
- mean delta
- interval for the delta
- shared seed count
- standardized delta when meaningful

Do not rely on p-values alone.

## Metric direction

State whether larger or smaller is better. Be careful with:
- error and loss metrics
- perplexity
- latency and runtime
- memory or parameter count

## When to weaken the claim

Weaken or qualify the paper's language when:
- the interval crosses zero or the practical equivalence threshold
- gains appear only on one dataset or one seed pattern
- one stronger baseline removes the claimed advantage
- the result depends on an unusually favorable tuning budget

## Minimum empirical evidence expectations

For a new empirical method with several components, expect at least:
- strongest fair baselines
- one component or design ablation
- robustness over seeds or splits when stochasticity matters
- efficiency evidence when the paper claims practical benefit
- failure cases or negative conditions where the method underperforms
