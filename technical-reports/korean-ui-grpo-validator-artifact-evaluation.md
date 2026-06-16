---
title: "한국어 UI 문구 생성에서 GRPO 형식 보정의 구조 아티팩트 분석"
layout: post
date: 2026-06-08 09:00:00 +0900
last_modified_at: 2026-06-16 09:00:00 +0900
categories: ["LLM EVAL"]
tags: [korean-ui-copy, structured-generation, grpo, dpo, reward-hacking, llm-judge, format-validation, automatic-evaluation]
excerpt: "한국어 구조화 UI 문구 생성에서 DPO 이후 GRPO 형식 보정이 형식 회복인지, 검증기 과최적화인지 공개 검증기·구조 휴리스틱·LLM judge 신호로 나눠 평가한다."
description: "한국어 UI 문구 생성에서 DPO 이후 GRPO 형식 보정이 공개 검증기 통과율, 구조 휴리스틱, judge 표본 선택, 생성 시드, constrained decoding에 미치는 영향을 분리해 분석한다."
permalink: /technical-reports/korean-ui-grpo-validator-artifact-evaluation/
image: /assets/images/common/editorial-hero-social.png
image_alt: "한국어 UI 문구 생성의 GRPO 형식 보정 구조 아티팩트 분석을 나타내는 소셜 썸네일"
hero_image: /assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/hero.svg
hero_alt: "DPO 기준점, GRPO 보상, 구조 신호 점검, 완화 루프를 연결한 구조 아티팩트 분석 도식"
hero_caption: "<strong>Figure 1.</strong> DPO 이후 GRPO 형식 보정을 분석하는 흐름이다. 공개 검증기, 구조 휴리스틱, 고정 LLM judge, 아티팩트 완화 과정을 분리해 집계한다."
hero_frame: true
hero_variant: rounded-wide
hidden: true
publication_status: "technical-report"
report_scope: "technical report"
lab_path: "experiment-lab/projects/ui-grade-copy-generation-reward-analysis"
---

[구조화된 한국어 UI 문구 생성에서 NLL 프록시와 정렬 학습](/technical-reports/korean-ui-nll-proxy-alignment/)은 DPO가 한국어 추천 카드 문구의 NLL 기반 품질 프록시를 낮추지만, 메타 슬롯 확장 카드의 형식 통과율을 크게 떨어뜨린다는 문제를 다뤘다. 이번 글은 그 다음 단계인 GRPO 형식 보정이 무엇을 회복하고 무엇을 새로 만드는지 분석한다.

최신 재측정에서는 SFT, DPO, GRPO를 같은 공유 테스트셋과 같은 평가 절차에서 다시 비교했다. 형식 통과율은 SFT `0.724`에서 DPO `0.389`로 떨어지고, GRPO는 이를 `0.587-0.694` 범위로 회복한다. 동시에 DPO가 얻은 NLL_ctx 개선은 대체로 유지된다. 자동 신호만 놓고 보면 GRPO 형식 보정은 강한 검증기 과최적화보다 형식 회복에 더 가깝다. 다만 회복 과정에서 구조 아티팩트가 남는다. GRPO는 LLM judge가 거의 보지 못하는 slot stuffing을 함께 만든다.

이 글은 운영 품질을 직접 판정한 사람 평가 정답셋 없이 세 신호를 분리한다. 공개 검증기는 보상이 직접 보는 형식 검사기다. 구조 휴리스틱은 보상이 보지 않는 좁은 실패를 잡기 위한 결정론적 신호다. 고정 LLM judge는 자연성과 문맥 적합도를 보는 보조 신호지만, 별도 인간 검토 라벨과의 일치도가 낮기 때문에 결론의 1차 근거로 쓰지 않는다.

> `hidden_auto_pass`는 `public_format_pass ∧ judge_ctx≥2 ∧ judge_nat≥1`의 약칭이다. 사람 평가 기준이 아니라 고정 LLM judge가 만든 보조 신호다.
>
> `slot stuffing`은 유효한 슬롯 값을 과도하게 나열하는 구조적 아티팩트다. 이 실패는 카테고리 위반처럼 검증기에 바로 걸리는 오류가 아니라, 검증기가 허용하는 값들을 많이 넣는 방식으로 나타난다.

