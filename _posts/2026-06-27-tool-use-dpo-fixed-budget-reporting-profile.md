---
title: "A Fixed-Budget Audit of Specialized Tool-Use DPO Recipes"
date: 2026-06-27 11:04:00 +0900
last_modified_at: 2026-08-26 23:29:18 +0900
lang: en
categories: ["LLM EVAL"]
tags: [llm, tool-use, dpo, function-calling, bfcl, when2call, ifeval, qwen3]
lab_host: "dgx3"
lab_path: "projects/tool-use-dpo-negative-sources"
featured: true
home_rank: 2
excerpt: "Under a fixed DPO budget, specialized tool-use recipes moved different evaluation axes, while filtering, source mixing, and longer training did not consistently remove the trade-off."
description: "A fixed-budget empirical audit of specialized Qwen3-8B tool-use DPO recipes, testing evaluation-axis transfer, semantic filtering, mixed-source training, and checkpoint-dependent guardrail trade-offs."
permalink: /research/2026/06/27/tool-use-dpo-fixed-budget-reporting-profile/
translation_url: /research/2026/06/27/tool-use-dpo-fixed-budget-reporting-profile/ko/
image: /assets/images/posts/tool-use-dpo-fixed-budget-reporting-profile/hero-checkpoint-prism.png
image_alt: "Two equal translucent recipe streams pass through a clear checkpoint prism and emerge as three differently shaped evaluation signals"
hero_image: /assets/images/posts/tool-use-dpo-fixed-budget-reporting-profile/hero-checkpoint-prism.png
hero_alt: "Two equal translucent recipe streams pass through a clear checkpoint prism and emerge as three differently shaped evaluation signals"
hero_frame: true
hero_compact: true
---

Specialized tool-use DPO recipes may improve the evaluation axis closest to their training source without transferring the gain to other tool-use capabilities. A fixed-budget comparison can test this specialization and whether straightforward interventions reduce the resulting trade-off.

This note compares DPO negative recipes under the same pair budget and optimizer-step budget, using a tool-use SFT checkpoint based on `Qwen3-8B` as the shared reference <a class="citation-ref" href="#ref-qwen3" aria-label="Reference 1">[1]</a>. The evaluation asks whether function-call-structure-focused and call-decision-focused recipes transfer across evaluation axes, and whether semantic filtering, a 50:50 mixed-source recipe, or longer training resolves the observed trade-off. The result is an empirical audit of these conditions, not a general recipe ranking or a new reporting framework.

> **Tool-use DPO** is a preference-optimization setup where chosen/rejected pairs are built from tool-call outputs or tool-use decisions, and DPO is used to update the policy <a class="citation-ref" href="#ref-dpo" aria-label="Reference 2">[2]</a>. This note does not propose a new objective; it compares the changes associated with specialized recipes, pair filtering, source mixing, and checkpoint choice under a fixed budget.

{% include model-mention-cards.html label="Key evaluation resources" aria_label="Key evaluation resources for the fixed-budget tool-use DPO audit" models="Qwen3-8B|Qwen/Qwen3-8B|https://huggingface.co/Qwen/Qwen3-8B;When2Call|nvidia/When2Call|https://huggingface.co/datasets/nvidia/When2Call" %}

## Summary

- Under the same `3000`-pair and `375`-step budget, the function-call-structure-focused recipe scored higher on BFCL core, while the call-decision-focused recipe scored higher on When2Call. Neither recipe dominated both evaluation axes.
- Semantic filtering produced small or uncertain changes, and the 50:50 mixed-source condition did not match either specialist on its intended metric while recording lower IFEval accuracy than both.
- The final checkpoint had lower IFEval accuracy than the 50-step checkpoint in both quality-gated recipes, but the uncertainty does not support a general early-stopping rule.
- The evaluation-axis pattern repeated with two additional training seeds and one reconstructed pair pool. Prompt overlap and the single-run mixed condition limit the robustness claim.

## Public Artifacts

{% include model-mention-cards.html label="GitHub repository" aria_label="Tool-use DPO fixed-budget report GitHub repository" models="Artifact release|muted-color/tool-use-dpo-fixed-budget-report|https://github.com/muted-color/tool-use-dpo-fixed-budget-report" %}

