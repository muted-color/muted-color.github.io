---
title: "Auditing Structural-Signal Interpretation in OpenBind Prediction Scores"
date: 2026-05-10 18:40:00 +0900
last_modified_at: 2026-08-01 08:07:32 +0900
published: true
publication_status: "published"
lang: en
categories: ["BIO ML"]
tags: [openbind, affinity-prediction, structure-based-ai, ligand-baseline, benchmark-check, rdkit, ecfp]
lab_path: "experiment-lab/projects/openbind-affinity-baseline-stress"
excerpt: "A reproducible benchmark audit comparing OpenBind prediction-score correlations with property baselines and ligand-only controls to examine the limits of structural-signal interpretation."
description: "An audit of public OpenBind EV-A71 2A prediction scores against property baselines and ligand-only controls, examining why pKD correlation alone makes it difficult to identify an independent structural contribution and what further evaluation would be needed."
permalink: /research/2026/05/10/openbind-affinity-baseline-audit/
image: /assets/images/posts/openbind-affinity-baseline-audit/social-thumbnail.png
image_alt: "Summary chart comparing each method's Spearman correlation with measured pKD and MW+cLogP-adjusted pKD in the OpenBind EV-A71 2A affinity audit"
hero_image: /assets/images/posts/openbind-affinity-baseline-audit/raw-vs-residual-spearman.svg
hero_alt: "Chart comparing how closely each method score tracks measured pKD and MW+cLogP-adjusted pKD in the compound-level OpenBind EV-A71 2A audit"
hero_caption: "<strong>Figure 1.</strong> Each row represents one method score, and the x-axis is the Spearman correlation between that score and the pKD ranking. Solid bars show correlation with measured pKD; hatched bars show correlation with MW+cLogP-adjusted pKD. The labels at left distinguish ligand-only controls trained on the same EV-A71 2A data, simple property baselines, and public benchmark scores. A shorter hatched bar indicates that overlap between the raw pKD correlation and the MW+cLogP trend should be considered. Exact values are reported in Table 3 and Appendix Table 2."
hero_frame: true
hero_compact: true
hero_variant: featured-plot
---

OpenBind's first public release provides compound-level affinity measurements together with prediction scores from several structure-based methods. The official analysis also reported molecular weight as a strong affinity-ranking baseline for this release <a class="citation-ref" href="#ref-openbind-first-release" aria-label="Reference 1">[1]</a>.

This note independently reconstructs the public compound table and tests whether the prediction scores retain correlation with pKD after adjustment for MW and cLogP. The public score with the highest correlation with adjusted pKD was Boltz-2 at `0.097`; a ligand-only ECFP control trained on labels from the same campaign reached `0.430`.

These values are not a model ranking obtained under identical training conditions. The comparison neither directly decomposes structural contribution nor evaluates generalization to new chemical series. Its scope is a retrospective audit that should precede interpretation of public score–pKD correlation as structure-based affinity signal.

## Summary

- OpenBind had already shown that molecular weight is a strong affinity-ranking baseline in this release. This audit confirms that observation at compound level and adds MW+cLogP adjustment and ligand-only controls.
- The analysis covers `494` compounds aligned to the public benchmark and `7` score files: `5` from trained or scoring methods and `2` property baselines, molecular weight and cLogP.
- MW+cLogP-adjusted pKD is a diagnostic value computed over the full compound table. The public method score with the highest correlation with this value was Boltz-2 at `0.097`.
- ECFP ridge at `0.430` is a shuffled 5-fold out-of-fold ligand-only control trained on raw pKD from the same campaign. It is neither a model ranking under the public scores' training conditions nor a generalization result for new chemical series.
- The mean ordering of public scores and ligand-only controls was preserved under compound and chemical-group resampling. Because the models were not retrained group-held-out, this is not evidence of strict scaffold generalization.
- In a separate follow-up, adding distance, contact, and atom-count descriptors from prepared structures to ECFP did not increase correlation. This is a secondary result for a limited structure-descriptor design, not a reproduction of the primary comparison.

