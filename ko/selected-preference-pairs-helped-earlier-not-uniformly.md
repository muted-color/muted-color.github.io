---
layout: post
title: "Alignment Data Map: 선별된 선호 쌍의 SimPO 경계 통과 시점과 모델별 차이"
date: 2026-09-01 17:00:00 +0900
last_modified_at: 2026-09-03 21:57:40 +0900
lang: ko
categories: ["LLM ALIGNMENT"]
tags: [llm, alignment, preference-data, data-selection, adm, simpo, qwen]
lab_host: "dgx1"
lab_path: "projects/adm-toolcall"
excerpt: "ADM으로 선택한 preference pair가 SimPO boundary를 통과하는 시점과 그 양상이 Qwen2.5-Instruct 모델별로 어떻게 달라지는지 추적한다."
description: "Qwen2.5-Instruct 1.5B·3B·7B에서 ADM HighAvg pair와 Random pair의 SimPO 경계 통과 시점, 그리고 모델과 checkpoint에 따른 차이를 살펴본 후속 연구 노트."
permalink: /research/2026/09/01/selected-preference-pairs-helped-earlier-not-uniformly/ko/
translation_url: /research/2026/09/01/selected-preference-pairs-helped-earlier-not-uniformly/
image: /assets/images/posts/selected-preference-pairs-helped-earlier-not-uniformly/social-thumbnail.png
image_alt: "흰 배경 위 세 줄의 반투명 선호 쌍 캡슐이 두 개의 유리 경계를 서로 다른 시점에 통과하는 장면"
hero_image: /assets/images/posts/selected-preference-pairs-helped-earlier-not-uniformly/hero-original.png
hero_alt: "세 줄의 반투명 선호 쌍 캡슐이 두 개의 유리 경계를 서로 다른 위치에서 통과하는 장면"
hero_frame: true
hero_compact: true
math: true
published: true
publication_status: "published"
---

Lee et al.의 Alignment Data Map(ADM) <a class="citation-ref" href="#ref-adm" aria-label="Reference 1">[1]</a>은 한 지시문의 후보 응답에서 계산한 alignment score의 평균과 분산으로 학습 데이터를 구분한다. 핵심은 모든 preference data가 같은 학습 가치를 갖는다고 보지 않고, 후보 응답의 **평균 품질과 응답 간 분산**으로 선택 구간을 찾는 것이다. 원 연구는 평균 점수가 높고 분산이 낮은 HighAvg 표본 33%만으로도 전체 데이터와 비슷하거나 더 높은 alignment 성능을 얻을 수 있다고 보고했다.

그러나 ADM이 어떤 데이터 영역을 선택하는지와, 선택된 데이터가 학습 대상 모델에서 실제로 어떤 학습 신호가 되는지는 별개의 문제다. 이 후속 분석은 ADM으로 선택한 지시문이 실제 preference pair로 바뀐 뒤, Qwen2.5-Instruct 1.5B·3B·7B가 **학습 전에 각 응답 쌍을 얼마나 구분하고 있었는지**와 학습 시점에 따라 어떤 변화가 나타나는지를 추적한다.

{% include related-research-note.html label="이전 연구 노트" aria_label="이 글에 앞선 Alignment Data Map 연구 노트" title="Alignment Data Map: 측정값에서 선호 학습 쌍까지" description="ADM의 선택 기준과 preference pair 구성 과정을 정리한 앞선 분석" image="/assets/images/posts/adm-measurement-to-preference-pairs/hero-adm-map-highavg.png" url="/research/2026/08/23/adm-measurement-to-preference-pairs/ko/" %}

## 요약

- HighAvg와 Random 조건에서 Qwen2.5-Instruct 1.5B·3B·7B를 각각 별도로 학습했다. 모든 모델은 학습 데이터와 겹치지 않는 600쌍의 공통 평가 데이터에서 비교했다.
- 세 모델 크기 모두에서 **학습 전보다 높은 `R/U/T` state로 끝난 pair 비율은 HighAvg가 Random보다 높았다.** 그러나 이점은 모델 크기에 따라 일정하게 커지지 않았다. 7B에서 가장 컸지만, 3B의 최종 차이는 1.5B보다 작았다.
- 이 차이는 모든 pair의 작은 개선에서 나온 것이 아니었다. HighAvg에서는 Random보다 boundary를 넘어 더 높은 state로 이동한 pair가 많고, 같은 state 안에서 margin만 증가한 pair는 적었으며, 일부 regression도 더 관찰됐다.
- 가장 분명한 차이는 **같은 학습량 안에서 boundary를 넘는 upward passage가 HighAvg에서 더 이른 checkpoint에 관찰됐다는 점**이다. 후반에는 Random이 일부 pair에서 따라오며 최종 격차가 줄었다.

