---
title: "Carbon-3B: Measuring 6-mer Token Phase Sensitivity"
date: 2026-05-23 16:50:00 +0900
last_modified_at: 2026-07-30 21:59:25 +0900
lang: en
categories: ["BIO ML"]
tags: [carbon-3b, dna-foundation-model, brca2, variant-effect-prediction, tokenization, phase-sensitivity, fns]
lab_path: "experiment-lab/projects/carbon-6mer-phase-sensitivity"
excerpt: "A test of how much 6-mer token phase changes Carbon-3B scores relative to score IQR across 500 BRCA2 MAVE SNVs, and how the corresponding FNS pipeline differs."
description: "Across 500 BRCA2 MAVE SNVs scored with Carbon-3B, the 6-mer token phase range exceeded a prespecified 0.10 threshold, while the FNS pipeline showed lower ranges than the corresponding token conditions."
permalink: /research/2026/05/23/carbon-6mer-phase-sensitivity/
image: /assets/images/posts/carbon-6mer-phase-sensitivity/social-thumbnail.png
image_alt: "Bar chart comparing 6-mer phase sensitivity across Carbon-3B scoring conditions with a prespecified 0.10 reference threshold"
hero_image: /assets/images/posts/carbon-6mer-phase-sensitivity/phase-instability-by-scorer.svg
hero_alt: "Bar chart comparing normalized phase ranges for full-sequence FNS, local-target FNS, downstream token, full-window token, and target-token scores"
hero_caption: "<strong>Figure 1.</strong> Normalized phase ranges across scoring conditions for 500 SNVs sampled from the BRCA2 MAVE. The dashed line marks the prespecified 0.10 reference threshold. All three token conditions exceeded it; both FNS conditions were lower than their corresponding token conditions but remained above the threshold."
hero_frame: true
hero_compact: true
hero_variant: featured-plot
---

Carbon presents non-overlapping 6-mer tokenization as an efficiency trade-off: encoding six nucleotides per token expands the nucleotide context covered by a fixed token budget, and the authors report that this scheme worked better than BPE for DNA. FNS is presented as the bridge from this coarse representation to single-nucleotide supervision and scoring <a class="citation-ref" href="#ref-carbon-paper" aria-label="Reference 1">[1]</a> <a class="citation-ref" href="#ref-carbon-3b" aria-label="Reference 2">[2]</a>.

Because Carbon also reports training-free VEP (variant effect prediction) results on BRCA2, phase stability is a practical complementary question: does the same SNV receive a stable reference-minus-alternative score across the six possible token offsets? This note tests that scoring-protocol question in 500 BRCA2 MAVE SNVs and compares the corresponding token and FNS pipelines; it does not re-evaluate overall Carbon VEP performance.

The normalized token-score phase range exceeded the 0.10 reference threshold across most variants. The paired FNS pipeline comparisons showed lower ranges, but the sensitivity remained.

> **6-mer phase** is the offset occupied by the variant base within a 6 bp token. Here, the same SNV is scored at all six phases.
>
> **MAVE** stands for multiplexed assay of variant effect. The BRCA2 resource from Huang et al. measures the functional effects of many variants in parallel.
>
> **FNS** stands for Factorised Nucleotide Supervision, Carbon's mechanism for connecting coarse 6-mer modeling to position-wise nucleotide supervision and scoring.

{% include model-mention-cards.html label="Primary resources" aria_label="Carbon and BRCA2 evaluation resources" models="Carbon-3B|HuggingFaceBio/Carbon-3B|https://huggingface.co/HuggingFaceBio/Carbon-3B;Carbon evaluation README|huggingface/carbon evaluation|https://github.com/huggingface/carbon/blob/main/evaluation/README.md;BRCA2 MAVE|Huang et al. Nature 2025|https://doi.org/10.1038/s41586-024-08388-8" %}

## Summary

