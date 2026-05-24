---
title: "Carbon-3B: 6-mer token phase sensitivity 측정"
date: 2026-05-23 16:50:00 +0900
last_modified_at: 2026-05-24 21:49:23 +0900
categories: ["BIO ML"]
tags: [carbon-3b, dna-foundation-model, brca2, variant-effect-prediction, tokenization, phase-sensitivity, fns]
lab_path: "experiment-lab/projects/carbon-6mer-phase-sensitivity"
excerpt: "Carbon-3B로 BRCA2 MVE SNV를 점수화할 때 6-mer token phase가 score IQR 대비 얼마나 흔드는지, FNS가 그 흔들림을 얼마나 줄이는지 점검한 노트."
description: "Carbon-3B BRCA2 MVE 500개 SNV에서 6-mer token phase가 token-level score를 score IQR 대비 크게 흔들었고, FNS는 대응 비교에서 phase range를 줄였지만 남는 phase sensitivity가 있었다."
permalink: /research/2026/05/23/carbon-6mer-phase-sensitivity/
image: /assets/images/posts/carbon-6mer-phase-sensitivity/social-thumbnail.png
image_alt: "Carbon-3B score 조건별 6-mer phase sensitivity를 비교하고 0.10 보조 기준선을 표시한 막대 차트"
hero_image: /assets/images/posts/carbon-6mer-phase-sensitivity/phase-instability-by-scorer.svg
hero_alt: "전체 sequence FNS, variant 위치 주변 FNS, downstream token, 전체 window token, variant 포함 token 조건의 정규화 phase range를 비교한 막대 차트"
hero_caption: "<strong>Figure 1.</strong> BRCA2 MVE 500개 SNV에서 score 조건별 median phase range를 각 조건의 score IQR로 나눈 값이다. 점선은 score IQR의 10%에 해당하는 0.10 보조 기준선이다. Paired 기준에서 FNS 조건은 대응하는 token 조건보다 낮았지만, 두 FNS 조건도 기준선을 넘었다."
hero_frame: true
hero_compact: true
---

Carbon-3B는 DNA를 non-overlapping 6-mer token으로 읽는 autoregressive genomic foundation model이다 <a class="citation-ref" href="#ref-carbon-3b" aria-label="Reference 1">[1]</a>. 이 구조에서는 같은 SNV(single-nucleotide variant)라도 window start를 몇 bp 옮기느냐에 따라 variant base가 6-mer token 안의 서로 다른 위치에 들어간다. 이 글은 그 phase 선택이 Carbon variant score를 얼마나 흔드는지 평가한다.

평가 질문은 Carbon VEP(variant effect prediction) 전체 성능이 아니라 score 계산 절차의 안정성이다. 같은 biological SNV를 거의 같은 BRCA2 genomic context 안에 두고, 6가지 6-mer phase가 reference score에서 alternative score를 뺀 값에 남기는 변동폭을 측정한다. 이어서 Carbon의 FNS base-level scoring이 그 변동을 줄이는지 확인한다.

핵심 관찰은 token score의 정규화 phase range가 0.10 보조 기준선을 크게 넘었고, FNS가 이 range를 줄였지만 제거하지는 못했다는 점이다.

> **Carbon-3B**는 Hugging Face Biology Research가 공개한 3B parameter DNA/RNA autoregressive model이다. DNA 입력에서는 `<dna>` tag 뒤 sequence가 6-mer token 단위로 묶인다.
>
> **6-mer phase**는 variant base가 6bp token 안에서 차지하는 offset이다. 이 글에서는 같은 SNV를 6가지 phase에 놓아 score range를 계산했다.
>
> **MVE**는 multiplexed variant effect를 뜻한다. 이 글의 BRCA2 MVE는 여러 BRCA2 variant의 functional effect label을 제공하는 평가 리소스다.
>
> **FNS**는 Factorised Nucleotide Supervision이다. Carbon model card는 Carbon training이 Cross-Entropy 단계 뒤 FNS objective 단계로 이어졌다고 설명한다 <a class="citation-ref" href="#ref-carbon-3b" aria-label="Reference 1">[1]</a>. 이 글에서는 Carbon이 제공하는 FNS base-level scoring을 token-level scoring과 비교한다.

