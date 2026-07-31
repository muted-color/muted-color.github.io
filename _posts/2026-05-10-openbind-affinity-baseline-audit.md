---
title: "OpenBind prediction score의 구조 신호 해석 점검"
date: 2026-05-10 18:40:00 +0900
last_modified_at: 2026-07-31 09:36:11 +0900
published: true
publication_status: "published"
categories: ["BIO ML"]
tags: [openbind, affinity-prediction, structure-based-ai, ligand-baseline, benchmark-check, rdkit, ecfp]
lab_path: "experiment-lab/projects/openbind-affinity-baseline-stress"
excerpt: "OpenBind EV-A71 2A prediction score와 MW+cLogP 조정 pKD의 상관을 ligand-only control과 함께 점검한 재현 가능한 benchmark audit."
description: "OpenBind EV-A71 2A의 공개 prediction score를 MW+cLogP 조정 pKD, 같은 campaign의 ligand-only control, 재표집 분석과 비교해 구조 신호 해석의 범위를 점검했다."
permalink: /research/2026/05/10/openbind-affinity-baseline-audit/
image: /assets/images/posts/openbind-affinity-baseline-audit/social-thumbnail.png
image_alt: "OpenBind EV-A71 2A affinity 점검에서 측정 pKD 및 MW+cLogP로 조정한 pKD와의 Spearman을 method별로 비교한 대표 차트"
hero_image: /assets/images/posts/openbind-affinity-baseline-audit/raw-vs-residual-spearman.svg
hero_alt: "OpenBind EV-A71 2A compound-level 점검에서 method별 score가 측정 pKD 및 MW+cLogP로 조정한 pKD와 얼마나 맞는지 비교한 차트"
hero_caption: "<strong>Figure 1.</strong> 각 row는 하나의 method score이며, x축은 그 score가 pKD 순위와 얼마나 비슷한지 나타내는 Spearman correlation이다. 진한 막대는 측정 pKD와의 상관이고, 빗금 막대는 MW+cLogP로 조정한 pKD와의 상관이다. 왼쪽 묶음은 같은 EV-A71 2A 데이터로 학습한 ligand-only control군, 단순 property 기준선, 공개 benchmark score를 구분한다. 진한 막대보다 빗금 막대가 짧아지면, raw pKD 상관이 MW+cLogP trend와 겹쳤을 가능성을 검토할 수 있다. 막대의 정확한 수치는 Table 3과 Appendix Table 2에 정리했다."
hero_frame: true
hero_compact: true
---

OpenBind의 첫 공개 release는 compound별 affinity와 여러 구조 기반 method의 prediction score를 함께 제공한다. 공식 분석에서는 molecular weight도 이 release의 강한 affinity-ranking baseline으로 보고됐다 <a class="citation-ref" href="#ref-openbind-first-release" aria-label="Reference 1">[1]</a>.

이 글은 공개 compound 표를 독립적으로 재구성하고, prediction score가 MW+cLogP로 조정한 pKD와도 상관을 유지하는지 확인한다. 조정 pKD와 가장 높은 상관을 보인 공개 score는 Boltz-2의 `0.097`이었고, 같은 campaign label로 학습한 ligand-only ECFP control은 `0.430`이었다.

두 값은 동일한 학습 조건에서 얻은 model ranking이 아니다. 이 비교는 구조 기여를 직접 분해하거나 새 chemical series의 일반화 성능을 평가하지 않으며, 공개 score와 pKD의 상관을 구조 기반 affinity 신호로 읽기 전에 필요한 retrospective audit으로 한정된다.

## 요약

- OpenBind는 이 release에서 molecular weight가 강한 affinity-ranking baseline이라는 점을 이미 제시했다. 이 audit은 그 관찰을 compound 단위에서 재확인하고 MW+cLogP 조정과 ligand-only control을 추가한다.
- 분석 대상은 공개 benchmark와 맞춘 `494` compounds와 `7`개 score 파일이다. 이 중 `5`개는 학습·scoring method의 score이고 `2`개는 molecular weight와 cLogP property baseline이다.
- MW+cLogP 조정 pKD는 전체 compound 표에서 계산한 진단용 값이다. 이 값과 가장 높은 상관을 보인 공개 method score는 Boltz-2의 `0.097`이었다.
- ECFP ridge의 `0.430`은 같은 campaign의 raw pKD로 학습한 shuffled 5-fold out-of-fold ligand-only control이다. 공개 score와 동일 학습 조건의 model ranking이나 새 chemical series에 대한 일반화 결과가 아니다.
- Compound 및 chemical-group 재표집에서도 공개 score와 ligand-only control의 평균 순서는 유지됐다. 다만 group-held-out 재학습이 아니므로 엄격한 scaffold 일반화 근거로 읽지 않는다.
- 별도 follow-up에서는 prepared structure에서 만든 거리·접촉·atom-count descriptor를 ECFP에 추가해도 상관이 높아지지 않았다. 이 결과는 주 비교의 재현이 아니라 제한된 구조 descriptor 설계에 대한 보조 결과다.

