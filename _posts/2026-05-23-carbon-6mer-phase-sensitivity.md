---
title: "Carbon-3B: 6-mer token phase sensitivity 측정"
date: 2026-05-23 16:50:00 +0900
last_modified_at: 2026-07-30 21:33:40 +0900
categories: ["BIO ML"]
tags: [carbon-3b, dna-foundation-model, brca2, variant-effect-prediction, tokenization, phase-sensitivity, fns]
lab_path: "experiment-lab/projects/carbon-6mer-phase-sensitivity"
excerpt: "Carbon-3B로 BRCA2 MAVE의 500개 SNV subset을 점수화할 때 6-mer token phase가 score IQR 대비 얼마나 흔드는지, FNS pipeline에서는 어떤 차이가 나타나는지 점검한 노트."
description: "Carbon-3B BRCA2 MAVE의 500개 SNV subset에서 6-mer token phase range가 사전 0.10 기준을 넘었고, FNS pipeline에서는 대응 token 조건보다 낮은 range가 관찰됐다."
permalink: /research/2026/05/23/carbon-6mer-phase-sensitivity/
image: /assets/images/posts/carbon-6mer-phase-sensitivity/social-thumbnail.png
image_alt: "Carbon-3B score 조건별 6-mer phase sensitivity를 비교하고 사전 0.10 보조 기준선을 표시한 막대 차트"
hero_image: /assets/images/posts/carbon-6mer-phase-sensitivity/phase-instability-by-scorer.svg
hero_alt: "전체 sequence FNS, variant 위치 주변 FNS, downstream token, 전체 window token, variant 포함 token 조건의 정규화 phase range를 비교한 막대 차트"
hero_caption: "<strong>Figure 1.</strong> BRCA2 MAVE에서 추출한 500개 SNV subset의 score 조건별 정규화 phase range다. 점선은 사전 0.10 보조 기준선이다. 세 token 조건은 모두 기준선을 넘었고, 두 FNS 조건은 대응 token 조건보다 낮았지만 기준선 위에 남았다."
hero_frame: true
hero_compact: true
hero_variant: featured-plot
---

Carbon-3B는 DNA를 non-overlapping 6-mer token으로 읽는 autoregressive genomic foundation model이다 <a class="citation-ref" href="#ref-carbon-paper" aria-label="Reference 1">[1]</a> <a class="citation-ref" href="#ref-carbon-3b" aria-label="Reference 2">[2]</a>. 이 구조에서는 같은 SNV(single-nucleotide variant)라도 window start를 몇 bp 옮기느냐에 따라 variant base가 6-mer token 안의 서로 다른 위치에 들어간다. 이 글은 그 phase 선택이 Carbon variant score를 얼마나 흔드는지 평가한다.

평가 질문은 Carbon VEP(variant effect prediction) 전체 성능이 아니라 score 계산 절차의 안정성이다. 같은 biological SNV를 거의 같은 BRCA2 genomic context 안에 두고, 6가지 6-mer phase가 reference score에서 alternative score를 뺀 값에 남기는 변동폭을 측정한다. 이어서 Carbon의 FNS base-level scoring 조건에서 대응 token 조건보다 낮은 변동폭이 나타나는지 확인한다.

핵심 관찰은 token score의 정규화 phase range가 0.10 보조 기준선을 넘었고, 이 민감도가 일부 outlier가 아니라 대부분의 variant에서 나타났다는 점이다. FNS pipeline의 대응 비교에서는 더 낮은 range가 관찰됐지만 차이는 제한적이었다.

> **Carbon-3B**는 Hugging Face Biology Research가 공개한 3B parameter DNA/RNA autoregressive model이다. DNA 입력에서는 `<dna>` tag 뒤 sequence가 6-mer token 단위로 묶인다.
>
> **6-mer phase**는 variant base가 6bp token 안에서 차지하는 offset이다. 이 글에서는 같은 SNV를 6가지 phase에 놓아 score range를 계산했다.
>
> **MAVE**는 multiplexed assay of variant effect를 뜻한다. Huang et al.의 BRCA2 자료는 여러 variant의 functional effect를 병렬로 측정한 평가 리소스다.
>
> **FNS**는 Factorised Nucleotide Supervision이다. Carbon paper와 model card는 Carbon training이 Cross-Entropy 단계 뒤 FNS objective 단계로 이어졌다고 설명한다 <a class="citation-ref" href="#ref-carbon-paper" aria-label="Reference 1">[1]</a> <a class="citation-ref" href="#ref-carbon-3b" aria-label="Reference 2">[2]</a>. 이 글에서는 Carbon이 제공하는 FNS base-level scoring을 token-level scoring과 비교한다.

