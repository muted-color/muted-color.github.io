---
title: "OpenBind prediction score를 구조 신호로 읽을 수 있을까"
date: 2026-05-10 18:40:00 +0900
last_modified_at: 2026-05-18 16:58:52 +0900
categories: ["BIO ML"]
tags: [openbind, affinity-prediction, structure-based-ai, ligand-baseline, benchmark-check, rdkit, ecfp]
lab_path: "experiment-lab/projects/openbind-affinity-baseline-stress"
excerpt: "OpenBind EV-A71 2A release에서 공개 prediction score가 측정 pKD와 보이는 상관이 MW+cLogP 영향을 뺀 뒤에도 유지되는지 점검한 노트."
description: "OpenBind EV-A71 2A release에서 공개 prediction score와 측정 pKD의 상관이 분자량과 cLogP trend에 얼마나 기대는지 점검한 노트."
permalink: /research/2026/05/10/openbind-affinity-baseline-audit/
image: /assets/images/posts/openbind-affinity-baseline-audit/social-thumbnail.png
image_alt: "OpenBind EV-A71 2A affinity 점검에서 측정 pKD와의 Spearman 및 MW+cLogP 영향을 뺀 뒤의 Spearman을 method별로 비교한 대표 차트"
hero_image: /assets/images/posts/openbind-affinity-baseline-audit/raw-vs-residual-spearman.svg
hero_alt: "OpenBind EV-A71 2A compound-level 점검에서 method별 score가 측정 pKD 및 MW+cLogP 영향을 뺀 뒤의 pKD와 얼마나 맞는지 비교한 차트"
hero_caption: "<strong>Figure 1.</strong> 각 row는 하나의 method score이며, x축은 그 score가 pKD 순위와 얼마나 비슷한지 나타내는 Spearman correlation이다. 빈 막대는 측정 pKD와의 상관이고, 진한 막대는 pKD에서 MW+cLogP trend를 뺀 뒤의 상관이다. 왼쪽 묶음은 같은 EV-A71 2A 데이터로 학습한 ligand-only 비교 기준, 단순 property 기준선, 공개 benchmark score를 구분한다. 빈 막대보다 진한 막대가 크게 짧아지면, 측정 pKD와의 상관 중 상당 부분이 MW+cLogP trend와 겹쳤을 가능성이 있다. 막대의 정확한 수치는 Table 3과 Appendix Table 1에 정리했다."
hero_frame: true
hero_compact: true
---

OpenBind의 첫 공개 release는 구조, affinity 측정값, benchmark 파일을 함께 제공한다 <a class="citation-ref" href="#ref-openbind-first-release" aria-label="Reference 1">[1]</a>. 이 release에는 compound별 측정 affinity와 여러 method의 prediction score가 함께 들어 있다.