{% include model-mention-cards.html label="사용한 공개 리소스" aria_label="OpenBind release와 benchmark 리소스" models="OpenBind first release|EV-A71 2A structure-affinity dataset|https://openbind.uk/news/blog-openbinds-first-release-a-structure-affinity-dataset-for-structure-based-ai/;Affinity data note|OpenBind affinity and kinetics data|https://openbind.uk/news/blog-affinity-and-kinetics-data-in-the-ev-a71-2a-openbind-release/;EV-A71 2A benchmark|Pinned OpenBind GitHub affinity files|https://github.com/OpenBind-Consortium/EV-A71_2A_benchmark/tree/86e5c12da518d749c33cfa9dcb6ae8eae1b804f9/affinity;Zenodo release|OpenBind structure-affinity data|https://zenodo.org/records/20026661" %}

## 평가 설정

EV-A71 2A protease는 Enterovirus A71 바이러스의 단백질 절단 효소다. OpenBind 첫 release의 실험 구조와 affinity는 EV-A71 2A와 서열의 다섯 위치만 다르고 그 차이가 active site 가까이에 없는 CVA16 2A surrogate에서 생성됐다 <a class="citation-ref" href="#ref-openbind-first-release" aria-label="Reference 1">[1]</a>.

> **pKD**는 dissociation constant를 로그 스케일로 표현한 값으로, 값이 클수록 강한 결합을 뜻한다. **Spearman correlation**은 두 값의 절대 크기보다 순위가 얼마나 비슷한지 본다.
>
> **MW와 cLogP**는 각각 분자량과 계산된 지용성이다. 이 글에서 MW+cLogP 조정 pKD는 두 물성으로 설명되는 trend를 뺀 진단용 값이며, 구조 정보에서 온 신호의 정답을 뜻하지 않는다. **Ligand-only control**은 단백질 구조 없이 ECFP/RDKit compound 표현만 사용하는 비교 기준이다.

이 글의 비교 단위는 compound다. OpenBind affinity 원자료에는 같은 compound에 대한 측정값이 여러 행으로 들어갈 수 있고, 공개 자료의 분석 포함 표시를 통해 그중 최종 benchmark에 사용된 행을 구분할 수 있다 <a class="citation-ref" href="#ref-openbind-affinity-note" aria-label="Reference 2">[2]</a>. OpenBind repository에는 affinity 측정값, compound 정보, method별 prediction score, score를 비교 표로 정리하는 규칙이 공개되어 있다 <a class="citation-ref" href="#ref-openbind-github" aria-label="Reference 3">[3]</a>.

이 글은 원자료의 측정값을 다시 해석하거나, 여러 측정 행을 pKD 하나로 다시 합치지 않는다. 대신 공개 benchmark에서 이미 정리된 compound 단위 표에 맞춘다. 같은 compound와 method 조합에 대해 공개 prediction score와 compound 단위 pKD를 나란히 두고 비교한다.

비교는 두 단계로 나눈다. 먼저 prediction score가 측정 pKD 순위와 얼마나 비슷한지 본다. 그다음 pKD에서 분자량과 cLogP로 설명되는 부분을 뺀 뒤에도 그 상관이 유지되는지 본다. 이 비교는 구조 기반 방법의 최종 평가가 아니라, pKD와의 상관을 구조 기반 affinity 신호로 해석해도 되는지 먼저 가르는 기본 점검이다.

평가 계약은 다음과 같다.

- **공개 benchmark score**는 OpenBind가 제공한 compound-level score를 재학습하거나 보정하지 않고 사용한다.
- **MW+cLogP 조정 pKD**는 `494` compounds 전체에서 pKD를 molecular weight와 cLogP에 선형 회귀한 뒤 남은 값이다. Held-out target이 아니라 전체 표에 대한 설명용 조정값이다.
- **Ligand-only control**은 같은 `494` compounds에서 shuffled 5-fold 교차검증으로 만든 out-of-fold prediction이다. ECFP ridge는 raw pKD를 학습하며, fold는 scaffold나 similarity cluster가 아닌 compound 단위로 나뉘다.
- **불확실성 범위**는 이미 계산된 score와 out-of-fold prediction을 고정한 채 compound 또는 chemical group을 재표집해 계산한다. 모델 재학습 변동이나 새 chemical series에 대한 성능 범위는 포함하지 않는다.

