---
title: "한국어 UI 문구 생성에서 GRPO 형식 보정의 구조 아티팩트 분석"
layout: post
date: 2026-06-08 09:00:00 +0900
last_modified_at: 2026-06-17 09:00:00 +0900
categories: ["LLM ALIGNMENT"]
tags: [korean-ui-copy, structured-generation, grpo, dpo, reward-hacking, llm-judge, format-validation, automatic-evaluation]
excerpt: "한국어 구조화 UI 문구 생성에서 DPO 이후 GRPO 형식 보정이 형식 회복인지, 검증기 과최적화인지 공개 검증기·구조 휴리스틱·LLM judge 신호로 나눠 평가한다."
description: "한국어 UI 문구 생성에서 DPO 이후 GRPO 형식 보정이 공개 검증기 통과율, 구조 휴리스틱, judge 표본 선택, 생성 시드, constrained decoding에 미치는 영향을 분리해 분석한다."
permalink: /technical-reports/korean-ui-grpo-validator-artifact-evaluation/
image: /assets/images/common/editorial-hero-social.png
image_alt: "한국어 UI 문구 생성의 GRPO 형식 보정 구조 아티팩트 분석을 나타내는 소셜 썸네일"
hero_image: /assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/hero.svg
hero_alt: "Minimal summary cards comparing partial format recovery, slot stuffing, anti-stuffing mitigation, and signal separation"
hero_caption: "<strong>Figure 1.</strong> DPO 이후 GRPO 형식 보정의 요약 도식이다. 공개 검증 통과율 회복, slot stuffing 증가, anti-stuffing 완화, 품질 프록시와 구조 부산물의 분리를 함께 보여준다."
hero_frame: true
hero_variant: rounded-wide
hidden: true
publication_status: "technical-report"
report_scope: "technical report"
lab_path: "experiment-lab/projects/ui-grade-copy-generation-reward-analysis"
---

[구조화된 한국어 UI 문구 생성에서 NLL 프록시와 정렬 학습](/technical-reports/korean-ui-nll-proxy-alignment/)은 DPO가 한국어 추천 카드 문구의 NLL 기반 품질 프록시를 개선하는 동시에, 메타 슬롯 확장 카드의 형식 통과율을 낮추고 이후 GRPO 형식 보정으로 이를 일부 회복하는 현상을 다뤘다. 이번 글은 그 후속 분석이다. 질문은 GRPO의 형식 회복이 품질 프록시를 유지한 보완인지, 아니면 공개 검증기 기준을 좁게 공략한 결과인지다.

실험은 원글의 공유 테스트셋과 평가 절차를 유지해 SFT, DPO, GRPO 변형을 비교한다. 형식 통과율은 SFT `0.724`에서 DPO `0.389`로 떨어지고, GRPO는 보상 변형에 따라 이를 `0.587-0.694` 범위로 회복한다. `0.694`는 이번 글에서 추가한 완화 보상 변형의 결과다. 동시에 DPO가 얻은 `NLL_ctx` 개선은 대체로 유지된다.

사람 평가 정답셋 없이 자동 계산 지표만 놓고 보면, GRPO 형식 보정은 강한 검증기 과최적화보다 형식 회복에 더 가깝다. 다만 회복 과정은 깨끗하지 않다. GRPO는 LLM judge가 거의 페널티하지 못하는 slot stuffing을 함께 만들며, 이 구조 아티팩트는 별도 휴리스틱으로 봐야 드러난다.

이 글은 운영 품질을 직접 판정한 사람 평가 정답셋 없이 세 종류의 신호를 분리한다. 공개 검증기는 보상이 직접 보는 형식 검사기다. 구조 휴리스틱은 보상이 보지 않는 좁은 실패를 잡기 위한 결정론적 신호다. 고정 LLM judge는 자연성과 문맥 적합도를 보는 보조 신호지만, 별도 인간 검토 라벨과의 일치도가 낮기 때문에 결론의 1차 근거로 쓰지 않는다.

## 요약

