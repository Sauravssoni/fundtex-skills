---
name: fundtex-visuals-reporting
description: Create professional Indian finance pie charts, bar charts, correlation heatmaps, historical return histograms, assumption waterfalls, PDF/Markdown memos and executive chart exports from approved sources.
---
# Fundtex Visuals and Reports
Call fundtex visual --kind pie|bar|heatmap|histogram|waterfall --inputs /approved/values.json --out /new/chart.svg. Inputs must be source-verified or explicitly marked synthetic; never invent correlations, NAVs, earnings, target prices or risk metrics. Use fundtex analyst-pack for all-in-one reports. Verify axis labels, units, source timestamps, legal rights and whether underlying data was actually opened. For PDF use ReportLab if installed, for XLSX vetted artifact_tool; warn on missing optional outputs. Serve the result with an executive decision summary, genuine original sources, counterarguments and a human review action.

## Fallbacks and review

- Unknown source means source verification pending, not externally validated research.
- A chart built from scenario assumptions must prominently say illustrative or hypothetical.
- Escaped labels and finite numeric inputs are mandatory for all SVG exports.
- Do not substitute visualization aesthetics for evidence or present retrospective shapes as alpha.
