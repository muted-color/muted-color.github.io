---
layout: post
title: "전문화된 Tool-Use DPO Recipe의 고정 예산 비교"
date: 2026-06-27 11:04:00 +0900
last_modified_at: 2026-08-26 23:29:18 +0900
lang: ko
categories: ["LLM EVAL"]
tags: [llm, tool-use, dpo, function-calling, bfcl, when2call, ifeval, qwen3]
lab_host: "dgx3"
lab_path: "projects/tool-use-dpo-negative-sources"
excerpt: "동일한 DPO 예산에서도 전문화된 tool-use recipe는 서로 다른 평가 축을 변화시켰으며, filtering·source mixing·longer training은 이 trade-off를 일관되게 해소하지 못했다."
description: "전문화된 Qwen3-8B tool-use DPO recipe를 고정 예산에서 비교하고, evaluation-axis transfer와 semantic filtering, mixed-source training, checkpoint별 guardrail trade-off를 점검한 미니 리서치 노트."
permalink: /research/2026/06/27/tool-use-dpo-fixed-budget-reporting-profile/ko/
translation_url: /research/2026/06/27/tool-use-dpo-fixed-budget-reporting-profile/
image: /assets/images/posts/tool-use-dpo-fixed-budget-reporting-profile/hero-checkpoint-prism.png
image_alt: "동일한 두 반투명 recipe 흐름이 투명한 checkpoint 프리즘을 지나 서로 다른 형태의 평가 신호 세 개로 나뉘는 장면"
hero_image: /assets/images/posts/tool-use-dpo-fixed-budget-reporting-profile/hero-checkpoint-prism.png
hero_alt: "동일한 두 반투명 recipe 흐름이 투명한 checkpoint 프리즘을 지나 서로 다른 형태의 평가 신호 세 개로 나뉘는 장면"
hero_frame: true
hero_compact: true
---

전문화된 tool-use DPO recipe는 training source와 가까운 평가 축을 개선하면서도 다른 tool-use 능력에서는 같은 개선으로 이어지지 않을 수 있다. 고정 예산에서 semantic filtering, source mixing, longer training이 이러한 specialization을 줄이는지도 함께 점검했다.

`Qwen3-8B`를 기반으로 한 tool-use SFT checkpoint를 공통 reference로 두고 <a class="citation-ref" href="#ref-qwen3" aria-label="참고문헌 1">[1]</a>, 동일한 pair 예산과 optimizer step 예산에서 DPO negative recipe를 비교했다. 평가 질문은 function-call structure와 call-decision에 초점을 둔 recipe의 개선이 다른 평가 축에서도 유지되는지, 그리고 semantic filtering, 50:50 mixed-source recipe, longer training이 관찰된 trade-off를 줄이는지다. 이 글은 해당 조건을 점검한 실험 보고이며, 일반적인 recipe 순위나 새로운 reporting framework를 제안하지 않는다.

> **Tool-use DPO**는 tool-call 출력이나 tool-use 판단에서 chosen/rejected pair를 구성하고, DPO로 policy를 업데이트하는 preference optimization 설정이다 <a class="citation-ref" href="#ref-dpo" aria-label="참고문헌 2">[2]</a>. 새로운 objective를 제안하지 않고, 고정 예산에서 specialized recipe, pair filtering, source mixing, checkpoint 조건에 따라 나타난 변화를 비교한다.

{% include model-mention-cards.html label="주요 평가 리소스" aria_label="고정 예산 tool-use DPO audit의 주요 평가 리소스" models="Qwen3-8B|Qwen/Qwen3-8B|https://huggingface.co/Qwen/Qwen3-8B;When2Call|nvidia/When2Call|https://huggingface.co/datasets/nvidia/When2Call" %}

## 요약

- 동일한 `3000`-pair, `375`-step 예산에서 function-call structure 중심 recipe는 BFCL core에서, call-decision 중심 recipe는 When2Call에서 더 높은 점수를 기록했다. 어느 recipe도 두 평가 축에서 모두 우세하지 않았다.
- Semantic filtering의 변화는 작거나 불확실했다. 50:50 mixed-source condition도 각 specialist의 intended metric에 미치지 못했고, IFEval accuracy는 두 specialist보다 낮았다.
- 두 quality-gated recipe 모두 final checkpoint의 IFEval accuracy가 50-step checkpoint보다 낮았지만, 불확실성을 고려하면 이를 일반적인 early-stopping 기준으로 해석할 수는 없다.
- 평가 축의 방향은 추가 training seed 2개와 재구성한 pair pool에서도 유지됐다. 다만 prompt overlap과 단일 run인 mixed-source condition 때문에 robustness 해석은 제한적이다.