{% include model-mention-cards.html label="사용한 주요 리소스" aria_label="Carbon과 BRCA2 평가 리소스" models="Carbon-3B|HuggingFaceBio/Carbon-3B|https://huggingface.co/HuggingFaceBio/Carbon-3B;Carbon evaluation README|huggingface/carbon evaluation|https://github.com/huggingface/carbon/blob/main/evaluation/README.md;BRCA2 MVE|Huang et al. Nature 2025|https://doi.org/10.1038/s41586-024-08388-8" %}

## 요약

- BRCA2 MVE 500개 SNV를 대상으로 Carbon-3B token-level scoring의 6-mer phase sensitivity를 평가했다. Label 구성은 LOF(loss-of-function) 85개, FUNC(functional)/INT(intermediate) 415개다.
- Token score의 score IQR(interquartile range) 정규화 phase range는 Full-window 0.409, Target-token 0.349, Downstream-only 0.466이었다. 세 값 모두 score IQR의 10%에 해당하는 0.10 보조 기준선을 넘었다.
- FNS scoring은 paired 정규화 phase range를 줄였다. Full-sequence FNS는 0.353, Local-target FNS는 0.331이었다.
- FNS mitigation의 median token-minus-FNS 정규화 차이는 full-sequence 비교에서 0.0544, local-target 비교에서 0.0198이었다. 95% CI(confidence interval)는 각각 0.0362-0.0709, 0.0118-0.0294였다.
- FNS는 phase range를 줄이는 완화 효과를 보였다. 동시에 두 FNS 조건도 score IQR 정규화 phase range가 0.10을 넘어, phase에 무관한 점수 기준으로 보기는 어렵다.
- 8,190 bp clean-window protocol은 partial-token tail을 만들지 않았다. Full-window 결과에는 window edge/context 변화도 들어갈 수 있으므로, local token boundary 효과는 target-token 결과와 함께 읽었다.

## 평가 설정

데이터는 Huang et al. BRCA2 functional evaluation resource를 hg19 chr13 reference와 맞춰 다시 구성한 SNV subset이다 <a class="citation-ref" href="#ref-huang-brca2" aria-label="Reference 3">[3]</a> <a class="citation-ref" href="#ref-brca2-source-table" aria-label="Reference 4">[4]</a> <a class="citation-ref" href="#ref-ucsc-hg19-chr13" aria-label="Reference 5">[5]</a>. 원자료 전체에서 ref allele match와 SNV 조건을 통과한 6,836개 중, label 구성이 유지되는 500개 MVE subset을 사용했다.

주 window는 8,190 bp다. 이 길이는 6으로 나누어 떨어지므로 Carbon tokenizer에서 tail padding을 만들지 않는다. Carbon BRCA2 평가와 맞춘 8,192 bp window도 따로 확인했고 <a class="citation-ref" href="#ref-carbon-eval" aria-label="Reference 2">[2]</a> <a class="citation-ref" href="#ref-carbon-brca2-prep" aria-label="Reference 6">[6]</a>, 주 phase score 결론에는 섞지 않았다.

<aside class="model-flow" aria-label="평가 흐름" markdown="1">
  <p class="metric-detail__eyebrow">평가 흐름</p>
<pre class="model-flow__diagram"><code>BRCA2 SNV
  -> 6가지 8,190 bp phase window
  -> reference / alternative sequence pair
  -> token score: Full-window, Target-token, Downstream-only
  -> FNS score: Full-sequence, Local-target
  -> variant별 phase range와 정규화 phase range</code></pre>
</aside>

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>항목</th>
          <th>고정한 값</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>모델</td>
          <td><code>HuggingFaceBio/Carbon-3B</code></td>
        </tr>
        <tr>
          <td>주 데이터</td>
          <td>BRCA2 MVE 500개 SNV<br><span class="table-note-inline">LOF 85, FUNC/INT 415</span></td>
        </tr>
        <tr>
          <td>주 window</td>
          <td><code>8,190 bp</code><br><span class="table-note-inline">6-mer clean window, partial token tail 없음</span></td>
        </tr>
        <tr>
          <td>주 score</td>
          <td>reference score에서 alternative score를 뺀 값</td>
        </tr>
        <tr>
          <td>보조 기준선</td>
          <td>median phase range / score IQR &ge; <code>0.10</code><br><span class="table-note-inline">score IQR의 10%를 scale-normalized effect-size 기준으로 사용</span></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> 평가 범위다. 이 글은 BRCA2 MVE subset에서 score 계산 절차의 phase sensitivity를 점검한다. Carbon VEP 전체 성능 평가는 별도 평가 문제로 둔다.</figcaption>