{% include model-mention-cards.html label="Paper" aria_label="Tool-use DPO fixed-budget report paper PDF" models="Paper PDF|paper.pdf|https://github.com/muted-color/tool-use-dpo-fixed-budget-report/blob/main/paper.pdf" %}

The result tables in this note and Figure 1 can be checked against the public artifact repository using sanitized evaluation outputs and aggregate tables <a class="citation-ref" href="#ref-artifact-release" aria-label="Reference 3">[3]</a>.

## Evaluation Design

The comparison uses a shared Qwen3-8B tool-use SFT checkpoint and two specialized DPO recipes, each with a same-budget ungated control. Every condition uses `3000` preference pairs, `375` optimizer steps, beta `0.1`, learning rate `5e-6`, LoRA rank `16`, and effective batch size `8`. This fixes pair count and optimizer-step count, not source distributions or loss-bearing token counts.

The evaluation is read across three axes. **BFCL core** is mainly a structural function-calling axis, focused on function selection and argument correctness <a class="citation-ref" href="#ref-bfcl" aria-label="Reference 4">[4]</a>. **When2Call** evaluates call-decision behavior such as tool call, follow-up question, and unable-to-answer decisions <a class="citation-ref" href="#ref-when2call" aria-label="Reference 5">[5]</a>. The frozen macro-F1 evaluator includes direct answer as a zero-support class even though the public slice has no direct-answer gold rows, so the metric is not interpreted as balanced four-class coverage. **IFEval prompt-strict accuracy** is not the primary intended metric; it is a guardrail metric for measuring how much DPO perturbs instruction following <a class="citation-ref" href="#ref-ifeval" aria-label="Reference 6">[6]</a>.

## Results

The results are organized by evidence role: differences across the BFCL and When2Call evaluation axes, the downstream effect of the semantic quality gate, the mixed-source test, the checkpoint-dependent guardrail trade-off, and the claim boundary supported by the seed and pair-pool checks.

### Recipe Comparison Across Evaluation Axes

Table 1 compares the function-call-structure-focused and call-decision-focused recipes at the selected 50-step checkpoint. The checkpoint is an exploratory lower-regression reporting point selected after checkpoint analysis, not a pre-registered or universal early-stopping rule. Values are percentage-point deltas computed as the function-call-structure-focused recipe minus the call-decision-focused recipe. A positive BFCL row means the former scored higher; a negative When2Call row means the latter scored higher. In the tables, `W2C` abbreviates When2Call.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Condition</th>
          <th>Metric</th>
          <th class="align-right">Delta (pp)</th>
          <th class="align-right">95% CI low</th>
          <th class="align-right">95% CI high</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td rowspan="3">Semantic quality gate applied</td>
          <td>BFCL core</td>
          <td class="align-right"><code>+3.33</code></td>
          <td class="align-right"><code>+1.53</code></td>
          <td class="align-right"><code>+5.67</code></td>
        </tr>
        <tr>
          <td>W2C behavior acc.</td>
          <td class="align-right"><code>-6.67</code></td>
          <td class="align-right"><code>-10.75</code></td>
          <td class="align-right"><code>-3.02</code></td>
        </tr>
        <tr>
          <td>W2C macro F1</td>
          <td class="align-right"><code>-5.31</code></td>
          <td class="align-right"><code>-8.85</code></td>
          <td class="align-right"><code>-2.34</code></td>
        </tr>
        <tr>
          <td rowspan="2">Ungated control</td>
          <td>BFCL core</td>
          <td class="align-right"><code>+2.67</code></td>
          <td class="align-right"><code>+1.02</code></td>
          <td class="align-right"><code>+4.86</code></td>
        </tr>
        <tr>
          <td>W2C macro F1</td>
          <td class="align-right"><code>-4.21</code></td>
          <td class="align-right"><code>-7.48</code></td>
          <td class="align-right"><code>-1.23</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> Evaluation-axis deltas at the selected 50-step checkpoint, computed as the function-call-structure-focused recipe minus the call-decision-focused recipe using grouped bootstrap.</figcaption>
</figure>