- GRPO 형식 보정은 DPO 이후 낮아진 공개 검증 통과율을 회복했고, DPO가 얻은 `NLL_ctx` 개선도 대체로 유지했다. 형식 회복과 NLL 기반 문맥 프록시가 반드시 trade-off로 움직인 것은 아니다.
- 자동 계산 지표만 보면 강한 검증기 과최적화라고 보기는 어렵다. `public_pass`와 `hidden_auto_pass`가 함께 오르고, 공개 검증기와 judge 사이의 차이도 모델 간에 크게 벌어지지 않았다.
- 더 중요한 문제는 품질 프록시와 구조 부산물이 분리된다는 점이다. 단순 형식 보상 변형은 `slot_stuffing`을 크게 늘리지만, LLM judge와 `NLL_ctx`는 이 변화를 충분히 페널티하지 못한다.
- anti-stuffing 페널티는 `slot_stuffing`을 줄였지만, 출력이 기본 슬롯 조합으로 이동하는 새 부산물을 만들었다. 결합 페널티를 넣었을 때에야 stuffing과 기본 슬롯 비율이 함께 낮아졌다.
- judge 기반 결론은 표본 설계에 민감했다. 앞쪽 400카드를 쓰면 공개 검증기와 judge 사이의 차이가 줄어드는 것처럼 보였지만, 무작위 400카드에서는 그 패턴이 약했다.
- constrained decoding은 특정 구조 문제를 직접 막을 수 있지만, 전체 형식 회복이나 문구 품질을 대체하지는 못했다. 구조화 생성에서는 학습 보상, 결정론적 휴리스틱, judge 표본 설계를 분리해 봐야 한다.

## 관련 연구

이 글은 새 정렬 알고리즘을 제안하기보다, 선호 정렬과 형식 보상을 순차적으로 쓸 때 생기는 평가 문제를 다룬다. RLHF 계열 연구는 사람 피드백으로 언어 모델을 정렬할 수 있음을 보였고 <a class="citation-ref" href="#ref-instructgpt">[2]</a>, DPO는 명시적 reward model 없이 선호쌍으로 정책을 직접 조정하는 방법을 제시했다 <a class="citation-ref" href="#ref-dpo">[3]</a>. GRPO는 group-relative policy optimization 계열 방법으로 제안됐고 <a class="citation-ref" href="#ref-grpo">[4]</a>, 이 글에서는 DPO 이후 별도 형식 신호를 보완하는 실험 설정으로 사용한다. 따라서 초점은 알고리즘 성능 비교가 아니라, 품질 프록시와 형식 신호가 분리되어 움직이는지에 있다.

검증기나 reward를 직접 최적화할 때 생기는 Goodhart/reward hacking 문제는 오래된 평가 위험이다 <a class="citation-ref" href="#ref-goodhart">[5]</a>. Concrete Problems in AI Safety는 잘못 지정된 보상과 reward hacking을 안전 문제의 한 축으로 정리했고 <a class="citation-ref" href="#ref-specification-gaming">[7]</a>, reward hacking/gaming의 정의와 유형화도 별도 연구로 정리됐다 <a class="citation-ref" href="#ref-reward-gaming">[8]</a>. reward model overoptimization 연구는 reward가 좋아져도 실제 선호 품질이 같이 좋아진다고 단정할 수 없음을 보였다 <a class="citation-ref" href="#ref-overoptimization">[6]</a>. 이 글은 이런 일반론을 구조화 UI 출력의 좁은 validator artifact로 옮겨, `slot_stuffing`이 실제 품질 프록시와 어떻게 분리되는지 확인한다.

LLM judge와 AI feedback은 사람 평가 비용을 낮추지만, 그 자체가 평가 기준이 될 때는 별도 검증이 필요하다. Constitutional AI/RLAIF는 모델 기반 피드백을 학습 신호로 활용하는 방향을 보였고 <a class="citation-ref" href="#ref-constitutional-ai">[9]</a>, MT-Bench/Chatbot Arena는 LLM-as-a-judge 평가의 유용성과 한계를 함께 다뤘다 <a class="citation-ref" href="#ref-llm-judge">[10]</a>. 이 글에서는 judge를 결론의 1차 근거가 아니라, 공개 검증기와 구조 휴리스틱을 보조하는 표본 기반 신호로 제한한다. 특히 judge 표본을 어떻게 뽑는지가 gap 추세를 바꿀 수 있음을 별도로 확인한다.

구조화 출력에서는 학습 보상 외에 constrained decoding도 자연스러운 대안이다. 문법 기반 또는 guided generation 방식은 출력이 주어진 문법이나 schema를 따르도록 강제할 수 있다 <a class="citation-ref" href="#ref-constrained-decoding">[11]</a>, <a class="citation-ref" href="#ref-cd-json">[12]</a>. 다만 이 글의 비교에서는 schema 제약이 slot cap 같은 일부 구조 문제는 줄였지만, 한국어 어미 규칙과 문구 품질까지 함께 회복하지는 못했다. 따라서 constrained decoding은 학습 기반 형식 보정의 대체재라기보다, 어떤 구조 실패를 문법으로 직접 막을 수 있는지 보는 보조 비교로 사용한다.

## 문제 설정

평가 대상은 한국어 추천 카드 문구다. 출력은 `reason`, `title`, `subtitle` 같은 짧은 문구 필드와 `season`, `time`, `place` 같은 메타 슬롯을 포함한다. 메타 슬롯 확장 카드는 일반 자유 생성보다 실패 조건이 좁다. 문장이 자연스러워도 길이, 어미, 슬롯 범주, 빈 값 제약을 어기면 UI에 배치하기 어렵다.