</figure>

Score scale은 계산 방식마다 다르다. Token score 조건은 score를 모으는 범위로 구분했다.

- **Full-window**는 8,190 bp window 전체의 valid DNA token에서 평균 log probability score를 계산한다.
- **Target-token**은 variant를 포함하는 단일 6-mer token만 score에 사용한다.
- **Downstream-only**는 variant 이후에 오는 token들만 score에 사용한다. Autoregressive model에서 variant context가 뒤쪽 token 예측에 남기는 변화를 보기 위한 조건이다.

FNS full-sequence와 FNS local-target score도 raw scale이 token score와 같지 않다. 따라서 서로 다른 계산 방식의 raw range를 직접 비교하지 않고, 각 score의 IQR로 나눈 정규화 phase range를 사용했다.

0.10 보조 기준선은 실험 설계 단계에서 score IQR의 10%로 미리 둔 effect-size 기준이다. Score 조건별 scale이 다르기 때문에 raw range 대신 이 기준으로 phase range의 상대적 크기를 비교했다.

## 결과

주 결과는 token score의 phase sensitivity와 FNS의 완화 효과다. Padding과 window edge 조건은 phase score의 해석 범위를 정하고, label 지표는 score가 BRCA2 MVE label 방향성과 연결되는지 확인하는 보조 결과다.

### Token phase 민감도

가장 직접적인 관찰은 token-level score가 phase 선택에 크게 흔들렸다는 점이다. BRCA2 MVE 500개 SNV에서 full-window token score의 정규화 phase range는 0.409였다. 같은 기준에서 target-token score는 0.349, downstream-only score는 0.466이었다. 모두 0.10 보조 기준선보다 충분히 크다.

Figure 1은 이 값을 score 조건별로 압축해 보여준다. Token score 세 조건은 모두 기준선 위에 있었다. FNS 조건은 paired 기준에서 대응하는 token score보다 낮은 값을 보였고, 동시에 기준선 위에 남았다.

Target-token raw range는 token 하나의 log-probability 차이에서 나오기 때문에 full-window raw range와 직접 비교하지 않는다. 여기서 중요한 값은 같은 score 조건 안에서 phase range가 score IQR 대비 얼마나 큰지다. 이 기준에서는 target token만 문제가 아니라 full-window와 downstream score도 phase-sensitive하다.

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Token score 조건</th>
          <th class="align-right">Median phase range</th>
          <th class="align-right">P90 phase range</th>
          <th class="align-right">Range / score IQR</th>
          <th class="align-right">Variants over 0.10 보조 기준선</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Full-window</td>
          <td class="align-right"><code>0.00634</code></td>
          <td class="align-right"><code>0.01801</code></td>
          <td class="align-right"><code>0.409</code></td>
          <td class="align-right"><code>99.6%</code></td>
        </tr>
        <tr>
          <td>Target-token</td>
          <td class="align-right"><code>1.87500</code></td>
          <td class="align-right"><code>4.12500</code></td>
          <td class="align-right"><code>0.349</code></td>
          <td class="align-right"><code>93.6%</code></td>
        </tr>
        <tr>
          <td>Downstream-only</td>
          <td class="align-right"><code>0.01206</code></td>
          <td class="align-right"><code>0.03633</code></td>
          <td class="align-right"><code>0.466</code></td>
          <td class="align-right"><code>100.0%</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> Token score 조건별 phase sensitivity다. Raw phase range는 score scale이 다르므로, 주 비교 값은 score IQR로 나눈 정규화 phase range다.</figcaption>
</figure>