The direction alone is not a causal effect of negative type. The call-decision training source belongs to the same task family as the When2Call evaluation, while prompts and chosen responses were not matched across recipes. The measured gaps are therefore treated as a repeatable recipe profile rather than source-intrinsic superiority.

### Role of the Semantic Quality Gate

Semantic filtering was used as a pair-quality gate: whether the rejected output was actually worse than the chosen output, schema-valid, and not an equivalent alternative. Within each recipe, Table 2 shows small or uncertain downstream differences between applying the semantic quality gate and using the same-budget ungated control.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Recipe</th>
          <th>Intended metric</th>
          <th class="align-right">Delta (pp)</th>
          <th class="align-right">95% CI</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Function-call structure</td>
          <td>BFCL core</td>
          <td class="align-right"><code>+0.33</code></td>
          <td class="align-right"><code>[0.00, +1.08]</code></td>
        </tr>
        <tr>
          <td>Call decision</td>
          <td>W2C macro F1</td>
          <td class="align-right"><code>+0.55</code></td>
          <td class="align-right"><code>[-0.83, +1.81]</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> Same-budget downstream-metric deltas, computed as the quality-gated condition minus the ungated control.</figcaption>
</figure>

Table 2 does not support removing the filter. Tool-use negatives easily mix optional/default/no-op differences, harmless normalization, acceptable alternate tools, and chosen/reference-suspect cases. A performance-improvement claim would require separate evidence; quality control and downstream movement are therefore reported separately.

### Mixed-Source Recipe

A 50:50 mixed-source recipe tested whether combining the two specialized sources could retain both intended-axis gains. It used `1500` quality-gated pairs from each source, for the same total budget of `3000` pairs and `375` optimizer steps.

At the 50-step checkpoint, the mixed-source recipe scored `0.700` on BFCL core, compared with `0.713` for the function-call-structure-focused recipe. Its When2Call macro F1 was `0.513`, compared with `0.530` for the call-decision-focused recipe. Its IFEval prompt-strict accuracy was `0.521`, below both specialized recipes (`0.573` and `0.583`). The mixed condition improved both intended axes relative to the SFT baseline, but it did not match either specialist on its intended metric and incurred greater guardrail regression than both. Simple source mixing therefore did not remove the observed trade-off under this budget; this condition is a single run without an additional seed or reconstructed-pool replicate.

### Checkpoint and Guardrail Trade-Off

Figure 1 plots intended-axis gain against IFEval prompt-strict regression, while Table 3 gives the corresponding absolute scores. Even within the same recipe, moving from the 50-step checkpoint to the final checkpoint changes both the intended metric and the guardrail metric.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/tool-use-dpo-fixed-budget-reporting-profile/pareto-2panel.svg" alt="Two-panel scatter plot of IFEval prompt-strict delta against BFCL core or When2Call macro F1 delta; Function-call structure and Call-decision paths connect Quality-gated and Ungated control points from the earlier checkpoint to the final checkpoint">
  <figcaption><strong>Figure 1.</strong> Intended-metric gains against IFEval prompt-strict deltas from the shared SFT baseline. The <em>Function-call structure</em> and <em>Call-decision</em> line styles identify the two recipes, the <em>Quality-gated</em> and <em>Ungated control</em> marker shapes identify the filtering conditions, and arrowheads run from the earlier checkpoint to the final checkpoint. Axes show percentage-point deltas using the report’s original domains.</figcaption>
</figure>

