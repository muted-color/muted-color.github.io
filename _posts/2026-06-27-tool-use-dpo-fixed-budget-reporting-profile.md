---
title: "Fixed-Budget Tool-Use DPO: Call Correctness and Follow-Up Decisions"
date: 2026-06-27 11:04:00 +0900
last_modified_at: 2026-09-06 11:42:21 +0900
lang: en
categories: ["LLM EVAL"]
tags: [llm, tool-use, dpo, function-calling, bfcl, when2call, ifeval, qwen3]
lab_host: "dgx3"
lab_path: "projects/tool-use-dpo-negative-sources"
featured: true
home_rank: 2
excerpt: "Two tool-use DPO recipes showed repeatable score differences. A closer look locates the decision recipe's advantage in follow-up cases, alongside errors on other decisions."
description: "A Qwen3-8B comparison with matched pair and update budgets examines repeated recipe differences, follow-up decision errors, and the distinction between behavior labels and call correctness."
permalink: /research/2026/06/27/tool-use-dpo-fixed-budget-reporting-profile/
translation_url: /research/2026/06/27/tool-use-dpo-fixed-budget-reporting-profile/ko/
image: /assets/images/posts/tool-use-dpo-fixed-budget-reporting-profile/hero-checkpoint-prism.png
image_alt: "Two equal translucent recipe streams pass through a clear checkpoint prism and emerge as three differently shaped evaluation signals"
hero_image: /assets/images/posts/tool-use-dpo-fixed-budget-reporting-profile/hero-checkpoint-prism.png
hero_alt: "Two equal translucent recipe streams pass through a clear checkpoint prism and emerge as three differently shaped evaluation signals"
hero_frame: true
hero_compact: true
---

Tool-use training can emphasize **forming the correct function call** or **choosing whether to call, ask a follow-up question, or decline to answer**. This note compares two DPO recipes from the same `Qwen3-8B` supervised checkpoint under matched pair and optimizer-step budgets, then examines which decisions account for their score differences <a class="citation-ref" href="#ref-qwen3" aria-label="Reference 1">[1]</a>.

The structure-focused recipe scored higher on BFCL call correctness; the decision-focused recipe scored higher on When2Call macro F1. Those aggregate differences repeated across training seeds and one reconstructed pair pool. In the original 50-step runs, however, the decision recipe correctly identified more follow-up cases while correctly identifying fewer tool-call and unable-to-answer cases. The aggregate score combines different patterns across these behaviors.

> **Tool-use DPO** applies Rafailov et al.'s **Direct Preference Optimization** to preferred and dispreferred tool-use responses <a class="citation-ref" href="#ref-dpo" aria-label="Reference 2">[2]</a>. A **recipe** specifies the data source and response-pair construction. The shared **SFT baseline** is the supervised checkpoint before DPO and also serves as its frozen reference model.

## Summary

- Each recipe used a `3000`-pair pool and `375` optimizer steps. The main comparison is at 50 steps, selected after inspecting checkpoint results.
- At that checkpoint, the quality-gated structure recipe led BFCL core by `3.33` percentage points (pp); the decision recipe led When2Call macro F1 by `5.31` pp. Both directions held across three training seeds and one reconstructed pair pool.
- In the original runs, structure and decision correctly labeled `32/100` and `57/100` follow-up cases, respectively. Tool-call counts were `94` and `88`; unable-to-answer counts were `66` and `64`. Decision therefore identified fewer cases correctly in those two classes.
- Prompts and chosen responses differ between recipes, and the decision source belongs to the When2Call family. The evidence establishes a recipe-level comparison; it does not isolate the rejected-error type.
- Filtering, mixing, and checkpoint results provide exploratory context. Unmatched SFT generation limits prevent interpreting the recorded baseline differences as training effects.

## Experimental Setup

The shared SFT checkpoint was trained on `70%` xLAM/APIGen, `20%` ToolACE, and `10%` When2Call. The two main DPO recipes and their unfiltered controls use the same settings <a class="citation-ref" href="#ref-artifact-release" aria-label="Reference 3">[3]</a>:

- **Training budget:** `3000` preference pairs and `375` optimizer steps per run.
- **Optimization:** beta `0.1`, learning rate `5e-6`, LoRA rank `16`, and effective batch size `8`.
- **Checkpoints:** the selected 50-step checkpoint and the final checkpoint after the full budget.