> **EV-A71 2A protease**는 Enterovirus A71 바이러스의 단백질 절단 효소다. OpenBind 첫 release는 이 target에 결합하는 compound들의 구조와 affinity 측정값, 그리고 benchmark용 prediction score를 함께 제공한다.
>
> **Prediction score**는 각 method가 compound에 매긴 점수다. 이 score가 pKD와 상관을 보인다는 것은 두 값의 순위가 비슷하다는 뜻이지, score 자체를 affinity 값으로 읽어도 된다는 뜻은 아니다.
>
> **pKD**는 binding affinity를 로그 스케일로 표현한 값이다. 여기서 KD는 kilodalton(kDa)이 아니라 dissociation constant다. KD는 작을수록 강한 결합이고, pKD는 클수록 강한 결합으로 읽는다. 이 글에서는 affinity가 높은 compound가 더 높은 pKD를 갖는 순위 비교로 해석한다.
>
> **Spearman correlation**은 두 값의 절대 크기보다 순위가 얼마나 비슷한지 보는 상관 지표다. 이 글에서는 method score가 pKD 순위를 얼마나 따라가는지 볼 때 사용한다.
>
> **MW와 cLogP**는 각각 molecular weight, 즉 분자량과 계산된 지용성 지표다. 둘 다 compound의 단순한 물성으로 볼 수 있다.
>
> **MW+cLogP 영향을 뺀 pKD**는 pKD에서 분자량과 cLogP만으로 설명되는 부분을 먼저 제거한 값이다. 이 값이 곧 “구조 정보에서 온 진짜 affinity 신호”라는 뜻은 아니다. 이 글에서는 측정 pKD와의 상관이 단순 ligand property trend에 얼마나 기대는지 보기 위한 비교 대상으로 사용한다.
>
> **공개 benchmark score**는 OpenBind benchmark repository에 공개된 method별 prediction score 파일을 뜻한다.
>
> **Ligand-only 비교 기준**은 구조 정보를 쓰지 않고 compound의 ligand 표현만 사용한 ECFP/RDKit 계열 모델이다. ECFP는 compound 구조를 fingerprint로 바꾼 표현이고, ridge는 그 표현으로 pKD 순서를 맞추는 단순 회귀 모델이다. 이 기준은 공개 prediction score를 대체하려는 모델이 아니라, 같은 데이터 안에서 ligand 정보만으로 어느 정도 상관이 나오는지 보기 위한 비교 기준이다.

이 글은 OpenBind의 prediction score가 pKD와 얼마나 잘 맞는지 compound 단위로 점검한다. 이 구분이 필요한 이유는 약물 후보를 최적화하는 과정 때문이다. Compound가 커지거나 cLogP가 높아지는 방향으로 바뀌면, score는 단백질 결합 부위를 잘 읽지 못해도 pKD와 상관을 보일 수 있다.

따라서 이 글은 prediction score와 pKD의 상관이 분자량과 cLogP 같은 단순 ligand property 영향을 뺀 뒤에도 유지되는지 확인한다. 공개 benchmark score와 ligand-only 비교 기준은 같은 compound 단위에서 나란히 비교한다.

{% include model-mention-cards.html label="사용한 공개 리소스" aria_label="OpenBind release와 benchmark 리소스" models="OpenBind first release|EV-A71 2A structure-affinity dataset|https://openbind.uk/news/blog-openbinds-first-release-a-structure-affinity-dataset-for-structure-based-ai/;Affinity data note|OpenBind affinity and kinetics data|https://openbind.uk/news/blog-affinity-and-kinetics-data-in-the-ev-a71-2a-openbind-release/;EV-A71 2A benchmark|OpenBind GitHub affinity files|https://github.com/OpenBind-Consortium/EV-A71_2A_benchmark/tree/main/affinity;Zenodo release|OpenBind structure-affinity data|https://zenodo.org/records/20026661" %}

## 요약

- OpenBind EV-A71 2A release에서 공개된 prediction score가 측정 pKD와 얼마나 잘 맞는지 compound 단위로 점검했다.
- 핵심 질문은 이 score-pKD 상관이 구조적 결합 신호 때문인지, 아니면 분자량과 cLogP 같은 단순 ligand property trend에 기대는지다.
- 공개 benchmark score는 측정 pKD와는 어느 정도 맞았지만, MW+cLogP 영향을 뺀 뒤에는 상관이 크게 약해졌다. MW+cLogP 제거 후 공개 score 중 가장 높은 Spearman은 `0.097`이었다.
- 반면 구조를 쓰지 않고 같은 EV-A71 2A 데이터로 학습한 ECFP ridge 비교 기준은 MW+cLogP 영향을 뺀 뒤에도 더 높은 상관을 보였다. MW+cLogP 제거 후 Spearman은 `0.430`이었다.
- 단순한 protein-ligand 접촉 수를 더해도 결과는 개선되지 않았다. 따라서 이 글의 결론은 prediction score와 pKD의 상관을 구조 기반 affinity 신호로 바로 해석하기 어렵다는 것이다.

## 평가 설정