공개 검증기 `V_public`은 GRPO 보상 계산에 직접 쓰는 형식 검사기다. 필드 존재, 길이 상한, 허용 어미, `season`/`time` 카테고리, 비어 있지 않은 `place` 등을 검사한다. 문제는 보상이 이 검증기만 직접 본다는 점이다. 통과율이 올랐다는 사실만으로는 구조가 실제로 좋아졌는지, 검증기가 허용하는 좁은 실패 패턴으로 이동했는지 구분할 수 없다.

본문의 표기는 평가 신호에서 바로 온다. `public_pass`는 공개 검증기 통과율, `hidden_auto_pass`는 공개 검증 통과와 judge 기준을 함께 만족한 비율, `NLL_ctx`는 참조 LM의 NLL로 본 문맥 프록시다. slot stuffing과 기본 슬롯 조합은 결과 섹션에서 구조 아티팩트로 따로 다룬다.

<figure class="table-figure table-figure--comparison">
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
          <td>참조 LM 기준 조건부 NLL</td>
          <td>품질 전체가 아니라 보조 신호</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> 평가에서 분리한 신호다. 공개 검증기는 보상이 직접 보는 신호이고, 구조 휴리스틱은 그 바깥의 구조적 사각지대를 확인하기 위한 신호다.</figcaption>
</figure>

judge 검증 결과는 이 신호의 해석 범위를 제한한다. 500건의 인간 검토 라벨과 비교했을 때 Gemini-2.5-flash의 `tpo/ctx` QWK는 `0.059`, `tpo/nat` QWK는 `0.143`이었다. judge와 사람이 정확히 같은 점수를 준 비율은 약 `0.53-0.56`, 1점 이내 일치율은 약 `0.94-0.95`였지만, 0/1/2 척도에서 순위 정합성은 약했다. 이 때문에 judge 기반 값은 보조 신호로만 읽는다.

## 평가 설계

GRPO는 DPO 정책에서 시작한다. 비교한 보상 변형은 네 가지다.

<figure class="table-figure table-figure--comparison">
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
          <td>SFT</td>
          <td>선호쌍 DPO</td>
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
          <td>파싱, 필드 존재, 길이, 어미, 슬롯 유효성, 빈 슬롯 여부를 나눠 부분 점수화</td>
          <td>완전 통과/실패 대신 형식 구성요소별로 보상</td>
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
  <figcaption><strong>Table 2.</strong> 비교한 기준점과 GRPO 보상 변형이다. <code>dense</code>는 공개 검증기의 하위 조건을 부분 점수로 나눠 주는 보상이고, <code>antistuff2</code>는 첫 완화가 만든 기본 슬롯 붕괴를 막기 위한 결합 완화다.</figcaption>
</figure>

`antistuff`의 슬롯 기준값 3은 `place`, `time`, `season` 각각에 하나씩을 강제한다는 뜻이 아니다. 세 필드 전체의 슬롯 값 개수가 3개까지면 페널티를 주지 않고, 3개를 넘는 값부터 slot stuffing으로 보고 초과분에 페널티를 준다는 뜻이다. `0.25`는 초과 슬롯 하나당 빼는 감점 계수다. `dense` 보상이 대체로 `0.0-1.0` 범위이므로, 초과 슬롯이 4개만 되어도 최대 형식 보상에 해당하는 `1.0`이 사라진다. `antistuff2`의 `0.40`은 첫 완화 뒤에 관찰된 `season=전체 ∧ time=전체` 쏠림을 다시 막기 위한 후속 페널티다. 따라서 이 값들은 최적화된 상수가 아니라, “탐지한 구조 부산물을 보상으로 강하게 눌렀을 때 실제로 줄어드는지와 어떤 부산물 이동이 생기는가”를 보기 위한 감사용 설정으로 해석해야 한다.

평가는 학습에 쓰지 않은 1,026개 입력에서 진행했다. 체크포인트마다 학습 시 샘플링 조건에 맞춰 입력당 K=4개 생성을 샘플링했고, 한 생성이 여러 카드를 낼 수 있으므로 전체 채점 단위는 약 5.5-6천 카드다. 공개 검증기와 구조 휴리스틱은 전체 카드 집합에서 계산했다. LLM judge는 체크포인트마다 고정 시드로 뽑은 400카드 표본에만 적용했다.

과최적화 판정은 여섯 기준으로 정리했다. 공개 검증 통과율이 오르는데 hidden_auto_pass가 정체/하락하는지, 검증기-judge gap이 DPO 대비 커지는지, 공개 검증 통과 후 judge 실패율이 오르는지, NLL_ctx가 악화되는지, 구조 휴리스틱이 상승하는지, 보상과 품질 프록시의 상관이 학습 후반에 악화되는지를 본다. 이 중 둘 이상이 같은 방향으로 나타날 때 강한 검증기 과최적화 증거로 읽는다.