Figure 2는 이 관찰이 일부 variant의 outlier 현상인지, 대부분의 variant에 걸친 현상인지 확인하기 위한 그림이다. Phase별 방향성을 보여주는 그림이 아니라, variant별 phase sensitivity의 크기를 보여준다. 여기서 y값은 한 variant의 6개 phase score가 만드는 최대-최소 차이를 full-window score IQR로 나눈 값이다. Median은 0.41, p90은 1.16이었고, 500개 중 498개 variant가 0.10 보조 기준선 이상이었다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/carbon-6mer-phase-sensitivity/full-window-phase-range-distribution.svg" alt="Full-window token score에서 variant별 six-phase range를 score IQR로 나눈 값의 ranked distribution">
  <figcaption><strong>Figure 2.</strong> 각 점은 하나의 variant다. y값은 그 variant가 6가지 phase에서 얼마나 크게 흔들렸는지를 나타내며, log scale로 표시했다. x축은 흔들림이 작은 variant부터 큰 variant까지 정렬한 순서다. 점선은 0.10 보조 기준선이며, 498/500개 variant가 기준선 이상이었다.</figcaption>
</figure>

이 관찰을 기준으로 Carbon이 제공하는 FNS base-level scoring의 완화 효과를 따로 측정했다.

### FNS 완화 효과

Paired comparison에서는 FNS가 token score보다 낮은 정규화 phase range를 보였다. Full-sequence FNS는 full-window token score의 0.409보다 낮은 0.353이었다. Local-target FNS는 target-token score의 0.349보다 낮은 0.331이었다. 두 FNS 값 모두 0.10 보조 기준선을 넘는다.

Figure 3은 두 paired comparison을 같은 scale에 놓는다. 두 비교 모두에서 FNS bar는 낮아졌고, 낮아진 뒤에도 0.10 보조 기준선 위에 남았다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/carbon-6mer-phase-sensitivity/fns-mitigation-normalized-range.svg" alt="Token score와 FNS score의 정규화 phase range를 full-sequence와 local-target 비교 쌍별로 나타낸 막대 차트">
  <figcaption><strong>Figure 3.</strong> FNS와 token score의 paired 정규화 phase range 비교다. FNS는 두 비교 쌍에서 token보다 낮았지만, 남는 range가 0.10 보조 기준선보다 컸다. 차이, CI, p값은 아래 표에 분리했다.</figcaption>
</figure>

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>비교</th>
          <th class="align-right">Token range / IQR</th>
          <th class="align-right">FNS range / IQR</th>
          <th class="align-right">Token - FNS</th>
          <th class="align-right">95% CI</th>
          <th class="align-right">FNS lower variants</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Full-sequence<br><span class="table-note-inline">FNS vs token</span></td>
          <td class="align-right"><code>0.409</code></td>
          <td class="align-right"><code>0.353</code></td>
          <td class="align-right"><code>0.0544</code></td>
          <td class="align-right"><code>0.0362-0.0709</code></td>
          <td class="align-right"><code>64%</code></td>
        </tr>
        <tr>
          <td>Local-target<br><span class="table-note-inline">FNS vs token</span></td>
          <td class="align-right"><code>0.349</code></td>
          <td class="align-right"><code>0.331</code></td>
          <td class="align-right"><code>0.0198</code></td>
          <td class="align-right"><code>0.0118-0.0294</code></td>
          <td class="align-right"><code>58%</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> FNS 완화 효과 점검이다. <code>Token - FNS</code>는 표에 보이는 두 median의 차이가 아니라 variant별 paired 정규화 차이의 median이다. <code>FNS lower variants</code>는 paired variant 중 FNS 정규화 phase range가 token 정규화 phase range보다 낮은 비율이다. CI는 10,000-repeat variant bootstrap으로 계산했다.</figcaption>
</figure>

이 결과는 FNS가 phase range를 줄인다는 결론을 지지한다. 동시에 실제 점수 계산 절차 관점에서는 남는 range가 여전히 크다. 따라서 FNS의 역할은 phase에 무관한 점수 기준이 아니라, phase range를 줄이는 보정 기준으로 정리된다. 남는 range를 해석하려면 window 길이와 edge context가 만드는 조건도 함께 확인해야 한다.

### Padding과 window edge

