---
title: "Preference Trajectories and Slot Behavior in a DiaTool-DPO Reconstruction"
date: 2026-07-29
last_modified_at: 2026-07-30
categories: ["LLM TOOL USE"]
tags: [llm, tool-use, dpo, preference-learning, function-calling, multi-turn-dialogue, llama3]
lang: en
lab_path: "experiment-lab/projects/diatool-dpo-reproduction"
excerpt: "An analysis of preference trajectories and Slot behavior under a public-information reconstruction of DiaTool-DPO."
description: "Under non-identical evaluation conditions, preference-trajectory diagnostics and a single-run sensitivity comparison examine a smaller local Slot gain despite a numerically similar aggregate gain."
permalink: /research/2026/07/29/diatool-dpo-public-reconstruction-preference-trajectories/
image: /assets/images/posts/diatool-dpo-public-reconstruction-preference-trajectories/social-thumbnail.png
image_alt: "A compact measured plot comparing similar Macro gains with selected Completion and Slot changes in the local reconstruction and paper report"
hero_image: /assets/images/posts/diatool-dpo-public-reconstruction-preference-trajectories/aggregate-behavior-featured.svg
hero_alt: "A compact plot showing similar Macro relative gains and different Completion and Slot changes for the local reconstruction and paper report"
hero_caption: "<strong>Featured summary.</strong> Numerically similar Macro gains did not distinguish the different Completion and Slot changes. This axis-level difference motivates the preference-trajectory diagnostics below; the profiles use different checkpoints, data, and judge backends and are not one common effect estimate."
hero_frame: true
hero_variant: featured-plot
published: true
publication_status: "published"
---

The local DiaTool-DPO model improved over its SFT baseline on all four FunctionChat-Bench axes, but its axis-level profile differed from the paper. This note examines that difference through the structure and distribution of tool-use preference trajectories, with Slot behavior—whether the assistant requests missing required fields before calling a tool—as the main diagnostic. The public-information reconstruction defines the experimental condition and its limits; the paper and local profiles use different checkpoints, preference data, and judge backends and are not one common effect estimate <a class="citation-ref" href="#ref-diatool-dpo" aria-label="Reference 1">[1]</a>.

## Summary

- Public pair counts, state paths, objective components, and DPO settings were matched; the unavailable checkpoint, preference data, and judge backend were not identical.
- Macro relative improvement was numerically similar (`+10.93%` locally; `+10.78%` in the paper), but the two conditions are not one comparable effect estimate.
- Slot improved by `+7.01` points locally, substantially less than the paper's `+27.80`-point change; this is the main boundary on effect reproduction.
- Local trajectory diagnostics and one post-hoc run indicate data-construction sensitivity, but do not establish shortcut learning or a generally superior reconstruction rule.

## DiaTool-DPO Method

DiaTool-DPO treats tool use as a choice of dialogue flow rather than a preference between isolated responses. The paper defines three query types over five conceptual states: Type1 calls immediately when all required arguments are available, Type2 gathers missing fields before calling, and Type3 refuses when no available tool supports the request. The states describe the task structure proposed by the paper, not model states observed directly <a class="citation-ref" href="#ref-diatool-dpo" aria-label="Reference 1">[1]</a>.

Each training example pairs a chosen full trajectory with a rejected one. They share the initial request and tool context, but later turns and lengths may differ. Rejected paths include redundant questions, premature calls, incorrect refusals, and unsupported tool calls. User and tool messages provide context while assistant turns are scored. The Easy and Hard subsets contain `16,794` pairs in total <a class="citation-ref" href="#ref-diatool-dpo" aria-label="Reference 1">[1]</a>. Figure 1 summarizes the resulting training flow.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/diatool-dpo-public-reconstruction-preference-trajectories/diatool-dpo-method.svg" alt="Conceptual flow from three tool-use query types to paired chosen and rejected multi-turn trajectories and a trajectory-level DPO objective with turn weighting, score normalization, and a reward-gap margin">
  <figcaption><strong>Figure 1.</strong> A request and tool set lead to an immediate call, filling <code>N</code> missing required fields before a call, or refusal. DiaTool-DPO pairs the intended path with a counter-trajectory and scores the pair at trajectory level. The geometry is conceptual and does not encode frequency or effect size.</figcaption>