## 공개 산출물

{% include model-mention-cards.html label="GitHub 저장소" aria_label="Tool-use DPO 고정 예산 보고서 GitHub 저장소" models="Artifact release|muted-color/tool-use-dpo-fixed-budget-report|https://github.com/muted-color/tool-use-dpo-fixed-budget-report" %}

{% include model-mention-cards.html label="논문" aria_label="Tool-use DPO 고정 예산 보고서 논문 PDF" models="Paper PDF|paper.pdf|https://github.com/muted-color/tool-use-dpo-fixed-budget-report/blob/main/paper.pdf" %}

결과 표와 Figure 1은 정리된 평가 출력과 집계 표가 포함된 공개 artifact 저장소에서 확인할 수 있다 <a class="citation-ref" href="#ref-artifact-release" aria-label="참고문헌 3">[3]</a>.

## 평가 설계

공통 Qwen3-8B tool-use SFT checkpoint를 기준으로 두 specialized DPO recipe와 각각의 동일 예산 ungated control을 비교한다. 모든 condition은 `3000` preference pair, `375` optimizer step, beta `0.1`, learning rate `5e-6`, LoRA rank `16`, effective batch size `8`을 사용한다. Pair 수와 optimizer step 수는 같지만 source distribution과 loss가 적용되는 token 수까지 동일하지는 않다.

평가는 세 축으로 나뉜다. **BFCL core**는 주로 함수 선택과 인자 정확성에 초점을 둔 function-call structure axis다 <a class="citation-ref" href="#ref-bfcl" aria-label="참고문헌 4">[4]</a>. **When2Call**은 tool call, follow-up question, unable-to-answer 같은 call-decision behavior를 평가한다 <a class="citation-ref" href="#ref-when2call" aria-label="참고문헌 5">[5]</a>. Public slice에는 direct-answer gold row가 없지만 frozen macro-F1 evaluator는 direct answer를 zero-support class로 포함하므로, 이 metric을 네 행동 유형이 균형 있게 포함된 macro F1으로 해석하지 않는다. **IFEval prompt-strict accuracy**는 주요 intended metric이 아니라, DPO가 instruction following을 얼마나 변화시키는지 측정하는 guardrail metric이다 <a class="citation-ref" href="#ref-ifeval" aria-label="참고문헌 6">[6]</a>.

## 결과

결과는 BFCL과 When2Call의 evaluation-axis 차이, semantic quality gate의 downstream 효과, mixed-source 비교, checkpoint별 guardrail trade-off, seed 및 pair-pool robustness 범위로 구분한다.

### 평가 축 비교

Table 1은 탐색적으로 선택한 50-step checkpoint에서 function-call structure 중심 recipe와 call-decision 중심 recipe를 비교한다. 이 checkpoint는 분석 뒤 regression이 더 작은 보고 시점으로 선택했으며, 사전 등록된 선택이나 보편적인 early-stopping 규칙은 아니다. 값은 `function-call structure 중심 recipe - call-decision 중심 recipe`로 계산한 percentage-point delta다. BFCL 행이 양수이면 function-call structure 중심 recipe의 점수가 더 높고, When2Call 행이 음수이면 call-decision 중심 recipe의 점수가 더 높다. 표에서 `W2C`는 When2Call의 약자다.

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
          <td rowspan="3">Semantic quality gate 적용</td>
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
          <td rowspan="2">Semantic quality gate 미적용 control</td>
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
  <figcaption><strong>Table 1.</strong> 선택한 50-step checkpoint에서 <code>function-call structure 중심 recipe - call-decision 중심 recipe</code>로 계산한 evaluation-axis delta와 grouped bootstrap CI다.</figcaption>
</figure>

이 방향만으로 negative type의 인과 효과를 말할 수는 없다. Call-decision training source는 When2Call evaluation과 같은 task family에 속하며, recipe 사이의 prompt와 chosen response도 일치시키지 않았다. 따라서 측정된 gap은 데이터 소스 자체의 우위가 아니라 반복해서 관찰된 recipe profile로 해석한다.