{% include model-mention-cards.html label="Public resources" aria_label="OpenBind release and benchmark resources" models="OpenBind first release|EV-A71 2A structure-affinity dataset|https://openbind.uk/news/blog-openbinds-first-release-a-structure-affinity-dataset-for-structure-based-ai/;Affinity data note|OpenBind affinity and kinetics data|https://openbind.uk/news/blog-affinity-and-kinetics-data-in-the-ev-a71-2a-openbind-release/;EV-A71 2A benchmark|Pinned OpenBind GitHub affinity files|https://github.com/OpenBind-Consortium/EV-A71_2A_benchmark/tree/86e5c12da518d749c33cfa9dcb6ae8eae1b804f9/affinity;Zenodo release|OpenBind structure-affinity data|https://zenodo.org/records/20026661" %}

## Evaluation Setup

EV-A71 2A protease is the protein-cleaving enzyme of Enterovirus A71. The experimental structures and affinities in OpenBind's first release were generated with a CVA16 2A surrogate whose sequence differs from EV-A71 2A at only five positions, none close to the active site <a class="citation-ref" href="#ref-openbind-first-release" aria-label="Reference 1">[1]</a>.

> **pKD** expresses the dissociation constant on a logarithmic scale; higher values indicate stronger binding. **Spearman correlation** measures similarity in rank rather than absolute magnitude.
>
> **MW and cLogP** are molecular weight and calculated lipophilicity, respectively. Here, MW+cLogP-adjusted pKD is a diagnostic value with the trend explained by these two properties removed; it is not ground truth for signal originating from structural information. A **ligand-only control** uses only ECFP/RDKit compound representations, without protein structure.

The comparison unit is the compound. The raw OpenBind affinity data can contain multiple measurement rows for one compound, and an inclusion flag in the public data identifies the rows used in the final benchmark <a class="citation-ref" href="#ref-openbind-affinity-note" aria-label="Reference 2">[2]</a>. The OpenBind repository publishes the affinity measurements, compound information, method-specific prediction scores, and the rules used to assemble the score comparison table <a class="citation-ref" href="#ref-openbind-github" aria-label="Reference 3">[3]</a>.

This note does not reinterpret raw measurements or recombine multiple measurement rows into a new compound-level pKD. Instead, it aligns to the compound-level table already prepared for the public benchmark and compares each public prediction score with the corresponding compound-level pKD.

The comparison has two steps. First, it measures how closely each prediction score follows the measured pKD ranking. It then tests whether that correlation remains after removing the component of pKD explained by molecular weight and cLogP. This is not a final evaluation of structure-based methods. It is a basic check on whether correlation with pKD can be interpreted as structure-based affinity signal.

The evaluation contract is:

- **Public benchmark scores** are the compound-level scores provided by OpenBind, used without retraining or calibration.
- **MW+cLogP-adjusted pKD** is the value remaining after linearly regressing pKD on molecular weight and cLogP across all `494` compounds. It is a descriptive adjustment over the full table, not a held-out target.
- **Ligand-only controls** are out-of-fold predictions generated by shuffled 5-fold cross-validation over the same `494` compounds. ECFP ridge is trained on raw pKD, and folds are split by compound rather than scaffold or similarity cluster.
- **Uncertainty ranges** are calculated by resampling compounds or chemical groups while holding the already computed scores and out-of-fold predictions fixed. They do not include variation from retraining or performance on new chemical series.

Table 1 summarizes how the raw data are organized into the final comparison unit.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--analysis-scope">
      <thead>
        <tr>
          <th>Group</th>
          <th>Item</th>
          <th class="align-right">Value</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td rowspan="3"><strong>Public raw data</strong></td>
          <td>Affinity measurement rows</td>
          <td class="align-right"><code>2733</code></td>
        </tr>
        <tr>
          <td>Measurement rows used in benchmark</td>
          <td class="align-right"><code>1613</code></td>
        </tr>
        <tr>
          <td>Rows linked to structures</td>
          <td class="align-right"><code>925</code></td>
        </tr>
        <tr>
          <td><strong>Public scores</strong></td>
          <td>Score rows by compound–method pair</td>
          <td class="align-right"><code>3458</code></td>
        </tr>
        <tr>
          <td rowspan="3"><strong>Final comparison unit</strong></td>
          <td>Compounds compared in this note</td>
          <td class="align-right"><code>494</code></td>
        </tr>
        <tr>
          <td>Compounds processable by RDKit</td>
          <td class="align-right"><code>494</code></td>
        </tr>
        <tr>
          <td>Public score files<br><span class="table-note-inline">5 methods + 2 property baselines</span></td>
          <td class="align-right"><code>7</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> Summary of how the raw data were organized into the final comparison table. The analysis uses <code>494</code> compounds with pKD aligned at the same compound level. The <code>7</code> public score files comprise <code>5</code> trained or scoring methods and <code>2</code> property baselines.</figcaption>
