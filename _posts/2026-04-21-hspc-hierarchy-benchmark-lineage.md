---
lang: ko
title: "HSPC low-anchor 분류에서 scGPT 결합의 순위 성능과 calibration"
date: 2026-04-21 12:00:00 +0900
last_modified_at: 2026-09-06 08:21:33 +0900
categories: ["SINGLE CELL ML"]
tags: [scrna, hspc, rare-cell, benchmark, semi-supervised, scvi, scgpt]
lab_path: "experiment-lab/projects/rare-cell-hspc-hierarchy-stage1"
hidden: true
excerpt: "적은 라벨로 새로운 donor의 HSPC 상태를 분류한 비교에서, 단독으로 기준선보다 약한 scGPT도 결합 시 순위 성능을 보완했지만 calibration은 악화됐다."
description: "normal cHSPC donor-heldout low-anchor 분류에서 scGPT 단독은 PCA 기반 기준선보다 낮았지만 중첩 검증 결합은 macro AUPRC를 높였으며, calibration과 확률 오차는 악화된 결과 및 평가 범위를 정리한다."
permalink: /research/2026/04/21/hspc-hierarchy-benchmark-lineage/
image: /assets/images/posts/hspc-hierarchy-benchmark-lineage/ig_0a0b41422bd564750169eb7876cf808191b805b89709616bf2.png
image_alt: "HSPC hierarchy benchmark에서 세포 집단 분기와 rare-cell boundary를 파란색으로 강조한 대표 이미지"
hero_image: /assets/images/posts/hspc-hierarchy-benchmark-lineage/ig_0a0b41422bd564750169eb7876cf808191b805b89709616bf2.png
hero_alt: "HSPC hierarchy benchmark에서 여러 세포 집단이 분기하고 오른쪽 rare-cell boundary가 파란색으로 강조된 hero 이미지"
hero_frame: true
---

이 글은 세포 집단, 라벨 구조, donor 분할, 라벨 예산을 고정하고 rare-cell 분류 방법을 비교한다. 여기서 rare-cell classification은 normal cHSPC 안의 가까운 세포 상태(fine state)를 **적은 공개 라벨(anchor)** 로 복원하는 low-anchor fine-state recovery를 뜻한다. 실제 임상 prevalence를 추정하는 평가는 아니다.

분석 대상은 normal circulating hematopoietic stem and progenitor cells (cHSPC) 안의 가까운 세포 상태를 새 donor에서 분류하는 조건이다 <a class="citation-ref" href="#ref-chspc-paper" aria-label="Reference 1">[1]</a>. 평가 질문은 **단독 성능이 기준선보다 낮은 scGPT 표현도 예측 확률의 결합에서는 보완 신호를 주는지, 그때 순위 성능과 확률 품질이 함께 좋아지는지**다.

기록된 outer-test 집계에서 scGPT 단독의 macro AUPRC는 PCA 기반 기준선보다 낮았지만, 두 방법의 예측 확률을 결합하면 높아졌다. 반면 confidence와 실제 정답률의 정합성을 나타내는 calibration과 확률 예측 오차는 나빠졌다. 이 글은 남아 있는 방법 설명과 집계값을 바탕으로 이 차이를 정리하며, 개별 예측이나 실행별 기록을 재검증한 결과는 아니다.

> **HSPC**
>
> HSPC는 혈액 세포 계열로 분화할 수 있는 stem/progenitor population을 가리킨다. 이 글에서는 normal cHSPC 안의 가까운 progenitor state를 구분하는 문제로 사용했다.

<aside class="research-question" aria-label="실험 초점">
  <p class="research-question__label">Experiment Focus</p>
  <p>normal cHSPC 안의 <code>HSPC hierarchy</code>를 donor-heldout low-anchor fine-state recovery 평가로 고정하고, local expression geometry와 scGPT-derived 순위 신호가 어떤 역할을 하는지 확인한다.</p>
</aside>

