---
layout: post
title: "Alignment Data Map: Timing of SimPO Boundary Crossings and Model-Specific Differences"
date: 2026-09-01 17:00:00 +0900
last_modified_at: 2026-09-03 21:39:48 +0900
lang: en
categories: ["LLM ALIGNMENT"]
tags: [llm, alignment, preference-data, data-selection, adm, simpo, qwen]
lab_host: "dgx1"
lab_path: "projects/adm-toolcall"
excerpt: "This note tracks when ADM-selected preference pairs cross SimPO boundaries and how the pattern differs across Qwen2.5-Instruct models."
description: "A follow-up research note examining when preference pairs derived from ADM's HighAvg region crossed SimPO boundaries relative to Random pairs across Qwen2.5-Instruct 1.5B, 3B, and 7B, and how the difference varied by model and checkpoint."
permalink: /research/2026/09/01/selected-preference-pairs-helped-earlier-not-uniformly/
translation_url: /research/2026/09/01/selected-preference-pairs-helped-earlier-not-uniformly/ko/
image: /assets/images/posts/selected-preference-pairs-helped-earlier-not-uniformly/social-thumbnail.png
image_alt: "Three rows of translucent preference-pair capsules crossing two glass boundaries at different times on a white background"
hero_image: /assets/images/posts/selected-preference-pairs-helped-earlier-not-uniformly/hero-original.png
hero_alt: "Three rows of translucent preference-pair capsules crossing two glass boundaries from different positions"
hero_frame: true
hero_compact: true
math: true
published: true
publication_status: "published"
---

Lee et al.'s Alignment Data Map (ADM) <a class="citation-ref" href="#ref-adm" aria-label="Reference 1">[1]</a> separates training data using the mean and variance of alignment scores computed over the candidate responses to an instruction. Its premise is that preference data do not all have equal learning value: **mean response quality and variance across responses** define the regions used for selection. The original study reported that training on only the 33% of samples in the high-mean, low-variance HighAvg region achieved alignment performance comparable to or better than training on the full dataset.

The region that ADM selects and the learning signal that the selected data produce for the model being trained are separate questions. After ADM-selected instructions are instantiated as preference pairs, this follow-up analysis tracks **how well Qwen2.5-Instruct 1.5B, 3B, and 7B distinguished each response pair before training** and how that distinction changed across training checkpoints.

{% include related-research-note.html label="Previous research note" aria_label="The preceding research note on Alignment Data Map" title="Alignment Data Map: From Measurements to Preference-Pair Supervision" description="The preceding analysis of ADM selection criteria and preference-pair construction" image="/assets/images/posts/adm-measurement-to-preference-pairs/hero-adm-map-highavg.png" url="/research/2026/08/23/adm-measurement-to-preference-pairs/" %}

## Summary

- Separate instances of Qwen2.5-Instruct 1.5B, 3B, and 7B were trained under the HighAvg and Random conditions. All models were compared on the same 600-pair evaluation set, with no overlap with the training data.
- At all three model sizes, **more pairs moved toward stronger preference for the chosen response under HighAvg.** The advantage did not grow consistently with model size: it was largest for 7B, while the final difference for 3B was smaller than for 1.5B.
- HighAvg did not produce small improvements across all pairs. It increased the number of pairs that crossed a boundary into a higher state rather than merely increasing margins within the same state, and was also associated with some regressions.
- The clearest difference was that **HighAvg produced boundary-crossing preference changes earlier within the same training budget.** Random caught up on some pairs later in training, narrowing the final gap.

## Problem Setting

ADM describes the measured properties of response sets and selects instructions for training. The unit of preference optimization is a prompt paired with chosen and rejected responses, constructed only after instruction selection. There is no reason to assume that the reference scorer used to select instructions and the model being trained find the same response pair equally difficult.

This distinction motivates the research question:

> Do preference pairs selected from a high-quality, low-variance region produce different learning signals depending on how well the model distinguishes the chosen and rejected responses before training?

The hypothesis examined here was that the effect of HighAvg might increase monotonically with model scale. If the selected pairs contained subtle but useful distinctions, a larger model might learn from them more effectively.

## Related Work

### Differences Among Selection Criteria