Table 1은 원자료가 최종 비교 단위로 정리되는 과정을 세 묶음으로 요약한다.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--analysis-scope">
      <thead>
        <tr>
          <th>묶음</th>
          <th>항목</th>
          <th class="align-right">값</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td rowspan="3"><strong>공개 원자료</strong></td>
          <td>affinity 측정 행</td>
          <td class="align-right"><code>2733</code></td>
        </tr>
        <tr>
          <td>benchmark에 사용된 측정 행</td>
          <td class="align-right"><code>1613</code></td>
        </tr>
        <tr>
          <td>구조가 연결된 행</td>
          <td class="align-right"><code>925</code></td>
        </tr>
        <tr>
          <td><strong>공개 score</strong></td>
          <td>compound와 method 조합별 score 행</td>
          <td class="align-right"><code>3458</code></td>
        </tr>
        <tr>
          <td rowspan="3"><strong>최종 비교 단위</strong></td>
          <td>이 글에서 비교한 compounds</td>
          <td class="align-right"><code>494</code></td>
        </tr>
        <tr>
          <td>RDKit 처리 가능 compounds</td>
          <td class="align-right"><code>494</code></td>
        </tr>
        <tr>
          <td>공개 score 파일<br><span class="table-note-inline">5 methods + 2 property baselines</span></td>
          <td class="align-right"><code>7</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> 원자료에서 최종 비교 표로 정리되는 과정을 요약했다. 실제 분석은 pKD를 같은 compound 단위로 맞춘 <code>494</code> compounds에서 진행했다. 공개 score 파일 <code>7</code>개는 학습·scoring method <code>5</code>개와 property baseline <code>2</code>개로 나뉘다.</figcaption>
</figure>

## 결과

### 공개 property baseline 관찰의 재확인

OpenBind 공개 글은 molecular weight가 이 release의 강한 affinity-ranking baseline이라는 점을 이미 제시했다 <a class="citation-ref" href="#ref-openbind-first-release" aria-label="Reference 1">[1]</a>. 이 audit에서도 molecular weight와 측정 pKD의 Spearman은 `0.484`였고, MW+cLogP 선형 모델은 전체 compound 표의 pKD 변동 중 약 30%를 설명했다 (`R2 = 0.299`).

이 결과는 새로운 ligand-property 효과를 주장하기 위한 것이 아니다. 이후 공개 prediction score의 상관을 MW+cLogP trend와 분리해 읽기 위한 출발 조건이다.

Figure 2는 molecular weight와 pKD의 관계를 나타낸다.

<figure class="media-figure">
  <img src="/assets/images/posts/openbind-affinity-baseline-audit/pkd-vs-mw.svg" alt="OpenBind EV-A71 2A compound-level table에서 molecular weight와 pKD의 양의 관계를 보여주는 산점도">
  <figcaption><strong>Figure 2.</strong> Molecular weight와 pKD의 관계다. 분자량만 봤을 때의 Spearman은 <code>0.484</code>였고, 선은 설명용 선형 trend다. 이 관계는 측정 pKD와의 상관을 해석할 때 먼저 확인해야 하는 단순 ligand property 기준선으로 사용했다.</figcaption>
</figure>

이후 비교는 `494` compounds 전체에서 pKD를 분자량과 cLogP에 선형 회귀한 뒤 남은 값에서 진행했다. 이 값은 실제 약물화학 과정에서 제거해야 할 모든 신호를 뜻하지 않는다. Compound가 커지거나 지용성이 바뀌는 흐름 자체도 potency 변화와 함께 움직일 수 있다. 따라서 여기서 만든 값은 “진짜 affinity 신호”의 정답이 아니라, 전체 표에 대한 descriptive adjustment이며 prediction score와 pKD의 상관이 큰 property trend에 얼마나 의존하는지 보기 위한 비교 대상이다.

Table 2는 MW+cLogP를 빼기 전에 확인한 ligand-property 기준선이다.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>비교</th>
          <th>지표</th>
          <th class="align-right">값</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>molecular weight</td>
          <td>측정 pKD와의 Spearman</td>
          <td class="align-right"><code>0.484</code></td>
        </tr>
        <tr>
          <td>MW+cLogP 선형 모델</td>
          <td>설명용 <code>R2</code></td>
          <td class="align-right"><code>0.299</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> 측정 pKD와의 상관을 해석하기 전에 확인한 단순 ligand property 기준선이다. MW+cLogP는 최종 모델 비교 기준이 아니라, 공개 release에서 property trend의 크기를 확인하기 위한 비교 대상이다.</figcaption>
</figure>

### MW+cLogP로 조정한 pKD와의 상관

먼저 전체 `494` compounds에서 pKD를 분자량과 cLogP에 선형 회귀하고 residual을 계산했다. 그런 다음 이 조정 pKD 순위와 각 method score 순위가 얼마나 비슷한지 봤다.

그 결과 OpenBind에 공개된 benchmark score 중 가장 높은 값은 Boltz-2의 Spearman `0.097`이었다. 반면 구조를 쓰지 않고 compound 정보만 본 ECFP ridge 비교 기준은 `0.430`을 보였다.

즉 공개 score는 측정 pKD와는 어느 정도 같이 움직였지만, MW+cLogP 조정 pKD 순위는 잘 따라가지 못했다. 같은 데이터 안에서는 구조를 쓰지 않은 ligand-only 비교 기준이 이 조정 pKD와 더 높은 상관을 보였다.

