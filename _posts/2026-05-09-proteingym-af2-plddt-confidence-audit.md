---
lang: ko
title: "ProteinGym 6-assay에서 WT geometry의 보완 신호와 pLDDT gate 비용"
date: 2026-05-09 09:58:14 +0900
last_modified_at: 2026-09-06 00:00:00 +0900
categories: ["PROTEIN ML"]
tags: [protein, proteingym, alphafold, plddt, esm2, protein-fitness, structure-features, low-label]
lab_path: "experiment-lab/projects/proteingym-af2-plddt-confidence-audit"
hidden: true
published: false
publication_status: "unpublished"
lock_reason: "geometry feature 정의·threshold 선택 규칙·assay별 paired 결과를 보완해야 하는 진단 초안이다."
excerpt: "ProteinGym 6-assay에서 WT geometry의 작은 양의 차이와 pLDDT threshold replacement의 음의 차이를 분리한 low-label Ridge 평가."
description: "ProteinGym single-mutant low-label 6-assay 점검에서 AlphaFold WT 구조 geometry feature의 단순 추가 차이는 작았고, pLDDT threshold replacement는 음수로 남았다."
permalink: /research/2026/05/09/proteingym-af2-plddt-confidence-audit/
image: /assets/images/posts/proteingym-af2-plddt-confidence-audit/social-thumbnail.png
image_alt: "흰 배경 위의 반투명 protein-like ribbon과 파란 residue confidence 경로로 WT geometry와 pLDDT 점검을 표현한 대표 이미지"
hero_image: /assets/images/posts/proteingym-af2-plddt-confidence-audit/hero.png
hero_alt: "흰 배경 위에 반투명 protein-like ribbon, 작은 residue bead, 파란 confidence 경로가 배치된 대표 이미지"
hero_frame: true
hero_compact: true
---

AlphaFold가 예측한 변이 전 단백질(wild type, WT)의 구조 정보가 변이의 fitness 순위 예측을 보완하는지 평가했다. 또 구조 신뢰도인 pLDDT가 낮은 위치의 정보를 끄는 규칙이 도움이 되는지 별도로 비교했다. 6개 실험(assay)의 집계에서 **구조 특징을 그대로 추가한 차이는 양수였고, pLDDT 임계값으로 걸러 대체한 차이는 음수였다.**

Notin et al.의 ProteinGym은 단백질 변이 효과를 평가하는 벤치마크다 <a class="citation-ref" href="#ref-proteingym" aria-label="Reference 1">[1]</a>. 여기서는 아미노산 하나만 바뀐 변이를 대상으로, 적은 수의 측정값으로 학습해 학습에서 제외한 변이의 순위를 예측하는 조건을 사용했다. Fitness는 각 assay가 측정한 기능 지표를 뜻한다. 기준선은 단백질 서열을 수치 벡터로 바꾼 embedding에 Ridge 회귀를 적용한 모델이다. Ridge는 계수 크기를 제한하는 선형 회귀다.

> **Raw geometry**는 pLDDT로 걸러내기 전의 WT 구조 특징이다. **Threshold gate**는 pLDDT 임계값에 따라 구조 특징의 사용 여부를 정하는 규칙이다. 이 글은 구조 특징 자체의 추가 효용과 이 규칙의 효용을 분리한다.
>
> **pLDDT**는 AlphaFold 계열 구조 예측에서 각 아미노산 잔기 주변 구조의 신뢰도를 나타낸다. 도메인 간 상대 배치나 fitness 예측 성능을 직접 보장하지는 않는다 <a class="citation-ref" href="#ref-plddt-guide" aria-label="Reference 2">[2]</a>.
>
> **DMS(deep mutational scanning)**는 많은 변이의 효과를 측정하는 실험이다. 이 글은 ProteinGym의 DMS 치환 자료 중 단일 변이만 사용한다.

{% include model-mention-cards.html label="사용한 주요 리소스" aria_label="사용한 핵심 벤치마크와 모델 리소스" models="ProteinGym|proteingym.org|https://proteingym.org/;ProteinGym v1|DMS substitutions|https://huggingface.co/datasets/OATML-Markslab/ProteinGym_v1;ESM2-8M|facebook/esm2_t6_8M_UR50D|https://huggingface.co/facebook/esm2_t6_8M_UR50D;ESM2-35M|facebook/esm2_t12_35M_UR50D|https://huggingface.co/facebook/esm2_t12_35M_UR50D" %}