The value of a preference pair can first be characterized by **properties measured from the data itself**. ADM separates instructions by the mean and variance of alignment scores over candidate responses <a class="citation-ref" href="#ref-adm" aria-label="Reference 1">[1]</a>. Xiao et al. compared the positions of chosen and rejected responses within an on-policy reward distribution <a class="citation-ref" href="#ref-sweet-spot" aria-label="Reference 2">[2]</a>, while Deng et al. selected training data by combining an external reward margin with an implicit DPO margin <a class="citation-ref" href="#ref-preference-selection" aria-label="Reference 3">[3]</a>.

Another axis is **the learning state measured under the current policy**. Yang et al. prioritized annotation for pairs with small implicit DPO reward margins under the policy and reference policy <a class="citation-ref" href="#ref-pair-efficiency" aria-label="Reference 4">[4]</a>. Huang et al. defined alignment potential as the gap between the current policy's implicit margin and a target explicit margin <a class="citation-ref" href="#ref-alignment-potential" aria-label="Reference 5">[5]</a>. A score gap is therefore not a universal measure of pair difficulty. Reference separation, policy-relative margin, and distance to a target provide different signals.

### Time-Varying Value

The value of the same pair can also change during training. Peng et al.'s Uni-DPO adjusts weights using both intrinsic pair quality and the model's evolving performance <a class="citation-ref" href="#ref-uni-dpo" aria-label="Reference 6">[6]</a>. Li et al.'s MetaPO learns time-dependent sample weights from reward-margin evolution, learning volatility, and reference deviation <a class="citation-ref" href="#ref-temporal-weighting" aria-label="Reference 7">[7]</a>. A separate analysis connected input complexity and output ambiguity to different learning dynamics <a class="citation-ref" href="#ref-learning-order" aria-label="Reference 8">[8]</a>. These studies share the view that a useful pair may depend on the current policy and the point in training.

### Scope of This Analysis

This note compares models trained under a fixed ADM selection on a shared evaluation set separated from the training data. It tracks policy-state transitions and the timing of upward state changes within a limited update budget. The analysis concerns not only static data quality, but the training trajectory observed for a selected pair under the current policy. It does not propose a new selection rule or weighting method.

## Experimental Setup

### Data Selection and Training Comparison

In this note, **HighAvg** refers to preference pairs constructed from instructions selected from the high-mean, low-variance region of an ADM built with a fixed set of reference answers and a fixed scorer. **Random** refers to pairs sampled at random from the same source pool.

The two conditions were constructed from the same source pool while preserving source and task composition, and were trained with the same LoRA and SimPO recipe. The training models were the official Qwen2.5-Instruct [1.5B](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct), [3B](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct), and [7B](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct) checkpoints. Three runs with different random seeds were conducted at each size. To match training exposure rather than dataset size, both conditions were fixed at 276 optimizer updates, equivalent to approximately 3 epochs.

A **shared evaluation set** of 600 pairs with no prompt or pair overlap with the training data was evaluated repeatedly at the base policy and at checkpoints at steps 92, 184, and 276. Keeping the same pairs made it possible to track not only endpoint aggregates but also the state into which each pair moved during training. Overall trends were compared over three seeds, while a single seed was used for the detailed transition decomposition. These were fixed development data used for the follow-up analysis, not a new blind test.

### SimPO Margin and State Trajectory

This note uses **training model** to refer to the Qwen2.5-Instruct variant being trained (1.5B, 3B, or 7B), and **policy** to refer to $\pi_t$, which assigns response probabilities at a particular checkpoint.

For a pair $z=(x,y_w,y_l)$, the policy's length-normalized log-probability margin is defined as

$$
\Delta_{\pi}(z)
=
\frac{\log \pi(y_w\mid x)}{|y_w|}
-
\frac{\log \pi(y_l\mid x)}{|y_l|}.
$$

Meng et al.'s SimPO <a class="citation-ref" href="#ref-simpo" aria-label="Reference 9">[9]</a> trains $β\Delta_{\pi}$ to exceed the target margin $γ$. With $β=2$ and $γ=1$ in this setup, the target boundary is $\Delta=0.5$. Each pair was therefore assigned to one of three states:

$$
R:\Delta\le 0,
\qquad
U:0<\Delta<0.5,
\qquad
T:\Delta\ge0.5.
$$

- **R — preference reversed:** the policy prefers the rejected response.
- **U — correct, below target:** the chosen response ranks higher, but its separation is below the SimPO target.
- **T — target satisfied:** the chosen–rejected separation has reached the target.

