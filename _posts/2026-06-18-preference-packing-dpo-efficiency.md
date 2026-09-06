---
title: "DPO Preference Packing: Dense Masks and Sparse Execution"
date: 2026-06-18 14:18:00 +0900
last_modified_at: 2026-09-06 09:26:32 +0900
lang: en
categories: ["LLM SYSTEMS"]
tags: [llm, dpo, preference-learning, preference-packing, sparse-attention, flexattention, fsdp, lora, qwen3]
lab_path: "projects/preference-packing-dpo-efficiency"
excerpt: "A DPO systems note separating shared-prompt layout requirements from dense and sparse execution, with recorded Qwen3-8B training-cost comparisons."
description: "A Qwen3-8B LoRA study reporting lower step time and allocated memory for sparse versus dense packed DPO, with small held-out metric differences and incomplete original validation records."
permalink: /research/2026/06/18/preference-packing-dpo-efficiency/
image: /assets/images/posts/preference-packing-dpo-efficiency/social-thumbnail.png
image_alt: "A three-panel chart comparing sparse packed DPO cost bars against dense packed baselines and showing held-out metric deltas near zero"
hero_image: /assets/images/posts/preference-packing-dpo-efficiency/hero-sparse-packing.svg
hero_alt: "A three-panel chart comparing sparse packed DPO cost bars against dense packed baselines and plotting held-out metric deltas near zero"
hero_caption: "<strong>Figure 1.</strong> Recorded sparse/dense packed cost ratios for the 200-step check and response-long repeats. The right panel shows aggregate held-out differences from the 200-step check; its separate metric scales and near-zero values do not establish log-probability or per-pair agreement. <a href='/assets/images/posts/preference-packing-dpo-efficiency/hero-sparse-packing.svg'>Open full-size figure</a>."
hero_frame: true
hero_compact: true
math: true
---

Rafailov et al.'s Direct Preference Optimization (DPO) trains on a preferred and a rejected response to the same prompt <a class="citation-ref" href="#ref-dpo" aria-label="Reference 3">[3]</a>. A conventional pairwise layout processes that prompt twice. Sharing it removes duplicate tokens. Correctness requires keeping the responses independent; the resulting cost also depends on how the attention backend executes the mask.

This note examines **response-context preservation and execution cost** in a trainer built with the TRL library and LoRA adapters. The main recorded comparison used Qwen3-8B on two GB10 nodes. Its 200-step sparse run used less step time and allocated memory than the dense packed run, while the reported held-out metric differences were small. The numerical validation records needed to establish implementation equivalence are no longer available for this revision.

## Summary

- Three paths separate the comparison: vanilla pairwise inputs, a shared prompt with dense masked attention, and the same packed layout with sparse block skipping.
- In the 200-step Qwen3-8B + LoRA comparison, sparse/dense ratios were `0.8066` for median step time and `0.6490` for rank-summed CUDA allocated memory: reductions of **19.34%** and **35.10%** in those recorded measures.
- Held-out sparse-minus-dense differences were `-0.0000118` in DPO loss and `+0.00195` in reward accuracy. Small aggregate differences do not establish token-level or per-pair agreement.
- Short checks and response-long repeats also recorded lower cost. Reward-accuracy differences had opposite signs across the two UltraFeedback variants, so the evidence does not support a general quality improvement.
- The scope is a finite-run implementation study. Original logs, complete configurations, and numerical parity-test outputs are unavailable; the retained summaries do not establish downstream quality or long-run convergence.

{% include model-mention-cards.html label="Main resources" aria_label="Main paper, model, and dataset resources for the preference packing experiment" models="Prefix Sharing for DPO|arXiv:2410.20305|https://arxiv.org/abs/2410.20305;Preference Packing|arXiv:2602.24082|https://arxiv.org/abs/2602.24082;Qwen3-8B|Qwen/Qwen3-8B|https://huggingface.co/Qwen/Qwen3-8B;H4 UltraFeedback|HuggingFaceH4/ultrafeedback_binarized|https://huggingface.co/datasets/HuggingFaceH4/ultrafeedback_binarized" %}

## Experimental Setup

### Prior work and implementation scope