이 글에서는 각 score가 MW+cLogP 조정 pKD와도 상관을 유지하는지를, 단순 ligand property trend를 넘어선 신호를 검토하는 최소 진단 기준으로 둔다. 이 상관이 곧 “구조 정보를 잘 읽었다”는 직접 증거는 아니다.

OpenBind 공개 benchmark score와 ECFP ridge control은 같은 역할의 모델이 아니다. 공개 benchmark score는 외부에서 제공된 고정 score이고, ECFP ridge는 같은 EV-A71 2A campaign의 raw pKD를 사용해 shuffled 5-fold 교차검증으로 만든 supervised ligand-only out-of-fold prediction이다. Morgan fingerprint는 radius `2`, `2048` bits를 사용했고 Ridge alpha는 `10`, split seed는 `20260508`이었다.

따라서 `0.097`과 `0.430`의 차이는 동일한 학습·평가 계약에서 얻은 model ranking이 아니다. 같은 campaign의 ligand 표현만으로도 MW+cLogP 조정 pKD와 더 높은 상관이 나올 수 있음을 보여주는 진단적 비교다. 이 조건에서 공개 score의 raw pKD 상관만으로 구조 정보의 독립적 기여를 특정하기 어렵다는 것이 남는 결론이다.

Table 3은 이 역할 구분을 유지한 채 MW+cLogP로 조정한 pKD와의 Spearman만 압축해 보여준다.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>score 출처</th>
          <th>가장 높은 method</th>
          <th>구조 정보 사용</th>
          <th class="align-right">MW+cLogP 조정 pKD<br><span class="table-note-inline">Spearman</span></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>공개 benchmark score</td>
          <td>Boltz-2</td>
          <td>구조/pose 사용</td>
          <td class="align-right"><code>0.097</code></td>
        </tr>
        <tr>
          <td>ligand-only<br><span class="table-note-inline">같은 EV-A71 2A 데이터</span></td>
          <td>ECFP ridge</td>
          <td>사용 안 함</td>
          <td class="align-right"><code>0.430</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> 각 score와 MW+cLogP로 조정한 pKD 사이의 주 비교다. 구조 정보 사용 여부를 함께 표시해 공개 benchmark score와 ligand-only control의 역할을 구분했다. 가장 높은 공개 benchmark Spearman에서 ligand-only control Spearman을 빼면, 반올림 전 값 기준 <code>-0.334</code>였다. 이 차이는 동일 학습 조건의 모델 간 성능 차이가 아니라 공개 고정 score와 campaign-supervised ligand control 사이의 진단적 간격이다.</figcaption>
</figure>

Figure 1은 각 score가 측정 pKD 및 MW+cLogP로 조정한 pKD와 보이는 Spearman을 함께 나타낸다. 공개 score의 상관은 조정 pKD에서 전반적으로 약해진 반면, 같은 campaign의 ligand 표현으로 만든 control은 더 높은 상관을 보였다. 이 비교는 유사 compound 사이의 예측 성능을 직접 평가하지 않지만, raw pKD 상관만으로 공개 score가 구조 정보를 잘 읽었다고 강하게 주장하기 어렵다는 점을 보여준다.

### 재표집 기반 민감도 확인

앞의 상관이 compound 구성 변화에 얼마나 민감한지 보기 위해, 이미 계산된 score와 out-of-fold prediction을 고정한 채 compound 행을 `1000`회 복원 재표집했다. 이 범위는 모델을 다시 학습했을 때의 변동이 아니라, 현재 `494` compounds의 재표집에 따른 상관 변동이다. MW+cLogP 조정 pKD와의 Spearman 평균은 Boltz-2 `0.096`, ECFP ridge control `0.429`였고, 95% 범위는 각각 `[0.008, 0.179]`, `[0.354, 0.497]`였다.

Table 4는 MW+cLogP로 조정한 pKD와의 Spearman 불확실성 범위를 method별로 정리한다.

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>method</th>
          <th>구조 정보 사용</th>
          <th class="align-right">MW+cLogP 조정 pKD<br><span class="table-note-inline">Spearman 평균</span></th>
          <th class="align-right">95% 범위</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>ECFP ridge</td><td>사용 안 함</td><td class="align-right"><code>0.429</code></td><td class="align-right"><code>[0.354, 0.497]</code></td></tr>
        <tr><td>RDKit descriptor RF</td><td>사용 안 함</td><td class="align-right"><code>0.337</code></td><td class="align-right"><code>[0.258, 0.413]</code></td></tr>
        <tr><td>RDKit descriptor ridge</td><td>사용 안 함</td><td class="align-right"><code>0.263</code></td><td class="align-right"><code>[0.175, 0.345]</code></td></tr>
        <tr><td>Boltz-2</td><td>구조/pose 사용</td><td class="align-right"><code>0.096</code></td><td class="align-right"><code>[0.008, 0.179]</code></td></tr>
        <tr><td>Gnina crystal</td><td>구조/pose 사용</td><td class="align-right"><code>0.015</code></td><td class="align-right"><code>[-0.073, 0.104]</code></td></tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> 이미 계산된 score와 out-of-fold prediction을 고정하고 compound 행을 <code>1000</code>회 재표집해 얻은 MW+cLogP 조정 pKD와의 Spearman 범위다. 공개 benchmark score 중 가장 높은 상관은 약하게 양수였지만, 이 비교에서는 ligand-only control과 같은 범위로 올라오지 않았다.</figcaption>