- The evaluation covers six token offsets for 500 BRCA2 MAVE SNVs: 85 LOF (loss-of-function) and 415 FUNC (functional)/INT (intermediate). Phase range is normalized by scorer-specific score IQR, with 0.10 as the prespecified reference threshold.
- Median normalized ranges were 0.409 for Full-window, 0.349 for Target-token, and 0.466 for Downstream-only; 93.6–100% of variants met or exceeded 0.10.
- Target-token is the most direct measure of sensitivity in scoring the variant-containing token. Full-window and Downstream-only also include global segmentation and edge/context changes; the shifted-reference control prevents a purely local attribution.
- FNS ranges were lower at 0.353 for Full-sequence and 0.331 for Local-target. Median paired differences were 0.0544 and 0.0198, but both FNS conditions remained above 0.10.

## Evaluation setup

The data are an SNV subset reconstructed from the Huang et al. BRCA2 MAVE resource against the hg19 chr13 reference <a class="citation-ref" href="#ref-huang-brca2" aria-label="Reference 4">[4]</a> <a class="citation-ref" href="#ref-brca2-source-table" aria-label="Reference 5">[5]</a> <a class="citation-ref" href="#ref-ucsc-hg19-chr13" aria-label="Reference 6">[6]</a>. Of 6,836 source variants that passed the reference-allele match and SNV filters, 500 were sampled with stratification and `seed=20260523`. Strata covered label, functional-score quantile, genomic-position decile, reference/alternative base, and genomic position modulo 6. The 100-variant protocol pilot is included in this subset.

The primary window is 8,190 bp. Its length is divisible by six, so it creates no tail padding in the Carbon tokenizer. An 8,192 bp window matching the Carbon BRCA2 evaluation was checked separately <a class="citation-ref" href="#ref-carbon-eval" aria-label="Reference 3">[3]</a> <a class="citation-ref" href="#ref-carbon-brca2-prep" aria-label="Reference 7">[7]</a> and was not mixed into the primary phase-score result.

<aside class="model-flow" aria-label="Evaluation flow" markdown="1">
  <p class="metric-detail__eyebrow">Evaluation flow</p>
<pre class="model-flow__diagram"><code>BRCA2 SNV
  -> six 8,190 bp phase windows
  -> reference / alternative sequence pair
  -> token score: Full-window, Target-token, Downstream-only
  -> FNS score: Full-sequence, Local-target
  -> per-variant phase range and normalized phase range</code></pre>
</aside>

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>Item</th>
          <th>Fixed value</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Model</td>
          <td><code>HuggingFaceBio/Carbon-3B</code><br><span class="table-note-inline">token <code>fe755cb5</code>; FNS revision <code>bf6f6bec</code></span></td>
        </tr>
        <tr>
          <td>Primary data</td>
          <td>500-SNV subset of the BRCA2 MAVE<br><span class="table-note-inline">LOF 85, FUNC/INT 415; seed 20260523</span></td>
        </tr>
        <tr>
          <td>Primary window</td>
          <td><code>8,190 bp</code><br><span class="table-note-inline">6-mer clean window; no partial-token tail</span></td>
        </tr>
        <tr>
          <td>Primary score</td>
          <td>Reference score minus alternative score</td>
        </tr>
        <tr>
          <td>Reference threshold</td>
          <td>Median phase range / score IQR &ge; <code>0.10</code><br><span class="table-note-inline">10% of score IQR as a scale-normalized effect-size threshold</span></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> Evaluation scope for testing scoring-protocol phase sensitivity in the 500-SNV BRCA2 MAVE subset.</figcaption>
</figure>

Within Table 1's scope, score scales differ across scoring methods. Token conditions are distinguished by the region over which scores are aggregated.

- **Full-window** averages log-probability scores over all valid DNA tokens in the 8,190 bp window.
- **Target-token** uses only the single 6-mer token containing the variant.
- **Downstream-only** uses only tokens after the variant, measuring how the changed variant context affects subsequent token predictions in the autoregressive model.

FNS Full-sequence and FNS Local-target scores are also on different raw scales from token scores. Raw ranges are therefore not compared across scoring methods. For each variant, the numerator of the normalized phase range is the difference between the maximum and minimum scores across six phases. The denominator is one IQR calculated over all `score_ref_minus_alt` values for the same scorer across 500 variants × 6 phases. Reported values are the medians of the 500 variant-level normalized ranges.

The 0.10 reference threshold was prespecified during experiment design as 10% of score IQR. It provides a common relative scale for phase ranges whose raw score scales differ.

