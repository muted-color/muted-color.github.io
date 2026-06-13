---
title: "DPO 이후 GRPO 형식 보정의 검증기 지향 아티팩트 평가"
layout: post
date: 2026-06-08 09:00:00 +0900
last_modified_at: 2026-06-09 09:00:00 +0900
categories: ["LLM EVAL"]
tags: [korean-ui-copy, structured-generation, grpo, dpo, reward-hacking, llm-judge, format-validation, automatic-evaluation]
excerpt: "한국어 구조화 UI 문구 생성에서 DPO 이후 GRPO 형식 보정이 형식 회복인지 검증기 프록시 과최적화인지 자동 신호로 평가한다."
description: "한국어 구조화 UI 문구 생성에서 DPO 이후 GRPO 형식 보정이 공개 검증기 통과율, 구조 휴리스틱, 보조 LLM judge 신호에 미치는 영향을 분리해 평가하고, slot stuffing과 기본 슬롯 자리 이동 완화 결과를 정리한다."
permalink: /technical-reports/korean-ui-grpo-validator-artifact-evaluation/
image: /assets/images/common/editorial-hero-social.png
image_alt: "한국어 구조화 UI 문구 생성의 GRPO 형식 보정 아티팩트 평가를 나타내는 소셜 썸네일"
hero_image: /assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/hero.svg
hero_alt: "DPO 기준점, GRPO 보상, 구조 신호 점검, 완화 루프를 연결한 검증기 지향 아티팩트 평가 도식"
hero_caption: "<strong>Figure 1.</strong> DPO 이후 GRPO 형식 보정을 평가하는 흐름이다. 공개 검증기, 구조 휴리스틱, 고정 LLM judge, 아티팩트 완화 루프를 분리해 집계한다."
hero_frame: true
hero_variant: rounded-wide
math: true
hidden: true
publication_status: "technical-report"
report_scope: "technical report"
lab_path: "experiment-lab/projects/ui-grade-copy-generation-reward-analysis"
---

[구조화된 한국어 UI 문구 생성에서 NLL 프록시와 정렬 학습](/technical-reports/korean-ui-nll-proxy-alignment/)은 DPO가 한국어 추천 카드 문구의 NLL 기반 품질 프록시를 낮추는 동시에, 메타 슬롯 확장 카드의 형식 통과율을 크게 떨어뜨린다는 문제를 다뤘다. 이후 GRPO 형식 보정은 공개 검증기 통과율을 회복했다. 남는 쟁점은 이 회복이 실제 구조 회복인지, 보상이 보는 검증기 프록시에 맞춘 아티팩트인지 구분하는 일이다.

인간 평가 예산 없이 이 질문을 직접 판정할 수는 없다. 대신 공개 검증기, judge와 독립적인 구조 휴리스틱, 고정 LLM judge를 분리해 자동 신호의 방향을 비교한다.

결과는 보수적으로 해석해야 한다. 현 설정에서 GRPO는 공개 검증 통과율과 `hidden_auto_pass`를 함께 올리고, 공개 검증기와 judge 사이의 gap은 통계적으로 평탄하다. 자동 신호만 놓고 보면 강한 검증기 과최적화보다 형식 회복에 더 가깝다. 그러나 LLM judge가 거의 보지 못하는 구조적 아티팩트, 특히 slot stuffing은 분명히 생긴다. 이 아티팩트를 페널티로 누르면 stuffing은 사라지지만 기본 슬롯 붕괴로 이동하고, 두 번째 페널티를 함께 두어야 자리 이동이 해소된다.

> **공개 검증기**는 GRPO 보상이 직접 보는 형식 검사기다. 필드 존재, 길이 상한, 허용 어미, 슬롯 범주, 비어 있지 않은 `place` 등을 검사한다.
>
> **구조 휴리스틱**은 보상이 직접 보지 않는 구조 신호다. `slot_stuffing`, `default_slot_rate`, `suffix_concentration`, `template_dup`, `slot_context_conflict` 등을 포함한다.
>
> **hidden_auto_pass**는 `public_format_pass ∧ judge_ctx≥2 ∧ judge_nat≥1`의 약칭이다. 사람 평가 기준이 아니라 고정 LLM judge가 만든 보조 신호다.