{% include model-mention-cards.html label="사용한 주요 리소스" aria_label="Carbon과 BRCA2 평가 리소스" models="Carbon-3B|HuggingFaceBio/Carbon-3B|https://huggingface.co/HuggingFaceBio/Carbon-3B;Carbon evaluation README|huggingface/carbon evaluation|https://github.com/huggingface/carbon/blob/main/evaluation/README.md;BRCA2 MAVE|Huang et al. Nature 2025|https://doi.org/10.1038/s41586-024-08388-8" %}

## 요약

- BRCA2 MAVE에서 추출한 500개 SNV subset을 대상으로 Carbon-3B score 계산의 6-mer phase sensitivity를 평가했다. Label 구성은 LOF(loss-of-function) 85개, FUNC(functional)/INT(intermediate) 415개다.
- Token score의 score IQR(interquartile range) 정규화 phase range는 Full-window 0.409, Target-token 0.349, Downstream-only 0.466이었다. 세 조건에서 variant의 93.6–100%가 사전 0.10 보조 기준 이상이었다.
- Target-token 결과는 variant를 포함한 token scoring이 six-shift protocol에 민감하다는 가장 직접적인 지표다. Full-window와 Downstream-only 결과에는 전체 segmentation과 window edge/context 변화가 추가로 포함된다.
- FNS pipeline의 정규화 range는 Full-sequence에서 0.353, Local-target에서 0.331로 대응 token 조건보다 낮았다. Paired median 차이는 각각 0.0544와 0.0198이었지만, 두 FNS 조건도 0.10 기준 위에 남았다.
- Six-phase mean score는 Full-window token과 Full-sequence FNS에서 모두 0.913 AUROC를 보였다. 이는 label 구분 신호가 남아 있다는 보조 결과이며 Carbon VEP 전체 성능 평가는 아니다.

## 평가 설정

데이터는 Huang et al. BRCA2 MAVE resource를 hg19 chr13 reference와 맞춰 다시 구성한 SNV subset이다 <a class="citation-ref" href="#ref-huang-brca2" aria-label="Reference 4">[4]</a> <a class="citation-ref" href="#ref-brca2-source-table" aria-label="Reference 5">[5]</a> <a class="citation-ref" href="#ref-ucsc-hg19-chr13" aria-label="Reference 6">[6]</a>. 원자료에서 ref allele match와 SNV 조건을 통과한 6,836개 중 500개를 `seed=20260523`으로 층화 추출했다. 층화 변수는 label, functional-score quantile, genomic-position decile, reference/alternative base, genomic position modulo 6이며, 100개 protocol pilot은 이 500개 subset에 포함된다.

주 window는 8,190 bp다. 이 길이는 6으로 나누어 떨어지므로 Carbon tokenizer에서 tail padding을 만들지 않는다. Carbon BRCA2 평가와 맞춘 8,192 bp window도 따로 확인했고 <a class="citation-ref" href="#ref-carbon-eval" aria-label="Reference 3">[3]</a> <a class="citation-ref" href="#ref-carbon-brca2-prep" aria-label="Reference 7">[7]</a>, 주 phase score 결론에는 섞지 않았다.

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
          <td><code>HuggingFaceBio/Carbon-3B</code><br><span class="table-note-inline">token <code>fe755cb5</code>; FNS revision <code>bf6f6bec</code></span></td>
        </tr>
        <tr>
          <td>주 데이터</td>
          <td>BRCA2 MAVE의 500개 SNV subset<br><span class="table-note-inline">LOF 85, FUNC/INT 415; seed 20260523</span></td>
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
  <figcaption><strong>Table 1.</strong> BRCA2 MAVE의 500개 SNV subset에서 score 계산 절차의 phase sensitivity를 점검한 평가 범위다.</figcaption>
</figure>

Table 1의 범위 안에서 score scale은 계산 방식마다 다르다. Token score 조건은 score를 모으는 범위로 구분했다.

- **Full-window**는 8,190 bp window 전체의 valid DNA token에서 평균 log probability score를 계산한다.
- **Target-token**은 variant를 포함하는 단일 6-mer token만 score에 사용한다.
- **Downstream-only**는 variant 이후에 오는 token들만 score에 사용한다. Autoregressive model에서 variant context가 뒤쪽 token 예측에 남기는 변화를 보기 위한 조건이다.

