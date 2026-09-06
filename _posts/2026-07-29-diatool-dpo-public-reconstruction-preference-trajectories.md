---
title: "DiaTool-DPO Reconstruction: Preference Accuracy and Tool-Use Behavior"
date: 2026-07-29
last_modified_at: 2026-09-06 10:37:49 +0900
categories: ["LLM TOOL USE"]
tags: [llm, tool-use, dpo, preference-learning, function-calling, multi-turn-dialogue, llama3]
lang: en
math: true
lab_path: "experiment-lab/projects/diatool-dpo-reproduction"
excerpt: "A DiaTool-DPO reconstruction connecting preference ranking, repeated training responses, and changes in missing-field handling and complete-call success."
description: "A DiaTool-DPO reconstruction showed high held-out preference accuracy; a single-run data-construction comparison improved missing-field handling while Call and Completion declined and auxiliary rollout success was unchanged."
permalink: /research/2026/07/29/diatool-dpo-public-reconstruction-preference-trajectories/
image: /assets/images/posts/diatool-dpo-public-reconstruction-preference-trajectories/social-thumbnail.png
image_alt: "Local DPO comparison showing Slot +7.69 percentage points, Call -2.39, Completion -1.41, Relevance +0.81, Macro +1.18, and unchanged auxiliary rollout success at 15 of 28"
hero_image: /assets/images/posts/diatool-dpo-public-reconstruction-preference-trajectories/posthoc-sensitivity-deltas.svg
hero_alt: "Local DPO comparison showing Slot +7.69 percentage points, Call -2.39, Completion -1.41, Relevance +0.81, Macro +1.18, and unchanged auxiliary rollout success at 15 of 28"
hero_caption: "<strong>Figure 1.</strong> Local sensitivity comparison: prefix-synchronized DPO minus primary DPO, in percentage points. Missing-field handling (Slot) improved, while Call and Completion declined and auxiliary rollout exact success stayed at 15/28. This single-run comparison changed prefixes, later content, and lengths together. <a href='/assets/images/posts/diatool-dpo-public-reconstruction-preference-trajectories/posthoc-sensitivity-deltas.svg'>Open full-size figure</a>."
hero_frame: true
hero_variant: featured-plot
hero_fit: contain
published: true
publication_status: "published"
---

A tool-using assistant must decide when it has enough information to act. For example, a booking request without a date requires a follow-up question before a tool call. In FunctionChat-Bench, this missing-field behavior is evaluated on the **Slot** axis. Learning to rank a supplied dialogue correctly and generating that follow-up question are different capabilities.

This reconstruction of Jung et al.'s DiaTool-DPO examines how those capabilities align <a class="citation-ref" href="#ref-diatool-dpo" aria-label="Reference 1">[1]</a>. The primary model ranked held-out preference pairs with `97.86%` accuracy and improved all four local benchmark axes over its SFT starting point. Under a later reconstruction, Slot scores were higher, while Call and Completion were lower and auxiliary complete-call success was unchanged. The useful observation is this **uneven behavioral response across two constructions of the training data**.

## Summary

- **Preference fit:** chosen trajectories scored above rejected trajectories on `97.86%` of 840 held-out pairs from 135 source groups, with no source overlap with training. This evaluates supplied dialogue pairs.
- **Generated behavior:** the primary DPO model improved local Slot performance from `54.07%` to `61.09%` (`239→270/442`), with 43 item-level improvements and 12 regressions. This is a separate evaluation of generated responses, not the same accuracy measure as preference ranking.
- **Training-signal distribution:** the most frequent rejected first response covered `49.13%` of the inspected partial-call pairs, compared with `8.18%` for the most frequent chosen response. The difference motivates inspecting what contrasts the data repeatedly presents; it does not prove shortcut learning.
- **Local sensitivity:** the condition with synchronized prefixes for `2,530` pairs scored `68.78%` on Slot, versus `61.09%` for primary DPO in one run. Call and Completion declined, and auxiliary rollout success remained `15/28` for both DPO variants (Figure 1).
- **Scope:** the alternative also changed later content, tokenization, and lengths. Each DPO condition was trained once, and original run artifacts are unavailable for this revision. The results support a local sensitivity finding, not an isolated prefix effect or a generally better reconstruction rule.