## 요약

- 6개 ProteinGym assay의 single-mutant supervised folds에서 ESM2/Ridge에 WT geometry와 pLDDT feature를 추가했다.
- ESM2-8M 기준 raw geometry의 paired median ΔSpearman은 Modulo/Random `+0.019805`, Contiguous `+0.014991`였다.
- ESM2-35M + mutation/position 기준선에서도 raw geometry 차이는 `+0.005989`로 양수였다. 작은 보완 신호를 관찰했으며 geometry의 무용성을 보인 결과는 아니다.
- 같은 보강 조건의 threshold replacement 차이는 `-0.003190`이었다. 이는 raw geometry 추가 효과와 별개의 비교다.
- pLDDT는 구조의 local confidence이며 fitness feature의 효용 점수가 아니다. 이 threshold 규칙을 통한 제거는 지지되지 않았다.
- 반복 fold·budget·seed 집계는 6개 assay의 범위를 넓히지 않는다. assay별 이질성과 불확실성 없이 일반적인 개선이나 실패를 주장하지 않는다.

## 배경 가설

AlphaFold WT geometry를 평가한 배경은 단백질 변이 효과가 아미노산 서열뿐 아니라 구조적 위치에도 영향을 받는다는 점이다. buried residue, contact-dense core, secondary structure, active site나 interface 근처의 mutation은 solvent-exposed loop의 mutation과 다른 제약을 받을 수 있다. 서열 embedding은 이런 제약을 간접적으로 담을 수 있지만, low-label Ridge 조건에서는 특정 단백질의 3D 이웃, local packing, backbone geometry처럼 구조에서 바로 읽히는 정보를 명시적으로 쓰지는 않는다.

평가 가설은 두 부분으로 나뉜다. AlphaFold WT 구조에서 변이 위치 주변의 raw geometry를 붙이면 sequence-only baseline 위에 일부 추가 정보가 남을 수 있다. 또한 pLDDT가 낮은 위치의 geometry는 예측 신뢰도가 낮으므로, threshold gate로 줄이는 편이 더 안정적일 수 있다. 이 가설은 AlphaFold 구조가 변이 후 기능 변화를 직접 예측한다는 뜻이 아니라, WT 구조 맥락이 low-label fitness ranking에서 보조 신호로 남는지 확인하는 질문에 가깝다.

## 평가 설정

평가 대상은 ProteinGym substitution DMS의 single-mutant assay다. 구조는 ProteinGym에서 제공한 predicted WT structure asset을 사용했고, pLDDT는 PDB B-factor field에서 추출했다. 모든 채택 assay는 mutant mapping fraction `1.0`과 mapped row WT-residue consistency `1.0` 조건을 통과했다.

Split 이름은 ProteinGym supervised protocol을 따른다. `Random`은 mutant row를 무작위로 나누는 비교이고, `Modulo`는 mutation position 기준으로 held-out position에 가까운 일반화를 더 보게 하는 비교다. `Contiguous`는 연속된 position block을 held-out으로 두는 보강 점검이다.

주 지표는 예측 순위와 측정값 순위의 일치도를 나타내는 Spearman 상관계수다. 같은 assay·분할·학습량·seed에서 두 조건의 Spearman 차이를 구한 뒤 그 중앙값을 보고한다(paired median ΔSpearman). 양수는 앞 조건이 뒤 조건보다 높다는 뜻이다. MSE, NDCG, Top-10% recall은 보조 진단 지표로 두었다.

