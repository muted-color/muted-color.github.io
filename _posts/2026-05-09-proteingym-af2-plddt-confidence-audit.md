---
title: "ProteinGym low-label fitness에서 AlphaFold WT geometry와 pLDDT gate 한계 점검"
date: 2026-05-09 09:58:14 +0900
last_modified_at: 2026-05-09 21:37:40 +0900
categories: ["PROTEIN ML"]
tags: [protein, proteingym, alphafold, plddt, esm2, protein-fitness, structure-features, low-label]
lab_path: "experiment-lab/projects/proteingym-af2-plddt-confidence-audit"
hidden: true
published: false
publication_status: "unpublished"
lock_reason: "초기 가설이 WT 구조 맥락과 mutant effect prediction을 충분히 구분하지 못해 공개 글로 두지 않는다."
excerpt: "ProteinGym single-mutant low-label 조건에서 AlphaFold WT 구조 geometry feature의 단순 추가와 pLDDT threshold gate가 뚜렷한 개선 경로로 보이지 않았다는 6-assay 점검."
description: "ProteinGym single-mutant low-label 6-assay 점검에서 AlphaFold WT 구조 geometry feature의 단순 추가 차이는 작았고, pLDDT threshold replacement는 음수로 남았다."
permalink: /research/2026/05/09/proteingym-af2-plddt-confidence-audit/
image: /assets/images/posts/proteingym-af2-plddt-confidence-audit/social-thumbnail.png
image_alt: "흰 배경 위의 반투명 protein-like ribbon과 파란 residue confidence 경로로 WT geometry와 pLDDT 점검을 표현한 대표 이미지"
hero_image: /assets/images/posts/proteingym-af2-plddt-confidence-audit/hero.png
hero_alt: "흰 배경 위에 반투명 protein-like ribbon, 작은 residue bead, 파란 confidence 경로가 배치된 대표 이미지"
hero_frame: true
hero_compact: true
---

## 비공개 메모

이 글은 공개하지 않는다. 핵심 이유는 결과가 약해서가 아니라, 초기 가설 설정이 충분히 정교하지 않았기 때문이다. AlphaFold wild-type (WT) geometry는 변이 전 구조 맥락을 설명하는 context descriptor에 가깝고, ProteinGym fitness prediction은 변이 후 기능 방향을 맞히는 mutation effect prediction 문제다. 초기 설계는 이 둘을 충분히 구분하지 못한 채, WT local geometry를 low-label Ridge feature로 단순 추가하면 sequence baseline 위에 보조 신호가 남을 수 있다는 느슨한 가설에서 출발했다.

따라서 이 글의 공개 가능한 결론은 제한적이다. 실험은 AlphaFold 구조 정보 전체의 무용성을 보인 것이 아니라, WT-only local geometry와 pLDDT threshold를 직접 feature로 붙이는 설계가 context descriptor와 mutation effect predictor 사이의 간격을 메우지 못했다는 내부 실패 기록에 가깝다. 후속 실험은 WT 구조 맥락 자체보다 mutant-aware 변화량, energy-like feature, assay mechanism별 readout, 또는 residue-pair/nonlinear interaction을 먼저 가설에 포함해야 한다.

ProteinGym single-mutant supervised low-label 조건에서는 적은 mutant label로 held-out mutant의 fitness 순위를 예측해야 한다 <a class="citation-ref" href="#ref-proteingym" aria-label="Reference 1">[1]</a>. Sequence embedding 기반 Ridge baseline은 단순하고 안정적인 비교 기준이지만, mutation이 놓인 wild-type (WT) 구조 주변의 geometry를 직접 보지는 않는다.

평가 질문은 AlphaFold WT 구조 feature의 단순 추가와 pLDDT confidence를 threshold gate로 쓰는 방식이 low-label fitness prediction의 뚜렷한 개선 경로로 남는지다 <a class="citation-ref" href="#ref-plddt-guide" aria-label="Reference 2">[2]</a>. 비교 목적은 새 구조 모델 제안이 아니라 feature 사용 방식의 한계 점검이며, 해석 범위는 official single-mutant supervised folds를 사용한 6-assay 결과로 제한한다.

