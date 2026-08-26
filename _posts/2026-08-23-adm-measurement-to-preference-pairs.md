---
title: "Alignment Data Map: From Measurements to Preference-Pair Supervision"
date: 2026-08-23 20:10:32 +0900
last_modified_at: 2026-08-26 19:52:48 +0900
lang: en
categories: ["LLM ALIGNMENT"]
tags: [llm, alignment, preference-data, data-selection, adm, simpo, ultrafeedback]
lab_host: "dgx1"
lab_path: "projects/adm-toolcall"
excerpt: "This note traces how Alignment Data Map coordinates vary with the reference answer and text processing, and how selected instructions become preference pairs used for training."
description: "A mini research note connecting Alignment Data Map measurement sensitivity and cohort composition on 4,500 UltraFeedback instructions to instantiated preference pairs and single-seed SimPO results."
permalink: /research/2026/08/23/adm-measurement-to-preference-pairs/
translation_url: /research/2026/08/23/adm-measurement-to-preference-pairs/ko/
image: /assets/images/posts/adm-measurement-to-preference-pairs/hero-adm-map-highavg.png
image_alt: "A translucent three-dimensional Alignment Data Map with three measured regions, with HighAvg highlighted in pale blue"
hero_image: /assets/images/posts/adm-measurement-to-preference-pairs/hero-adm-map-highavg.png
hero_alt: "A translucent three-dimensional Alignment Data Map with three measured regions, with HighAvg highlighted in pale blue."
hero_frame: true
hero_compact: true
math: true
published: true
publication_status: "published"
---

Lee et al.'s Alignment Data Map (ADM) <a class="citation-ref" href="#ref-adm" aria-label="Reference 1">[1]</a> selects preference data by grouping instructions according to the mean and variance of alignment scores computed over their candidate responses. Whether these coordinates remain stable across reference answers and text-processing methods, and how instruction selection translates into the composition of the actual training pairs, require separate validation. This note traces 4,500 instructions from changes in coordinates and regions under different measurement conditions to the conversion of selected instructions into preference pairs used for training.

ADM regions changed with the reference answer, long-text processing method, and cohort composition. Even with the same instruction quotas, expanding the selected instructions into response pairs produced different preference directions, score gaps, and repeated-exposure structures.

> In this note, **quality** is the mean sentence-embedding similarity between candidate responses and the reference answer. It does not denote overall response quality or agreement with human preferences.

## Summary

- The analysis traced how ADM measurements for 4,500 instructions, each with 4 candidate responses, became actual preference pairs used for training.
- Changing the reference-answer generation policy or long-text processing method changed the ADM region assigned to the same instruction.
- Matching instruction composition did not equalize the score gaps, preference directions, or repeated exposures of the instantiated response pairs.
- The single-seed training comparison showed differences across region pipelines, but did not isolate an effect of the ADM region itself.

## Problem Setting

ADM forms HighAvg, LowAvg, and HighVar regions from the mean and variation of candidate-level alignment scores. The use of mean and variation to characterize data follows Swayamdipta et al.'s Dataset Cartography <a class="citation-ref" href="#ref-dataset-cartography" aria-label="Reference 2">[2]</a>, while ADM applies this view to preference-data selection.

The original ADM study reported that the aggregate training-performance advantage of HighAvg selection persisted across maps built with LLM-as-a-judge, reward-model, and reference-based scoring <a class="citation-ref" href="#ref-adm" aria-label="Reference 1">[1]</a>. Rather than re-evaluating aggregate performance, this analysis examines **whether the coordinates and region of the same instruction remain stable across measurement conditions, and how instruction-level selection is transformed into actual training pairs**. Stability of aggregate performance and stability of individual-sample region assignments are distinct questions.

Song's data-centric alignment pipeline <a class="citation-ref" href="#ref-data-centric-alignment" aria-label="Reference 3">[3]</a> separates alignment data construction into response synthesis, preference evaluation, and preference instantiation. The contribution here is not this pipeline view itself, but a quantitative case study of the transformation from ADM's reference-based measurement to actual SimPO preference pairs.

Preference-pair score gaps and composition have been studied by Yang et al. <a class="citation-ref" href="#ref-pair-efficiency" aria-label="Reference 4">[4]</a>, Deng et al. <a class="citation-ref" href="#ref-preference-selection" aria-label="Reference 5">[5]</a>, and Xiao et al. <a class="citation-ref" href="#ref-sweet-spot" aria-label="Reference 6">[6]</a>, while Pan et al. analyzed the quality of chosen responses <a class="citation-ref" href="#ref-what-matters-dpo" aria-label="Reference 7">[7]</a>. This note does not evaluate the general superiority of a particular selection rule; it analyzes the response-pair-level training signal formed after instruction-level selection.