</figure>

## Results

### Confirmation of the public property-baseline observation

The OpenBind release article had already identified molecular weight as a strong affinity-ranking baseline for this release <a class="citation-ref" href="#ref-openbind-first-release" aria-label="Reference 1">[1]</a>. In this audit, the Spearman correlation between molecular weight and measured pKD was `0.484`, and an MW+cLogP linear model explained about 30% of the pKD variation in the full compound table (`R² = 0.299`).

This result is not presented as a new ligand-property effect. It establishes the starting condition for separating public prediction-score correlation from the MW+cLogP trend.

Figure 2 shows the relationship between molecular weight and pKD.

<figure class="media-figure">
  <img src="/assets/images/posts/openbind-affinity-baseline-audit/pkd-vs-mw.svg" alt="Scatter plot showing the positive relationship between molecular weight and pKD in the compound-level OpenBind EV-A71 2A table">
  <figcaption><strong>Figure 2.</strong> Relationship between molecular weight and pKD. The Spearman correlation for molecular weight alone was <code>0.484</code>; the line is a descriptive linear trend. This relationship serves as a simple ligand-property baseline that should be checked before interpreting correlation with measured pKD.</figcaption>
</figure>

Subsequent comparisons use the value remaining after pKD was linearly regressed on molecular weight and cLogP across all `494` compounds. This value does not represent every signal that should be removed in a real medicinal-chemistry process. Changes in compound size or lipophilicity can themselves move with potency. The resulting value is therefore not ground truth for “true affinity signal,” but a descriptive adjustment over the full table used to examine how strongly prediction-score correlation with pKD depends on a large property trend.

Table 2 reports the ligand-property baselines checked before MW+cLogP adjustment.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>Comparison</th>
          <th>Metric</th>
          <th class="align-right">Value</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>molecular weight</td>
          <td>Spearman with measured pKD</td>
          <td class="align-right"><code>0.484</code></td>
        </tr>
        <tr>
          <td>MW+cLogP linear model</td>
          <td>Descriptive <code>R²</code></td>
          <td class="align-right"><code>0.299</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> Simple ligand-property baselines checked before interpreting correlation with measured pKD. MW+cLogP is not a final model-comparison standard; it is a reference for the magnitude of the property trend in the public release.</figcaption>
</figure>

### Correlation with MW+cLogP-adjusted pKD

First, pKD was linearly regressed on molecular weight and cLogP across all `494` compounds, and the remaining values were calculated. The analysis then measured how closely the ranking of this adjusted pKD matched each method-score ranking.

Among the benchmark scores published by OpenBind, the highest value was Boltz-2 at Spearman `0.097`. By comparison, the ECFP ridge control, which uses compound information without structure, reached `0.430`.

The public scores moved to some extent with measured pKD, but did not closely track the MW+cLogP-adjusted pKD ranking. Within the same dataset, a ligand-only control showed a higher correlation with adjusted pKD.

This note uses whether each score retains correlation with MW+cLogP-adjusted pKD as a minimal diagnostic for signal beyond a simple ligand-property trend. Even this correlation is not direct evidence that a method “reads structural information well.”

The public OpenBind benchmark scores and the ECFP ridge control do not have the same role. The public benchmark scores are externally supplied fixed scores. ECFP ridge is a supervised ligand-only out-of-fold prediction generated by shuffled 5-fold cross-validation using raw pKD from the same EV-A71 2A campaign. The Morgan fingerprint used radius `2` and `2048` bits; Ridge alpha was `10`, and the split seed was `20260508`.

The difference between `0.097` and `0.430` is therefore not a model ranking under an identical training and evaluation contract. It is a diagnostic comparison showing that ligand representations alone, trained within the same campaign, can produce a higher correlation with MW+cLogP-adjusted pKD. Under this condition, it is difficult to identify an independent contribution from structural information from the public scores' raw-pKD correlation alone.