이 글의 비교 단위는 compound다. OpenBind repository에는 affinity 측정값, compound 정보, method별 prediction score, score를 비교 표로 정리하는 규칙이 공개되어 있다 <a class="citation-ref" href="#ref-openbind-github" aria-label="Reference 3">[3]</a>. OpenBind affinity 원자료에는 같은 compound에 대한 측정값이 여러 행으로 들어갈 수 있고, 공개 자료의 분석 포함 표시를 통해 그중 최종 benchmark에 사용된 행을 구분할 수 있다 <a class="citation-ref" href="#ref-openbind-affinity-note" aria-label="Reference 2">[2]</a>.

이 글은 원자료의 측정값을 다시 해석하거나, 여러 측정 행을 pKD 하나로 다시 합치지 않는다. 대신 공개 benchmark에서 이미 정리된 compound 단위 표에 맞춘다. 같은 compound와 method 조합에 대해 공개 prediction score와 compound 단위 pKD를 나란히 두고 비교한다.

비교는 두 단계로 나눈다. 먼저 prediction score가 측정 pKD 순위와 얼마나 비슷한지 본다. 그다음 pKD에서 분자량과 cLogP로 설명되는 부분을 뺀 뒤에도 그 상관이 유지되는지 본다. 이 비교는 구조 기반 방법의 최종 평가가 아니라, pKD와의 상관을 구조 기반 affinity 신호로 해석해도 되는지 먼저 가르는 기본 점검이다.

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
          <td>공개 benchmark methods</td>
          <td class="align-right"><code>7</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> 원자료에서 최종 비교 표로 정리되는 과정을 요약했다. 실제 분석은 공개 benchmark score와 pKD를 같은 compound 단위로 맞춘 <code>494</code> compounds와 <code>7</code> methods에서 진행했다.</figcaption>
</figure>

## 결과

### 단순 ligand property 기준선

측정 pKD에서는 molecular weight, 즉 분자량 하나만으로도 Spearman `0.484`가 나왔다. MW+cLogP 선형 모델은 pKD 변동의 약 30%를 설명했다 (`R2 = 0.299`). Affinity benchmark에서는 이런 단순 ligand property 기준선을 먼저 확인해야 한다. 여기서는 그 효과가 OpenBind EV-A71 2A release 안에서 어느 정도인지 확인한다.

Figure 2는 molecular weight와 pKD의 관계를 나타낸다.

<figure class="media-figure">
  <img src="/assets/images/posts/openbind-affinity-baseline-audit/pkd-vs-mw.svg" alt="OpenBind EV-A71 2A compound-level table에서 molecular weight와 pKD의 양의 관계를 보여주는 산점도">
  <figcaption><strong>Figure 2.</strong> Molecular weight와 pKD의 관계다. 분자량만 봤을 때의 Spearman은 <code>0.484</code>였고, 선은 설명용 선형 trend다. 이 관계는 측정 pKD와의 상관을 해석할 때 먼저 확인해야 하는 단순 ligand property 기준선으로 사용했다.</figcaption>
</figure>

이후 비교는 pKD에서 분자량과 cLogP로 설명되는 부분을 제거한 값에서 진행했다. 이 값은 실제 약물화학 과정에서 제거해야 할 모든 신호를 뜻하지 않는다. Compound가 커지거나 지용성이 바뀌는 흐름 자체도 potency 변화와 함께 움직일 수 있다. 따라서 여기서 만든 값은 “진짜 affinity 신호”의 정답이 아니라, prediction score와 pKD의 상관이 큰 property trend에 얼마나 의존하는지 보기 위한 비교 대상이다.

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

### MW+cLogP 영향을 뺀 뒤의 상관

먼저 pKD에서 분자량과 cLogP로 설명되는 부분을 뺐다. 그런 다음 이렇게 조정한 pKD 순위와 각 method score 순위가 얼마나 비슷한지 다시 봤다.

그 결과 OpenBind에 공개된 benchmark score 중 가장 높은 값은 Boltz-2의 Spearman `0.097`이었다. 반면 구조를 쓰지 않고 compound 정보만 본 ECFP ridge 비교 기준은 `0.430`을 보였다.

