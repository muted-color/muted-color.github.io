---
title: "HSPC hierarchy benchmark 설계와 rare-cell classification 적용"
date: 2026-04-21 18:40:00 +0900
last_modified_at: 2026-04-24 23:17:18 +0900
categories: ["SINGLE CELL ML"]
tags: [scrna, hspc, rare-cell, benchmark, semi-supervised, scvi, scgpt]
lab_path: "experiment-lab/projects/rare-cell-hspc-hierarchy-stage1"
excerpt: "HSPC hierarchy를 실질적인 rare-cell classification task로 구성하고, local geometry, 표현학습 모델, scGPT fusion 적용에서 확인한 개선과 한계를 정리한다."
description: "rare-cell 분류에서 HSPC hierarchy benchmark를 실질적인 task 환경으로 구성한 배경과 donor-heldout low-anchor 조건의 어려움, pca30-B3 calibrated reference, whole-human scGPT PCA400-linear fusion 결과와 calibration 한계를 정리한 미니 리서치 글."
permalink: /research/2026/04/21/hspc-hierarchy-benchmark-lineage/
image: /assets/images/posts/hspc-hierarchy-benchmark-lineage/ig_0a0b41422bd564750169eb7876cf808191b805b89709616bf2.png
image_alt: "HSPC hierarchy benchmark에서 세포 집단 분기와 rare-cell boundary를 파란색으로 강조한 대표 이미지"
hero_image: /assets/images/posts/hspc-hierarchy-benchmark-lineage/ig_0a0b41422bd564750169eb7876cf808191b805b89709616bf2.png
hero_alt: "HSPC hierarchy benchmark에서 여러 세포 집단이 분기하고 오른쪽 rare-cell boundary가 파란색으로 강조된 hero 이미지"
hero_frame: true
---

Rare-cell 분류 문제를 다루기 위해서는 먼저 방법을 실제로 적용해볼 수 있는 task 환경이 필요하다. 여기서 benchmark는 데이터셋 선택만이 아니라 세포 집단, 라벨 구조, donor split, label budget을 함께 고정한 평가 환경을 뜻한다. 단순 기준선으로 바로 포화되거나 metadata shortcut이 강한 설정에서는 방법을 적용해도 개선의 의미를 해석하기 어렵다.

분석 대상은 normal cHSPC 안의 `HSPC hierarchy`를 donor-heldout low-anchor fine-state 복원 benchmark로 구성한 설정이다. 초점은 새로운 모델 제안이 아니라, rare-cell classification을 너무 쉽지도 불가능하지도 않은 실질적인 task 환경으로 고정한 뒤, 여러 방법을 적용하면서 무엇이 어려웠고 어떤 신호가 개선에 기여했는지 정리하는 데 있다.

<aside class="research-question" aria-label="실험 초점">
  <p class="research-question__label">Experiment Focus</p>
  <p>normal cHSPC 안의 <code>HSPC hierarchy</code>를 donor-heldout low-anchor fine-state recovery task로 고정하고, local expression geometry, 표현학습 latent, single-cell foundation model signal, late fusion을 적용하면서 rare-cell classification에서 어떤 신호가 실제로 도움이 되고 어떤 한계가 남는지 확인한다.</p>
</aside>

{% include model-mention-cards.html label="사용한 주요 리소스" aria_label="사용한 데이터셋과 single-cell 모델 리소스" models="cHSPC CELLxGENE collection|10.1038/s41591-025-03716-5|https://doi.org/10.1038/s41591-025-03716-5;scVI / scvi-tools|scvi-tools|https://scvi-tools.org/;scGPT|tdc/scGPT|https://huggingface.co/tdc/scGPT" %}

## 요약

- HSPC hierarchy benchmark는 가까운 progenitor state, donor-heldout split, low-anchor 조건을 함께 묶어 새 donor에서도 fine state를 구분해야 하는 실질적인 rare-cell classification task로 구성했다.
- 초기 가능성 점검에서는 metadata shortcut이 강하지 않았고, expression 기반의 단순 classifier가 centroid baseline을 충분히 넘었다. 이 결과가 본 평가로 진행할 근거가 됐다.
- 본 평가에서는 inductive kNN label propagation이 anchor prior, centroid, cheap linear classifier를 넘었다. 이 결과는 rare-cell classification에서 단순 marker 유무보다 local neighborhood 구조를 쓰는 방식이 중요하다는 신호로 읽었다.
- 30차원 PCA 표현 위에서 label propagation을 적용한 `pca30-B3`는 `primary_score = 0.902323`, `mean_ECE = 0.023626`으로 가장 안정적인 calibrated reference였다.
- fast `scVI`, blood/continual `scGPT`, scGPT embedding 위의 direct label propagation은 이 reference를 넘지 못했다. 더 복잡한 표현이나 foundation-model embedding이 바로 좋은 rare-cell decision geometry가 되지는 않았다.
- whole-human `scGPT` PCA400-linear probability는 단독으로는 reference보다 낮았지만, `pca30-B3`와 late fusion했을 때 primary score가 `0.915108`로 증가했다. 다만 ECE는 `0.093359`로 나빠져, 결론은 `primary score 기준 fusion 조합 + pca30-B3 calibrated reference`로 나누어 해석한다.

## HSPC hierarchy benchmark

### 설계 배경