{% include model-mention-cards.html label="사용한 주요 리소스" aria_label="사용한 모델과 방법 리소스" models="Gemma 3 4B IT|google/gemma-3-4b-it|https://huggingface.co/google/gemma-3-4b-it;Direct Preference Optimization|Rafailov et al. 2023|https://proceedings.neurips.cc/paper_files/paper/2023/hash/a85b405ed65c6477a4fe8302b5e06ce7-Abstract-Conference.html;GRPO / DeepSeekMath|Shao et al. 2024|https://arxiv.org/abs/2402.03300;LLM-as-a-Judge|Zheng et al. 2023|https://proceedings.neurips.cc/paper_files/paper/2023/hash/91f18a1287b398d378ef22505bf41832-Abstract-Datasets_and_Benchmarks.html" %}

## 요약

- SFT-DPO-GRPO 흐름을 같은 테스트셋에서 재측정했다. 공개 검증 통과율은 SFT `0.724`에서 DPO `0.389`로 떨어지고, GRPO 종점은 binary `0.587`, dense `0.669`, antistuff `0.694`까지 회복했다.
- `hidden_auto_pass`도 DPO `0.278`에서 binary `0.460`, dense `0.517`, antistuff `0.580`으로 함께 상승했다. 검증기-judge gap의 모델 간 변화는 bootstrap CI가 모두 0을 포함한다.
- 사전 정의한 여섯 과최적화 기준 중 충족된 것은 구조 실패율 상승, 특히 slot stuffing 하나다. 기준을 둘 이상 요구하면 강한 reward hacking 증거로 보기는 어렵다.
- slot stuffing은 SFT `0.191`, DPO `0.218`에서 GRPO-binary `0.640`, GRPO-dense `0.668`로 약 3배 오른다. judge_ctx 평균이 함께 상승하는 조건에서도 생기므로 judge가 쉽게 잡는 실패가 아니다.
- anti-stuffing 페널티는 stuffing을 `0.668 -> 0.015`로 낮추지만 default_slot_rate를 `0.056 -> 0.345`로 밀어 올린다. 결합 페널티인 `antistuff2`는 default_slot_rate를 `0.068`로 되돌리고 stuffing을 `0.141`로 낮게 유지한다.
- judge 부분표본 선택은 결론을 바꿀 수 있다. 앞에서 400개를 연속으로 뽑으면 gap 추세가 감소처럼 보이고, 무작위 400카드 표본은 평탄하거나 소폭 상승하는 추세를 준다.
- 생성 시드를 다섯 번 바꿔도 종점 효과는 안정적이다. 모든 구조 휴리스틱의 시드별 표준편차는 최대 `0.0075`였다.
- 추론 시점 constrained decoding은 대체재가 아니었다. DPO 기준 정책에서 slot stuffing은 `0.000`까지 낮출 수 있지만 public_pass는 `0.440`에 머물고 length-boundary 문제가 증가하며 hidden_auto_pass는 안정적으로 개선되지 않는다.

## 문제 설정

평가 대상은 한국어 추천 카드 문구다. 출력은 `reason`, `title`, `subtitle` 같은 짧은 문구 필드와 `season`, `time`, `place` 같은 메타 슬롯을 포함한다. 메타 슬롯 확장 카드는 일반 자유 생성보다 실패 조건이 좁다. 문장이 자연스러워도 길이, 어미, 슬롯 범주, 빈 값 제약을 어기면 UI에 배치하기 어렵다.

공개 검증기 `V_public`은 GRPO 보상이 직접 사용하는 형식 검사기다. 필드 존재, 길이 상한, 허용 어미, `season`/`time` 카테고리, 비어 있지 않은 `place` 등을 검사한다. 문제는 보상이 이 검증기만 직접 본다는 점이다. 통과율이 올랐다는 사실만으로는 구조가 실제로 좋아졌는지, 검증기가 허용하는 좁은 실패 양식으로 이동했는지 구분할 수 없다.

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