즉 공개 score는 측정 pKD와는 어느 정도 같이 움직였지만, 분자량과 cLogP trend를 빼고 나면 조정된 pKD 순위를 잘 따라가지 못했다. 같은 데이터 안에서는 구조를 쓰지 않은 ligand-only 비교 기준이 오히려 이 순위를 더 잘 따라갔다.

MW+cLogP 영향을 뺀 뒤에도 상관이 유지되어야, 측정 pKD와의 상관을 단순 ligand property trend를 넘어선 신호로 조심스럽게 해석할 수 있다. 이 상관이 곧 “구조 정보를 잘 읽었다”는 직접 증거는 아니지만, 최소한 그런 해석을 검토할 출발점은 된다.

OpenBind 공개 benchmark score와 ECFP ridge 비교 기준은 역할이 다르다. 공개 benchmark score는 외부에서 제공된 method 점수이고, ECFP ridge는 구조 정보를 쓰지 않은 채 같은 EV-A71 2A pKD 데이터로 학습한 ligand-only 기준이다.

ECFP ridge를 함께 둔 이유는 단순하다. 구조 정보를 보지 않아도 같은 데이터 안에서 ligand 정보만으로 어느 정도 pKD 순위를 따라갈 수 있는지 확인하기 위해서다. 공개 score가 측정 pKD와는 맞아 보이지만 MW+cLogP 영향을 뺀 뒤에는 이 기준선보다 약하다면, 그 상관을 구조 정보에서 온 affinity 신호로 바로 읽기는 어렵다.

Table 3은 이 역할 구분을 유지한 채 MW+cLogP 영향을 뺀 뒤의 Spearman만 압축해 보여준다.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>score 출처</th>
          <th>가장 높은 method</th>
          <th>구조 정보 사용</th>
          <th class="align-right">MW+cLogP 제거 후<br><span class="table-note-inline">Spearman</span></th>
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
  <figcaption><strong>Table 3.</strong> MW+cLogP 영향을 뺀 뒤의 주 비교다. 구조 정보 사용 여부를 함께 표시해 공개 benchmark score와 ligand-only 기준선의 역할을 구분했다. 가장 높은 공개 benchmark Spearman에서 가장 높은 ligand-only 비교 기준 Spearman을 빼면, 반올림 전 값 기준 <code>-0.334</code>였다.</figcaption>
</figure>

Figure 1은 같은 결과를 측정 pKD와의 Spearman, 그리고 MW+cLogP 영향을 뺀 뒤의 Spearman으로 나눠 나타낸다. Gnina crystal은 공개 benchmark methods 중 측정 pKD와의 Spearman이 가장 높았지만, MW+cLogP 영향을 뺀 뒤에는 약해졌다. 반대로 ECFP/RDKit 계열 ligand-only 비교 기준은 측정 pKD뿐 아니라 MW+cLogP 영향을 뺀 뒤에도 더 높은 상관을 보였다.

같은 EV-A71 2A 데이터 안에서는 ligand-only 비교 기준도 비슷한 compound들 사이의 potency 차이를 어느 정도 잡을 수 있다. 이 기준과 함께 보면, prediction score와 pKD의 상관만으로 공개 benchmark score가 구조 정보를 잘 읽었다고 강하게 주장하기 어렵다.

### 유사 compound 기준의 보조 확인

앞의 비교가 특정 compound 구성에만 의존하는지 확인하기 위해 데이터를 여러 번 다시 뽑아 불확실성을 추정했다. MW+cLogP 영향을 뺀 뒤에도 공개 benchmark score의 상관이 항상 0 근처에만 있지는 않았다. 다만 가장 높은 Boltz-2도 Spearman 평균은 `0.096`, 95% 범위는 `[0.008, 0.179]`였다. ECFP ridge 비교 기준은 평균 `0.429`, 95% 범위 `[0.354, 0.497]`로 더 높았다.