FNS Full-sequence와 FNS Local-target score도 raw scale이 token score와 같지 않다. 따라서 서로 다른 계산 방식의 raw range를 직접 비교하지 않고, scorer별 정규화 phase range를 사용했다. 각 variant의 분자는 6개 phase score의 최댓값과 최솟값 차이다. 분모는 같은 scorer의 500 variants × 6 phases 전체 `score_ref_minus_alt`에서 계산한 하나의 IQR이다. Table과 Figure의 대표값은 이 variant별 정규화 range 500개의 median이다.

0.10 보조 기준선은 실험 설계 단계에서 score IQR의 10%로 미리 둔 effect-size 기준이다. Score 조건별 scale이 다르기 때문에 raw range 대신 이 기준으로 phase range의 상대적 크기를 비교했다.

## 결과

주 결과는 token score의 phase sensitivity다. Padding과 shifted-reference control로 Full-window 결과의 해석 범위를 먼저 정한 뒤 FNS pipeline의 paired 차이를 비교하고, 마지막으로 label 방향성이 남아 있는지 보조 지표로 확인한다.

### Token phase 민감도

BRCA2 500개 SNV subset에서 token-level score의 정규화 phase range는 Full-window 0.409, Target-token 0.349, Downstream-only 0.466이었다. 세 값은 사전 0.10 보조 기준의 3.5–4.7배였고, 각 조건에서 variant의 93.6–100%가 기준 이상이었다. 현재 subset에서 phase sensitivity는 일부 outlier가 아니라 분포 전반에 나타난 현상이었다.

Figure 1은 이 값을 score 조건별로 압축해 보여준다. Token score 세 조건은 모두 기준선 위에 있었다. FNS 조건은 paired 기준에서 대응하는 token score보다 낮은 값을 보였고, 동시에 기준선 위에 남았다.

Target-token은 variant를 포함하는 단일 6-mer token의 log-probability 차이에서 나오므로, target-token scoring의 six-shift 민감도를 보여주는 가장 직접적인 지표다. Full-window와 Downstream-only의 raw range는 scale이 달라 직접 비교하지 않으며, 정규화 기준에서는 세 token 조건 모두 phase-sensitive했다.

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Token score 조건</th>
          <th class="align-right">Median phase range</th>
          <th class="align-right">P90 phase range</th>
          <th class="align-right">Median range / score IQR</th>
          <th class="align-right">Variants at or above 0.10</th>
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
  <figcaption><strong>Table 2.</strong> Token score 조건별 phase sensitivity다. Raw phase range는 score scale이 다르므로, 주 비교 값은 scorer별 전체 score IQR로 나눈 variant-level phase range의 median이다.</figcaption>
</figure>

Table 2의 분포를 variant 단위로 펼친 Figure 2는 이 관찰이 일부 variant의 outlier 현상인지, 대부분의 variant에 걸친 현상인지 확인하기 위한 그림이다. Phase별 방향성을 보여주는 그림이 아니라, variant별 phase sensitivity의 크기를 보여준다. 여기서 y값은 한 variant의 6개 phase score가 만드는 최대-최소 차이를 Full-window score IQR로 나눈 값이다. Median은 0.41, p90은 1.16이었고, 500개 중 498개 variant가 0.10 보조 기준선 이상이었다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/carbon-6mer-phase-sensitivity/full-window-phase-range-distribution.svg" alt="Full-window token score에서 variant별 six-phase range를 score IQR로 나눈 값의 ranked distribution">
  <figcaption><strong>Figure 2.</strong> 각 점은 하나의 variant다. y값은 그 variant의 6가지 phase score range를 나타내며, log scale로 표시했다. x축은 range가 작은 variant부터 큰 variant까지 정렬한 순서다. 점선은 0.10 보조 기준선이며, 498/500개 variant가 기준선 이상이었다.</figcaption>
</figure>

### Padding과 shifted-reference control

이 절은 Full-window phase range의 해석 범위를 정리한다. 먼저 8,190 bp와 8,192 bp window의 padding 조건을 분리하고, 이어서 window 이동 자체가 reference full-window likelihood에 남기는 변화를 확인한다.

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
  <figcaption><strong>Table 3.</strong> Padding 점검 요약이다. 8,190 bp는 partial-token tail이 없는 주 분석 조건이고, 8,192 bp는 Carbon BRCA2 호환성 확인용 조건이다.</figcaption>