Table 1은 최종 분석에 포함한 6개 assay의 구조 mapping 상태와 mutated-position pLDDT 범위를 먼저 고정한다.

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <colgroup>
        <col style="width: 42%;">
        <col style="width: 18%;">
        <col style="width: 20%;">
        <col style="width: 12%;">
        <col style="width: 8%;">
      </colgroup>
      <thead>
        <tr>
          <th>assay</th>
          <th class="align-right">mutated positions</th>
          <th class="align-right">median pLDDT</th>
          <th class="align-right">IQR</th>
          <th>mapping</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>CASP7_HUMAN_Roychowdhury_2020</code></td>
          <td class="align-right"><code>280</code></td>
          <td class="align-right"><code>95.14</code></td>
          <td class="align-right"><code>22.24</code></td>
          <td>exact</td>
        </tr>
        <tr>
          <td><code>KCNE1_HUMAN_Muhammad_2023_expression</code></td>
          <td class="align-right"><code>127</code></td>
          <td class="align-right"><code>66.62</code></td>
          <td class="align-right"><code>22.60</code></td>
          <td>exact</td>
        </tr>
        <tr>
          <td><code>REV_HV1H2_Fernandes_2016</code></td>
          <td class="align-right"><code>113</code></td>
          <td class="align-right"><code>77.24</code></td>
          <td class="align-right"><code>40.14</code></td>
          <td>exact</td>
        </tr>
        <tr>
          <td><code>TPOR_HUMAN_Bridgford_2020</code></td>
          <td class="align-right"><code>31</code></td>
          <td class="align-right"><code>86.72</code></td>
          <td class="align-right"><code>9.02</code></td>
          <td>exact</td>
        </tr>
        <tr>
          <td><code>TCRG1_MOUSE_Tsuboyama_2023_1E0L</code></td>
          <td class="align-right"><code>35</code></td>
          <td class="align-right"><code>86.38</code></td>
          <td class="align-right"><code>18.31</code></td>
          <td>exact</td>
        </tr>
        <tr>
          <td><code>Q837P4_ENTFA_Meier_2023</code></td>
          <td class="align-right"><code>38</code></td>
          <td class="align-right"><code>89.69</code></td>
          <td class="align-right"><code>8.00</code></td>
          <td>exact</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> 최종 6개 assay의 mutated-position pLDDT와 mapping 상태다. Median pLDDT는 변이 위치의 신뢰도 중앙값이고, IQR은 사분위 범위다. pLDDT threshold의 성능을 주장하기보다, 서로 다른 confidence 범위의 assay가 모두 exact mapping 조건을 통과했음을 확인하는 기준이다.</figcaption>
</figure>

### Feature 비교 조건

비교 조건은 구조 신호와 confidence 신호의 역할을 분리하도록 구성했다. `B1`은 ESM2-8M sequence embedding 기반 Ridge 기준선이다. `B2`는 raw geometry feature를 추가한 조건이고, `B2.5`는 pLDDT를 보조 변수로 더한 조건이다. `B3`는 raw geometry를 pLDDT 임계값으로 걸러낸 구조 특징으로 대체하며, `B4`는 raw geometry를 유지한 채 gated geometry interaction을 추가한다. Table 2는 이 조건들의 역할을 요약한다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <colgroup>
        <col style="width: 14%;">
        <col style="width: 46%;">
        <col style="width: 40%;">
      </colgroup>
      <thead>
        <tr>
          <th>label</th>
          <th>feature 구성</th>
          <th>목적</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>B0</code></td>
          <td>mutation identity, BLOSUM62,<br><span class="table-note-inline">physicochemical delta</span></td>
          <td>저비용 mutation baseline<br><span class="table-note-inline">sequence와 position에서 바로 계산되는 feature</span></td>
        </tr>
        <tr>
          <td><code>B1</code></td>
          <td>ESM2-8M sequence embedding 기반 Ridge</td>
          <td>sequence-only baseline</td>
        </tr>
        <tr>
          <td><code>B2</code></td>
          <td><code>B1 + raw geometry</code></td>
          <td>구조 feature를 단순 추가했을 때의 차이</td>
        </tr>
        <tr>
          <td><code>B2.5</code></td>
          <td><code>B2 + pLDDT covariates</code></td>
          <td>pLDDT를 진단 covariate로 추가</td>
        </tr>
        <tr>
          <td><code>B3</code></td>
          <td><code>B1 + gated geometry</code><br><span class="table-note-inline">+ pLDDT covariates</span></td>
          <td>raw geometry를 pLDDT 임계값으로 걸러낸 구조 특징으로 대체</td>
        </tr>
        <tr>
          <td><code>B4</code></td>
          <td><code>B1 + raw geometry</code><br><span class="table-note-inline">+ gated geometry interaction + pLDDT covariates</span></td>
          <td>gate를 대체가 아니라 additive interaction으로 사용</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> 비교한 Ridge feature 구성이다. raw geometry를 그대로 추가하는 조건, pLDDT를 보조 변수로 두는 조건, pLDDT threshold가 raw geometry를 대체하는 조건을 분리해 읽기 위한 표다.</figcaption>
</figure>

Replacement는 기존 구조 특징을 걸러낸 특징으로 바꾸는 조건이다. Additive interaction은 기존 특징을 유지하면서 gate를 적용한 특징을 추가하는 조건이다. 두 비교를 분리해야 낮은 신뢰도의 정보를 제거하는 효과와 보조 정보로 더하는 효과를 구분할 수 있다.