Table 4는 MW+cLogP 영향을 뺀 뒤 Spearman의 불확실성 범위를 method별로 정리한다.

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>method</th>
          <th>구조 정보 사용</th>
          <th class="align-right">MW+cLogP 제거 후<br><span class="table-note-inline">Spearman 평균</span></th>
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
  <figcaption><strong>Table 4.</strong> MW+cLogP 영향을 뺀 뒤 Spearman을 반복 계산으로 확인한 범위다. 구조/pose를 사용하는 공개 benchmark score와 구조를 쓰지 않는 ligand-only 기준선을 같은 표에서 구분했다. 공개 benchmark score 중 가장 높은 상관은 약하게 양수였지만, 이 비교에서는 ligand-only 비교 기준과 같은 범위로 올라오지는 않았다.</figcaption>
</figure>

비슷한 compound가 많이 섞여 있으면, 같은 화학 계열 안의 쉬운 차이가 결과를 크게 좌우할 수 있다. 이를 완전히 제거하려면 화학 골격을 엄격히 나눠 평가해야 하지만, 여기서는 보조 확인으로만 다뤘다. 유사한 compound를 같은 묶음에 넣고 다시 계산했을 때도 공개 benchmark score 중 가장 높은 Spearman 평균은 `0.098`, ligand-only 비교 기준 중 가장 높은 Spearman 평균은 `0.421`이었다. 두 값의 차이는 `-0.323`으로 유지됐다.

> **Murcko scaffold**는 compound의 중심 골격을 기준으로 비슷한 compound를 묶는 방식이다.
>
> **Butina Tanimoto 0.6**은 fingerprint similarity가 높은 compound를 cluster로 묶는 방식이다. 이 글에서는 비슷한 compound 때문에 결론이 쉽게 뒤집히는지 보는 보조 확인으로 사용한다.

Figure 3은 이 보조 확인의 결과를 보여준다. Table 5는 이 확인이 얼마나 강한지 판단하기 위해 묶음 구성을 따로 보여준다.

<figure class="media-figure">
  <img src="/assets/images/posts/openbind-affinity-baseline-audit/butina-grouped-residual-spearman.svg" alt="Butina Tanimoto 0.6 cluster로 유사 compound를 묶은 뒤 method별 MW+cLogP 제거 후 Spearman 평균과 95% 범위를 비교한 막대 차트">
  <figcaption><strong>Figure 3.</strong> Butina Tanimoto 0.6 cluster로 유사 compound를 같은 묶음에 넣은 뒤, MW+cLogP 영향을 뺀 Spearman을 다시 계산했다. 이 결과는 화학 골격을 엄격히 분리한 평가가 아니라 보조 확인으로 해석한다. Figure 1과 같은 세 묶음으로 배치했고, 막대는 반복 계산 평균, 얇은 선은 95% 범위다.</figcaption>
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
  <figcaption><strong>Table 5.</strong> 유사 compound 기준의 보조 확인이 얼마나 강한지 보여주는 묶음 구성이다. compound 1개짜리 묶음 비율이 높으므로, 이 확인은 화학 골격을 엄격히 분리한 평가가 아니다. 다만 유사 compound를 일부 묶어도 Figure 1과 Table 3의 결론이 쉽게 뒤집히지 않는지 보는 보조 확인으로 사용했다.</figcaption>
</figure>

### 단순 protein-ligand 접촉 수 보조 확인

> **Protein-ligand 접촉 수**는 공개 구조에서 protein atom과 ligand atom이 가까이 놓인 횟수를 세어 만든 단순 구조 요약값이다. 정교한 구조 모델이 아니라, 결합 자세 주변의 접촉량을 거칠게 요약한 값으로 사용한다.

MW+cLogP 영향을 뺀 뒤 공개 benchmark score가 약해졌다고 해서, 구조 정보가 전혀 쓸모없다고 말할 수는 없다. 그래서 공개 구조에서 protein-ligand 접촉 수를 세고, 이 단순한 구조 요약을 ligand-only 기준에 더해 봤다.