## Experimental Setup

### Dialogue paths and preference training

DiaTool-DPO trains on preferred and rejected **trajectories**: complete sequences of assistant, user, and tool turns. Jung et al. define three query types: call immediately when required arguments are known, ask for missing fields before calling, or respond without a tool call when the request is unsupported <a class="citation-ref" href="#ref-diatool-dpo" aria-label="Reference 1">[1]</a>. Figure 2 summarizes this structure. The three query types were originally described over five conceptual dialogue states; they are task definitions, not observed internal model states.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/diatool-dpo-public-reconstruction-preference-trajectories/diatool-dpo-method.svg" alt="Conceptual flow from three tool-use query types—call, ask then call, and respond without a call—to paired full dialogues and a trajectory-level preference objective">
  <figcaption><strong>Figure 2.</strong> DiaTool-DPO pairs complete dialogue paths for immediate calls, questions about missing required fields, or responses without a tool call. The objective combines early-turn weighting, normalization by total turn weight, and a reward-gap margin. This is a conceptual method diagram; its geometry encodes no counts or effect sizes.</figcaption>
</figure>

Each pair shares the initial request and tool context, but its later turns and lengths can differ. Rejected paths include premature calls, redundant questions, incorrect refusals, and unsupported calls. The objective scores assistant turns relative to the reference policy, gives earlier turns more weight, normalizes by total turn weight, and applies a chosen/rejected reward-gap margin. User and tool messages provide context.

The reconstruction followed the public method and reference implementation, retaining DPO's policy-versus-reference comparison <a class="citation-ref" href="#ref-diatool-code" aria-label="Reference 2">[2]</a> <a class="citation-ref" href="#ref-dpo" aria-label="Reference 3">[3]</a>. It used separately reconstructed Korean preference data and a locally trained starting checkpoint. Appendix Table 1 records the reconstruction choices; the local comparisons below carry the main findings.

### Local training and evaluation conditions

Supervised fine-tuning (SFT) provided the starting tool-use policy. Both DPO conditions continued the same local rank-8 LoRA adapter, which updates a small set of trainable parameters while retaining the base model. Table 1 summarizes the recorded settings. The public SFT artifact documents the starting model, not the later DPO outcomes.

{% include model-mention-cards.html label="Reconstructed SFT checkpoint" aria_label="Reconstructed Korean tool-use SFT checkpoint used as the local DPO starting point" models="LLaMA 3 8B DiaTool Korean SFT LoRA|soleaf/Llama-3-8B-DiaTool-Ko-SFT-LoRA|https://huggingface.co/soleaf/Llama-3-8B-DiaTool-Ko-SFT-LoRA" %}

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>Field</th>
          <th>Recorded condition</th>
          <th>Role in this study</th>
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
          <td>Reported pair counts match the public specification</td>
        </tr>
        <tr>
          <td>DPO training</td>
          <td>1 epoch, total batch <code>8</code>, LR <code>1e-7</code>, bf16, max length <code>8,192</code></td>
          <td>Settings recorded for the reconstruction</td>
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
  <figcaption><strong>Table 1.</strong> Recorded local training and evaluation conditions. The two DPO conditions shared the reconstructed SFT starting point. The evaluated benchmark revision is specified; complete run and decoding configurations are not available for this revision.</figcaption>
</figure>

FunctionChat-Bench separates four behaviors <a class="citation-ref" href="#ref-functionchat-bench" aria-label="Reference 6">[6]</a>:

- **Call:** produce the correct tool and arguments. The local implementation used normalized tool-call exact match.
- **Completion:** convey the tool's returned result appropriately.
- **Slot:** request missing required information before a call.
- **Relevance:** respond appropriately when no tool supports the request or a tool call is unnecessary.

Completion, Slot, and Relevance used a rubric-based judge. These benchmark items evaluate an assistant response in a supplied context. The separate 28-case **free-running rollout** check lets earlier generated turns affect later context and evaluates complete-call success. Improvement on a fixed-context Slot item can therefore be meaningful without establishing improvement across an entire dialogue.