judge 검증 결과는 해석 범위를 좁힌다. 500건의 인간 검토 라벨과 비교했을 때 Gemini-2.5-flash의 tpo ctx QWK는 `0.059`, tpo nat QWK는 `0.143`이었다. 정확히 같은 점수를 준 비율은 약 `0.53-0.56`, 1점 이내 일치율은 약 `0.94-0.95`였지만, 0/1/2 척도에서 순위 정합성은 약했다. 이 때문에 judge 기반 값은 보조 신호로만 읽는다.

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
          <td>기본 슬롯 자리 이동 차단</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> 비교한 보상 변형이다. <code>antistuff2</code>는 첫 완화가 만든 기본 슬롯 붕괴를 막기 위한 결합 완화다.</figcaption>
</figure>

평가는 학습에 쓰지 않은 1,026개 입력에서 진행했다. 체크포인트마다 학습 시 샘플링 조건과 맞춰 입력당 K=4 생성을 만들었고, 한 생성이 여러 카드를 낼 수 있으므로 전체 채점 단위는 약 5.5-6천 카드다. 공개 검증기와 구조 휴리스틱은 전체 카드 집합에서 계산했다. LLM judge는 체크포인트마다 고정 시드로 뽑은 400카드 표본에만 적용했다.

과최적화 판정은 여섯 기준으로 정리했다. 공개 검증 통과율이 오르는데 hidden_auto_pass가 정체/하락하는지, 검증기-judge gap이 DPO 대비 커지는지, 공개 검증 통과 후 judge 실패율이 오르는지, NLL_ctx가 악화되는지, 구조 휴리스틱이 상승하는지, 보상과 품질 프록시의 상관이 학습 후반에 악화되는지를 본다. 이 중 둘 이상이 같은 방향으로 나타날 때 강한 검증기 과최적화 증거로 읽는다.

## 결과

### SFT-DPO-GRPO 재측정

이번 재측정은 SFT와 DPO 단계까지 같은 테스트셋에서 다시 비교한다. DPO는 public_pass를 `0.724 -> 0.389`로 떨어뜨리지만 NLL_ctx는 `3.152 -> 2.641`로 낮춘다. 이후 GRPO는 NLL_ctx 개선을 유지한 채 public_pass를 다시 `0.587-0.694` 범위로 회복한다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/lineage-recheck.svg" alt="SFT, DPO, GRPO 변형의 공개 검증 통과율, hidden_auto_pass, slot stuffing 변화를 비교한 재측정 도표">
  <figcaption><strong>Figure 2.</strong> 같은 테스트셋에서 재측정한 SFT-DPO-GRPO 비교다. DPO는 형식 통과율을 낮추지만 NLL_ctx를 개선하고, GRPO는 형식을 회복한다. slot stuffing은 SFT/DPO에서 낮다가 GRPO 형식 보상 아래에서 크게 오른다.</figcaption>
</figure>

이 결과는 평가 질문이 이전 리포트의 수치에만 의존하지 않는다는 점에서 중요하다. 같은 평가 절차 안에서도 DPO의 형식 퇴행과 GRPO의 형식 회복이 재현된다. 동시에 slot stuffing은 SFT `0.191`, DPO `0.218`에서 낮다가 GRPO-binary `0.640`, GRPO-dense `0.668`로 상승한다. 아티팩트는 기반 정책에 이미 있던 잔여 문제가 아니라 GRPO 형식 보정 단계에서 커진다.

### 종점 평가

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/endpoint-evaluation-matrix.svg" alt="DPO, binary, dense, antistuff, antistuff2의 공개 검증 통과율, hidden_auto_pass, 검증기-judge gap, slot stuffing, default_slot_rate를 비교한 종점 요약 도표">
  <figcaption><strong>Figure 3.</strong> 종점 평가 요약 도표다. binary와 dense는 공개 검증 통과율과 <code>hidden_auto_pass</code>를 올리지만 slot stuffing도 크게 늘린다. antistuff는 stuffing을 거의 제거하지만 기본 슬롯 붕괴를 만든다. antistuff2는 두 아티팩트를 함께 낮춘다.</figcaption>
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
          <td>suffix_concentration</td>
          <td class="align-right"><code>0.268</code></td>
          <td class="align-right"><code>0.344</code></td>
          <td class="align-right"><code>0.390</code></td>
          <td class="align-right"><code>0.417</code></td>
          <td class="align-right"><code>0.308</code></td>
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
  <figcaption><strong>Table 3.</strong> 종점의 핵심 평가 신호다. 비율 행은 카드 단위이며, <code>NLL_ctx median</code>은 카드 단위 중앙값이다. judge 기반 행은 무작위 400카드 judge 표본에서 계산했다.</figcaption>
