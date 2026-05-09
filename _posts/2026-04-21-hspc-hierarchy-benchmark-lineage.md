---
title: "HSPC hierarchy low-anchor benchmark: pca30-B3와 nested scGPT fusion"
date: 2026-04-21 12:00:00 +0900
last_modified_at: 2026-05-10 07:27:22 +0900
categories: ["SINGLE CELL ML"]
tags: [scrna, hspc, rare-cell, benchmark, semi-supervised, scvi, scgpt]
lab_path: "experiment-lab/projects/rare-cell-hspc-hierarchy-stage1"
excerpt: "normal cHSPC fine-state recovery에서 pca30-B3 reference와 nested scGPT fusion의 outer-test primary-score 개선, calibration과 probability-error 한계를 정리한다."
description: "normal cHSPC fine-state recovery를 donor-heldout low-anchor benchmark로 구성하고, pca30-B3 calibrated reference와 whole-human scGPT PCA400-linear nested fusion의 outer-test 결과 및 calibration/probability-error 한계를 정리한다."
permalink: /research/2026/04/21/hspc-hierarchy-benchmark-lineage/
image: /assets/images/posts/hspc-hierarchy-benchmark-lineage/ig_0a0b41422bd564750169eb7876cf808191b805b89709616bf2.png
image_alt: "HSPC hierarchy benchmark에서 세포 집단 분기와 rare-cell boundary를 파란색으로 강조한 대표 이미지"
hero_image: /assets/images/posts/hspc-hierarchy-benchmark-lineage/ig_0a0b41422bd564750169eb7876cf808191b805b89709616bf2.png
hero_alt: "HSPC hierarchy benchmark에서 여러 세포 집단이 분기하고 오른쪽 rare-cell boundary가 파란색으로 강조된 hero 이미지"
hero_frame: true
---

Rare-cell 분류 방법을 검토하려면 먼저 해석 가능한 benchmark가 필요하다. 여기서 benchmark는 데이터셋 선택만이 아니라 세포 집단, 라벨 구조, donor split, label budget을 함께 고정한 평가 환경을 뜻한다. 이 글에서 말하는 rare-cell classification은 실제 임상 prevalence를 추정하는 문제가 아니라, normal cHSPC 안의 가까운 fine state를 **적은 공개 라벨(anchor)** 로 복원하는 low-anchor fine-state recovery 문제에 가깝다.

분석 대상은 normal circulating hematopoietic stem and progenitor cells (cHSPC) 안의 `HSPC (hematopoietic stem and progenitor cells) hierarchy`를 donor-heldout low-anchor fine-state 복원 benchmark로 구성한 설정이다 <a class="citation-ref" href="#ref-chspc-paper" aria-label="Reference 1">[1]</a>. 초점은 새로운 모델 제안이 아니라, task가 방법 비교에 충분히 성립하는지, `pca30-B3` reference가 왜 남았는지, 그리고 `whole-human scGPT PCA400-linear` fusion이 어떤 범위에서 보완 신호를 주는지 정리하는 데 있다.

> **HSPC**
>
> HSPC는 혈액 세포 계열로 분화할 수 있는 stem/progenitor population을 가리킨다. 이 글에서는 normal cHSPC 안의 가까운 progenitor state를 구분하는 문제로 사용했다.

<aside class="research-question" aria-label="실험 초점">
  <p class="research-question__label">Experiment Focus</p>
  <p>normal cHSPC 안의 <code>HSPC hierarchy</code>를 donor-heldout low-anchor fine-state recovery task로 고정하고, local expression geometry와 scGPT-derived ranking signal이 어떤 역할을 하는지 확인한다.</p>
</aside>

{% include model-mention-cards.html label="사용한 주요 리소스" aria_label="사용한 데이터셋과 single-cell 모델 리소스" models="cHSPC CELLxGENE collection|CELLxGENE|https://cellxgene.cziscience.com/collections/5542eeb0-96ef-4ab9-95ea-eb6abc178461;scGPT|tdc/scGPT|https://huggingface.co/tdc/scGPT" %}