Table 3 retains this role distinction while compactly reporting Spearman correlation with MW+cLogP-adjusted pKD.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>Score source</th>
          <th>Highest method</th>
          <th>Structural information</th>
          <th class="align-right">MW+cLogP-adjusted pKD<br><span class="table-note-inline">Spearman</span></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Public benchmark score</td>
          <td>Boltz-2</td>
          <td>Uses structure/pose</td>
          <td class="align-right"><code>0.097</code></td>
        </tr>
        <tr>
          <td>Ligand-only<br><span class="table-note-inline">Same EV-A71 2A data</span></td>
          <td>ECFP ridge</td>
          <td>Not used</td>
          <td class="align-right"><code>0.430</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> Primary comparison between each score and MW+cLogP-adjusted pKD. The structural-information column distinguishes the roles of the public benchmark scores and the ligand-only control. Subtracting the ligand-only control Spearman from the highest public benchmark Spearman gives <code>-0.334</code> before rounding. This difference is not a performance difference between models trained under identical conditions; it is a diagnostic gap between public fixed scores and a campaign-supervised ligand control.</figcaption>
</figure>

Figure 1 places each score's Spearman correlation with measured pKD and MW+cLogP-adjusted pKD side by side. Correlations for the public scores generally weakened after adjustment, while controls built from ligand representations within the same campaign showed higher correlations.

### Resampling sensitivity

To assess sensitivity to compound composition, compound rows were resampled with replacement `1000` times while holding the already computed scores and out-of-fold predictions fixed. These ranges reflect correlation variation from resampling the current `494` compounds, not variation from retraining the models. Mean Spearman correlations with MW+cLogP-adjusted pKD were `0.096` for Boltz-2 and `0.429` for the ECFP ridge control; their respective 95% ranges were `[0.008, 0.179]` and `[0.354, 0.497]`.

Table 4 reports method-level uncertainty ranges for Spearman correlation with MW+cLogP-adjusted pKD.

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>Method</th>
          <th>Structural information</th>
          <th class="align-right">MW+cLogP-adjusted pKD<br><span class="table-note-inline">Mean Spearman</span></th>
          <th class="align-right">95% range</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>ECFP ridge</td><td>Not used</td><td class="align-right"><code>0.429</code></td><td class="align-right"><code>[0.354, 0.497]</code></td></tr>
        <tr><td>RDKit descriptor RF</td><td>Not used</td><td class="align-right"><code>0.337</code></td><td class="align-right"><code>[0.258, 0.413]</code></td></tr>
        <tr><td>RDKit descriptor ridge</td><td>Not used</td><td class="align-right"><code>0.263</code></td><td class="align-right"><code>[0.175, 0.345]</code></td></tr>
        <tr><td>Boltz-2</td><td>Uses structure/pose</td><td class="align-right"><code>0.096</code></td><td class="align-right"><code>[0.008, 0.179]</code></td></tr>
        <tr><td>Gnina crystal</td><td>Uses structure/pose</td><td class="align-right"><code>0.015</code></td><td class="align-right"><code>[-0.073, 0.104]</code></td></tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> Spearman ranges with MW+cLogP-adjusted pKD obtained by resampling compound rows <code>1000</code> times while holding the already computed scores and out-of-fold predictions fixed. The highest public benchmark correlation remained weakly positive, but did not reach the range of the ligand-only control in this comparison.</figcaption>
</figure>

The grouped bootstrap used Murcko scaffolds or Butina clusters as the resampling unit to test whether changes in the weight of particular chemical groups reversed the direction of the correlations. At each iteration, groups were sampled with replacement and Spearman correlation was recalculated over the compound rows belonging to those groups. ECFP ridge was not retrained with group-held-out folds, so this procedure does not remove the possibility that similar compounds occur in both training and evaluation folds.

Across `300` Murcko-scaffold resamples, the highest mean among public benchmark scores was `0.098` for Boltz-2, and the highest mean among ligand-only controls was `0.421` for ECFP ridge, a difference of `-0.323`. Figure 3 shows a separate Butina Tanimoto 0.6 resampling result: `0.075` for Boltz-2 and `0.395` for ECFP ridge, a difference of `-0.320`. The comparison direction was preserved under both groupings, but this measures group-weighting sensitivity of the current scores rather than chemical-series generalization.

