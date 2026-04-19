---
title: "TrpB low-label 후보 reranking: 전역 prior 실패와 radius4 안의 작은 보정 신호"
date: 2026-04-19 10:50:00 +0900
categories: ["PROTEIN ML"]
tags: [protein, trpb, flip2, esm2, diffusion, fitness-prediction, low-label, reranking]
lab_path: "experiment-lab/projects/trpb-local-fitness-diffusion"
excerpt: "FLIP2 TrpB two-to-many에서 local denoising prior를 low-label ESM2/Ridge oracle에 섞어 봤다. 전역 보상 신호로는 실패했지만, radius4로 후보 공간을 통제하면 작은 랭킹 보정 신호가 남았다."
permalink: /research/2026/04/19/trpb-local-fitness-diffusion-prior-reranking/
image: /assets/images/posts/trpb-local-fitness-diffusion/trpb-5e0k-ribbon-featured.png
hero_image: /assets/images/posts/trpb-local-fitness-diffusion/trpb-5e0k-ribbon-featured.png
hero_alt: "PDB 5E0K tryptophan synthase complex에서 TrpB beta chain을 파란색 ribbon으로 강조한 구조 렌더링 이미지"
hero_caption: "<strong>Figure 1.</strong> PDB 5E0K의 <em>Pyrococcus furiosus</em> tryptophan synthase complex 구조를 ribbon으로 렌더링했다. 파란색으로 강조한 부분은 complex 전체 중 TrpB에 해당하는 beta chain B이다."
math: true
mermaid: false
---

단백질 엔지니어링에서 fitness label은 보통 넉넉하지 않다. 변이를 만들고 assay를 돌리는 비용이 있으니, 실제로는 수십 개에서 수백 개 label만 보고 다음 후보를 골라야 하는 경우가 많다. 그래서 low-label oracle 하나만 믿고 후보를 고르면, 예측기가 과신하는 이상한 후보를 집는 문제가 생길 수 있다.

> **Oracle**: 여기서는 실제 실험을 대신하는 완벽한 답안지가 아니다.
> 이 글에서는 적은 fitness label로 학습한 `frozen ESM2 embedding + Ridge regression` 예측기를 oracle이라고 부른다. 즉 후보 서열을 넣으면 fitness를 추정해 주는 기준 점수 모델이다.

이 실험은 그 지점에서 시작했다.

<aside class="research-question" aria-label="실험 질문">
  <p class="research-question__label">Experiment Focus</p>
  <p>low-label setting에서 frozen ESM2/Ridge fitness oracle이 과신하는 후보를 local denoising prior가 눌러 주고, TrpB fitness 상위 mutant 후보 ranking을 더 좋게 만들 수 있는지 확인한다.</p>
</aside>

짧게 말하면, 기대했던 그림은 단순했다. prior가 low-label oracle의 과신을 눌러 주고, fitness 상위 후보를 더 잘 올려 주길 바랐다. 하지만 답은 깔끔한 성공이 아니었다. **전역 후보 풀에서 prior를 보상 신호처럼 더하는 방식은 실패했다.** 오히려 prior가 싫어하는 후보를 올리는 negative lambda가 좋아 보였는데, 그 신호를 쪼개 보니 대부분은 mutation radius 교란 효과였다. 그래도 완전히 빈손은 아니었다. 후보 공간을 radius4로 고정하면 학습된 prior `+0.25`가 oracle 랭킹을 작게 보정했다. 다만 이 신호도 강한 후보 발굴 방법이나 실제 후보 필터로 쓰기에는 부족했다.

{% include model-mention-cards.html label="사용한 주요 리소스" aria_label="사용한 주요 모델과 벤치마크 리소스" models="FLIP2 TrpB|protein.properties/FLIP2|https://flip.protein.properties/;ESM2-35M|facebook/esm2_t12_35M_UR50D|https://huggingface.co/facebook/esm2_t12_35M_UR50D;Guided protein generation paper|OpenReview Ice2BHIumz|https://openreview.net/forum?id=Ice2BHIumz" %}

## 요약