</figure>

Grouped bootstrap은 Murcko scaffold 또는 Butina cluster를 재표집 단위로 사용해, 특정 chemical group의 비중 변화가 상관의 방향을 뒤집는지 확인했다. 각 반복에서 group을 복원 추출하고 그 group에 속한 compound 행의 Spearman을 다시 계산했다. ECFP ridge를 group-held-out fold에서 다시 학습한 것은 아니므로, 유사 compound가 학습 fold와 평가 fold에 함께 들어가는 문제를 제거하지 않는다.

Murcko scaffold 단위 `300`회 재표집에서 공개 benchmark score 중 가장 높은 평균은 Boltz-2의 `0.098`, ligand-only control 중 가장 높은 평균은 ECFP ridge의 `0.421`이었고 차이는 `-0.323`이었다. Figure 3은 별도의 Butina Tanimoto 0.6 재표집 결과를 보여준다. 여기서 Boltz-2는 `0.075`, ECFP ridge는 `0.395`, 차이는 `-0.320`이었다. 두 grouping에서 비교 방향은 유지됐지만, 이는 chemical-series generalization이 아니라 현재 score의 group-weighting sensitivity다.

> **Murcko scaffold**는 compound의 중심 골격을 기준으로 비슷한 compound를 묶는 방식이다.
>
> **Butina Tanimoto 0.6**은 fingerprint similarity가 높은 compound를 cluster로 묶는 방식이다. 이 글에서는 비슷한 compound 때문에 결론이 쉽게 뒤집히는지 보는 보조 확인으로 사용한다.

Figure 3은 Butina 재표집 결과를, Table 5는 높은 singleton 비율을 포함한 묶음 구성과 해석 한계를 보여준다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/openbind-affinity-baseline-audit/butina-grouped-residual-spearman.svg" alt="고정된 method score와 out-of-fold prediction을 Butina Tanimoto 0.6 cluster 단위로 재표집해 MW+cLogP 조정 pKD와의 Spearman 평균을 점으로, 95% 범위를 선으로 비교한 forest plot">
  <figcaption><strong>Figure 3.</strong> Butina Tanimoto 0.6 cluster를 재표집 단위로 사용해, 이미 계산된 method score와 out-of-fold prediction이 MW+cLogP 조정 pKD와 보이는 Spearman을 다시 계산했다. 점은 <code>300</code>회 grouped bootstrap 평균, 선은 95% 범위다. 모델을 cluster-held-out 조건에서 다시 학습한 결과가 아니므로 chemical-series generalization이 아니라 cluster 구성에 대한 민감도로 해석한다.</figcaption>
</figure>

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>묶는 기준</th>
          <th class="align-right">묶음 수</th>
          <th class="align-right">compound 1개짜리 묶음</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Murcko scaffold</td>
          <td class="align-right"><code>275</code></td>
          <td class="align-right"><code>82.2%</code></td>
        </tr>
        <tr>
          <td>Butina Tanimoto 0.6</td>
          <td class="align-right"><code>175</code></td>
          <td class="align-right"><code>71.4%</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 5.</strong> Grouped bootstrap의 묶음 구성이다. Compound 1개짜리 묶음 비율이 높고 모델을 group-held-out 조건에서 재학습하지 않았으므로 엄격한 scaffold split이 아니다. 현재 상관의 방향이 일부 chemical group의 재표집 가중치에 쉽게 뒤집히는지만 확인한다.</figcaption>
</figure>

### Prepared-structure descriptor 보조 확인

> **Prepared-structure descriptor**는 공개 구조에서 protein·ligand atom 수, 최소 거리, 거리 threshold별 접촉 수, 원소쌍과 pocket residue 정보를 계산하고 compound별 평균과 최댓값으로 모은 feature다. 정교한 interaction model이 아니라 prepared pose 주변의 크기·거리·접촉량을 거칠게 요약한다.

공개 score 분석과 별도로, 단순한 prepared-structure descriptor가 ligand representation에 추가 신호를 주는지만 제한적으로 확인했다. Zenodo v1의 prepared structure archive <a class="citation-ref" href="#ref-openbind-zenodo" aria-label="Reference 4">[4]</a>에서 atom 수와 최소 거리, 거리 threshold `3.5`, `4.5`, `6.0`, `8.0` Å의 protein-ligand 접촉, 원소쌍과 pocket residue 정보를 포함한 `312`개 descriptor를 만들었다.

구조 파일 `925`개는 모두 파싱했다. 이 가운데 공개 compound reference에 연결된 `649`개 structure instances를 `494` compounds 단위로 모아 follow-up 모델 입력으로 사용했다.