> **cHSPC CELLxGENE collection**
>
> 이 benchmark는 public CELLxGENE collection의 circulating HSPC 데이터에서 normal cHSPC subset을 사용해 구성했다 <a class="citation-ref" href="#resource-chspc-cellxgene" aria-label="Experiment resource 1">[resource]</a>. 핵심은 collection 전체를 평가하는 것이 아니라, donor-heldout low-anchor 조건에서 fine-state recovery가 가능한 task 환경을 고정하는 데 있다.

> **범위 주의**
>
> 여기서 rare-cell이라는 표현은 benchmark sample 안의 class prevalence를 그대로 주장하는 말이 아니다. 평가 sample은 방법 비교를 위해 fine label별 셀 수를 제한해 구성했으며, 주된 난점은 class rarity 자체보다 donor-heldout 조건에서 적은 anchor label만으로 가까운 progenitor state를 복원하는 데 있다.

## 요약

- HSPC hierarchy benchmark는 가까운 progenitor state, donor-heldout split, low-anchor 조건을 함께 묶어 새 donor에서도 fine state를 구분해야 하는 평가 문제로 구성했다.
- `pca30-B3`는 primary score `0.902323`, mean ECE `0.023626`으로 가장 안정적인 calibrated reference였다.
- scVI latent, raw scGPT embedding, scGPT 위의 direct label propagation은 reference를 대체하지 못했다. 병목은 단순히 더 복잡한 representation을 쓰는 문제가 아니었다.
- `pca30-B3 + whole-human scGPT PCA400-linear` fusion은 train-only nested selection의 outer-test 평가에서 primary score `0.913785`를 기록했다.
- 다만 fusion의 ECE/Brier는 `pca30-B3`보다 나빠졌다. 따라서 결론은 단일 최종 방법이 아니라, **primary-score fusion 후보와 calibration이 안정적인 reference의 역할 분리**다.

## HSPC hierarchy benchmark

### 설계 배경

rare-cell 분류 문제의 방법론 비교에는 안정적으로 정의된 benchmark가 필요하다. 여기서 benchmark는 단순히 데이터셋 하나를 고르는 일이 아니라, 어떤 세포 집단을 대상으로 삼고, 어떤 라벨 구조를 가리고 복원하게 하며, 어떤 split과 label budget에서 일반화를 볼 것인지 정해 **방법을 적용할 수 있는 task 환경**을 만드는 일에 가깝다.

너무 쉬운 과제에서는 baseline만으로도 성능이 빨리 포화되고, shortcut이 강한 과제에서는 새 방법이 무엇을 배운 것인지 해석하기 어렵다. 따라서 이 단계의 기준은 특정 방법의 즉시 성능 개선이 아니라, **rare-cell 분류 방법을 적용했을 때 개선과 한계를 해석할 수 있는 task 환경의 성립 여부**였다.

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
  <figcaption><strong>Table 1.</strong> HSPC hierarchy를 donor-heldout low-anchor fine-state recovery task로 구성할 때 사용한 설계 조건과 해석상 역할.</figcaption>
</figure>

따라서 HSPC hierarchy는 단순한 데이터셋 선택이 아니라, rare-cell classification 방법을 실제로 적용하고 해석하기 위해 설계한 task 환경이었다. 이후 실험은 이 task를 풀면서 어떤 접근이 실제로 효과가 있었고, 어떤 어려움이 구조적으로 남는지 확인하는 과정에 가깝다.

### 평가 설계

이 task의 입력은 cell-by-gene expression matrix에서 나온 single-cell expression vector다. 각 값은 해당 cell에서 특정 gene의 mRNA가 얼마나 관측됐는지를 나타내며, DNA 서열 자체가 아니라 cell state를 반영하는 transcriptome signal로 해석한다.

이 benchmark는 아래 네 가지 축을 함께 묻도록 구성했다.

- 가까운 sibling state를 실제로 구분해야 한다.
- 같은 donor를 다시 맞히지 않고 새 donor에서도 일반화돼야 한다.
- 라벨이 충분하지 않은 low-anchor 조건을 견뎌야 한다.
- 테스트 셀을 학습 때 직접 보지 않는 inductive setting이어야 한다.

실제 평가 contract는 아래처럼 고정했다.

- dataset: `cHSPC Illumina`
- condition: `diagnosis == normal`
- population: `hematopoietic precursor cell`
- fine labels: `MEBEMP-L`, `CLP`, `ERYP`, `BEMP`, `GMP-L`, `NKTDP`
- split: `donor-heldout`
- mode: `inductive-only`
- primary budget: `20 anchors per class`