</figure>

Table 3처럼 padding 조건을 분리한 뒤에도 six-phase windows는 양끝 bases와 전체 6-mer segmentation을 함께 바꾼다. 따라서 Full-window range를 순수한 local token-boundary 효과로 귀속할 수 없다.

이를 보기 위해 alternate allele을 넣지 않은 reference window를 같은 six-shift protocol로 옮겨 shifted-reference control range를 계산했다. 이 control range를 ref-minus-alt Full-window phase range로 나눈 진단 비율의 median은 4.162였고, 500개 중 93.6%에서 control range가 Full-window phase range 이상이었다. 분자와 분모의 score 의미가 다르므로 이 비율은 edge 기여율이 아니다.

Figure 3은 shifted-reference control range의 분포다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/carbon-6mer-phase-sensitivity/edge-context-control.svg" alt="Shifted-reference control에서 variant별 reference-score range 분포를 보여주는 histogram">
  <figcaption><strong>Figure 3.</strong> Shifted-reference control range 분포다. x축은 reference full-window likelihood의 six-shift range, y축은 variant count다. 이 control range가 ref-minus-alt Full-window phase range 이상인 variant는 93.6%였고, 두 range의 진단 비율 median은 4.162였다.</figcaption>
</figure>

이 결과 때문에 Target-token과 Full-window는 따로 읽어야 한다. Target-token 결과는 variant를 포함한 token score가 six-shift protocol에 민감하다는 신호다. Full-window 결과는 local tokenization, 전체 segmentation, window edge/context 변화를 분리하지 않은 protocol-level score다.

### FNS pipeline의 paired 차이

이 해석 범위 안에서 FNS base-level scoring 조건을 대응 token 조건과 비교했다. FNS Full-sequence의 정규화 phase range는 token Full-window의 0.409보다 낮은 0.353이었고, FNS Local-target은 token Target-token의 0.349보다 낮은 0.331이었다. 두 FNS 값도 0.10 보조 기준선을 넘었다.

Figure 4는 두 paired comparison을 같은 scale에 놓는다. FNS 조건의 range는 두 비교에서 모두 낮았고, 두 FNS 값도 0.10 기준선 위에 남았다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/carbon-6mer-phase-sensitivity/fns-mitigation-normalized-range.svg" alt="Token score와 FNS score의 정규화 phase range를 full-sequence와 local-target 비교 쌍별로 나타낸 막대 차트">
  <figcaption><strong>Figure 4.</strong> FNS와 token score의 paired 정규화 phase range 비교다. FNS 조건은 두 비교 쌍에서 더 낮았지만, 두 값 모두 0.10 보조 기준선보다 컸다. Variant-level paired 차이와 bootstrap CI는 Table 4에 분리했다.</figcaption>
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
          <td class="align-right"><code>[0.0362, 0.0709]</code></td>
          <td class="align-right"><code>64%</code></td>
        </tr>
        <tr>
          <td>Local-target<br><span class="table-note-inline">FNS vs token</span></td>
          <td class="align-right"><code>0.349</code></td>
          <td class="align-right"><code>0.331</code></td>
          <td class="align-right"><code>0.0198</code></td>
          <td class="align-right"><code>[0.0118, 0.0294]</code></td>
          <td class="align-right"><code>58%</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> FNS pipeline의 paired 정규화 range 차이다. <code>Token - FNS</code>는 표에 보이는 두 median의 차이가 아니라 variant별 paired 정규화 차이의 median이다. <code>FNS lower variants</code>는 paired variant 중 FNS가 낮은 비율이다. CI는 고정된 scorer별 IQR 분모를 사용해 paired delta를 계산한 뒤, seed <code>20260523</code>으로 10,000회 variant bootstrap한 post-hoc audit 결과다.</figcaption>
</figure>

Token과 FNS revision은 같은 safetensor weight blob을 사용하지만 scorer config와 modeling/tokenizer code가 다르다. 따라서 Table 4는 FNS objective만의 인과 효과가 아니라, 두 pipeline에서 정규화 range가 다르게 관찰됐다는 결과로 해석한다.

### Label 구분 신호