이 follow-up의 ECFP 기준은 앞의 `0.430` ECFP ridge와 평가 파이프라인이 다르다. 주 비교의 `0.430`은 ECFP로 raw pKD를 예측한 5-fold out-of-fold score와 전체 표에서 계산한 조정 pKD의 상관이다. 여기서 사용하는 `0.360`은 ECFP를 sparse scaling한 뒤 조정 pKD 자체를 직접 예측하도록 같은 shuffled 5-fold 교차검증에서 다시 학습한 결과다. 따라서 `0.430`에서 `0.360`으로 성능이 감소했다는 비교는 성립하지 않으며, `0.360`은 prepared-structure descriptor 추가 효과를 보기 위한 follow-up 내부 기준선이다.

이 동일 follow-up 파이프라인 안에서는 prepared-structure descriptor만 사용한 모델이 Spearman `0.156`, ECFP에 descriptor를 더한 모델이 `0.279`, ECFP만 사용한 기준선이 `0.360`이었다. 따라서 descriptor를 추가했을 때의 차이는 `-0.081`이다.

Table 6은 prepared-structure descriptor를 더했을 때 MW+cLogP 조정 pKD와의 Spearman을 요약한다.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--compact-two-col">
      <thead>
        <tr>
          <th>입력 정보</th>
          <th class="align-right">MW+cLogP 조정 pKD<br><span class="table-note-inline">Spearman</span></th>
        </tr>
      </thead>
      <tbody>
        <tr><td>ECFP만 사용</td><td class="align-right"><code>0.360</code></td></tr>
        <tr><td>Prepared-structure descriptors</td><td class="align-right"><code>0.156</code></td></tr>
        <tr><td>ECFP + structure descriptors</td><td class="align-right"><code>0.279</code></td></tr>
        <tr><td>RDKit descriptors + ECFP</td><td class="align-right"><code>0.369</code></td></tr>
        <tr><td>RDKit descriptors + ECFP<br><span class="table-note-inline">+ structure descriptors</span></td><td class="align-right"><code>0.283</code></td></tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 6.</strong> MW+cLogP 조정 pKD를 직접 예측하도록 동일한 shuffled 5-fold 교차검증에서 학습한 follow-up 내부 비교다. ECFP에 prepared structure에서 만든 <code>312</code>개 거리·접촉·atom-count descriptor를 더했을 때의 차이는 <code>-0.081</code>이었고, 고정된 out-of-fold prediction을 <code>1000</code>회 paired row bootstrap한 95% 범위는 <code>[-0.146, -0.012]</code>였다.</figcaption>
</figure>

## 해석

핵심은 prediction score와 측정 pKD의 상관만으로 모델이 구조적 결합 원리를 포착했다고 판단하기 어렵다는 점이다. Score와 pKD의 순위가 비슷해 보여도, 그 상관이 단백질-리간드 구조에서 온 신호인지 단순 ligand property나 campaign의 chemical-series 구성에서 온 신호인지는 따로 확인해야 한다.

OpenBind 공개 benchmark score는 측정 pKD와는 어느 정도 같이 움직였다. 하지만 공개 method 전반에서 MW+cLogP 조정 pKD와의 상관은 약해졌으며, raw pKD 상관이 compound의 크기나 지용성 같은 ligand-property trend와 겹쳤을 가능성이 있다.

구조 정보를 쓰지 않은 ligand-only control은 이 retrospective audit에서 MW+cLogP 조정 pKD와 더 강한 상관을 보였다. 다만 이 control은 같은 campaign의 label로 학습한 random-fold out-of-fold prediction이므로, 공개 benchmark score를 대체하거나 prospective model 우위를 보이는 결과가 아니다. 같은 campaign의 ligand 정보만으로도 더 높은 상관이 나오는 조건에서는 공개 score의 raw pKD 상관만으로 구조 기반 affinity 신호를 강하게 해석하기 어렵다는 것이 이 비교의 범위다.

이 결론은 OpenBind 전체나 구조 기반 affinity prediction 일반에 대한 판정이 아니다. 이 release의 공개 prediction score를 구조 신호로 해석하려면 측정 pKD와의 상관만 보지 말고, 분자량·cLogP 같은 단순 property 기준선과 ligand-only control을 함께 비교해야 한다. 더 나아가 구조 기반 일반화를 주장하려면 새로운 chemical series를 분리한 group-held-out 또는 prospective 평가가 필요하다.

## 한계