이 절은 phase effect의 해석 범위를 정리한다. Padding 점검은 8,190 bp와 8,192 bp window를 같은 score 조건으로 섞을 수 있는지 확인하고, edge 대조는 full-window score에 window 양끝 context 변화가 얼마나 들어올 수 있는지 본다.

먼저 window 길이다. 8,190 bp는 6으로 나누어 떨어지므로 Carbon의 6-mer tokenizer에서 partial-token tail이 없다. 반면 Carbon BRCA2 평가와 맞춘 8,192 bp window는 length 2 tail을 만든다. 따라서 이 글의 주 phase score는 8,190 bp clean-window 조건으로 해석하고, 8,192 bp 조건은 호환성 점검으로 분리했다.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>점검 항목</th>
          <th>조건</th>
          <th class="align-right">관찰</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Clean window</td>
          <td><code>8,190 bp</code></td>
          <td class="align-right"><code>0/3,000</code> partial-token tails</td>
        </tr>
        <tr>
          <td>Carbon BRCA2 호환 window</td>
          <td><code>8,192 bp</code></td>
          <td class="align-right"><code>3,000/3,000</code> length 2 tails</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> Padding 점검 요약이다. 8,190 bp는 partial-token tail이 없는 주 분석 조건이고, 8,192 bp는 Carbon BRCA2 호환성 확인용 조건이다.</figcaption>
</figure>

다음은 window edge다. Six-phase windows는 variant 근처 context를 거의 유지하지만, window start를 옮기는 만큼 양끝 bases는 바뀐다. 그래서 full-window score의 phase range에는 variant의 token 위치 효과와 window edge/context 변화가 함께 들어갈 수 있다.

이를 보기 위해 alternate allele을 넣지 않은 reference window만 phase처럼 옮겨 edge-only range를 계산했다. Variant별 edge-only/full-window phase range ratio의 median은 4.162였다.

Figure 4는 이 edge-only range의 분포다. 이 결과는 full-window phase range를 local token boundary 효과만으로 읽으면 안 된다는 점을 보여준다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/carbon-6mer-phase-sensitivity/edge-context-control.svg" alt="Shifted-reference edge-only 대조에서 variant별 edge-only range 분포를 보여주는 histogram">
  <figcaption><strong>Figure 4.</strong> Shifted-reference edge-only range 분포다. x축은 edge-only range, y축은 variant count다. Variant별 edge-only/full-window phase range ratio의 median은 4.162였고, full-window phase range에는 window edge/context 변화도 함께 들어올 수 있다.</figcaption>
</figure>

이 결과 때문에 target-token과 full-window는 따로 읽어야 한다. Target-token 결과는 variant가 들어간 6-mer token 자체가 phase-sensitive하다는 신호이고, full-window 결과는 그 local 효과에 window edge/context 변화가 더해진 score다.

### Label 구분 신호

여기까지의 결과는 score 계산 절차가 phase에 민감하다는 점을 보여준다. 남는 질문은 phase-sensitive한 score가 BRCA2 MVE label 방향성과도 연결되어 있는지다. 이를 확인하기 위해 LOF를 positive class로 두고, Carbon score가 LOF variant와 FUNC/INT variant를 구분할 수 있는지를 AUROC로 측정했다.

BRCA2 MVE 500개 SNV에서 full-window token과 full-sequence FNS의 6개 phase 평균 AUROC(area under the receiver operating characteristic curve)는 세 자리 반올림 기준으로 모두 0.913이었다. 이 값은 label을 섞어 만든 shuffled-label control보다 높았다. 따라서 보조 지표상 phase-sensitive score에도 BRCA2 MVE label signal이 남아 있었다.