Wang and Hegde's prefix-sharing work already combined a shared prompt with branch-aware masking and FlexAttention block skipping. Cho's Preference Packing likewise studied a shared-prompt layout for preference optimization <a class="citation-ref" href="#ref-prefix-sharing" aria-label="Reference 1">[1]</a> <a class="citation-ref" href="#ref-preference-packing" aria-label="Reference 2">[2]</a>. The implementation work recorded here applied these ideas to a TRL trainer and collator, then compared dense and sparse execution under LoRA and distributed training.

LoRA trains low-rank adapters while retaining the base weights; FSDP (Fully Sharded Data Parallel) distributes training state across devices. Table 1 lists the retained conditions for the main Qwen3-8B checks <a class="citation-ref" href="#ref-qwen3-8b" aria-label="Reference 4">[4]</a> <a class="citation-ref" href="#ref-lora" aria-label="Reference 5">[5]</a>.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead><tr><th>Component</th><th>Recorded condition</th></tr></thead>
      <tbody>
        <tr><td>Model and adaptation</td><td><code>Qwen/Qwen3-8B</code>, LoRA, bf16</td></tr>
        <tr><td>Distributed setting</td><td>Two GB10 nodes, FSDP, one GPU per node; <code>100GB</code> CUDA memory cap per node</td></tr>
        <tr><td>Reference policy</td><td>Base model with adapters temporarily disabled through <code>model.disable_adapter()</code></td></tr>
        <tr><td>200-step data</td><td>H4 UltraFeedback binarized, <code>512/512</code> train/eval slice</td></tr>
        <tr><td>Measured outcomes</td><td>Step time, CUDA allocated memory, held-out DPO loss, reward margin, and reward accuracy</td></tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> Retained conditions for the main distributed comparisons. These are a partial experiment specification; missing settings are listed under Limitations.</figcaption>
</figure>

### Layout requirements

Figure 2 separates input layout from backend execution. In the packed sequence, both responses use the same prompt, and each response can attend only to that prompt and its own preceding tokens.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/preference-packing-dpo-efficiency/layout-comparison.svg" alt="Diagram comparing vanilla pairwise, dense packed prior layout, and sparse-backed packed execution">
  <figcaption><strong>Figure 2.</strong> Layout-level comparison of the three paths. Vanilla pairwise duplicates prompt-side work, dense packed uses the packed layout with dense masked attention, and the sparse-backed path passes the branch structure to sparse block skipping.</figcaption>
</figure>

```text
prompt + chosen_branch + rejected_branch
```

The implementation account identifies three details needed to preserve the ordinary pairwise computation:

- **Branch-aware masking:** prevent either response from seeing the other response's tokens.
- **Aligned positions:** give response tokens the same `position_ids` they would have in their separate `prompt + response` sequence.
- **Explicit log-prob gathering:** select the logits that predict each response token, including the branch start.

The last detail matters because the first token of either response is predicted from the final prompt logits. A simple one-position shift over the packed sequence would instead predict the rejected branch's first token from the end of the chosen branch.

These are the layout requirements described by the implementation. The prior note reported successful log-prob checks, but retained neither their maximum error and tolerance nor the tested cases or gradient comparisons. The available record therefore supports the implementation rationale, without independently establishing numerical equivalence.

### Dense and sparse execution

The dense masked path can compute scores for positions it later masks:

```python
scores = q @ k.T
scores = scores.masked_fill(...)
```

A simple score-matrix size proxy makes the length trade-off visible. For a prompt of length $p$ and two responses of equal length $r$:

$$
C_{\mathrm{pairwise}} = 2(p+r)^2
$$

$$
C_{\mathrm{packed,dense}} = (p+2r)^2.
$$

At $p = 1024$ and $r = 1024$, the packed/pairwise proxy ratio is `1.125`. This is a dense attention-size illustration, not a total training-time prediction: it omits projections, feed-forward layers, communication, and backend-specific optimizations. Sharing the prompt can reduce those other token-dependent costs even when the dense attention proxy grows.