## 결과

### 공유 테스트셋 기준 SFT-DPO-GRPO

이 비교는 원글의 공유 테스트셋과 평가 절차를 그대로 따른다. DPO는 public_pass를 `0.724 -> 0.389`로 떨어뜨리지만 NLL_ctx는 `3.152 -> 2.641`로 낮춘다. 이후 GRPO는 NLL_ctx 개선을 유지한 채 public_pass를 `0.587-0.694` 범위로 회복한다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/lineage-recheck.svg" alt="Shared-test comparison of public pass, hidden auto pass, and slot stuffing across SFT, DPO, and GRPO variants">
  <figcaption><strong>Figure 2.</strong> 공유 테스트셋에서 SFT, DPO, GRPO 변형을 다시 비교한 결과다. DPO는 <code>NLL_ctx</code>를 낮추지만 형식 통과율을 떨어뜨리고, GRPO는 형식 통과율을 회복하는 동시에 형식 보상 조건에서 slot stuffing을 키운다.</figcaption>
</figure>

이 결과는 원글의 형식 회복 관찰을 reward 변형과 구조 신호까지 확장한다는 점에서 중요하다. 같은 평가 절차 안에서도 DPO의 형식 퇴행과 GRPO의 형식 회복이 유지된다. 동시에 slot stuffing은 SFT `0.191`, DPO `0.218`에서 낮다가 GRPO-binary `0.640`, GRPO-dense `0.668`로 상승한다. 아티팩트는 기반 정책에 이미 있던 잔여 문제가 아니라 GRPO 형식 보정 단계에서 커진다.

### 형식 신호와 구조 신호의 분리

이 섹션의 `public_judge_gap`은 같은 judge 표본에서 계산한 `public_pass - hidden_auto_pass`다. `default_slot_rate`는 기본 슬롯 조합으로 몰리는 비율이고, `suffix_concentration`은 특정 어미·접미 패턴이 과도하게 반복되는 정도다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/endpoint-evaluation-matrix.svg" alt="Endpoint trade-off map comparing public pass against slot stuffing and default slot rate">
  <figcaption><strong>Figure 3.</strong> 최종 체크포인트에서 <code>public_pass</code>와 구조 부산물의 관계를 나눠 본 그림이다. 왼쪽은 slot stuffing, 오른쪽은 기본 슬롯 비율과의 관계를 보여준다. binary와 dense는 형식 통과율을 올리지만 stuffing도 키우고, antistuff는 stuffing을 낮추는 대신 기본 슬롯 조합으로 이동하며, antistuff2는 이동한 부산물을 다시 낮춘다.</figcaption>
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
          <td class="align-right"><code>0.016</code></td>
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
  <figcaption><strong>Table 3.</strong> 최종 체크포인트의 핵심 평가 신호다. 비율 행은 카드 단위이며, <code>NLL_ctx median</code>은 카드 단위 중앙값이다. judge 기반 행은 무작위 400카드 judge 표본에서 계산했다.</figcaption>
</figure>

binary와 dense에서는 공개 검증 통과율과 `hidden_auto_pass`가 함께 오른다. `judge_fail_given_public_pass`는 DPO `0.284`에서 binary `0.230`, dense `0.191`로 낮아졌고, NLL_ctx 중앙값도 큰 악화를 보이지 않는다. 반면 slot stuffing은 DPO 대비 약 3배로 늘어난다. slot stuffing이 늘어났지만 judge의 문맥 적합도 점수와 NLL_ctx 중앙값은 함께 나빠지지 않았다. 따라서 LLM judge나 NLL 기반 문맥 프록시만으로는 이런 구조적 부산물을 잡기 어렵다.

최적화 진단도 형식 보상과 내용 품질 프록시가 거의 분리되어 움직인다는 해석을 뒷받침한다. 학습 step 810에서 `corr(reward, judge_ctx)`는 binary `-0.016`, dense `-0.071`, antistuff `-0.086`, antistuff2 `+0.047`이었다. `corr(reward, NLL_ctx)`도 `-0.086`에서 `-0.108` 사이에 머문다. 형식 보상은 내용 품질 프록시와 거의 무상관이며, 학습 로그 기준 DPO 기준점 대비 KL도 최종 체크포인트에서 `1.077-1.182` 범위에 있어 급격한 분포 이동 신호로 보기는 어렵다.

### 판정 기준과 통계적 신호

