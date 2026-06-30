---
title: "Reporting Fixed-Budget Tool-Use DPO as Recipe-Checkpoint Profiles"
date: 2026-06-27 11:04:00 +0900
last_modified_at: 2026-06-30 20:48:01 +0900
categories: ["LLM EVAL"]
tags: [llm, tool-use, dpo, function-calling, bfcl, when2call, ifeval, qwen3]
lab_path: "experiment-lab/projects/tool-use-dpo-negative-sources"
excerpt: "A fixed-budget tool-use DPO comparison is better reported as a recipe-checkpoint profile than as a single recipe winner."
description: "A mini research note on fixed-budget Qwen3-8B tool-use DPO, where structural and behavior negatives move different evaluation axes and checkpoint selection changes the IFEval guardrail trade-off."
permalink: /research/2026/06/27/tool-use-dpo-fixed-budget-reporting-profile/
image: /assets/images/posts/tool-use-dpo-fixed-budget-reporting-profile/social-thumbnail.png
image_alt: "Translucent checkpoint beads connected by branching gray paths and one subtle light-blue selected path on a near-white background"
hero_image: /assets/images/posts/tool-use-dpo-fixed-budget-reporting-profile/social-thumbnail.png
hero_alt: "A near-white glass-style scene with translucent checkpoint beads, branching recipe-checkpoint paths, and one subtle light-blue selected path"
hero_frame: true
hero_compact: true
---

Tool-use DPO results are often compressed into a single improvement over an SFT baseline. That summary was too thin in this experiment. Function-call structure, call-decision behavior, and instruction-following guardrails moved in different directions.

This note compares DPO negative recipes under the same pair budget and optimizer-step budget, using a `Qwen3-8B` tool-use SFT checkpoint as the shared reference <a class="citation-ref" href="#ref-qwen3" aria-label="Reference 18">[18]</a>. The main result is not a recipe ranking. **Tool-use DPO should be reported as a recipe-checkpoint profile.** A profile records the negative recipe, fixed budget, reported checkpoint, intended metric, guardrail regression, seed scope, pair-sampling scope, benchmark coverage, data-quality gate, and overlap checks together.

> **Tool-use DPO** is a preference-optimization setup where chosen/rejected pairs are built from tool-call outputs or tool-use decisions, and DPO is used to update the policy <a class="citation-ref" href="#ref-dpo" aria-label="Reference 13">[13]</a>. This note does not propose a new objective. It asks which evaluation axes move under fixed-budget negative recipes and checkpoints.

{% include model-mention-cards.html label="Key evaluation resources" aria_label="Key evaluation resources for the tool-use DPO reporting profile note" models="Qwen3-8B|Qwen/Qwen3-8B|https://huggingface.co/Qwen/Qwen3-8B;When2Call|nvidia/When2Call|https://huggingface.co/datasets/nvidia/When2Call" %}

## Summary

- The main reporting unit is a recipe-checkpoint profile, not a single recipe winner.
- The comparison used a fixed budget of `3000` pairs, `375` optimizer steps, DPO beta `0.1`, LR `5e-6`, LoRA rank `16`, and effective batch size `8`.
- At the preferred `step50` checkpoint, clean structural DPO was `+3.33` points above clean behavior DPO on BFCL core, but `-6.67` points lower on When2Call behavior accuracy and `-5.31` points lower on When2Call macro F1.
- Clean-vs-unfiltered effects within the same source family were small or uncertain. In this setting, semantic filtering behaved more like a pair-quality gate than a downstream performance axis.
- The final checkpoint was not automatically the best reporting point: in the reported clean conditions, it worsened the IFEval guardrail trade-off relative to step50.
- Additional seeds and an independent pool-B replicate preserved the source-axis sign pattern, but the robustness claim remains narrow.

## Repository and Paper

{% include model-mention-cards.html label="GitHub repository" aria_label="Tool-use DPO fixed-budget report GitHub repository" models="Artifact release|muted-color/tool-use-dpo-fixed-budget-report|https://github.com/muted-color/tool-use-dpo-fixed-budget-report" %}

{% include model-mention-cards.html label="Paper" aria_label="Tool-use DPO fixed-budget report paper PDF" models="Paper PDF|paper.pdf|https://github.com/muted-color/tool-use-dpo-fixed-budget-report/blob/main/paper.pdf" %}

