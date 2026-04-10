---
title: "왜 Gemma 4는 더 잘 읽히고, Gemma 3는 더 잘 따라갔을까"
date: 2026-04-10 21:10:00 +0900
categories: [research]
tags: [gemma, korean, sft, eval]
excerpt: "같은 한국어 SFT 비교에서도 LLM judge 기반 선호는 Gemma 4를, 정답 유사도는 Gemma 3를 더 자주 골랐다. 후속 확인을 거친 뒤 남은 차이는 읽기 품질과 신호 추종이었다."
permalink: /research/2026/04/10/gemma-readability-vs-signal-following/
hero_image: /assets/images/gemma4-gemma3-evidence-map.svg
hero_alt: "Gemma 4와 Gemma 3 비교에서 각 축별 우세를 정리한 axis heatmap"
hero_caption: "Figure 1. 각 행은 실험 묶음을, 각 열은 `LLM Judge`, `Reference Match`, `Signal Following`을 뜻한다. 셀은 그 축에서 더 강하게 보인 쪽을 표시한다."
---

결과를 나란히 놓고 보면, 두 모델은 같은 방향으로 우세하지 않았다.

같은 한국어 SFT 비교인데도 `LLM judge`는 `Gemma 4`를 더 자주 고르고, `Reference Match`는 `Gemma 3`를 더 자주 골랐다. 한쪽은 더 좋아 보인다고 평가됐고, 다른 한쪽은 기준 답안에 더 가깝게 맞췄다.

이 글은 이 엇갈린 결과를 `누가 더 좋으냐`보다 `무엇을 다르게 잘했느냐`의 관점에서 짧게 정리한다. 읽기 품질과 신호 추종을 나눠서 보면, 이 차이는 조금 더 또렷하게 보인다.

## 세 줄 요약

- `LLM judge` 기준에서는 `Gemma 4`가 더 자주 선호됐다.
- `Reference Match`와 `Signal Following` 쪽에서는 `Gemma 3`가 더 강하게 보였다.
- 다만 `signal following`을 곧바로 `robustness`로 읽으면 안 된다.

## 무엇을 어떻게 평가했는가

이번 글에서 평가를 두 축으로 본 이유는, 한 가지 숫자만으로는 두 모델의 차이를 설명하기 어려웠기 때문이다. 한 축은 답이 얼마나 좋아 보이는지를 보고, 다른 한 축은 기준 답안과 얼마나 가까운 표현을 썼는지를 본다. 읽기 품질과 정답 근접도를 나눠서 봐야, 어떤 모델이 무엇에서 앞서는지가 덜 뭉개진다.

> **LLM Judge**
>
> `LLM judge`는 `gpt-oss-120b`를 판정기로 쓴 `pairwise` 비교다. 같은 질문에 대한 두 모델의 답을 나란히 보여주고, 답변 순서는 섞은 뒤 더 나은 쪽을 고르게 했다. 핵심 비교는 `blind_to_reference`로 진행했고, 일부 확인 실험에서는 `with_reference`도 함께 써서 reference 정합성과 분리해 읽었다. 그래서 이 점수는 절대 점수라기보다, 같은 질문에서 두 답 중 어느 쪽이 더 좋아 보였는지를 보는 상대 비교 지표에 가깝다.

> **Reference Match**
>
> `Reference Match`는 기준 답안과 얼마나 가까운 표현을 썼는지를 보는 자동 지표 쪽이다. 이 글에서는 주로 reference overlap, 특히 `ROUGE` 계열 차이를 함께 읽는다. 즉 `LLM judge`가 "무엇이 더 좋아 보이는가"를 본다면, `Reference Match`는 "기준 답안과 얼마나 비슷하게 썼는가"를 본다.

정리하면 `LLM judge`는 전체 인상을, `Reference Match`는 기준 답안과의 표현 유사도를 더 많이 본다. 이 두 축을 나눠서 봐야, 한 모델이 무엇에서 앞서는지 더 분명하게 읽을 수 있다.

## 먼저 보인 결과

Table 1은 이 차이를 세 장면의 점수로 바로 보여준다. 각 행에서 `LLM Judge`는 Gemma 4 쪽이 더 높고, `Reference Match`는 Gemma 3 쪽이 더 높다.