강한 검증기 과최적화로 보려면 공개 검증 통과율 상승만으로는 부족하다. judge 기반 신호, NLL_ctx, 구조 휴리스틱 같은 검증기 바깥의 신호들이 함께 나빠지는지 봐야 한다. 이번 결과에서는 공개 검증 통과율만 오른 것이 아니라 `hidden_auto_pass`도 함께 올랐다. 또 공개 검증기는 통과했지만 judge 조건까지는 통과하지 못한 비율이 DPO보다 GRPO에서 뚜렷하게 커졌다고 보기 어려웠다.

<figure class="table-figure table-figure--comparison">
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

DPO에서 binary/dense로 가면 `public_pass`와 `hidden_auto_pass`가 함께 오른다. 동시에 `slot_stuffing`도 커지며, 이 변화는 95% CI가 DPO와 겹치지 않을 정도로 크다. 반대로 antistuff에서는 `slot_stuffing`이 다른 조건보다 뚜렷하게 낮아, anti-stuffing 페널티가 slot stuffing을 줄이는 데 효과가 있었다.

각 모델 안에서 `public_pass`가 `hidden_auto_pass`보다 높은 것은 예상된 결과다. `hidden_auto_pass`가 공개 검증 통과에 judge 조건을 추가한 더 엄격한 기준이기 때문이다. 따라서 이 내부 차이만으로는 과최적화 증거가 되지 않는다. 과최적화 신호가 되려면 이 차이가 DPO보다 GRPO에서 더 커져야 하지만, 아래 표에서는 그런 모델 간 gap 증가가 유의하게 나타나지 않았다.

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

여섯 판정 기준 중 과최적화 방향으로 뚜렷하게 움직인 것은 구조 휴리스틱, 특히 slot stuffing이었다. 반면 `hidden_auto_pass`는 정체하거나 하락하지 않고 `public_pass`와 함께 상승했다. 모델 간 `public_judge_gap` 변화도 유의하지 않았다. 공개 검증을 통과한 출력의 judge 실패율은 오르지 않았고, 오히려 낮아졌다. `NLL_ctx`도 큰 악화를 보이지 않았다. 보상과 품질 프록시의 상관 역시 학습 후반에 나빠지는 패턴을 보이지 않았다. 따라서 현재 자동 계산 지표는 강한 reward hacking보다 형식 회복과 구조 아티팩트가 함께 나타난 결과에 가깝다.

### 형식 회복과 slot stuffing의 동반 상승

학습 step별 곡선은 형식 회복과 구조 부산물이 함께 커지는 과정을 보여준다. binary와 dense 모두 학습이 진행되면서 공개 검증 통과율과 `hidden_auto_pass`가 올라간다. 그러나 같은 구간에서 `slot_stuffing`도 빠르게 증가한다. dense는 binary보다 최종 공개 검증 통과율이 높지만, `slot_stuffing`은 두 설정 모두 높은 수준으로 수렴한다. 따라서 dense 보상은 형식 통과율을 더 잘 끌어올렸지만, slot stuffing을 따로 억제하지는 못했다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/overoptimization-curves.svg" alt="Step-wise public pass, hidden auto pass, and slot stuffing curves for binary and dense GRPO">
  <figcaption><strong>Figure 4.</strong> binary와 dense GRPO의 학습 step별 검증기 신호다. 두 보상 모두 <code>public_pass</code>와 <code>hidden_auto_pass</code>를 올리지만, 같은 구간에서 slot stuffing도 상승한다. dense는 더 높은 통과율에 도달하지만 구조 실패를 제거하지는 못한다.</figcaption>
</figure>

### slot stuffing 중심의 구조 부산물과 완화 후 이동

출력 구조 문제는 전반적인 템플릿 붕괴가 아니라 slot stuffing과 특정 어미·접미 패턴 과사용에 집중됐다. 이 섹션의 구조 휴리스틱은 템플릿 반복, 다양성, 슬롯-맥락 충돌, 복사/문자 이상, 어미·접미 패턴 집중을 나눠 본 보조 지표다. slot stuffing은 이번 평가에서 가장 크게 움직인 변화였다. 반면 템플릿 반복은 감소했고 다양성 지표는 개선됐다. 슬롯-맥락 충돌과 복사/문자 이상도 거의 0으로 유지됐다. 특정 어미·접미 패턴의 집중은 모든 변형에서 상승했지만, antistuff2에서 가장 낮게 유지됐다. 따라서 이 실패는 파서 공략이나 템플릿 붕괴보다, 검증기가 허용하는 구조 안에서 특정 슬롯·어미 패턴이 과사용되는 문제에 가깝다.

카드 단위 점검에서도 stuffing을 유용한 정보 추가로 보기는 어려웠다. 모든 최종 체크포인트 카드를 합치면 slot 수와 `NLL_ctx`의 Spearman 상관은 약 `-0.008`로 거의 0이다. stuffed/non-stuffed의 NLL 평균도 `2.635` 대 `2.643`으로 거의 구분되지 않는다. `judge_ctx` 평균은 stuffed 카드 `1.697`, non-stuffed 카드 `1.724`로 stuffed 쪽이 오히려 약간 낮다. 따라서 추가 슬롯 토큰은 측정 가능한 품질 이득 없이 구조 복잡도만 늘린 채우기성 부산물에 가깝다.