- 먼저 TrpB `two-to-many`에서 frozen ESM2/Ridge oracle에 local prior를 더해 fitness 상위 후보 ranking이 좋아지는지 봤다.
- 하지만 전역 후보 풀에서는 prior를 보상 신호처럼 쓰는 가설이 실패했다.
- 그래서 좋아 보였던 negative lambda 이득을 따라가 보니, 대부분은 mutation radius 효과였고 prior 성공으로 보기 어려웠다.
- 그 뒤 radius4 안으로 문제를 좁히자 학습된 prior `+0.25`가 `Hit@64`를 작게 올렸다: `+0.012`.
- 결국 남은 것은 약한 랭킹 보정 신호다. 생성 성공도 아니고, validation만으로 고른 위험 필터로도 이어지지 않았다.

## 실험 범위

이 글의 실험은 새 TrpB 서열을 자유롭게 생성해서 실험실에서 확인한 실험이 아니다. 이미 FLIP2 test 후보 라이브러리 안에 있는 후보들을 점수로 다시 정렬하고, 그 정렬이 실제 fitness 상위 후보를 더 잘 잡는지 본다. 따라서 이 글에서 말할 수 있는 것은 `생성 성공`이 아니라 `이미 측정된 라이브러리 안에서의 재랭킹`이다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>항목</th>
          <th>설정</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>데이터셋</td>
          <td>FLIP2 TrpB <code>two-to-many</code></td>
        </tr>
        <tr>
          <td>과제</td>
          <td>0/1/2-mutation train에서 higher-order test 후보 ranking</td>
        </tr>
        <tr>
          <td>전체 변이</td>
          <td><code>228,298</code></td>
        </tr>
        <tr>
          <td>test 후보</td>
          <td><code>217,507</code></td>
        </tr>
        <tr>
          <td>radius4 후보</td>
          <td><code>129,518</code></td>
        </tr>
        <tr>
          <td>label budget</td>
          <td><code>64 / 128 / 256</code></td>
        </tr>
        <tr>
          <td>주요 지표</td>
          <td><code>Hit@64</code>: 상위 64개로 고른 후보 중 실측 fitness 상위 5% 후보 비율</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> 실험 범위 요약이다. 이 글의 평가는 이미 fitness label이 있는 FLIP2 TrpB test 후보 라이브러리 안에서 후보를 다시 정렬하는 문제이며, 이 범위를 넘어 자유 생성 성능으로 읽으면 안 된다.</figcaption>
</figure>

<details>
  <summary>TrpB 소개: tryptophan synthase beta subunit</summary>
  <div class="details-content">
    <p><strong>TrpB</strong>는 tryptophan synthase complex의 beta subunit이다. 생화학적으로는 indole과 L-serine을 결합해 L-tryptophan을 만드는 beta reaction에 관여하는 효소 subunit으로 볼 수 있다 <a class="citation-ref" href="#ref-trpb-review" aria-label="Reference 1">[1]</a>.</p>
    <p>이 글에서는 TrpB의 구조나 반응 메커니즘 자체를 예측하지 않는다. FLIP2 TrpB <code>two-to-many</code> split에서 이미 측정된 variant fitness를 이용해, 적은 label로 학습한 sequence-only 점수 모델이 higher-order mutant 후보를 얼마나 잘 다시 정렬하는지 본다 <a class="citation-ref" href="#ref-flip2" aria-label="Reference 3">[3]</a>.</p>
    <ul>
      <li><strong>생물학적 맥락:</strong> tryptophan synthase complex에서 L-tryptophan 생성 반응을 맡는 beta subunit.</li>
      <li><strong>벤치마크 역할:</strong> 0/1/2-mutation label에서 higher-order mutant 후보로 넘어가는 ranking 과제.</li>
      <li><strong>주장 범위:</strong> 이 글은 TrpB enzyme design이나 실험실 검증이 아니라 이미 측정된 라이브러리 안에서의 재랭킹만 다룬다.</li>
    </ul>
  </div>
</details>