The evaluated repository revision contains `1,306` items across Singlecall, Dialog, and CallDecision. The original FunctionChat paper described 700 items <a class="citation-ref" href="#ref-functionchat-bench" aria-label="Reference 6">[6]</a>, and DiaTool-DPO does not pin its evaluation commit or item count. This is another reason to treat the paper comparison in the Appendix as context rather than a matched reproduction.

Macro is the unweighted mean of the four axis percentages. Because their sample counts and scoring mechanisms differ, Macro summarizes the benchmark rather than a pooled pass rate. Main-result changes are reported in percentage points; the relative-gain calculation used for the paper comparison is given in the Appendix.

Identical-response judgment adjustments and the difference from the public SFT card's score snapshot are documented in the Appendix.

## Results

### Preference fit and missing-field handling

The primary model's held-out preference accuracy was `97.86%` on a 5% source-group validation split: 840 pairs from 135 groups, with zero source overlap with training. This shows that the learned score ordering extended to held-out source groups under the reconstructed pair distribution. The responses in this check were already supplied to the model; it did not test whether the model would generate the desired dialogue path.

Table 2 shows the separate generation-based evaluation. All four local axes improved over SFT. On Slot, the net gain was 31 passing items: 43 previously failing items improved and 12 previously passing items regressed. The model therefore improved missing-field handling in this evaluation while retaining substantial room for improvement. The high preference-ranking accuracy and the Slot result answer different questions and should not be compared as a single accuracy gap.

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Evaluation axis</th>
          <th class="align-right">SFT</th>
          <th class="align-right">Primary DPO</th>
          <th class="align-right">Change</th>

        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Call <span class="table-note-inline"><code>n=670</code></span></td>
          <td class="align-right"><code>63.88%</code> (428)</td>
          <td class="align-right"><code>68.81%</code> (461)</td>
          <td class="align-right"><code>+4.93</code> pp</td>

        </tr>
        <tr>
          <td>Completion <span class="table-note-inline"><code>n=71</code></span></td>
          <td class="align-right"><code>85.92%</code> (61)</td>
          <td class="align-right"><code>92.96%</code> (66)</td>
          <td class="align-right"><code>+7.04</code> pp</td>

        </tr>
        <tr>
          <td>Slot <span class="table-note-inline"><code>n=442</code></span></td>
          <td class="align-right"><code>54.07%</code> (239)</td>
          <td class="align-right"><code>61.09%</code> (270)</td>
          <td class="align-right"><strong><code>+7.01</code> pp</strong></td>

        </tr>
        <tr>
          <td>Relevance <span class="table-note-inline"><code>n=123</code>, locally adjusted</span></td>
          <td class="align-right"><code>21.95%</code> (27)</td>
          <td class="align-right"><code>27.64%</code> (34)</td>
          <td class="align-right"><code>+5.69</code> pp</td>

        </tr>
        <tr>
          <td>Macro</td>
          <td class="align-right"><code>56.45%</code></td>
          <td class="align-right"><code>62.62%</code></td>
          <td class="align-right"><code>+6.17</code> pp</td>

        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> Local SFT-to-DPO results. Parentheses give passing-item counts; changes are percentage points computed from counts before rounding. Relevance uses the identical-response judgment reconciliation described in the Appendix. Macro is an unweighted average across axes, not a pooled item accuracy.</figcaption>
</figure>

### Repeated contrasts in the primary preference data

The first data audit checked schema, state paths, loaders, duplicates, masks, and pair validity. The subsequent diagnostic examined whether the reconstructed data repeatedly contrasted a small set of response patterns.

The inspected subset contained `2,530` pairs for missing-field queries, labeled Hard Type2 partial-call in the original record. They were part of `7,832` Type2 pairs and derived from 562 source trajectories. A partial-call rejection calls a tool before all required fields have been gathered. An **exact first-response pattern** groups identical assistant `content + tool_calls`; it does not group paraphrases. **Top-1 and top-5 shares** are the fractions of inspected pairs covered by the most common one and five patterns. **Source-equal weighting** gives each source trajectory the same total weight, preventing sources with many derived pairs from dominating the count.