rare-cell 분류 문제의 방법론 비교에는 안정적으로 정의된 benchmark가 필요하다. 여기서 benchmark는 단순히 데이터셋 하나를 고르는 일이 아니라, 어떤 세포 집단을 대상으로 삼고, 어떤 라벨 구조를 가리고 복원하게 하며, 어떤 split과 label budget에서 일반화를 볼 것인지 정해 **방법을 적용할 수 있는 task 환경**을 만드는 일에 가깝다.

너무 쉬운 과제에서는 단순한 기준선만으로도 성능이 빨리 포화되고, shortcut이 강한 과제에서는 새 방법이 무엇을 배운 것인지 해석하기 어렵다. 따라서 이 단계의 기준은 특정 방법의 즉시 성능 개선이 아니라, **rare-cell 분류 방법을 적용했을 때 개선과 한계를 해석할 수 있는 task 환경의 성립 여부**였다.

HSPC hierarchy는 이 기준에 맞춰 구성하기 좋은 설정이었다. 같은 큰 세포 집단 안에 biologically 가까운 progenitor state들이 있고, donor 수가 충분해 donor-heldout split을 만들 수 있으며, 상위 라벨만 남긴 뒤 세부 라벨을 복원하는 parent-label collapse 설정을 만들 수 있었다. 즉, 단순히 데이터가 있었기 때문이 아니라 **데이터, 라벨 구조, split 조건이 함께 benchmark 난이도를 만들 수 있었기 때문에** 이 설정을 사용했다. 이 선택의 기준은 Table 1에 정리했다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>조건</th>
          <th>중요한 이유</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>hierarchy가 명확함</td>
          <td><code>parent-label collapse</code>, 즉 세부 라벨 일부를 가리고 더 큰 상위 라벨만 남기는 benchmark를 설계하기 좋았다</td>
        </tr>
        <tr>
          <td>sibling state가 biologically 가까움</td>
          <td>서로 비슷한 세포 상태라서 실제로 어려운 구분 문제가 된다</td>
        </tr>
        <tr>
          <td>donor 수가 충분함</td>
          <td><code>donor-heldout</code> split을 안정적으로 구성할 수 있었다</td>
        </tr>
        <tr>
          <td>shortcut을 점검할 수 있음</td>
          <td>metadata나 donor shortcut이 강한 문제인지 먼저 확인할 수 있었다</td>
        </tr>
        <tr>
          <td>feasibility를 먼저 점검할 수 있음</td>
          <td>복잡한 방법을 적용하기 전에 이 task가 너무 쉽거나 불가능한 설정이 아닌지 확인할 수 있었다</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> HSPC hierarchy를 rare-cell classification task 환경으로 구성할 때 중요했던 설계 조건과 해석상 역할.</figcaption>
</figure>

따라서 HSPC hierarchy는 단순한 데이터셋 선택이 아니라, rare-cell classification 방법을 실제로 적용하고 해석하기 위해 설계한 task 환경이었다. 이후 실험은 이 task를 풀면서 어떤 접근이 실제로 효과가 있었고, 어떤 어려움이 구조적으로 남는지 확인하는 과정에 가깝다.

### 평가 설계

이 benchmark는 아래 네 가지 축을 함께 묻도록 구성했다.

- 가까운 sibling state를 실제로 구분해야 한다.
- 같은 donor를 다시 맞히지 않고 새 donor에서도 일반화돼야 한다.
- 라벨이 충분하지 않은 low-anchor 조건을 견뎌야 한다.
- 테스트 셀을 학습 때 직접 보지 않는 inductive setting이어야 한다.

실제 평가 질문은 다음처럼 구체화됐다.

- dataset: `cHSPC Illumina`
- condition: `diagnosis == normal`
- population: `hematopoietic precursor cell`
- fine labels: `MEBEMP-L`, `CLP`, `ERYP`, `BEMP`, `GMP-L`, `NKTDP`
- split: `donor-heldout`
- mode: `inductive-only`
- primary budget: `20 anchors/class`

여기서 `donor-heldout`은 같은 donor의 셀이 train과 test에 동시에 들어가지 않게 막는 설정이다. 다시 말해, 같은 사람 안에서 비슷한 셀을 다시 맞히는 문제가 아니라 **새 donor에서도 같은 패턴이 유지되는지**를 보는 더 엄격한 평가다. `anchor`는 학습할 때 정답 라벨이 공개된 소수의 셀이고, `inductive`는 테스트용 셀을 학습 때 직접 보지 않고 예측하는 방식이다.

이 조합이 task 환경의 핵심 조건이다. biologically 가까운 sibling state를 새 donor 일반화 조건과 low-anchor 조건 아래에서 묻도록 구성했기 때문에, 단순한 shortcut보다 실제 분류 난이도와 남아 있는 차이를 더 직접적으로 볼 수 있다.

### Task 환경의 성립 조건