기본 점수와 정답 기준은 아래처럼 읽는다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table comparison-table--score-terms">
      <colgroup>
        <col style="width: 42%;">
        <col style="width: 58%;">
      </colgroup>
      <thead>
        <tr>
          <th>용어</th>
          <th>읽는 법</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>target(x)</code> / fitness 상위 후보</td>
          <td>FLIP2가 이미 제공하는 실측 fitness label이다. 이 글에서 fitness 상위 후보는 test 후보 중 <code>target</code> 상위 5%에 들어가는 서열을 뜻한다.</td>
        </tr>
        <tr>
          <td><code>oracle_pred(x)</code></td>
          <td>적은 train/validation label만 보고 학습한 frozen ESM2/Ridge의 fitness 예측값이다. 실제 측정값이 아니라 후보 ranking에 쓰는 모델 점수다.</td>
        </tr>
        <tr>
          <td><code>prior_score(x)</code></td>
          <td>fitness label을 보지 않고 후보 서열이 변이 위치별 아미노산 패턴과 얼마나 잘 맞는지 점수화한 값이다. 첫 empirical local prior는 각 변이 위치에서 자주 관찰된 아미노산 조합에 더 높은 로그확률을 준다.</td>
        </tr>
        <tr>
          <td><code>z(oracle_pred) + lambda*z(prior_score)</code></td>
          <td>후보 풀 안에서 두 점수를 표준화한 뒤 prior 보정을 섞은 최종 랭킹 점수다.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> 이 실험에서 비교한 점수와 정답 기준이다. <code>target</code>은 평가용 실측 label이고, <code>oracle_pred</code>와 <code>prior_score</code>는 후보를 정렬하기 위한 모델 점수다. <code>lambda &gt; 0</code>은 prior가 좋아하는 후보를 올리고, <code>lambda &lt; 0</code>은 prior가 싫어하는 후보를 올리는 진단 조건으로 해석했다.</figcaption>
</figure>

처음 기대는 단순했다. low-label oracle은 흔들릴 수 있으니, local prior를 더하면 너무 이상한 후보를 누르고 fitness 상위 후보를 더 안정적으로 고를 수 있을 것이라고 봤다. 하지만 TrpB에서는 이 기대가 그대로 맞지 않았다.

## 실험의 흐름

이 실험은 전역 보상 신호 가설에서 시작해, 실패 원인을 분해하고, 더 좁은 후보 공간에서 남는 신호를 확인하는 순서로 진행했다. 마지막에는 그 신호가 실제 선택 방식으로 이어질 수 있는지 따로 점검했다.

## Phase 1: Prior는 전역 보상 신호가 아니었다

첫 번째 확인은 가장 직접적인 positive prior 보정 실험이었다. 전역 TrpB test 후보 풀에서 `oracle_pred`에 local prior를 positive 보상 신호로 더하면, oracle 단독 ranking보다 FLIP2 `target` 기준 상위 5% 후보를 더 잘 끌어올릴 수 있는지 봤다.

먼저 학습된 prior가 아니라 empirical local prior를 썼다.

> **Empirical local prior**: fitness label로 학습한 모델이 아니다.
> 변이가 관찰된 local position별 amino acid 빈도를 세어, 자주 보인 조합에 더 높은 log-prob를 주는 경험적 점수다.

기대는 단순했다. low-label oracle이 과신하는 이상한 후보를 prior가 눌러 주고, 관찰된 변이 패턴과 더 잘 맞는 후보를 위로 올려 주는 것이다. 하지만 결과는 그 방향이 아니었다.

<figure class="media-figure">
  <img src="/assets/images/posts/trpb-local-fitness-diffusion/table3-empirical-prior-delta.svg" alt="empirical local prior를 더했을 때 label budget 64 128 256 모두에서 Hit@64 delta가 0 아래로 내려가는 horizontal bar plot">
  <figcaption><strong>Figure 2.</strong> empirical local prior를 oracle score에 더했을 때의 <code>Hit@64</code> 변화량이다. 세 label budget 모두에서 delta가 0보다 작았고, 이 설정에서는 prior 보정이 oracle 단독보다 낮은 ranking을 만들었다.</figcaption>
</figure>