여기서 `donor-heldout`은 같은 donor의 셀이 train과 test에 동시에 들어가지 않게 막는 설정이다. 다시 말해, 같은 사람 안에서 비슷한 셀을 다시 맞히는 문제가 아니라 **새 donor에서도 같은 패턴이 유지되는지**를 보는 더 엄격한 평가다. `anchor`는 학습할 때 정답 라벨이 공개된 소수의 셀이고, `inductive`는 테스트용 셀을 학습 때 직접 보지 않고 예측하는 방식이다.

구현상 inductive 조건은 fold별 train donor에서만 preprocessing과 propagation graph를 fit하는 방식으로 고정했다. Normalization, HVG selection, scaling, PCA fit, label propagation graph는 train donor cell만 사용했고, held-out donor cell은 fold별 frozen transform을 거쳐 prediction과 evaluation에만 들어갔다. 따라서 본 평가의 B3는 held-out donor의 unlabeled expression을 graph construction에 넣는 transductive label propagation이 아니라, train graph에서 학습한 확률 함수를 held-out donor cell에 적용하는 induction-style 비교로 해석한다 <a class="citation-ref" href="#ref-label-propagation" aria-label="Reference 2">[2]</a>.

이 조합이 task 환경의 핵심 조건이다. biologically 가까운 sibling state를 새 donor 일반화 조건과 low-anchor 조건 아래에서 묻도록 구성했기 때문에, 단순한 shortcut보다 실제 분류 난이도와 남아 있는 차이를 더 직접적으로 볼 수 있다.

### Benchmark 성립 확인

초기 가능성 점검은 최종 방법을 고르는 단계가 아니라, 이 설정이 방법 비교에 충분한 평가 문제인지 확인하는 단계였다. metadata-only donor-heldout max AUC는 `0.582`였고, low-anchor 조건에서도 expression 기반 classifier가 prior와 centroid baseline을 넘었다. Budget을 바꾸거나 Ultima cross-platform 조건으로 확인해도 방향은 유지됐다.

본 평가에서는 `26,681` cells, `90` donors, `6` fine labels, `20 anchors per class` 조건을 고정했다. `inductive kNN label propagation` (`B3`)은 anchor prior, nearest centroid, cheap linear classifier 중 가장 강한 baseline 대비 paired gain `+0.0255`, `95% CI = (+0.0096, +0.0314)`를 보였다. 따라서 이 benchmark는 단순한 shortcut이나 불가능한 구분 문제가 아니라, 같은 평가 조건 안에서 방법 간 차이를 비교할 여지가 있는 task로 남았다.

## 방법 비교와 reference

### Local Geometry Reference

가장 안정적인 개선은 모델 계열을 바꾸는 것보다 표현 공간을 조정할 때 나왔다. 여기서 `pca50`과 `pca30`은 expression matrix를 각각 50차원 또는 30차원 PCA 표현으로 줄인 뒤, 그 공간에서 label propagation을 적용한 설정이다. 같은 label propagation이라도 `pca50` 대신 `pca30` 위에서 local neighborhood를 만들었을 때 primary score와 pair confusion이 함께 개선됐다. Table 2는 이 차이를 요약한다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table">
      <thead>
        <tr>
          <th>condition</th>
          <th class="align-right">primary score</th>
          <th class="align-right">mean macro AUPRC</th>
          <th class="align-right">mean ECE</th>
          <th class="align-right">mean Brier</th>
          <th class="align-right"><code>MEBEMP-L &lt;-&gt; ERYP</code> pair confusion</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>pca50-B3</code></td>
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
  <figcaption><strong>Table 2.</strong> <code>pca50-B3</code>와 <code>pca30-B3</code>의 primary score, calibration, 핵심 pair confusion 비교. Primary score는 높을수록 좋고, ECE, Brier, pair confusion은 낮을수록 좋다.</figcaption>
</figure>

Figure 1은 같은 비교를 세 지표의 방향성으로 다시 보여준다. `pca30-B3`는 primary score를 올리는 동시에 ECE와 `MEBEMP-L <-> ERYP` pair confusion을 낮췄다.