<figure class="table-figure table-figure--comparison">
  <table class="comparison-table">
    <thead>
      <tr>
        <th rowspan="2"></th>
        <th colspan="2">LLM Judge</th>
        <th colspan="2">Reference Match</th>
      </tr>
      <tr>
        <th>Gemma 4</th>
        <th>Gemma 3</th>
        <th>Gemma 4</th>
        <th>Gemma 3</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>기본 질의응답</strong></td>
        <td class="is-better">0.74</td>
        <td>0.26</td>
        <td>0.2928</td>
        <td class="is-better">0.3058</td>
      </tr>
      <tr>
        <td><strong>튜닝 후 질의응답</strong></td>
        <td class="is-better">0.88</td>
        <td>0.12</td>
        <td>0.2928</td>
        <td class="is-better">0.3312</td>
      </tr>
      <tr>
        <td><strong>뉴스 요약</strong></td>
        <td class="is-better">0.73</td>
        <td>0.27</td>
        <td>0.3773</td>
        <td class="is-better">0.5235</td>
      </tr>
    </tbody>
  </table>
  <figcaption><strong>Table 1.</strong> 초반 세 장면의 개별 점수를 나란히 놓고 보면, <code>LLM Judge</code>는 Gemma 4 쪽이, <code>Reference Match</code>는 Gemma 3 쪽이 더 높게 나타난다.</figcaption>
</figure>

뉴스 요약에서도 같은 패턴이 반복됐다. `Gemma 4`는 더 읽기 좋게 마무리하고, `Gemma 3`는 정답 표현에 더 가깝게 맞췄다.

같은 실험에서도 "`더 좋아 보이는 답`"과 "`정답에 더 닮은 답`"은 다를 수 있었고, 이번 비교가 그 사례였다.

## 결과를 어떻게 읽을 것인가

여기서부터는 이 독특한 결과를 바로 결론으로 받아들이지 않고, 몇 가지 축으로 나눠 해석해본다. 먼저 더 단순한 설명이 충분한지 보고, 그다음에도 남는 차이가 무엇인지 살펴보는 순서다.

### 평가 조건이 만든 차이였을까

이 차이가 정말 모델 성격 차이인지 보려면, 먼저 더 단순한 설명부터 지워야 했다. 여기서는 세 가지를 봤다. `Gemma 4`가 더 길게 써서 judge에서 유리했던 것은 아닌지, 기준 답안 품질 때문에 `Gemma 3`가 reference 기반 지표에서 유리했던 것은 아닌지, 기준 답안을 하나만 둔 탓에 phrasing 편향이 생긴 것은 아닌지다.

답 길이부터 보면, 뉴스 요약의 길이 통제 조건에서 두 모델의 평균 출력 길이는 `Gemma 4 = 111.5자`, `Gemma 3 = 106.4자`로 이미 비슷했다. 그래도 `LLM Judge`는 `Gemma 4`를, reference 기반 metric은 `Gemma 3`를 더 높게 봤다. 기준 답안을 더 다듬거나, 기준 답안을 하나에서 둘로 늘려도 방향은 바뀌지 않았다.

<figure class="table-figure table-figure--metrics">
  <table class="metrics-table">
    <thead>
      <tr>
        <th rowspan="2">점검한 설명</th>
        <th rowspan="2">대표 조건</th>
        <th colspan="2">LLM Judge</th>
        <th colspan="2">Reference 기반 지표</th>
      </tr>
      <tr>
        <th>Gemma 4</th>
        <th>Gemma 3</th>
        <th>Gemma 4</th>
        <th>Gemma 3</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>답 길이 차이</td>
        <td>길이 통제 + reference 포함</td>
        <td class="is-better">0.69</td>
        <td>0.26</td>
        <td>0.4047</td>
        <td class="is-better">0.4967</td>
      </tr>
      <tr>
        <td>기준 답안 품질</td>
        <td>다듬은 기준 답안</td>
        <td class="is-better">0.90</td>
        <td>0.10</td>
        <td>0.2933</td>
        <td class="is-better">0.3190</td>
      </tr>
      <tr>
        <td>single-reference 편향</td>
        <td>기준 답안 2개</td>
        <td class="is-better">0.90</td>
        <td>0.10</td>
        <td>0.3101</td>
        <td class="is-better">0.3593</td>
      </tr>
    </tbody>
  </table>
  <figcaption><strong>Table 2.</strong> 각 의심을 대표 조건으로 줄여 봐도 방향은 같았다. <code>LLM Judge</code>는 Gemma 4 쪽이 높고, reference 기반 지표는 Gemma 3 쪽이 높았다. 첫 행의 reference 기반 지표는 <code>ROUGE-L</code>, 나머지 행은 <code>Reference Match</code>다.</figcaption>