Table 5는 이 보조 지표를 score 조건별로 정리한다. 여기서는 AUROC를 성능 순위가 아니라, phase-sensitive score에도 label 방향성이 남아 있는지 확인하는 값으로 사용한다.

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Score</th>
          <th class="align-right">Observed AUROC</th>
          <th class="align-right">Shuffled null p95</th>
          <th>해석</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Full-window token<br><span class="table-note-inline">6개 phase 평균</span></td>
          <td class="align-right"><code>0.913</code></td>
          <td class="align-right"><code>0.553</code></td>
          <td>LOF와 FUNC/INT 구분 signal이 보인다.</td>
        </tr>
        <tr>
          <td>Full-sequence FNS<br><span class="table-note-inline">6개 phase 평균</span></td>
          <td class="align-right"><code>0.913</code></td>
          <td class="align-right"><code>0.559</code></td>
          <td>Full-window token과 거의 같은 AUROC를 보였다.</td>
        </tr>
        <tr>
          <td>Local-target FNS<br><span class="table-note-inline">6개 phase 평균</span></td>
          <td class="align-right"><code>0.760</code></td>
          <td class="align-right"><code>0.559</code></td>
          <td>Variant 주변만 보는 score라 full-sequence 조건과 역할이 다르다.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 5.</strong> Label metric은 Carbon score가 LOF와 FUNC/INT label을 구분하는지 확인하는 보조 축이다. Shuffled-label보다 높은 AUROC가 확인됐고, 이 표는 score-label 연결을 확인하기 위한 보조 표다.</figcaption>
</figure>

## 해석과 결론

앞의 결과를 합치면 결론은 두 겹이다. Carbon-3B score는 BRCA2 MVE label signal을 일부 담고 있었고, 동시에 6-mer phase 선택에 따른 score 변동도 score scale 대비 충분히 컸다. 따라서 Carbon SNV 점수 보고에서는 phase sensitivity를 함께 보고해야 한다. 단일 기준 phase score만 저장하면, 그 score가 biological allele evidence인지 임의의 6-mer 경계 선택에서 나온 차이인지 분리하기 어렵다.

현재 설정에서 적용 기준은 세 가지다.

1. Reference score에서 alternative score를 뺀 값을 보고할 때 6개 phase range 또는 불안정성 표식을 함께 둔다.
2. FNS가 가능한 환경에서는 token score와 FNS score를 paired 정규화 지표로 비교한다. FNS는 phase range를 줄이는 기준이지, phase에 무관한 기준은 아니었다.
3. 8,190 bp clean-window 점수와 8,192 bp padding 포함 호환성 점검을 같은 표에서 섞지 않는다. 8,192 bp를 쓰려면 padding tail 점검과 별도 score 절을 둔다.

가장 안정적으로 남는 결론은 단순하다. BRCA2 MVE 500개 SNV, Carbon-3B, 8,190 bp 평가 조건에서는 6-mer phase가 SNV score에서 score scale 대비 의미 있는 변동을 만들었다. FNS는 이 phase range를 줄였지만 제거하지 않았다. 따라서 이 설정의 공개 결론은 "phase-sensitive score 계산 절차와 FNS 완화 효과"로 정리된다.

## Appendix: 재현 조건과 결론 범위

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>계산 묶음</th>
          <th>역할</th>
          <th class="align-right">항목 수</th>
          <th class="align-right">소요 시간</th>
          <th class="align-right">최대 CUDA 메모리</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Token score 계산</td>
          <td>Token 기반 MVE score 계산</td>
          <td class="align-right"><code>12,000</code> 점수 계산 항목<br><span class="table-note-inline"><code>3,000</code> window 조건 점검, 오류 0건</span></td>
          <td class="align-right"><code>1,192.93 s</code></td>
          <td class="align-right"><code>14.40 GB</code></td>
        </tr>
        <tr>
          <td>FNS score 계산</td>
          <td>FNS 기반 score 계산</td>
          <td class="align-right"><code>6,000</code> 점수 계산 항목<br><span class="table-note-inline"><code>6,000</code> paired 비교 항목, 오류 0건</span></td>
          <td class="align-right"><code>1,149.77 s</code></td>
          <td class="align-right"><code>8.33 GB</code></td>
        </tr>
        <tr>
          <td>보조 점검</td>
          <td>Padding, edge, ensemble 점검</td>
          <td class="align-right"><code>6,000</code> padding 점검 항목</td>
          <td class="align-right"><code>13.21 s</code></td>
          <td class="align-right">해당 없음</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 1.</strong> 계산별 재현 조건 요약이다. 세부 재현 정보와 결과 파일 대조는 별도 재현 기록에 보존했다.</figcaption>