FlexAttention can use a block mask to skip fully masked blocks <a class="citation-ref" href="#ref-flexattention" aria-label="Reference 6">[6]</a>. In the sparse packed path, that includes blocks crossing between response branches. This is the execution distinction examined in the recorded comparisons.

### Reading the measurements

Time and memory ratios divide the named numerator by its baseline; lower values mean lower recorded cost. All held-out deltas below are **sparse minus dense**. Reward accuracy tracks the fraction of pairs for which the chosen response has the higher implicit DPO reward; reward margin tracks that reward difference. They are preference-training diagnostics, not an external judge's assessment of generated answers. The exact tie rule and aggregation settings are not retained.

Rank-summed memory was defined as the sum of per-rank `torch.cuda.max_memory_allocated()` peaks within each optimizer step, followed by the maximum of those step sums. Peaks on different ranks need not occur at the same instant. This measure excludes allocator reserved memory, CPU/UMA host allocation, model-load peaks, and other system processes; it is not total machine memory usage. The underlying peak-reset instrumentation cannot now be checked.

## Results

### Short mechanism checks

Table 2 compares the three execution paths in 5-step checks labeled prompt-long, balanced, and response-long. Those labels describe the relative prompt/response lengths; their exact token-length settings are not retained. The medians indicate lower cost for sparse packing, but do not recover the individual regime results or timing variability.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Comparison</th>
          <th class="align-right">Median step-time<br><span class="table-note-inline">ratio</span></th>
          <th class="align-right">Rank-summed<br><span class="table-note-inline">memory ratio</span></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>sparse packed /<br><span class="table-note-inline">dense packed</span></td>
          <td class="align-right"><code>0.7528</code></td>
          <td class="align-right"><code>0.6701</code></td>
        </tr>
        <tr>
          <td>sparse packed /<br><span class="table-note-inline">vanilla pairwise</span></td>
          <td class="align-right"><code>0.6395</code></td>
          <td class="align-right"><code>0.6046</code></td>
        </tr>
        <tr>
          <td>dense packed /<br><span class="table-note-inline">vanilla pairwise</span></td>
          <td class="align-right"><code>0.8495</code></td>
          <td class="align-right"><code>0.9022</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> Recorded 5-step mechanism checks. Each ratio divides the first layout by the second; lower is better. Values are medians across the three length regimes, so they summarize those checks rather than establish an improvement in every regime.</figcaption>
</figure>

The response-long repeats extended the sparse/dense comparison to `20` steps per run, using `64/192` train/eval slices and seeds `17` and `23`. The recorded median step-time ratio was `0.7647`, and the rank-summed memory ratio was `0.5968`. Mean reward-accuracy delta was `+0.00260`, with range `[0.0, +0.00521]`. These two seeds support a repeat check in that setting; they are not repeats of the separate 200-step experiment.

### UltraFeedback comparisons

Table 3 separates the two UltraFeedback variants rather than relying only on their aggregate <a class="citation-ref" href="#ref-argilla-ultrafeedback" aria-label="Reference 7">[7]</a> <a class="citation-ref" href="#ref-h4-ultrafeedback" aria-label="Reference 8">[8]</a>. The cost ratios were below one for both, while reward accuracy moved in opposite directions. These are two variants from the same dataset family, not two independent task families.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--numeric-columns">
      <thead>
        <tr><th>Dataset</th><th class="align-right">Step-time<br><span class="table-note-inline">ratio</span></th><th class="align-right">Rank-summed<br><span class="table-note-inline">memory ratio</span></th><th class="align-right">Reward accuracy<br><span class="table-note-inline">delta</span></th></tr>
      </thead>
      <tbody>
        <tr><td>Argilla UltraFeedback</td><td class="align-right"><code>0.8097</code></td><td class="align-right"><code>0.6521</code></td><td class="align-right"><code>+0.054688</code></td></tr>
        <tr><td>H4 UltraFeedback</td><td class="align-right"><code>0.8005</code></td><td class="align-right"><code>0.6719</code></td><td class="align-right"><code>-0.015625</code></td></tr>
        <tr><td>Recorded aggregate<br><span class="table-note-inline">median ratios; mean delta</span></td><td class="align-right"><code>0.8051</code></td><td class="align-right"><code>0.6620</code></td><td class="align-right"><code>+0.019531</code></td></tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> UltraFeedback comparisons labeled as 20-step runs in Figure 3. Cost ratios are sparse/dense; accuracy deltas are sparse minus dense. The positive mean accuracy delta does not describe both datasets.</figcaption>