This section is only for the GitHub repository and paper PDF. The result tables in this note and Figure 1 can be checked against the public artifact repository, using sanitized evaluation outputs and aggregate tables. The repository is an artifact-level verification release for the reported tables, confidence intervals, and Pareto figure. It is not an end-to-end retraining bundle.

For the full paper-style report and appendix, see the separate [paper PDF](https://github.com/muted-color/tool-use-dpo-fixed-budget-report/blob/main/paper.pdf). The result snapshot is pinned by the `arxiv-v1` tag, which currently points to commit `3f4799e`. For a quick check, start with `reproduced/tables/` and `reproduced/figures/` in the repository.

## Evaluation Design

Table 1 fixes the unit of interpretation for this note. A fixed budget means the same number of preference pairs and optimizer steps. It does not mean identical source distributions or identical loss-bearing token counts.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>Profile field</th>
          <th>Value in this note</th>
          <th>Interpretive role</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>Negative recipe</code></td>
          <td>clean structural, clean behavior,<br><span class="table-note-inline">same-budget unfiltered controls</span></td>
          <td>Separates source-axis movement instead of ranking one recipe as the winner.</td>
        </tr>
        <tr>
          <td><code>Fixed budget</code></td>
          <td><code>3000</code> pairs, <code>375</code> steps,<br><span class="table-note-inline">beta <code>0.1</code>, LR <code>5e-6</code>, LoRA rank <code>16</code></span></td>
          <td>Fixes pair, step, and DPO recipe settings without making an equal-token causal claim.</td>
        </tr>
        <tr>
          <td><code>Reference</code></td>
          <td>Shared Qwen3-8B tool-use SFT checkpoint</td>
          <td>Removes variation from changing the DPO reference across recipes.</td>
        </tr>
        <tr>
          <td><code>Intended metric</code></td>
          <td>BFCL core, When2Call behavior accuracy,<br><span class="table-note-inline">When2Call macro F1</span></td>
          <td>Separates function-call structure from call-decision behavior.</td>
        </tr>
        <tr>
          <td><code>Guardrail metric</code></td>
          <td>IFEval prompt-level strict accuracy</td>
          <td>Reports intended gain together with instruction-following regression.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> Core fields of the reporting profile used in this note. The paper and repository manifest also include seed scope, pair-sampling scope, data-quality gates, benchmark coverage, and overlap checks in the same profile.</figcaption>
</figure>

The evaluation is read across three axes. **BFCL core** is mainly a structural function-calling axis, focused on function selection and argument correctness <a class="citation-ref" href="#ref-bfcl" aria-label="Reference 11">[11]</a>. **When2Call** evaluates call-decision behavior such as tool call, follow-up question, and unable-to-answer decisions <a class="citation-ref" href="#ref-when2call" aria-label="Reference 15">[15]</a>. **IFEval prompt-strict** is not the primary intended metric; it is a guardrail metric for measuring how much DPO perturbs instruction following <a class="citation-ref" href="#ref-ifeval" aria-label="Reference 20">[20]</a>.

## Results

The results are easiest to read in four groups. First, the source-axis split between BFCL and When2Call. Second, whether clean filtering itself explains downstream performance. Third, how checkpoint selection changes the guardrail trade-off. Fourth, how far the seed and pair-pool robustness checks can support the claim.

### Source-Axis Comparison

Table 2 compares the structural and behavior recipes at the preferred `step50` checkpoint. Values are percentage-point deltas computed as `structural - behavior`. A positive BFCL row means the structural recipe scored higher; a negative When2Call row means the behavior recipe scored higher.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Comparison</th>
          <th>Metric</th>
          <th class="align-right">Delta</th>
          <th class="align-right">CI95 low</th>
          <th class="align-right">CI95 high</th>
          <th>How to read it</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>clean structural<br><span class="table-note-inline">minus clean behavior</span></td>
          <td>BFCL core</td>
          <td class="align-right"><code>+3.33</code></td>
          <td class="align-right"><code>+1.53</code></td>
          <td class="align-right"><code>+5.67</code></td>
          <td>Structural recipe moved BFCL more.</td>
        </tr>
        <tr>
          <td>clean structural<br><span class="table-note-inline">minus clean behavior</span></td>
          <td>W2C behavior acc.</td>
          <td class="align-right"><code>-6.67</code></td>
          <td class="align-right"><code>-10.75</code></td>
          <td class="align-right"><code>-3.02</code></td>
          <td>Behavior recipe moved call-decision accuracy more.</td>
        </tr>
        <tr>
          <td>clean structural<br><span class="table-note-inline">minus clean behavior</span></td>
          <td>W2C macro F1</td>
          <td class="align-right"><code>-5.31</code></td>
          <td class="align-right"><code>-8.85</code></td>
          <td class="align-right"><code>-2.34</code></td>
          <td>Behavior recipe moved macro F1 more.</td>
        </tr>
        <tr>
          <td>unfiltered structural<br><span class="table-note-inline">minus unfiltered behavior</span></td>
          <td>BFCL core</td>
          <td class="align-right"><code>+2.67</code></td>
          <td class="align-right"><code>+1.02</code></td>
          <td class="align-right"><code>+4.86</code></td>
          <td>The same direction appears in the unfiltered control.</td>
        </tr>
        <tr>
          <td>unfiltered structural<br><span class="table-note-inline">minus unfiltered behavior</span></td>
          <td>W2C macro F1</td>
          <td class="align-right"><code>-4.21</code></td>
          <td class="align-right"><code>-7.48</code></td>
          <td class="align-right"><code>-1.23</code></td>
          <td>The When2Call signal remains stronger for behavior negatives.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> Source-axis deltas at the preferred <code>step50</code> checkpoint, computed with grouped bootstrap. This is a source-native fixed-budget recipe comparison, not a prompt-matched causal ranking of source quality.</figcaption>
</figure>

The stable observation is simple. Structural negatives moved BFCL more, while behavior negatives moved When2Call more. This does not mean that the structural source is better, or that the behavior source is better. It means the two recipes fill different evaluation axes.

There is an important caveat. The behavior condition is tied to a When2Call-style data and evaluation family, and BFCL core also contains relevance/irrelevance-style buckets. Table 2 should therefore be read as a **fixed-budget recipe profile under the represented decision regime**, not as a source-superiority result.

### Role of Clean Filtering

Semantic filtering was used as a pair-quality gate: whether the rejected output was actually worse than the chosen output, schema-valid, and not an equivalent alternative. But when clean and unfiltered variants are compared within the same source family, Table 3 shows small or uncertain downstream differences.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Comparison</th>
          <th>Metric</th>
          <th class="align-right">Delta</th>
          <th class="align-right">CI95 low</th>
          <th class="align-right">CI95 high</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>clean structural<br><span class="table-note-inline">minus unfiltered structural</span></td>
          <td>BFCL core</td>
          <td class="align-right"><code>+0.33</code></td>
          <td class="align-right"><code>0.00</code></td>
          <td class="align-right"><code>+1.08</code></td>
        </tr>
        <tr>
          <td>clean behavior<br><span class="table-note-inline">minus unfiltered behavior</span></td>
          <td>W2C macro F1</td>
          <td class="align-right"><code>+0.55</code></td>
          <td class="align-right"><code>-0.83</code></td>
          <td class="align-right"><code>+1.81</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> Same-budget clean-vs-unfiltered comparison. The clean gate reduced pair-level risk, but it did not appear to be a general downstream performance axis in this setting.</figcaption>
</figure>

This is not a reason to drop filtering. Tool-use negatives easily mix optional/default/no-op differences, harmless normalization, acceptable alternate tools, and chosen/reference-suspect cases. The narrower point is that filtering should not be summarized as a performance improvement unless there is separate evidence for that claim. Here, quality control and downstream movement are reported separately.

### Checkpoint and Guardrail Trade-Off

Figure 1 plots intended-axis gain against IFEval prompt-strict regression, while Table 4 gives the corresponding absolute scores. Even within the same recipe, moving from `step50` to the final checkpoint changes both the intended metric and the guardrail metric.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/tool-use-dpo-fixed-budget-reporting-profile/pareto-2panel.svg" alt="Two-panel Pareto figure comparing BFCL core and When2Call macro F1 gains against IFEval prompt-strict regression">
  <figcaption><strong>Figure 1.</strong> Pareto view of intended-axis gain and IFEval prompt-strict regression under a fixed-budget tool-use DPO setting. The left panel uses BFCL core as the intended metric; the right panel uses When2Call macro F1. Arrows show the movement from the step50 checkpoint to the final checkpoint within the same condition.</figcaption>
</figure>

For the clean structural condition, `step50` had BFCL core `+4.67` points and IFEval prompt-strict `-6.25` points. The final checkpoint changed to BFCL core `+2.67` points and IFEval prompt-strict `-11.46` points. In this condition, the final checkpoint reduced intended gain and increased guardrail regression.

For the clean behavior condition, `step50` had When2Call macro F1 `+4.86` points and IFEval prompt-strict `-5.21` points. The final checkpoint had When2Call macro F1 `+4.68` points and IFEval prompt-strict `-7.29` points. The intended metric was nearly preserved, but the guardrail metric deteriorated.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Condition</th>
          <th>Checkpoint</th>
          <th class="align-right">BFCL core</th>
          <th class="align-right">W2C macro F1</th>
          <th class="align-right">IFEval prompt strict</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>SFT baseline</td>
          <td>SFT best</td>
          <td class="align-right"><code>0.667</code></td>
          <td class="align-right"><code>0.481</code></td>
          <td class="align-right"><code>0.635</code></td>
        </tr>
        <tr>
          <td>clean structural</td>
          <td>step50</td>
          <td class="align-right"><code>0.713</code></td>
          <td class="align-right"><code>0.477</code></td>
          <td class="align-right"><code>0.573</code></td>
        </tr>
        <tr>
          <td>clean structural</td>
          <td>final</td>
          <td class="align-right"><code>0.693</code></td>
          <td class="align-right"><code>0.479</code></td>
          <td class="align-right"><code>0.521</code></td>
        </tr>
        <tr>
          <td>clean behavior</td>
          <td>step50</td>
          <td class="align-right"><code>0.680</code></td>
          <td class="align-right"><code>0.530</code></td>
          <td class="align-right"><code>0.583</code></td>
        </tr>
        <tr>
          <td>clean behavior</td>
          <td>final</td>
          <td class="align-right"><code>0.660</code></td>
          <td class="align-right"><code>0.528</code></td>
          <td class="align-right"><code>0.562</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> Absolute scores for the baseline and clean conditions. Deltas alone can hide the starting point and the size of guardrail regression, so the reporting profile should include absolute scores as well.</figcaption>
</figure>

This does not imply that early checkpoints are always better. It does show that automatically reporting the final checkpoint can hide the trade-off between intended-axis gain and guardrail regression. In this setting, checkpoint selection is part of the empirical claim.

### Robustness and Coverage Scope

Additional checks were used to narrow the claim, not to turn the source-axis result into a general robustness claim. Table 5 separates what was checked from what it can support.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>Check</th>
          <th>Evidence</th>
          <th>Boundary</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Training-seed check</td>
          <td>With the same pair pool, seed2 and seed3 preserved the source-axis pattern. Including the original seed, <code>18/18</code> sign checks matched the expected direction.</td>
          <td>Supports fixed-pool training-seed stability, not broad data-distribution robustness.</td>
        </tr>
        <tr>
          <td>Independent pool-B replicate</td>
          <td>Clean structural selected <code>3000</code> rows from <code>9988</code> candidates; clean behavior selected <code>3000</code> rows from <code>4294</code> candidates. Pair-id and content-hash overlap with pool-A were both <code>0</code>. Across pool-A and pool-B step50/best checkpoints, <code>12/12</code> sign checks matched the expected direction.</td>
          <td>Supports sign stability under one independent pair-pool reconstruction, not a causal ranking of source quality.</td>
        </tr>
        <tr>
          <td>When2Call coverage audit</td>
          <td>The audited public labeled configs contained <code>27,952</code> rows and <code>0</code> direct-answer gold rows.</td>
          <td>Limits the When2Call behavior claim to the represented tool-call, follow-up-question, and unable-to-answer slices.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 5.</strong> Robustness and coverage checks used to bound the claim. The checks support sign stability in the evaluated setup, but they do not establish broad distribution robustness or source-level superiority.</figcaption>
</figure>

## Interpretation

The shortest interpretation is that tool-use DPO was not a one-axis improvement problem. Structural negatives moved function-call correctness more. Behavior negatives moved the represented call-decision slice more. Clean filtering reduced pair-quality risk, but the evidence for a general same-budget downstream improvement was weak. Checkpoint selection changed both intended gain and guardrail regression.

The conclusion is therefore about reporting, not recipe selection. Public tool-use DPO results should state:

- which negative recipe was used
- the pair count, step count, DPO recipe, and reference checkpoint
- why the reported checkpoint was selected
- how the intended metric and guardrail metric moved
- what seed and pair-sampling robustness was checked
- what limitations remain from the clean gate and benchmark coverage
- which exact overlap keys were checked, and what those checks do not guarantee

Without this profile, a `+x points` improvement is easy to over-interpret. In tool-use evaluation, formatting a tool call correctly and deciding whether a tool should be called are not the same capability.

## Limitations

The DPO training pools are source-native rather than prompt-matched. The behavior condition is confounded with the When2Call-style data and evaluation family. The source-axis result is therefore a fixed-budget recipe comparison, not a causal ranking of source quality.

The fixed-budget condition is also limited. Pair count, optimizer steps, DPO recipe, and reference checkpoint were fixed, but token count and source distribution were not identical. All DPO conditions come from one Qwen3-8B SFT reference, one QLoRA DPO recipe, and one pair/step budget <a class="citation-ref" href="#ref-lora" aria-label="Reference 3">[3]</a> <a class="citation-ref" href="#ref-qlora" aria-label="Reference 2">[2]</a>.

The IFEval slice should be read as a guardrail diagnostic. Bootstrap intervals address evaluation-sample uncertainty, but they do not cover all uncertainty from training stochasticity, data sampling, or benchmark construction.

## References

<div class="reference-list" markdown="1">

<ol>
  <li id="ref-robust-dpo">Chowdhury, Sayak Ray, Kini, Anush, and Natarajan, Nagarajan. <strong>Provably Robust DPO: Aligning Language Models with Noisy Feedback</strong>. ICML, 2024. <a href="https://arxiv.org/abs/2403.00409">arXiv</a></li>
  <li id="ref-qlora">Dettmers, Tim et al. <strong>QLoRA: Efficient Finetuning of Quantized LLMs</strong>. NeurIPS, 2023. <a href="https://arxiv.org/abs/2305.14314">arXiv</a></li>
  <li id="ref-lora">Hu, Edward J. et al. <strong>LoRA: Low-Rank Adaptation of Large Language Models</strong>. ICLR, 2022. <a href="https://arxiv.org/abs/2106.09685">arXiv</a></li>
  <li id="ref-diatool-dpo">Jung, Sunghee et al. <strong>DiaTool-DPO: Multi-Turn Direct Preference Optimization for Tool-Augmented Large Language Models</strong>. SIGDIAL, 2025. <a href="https://aclanthology.org/2025.sigdial-1.32/">ACL Anthology</a></li>
  <li id="ref-functionchat-bench">Lee, Shinbok et al. <strong>FunctionChat-Bench: Comprehensive Evaluation of Language Models' Generative Capabilities in Korean Tool-use Dialogs</strong>. arXiv:2411.14054, 2024. <a href="https://arxiv.org/abs/2411.14054">arXiv</a></li>
  <li id="ref-api-bank">Li, Minghao et al. <strong>API-Bank: A Comprehensive Benchmark for Tool-Augmented LLMs</strong>. EMNLP, 2023. DOI: <a href="https://doi.org/10.18653/v1/2023.emnlp-main.187">10.18653/v1/2023.emnlp-main.187</a></li>
  <li id="ref-helm">Liang, Percy et al. <strong>Holistic Evaluation of Language Models</strong>. <em>Transactions on Machine Learning Research</em>, 2023.</li>
  <li id="ref-toolace">Liu, Weiwen et al. <strong>ToolACE: Winning the Points of LLM Function Calling</strong>. arXiv:2409.00920, 2024. <a href="https://arxiv.org/abs/2409.00920">arXiv</a></li>
  <li id="ref-apigen">Liu, Zuxin et al. <strong>APIGen: Automated Pipeline for Generating Verifiable and Diverse Function-Calling Datasets</strong>. NeurIPS, 2024.</li>
  <li id="ref-what-matters-dpo">Pan, Yu et al. <strong>What Matters in Data for DPO?</strong> arXiv:2508.18312, 2025. <a href="https://arxiv.org/abs/2508.18312">arXiv</a></li>
  <li id="ref-bfcl">Patil, Shishir G. et al. <strong>The Berkeley Function Calling Leaderboard (BFCL): From Tool Use to Agentic Evaluation of Large Language Models</strong>. ICML, 2025. <a href="https://proceedings.mlr.press/v267/patil25a.html">PMLR</a>; <a href="https://gorilla.cs.berkeley.edu/leaderboard.html">Project page</a></li>
  <li id="ref-toollm">Qin, Yujia et al. <strong>ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs</strong>. ICLR, 2024. <a href="https://openreview.net/forum?id=dHng2O0Jjr">OpenReview</a></li>
  <li id="ref-dpo">Rafailov, Rafael et al. <strong>Direct Preference Optimization: Your Language Model is Secretly a Reward Model</strong>. NeurIPS, 2023. <a href="https://arxiv.org/abs/2305.18290">arXiv</a></li>
  <li id="ref-overoptimization">Rafailov, Rafael et al. <strong>Scaling Laws for Reward Model Overoptimization in Direct Alignment Algorithms</strong>. arXiv:2406.02900, 2024. <a href="https://arxiv.org/abs/2406.02900">arXiv</a></li>
  <li id="ref-when2call">Ross, Hayley, Mahabaleshwarkar, Ameya Sunil, and Suhara, Yoshi. <strong>When2Call: When (not) to Call Tools</strong>. NAACL, 2025. DOI: <a href="https://doi.org/10.18653/v1/2025.naacl-long.174">10.18653/v1/2025.naacl-long.174</a>; <a href="https://huggingface.co/datasets/nvidia/When2Call">Dataset card</a></li>
  <li id="ref-toolformer">Schick, Timo et al. <strong>Toolformer: Language Models Can Teach Themselves to Use Tools</strong>. NeurIPS, 2023.</li>
  <li id="ref-yan-function-calling">Yan, Fanjia. <strong>A Function Calling Perspective on Scalable Large Language Model Agent Evaluation</strong>. Master's thesis, UC Berkeley EECS, 2025. <a href="https://www2.eecs.berkeley.edu/Pubs/TechRpts/2025/EECS-2025-184.html">Technical report</a></li>
  <li id="ref-qwen3">Yang, An et al. <strong>Qwen3 Technical Report</strong>. arXiv:2505.09388, 2025. <a href="https://arxiv.org/abs/2505.09388">arXiv</a>; Qwen Team. <strong>Qwen3-8B</strong>. Hugging Face model repository. <a href="https://huggingface.co/Qwen/Qwen3-8B">Model card</a></li>
  <li id="ref-xlam">Zhang, Jianguo et al. <strong>xLAM: A Family of Large Action Models to Empower AI Agent Systems</strong>. NAACL, 2025. <a href="https://arxiv.org/abs/2409.03215">arXiv</a></li>
  <li id="ref-ifeval">Zhou, Jeffrey et al. <strong>Instruction-Following Evaluation for Large Language Models</strong>. arXiv:2311.07911, 2023. <a href="https://arxiv.org/abs/2311.07911">arXiv</a></li>
</ol>

</div>

## Citation

Text citation:

```text
Ilho Ahn, "Reporting Fixed-Budget Tool-Use DPO as Recipe-Checkpoint Profiles", Mini Research, June 27, 2026.
```

BibTeX:

```bibtex
@article{ahn2026toolusedporeportingprofile,
  author = {Ilho Ahn},
  title = {Reporting Fixed-Budget Tool-Use DPO as Recipe-Checkpoint Profiles},
  journal = {Mini Research},
  year = {2026},
  month = jun,
  url = {https://muted-color.github.io/research/2026/06/27/tool-use-dpo-fixed-budget-reporting-profile/}
}
```