## 결과

### pLDDT gate와 raw geometry

6개 assay, official Modulo/Random split, train budget `24/48/96/192/384`, seed 5개 조건에서 총 1500개 paired 결과를 비교했다. Raw WT geometry의 양의 차이와 threshold gate의 음의 차이는 별개로 읽는다. 1500개는 같은 assay에서 fold·budget·seed를 반복한 비교 수이며 독립 assay 수는 6개다.

Modulo/Random 합산에서 raw geometry 추가 조건인 `B2 - B1`은 `+0.019805`였지만, pLDDT covariate 추가인 `B2.5 - B2`는 `+0.001938`에 그쳤다. 반면 pLDDT threshold replacement인 `B3 - B2.5`는 `-0.005542`였다. Additive interaction인 `B4 - B2.5`는 `+0.001289`로 거의 중립에 가까웠지만, `B4 - B3`는 `+0.006355`로 replacement 조건보다 높았다.

Table 3은 메인 비교를 paired median ΔSpearman으로 압축한다.

<figure class="table-figure table-figure--metrics table-figure--compact-metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--compact-two-col">
      <thead>
        <tr>
          <th>comparison</th>
          <th class="align-right">median ΔSpearman</th>
          <th>해석</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>B2 - B1</code></td>
          <td class="align-right"><code>+0.019805</code></td>
          <td>raw WT geometry 추가 차이</td>
        </tr>
        <tr>
          <td><code>B2.5 - B2</code></td>
          <td class="align-right"><code>+0.001938</code></td>
          <td>pLDDT 보조 변수 차이는 매우 작음</td>
        </tr>
        <tr>
          <td><code>B3 - B2.5</code></td>
          <td class="align-right"><code>-0.005542</code></td>
          <td>threshold replacement는 음수</td>
        </tr>
        <tr>
          <td><code>B4 - B2.5</code></td>
          <td class="align-right"><code>+0.001289</code></td>
          <td>additive interaction은 거의 중립</td>
        </tr>
        <tr>
          <td><code>B4 - B3</code></td>
          <td class="align-right"><code>+0.006355</code></td>
          <td>additive가 replacement보다 높음</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> Modulo와 Random split을 합친 paired median ΔSpearman이다. 양수는 앞 조건이 뒤 조건보다 Spearman이 높다는 뜻이다. raw geometry 추가 조건의 차이는 작았고, pLDDT threshold replacement는 음수로 남았다.</figcaption>
</figure>

이 threshold 규칙이 성능을 높인다는 해석은 지지되지 않았다. Raw WT geometry의 양의 차이는 별도로 남는다. Confidence 구간별 성능 보고는 후속 진단 후보이며 여기서 그 효용까지 입증한 것은 아니다.

### 기준선 강화 후 축소된 geometry 차이

ESM2-8M baseline이 약해서 raw geometry 차이가 커 보였을 가능성을 줄이기 위해, mutation identity, position fraction, BLOSUM62, hydrophobicity/charge/volume delta를 포함한 보강 기준선도 비교했다. 여기서 mutation/position 보강 기준선은 별도 구조 예측이나 학습 없이 sequence와 mutation position에서 바로 계산되는 저비용 feature 묶음이다. 이 보강 비교에서는 ESM2-8M뿐 아니라 ESM2-35M embedding도 같은 Ridge protocol로 비교했다 <a class="citation-ref" href="#ref-esm2" aria-label="Reference 3">[3]</a>.

ESM2-35M + mutation/position 보강 baseline에서도 raw geometry 추가 차이는 `+0.005989`로 남았다. 크기는 줄었지만 방향은 양수였다. split별로도 Modulo `+0.010051`, Random `+0.003792`, Contiguous `+0.005716`이었다.

Table 4는 보강 기준선에서도 raw geometry 차이가 남는지와 pLDDT gate 계열 조건이 추가 차이를 만드는지를 함께 확인한다.