## Results

The primary result is phase sensitivity in token scores.

### Token phase sensitivity

Across the 500-SNV BRCA2 subset, normalized token-score phase ranges were 0.409 for Full-window, 0.349 for Target-token, and 0.466 for Downstream-only. These values were 3.5–4.7 times the prespecified 0.10 reference threshold, and 93.6–100% of variants met or exceeded it in each condition. Within this subset, phase sensitivity was distributed across variants rather than confined to a few outliers.

Target-token provides the most direct measure of sensitivity in scoring the variant-containing token; scorer-specific normalization is required for comparisons with the other token conditions.

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Token score condition</th>
          <th class="align-right">Median phase range</th>
          <th class="align-right">P90 phase range</th>
          <th class="align-right">Median range / score IQR</th>
          <th class="align-right">Variants at or above 0.10</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Full-window</td>
          <td class="align-right"><code>0.00634</code></td>
          <td class="align-right"><code>0.01801</code></td>
          <td class="align-right"><code>0.409</code></td>
          <td class="align-right"><code>99.6%</code></td>
        </tr>
        <tr>
          <td>Target-token</td>
          <td class="align-right"><code>1.87500</code></td>
          <td class="align-right"><code>4.12500</code></td>
          <td class="align-right"><code>0.349</code></td>
          <td class="align-right"><code>93.6%</code></td>
        </tr>
        <tr>
          <td>Downstream-only</td>
          <td class="align-right"><code>0.01206</code></td>
          <td class="align-right"><code>0.03633</code></td>
          <td class="align-right"><code>0.466</code></td>
          <td class="align-right"><code>100.0%</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> Phase sensitivity by token-score condition. Because raw phase ranges use different score scales, the primary comparison is the median variant-level phase range divided by the scorer-specific overall score IQR.</figcaption>
</figure>

Figure 2 expands the Table 2 distribution by variant to test whether the observation is driven by outliers. It shows the magnitude of per-variant phase sensitivity, not a direction associated with any phase. Each y-value is the range across a variant's six phase scores divided by the Full-window score IQR. The median was 0.41, the p90 was 1.16, and 498 of 500 variants met or exceeded the 0.10 threshold.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/carbon-6mer-phase-sensitivity/full-window-phase-range-distribution.svg" alt="Ranked distribution of per-variant six-phase ranges divided by score IQR for the Full-window token score">
  <figcaption><strong>Figure 2.</strong> Each point represents one variant. The y-axis shows its six-phase score range on a log scale, and the x-axis ranks variants from the smallest to largest range. The dashed line marks 0.10; 498/500 variants were at or above it.</figcaption>
</figure>

### Padding and shifted-reference control

An 8,190 bp sequence is divisible by six and creates no partial-token tail. The 8,192 bp window matching the Carbon BRCA2 evaluation creates a length-2 tail. Primary phase scores therefore use the 8,190 bp clean-window condition; the 8,192 bp condition is kept as a separate compatibility check.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>Check</th>
          <th>Condition</th>
          <th class="align-right">Observation</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Clean window</td>
          <td><code>8,190 bp</code></td>
          <td class="align-right"><code>0/3,000</code> partial-token tails</td>
        </tr>
        <tr>
          <td>Carbon BRCA2 compatibility window</td>
          <td><code>8,192 bp</code></td>
          <td class="align-right"><code>3,000/3,000</code> length-2 tails</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> Padding checks. The 8,190 bp window is the primary condition without a partial-token tail; 8,192 bp is used only for compatibility with the Carbon BRCA2 evaluation.</figcaption>
</figure>

Even after separating padding conditions, the six shifted windows change both edge bases and global 6-mer segmentation. The Full-window range therefore cannot be attributed to a purely local token-boundary effect.

For the shifted-reference control, reference windows without the alternative allele were moved through the same six-shift protocol. The median diagnostic ratio of this control range to the reference-minus-alternative Full-window phase range was 4.162, and the control range was at least as large as the Full-window phase range for 93.6% of variants. Because numerator and denominator measure different score quantities, this ratio is not an estimate of edge contribution.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/carbon-6mer-phase-sensitivity/edge-context-control.svg" alt="Histogram of per-variant reference-score ranges in the shifted-reference control">
  <figcaption><strong>Figure 3.</strong> Distribution of shifted-reference control ranges. The x-axis is the six-shift range in reference full-window likelihood and the y-axis is variant count. The control range was at least as large as the reference-minus-alternative Full-window phase range for 93.6% of variants; the median diagnostic ratio between the two ranges was 4.162.</figcaption>