{% include model-mention-cards.html label="사용한 주요 리소스" aria_label="사용한 데이터셋과 single-cell 모델 리소스" models="cHSPC CELLxGENE collection|CELLxGENE|https://cellxgene.cziscience.com/collections/5542eeb0-96ef-4ab9-95ea-eb6abc178461;scGPT|tdc/scGPT|https://huggingface.co/tdc/scGPT" %}

> **cHSPC CELLxGENE collection**
>
> 이 benchmark는 public CELLxGENE collection의 circulating HSPC 데이터에서 normal cHSPC subset을 사용해 구성했다 <a class="citation-ref" href="#resource-chspc-cellxgene" aria-label="Experiment resource 1">[resource]</a>. 핵심은 collection 전체를 평가하는 것이 아니라, donor-heldout low-anchor 조건에서 fine-state recovery가 가능한 평가 조건을 고정하는 데 있다.

평가 sample은 방법 비교를 위해 fine label별 셀 수를 제한해 구성했다. 주된 난점은 class rarity 자체보다 새 donor에서 적은 anchor label만으로 가까운 progenitor state를 복원하는 데 있다.

## 요약

- Normal cHSPC의 6개 fine state를 donor-heldout·inductive 조건에서 분류했다. 기록된 평가 규모는 26,681 cells, 90 donors이며, 라벨 예산은 class당 20개 anchor였다.
- 30차원 PCA 위의 label propagation 기준선인 `pca30-B3`는 mean macro AUPRC `0.899463`, mean ECE `0.023626`, mean Brier `0.220972`를 기록했다.
- `whole-human scGPT PCA400-linear` 단독의 mean macro AUPRC는 `0.892713`이었지만, 중첩 검증으로 가중치를 고른 결합에서는 `0.914734`로 높아졌다.
- 결합의 mean ECE와 mean Brier는 각각 `0.090729`, `0.238089`로 나빠졌다. 따라서 **순위 성능을 보완한 결합과 확률 품질의 비교 기준을 구분**한다.
- 이 차이는 보존된 집계값의 관찰이다. 현재 노트에는 donor fold·anchor seed별 결과와 결합 개선의 신뢰구간이 제시되어 있지 않아 반복 안정성은 판단하지 않는다.

## Experimental Setup

### 설계 배경

HSPC hierarchy는 같은 큰 세포 집단 안의 가까운 progenitor state를 구분하는 평가다. 상위 라벨만 남기고 세부 라벨을 복원하는 `parent-label collapse`, donor 분리, 적은 anchor label을 함께 적용할 수 있어 비교 대상으로 사용했다. Table 1은 평가 조건을 정할 때 고려한 항목을 정리한다.

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
          <td>초기 성립 가능성을 점검할 수 있음</td>
          <td>복잡한 방법을 적용하기 전에 이 평가 문제가 너무 쉽거나 불가능한 설정이 아닌지 확인할 수 있었다</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> HSPC hierarchy를 donor-heldout low-anchor fine-state recovery task로 구성할 때 사용한 설계 조건과 해석상 역할.</figcaption>
</figure>

### 평가 설계

이 task의 입력은 cell-by-gene expression matrix에서 나온 single-cell expression vector다. 각 값은 해당 cell에서 특정 gene의 mRNA가 얼마나 관측됐는지를 나타내며, DNA 서열 자체가 아니라 cell state를 반영하는 transcriptome signal로 해석한다.

이 benchmark는 아래 네 가지 축을 함께 묻도록 구성했다.

- 가까운 sibling state를 실제로 구분해야 한다.
- 같은 donor를 다시 맞히지 않고 새 donor에서도 일반화돼야 한다.
- 라벨이 충분하지 않은 low-anchor 조건을 견뎌야 한다.
- 테스트 셀을 학습 때 직접 보지 않는 inductive setting이어야 한다.

실제 평가 조건은 아래처럼 고정했다.

- dataset: `cHSPC Illumina`
- condition: `diagnosis == normal`
- population: `hematopoietic precursor cell`
- fine labels: `MEBEMP-L`, `CLP`, `ERYP`, `BEMP`, `GMP-L`, `NKTDP`
- split: `donor-heldout`
- mode: `inductive-only`
- primary budget: `20 anchors per class`