## 문제 설정

ADM은 측정된 응답 집합의 특성을 나타내고 학습할 지시문을 선택한다. 실제 preference optimization의 단위는 지시문 선택 뒤에 구성되는 prompt와 chosen–rejected 응답 쌍이다. 지시문을 선택할 때 사용한 reference scorer와 학습 대상 모델이 같은 응답 쌍을 똑같이 어렵다고 볼 이유는 없다.

이 구분을 바탕으로 다음 질문을 검토했다.

> 높은 품질·낮은 분산 영역에서 선택된 preference pair도, 학습 대상 모델이 학습 전에 chosen–rejected 응답을 얼마나 구분하고 있었는지에 따라 서로 다른 학습 신호가 되는가?

검토한 가설은 모델 규모가 커질수록 HighAvg의 효과도 단조 증가할 수 있다는 것이었다. 선택된 pair가 미묘하지만 유용한 차이를 담고 있다면 더 큰 모델이 이를 더 효과적으로 학습할 수 있다고 예상했다.

## 관련 연구

### 선택 기준의 차이

Preference pair의 가치는 먼저 **데이터 자체에서 측정한 특성**으로 구분할 수 있다. ADM은 후보 응답의 alignment score 평균과 분산으로 지시문을 나눈다 <a class="citation-ref" href="#ref-adm" aria-label="Reference 1">[1]</a>. Xiao et al.은 on-policy reward distribution에서 chosen과 rejected의 위치를 비교했고 <a class="citation-ref" href="#ref-sweet-spot" aria-label="Reference 2">[2]</a>, Deng et al.은 external reward margin과 implicit DPO margin을 결합해 학습 데이터를 선택했다 <a class="citation-ref" href="#ref-preference-selection" aria-label="Reference 3">[3]</a>.

다른 축은 **현재 policy에서 측정한 학습 상태**다. Yang et al.은 policy와 reference policy가 만드는 implicit DPO reward margin이 작은 pair를 우선 annotation했고 <a class="citation-ref" href="#ref-pair-efficiency" aria-label="Reference 4">[4]</a>, Huang et al.은 현재 policy의 implicit margin과 목표 explicit margin 사이의 간격을 alignment potential로 정의했다 <a class="citation-ref" href="#ref-alignment-potential" aria-label="Reference 5">[5]</a>. 따라서 `score gap`이나 `difficulty`는 하나의 공통 난이도 지표가 아니다. Reference separation, policy-relative margin, target까지의 거리는 서로 다른 신호다.

### 시간에 따라 변하는 가치

학습이 진행되면 같은 pair의 가치도 달라질 수 있다. Peng et al.의 Uni-DPO는 pair의 intrinsic quality와 학습 중 변하는 model performance를 함께 사용해 가중치를 조정한다 <a class="citation-ref" href="#ref-uni-dpo" aria-label="Reference 6">[6]</a>. Li et al.의 MetaPO는 reward-margin evolution, learning volatility, reference deviation으로 시간 의존적 sample weight를 학습한다 <a class="citation-ref" href="#ref-temporal-weighting" aria-label="Reference 7">[7]</a>. 별도의 분석에서는 input complexity와 output ambiguity가 서로 다른 학습 동역학과 연결된다고 보고했다 <a class="citation-ref" href="#ref-learning-order" aria-label="Reference 8">[8]</a>. 이 연구들의 공통점은 유용한 pair가 현재 policy와 학습 시점에 따라 달라질 수 있다는 점이다.

### 이 글의 분석 범위

이 글은 고정된 ADM selection으로 학습한 조건을 학습 데이터와 분리된 공통 평가 데이터에서 비교하고, policy state transition과 제한된 update budget 안에서 더 높은 state가 관측되는 시점을 추적한다. 분석 대상은 데이터의 정적 품질만이 아니라 선택된 pair가 현재 policy에서 보이는 학습 궤적이다. 새로운 selection rule이나 weighting method를 제안하지는 않는다.

## 실험 설계

### 데이터 선택과 학습 비교

이 글에서 **HighAvg**는 고정된 reference answer 집합과 scorer로 만든 ADM의 높은 평균·낮은 분산 영역에서 선택한 지시문으로 구성한 preference pair, **Random**은 같은 원천 pool에서 무작위로 선택한 지시문으로 구성한 preference pair를 뜻한다.

두 조건은 같은 원천 pool에서 source와 task 구성을 유지해 만들고, 동일한 LoRA·SimPO recipe로 학습했다. 학습 대상 모델은 official Qwen2.5-Instruct [1.5B](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct), [3B](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct), [7B](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)이며, 각 모델 크기마다 서로 다른 seed로 세 번씩 실행했다. 데이터 수가 아니라 학습량을 맞추기 위해 두 조건 모두 약 3 epoch에 해당하는 276 optimizer update로 고정했다.