<figure class="media-figure">
  <img src="/assets/images/posts/hspc-hierarchy-benchmark-lineage/pca30-b3-reference-metrics.svg" alt="pca50-B3와 pca30-B3의 primary score, mean ECE, MEBEMP-L ERYP pair confusion을 비교한 세 지표 dumbbell plot">
  <figcaption><strong>Figure 1.</strong> 같은 label propagation이라도 local neighborhood를 정의하는 PCA 공간에 따라 primary score, calibration, 주요 sibling-boundary confusion이 함께 달라졌다. <code>pca30-B3</code>는 primary score와 calibration을 함께 본 calibrated in-domain reference로 남았다.</figcaption>
</figure>

핵심 비교는 아래와 같다.

- `pca30` vs `pca50` primary score median gain: `+0.0097`
- bootstrap `95% CI = (+0.0044, +0.0155)`
- pair confusion delta: `-0.0219`
- pair bootstrap `95% CI = (-0.0337, -0.0120)`

이 결과는 compact PCA view가 고차원 noise를 줄이고, HSPC lineage와 관련된 local geometry를 더 안정적으로 보존했을 가능성을 시사한다. 이 때문에 `pca30-B3`는 단순히 점수가 높은 설정이 아니라, 이후 비교에서 기준으로 삼을 calibrated in-domain reference가 됐다. 참고로 `macro AUPRC`는 각 클래스를 고르게 보고 평균낸 성능 점수이고, `ECE`는 confidence와 실제 정답률의 정합성을 보는 calibration 지표다 <a class="citation-ref" href="#ref-calibration" aria-label="Reference 3">[3]</a>.

추가 safety / sensitivity도 같은 방향을 지지했다.

- donor leakage AUC: `0.559952`
- all-diagnosis gain: `+0.030604`
- Ultima gain: `+0.025175`
- 두 sensitivity 모두 calibration은 `cheap linear classifier`보다 나빠지지 않았다

### 표현학습 모델의 한계

성능을 갱신하지 못한 시도들은 간단히만 남긴다. 같은 `pca30-B3` 안에서 `k`, `alpha`, pair-local rescue를 바꿔도 의미 있는 gain은 거의 없었다. fast `scVI` latent + label propagation은 primary score `0.893955`, mean ECE `0.069573`으로 `pca30-B3`보다 낮았다 <a class="citation-ref" href="#ref-scvi" aria-label="Reference 4">[4]</a>. 이는 남은 오류가 단순한 propagation hyperparameter 문제나 더 매끄러운 latent 하나로 닫히는 문제가 아니라는 뜻이다.

> **scGPT**
>
> scGPT는 single-cell transcriptomic data를 대상으로 학습된 foundation model이다 <a class="citation-ref" href="#ref-scgpt" aria-label="Reference 5">[5]</a>. 여기서는 scGPT 자체를 새로 학습하거나 일반 성능을 평가한 것이 아니라, scGPT embedding과 PCA400-linear probability가 `pca30-B3` reference를 보완하는지 확인했다.

초기 `scGPT` 결과도 같은 방향이었다. original blood 또는 continual checkpoint의 raw embedding에 linear classifier, prototype, label propagation을 붙인 설정은 모두 reference보다 낮았다. whole-human scGPT raw embedding은 더 나았지만, raw linear `0.880685`, raw label propagation `0.874831`로 여전히 `pca30-B3`를 넘지 못했다. 따라서 foundation-model embedding이 바로 좋은 local propagation graph가 된다고 보기는 어려웠다.

이 결과들이 남기는 핵심은 단순하다. **foundation-model signal은 reference를 대체하기보다, reference가 놓치는 label ranking을 보완할 때 더 유효했다.**

### 보완적 ranking signal의 결합

`whole-human scGPT`를 추가하면서 개선 방향이 바뀌었다. 단독 `scGPT`나 `scGPT` embedding 위의 direct label propagation은 reference를 넘지 못했지만, fold-local PCA400으로 denoise한 뒤 linear probability를 만들면 `pca30-B3`와 다른 오류 구조가 나타났다. 즉, `scGPT`가 reference를 대체한 것이 아니라, `pca30-B3`가 약한 일부 label ranking에서 보완 신호를 제공한 결과로 해석했다.

마지막 비교는 embedding을 교체하는 방식이 아니라 probability를 결합하는 방식이었다. `pca30-B3`는 in-domain local manifold signal을 제공하고, `whole-human scGPT PCA400-linear`는 complementary ranking signal을 제공한다.