> A **Murcko scaffold** groups similar compounds by their central molecular framework.
>
> **Butina Tanimoto 0.6** clusters compounds with high fingerprint similarity. Here it is used as a secondary check on whether similar compounds easily reverse the conclusion.

Figure 3 presents the Butina resampling result, while Table 5 reports the group composition, including the high singleton rate, and the resulting interpretive limit.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/openbind-affinity-baseline-audit/butina-grouped-residual-spearman.svg" alt="Forest plot comparing mean Spearman correlation with MW+cLogP-adjusted pKD as points and 95% ranges as lines after resampling fixed method scores and out-of-fold predictions by Butina Tanimoto 0.6 cluster">
  <figcaption><strong>Figure 3.</strong> Spearman correlation with MW+cLogP-adjusted pKD was recalculated for the already computed method scores and out-of-fold predictions using Butina Tanimoto 0.6 clusters as the resampling unit. Points show the means across <code>300</code> grouped-bootstrap iterations; lines show 95% ranges. Because the models were not retrained cluster-held-out, this measures sensitivity to cluster composition rather than chemical-series generalization.</figcaption>
</figure>

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>Grouping rule</th>
          <th class="align-right">Groups</th>
          <th class="align-right">Singleton groups</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Murcko scaffold</td>
          <td class="align-right"><code>275</code></td>
          <td class="align-right"><code>82.2%</code></td>
        </tr>
        <tr>
          <td>Butina Tanimoto 0.6</td>
          <td class="align-right"><code>175</code></td>
          <td class="align-right"><code>71.4%</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 5.</strong> Group composition for the grouped bootstrap. The high proportion of singleton groups and the absence of group-held-out retraining mean this is not a strict scaffold split. It tests only whether the direction of the current correlations is easily reversed by resampling weights assigned to particular chemical groups.</figcaption>
</figure>

### Prepared-structure descriptor follow-up

> A **prepared-structure descriptor** is a feature derived from public structures by calculating protein and ligand atom counts, minimum distances, contact counts at several distance thresholds, element pairs, and pocket-residue information, then aggregating means and maxima by compound. It is not a detailed interaction model; it coarsely summarizes size, distance, and contact counts around a prepared pose.

Separately from the public-score analysis, a limited follow-up tested whether simple prepared-structure descriptors added signal to the ligand representation. From the Zenodo v1 prepared-structure archive <a class="citation-ref" href="#ref-openbind-zenodo" aria-label="Reference 4">[4]</a>, `312` descriptors were created from atom counts, minimum distances, protein–ligand contacts at distance thresholds of `3.5`, `4.5`, `6.0`, and `8.0` Å, element pairs, and pocket-residue information.

All `925` structure files were parsed. Of these, `649` structure instances linked to public compound references were aggregated over `494` compounds and used as follow-up model inputs.

The ECFP baseline in this follow-up uses a different evaluation pipeline from the earlier ECFP ridge result of `0.430`. In the primary comparison, `0.430` is the correlation between a 5-fold out-of-fold score trained with ECFP to predict raw pKD and adjusted pKD computed over the full table. Here, `0.360` comes from sparse-scaling ECFP and retraining it under the same shuffled 5-fold cross-validation to predict adjusted pKD directly. It is therefore invalid to interpret the change from `0.430` to `0.360` as a performance decrease. The `0.360` value is an internal follow-up baseline for assessing the addition of prepared-structure descriptors.

Within this same follow-up pipeline, the model using prepared-structure descriptors alone reached Spearman `0.156`, the model adding the descriptors to ECFP reached `0.279`, and the ECFP-only baseline reached `0.360`. The difference after adding the descriptors was therefore `-0.081`.