정확한 원 수치는 아래 표에 정리했다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>label budget</th>
          <th>oracle 단독</th>
          <th>oracle + empirical local prior</th>
          <th>Hit@64 변화</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>64</td>
          <td>0.203</td>
          <td>0.167</td>
          <td>-0.036</td>
        </tr>
        <tr>
          <td>128</td>
          <td>0.188</td>
          <td>0.031</td>
          <td>-0.156</td>
        </tr>
        <tr>
          <td>256</td>
          <td>0.865</td>
          <td>0.672</td>
          <td>-0.193</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> Figure 2의 delta를 원 수치로 풀어 본 비교다. 64 label에서는 하락폭이 작았지만, 128/256 label에서는 더 크게 낮아졌다. 이 결과만 놓고 보면 empirical local prior를 전역 positive 보상 신호로 더하는 전략은 뒷받침되지 않았다.</figcaption>
</figure>

**핵심은 세 label budget 모두에서 방향이 같았다는 점이다.** Figure 2처럼 `64 / 128 / 256` 모두 delta가 0 아래에 있다. 이 비교만 놓고 보면 prior를 positive 보상 신호로 계속 더하는 전략은 정당화하기 어렵다.

다만 이 결과를 곧바로 "prior는 쓸모없다"로 읽으면 과하다. 첫 비교는 empirical local prior였고, 학습된 denoising prior가 더 나은 신호를 줄 가능성은 아직 남아 있었다.

그래서 학습된 prior로 같은 질문을 다시 봤다. 결과는 더 공격적인 보정이 아니라 **보정을 끄는 쪽**이었다. validation이 선택한 lambda는 `0.0`이었고, 이는 validation 기준에서 학습된 prior를 oracle score에 더할 이유가 없었다는 뜻이다.

따라서 이 단계의 결론은 prior 전체의 실패가 아니다. 더 좁게는, **TrpB 전역 후보 풀에서 local prior를 fitness 상위 보상 신호로 바로 더하는 방식이 맞지 않았다**는 것이다.

## Phase 2: negative lambda 개선의 착시

positive prior 보정이 실패한 뒤, 숫자만 보면 유혹적인 결과가 하나 나왔다. prior가 좋아하는 후보를 올리는 대신, prior가 싫어하는 후보를 올리는 negative lambda가 low-label 조건에서 크게 좋아 보였다.

> **Negative lambda**: oracle score에 prior score를 더해 보상하는 대신, prior score가 낮은 후보가 위로 올라오게 만드는 설정이다.
> 즉 "prior가 좋아하는 후보"를 올리는 실험이 아니라, 반대로 "prior가 덜 그럴듯하다고 본 후보"를 올렸을 때 ranking이 어떻게 바뀌는지 보는 진단이다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>label budget</th>
          <th>oracle 단독</th>
          <th>negative prior 보정</th>
          <th>Hit@64 변화</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>64</td>
          <td>0.203</td>
          <td>0.542</td>
          <td class="is-better">+0.339</td>
        </tr>
        <tr>
          <td>128</td>
          <td>0.188</td>
          <td>0.604</td>
          <td class="is-better">+0.417</td>
        </tr>
        <tr>
          <td>256</td>
          <td>0.865</td>
          <td>0.859</td>
          <td>-0.005</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> negative lambda를 적용했을 때의 <code>Hit@64</code> 변화다. 64/128 label에서는 큰 개선처럼 보이지만, 이 숫자는 방법의 성공으로 바로 해석하지 않았다. 이후 분석의 출발점은 "왜 prior를 반대로 썼을 때 좋아 보였는가"였다.</figcaption>
</figure>

하지만 **이 결과는 성공 사례가 아니라, 왜 이런 일이 생겼는지 분해해야 하는 신호에 가까웠다.**

먼저 학습된 prior score와 measured fitness의 관계를 확인했다. 전역 후보 풀에서는 prior score가 높은 후보가 실제 fitness도 높다는 보장이 없었고, 오히려 반대로 움직이는 구간이 보였다.

다음으로 mutation radius를 맞춘 비교를 했다. **negative lambda가 좋아 보인 후보들은 단순히 prior를 뒤집어서 찾은 고품질 후보라기보다, ranking이 mutation radius 4 후보 쪽으로 이동한 효과를 크게 포함하고 있었다.**