학습 데이터와 prompt·pair가 겹치지 않는 600쌍을 **공통 평가 데이터**로 정하고, base policy와 step 92·184·276 checkpoint에서 반복 평가했다. 같은 pair를 유지했기 때문에 endpoint aggregate뿐 아니라 각 pair가 학습 중 어느 상태로 이동했는지도 추적할 수 있다. 이 데이터는 새 blind test가 아니라 후속 분석에서도 고정해 사용한 development 자료다.

### SimPO margin과 state trajectory

이 글에서는 Qwen2.5-Instruct의 모델 변형과 크기를 말할 때는 **학습 대상 모델**, 특정 checkpoint에서 응답 확률을 정하는 $\pi_t$를 **policy**로 구분한다.

하나의 pair를 $z=(x,y_w,y_l)$라고 할 때 policy의 length-normalized log-probability margin을 다음과 같이 정의한다.

$$
\Delta_{\pi}(z)
=
\frac{\log \pi(y_w\mid x)}{|y_w|}
-
\frac{\log \pi(y_l\mid x)}{|y_l|}.
$$

Meng et al.의 SimPO <a class="citation-ref" href="#ref-simpo" aria-label="Reference 9">[9]</a>는 $\beta\Delta_{\pi}$가 target margin $\gamma$를 넘도록 학습한다. 이번 설정은 $\beta=2$, $\gamma=1$이므로 target boundary는 $\Delta=0.5$다. 이에 따라 각 pair를 세 state로 구분했다.

$$
R:\Delta\le 0,
\qquad
U:0<\Delta<0.5,
\qquad
T:\Delta\ge0.5.
$$

- **R — preference reversed:** policy가 rejected 응답을 더 선호한다.
- **U — correct, below target:** chosen 응답의 순위는 높지만 separation이 SimPO target보다 작다.
- **T — target satisfied:** chosen–rejected separation이 target에 도달했다.

Figure 1은 두 objective boundary가 세 state를 어떻게 나누는지 보여 준다. 오른쪽으로 이동하는 `R→U`, `R→T`, `U→T`를 upward transition으로 집계했다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/selected-preference-pairs-helped-earlier-not-uniformly/figure1_simpo_margin_states.svg" alt="하나의 가로 policy-margin bar를 0과 0.5에서 나눠 preference reversed, correct but below target, target satisfied의 세 SimPO state로 표시한 도식.">
  <figcaption><strong>Figure 1.</strong> Policy margin의 부호와 SimPO target boundary로 정의한 <code>R/U/T</code> state 공간. 오른쪽은 policy margin이 커지는 방향이며, 양끝 화살표는 <code>R</code>과 <code>T</code>가 열린 구간임을 나타낸다. 구간 폭은 수치 범위나 pair 비율을 뜻하지 않는다.</figcaption>
</figure>

이 state 구분에서 policy가 rejected 응답을 크게 선호하는 pair는 제한된 update 안에 다음 boundary를 넘기 어려울 수 있다. 이미 chosen 응답을 target margin 이상으로 선호하는 pair는 `R/U/T` 상태 기준으로 더 올라갈 단계가 없다. 그 사이에서는 다음 preference 또는 target-margin boundary가 도달 가능한 거리에 있어 같은 pair가 upward state transition을 만들 수 있다.

**첫 upward passage 관측 시점**은 학습 전보다 높은 state가 처음 확인된 평가 checkpoint를 뜻한다. **State-standardized upward movement**는 특정 checkpoint의 state가 base보다 높은 pair 비율에서 HighAvg-minus-Random 차이를 계산하고, base state별 차이를 공통 `R/U/T` 분포로 가중 평균한 값이다.

모델 크기 비교는 세 official Qwen2.5-Instruct 변형인 1.5B·3B·7B에서 관측한 결과다. 이 모델 변형들은 parameter count 외의 학습 조건과 post-training 결과도 함께 다르므로, parameter 수만 바꾼 통제 실험은 아니다.

## 결과

### 모델 크기별·학습 시점별 효과

Step 276에서 HighAvg는 세 모델 크기의 세 seed 모두에서 Random보다 reward accuracy, policy margin, final upward movement, target reach가 높았고 SimPO loss는 낮았다.

그러나 효과 크기는 예상한 단조 순서를 만들지 않았다. 초기 state 구성을 공통 분포로 표준화한 HighAvg-minus-Random 최종 upward-movement 차이는 1.5B `+5.64%p`, 3B `+4.27%p`, 7B `+8.06%p`였다.