Table 6 summarizes Spearman correlation with MW+cLogP-adjusted pKD after adding prepared-structure descriptors.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--compact-two-col">
      <thead>
        <tr>
          <th>Input information</th>
          <th class="align-right">MW+cLogP-adjusted pKD<br><span class="table-note-inline">Spearman</span></th>
        </tr>
      </thead>
      <tbody>
        <tr><td>ECFP only</td><td class="align-right"><code>0.360</code></td></tr>
        <tr><td>Prepared-structure descriptors</td><td class="align-right"><code>0.156</code></td></tr>
        <tr><td>ECFP + structure descriptors</td><td class="align-right"><code>0.279</code></td></tr>
        <tr><td>RDKit descriptors + ECFP</td><td class="align-right"><code>0.369</code></td></tr>
        <tr><td>RDKit descriptors + ECFP<br><span class="table-note-inline">+ structure descriptors</span></td><td class="align-right"><code>0.283</code></td></tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 6.</strong> Internal follow-up comparison trained under the same shuffled 5-fold cross-validation to predict MW+cLogP-adjusted pKD directly. Adding <code>312</code> distance, contact, and atom-count descriptors from prepared structures to ECFP produced a difference of <code>-0.081</code>; the 95% range from <code>1000</code> paired row-bootstrap iterations over fixed out-of-fold predictions was <code>[-0.146, -0.012]</code>.</figcaption>
</figure>

This result is limited to this coarse descriptor set and follow-up pipeline. It does not test whether the public methods use structural information, and it does not rule out gains from richer structural representations.

## Interpretation

The central point is that correlation between a public prediction score and measured pKD alone makes it difficult to determine how much of that correlation is attributable to structure-based affinity signal. Even when score and pKD rankings appear similar, separate checks are needed to assess whether the correlation may reflect protein–ligand structure, simple ligand properties, or the chemical-series composition of the campaign.

The public OpenBind benchmark scores moved to some extent with measured pKD. Across the public methods, however, correlation with MW+cLogP-adjusted pKD weakened, leaving open the possibility that raw pKD correlation overlaps with ligand-property trends such as compound size or lipophilicity.

The ligand-only controls, which use no structural information, showed stronger correlation with MW+cLogP-adjusted pKD in this retrospective audit. These controls are random-fold out-of-fold predictions trained on labels from the same campaign, so they neither replace the public benchmark scores nor demonstrate prospective model superiority. The scope of this comparison is narrower: when ligand information from the same campaign can produce higher correlation, it remains difficult to interpret the public scores' raw pKD correlation alone as strong evidence of structure-based affinity signal.

This conclusion is not a judgment on OpenBind as a whole or on structure-based affinity prediction in general. Interpreting the public prediction scores in this release as structural signal requires comparison not only with measured pKD, but also with simple property baselines such as molecular weight and cLogP and with ligand-only controls. A claim of structure-based generalization would further require group-held-out or prospective evaluation that separates new chemical series.

## Limitations

- These results are limited to one public EV-A71 2A release. This is not a prospective evaluation with new compounds separated in advance, and it does not assess the performance of OpenBind as a whole or of structure-based affinity prediction in general.
- MW+cLogP adjustment is a descriptive adjustment calculated across all `494` compounds. Property trends can be entangled with real potency changes, so adjusted pKD is not interpreted as ground truth for signal originating from structural information.
- The ECFP controls are random 5-fold out-of-fold models trained on raw pKD from the same campaign. They do not form a model ranking under conditions identical to the public fixed scores and do not measure generalization to new chemical series.
- The grouped bootstrap resamples chemical groups while holding existing scores and predictions fixed. Because it does not retrain group-held-out and has a high proportion of singleton groups, it neither removes analog leakage nor establishes scaffold generalization.
- Sensitivity to the rule used to consolidate measurement rows into compound-level pKD and to measurement uncertainty was not evaluated. The structure follow-up is also limited to `312` distance, contact, and atom-count descriptors aggregated from prepared poses, so it does not rule out the value of more detailed structural representations.