## Experimental Setup

### Reference-Based Measurement and Region Construction

The measurement cohort contained 4,500 UltraFeedback instructions <a class="citation-ref" href="#ref-ultrafeedback" aria-label="Reference 8">[8]</a>, sampled with consideration of source dataset, task type, and instruction length, with 4 candidate responses per instruction. Reference answers were generated using <a href="https://huggingface.co/Qwen/Qwen3.5-122B-A10B"><code>Qwen3.5-122B-A10B</code></a> in non-thinking mode with temperature 0 and a maximum of 4,096 tokens.

For each candidate response, cosine similarity to the reference answer was computed with the Sentence-BERT-family <a href="https://huggingface.co/sentence-transformers/all-mpnet-base-v2"><code>all-mpnet-base-v2</code></a> model <a class="citation-ref" href="#ref-sentence-bert" aria-label="Reference 9">[9]</a> <a class="citation-ref" href="#ref-mpnet" aria-label="Reference 10">[10]</a>. The prefix baseline used at most 384 tokens. For each instruction, the mean of the four similarities was defined as quality and their population variance as variability. Based on ranks within the full cohort, LowAvg, HighAvg, and HighVar were each assigned 1,500 instructions. A region therefore denotes a relative position within a particular reference-answer, scoring-method, and cohort configuration, not an absolute grade.

The analysis of actual training pairs used a map recomputed with overlapping-window means and stratified by source and task type. This condition is not the same as the initial map partitioned directly over the full cohort.

### Preference Pairs and Training Comparison

ADM selects instructions, whereas Meng et al.'s SimPO <a class="citation-ref" href="#ref-simpo" aria-label="Reference 11">[11]</a> trains on chosen–rejected response pairs. This analysis constructed all pairs of candidate responses whose source ratings differed and matched instruction quotas across the three regions within each source-by-task-type stratum. The realized training split contained 1,080 instructions per region, or 3,240 in total, which expanded into 17,301 pairs.

<a href="https://huggingface.co/Qwen/Qwen2.5-3B-Instruct"><code>Qwen2.5-3B-Instruct</code></a> was trained for up to 5 epochs with LoRA and SimPO. The learning rate was 5e-6 and the global batch size was 63. Within each region-specific development set, models were selected by the number of pairs matching the preferred direction, then by loss, then by earlier checkpoint. They were then compared on the same 600-pair development set with no prompt or pair overlap with the training data. The analysis separately tracked the instructions selected by ADM and the response pairs used by SimPO.

Figure 1 summarizes the full path from reference-conditioned candidate measurement to region-specific SimPO evaluation.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/adm-measurement-to-preference-pairs/adm-measurement-to-training-pairs.svg" alt="Four-stage flow from measuring four candidate responses for each of 4,500 instructions to mapping instructions into three ADM regions, instantiating 17,301 training pairs, and evaluating region-specific SimPO pipelines on a shared 600-pair set.">
  <figcaption><strong>Figure 1.</strong> Data path from reference-conditioned candidate measurement to region-specific SimPO evaluation. ADM selects instructions, whereas training uses instantiated response pairs; the highlighted stage marks this change in analysis unit. Counts are observed totals, but box widths are conceptual and do not encode scale.</figcaption>
</figure>

## Results

### Sensitivity to Reference Answers and Long-Text Processing

When GPT-4o and Qwen3.5 reference-answer generation policies were applied to the same 100 instructions and identical candidate responses, candidate-order agreement was .760, with a 95% bootstrap CI of .710–.808. The rank correlation for variance was .854, region macro-F1 was .7395, and 64 of 100 instructions had at least one reversal in candidate order.

In a separate comparison on a shared set of 60 samples, pairwise candidate-order agreement across GPT-4o, Qwen3.5, and three gpt-oss-120B repeats ranged from .7722 to .8472, and region macro-F1 ranged from .6500 to .8000.

Region shifts remained even when candidate responses and reference answers were fixed and only the long-text processing method changed. In Figure 2, higher values on all three metrics indicate greater agreement with the prefix baseline. Overlapping-window mean was farther from the baseline than head–tail segment mean on every metric.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/adm-measurement-to-preference-pairs/long-text-processing-stability.svg" alt="Dot plot comparing head–tail segment mean and overlapping-window mean against a 100 percent prefix baseline. Overlapping-window mean is lower for candidate-pair order agreement, region macro-F1, and original HighAvg retention.">
  <figcaption><strong>Figure 2.</strong> Stability under long-text processing changes with the same MPNet model, reference answers, and candidate responses. Head–tail segment mean changed 453 of 4,500 region assignments, while overlapping-window mean changed 615; the largest movement remained near the LowAvg–HighAvg boundary. The figure reports agreement with the prefix baseline.</figcaption>