</figure>

The objective aggregates policy-versus-reference scores across assistant turns. It gives earlier actions more influence, normalizes each trajectory by its total turn weight, and requires a margin between chosen and rejected scores. These adjustments accommodate the structural length differences between Slot-filling and rejection paths <a class="citation-ref" href="#ref-diatool-dpo" aria-label="Reference 1">[1]</a>.

## Reconstruction Scope

The reconstruction implemented the published trajectory structure and objective components using the reference implementation as a public resource <a class="citation-ref" href="#ref-diatool-code" aria-label="Reference 2">[2]</a>. It retained ordinary DPO's policy-versus-reference comparison <a class="citation-ref" href="#ref-dpo" aria-label="Reference 3">[3]</a>, but several artifacts needed for an exact reproduction were not public.

Table 1 separates specifications taken from the paper from choices made during the reconstruction. This boundary is central to the result: matching a published trajectory schema does not imply matching the unpublished trajectory distribution.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <colgroup>
        <col style="width: 24%;">
        <col style="width: 34%;">
        <col style="width: 42%;">
      </colgroup>
      <thead>
        <tr>
          <th>Component</th>
          <th>Public specification</th>
          <th>Local reconstruction / boundary</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Preference-pair counts and<br>state-transition paths</td>
          <td>Counts and state-transition paths reported by trajectory type</td>
          <td>Rebuilt to match the reported table<br><span class="table-note-inline">Boundary: Structurally aligned</span></td>
        </tr>
        <tr>
          <td>Objective and DPO settings</td>
          <td>Early-turn weight, turn-weight normalization, margin, and training settings</td>
          <td>Applied from the reported specification<br><span class="table-note-inline">Boundary: Training specification aligned</span></td>
        </tr>
        <tr>
          <td>CPT/SFT starting point</td>
          <td>Training procedure and source described</td>
          <td>Separately trained from public data<br><span class="table-note-inline">Boundary: Not the same checkpoint</span></td>
        </tr>
        <tr>
          <td>Korean preference data</td>
          <td>Generation procedure and total scale described</td>
          <td>Public prompts with local generation models and rules<br><span class="table-note-inline">Boundary: Reconstructed data</span></td>
        </tr>
        <tr>
          <td>Source sampling and<br>partial-reveal distribution</td>
          <td>Not fully determined by the public description</td>
          <td>Local sources and partial-reveal rules<br><span class="table-note-inline">Boundary: Potential sensitivity axis</span></td>
        </tr>
        <tr>
          <td>Branch-level surface concentration</td>
          <td>Not a required measurement in the paper</td>
          <td>Measured as a post-hoc diagnostic<br><span class="table-note-inline">Boundary: Local evidence only</span></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> Scope of structural alignment against the published specification <a class="citation-ref" href="#ref-diatool-dpo" aria-label="Reference 1">[1]</a>. “Aligned” applies to reported preference-pair counts, state-transition paths, and settings, not checkpoint or data identity.</figcaption>
</figure>

## Evaluation Design

The primary comparison used the same local SFT lineage for the SFT baseline and reconstructed DPO model. The SFT adapter reconstructed for this project is publicly available, which makes the local starting point inspectable even though it is not the paper's checkpoint.

{% include model-mention-cards.html label="Reconstructed SFT checkpoint" aria_label="Reconstructed Korean tool-use SFT checkpoint used as the local DPO starting point" models="LLaMA 3 8B DiaTool Korean SFT LoRA|soleaf/Llama-3-8B-DiaTool-Ko-SFT-LoRA|https://huggingface.co/soleaf/Llama-3-8B-DiaTool-Ko-SFT-LoRA" %}