</figure>

Target-token and Full-window should therefore be interpreted separately. Target-token indicates sensitivity of the token-containing-variant score to the six-shift protocol. Full-window is a protocol-level score that does not separate local tokenization, global segmentation, and window edge/context changes.

### Paired differences in the FNS pipeline

Within these bounds, FNS base-level scoring was compared with the corresponding token conditions. The normalized range was 0.353 for FNS Full-sequence versus 0.409 for token Full-window, and 0.331 for FNS Local-target versus 0.349 for token Target-token. Both FNS values exceeded the 0.10 threshold.

Figure 4 places both paired comparisons on the same normalized scale.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/carbon-6mer-phase-sensitivity/fns-mitigation-normalized-range.svg" alt="Bar chart comparing normalized phase ranges between token and FNS scores for full-sequence and local-target pairs">
  <figcaption><strong>Figure 4.</strong> Paired normalized phase ranges for FNS and token scores. FNS was lower in both pairs, but both FNS values remained above 0.10. Variant-level paired differences and bootstrap confidence intervals are reported in Table 4.</figcaption>
</figure>

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Comparison</th>
          <th class="align-right">Token range / IQR</th>
          <th class="align-right">FNS range / IQR</th>
          <th class="align-right">Token - FNS</th>
          <th class="align-right">95% CI</th>
          <th class="align-right">Variants with lower FNS</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Full-sequence<br><span class="table-note-inline">FNS vs token</span></td>
          <td class="align-right"><code>0.409</code></td>
          <td class="align-right"><code>0.353</code></td>
          <td class="align-right"><code>0.0544</code></td>
          <td class="align-right"><code>[0.0362, 0.0709]</code></td>
          <td class="align-right"><code>64%</code></td>
        </tr>
        <tr>
          <td>Local-target<br><span class="table-note-inline">FNS vs token</span></td>
          <td class="align-right"><code>0.349</code></td>
          <td class="align-right"><code>0.331</code></td>
          <td class="align-right"><code>0.0198</code></td>
          <td class="align-right"><code>[0.0118, 0.0294]</code></td>
          <td class="align-right"><code>58%</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> Paired normalized-range differences in the FNS pipeline. <code>Token - FNS</code> is the median per-variant paired difference, not the difference between displayed medians. The final column reports the proportion of variants with lower FNS values. Post-hoc CIs use 10,000 variant bootstrap resamples with fixed scorer-specific IQR denominators (<code>seed=20260523</code>).</figcaption>
</figure>

The token and FNS revisions use the same safetensor weight blob, but their scorer configuration and modeling/tokenizer code differ. Table 4 therefore reports an observed pipeline-level difference in normalized range, not the causal effect of the FNS objective alone.

### Label-direction signal

The results above establish sensitivity to the six-shift scoring protocol. As a separate sanity check, LOF was treated as the positive class and AUROC was used to test whether Carbon scores aligned with the BRCA2 MAVE label direction.

Scores were first averaged across six phases for each variant. On the 500-SNV subset, this mean-score AUROC was 0.913 for both Full-window token and Full-sequence FNS after rounding to three decimals. Both exceeded the p95 of scorer-specific null distributions created by 500 label permutations, indicating that label-direction signal remained in the phase-sensitive scores.

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Score</th>
          <th class="align-right">Observed AUROC</th>
          <th class="align-right">Shuffled null p95</th>
          <th>Interpretation</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Full-window token<br><span class="table-note-inline">Six-phase mean score</span></td>
          <td class="align-right"><code>0.913</code></td>
          <td class="align-right"><code>0.553</code></td>
          <td>Signal separating LOF from FUNC/INT remained.</td>
        </tr>
        <tr>
          <td>Full-sequence FNS<br><span class="table-note-inline">Six-phase mean score</span></td>
          <td class="align-right"><code>0.913</code></td>
          <td class="align-right"><code>0.559</code></td>
          <td>AUROC was nearly identical to Full-window token.</td>
        </tr>
        <tr>
          <td>Local-target FNS<br><span class="table-note-inline">Six-phase mean score</span></td>
          <td class="align-right"><code>0.760</code></td>
          <td class="align-right"><code>0.559</code></td>
          <td>This local score has a different role from the full-sequence conditions.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 5.</strong> Observed AUROC was calculated after averaging the six phase scores for each variant. Shuffled null p95 is the 95th percentile of 500 label-permuted AUROCs generated with seed <code>20260523</code>.</figcaption>