> **pLDDT**는 AlphaFold 계열 구조 예측의 residue-level local confidence score다. 이 값은 local 구조 신뢰도를 읽는 데 유용하지만, domain 간 상대 배치나 fitness prediction 성능을 직접 보장하는 점수는 아니다 <a class="citation-ref" href="#ref-plddt-guide" aria-label="Reference 2">[2]</a>.
>
> **DMS**는 deep mutational scanning assay다. ProteinGym의 substitution DMS 중 single-mutant row만 사용해, 이미 측정된 변이의 fitness ranking을 예측한다.

{% include model-mention-cards.html label="사용한 주요 리소스" aria_label="사용한 핵심 벤치마크와 모델 리소스" models="ProteinGym|proteingym.org|https://proteingym.org/;ProteinGym v1|DMS substitutions|https://huggingface.co/datasets/OATML-Markslab/ProteinGym_v1;ESM2-8M|facebook/esm2_t6_8M_UR50D|https://huggingface.co/facebook/esm2_t6_8M_UR50D;ESM2-35M|facebook/esm2_t12_35M_UR50D|https://huggingface.co/facebook/esm2_t12_35M_UR50D" %}

## 요약

- AlphaFold WT geometry는 변이 위치의 구조적 제약이 sequence-only baseline 위에 보조 신호로 남을 수 있다는 가설에서 평가했다.
- 6개 assay 점검에서 AlphaFold WT 구조 geometry feature의 단순 추가와 pLDDT threshold gate는 뚜렷한 개선 경로로 분리되지 않았다.
- pLDDT를 보조 변수로 넣은 차이는 거의 없었고, pLDDT threshold replacement는 Modulo/Random과 Contiguous 모두에서 음수였다.
- Sequence-only Ridge 기준선에 raw geometry를 더하면 median ΔSpearman은 양수였지만 차이는 작았다. ESM2-8M 기준 Modulo/Random 합산 값은 `+0.019805`, Contiguous split 값은 `+0.014991`였다.
- ESM2-35M + mutation/position 보강 기준선에서는 raw geometry 차이가 `+0.005989`로 더 줄었다.
- 가능한 이유는 WT-only static geometry, coarse local feature, assay readout과 구조 feature의 불일치, sequence 기준선과의 정보 중복으로 나뉜다.
- pLDDT는 geometry feature의 fitness prediction 유용성이 아니라 구조 예측 confidence에 가까워, 현 설정에서는 gate보다 mapping 점검과 low-confidence region별 성능 보고에 더 적합하다.
- 해석 범위는 ProteinGym 전체가 아니라 official single-mutant supervised folds를 사용한 6-assay 결과로 제한하며, 통계적 유의성을 주장하지 않는다.

## 배경 가설

AlphaFold WT geometry를 평가한 배경은 단백질 변이 효과가 sequence identity만이 아니라 구조적 위치에도 영향을 받는다는 점이다. buried residue, contact-dense core, secondary structure, active site나 interface 근처의 mutation은 solvent-exposed loop의 mutation과 다른 제약을 받을 수 있다. Sequence embedding은 이런 제약을 간접적으로 담을 수 있지만, low-label Ridge 조건에서는 특정 단백질의 3D 이웃, local packing, backbone geometry처럼 구조에서 바로 읽히는 정보를 명시적으로 쓰지는 않는다.

평가 가설은 두 부분으로 나뉜다. AlphaFold WT 구조에서 변이 위치 주변의 raw geometry를 붙이면 sequence-only baseline 위에 일부 추가 정보가 남을 수 있다. 또한 pLDDT가 낮은 위치의 geometry는 예측 신뢰도가 낮으므로, threshold gate로 줄이는 편이 더 안정적일 수 있다. 이 가설은 AlphaFold 구조가 변이 후 기능 변화를 직접 예측한다는 뜻이 아니라, WT 구조 맥락이 low-label fitness ranking에서 보조 신호로 남는지 확인하는 질문에 가깝다.

## 문제 설정