{% include model-mention-cards.html label="사용한 주요 리소스" aria_label="사용한 모델과 방법 리소스" models="Gemma 3 4B IT|google/gemma-3-4b-it|https://huggingface.co/google/gemma-3-4b-it;Direct Preference Optimization|Rafailov et al. 2023|https://proceedings.neurips.cc/paper_files/paper/2023/hash/a85b405ed65c6477a4fe8302b5e06ce7-Abstract-Conference.html;GRPO / DeepSeekMath|Shao et al. 2024|https://arxiv.org/abs/2402.03300;LLM-as-a-Judge|Zheng et al. 2023|https://proceedings.neurips.cc/paper_files/paper/2023/hash/91f18a1287b398d378ef22505bf41832-Abstract-Datasets_and_Benchmarks.html" %}

## 요약

- DPO 기준점의 공개 검증 통과율은 `0.389`였고, GRPO 종점은 binary `0.587`, dense `0.669`까지 회복했다.
- 고정 judge를 결합한 `hidden_auto_pass`도 DPO `0.278`에서 binary `0.460`, dense `0.517`로 함께 올랐다.
- 공개 검증기와 judge 사이의 gap은 DPO `0.110`, binary `0.138`, dense `0.122`로 약 `0.11-0.14` 범위에 머물렀고, 모델 간 gap 변화의 bootstrap CI는 모두 0을 포함했다.
- 가장 큰 구조 변화는 slot stuffing이다. DPO `0.218`에서 binary `0.640`, dense `0.668`로 약 3배 상승했다.
- anti-stuffing penalty는 slot stuffing을 `0.668 -> 0.015`로 낮췄지만, default-slot rate를 `0.056 -> 0.345`로 밀어 올렸다.
- 결합 penalty인 `antistuff2`는 default-slot rate를 `0.068`로 되돌리고 slot stuffing을 `0.141`로 낮게 유지했다. 비용은 dense 대비 공개 검증 통과율 약 2포인트였다.
- judge와 인간 라벨의 일치도는 낮았다. Gemini-2.5-flash의 quadratic-weighted kappa는 tpo ctx `0.059`, tpo nat `0.143`이므로 judge는 보조 신호로만 사용한다.
- 이 평가의 1차 근거는 judge가 아니라 결정론적 구조 휴리스틱과 공개 검증기의 분리 집계다.

## 문제 설정

평가 대상은 한국어 추천 카드 문구다. 출력은 `reason`, `title`, `subtitle` 같은 짧은 문구 필드와 `season`, `time`, `place` 같은 메타 슬롯을 포함한다. 메타 슬롯 확장 카드는 일반 자유 생성보다 실패 조건이 좁다. 문장이 자연스러워도 길이, 어미, 슬롯 범주, 빈 값 제약을 어기면 UI에 배치하기 어렵다.

이전 정렬 분석에서 DPO는 형식 통과 부분집합의 NLL 프록시를 낮췄지만, 메타 슬롯 카드의 형식 통과율을 `0.764 -> 0.376`으로 떨어뜨렸다. 이 글에서 사용한 별도 검증 생성 집계에서는 DPO 기준점의 공개 검증 통과율이 `0.389`로 계산된다. 이후 GRPO 형식 보정은 공개 검증기 통과율을 다시 끌어올렸다. 그러나 보상이 보는 것은 공개 검증기이므로, 통과율 상승만으로 구조가 실제로 회복됐다고 말할 수 없다.