Train-only nested selection 평가에서는 각 outer donor-heldout fold의 held-out donor를 마지막 평가에만 쓰고, outer train donor 안에서 다시 inner donor validation을 만들어 fusion weight를 골랐다. 이때 inner validation용 표현도 inner-train donor만으로 HVG, scaling, PCA를 다시 맞췄다. 이 nested-selected fusion은 primary score `0.913785`로 `pca30-B3` 단독을 넘었지만, ECE와 Brier는 여전히 나빠졌다. Table 3은 이 outer-test 평가 결과를 중심으로 정리한다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table">
      <thead>
        <tr>
          <th>setting</th>
          <th class="align-right">primary score</th>
          <th class="align-right">mean macro AUPRC</th>
          <th class="align-right">mean ECE</th>
          <th class="align-right">mean Brier</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>pca30-B3</code></td>
          <td class="align-right"><code>0.902323</code></td>
          <td class="align-right"><code>0.899463</code></td>
          <td class="align-right"><code>0.023626</code></td>
          <td class="align-right"><code>0.220972</code></td>
        </tr>
        <tr>
          <td><code>whole-human scGPT</code><br><span class="table-note-inline"><code>PCA400-linear</code></span></td>
          <td class="align-right"><code>0.894952</code></td>
          <td class="align-right"><code>0.892713</code></td>
          <td class="align-right"><code>0.071926</code></td>
          <td class="align-right"><code>0.315177</code></td>
        </tr>
        <tr>
          <td><code>pca30-B3</code><br><span class="table-note-inline">+ <code>whole-human scGPT PCA400-linear</code><br>nested-selected fusion</span></td>
          <td class="align-right"><code>0.913785</code></td>
          <td class="align-right"><code>0.914734</code></td>
          <td class="align-right"><code>0.090729</code></td>
          <td class="align-right"><code>0.238089</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> <code>pca30-B3</code> reference, <code>whole-human scGPT PCA400-linear</code> 단독, train-only nested-selected fusion의 outer-test 성능 비교. Primary score와 macro AUPRC는 높을수록 좋다. ECE는 낮을수록 calibration이 좋고, Brier는 낮을수록 probability error가 작다.</figcaption>
</figure>

세 결과의 역할은 분리해서 해석했다. `pca30-B3`는 calibration이 안정적인 reference이고, `whole-human scGPT PCA400-linear`는 단독으로는 reference보다 낮지만 보완적인 ranking signal을 제공했다. Nested-selected fusion은 primary score 기준으로 reference를 넘었지만, ECE와 Brier는 나빠졌다. 따라서 이 단계의 결론은 calibration이 안정적인 reference와 primary-score fusion 후보를 분리해서 보는 것이다.

이 결과는 fusion 신호가 held-out outer test에서도 남는다는 점을 지지하지만, calibration까지 포함한 단일 최종 방법으로 승격시키기에는 부족하다.

### 남은 경계: `MEBEMP-L <-> ERYP`

남은 주요 오류 경계는 `MEBEMP-L <-> ERYP`였다. 이 pair는 완전히 분리 불가능한 경계는 아니었다. donor-heldout pairwise separability는 mean pair AP `0.9233`, mean pair AUC `0.9177`로 높았고, anchor 분포도 단순한 imbalance로 설명되지는 않았다.

다만 전체 score가 개선되는 동안에도 이 경계는 반복적으로 남았다. Fusion은 핵심 boundary에서 개선 여지를 보였지만, 이 결과만으로 문제가 해결됐다고 볼 수는 없다. primary score와 일부 ranking은 좋아졌지만, calibration은 `pca30-B3`보다 나빠졌다.

## 결론

**HSPC hierarchy benchmark는 low-anchor fine-state recovery 방법을 실험하기 위한 task 환경으로 성립했다.** 핵심은 데이터셋 하나를 고르는 것이 아니라, 가까운 progenitor state, donor-heldout split, low-anchor label budget, inductive prediction 조건을 함께 고정한 데 있었다. 이 조건에서는 단순 metadata shortcut만으로 문제가 닫히지 않았고, 같은 평가 조건 안에서 방법 간 성능 차이를 비교할 여지도 남아 있었다.