여기서 `donor-heldout`은 같은 donor의 셀이 train과 test에 동시에 들어가지 않게 막는 설정이다. 다시 말해, 같은 사람 안에서 비슷한 셀을 다시 맞히는 문제가 아니라 **새 donor에서도 같은 패턴이 유지되는지**를 보는 더 엄격한 평가다. `anchor`는 학습할 때 정답 라벨이 공개된 소수의 셀이고, `inductive`는 테스트용 셀을 학습 때 직접 보지 않고 예측하는 방식이다.

구현상 inductive 조건은 fold별 train donor에서만 preprocessing과 propagation graph를 fit하는 방식으로 고정했다. Normalization, 고변이 유전자(highly variable gene, HVG) 선택, scaling, PCA fit, label propagation graph는 train donor cell만 사용했고, held-out donor cell은 fold별 frozen transform을 거쳐 prediction과 evaluation에만 들어갔다. 따라서 본 평가의 B3는 held-out donor의 unlabeled expression을 graph construction에 넣는 transductive label propagation이 아니라, train graph에서 학습한 확률 함수를 held-out donor cell에 적용하는 induction-style 비교로 해석한다 <a class="citation-ref" href="#ref-label-propagation" aria-label="Reference 2">[2]</a>.

이 조건은 학습 donor의 세포를 다시 분류하는 성능과 새 donor의 상태를 예측하는 성능을 구분하기 위한 것이다.

### 평가 규모와 기록 범위

기록된 본 평가 규모는 `26,681` cells, `90` donors, `6` fine labels다. 초기 비교에는 anchor prior, nearest centroid와 linear classifier를 두었고, metadata-only 점검과 Ultima cross-platform 비교도 수행했다. 다만 이 보조 비교의 지표·집계 명세는 충분히 남아 있지 않아 아래의 세 방법 비교를 중심으로 해석한다.

본문의 순위 성능은 별도로 기록된 **mean macro AUPRC**, calibration은 **mean ECE**, 확률 예측 오차는 **mean Brier**로 비교한다. Macro AUPRC는 클래스별 precision–recall 성능의 평균이며 높을수록 좋다. ECE는 confidence와 실제 정답률의 차이, Brier는 예측 확률의 오차를 요약하며 낮을수록 좋다 <a class="citation-ref" href="#ref-calibration" aria-label="Reference 3">[3]</a>. 실행별 가중 방식이나 ECE bin 설정 등 세부 집계 규칙은 현재 기록에서 확인할 수 없다.

기존 노트의 `primary score`는 계산식과 split별 집계 규칙을 확인할 수 없어 핵심 결론의 근거로 사용하지 않는다. 해당 수치와 보조 비교는 Appendix Table 4에 구분해 보존했다.

## Results

### PCA 기반 기준선

`pca50-B3`와 `pca30-B3`는 expression matrix를 각각 50차원과 30차원 PCA 표현으로 줄인 뒤 inductive kNN label propagation을 적용한 설정이다. Table 2의 집계에서 `pca30-B3`는 macro AUPRC가 높고 ECE와 Brier가 낮았다. 이후 scGPT 비교에는 이 설정을 기준선으로 사용했다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>조건</th>
          <th class="align-right">mean macro AUPRC</th>
          <th class="align-right">mean ECE</th>
          <th class="align-right">mean Brier</th>
          <th class="align-right">Pair confusion<br><span class="table-note-inline"><code>MEBEMP-L &lt;-&gt; ERYP</code></span></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>pca50-B3</code></td>
          <td class="align-right"><code>0.895621</code></td>
          <td class="align-right"><code>0.027164</code></td>
          <td class="align-right"><code>0.226867</code></td>
          <td class="align-right"><code>0.278660</code></td>
        </tr>
        <tr>
          <td><code>pca30-B3</code></td>
          <td class="align-right"><code>0.899463</code></td>
          <td class="align-right"><code>0.023626</code></td>
          <td class="align-right"><code>0.220972</code></td>
          <td class="align-right"><code>0.266080</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> 같은 label propagation을 두 PCA 공간에서 비교한 기록된 집계값이다. Macro AUPRC는 높을수록 좋고 ECE와 Brier는 낮을수록 좋다. Pair confusion은 두 라벨 사이의 오류에 대한 보조 기록이며, 분모와 집계 규칙이 확인되지 않아 절대 비율로 확대해 해석하지 않는다.</figcaption>