평가 신호는 세 층으로 나눴다.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>신호</th>
          <th>무엇을 측정하나</th>
          <th>해석 기준</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>공개 검증기</td>
          <td>보상이 직접 보는 형식 규칙 통과 여부</td>
          <td>UI 배치 가능한 구조인지 보는 1차 형식 제약</td>
        </tr>
        <tr>
          <td>구조 휴리스틱</td>
          <td>slot stuffing, 기본 슬롯 붕괴, suffix concentration 등</td>
          <td>검증기가 통과시킬 수 있는 구조적 아티팩트 감지</td>
        </tr>
        <tr>
          <td>고정 LLM judge</td>
          <td>자연성 <code>nat</code>과 입력-출력 문맥 적합도 <code>ctx</code></td>
          <td>일치도가 낮으므로 보조 신호로만 사용</td>
        </tr>
        <tr>
          <td>NLL 프록시</td>
          <td>참조 LM 기준 조건부 설명 가능성</td>
          <td>품질 전체가 아니라 보조 신호</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> 평가에서 분리한 신호다. 공개 검증기는 보상이 직접 보는 신호이고, 구조 휴리스틱은 그 바깥의 구조적 사각지대를 확인하기 위한 신호다.</figcaption>
</figure>

judge 검증 결과는 해석 범위를 좁힌다. 500건의 인간 검토 라벨과 비교했을 때 Gemini-2.5-flash의 tpo ctx QWK는 `0.059`, tpo nat QWK는 `0.143`이었다. 정확히 같은 점수를 준 비율은 약 `0.53-0.56`, 1점 이내 일치율은 약 `0.94-0.95`였지만, 0/1/2 척도에서 순위 정합성은 약했다. 이 때문에 `hidden_auto_pass`는 사람 평가 품질이 아니라 고정 judge가 만든 보조 신호로만 읽는다.

## 평가 설계