## Appendix: Evaluation and Reproduction Contract

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>Stage</th>
          <th>Fixed contract</th>
          <th>Interpretive boundary</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Input snapshot</td>
          <td><a href="https://github.com/OpenBind-Consortium/EV-A71_2A_benchmark/tree/86e5c12da518d749c33cfa9dcb6ae8eae1b804f9/affinity"><code>86e5c12</code> revision</a> of the OpenBind affinity repository and Zenodo <code>v1</code></td>
          <td>Rechecked on <code>2026-07-30</code> that the SHA-256 hashes of the <code>11</code> affinity inputs in the experiment provenance match the files at this revision</td>
        </tr>
        <tr>
          <td>MW+cLogP adjustment</td>
          <td>One OLS fit across all <code>494</code> compounds</td>
          <td>Descriptive adjustment calculated over the full table; not a cross-fitted target</td>
        </tr>
        <tr>
          <td>Ligand-only control</td>
          <td>Shuffled 5-fold CV, seed <code>20260508</code>; ECFP radius <code>2</code>, <code>2048</code> bits; Ridge alpha <code>10</code></td>
          <td>Compound-random OOF prediction; not a scaffold-disjoint evaluation</td>
        </tr>
        <tr>
          <td>Compound bootstrap</td>
          <td>Sample rows of fixed scores/predictions with replacement <code>1000</code> times</td>
          <td>Percentile 95% range; models and the MW+cLogP adjustment model are not refit</td>
        </tr>
        <tr>
          <td>Grouped bootstrap</td>
          <td>Sample Murcko or Butina Tanimoto 0.6 groups with replacement <code>300</code> times</td>
          <td>Group-weighting sensitivity, not group-held-out retraining</td>
        </tr>
        <tr>
          <td>Prepared-structure descriptor</td>
          <td>Parse <code>925</code> Zenodo v1 structures; aggregate <code>649</code> reference-linked instances into <code>494</code> compounds and <code>312</code> features</td>
          <td>Separate 5-fold pipeline trained directly on adjusted pKD; not compared directly with the primary ECFP result of <code>0.430</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 1.</strong> Evaluation contract required to reproduce and interpret the values in the main text. The analysis ran with Python <code>3.12.3</code>, NumPy <code>2.2.6</code>, pandas <code>2.3.3</code>, SciPy <code>1.17.1</code>, scikit-learn <code>1.7.1</code>, and RDKit <code>2026.03.1</code>.</figcaption>
</figure>

The core analysis can be rerun from the <a href="https://github.com/muted-color/openbind-affinity-score-audit">OpenBind Affinity Score Audit reproduction repository</a> <a class="citation-ref" href="#ref-openbind-audit-reproduction" aria-label="Reference 5">[5]</a>. The repository downloads input CSVs from the pinned OpenBind revision, verifies SHA-256 hashes, and reproduces compound-table reconstruction, MW+cLogP adjustment, ligand-only controls, and Murcko and Butina grouped sensitivity with one command. The prepared-structure descriptor follow-up is outside the public scope of the core audit.

{% include model-mention-cards.html label="Reproduction repository" aria_label="Public GitHub repository for reproducing the OpenBind affinity score audit" models="OpenBind Affinity Score Audit|muted-color/openbind-affinity-score-audit|https://github.com/muted-color/openbind-affinity-score-audit" %}