여기까지의 결과는 score 계산 절차가 six-shift protocol에 민감하다는 점을 보여준다. 남는 질문은 phase-sensitive한 score가 BRCA2 MAVE label 방향성과도 연결되어 있는지다. 이를 확인하기 위해 LOF를 positive class로 두고, Carbon score가 LOF variant와 FUNC/INT variant를 구분할 수 있는지를 AUROC로 측정했다.

BRCA2 500개 SNV subset에서 6개 phase score를 variant별로 먼저 평균한 뒤 AUROC(area under the receiver operating characteristic curve)를 계산했다. 이 six-phase mean-score AUROC는 Full-window token과 Full-sequence FNS에서 세 자리 반올림 기준으로 모두 0.913이었다. 각 scorer의 label을 500회 섞어 만든 shuffled-label null p95보다 높았으므로, 보조 지표상 phase-sensitive score에도 BRCA2 MAVE label 방향성이 남아 있었다.

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
          <td>Full-window token<br><span class="table-note-inline">Six-phase mean score</span></td>
          <td class="align-right"><code>0.913</code></td>
          <td class="align-right"><code>0.553</code></td>
          <td>LOF와 FUNC/INT 구분 signal이 보인다.</td>
        </tr>
        <tr>
          <td>Full-sequence FNS<br><span class="table-note-inline">Six-phase mean score</span></td>
          <td class="align-right"><code>0.913</code></td>
          <td class="align-right"><code>0.559</code></td>
          <td>Full-window token과 거의 같은 AUROC를 보였다.</td>
        </tr>
        <tr>
          <td>Local-target FNS<br><span class="table-note-inline">Six-phase mean score</span></td>
          <td class="align-right"><code>0.760</code></td>
          <td class="align-right"><code>0.559</code></td>
          <td>Variant 주변만 보는 score라 full-sequence 조건과 역할이 다르다.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 5.</strong> Observed AUROC는 variant별 6개 phase score를 먼저 평균한 뒤 계산한 값이다. Shuffled null p95는 seed <code>20260523</code>으로 label을 500회 순열한 AUROC 분포의 95th percentile이다.</figcaption>
</figure>

## 해석과 결론

BRCA2 500개 SNV subset에서 Carbon-3B token score의 six-shift sensitivity는 일부 outlier가 아니라 대부분의 variant에 걸친 현상이었다. Target-token 결과는 variant를 포함한 token scoring의 민감도를 가장 직접적으로 보여준다. Full-window와 Downstream-only 결과에는 전체 segmentation과 window edge/context 변화가 추가로 포함된다.

FNS pipeline의 정규화 range는 Full-sequence에서 0.409에서 0.353으로, Local-target에서 0.349에서 0.331로 낮았다. 방향상 차이는 있었지만 감소 폭은 제한적이었고, 두 FNS 조건도 0.10 기준선 위에 남았다. Six-phase mean score의 AUROC는 label 구분 신호가 남아 있음을 보여주지만, 이 보조 결과가 phase sensitivity를 없애거나 Carbon VEP 전체 성능을 확정하지는 않는다.

따라서 이 평가 설정과 유사한 Carbon SNV scoring에서는 단일 기준 phase 값보다 six-phase 요약값과 range를 함께 보고하는 편이 타당하다. 이 글에서 사용한 mean은 가능한 요약 방식의 한 예이며, 최적 aggregation 방법을 비교한 결과는 아니다. 단일 값만 저장하면 allele에 연결된 점수 차이와 window/tokenization 선택에서 생긴 변동을 구분하기 어렵다.

현재 설정에서 적용 기준은 세 가지다.

1. Reference score에서 alternative score를 뺀 값을 보고할 때 6개 phase range 또는 불안정성 표식을 함께 둔다.
2. FNS가 가능한 환경에서는 token score와 FNS score를 paired 정규화 지표로 비교하되, pipeline 간 관찰 차이로 보고한다.
3. 8,190 bp clean-window 점수와 8,192 bp padding 포함 호환성 점검을 같은 표에서 섞지 않는다. 8,192 bp를 쓰려면 padding tail 점검과 별도 score 절을 둔다.

## 한계