초기 검증(`Stage 0H`)은 최종 기준을 고르는 단계가 아니라, **이 설정이 실질적인 rare-cell classification task 환경으로 성립하는지** 확인하는 단계였다. Table 2는 이때 사용한 데이터 규모와 기본 조건을 요약한다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>항목</th>
          <th>값</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>primary dataset</td>
          <td><code>human cHSPCs - Illumina</code></td>
        </tr>
        <tr>
          <td>scale</td>
          <td><code>495,763</code> cells, <code>132</code> donors, <code>28,968</code> genes</td>
        </tr>
        <tr>
          <td>primary fine labels</td>
          <td><code>6</code></td>
        </tr>
        <tr>
          <td>metadata-only donor-heldout max AUC</td>
          <td><code>0.582</code></td>
        </tr>
        <tr>
          <td>primary budgets</td>
          <td><code>20 / 50 / 100 anchors/class</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> 초기 가능성 점검에서 사용한 cHSPC 데이터 규모와 task 구성 조건.</figcaption>
</figure>

Table 3의 숫자는 아래처럼 읽었다.

- anchor prior: label 비율만 보는 prior baseline
- centroid baseline: 공개된 셀 평균에 가장 가까운 라벨을 주는 아주 단순한 기준선
- cheap expression classifier: expression만 쓰는 간단한 선형 분류기

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table">
      <thead>
        <tr>
          <th>anchors/class</th>
          <th class="align-right">anchor prior</th>
          <th class="align-right">centroid</th>
          <th class="align-right">cheap classifier</th>
          <th class="align-right">cheap classifier - centroid</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>20</code></td>
          <td class="align-right"><code>0.1667</code></td>
          <td class="align-right"><code>0.3227</code></td>
          <td class="align-right"><code>0.7814</code></td>
          <td class="align-right"><code>+0.4587</code></td>
        </tr>
        <tr>
          <td><code>50</code></td>
          <td class="align-right"><code>0.1667</code></td>
          <td class="align-right"><code>0.3259</code></td>
          <td class="align-right"><code>0.8534</code></td>
          <td class="align-right"><code>+0.5275</code></td>
        </tr>
        <tr>
          <td><code>100</code></td>
          <td class="align-right"><code>0.1667</code></td>
          <td class="align-right"><code>0.3257</code></td>
          <td class="align-right"><code>0.8838</code></td>
          <td class="align-right"><code>+0.5581</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> 초기 가능성 점검에서 anchor 수에 따라 단순 기준선과 expression classifier가 보인 성능 차이.</figcaption>
</figure>

다른 확인에서도 방향은 같았다.

- cheap classifier의 `max(anchor prior, centroid)` 대비 mean gain은 `0.4248 / 0.5227 / 0.5593`였다.
- CI lower는 `0.4037 / 0.5143 / 0.5500`이었다.
- Ultima cross-platform에서도 cheap classifier - centroid가 `+0.4674 / +0.5322 / +0.5613`로 방향이 유지됐다.

이 숫자는 뒤에서 나오는 본 평가의 centroid baseline과 cheap linear classifier 숫자와 직접 비교하지 않는다. 초기 가능성 점검은 더 큰 feasibility audit이고, 본 평가는 `r102`에서 얼린 좁은 donor-heldout benchmark sample 위에서 다시 정의한 비교다. 같은 계열의 기준선을 쓰지만, 여기서는 **역할이 다른 두 단계의 신호**로 해석한다.

이 단계의 판정 기준은 이 설정이 실제 분류 task로 성립하는지 확인하는 체크에 가까웠다.

- metadata shortcut은 강하지 않았다.
- low-anchor regime에서도 cheap classifier와 단순 기준선 사이의 차이가 컸다.
- cross-platform 확인에서도 방향이 유지됐다.

이 세 가지가 함께 확인되었기 때문에 이 설정을 **본 비교로 가져갈 수 있는 rare-cell classification task 환경**으로 판단했다.

### 본 분류 task에서 확인한 headroom

본 비교(`Stage 1`)는 구성한 task 환경에서 실제 성능 차이가 확인되는지 보는 단계였다. 초기 검증과 본 비교의 숫자는 직접 줄세워 비교하기보다, 역할이 다른 두 단계의 결과로 해석한다.

`r102`에서 얼린 benchmark sample은 `26,681` cells, `90` donors, `6` fine labels였다. 여기서 핵심 방법인 inductive kNN label propagation (`B3`)은 공개된 소수의 라벨 정보를 가까운 셀로 퍼뜨려 예측하는 방식이다. budget `20`에서의 primary ladder는 Table 4와 같았다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table">
      <thead>
        <tr>
          <th>method</th>
          <th>short name</th>
          <th class="align-right">primary score</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>anchor prior</td>
          <td><code>B0</code></td>
          <td class="align-right"><code>0.1667</code></td>
        </tr>
        <tr>
          <td>nearest centroid / reference-transfer proxy</td>
          <td><code>B1</code></td>
          <td class="align-right"><code>0.8787</code></td>
        </tr>
        <tr>
          <td>cheap linear expression classifier</td>
          <td><code>B2</code></td>
          <td class="align-right"><code>0.8217</code></td>
        </tr>
        <tr>
          <td>inductive kNN label propagation</td>
          <td><code>B3</code></td>
          <td class="align-right"><code>0.8967</code></td>
        </tr>
        <tr>
          <td>inductive graph SSL</td>
          <td><code>B4</code></td>
          <td class="align-right"><code>0.8694</code></td>
        </tr>
        <tr>
          <td>calibrated pseudo-labeling</td>
          <td><code>B5</code></td>
          <td class="align-right"><code>0.8291</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> 본 분류 task의 budget <code>20 anchors/class</code> 조건에서 비교한 기준선과 semi-supervised 방법의 primary score.</figcaption>
