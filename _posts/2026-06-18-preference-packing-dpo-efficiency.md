---
title: "Where Sparse-Backed Preference Packing Reduced DPO Training Cost"
date: 2026-06-18 14:18:00 +0900
last_modified_at: 2026-06-18 20:17:34 +0900
categories: ["LLM SYSTEMS"]
tags: [llm, dpo, preference-learning, preference-packing, sparse-attention, flexattention, fsdp, lora, qwen3]
lab_path: "projects/preference-packing-dpo-efficiency"
excerpt: "A DPO efficiency note evaluating a sparse-backed implementation path for prior preference packing."
description: "A Qwen3-8B LoRA 2-node FSDP note evaluating a sparse-backed implementation path for prior preference packing, with DPO log-prob parity, dense-versus-sparse comparison, and bounded FSDP validation."
permalink: /research/2026/06/18/preference-packing-dpo-efficiency/
image: /assets/images/posts/preference-packing-dpo-efficiency/social-thumbnail.png
image_alt: "A three-panel chart comparing sparse packed DPO cost bars against dense packed baselines and showing held-out metric deltas near zero"
hero_image: /assets/images/posts/preference-packing-dpo-efficiency/hero-sparse-packing.svg
hero_alt: "A three-panel chart comparing sparse packed DPO cost bars against dense packed baselines and plotting held-out metric deltas near zero"
hero_caption: "<strong>Figure 1.</strong> Three-panel summary of the main result. Cost panels compare sparse packed bars against the dense packed baseline; the held-out panel plots DPO loss and reward accuracy deltas near the zero line."
hero_frame: true
hero_compact: true
math: true
---

DPO has a simple-looking inefficiency: each preference pair usually evaluates the same prompt twice, once as `prompt + chosen` and once as `prompt + rejected` <a class="citation-ref" href="#ref-dpo" aria-label="Reference 2">[2]</a>. Preference packing, introduced by Cho, removes that duplicate prompt by keeping one shared prompt and attaching the two responses as separate branches <a class="citation-ref" href="#ref-preference-packing" aria-label="Reference 1">[1]</a>.

This note does not propose preference packing itself and is not an official implementation of the paper. It evaluates and packages an implementation path around the prior layout: reproducing DPO response log-prob parity, separating dense masked packing from sparse-backed packing, and connecting the packed branch mask to a FlexAttention sparse backend. The useful result is not “pack the prompt once and stop there.” Dense attention still computes masked branch blocks, while response-long cases became efficient only when the branch-aware layout reached a backend that could skip those blocks.

The main check used `Qwen/Qwen3-8B` + LoRA, 2-node FSDP, and bf16 <a class="citation-ref" href="#ref-qwen3-8b" aria-label="Reference 3">[3]</a> <a class="citation-ref" href="#ref-lora" aria-label="Reference 4">[4]</a>. In the 200-step stability run, sparse packed training preserved held-out DPO metric parity while reducing median step-time ratio to `0.8066` and rank-summed CUDA allocated memory ratio to `0.6490`. This is an **efficiency plus tested metric parity** result, not downstream win-rate or long-convergence evidence.

> **Preference packing** is prior work from Cho 2026. It changes the input layout for preference pairs with the same prompt so the prompt tokens are not computed twice.
>
> **Branch-aware masking** prevents the chosen and rejected branches from attending to each other. If the branches can see each other, the packed layout no longer matches the original `prompt + response` log-prob computation.
>
> **Rank-summed CUDA allocated memory** sums per-rank `torch.cuda.max_memory_allocated()` peaks after aligning them by optimizer step. This note does not use rank0 alone or a simple `2 * rank0` estimate.

{% include model-mention-cards.html label="Main resources" aria_label="Main paper, model, and dataset resources for the preference packing experiment" models="Preference Packing|arXiv:2602.24082|https://arxiv.org/abs/2602.24082;Qwen3-8B|Qwen/Qwen3-8B|https://huggingface.co/Qwen/Qwen3-8B;H4 UltraFeedback|HuggingFaceH4/ultrafeedback_binarized|https://huggingface.co/datasets/HuggingFaceH4/ultrafeedback_binarized" %}