</figure>

binary와 dense는 공개 검증 통과율만 올리지 않는다. `hidden_auto_pass`도 함께 올라가고, `judge_fail_given_public_pass`는 DPO `0.284`에서 binary `0.230`, dense `0.191`로 낮아졌다. NLL_ctx 중앙값도 큰 악화를 보이지 않는다. 반면 slot stuffing은 DPO 대비 약 3배로 늘어난다. 이 아티팩트는 judge_ctx_mean이 함께 상승하는 조건에서도 생겼기 때문에, judge가 자연성이나 문맥 적합도만으로 쉽게 잡는 실패는 아니다.

최적화 진단도 같은 방향이다. 학습 step 810에서 `corr(reward, judge_ctx)`는 binary `-0.016`, dense `-0.071`, antistuff `-0.086`, antistuff2 `+0.047`이었다. `corr(reward, NLL_ctx)`도 `-0.086`에서 `-0.108` 사이에 머문다. 형식 보상은 내용 품질 프록시와 거의 무상관이며, 학습 로그 기준 DPO 기준점 대비 KL도 종점에서 `1.077-1.182` 범위에 있어 급격한 분포 이동 신호로 보기는 어렵다.

### 판정 기준과 통계적 신호

강한 검증기 과최적화라면 공개 검증 통과율 상승과 보조 신호 악화가 함께 나타나야 한다. 이 조건에서는 공개 검증 통과율과 `hidden_auto_pass`가 함께 상승하고, 검증기-judge gap의 모델 간 변화도 유의하지 않았다.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>모델</th>
          <th class="align-right">public_pass 95% CI</th>
          <th class="align-right">slot_stuffing 95% CI</th>
          <th class="align-right">hidden_auto 95% CI</th>
          <th class="align-right">McNemar</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>DPO</td>
          <td class="align-right"><code>0.389 [0.377, 0.402]</code></td>
          <td class="align-right"><code>0.218 [0.207, 0.229]</code></td>
          <td class="align-right"><code>0.278 [0.232, 0.323]</code></td>
          <td class="align-right"><code>p&lt;0.001</code></td>
        </tr>
        <tr>
          <td>binary</td>
          <td class="align-right"><code>0.587 [0.575, 0.599]</code></td>
          <td class="align-right"><code>0.640 [0.628, 0.653]</code></td>
          <td class="align-right"><code>0.460 [0.412, 0.510]</code></td>
          <td class="align-right"><code>p&lt;0.001</code></td>
        </tr>
        <tr>
          <td>dense</td>
          <td class="align-right"><code>0.669 [0.657, 0.680]</code></td>
          <td class="align-right"><code>0.668 [0.656, 0.681]</code></td>
          <td class="align-right"><code>0.517 [0.468, 0.568]</code></td>
          <td class="align-right"><code>p&lt;0.001</code></td>
        </tr>
        <tr>
          <td>antistuff</td>
          <td class="align-right"><code>0.694 [0.682, 0.705]</code></td>
          <td class="align-right"><code>0.016 [0.012, 0.019]</code></td>
          <td class="align-right"><code>0.580 [0.532, 0.627]</code></td>
          <td class="align-right"><code>p&lt;0.001</code></td>
        </tr>
        <tr>
          <td>antistuff2</td>
          <td class="align-right"><code>0.647 [0.635, 0.659]</code></td>
          <td class="align-right"><code>0.141 [0.132, 0.150]</code></td>
          <td class="align-right"><code>0.535 [0.486, 0.584]</code></td>
          <td class="align-right"><code>p&lt;0.001</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> 주요 비율의 불확실성이다. 공개 검증 통과율과 slot stuffing의 CI는 전체 카드 집합 bootstrap, <code>hidden_auto</code>는 judge 400카드 표본의 이항 CI다. McNemar는 같은 judge 표본 안에서 공개 검증 통과와 hidden pass를 짝지어 비교한다.</figcaption>