구체적으로는 구조가 있는 925개 항목에서 이 접촉 수를 세고, 이를 494 compounds 단위로 모았다.

결과는 개선되지 않았다. 접촉 수만 사용한 모델은 MW+cLogP 제거 후 Spearman `0.156`이었고, ECFP에 접촉 수를 더한 모델은 `0.279`였다. 이는 ECFP만 사용한 모델의 `0.360`보다 낮다.

Table 6은 단순 protein-ligand 접촉 수를 더했을 때의 MW+cLogP 제거 후 Spearman을 요약한다.

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>입력 정보</th>
          <th class="align-right">MW+cLogP 제거 후<br><span class="table-note-inline">Spearman</span></th>
        </tr>
      </thead>
      <tbody>
        <tr><td>ECFP만 사용</td><td class="align-right"><code>0.360</code></td></tr>
        <tr><td>접촉 수만 사용</td><td class="align-right"><code>0.156</code></td></tr>
        <tr><td>ECFP + 접촉 수</td><td class="align-right"><code>0.279</code></td></tr>
        <tr><td>RDKit descriptors + ECFP</td><td class="align-right"><code>0.369</code></td></tr>
        <tr><td>RDKit descriptors + ECFP<br><span class="table-note-inline">+ 접촉 수</span></td><td class="align-right"><code>0.283</code></td></tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 6.</strong> 공개 구조에서 세어 만든 단순 protein-ligand 접촉 수 보조 확인이다. ECFP에 접촉 수를 더했을 때의 차이는 <code>-0.081</code>였고, 반복 계산의 95% 범위는 <code>[-0.146, -0.012]</code>였다. 이 결과는 단순 접촉 수만으로는 앞의 결론이 뒤집히지 않는다는 뜻으로 해석한다.</figcaption>
</figure>

## 해석

핵심은 prediction score와 pKD의 상관을 affinity 예측 성공으로 바로 읽기 어렵다는 점이다. Score와 pKD의 순위가 비슷해 보여도, 그 상관이 단백질-리간드 구조에서 온 신호인지 단순 ligand property trend에서 온 신호인지는 따로 확인해야 한다.

OpenBind 공개 benchmark score는 측정 pKD와는 어느 정도 같이 움직였다. 하지만 pKD에서 분자량과 cLogP로 설명되는 부분을 빼고 나면 그 상관은 크게 약해졌다. 처음에 보였던 상관의 상당 부분이 compound의 크기나 지용성 같은 ligand property trend와 겹쳤을 가능성이 있다.

구조 정보를 쓰지 않은 ligand-only 비교 기준은 MW+cLogP 영향을 뺀 뒤에도 더 강한 상관을 보였다. 이 기준은 공개 benchmark score를 대체하려는 모델이 아니라, 같은 데이터 안에서 ligand 정보만으로 어느 정도 pKD 순서를 따라갈 수 있는지 보기 위한 기준선이다. 공개 score가 이 기준선보다 약하다면, 공개 score의 pKD 상관을 구조 기반 affinity 신호로 강하게 해석하기 어렵다.

이 결론은 OpenBind 전체나 구조 기반 affinity prediction 일반에 대한 판정이 아니다. 이 release의 공개 prediction score를 해석할 때, 측정 pKD와의 상관만 보지 말고 분자량과 cLogP 같은 단순 property 기준선과 함께 봐야 한다는 점을 확인한 것이다.

## 한계