</figure>

## Interpretation and conclusion

Across the 500-SNV BRCA2 subset, six-shift sensitivity in Carbon-3B token scores was present for most variants rather than a few outliers. Target-token is the most direct measure here of sensitivity in scoring the token containing the variant. Full-window and Downstream-only additionally include changes to global segmentation and window edge/context.

Under this protocol, the nucleotide-resolution FNS pipeline showed lower normalized ranges—from 0.409 to 0.353 for the full-sequence pair and from 0.349 to 0.331 for the local-target pair—but did not eliminate the observed six-shift sensitivity; both FNS conditions remained above 0.10. Mean-score AUROC showed that label-direction signal remained, but it does not alter the phase-sensitivity finding or establish overall Carbon VEP performance.

For Carbon SNV scoring under similar conditions, reporting a six-phase summary and range is therefore more appropriate than reporting a single reference-phase score. The mean used here is one possible summary, not the result of an aggregation-method comparison. Storing only one value makes allele-associated score differences difficult to separate from variation introduced by window and tokenization choices.

Three reporting rules follow for this setting:

1. Report the six-phase range or an instability flag alongside the reference-minus-alternative score.
2. Where FNS is available, compare token and FNS scores with paired normalized metrics and report the result as an observed pipeline-level difference.
3. Keep the 8,190 bp clean-window score separate from the 8,192 bp compatibility check with padding. If 8,192 bp is used, report the padding-tail check and its scores separately.

## Limitations

- Results are limited to 500 SNVs from the BRCA2 MAVE and an 8,190 bp window. The 100-variant protocol pilot is included in the subset, although normalized ranges for all three token scorers also exceeded 0.10 in the remaining 400 variants.
- Bootstrap confidence intervals were not calculated for the primary phase effects. The values `0.409`, `0.349`, and `0.466` are observations above the prespecified effect-size threshold in this subset; generalization to other genes or window conditions requires further evaluation.
- The shifted-reference control changes both edge context and global 6-mer segmentation phase. It does not separate a pure edge effect, a local token-boundary effect, or their causal contributions.
- Table 5 AUROCs exceeded the shuffled-label null, but no simple sequence/position baseline, reverse-complement evaluation, or external VEP benchmark was included. These results do not establish overall Carbon VEP performance or improved biological performance from FNS.
- The paired FNS confidence intervals are from a post-hoc audit rather than the prespecified primary analysis. Differences in scorer code and normalization scale between token and FNS revisions prevent isolation of the FNS objective's effect.

## Appendix: Reproduction conditions

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>Computation</th>
          <th>Role</th>
          <th class="align-right">Items</th>
          <th class="align-right">Runtime</th>
          <th class="align-right">Peak CUDA memory</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Token scoring</td>
          <td>Token-based variant scores</td>
          <td class="align-right"><code>12,000</code> scoring items<br><span class="table-note-inline"><code>3,000</code> window checks; 0 errors</span></td>
          <td class="align-right"><code>1,192.93 s</code></td>
          <td class="align-right"><code>14.40 GB</code></td>
        </tr>
        <tr>
          <td>FNS scoring</td>
          <td>FNS-based scores</td>
          <td class="align-right"><code>6,000</code> scoring items<br><span class="table-note-inline"><code>6,000</code> paired-comparison items; 0 errors</span></td>
          <td class="align-right"><code>1,149.77 s</code></td>
          <td class="align-right"><code>8.33 GB</code></td>
        </tr>
        <tr>
          <td>Auxiliary checks</td>
          <td>Padding checks</td>
          <td class="align-right"><code>6,000</code> padding-check items</td>
          <td class="align-right"><code>13.21 s</code></td>
          <td class="align-right">N/A</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 1.</strong> Reproduction conditions by computation. Model revisions, input hashes, sampling seed, and score artifacts are preserved in the separate experiment record.</figcaption>