Figure 2에서 checkpoint별 변화를 함께 보면, step 276에서 3B의 효과가 1.5B보다 작았던 순서는 전체 학습 구간에 걸쳐 유지되지 않았다. 3B와 7B의 HighAvg-minus-Random 평균 차이는 step 184에서 가장 컸다가 최종 checkpoint에서 다소 줄었다. 3B의 세 seed에서도 이 차이는 `92→184` 구간에 커지고 `184→276` 구간에 줄었다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/selected-preference-pairs-helped-earlier-not-uniformly/figure2_scale_and_checkpoint_timing.svg" alt="Qwen2.5-Instruct 1.5B는 회색 원과 실선, 3B는 파란색 사각형과 파선, 7B는 검정색 다이아몬드와 점선으로 표시한 optimizer step 92, 184, 276의 state-standardized HighAvg-minus-Random upward movement 차이. 가는 선은 seed별 궤적이고 굵은 선은 평균이다.">
  <figcaption><strong>Figure 2.</strong> 모델 크기와 평가 checkpoint별 HighAvg-minus-Random state-standardized upward movement. 1.5B는 회색 원, 3B는 파란색 사각형, 7B는 검정색 다이아몬드로 구분했다. 가는 선은 seed별 궤적, 굵은 선은 평균이다. 평균 최종 차이는 3B에서 가장 작고 7B에서 가장 컸으며, 3B와 7B의 평균 차이는 모두 step 184에서 최대였다.</figcaption>
</figure>

HighAvg의 효과는 모델 크기가 커질수록 일정하게 증가하지 않았고, 같은 모델에서도 평가 checkpoint에 따라 달라졌다. 따라서 모델 크기뿐 아니라 각 pair의 초기 `R/U/T` 상태와 다음 boundary까지의 거리도 함께 고려해야 한다.

### Endpoint accuracy와 transition 구성

Reward accuracy는 $\Delta>0$인지 여부만 본다. 따라서 reversed preference의 교정, target margin 돌파, state가 바뀌지 않은 margin 변화, 두 boundary를 가로지르는 regression이 하나의 endpoint 값 안에 섞인다.

동일 pair의 학습 궤적을 세부 분해하면, HighAvg가 모든 pair에서 조금씩 더 큰 margin 증가를 만든 것은 아니었다. 세 모델 모두에서 학습 내내 같은 state에 머문 pair가 줄었고, downward transition 없이 더 높은 state로 끝나거나 step 276까지 target state에 도달한 pair가 늘었다. 변화 폭은 대체로 1.5B와 7B에서 크고 3B에서 작았다.

Figure 3과 같이 이동이 모두 위쪽이었던 것은 아니다. 학습 중 한 번이라도 downward transition을 경험한 pair의 비율도 HighAvg가 Random보다 세 모델 모두에서 약 `2%p` 높았다. HighAvg에서는 더 많은 pair의 state가 바뀌었고, 그 안에는 일부 regression도 포함됐다.

공통 평가 데이터를 pair 단위로 보면, HighAvg와 Random의 차이는 같은 state 안에서 margin이 조금 증가한 경우보다 boundary를 넘어 더 높은 state로 이동한 경우에 더 뚜렷했다. 모든 모델에서 이 이동이 HighAvg에서만 관찰된 pair가 Random에서만 관찰된 pair보다 많았다. 반면 state가 유지된 채 $\Delta$만 증가한 pair는 HighAvg에서 오히려 적었다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/selected-preference-pairs-helped-earlier-not-uniformly/figure3_transition_redistribution.svg" alt="No-state-change, upward progress, target reach, downward transition에서 HighAvg-minus-Random 차이를 1.5B, 3B, 7B별로 비교한 발산형 막대그래프.">
  <figcaption><strong>Figure 3.</strong> HighAvg-minus-Random transition 구성. Random과 비교하면 HighAvg에서는 같은 state에 머문 pair가 적고, downward move 없이 upward progress를 보이거나 target에 도달한 pair가 많았으며, downward movement를 보인 pair도 소폭 많았다. Whisker는 pair-cluster bootstrap 95% 구간이다. Target-reach 비율은 base부터 <code>T</code>였던 pair를 제외한다.</figcaption>
</figure>

### Reference score와 다음 boundary까지의 거리

모델 크기에 따른 차이를 설명하는 한 가설은 HighAvg로 선택된 지시문에서 만든 pair의 chosen과 rejected 응답이 서로 구분하기 어려워 미묘한 학습 신호를 만든다는 것이다. Reference scorer가 chosen과 rejected에 부여한 절대 점수 차이는 이 응답 구분의 모호성을 나타내는 보조 지표다. 점수 차이가 클수록 reference scorer에서는 두 응답의 구분이 선명하다.