## Contributions

{% include model-mention-cards.html label="Code artifact" aria_label="Public GitHub repository and reusable trainer code" models="Public repository|muted-color/preference-packing-dpo-efficiency|https://github.com/muted-color/preference-packing-dpo-efficiency" %}

The contribution boundary is intentionally narrow. The original Preference Packing paper introduced the shared-prompt packed layout for RM/DPO preference data, including branch-aware masking and the broader packing-plus-sorting setup.

This repository contributes an implementation and evaluation layer around the prior layout: it reproduces the DPO response log-prob contract, packages a reusable TRL/LoRA trainer and collator, separates dense masked packing from sparse-backed packing, connects the packed branch mask to FlexAttention, and validates the path on GB10 2-node FSDP runs.

## Summary

- Dense packing adopted the prior layout but did not remove masked branch-block compute.
- Correct DPO parity required branch-aware masking, aligned `position_ids`, and explicit response-token target-position log-prob gathering.
- Sparse packed training made the response-long regime efficient in these checks by passing the branch mask to a sparse backend.
- In the Qwen3-8B + LoRA 2-node FSDP 200-step check, sparse packed training had step-time ratio `0.8066`, rank-summed memory ratio `0.6490`, DPO loss delta `-0.0000118`, and reward accuracy delta `+0.00195`.
- The claim is limited to efficiency plus tested held-out DPO metric parity.

## Evaluation Design

The evaluation has two checks. The first asks whether the prior packed layout reproduces ordinary pairwise DPO response log-probs. The second asks whether this repository's sparse backend path turns the same branch structure into lower step time and memory.

This separation matters because dense packing and sparse-backed packing answer different questions. Dense masks can make a packed sequence correct, but they do not by themselves skip masked branch-block computation. Sparse packed training passes the branch structure to a FlexAttention block mask so the backend can skip branch-crossing blocks <a class="citation-ref" href="#ref-flexattention" aria-label="Reference 5">[5]</a>.

### Prior Layout Validation

DPO loss depends on chosen/rejected response-token log-probs. A packed sequence is valid only if each response token sees the same context it would have seen in `prompt + response`.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/preference-packing-dpo-efficiency/layout-comparison.svg" alt="Diagram comparing vanilla pairwise, dense packed from Cho 2026, and sparse packed from this repository">
  <figcaption><strong>Figure 2.</strong> Layout-level comparison of the three paths. Vanilla pairwise duplicates prompt-side work, dense packed denotes the prior packed layout from Cho 2026 with dense masked attention, and sparse packed denotes this repository's backend path that passes the branch structure to sparse block skipping.</figcaption>
</figure>

A packed sequence is only useful if it also preserves the original target positions.

```text
prompt + chosen_branch + rejected_branch
```

Three pieces are required:

- branch-aware causal masking between chosen and rejected responses;
- `position_ids` aligned to the original `prompt + response` layout;
- explicit response-token target-position gathering instead of a plain shifted-label loss.

The first response token is the critical alignment case. It sits at a branch start in the packed sequence, but in the original layout it is predicted from the final prompt logits. The implementation therefore tracks response-token target positions directly.

### Sparse Backend Validation

Dense masking gives correctness, not compute skipping. A dense attention path still forms the score matrix and then masks forbidden positions.

```python
scores = q @ k.T
scores = scores.masked_fill(...)
```

If `p` is prompt length and `r` is each response length, response-long settings can make packed dense attention more expensive:

$$
\mathrm{vanilla\ dense\ cost}=2(p+r)^2
$$

$$
\mathrm{packed\ dense\ cost}=(p+2r)^2
$$

For `p = 1024` and `r = 1024`, the packed/vanilla proxy ratio is `1.125`. Prompt-long / short-response settings favored packing, but balanced and response-long settings were weaker because packed sequence length increased faster than dense attention compute disappeared.