</figure>

## References

<div class="reference-list" markdown="1">

<ol>
  <li id="ref-carbon-paper">Ben Allal, L., Li, Q., Fiusco, M. et al. <strong>Carbon: Decoding the Language of Life</strong>. <em>bioRxiv</em>, 2026.05.22.727119, 2026. DOI: <a href="https://doi.org/10.64898/2026.05.22.727119">10.64898/2026.05.22.727119</a></li>
  <li id="ref-carbon-3b">Hugging Face Biology Research. <strong>Carbon-3B model card and pinned scorer revisions</strong>. Hugging Face, 2026. <a href="https://huggingface.co/HuggingFaceBio/Carbon-3B">Model card</a>; token revision <a href="https://huggingface.co/HuggingFaceBio/Carbon-3B/tree/fe755cb5c7498acbf630080609ef61ecc4e36c17"><code>fe755cb5</code></a>; FNS revision <a href="https://huggingface.co/HuggingFaceBio/Carbon-3B/tree/bf6f6bec000ea6ced8cb656d02f3120a24795c91"><code>bf6f6bec</code></a>. Accessed 2026-07-30.</li>
  <li id="ref-carbon-eval">Hugging Face Biology Research. <strong>Carbon evaluation README</strong>. GitHub, 2026. <a href="https://github.com/huggingface/carbon/blob/0c4a63e985f376426d3e656a4be875e27440473f/evaluation/README.md">pinned evaluation README</a>. Accessed 2026-05-23.</li>
  <li id="ref-huang-brca2">Huang, H., Hu, C., Na, J. et al. <strong>Functional evaluation and clinical classification of BRCA2 variants</strong>. <em>Nature</em> 638, 528-537, 2025. DOI: <a href="https://doi.org/10.1038/s41586-024-08388-8">10.1038/s41586-024-08388-8</a></li>
  <li id="ref-brca2-source-table">Huang et al. <strong>Functional evaluation and clinical classification of BRCA2 variants</strong>, Supplementary Table 3. Nature/Springer, 2025. <a href="https://static-content.springer.com/esm/art%3A10.1038%2Fs41586-024-08388-8/MediaObjects/41586_2024_8388_MOESM3_ESM.xlsx">Supplementary Table S3 XLSX</a></li>
  <li id="ref-ucsc-hg19-chr13">UCSC Genome Browser. <strong>hg19/GRCh37 chr13 chromosome FASTA, goldenPath</strong>. <a href="https://hgdownload.soe.ucsc.edu/goldenPath/hg19/chromosomes/chr13.fa.gz">chr13.fa.gz</a>. Accessed 2026-05-23.</li>
  <li id="ref-carbon-brca2-prep">Hugging Face Biology Research. <strong>Carbon BRCA2 data preparation script</strong>. <a href="https://raw.githubusercontent.com/huggingface/carbon/0c4a63e985f376426d3e656a4be875e27440473f/evaluation/data_prep/prep_brca2.py">pinned <code>prep_brca2.py</code></a>. Source content frozen with the experiment inputs; accessed 2026-05-23.</li>
</ol>

Appendix Table 1 summarizes the computations. Detailed reproduction metadata are preserved in the experiment record referenced by the front matter <code>lab_path</code>.

</div>

## Citation

Text citation:

```text
Ilho Ahn, "Carbon-3B: Measuring 6-mer Token Phase Sensitivity", Mini Research, May 23, 2026.
```

BibTeX:

```bibtex
@misc{ahn2026carbon_6mer_phase_sensitivity,
  author = {Ahn, Ilho},
  title = {Carbon-3B: Measuring {6-mer} Token Phase Sensitivity},
  year = {2026},
  month = {May},
  howpublished = {Mini Research},
  url = {https://muted-color.github.io/research/2026/05/23/carbon-6mer-phase-sensitivity/}
}
```