</figure>

이 집계에서 PCA 차원 변경은 순위 성능과 확률 품질 양쪽에 유리한 방향이었다. 그러나 노이즈 감소나 lineage geometry의 보존을 직접 측정한 결과는 아니므로, 이를 차원 축소가 작동한 원인으로 확정하지 않는다.

### scGPT 표현의 비교 범위

Cui et al.의 **scGPT**는 single-cell transcriptomic data를 대상으로 학습된 foundation model이다 <a class="citation-ref" href="#ref-scgpt" aria-label="Reference 5">[5]</a>. 여기서는 scGPT를 새로 학습하지 않고, whole-human checkpoint의 embedding을 fold-local PCA400으로 줄인 뒤 linear classifier의 예측 확률을 사용했다.

보조 탐색에는 scVI latent와 label propagation <a class="citation-ref" href="#ref-scvi" aria-label="Reference 4">[4]</a>, scGPT raw embedding 위의 linear classifier와 label propagation도 포함했다. 이들의 요약 점수는 Appendix Table 4에 남겼지만, 지표 정의를 복구하지 못한 비교에서 표현 모델 전반의 우열이나 오류 원인을 결론내리지는 않는다. 아래에서는 macro AUPRC·ECE·Brier가 함께 남아 있는 `pca30-B3`, `whole-human scGPT PCA400-linear`, 두 방법의 결합을 비교한다.

### 보완적 순위 신호의 결합

결합은 `pca30-B3`와 `whole-human scGPT PCA400-linear`의 예측 확률을 함께 사용하는 방식이다. 두 표현을 하나의 embedding으로 합친 비교는 아니다.

중첩 검증은 결합 가중치를 고르는 단계와 최종 성능을 측정하는 단계를 donor 단위로 분리했다. 각 outer fold에서 test donor를 먼저 제외하고, 남은 train donor 안에 inner training과 validation donor를 나눴다. 결합 가중치는 inner validation에서 선택했으며, 이때 HVG selection, scaling, PCA도 inner-train donor만으로 다시 맞췄다. Outer test donor는 가중치 선택에 쓰지 않고 마지막 평가에만 사용했다. Table 3은 이 절차로 기록된 outer-test 집계다. 결합의 macro AUPRC는 `0.914734`로 기준선의 `0.899463`보다 높았지만, ECE와 Brier는 나빠졌다. 가중치 후보와 선택 지표의 세부 명세는 현재 기록에서 확인할 수 없다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>방법</th>
          <th class="align-right">mean macro AUPRC</th>
          <th class="align-right">mean ECE</th>
          <th class="align-right">mean Brier</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>pca30-B3</code></td>
          <td class="align-right"><code>0.899463</code></td>
          <td class="align-right"><code>0.023626</code></td>
          <td class="align-right"><code>0.220972</code></td>
        </tr>
        <tr>
          <td><code>whole-human scGPT</code><br><span class="table-note-inline"><code>PCA400-linear</code></span></td>
          <td class="align-right"><code>0.892713</code></td>
          <td class="align-right"><code>0.071926</code></td>
          <td class="align-right"><code>0.315177</code></td>
        </tr>
        <tr>
          <td><code>pca30-B3</code><br><span class="table-note-inline">+ <code>whole-human scGPT PCA400-linear</code><br>중첩 검증 결합</span></td>
          <td class="align-right"><code>0.914734</code></td>
          <td class="align-right"><code>0.090729</code></td>
          <td class="align-right"><code>0.238089</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> <code>pca30-B3</code> 기준, <code>whole-human scGPT PCA400-linear</code> 단독, 중첩 검증으로 고른 결합의 outer-test 성능 비교. Macro AUPRC는 높을수록 좋고, ECE와 Brier는 낮을수록 좋다. 기록된 집계값이며 반복 간 분산이나 결합 개선의 신뢰구간은 포함하지 않는다.</figcaption>