Base state가 `R` 또는 `U`인 각 pair에서 **Random의 첫 upward passage 빈도**는 세 Random 실행 중 step 276까지 upward passage가 관찰된 실행의 비율로 정의했다. Figure 4에서 이 빈도와 reference score gap 사이의 Spearman 상관은 `ρ=.070–.124`로 작았다. 지시문 단위 ADM mean, variance, score range도 276-update 범위의 passage와 거의 상관이 없었다.

학습 전 policy에서 다음 objective boundary까지의 거리는 더 강한 연관을 보였고, 상관은 `ρ=−.469`에서 `−.443` 사이였다. 다음 boundary가 멀수록 276 update 안에 upward passage가 발생할 가능성이 낮았다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/selected-preference-pairs-helped-earlier-not-uniformly/figure4_reference_gap_vs_policy_headroom.svg" alt="하나의 공통 Spearman 상관 축에서 세 seed의 Random 첫 upward passage 빈도와 reference score gap·초기 policy의 next-boundary distance 사이의 상관을 1.5B, 3B, 7B별 점과 95% 구간으로 비교한 그림.">
  <figcaption><strong>Figure 4.</strong> Random의 첫 upward passage 빈도와 reference score gap·학습 전 policy의 next-boundary distance 사이의 Spearman 상관. 오른쪽 숫자는 정확한 Spearman <span aria-label="rho">ρ</span> 값이며, whisker는 pair-cluster bootstrap 95% 구간이다. Reference score gap의 상관은 <code>+.070–+.124</code>로 작았고, next-boundary distance는 <code>−.469–−.443</code>으로 일관된 음의 상관을 보였다.</figcaption>
</figure>

두 측정은 서로 다른 질문에 답한다. ADM은 고정된 reference measurement로 데이터 영역을 정의하고 지시문을 선택한다. 학습 전 policy에서 다음 boundary까지의 거리는 선택된 pair가 다음 state와 얼마나 떨어져 있는지를 나타낸다. 이번 결과에서 pair의 관측 궤적은 데이터 특성뿐 아니라 학습 시작 시 policy가 해당 pair를 얼마나 구분하고 있었는지, 그리고 어느 update 구간에서 변화를 측정했는지에 따라서도 달라졌다.

### Upward passage의 시점 차이

Base state가 `R` 또는 `U`인 pair에서 base보다 높은 state가 처음 관측된 checkpoint를 비교했다. 비교값은 학습 전 state와 각 state 내 다음 boundary 거리 사분위의 공통 분포로 직접 표준화했다. 그 결과 HighAvg-minus-Random cumulative upward passage 차이는 step 92부터 양수였고, 대체로 step 184에서 가장 컸다(Table 1).

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>모델</th>
          <th class="align-right">Step 92</th>
          <th class="align-right">Step 184</th>
          <th class="align-right">Step 276</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>1.5B</td>
          <td class="align-right">+6.44%p</td>
          <td class="align-right">+9.28%p</td>
          <td class="align-right">+8.79%p</td>
        </tr>
        <tr>
          <td>3B</td>
          <td class="align-right">+2.79%p</td>
          <td class="align-right">+7.64%p</td>
          <td class="align-right">+5.78%p</td>
        </tr>
        <tr>
          <td>7B</td>
          <td class="align-right">+2.26%p</td>
          <td class="align-right">+15.11%p</td>
          <td class="align-right">+13.88%p</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> 8개 base-state × boundary-distance-quartile 층으로 직접 표준화한 HighAvg-minus-Random cumulative upward passage 차이. 양수는 HighAvg에서 cumulative upward passage가 더 많았음을 뜻한다. 9개 pair-cluster bootstrap 95% 구간은 모두 0보다 컸다.</figcaption>
</figure>

Step 184 이후 격차는 줄었지만, 주된 변화는 HighAvg가 먼저 넘은 boundary를 Random이 뒤늦게 통과한 것이었다. 3B에서 base가 `U`이고, step 184에 HighAvg는 `T`에 도달했지만 Random은 `U`에 머문 pair×seed trajectory는 63개였다. Step 276에는 이 가운데 61개가 HighAvg에서 `T`를 유지했고, Random은 35개에서 `T`에 도달했다. 최종 격차가 줄어든 것은 HighAvg가 넓게 후퇴했기보다 Random의 후반 추격이 컸기 때문이다. Figure 5는 이 누적 passage와 다음 boundary까지의 거리 구간별 차이를 함께 보여 준다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/selected-preference-pairs-helped-earlier-not-uniformly/figure5_budget_conditioned_upward_passage.svg" alt="1.5B, 3B, 7B의 HighAvg와 Random cumulative upward passage 곡선과 initial next-boundary distance 사분위별 checkpoint-grid advantage heatmap.">
  <figcaption><strong>Figure 5.</strong> 위쪽은 8개 base-state × boundary-distance-quartile 층으로 표준화한 cumulative upward passage다. 아래쪽은 사분위별 차이를 92-step 평가 간격으로 요약한다. 값이 클수록 시간에 따라 누적된 HighAvg 우위가 컸음을 뜻하며, 실제로 절약한 optimizer update 수는 아니다. Q1이 boundary에 가장 가깝고 Q4가 가장 멀며, Q4는 모든 모델에서 가장 약했다.</figcaption>