</figure>

표의 단순 차이보다 중요한 값은 split별 gain을 따로 모아 계산한 paired gain이다.

- displayed primary score: 여러 split 결과를 요약한 대표값
- paired gain score: split별 gain을 직접 비교해 만든 판단값

실제 paired gain은 Table 5에 정리했다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table">
      <thead>
        <tr>
          <th>비교</th>
          <th class="align-right">값</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>label propagation - max(anchor prior, centroid, cheap linear) point estimate</td>
          <td class="align-right"><code>+0.0255</code></td>
        </tr>
        <tr>
          <td><code>95% CI</code></td>
          <td class="align-right"><code>(+0.0096, +0.0314)</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 5.</strong> Split별 gain을 직접 비교해 계산한 label propagation의 paired gain.</figcaption>
</figure>

이 결과의 의미는 단일 점수 개선보다, **이 분류 task에 아직 non-trivial headroom이 남아 있는지**를 확인했다는 데 있다.

- inductive kNN label propagation이 실제로 comparator를 넘었다.
- 따라서 이 설정에는 **비교할 만한 성능 차이가 실제로 남아 있었다**.
- 다만 `MEBEMP-L <-> ERYP` sibling boundary는 이 시점부터 분명한 caveat로 남았다.

## Rare-cell classification 적용

### 기준선으로 확인한 기본 난이도

benchmark를 고정한 뒤에는 같은 조건에서 rare-cell classification task를 풀었다. 이 단계에서 얻은 핵심은 단순 점수 개선이 아니라, 가까운 HSPC state를 새 donor와 low-anchor 조건에서 분류할 때 어떤 방법론이 실제로 효과가 있었고, 왜 어떤 접근은 충분하지 않았으며, 어떤 난점이 반복적으로 남는지에 대한 정리였다.

먼저 nearest centroid baseline (`B1`)은 공개된 anchor의 평균 위치만으로 fine state를 복원할 수 있는지 보는 가장 단순한 출발점이었다. 이 방법이 충분했다면 HSPC hierarchy는 각 state가 하나의 대표점으로 잘 요약되는 prototype matching 문제에 가까웠을 것이다. 그러나 donor-heldout low-anchor 조건에서는 이 방식만으로 충분하지 않았다.

cheap linear expression classifier (`B2`)는 marker signal이 실제로 남아 있는지 확인하는 역할을 했다. 초기 가능성 점검에서 이 classifier가 강했다는 것은 라벨이 완전히 뒤섞인 문제가 아니라는 뜻이다. expression 안에는 fine state를 구분할 신호가 남아 있었다. 다만 본 평가에서는 nearest centroid도 강한 comparator가 됐고, 단순한 선형 경계만으로 task가 닫히지는 않았다.

inductive kNN label propagation (`B3`)은 local neighborhood를 쓰는 방향이었다. HSPC sibling state가 완전히 분리된 섬이라기보다 local expression manifold 위에서 이어져 있다면, 적은 anchor만으로도 주변 구조를 이용할 수 있어야 한다. 실제로 이 방법은 anchor prior, centroid, cheap linear classifier 중 가장 강한 comparator를 넘었다. 이 결과는 rare-cell classification의 어려움이 단순 marker 유무가 아니라, **가까운 세포들의 구조를 어떻게 쓰는지**와 연결되어 있음을 보여준다.

### Local geometry를 활용한 개선

그다음 개선은 모델 계열을 바꾸는 것보다 표현 공간을 조정할 때 나왔다. 같은 label propagation이라도 `pca50` 대신 `pca30` 위에서 local neighborhood를 만들었을 때 primary score와 pair confusion이 함께 개선됐다. Table 6은 이 차이를 요약한다. 남은 병목은 단순히 더 복잡한 classifier 부족이 아니라, 어떤 표현 공간에서 가까운 이웃을 정의할 것인지와 관련되어 있었다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table">
      <thead>
        <tr>
          <th>condition</th>
          <th class="align-right"><code>primary_score</code></th>
          <th class="align-right"><code>mean_macro_AUPRC</code></th>
          <th class="align-right"><code>mean_ECE</code></th>
          <th class="align-right"><code>mean_Brier</code></th>
          <th class="align-right"><code>MEBEMP-L &lt;-&gt; ERYP</code> pair confusion</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>pca50-B3</code> baseline</td>
          <td class="align-right"><code>0.896652</code></td>
          <td class="align-right"><code>0.895621</code></td>
          <td class="align-right"><code>0.027164</code></td>
          <td class="align-right"><code>0.226867</code></td>
          <td class="align-right"><code>0.278660</code></td>
        </tr>
        <tr>
          <td><code>pca30-B3</code></td>
          <td class="align-right"><code>0.902323</code></td>
          <td class="align-right"><code>0.899463</code></td>
          <td class="align-right"><code>0.023626</code></td>
          <td class="align-right"><code>0.220972</code></td>
          <td class="align-right"><code>0.266080</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 6.</strong> <code>pca50-B3</code>와 <code>pca30-B3</code>의 primary score, calibration, 핵심 pair confusion 비교.</figcaption>
</figure>

Figure 1은 같은 비교를 세 지표의 방향성으로 다시 보여준다. `pca30-B3`는 primary score를 올리는 동시에 ECE와 `MEBEMP-L <-> ERYP` pair confusion을 낮췄다.