- 이 결과는 공개된 EV-A71 2A release 하나에 한정된다. 새 compound를 미리 분리한 prospective 평가가 아니며, OpenBind 전체나 구조 기반 affinity prediction 일반의 성능을 판정하지 않는다.
- MW+cLogP 조정은 전체 `494` compounds에서 계산한 descriptive adjustment다. Property trend도 실제 potency 변화와 얽힐 수 있으므로, 조정 후 pKD를 구조 정보에서 온 신호의 정답으로 해석하지 않는다.
- ECFP control은 같은 campaign의 raw pKD로 학습한 random 5-fold out-of-fold 모델이다. 공개된 고정 score와 동일 조건의 model ranking이 아니며, 새로운 chemical series에 대한 일반화 성능을 보여주지 않는다.
- Grouped bootstrap은 기존 score와 prediction을 고정한 채 chemical group을 재표집했다. Group-held-out 재학습이 아니고 singleton group 비율도 높으므로, analog leakage를 제거하거나 scaffold 일반화를 입증하지 않는다.
- 측정 행을 compound pKD로 정리하는 규칙과 측정 불확실성에 대한 민감도는 평가하지 않았다. Structure follow-up도 prepared pose에서 집계한 `312`개 거리·접촉·atom-count descriptor에 한정되므로, 더 정교한 구조 표현의 유효성을 배제하지 않는다.

## Appendix: 평가·재현 계약

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>단계</th>
          <th>고정한 계약</th>
          <th>해석 경계</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>입력 snapshot</td>
          <td>OpenBind affinity repository의 <a href="https://github.com/OpenBind-Consortium/EV-A71_2A_benchmark/tree/86e5c12da518d749c33cfa9dcb6ae8eae1b804f9/affinity"><code>86e5c12</code> revision</a>과 Zenodo <code>v1</code></td>
          <td>실험 provenance의 affinity 입력 <code>11</code>개 SHA-256이 이 revision의 파일과 일치함을 <code>2026-07-30</code>에 다시 확인</td>
        </tr>
        <tr>
          <td>MW+cLogP 조정</td>
          <td>전체 <code>494</code> compounds에 OLS 1회 적합</td>
          <td>전체 표에서 계산한 설명용 조정값이며 cross-fitted target이 아님</td>
        </tr>
        <tr>
          <td>Ligand-only control</td>
          <td>Shuffled 5-fold CV, seed <code>20260508</code>; ECFP radius <code>2</code>, <code>2048</code> bits; Ridge alpha <code>10</code></td>
          <td>Compound-random OOF prediction이며 scaffold-disjoint 평가가 아님</td>
        </tr>
        <tr>
          <td>Compound bootstrap</td>
          <td>고정 score/prediction의 행을 <code>1000</code>회 복원 추출</td>
          <td>Percentile 95% 범위; 모델과 MW+cLogP 조정 모델을 다시 적합하지 않음</td>
        </tr>
        <tr>
          <td>Grouped bootstrap</td>
          <td>Murcko 또는 Butina Tanimoto 0.6 group을 <code>300</code>회 복원 추출</td>
          <td>Group-held-out 재학습이 아니라 group-weighting sensitivity</td>
        </tr>
        <tr>
          <td>Prepared-structure descriptor</td>
          <td>Zenodo v1 구조 <code>925</code>개 파싱, reference-linked instances <code>649</code>개를 <code>494</code> compounds와 <code>312</code> features로 집계</td>
          <td>조정 pKD를 직접 학습한 별도 5-fold pipeline; 주 비교의 ECFP <code>0.430</code>과 직접 비교하지 않음</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 1.</strong> 본문의 수치를 재현하고 해석할 때 필요한 평가 계약이다. Python <code>3.12.3</code>, NumPy <code>2.2.6</code>, pandas <code>2.3.3</code>, SciPy <code>1.17.1</code>, scikit-learn <code>1.7.1</code>, RDKit <code>2026.03.1</code>에서 실행했다.</figcaption>
</figure>

핵심 분석은 <a href="https://github.com/muted-color/openbind-affinity-score-audit">OpenBind Affinity Score Audit 재현 저장소</a>에서 다시 실행할 수 있다. 저장소는 고정된 OpenBind revision에서 입력 CSV를 내려받아 SHA-256을 확인하고, compound 표 재구성, MW+cLogP 조정, ligand-only control, Murcko·Butina grouped sensitivity를 한 명령으로 재현한다. Prepared-structure descriptor follow-up은 핵심 audit의 공개 범위에 포함하지 않는다.