The main text retains only the values needed for interpretation. Appendix Table 2 is a supporting view of measured-pKD and MW+cLogP-adjusted-pKD Spearman correlations across all methods. It is intended to inspect the difference between the two correlations, not to establish a definitive method ranking.

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>Method</th>
          <th class="align-right">Measured pKD<br><span class="table-note-inline">Spearman</span></th>
          <th class="align-right">MW+cLogP-adjusted pKD<br><span class="table-note-inline">Spearman</span></th>
          <th class="align-right">Difference vs ECFP ridge</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>ECFP ridge</td><td class="align-right"><code>0.672</code></td><td class="align-right"><code>0.430</code></td><td class="align-right"><code>0.000</code></td></tr>
        <tr><td>RDKit descriptor RF</td><td class="align-right"><code>0.627</code></td><td class="align-right"><code>0.337</code></td><td class="align-right"><code>-0.093</code></td></tr>
        <tr><td>RDKit descriptor ridge</td><td class="align-right"><code>0.605</code></td><td class="align-right"><code>0.264</code></td><td class="align-right"><code>-0.166</code></td></tr>
        <tr><td>Boltz-2</td><td class="align-right"><code>0.397</code></td><td class="align-right"><code>0.097</code></td><td class="align-right"><code>-0.334</code></td></tr>
        <tr><td>Smina crystal</td><td class="align-right"><code>0.255</code></td><td class="align-right"><code>0.038</code></td><td class="align-right"><code>-0.392</code></td></tr>
        <tr><td>Gnina crystal</td><td class="align-right"><code>0.453</code></td><td class="align-right"><code>0.018</code></td><td class="align-right"><code>-0.412</code></td></tr>
        <tr><td>cLogP</td><td class="align-right"><code>0.174</code></td><td class="align-right"><code>0.014</code></td><td class="align-right"><code>-0.416</code></td></tr>
        <tr><td>molecular weight</td><td class="align-right"><code>0.484</code></td><td class="align-right"><code>-0.017</code></td><td class="align-right"><code>-0.448</code></td></tr>
        <tr><td>MW+cLogP ridge</td><td class="align-right"><code>0.484</code></td><td class="align-right"><code>-0.020</code></td><td class="align-right"><code>-0.451</code></td></tr>
        <tr><td>AqAffinity</td><td class="align-right"><code>0.117</code></td><td class="align-right"><code>-0.057</code></td><td class="align-right"><code>-0.487</code></td></tr>
        <tr><td>AEV-PLIG</td><td class="align-right"><code>0.227</code></td><td class="align-right"><code>-0.085</code></td><td class="align-right"><code>-0.516</code></td></tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 2.</strong> Method-level Spearman correlations with measured pKD and MW+cLogP-adjusted pKD. Differences versus ECFP ridge were calculated from the control's unrounded adjusted-pKD Spearman. This is a supporting table for comparing raw-pKD and adjusted-pKD correlations, not a direct ranking.</figcaption>
</figure>

## References

<div class="reference-list" markdown="1">

<ol>
  <li id="ref-openbind-first-release">OpenBind Consortium. <strong>OpenBind's first release: A structure-affinity dataset for structure-based AI</strong>. OpenBind, May 5, 2026. <a href="https://openbind.uk/news/blog-openbinds-first-release-a-structure-affinity-dataset-for-structure-based-ai/">OpenBind blog</a></li>
  <li id="ref-openbind-affinity-note">OpenBind Consortium. <strong>Affinity and Kinetics Data in the EV-A71 2A OpenBind Release</strong>. OpenBind, May 5, 2026. <a href="https://openbind.uk/news/blog-affinity-and-kinetics-data-in-the-ev-a71-2a-openbind-release/">OpenBind blog</a></li>
  <li id="ref-openbind-github">OpenBind Consortium. <strong>EV-A71_2A_benchmark affinity files</strong>. GitHub, revision <code>86e5c12</code>, 2026. <a href="https://github.com/OpenBind-Consortium/EV-A71_2A_benchmark/tree/86e5c12da518d749c33cfa9dcb6ae8eae1b804f9/affinity">Pinned repository directory</a>. Repository code: Apache-2.0; released data: CC0 1.0.</li>
  <li id="ref-openbind-zenodo">OpenBind Consortium. <strong>OpenBind Structure-Affinity Data Release: Enterovirus A71 (EV-A71) / Coxsackievirus A16 (CVA16) 2A protease</strong>. Zenodo, version v1, May 5, 2026. DOI: <a href="https://doi.org/10.5281/zenodo.20026661">10.5281/zenodo.20026661</a>. Data license: CC0 1.0.</li>
  <li id="ref-openbind-audit-reproduction">Soleaf. <strong>OpenBind Affinity Score Audit</strong>. GitHub, version <code>0.1.0</code>, 2026. <a href="https://github.com/muted-color/openbind-affinity-score-audit">Reproduction repository</a>. License: Apache-2.0.</li>
</ol>

</div>

The comparison unit and full method results are summarized in Table 1 and Appendix Table 2.

## Citation

Text citation:

```text
Ilho Ahn, "Auditing Structural-Signal Interpretation in OpenBind Prediction Scores", Mini Research, May 10, 2026.
```

BibTeX:

```bibtex
@misc{ahn2026openbind_affinity_baseline_check,
  author = {Ahn, Ilho},
  title = {Auditing Structural-Signal Interpretation in {OpenBind} Prediction Scores},
  year = {2026},
  month = {May},
  howpublished = {Mini Research},
  url = {https://muted-color.github.io/research/2026/05/10/openbind-affinity-baseline-audit/}
}
```