<figure class="media-figure">
  <img src="/assets/images/posts/hspc-hierarchy-benchmark-lineage/pca30-b3-reference-metrics.svg" alt="pca50-B3와 pca30-B3의 primary score, mean ECE, MEBEMP-L ERYP pair confusion을 비교한 세 패널 막대 그래프">
  <figcaption><strong>Figure 1.</strong> 같은 label propagation이라도 local neighborhood를 정의하는 PCA 공간에 따라 primary score, calibration, 주요 sibling-boundary confusion이 함께 달라졌다. <code>pca30-B3</code>는 점수만 높은 run이 아니라 calibrated in-domain reference로 남을 조건을 함께 만족했다.</figcaption>
</figure>

핵심 비교는 아래와 같다.

- `pca30` vs `pca50` primary score median gain: `+0.0097`
- bootstrap `95% CI = (+0.0044, +0.0155)`
- pair confusion delta: `-0.0219`
- pair bootstrap `95% CI = (-0.0337, -0.0120)`

여기서 `pca30`은 데이터를 30차원으로 줄여서 보는 표현 방식이다. compact PCA view가 고차원 noise를 줄이고, HSPC lineage와 관련된 local geometry를 더 안정적으로 보존한 것으로 해석할 수 있다. 이 때문에 `pca30-B3`는 단순한 best run이 아니라, 이후 비교에서 기준으로 삼을 calibrated in-domain reference가 됐다. 참고로 `macro AUPRC`는 각 클래스를 고르게 보고 평균낸 성능 점수이고, `ECE`는 confidence와 실제 정답률의 정합성을 보는 calibration 지표다.

추가 safety / sensitivity도 같은 방향을 지지했다.

- donor leakage AUC: `0.559952`
- all-diagnosis gain: `+0.030604`
- Ultima gain: `+0.025175`
- 두 sensitivity 모두 calibration은 cheap linear classifier보다 나빠지지 않았다

### 표현학습 모델의 적용과 한계

성능을 갱신하지 못한 시도들도 task의 성격을 이해하는 데 필요했다. 먼저 같은 `pca30-B3` 안에서 `k`, `alpha`, pair-local rescue를 바꿔도 material gain은 거의 없었다. 이는 남은 오류가 단순한 propagation hyperparameter 문제가 아니라는 뜻이다.

이후에는 표현학습 모델을 적용했다. `scVI`는 batch나 noise를 줄인 generative latent가 rare-cell classification에 도움이 되는지 확인하기 위한 선택이었다. 이 가정이 맞았다면 scVI latent 위의 label propagation이 reference를 넘어야 했다. 그러나 성능, calibration, `MEBEMP-L <-> ERYP` boundary 모두에서 `pca30-B3`보다 불리했다. 더 매끄러운 latent가 항상 더 좋은 decision geometry를 만드는 것은 아니었다.

초기 `scGPT` 결과도 같은 방향이었다. foundation-model embedding은 더 넓은 transcriptomic prior를 줄 수 있지만, 그것이 곧바로 이 task의 local propagation graph가 되지는 않았다. 특히 raw scGPT embedding에 label propagation을 붙인 결과가 낮았다는 점은, scGPT 공간이 label ranking signal을 일부 갖고 있더라도 이 방법이 요구하는 local neighborhood geometry와는 맞지 않을 수 있음을 보여준다. 관련 음성 결과는 Table 7에 모았다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>비교 항목</th>
          <th>핵심 결과</th>
          <th>읽는 법</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>같은 설정 안의 <code>pca30-B3</code> hyperparameter sweep</td>
          <td>best simple variant의 seed-median primary gain <code>+0.0008</code>, <code>95% CI = (+0.0002, +0.0013)</code></td>
          <td>방향성은 있으나 reference를 바꿀 수준은 아님</td>
        </tr>
        <tr>
          <td>fast <code>scVI</code> latent + label propagation</td>
          <td><code>primary_score = 0.893955</code>, <code>mean_ECE = 0.069573</code>, <code>pair_confusion = 0.275425</code></td>
          <td><code>pca30-B3</code>보다 성능, calibration, pair boundary 모두 불리</td>
        </tr>
        <tr>
          <td>original blood <code>scGPT</code> + linear</td>
          <td><code>0.837242</code></td>
          <td>실행은 됐지만 reference 아래</td>
        </tr>
        <tr>
          <td>original blood <code>scGPT</code> + prototype</td>
          <td><code>0.698214</code></td>
          <td>nearest-prototype assumption이 크게 깨짐</td>
        </tr>
        <tr>
          <td>original blood <code>scGPT</code> + label propagation</td>
          <td><code>0.838096</code></td>
          <td>raw embedding을 propagation graph로 쓰기 어려움</td>
        </tr>
        <tr>
          <td>continual <code>scGPT</code> + linear / label propagation</td>
          <td><code>0.850564</code> / <code>0.846002</code></td>
          <td>blood checkpoint보다는 낫지만 reference와 큰 gap</td>
        </tr>
        <tr>
          <td>whole-human <code>scGPT</code> raw linear / raw label propagation</td>
          <td><code>0.880685</code> / <code>0.874831</code></td>
          <td>checkpoint는 나아졌지만 단독으로는 reference 미달</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 7.</strong> <code>pca30-B3</code> reference를 대체하지 못한 tuning, scVI, scGPT 계열 적용 결과와 해석.</figcaption>