</figure>

DPO에서 binary/dense로 가며 public_pass, hidden_auto_pass, slot_stuffing이 오른 변화는 95% CI가 서로 겹치지 않을 정도로 크다. 반대로 antistuff의 slot_stuffing은 다른 조건과 완전히 분리되어 완화 효과가 크다. 각 모델 내부에서 public_pass가 hidden_auto_pass보다 높은 것은 McNemar 기준으로 유의하지만, 이 내부 gap 자체는 예상된 결과다. 강한 과최적화 신호가 되려면 모델 간 gap 변화가 커져야 하며, 그 변화는 아래 표에서 유의하지 않다.

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
  <figcaption><strong>Table 5.</strong> 모델 간 검증기-judge gap 변화의 bootstrap CI다. 모든 구간이 0을 포함하므로, 이 평가에서는 gap 변화가 보상 변형 간 결론을 밀어주는 신호가 아니다.</figcaption>
</figure>

여섯 판정 기준 중 충족된 것은 구조 휴리스틱 상승, 특히 slot stuffing 하나다. `hidden_auto_pass`는 정체나 하락이 아니라 public_pass와 함께 상승한다. 모델 간 public_judge_gap 변화는 유의하지 않다. 공개 검증 통과 후 judge 실패율은 상승하지 않고 오히려 낮아진다. NLL_ctx도 평탄하다. 보상과 품질 프록시의 상관도 학습 후반에 악화되는 패턴을 보이지 않는다. 그래서 현재 자동 신호는 강한 reward hacking보다 형식 회복과 구조 아티팩트의 공존에 가깝다.

### 검증기 신호 변화

학습 step별 곡선에서도 같은 패턴이 반복된다. binary와 dense 모두 공개 검증 통과율과 `hidden_auto_pass`가 올라가지만, slot stuffing 역시 학습 초반부터 빠르게 상승한다. dense는 binary보다 종점의 공개 검증 통과율이 높지만, stuffing도 거의 같은 높은 구간으로 수렴한다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/overoptimization-curves.svg" alt="binary와 dense GRPO에서 step별 공개 검증 통과율, hidden_auto_pass, slot_stuffing_rate가 함께 변하는 선 그래프">
  <figcaption><strong>Figure 4.</strong> binary와 dense의 검증기 신호 변화다. 두 보상 모두 공개 검증 통과율과 <code>hidden_auto_pass</code>를 올리지만, slot stuffing도 함께 늘어난다. dense 보상은 더 높은 통과율 구간을 만들지만 구조적 실패 양식 자체를 제거하지는 못한다.</figcaption>
</figure>

### 구조 신호 범위와 완화

slot stuffing이 유일한 구조 신호는 아니지만 가장 지배적인 변화다. template duplication은 떨어지고 distinct-2는 오른다. slot-context conflict와 copy/unicode 신호는 거의 0으로 유지된다. suffix concentration은 모든 변형에서 상승하지만 antistuff2에서 가장 낮게 유지된다. 이 패턴은 파서 공략이나 템플릿 붕괴보다, 검증기가 허용하는 구조 안에서 특정 슬롯·어미 패턴이 과사용되는 문제에 가깝다.

카드 단위 점검에서도 stuffing은 유용한 정보 추가보다 채우기 아티팩트에 가깝다. 모든 종점 카드를 합치면 slot 수와 `NLL_ctx`의 Spearman 상관은 약 `-0.008`이고, stuffed/non-stuffed의 NLL 평균도 `2.635` 대 `2.643`으로 거의 구분되지 않는다. judge_ctx 평균은 stuffed 카드 `1.697`, non-stuffed 카드 `1.724`로 오히려 약간 낮다. 추가 슬롯 토큰이 측정 가능한 품질 이득을 주었다고 보기는 어렵다.