</figure>

### Cohort Composition and Region Association

Figure 3 shows the ADM coordinates and relative-rank boundaries for all 4,500 instructions. Each region contains 1,500 instructions, but their data-source, instruction-length, and task-type compositions were not the same.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/adm-measurement-to-preference-pairs/adm-cohort-measured-map.svg" alt="Two-panel scatter plot of mean cosine similarity versus population variance across four candidate responses for 4,500 instructions. The left panel shows the full range and the right panel enlarges variability from 0 to 0.03; HighAvg, LowAvg, and HighVar each contain 1,500 instructions, with dashed cohort-relative boundaries.">
  <figcaption><strong>Figure 3.</strong> ADM coordinate distribution for a fixed cohort of 4,500 instructions. The left panel shows the full measured range, while the right panel enlarges the variability range from 0 to 0.03. Dashed lines mark the cohort-relative boundaries at variability 0.015260 and quality 0.7882 within the low-variability region. Each region contains 1,500 instructions, and quality is the mean cosine similarity to the Qwen reference answer. This is a Qwen-defined cohort map.</figcaption>
</figure>

Cramér's V between data source and ADM region assignment was .388. By region, 69.7% of HighAvg samples came from Evol-Instruct, while 58.4% of HighVar samples came from FLAN/NIV2. Cramér's V between instruction-length quartile and region assignment was .192, and mean instruction length was 487 characters for HighAvg and 888 characters for HighVar. Cramér's V between task type and region assignment was .160; 44.83% of Code instructions and 23.54% of Multi-constraint instructions were assigned to HighAvg.

On the overlapping-window-mean map, the source-distribution TV between the HighAvg training and development sets was .289 when matching considered task type only. After reconstruction by source and task type, it decreased to .030. This decrease follows directly from matching source composition, but the reconstruction also changed the regions of 1,387 of 4,500 instructions and changed the selected instructions and response pairs. Later training differences therefore combine multiple changes in data construction.

### Instruction Selection and Instantiated Preference Pairs

In a separate HighAvg data construction, the overall-quality rating direction and alignment-score direction disagreed on 862 of 3,229 non-tied pairs, or 26.7%. ADM instruction selection and response-pair preference labeling are not the same stage.

The instantiated training-pair composition also differed across the three regions after matching instruction quotas within each source-by-task-type stratum. In Table 1, the differences in source rating and alignment score are absolute values. A lower opposite-direction rate means the two criteria agree more often.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Region</th>
          <th class="align-right">Training pairs</th>
          <th class="align-right">Source-rating gap<br><span class="table-note-inline">median</span></th>
          <th class="align-right">Alignment-score gap<br><span class="table-note-inline">median</span></th>
          <th class="align-right">Alignment-score gap<br><span class="table-note-inline">&lt;.05</span></th>
          <th class="align-right">Opposite direction</th>
          <th class="align-right">Mean pairs<br><span class="table-note-inline">per instruction</span></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>LowAvg</td>
          <td class="align-right">5,774</td>
          <td class="align-right">1.000</td>
          <td class="align-right">.0727</td>
          <td class="align-right">36.91%</td>
          <td class="align-right">37.51%</td>
          <td class="align-right">5.346</td>
        </tr>
        <tr>
          <td>HighAvg</td>
          <td class="align-right">5,682</td>
          <td class="align-right">.750</td>
          <td class="align-right">.0490</td>
          <td class="align-right">50.70%</td>
          <td class="align-right">32.95%</td>
          <td class="align-right">5.261</td>
        </tr>
        <tr>
          <td>HighVar</td>
          <td class="align-right">5,845</td>
          <td class="align-right">1.250</td>
          <td class="align-right">.2047</td>
          <td class="align-right">17.74%</td>
          <td class="align-right">26.48%</td>
          <td class="align-right">5.412</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> Composition of instantiated training pairs derived from source ratings. HighAvg had the smallest median alignment-score gap and the largest share of pairs below .05.</figcaption>
</figure>

Source-by-task-type TV was 0 at the instruction level, but after expansion into response pairs, source-by-task-type TV remained .0101–.0127 and length-bin TV remained .0418–.0728. Matching instruction composition alone did not equalize response-pair direction, score gap, or repeated exposure.

### Single-Seed Pipeline Comparison