</figure>

Figure 1은 Table 3의 세 지표를 나란히 보여 준다. scGPT 단독의 macro AUPRC는 기준선보다 낮지만 결합에서는 높아져, 두 예측의 결합이 순위 성능을 보완했음을 시사한다. 반면 ECE는 `0.023626 → 0.090729`, Brier는 `0.220972 → 0.238089`로 높아졌다. 순위 개선과 확률 품질 개선은 이 비교에서 같은 방향으로 움직이지 않았다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/hspc-hierarchy-benchmark-lineage/scgpt-fusion-ranking-calibration.svg" alt="pca30-B3, whole-human scGPT PCA400-linear, 중첩 검증 결합의 macro AUPRC, ECE, Brier를 비교한 세 패널 점 그래프. 결합의 AUPRC가 가장 높지만 ECE와 Brier는 pca30-B3보다 높다.">
  <figcaption><strong>Figure 1.</strong> Table 3에 남아 있는 세 방법의 집계값 비교. Macro AUPRC는 높을수록 좋고 ECE와 Brier는 낮을수록 좋다. AUPRC 축은 0.89–0.92, ECE 축은 0–0.10, Brier 축은 0–0.35이며 패널 사이의 거리 크기를 직접 비교하지 않는다. 현재 노트에 반복별 자료가 제시되어 있지 않아 오차막대는 표시하지 않았다.</figcaption>
</figure>

### 남은 경계: `MEBEMP-L <-> ERYP`

기존 노트에서 주요 오류 경계로 남은 라벨 쌍은 `MEBEMP-L <-> ERYP`였다. 별도 donor-heldout pairwise 비교에는 mean pair AP `0.9233`, mean pair AUC `0.9177`이 기록되어 있다. 이 두 라벨만을 구분한 성능은 전체 6-class 분류와 다른 평가이므로, 이 값으로 결합이 해당 오류를 해결했다고 해석하지 않는다. Table 3의 집계만으로는 어떤 donor나 라벨에서 결합의 이득과 손실이 발생했는지도 구분할 수 없다.

## 해석

이 비교에서 scGPT 단독의 낮은 macro AUPRC는 결합의 가치를 배제하지 않았다. 두 방법의 예측 확률을 결합한 집계는 순위 성능의 보완 가능성을 보여 주었다. 다만 개별 예측을 다시 분석하지 않았으므로 어떤 오류의 상보성이 이를 만들었는지까지 확인한 것은 아니다.

확률을 threshold나 후속 의사결정에 사용하는 경우에는 순위 성능 외에 calibration과 확률 오차도 필요하다. 관측된 세 방법 중 `pca30-B3`는 ECE와 Brier가 가장 낮은 비교 기준으로 남았고, 결합은 macro AUPRC가 가장 높은 설정이었다. 어느 한 방법이 모든 평가 축에서 우세한 결과는 아니었다.

결합 후 별도 calibration을 적용한 결과는 없어, 순위 개선과 확률 품질 악화를 불가피한 trade-off로 일반화하지 않는다. 이 글이 남기는 관찰은 **단독 표현의 성능, 결합의 순위 성능, 예측 확률의 품질을 분리해 비교할 필요가 있다는 점**이다.

## 한계