</figure>

이 음성 결과들은 더 복잡한 방법이 reference를 넘지 못했다는 기록에 그치지 않는다. rare-cell classification에서 실제로 맞닿게 되는 어려움이 무엇인지 분리해 보여준다.

- 복잡한 모델 계열이라고 자동으로 좋아지지 않았다.
- foundation-model embedding이라고 자동으로 reference를 대체하지 않았다.
- 같은 설정 안의 미세 튜닝은 남은 오류를 크게 줄이지 못했다.

따라서 이 task에서 남은 병목은 단순한 local hyperparameter 부족이라기보다, **representation / decision geometry / label ranking signal의 조합 문제**에 더 가깝다.

### 보완적 ranking signal의 결합

whole-human `scGPT`를 추가하면서 개선 방향이 바뀌었다. 단독 scGPT나 scGPT embedding 위의 direct label propagation은 reference를 넘지 못했지만, fold-local PCA400으로 denoise한 뒤 linear probability를 만들면 `pca30-B3`와 다른 오류 구조가 나타났다. 즉, scGPT가 reference를 대체한 것이 아니라, `pca30-B3`가 약한 일부 label ranking에서 보완 신호를 제공한 것으로 읽는 편이 맞다.

마지막 비교는 embedding을 교체하는 방식이 아니라 probability를 결합하는 방식이었다. `pca30-B3`는 in-domain local manifold signal을 제공하고, whole-human `scGPT` PCA400-linear는 complementary ranking signal을 제공한다. Table 8처럼 둘을 `w=0.5`로 late fusion하자 primary score는 `0.915108`까지 올라갔다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table">
      <thead>
        <tr>
          <th>line</th>
          <th class="align-right"><code>primary_score</code></th>
          <th class="align-right"><code>mean_macro_AUPRC</code></th>
          <th class="align-right"><code>mean_ECE</code></th>
          <th class="align-right"><code>mean_Brier</code></th>
          <th>역할</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>pca30-B3</code></td>
          <td class="align-right"><code>0.902323</code></td>
          <td class="align-right"><code>0.899463</code></td>
          <td class="align-right"><code>0.023626</code></td>
          <td class="align-right"><code>0.220972</code></td>
          <td>calibrated reference</td>
        </tr>
        <tr>
          <td>whole-human <code>scGPT PCA400-linear</code></td>
          <td class="align-right"><code>0.894952</code></td>
          <td class="align-right"><code>0.892713</code></td>
          <td class="align-right"><code>0.071926</code></td>
          <td class="align-right"><code>0.315177</code></td>
          <td>단독으로는 reference 미달</td>
        </tr>
        <tr>
          <td><code>pca30-B3 + scGPT PCA400-linear fusion w0.5</code></td>
          <td class="align-right"><code>0.915108</code></td>
          <td class="align-right"><code>0.916052</code></td>
          <td class="align-right"><code>0.093359</code></td>
          <td class="align-right"><code>0.226904</code></td>
          <td>primary score 기준 최종 조합</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 8.</strong> Calibrated reference, whole-human scGPT PCA400-linear 단독, late fusion 조합의 성능과 역할 비교.</figcaption>
</figure>

이 결과는 foundation model 단독 승리로 해석하지 않는다. foundation model은 단독 decision space로는 부족했지만, `pca30-B3`가 만든 안정적인 reference 위에 올렸을 때 남은 ranking 오류 일부를 보완했다. 그래서 이 단계의 결론은 `pca30-B3`를 버리는 것이 아니라, calibrated reference와 primary-score fusion 조합을 분리해서 보는 것이다.

fusion weight도 제한적으로 해석한다. Table 9는 scGPT probability weight를 바꿨을 때의 primary score 변화를 보여준다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table">
      <thead>
        <tr>
          <th class="align-right"><code>scGPT</code> weight</th>
          <th class="align-right">primary score</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="align-right"><code>0.0</code></td>
          <td class="align-right"><code>0.902323</code></td>
        </tr>
        <tr>
          <td class="align-right"><code>0.3</code></td>
          <td class="align-right"><code>0.913787</code></td>
        </tr>
        <tr>
          <td class="align-right"><code>0.4</code></td>
          <td class="align-right"><code>0.914720</code></td>
        </tr>
        <tr>
          <td class="align-right"><code>0.5</code></td>
          <td class="align-right"><code>0.915108</code></td>
        </tr>
        <tr>
          <td class="align-right"><code>0.55</code></td>
          <td class="align-right"><code>0.915041</code></td>
        </tr>
        <tr>
          <td class="align-right"><code>0.6</code></td>
          <td class="align-right"><code>0.914702</code></td>
        </tr>
        <tr>
          <td class="align-right"><code>1.0</code></td>
          <td class="align-right"><code>0.894952</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 9.</strong> scGPT PCA400-linear probability의 late-fusion weight에 따른 primary score 변화.</figcaption>
</figure>

Figure 2는 같은 결과를 curve로 나타낸 것이다. 중간 weight에서는 reference를 넘지만, `w=1.0`의 scGPT 단독은 다시 낮아진다.