이 결과를 성공으로 읽기 전에, 가능한 해석을 한 번 분리해 볼 필요가 있었다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>좋아 보인 해석</th>
          <th>더 그럴듯한 설명</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>negative lambda가 fitness 상위 후보를 직접 찾았다.</td>
          <td>랭킹이 mutation radius 4 후보 쪽으로 이동한 효과가 컸다.</td>
        </tr>
        <tr>
          <td>prior를 뒤집으면 좋은 보상 신호가 된다.</td>
          <td>전역 후보 풀에서 prior score와 실측 fitness가 반대로 움직였다.</td>
        </tr>
        <tr>
          <td>diffusion prior가 생성에서도 성공했다.</td>
          <td>이 실험은 이미 측정된 라이브러리 안에서의 재랭킹이며 생성 성공 증거는 아직 없다.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 5.</strong> negative lambda 결과를 다시 읽는 표다. 이 단계의 핵심은 큰 숫자를 성공으로 홍보하는 것이 아니라, 그 숫자가 어떤 radius 효과를 포함하는지 분리하는 것이다.</figcaption>
</figure>

그래서 이 단계의 결론은 **"negative lambda가 좋은 prior 사용법이다"가 아니었다.** 더 좁게는, 전역 후보 풀에서 prior score와 mutation radius가 얽혀 있었고, 그 얽힘이 큰 개선처럼 보이는 숫자를 만들었다는 것이다. 다음 질문은 자연스럽게 더 좁아졌다.

> radius를 고정한 뒤에도 prior가 oracle 랭킹을 조금이라도 보정하는지 확인한다.

## Phase 3: radius4 안에서는 작은 신호가 남았다

Phase 2의 문제는 prior score와 mutation radius가 전역 후보 풀에서 얽혀 있다는 점이었다. 그래서 다음 비교에서는 후보 공간을 radius4로 고정해, prior가 radius 이동이 아니라 같은 후보 공간 안에서 ranking을 보정하는지 봤다.

기준선은 `radius4_oracle`이었다. 이는 후보를 mutation radius 4 안으로 제한한 뒤, 고정된 ESM2/Ridge oracle 점수만으로 ranking하는 방식이다. 이 기준선에 미리 정한 작은 positive prior weight, `+0.25`,를 더한 조건을 비교했다.

메인으로 볼 결과는 30개 seed로 확인한 비교다. label budget `64 / 128 / 256`을 함께 보므로 `30 seed × 3 label budget = 90`개 budget-seed 조합의 평균이다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>조건</th>
          <th>Hit@64</th>
          <th>MeanTrue@64</th>
          <th>Spearman</th>
          <th>NDCG@64</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>radius4 oracle</td>
          <td>0.602</td>
          <td>0.281</td>
          <td>0.078</td>
          <td>0.297</td>
        </tr>
        <tr>
          <td>radius4 oracle + 학습된 prior +0.25</td>
          <td class="is-better">0.614</td>
          <td class="is-better">0.308</td>
          <td class="is-better">0.092</td>
          <td class="is-better">0.310</td>
        </tr>
        <tr>
          <td>변화</td>
          <td>+0.012</td>
          <td>+0.026</td>
          <td>+0.014</td>
          <td>+0.014</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 6.</strong> radius4 후보 안에서 30개 seed로 확인한 평균 결과다. 핵심 지표인 <code>Hit@64</code>는 학습된 prior +0.25를 더했을 때 <code>+0.012</code> 올랐고, <code>MeanTrue@64</code>, <code>Spearman</code>, <code>NDCG@64</code>도 같은 방향으로 움직였다. 다만 효과 크기는 작아서 강한 후보 발굴 방법으로 읽기에는 부족하다.</figcaption>
</figure>

**핵심은 prior가 크게 이긴 것이 아니라, radius4 안에서는 작은 positive signal이 사라지지 않았다는 점이다.**

다만 이 평균값은 label budget별 차이를 가린다. 개선은 주로 64/128 label 조건에서 남았고, 256 label에서는 오히려 negative가 됐다.

<figure class="media-figure">
  <img src="/assets/images/posts/trpb-local-fitness-diffusion/radius4-prior-hit64-budget-delta.svg" alt="radius4 후보 안에서 prior 0.25를 더했을 때 label budget 64와 128은 positive delta를 보이고 256은 negative delta를 보이는 horizontal bar plot">
  <figcaption><strong>Figure 3.</strong> radius4 후보 안에서 prior +0.25를 더했을 때의 label budget별 <code>Hit@64</code> 변화다. 64/128 label에서는 작은 positive delta가 남았지만, 256 label에서는 negative로 바뀐다. 그래서 Phase 3의 신호는 “항상 좋아진다”가 아니라 “low-label 조건에서 약하게 남는다”로 읽는 편이 안전하다.</figcaption>