</figure>

Average response lengths were roughly `338-416` tokens for training and `364-405` for evaluation. Exact slice sizes for these transfer checks are not retained in the text.

Figure 3 collects the recorded distributed cost ratios. Its rows summarize different checks and should not be treated as a common set of repeated measurements. The additional larger-eval row has incomplete condition metadata, preserved separately in the Appendix.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/preference-packing-dpo-efficiency/qwen3-fsdp-ratio-summary.svg" alt="Bar chart of sparse packed over dense packed step-time and rank-summed memory ratios across four Qwen3-8B FSDP checks">
  <figcaption><strong>Figure 3.</strong> Recorded Qwen3-8B + LoRA 2-node FSDP cost comparisons. Ratios are <code>sparse packed / dense packed</code>, so shorter bars are more efficient; blue bars show step time and gray bars show rank-summed allocated memory. Rows summarize different checks.</figcaption>
</figure>

### The 200-step comparison

The longest recorded comparison used the H4 UltraFeedback `512/512` train/eval slice from Table 1. Table 4 separates execution cost from the held-out metric differences summarized in Figure 1. Cost values are sparse/dense ratios; held-out values are sparse-minus-dense deltas.

<figure class="table-figure table-figure--metrics table-figure--compact-metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--compact-two-col">
      <thead><tr><th>Measure</th><th class="align-right">Value</th></tr></thead>
      <tbody>
        <tr><td>Median step time</td><td class="align-right"><code>0.8066</code></td></tr>
        <tr><td>Rank-summed<br><span class="table-note-inline">allocated memory</span></td><td class="align-right"><code>0.6490</code></td></tr>
        <tr><td>Held-out DPO loss</td><td class="align-right"><code>-0.0000118</code></td></tr>
        <tr><td>Held-out reward accuracy</td><td class="align-right"><code>+0.00195</code></td></tr>
        <tr><td>Held-out reward margin</td><td class="align-right"><code>+0.0000236</code></td></tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> Recorded 200-step comparison. The first two rows are sparse/dense cost ratios; the remaining rows are sparse-minus-dense held-out deltas. No uncertainty interval or numerical equivalence threshold is available.</figcaption>
</figure>

The time and rank-summed memory ratios correspond to `19.34%` and `35.10%` reductions relative to dense packed training. They describe the reported step and allocation measures; without startup/compile timings they do not establish the reduction in end-to-end job time.

The held-out deltas were small at this endpoint. Aggregate accuracy can remain close even if individual pair decisions change, and close loss values do not establish matching token log-probs or gradients. The result supports a recorded cost reduction with similar aggregate diagnostics in this finite run. The separately recorded, ambiguously labeled “final loss” values are retained in the Appendix and are not used to reconstruct held-out deltas.

## Limitations

- **Incomplete measurement records.** Absolute seconds per step and peak GB, timing variability, compile/warmup treatment, CUDA synchronization, and memory-reset details cannot be recovered from the retained summaries. This particularly limits interpretation of the 5-step checks.
- **Incomplete training specification.** Effective pair batch size, accumulation, learning rate, DPO temperature, LoRA configuration, exact length/truncation settings, software/model/data revisions, and the seed/repeat count for the 200-step comparison are not retained. Only the response-long repeat explicitly records two seeds.
- **Restricted baseline and quality claims.** The reported gains are within this implementation's comparisons. The actual vanilla/dense backend and matched optimization settings cannot be audited, so the results do not establish an advantage over an optimized SDPA or FlashAttention baseline. No human win-rate, generated-answer quality, or convergence beyond 200 steps was tested.
- **Restricted implementation coverage.** The recorded reference path disables LoRA adapters. Full fine-tuning with a separate frozen reference model is outside this study. Hardware and data coverage remain limited to the reported GB10 setting and Intel Orca-style / UltraFeedback-family data.

## Appendix: Incompletely specified records