From 50 steps to the final checkpoint, the function-call-structure recipe's BFCL gain decreased by `2.00` points and IFEval accuracy decreased by `5.21` points (95% CI `[0.00, 10.42]`). For the call-decision recipe, When2Call macro F1 changed by `-0.18` points and IFEval accuracy by `-2.08` points (95% CI `[-2.08, 6.25]`). Both IFEval intervals reached or crossed zero.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Condition</th>
          <th>Checkpoint</th>
          <th class="align-right">BFCL core</th>
          <th class="align-right">W2C macro F1</th>
          <th class="align-right">IFEval prompt-strict</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>SFT baseline</td>
          <td>Selected</td>
          <td class="align-right"><code>0.667</code></td>
          <td class="align-right"><code>0.481</code></td>
          <td class="align-right"><code>0.635</code></td>
        </tr>
        <tr>
          <td rowspan="2">Function-call structure</td>
          <td>50 steps</td>
          <td class="align-right"><code>0.713</code></td>
          <td class="align-right"><code>0.477</code></td>
          <td class="align-right"><code>0.573</code></td>
        </tr>
        <tr>
          <td>Final</td>
          <td class="align-right"><code>0.693</code></td>
          <td class="align-right"><code>0.479</code></td>
          <td class="align-right"><code>0.521</code></td>
        </tr>
        <tr>
          <td rowspan="2">Call decision</td>
          <td>50 steps</td>
          <td class="align-right"><code>0.680</code></td>
          <td class="align-right"><code>0.530</code></td>
          <td class="align-right"><code>0.583</code></td>
        </tr>
        <tr>
          <td>Final</td>
          <td class="align-right"><code>0.660</code></td>
          <td class="align-right"><code>0.528</code></td>
          <td class="align-right"><code>0.562</code></td>
        </tr>
        <tr>
          <td>50:50 mixed source</td>
          <td>50 steps</td>
          <td class="align-right"><code>0.700</code></td>
          <td class="align-right"><code>0.513</code></td>
          <td class="align-right"><code>0.521</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> Absolute scores for the SFT baseline and quality-gated DPO conditions, reported as proportions where higher is better. IFEval prompt-strict accuracy is the guardrail axis.</figcaption>
</figure>

The results do not establish a general advantage for early checkpoints. Automatically reporting the final checkpoint can nevertheless hide the trade-off between intended-axis gain and guardrail regression. In this setting, checkpoint selection is part of the empirical claim.

### Robustness and Coverage Scope

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>Check</th>
          <th>Observed result</th>
          <th>Scope</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Training seeds</td>
          <td>Same direction across three seeds.<br><span class="table-note-inline">Gap ranges (pp): BFCL <code>3.00–4.00</code>; W2C accuracy <code>5.00–6.67</code>; W2C macro F1 <code>4.26–5.31</code>.</span></td>
          <td>Fixed pair pool only.</td>
        </tr>
        <tr>
          <td>Reconstructed pair pool</td>
          <td>No pair-id or content-hash overlap; prompt-id overlap was <code>401/3000</code> and <code>1337/3000</code>.<br><span class="table-note-inline">Reconstructed-pool gaps (pp): BFCL <code>3.33</code>; W2C accuracy <code>6.33</code>; W2C macro F1 <code>5.04</code>.</span></td>
          <td>One reconstruction; prompts are not independent.</td>
        </tr>
        <tr>
          <td>When2Call coverage</td>
          <td><code>27,952</code> labeled rows; <code>0</code> direct-answer gold rows.</td>
          <td>Three represented decision slices.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> Robustness checks and the scope supported by each result.</figcaption>
</figure>

## Interpretation

Tool-use DPO did not produce a uniform improvement across evaluation axes. The function-call-structure-focused recipe moved function-call correctness more, while the call-decision-focused recipe moved the represented call-decision slices more. The semantic quality gate did not produce a clear general downstream gain, and a 50:50 mixed-source recipe did not simultaneously match both specialists and the stronger guardrail result. Longer training reduced the function-call recipe's intended gain and increased its IFEval regression; the same IFEval direction for the call-decision recipe had wider uncertainty.

These results do not establish a new reporting framework. They show that a single metric or final checkpoint can hide recipe specialization, guardrail regression, and sampling scope. A Recipe-Checkpoint Profile is therefore used here only as a reporting implication: state the fixed budget, recipe, checkpoint, intended and guardrail metrics, seed scope, pair-sampling scope, and overlap results together.

## Limitations

The source distributions and prompts of the DPO training pairs were not matched across recipes. The call-decision-focused recipe uses a When2Call-style data family, so its training source is confounded with the related evaluation family. The evaluation-axis pattern is therefore a fixed-budget recipe comparison, not evidence that the negative failure type itself caused the axis difference or a causal ranking of source quality.