<figure class="media-figure">
  <img src="/assets/images/posts/hspc-hierarchy-benchmark-lineage/scgpt-fusion-weight-curve.svg" alt="scGPT fusion weight가 0.3에서 0.6 사이일 때 primary score가 pca30-B3 reference보다 높고 scGPT 단독에서는 낮아지는 선 그래프">
  <figcaption><strong>Figure 2.</strong> scGPT PCA400-linear probability의 fusion weight에 따른 primary score 변화다. 중간 weight에서 reference를 넘지만, scGPT 단독은 reference보다 낮다. 따라서 이 결과는 foundation model 단독 승리보다 complementary ranking signal의 결합으로 읽는 편이 맞다.</figcaption>
</figure>

`w=0.0`은 `pca30-B3` reference 재현이고, `w=1.0`은 scGPT PCA400-linear 단독이다. `w=0.3~0.6` 구간에서 reference를 안정적으로 넘었고 그중 primary median 기준 최고가 `w=0.5`였다. 다만 이 weight는 최종 평가 grid 위에서 관측한 best이므로, 일반화된 고정 fusion recipe라고 주장하려면 train-only 또는 nested 방식의 weight selection rule을 따로 검증해야 한다.

### 남은 경계: `MEBEMP-L <-> ERYP`

남은 주요 오류 경계는 비교적 명확했다.

- `MEBEMP-L`은 성격이 조금 섞여 보이는 전구세포 쪽 상태였고, `ERYP`는 적혈구 계열 신호가 더 강한 상태였다.
- 전체 score가 개선되는 동안에도 `MEBEMP-L <-> ERYP`는 주요 오류 경계로 남았다.
- `r124` failure anatomy에서는 일부 donor-label slice에서 `pca30-B3`가 cheap linear classifier보다 더 confidently wrong한 패턴이 남았다.
- 그런데 `r125` anchor audit에서는 pair-anchor donor coverage가 대체로 균형적이었다.
- `r126` separability audit에서는 donor-heldout pairwise separability가 높았다: mean pair AP `0.9233`, mean pair AUC `0.9177`.

여기서 `pair AP`와 `pair AUC`는 이 두 상태만 따로 놓고 봤을 때 얼마나 잘 구분되는지를 보는 점수다. 이 경계가 어렵기는 해도 완전히 뒤섞인 것은 아니라는 뜻이다.

이 pair는 아래처럼 해석한다.

- 완전히 분리 불가능한 경계는 아니다.
- 단순 anchor imbalance 문제도 아니다.
- marker structure는 여전히 남아 있다.
- 현재 평가 설정에서는 **표현의 한계가 남아 있지만 완전히 뒤섞인 경계는 아닌 상태**에 가깝다.

fusion은 이 경계를 일부 줄였다. Table 10처럼 label별로 보면 `MEBEMP-L`과 `ERYP`에서 scGPT PCA-linear signal이 reference를 보완했다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table">
      <thead>
        <tr>
          <th>label</th>
          <th class="align-right"><code>pca30-B3</code> AP</th>
          <th class="align-right">fusion <code>w0.5</code> AP</th>
          <th class="align-right">gain</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>MEBEMP-L</code></td>
          <td class="align-right"><code>0.731729</code></td>
          <td class="align-right"><code>0.763169</code></td>
          <td class="align-right"><code>+0.031440</code></td>
        </tr>
        <tr>
          <td><code>ERYP</code></td>
          <td class="align-right"><code>0.759149</code></td>
          <td class="align-right"><code>0.800668</code></td>
          <td class="align-right"><code>+0.041519</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 10.</strong> <code>MEBEMP-L</code>과 <code>ERYP</code>에서 <code>pca30-B3</code> 대비 fusion <code>w0.5</code>가 만든 label별 AP gain.</figcaption>
</figure>

따라서 이 boundary는 task 환경 자체를 무효화하는 blocker라기보다, fusion 조합이 실제 headroom을 만들 수 있는 핵심 경계로 남는다. 다만 이 결과만으로 문제가 해결됐다고 볼 수는 없다. fusion은 primary score와 일부 ranking을 개선했지만 calibration은 `pca30-B3`보다 나빠졌다.

## 현재 단계의 정리

현재 단계의 결론은 단순한 순위 선언보다, 이 rare-cell classification task의 어려움과 맞닿으면서 확인한 신호의 역할 구분에 가깝다.

- 먼저 task 환경의 성립 여부를 걸러낸 접근은 유효했다. HSPC hierarchy는 rare-cell classification 방법을 적용했을 때 개선과 한계를 해석할 수 있는 평가 환경으로 구성할 수 있었다.
- `pca30-B3`는 local expression geometry를 가장 안정적으로 쓴 calibrated in-domain reference로 남았다.
- 동일한 평가 조건 안의 작은 tuning, fast `scVI`, blood `scGPT`, continual `scGPT`, scGPT embedding 위의 direct label propagation은 이 reference를 넘지 못했다.
- whole-human `scGPT`는 단독으로 reference를 넘지 못했지만, PCA400 linear probability를 `pca30-B3`와 late fusion했을 때 primary score를 갱신했다.
- primary score 기준 최종 조합은 `pca30-B3 + whole-human scGPT PCA400-linear fusion w0.5`다.
- 이 결과는 foundation model 단독 승리가 아니라, in-domain local geometry와 foundation-model ranking signal이 서로 보완된 결과로 읽는 편이 맞다.
- 남은 과제는 fusion의 calibration, train-only weight selection rule, 그리고 `MEBEMP-L <-> ERYP` 경계를 더 안전하게 줄이는 방법이다.