### Semantic quality gate의 역할

Semantic filtering은 rejected output이 chosen output보다 실제로 나쁜지, schema-valid인지, 동등한 대안이 아닌지를 확인하는 pair-quality gate로 사용했다. 그러나 동일한 recipe에서 semantic quality gate 적용 condition과 미적용 control을 비교하면, Table 2의 downstream performance delta는 작거나 불확실하다.

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
  <figcaption><strong>Table 2.</strong> 동일 예산에서 <code>quality-gated condition - ungated control</code>로 계산한 downstream metric delta다.</figcaption>
</figure>

Table 2는 filtering 제거의 근거가 아니다. Tool-use negative에는 optional/default/no-op 차이, 무해한 normalization, 허용 가능한 대체 tool, chosen/reference가 의심스러운 사례가 쉽게 섞인다. Filtering을 performance gain으로 보고하려면 별도 근거가 필요하며, quality control과 downstream 변화는 분리해 보고한다.

### Mixed-source recipe

50:50 mixed-source recipe는 두 specialized source를 결합하면 두 intended-axis gain을 함께 유지할 수 있는지 확인한다. 각 source에서 quality-gated pair `1500`개를 사용해 총 `3000` pair와 `375` optimizer step으로 예산을 맞췄다.

50-step checkpoint에서 mixed-source recipe의 BFCL core는 `0.700`으로 function-call structure 중심 recipe의 `0.713`보다 낮았다. When2Call macro F1은 `0.513`으로 call-decision 중심 recipe의 `0.530`보다 낮았다. IFEval prompt-strict accuracy도 `0.521`로 두 specialized recipe의 `0.573`, `0.583`보다 낮았다. Mixed condition은 SFT baseline보다 두 intended axis를 모두 개선했지만, 각 specialist의 intended metric에 미치지 못했고 guardrail regression도 더 컸다. 이 예산에서 단순한 source mixing은 trade-off를 해소하지 못했다. 이 condition은 추가 seed나 reconstructed-pool replicate가 없는 단일 run이다.

### Checkpoint와 guardrail trade-off

Figure 1은 intended-axis gain과 IFEval prompt-strict regression을 함께 표시하고, Table 3은 이에 대응하는 absolute score를 제시한다. 동일한 recipe에서도 50-step checkpoint에서 final checkpoint로 이동하면 intended metric과 guardrail metric이 모두 달라진다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/tool-use-dpo-fixed-budget-reporting-profile/pareto-2panel.svg" alt="IFEval prompt-strict delta와 BFCL core 또는 When2Call macro F1 delta를 비교한 두 패널 산점도. Function-call structure 중심 recipe와 call-decision 중심 recipe에서 semantic quality gate 적용 여부에 따른 지점을 50-step checkpoint부터 final checkpoint까지 연결한다.">
  <figcaption><strong>Figure 1.</strong> Shared SFT baseline 대비 intended-metric gain과 IFEval prompt-strict delta를 함께 표시했다. 선 종류는 두 recipe를, marker 형태는 semantic quality gate 적용 condition과 미적용 control을 구분하며, 화살표는 50-step checkpoint에서 final checkpoint로 향한다. 축은 원 보고서와 동일한 percentage-point delta를 사용한다.</figcaption>
</figure>

50-step에서 final checkpoint로 이동할 때 function-call structure recipe의 BFCL gain은 `2.00` pp, IFEval accuracy는 `5.21` pp 감소했다(95% CI `[0.00, 10.42]`). Call-decision recipe의 When2Call macro F1은 `0.18` pp, IFEval accuracy는 `2.08` pp 감소했다(95% CI `[-2.08, 6.25]`). 두 IFEval interval 모두 0에 닿거나 포함했다.

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
  <figcaption><strong>Table 3.</strong> SFT baseline과 quality-gated DPO condition의 absolute score다. 값은 높을수록 좋은 비율이며, IFEval prompt-strict accuracy는 guardrail axis다.</figcaption>
</figure>

Early checkpoint의 일반적 우위는 이 결과로 뒷받침되지 않는다. Final checkpoint를 자동으로 보고하면 intended-axis gain과 guardrail regression 사이의 trade-off가 가려질 수 있다. 이 설정에서는 checkpoint 선택도 실험 결과의 일부다.