Sparse packed training changes that response-long regime. It passes the branch-aware layout as a FlexAttention block mask, so branch-crossing blocks can be skipped instead of only hidden by an additive mask. Prompt de-duplication and branch-block skipping then work together.

### Measurement Scope

The main public numbers use `Qwen/Qwen3-8B` + LoRA, bf16, 2-node FSDP with one GPU per node, and a `100GB` CUDA memory cap per node. The compared layouts are vanilla pairwise, dense packed, and sparse packed. Quality checks use held-out DPO loss, reward margin, and reward accuracy.

Memory is reported as rank-aligned, rank-summed `torch.cuda.max_memory_allocated()`, not rank0 memory. The reported peak is the maximum per-step sum across ranks; it excludes allocator reserved memory, CPU/UMA host allocation, model-load peaks, and other system processes.

## Results

### Prior Layout Reproduction

The first result is correctness, not speed. The packed layout reproduced the DPO log-prob contract only after three implementation details were made explicit: branch-aware causal masking, original-layout `position_ids`, and response-token target-position gathering.

This reproduces the core layout requirement from prior preference packing in a TRL/LoRA trainer path. It does not claim the layout as a new method; it establishes that the trainer can evaluate the prior layout without silently changing the DPO objective.

### Sparse-Backed Efficiency

The sparse-backend check separates layout gains from block-skipping gains. Dense packing alone can help versus vanilla pairwise, but sparse packed training reduced both step time and memory further across the prompt-long, balanced, and response-long mechanism checks.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Comparison</th>
          <th class="align-right">Median step ratio</th>
          <th class="align-right">Rank-summed<br><span class="table-note-inline">memory ratio</span></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>sparse packed vs dense packed</td>
          <td class="align-right"><code>0.7528</code></td>
          <td class="align-right"><code>0.6701</code></td>
        </tr>
        <tr>
          <td>sparse packed vs vanilla pairwise</td>
          <td class="align-right"><code>0.6395</code></td>
          <td class="align-right"><code>0.6046</code></td>
        </tr>
        <tr>
          <td>dense packed vs vanilla pairwise</td>
          <td class="align-right"><code>0.8495</code></td>
          <td class="align-right">not reported</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> A 5-step mechanism check separating vanilla pairwise, dense packed, and sparse packed layouts. Dense packing helped versus vanilla pairwise, while connecting the packed mask to the sparse backend produced larger step-time and memory gains.</figcaption>
</figure>

The response-long repeat was the important stress case because dense-only packing had been weak there. With `64/192` train/eval slices, seeds `17` and `23`, and `20` steps per run, sparse packed training had median sparse/dense step ratio `0.7647` and rank-summed memory ratio `0.5968`. Mean reward accuracy delta was `+0.00260`, with range `[0.0, +0.00521]`.

### Bounded Qwen3-8B FSDP Evidence

Across Qwen3-8B + LoRA 2-node FSDP checks, sparse packed training stayed below dense packed training on time and rank-summed memory.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/preference-packing-dpo-efficiency/qwen3-fsdp-ratio-summary.svg" alt="Bar chart of sparse packed over dense packed step-time and rank-summed memory ratios across four Qwen3-8B FSDP checks">
  <figcaption><strong>Figure 3.</strong> Qwen3-8B + LoRA 2-node FSDP sparse packed results. Ratios are <code>sparse packed / dense packed</code>, so shorter bars are more efficient; blue bars show step time and gray bars show rank-summed memory.</figcaption>
</figure>

The UltraFeedback transfer check used two real preference datasets, not synthetic behavior checks. Argilla UltraFeedback had reward accuracy delta `+0.054688`, step ratio `0.8097`, and rank-summed memory ratio `0.6521`; H4 UltraFeedback had reward accuracy delta `-0.015625`, step ratio `0.8005`, and rank-summed memory ratio `0.6719` <a class="citation-ref" href="#ref-argilla-ultrafeedback" aria-label="Reference 6">[6]</a> <a class="citation-ref" href="#ref-h4-ultrafeedback" aria-label="Reference 7">[7]</a>. The aggregate was mean reward accuracy delta `+0.019531`, median step ratio `0.8051`, and median memory ratio `0.6620`. Average response lengths were roughly `338-416` tokens for train and `364-405` for eval.