</figure>

그래서 평가 결과의 엇갈림은 답 길이, 기준 답안 품질, 기준 답안 개수만으로는 잘 설명되지 않는다. 비슷한 길이 안에서도 더 잘 읽히는 답과 기준 답안 문구를 더 닮게 쓰는 답이 갈렸고, 기준 답안을 다듬거나 늘려도 그 방향은 유지됐다.

숫자만으로는 왜 두 평가가 갈리는지 감이 덜 올 수 있어서, 아래에는 judge와 match가 갈린 답변 모양을 한 사례만 붙였다.

<figure class="sample-compare">
  <div class="sample-compare__question">
    <strong>질문</strong>
    <p>자신의 일을 남의 일인 것처럼 이야기하는 심리 현상은 무엇인가? 이것은 왜 발생하는가?</p>
  </div>
  <div class="sample-compare__grid">
    <article class="sample-compare__card">
      <div class="sample-compare__label">Gemma 4 전체 답안</div>
      <div class="sample-compare__body">
        <p>자신의 일을 남의 일인 것처럼 이야기하는 심리 현상은 여러 가지 심리적 기제와 상황적 요인에 의해 발생할 수 있습니다. 이 현상을 지칭하는 하나의 명확한 심리학 용어는 없을 수 있지만, 관련된 몇 가지 개념을 통해 그 원인을 분석해 볼 수 있습니다.</p>
        <p><strong>이 현상을 설명하는 심리적 현상들</strong></p>
        <p>이러한 행동은 주로 <strong>책임 회피</strong>, <strong>자기 방어</strong>, 또는 <strong>인지적 부조화 해소</strong>의 과정에서 나타납니다.</p>
      </div>
    </article>
    <article class="sample-compare__card">
      <div class="sample-compare__label">Gemma 3 전체 답안</div>
      <div class="sample-compare__body">
        <p>이러한 현상은 '자기자신을 묘사하는 일'이라고 불리며, 이는 인간의 심리적 특성 중 하나입니다. 이는 인간이 자신의 경험을 다른 사람에게 설명할 때, 자신의 경험을 다른 사람의 경험으로 바꾸는 것입니다. 이러한 현상은 인간이 자신의 경험을 이해하고 공유하기 위해 발생하는 것으로, 이는 인간의 사회적 관계를 형성하는 데 중요한 역할을 합니다. 이러한 현상은 인간의 자기 인식과 사회적 관계를 이해하는 데 도움이 될 수 있습니다.</p>
      </div>
    </article>
  </div>
  <figcaption><strong>Sample 1.</strong> 같은 질문에 대한 실제 전체 답안 비교다. `LLM Judge`는 Gemma 4를, `Reference Match`는 Gemma 3를 더 높게 가리킨 사례다.</figcaption>
</figure>

이 샘플에서 `Gemma 4`는 먼저 현상을 정의하고, 관련 개념을 묶어 설명의 틀을 세운다. 반면 `Gemma 3`는 문장은 끝까지 닫히지만, 정의가 모호하고 같은 내용을 평면적으로 반복한다. 그래서 `LLM Judge`는 `Gemma 4` 쪽이 `7:3`으로 더 높았고, `Reference Match`는 `Gemma 3 = 0.423`이 `Gemma 4 = 0.301`보다 높았다. 결국 조건을 바꿔봐도 judge는 Gemma 4를, reference 기반 지표는 Gemma 3를 가리키는 흐름이 남는다.

### 그래서 남는 차이는 무엇인가

앞 섹션까지 보면, 두 평가가 갈리는 흐름이 단지 평가 조건의 산물만은 아니라는 점은 남는다. 그래서 다음 질문은 자연스럽다. 그렇다면 실제로 무엇이 갈렸는가. 여기까지 오면 두 모델의 차이는 조금 더 또렷해진다. 한쪽이 모든 면에서 앞섰다기보다, 서로 다른 방향으로 강점을 보였다고 읽는 편이 자연스럽다.