</figure>

정확한 원 수치는 아래 표에 정리했다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>label budget</th>
          <th>radius4 oracle</th>
          <th>+ prior 0.25</th>
          <th>Hit@64 변화</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>64</td>
          <td>0.452</td>
          <td>0.489</td>
          <td class="is-better">+0.037</td>
        </tr>
        <tr>
          <td>128</td>
          <td>0.575</td>
          <td>0.588</td>
          <td class="is-better">+0.013</td>
        </tr>
        <tr>
          <td>256</td>
          <td>0.780</td>
          <td>0.765</td>
          <td>-0.015</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 7.</strong> <code>Hit@64</code> 변화를 label budget별로 나눈 결과다. prior +0.25의 개선은 64/128 label 조건에서만 남았고, 256 label에서는 negative였다. 따라서 이 결과는 “prior가 항상 좋다”가 아니라 “low-label radius4 조건에서 약한 보정 신호가 있다”로 읽는 편이 안전하다.</figcaption>
</figure>

이 결과의 좋은 점은 방향이 완전히 사라지지 않았다는 것이다. 초기 탐색 신호는 확인 비교로 갈수록 작아졌지만, 30개 seed 평균에서도 positive로 남았다. 반대로 나쁜 점은 바로 그 작음이다. `Hit@64 +0.012`는 실전 선택 방식을 바꿀 만큼 큰 차이라고 말하기 어렵다.

그래서 이 실험의 중심 문장은 이렇게 두는 편이 맞다.

> **Phase 3의 결론**: 전역 prior 보상 신호는 실패했다.
> 하지만 radius4로 후보 공간을 고정하면, 학습된 local denoising prior는 low-label oracle ranking을 작게 보정했다.

## Phase 4: 위험 필터로 바꾸려 했지만 아직 부족했다

prior가 보상 신호가 아니라면, 다른 역할은 있을 수 있다. 예를 들어 oracle이 과신하는 후보를 알려주는 위험 신호나 보조 신호로 쓸 수 있는지 확인했다. 이어진 위험 필터 분석은 이 질문을 본다.

먼저 prior residual을 radius4 내부의 선택 실패 진단 신호로 써 봤다.

> **Prior residual**: oracle이 높게 본 정도와 prior가 그 후보를 그럴듯하게 본 정도 사이의 불일치다.
> 여기서는 oracle이 과신한 후보를 prior가 약하게 경고할 수 있는지 보는 위험 신호로 사용했다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--risk-diagnostics">
      <thead>
        <tr>
          <th>그룹</th>
          <th>지표</th>
          <th>값</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td rowspan="3">AUROC/AUPRC</td>
          <td>선택 실패 AUROC</td>
          <td>0.554</td>
        </tr>
        <tr>
          <td>선택 실패 AUPRC</td>
          <td>0.515</td>
        </tr>
        <tr>
          <td>큰 절대 오차 AUROC</td>
          <td>0.470</td>
        </tr>
        <tr>
          <td rowspan="3">Hit@64</td>
          <td>oracle 단독 Hit@64</td>
          <td>0.602</td>
        </tr>
        <tr>
          <td>고정 coverage 0.5 위험 필터 Hit@64</td>
          <td>0.619</td>
        </tr>
        <tr>
          <td>Hit@64 변화</td>
          <td class="is-better">+0.016</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 8.</strong> prior residual의 사후 위험 진단 결과다. prior residual은 선택 실패를 약하게 감지했지만, 절대 오차를 찾는 지표로는 좋지 않았다. 고정 필터의 이득은 사후 진단 성격이 강하므로 실전 OOD 탐지 성능으로 읽으면 안 된다.</figcaption>
</figure>

**Table 8의 개선은 test 결과를 본 뒤 고정한 필터에서 나온 값이므로, 그대로 실제 후보를 고르는 기준으로 쓰기는 어렵다.**