Table 3 separates two observations. First, the endpoint implicit rewards relative to the frozen SFT reference were `-0.038` for chosen trajectories and `-6.021` for rejected trajectories. The score contrast was dominated by lower rejected scores. Second, rejected first responses were more concentrated than chosen ones, and that difference remained under source-equal weighting.

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Diagnostic and population</th>
          <th class="align-right">Observation</th>
          <th>Interpretive boundary</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Chosen implicit reward<br><span class="table-note-inline">held-out preference pairs</span></td>
          <td class="align-right"><code>-0.038</code></td>
          <td>Near the SFT reference under the trajectory score</td>
        </tr>
        <tr>
          <td>Rejected implicit reward<br><span class="table-note-inline">held-out preference pairs</span></td>
          <td class="align-right"><code>-6.021</code></td>
          <td>Further below the SFT reference than the chosen score</td>
        </tr>
        <tr>
          <td>Rejected share of absolute reward magnitude</td>
          <td class="align-right"><code>99.38%</code></td>
          <td>Recorded decomposition of reward magnitudes</td>
        </tr>
        <tr>
          <td>Chosen first response, top-1 / top-5<br><span class="table-note-inline">exact text + tool calls</span></td>
          <td class="align-right"><code>8.18%</code> / <code>28.50%</code></td>
          <td>Hard Type2 partial-call subset; source-equal values were <code>8.19%</code> / <code>28.83%</code></td>
        </tr>
        <tr>
          <td>Rejected first response, top-1 / top-5<br><span class="table-note-inline">exact text + tool calls</span></td>
          <td class="align-right"><code>49.13%</code> / <code>71.30%</code></td>
          <td>Source-equal values were <code>49.47%</code> / <code>71.71%</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> Primary-reconstruction diagnostics. Reward rows use 840 held-out pairs from 135 source groups; response-concentration rows use the 2,530 Hard Type2 partial-call pairs. Source-equal weighting gives each source trajectory the same total weight. The two groups measure preference fit and data repetition, respectively.</figcaption>
</figure>

Lower rejected reward is a valid DPO optimization path <a class="citation-ref" href="#ref-dpo" aria-label="Reference 3">[3]</a>. The concentration finding identifies repeated supervision that can be inspected; it does not show that the model relied on those patterns as a shortcut <a class="citation-ref" href="#ref-shortcut-learning" aria-label="Reference 7">[7]</a>. Together, these observations motivate testing the sensitivity of generated behavior to dialogue construction. They do not identify the cause of the primary model's remaining Slot errors.

### Changing where the paired dialogues diverge

The alternative reconstruction synchronized chosen and rejected prefixes through the turn immediately before their behaviors diverged. It changed the `2,530` Hard Type2 partial-call pairs; the other `14,264` pairs, starting SFT model, objective, and optimizer-update budget were held fixed in the recorded setup. Synchronizing the prefix also changed later trajectory content, tokenization, and branch lengths. The exact recorded length changes are retained in the Appendix.

A coverage check on this **alternative dataset** found that `2,521 / 2,530` pairs (`99.64%`) diverged with only one required field still missing. At source level, all inspected pairs from `559 / 562` sources (`99.47%`) had that property. This locates the contrastive decision mostly at the final missing field. It does not mean those source dialogues lacked earlier states with several missing fields, and it is separate from the primary-data concentration measurements in Table 3.

### Behavioral changes in the sensitivity run

Figure 1 and Table 4 compare the primary and alternative conditions. Slot improved by `+7.69` percentage points, from 270 to 304 passing items out of 442. At the same time, Call lost 16 passing items and Completion lost one. The higher Macro score therefore summarizes a trade-off across behaviors, not a uniform improvement.

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
          <td>Prefix-synchronized<br><span class="table-note-inline">DPO</span></td>
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
  <figcaption><strong>Table 4.</strong> Local data-construction sensitivity comparison. Each DPO condition was trained once. Changes are prefix-synchronized minus primary DPO, computed from counts before rounding; positive values favor the alternative on that axis. Slot scores retain the 442-item judgment snapshot, separate from the filtered transition audit below.</figcaption>
</figure>