Table 2 summarizes the shared local comparison contract and the boundary of each condition.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>Field</th>
          <th>Reconstruction condition</th>
          <th>Interpretive role</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Starting model</td>
          <td>Llama 3 8B Instruct <a class="citation-ref" href="#ref-llama3" aria-label="Reference 4">[4]</a> + reconstructed tool-use SFT LoRA</td>
          <td>Shared local reference for SFT-versus-DPO comparison</td>
        </tr>
        <tr>
          <td>Preference data</td>
          <td>Easy <code>8,357</code> + Hard <code>8,437</code> = <code>16,794</code> pairs</td>
          <td>Matches the public pair-count specification</td>
        </tr>
        <tr>
          <td>DPO training</td>
          <td>1 epoch, total batch <code>8</code>, LR <code>1e-7</code>, bf16, max length <code>8,192</code></td>
          <td>Uses the reported optimization settings</td>
        </tr>
        <tr>
          <td>Parameter update</td>
          <td>Continued rank-8 LoRA <a class="citation-ref" href="#ref-lora" aria-label="Reference 5">[5]</a></td>
          <td>The paper does not separately specify whether PEFT was used</td>
        </tr>
        <tr>
          <td>Evaluation set</td>
          <td>FunctionChat-Bench, <code>1,306</code> items at the evaluated revision <a class="citation-ref" href="#ref-functionchat-bench" aria-label="Reference 6">[6]</a></td>
          <td>Call 670, Completion 71, Slot 442, Relevance 123</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> Primary reconstruction and evaluation conditions. Reported pair counts and optimization settings follow DiaTool-DPO <a class="citation-ref" href="#ref-diatool-dpo" aria-label="Reference 1">[1]</a>. The comparison is internally controlled against the reconstructed SFT starting point, not against the paper's original checkpoint.</figcaption>
</figure>

Call is normalized tool-call exact match. Completion, Slot, and Relevance use a fixed-rubric judge following the benchmark's four-axis evaluation design <a class="citation-ref" href="#ref-functionchat-bench" aria-label="Reference 6">[6]</a>. Macro is the unweighted mean of these four axes despite their different sample counts and judgment mechanisms, so it is used only as a benchmark summary. Relative Macro gain is computed as

<div class="metric-formulas" aria-label="Relative Macro gain formula">
  <div class="metric-formula">
    <span class="metric-formula__label">Relative Macro gain</span>
    <span class="metric-formula__body">(Macro<sub>DPO</sub> − Macro<sub>SFT</sub>) / Macro<sub>SFT</sub> × 100%</span>
  </div>
</div>

For Relevance, byte-identical responses were assigned the same local judgment. A manual audit found two inconsistent judgments among 42 identical-response cases. This adjustment did not change the main conclusion.

## Aggregate Gain and Behavioral Composition

The reconstructed DPO model scored above its SFT baseline on all four evaluation axes. Figure 2 shows why the Macro result is insufficient: the local and paper relative Macro gains were numerically close, but the behavioral components moved differently. The two profiles come from different checkpoints, preference data, and judge backends, so their values are not one common effect estimate. Table 3 retains the exact values.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/diatool-dpo-public-reconstruction-preference-trajectories/aggregate-behavior-change-focused.svg" alt="Measured comparison with Macro relative gains of 10.93% locally and 10.78% in the paper, followed by zero-centered local versus paper axis changes: Call +4.93 versus +1.40, Completion +7.04 versus -2.80, Slot +7.01 versus +27.80, and Relevance +5.69 versus +8.70 percentage points">
  <figcaption><strong>Figure 2.</strong> The top strip compares relative Macro gain on a common <code>0–12%</code> scale; the zero-centered plot below shows SFT-to-DPO changes for each evaluation axis in percentage points. Similar aggregate ratios were composed differently, including a larger reported Slot change and a reported Completion decrease. The local and paper profiles come from separate checkpoints, preference data, and judge backends and are not one common effect estimate.</figcaption>