여기서 멈추면 prior residual이 곧바로 유용한 위험 필터처럼 보일 수 있다. 그래서 다음에는 test 정보를 쓰지 않고 validation만으로 coverage를 고른 뒤 test에 적용했다. 결과는 좋아지지 않았다.

> **Coverage**: 필터를 통과시켜 실제 ranking에 남기는 후보 비율이다.
> `coverage=1.0`은 사실상 필터를 쓰지 않는 선택이다.

<figure class="table-figure table-figure--metrics table-figure--compact-metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--numeric-columns metrics-table--compact-two-col">
      <thead>
        <tr>
          <th>선택 방식</th>
          <th>Hit@64</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>oracle 단독</td>
          <td>0.602</td>
        </tr>
        <tr>
          <td>validation에서 고른 위험 필터</td>
          <td>0.602</td>
        </tr>
        <tr>
          <td>변화</td>
          <td>-0.001</td>
        </tr>
        <tr>
          <td>고정 coverage 0.5 진단 필터</td>
          <td>0.619</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 9.</strong> validation만으로 coverage를 고른 뒤 test에 적용한 결과다. 사후 고정 필터는 좋아 보였지만, validation 선택기는 oracle 단독을 넘지 못했다. 따라서 prior residual을 현재 설정에서 실전 위험 필터로 주장하기는 어렵다.</figcaption>
</figure>

추가 분석에서는 왜 실패했는지를 확인했다. validation 선택기는 대부분 필터를 쓰지 않는 `coverage=1.0`을 골랐다. 특히 64-label 조건에서는 30개 seed 모두 `coverage=1.0`이었다. validation에서 좋아 보인 선택과 test에서 실제로 얻은 hit 사이의 대응도 약했다.

**Phase 4의 핵심은 prior residual에 약한 사후 진단 신호가 있었지만, validation만으로 안정적인 필터 정책을 고르기에는 부족했다는 점이다.**

## 결론 및 한계

이 실험은 성공 또는 실패 한 단어로 정리하기 어렵다. 실패한 것은 명확하다. 전역 prior 보정은 실패했고, validation에서 고른 위험 필터도 oracle 단독을 넘지 못했다. 하지만 제한적 성과도 있다. radius4로 후보 공간을 통제하면 학습된 prior가 아주 작게 랭킹을 보정했다.

**이 실험에서 주장할 수 있는 것은 “prior가 강한 보상 신호였다”가 아니라, “radius4로 후보 공간을 고정했을 때 작은 보정 신호가 남았다”는 정도다.**

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table comparison-table--claim-scope">
      <colgroup>
        <col style="width: 50%;">
        <col style="width: 50%;">
      </colgroup>
      <thead>
        <tr>
          <th>말할 수 있는 것</th>
          <th>아직 말하면 안 되는 것</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>empirical local prior의 positive 보정은 TrpB two-to-many 랭킹에서 실패했다.</td>
          <td>prior가 fitness 상위 후보를 찾는 전역 보상 신호로 성공했다.</td>
        </tr>
        <tr>
          <td>학습된 positive prior는 전역 후보 풀에서 validation 기준으로 선택되지 않았다.</td>
          <td>학습된 prior가 oracle 단독보다 실용적으로 우월하다.</td>
        </tr>
        <tr>
          <td>negative lambda 이득은 대부분 mutation radius 효과다.</td>
          <td>negative lambda가 생성 prior 성공을 의미한다.</td>
        </tr>
        <tr>
          <td>radius4 안에서는 학습된 prior +0.25가 작게 랭킹을 보정했다.</td>
          <td>diffusion model이 새 TrpB fitness 상위 서열을 생성했다.</td>
        </tr>
        <tr>
          <td>prior residual은 약한 사후 선택 실패 진단 신호다.</td>
          <td>prior residual이 신뢰할 만한 OOD detector로 검증됐다.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 10.</strong> 결론과 한계를 나눠 정리한 표다. 이 글의 핵심은 성과를 크게 보이게 만드는 것이 아니라, 실험 범위 안에서 주장 가능한 내용과 아직 주장하면 안 되는 내용을 분리하는 것이다.</figcaption>
</figure>