- 결과는 normal cHSPC의 여섯 fine state를 적은 anchor label로 분류한 donor-heldout 조건에 한정된다. 실제 임상 prevalence에서의 희귀 세포 검출 성능이나 scGPT의 일반 성능을 평가한 결과는 아니다.
- 본문은 기존 노트의 방법 설명과 집계값을 정리했다. 개별 예측, donor fold·anchor seed별 결과, 세부 집계 규칙을 재검증하지 못해 결합 개선의 반복 안정성이나 신뢰구간을 제시하지 않는다.
- 중첩 검증 기록은 결합 가중치 선택에 관한 것이다. 가중치 후보·선택 지표와 다른 표현 설정의 선택 과정까지 동일하게 분리했는지는 현재 기록만으로 확인할 수 없다.
- 정의가 확인되지 않은 primary score와 과거의 bootstrap 구간은 보조 기록으로 구분했다. 이를 본문 macro AUPRC 차이의 불확실성으로 대신 사용할 수 없다.
- 결합 후 calibration을 다시 보정한 비교와 donor·class별 오차 분석은 포함하지 않았다.

## Appendix: 평가 조건

기록에 남아 있는 평가 조건은 Appendix Table 1, 방법명은 Appendix Table 2, 지표의 역할은 Appendix Table 3에 정리한다. 정의나 집계 규칙이 확인되지 않은 기존 점수는 Appendix Table 4에서 별도로 보존한다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>항목</th>
          <th>조건</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>대상 데이터</strong></td>
          <td>normal cHSPC 안의 hematopoietic precursor cell population</td>
        </tr>
        <tr>
          <td><strong>분류 대상 라벨</strong></td>
          <td><code>MEBEMP-L</code>, <code>CLP</code>, <code>ERYP</code>, <code>BEMP</code>, <code>GMP-L</code>, <code>NKTDP</code></td>
        </tr>
        <tr>
          <td><strong>평가 split</strong></td>
          <td><code>donor-heldout</code>. 같은 donor의 cell이 train과 test에 동시에 들어가지 않도록 분리했다.</td>
        </tr>
        <tr>
          <td><strong>라벨 조건</strong></td>
          <td><code>20 anchors per class</code>를 primary budget으로 사용했다. Anchor는 학습 시 정답 라벨이 공개된 소수 cell을 뜻한다.</td>
        </tr>
        <tr>
          <td><strong>예측 조건</strong></td>
          <td><code>inductive-only</code>. test cell은 학습 때 직접 보지 않고 예측한다.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 1.</strong> 본문 결과를 해석할 때 고정한 HSPC hierarchy 평가 조건.</figcaption>
</figure>

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>이름</th>
          <th>본문에서의 역할</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>anchor prior</code></td>
          <td>anchor label 비율만 사용하는 prior baseline이다. 초기 가능성 점검과 본 평가에서 비교 기준으로 사용했다.</td>
        </tr>
        <tr>
          <td><code>nearest centroid</code></td>
          <td>anchor 평균 위치에 가장 가까운 라벨을 주는 prototype matching baseline이다.</td>
        </tr>
        <tr>
          <td><code>cheap classifier</code></td>
          <td>초기 가능성 점검에서 expression signal이 남아 있는지 확인한 간단한 classifier다.</td>
        </tr>
        <tr>
          <td><code>cheap linear classifier</code></td>
          <td>본 평가에서 marker/prototype signal만으로 충분한지 확인한 linear baseline이다.</td>
        </tr>
        <tr>
          <td><code>pca30-B3</code></td>
          <td>30차원 PCA 공간에서 inductive kNN label propagation을 적용한 in-domain calibration 비교 기준이다.</td>
        </tr>
        <tr>
          <td><code>whole-human scGPT</code><br><span class="table-note-inline"><code>PCA400-linear</code></span></td>
          <td>whole-human scGPT embedding을 fold-local PCA400으로 줄인 뒤 linear probability를 만든 보완 신호다.</td>
        </tr>
        <tr>
          <td>중첩 검증 결합<br><span class="table-note-inline"><code>nested-selected fusion</code></span></td>
          <td><code>pca30-B3</code> probability와 <code>whole-human scGPT PCA400-linear</code> probability를 결합하되, fusion weight를 outer train donor 안의 inner validation에서 고른 비교다.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 2.</strong> 본문과 표에서 반복해서 쓰는 방법명과 비교상 역할.</figcaption>