Pair count and optimizer steps are matched; source distributions, prompts, and loss-bearing token counts are not. The budget is a control on the comparison, not a measurement of equal compute cost.

### Recipe Construction

Table 1 summarizes the [pinned pair-construction rules](https://github.com/muted-color/tool-use-dpo-fixed-budget-report/blob/arxiv-v1/docs/negative_construction.md). Chosen responses come from each source's reference output; prompts and chosen responses were not matched across recipes.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr><th>Recipe</th><th>Pair source and rejected-output construction</th></tr>
      </thead>
      <tbody>
        <tr>
          <td>Function-call structure</td>
          <td>Gold tool-call responses are altered to introduce a wrong function, required argument or value, call count, or material type/schema error.<br><span class="table-note-inline">The public artifacts call this source <code>noised_gold</code>.</span></td>
        </tr>
        <tr>
          <td>Call decision</td>
          <td>When2Call-family decision examples pair the reference response with an incorrect call/no-call decision, unnecessary follow-up, abstention, or answer-completion error.<br><span class="table-note-inline">The public artifacts call this source <code>behavior</code>.</span></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> Preference-pair construction for the structure-focused and decision-focused recipes. Prompts and chosen responses differ between sources.</figcaption>
</figure>

**Quality-gated** conditions remove ambiguous or equivalent pairs, acceptable alternatives, and suspect reference responses. Each source passes an LLM-assisted holdout audit of at least `100` selected rows; this is quality control, not human annotation. **Ungated controls** are sampled before that semantic filter, with trainability-only exclusions.

### Evaluation Slices and Metrics

Table 2 defines the evaluation slices. BFCL assesses call correctness <a class="citation-ref" href="#ref-bfcl" aria-label="Reference 4">[4]</a>, while When2Call covers call-decision tasks <a class="citation-ref" href="#ref-when2call" aria-label="Reference 5">[5]</a>. The **IFEval-style prompt-strict diagnostic** is derived from IFEval <a class="citation-ref" href="#ref-ifeval" aria-label="Reference 6">[6]</a>: a prompt passes when all instructions supported by the local evaluator pass. Unsupported instructions are omitted, and prompts with none supported are excluded.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr><th>Evaluation slice</th><th class="align-right">Evaluated prompts</th><th>Selection and scoring</th></tr>
      </thead>
      <tbody>
        <tr>
          <td>BFCL core</td>
          <td class="align-right"><code>300</code></td>
          <td>First 60 rows from each of five BFCL v3 categories: simple, multiple, parallel, irrelevance, and live multiple.<br><span class="table-note-inline">Exact-match function-call correctness under the fixed local parser and evaluator.</span></td>
        </tr>
        <tr>
          <td>When2Call</td>
          <td class="align-right"><code>300</code></td>
          <td>From the test configuration's MCQ split: 100 tool-call, 100 follow-up, and 100 unable-to-answer examples.<br><span class="table-note-inline">Macro F1 uses behavior labels assigned by tool-call parsing and deterministic text heuristics. Response exact match additionally checks call correctness on tool-call rows.</span></td>
        </tr>
        <tr>
          <td>IFEval-style<br><span class="table-note-inline">Prompt-strict diagnostic</span></td>
          <td class="align-right"><code>96</code></td>
          <td>First 100 source prompts, with 4 excluded because the evaluator supports none of their instructions.<br><span class="table-note-inline">Accuracy requires all supported instructions in a prompt to pass.</span></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> Fixed evaluation slices and local scoring definitions. These are local evaluations on fixed slices, rather than official full-benchmark scores.</figcaption>
</figure>

The public metric named `When2Call_behavior_accuracy` averages the released `exact_match` flags. A correct call decision can still fail this metric because of a wrong function, argument, or call count. This note labels it **W2C response exact match**. **Behavior-label accuracy** instead compares `expected_behavior` with `observed_behavior`; macro F1 also uses these labels. The [released computation](https://github.com/muted-color/tool-use-dpo-fixed-budget-report/blob/arxiv-v1/src/tool_use_dpo_negative_sources/bootstrap.py) keeps these two scoring paths distinct.

The frozen macro-F1 evaluator includes direct answer as a zero-support class with `zero_division=0`. The [coverage audit](https://github.com/muted-color/tool-use-dpo-fixed-budget-report/blob/arxiv-v1/docs/direct_answer_coverage.md) found no direct-answer gold rows among `3,952` labeled test rows; another `24,000` inspected training rows had no exposed behavior gold labels. That `27,952`-row audit does not enlarge the `300`-prompt model evaluation or establish training-label coverage.

DPO evaluations share deterministic decoding (`do_sample=false`) with thinking disabled (`enable_thinking=false`). The reported 95% confidence intervals (CIs) use paired, prompt-ID-grouped percentile bootstrap with `1000` resamples. They describe evaluation-sample uncertainty conditional on the runs, excluding training and checkpoint-selection uncertainty. The separate SFT comparison requires the generation-limit qualification in Appendix A.

## Results

### Recipe Differences and Repeated Checks

Table 3 gives the selected 50-step differences as structure minus decision. Positive BFCL values favor structure; negative When2Call (`W2C`) values favor decision. For the quality-gated conditions, BFCL was `0.713` versus `0.680`, and W2C macro F1 was `0.477` versus `0.530`.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Condition</th>
          <th>Metric</th>
          <th class="align-right">Score difference (pp)</th>
          <th class="align-right">95% CI low</th>
          <th class="align-right">95% CI high</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td rowspan="3">Quality-gated</td>
          <td>BFCL core</td>
          <td class="align-right"><code>+3.33</code></td>
          <td class="align-right"><code>+1.53</code></td>
          <td class="align-right"><code>+5.67</code></td>
        </tr>
        <tr>
          <td>W2C response exact match</td>
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
  <figcaption><strong>Table 3.</strong> Evaluation-axis deltas at the selected 50-step checkpoint, computed as the structure-focused recipe minus the decision-focused recipe using grouped bootstrap.</figcaption>
</figure>

The same aggregate directions held across three training seeds and one reconstructed pair pool (Table 4). This supports a repeatable difference under the tested settings. The reconstructed pool still shares prompts with the original, and these checks do not isolate source effects from prompt composition.

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
          <td>Same direction across three seeds.<br><span class="table-note-inline">Gap ranges (pp): BFCL <code>3.00–4.00</code>; W2C response exact match <code>5.00–6.67</code>; W2C macro F1 <code>4.26–5.31</code>.</span></td>
          <td>Fixed pair pool only.</td>
        </tr>
        <tr>
          <td>Reconstructed pair pool</td>
          <td>No pair-id or content-hash overlap; prompt-id overlap was <code>401/3000</code> and <code>1337/3000</code>.<br><span class="table-note-inline">Reconstructed-pool gaps (pp): BFCL <code>3.33</code>; W2C response exact match <code>6.33</code>; W2C macro F1 <code>5.04</code>.</span></td>
          <td>One reconstruction; prompts are not independent.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> Aggregate recipe differences at 50 steps. Gaps are shown without signs: BFCL favors structure; both W2C metrics favor decision. The behavior breakdown in Figure 1 is a separate analysis of the original runs.</figcaption>
</figure>

### Correct and Incorrect Follow-Up Decisions

Figure 1 recounts behavior-label matches in the original quality-gated 50-step [structure](https://github.com/muted-color/tool-use-dpo-fixed-budget-report/blob/arxiv-v1/results/per_example/primary/r028_step50.csv) and [decision](https://github.com/muted-color/tool-use-dpo-fixed-budget-report/blob/arxiv-v1/results/per_example/primary/r029_step50.csv) runs. The `300` prompt IDs and hashes match between files. Each gold class contains `100` prompts, so the counts also give class recall in percent. This is a post-hoc breakdown of those two runs; the repeated aggregate checks do not establish that every class-level pattern repeats.

<figure class="media-figure">
  <img src="/assets/images/posts/tool-use-dpo-fixed-budget-reporting-profile/when2call-behavior-breakdown.svg" alt="Correct behavior labels out of 100 prompts per gold class: structure versus decision is 94 versus 88 for tool calls, 32 versus 57 for follow-up questions, and 66 versus 64 for unable-to-answer cases">
  <figcaption><strong>Figure 1.</strong> Correct behavior labels out of 100 prompts per behavior class. The original quality-gated 50-step runs are shown in structure-focused, then decision-focused order. The shared scale is 0–100. Counts exclude function and argument correctness. There is one run per recipe; uncertainty intervals are not shown.</figcaption>
</figure>

The largest difference between recipes is in follow-up cases. The decision recipe correctly labels `25` additional prompts: the structure recipe labeled `22` of these as tool calls and `3` as unable to answer. Erroneous tool-call labels on this class number `61` for structure and `36` for decision. Conversely, erroneous follow-up labels on tool-call or unable-to-answer cases number `3` and `20`, respectively. The pattern is consistent with a greater tendency to ask for clarification, including both necessary and unnecessary questions.

The metric definitions matter here. Behavior-label accuracy is `192/300` (`64.00%`) for structure and `209/300` (`69.67%`) for decision. Response exact match is lower at `170/300` (`56.67%`) and `190/300` (`63.33%`): respectively `22` and `19` correct call decisions still contain a call-content error. Decision’s `5.31` pp higher macro F1 partly reflects higher tool-call precision from fewer false tool calls. Tool-call recall is lower: `94%` for structure versus `88%` for decision.

The BFCL gap is also localized. Structure's `10` additional correct responses come from live multiple (`+5`), multiple (`+2`), and irrelevance (`+3`); simple and parallel have equal correct counts. Both recipes score poorly on irrelevance (`6/60` and `3/60`). The When2Call advantage therefore does not imply uniformly better behavior wherever a call should be withheld.

### Exploratory Checkpoint, Filtering, and Mixing Results

Table 5 shows scores by checkpoint and for the mixed-source recipe. These comparisons have fewer repeat runs than the main recipe comparison.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Condition</th>
          <th>Checkpoint</th>
          <th class="align-right">BFCL core</th>
          <th class="align-right">W2C macro F1</th>
          <th class="align-right">IFEval-style<br><span class="table-note-inline">Prompt-strict</span></th>
        </tr>
      </thead>
      <tbody>
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
  <figcaption><strong>Table 5.</strong> Absolute scores for quality-gated DPO conditions. Higher is better for all metrics; IFEval-style uses the scoring definition in Table 2.</figcaption>
</figure>

- **Checkpoint:** from 50 steps to final, structure's BFCL score changed by `-2.00` pp and IFEval-style by `-5.21` pp (95% CI `[-10.42, 0.00]`). Decision's W2C macro F1 changed by `-0.19` pp and IFEval-style by `-2.08` pp (`[-6.25, +2.08]`). These point estimates favor the earlier checkpoint on each intended metric and on IFEval-style, but both IFEval intervals include zero and 50 steps was selected after seeing results.
- **Filtering:** at 50 steps, quality-gated minus ungated was `+0.33` pp BFCL for structure (`[0.00, +1.08]`) and `+0.55` pp W2C macro F1 for decision (`[-0.83, +1.81]`). Pair-validity checks did not yield a clear downstream performance benefit here.
- **Mixing:** the `50:50` run uses `1500` pairs per source. Its BFCL and W2C scores lie between the specialists, while IFEval-style (`0.521`) is below both. Half as many pairs per source and the absence of a mixed-run replicate leave harmful interference unestablished.

## Interpretation and Scope

Structure leads on BFCL, while decision leads on When2Call macro F1, with the same aggregate directions across the repeated checks. Source-related specialization is a plausible explanation. Ross et al.'s When2Call already pairs decision-focused data with preference optimization <a class="citation-ref" href="#ref-when2call" aria-label="Reference 5">[5]</a>; this comparison measures the gaps under a fixed budget and identifies the errors that differ between recipes.

In the original runs, the decision recipe has more correct follow-up labels and more incorrect follow-up labels elsewhere; BFCL irrelevance remains weak for both recipes. A choice for a setting where unnecessary calls are costly should therefore examine these error counts alongside the cost of asking an unnecessary question. Macro F1 alone does not supply those costs.

- **Attribution:** training prompts and chosen responses differ, so the experiment cannot identify the rejected-error type as the cause. Matched prompts and chosen responses, followed by evaluation outside the source family, would address that question.
- **Measurement and repetition:** behavior labels come from deterministic parsing and text heuristics. The released rows omit generated text, so the breakdown cannot establish whether an answer was semantically appropriate. It covers the original runs; the three-seed and reconstructed-pool checks cover aggregate gaps.
- **Scope:** one Qwen3-8B SFT starting point and one QLoRA DPO configuration were tested <a class="citation-ref" href="#ref-lora" aria-label="Reference 7">[7]</a> <a class="citation-ref" href="#ref-qlora" aria-label="Reference 8">[8]</a>. The local slices, missing direct-answer gold class, and post-hoc checkpoint choice limit generalization. The SFT comparison below cannot establish a training-induced instruction-following loss.

## Appendix A. Recorded SFT Comparison

The [released IFEval rows](https://github.com/muted-color/tool-use-dpo-fixed-budget-report/tree/arxiv-v1/results/per_example/ifeval) include SFT generation widths up to `768`, while the [DPO manifest](https://github.com/muted-color/tool-use-dpo-fixed-budget-report/blob/arxiv-v1/manifests/benchmark_manifest.yaml) specifies an IFEval output limit of `384`. Widths include batch padding and cannot identify individual truncated answers, but they rule out all SFT rows having been generated under that same limit. Exact SFT generation arguments could not be recovered.

Appendix Table 1 preserves the recorded differences. The SFT scores were `0.667` BFCL, `0.481` W2C macro F1, and `0.635` IFEval-style; deltas use unrounded aggregates. Matched generation limits are needed before attributing these changes to training.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Quality-gated recipe<br><span class="table-note-inline">50-step checkpoint</span></th>
          <th class="align-right">BFCL core<br><span class="table-note-inline">Delta (pp)</span></th>
          <th class="align-right">W2C macro F1<br><span class="table-note-inline">Delta (pp)</span></th>
          <th class="align-right">IFEval-style<br><span class="table-note-inline">Prompt-strict delta (pp)</span></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Function-call structure</td>
          <td class="align-right"><code>+4.67</code></td>
          <td class="align-right"><code>-0.45</code></td>
          <td class="align-right"><code>-6.25</code><br><span class="table-note-inline">[-11.46, -1.04]</span></td>
        </tr>
        <tr>
          <td>Call decision</td>
          <td class="align-right"><code>+1.33</code></td>
          <td class="align-right"><code>+4.86</code></td>
          <td class="align-right"><code>-5.21</code><br><span class="table-note-inline">[-11.46, 0.00]</span></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 1.</strong> Recorded 50-step DPO minus SFT point estimates (pp); brackets show the published 95% IFEval prompt-strict bootstrap intervals. Positive values are higher scores. The unmatched generation limits prevent attributing these differences to training alone.</figcaption>
</figure>

On the `96` supported IFEval prompts, SFT passed `61`, structure `55`, and decision `56`. Each DPO recipe passed one prompt that SFT failed. Structure failed seven prompts that SFT passed; decision failed six. Prompt IDs, hashes, and supported-instruction counts matched. These are recorded score transitions under unmatched generation conditions; the bootstrap intervals do not remove that confounding.

## Public Artifacts

{% include model-mention-cards.html label="GitHub repository" aria_label="Tool-use DPO fixed-budget report GitHub repository" models="Artifact release|muted-color/tool-use-dpo-fixed-budget-report|https://github.com/muted-color/tool-use-dpo-fixed-budget-report" %}

{% include model-mention-cards.html label="Paper" aria_label="Tool-use DPO fixed-budget report paper PDF" models="Paper PDF|paper.pdf|https://github.com/muted-color/tool-use-dpo-fixed-budget-report/blob/main/paper.pdf" %}

The pinned report snapshot provides aggregate tables, prompt-level metric rows, evaluation manifests, and bootstrap outputs <a class="citation-ref" href="#ref-artifact-release" aria-label="Reference 3">[3]</a>. Figure 1 and the behavior-label counts are additional analyses of those released rows. The release supports score-level verification; it excludes original prompts and generated answers.

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
Ilho Ahn, "Fixed-Budget Tool-Use DPO: Call Correctness and Follow-Up Decisions", Mini Research, June 27, 2026.
```

BibTeX:

```bibtex
@article{ahn2026toolusedporeportingprofile,
  author = {Ilho Ahn},
  title = {Fixed-Budget Tool-Use DPO: Call Correctness and Follow-Up Decisions},
  journal = {Mini Research},
  year = {2026},
  month = jun,
  url = {https://muted-color.github.io/research/2026/06/27/tool-use-dpo-fixed-budget-reporting-profile/}
}
```