Figure 1 shows how two objective boundaries divide the three states. Rightward movements `R→U`, `R→T`, and `U→T` were counted as upward transitions.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/selected-preference-pairs-helped-earlier-not-uniformly/figure1_simpo_margin_states.svg" alt="A horizontal policy-margin bar divided at zero and 0.5 into three SimPO states: preference reversed, correct but below target, and target satisfied.">
  <figcaption><strong>Figure 1.</strong> The <code>R/U/T</code> state space defined by the sign of the policy margin and the SimPO target boundary. Moving right increases the policy margin; arrows at the ends indicate that <code>R</code> and <code>T</code> are open-ended intervals. Segment widths do not encode numeric ranges or pair proportions.</figcaption>
</figure>

Under this state definition, a pair for which the policy strongly prefers the rejected response may not cross the next boundary within a limited number of updates. A pair for which the policy already prefers the chosen response beyond the target margin has no higher `R/U/T` state to reach. Between them, the next preference or target-margin boundary may lie within reach, allowing the same pair to produce an upward state transition.

The **first observed upward passage** is the first evaluation checkpoint at which a state higher than the pre-training state is observed. **State-standardized upward movement** is the HighAvg-minus-Random difference in the proportion of pairs whose state at a given checkpoint is higher than at base, averaged over base-state-specific differences under a shared `R/U/T` distribution.

The model-size comparison reports observations from the Qwen2.5-Instruct 1.5B, 3B, and 7B family. These official checkpoints differ in training conditions and post-training outcomes as well as parameter count; this is not a controlled experiment in which only parameter count changes.

## Results

### Effects by Model Size and Training Checkpoint

At step 276, HighAvg showed higher reward accuracy, policy margin, final upward movement, and target reach than Random for all three seeds at all three model sizes, and lower SimPO loss.

The effect size, however, did not follow the hypothesized monotonic order. After standardizing to a shared initial-state composition, the final HighAvg-minus-Random upward-movement differences were `+5.64 pp` for 1.5B, `+4.27 pp` for 3B, and `+8.06 pp` for 7B.

The checkpoint trajectories in Figure 2 show that the smaller effect for 3B than 1.5B at step 276 did not hold throughout training. For both 3B and 7B, the HighAvg-minus-Random difference peaked at step 184 and then declined at the final checkpoint. Across the three 3B seeds, the difference likewise grew during steps `92→184` and shrank during steps `184→276`.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/selected-preference-pairs-helped-earlier-not-uniformly/figure2_scale_and_checkpoint_timing.svg" alt="State-standardized HighAvg-minus-Random upward-movement differences at optimizer steps 92, 184, and 276. Qwen2.5-Instruct 1.5B uses gray circles and solid lines, 3B uses blue squares and dashed lines, and 7B uses black diamonds and dotted lines. Thin lines show seed trajectories and thick lines show means.">
  <figcaption><strong>Figure 2.</strong> State-standardized HighAvg-minus-Random upward movement by model size and evaluation checkpoint. Gray circles denote 1.5B, blue squares 3B, and black diamonds 7B. Thin lines show individual seed trajectories and thick lines show their means. The final difference was smallest for 3B and largest for 7B, while both 3B and 7B peaked at step 184.</figcaption>
</figure>

The HighAvg effect did not increase consistently with model size, and it varied with evaluation checkpoint within the same model. The initial `R/U/T` state of each pair and its distance to the next boundary therefore need to be considered alongside model size.

### Endpoint Accuracy and Transition Composition

Reward accuracy is based only on whether $\Delta>0$. Correction of a reversed preference, crossing of the target margin, within-state margin changes, and regression across either boundary are therefore combined into one endpoint value.

A detailed decomposition of same-pair training trajectories showed that HighAvg did not produce slightly larger margin gains for every pair. At all three model sizes, fewer pairs stayed in the same state throughout training, while more pairs ended in a higher state without any downward transition or reached the target state by step 276. The changes were generally larger for 1.5B and 7B and smaller for 3B.

Not every movement was upward, as Figure 3 shows. At all three model sizes, the proportion of pairs that experienced at least one downward transition during training was also approximately `2 pp` higher under HighAvg than Random. HighAvg was associated with state changes in more pairs, including some regressions.