Reward accuracy is the proportion of pairs for which the model assigns a higher reward to the chosen response than to the rejected response; higher is better. Reward margin is the mean difference between the two rewards; higher is better. SimPO loss is sensitive to failures to reach the target margin and to the negative-margin tail; lower is better.

Table 2 compares three region pipelines, each including region-specific model selection, with the base model on the same shared 600-pair development set.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Pipeline</th>
          <th class="align-right">Preferred-direction matches</th>
          <th class="align-right">Reward accuracy</th>
          <th class="align-right">Reward accuracy Δ<br><span class="table-note-inline">vs. base model</span></th>
          <th class="align-right">SimPO loss</th>
          <th class="align-right">Reward margin</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Qwen base</td>
          <td class="align-right">378/600</td>
          <td class="align-right">63.00%</td>
          <td class="align-right">—</td>
          <td class="align-right">1.253075</td>
          <td class="align-right">1.395679</td>
        </tr>
        <tr>
          <td>LowAvg</td>
          <td class="align-right">421/600</td>
          <td class="align-right">70.17%</td>
          <td class="align-right">+7.17pp</td>
          <td class="align-right">1.031459</td>
          <td class="align-right">1.506562</td>
        </tr>
        <tr>
          <td>HighVar</td>
          <td class="align-right">431/600</td>
          <td class="align-right">71.83%</td>
          <td class="align-right">+8.83pp</td>
          <td class="align-right">1.031298</td>
          <td class="align-right">1.573699</td>
        </tr>
        <tr>
          <td>HighAvg</td>
          <td class="align-right">442/600</td>
          <td class="align-right">73.67%</td>
          <td class="align-right">+10.67pp</td>
          <td class="align-right">1.019236</td>
          <td class="align-right">2.149893</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> Region pipelines, including region-specific model selection, evaluated on the same shared 600-pair development set. Higher reward accuracy and reward margin are better; lower SimPO loss is better.</figcaption>
</figure>

In this single-seed comparison, HighAvg had 11 more preferred-direction matches than HighVar and the best observed reward accuracy, reward margin, and SimPO loss.

## Pipeline Interpretation

ADM coordinates are relative measurements that depend on the reference answer and text-processing method. The unit selected on the map is also different from the unit used in training: instructions versus response pairs. Even after matching instruction quotas, pair margins, directional disagreements, and repeated exposures per instruction differed.

Reproducing data selection and interpreting the scope of training results therefore requires recording not only the ADM region name, but also the reference-answer generation conditions, candidate-response set, text-processing method, cohort and region boundaries, response-pair construction rule, and the observed response-pair-level distributions.

## Limitations and Follow-Up Comparisons

- The reference-answer comparison changed both the model and generation settings, and the 60-sample ranges summarize pairwise comparisons and repeated runs rather than confidence intervals. A complete measurement validation would apply multiple reference answers to the same 4,500 instructions and candidate responses, then compare long-text scoring methods against human judgments or task-answer-grounded annotations.
- The shared 600 pairs formed a repeatedly used development set, and pair-level confidence intervals were not computed. The pipeline comparison lacked random-selection and full-data conditions, and every training result came from a single seed. Region-specific model selection and response-pair composition also varied, so the comparison does not isolate an ADM-region effect. A multi-seed comparison should change only response-pair direction while holding data composition, model, and training settings fixed.
- Generalization to external data and downstream benchmarks was outside the evaluation scope.

## Appendix: Main Metrics

- **Mean similarity to the reference answer:** Mean MPNet cosine similarity between the four candidate responses and the reference answer.
- **Variability:** Population variance of the four similarity scores (`ddof=0`).
- **Candidate-response order agreement:** Proportion of the six pairs formed by four candidates whose ordering agrees under two reference answers.
- **Region macro-F1:** Equally weighted mean of per-class F1 scores between two ADM region assignments.
- **Cramér's V:** Strength of association between region and source, task type, or length category.
- **Source-distribution distance (TV):** Difference between the source proportions of two sets, $\frac{1}{2}\sum_i\lvert p_{1,i}-p_{2,i}\rvert$.
- **Reward accuracy, reward margin, and SimPO loss:** Respectively, the preferred-direction match rate, mean reward difference, and loss reflecting target-margin shortfalls and the negative-margin tail.

## References

<div class="reference-list" markdown="1">