분리해야 할 축은 두 가지다. 하나는 WT 구조에서 계산한 raw geometry가 sequence embedding이 놓치는 위치 주변 신호를 보완하는지이고, 다른 하나는 AlphaFold confidence인 pLDDT가 그 geometry를 직접 켜고 끄는 기준으로 충분한지다.

이 구분이 필요한 이유는 AlphaFold WT 구조와 pLDDT가 서로 다른 종류의 정보를 담기 때문이다. WT geometry는 변이 위치의 정적 구조 맥락을 제공하지만, 변이 후 안정성, 활성, 발현, binding 변화의 방향을 직접 예측하지는 않는다. pLDDT는 구조 예측의 local confidence이며, 해당 geometry feature가 fitness prediction에 유용한지까지 보장하지 않는다.

따라서 평가 질문은 **성능 feature 발굴이 아니라, AlphaFold WT geometry와 pLDDT confidence를 low-label fitness prediction에서 어디까지 진단 신호로만 남겨야 하는지**로 좁혀진다.

## 평가 설정

평가 대상은 ProteinGym substitution DMS의 single-mutant assay다. 구조는 ProteinGym에서 제공한 predicted WT structure asset을 사용했고, pLDDT는 PDB B-factor field에서 추출했다. 모든 채택 assay는 mutant mapping fraction `1.0`과 mapped row WT-residue consistency `1.0` 조건을 통과했다.

Split 이름은 ProteinGym supervised protocol을 따른다. `Random`은 mutant row를 무작위로 나누는 비교이고, `Modulo`는 mutation position 기준으로 held-out position에 가까운 일반화를 더 보게 하는 비교다. `Contiguous`는 연속된 position block을 held-out으로 두는 보강 점검이다.

Primary metric은 Spearman이다. MSE, NDCG, Top-10% recall은 diagnostic metric으로 남기고, 본문 결론은 paired median ΔSpearman 중심으로 제한한다.

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
  <figcaption><strong>Table 1.</strong> 최종 6개 assay의 mutated-position pLDDT와 mapping 상태다. Median pLDDT와 IQR은 mutated position에서의 confidence 분포를 요약한다. pLDDT threshold의 성능을 주장하기보다, 서로 다른 confidence 범위의 assay가 모두 exact mapping 조건을 통과했음을 확인하는 기준이다.</figcaption>
</figure>

## 비교 조건

비교 조건은 구조 신호와 confidence 신호의 역할을 분리하도록 구성했다. `B1`은 ESM2-8M sequence embedding 기반 Ridge 기준선이다. `B2`는 raw geometry feature를 추가한 조건이고, `B2.5`는 pLDDT를 보조 변수로 더한 조건이다. `B3`는 raw geometry를 pLDDT threshold feature로 대체하며, `B4`는 raw geometry를 유지한 채 gated geometry interaction을 추가한다. Table 2는 이 조건들의 역할을 요약한다.

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
          <td>raw geometry를 pLDDT threshold feature로 대체</td>
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

중요한 구분은 replacement와 additive interaction이다. pLDDT가 낮은 위치의 geometry를 끄는 규칙이 실제로 도움이 되는지, 아니면 confidence를 진단 변수로만 두는 편이 나은지를 분리한다.

## 결과: 개선 경로 점검

### pLDDT gate와 raw geometry

6개 assay, official Modulo/Random split, train budget `24/48/96/192/384`, seed 5개 조건에서 총 1500개 paired 결과를 비교했다. 가장 안정적인 결론은 raw WT geometry의 작은 양수가 아니라, pLDDT threshold gate가 개선 경로로 분리되지 않았다는 점이다.

Modulo/Random 합산에서 raw geometry 추가 조건인 `B2 - B1`은 `+0.019805`였지만, pLDDT covariate 추가인 `B2.5 - B2`는 `+0.001938`에 그쳤다. 반면 pLDDT threshold replacement인 `B3 - B2.5`는 `-0.005542`였다. Additive interaction인 `B4 - B2.5`는 `+0.001289`로 거의 중립에 가까웠지만, `B4 - B3`는 `+0.006355`로 replacement 조건보다 안정적이었다.

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
          <td>additive가 replacement보다 안정적</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> Modulo와 Random split을 합친 paired median ΔSpearman이다. 양수는 앞 조건이 뒤 조건보다 Spearman이 높다는 뜻이다. raw geometry 추가 조건의 차이는 작았고, pLDDT threshold replacement는 음수로 남았다.</figcaption>