<figure class="table-figure table-figure--metrics table-figure--compact-metrics">
  <div class="table-shell">
    <table class="metrics-table">
      <thead>
        <tr>
          <th>embedding baseline</th>
          <th>comparison</th>
          <th class="align-right">median ΔSpearman</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>ESM2-8M<br><span class="table-note-inline">+ mutation/position</span></td>
          <td>raw geometry - 보강 기준선</td>
          <td class="align-right"><code>+0.013140</code></td>
        </tr>
        <tr>
          <td>ESM2-35M<br><span class="table-note-inline">+ mutation/position</span></td>
          <td>raw geometry - 보강 기준선</td>
          <td class="align-right"><code>+0.005989</code></td>
        </tr>
        <tr>
          <td>ESM2-35M<br><span class="table-note-inline">+ mutation/position</span></td>
          <td>threshold replacement - pLDDT covariate</td>
          <td class="align-right"><code>-0.003190</code></td>
        </tr>
        <tr>
          <td>ESM2-35M<br><span class="table-note-inline">+ mutation/position</span></td>
          <td>additive gate - pLDDT covariate</td>
          <td class="align-right"><code>+0.000532</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> 보강 기준선 결과다. 기준선의 표현력이 부족해 구조 특징의 차이가 커 보였을 가능성을 점검한 비교다. raw geometry 차이는 ESM2-35M embedding에 mutation/position feature를 보강한 baseline에서 더 작아졌다. 비교 열은 각 조건의 기능적 역할을 기준으로 표기했다.</figcaption>
</figure>

보강 비교에서도 raw WT geometry의 양의 차이는 남았고 크기는 줄었다. 이는 강한 기준선 위에서도 일부 보완 신호가 남을 가능성을 보여주지만, 실용적 가치와 불확실성은 별도 확인이 필요하다. 기준선을 강화한 비교이며 assay 수를 늘린 검증은 아니다.

분할별 수치와 연속 위치 점검은 Appendix에 둔다.

## 해석: 보완 신호와 threshold 비용

작은 보완 신호와 gate 대체의 음의 차이는 서로 다른 원인에서 생겼을 수 있다. 아래는 WT 구조 특징과 DMS 측정값의 성격을 바탕으로 한 가능한 설명이며, 이번 비교가 원인까지 분리한 것은 아니다.

첫 번째 가능한 요인은 WT의 정적 구조만 사용하는 한계다. 사용한 구조 feature는 mutant별 구조 변화가 아니라 AlphaFold WT 구조에서 변이 위치 주변의 local geometry를 요약한 값이다. 이 정보는 mutation이 놓인 구조 맥락을 알려주지만, side-chain 재배치, contact loss/gain, ΔΔG, 활성 부위 화학, binding interface 변화처럼 변이 후 fitness 방향을 직접 결정할 수 있는 변화량을 담지는 않는다.

두 번째 가능한 요인은 구조 특징의 해상도와 assay 측정 대상의 불일치다. DMS fitness label은 assay에 따라 folding, expression, binding, catalytic activity, stability, growth selection이 섞인 결과일 수 있다. 반면 이 실험의 raw geometry는 변이 위치 근처의 local packing과 backbone context에 가까운 요약 feature다. 기능 변화가 장거리 allostery, domain orientation, partner binding, expression burden처럼 local geometry 밖에서 결정되면, WT 주변 geometry만으로는 label을 충분히 설명하기 어렵다.

세 번째 가능한 요인은 sequence 기준선과의 정보 중복 또는 추가 개선 여지의 감소다. ESM2 embedding은 residue context와 position-dependent sequence pattern을 이미 품고 있고, mutation identity, position fraction, BLOSUM62, physicochemical delta를 더하면 위치와 치환 성격에 대한 저비용 정보도 보강된다. 실제로 ESM2-35M + mutation/position 보강 기준선에서는 raw geometry 차이가 `+0.005989`로 줄었다. 이 결과는 정보 중복을 직접 증명하지는 않지만, 강한 sequence/mutation 기준선 위에서 단순 local geometry가 새로 남기는 신호가 제한적일 수 있음을 시사한다.

네 번째 가능한 요인은 pLDDT의 역할 불일치다. pLDDT는 AlphaFold 계열 prediction에서 residue-level local confidence를 나타내는 점수이며, 해당 위치의 geometry feature가 fitness prediction에 유용한지까지 말해주지는 않는다. 따라서 현 threshold replacement에서는 낮은-confidence geometry를 줄이는 효과와 함께, 유효할 수 있는 구조 맥락을 약화했을 가능성도 있다. 다만 이 결과만으로는 threshold 설계 문제와 pLDDT 자체의 부적합성을 분리하지 못한다.