GRPO는 DPO 정책에서 시작한다. 비교한 보상 변형은 네 가지다.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>초기화</th>
          <th>보상</th>
          <th>역할</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>DPO</td>
          <td>-</td>
          <td>-</td>
          <td>GRPO step 0 기준점</td>
        </tr>
        <tr>
          <td>GRPO-binary</td>
          <td>DPO</td>
          <td><code>V_public</code>를 통과하면 1, 아니면 0</td>
          <td>가장 단순한 형식 보상 기준선</td>
        </tr>
        <tr>
          <td>GRPO-dense</td>
          <td>DPO</td>
          <td>부분 점수형 형식 보상</td>
          <td>더 매끄러운 형식 보상 조정</td>
        </tr>
        <tr>
          <td>GRPO-antistuff</td>
          <td>DPO</td>
          <td><code>dense - 0.25 * max(0, #slot_tokens - 3)</code></td>
          <td>slot stuffing 표적 완화</td>
        </tr>
        <tr>
          <td>GRPO-antistuff2</td>
          <td>DPO</td>
          <td><code>antistuff - 0.40 * [season=전체 ∧ time=전체]</code></td>
          <td>아티팩트 자리 이동 차단</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> 비교한 보상 변형이다. <code>antistuff2</code>는 첫 완화가 만든 기본 슬롯 붕괴를 막기 위한 결합 완화다.</figcaption>
</figure>

평가는 학습에 쓰지 않은 1,026개 입력에서 진행했다. 각 checkpoint에서는 학습 시 샘플링 조건과 맞춰 입력당 K=4 생성을 만들었고, 한 생성이 여러 카드를 낼 수 있으므로 전체 채점 단위는 약 5.5-6천 카드다. 공개 검증기와 구조 휴리스틱은 전체 카드 집합에서 계산했다. LLM judge는 checkpoint마다 고정 seed로 뽑은 400카드 표본에만 적용했다. 연속된 앞쪽 N개 표본은 입력 난이도와 순서가 얽혀 gap 추세를 뒤집을 수 있었기 때문에, 본문 집계는 무작위 400카드 표본만 사용한다.

통계는 비율에 대한 bootstrap 95% CI를 사용했다. 모델 간 검증기-judge gap 변화는 judge 표본을 재사용한 bootstrap difference로 확인했다. 같은 카드에서 공개 검증 통과와 `hidden_auto_pass`가 갈리는지 보는 내부 점검에는 McNemar test를 사용했지만, 해석의 중심은 모델 간 gap 변화와 구조 휴리스틱에 둔다.

## 결과

### 종점 평가

종점 집계에서는 공개 검증 통과율과 `hidden_auto_pass`가 함께 상승한다. 동시에 slot stuffing도 커진다. 공개 검증 통과율만 보면 형식 회복으로 보이지만, 구조 휴리스틱을 함께 보면 검증기가 허용하는 좁은 실패 양식이 남는다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/endpoint-evaluation-matrix.svg" alt="DPO, binary, dense, antistuff, antistuff2의 공개 검증 통과율, hidden_auto_pass, 검증기-judge gap, slot stuffing, default_slot_rate를 비교한 종점 요약 도표">
  <figcaption><strong>Figure 2.</strong> 종점 평가 요약 도표다. binary와 dense는 공개 검증 통과율과 <code>hidden_auto_pass</code>를 올리지만 slot stuffing도 크게 늘린다. antistuff는 stuffing을 거의 제거하지만 기본 슬롯 붕괴를 만든다. antistuff2는 두 아티팩트를 함께 낮춘다.</figcaption>
</figure>

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>지표</th>
          <th class="align-right">DPO</th>
          <th class="align-right">binary</th>
          <th class="align-right">dense</th>
          <th class="align-right">antistuff</th>
          <th class="align-right">antistuff2</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>public_pass</td>
          <td class="align-right"><code>0.389</code></td>
          <td class="align-right"><code>0.587</code></td>
          <td class="align-right"><code>0.669</code></td>
          <td class="align-right"><code>0.694</code></td>
          <td class="align-right"><code>0.647</code></td>
        </tr>
        <tr>
          <td>hidden_auto_pass</td>
          <td class="align-right"><code>0.278</code></td>
          <td class="align-right"><code>0.460</code></td>
          <td class="align-right"><code>0.517</code></td>
          <td class="align-right"><code>0.580</code></td>
          <td class="align-right"><code>0.535</code></td>
        </tr>
        <tr>
          <td>public_judge_gap</td>
          <td class="align-right"><code>0.110</code></td>
          <td class="align-right"><code>0.138</code></td>
          <td class="align-right"><code>0.122</code></td>
          <td class="align-right"><code>0.115</code></td>
          <td class="align-right"><code>0.135</code></td>
        </tr>
        <tr>
          <td>slot_stuffing</td>
          <td class="align-right"><code>0.218</code></td>
          <td class="align-right"><code>0.640</code></td>
          <td class="align-right"><code>0.668</code></td>
          <td class="align-right"><code>0.015</code></td>
          <td class="align-right"><code>0.141</code></td>
        </tr>
        <tr>
          <td>default_slot_rate</td>
          <td class="align-right"><code>0.072</code></td>
          <td class="align-right"><code>0.066</code></td>
          <td class="align-right"><code>0.056</code></td>
          <td class="align-right"><code>0.345</code></td>
          <td class="align-right"><code>0.068</code></td>
        </tr>
        <tr>
          <td>NLL_ctx median</td>
          <td class="align-right"><code>2.641</code></td>
          <td class="align-right"><code>2.613</code></td>
          <td class="align-right"><code>2.625</code></td>
          <td class="align-right"><code>2.621</code></td>
          <td class="align-right"><code>2.621</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> 종점의 핵심 평가 신호다. 공개 검증 통과율과 <code>hidden_auto_pass</code>는 함께 상승하지만, binary와 dense에서는 slot stuffing도 크게 늘어난다. 비율 행은 카드 단위이며, <code>NLL_ctx median</code>은 카드 단위 중앙값이다. judge 기반 행은 무작위 400카드 judge 표본에서 계산했다.</figcaption>
</figure>

binary와 dense는 공개 검증 통과율만 올리지 않는다. `hidden_auto_pass`도 함께 올라가고, `judge_fail_given_public_pass`는 DPO `0.284`에서 binary `0.230`, dense `0.191`로 낮아졌다. NLL_ctx 중앙값도 큰 악화를 보이지 않는다. 반면 slot stuffing은 DPO 대비 약 3배로 늘어난다. 이 아티팩트는 judge_ctx_mean이 함께 상승하는 조건에서도 생겼기 때문에, judge가 자연성이나 문맥 적합도만으로 쉽게 잡는 실패는 아니다.

### 검증기 신호 변화

step별 곡선에서도 같은 패턴이 반복된다. binary와 dense 모두 공개 검증 통과율과 `hidden_auto_pass`가 올라가지만, slot stuffing 역시 학습 초반부터 빠르게 상승한다. dense는 binary보다 종점의 공개 검증 통과율이 높지만, stuffing도 거의 같은 높은 구간으로 수렴한다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/overoptimization-curves.svg" alt="binary와 dense GRPO에서 step별 공개 검증 통과율, hidden_auto_pass, slot_stuffing_rate가 함께 변하는 선 그래프">
  <figcaption><strong>Figure 3.</strong> binary와 dense의 검증기 신호 변화다. 두 보상 모두 공개 검증 통과율과 <code>hidden_auto_pass</code>를 올리지만, slot stuffing도 함께 늘어난다. dense 보상은 더 높은 통과율 구간을 만들지만 구조적 실패 양식 자체를 제거하지는 못한다.</figcaption>
</figure>

강한 검증기 과최적화라면 공개 검증 통과율 상승과 보조 신호 악화가 함께 나타나야 한다. 이 조건에서는 공개 검증 통과율과 `hidden_auto_pass`가 함께 상승하고, 검증기-judge gap의 모델 간 변화도 유의하지 않았다.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>비교</th>
          <th class="align-right">Δ public_judge_gap</th>
          <th class="align-right">95% CI</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>binary - DPO</td>
          <td class="align-right"><code>+0.028</code></td>
          <td class="align-right"><code>[-0.018, +0.073]</code></td>
        </tr>
        <tr>
          <td>dense - DPO</td>
          <td class="align-right"><code>+0.013</code></td>
          <td class="align-right"><code>[-0.032, +0.057]</code></td>
        </tr>
        <tr>
          <td>antistuff - dense</td>
          <td class="align-right"><code>-0.008</code></td>
          <td class="align-right"><code>[-0.052, +0.037]</code></td>
        </tr>
        <tr>
          <td>antistuff2 - dense</td>
          <td class="align-right"><code>+0.012</code></td>
          <td class="align-right"><code>[-0.033, +0.057]</code></td>
        </tr>
        <tr>
          <td>antistuff2 - antistuff</td>
          <td class="align-right"><code>+0.020</code></td>
          <td class="align-right"><code>[-0.025, +0.065]</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> 모델 간 검증기-judge gap 변화의 bootstrap CI다. 모든 구간이 0을 포함하므로, 이 평가에서는 gap 변화가 보상 변형 간 결론을 밀어주는 신호가 아니다.</figcaption>
</figure>

### 완화와 자리 이동

완화 실험은 slot stuffing을 유용한 내용보다 아티팩트에 가깝게 보게 하는 근거다. `antistuff`는 slot token이 3개를 넘으면 페널티를 준다. 이 단일 페널티는 stuffing을 `0.668 -> 0.015`로 낮추면서도 공개 검증 통과율을 `0.694`까지 올렸다. hidden_auto_pass도 `0.580`으로 가장 높았다. 이 설정에서 과도한 slot token은 높은 공개 검증 통과율에 필요하지 않았다.

그러나 아티팩트는 완전히 사라지기보다 이동했다. stuffing이 막히자 정책은 `season=전체 ∧ time=전체` 같은 일반 슬롯 조합으로 붕괴했고, default_slot_rate가 `0.056 -> 0.345`로 올랐다. `antistuff2`는 이 조합을 추가로 페널티해 default_slot_rate를 `0.068`로 되돌렸다. slot stuffing은 `0.141`로 dense 대비 낮게 유지됐고, 공개 검증 통과율 비용은 약 2포인트였다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/mitigation-shift.svg" alt="dense, antistuff, antistuff2에서 slot stuffing, 기본 슬롯 비율, 공개 검증 통과율을 비교한 막대 그래프">
  <figcaption><strong>Figure 4.</strong> 완화와 아티팩트 자리 이동이다. antistuff는 stuffing을 거의 제거하지만 기본 슬롯 붕괴를 만든다. antistuff2는 이동한 아티팩트까지 함께 제약하면서 stuffing과 기본 슬롯 비율을 낮게 유지한다.</figcaption>
</figure>

같은 입력의 정성 예시도 이 해석과 맞는다. 헤어스타일링 제품 입력에서 dense는 `time=[아침, 저녁, 밤]`, `place=[집, 미용실]`처럼 유효 슬롯을 과다 나열했다. antistuff는 `season=전체`, `time=전체`, `place=전체`에 가까운 일반 조합으로 이동했다. antistuff2는 `time=아침`, `place=헤어샵`처럼 더 구체적인 슬롯으로 돌아왔다. 이 예시는 결론의 주된 근거가 아니라, 정량 지표가 가리키는 이동 양상을 보여주는 샘플이다.

### 시드 안정성

두 핵심 변형은 두 번째 seed에서도 종점을 확인했다. binary의 slot stuffing은 seed 42에서 `0.640`, seed 43에서 `0.696`이었다. 둘 다 DPO 기준점 `0.218`보다 크게 높다. binary의 공개 검증 통과율은 `0.587`과 `0.619`, 검증기-judge gap은 `0.138`과 `0.140`이었다.

antistuff의 slot stuffing은 seed 42에서 `0.015`, seed 43에서 `0.023`이었다. hidden_auto_pass는 `0.580`과 `0.565`였다. seed 간 차이는 효과 크기보다 작았다. binary에서 stuffing이 생기고 antistuff에서 stuffing이 제거되는 현상은 두 seed 범위에서는 유지된다. 모든 변형에 대한 다중 seed 평균은 수행하지 않았다.

### 실패 유형 분해

GRPO-binary 내부 실패 분류에서는 길이 위반 감소가 가장 크게 보인다. `LEN_EXCEEDED`는 step 50의 `0.539`에서 step 810의 `0.225`로 줄었다. 반면 `BAD_SUFFIX`는 `0.291 -> 0.275`로 큰 변화 없이 남았다. `INVALID_CATEGORY`는 거의 0이다. 이 패턴은 stuffing이 잘못된 카테고리 선택보다 유효 슬롯 값을 과도하게 나열하는 문제에 가깝다는 해석을 뒷받침한다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/failure-taxonomy.svg" alt="GRPO-binary step별 LEN_EXCEEDED, BAD_SUFFIX, INVALID_CATEGORY 문제 비율 변화 선 그래프">
  <figcaption><strong>Figure 5.</strong> GRPO-binary의 실패 분류 변화다. 길이 위반은 감소하지만 BAD_SUFFIX는 남고, 카테고리 위반은 거의 0이다. stuffing은 잘못된 카테고리 선택보다 유효 슬롯 과다 나열에 가깝다.</figcaption>
</figure>

## 해석

현 설정에서 GRPO 형식 보정은 자동 신호 기준으로 강한 검증기 과최적화보다 형식 회복에 더 가깝다. 공개 검증 통과율과 `hidden_auto_pass`가 함께 상승하고, 검증기-judge gap은 모델 간 유의한 변화를 보이지 않는다. NLL_ctx도 종점에서 큰 악화를 보이지 않는다.

그렇다고 구조적 아티팩트가 없다는 뜻은 아니다. binary와 dense 모두 slot stuffing을 크게 만든다. 이 아티팩트는 공개 검증기를 통과하고 고정 judge도 거의 페널티하지 못한다. LLM judge 단독으로는 구조화 UI 생성의 좁은 실패를 놓칠 수 있다.

완화도 단일 지표만 보고 설계하기 어렵다. slot stuffing만 누르면 기본 슬롯 붕괴가 생긴다. 이동한 아티팩트를 다시 점검하고 결합 페널티로 막았을 때에야 stuffing과 기본 슬롯 비율을 함께 낮출 수 있었다.

## 한계

- 인간 평가를 사용하지 않았다. `hidden_auto_pass`는 고정 LLM judge 기반 보조 신호이며, 사람 판단이나 운영 품질 전체를 뜻하지 않는다.
- judge와 인간 라벨의 일치도가 낮다. tpo ctx QWK는 `0.059`, tpo nat QWK는 `0.143`이라서 judge 기반 값은 보조 신호로만 사용한다.
- judge는 무작위 400카드 표본에서만 계산했다. 전체 카드 집합의 공개 검증기/휴리스틱 비율보다 CI가 넓고, 표본 추출 방식이 결론에 영향을 줄 수 있다.
- 곡선은 대부분 단일 seed다. 두 핵심 변형은 seed 43으로 반복했지만, 모든 변형의 다중 seed 평균은 아니다.
- slot stuffing cutoff, anti-stuffing cap, penalty weight, judge pass threshold는 수작업 설정이다. 인접 cutoff에서 순서는 유지됐지만 절대 비율을 표준값처럼 해석해서는 안 된다.
- 실증 범위는 Gemma3-4B 계열, 한국어 추천 카드, DPO 이후 GRPO 형식 보정이다. 다른 언어, 더 긴 UI copy, constrained decoding, reranking은 별도 비교가 필요하다.

## References

<div class="reference-list" markdown="1">

1. <span id="ref-gemma-3"></span>Google DeepMind. [Gemma 3 model card](https://huggingface.co/google/gemma-3-4b-it). 2025.
2. <span id="ref-dpo"></span>Rafael Rafailov et al. [Direct Preference Optimization: Your Language Model is Secretly a Reward Model](https://proceedings.neurips.cc/paper_files/paper/2023/hash/a85b405ed65c6477a4fe8302b5e06ce7-Abstract-Conference.html). NeurIPS 2023.
3. <span id="ref-grpo"></span>Zhihong Shao et al. [DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models](https://arxiv.org/abs/2402.03300). 2024.
4. <span id="ref-overoptimization"></span>Leo Gao, John Schulman, and Jacob Hilton. [Scaling Laws for Reward Model Overoptimization](https://arxiv.org/abs/2210.10760). ICML 2023.
5. <span id="ref-specification-gaming"></span>Dario Amodei et al. [Concrete Problems in AI Safety](https://arxiv.org/abs/1606.06565). 2016.
6. <span id="ref-reward-hacking"></span>Joar Skalse et al. [Defining and Characterizing Reward Hacking](https://arxiv.org/abs/2209.13085). NeurIPS 2022.
7. <span id="ref-llm-judge"></span>Lianmin Zheng et al. [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://proceedings.neurips.cc/paper_files/paper/2023/hash/91f18a1287b398d378ef22505bf41832-Abstract-Datasets_and_Benchmarks.html). NeurIPS 2023.

</div>

## Citation

Text citation:

```text
Ahn, I. (2026). DPO 이후 GRPO 형식 보정의 검증기 지향 아티팩트 평가. Technical report.
```

BibTeX:

```bibtex
@techreport{ahn2026grpoValidatorArtifactEvaluation,
  title = {DPO 이후 GRPO 형식 보정의 검증기 지향 아티팩트 평가},
  author = {Ahn, Ilho},
  year = {2026},
  type = {Technical report},
  url = {/technical-reports/korean-ui-grpo-validator-artifact-evaluation/}
}
```