**Final loss.** The earlier note separately recorded dense `0.69298` and sparse `0.69336` as “final loss.” Their difference is `+0.00038`, whereas the explicitly labeled held-out DPO loss delta is `-0.0000118`. The final-loss evaluation split and aggregation are unknown. They may refer to a different statistic; the record does not justify relabeling them as training loss or treating them as the source of the held-out delta.

**Max-rank memory.** An additional sparse/dense memory ratio of `0.6046` was labeled “max-rank.” Its exact aggregation across ranks and optimizer steps was not retained. The main comparison uses the rank-summed measure defined above.

**Larger-eval row.** Figure 3 preserves an additional row labeled “Larger eval robustness,” with `512 / 256 / 256 eval`, step-time ratio `0.820`, and memory ratio `0.688`. The dataset-to-count mapping and aggregation cannot be recovered. These displayed, rounded ratios remain in the figure as a retained record, without using that row to claim broader evaluation coverage.

## Experiment Resources

<div class="reference-list" markdown="1">

- **Available evidence:** numerical summaries and figures retained in this note. Original logs, full configurations, and numerical parity-test outputs were unavailable for the September 6, 2026 revision; no new training or evaluation was run.
- **Implementation availability:** the [previously linked repository](https://github.com/muted-color/preference-packing-dpo-efficiency) returned HTTP 404 on unauthenticated access on September 6, 2026. It is not currently an accessible reproduction artifact.

</div>

## References

<div class="reference-list" markdown="1">

<ol>
  <li id="ref-prefix-sharing">Wang, Franklin and Hegde, Sumanth. <strong>Accelerating Direct Preference Optimization with Prefix Sharing</strong>. arXiv:2410.20305, 2024. <a href="https://arxiv.org/abs/2410.20305">arXiv</a></li>
  <li id="ref-preference-packing">Cho, Jaekyung. <strong>Preference Packing: Efficient Preference Optimization for Large Language Models</strong>. arXiv:2602.24082, 2026. <a href="https://arxiv.org/abs/2602.24082">arXiv</a></li>
  <li id="ref-dpo">Rafailov, Rafael et al. <strong>Direct Preference Optimization: Your Language Model is Secretly a Reward Model</strong>. arXiv:2305.18290, 2023. <a href="https://arxiv.org/abs/2305.18290">arXiv</a></li>
  <li id="ref-qwen3-8b">Qwen Team. <strong>Qwen3-8B</strong>. Hugging Face model repository. <a href="https://huggingface.co/Qwen/Qwen3-8B">Model card</a></li>
  <li id="ref-lora">Hu, Edward J. et al. <strong>LoRA: Low-Rank Adaptation of Large Language Models</strong>. arXiv:2106.09685, 2021. <a href="https://arxiv.org/abs/2106.09685">arXiv</a></li>
  <li id="ref-flexattention">PyTorch. <strong>FlexAttention</strong>. PyTorch documentation. <a href="https://docs.pytorch.org/docs/stable/nn.attention.flex_attention.html">Docs</a></li>
  <li id="ref-argilla-ultrafeedback">Argilla. <strong>UltraFeedback Binarized Preferences Cleaned</strong>. Hugging Face dataset repository. <a href="https://huggingface.co/datasets/argilla/ultrafeedback-binarized-preferences-cleaned">Dataset card</a></li>
  <li id="ref-h4-ultrafeedback">Hugging Face H4. <strong>UltraFeedback Binarized</strong>. Hugging Face dataset repository. <a href="https://huggingface.co/datasets/HuggingFaceH4/ultrafeedback_binarized">Dataset card</a></li>
</ol>

</div>

## Citation

Text citation:

```text
Ilho Ahn, "DPO Preference Packing: Dense Masks and Sparse Execution", Mini Research, June 18, 2026.
```

BibTeX:

```bibtex
@article{ahn2026preferencepackingdpo,
  author = {Ilho Ahn},
  title = {DPO Preference Packing: Dense Masks and Sparse Execution},
  journal = {Mini Research},
  year = {2026},
  month = jun,
  url = {https://muted-color.github.io/research/2026/06/18/preference-packing-dpo-efficiency/}
}
```