모델 적용에서 얻은 일반화 가능한 신호는 세 가지였다.

1. 가까운 HSPC fine state를 구분할 때는 marker/prototype signal만으로 모든 headroom이 닫히지 않았고, **표현 공간에 따라 local neighborhood 기반 성능과 calibration이 함께 달라졌다.**
2. 표현학습 latent나 foundation-model embedding은 더 넓은 prior를 담고 있더라도, **그 공간이 바로 좋은 decision geometry가 되지는 않았다.**
3. foundation-model signal은 단독 대체보다 기존 local geometry reference가 놓치는 ranking 오류를 보완할 때 더 유효했다.

scGPT signal이 완전히 무효였던 것은 아니다. Whole-human scGPT embedding을 fold-local PCA400으로 정리한 뒤 만든 linear probability는 단독으로는 reference보다 낮았지만, `pca30-B3`와 nested-selected fusion했을 때 outer-test primary score를 높였다. 이 결과는 foundation model의 단독 대체보다, **in-domain local geometry와 foundation-model ranking signal의 보완적 결합**으로 해석한다.

따라서 이 단계의 결론은 단일 최종 방법이 아니라 역할 분리다. **`pca30-B3`는 calibration이 안정적인 in-domain reference로 남았고, `pca30-B3 + whole-human scGPT PCA400-linear`는 nested-selected rule에서 primary score를 높인 fusion 후보로 남았다.** 다만 fusion 이후 ECE와 Brier가 나빠졌기 때문에, 최종 결론은 “primary-score 기준 보완 신호는 확인됐고 calibrated reference는 pca30-B3”로 닫는다.

## Appendix: 평가 조건

본문에는 결과 해석에 필요한 수치만 남겼다. 재현과 해석에 필요한 조건은 아래처럼 benchmark contract, 방법명, metric 정의로 나누어 정리한다.

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
          <td>30차원 PCA 공간에서 inductive kNN label propagation을 적용한 calibrated in-domain reference다.</td>
        </tr>
        <tr>
          <td><code>whole-human scGPT PCA400-linear</code></td>
          <td>whole-human scGPT embedding을 fold-local PCA400으로 줄인 뒤 linear probability를 만든 보완 신호다.</td>
        </tr>
        <tr>
          <td><code>nested-selected fusion</code></td>
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
          <td><code>primary score</code></td>
          <td>본문에서 방법 간 순위를 비교할 때 사용한 중심 성능 지표다.</td>
        </tr>
        <tr>
          <td><code>macro AUPRC</code></td>
          <td>각 class를 고르게 본 뒤 평균낸 ranking 성능이다. rare label이 섞인 설정에서 class별 성능을 함께 보기 위해 사용했다.</td>
        </tr>
        <tr>
          <td><code>ECE</code></td>
          <td>prediction confidence와 실제 정답률의 정합성을 보는 calibration 지표다. Fusion은 primary score를 올렸지만 이 축에서는 불리했다.</td>
        </tr>
        <tr>
          <td><code>Brier</code></td>
          <td>probability prediction error를 보는 지표다. 낮을수록 좋으며, fusion은 primary score 개선에도 이 값이 reference보다 나빠졌다.</td>
        </tr>
        <tr>
          <td><code>MEBEMP-L &lt;-&gt; ERYP</code> pair confusion</td>
          <td>본문에서 반복적으로 남은 sibling-boundary 오류다. 이 경계는 완전히 뒤섞인 문제라기보다 표현과 ranking 신호가 더 필요한 개선 여지로 해석했다.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 3.</strong> 본문 수치를 읽을 때 필요한 metric과 caveat.</figcaption>
</figure>

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
Ilho Ahn, "HSPC hierarchy low-anchor benchmark: pca30-B3와 nested scGPT fusion", Mini Research, Apr 21, 2026.
```

또는 BibTeX 형식으로는 다음처럼 적을 수 있다.

```bibtex
@article{ahn2026hspchierarchylineage,
  author = {Ilho Ahn},
  title = {HSPC hierarchy low-anchor benchmark: pca30-B3와 nested scGPT fusion},
  journal = {Mini Research},
  year = {2026},
  month = apr,
  url = {https://muted-color.github.io/research/2026/04/21/hspc-hierarchy-benchmark-lineage/}
}
```