The paired transition audit supports a change in the generated Slot responses, beyond comparing two aggregate scores. The recorded judge-based improvement/regression counts were `0/1` for Completion, `45/11` for Slot, and `3/2` for Relevance. After excluding three Slot cases where identical outputs received inconsistent judgments, the filtered Slot audit contained **44 improvements and 9 regressions**. That exclusion changes the audited population; those counts are not a recomputation of the 442-item score row in Table 4.

Both DPO variants completed `15/28` auxiliary rollouts successfully. This small check showed no increase in complete-call success, despite the positive Slot movement. It does not establish zero effect on dialogue success. With one training run per condition and simultaneous changes to prefixes, content, and lengths, the observed shift is associated with the combined reconstruction change; its separate causes and sensitivity to training randomness remain unresolved.

## Interpretation

The contribution of this reconstruction is a connected assessment of **preference fit, the contrasts presented by the data, and generated tool-use behavior**.

- **Preference fit:** held-out ranking showed that the model learned the reconstructed preference distinction. The reward decomposition described how chosen and rejected scores differed relative to SFT.
- **Contrast coverage:** repeated rejected responses in the primary data and final-missing-field divergence in the alternative data exposed properties that pair counts and a valid dialogue schema do not describe. These are separate distribution diagnostics, not an established shortcut mechanism.
- **Behavioral transfer:** paired output changes supported a local Slot improvement, while Call, Completion, and complete-call success prevented that improvement from being read as a general gain in tool use.

The practical implication is to evaluate reconstructed preference data at all three levels. A schema and a high preference score describe what was supplied and learned; axis-level responses and free-running dialogues reveal which behaviors changed. This study supports that distinction through a specific reconstruction and one sensitivity comparison, without selecting a generally superior data-construction rule.

## Limitations