본문에는 해석에 필요한 주요 수치만 두었다. Appendix Table 2는 전체 method의 측정 pKD Spearman과 MW+cLogP 조정 pKD Spearman을 함께 보기 위한 보조 자료다. 이 표도 method 순위를 확정하기보다 두 상관의 차이를 점검하는 용도로 둔다.

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>method</th>
          <th class="align-right">측정 pKD<br><span class="table-note-inline">Spearman</span></th>
          <th class="align-right">MW+cLogP 조정 pKD<br><span class="table-note-inline">Spearman</span></th>
          <th class="align-right">ECFP ridge 대비 차이</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>ECFP ridge</td><td class="align-right"><code>0.672</code></td><td class="align-right"><code>0.430</code></td><td class="align-right"><code>0.000</code></td></tr>
        <tr><td>RDKit descriptor RF</td><td class="align-right"><code>0.627</code></td><td class="align-right"><code>0.337</code></td><td class="align-right"><code>-0.093</code></td></tr>
        <tr><td>RDKit descriptor ridge</td><td class="align-right"><code>0.605</code></td><td class="align-right"><code>0.264</code></td><td class="align-right"><code>-0.166</code></td></tr>
        <tr><td>Boltz-2</td><td class="align-right"><code>0.397</code></td><td class="align-right"><code>0.097</code></td><td class="align-right"><code>-0.334</code></td></tr>
        <tr><td>Smina crystal</td><td class="align-right"><code>0.255</code></td><td class="align-right"><code>0.038</code></td><td class="align-right"><code>-0.392</code></td></tr>
        <tr><td>Gnina crystal</td><td class="align-right"><code>0.453</code></td><td class="align-right"><code>0.018</code></td><td class="align-right"><code>-0.412</code></td></tr>
        <tr><td>cLogP</td><td class="align-right"><code>0.174</code></td><td class="align-right"><code>0.014</code></td><td class="align-right"><code>-0.416</code></td></tr>
        <tr><td>molecular weight</td><td class="align-right"><code>0.484</code></td><td class="align-right"><code>-0.017</code></td><td class="align-right"><code>-0.448</code></td></tr>
        <tr><td>MW+cLogP ridge</td><td class="align-right"><code>0.484</code></td><td class="align-right"><code>-0.020</code></td><td class="align-right"><code>-0.451</code></td></tr>
        <tr><td>AqAffinity</td><td class="align-right"><code>0.117</code></td><td class="align-right"><code>-0.057</code></td><td class="align-right"><code>-0.487</code></td></tr>
        <tr><td>AEV-PLIG</td><td class="align-right"><code>0.227</code></td><td class="align-right"><code>-0.085</code></td><td class="align-right"><code>-0.516</code></td></tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 2.</strong> Method별 측정 pKD Spearman과 MW+cLogP 조정 pKD Spearman이다. ECFP ridge 대비 차이는 그 control의 조정 pKD Spearman 반올림 전 값을 기준으로 계산했으며, 직접 순위표가 아니라 raw pKD와 조정 pKD의 상관 차이를 보는 보조 표로 사용한다.</figcaption>
</figure>

## References

<div class="reference-list" markdown="1">

<ol>
  <li id="ref-openbind-first-release">OpenBind Consortium. <strong>OpenBind's first release: A structure-affinity dataset for structure-based AI</strong>. OpenBind, May 5, 2026. <a href="https://openbind.uk/news/blog-openbinds-first-release-a-structure-affinity-dataset-for-structure-based-ai/">OpenBind blog</a></li>
  <li id="ref-openbind-affinity-note">OpenBind Consortium. <strong>Affinity and Kinetics Data in the EV-A71 2A OpenBind Release</strong>. OpenBind, May 5, 2026. <a href="https://openbind.uk/news/blog-affinity-and-kinetics-data-in-the-ev-a71-2a-openbind-release/">OpenBind blog</a></li>
</ol>

</div>

## Experiment Resources

<div class="reference-list" markdown="1">

<ol start="3">
  <li id="ref-openbind-github">OpenBind Consortium. <strong>EV-A71_2A_benchmark affinity files</strong>. GitHub, revision <code>86e5c12</code>, 2026. <a href="https://github.com/OpenBind-Consortium/EV-A71_2A_benchmark/tree/86e5c12da518d749c33cfa9dcb6ae8eae1b804f9/affinity">Pinned repository directory</a>. Repository code: Apache-2.0; released data: CC0 1.0.</li>
  <li id="ref-openbind-zenodo">OpenBind Consortium. <strong>OpenBind Structure-Affinity Data Release: Enterovirus A71 (EV-A71) / Coxsackievirus A16 (CVA16) 2A protease</strong>. Zenodo, version v1, May 5, 2026. DOI: <a href="https://doi.org/10.5281/zenodo.20026661">10.5281/zenodo.20026661</a>. Data license: CC0 1.0.</li>
  <li id="ref-openbind-audit-reproduction">Soleaf. <strong>OpenBind Affinity Score Audit</strong>. GitHub, version <code>0.1.0</code>, 2026. <a href="https://github.com/muted-color/openbind-affinity-score-audit">Reproduction repository</a>. License: Apache-2.0.</li>
</ol>

</div>

본문의 비교 단위와 전체 method 결과는 Table 1과 Appendix Table 2에 요약했다.

## Citation

Text citation:

```text
Ilho Ahn, "OpenBind prediction score의 구조 신호 해석 점검", Mini Research, May 10, 2026.
```

BibTeX:

```bibtex
@misc{ahn2026openbind_affinity_baseline_check,
  author = {Ahn, Ilho},
  title = {OpenBind prediction score의 구조 신호 해석 점검},
  year = {2026},
  month = {May},
  howpublished = {Mini Research},
  url = {https://muted-color.github.io/research/2026/05/10/openbind-affinity-baseline-audit/}
}
```