</figure>

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>지표 또는 분석</th>
          <th>해석</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>macro AUPRC</code></td>
          <td>각 class를 고르게 본 뒤 평균낸 ranking 성능이다. rare label이 섞인 설정에서 class별 성능을 함께 보기 위해 사용했다.</td>
        </tr>
        <tr>
          <td><code>ECE</code></td>
          <td>prediction confidence와 실제 정답률의 차이를 요약하는 calibration 지표다. 낮을수록 좋다. Bin 설정 등 세부 계산 조건은 현재 기록에서 확인할 수 없다.</td>
        </tr>
        <tr>
          <td><code>Brier</code></td>
          <td>예측 확률의 오차를 요약한 지표다. 낮을수록 좋다. Class·fold별 가중과 normalization의 세부 조건은 현재 기록에서 확인할 수 없다.</td>
        </tr>
        <tr>
          <td><code>MEBEMP-L &lt;-&gt; ERYP</code> pair confusion</td>
          <td>두 라벨 사이의 오류에 대한 보조 기록이다. 분모와 fold별 집계 규칙이 확인되지 않아, 표의 값은 당시 기록 범위에서만 제시한다.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 3.</strong> 본문 수치를 읽을 때 필요한 metric과 caveat.</figcaption>
</figure>

### 기존 요약 점수와 보조 비교

Appendix Table 4의 primary score는 기존 노트에 남아 있는 요약 점수다. 계산식과 split별 집계 규칙을 확인할 수 없으며, macro AUPRC와 같은 지표로 취급하지 않는다. 본문의 순위·확률 품질 비교는 Table 2와 Table 3에 별도로 기록된 지표를 사용했다.

<figure class="table-figure table-figure--compact-metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--compact-two-col">
      <thead>
        <tr><th>기존 설정</th><th class="align-right">기록된 primary score<br><span class="table-note-inline">정의 미확인</span></th></tr>
      </thead>
      <tbody>
        <tr><td><code>pca50-B3</code></td><td class="align-right">0.896652</td></tr>
        <tr><td><code>pca30-B3</code></td><td class="align-right">0.902323</td></tr>
        <tr><td>scVI latent<br><span class="table-note-inline">+ label propagation</span></td><td class="align-right">0.893955</td></tr>
        <tr><td>whole-human scGPT<br><span class="table-note-inline">raw linear</span></td><td class="align-right">0.880685</td></tr>
        <tr><td>whole-human scGPT<br><span class="table-note-inline">raw label propagation</span></td><td class="align-right">0.874831</td></tr>
        <tr><td>whole-human scGPT<br><span class="table-note-inline">PCA400-linear</span></td><td class="align-right">0.894952</td></tr>
        <tr><td><code>pca30-B3</code> + scGPT<br><span class="table-note-inline">중첩 검증 결합</span></td><td class="align-right">0.913785</td></tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 4.</strong> 기존 요약 점수의 보존 기록. 지표 정의를 확인하지 못했으므로 방법의 일반적 우열이나 본문의 macro AUPRC 개선을 입증하는 근거로 사용하지 않는다.</figcaption>
</figure>

기존 노트의 보조 수치도 다음과 같이 남아 있다. 아래 gain과 신뢰구간의 실행별 표본·집계 명세는 확인하지 못했으므로 새로 검증한 결과로 제시하지 않는다.