</figure>

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>결론 항목</th>
          <th>상태</th>
          <th>주의점</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Token-level phase 불안정성</td>
          <td>지지됨</td>
          <td>BRCA2 MVE와 8,190 bp 평가 조건에서 확인됐다.</td>
        </tr>
        <tr>
          <td>FNS 점수 계산 동작</td>
          <td>지지됨</td>
          <td>FNS score는 token score와 scale이 다르다.</td>
        </tr>
        <tr>
          <td>FNS 완화 효과</td>
          <td>지지됨</td>
          <td>완화 뒤에도 phase range가 0.10 보조 기준선을 넘는다.</td>
        </tr>
        <tr>
          <td>FNS phase 불변성</td>
          <td>지지되지 않음</td>
          <td>FNS는 불변성보다 완화 효과로 해석한다.</td>
        </tr>
        <tr>
          <td>Carbon VEP 전체 성능</td>
          <td>별도 평가</td>
          <td>외부 평가와 단순 sequence/position 기준선이 필요한 별도 문제다.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 2.</strong> 결론 범위 요약이다. 이 글은 Carbon-3B score 계산 절차의 phase sensitivity와 FNS 완화 효과를 결론으로 둔다.</figcaption>
</figure>

## References

<div class="reference-list" markdown="1">

<ol>
  <li id="ref-carbon-3b">Hugging Face Biology Research. <strong>Carbon-3B model card and FNS model revision</strong>. Hugging Face, 2026. <a href="https://huggingface.co/HuggingFaceBio/Carbon-3B">HuggingFaceBio/Carbon-3B</a>. Technical report: <a href="https://github.com/huggingface/carbon/blob/main/tech-report.pdf">Carbon technical report</a>. Accessed 2026-05-24.</li>
  <li id="ref-carbon-eval">Hugging Face Biology Research. <strong>Carbon evaluation README</strong>. GitHub, 2026. <a href="https://github.com/huggingface/carbon/blob/main/evaluation/README.md">huggingface/carbon evaluation</a>. Accessed 2026-05-24.</li>
  <li id="ref-huang-brca2">Huang, H., Hu, C., Na, J. et al. <strong>Functional evaluation and clinical classification of BRCA2 variants</strong>. <em>Nature</em> 638, 528-537, 2025. DOI: <a href="https://doi.org/10.1038/s41586-024-08388-8">10.1038/s41586-024-08388-8</a></li>
  <li id="ref-brca2-source-table">Huang et al. <strong>Functional evaluation and clinical classification of BRCA2 variants</strong>, Supplementary Table 3. Nature/Springer, 2025. <a href="https://static-content.springer.com/esm/art%3A10.1038%2Fs41586-024-08388-8/MediaObjects/41586_2024_8388_MOESM3_ESM.xlsx">Supplementary Table S3 XLSX</a></li>
  <li id="ref-ucsc-hg19-chr13">UCSC Genome Browser. <strong>hg19/GRCh37 chr13 chromosome FASTA, goldenPath</strong>. <a href="https://hgdownload.soe.ucsc.edu/goldenPath/hg19/chromosomes/chr13.fa.gz">chr13.fa.gz</a></li>
  <li id="ref-carbon-brca2-prep">Hugging Face Biology Research. <strong>Carbon BRCA2 data preparation script</strong>. <a href="https://raw.githubusercontent.com/huggingface/carbon/main/evaluation/data_prep/prep_brca2.py">prep_brca2.py</a>. Accessed 2026-05-24.</li>
</ol>

계산 요약은 Appendix Table 1에 정리했다. 세부 재현 정보는 front matter의 <code>lab_path</code>가 가리키는 실험 기록에 보존했다.

</div>

## Citation

Text citation:

```text
Ilho Ahn, "Carbon-3B: 6-mer token phase sensitivity 측정", Mini Research, May 23, 2026.
```

BibTeX:

```bibtex
@misc{ahn2026carbon_6mer_phase_sensitivity,
  author = {Ahn, Ilho},
  title = {Carbon-3B: {6-mer} token phase sensitivity 측정},
  year = {2026},
  month = {May},
  howpublished = {Mini Research},
  url = {https://muted-color.github.io/research/2026/05/23/carbon-6mer-phase-sensitivity/}
}
```