### Robustness와 coverage 범위

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
          <td>3개 seed에서 같은 방향이 유지됐다.<br><span class="table-note-inline">Gap 범위 (pp): BFCL <code>3.00–4.00</code>; W2C accuracy <code>5.00–6.67</code>; W2C macro F1 <code>4.26–5.31</code>.</span></td>
          <td>고정 pair pool에 한정.</td>
        </tr>
        <tr>
          <td>재구성한 pair pool</td>
          <td>Pair-id와 content-hash overlap은 없었고, prompt-id overlap은 <code>401/3000</code>, <code>1337/3000</code>이었다.<br><span class="table-note-inline">재구성 pool gap (pp): BFCL <code>3.33</code>; W2C accuracy <code>6.33</code>; W2C macro F1 <code>5.04</code>.</span></td>
          <td>재구성 1회; prompt는 독립적이지 않음.</td>
        </tr>
        <tr>
          <td>When2Call coverage</td>
          <td>Labeled row <code>27,952</code>개; direct-answer gold row <code>0</code>개.</td>
          <td>포함된 decision slice 3종에 한정.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> Robustness 검사와 각 결과가 지지하는 범위.</figcaption>
</figure>

## 해석

Tool-use DPO는 모든 평가 축을 일관되게 개선하지 않았다. Function-call structure 중심 recipe는 function-call correctness에서, call-decision 중심 recipe는 평가에 포함된 call-decision slice에서 더 큰 변화를 보였다. Semantic quality gate는 일반적인 downstream gain을 지지하지 않았고, 50:50 mixed-source recipe도 두 specialist의 intended metric과 더 나은 guardrail 결과를 동시에 달성하지 못했다. Longer training은 function-call recipe의 intended gain을 줄이고 IFEval regression을 키웠으며, call-decision recipe에서는 같은 방향의 point estimate가 더 큰 불확실성과 함께 관찰됐다.

이 결과는 새로운 reporting framework를 입증하지 않는다. 다만 단일 metric이나 final checkpoint만으로는 recipe specialization, guardrail regression, sampling 범위가 가려질 수 있음을 보여준다. Recipe–Checkpoint Profile은 여기서 새로운 기여가 아니라 reporting implication으로 사용한다. 고정 예산, recipe, checkpoint, intended·guardrail metric, seed, pair-sampling 범위, overlap 결과를 함께 명시하는 방식이다.

## 한계

DPO training pair는 recipe별 source distribution과 prompt를 서로 일치시키지 않았다. Call-decision 중심 recipe에서는 When2Call 계열의 data source와 evaluation family가 분리되지 않는다. 따라서 evaluation-axis pattern은 negative failure type 자체의 인과 효과나 어느 데이터 소스의 quality가 더 높은지를 보여 주는 결과가 아니라 고정 예산 recipe 비교다.

고정 예산 조건에도 한계가 있다. Pair 수, optimizer step, DPO recipe, reference checkpoint는 고정했지만 token 수와 source distribution은 동일하지 않았다. 모든 DPO 결과는 하나의 Qwen3-8B SFT reference, 하나의 QLoRA DPO recipe, 하나의 pair/step 예산에서 나왔다 <a class="citation-ref" href="#ref-lora" aria-label="참고문헌 7">[7]</a> <a class="citation-ref" href="#ref-qlora" aria-label="참고문헌 8">[8]</a>. Mixed-source condition도 자체 seed 또는 reconstructed-pool replicate가 없는 단일 run이다.

IFEval slice는 guardrail diagnostic으로 해석해야 한다. Bootstrap interval은 평가 표본의 불확실성을 다루지만, training stochasticity, data sampling, benchmark construction에서 오는 모든 불확실성을 포함하지는 않는다.

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
Ilho Ahn, "전문화된 Tool-Use DPO Recipe의 고정 예산 비교", Mini Research, June 27, 2026.
```

BibTeX:

```bibtex
@article{ahn2026toolusedporeportingprofile,
  author = {Ilho Ahn},
  title = {전문화된 Tool-Use DPO Recipe의 고정 예산 비교},
  journal = {Mini Research},
  year = {2026},
  month = jun,
  url = {https://muted-color.github.io/research/2026/06/27/tool-use-dpo-fixed-budget-reporting-profile/ko/}
}
```