마지막으로 현재 비교는 Ridge feature 비교다. 구조 feature가 fitness에 영향을 주더라도 그 관계가 nonlinear interaction, residue-pair interaction, assay-specific mechanism으로 나타나면 단순 additive feature가 충분히 표현하지 못할 수 있다. 따라서 이 결과는 AlphaFold 구조 정보 전체의 부정이라기보다, WT local geometry와 pLDDT threshold를 low-label Ridge feature로 직접 붙이는 방식의 한계로 해석하는 편이 더 정확하다.

## 일반화 범위와 적용 기준

현 6-assay 결과에서 raw geometry는 작은 양의 보완 신호를 남겼고, threshold replacement는 그와 별개로 음의 차이를 보였다. Geometry를 채택할 실용적 가치는 추가 feature 계산 비용과 assay별 차이를 함께 평가해야 한다. pLDDT의 confidence 분포와 구간별 성능을 보고하는 것은 가능한 후속 진단이며, 이 비교만으로 최선의 사용법을 확정하지 않는다.

분석 범위는 6-assay 점검이다. ProteinGym 전체 benchmark, UniProt-level aggregate, functional category-level 평균으로 일반화하지 않는다. 본문 수치는 paired median ΔSpearman의 방향과 크기를 보는 점검이며, 통계적 유의성을 주장하지 않는다.

구조 confidence도 pLDDT에 제한된다. PAE, domain orientation confidence, multimer context, disorder-specific interpretation은 다루지 않았다. 따라서 pLDDT가 fitness prediction 성능을 직접 예측한다는 주장은 두지 않는다.

후속 검증에서는 assay 수와 단백질 계열의 다양성을 늘려, 작은 구조 보완 신호와 gate 대체의 음의 차이가 유지되는지 먼저 확인할 필요가 있다. Soft gate나 임계값 탐색은 그다음의 설계 질문으로 남는다.

## Appendix: 분할별 결과

### 분할 조건별 안정성

Split별로 raw geometry 추가 차이는 모두 양수였다. `B2 - B1`은 Modulo에서 `+0.024724`, Random에서 `+0.016141`이었다. 다만 이 관찰은 작은 양수 방향이 반복됐다는 보조 근거일 뿐, 단순 WT geometry 추가가 뚜렷한 개선 경로라는 결론으로 이어지지는 않는다.

Split별 결과에서도 pLDDT threshold replacement의 결론은 유지된다. `B3 - B2.5`는 Modulo `-0.009455`, Random `-0.003802`로 모두 음수였다. pLDDT covariate와 additive interaction의 차이는 양수라도 매우 작았다.

Table 5는 같은 비교를 Modulo, Random, Contiguous 조건으로 나눠 보여준다.

<figure class="table-figure table-figure--metrics table-figure--compact-metrics">
  <div class="table-shell">
    <table class="metrics-table">
      <thead>
        <tr>
          <th>split</th>
          <th class="align-right"><code>B2-B1</code></th>
          <th class="align-right"><code>B2.5-B2</code></th>
          <th class="align-right"><code>B3-B2.5</code></th>
          <th class="align-right"><code>B4-B2.5</code></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Modulo</td>
          <td class="align-right"><code>+0.024724</code></td>
          <td class="align-right"><code>+0.002148</code></td>
          <td class="align-right"><code>-0.009455</code></td>
          <td class="align-right"><code>+0.001795</code></td>
        </tr>
        <tr>
          <td>Random</td>
          <td class="align-right"><code>+0.016141</code></td>
          <td class="align-right"><code>+0.001757</code></td>
          <td class="align-right"><code>-0.003802</code></td>
          <td class="align-right"><code>+0.000941</code></td>
        </tr>
        <tr>
          <td>Contiguous</td>
          <td class="align-right"><code>+0.014991</code></td>
          <td class="align-right"><code>+0.001660</code></td>
          <td class="align-right"><code>-0.007403</code></td>
          <td class="align-right"><code>+0.000061</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 5.</strong> 분할 조건별 paired median ΔSpearman이다. Modulo/Random은 본문 중심 split이고 Contiguous는 보강 점검이다. raw geometry 추가 차이는 세 split 모두에서 양수였지만, 6-assay 범위의 split 안정성으로만 읽는다.</figcaption>
</figure>

### 연속 위치 분할 점검