</figure>

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Evaluation axis</th>
          <th class="align-right">SFT</th>
          <th class="align-right">Reconstructed DPO</th>
          <th class="align-right">Local change</th>
          <th class="align-right">Paper change</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Call <span class="table-note-inline"><code>n=670</code></span></td>
          <td class="align-right"><code>63.88%</code> (428)</td>
          <td class="align-right"><code>68.81%</code> (461)</td>
          <td class="align-right"><code>+4.93</code> pp</td>
          <td class="align-right"><code>+1.40</code> pp</td>
        </tr>
        <tr>
          <td>Completion <span class="table-note-inline"><code>n=71</code></span></td>
          <td class="align-right"><code>85.92%</code> (61)</td>
          <td class="align-right"><code>92.96%</code> (66)</td>
          <td class="align-right"><code>+7.04</code> pp</td>
          <td class="align-right"><code>-2.80</code> pp</td>
        </tr>
        <tr>
          <td>Slot <span class="table-note-inline"><code>n=442</code></span></td>
          <td class="align-right"><code>54.07%</code> (239)</td>
          <td class="align-right"><code>61.09%</code> (270)</td>
          <td class="align-right"><strong><code>+7.01</code> pp</strong></td>
          <td class="align-right"><strong><code>+27.80</code> pp</strong></td>
        </tr>
        <tr>
          <td>Relevance <span class="table-note-inline"><code>n=123</code>, locally adjusted</span></td>
          <td class="align-right"><code>21.95%</code> (27)</td>
          <td class="align-right"><code>27.64%</code> (34)</td>
          <td class="align-right"><code>+5.69</code> pp</td>
          <td class="align-right"><code>+8.70</code> pp</td>
        </tr>
        <tr>
          <td>Macro</td>
          <td class="align-right"><code>56.45%</code></td>
          <td class="align-right"><code>62.62%</code></td>
          <td class="align-right"><code>+6.17</code> pp</td>
          <td class="align-right"><code>+8.80</code> pp</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> SFT-to-DPO changes in the local reconstruction and changes reported by DiaTool-DPO <a class="citation-ref" href="#ref-diatool-dpo" aria-label="Reference 1">[1]</a>. Higher is better on all four axes. The columns do not estimate one common effect because the checkpoints, preference data, and judge backends differ.</figcaption>
</figure>

The local Macro relative gain was `+10.93%`; the paper's was `+10.78%`. In the paper, Slot was the largest positive change while Completion decreased. Locally, Completion and Call contributed more and Slot increased less. Similar aggregate ratios therefore did not distinguish the different behavioral composition.

At the item level, the local Slot comparison contained 43 improvements and 12 regressions. This confirms a positive aggregate Slot movement, but not the magnitude or behavioral composition reported in the paper. The difference between the local profile and the paper's Slot-dominant profile motivates the trajectory-level diagnostics below.

## Preference-Trajectory Diagnostics

The initial data audit covered schema, state paths, loaders, duplicates, masks, and pair-level semantic validity. Two additional measurements were added after the behavioral difference appeared: branch-level surface concentration and divergence-state coverage.

The surface diagnostics use the `2,530` Hard Type2 partial-call target pairs within `7,832` Type2 pairs, derived from 562 source trajectories. An exact surface groups only identical first-assistant `content + tool_calls`; source-equal weighting assigns the same total weight to each source. The remaining-one row is separate: it measures divergence coverage in the prefix-synchronized post-hoc reconstruction.

On a 5% source-group validation split, chosen reward exceeded rejected reward for `97.86%` of pairs. The split contained 840 pairs derived from 135 source groups, with zero source overlap with training. The trajectory-level implicit rewards were recorded relative to the frozen SFT reference. They diagnose where the learned margin formed; they do not directly measure generated behavior. Figure 3 summarizes the Hard Type2 surface-concentration and divergence-state diagnostics; Table 4 reports them alongside the reward diagnostics and interpretation boundaries.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/diatool-dpo-public-reconstruction-preference-trajectories/preference-trajectory-diagnostics.svg" alt="Relational diagram from a shared user query to a chosen missing-field question and a rejected early tool call, with exact-surface concentration values and one-Slot-remaining divergence coverage">
  <figcaption><strong>Figure 3.</strong> Chosen and rejected trajectories share the user query but diverge into different behaviors. Exact-surface concentrations come from the primary reconstruction; remaining-one coverage comes from the prefix-synchronized post-hoc reconstruction. The box geometry is conceptual and does not establish shortcut learning.</figcaption>