완화 실험도 slot stuffing을 유용한 정보 추가보다 아티팩트에 가깝게 보는 근거다. `antistuff`는 stuffing을 `0.668 -> 0.016` 수준으로 낮추면서도 공개 검증 통과율을 `0.694`까지 올렸다. hidden_auto_pass도 `0.580`으로 가장 높았다. 이 설정에서 과도한 슬롯 토큰은 높은 공개 검증 통과율에 필요하지 않았다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/mitigation-shift.svg" alt="dense, antistuff, antistuff2에서 slot stuffing, 기본 슬롯 비율, 공개 검증 통과율을 비교한 막대 그래프">
  <figcaption><strong>Figure 5.</strong> 완화와 아티팩트 자리 이동이다. antistuff는 stuffing을 거의 제거하지만 기본 슬롯 붕괴를 만든다. antistuff2는 이동한 아티팩트까지 함께 제약하면서 stuffing과 기본 슬롯 비율을 낮게 유지한다.</figcaption>
</figure>

아티팩트는 완전히 사라지기보다 이동했다. stuffing이 막히자 정책은 `season=전체 ∧ time=전체` 같은 일반 슬롯 조합으로 붕괴했고, default_slot_rate가 `0.056 -> 0.345`로 올랐다. `antistuff2`는 이 조합을 추가로 페널티해 default_slot_rate를 `0.068`로 되돌렸다. slot stuffing은 `0.141`로 dense 대비 낮게 유지됐고, 공개 검증 통과율 비용은 약 2포인트였다.

### 강건성: 시드, 기준값, 카드 가중, 생성 반복

두 핵심 변형은 두 번째 학습 시드에서도 종점을 확인했다. binary의 slot stuffing은 seed 42에서 `0.640`, seed 43에서 `0.696`이었다. 둘 다 DPO 기준점 `0.218`보다 크게 높다. antistuff의 slot stuffing은 seed 42에서 `0.016`, seed 43에서 `0.023`이었다. binary에서 stuffing이 생기고 antistuff에서 stuffing이 제거되는 현상은 두 시드 범위에서는 유지된다.

slot stuffing 기준값도 결론을 바꾸지 않았다. 슬롯 토큰 기준을 `>3`, `>4`, `>5`로 바꿔도 binary/dense는 DPO보다 높고 antistuff/antistuff2는 낮다. 카드 단위 집계 대신 입력 단위 평균을 써도 public_pass와 stuffing 변화는 약 `0.01` 이하로만 움직였다.

생성 반복도 종점 결론을 바꾸지 않았다. step-810 체크포인트를 고정하고 다섯 생성 시드로 다시 뽑았을 때 모든 구조 휴리스틱의 시드별 표준편차는 최대 `0.0075`였다.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>변형</th>
          <th class="align-right">public_pass</th>
          <th class="align-right">slot_stuffing</th>
          <th class="align-right">default_slot</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>binary</td>
          <td class="align-right"><code>0.598 +/- 0.007</code></td>
          <td class="align-right"><code>0.647 +/- 0.008</code></td>
          <td class="align-right"><code>0.061 +/- 0.002</code></td>
        </tr>
        <tr>
          <td>dense</td>
          <td class="align-right"><code>0.666 +/- 0.007</code></td>
          <td class="align-right"><code>0.663 +/- 0.005</code></td>
          <td class="align-right"><code>0.060 +/- 0.002</code></td>
        </tr>
        <tr>
          <td>antistuff</td>
          <td class="align-right"><code>0.684 +/- 0.004</code></td>
          <td class="align-right"><code>0.016 +/- 0.001</code></td>
          <td class="align-right"><code>0.354 +/- 0.004</code></td>
        </tr>
        <tr>
          <td>antistuff2</td>
          <td class="align-right"><code>0.649 +/- 0.007</code></td>
          <td class="align-right"><code>0.138 +/- 0.006</code></td>
          <td class="align-right"><code>0.067 +/- 0.001</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 6.</strong> 다섯 생성 시드의 step-810 평균과 표준편차다. 생성 반복에 따른 분산은 핵심 효과에 비해 작다.</figcaption>
</figure>

### judge 부분표본 편향