</figure>

효과가 가장 큰 곳은 boundary에서 가장 먼 pair가 아니었다. HighAvg의 차이는 학습 전 policy가 관측 범위 안에서 다음 state에 도달할 수 있는 거리 구간에 집중됐다. 7B policy는 1.5B·3B policy보다 효과가 나타난 거리 구간이 넓었지만, 이 세 모델 변형만으로 모델 크기에 따른 단조 증가를 결론 내릴 수는 없었다.

여기서 **이르다**는 upward passage가 동일한 276-update 관측 범위의 더 앞선 평가 checkpoint에서 확인됐다는 뜻이다. 평가 checkpoint가 step 92·184·276에만 있으므로 각 pair가 정확히 몇 번째 optimizer step에서 boundary를 넘었는지는 알 수 없다.

### 학습 메트릭의 보조 근거

Epoch 1부터 3까지 training accuracy와 training reward margin의 변화량은 세 모델 모두 HighAvg가 Random보다 컸다. SimPO loss 변화도 1.5B와 7B에서는 HighAvg가 더 낮아지는 방향이었고, 3B에서는 두 조건의 차이가 거의 없었다. 정확한 모델별 값과 분석 범위는 Appendix Table 1에 정리했다.

최종 upward-movement 차이가 가장 작았던 3B에서도 training metric 차이는 관찰됐다. 다만 이 값은 서로 다른 학습 데이터에서 측정한 학습 배치 지표다. 공통 평가 데이터에서 관찰한 궤적을 대신하지 않으며, 세 모델 크기에서 HighAvg와 Random 사이에 최적화 관련 차이가 있었음을 보여 주는 보조 근거로만 사용했다.

## 결론

모델 크기만을 기준으로 한 가설은 다음과 같았다.

$$
\text{larger parameter scale}
\quad\Rightarrow\quad
\text{larger HighAvg advantage}.
$$

관측 결과는 다음 연결에 더 가까웠다.

$$
\text{initial policy state}
\rightarrow
\text{distance to the next boundary}
\rightarrow
\text{transition reachable within the budget}
\rightarrow
\text{observed training effect}.
$$

모델 역량이 영향을 줄 가능성은 남아 있다. 다만 세 모델 변형은 초기 `R/U/T` 구성과 다음 boundary까지의 거리에서도 달랐고, 이 차이가 관찰된 모델별 양상을 더 직접적으로 설명했다. 이 해석은 HighAvg 효과가 세 모델에서 모두 양수이면서 3B보다 1.5B에서 크고, 다시 7B에서 가장 큰 비단조 결과와 시점별 변화에 부합한다. 또한 효과가 학습 중간에 커졌다가 Random의 후반 추격으로 줄어든 관찰과도 부합한다.

고정된 ADM data map은 데이터가 어느 측정 영역에서 선택됐는지를 알려 준다. 각 checkpoint의 policy margin은 그 pair가 현재 어떤 objective boundary 통과에 가까운지를 보여 준다. 두 정보를 동일 pair의 학습 궤적으로 연결했을 때 이번 비교의 중심 결과는 다음과 같았다.

> **HighAvg는 이 고정 비교에서 일관된 집계상 우위를 보였지만, 모든 pair에서 더 큰 개선을 만들거나 모델 크기에 따라 단조 증가한 것은 아니었다. 가장 분명한 차이는 policy 기준 SimPO boundary를 더 일찍 넘긴 upward passage였다.**

선택된 preference data의 실제 학습 효과를 이해하려면 데이터 영역뿐 아니라 policy가 각 pair에서 출발한 위치와 그 transition을 관측한 update 범위를 함께 봐야 했다.

## 한계

- 공통 평가 데이터는 후속 분석에서도 고정해 사용한 development 자료이므로, 같은 transition pattern이 새로운 외부 평가 데이터에서도 유지되는지는 확인하지 않았다.
- 세 official Qwen2.5-Instruct 모델 변형은 parameter count 외의 학습 조건과 post-training 결과도 함께 다르므로, 관측 차이를 순수한 모델 크기 효과로 해석할 수 없다.
- Upward passage는 step 92·184·276에서만 관찰했으므로, 각 pair가 정확히 어느 optimizer step에서 boundary를 넘었는지는 알 수 없다.

## Appendix

### 평가 및 재현 조건