**Gemma 4 쪽에 남은 인상.** `LLM Judge`가 더 자주 고른 답은 대체로 이쪽이었다. 답의 첫 문장에서 주제를 잡고, 설명의 틀을 세운 뒤, 문장을 더 매끈하게 마무리하는 경우가 많았다. 그래서 전체 인상이 더 정돈되고 완결적으로 읽혔다.

**Gemma 3 쪽에서 더 강했던 부분.** 기준 답안 문구와 더 가깝게 맞추는 능력은 이쪽에서 더 자주 보였다. 답변 형식이나 문체 지시, 추가 힌트 같은 바깥 신호가 들어왔을 때도 더 크게 움직였다. 즉 읽기 품질 전체보다는, 주어진 기준과 신호를 더 민감하게 흡수하는 쪽에 가까웠다.

그래서 이번 비교를 한 문장으로 줄이면, 아래 표현이 가장 덜 과장되고도 핵심을 잘 잡는다.

> Gemma 4는 더 잘 읽히고, Gemma 3는 더 닮게 쓰며 더 잘 따라간다.

### 왜 Gemma 3를 signal following으로 읽는가

앞 섹션까지의 정리는 `Gemma 3`가 기준 답안에 더 가깝게 쓴다는 데서 끝나지 않는다. 뒤쪽 실험을 다시 보면, `Gemma 3`는 추가 힌트나 형식 지시가 들어왔을 때 더 크게 움직이는 모델에 가까웠다. 그래서 여기서는 그 차이를 `정답을 더 닮게 쓴다`를 넘어, `바깥에서 들어오는 신호를 더 민감하게 따른다`는 쪽으로 읽을 수 있는지를 본다.

여기서 말하는 `signal following`도 거창한 뜻은 아니다. 정답이 여러 개일 수 있다는 힌트, 프롬프트 문구가 주는 형식 신호처럼 바깥에서 들어오는 추가 단서를 얼마나 민감하게 받아들이는지를 가리킨다. 아래 두 장면은 이 정의를 서로 다른 방식으로 확인해준다. 하나는 `정답 다양성`에 대한 반응이고, 다른 하나는 `프롬프트 형식 신호`에 대한 반응이다.

#### 한 질문에 정답을 여러 개 붙여 학습했을 때

한 질문에 정답을 하나만 붙이는 대신, 서로 다른 정답을 여러 개 붙여 SFT하면 모델이 `정답 다양성`이라는 supervision 신호를 얼마나 흡수하는지 볼 수 있다.

여기서는 `Gemma 3` 쪽 변화가 더 컸다. `Gemma 3`는 judge 선호가 `0.10 -> 0.23`, reference match가 `0.327 -> 0.338`으로 올랐다. 반면 `Gemma 4`는 judge 우세는 유지했지만 같은 변화에서 추가 이득은 크지 않았다.

<figure class="media-figure">
  <img src="/assets/images/gemma4-gemma3-exp17b.svg" alt="정답을 하나 줄 때와 여러 개 줄 때 Gemma 4와 Gemma 3의 judge와 reference match 변화 비교">
  <figcaption><strong>Figure 2.</strong> 정답을 하나 둘 때보다 여러 개 둘 때 `Gemma 3`가 더 크게 움직였다. `Gemma 4`는 원래 `LLM Judge`가 높았고, `Gemma 3`는 `Reference Match`와 judge 모두에서 변화 폭이 더 컸다.</figcaption>
</figure>

이 장면이 남기는 인상은 비교적 단순하다. `Gemma 3`는 "정답이 하나가 아닐 수 있다"는 힌트를 더 잘 흡수했고, `Gemma 4`는 이미 읽기 품질이 높은 대신 이런 추가 신호에 크게 흔들리지는 않았다. 즉 이 사례는 `여러 가능한 정답`이라는 supervision 신호에 대한 반응 차이를 보여준다.

#### 프롬프트 문구를 정리했을 때

프롬프트 문구를 조금만 정리해도 같은 차이가 다시 나타났다. 문구가 정돈된 프롬프트와 덜 정돈된 프롬프트를 비교했을 때도 `Gemma 3`가 더 민감하게 반응했다. 이번에는 `정답 다양성`이 아니라, 프롬프트가 주는 `형식 신호`를 건드린 셈이다.