- B3와 가장 강한 단순 기준선의 paired gain: `+0.0255`, 기록된 95% CI `(+0.0096, +0.0314)`. Gain의 지표·집계 명세는 확인되지 않았다.
- PCA30–PCA50 primary score median gain: `+0.0097`, 기록된 bootstrap 95% CI `(+0.0044, +0.0155)`. Table 2의 평균 macro AUPRC 차이와는 다른 통계다.
- 같은 PCA 비교의 pair confusion delta: `−0.0219`, 기록된 pair bootstrap 95% CI `(−0.0337, −0.0120)`. Table 2의 집계값 차이와 같다고 가정하지 않는다.
- 보조 donor 점검에는 metadata-only max AUC `0.582`, donor leakage AUC `0.559952`가 각각 기록되어 있다. 서로 다른 점검이며, 이 값만으로 donor 관련 shortcut이 배제됐다고 결론내리지 않는다.
- All-diagnosis gain `+0.030604`, Ultima gain `+0.025175`, scVI latent + label propagation의 mean ECE `0.069573`도 기록되어 있다. 두 민감도 비교에서는 calibration이 cheap linear classifier보다 나빠지지 않았다고 서술했으나, 개별 결과를 재검증하지 못했다.

## References

<div class="reference-list" markdown="1">

<ol>
  <li id="ref-chspc-paper">Furer, N. et al. <strong>A reference model of circulating hematopoietic stem cells across the lifespan with applications to diagnostics</strong>. <em>Nature Medicine</em> 31, 2442-2451 (2025). DOI: <a href="https://doi.org/10.1038/s41591-025-03716-5">10.1038/s41591-025-03716-5</a></li>
  <li id="ref-label-propagation">Zhu, X. & Ghahramani, Z. <strong>Learning from labeled and unlabeled data with label propagation</strong>. Technical Report CMU-CALD-02-107 (2002). <a href="https://reports-archive.adm.cs.cmu.edu/anon/cald/abstracts/02-107.html">CMU report</a></li>
  <li id="ref-calibration">Guo, C. et al. <strong>On Calibration of Modern Neural Networks</strong>. <em>Proceedings of Machine Learning Research</em> 70, 1321-1330 (2017). <a href="https://proceedings.mlr.press/v70/guo17a.html">PMLR</a></li>
  <li id="ref-scvi">Lopez, R. et al. <strong>Deep generative modeling for single-cell transcriptomics</strong>. <em>Nature Methods</em> 15, 1053-1058 (2018). DOI: <a href="https://doi.org/10.1038/s41592-018-0229-2">10.1038/s41592-018-0229-2</a></li>
  <li id="ref-scgpt">Cui, H. et al. <strong>scGPT: toward building a foundation model for single-cell multi-omics using generative AI</strong>. <em>Nature Methods</em> 21, 1470-1480 (2024). DOI: <a href="https://doi.org/10.1038/s41592-024-02201-0">10.1038/s41592-024-02201-0</a></li>
</ol>

</div>

## Experiment Resources

<div class="reference-list" markdown="1">

<ul>
  <li id="resource-chspc-cellxgene">cHSPC CELLxGENE collection. <strong>Human circulating hematopoietic stem and progenitor cells in aging, cytopenia and MDS</strong>. <a href="https://cellxgene.cziscience.com/collections/5542eeb0-96ef-4ab9-95ea-eb6abc178461">CELLxGENE collection</a></li>
  <li id="resource-scgpt-hf">Therapeutics Data Commons. <strong>tdc/scGPT</strong>. <a href="https://huggingface.co/tdc/scGPT">Hugging Face model</a></li>
  <li id="resource-scgpt-code">bowang-lab. <strong>scGPT codebase</strong>. <a href="https://github.com/bowang-lab/scGPT">GitHub repository</a></li>
</ul>

</div>

## Citation

이 글을 인용할 때는 아래 형식을 사용할 수 있다.

```text
Ilho Ahn, "HSPC low-anchor 분류에서 scGPT 결합의 순위 성능과 calibration", Ilho’s Notes, Apr 21, 2026.
```

또는 BibTeX 형식으로는 다음처럼 적을 수 있다.

```bibtex
@article{ahn2026hspchierarchylineage,
  author = {Ilho Ahn},
  title = {HSPC low-anchor 분류에서 scGPT 결합의 순위 성능과 calibration},
  journal = {Ilho’s Notes},
  year = {2026},
  month = apr,
  url = {https://muted-color.github.io/research/2026/04/21/hspc-hierarchy-benchmark-lineage/}
}
```