Contiguous split에서도 raw geometry의 작은 양수 방향은 유지됐다. 6개 assay, 5 folds, 5 budgets, 5 seeds 조건에서 총 750개 paired 결과를 비교했고, `B2 - B1`은 `+0.014991`였다. 이 값은 Modulo/Random 밖에서도 양의 차이를 관찰했다는 보조 근거다. 통계적 유의성이나 새로운 assay로의 일반화를 보장하지는 않는다.

pLDDT threshold replacement는 이 조건에서도 음수였다. `B3 - B2.5`는 `-0.007403`이었고, `B4 - B2.5`는 `+0.000061`로 사실상 중립이었다. 따라서 pLDDT gate interaction 자체의 독립적 개선은 현재 점검에서는 주장하기 어렵다.

Leave-one-assay-out 성격의 점검에서도 raw geometry 추가 차이는 양수 방향을 자주 유지했다. Modulo/Random에서는 6개 assay 모두 `B2-B1`이 양수였고, LOO median range는 `+0.01263`에서 `+0.02483`이었다. Contiguous에서는 6개 중 5개 assay에서 양수였고, LOO median range는 `+0.00937`에서 `+0.02421`이었다. 이 안정성은 진단적으로는 남지만, geometry의 보완 신호와 threshold replacement의 비용을 분리해서 읽게 한다.

## Appendix: 재현과 불확실성의 공백

표는 동일 조건 간 paired 차이의 중앙값이다. 중앙값끼리 더하거나 빼서 다른 비교의 중앙값을 재구성할 수 없다. `B4 - B3`는 `B4 - B2.5`와 `B3 - B2.5`의 중앙값 차이와 반드시 같지 않다.

보존된 집계만으로는 raw geometry feature 목록·계산 반경·정규화, pLDDT threshold 값과 선택 집합, Ridge 규제 선택, assay별 fold·budget·seed 대응 결과를 확인할 수 없다. 따라서 assay 단위 불확실성이나 threshold 최적화 여부를 재구성하지 않으며, 위 결과는 기록된 비교 조건의 집계 관찰로 해석한다.

## References

<div class="reference-list" markdown="1">

<ol>
  <li id="ref-proteingym">Notin, P. et al. <strong>ProteinGym: Large-Scale Benchmarks for Protein Fitness Prediction and Design</strong>. <em>NeurIPS Datasets and Benchmarks</em>, 2023.<br>
    <a href="https://proceedings.neurips.cc/paper_files/paper/2023/hash/cac723e5ff29f65e3fcbb0739ae91bee-Abstract-Datasets_and_Benchmarks.html">NeurIPS proceedings</a> · <a href="https://proteingym.org/">ProteinGym website</a> · <a href="https://huggingface.co/datasets/OATML-Markslab/ProteinGym_v1">Hugging Face dataset</a> · <a href="https://github.com/OATML-Markslab/ProteinGym">GitHub repository</a>
  </li>
  <li id="ref-plddt-guide">EMBL-EBI Training. <strong>pLDDT: Understanding local confidence</strong>. AlphaFold training material.<br>
    <a href="https://www.ebi.ac.uk/training/online/courses/alphafold/inputs-and-outputs/evaluating-alphafolds-predicted-structures-using-confidence-scores/plddt-understanding-local-confidence/">EBI pLDDT guide</a>
  </li>
  <li id="ref-esm2">Lin, Z. et al. <strong>Evolutionary-scale prediction of atomic-level protein structure with a language model</strong>. <em>Science</em>, 2023.<br>
    <a href="https://www.science.org/doi/10.1126/science.ade2574">Paper / DOI</a> · <a href="https://huggingface.co/facebook/esm2_t6_8M_UR50D">ESM2-8M model</a> · <a href="https://huggingface.co/facebook/esm2_t12_35M_UR50D">ESM2-35M model</a>
  </li>
</ol>

</div>

## Citation

이 글을 인용할 때는 아래 형식을 사용할 수 있다.

```text
Ilho Ahn, "ProteinGym 6-assay에서 WT geometry의 보완 신호와 pLDDT gate 비용", Mini Research, May 9, 2026.
```

또는 BibTeX 형식으로는 다음처럼 적을 수 있다.

```bibtex
@article{ahn2026proteingymaf2plddt,
  author = {Ilho Ahn},
  title = {ProteinGym 6-assay에서 WT geometry의 보완 신호와 pLDDT gate 비용},
  journal = {Mini Research},
  year = {2026},
  month = may,
  url = {https://muted-color.github.io/research/2026/05/09/proteingym-af2-plddt-confidence-audit/}
}
```