The 200-step run strengthens finite-run stability evidence. It used the same Qwen3-8B + LoRA 2-node FSDP path on an H4 UltraFeedback binarized `512/512` train/eval slice.

Both sparse packed and dense packed training passed the same held-out metric and efficiency checks. Dense final loss was `0.69298`; sparse final loss was `0.69336`. Held-out DPO loss delta, sparse minus dense, was `-0.0000118`; reward accuracy delta was `+0.00195`; reward margin delta was `+0.0000236`. Median step ratio was `0.8066`, rank-summed memory ratio was `0.6490`, and max-rank memory ratio was `0.6046`.

This is still not a convergence claim; it only shows 200-step completion with the held-out DPO checks used here.

## Limitations

The result should be read as efficiency plus tested held-out metric parity, not as a downstream quality claim. It does not test human win-rate, generation quality, or long convergence beyond the 200-step stability run.

The implementation scope is also narrow. The reusable trainer targets LoRA/PEFT, with reference log-probs computed by temporarily disabling adapters through `model.disable_adapter()`. Full fine-tuning with a separate frozen reference model is not covered here.

Hardware and data coverage remain limited to the reported GB10 2-node bf16 FSDP runs and Intel Orca-style / UltraFeedback-family preference data. Other model families, tokenizer behavior, length distributions, and backend configurations need separate audits.

## References

<div class="reference-list" markdown="1">

<ol>
  <li id="ref-preference-packing">Cho, Jaekyung. <strong>Preference Packing: Efficient Preference Optimization for Large Language Models</strong>. arXiv:2602.24082, 2026. <a href="https://arxiv.org/abs/2602.24082">arXiv</a></li>
  <li id="ref-dpo">Rafailov, Rafael et al. <strong>Direct Preference Optimization: Your Language Model is Secretly a Reward Model</strong>. arXiv:2305.18290, 2023. <a href="https://arxiv.org/abs/2305.18290">arXiv</a></li>
  <li id="ref-qwen3-8b">Qwen Team. <strong>Qwen3-8B</strong>. Hugging Face model repository. <a href="https://huggingface.co/Qwen/Qwen3-8B">Model card</a></li>
  <li id="ref-lora">Hu, Edward J. et al. <strong>LoRA: Low-Rank Adaptation of Large Language Models</strong>. arXiv:2106.09685, 2021. <a href="https://arxiv.org/abs/2106.09685">arXiv</a></li>
  <li id="ref-flexattention">PyTorch. <strong>FlexAttention</strong>. PyTorch documentation. <a href="https://pytorch.org/docs/stable/nn.attention.flex_attention.html">Docs</a></li>
  <li id="ref-argilla-ultrafeedback">Argilla. <strong>UltraFeedback Binarized Preferences Cleaned</strong>. Hugging Face dataset repository. <a href="https://huggingface.co/datasets/argilla/ultrafeedback-binarized-preferences-cleaned">Dataset card</a></li>
  <li id="ref-h4-ultrafeedback">Hugging Face H4. <strong>UltraFeedback Binarized</strong>. Hugging Face dataset repository. <a href="https://huggingface.co/datasets/HuggingFaceH4/ultrafeedback_binarized">Dataset card</a></li>
</ol>

</div>

## Citation

Text citation:

```text
Ilho Ahn, "Where Sparse-Backed Preference Packing Reduced DPO Training Cost", Mini Research, June 18, 2026.
```

BibTeX:

```bibtex
@article{ahn2026preferencepackingdpo,
  author = {Ilho Ahn},
  title = {Where Sparse-Backed Preference Packing Reduced DPO Training Cost},
  journal = {Mini Research},
  year = {2026},
  month = jun,
  url = {https://muted-color.github.io/research/2026/06/18/preference-packing-dpo-efficiency/}
}
```