At the pair level on the shared evaluation set, the difference between HighAvg and Random was clearer for movements that crossed a boundary into a higher state than for small margin increases within the same state. At every model size, more pairs showed this outcome only under HighAvg than only under Random. Pairs whose $\Delta$ increased without a state change were instead less common under HighAvg.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/selected-preference-pairs-helped-earlier-not-uniformly/figure3_transition_redistribution.svg" alt="Diverging bars comparing HighAvg-minus-Random differences for no state change, upward progress, target reach, and downward transition across 1.5B, 3B, and 7B.">
  <figcaption><strong>Figure 3.</strong> HighAvg-minus-Random transition composition. HighAvg reduced the number of pairs that remained in the same state and increased upward progress without a downward move and target reach, while also producing some downward movement. Whiskers show pair-cluster bootstrap 95% intervals. Target-reach rates exclude pairs already in <code>T</code> at base; this detailed decomposition uses a single seed.</figcaption>
</figure>

### Reference Score and Distance to the Next Boundary

One hypothesis for the model-size differences is that the chosen and rejected responses in pairs derived from HighAvg-selected instructions are difficult to distinguish, producing subtle learning signals. The absolute **reference score gap** between the chosen and rejected responses is an auxiliary measure of this ambiguity: a larger gap indicates a clearer distinction under the reference scorer.

For each pair eligible for upward passage, **Random first-passage frequency** was the fraction of the three Random runs in which an upward passage was observed by step 276. In Figure 4, its Spearman correlations with the reference score gap were small, at `ρ=.070–.124`. Instruction-level ADM mean, variance, and score range were also nearly uncorrelated with passage within 276 updates.

The distance from the pre-training policy to the next objective boundary showed a stronger association, with correlations between `ρ=−.469` and `−.443`. The farther away the next boundary was, the less likely upward passage was within 276 updates.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/selected-preference-pairs-helped-earlier-not-uniformly/figure4_reference_gap_vs_policy_headroom.svg" alt="Points and 95% intervals on a shared Spearman-correlation axis compare Random first-passage frequency across three seeds with the reference score gap and the pre-training policy's distance to the next boundary for 1.5B, 3B, and 7B.">
  <figcaption><strong>Figure 4.</strong> Spearman correlations between Random first-passage frequency across the three seeds and either the reference score gap or the pre-training policy's distance to the next boundary. Numbers at right give exact Spearman <span aria-label="rho">ρ</span> values; points and whiskers show estimates and pair-cluster bootstrap 95% intervals. The correlations for the reference score gap were close to zero, ranging from <code>+.070</code> to <code>+.124</code>, while distance to the next boundary showed a consistent negative correlation of <code>−.469–−.443</code>. A more distant boundary was therefore associated with a lower likelihood of upward passage within the limited update budget.</figcaption>
</figure>

The two measurements answer different questions. ADM uses a fixed reference measurement to define data regions and select instructions. The pre-training policy's distance to the next boundary describes how far a selected pair is from its next state. In these results, a pair's observed trajectory varied not only with data properties, but also with how well the policy distinguished that pair at the start of training and with the update window over which the change was measured.

### Timing of Upward Passage

For pairs whose base state was `R` or `U`, the analysis compared the first checkpoint at which each pair occupied a state above its base state. After direct standardization to a common distribution over pre-training state and within-state quartiles of distance to the next boundary, the HighAvg-minus-Random difference in cumulative upward passage was positive from step 92 and was generally largest at step 184 (Table 1).

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Model</th>
          <th class="align-right">Step 92</th>
          <th class="align-right">Step 184</th>
          <th class="align-right">Step 276</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>1.5B</td>
          <td class="align-right">+6.44 pp</td>
          <td class="align-right">+9.28 pp</td>
          <td class="align-right">+8.79 pp</td>
        </tr>
        <tr>
          <td>3B</td>
          <td class="align-right">+2.79 pp</td>
          <td class="align-right">+7.64 pp</td>
          <td class="align-right">+5.78 pp</td>
        </tr>
        <tr>
          <td>7B</td>
          <td class="align-right">+2.26 pp</td>
          <td class="align-right">+15.11 pp</td>
          <td class="align-right">+13.88 pp</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> HighAvg-minus-Random differences in cumulative upward passage after direct standardization over base state and within-state quartiles of distance to the next boundary. All nine pair-cluster bootstrap 95% intervals across three models and three checkpoints were above zero.</figcaption>