- 이 결과는 BRCA2 MAVE의 500개 SNV subset과 8,190 bp window에 한정된다. 100개 protocol pilot이 500개 subset에 포함되지만, pilot을 제외한 400개에서도 세 token scorer의 정규화 range가 모두 0.10을 넘었다.
- 주 phase-effect의 bootstrap CI는 계산하지 않았다. `0.409`, `0.349`, `0.466`은 현재 subset에서 사전 effect-size 기준을 넘은 관찰값이며, 다른 유전자나 window 조건으로의 일반화에는 추가 평가가 필요하다.
- Shifted-reference 대조는 edge와 전체 6-mer segmentation phase를 함께 바꾼다. 순수한 edge effect, local token-boundary effect, 그 인과적 기여율을 분리하지 않는다.
- Table 5의 AUROC는 shuffled-label null보다 높았지만 단순 sequence/position 기준선, reverse-complement 평가, 외부 VEP benchmark가 없다. Carbon VEP 전체 성능이나 FNS의 biological-performance 개선을 결론으로 두지 않는다.
- FNS paired CI는 사전 주 분석이 아니라 post-hoc audit이다. Token과 FNS revision의 scorer code와 정규화 scale이 달라 FNS objective만의 효과를 분리하지 않는다.

## Appendix: 재현 조건

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
          <td>Token 기반 variant score 계산</td>
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
          <td>Padding 점검</td>
          <td class="align-right"><code>6,000</code> padding 점검 항목</td>
          <td class="align-right"><code>13.21 s</code></td>
          <td class="align-right">해당 없음</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 1.</strong> 계산별 재현 조건 요약이다. Model revision, input hash, sampling seed, score artifact는 별도 재현 기록에 보존했다.</figcaption>
</figure>

## References

<div class="reference-list" markdown="1">

<ol>
  <li id="ref-carbon-paper">Ben Allal, L., Li, Q., Fiusco, M. et al. <strong>Carbon: Decoding the Language of Life</strong>. <em>bioRxiv</em>, 2026.05.22.727119, 2026. DOI: <a href="https://doi.org/10.64898/2026.05.22.727119">10.64898/2026.05.22.727119</a></li>
  <li id="ref-carbon-3b">Hugging Face Biology Research. <strong>Carbon-3B model card and pinned scorer revisions</strong>. Hugging Face, 2026. <a href="https://huggingface.co/HuggingFaceBio/Carbon-3B">Model card</a>; token revision <a href="https://huggingface.co/HuggingFaceBio/Carbon-3B/tree/fe755cb5c7498acbf630080609ef61ecc4e36c17"><code>fe755cb5</code></a>; FNS revision <a href="https://huggingface.co/HuggingFaceBio/Carbon-3B/tree/bf6f6bec000ea6ced8cb656d02f3120a24795c91"><code>bf6f6bec</code></a>. Accessed 2026-07-30.</li>
  <li id="ref-carbon-eval">Hugging Face Biology Research. <strong>Carbon evaluation README</strong>. GitHub, 2026. <a href="https://github.com/huggingface/carbon/blob/0c4a63e985f376426d3e656a4be875e27440473f/evaluation/README.md">pinned evaluation README</a>. Accessed 2026-05-23.</li>
  <li id="ref-huang-brca2">Huang, H., Hu, C., Na, J. et al. <strong>Functional evaluation and clinical classification of BRCA2 variants</strong>. <em>Nature</em> 638, 528-537, 2025. DOI: <a href="https://doi.org/10.1038/s41586-024-08388-8">10.1038/s41586-024-08388-8</a></li>
  <li id="ref-brca2-source-table">Huang et al. <strong>Functional evaluation and clinical classification of BRCA2 variants</strong>, Supplementary Table 3. Nature/Springer, 2025. <a href="https://static-content.springer.com/esm/art%3A10.1038%2Fs41586-024-08388-8/MediaObjects/41586_2024_8388_MOESM3_ESM.xlsx">Supplementary Table S3 XLSX</a></li>
  <li id="ref-ucsc-hg19-chr13">UCSC Genome Browser. <strong>hg19/GRCh37 chr13 chromosome FASTA, goldenPath</strong>. <a href="https://hgdownload.soe.ucsc.edu/goldenPath/hg19/chromosomes/chr13.fa.gz">chr13.fa.gz</a>. Accessed 2026-05-23.</li>
  <li id="ref-carbon-brca2-prep">Hugging Face Biology Research. <strong>Carbon BRCA2 data preparation script</strong>. <a href="https://raw.githubusercontent.com/huggingface/carbon/0c4a63e985f376426d3e656a4be875e27440473f/evaluation/data_prep/prep_brca2.py">pinned <code>prep_brca2.py</code></a>. Source content frozen with the experiment inputs; accessed 2026-05-23.</li>
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