The fixed-budget condition is also limited. Pair count, optimizer steps, DPO recipe, and reference checkpoint were fixed, but token count and source distribution were not identical. All DPO conditions come from one Qwen3-8B SFT reference, one QLoRA DPO recipe, and one pair/step budget <a class="citation-ref" href="#ref-lora" aria-label="Reference 7">[7]</a> <a class="citation-ref" href="#ref-qlora" aria-label="Reference 8">[8]</a>. The mixed-source condition is a single run without its own seed or reconstructed-pool replicate.

The IFEval slice should be read as a guardrail diagnostic. Bootstrap intervals address evaluation-sample uncertainty, but they do not cover all uncertainty from training stochasticity, data sampling, or benchmark construction.

## References

<div class="reference-list" markdown="1">

<ol>
  <li id="ref-qwen3">Yang, An et al. <strong>Qwen3 Technical Report</strong>. arXiv:2505.09388, 2025. <a href="https://arxiv.org/abs/2505.09388">arXiv</a>; Qwen Team. <strong>Qwen3-8B</strong>. Hugging Face model repository. <a href="https://huggingface.co/Qwen/Qwen3-8B">Model card</a></li>
  <li id="ref-dpo">Rafailov, Rafael et al. <strong>Direct Preference Optimization: Your Language Model is Secretly a Reward Model</strong>. NeurIPS, 2023. <a href="https://arxiv.org/abs/2305.18290">arXiv</a></li>
  <li id="ref-artifact-release">Ahn, Ilho. <strong>Reporting Tool-Use DPO Under Fixed Budgets: Recipe–Checkpoint Profiles and Guardrail Trade-offs</strong>. Artifact release, June 5, 2026. <a href="https://github.com/muted-color/tool-use-dpo-fixed-budget-report/tree/arxiv-v1">Pinned artifact snapshot</a>; <a href="https://github.com/muted-color/tool-use-dpo-fixed-budget-report/blob/main/paper.pdf">Current paper PDF</a></li>
  <li id="ref-bfcl">Patil, Shishir G. et al. <strong>The Berkeley Function Calling Leaderboard (BFCL): From Tool Use to Agentic Evaluation of Large Language Models</strong>. ICML, 2025. <a href="https://proceedings.mlr.press/v267/patil25a.html">PMLR</a>; <a href="https://gorilla.cs.berkeley.edu/leaderboard.html">Project page</a></li>
  <li id="ref-when2call">Ross, Hayley, Mahabaleshwarkar, Ameya Sunil, and Suhara, Yoshi. <strong>When2Call: When (not) to Call Tools</strong>. NAACL, 2025. DOI: <a href="https://doi.org/10.18653/v1/2025.naacl-long.174">10.18653/v1/2025.naacl-long.174</a>; <a href="https://huggingface.co/datasets/nvidia/When2Call">Dataset card</a></li>
  <li id="ref-ifeval">Zhou, Jeffrey et al. <strong>Instruction-Following Evaluation for Large Language Models</strong>. arXiv:2311.07911, 2023. <a href="https://arxiv.org/abs/2311.07911">arXiv</a></li>
  <li id="ref-lora">Hu, Edward J. et al. <strong>LoRA: Low-Rank Adaptation of Large Language Models</strong>. ICLR, 2022. <a href="https://arxiv.org/abs/2106.09685">arXiv</a></li>
  <li id="ref-qlora">Dettmers, Tim et al. <strong>QLoRA: Efficient Finetuning of Quantized LLMs</strong>. NeurIPS, 2023. <a href="https://arxiv.org/abs/2305.14314">arXiv</a></li>
</ol>

</div>

## Citation

Text citation:

```text
Ilho Ahn, "A Fixed-Budget Audit of Specialized Tool-Use DPO Recipes", Mini Research, June 27, 2026.
```

BibTeX:

```bibtex
@article{ahn2026toolusedporeportingprofile,
  author = {Ilho Ahn},
  title = {A Fixed-Budget Audit of Specialized Tool-Use DPO Recipes},
  journal = {Mini Research},
  year = {2026},
  month = jun,
  url = {https://muted-color.github.io/research/2026/06/27/tool-use-dpo-fixed-budget-reporting-profile/}
}
```