</figure>

The gap narrowed after step 184, primarily because Random later crossed boundaries that HighAvg had crossed earlier. Among the 63 base-`U` pair-by-seed trajectories for which HighAvg had reached `T` while Random remained in `U` at step 184, 61 remained in `T` under HighAvg at step 276, while Random had reached `T` in 35. The final gap narrowed because of Random's later catch-up rather than a broad retreat under HighAvg. Figure 5 shows both cumulative passage and the difference across distance-to-next-boundary bins.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/selected-preference-pairs-helped-earlier-not-uniformly/figure5_budget_conditioned_upward_passage.svg" alt="Cumulative upward-passage curves for HighAvg and Random on 1.5B, 3B, and 7B, with a checkpoint-grid advantage heatmap by quartile of initial distance to the next boundary.">
  <figcaption><strong>Figure 5.</strong> The upper panel shows cumulative upward passage after direct standardization over base state and within-state quartiles of distance to the next boundary. Values in the lower panel summarize quartile-specific cumulative-passage differences over the 92-step evaluation intervals; larger values indicate a larger HighAvg advantage in cumulative upward passage over time. They are not optimizer updates actually saved. Q1 is closest to the boundary and Q4 farthest; Q4 was weakest for every model.</figcaption>
</figure>

The largest effect did not occur among pairs farthest from the boundary. The HighAvg difference was concentrated in distance ranges from which the pre-training policy could reach the next state within the observation window. The effective distance range was wider for the 7B policy than for the 1.5B and 3B policies, but three official checkpoints do not establish a monotonic model-size effect.

Here, **earlier** means that upward passage was observed at an earlier evaluation checkpoint within the same 276-update window. Because checkpoints were evaluated only at steps 92, 184, and 276, the exact optimizer step at which an individual pair crossed a boundary is unknown.

### Supporting Evidence from Training Metrics

In seed 42, increases in training accuracy and training reward margin from epochs 1 to 3 were larger under HighAvg than Random for all three models. The change in SimPO loss also favored HighAvg for 1.5B and 7B, while the two conditions were nearly equal for 3B. Exact values by model are reported in Appendix Table 1.

The 3B model nevertheless showed differences in the training metrics even though its final transition difference was the smallest. These metrics were measured on different training datasets and do not substitute for trajectories on the shared evaluation set; they serve only as supporting evidence of optimization-related differences under HighAvg at all three model sizes.

## Conclusion

The model-size-only hypothesis was

$$
\text{larger parameter scale}
\quad\Rightarrow\quad
\text{larger HighAvg advantage}.
$$

The observed results were closer to the following chain:

$$
\text{initial policy state}
\rightarrow
\text{distance to the next boundary}
\rightarrow
\text{transition reachable within the budget}
\rightarrow
\text{observed training effect}.
$$

Model capacity may still matter, but the three checkpoints differed in their initial `R/U/T` composition and distances to the next boundary; those differences more directly described the observed model-specific patterns. This interpretation is consistent with the non-monotonic result—positive HighAvg effects for all three models, larger for 1.5B than 3B, and largest for 7B—and with changes over training. It is also consistent with the effect growing midway through training and then declining as Random caught up later.

A fixed ADM data map identifies the measurement region from which data were selected. The policy margin at each checkpoint shows which objective boundary a pair is currently close to crossing. Connecting these two pieces of information through the training trajectory of the same pair yields the central result of this comparison:

> **HighAvg showed a consistent aggregate advantage in this fixed comparison, but it did not produce a larger improvement for every pair or increase monotonically with model size. Its clearest difference was earlier upward passage across a policy-relative SimPO boundary.**

Understanding the learning effect of selected preference data required considering not only the data region, but also the policy's starting position on each pair and the update window over which its transition was observed.

## Limitations

- The shared evaluation set was development data held fixed for the follow-up analysis; whether the same transition pattern persists on a new external evaluation set was not tested.
- The three official checkpoints differ in training conditions and post-training outcomes as well as parameter count, so the observed differences cannot be interpreted as a pure model-size effect.
- Upward passage was observed only at steps 92, 184, and 276, so the exact optimizer step at which each pair crossed a boundary is unknown.

## Appendix

### Evaluation and Reproduction Conditions