- **Single-run sensitivity:** the primary and alternative DPO conditions were each trained once. Seed variation was not measured, and no random-rewrite or placebo control isolated prefix synchronization from the other changes.
- **Judgment uncertainty:** the recorded Slot agreement with an independent judge was `98.19%` (Cohen's kappa `0.957`). This is evidence about that subset; it does not establish agreement with the paper's judge or validate every local score. Identical-output inconsistencies were handled as described above and in the Appendix.
- **Different evaluation roles:** the 28 rollouts are a small auxiliary check, separate from the fixed-context, teacher-forced turn evaluation described by DiaTool-DPO. Equal success counts on this check do not establish equivalent dialogue policies.
- **Unavailable run artifacts:** this revision uses retained tables, figures, and the public SFT documentation. Original DPO logs, paired outputs, full generation/judge configurations, and the paper's original preference data are unavailable for a fresh audit. The local concentration measurements cannot establish whether the paper's data had the same patterns.

## Appendix: Reconstruction and comparison context

### Recorded reconstruction scope

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
          <td>Continued pretraining / SFT<br>starting point</td>
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
  <figcaption><strong>Appendix Table 1.</strong> Recorded reconstruction choices relative to DiaTool-DPO <a class="citation-ref" href="#ref-diatool-dpo" aria-label="Reference 1">[1]</a>. Matching the reported pair counts, state paths, and settings establishes the intended structural comparison; it does not establish identity of checkpoints, trajectories, or evaluation conditions.</figcaption>
</figure>

### Paper comparison

For Macro scores $M_{\mathrm{SFT}}$ and $M_{\mathrm{DPO}}$, the relative gain $g$ is

$$
g = \frac{M_{\mathrm{DPO}}-M_{\mathrm{SFT}}}{M_{\mathrm{SFT}}}\times 100\%.
$$

The recorded local Macro relative gain was `+10.93%`, numerically close to the paper's `+10.78%`. Their behavioral composition differed: local Slot rose by `+7.01` points and Completion by `+7.04`, while the paper reported `+27.80` and `-2.80`, respectively. Appendix Figure 1 and Appendix Table 2 preserve that comparison.

This difference originally motivated the data diagnostics. It cannot quantify a reproduction shortfall: the checkpoints and preference trajectories differed, the paper's evaluation revision and detailed scoring implementation were not pinned, and the local Call score used exact match whereas the original benchmark described judge-based rubrics. A similar Macro ratio cannot resolve those differences.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/diatool-dpo-public-reconstruction-preference-trajectories/aggregate-behavior-change-focused.svg" alt="Measured comparison with Macro relative gains of 10.93% locally and 10.78% in the paper, followed by zero-centered local versus paper axis changes: Call +4.93 versus +1.40, Completion +7.04 versus -2.80, Slot +7.01 versus +27.80, and Relevance +5.69 versus +8.70 percentage points">
  <figcaption><strong>Appendix Figure 1.</strong> Contextual comparison of two reported profiles. The top strip shows relative Macro gains on a 0–12% scale; the lower plot shows axis changes in percentage points. Checkpoints, preference data, and scoring conditions differ, and the paper's evaluation revision is not pinned. These columns do not estimate a common effect.</figcaption>
</figure>

<figure class="table-figure table-figure--metrics table-figure--compact-metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--compact-two-col">
      <thead><tr><th>Evaluation axis</th><th class="align-right">Paper change</th></tr></thead>
      <tbody>
        <tr><td>Call</td><td class="align-right"><code>+1.40</code> pp</td></tr>
        <tr><td>Completion</td><td class="align-right"><code>-2.80</code> pp</td></tr>
        <tr><td>Slot</td><td class="align-right"><strong><code>+27.80</code> pp</strong></td></tr>
        <tr><td>Relevance</td><td class="align-right"><code>+8.70</code> pp</td></tr>
        <tr><td>Macro</td><td class="align-right"><code>+8.80</code> pp</td></tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 2.</strong> SFT-to-DPO changes calculated from DiaTool-DPO's reported scores. Values are retained for context alongside the local results in Table 2, not as a matched benchmark comparison.</figcaption>
</figure>

### Judgment snapshots and data-length changes

**SFT score snapshot.** The public SFT card lists Relevance `21.14%` and Macro `56.25%`. This note retains the later locally adjusted values `21.95%` and `56.45%`. The prior audit recorded two inconsistent judgments among 42 byte-identical Relevance responses and assigned identical outputs the same local judgment. The card and adjusted table are separate score snapshots; the adjustment logs are no longer available to recheck.

**Alternative-data lengths.** Under the training tokenizer and chat-template rendering, full-dataset chosen tokens changed by `-0.73%` and rejected tokens by `-0.09%`. Within the changed pairs, combined tokens changed by `-2.30%`, and the mean chosen-minus-rejected length gap fell from `41.03` to `28.36` tokens. Neither dataset contained trajectories longer than `8,192` tokens. These changes are part of the sensitivity condition, so the comparison does not isolate prefix synchronization.

## Experiment Resources

<div class="reference-list" markdown="1">

- [Reconstructed SFT adapter and model card](https://huggingface.co/soleaf/Llama-3-8B-DiaTool-Ko-SFT-LoRA), with its [training report](https://huggingface.co/soleaf/Llama-3-8B-DiaTool-Ko-SFT-LoRA/blob/main/reports/training.md). These document the Instruct-based continued-pretraining-to-SFT lineage and rank-8 LoRA. The card names `gpt-oss-120b` for its local judged axes; it does not supply the full DPO scoring configuration.
- [Evaluated FunctionChat-Bench revision](https://github.com/kakao/FunctionChat-Bench/tree/5ddb0b5bb37d6423e1f3381ef693cda811a7847e). The retained local axis counts are 670 Call, 71 Completion, 442 Slot, and 123 Relevance items.
- The September 6, 2026 revision reorganizes retained results and checks accessible primary sources. No new training, generation, or model judging was performed.

</div>

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
Ilho Ahn, "DiaTool-DPO Reconstruction: Preference Accuracy and Tool-Use Behavior", Mini Research, July 29, 2026.
```

BibTeX:

```bibtex
@article{ahn2026diatooldpopublicreconstruction,
  author = {Ilho Ahn},
  title = {DiaTool-DPO Reconstruction: Preference Accuracy and Tool-Use Behavior},
  journal = {Mini Research},
  year = {2026},
  month = jul,
  url = {https://muted-color.github.io/research/2026/07/29/diatool-dpo-public-reconstruction-preference-trajectories/}
}
```