지금 이 결과만 보고 후보 추천 방식을 하나 고른다면 `radius4_oracle`이 가장 안전하다. `radius4 + prior +0.25`는 low-label 조건에서 작은 보정 신호가 있었으므로 비교 후보로 남길 수 있다. 반면 validation에서 고른 위험 필터는 oracle 단독을 넘지 못했으므로, 현재 결과만으로는 선택 방식에 넣지 않는 편이 맞다.

## 후속 검증 과제

이 글의 범위에서는 여기까지가 안전한 결론이다. 이미 측정된 라이브러리 안에서의 재랭킹 문제로는 주장 범위가 충분히 정리됐다. 더 나아가려면 아래 질문들은 별도 실험으로 분리해야 한다.

- `prior residual`을 불확실성 신호로 주장하려면 ensemble/dropout 기준선과 비교해야 한다.
- validation으로 coverage를 고르는 절차는 cross-fitting이나 더 큰 validation 설계로 다시 봐야 한다.
- 고정 coverage 필터는 독립 split에서 사전 등록한 방식으로 확인해야 한다.
- diffusion 기반 생성을 말하려면 라이브러리 밖 생성과 별도 oracle 또는 실험실 검증이 필요하다.

가장 안정적으로 남는 결론은 단순하다.

> diffusion prior는 이 실험에서 보상 신호가 아니었다.
> 그래도 radius4로 통제한 재랭킹 안에서는 작은 보정 신호가 남았다.
> 그 신호를 실전 위험 필터로 바꾸기에는 아직 약했다.

## References

<div class="reference-list" markdown="1">

<ol>
  <li id="ref-trpb-review">Watkins-Dulaney, E., Straathof, S., & Arnold, F. <strong>Tryptophan Synthase: Biocatalyst Extraordinaire</strong>. <em>ChemBioChem</em>, 2021.<br>
    <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC7935429/">PMC full text</a>
  </li>
  <li id="ref-trpb-structure">Buller, A. R. et al. <strong>Directed evolution of the tryptophan synthase beta-subunit for stand-alone function recapitulates allosteric activation</strong>. <em>PNAS</em>, 2015.<br>
    <a href="https://www.rcsb.org/structure/5E0K">PDB 5E0K</a> · <a href="https://doi.org/10.1073/pnas.1516401112">Paper / DOI</a>
  </li>
  <li id="ref-flip2">Didi, K. et al. <strong>FLIP2: Expanding Protein Fitness Landscape Benchmarks for Real-World Machine Learning Applications</strong>. 2026.<br>
    <a href="https://flip.protein.properties/">Project page</a>
  </li>
  <li id="ref-flip">Dallago, C. et al. <strong>FLIP: Benchmark tasks in fitness landscape inference for proteins</strong>. NeurIPS Datasets and Benchmarks, 2021.<br>
    <a href="https://doi.org/10.1101/2021.11.09.467890">Preprint DOI</a>
  </li>
  <li id="ref-esm2">Lin, Z. et al. <strong>Evolutionary-scale prediction of atomic-level protein structure with a language model</strong>. <em>Science</em>, 2023.<br>
    <a href="https://doi.org/10.1126/science.ade2574">Paper / DOI</a>
  </li>
  <li id="ref-guided-protein-generation">Yang, J. et al. <strong>Steering Generative Models with Experimental Data for Protein Fitness Optimization</strong>. NeurIPS 2025 poster.<br>
    <a href="https://openreview.net/forum?id=Ice2BHIumz">OpenReview</a>
  </li>
</ol>

</div>

## Citation

이 글을 인용할 때는 아래 형식을 사용할 수 있다.

```text
Ilho Ahn, "TrpB low-label 후보 reranking: 전역 prior 실패와 radius4 안의 작은 보정 신호", Mini Research, Apr 19, 2026.
```

또는 BibTeX 형식으로는 다음처럼 적을 수 있다.

```bibtex
@article{ahn2026trpblocalfitnessdiffusion,
  author = {Ilho Ahn},
  title = {TrpB low-label 후보 reranking: 전역 prior 실패와 radius4 안의 작은 보정 신호},
  journal = {Mini Research},
  year = {2026},
  month = apr,
  url = {https://muted-color.github.io/research/2026/04/19/trpb-local-fitness-diffusion-prior-reranking/}
}
```