- **원천 및 ADM 측정:** 앞선 연구 노트와 같은 [UltraFeedback](https://huggingface.co/datasets/openbmb/UltraFeedback) 4,500개 지시문과 지시문당 후보 응답 4개를 사용했다. Reference answer는 [Qwen3.5-122B-A10B](https://huggingface.co/Qwen/Qwen3.5-122B-A10B)로 생성했다. [all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2)의 중첩 창 평균 유사도로 후보 응답을 측정하고, source×task 안에서 ADM 영역을 정했다.
- **학습 데이터:** HighAvg와 Random은 각각 1,080개 지시문으로 구성했으며, 유효 preference pair는 5,682쌍과 5,773쌍이다. Chosen–rejected 방향은 원천 데이터의 fine-grained score로 고정했다.
- **학습:** SimPO objective와 learning rate `5e-6`, linear scheduler, warmup ratio `0.1`을 사용했다. LoRA 설정은 rank `64`, alpha `128`, dropout `0.05`이며 cutoff length는 `2048`, precision은 BF16이다.
- **노출량:** Global batch size `63`으로 276 optimizer update를 수행하고 step 92·184·276 checkpoint를 저장했다. 두 조건의 명목상 학습 pair 노출량은 모두 17,388이며 약 3 epoch에 해당한다. 결과에 따른 checkpoint 선택은 하지 않고 step 276을 endpoint로 고정했다.
- **평가:** 학습 데이터와 겹치지 않는 공통 평가 데이터 600쌍을 base와 세 checkpoint에 반복 사용했다. 이 데이터는 blind test가 아니라 고정된 development 자료다.
- **분석:** 주요 endpoint와 upward-passage 비교, reference–boundary-distance 상관 분석은 seed 42·43·44를 사용했다. Figure 3의 세부 transition 분해와 Appendix의 training-metric table은 seed 42를 사용했다. 불확실성 구간은 동일 pair의 반복 관측을 함께 유지한 채 pair ID를 재표집하는 pair-cluster bootstrap으로 계산했다.

### 학습 메트릭 세부값

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Epoch 1→3 변화량의<br><span class="table-note-inline">HighAvg-minus-Random 차이</span></th>
          <th class="align-right">1.5B</th>
          <th class="align-right">3B</th>
          <th class="align-right">7B</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Training accuracy</td>
          <td class="align-right">+4.06%p</td>
          <td class="align-right">+2.50%p</td>
          <td class="align-right">+4.20%p</td>
        </tr>
        <tr>
          <td>Training reward margin<br><span class="table-note-inline">$\beta\Delta$</span></td>
          <td class="align-right">+0.124</td>
          <td class="align-right">+0.130</td>
          <td class="align-right">+0.417</td>
        </tr>
        <tr>
          <td>SimPO loss</td>
          <td class="align-right">−0.0343</td>
          <td class="align-right">+0.0039</td>
          <td class="align-right">−0.0333</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 1.</strong> Seed 42에서 epoch 1부터 3까지 training metric 변화량의 HighAvg-minus-Random 차이. Training accuracy와 reward margin은 양수, SimPO loss는 음수일 때 HighAvg에 유리한 방향이다. 이 값은 서로 다른 학습 데이터에서 측정한 in-distribution 보조 지표이며, 공통 평가 데이터의 trajectory를 대신하지 않는다.</figcaption>
</figure>

### 주요 지표

- **Policy margin $\Delta$:** policy의 length-normalized chosen–rejected log-probability 차이.
- **Reward accuracy:** $\Delta>0$인 pair, 즉 policy가 chosen 응답을 rejected 응답보다 선호한 pair의 비율.
- **Training reward margin:** SimPO 학습 로그에 기록된 $\beta\Delta$의 평균.
- **State-standardized upward movement:** checkpoint state가 base보다 높은 pair 비율의 HighAvg-minus-Random 차이를 base state별로 계산한 뒤, 공통 `R/U/T` 분포로 가중 평균한 값.
- **첫 upward passage 관측 시점:** base가 `R` 또는 `U`인 pair가 처음으로 더 높은 state에 도달한 평가 checkpoint.
- **다음 boundary까지의 거리:** base margin에서 다음 SimPO boundary까지의 거리. `R`에서는 $0-\Delta$, `U`에서는 $0.5-\Delta$다.
- **Base state × boundary-distance-quartile 표준화:** upward passage가 가능한 pair를 두 base state와 각 state 내 네 거리 사분위의 8개 층으로 나누고, 조건 간 차이를 공통 층 분포로 직접 가중한 절차.
- **평가 간격 환산값:** step 92·184·276의 cumulative passage indicator를 92-step 평가 간격의 면적으로 요약한 서술 통계. 실제 boundary 통과 step이나 절약한 update 수를 뜻하지 않는다.
- **Pair-cluster bootstrap:** 각 분석에서 동일 pair의 반복 관측을 함께 유지한 채 pair ID를 재표집한 불확실성 계산.

## References

<div class="reference-list" markdown="1">

<ol>
  <li id="ref-adm">Lee, S., Kim, E., Lee, H., and Chang, B. <strong>Alignment Data Map for Efficient Preference Data Selection and Diagnosis</strong>. <em>Findings of ACL 2026</em>, 38225–38241, 2026. <a href="https://aclanthology.org/2026.findings-acl.1906/">ACL Anthology</a>; <a href="https://arxiv.org/abs/2505.23114">arXiv</a></li>
  <li id="ref-sweet-spot">Xiao, Y. et al. <strong>Finding the Sweet Spot: Preference Data Construction for Scaling Preference Optimization</strong>. <em>ACL 2025</em>, 12538–12552, 2025. <a href="https://aclanthology.org/2025.acl-long.615/">ACL Anthology</a></li>
  <li id="ref-preference-selection">Deng, X. et al. <strong>Less is More: Improving LLM Alignment via Preference Data Selection</strong>. <em>NeurIPS 2025</em>, 161259–161285, 2025. DOI: <a href="https://doi.org/10.52202/085713-5383">10.52202/085713-5383</a>; <a href="https://proceedings.neurips.cc/paper_files/paper/2025/hash/ebf95a6f3c575322da15d4fd0fc2b3c8-Abstract-Conference.html">NeurIPS</a></li>
  <li id="ref-pair-efficiency">Yang, S. et al. <strong>Not All Preference Pairs Are Created Equal: A Recipe for Annotation-Efficient Iterative Preference Learning</strong>. <em>Findings of EMNLP 2024</em>, 6549–6561, 2024. <a href="https://aclanthology.org/2024.findings-emnlp.382/">ACL Anthology</a></li>
  <li id="ref-alignment-potential">Huang, K. et al. <strong>Larger or Smaller Reward Margins to Select Preferences for LLM Alignment?</strong> <em>ICML 2025</em>, 25922–25946, 2025. <a href="https://proceedings.mlr.press/v267/huang25al.html">PMLR</a></li>
  <li id="ref-uni-dpo">Peng, S. et al. <strong>Uni-DPO: A Unified Paradigm for Dynamic Preference Optimization of LLMs</strong>. <em>ICLR 2026</em>, 2026. <a href="https://openreview.net/forum?id=G7DBGlgjjp">OpenReview</a></li>
  <li id="ref-temporal-weighting">Li, M., Zhou, X., and Zhao, P. <strong>Learning Temporally-Aware Sample Weights for Preference Optimization</strong>. <em>Findings of ACL 2026</em>, 12361–12377, 2026. <a href="https://aclanthology.org/2026.findings-acl.601/">ACL Anthology</a></li>
  <li id="ref-learning-order">Li, M., Wang, J., and Zhao, P. <strong>What Do LLMs Learn First? Asymmetric Learning Dynamics of Input Complexity and Output Ambiguity in Preference Alignment</strong>. <em>ACL 2026</em>, 17373–17388, 2026. <a href="https://aclanthology.org/2026.acl-long.789/">ACL Anthology</a></li>
  <li id="ref-simpo">Meng, Y., Xia, M., and Chen, D. <strong>SimPO: Simple Preference Optimization with a Reference-Free Reward</strong>. <em>NeurIPS 2024</em>, 124198–124235, 2024. <a href="https://proceedings.neurips.cc/paper_files/paper/2024/hash/e099c1c9699814af0be873a175361713-Abstract-Conference.html">NeurIPS</a></li>
</ol>

**모델 및 데이터셋 리소스:** [Qwen3.5-122B-A10B](https://huggingface.co/Qwen/Qwen3.5-122B-A10B), [all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2), [UltraFeedback](https://huggingface.co/datasets/openbmb/UltraFeedback), [Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct), [Qwen2.5-3B-Instruct](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct), [Qwen2.5-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct).

</div>

## Citation

Text citation:

```text
Ilho Ahn, "Alignment Data Map: 선별된 선호 쌍의 SimPO 경계 통과 시점과 모델별 차이", Mini Research, September 1, 2026.
```

BibTeX:

```bibtex
@article{ahn2026selectedpreferencepairsearlier,
  author = {Ilho Ahn},
  title = {Alignment Data Map: 선별된 선호 쌍의 SimPO 경계 통과 시점과 모델별 차이},
  journal = {Mini Research},
  year = {2026},
  month = sep,
  url = {https://muted-color.github.io/research/2026/09/01/selected-preference-pairs-helped-earlier-not-uniformly/ko/}
}
```