</figure>

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Diagnostic</th>
          <th class="align-right">Observation</th>
          <th>Interpretive boundary</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Chosen-arm implicit reward</td>
          <td class="align-right"><code>-0.038</code></td>
          <td>Small recorded trajectory-reward change</td>
        </tr>
        <tr>
          <td>Rejected-arm implicit reward</td>
          <td class="align-right"><code>-6.021</code></td>
          <td>Most of the recorded margin formed through the rejected arm</td>
        </tr>
        <tr>
          <td>Rejected share of absolute reward magnitude</td>
          <td class="align-right"><code>99.38%</code></td>
          <td>A reward decomposition, not behavioral evidence</td>
        </tr>
        <tr>
          <td>Chosen first-assistant exact surface, top-1 / top-5</td>
          <td class="align-right"><code>8.18%</code> / <code>28.50%</code></td>
          <td>Hard Type2 partial-call subset; source-equal values were <code>8.19%</code> / <code>28.83%</code></td>
        </tr>
        <tr>
          <td>Rejected first-assistant exact surface, top-1 / top-5</td>
          <td class="align-right"><code>49.13%</code> / <code>71.30%</code></td>
          <td>Source-equal values were <code>49.47%</code> / <code>71.71%</code></td>
        </tr>
        <tr>
          <td>One Slot remaining at partial-call divergence</td>
          <td class="align-right"><code>2,521 / 2,530</code> (<code>99.64%</code>)</td>
          <td>Prefix-synchronized post-hoc reconstruction; source-level all-remaining-one coverage was <code>559 / 562</code> (<code>99.47%</code>)</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> Diagnostics from three populations: reward rows use the 5% source-group validation split; surface rows use the Hard Type2 partial-call subset; the remaining-one row uses the prefix-synchronized post-hoc reconstruction. These measurements locate repeated training signals; none alone demonstrates shortcut learning or generated behavior.</figcaption>
</figure>

The pair-level and source-equal concentration values were similar. The observed skew is therefore difficult to explain solely by a small number of sources producing many pairs. In the prefix-synchronized reconstruction, `remaining-one` does not mean that the source trajectories lacked multi-missing states. It means the chosen and rejected behaviors usually diverged immediately before the final missing field.

Lowering rejected reward is a normal DPO optimization path <a class="citation-ref" href="#ref-dpo" aria-label="Reference 3">[3]</a>. High rejected-surface concentration and narrow divergence-state coverage can coexist with valid preference learning; these measurements alone do not demonstrate shortcut learning <a class="citation-ref" href="#ref-shortcut-learning" aria-label="Reference 7">[7]</a>. Because the original preference data were unavailable for the same measurements, these diagnostics remain specific to the local reconstruction and do not establish a difference from the original data distribution. They instead motivate a bounded sensitivity test of whether a different trajectory construction is associated with different Slot behavior.

## Post-Hoc Trajectory Sensitivity

A separate post-hoc reconstruction tested whether the Hard Type2 trajectory construction was associated with the observed Slot behavior. For the `2,530` partial-call target pairs, chosen and rejected prefixes were synchronized through the turn immediately before their behaviors diverged.

The other `14,264` pairs, starting SFT model, objective, and optimizer-update budget were held fixed. Prefix synchronization nevertheless altered later trajectory content, tokenization, and branch lengths, so this condition is a sensitivity comparison rather than an isolated ablation.

The intervention did not isolate prefix equality. Under the tokenizer and chat-template rendering used for training, chosen tokens changed by `-0.73%` and rejected tokens by `-0.09%` over the full dataset. Within the changed pairs, combined chosen-plus-rejected tokens changed by `-2.30%`, and the mean chosen-minus-rejected length gap decreased from `41.03` to `28.36` tokens. Neither dataset contained trajectories longer than `8,192` tokens. Figure 4 summarizes the direction of the axis-level changes and the unchanged auxiliary rollout result. Table 5 retains the exact values and presents the run as a sensitivity comparison rather than an isolated ablation.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/diatool-dpo-public-reconstruction-preference-trajectories/posthoc-sensitivity-deltas.svg" alt="Zero-centered bars showing lower Call and Completion, higher Slot, Relevance, and Macro, with unchanged auxiliary rollout success in the post-hoc sensitivity run">
  <figcaption><strong>Figure 4.</strong> Deltas are prefix-synchronized DPO minus primary DPO, in percentage points. Slot increased in this single run, while Call and Completion decreased and auxiliary rollout exact success remained <code>15/28</code>. Prefixes, later trajectory content, tokenization, and branch lengths changed together, so the chart does not isolate a prefix-only effect.</figcaption>