</figure>

pLDDT가 직접적인 성능 gate라는 해석은 지지되지 않았다. raw WT geometry 추가 조건도 큰 개선으로 보기 어렵고, pLDDT는 그 작은 차이를 해석하고 stratify하는 보조 축에 가깝다.

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
  <figcaption><strong>Table 4.</strong> 보강 기준선 결과다. ESM2-8M baseline이 약해서 생긴 착시 가능성을 줄이기 위한 비교다. raw geometry 차이는 ESM2-35M embedding에 mutation/position feature를 보강한 baseline에서 더 작아졌다. 비교 열은 각 조건의 기능적 역할을 기준으로 표기했다.</figcaption>
</figure>

보강 비교에서는 raw WT geometry 차이가 더 작아졌다. 따라서 결론은 “AlphaFold WT 구조 geometry를 단순 추가하는 방식은 뚜렷한 개선 경로로 보기 어렵다”에 가깝다. 이 값은 baseline 강도를 높인 조건에서 나온 것이지, assay 수를 늘린 검증은 아니다.

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

Contiguous split에서도 raw geometry의 작은 양수 방향은 유지됐다. 6개 assay, 5 folds, 5 budgets, 5 seeds 조건에서 총 750개 paired 결과를 비교했고, `B2 - B1`은 `+0.014991`였다. 이 값은 Modulo/Random 조건에만 제한되지 않는 보조 관찰이지만, 효과 크기와 통계적 유의성을 주장하는 근거는 아니다.

pLDDT threshold replacement는 이 조건에서도 음수였다. `B3 - B2.5`는 `-0.007403`이었고, `B4 - B2.5`는 `+0.000061`로 사실상 중립이었다. 따라서 pLDDT gate interaction 자체의 독립적 개선은 현재 점검에서는 주장하기 어렵다.

Leave-one-assay-out 성격의 점검에서도 raw geometry 추가 차이는 양수 방향을 자주 유지했다. Modulo/Random에서는 6개 assay 모두 `B2-B1`이 양수였고, LOO median range는 `+0.01263`에서 `+0.02483`이었다. Contiguous에서는 6개 중 5개 assay에서 양수였고, LOO median range는 `+0.00937`에서 `+0.02421`이었다. 이 안정성은 진단적으로는 남지만, pLDDT gate 실패와 작은 차이라는 결론을 바꾸지는 않는다.

## 뚜렷한 개선으로 이어지지 않은 가능한 요인

결과 자체는 원인이 아니다. 가능한 설명은 AlphaFold WT geometry가 제공하는 정보와 DMS fitness label이 요구하는 정보 사이의 간격에서 찾는 편이 더 적절하다.

첫 번째 가능한 요인은 WT-only static geometry의 한계다. 사용한 구조 feature는 mutant별 구조 변화가 아니라 AlphaFold WT 구조에서 변이 위치 주변의 local geometry를 요약한 값이다. 이 정보는 mutation이 놓인 구조 맥락을 알려주지만, side-chain 재배치, contact loss/gain, ΔΔG, 활성 부위 화학, binding interface 변화처럼 변이 후 fitness 방향을 직접 결정할 수 있는 변화량을 담지는 않는다.

두 번째 가능한 요인은 feature의 해상도와 assay readout의 불일치다. DMS fitness label은 assay에 따라 folding, expression, binding, catalytic activity, stability, growth selection이 섞인 결과일 수 있다. 반면 이 실험의 raw geometry는 변이 위치 근처의 local packing과 backbone context에 가까운 요약 feature다. 기능 변화가 장거리 allostery, domain orientation, partner binding, expression burden처럼 local geometry 밖에서 결정되면, WT 주변 geometry만으로는 label을 충분히 설명하기 어렵다.