judge 표본은 결론에 직접 영향을 줄 수 있다. 각 체크포인트의 앞쪽 400카드를 연속으로 뽑으면 public_judge_gap이 학습과 함께 감소하는 것처럼 보인다. 같은 체크포인트에서 무작위 400카드를 뽑으면 gap은 평탄하거나 소폭 상승한다. 체크포인트 내부 카드 순서가 입력 순서를 따르기 때문에, 앞쪽 연속 표본은 특정 입력 하위집단을 과표집한다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/sampling-bias-gap.svg" alt="앞쪽 400카드와 무작위 400카드 judge 표본에서 binary와 dense의 public_judge_gap 추세가 달라지는 선 그래프">
  <figcaption><strong>Figure 6.</strong> judge 부분표본 방식에 따른 public_judge_gap 변화다. 앞쪽 400카드는 gap이 감소하는 것처럼 보이지만, 무작위 400카드는 평탄하거나 소폭 상승한다. judge 부분표본은 무작위로 뽑고 그 방식을 함께 보고해야 한다.</figcaption>
</figure>

이 결과는 `hidden_auto_pass` 자체보다 방법론에 가깝다. judge가 약한 신호인 데다 표본 선택에도 민감하므로, judge 기반 결론은 구조 휴리스틱을 보조하는 수준에 머물러야 한다.

### constrained decoding 비교

추론 시점 constrained decoding은 형식 아티팩트의 대체 해법처럼 보일 수 있다. DPO 기준 정책에 JSON-schema 기반 제약을 걸면 파싱 가능한 카드와 slot cap은 강제할 수 있다. 그러나 한국어 어미 규칙과 문구 자연성까지 해결하지는 못했다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/constrained-decoding.svg" alt="DPO unconstrained, constrained decoding, RL antistuff의 public pass, slot stuffing, length boundary, hidden_auto_pass 비교 도표">
  <figcaption><strong>Figure 7.</strong> DPO 기준 정책 위의 constrained decoding과 학습 기반 보정 비교다. array cap은 slot stuffing을 0으로 만들지만 public_pass는 0.44에 머물고 length_boundary가 늘어난다. RL antistuff는 public_pass와 hidden_auto_pass를 더 크게 회복한다.</figcaption>
</figure>

constrained decoding은 모든 출력을 파싱 가능하게 만들지만 public_pass를 `0.389 -> 0.403-0.440` 정도로만 올린다. `+array-cap`은 slot_stuffing을 `0.000`으로 낮추지만 length_boundary_rate를 `0.202 -> 0.394`로 키우고 hidden_auto_pass는 `0.265`로 낮아진다. 반면 학습 기반 antistuff는 slot_stuffing을 `0.015`로 낮추면서 public_pass `0.694`, hidden_auto_pass `0.580`에 도달한다. 문법 제약은 특정 구조 지표를 0으로 만들 수 있지만, 형식 규칙 전체와 내용 품질을 함께 회복하는 대체재는 아니었다.

### 실패 유형과 정성 예시

GRPO-binary 내부 실패 분류에서는 길이 위반 감소가 가장 크게 보인다. `LEN_EXCEEDED`는 step 50의 `0.539`에서 step 810의 `0.225`로 줄었다. 반면 `BAD_SUFFIX`는 `0.291 -> 0.275`로 큰 변화 없이 남았다. `INVALID_CATEGORY`는 거의 0이다. 이 패턴은 stuffing이 잘못된 카테고리 선택보다 유효 슬롯 값을 과도하게 나열하는 문제에 가깝다는 해석을 뒷받침한다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/failure-taxonomy.svg" alt="GRPO-binary step별 LEN_EXCEEDED, BAD_SUFFIX, INVALID_CATEGORY 문제 비율 변화 선 그래프">
  <figcaption><strong>Figure 8.</strong> GRPO-binary의 실패 분류 변화다. 길이 위반은 감소하지만 BAD_SUFFIX는 남고, 카테고리 위반은 거의 0이다. stuffing은 잘못된 카테고리 선택보다 유효 슬롯 과다 나열에 가깝다.</figcaption>
</figure>

같은 입력의 정성 예시도 이 해석과 맞는다. 헤어스타일링 제품 입력에서 dense는 `time=[아침, 저녁, 밤]`, `place=[집, 미용실]`처럼 유효 슬롯을 과다 나열했다. antistuff는 `season=전체`, `time=전체`, `place=전체`에 가까운 일반 조합으로 이동했다. antistuff2는 `time=아침`, `place=헤어샵`처럼 더 구체적인 슬롯으로 돌아왔다. 이 예시는 결론의 주된 근거가 아니라, 정량 지표가 가리키는 이동 양상을 보여주는 샘플이다.