`Gemma 3 / base`는 정돈된 프롬프트에서 `readability 0.62 vs raw 0.38`, `faithfulness 0.94 vs raw 0.06`으로 강하게 반응했다. 덜 정돈된 짧은 프롬프트에서도 `faithfulness 0.86 vs raw 0.10`으로 차이가 컸다. `Gemma 4`도 지시를 더 잘 따르는 쪽의 변화는 있었지만, 읽기 품질 자체는 raw 쪽이 더 안정적이었다.

이 장면도 같은 쪽을 가리킨다. `Gemma 3`는 프롬프트가 주는 형식 신호에 더 민감했고, `Gemma 4`는 문구가 조금 바뀌어도 읽기 품질을 비교적 비슷하게 유지했다. 그래서 두 사례를 함께 읽으면, `Gemma 3`의 강점은 단순한 표현 유사도가 아니라 `외부 신호에 더 크게 반응하는 성향`에 가깝다고 정리할 수 있다.

### Gemma 3는 잘 따랐지만, Gemma 4가 더 잘 버텼다

신호 추종과 입력 손상 내성은 같은 능력이 아니었다. 앞의 두 사례에서 `Gemma 3`는 추가 supervision과 프롬프트 형식 신호에 더 크게 반응했다. 하지만 질문 본문 자체를 손상시키면 이야기가 달라진다.

<figure class="media-figure">
  <img src="/assets/images/gemma4-gemma3-robustness-contrast.svg" alt="질문 본문 손상 조건에서 raw와 body-hard readability를 비교한 plot">
  <figcaption><strong>Figure 3.</strong> 값은 같은 모델 안에서 `raw`와 `body-hard`를 맞붙였을 때, 각 조건이 `readability` 판정에서 이긴 비율이다. 예를 들어 `0.66`은 `Gemma 3`의 `raw` 답이 `body-hard`보다 readability 기준으로 `66%` 더 자주 선택됐다는 뜻이다. 두 모델 모두 질문 본문이 망가지면 `raw` 쪽이 더 자주 이겼다.</figcaption>
</figure>

Figure 3에서 `Gemma 3`는 `raw 0.66`에서 `body-hard 0.32`로 크게 떨어졌고, `Gemma 4`는 `raw 0.56`에서 `body-hard 0.38`로 더 작게 떨어졌다. 두 모델 모두 손상 입력에서는 `raw`보다 나빠졌지만, 이 조건에서는 `Gemma 4`가 상대적으로 덜 무너졌다.

따라서 `Gemma 3`를 signal following이 강한 모델로 읽는 것은 가능하지만, 그걸 noisy-input robustness로 일반화하면 안 된다. 반대로 `Gemma 4`가 더 잘 버틴다는 해석도 아직은 `synthetic body corruption` 조건 안의 제한적 결과로 읽어야 한다.

## 최종 결론

여기까지를 가장 짧게 줄이면 이렇다. `Gemma 4`는 읽기 품질과 완결성 쪽에서 더 강했고, `Gemma 3`는 기준 답안에 가까운 표현을 쓰고 추가 신호를 따라 움직이는 쪽에서 더 강했다. 이번 결과는 한 모델이 모든 축에서 이겼다는 이야기라기보다, 서로 다른 강점을 드러냈다는 쪽에 가깝다.

실무적으로 읽으면 아래처럼 정리할 수 있다.

<figure class="table-figure">
  <table>
    <thead>
      <tr>
        <th>모델</th>
        <th>기대하기 좋은 것</th>
        <th>과하게 말하면 안 되는 것</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Gemma 4</td>
        <td>읽기 품질, 완결성, judge 기준 선호 품질</td>
        <td>noisy input에도 특별히 강하다고 단정하는 것</td>
      </tr>
      <tr>
        <td>Gemma 3</td>
        <td>정답 스타일 추종, 형식 준수, 추가 supervision 흡수</td>
        <td>전체 품질이 항상 더 낫다거나 입력 손상에도 더 강하다고 일반화하는 것</td>
      </tr>
    </tbody>
  </table>
  <figcaption><strong>Table 3.</strong> 이번 결과를 실무에서 해석할 때, 각 모델에 무엇을 기대할 수 있고 어디서부터는 과장인지 정리한 표다.</figcaption>
</figure>

지금 기준에서 가장 덜 과장된 요약도 같다. `Gemma 4`는 읽기 품질 쪽에서 강했고, `Gemma 3`는 신호를 따라 움직이는 쪽에서 강했다.