<ol>
  <li id="ref-adm">Lee, S., Kim, E., Lee, H., and Chang, B. <strong>Alignment Data Map for Efficient Preference Data Selection and Diagnosis</strong>. <em>Findings of ACL 2026</em>, 38225–38241, 2026. <a href="https://aclanthology.org/2026.findings-acl.1906/">ACL Anthology</a>; <a href="https://arxiv.org/abs/2505.23114">arXiv</a></li>
  <li id="ref-dataset-cartography">Swayamdipta, S. et al. <strong>Dataset Cartography: Mapping and Diagnosing Datasets with Training Dynamics</strong>. <em>EMNLP 2020</em>, 9275–9293, 2020. <a href="https://aclanthology.org/2020.emnlp-main.746/">ACL Anthology</a></li>
  <li id="ref-data-centric-alignment">Song, H. <strong>Alignment Tuning for Large Language Models: A Data-Centric Lens on Alignment Data Pipelines</strong>. <em>Findings of ACL 2026</em>, 2541–2561, 2026. <a href="https://aclanthology.org/2026.findings-acl.121/">ACL Anthology</a></li>
  <li id="ref-pair-efficiency">Yang, S. et al. <strong>Not All Preference Pairs Are Created Equal: A Recipe for Annotation-Efficient Iterative Preference Learning</strong>. <em>Findings of EMNLP 2024</em>, 6549–6561, 2024. <a href="https://aclanthology.org/2024.findings-emnlp.382/">ACL Anthology</a></li>
  <li id="ref-preference-selection">Deng, X. et al. <strong>Less is More: Improving LLM Alignment via Preference Data Selection</strong>. arXiv:2502.14560, 2025. <a href="https://arxiv.org/abs/2502.14560">arXiv</a></li>
  <li id="ref-sweet-spot">Xiao, Y. et al. <strong>Finding the Sweet Spot: Preference Data Construction for Scaling Preference Optimization</strong>. <em>ACL 2025</em>, 12538–12552, 2025. <a href="https://aclanthology.org/2025.acl-long.615/">ACL Anthology</a></li>
  <li id="ref-what-matters-dpo">Pan, Y. et al. <strong>What Matters in Data for DPO?</strong> <em>NeurIPS 2025</em>, 44689–44716, 2025. <a href="https://proceedings.neurips.cc/paper_files/paper/2025/hash/3f37b8fbd43303106dd141a602838ad5-Abstract-Conference.html">NeurIPS</a></li>
  <li id="ref-ultrafeedback">Cui, G. et al. <strong>UltraFeedback: Boosting Language Models with Scaled AI Feedback</strong>. <em>ICML 2024</em>, 9722–9744, 2024. <a href="https://proceedings.mlr.press/v235/cui24f.html">PMLR</a>; <a href="https://huggingface.co/datasets/openbmb/UltraFeedback">Dataset</a></li>
  <li id="ref-sentence-bert">Reimers, N. and Gurevych, I. <strong>Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks</strong>. <em>EMNLP-IJCNLP 2019</em>, 3982–3992, 2019. <a href="https://aclanthology.org/D19-1410/">ACL Anthology</a></li>
  <li id="ref-mpnet">Song, K., Tan, X., Qin, T., Lu, J., and Liu, T.-Y. <strong>MPNet: Masked and Permuted Pre-training for Language Understanding</strong>. <em>NeurIPS 2020</em>, 16857–16867, 2020. <a href="https://proceedings.neurips.cc/paper/2020/hash/c3a690be93aa602ee2dc0ccab5b7b67e-Abstract.html">NeurIPS</a></li>
  <li id="ref-simpo">Meng, Y., Xia, M., and Chen, D. <strong>SimPO: Simple Preference Optimization with a Reference-Free Reward</strong>. <em>NeurIPS 2024</em>, 124198–124235, 2024. <a href="https://proceedings.neurips.cc/paper_files/paper/2024/hash/e099c1c9699814af0be873a175361713-Abstract-Conference.html">NeurIPS</a></li>
</ol>

**Model and dataset resources:** [Qwen3.5-122B-A10B](https://huggingface.co/Qwen/Qwen3.5-122B-A10B), [Qwen2.5-3B-Instruct](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct), [all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2), and [UltraFeedback](https://huggingface.co/datasets/openbmb/UltraFeedback).

</div>

## Citation

Text citation:

```text
Ilho Ahn, "Alignment Data Map: From Measurements to Preference-Pair Supervision", Mini Research, August 23, 2026.
```

BibTeX:

```bibtex
@article{ahn2026admmeasurementpreferencepairs,
  author = {Ilho Ahn},
  title = {Alignment Data Map: From Measurements to Preference-Pair Supervision},
  journal = {Mini Research},
  year = {2026},
  month = aug,
  url = {https://muted-color.github.io/research/2026/08/23/adm-measurement-to-preference-pairs/}
}
```