완화 실험도 과도한 슬롯 토큰이 높은 점수에 필요한 구성요소는 아니었음을 보여준다. `antistuff`는 dense의 stuffing `0.668`을 `0.016`으로 낮췄지만, 공개 검증 통과율은 `0.694`로 비교 조건 중 가장 높았다. `hidden_auto_pass`도 `0.580`으로 가장 높았다. 따라서 과도한 슬롯 토큰은 높은 형식 통과율이나 보조 judge 통과에 필요한 정보라기보다, 보상 최적화 과정에서 생긴 채우기성 부산물에 가깝다.

다만 첫 완화가 모든 구조 문제를 없앤 것은 아니다. `antistuff`에서 stuffing이 줄어들자 출력은 `season=전체 ∧ time=전체` 같은 일반 슬롯 조합으로 이동했고, `default_slot_rate`는 dense `0.056`에서 antistuff `0.345`로 올랐다. `antistuff2`는 이 조합을 추가로 페널티해 `default_slot_rate`를 `0.068`로 낮췄다. 대신 `slot_stuffing`은 `0.141`로 antistuff보다 다시 올랐지만 dense `0.668`보다는 낮게 유지됐다. 공개 검증 통과율은 dense `0.669`에서 antistuff2 `0.647`로 약 2.2포인트 낮아졌다.

### 강건성: 시드, 기준값, 카드 가중, 생성 반복

핵심 효과는 확인한 범위의 변동에 민감하지 않았다. 두 번째 학습 시드에서도 binary의 slot stuffing은 DPO 기준점 `0.218`보다 높았고(`0.640`, `0.696`), antistuff는 낮게 유지됐다(`0.016`, `0.023`). 슬롯 토큰 기준을 `>3`, `>4`, `>5`로 바꾸거나 카드 단위 대신 입력 단위 평균을 써도 결론은 바뀌지 않았다.

생성 반복에 따른 분산도 작았다. step-810 체크포인트를 고정하고 다섯 생성 시드로 다시 뽑았을 때, 주요 구조 휴리스틱의 시드별 표준편차는 핵심 효과보다 훨씬 작았다.

<figure class="table-figure table-figure--comparison">
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

### judge 표본 선택에 민감한 gap 추세

judge 기반 gap 추세는 표본 선택에 민감했다. 각 체크포인트의 앞쪽 400카드를 연속으로 쓰면 `public_judge_gap`이 학습과 함께 감소하는 것처럼 보인다. 그러나 같은 체크포인트에서 무작위 400카드를 뽑으면 gap은 평탄하거나 소폭 상승한다. 체크포인트 내부 카드 순서가 입력 순서를 따르기 때문에, 앞쪽 연속 표본은 특정 입력 하위집단을 과표집한 것으로 보인다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/sampling-bias-gap.svg" alt="Public judge gap trends under first-400 and random-400 judge samples for binary and dense GRPO">
  <figcaption><strong>Figure 5.</strong> judge 부분표본에 따른 <code>public_judge_gap</code> 민감도다. 앞쪽 400카드를 쓰면 gap이 학습 중 줄어드는 것처럼 보이지만, 무작위 400카드 표본에서는 더 평탄하거나 약간 높아진다. judge 표본은 무작위화하고 보고해야 한다.</figcaption>
</figure>

따라서 이 결과는 `hidden_auto_pass` 값 자체보다 judge 표본 설계에 대한 경고로 읽어야 한다. judge는 인간 검토 라벨과의 순위 정합성이 약했고 표본 선택에도 민감했다. 이 글에서는 judge 기반 결론을 구조 휴리스틱을 보조하는 신호로만 사용한다.

### constrained decoding의 부분 완화 효과

constrained decoding은 학습을 바꾸지 않고 추론 시점에 JSON schema나 문법 제약으로 출력 구조를 제한하는 방법이다. 형식 아티팩트의 대체 해법처럼 보일 수 있지만, 이 비교에서는 구조 문제 일부만 직접 막았다. DPO 기준 정책에 JSON-schema 기반 제약을 걸면 파싱 가능한 카드와 slot cap은 강제할 수 있지만, 한국어 어미 규칙과 문구 자연성까지 회복하지는 못했다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/constrained-decoding.svg" alt="Constrained decoding comparison of public pass, slot stuffing, length boundary, and hidden auto pass">
  <figcaption><strong>Figure 6.</strong> DPO 정책 위에 constrained decoding을 적용한 결과와 학습 기반 보정을 비교한 그림이다. array cap은 slot stuffing을 0으로 낮추지만 <code>public_pass</code>는 0.44 수준에 머물고 length boundary 문제가 커진다. RL antistuff는 <code>public_pass</code>와 <code>hidden_auto_pass</code>를 더 크게 회복한다.</figcaption>