</figure>

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Model</th>
          <th class="align-right">Call<br><span class="table-note-inline"><code>n=670</code></span></th>
          <th class="align-right">Completion<br><span class="table-note-inline"><code>n=71</code></span></th>
          <th class="align-right">Slot<br><span class="table-note-inline"><code>n=442</code></span></th>
          <th class="align-right">Relevance<br><span class="table-note-inline"><code>n=123</code>, adjusted</span></th>
          <th class="align-right">Macro</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Primary DPO</td>
          <td class="align-right"><code>68.81%</code> (461)</td>
          <td class="align-right"><code>92.96%</code> (66)</td>
          <td class="align-right"><code>61.09%</code> (270)</td>
          <td class="align-right"><code>27.64%</code> (34)</td>
          <td class="align-right"><code>62.62%</code></td>
        </tr>
        <tr>
          <td>Prefix-synchronized DPO</td>
          <td class="align-right"><code>66.42%</code> (445)</td>
          <td class="align-right"><code>91.55%</code> (65)</td>
          <td class="align-right"><code>68.78%</code> (304)</td>
          <td class="align-right"><code>28.46%</code> (35)</td>
          <td class="align-right"><code>63.80%</code></td>
        </tr>
        <tr>
          <td>Change</td>
          <td class="align-right"><code>-2.39</code> pp</td>
          <td class="align-right"><code>-1.41</code> pp</td>
          <td class="align-right"><strong><code>+7.69</code> pp</strong></td>
          <td class="align-right"><code>+0.81</code> pp</td>
          <td class="align-right"><code>+1.18</code> pp</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 5.</strong> Single-run post-hoc sensitivity comparison. The prefix-synchronized reconstruction increased Slot, but also changed lengths and later trajectory content while slightly reducing Call and Completion.</figcaption>
</figure>

Judge-based paired transitions for the sensitivity run were improvement/regression `0/1` on Completion, `45/11` on Slot, and `3/2` on Relevance. After excluding three Slot cases where identical outputs received inconsistent judgments, the output-level Slot transitions were 44 improvements and 9 regressions.

The Slot benchmark output changed in the positive direction in this run. The evidence does not identify prefix synchronization as the sole cause: both arms were reconstructed, and tokenization, sequence lengths, and later trajectory content changed together. There was no random-rewrite or placebo control. Call and Completion decreased slightly, and exact success on 28 auxiliary free-running rollouts remained `15/28` for both DPO variants. The aggregate mismatch, local diagnostics, and post-hoc sensitivity result therefore support three separate audit axes rather than a single causal explanation.

## Three Audit Axes for Preference Trajectories

The evidence separates structural agreement, objective fit, and behavioral transfer. Pair counts, state paths, and objective components establish the first; preference accuracy and implicit reward margins describe the second; FunctionChat-Bench axes and paired output transitions test the third. Structural agreement and objective fit did not determine behavioral transfer: the primary reconstruction improved in aggregate without matching the paper's Slot-dominant profile, and the post-hoc run changed Slot without uniformly improving the other axes.

Three audit axes remain useful for preference trajectories with different branch lengths, expressions, and state paths:

- **Surface concentration:** measure whether a small set of exact branch expressions repeatedly co-occurs with the preference label. This is a distribution diagnostic, not a shortcut test by itself.
- **Divergence-state coverage:** report the source count and missing-Slot distribution at the point where chosen and rejected behaviors separate. Pair count alone does not reveal the covered contrastive states.
- **Objective-to-behavior transfer:** report preference accuracy and reward margins separately from generated behavior and axis-level paired transitions.

These checks do not prescribe a particular reconstruction method. They make the boundary between a structurally valid preference dataset and behaviorally equivalent training evidence more explicit.

## Conclusion

The central observation is that aggregate improvement and Slot behavior followed different profiles under the local and paper conditions. The local Slot gain was `+7.01` points, compared with the paper's `+27.80`-point change, while the relative Macro gains were numerically similar. These values come from different checkpoints, preference data, and judge backends and are not one common effect estimate.