## Appendix

### 본문이 기대는 문서

- `report/STAGE0H_FINAL_REPORT_KO.md`
- `report/STAGE1_FINAL_CLOSEOUT_REPORT_KO.md`
- `report/HSPC_HIERARCHY_BENCHMARK_MINI_RESEARCH_REPORT_KO.md`
- `report/FINAL_WINNER_MANIFEST.md`
- `report/key_results.md`

### 주요 결과 표

- `rare-cell-hspc-hierarchy-stage0/experiments/exp_09_healthy_only_sensitivity/artifacts/runs/r009/robustness_summary.tsv`
- `rare-cell-hspc-hierarchy-stage1/experiments/exp_04_b3_inductive_knn_label_propagation/artifacts/runs/r104/summary.tsv`
- `rare-cell-hspc-hierarchy-stage1/experiments/exp_07_ci_and_hard_label_analysis/artifacts/runs/r107/metric_ci.tsv`
- `rare-cell-hspc-hierarchy-stage1/experiments/exp_19_b3_frozen_latent_view_sweep/artifacts/runs/r119/summary.tsv`
- `rare-cell-hspc-hierarchy-stage1/experiments/exp_20_pca30_b3_safety_audit/artifacts/runs/r120/calibration_summary.tsv`
- `rare-cell-hspc-hierarchy-stage1/experiments/exp_35_pca30_b3_scgpt_fusion/artifacts/runs/r13x_wholehuman_pca400_linear_fusion_refine_v1/summary.tsv`

### 보조 분석 파일

- `rare-cell-hspc-hierarchy-stage1/experiments/exp_24_pair_error_anatomy/artifacts/runs/r124/donor_pair_error_summary.tsv`
- `rare-cell-hspc-hierarchy-stage1/experiments/exp_25_anchor_imbalance_donor_audit/artifacts/runs/r125/anchor_pair_balance_summary.tsv`
- `rare-cell-hspc-hierarchy-stage1/experiments/exp_26_separability_marker_audit/artifacts/runs/r126/pair_separability_overall.tsv`
- `rare-cell-hspc-hierarchy-stage1/experiments/exp_30_scgpt_embedding_extract/artifacts/runs/r130/embedding_manifest.tsv`
- `rare-cell-hspc-hierarchy-stage1/code/r1337_pca30_b3_scgpt_linear_fusion.py`

## References

<div class="reference-list" markdown="1">

<ol>
  <li id="ref-chspc-collection">Human circulating hematopoietic stem and progenitor cells in aging, cytopenia and MDS. <em>CELLxGENE collection</em>. DOI: <a href="https://doi.org/10.1038/s41591-025-03716-5">10.1038/s41591-025-03716-5</a></li>
  <li id="ref-scvi">Lopez, R. et al. <strong>Deep generative modeling for single-cell transcriptomics</strong>. <em>Nature Methods</em> 15, 1053-1058 (2018). DOI: <a href="https://doi.org/10.1038/s41592-018-0229-2">10.1038/s41592-018-0229-2</a></li>
  <li id="ref-scgpt">Cui, H. et al. <strong>scGPT: toward building a foundation model for single-cell multi-omics using generative AI</strong>. <em>Nature Methods</em> (2024). DOI: <a href="https://doi.org/10.1038/s41592-024-02201-0">10.1038/s41592-024-02201-0</a></li>
</ol>

</div>

## Experiment Resources

<div class="reference-list" markdown="1">

- 이 글의 중심 `lab_path`는 `experiment-lab/projects/rare-cell-hspc-hierarchy-stage1`이다.
- 이 글의 해석에는 `rare-cell-hspc-hierarchy-stage0`와 `rare-cell-hspc-hierarchy-stage1`의 최종 보고서와 artifact를 함께 사용했다.
- 본문 핵심 수치는 주로 `summary.tsv`, `metric_ci.tsv`, `calibration_summary.tsv`, `sensitivity_summary.tsv` 계열에서 가져왔다.
- boundary 분석을 더 자세히 볼 때는 `pair_confusion.tsv`, `sibling_*`, `donor_pair_error_summary.tsv`, `pair_separability_overall.tsv` 계열이 유용하다.
- 최신 최종 조합 해석은 `FINAL_WINNER_MANIFEST.md`, `STAGE1_FINAL_CLOSEOUT_REPORT_KO.md`, `exp_35_pca30_b3_scgpt_fusion` 계열 산출물에 기대고 있다.

</div>

## Citation

이 글을 인용할 때는 아래 형식을 사용할 수 있다.

```text
Ilho Ahn, "HSPC hierarchy benchmark 설계와 rare-cell classification 적용", Mini Research, Apr 21, 2026.
```

또는 BibTeX 형식으로는 다음처럼 적을 수 있다.

```bibtex
@article{ahn2026hspchierarchylineage,
  author = {Ilho Ahn},
  title = {HSPC hierarchy benchmark 설계와 rare-cell classification 적용},
  journal = {Mini Research},
  year = {2026},
  month = apr,
  url = {https://muted-color.github.io/research/2026/04/21/hspc-hierarchy-benchmark-lineage/}
}
```