## 해석

현 설정에서 DPO 이후 GRPO 형식 보정은 자동 신호 기준으로 강한 검증기 과최적화보다 형식 회복에 더 가깝다. public_pass와 `hidden_auto_pass`가 함께 상승하고, 모델 간 public_judge_gap 변화는 유의하지 않으며, NLL_ctx도 큰 악화를 보이지 않는다. 사전 정의한 여섯 기준 중 하나만 충족되므로 강한 reward hacking이라고 부르기는 어렵다.

그렇다고 구조적 아티팩트가 없다는 뜻은 아니다. binary와 dense 모두 slot stuffing을 크게 만든다. 이 아티팩트는 공개 검증기를 통과하고 고정 judge도 거의 페널티하지 못한다. LLM judge 단독으로는 구조화 UI 생성의 좁은 실패를 놓칠 수 있다.

완화도 단일 지표만 보고 설계하기 어렵다. slot stuffing만 누르면 기본 슬롯 붕괴가 생긴다. 이동한 아티팩트를 다시 점검하고 결합 페널티로 막았을 때에야 stuffing과 기본 슬롯 비율을 함께 낮출 수 있었다. constrained decoding 역시 같은 교훈을 준다. 특정 구조 지표를 0으로 만들 수는 있지만, 다른 형식·품질 비용을 가릴 수 있다.

## 한계

- 운영 품질을 직접 판정한 사람 평가 정답셋은 없다. judge 검증에는 별도 인간 검토 라벨 500건을 사용했지만, `hidden_auto_pass`는 고정 LLM judge 기반 보조 신호이며 사람 판단이나 운영 품질 전체를 뜻하지 않는다.
- judge와 인간 라벨의 일치도가 낮다. tpo ctx QWK는 `0.059`, tpo nat QWK는 `0.143`이라서 judge 기반 값은 보조 신호로만 사용한다.
- judge는 무작위 400카드 표본에서만 계산했다. 표본 선택이 gap 추세를 바꿀 수 있음을 별도 분석으로 확인했으므로, judge 부분표본 방식은 결과 해석의 일부다.
- 곡선은 대부분 단일 학습 시드다. 두 핵심 변형은 seed 43으로 반복했고, 종점 생성은 다섯 시드로 재생성했지만, 모든 변형의 다중 학습 시드 평균은 아니다.
- slot stuffing 기준값, anti-stuffing cap, penalty weight, judge pass threshold는 수작업 설정이다. 인접 기준값에서 순서는 유지됐지만 절대 비율을 표준값처럼 해석해서는 안 된다.
- constrained decoding 비교는 DPO 기준 정책 위의 단일 조건 비교다. 더 강한 파서, 더 좁은 문법, reranking과의 조합은 별도 비교가 필요하다.
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
8. <span id="ref-constrained-decoding"></span>Brandon T. Willard and Rémi Louf. [Efficient Guided Generation for Large Language Models](https://arxiv.org/abs/2307.09702). 2023.
9. <span id="ref-cd-json"></span>Saibo Geng et al. [Grammar-Constrained Decoding for Structured NLP Tasks without Finetuning](https://arxiv.org/abs/2305.13971). 2023.
10. <span id="ref-goodhart"></span>David Manheim and Scott Garrabrant. [Categorizing Variants of Goodhart's Law](https://arxiv.org/abs/1803.04585). 2018.

</div>

## Citation

Text citation:

```text
Ahn, I. (2026). 한국어 UI 문구 생성에서 GRPO 형식 보정의 구조 아티팩트 분석. Technical report.
```

BibTeX:

```bibtex
@techreport{ahn2026grpoValidatorArtifactEvaluation,
  title = {한국어 UI 문구 생성에서 GRPO 형식 보정의 구조 아티팩트 분석},
  author = {Ahn, Ilho},
  year = {2026},
  type = {Technical report},
  url = {/technical-reports/korean-ui-grpo-validator-artifact-evaluation/}
}
```