- **Source and ADM measurement:** The analysis used the same 4,500 [UltraFeedback](https://huggingface.co/datasets/openbmb/UltraFeedback) instructions and four candidate responses per instruction as the preceding research note. Reference answers were generated with [Qwen3.5-122B-A10B](https://huggingface.co/Qwen/Qwen3.5-122B-A10B). Candidate responses were measured using overlapping-window mean similarity from [all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2), and ADM regions were assigned within source × task strata.
- **Training data:** HighAvg and Random each contained 1,080 instructions, yielding 5,682 and 5,773 valid preference pairs, respectively. The chosen–rejected direction was fixed by fine-grained scores from the source data.
- **Training:** Training used the SimPO objective with a learning rate of `5e-6`, a linear scheduler, and a warmup ratio of `0.1`. LoRA used rank `64`, alpha `128`, and dropout `0.05`; cutoff length was `2048`, with BF16 precision.
- **Exposure:** Training ran for 276 optimizer updates with a global batch size of `63`, saving checkpoints at steps 92, 184, and 276. Nominal training-pair exposure was 17,388 in both conditions, equivalent to approximately 3 epochs. Step 276 was fixed as the endpoint without checkpoint selection based on results.
- **Evaluation:** The same 600-pair evaluation set, disjoint from the training data, was used at base and at all three checkpoints. This was fixed development data, not a blind test.
- **Analysis:** The primary endpoints, upward-passage comparison, and reference–boundary-distance correlation analysis used seeds 42, 43, and 44. The detailed transition decomposition in Figure 3 and the Appendix training-metric table use seed 42. Uncertainty intervals used a pair-cluster bootstrap that resampled pair IDs while preserving repeated observations of the same pair.

### Training-Metric Details

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>HighAvg-minus-Random difference in<br><span class="table-note-inline">change from epochs 1→3</span></th>
          <th class="align-right">1.5B</th>
          <th class="align-right">3B</th>
          <th class="align-right">7B</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Training accuracy</td>
          <td class="align-right">+4.06 pp</td>
          <td class="align-right">+2.50 pp</td>
          <td class="align-right">+4.20 pp</td>
        </tr>
        <tr>
          <td>Training reward margin<br><span class="table-note-inline">$\beta\Delta$</span></td>
          <td class="align-right">+0.124</td>
          <td class="align-right">+0.130</td>
          <td class="align-right">+0.417</td>
        </tr>
        <tr>
          <td>SimPO loss</td>
          <td class="align-right">−0.0343</td>
          <td class="align-right">+0.0039</td>
          <td class="align-right">−0.0333</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 1.</strong> Seed-42 HighAvg-minus-Random differences in training-metric changes from epochs 1 to 3. These are in-distribution supporting metrics measured on different training datasets; they do not substitute for trajectories on the shared evaluation set.</figcaption>
</figure>

### Key Metrics

- **Policy margin $\Delta$:** the policy's length-normalized chosen–rejected log-probability difference.
- **Reward accuracy:** the proportion of pairs with $\Delta>0$, meaning that the policy prefers the chosen response to the rejected response.
- **Training reward margin:** the mean $\beta\Delta$ recorded in the SimPO training logs.
- **State-standardized upward movement:** the HighAvg-minus-Random difference in the proportion of pairs whose checkpoint state is higher than at base, averaged over base-state-specific differences under a shared `R/U/T` distribution.
- **First observed upward passage:** the evaluation checkpoint at which a pair whose base state is `R` or `U` first reaches a higher state.
- **Distance to the next boundary:** the distance from the base margin to the next SimPO boundary: $0-\Delta$ in `R` and $0.5-\Delta$ in `U`.
- **Base-state × boundary-distance-quartile standardization:** a direct weighting procedure that divides eligible pairs into eight strata—two base states and four within-state distance quartiles—and averages condition differences under a common stratum distribution.
- **Evaluation-interval summary:** a descriptive statistic that summarizes cumulative-passage indicators at steps 92, 184, and 276 as area over 92-step evaluation intervals. It is neither the actual boundary-crossing step nor the number of updates saved.
- **Pair-cluster bootstrap:** an uncertainty calculation that resamples pair IDs while retaining repeated observations of the same pair within each analysis.

## References

<div class="reference-list" markdown="1">

<ol>
  <li id="ref-adm">Lee, S., Kim, E., Lee, H., and Chang, B. <strong>Alignment Data Map for Efficient Preference Data Selection and Diagnosis</strong>. <em>Findings of ACL 2026</em>, 38225–38241, 2026. <a href="https://aclanthology.org/2026.findings-acl.1906/">ACL Anthology</a>; <a href="https://arxiv.org/abs/2505.23114">arXiv</a></li>
  <li id="ref-sweet-spot">Xiao, Y. et al. <strong>Finding the Sweet Spot: Preference Data Construction for Scaling Preference Optimization</strong>. <em>ACL 2025</em>, 12538–12552, 2025. <a href="https://aclanthology.org/2025.acl-long.615/">ACL Anthology</a></li>
  <li id="ref-preference-selection">Deng, X. et al. <strong>Less is More: Improving LLM Alignment via Preference Data Selection</strong>. <em>NeurIPS 2025</em>, 161259–161285, 2025. DOI: <a href="https://doi.org/10.52202/085713-5383">10.52202/085713-5383</a>; <a href="https://proceedings.neurips.cc/paper_files/paper/2025/hash/ebf95a6f3c575322da15d4fd0fc2b3c8-Abstract-Conference.html">NeurIPS</a></li>
  <li id="ref-pair-efficiency">Yang, S. et al. <strong>Not All Preference Pairs Are Created Equal: A Recipe for Annotation-Efficient Iterative Preference Learning</strong>. <em>Findings of EMNLP 2024</em>, 6549–6561, 2024. <a href="https://aclanthology.org/2024.findings-emnlp.382/">ACL Anthology</a></li>
  <li id="ref-alignment-potential">Huang, K. et al. <strong>Larger or Smaller Reward Margins to Select Preferences for LLM Alignment?</strong> <em>ICML 2025</em>, 25922–25946, 2025. <a href="https://proceedings.mlr.press/v267/huang25al.html">PMLR</a></li>
  <li id="ref-uni-dpo">Peng, S. et al. <strong>Uni-DPO: A Unified Paradigm for Dynamic Preference Optimization of LLMs</strong>. <em>ICLR 2026</em>, 2026. <a href="https://openreview.net/forum?id=G7DBGlgjjp">OpenReview</a></li>
  <li id="ref-temporal-weighting">Li, M., Zhou, X., and Zhao, P. <strong>Learning Temporally-Aware Sample Weights for Preference Optimization</strong>. <em>Findings of ACL 2026</em>, 12361–12377, 2026. <a href="https://aclanthology.org/2026.findings-acl.601/">ACL Anthology</a></li>
  <li id="ref-learning-order">Li, M., Wang, J., and Zhao, P. <strong>What Do LLMs Learn First? Asymmetric Learning Dynamics of Input Complexity and Output Ambiguity in Preference Alignment</strong>. <em>ACL 2026</em>, 17373–17388, 2026. <a href="https://aclanthology.org/2026.acl-long.789/">ACL Anthology</a></li>
  <li id="ref-simpo">Meng, Y., Xia, M., and Chen, D. <strong>SimPO: Simple Preference Optimization with a Reference-Free Reward</strong>. <em>NeurIPS 2024</em>, 124198–124235, 2024. <a href="https://proceedings.neurips.cc/paper_files/paper/2024/hash/e099c1c9699814af0be873a175361713-Abstract-Conference.html">NeurIPS</a></li>
</ol>

**Model and dataset resources:** [Qwen3.5-122B-A10B](https://huggingface.co/Qwen/Qwen3.5-122B-A10B), [all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2), [UltraFeedback](https://huggingface.co/datasets/openbmb/UltraFeedback), [Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct), [Qwen2.5-3B-Instruct](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct), [Qwen2.5-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct).

</div>

## Citation

Text citation:

```text
Ilho Ahn, "Alignment Data Map: Timing of SimPO Boundary Crossings and Model-Specific Differences", Mini Research, September 1, 2026.
```

BibTeX:

```bibtex
@article{ahn2026selectedpreferencepairsearlier,
  author = {Ilho Ahn},
  title = {Alignment Data Map: Timing of SimPO Boundary Crossings and Model-Specific Differences},
  journal = {Mini Research},
  year = {2026},
  month = sep,
  url = {https://muted-color.github.io/research/2026/09/01/selected-preference-pairs-helped-earlier-not-uniformly/}
}
```