</figure>

실제로 constrained decoding은 모든 출력을 파싱 가능하게 만들었지만, public_pass는 `0.389 -> 0.403-0.440` 정도로만 올랐다. `+array-cap`은 slot_stuffing을 `0.000`으로 낮췄지만, length_boundary_rate를 `0.202 -> 0.394`로 키웠고 hidden_auto_pass는 `0.265`로 낮았다. 반면 학습 기반 antistuff는 slot_stuffing을 `0.016`으로 낮추면서 public_pass `0.694`, hidden_auto_pass `0.580`에 도달했다. 문법 제약은 특정 구조 지표를 0으로 만들 수 있지만, 형식 규칙 전체와 내용 품질을 함께 회복하는 대체재는 아니었다.

### 유효 슬롯 과사용 중심의 실패 유형

GRPO-binary의 실패 분류도 같은 해석을 뒷받침한다. 학습이 진행되면서 `LEN_EXCEEDED`는 step 50의 `0.539`에서 step 810의 `0.225`로 줄었다. 반면 `BAD_SUFFIX`는 `0.291 -> 0.275`로 거의 남았고, `INVALID_CATEGORY`는 계속 0에 가깝다. 즉 주요 실패는 잘못된 카테고리 선택보다, 검증기가 허용하는 유효 슬롯 값을 과도하게 나열하는 문제에 가깝다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/failure-taxonomy.svg" alt="Failure taxonomy curves for LEN_EXCEEDED, BAD_SUFFIX, and INVALID_CATEGORY in GRPO-binary">
  <figcaption><strong>Figure 7.</strong> GRPO-binary의 실패 유형 변화다. 길이 위반은 줄어들지만 <code>BAD_SUFFIX</code>는 남고 카테고리 위반은 거의 0에 가깝다. stuffing은 잘못된 카테고리 선택보다 유효 슬롯 값을 과도하게 나열하는 문제에 가깝다.</figcaption>
</figure>

같은 입력의 정성 예시도 이 이동 양상을 보여준다. 헤어스타일링 제품 입력에서 dense는 `time=[아침, 저녁, 밤]`, `place=[집, 미용실]`처럼 유효 슬롯을 과다 나열했다. antistuff는 `season=전체`, `time=전체`, `place=전체`에 가까운 일반 조합으로 이동했고, antistuff2는 `time=아침`, `place=헤어샵`처럼 더 구체적인 슬롯으로 돌아왔다. 이 예시는 결론의 주된 근거가 아니라, 정량 지표가 가리키는 변화의 예시다.

## 해석

GRPO 형식 보정은 목적대로 DPO 이후 낮아진 공개 형식 통과율을 회복했다. 해석의 핵심은 이 회복이 공개 검증기만 공략한 결과인지, 아니면 품질 프록시를 크게 해치지 않은 형식 회복인지다. 사람 평가 정답셋 없이 자동 계산 지표만 놓고 보면 후자에 더 가깝다. `public_pass`와 `hidden_auto_pass`가 함께 상승하고, 모델 간 `public_judge_gap` 변화는 유의하지 않으며, `NLL_ctx`도 큰 악화를 보이지 않는다. 여섯 판정 기준 중 과최적화 방향으로 뚜렷하게 움직인 신호는 slot stuffing 하나였으므로, 강한 reward hacking이라고 부르기는 어렵다.

이 분리 반응은 원 실험의 설계 선택도 자동 지표 기준으로 뒷받침한다. DPO가 문맥 품질 프록시를 먼저 개선하고, GRPO가 별도의 형식 신호를 보완하는 순서는 타당했다. 형식 보정이 품질 프록시를 크게 되돌리지 않았기 때문이다.

동시에 형식·품질 신호와 구조 부산물은 분리될 수 있다. binary와 dense 모두 slot stuffing을 크게 만들지만, 이 아티팩트는 공개 검증기를 통과하고 고정 judge도 거의 페널티하지 못한다. `NLL_ctx` 역시 큰 악화를 보이지 않는다. 따라서 LLM judge나 NLL 기반 프록시만으로는 구조화 UI 생성의 좁은 실패를 놓칠 수 있다.

완화도 단일 지표만 보고 설계하기 어렵다. slot stuffing만 억제하면 기본 슬롯 조합으로 이동하는 새 부산물이 생긴다. 이동한 아티팩트를 다시 점검하고 결합 페널티로 막았을 때에야 stuffing과 기본 슬롯 비율을 함께 낮출 수 있었다. constrained decoding 역시 특정 구조 지표를 0으로 만들 수는 있지만, 다른 형식·품질 비용을 숨길 수 있다. 따라서 이 결과의 실무적 결론은 단일 validator pass를 높이는 것이 아니라, 보상 바깥의 구조 휴리스틱과 표본화된 judge 신호를 함께 두고 부산물의 이동까지 추적해야 한다는 것이다.