세 번째 가능한 요인은 sequence 기준선과의 정보 중복 또는 추가 headroom 감소다. ESM2 embedding은 residue context와 position-dependent sequence pattern을 이미 품고 있고, mutation identity, position fraction, BLOSUM62, physicochemical delta를 더하면 위치와 치환 성격에 대한 저비용 정보도 보강된다. 실제로 ESM2-35M + mutation/position 보강 기준선에서는 raw geometry 차이가 `+0.005989`로 줄었다. 이 결과는 정보 중복을 직접 증명하지는 않지만, 강한 sequence/mutation 기준선 위에서 단순 local geometry가 새로 남기는 신호가 제한적일 수 있음을 시사한다.

네 번째 가능한 요인은 pLDDT의 역할 불일치다. pLDDT는 AlphaFold 계열 prediction에서 residue-level local confidence를 나타내는 점수이며, 해당 위치의 geometry feature가 fitness prediction에 유용한지까지 말해주지는 않는다. 따라서 현 threshold replacement에서는 낮은-confidence geometry를 줄이는 효과와 함께, 유효할 수 있는 구조 맥락을 약화했을 가능성도 있다. 다만 이 결과만으로는 threshold 설계 문제와 pLDDT 자체의 부적합성을 분리하지 못한다.

마지막으로 현재 비교는 Ridge feature 비교다. 구조 feature가 fitness에 영향을 주더라도 그 관계가 nonlinear interaction, residue-pair interaction, assay-specific mechanism으로 나타나면 단순 additive feature가 충분히 표현하지 못할 수 있다. 따라서 이 결과는 AlphaFold 구조 정보 전체의 부정이라기보다, WT local geometry와 pLDDT threshold를 low-label Ridge feature로 직접 붙이는 방식의 한계로 해석하는 편이 더 정확하다.

## 일반화 범위와 적용 기준

이 결과에서 일반화할 수 있는 적용 기준은 제한적이다. AlphaFold WT geometry의 단순 추가는 뚜렷한 성능 개선용 feature보다 진단용 비교 축으로 두고, pLDDT는 직접적인 성능 gate가 아니라 진단 신호로 둔다. pLDDT는 assay별 mapping 품질, mutated-position confidence 분포, low-confidence region별 성능 보고에 더 적합하다.

분석 범위는 6-assay 점검이다. ProteinGym 전체 benchmark, UniProt-level aggregate, functional category-level 평균으로 일반화하지 않는다. 본문 수치는 paired median ΔSpearman의 방향과 크기를 보는 점검이며, 통계적 유의성을 주장하지 않는다.

구조 confidence도 pLDDT에 제한된다. PAE, domain orientation confidence, multimer context, disorder-specific interpretation은 다루지 않았다. 따라서 pLDDT가 fitness prediction 성능을 직접 예측한다는 주장은 두지 않는다.

또한 현재 결과는 Ridge feature 비교다. 더 복잡한 model class, mutation-aware structure feature, energy-like feature, learned confidence model을 쓰면 다른 결과가 나올 수 있지만, 결론은 현 설정의 diagnostic 점검으로 제한한다.

가장 실용적인 다음 질문은 현 threshold rule을 더 미세 조정하는 것보다, 먼저 assay 수를 늘렸을 때 6-assay 결론이 유지되는지 확인하는 쪽이다. 별도의 soft gate나 threshold sweep은 그 다음의 설계 질문으로 남는다. 후속 실험은 assay coverage와 protein family 다양성을 늘려, AlphaFold WT geometry 단순 추가가 구조적으로 제한적인지 확인하는 편이 더 직접적이다.

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
Ilho Ahn, "ProteinGym low-label fitness에서 AlphaFold WT geometry와 pLDDT gate 한계 점검", Mini Research, May 9, 2026.
```

또는 BibTeX 형식으로는 다음처럼 적을 수 있다.

```bibtex
@article{ahn2026proteingymaf2plddt,
  author = {Ilho Ahn},
  title = {ProteinGym low-label fitness에서 AlphaFold WT geometry와 pLDDT gate 한계 점검},
  journal = {Mini Research},
  year = {2026},
  month = may,
  url = {https://muted-color.github.io/research/2026/05/09/proteingym-af2-plddt-confidence-audit/}
}
```