The trajectory diagnostics describe repeated local branch surfaces and narrow divergence-state coverage, and the prefix-synchronized condition was associated with a further `+7.69`-point Slot change in one run. That comparison changed tokenization, lengths, and later trajectory content together, reduced Call and Completion, and left auxiliary rollout success at `15/28`; it does not identify a sole cause or establish a generally superior reconstruction rule. The most stable conclusion is narrow: surface concentration, divergence-state coverage, and objective-to-behavior transfer complement pair-count and state-path checks when preference trajectories are reconstructed rather than directly available.

## Limitations

- The reconstruction did not use the paper's exact checkpoint, preference JSONL, or judge backend. On the Slot subset, the local judge agreed with an independent judge on `98.19%` of cases (Cohen's kappa `0.957`). This supports stability for that subset but does not establish compatibility with the paper's judge or scores.
- The primary DPO and post-hoc sensitivity condition were each trained once. Seed variation in the reported effect sizes was not measured.
- The post-hoc condition changed prefixes, later trajectory content, tokenization, and branch lengths together. It cannot isolate the contribution of any one component.
- The 28 auxiliary rollouts were separate from the paper's turn-level teacher-forced FunctionChat evaluation <a class="citation-ref" href="#ref-diatool-dpo" aria-label="Reference 1">[1]</a> and did not show a complete-call success increase.
- The original branch-level surface and divergence-state distributions were unavailable. The local diagnostics cannot establish whether the original data had the same or different concentration patterns.

## References

<div class="reference-list" markdown="1">

<ol>
  <li id="ref-diatool-dpo">Jung, S. et al. <strong>DiaTool-DPO: Multi-Turn Direct Preference Optimization for Tool-Augmented Large Language Models</strong>. <em>SIGDIAL 2025</em>, 2025. <a href="https://aclanthology.org/2025.sigdial-1.32/">ACL Anthology</a></li>
  <li id="ref-diatool-code">Kakao. <strong>DiaTool-DPO Reference Implementation</strong>. <a href="https://github.com/kakao/diatool-dpo">GitHub repository</a></li>
  <li id="ref-dpo">Rafailov, Rafael et al. <strong>Direct Preference Optimization: Your Language Model is Secretly a Reward Model</strong>. <em>NeurIPS 2023</em>, 2023. <a href="https://arxiv.org/abs/2305.18290">arXiv</a></li>
  <li id="ref-llama3">Meta. <strong>Meta-Llama-3-8B-Instruct</strong>. <a href="https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct">Hugging Face model card</a></li>
  <li id="ref-lora">Hu, Edward J. et al. <strong>LoRA: Low-Rank Adaptation of Large Language Models</strong>. <em>ICLR 2022</em>, 2022. <a href="https://arxiv.org/abs/2106.09685">arXiv</a></li>
  <li id="ref-functionchat-bench">Lee, Shinbok et al. <strong>FunctionChat-Bench: Comprehensive Evaluation of Language Models' Generative Capabilities in Korean Tool-use Dialogs</strong>. 2024. <a href="https://arxiv.org/abs/2411.14054">arXiv</a>; <a href="https://github.com/kakao/FunctionChat-Bench/tree/5ddb0b5bb37d6423e1f3381ef693cda811a7847e">evaluated repository revision</a></li>
  <li id="ref-shortcut-learning">Geirhos, Robert et al. <strong>Shortcut Learning in Deep Neural Networks</strong>. <em>Nature Machine Intelligence</em>, 2, 665-673, 2020. <a href="https://doi.org/10.1038/s42256-020-00257-z">DOI</a></li>
</ol>

</div>

## Citation

Text citation:

```text
Ilho Ahn, "Preference Trajectories and Slot Behavior in a DiaTool-DPO Reconstruction", Mini Research, July 29, 2026.
```

BibTeX:

```bibtex
@article{ahn2026diatooldpopublicreconstruction,
  author = {Ilho Ahn},
  title = {Preference Trajectories and Slot Behavior in a {DiaTool-DPO} Reconstruction},
  journal = {Mini Research},
  year = {2026},
  month = jul,
  url = {https://muted-color.github.io/research/2026/07/29/diatool-dpo-public-reconstruction-preference-trajectories/}
}
```