- 이 결과는 이미 공개된 EV-A71 2A compound 표를 다시 확인한 결과에 한정된다. OpenBind 전체나 구조 기반 affinity prediction 일반을 판정하지 않는다.
- 새 compound를 미리 분리해 놓고 발견 성능을 평가한 설정이 아니며, 새 affinity model의 일반화 성능도 평가하지 않는다.
- MW/cLogP 영향 자체가 뜻밖의 발견이라는 주장은 아니다. 이 글의 초점은 공개 release 안에서 그 크기를 수치화하고, prediction score와 pKD의 상관을 해석할 때 필요한 기준선을 확인하는 데 있다.
- ECFP ridge 비교 기준은 공개 benchmark score를 대체하려는 모델이 아니다. 구조 정보를 쓰지 않고 같은 EV-A71 2A pKD 데이터로 학습한 ligand-only 비교 기준이다.
- MW+cLogP로 설명되는 부분을 빼는 절차는 진단용이다. 약물화학 최적화 과정에서는 property trend와 compound 최적화 흐름 자체도 실제 potency 변화와 얽힐 수 있으므로, 이렇게 조정한 값을 구조 정보의 정답으로 해석하지 않는다.
- 유사 compound 기준의 보조 확인은 결론을 뒤집지 않았지만, Murcko 기준에서는 `82.2%`, Butina 기준에서는 `71.4%`의 묶음에 compound가 하나만 들어 있었다. 따라서 새로운 화학 골격(scaffold)을 엄격히 분리한 평가 설정은 아니다.
- pKD 값이 정리되는 과정에 대한 민감도는 아직 확인하지 않았다. 예를 들어 여러 측정 행을 하나로 모으는 규칙, 측정값의 불확실성, benchmark 포함 행 선택이 MW+cLogP 제거 후 결론에 미치는 영향은 별도로 확인해야 한다.
- 단순 protein-ligand 접촉 수 보조 확인은 접촉 수 하나만 평가했다. 구조 정보가 무의미하다는 결론이 아니며, 더 정교한 구조 정보나 pKD에 맞춘 구조 모델을 배제하지 않는다.

## Appendix

본문에는 해석에 필요한 주요 수치만 두었다. Appendix Table 1은 전체 method의 측정 pKD Spearman과 MW+cLogP 제거 후 Spearman을 함께 보기 위한 보조 자료다. 이 표도 method 순위를 확정하기보다 두 상관의 차이를 점검하는 용도로 둔다.

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>method</th>
          <th class="align-right">측정 pKD<br><span class="table-note-inline">Spearman</span></th>
          <th class="align-right">MW+cLogP 제거 후<br><span class="table-note-inline">Spearman</span></th>
          <th class="align-right">ligand-only 대비 차이</th>
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
  <figcaption><strong>Appendix Table 1.</strong> Method별 측정 pKD Spearman과 MW+cLogP 제거 후 Spearman이다. Ligand-only 대비 차이는 ECFP ridge 비교 기준의 MW+cLogP 제거 후 Spearman 반올림 전 값을 기준으로 계산했으며, 직접 순위표가 아니라 제거 전후 차이를 보는 보조 표로 사용한다.</figcaption>
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
  <li id="ref-openbind-github">OpenBind Consortium. <strong>EV-A71_2A_benchmark affinity files</strong>. GitHub, 2026. <a href="https://github.com/OpenBind-Consortium/EV-A71_2A_benchmark/tree/main/affinity">Repository directory</a></li>
  <li id="ref-openbind-zenodo">OpenBind Consortium. <strong>OpenBind Structure-Affinity Data Release: Enterovirus A71 (EV-A71) / Coxsackievirus A16 (CVA16) 2A protease</strong>. Zenodo, version v1, May 5, 2026. DOI: <a href="https://doi.org/10.5281/zenodo.20026661">10.5281/zenodo.20026661</a></li>
</ol>

본문의 비교 단위와 전체 method 결과는 Table 1과 Appendix Table 1에 요약했다.

</div>

## Citation

Text citation:

```text
Ilho Ahn, "OpenBind prediction score를 구조 신호로 읽을 수 있을까", Mini Research, May 10, 2026.
```

BibTeX:

```bibtex
@misc{ahn2026openbind_affinity_baseline_check,
  author = {Ahn, Ilho},
  title = {OpenBind prediction score를 구조 신호로 읽을 수 있을까},
  year = {2026},
  month = {May},
  howpublished = {Mini Research},
  url = {https://muted-color.github.io/research/2026/05/10/openbind-affinity-baseline-audit/}
}
```