## 한계

- 운영 품질을 직접 판정한 사람 평가 정답셋은 없다. `hidden_auto_pass`는 고정 LLM judge를 결합한 보조 신호이며, 사람 판단이나 운영 품질 전체를 뜻하지 않는다.
- judge와 인간 라벨의 일치도는 약했다. 별도 인간 검토 500건에서 `tpo/ctx` QWK는 `0.059`, `tpo/nat` QWK는 `0.143`이었으므로 judge 기반 값은 보조 신호로만 사용한다.
- judge는 체크포인트별 무작위 400카드 표본에서만 계산했다. 표본 선택이 gap 추세를 바꿀 수 있음을 확인했기 때문에, judge 부분표본 방식 자체가 결과 해석의 한계다.
- 학습 곡선은 대부분 단일 학습 시드다. 두 핵심 변형은 seed 43으로 반복했고 최종 체크포인트 생성은 다섯 시드로 재생성했지만, 모든 변형의 다중 학습 시드 평균은 아니다.
- slot stuffing 기준값, anti-stuffing cap, penalty weight, judge pass threshold는 수작업 설정이다. 인접 기준값에서 순서는 유지됐지만, 절대 비율을 표준값처럼 해석해서는 안 된다.
- constrained decoding 비교는 DPO 기준 정책에 적용한 단일 조건 비교다. 더 강한 파서, 더 좁은 문법, reranking 조합은 별도 비교가 필요하다.
- 실증 범위는 Gemma 3 4B 계열, 한국어 추천 카드, DPO 이후 GRPO 형식 보정이다. 다른 언어, 더 긴 UI copy, 다른 구조화 출력에서는 같은 결론을 다시 확인해야 한다.

## References

<div class="reference-list" markdown="1">

1. <span id="ref-gemma-3"></span>Google DeepMind. [Gemma 3 model card](https://huggingface.co/google/gemma-3-4b-it). 2025.
2. <span id="ref-instructgpt"></span>Long Ouyang et al. [Training language models to follow instructions with human feedback](https://proceedings.neurips.cc/paper_files/paper/2022/hash/b1efde53be364a73914f58805a001731-Abstract-Conference.html). NeurIPS 2022.
3. <span id="ref-dpo"></span>Rafael Rafailov et al. [Direct Preference Optimization: Your Language Model is Secretly a Reward Model](https://proceedings.neurips.cc/paper_files/paper/2023/hash/a85b405ed65c6477a4fe8302b5e06ce7-Abstract-Conference.html). NeurIPS 2023.
4. <span id="ref-grpo"></span>Zhihong Shao et al. [DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models](https://arxiv.org/abs/2402.03300). 2024.
5. <span id="ref-goodhart"></span>David Manheim and Scott Garrabrant. [Categorizing Variants of Goodhart's Law](https://arxiv.org/abs/1803.04585). 2018.
6. <span id="ref-overoptimization"></span>Leo Gao, John Schulman, and Jacob Hilton. [Scaling Laws for Reward Model Overoptimization](https://proceedings.mlr.press/v202/gao23h.html). ICML 2023.
7. <span id="ref-specification-gaming"></span>Dario Amodei et al. [Concrete Problems in AI Safety](https://arxiv.org/abs/1606.06565). 2016.
8. <span id="ref-reward-gaming"></span>Joar Skalse et al. [Defining and Characterizing Reward Gaming](https://proceedings.neurips.cc/paper_files/paper/2022/hash/3d719fee332caa23d5038b8a90e81796-Abstract-Conference.html). NeurIPS 2022.
9. <span id="ref-constitutional-ai"></span>Yuntao Bai et al. [Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073). 2022.
10. <span id="ref-llm-judge"></span>Lianmin Zheng et al. [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://proceedings.neurips.cc/paper_files/paper/2023/hash/91f18a1287b398d378ef22505bf41832-Abstract-Datasets_and_Benchmarks.html). NeurIPS 2023.
11. <span id="ref-constrained-decoding"></span>Brandon T. Willard and Rémi Louf. [Efficient Guided Generation for Large Language Models](https://arxiv.org/abs/2307.09702). 2023.
12. <span id="ref-cd-json"></span>Saibo Geng et al. [Grammar-Constrained Decoding for Structured NLP Tasks without Finetuning](https://aclanthology.org/2023.emnlp-main.674/). EMNLP 2023.

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
  url = {https://muted-color.github.io/technical-reports/korean-ui-grpo-validator-artifact-evaluation/}
}
```
