---
layout: post
title: "고정 예산 Tool-Use DPO: 호출 정확도와 추가 질문 판단"
date: 2026-06-27 11:04:00 +0900
last_modified_at: 2026-09-06 22:16:46 +0900
lang: ko
categories: ["LLM EVAL"]
tags: [llm, tool-use, dpo, function-calling, bfcl, when2call, ifeval, qwen3]
lab_host: "dgx3"
lab_path: "projects/tool-use-dpo-negative-sources"
excerpt: "같은 학습 예산에서 구조 중심 DPO는 호출 정확도, 판단 중심 DPO는 행동 선택 점수가 높았다. 반복된 구성별 우위와 추가 질문의 정답·오판을 함께 분석한다."
description: "Qwen3-8B의 학습 쌍·업데이트 예산을 맞춘 DPO 비교에서 호출 정확도와 행동 선택의 우위가 갈렸고, 최초 실행의 높은 판단 점수에는 추가 질문의 정답과 오판이 함께 나타났다."
permalink: /research/2026/06/27/tool-use-dpo-fixed-budget-reporting-profile/ko/
translation_url: /research/2026/06/27/tool-use-dpo-fixed-budget-reporting-profile/
image: /assets/images/posts/tool-use-dpo-fixed-budget-reporting-profile/hero-checkpoint-prism.png
image_alt: "동일한 두 반투명 구성 흐름이 투명한 체크포인트 프리즘을 지나 서로 다른 형태의 평가 신호 세 개로 나뉘는 장면"
hero_image: /assets/images/posts/tool-use-dpo-fixed-budget-reporting-profile/hero-checkpoint-prism.png
hero_alt: "동일한 두 반투명 구성 흐름이 투명한 체크포인트 프리즘을 지나 서로 다른 형태의 평가 신호 세 개로 나뉘는 장면"
hero_frame: true
hero_compact: true
---

도구 사용 모델은 함수와 인자를 정확히 골라야 하고, 정보가 부족할 때는 호출 대신 추가 질문이나 답변 불가를 선택해야 한다. 이 글은 **같은 학습 예산에서 두 능력의 우위가 같은 구성에 모이는지, 점수 차이는 어떤 행동 차이를 담고 있는지**를 묻는다. 같은 `Qwen3-8B` 지도 학습 체크포인트에서 출발해 함수 호출 구조 중심과 호출 판단 중심의 두 DPO 구성을 비교한다 <a class="citation-ref" href="#ref-qwen3" aria-label="참고문헌 1">[1]</a>.

관찰된 우위는 평가 항목에 따라 갈렸다. 구조 중심 구성은 호출 정확도에서, 판단 중심 구성은 행동 선택의 집계 점수에서 높았고, 그 방향은 반복 검증에서도 유지됐다. 최초 실행을 행동별로 나누면 판단 중심 구성에는 추가 질문의 정답과 오판이 모두 더 많았다. **구성별 점수 차이의 반복성과, 그 점수에 함께 담긴 행동별 이득과 오류**가 이 글이 보여주는 두 결과다.

> **Tool-use DPO**는 도구 사용의 선호·비선호 응답 쌍에 Rafailov et al.의 **Direct Preference Optimization (DPO)**를 적용한다 <a class="citation-ref" href="#ref-dpo" aria-label="참고문헌 2">[2]</a>. 이 글의 **학습 구성(recipe)**은 데이터 출처와 응답 쌍 구성 방식을 뜻한다. 공통 **SFT 기준선**은 DPO 전의 지도 학습 체크포인트이며, DPO의 고정 reference model로도 사용한다.

## 요약

- **같은 학습 예산에서도 구성별 강점이 달랐다.** 품질 필터를 적용한 50-step 비교에서 구조 중심 구성은 BFCL 호출 정확도가 `3.33` 퍼센트포인트(pp) 높았고, 판단 중심 구성은 When2Call macro F1이 `5.31` pp 높았다.
- **판단 중심 구성은 추가 질문의 정답과 오판이 모두 더 많았다.** 최초 실행에서 추가 질문 정답 수는 구조 중심 `32/100`개, 판단 중심 `57/100`개였다. 반면 판단 중심 구성은 도구 호출과 답변 불가 사례를 더 적게 맞혔다.
- **반복 확인된 것은 집계 점수 차이의 방향이다.** 3개 학습 시드와 한 번 재구성한 학습 쌍 집합에서도 각 구성의 우위가 유지됐다. 행동 유형별 차이는 최초 실행에서만 분석했다.
- **점수 차이의 원인을 오류 유형 하나로 좁힐 수는 없다.** 두 구성의 질문과 선호 응답이 다르고, 판단 중심 학습 데이터는 평가와 같은 When2Call 계열이다. 대표 체크포인트도 결과를 확인한 뒤 선택했다.

## 실험 설계

비교의 단위는 데이터 출처와 응답 쌍 구성 방식이 다른 두 학습 구성이다. 공통 시작점과 학습 쌍·업데이트 예산을 맞춰 구성 간 차이를 측정하고, 평가 질문별 채점 행으로 그 차이의 내용을 살펴본다.

공통 SFT 체크포인트는 xLAM/APIGen `70%`, ToolACE `20%`, When2Call `10%`로 학습했다. 두 주요 DPO 구성과 필터 미적용 대조군은 다음 설정을 공유한다 <a class="citation-ref" href="#ref-artifact-release" aria-label="참고문헌 3">[3]</a>.

- **학습 예산:** 실행당 선호 응답 쌍 `3000`개와 `375`번의 최적화 업데이트.
- **최적화 설정:** beta `0.1`, learning rate `5e-6`, LoRA rank `16`, effective batch size `8`.
- **체크포인트:** 결과를 확인한 뒤 대표 비교로 선택한 50-step 시점과 전체 예산을 사용한 마지막 시점(final). 체크포인트·필터링·소스 혼합의 보조 비교는 Appendix B에 정리한다.

학습 쌍 수와 업데이트 수는 같지만 데이터 분포·질문·손실을 계산하는 토큰 수는 다르다. 여기서 예산은 비교의 통제 조건이며, 계산 비용이 같음을 측정한 결과는 아니다.

### 학습 쌍 구성

Table 1은 [고정 버전의 학습 쌍 구성 규칙](https://github.com/muted-color/tool-use-dpo-fixed-budget-report/blob/arxiv-v1/docs/negative_construction.md)을 정리한다. 선호 응답은 각 소스의 기준 응답을 사용하며, 구성 사이의 질문과 선호 응답은 일치시키지 않았다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr><th>학습 구성</th><th>학습 쌍 출처와 비선호 응답 구성</th></tr>
      </thead>
      <tbody>
        <tr>
          <td>함수 호출 구조 중심 구성<br><span class="table-note-inline">Function-call structure</span></td>
          <td>정답 도구 호출 응답을 변형해 함수 선택, 필수 인자나 값, 호출 수, 또는 응답의 의미에 영향을 주는 타입·스키마 오류를 만든다.<br><span class="table-note-inline">공개 산출물에서는 이 소스를 <code>noised_gold</code>로 표기한다.</span></td>
        </tr>
        <tr>
          <td>호출 판단 중심 구성<br><span class="table-note-inline">Call decision</span></td>
          <td>When2Call 계열의 판단 예제에서 기준 응답과 잘못된 호출·비호출, 불필요한 추가 질문, 응답 포기, 답변 완성 오류를 짝짓는다.<br><span class="table-note-inline">공개 산출물에서는 이 소스를 <code>behavior</code>로 표기한다.</span></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> 데이터 소스별 학습 쌍 구성. 학습 쌍 수와 업데이트 수는 같지만 질문과 선호 응답은 다르다.</figcaption>
</figure>

**품질 필터 적용(quality-gated)** 조건은 모호하거나 동등한 응답 쌍, 허용 가능한 대안, 기준 응답의 오류가 의심되는 쌍을 제외한다. 각 소스는 선택된 예제 최소 `100`개에 대한 LLM 보조 홀드아웃 검토를 통과했다. 이는 사람이 정답을 부여한 절차가 아니라 LLM을 활용한 품질 관리다. **필터 미적용 대조군(ungated control)**은 이 의미적 품질 필터를 적용하기 전 집합에서 학습에 사용할 수 없는 쌍만 제외하고 추출한다.

### 평가 표본과 지표

Table 2는 평가 표본을 정리한다. BFCL은 호출 정확도를 <a class="citation-ref" href="#ref-bfcl" aria-label="참고문헌 4">[4]</a>, When2Call은 호출 판단 과제를 평가한다 <a class="citation-ref" href="#ref-when2call" aria-label="참고문헌 5">[5]</a>. **IFEval-style prompt-strict 진단**은 IFEval에서 파생한 지표다 <a class="citation-ref" href="#ref-ifeval" aria-label="참고문헌 6">[6]</a>. 로컬 평가기가 지원하는 지시를 모두 충족하면 해당 문항을 통과로 처리한다. 지원하지 않는 지시는 채점하지 않고, 지원되는 지시가 하나도 없는 문항은 제외한다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr><th>평가 표본</th><th class="align-right">채점 문항 수</th><th>표본 선택과 채점</th></tr>
      </thead>
      <tbody>
        <tr>
          <td>BFCL core</td>
          <td class="align-right"><code>300</code></td>
          <td>BFCL v3의 simple, multiple, parallel, irrelevance, live multiple에서 각각 앞쪽 60개 행을 사용한다.<br><span class="table-note-inline">고정된 로컬 parser와 평가기로 함수 호출의 exact match 여부를 채점한다.</span></td>
        </tr>
        <tr>
          <td>When2Call</td>
          <td class="align-right"><code>300</code></td>
          <td>Test 설정의 MCQ split에서 tool-call, follow-up, unable-to-answer 예제를 각각 100개 사용한다.<br><span class="table-note-inline">Macro F1은 도구 호출 파싱과 고정된 텍스트 규칙으로 정한 행동 라벨을 사용한다. 응답 exact match는 tool-call 문항의 호출 내용도 확인한다.</span></td>
        </tr>
        <tr>
          <td>IFEval-style<br><span class="table-note-inline">Prompt-strict accuracy</span></td>
          <td class="align-right"><code>96</code></td>
          <td>원본의 앞쪽 100개 prompt 중 지원되는 지시가 없는 4개를 제외한다.<br><span class="table-note-inline">각 prompt에서 평가기가 지원하는 지시를 모두 충족해야 통과한다.</span></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> 고정된 평가 표본과 로컬 채점 정의. 공식 전체 벤치마크 점수가 아닌, 고정 표본에 대한 로컬 평가다.</figcaption>
</figure>

공개 지표 `When2Call_behavior_accuracy`는 채점 행의 `exact_match` 값을 평균한다. 호출 여부를 올바르게 판단해도 함수·인자·호출 수가 틀리면 이 지표에서는 실패할 수 있다. 이 글에서는 이를 **W2C 응답 exact match**로 표기한다. 반면 **행동 라벨 정확도(behavior-label accuracy)**는 `expected_behavior`와 `observed_behavior`를 비교하며, macro F1도 이 라벨을 사용한다. [공개 계산 코드](https://github.com/muted-color/tool-use-dpo-fixed-budget-report/blob/arxiv-v1/src/tool_use_dpo_negative_sources/bootstrap.py)는 두 채점 경로를 구분한다.

고정된 macro-F1 평가기는 정답 예제가 없는 직접 답변(direct answer)도 분류 항목에 포함하고 `zero_division=0`을 적용한다. [데이터 범위 점검](https://github.com/muted-color/tool-use-dpo-fixed-budget-report/blob/arxiv-v1/docs/direct_answer_coverage.md)에서 라벨이 있는 테스트 데이터 `3,952`행에는 direct-answer 정답이 없었고, 별도로 확인한 학습 데이터 `24,000`행에는 행동 정답 라벨이 공개되지 않았다. 이 `27,952`행 점검이 모델 평가 표본 `300`개를 늘려 주거나 학습 데이터의 라벨 분포를 확인해 주는 것은 아니다.

DPO 평가에는 deterministic decoding(`do_sample=false`)과 thinking 비활성화(`enable_thinking=false`)를 공통으로 사용한다. 95% 신뢰구간(CI)은 문항 ID로 조건 간 대응을 유지한 grouped percentile bootstrap `1000`회로 계산한다. 기록된 실행에 대한 평가 표본의 불확실성을 나타내며, 학습과 체크포인트 선택의 불확실성은 포함하지 않는다. 별도의 SFT 비교에는 Appendix A의 생성 길이 조건 제한이 적용된다.

## 결과

### 호출 정확도와 행동 선택에서 갈린 우위

품질 필터를 적용한 50-step 비교에서 BFCL 호출 정확도는 구조 중심 구성이, When2Call(`W2C`) macro F1은 판단 중심 구성이 높았다. 구조 중심·판단 중심 순서로 BFCL은 `0.713` 대 `0.680`, W2C macro F1은 `0.477` 대 `0.530`이었다. Table 3은 이 차이를 구조 중심 점수에서 판단 중심 점수를 뺀 값으로 보여준다. BFCL의 양수와 W2C의 음수가 각 구성의 우위를 뜻하며, 필터 미적용 대조군에서도 같은 방향이다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>조건</th>
          <th>지표</th>
          <th class="align-right">점수 차이 (pp)</th>
          <th class="align-right">95% CI 하한</th>
          <th class="align-right">95% CI 상한</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td rowspan="3">Quality-gated</td>
          <td>BFCL core</td>
          <td class="align-right"><code>+3.33</code></td>
          <td class="align-right"><code>+1.53</code></td>
          <td class="align-right"><code>+5.67</code></td>
        </tr>
        <tr>
          <td>W2C 응답 exact match</td>
          <td class="align-right"><code>-6.67</code></td>
          <td class="align-right"><code>-10.75</code></td>
          <td class="align-right"><code>-3.02</code></td>
        </tr>
        <tr>
          <td>W2C macro F1</td>
          <td class="align-right"><code>-5.31</code></td>
          <td class="align-right"><code>-8.85</code></td>
          <td class="align-right"><code>-2.34</code></td>
        </tr>
        <tr>
          <td rowspan="2">Ungated control</td>
          <td>BFCL core</td>
          <td class="align-right"><code>+2.67</code></td>
          <td class="align-right"><code>+1.02</code></td>
          <td class="align-right"><code>+4.86</code></td>
        </tr>
        <tr>
          <td>W2C macro F1</td>
          <td class="align-right"><code>-4.21</code></td>
          <td class="align-right"><code>-7.48</code></td>
          <td class="align-right"><code>-1.23</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> 대표 50-step 체크포인트의 구성 간 평가 축별 차이와 grouped bootstrap CI. 차이는 함수 호출 구조 중심 구성 점수에서 호출 판단 중심 구성 점수를 뺀 값이다.</figcaption>
</figure>

집계 점수 차이의 방향은 3개 학습 시드와 한 번 재구성한 학습 쌍 집합에서도 유지됐다(Table 4). 이는 평가한 설정 안에서 구성별 차이가 반복됨을 뒷받침한다. 다만 재구성한 집합도 원래 집합과 질문 일부를 공유하며, 이 검사로 데이터 소스의 효과와 질문 구성의 효과를 분리할 수는 없다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>검사</th>
          <th>관찰 결과</th>
          <th>범위</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>학습 시드</td>
          <td>3개 시드에서 같은 방향이 유지됐다.<br><span class="table-note-inline">점수 차이 범위 (pp): BFCL <code>3.00–4.00</code>; W2C 응답 exact match <code>5.00–6.67</code>; W2C macro F1 <code>4.26–5.31</code>.</span></td>
          <td>고정된 학습 쌍 집합에 한정.</td>
        </tr>
        <tr>
          <td>재구성한 학습 쌍 집합</td>
          <td>학습 쌍 ID와 내용 해시의 중복은 없었고, 질문 ID의 중복은 <code>401/3000</code>, <code>1337/3000</code>이었다.<br><span class="table-note-inline">재구성한 집합의 점수 차이 (pp): BFCL <code>3.33</code>; W2C 응답 exact match <code>6.33</code>; W2C macro F1 <code>5.04</code>.</span></td>
          <td>재구성 1회; 원래 집합과 질문 일부를 공유.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> 50-step의 구성별 집계 점수 차이. 점수 차이는 부호 없이 표시했다. BFCL은 구조 중심, 두 W2C 지표는 판단 중심 구성이 높다. Figure 1의 행동별 분석은 최초 실행에 대한 별도 분석이다.</figcaption>
</figure>

### 추가 질문에서 드러난 정답과 오판

집계 순위가 반복됐다는 사실만으로 각 행동 유형에서 어느 구성이 더 나은지는 알 수 없다. 이를 살펴보기 위해 Figure 1에서는 유형별 정답 수를 비교하고, 이어지는 문항별 분석에서는 잘못된 추가 질문이 어디서 나왔는지 확인한다.

Figure 1은 품질 필터를 적용한 최초 50-step [구조 중심](https://github.com/muted-color/tool-use-dpo-fixed-budget-report/blob/arxiv-v1/results/per_example/primary/r028_step50.csv)·[판단 중심](https://github.com/muted-color/tool-use-dpo-fixed-budget-report/blob/arxiv-v1/results/per_example/primary/r029_step50.csv) 실행에서 행동 라벨의 정답 수를 다시 센 결과다. 두 파일은 문항 ID와 질문 해시가 같은 `300`문항을 담고 있다. 각 유형에 `100`문항이 있어 정답 수와 재현율(%)의 숫자가 같다. 이 유형별 분석은 구성당 한 번의 실행을 사후에 나눈 결과이며, 앞서 제시한 집계 점수의 반복 검증과 구분한다.

<figure class="media-figure" style="max-width: 600px; margin-inline: auto;">
  <img src="/assets/images/posts/tool-use-dpo-fixed-budget-reporting-profile/when2call-behavior-breakdown.svg" alt="정답 유형별 100문항 중 행동 라벨 정답 수. 구조 중심 대 판단 중심 구성은 도구 호출 94 대 88, 추가 질문 32 대 57, 답변 불가 66 대 64다.">
  <figcaption><strong>Figure 1.</strong> 각 행동 유형의 100문항 중 정답 라벨을 선택한 수. 품질 필터를 적용한 최초 두 실행의 50-step 결과를 구조 중심, 판단 중심 순서로 비교한다. 축은 0–100이며 함수·인자 정확도는 포함하지 않는다. 구성당 한 번의 실행 결과로, 신뢰구간은 표시하지 않았다.</figcaption>
</figure>

Figure 1에서 정답 수 차이가 가장 큰 유형은 추가 질문이었다. 같은 채점 행을 문항별로 대조하면, 판단 중심 구성이 추가로 맞힌 추가 질문 `25`문항 중 구조 중심 구성은 `22`개를 도구 호출로, `3`개를 답변 불가로 분류했다. 이 유형에서 잘못된 도구 호출 라벨은 구조 중심 `61`개, 판단 중심 `36`개였다. 반대로 도구 호출이나 답변 불가가 정답인데 추가 질문으로 잘못 분류한 수는 각각 `3`개와 `20`개였다. 즉, 판단 중심 구성은 추가 질문이 정답인 문항을 더 잘 식별하면서도, 다른 행동이 정답인 문항을 추가 질문으로 잘못 분류한 경우가 더 많았다.

Figure 1의 정답 수를 합친 행동 라벨 정확도는 구조 중심 구성 `192/300`(`64.00%`), 판단 중심 구성 `209/300`(`69.67%`)다. 호출 내용까지 확인하는 응답 exact match는 이보다 낮은 `170/300`(`56.67%`), `190/300`(`63.33%`)로, 호출 여부는 맞혔지만 호출 내용이 틀린 사례가 각각 `22`개와 `19`개다. 판단 중심 구성의 macro F1이 `5.31` pp 높은 데에는 잘못된 호출이 적어 도구 호출 정밀도(precision)가 높은 영향도 있다. 반면 도구 호출 재현율(recall)은 구조 중심 `94%`, 판단 중심 `88%`로 판단 중심 구성이 낮았다.

BFCL 차이도 일부 유형에 집중됐다. 구조 중심 구성이 더 맞힌 `10`문항은 live multiple(`+5`), multiple(`+2`), irrelevance(`+3`)에서 나왔고, simple과 parallel의 정답 수는 같았다. Irrelevance에서는 두 구성 모두 낮은 점수(`6/60`, `3/60`)를 보였다. 따라서 When2Call의 우위가 호출을 하지 말아야 하는 모든 상황에서 더 나은 판단을 뜻하지는 않는다.

## 결론과 한계

같은 시작점과 학습 쌍·업데이트 예산에서 **구조 중심 구성의 BFCL 우위와 판단 중심 구성의 When2Call 우위가 반복됐다**. 최초 실행의 문항별 분석은 이 순위에 담긴 행동 차이를 구체화한다. 판단 중심 구성은 추가 질문을 더 많이 맞혔지만, 다른 행동을 추가 질문으로 오판한 경우도 더 많았고 도구 호출·답변 불가의 재현율은 낮았다. 따라서 높은 When2Call macro F1이 모든 행동 유형에서 판단 중심 구성이 우세하다는 뜻은 아니다.

데이터 소스와 관련된 전문화는 가능한 설명이다. Ross et al.의 When2Call도 판단 중심 데이터와 preference optimization을 결합한다 <a class="citation-ref" href="#ref-when2call" aria-label="참고문헌 5">[5]</a>. 이 비교에서 확인한 것은 고정 예산의 점수 차이와 반복 방향, 그리고 최초 실행에서 그 차이에 동반된 정답·오판의 분포다. 그 원인과 적용 범위에는 다음 제한이 있다.

- **원인 분리:** 학습 질문과 선호 응답이 달라 비선호 응답의 오류 유형을 차이의 원인으로 특정할 수 없다. 이를 확인하려면 질문과 선호 응답을 맞추고, 학습 소스 계열 밖에서도 평가해야 한다.
- **측정과 반복:** 행동 라벨은 고정된 파싱·텍스트 규칙으로 정한다. 공개 행에는 생성 답변이 없어 의미적으로 적절한 응답인지는 이 분석으로 확인할 수 없다. 행동별 분석은 최초 실행에 한정되며, 3개 시드와 재구성한 학습 쌍 집합의 검증은 집계 차이를 확인한 것이다.
- **범위:** 하나의 Qwen3-8B SFT 시작점과 하나의 QLoRA DPO 설정을 평가했다 <a class="citation-ref" href="#ref-lora" aria-label="참고문헌 7">[7]</a> <a class="citation-ref" href="#ref-qlora" aria-label="참고문헌 8">[8]</a>. 로컬 평가 표본, 직접 답변 정답의 부재, 사후 체크포인트 선택은 일반화를 제한한다. Appendix A의 SFT 비교는 생성 길이 조건도 일치하지 않아, 학습 때문에 지시 이행 능력이 하락했다고 확정할 수는 없다.

실제 사용 환경에서 구성을 선택하려면 어떤 오류를 줄이는 데 가치를 둘지 정해야 한다. 이 결과는 호출 정확도, 추가 질문의 정답과 오판을 함께 비교할 근거를 제공한다. 어느 구성이 사용 비용까지 낮추는지는 불필요한 호출과 질문의 비용을 별도로 평가해야 알 수 있다.

## Appendix A. 기록된 SFT 비교

[공개 IFEval 채점 행](https://github.com/muted-color/tool-use-dpo-fixed-budget-report/tree/arxiv-v1/results/per_example/ifeval)에는 SFT의 생성 텐서 길이가 `768`까지 기록돼 있지만, [DPO manifest](https://github.com/muted-color/tool-use-dpo-fixed-budget-report/blob/arxiv-v1/manifests/benchmark_manifest.yaml)의 IFEval 출력 상한은 `384`다. 길이에는 배치 padding이 포함되므로 개별 답변의 잘림 여부는 알 수 없지만, SFT 행 전체가 같은 상한에서 생성된 결과일 수는 없다. SFT의 정확한 생성 인자는 복원하지 못했다.

Appendix Table 1은 기록된 점수 차이를 보존한다. SFT 점수는 BFCL `0.667`, W2C macro F1 `0.481`, IFEval-style `0.635`이며 변화량은 반올림 전 집계값으로 계산했다. 이 변화를 학습의 효과로 해석하려면 생성 길이 조건을 맞춘 비교가 필요하다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>학습 구성<br><span class="table-note-inline">Quality-gated 조건 · 50 steps</span></th>
          <th class="align-right">BFCL core<br><span class="table-note-inline">변화 (pp)</span></th>
          <th class="align-right">W2C macro F1<br><span class="table-note-inline">변화 (pp)</span></th>
          <th class="align-right">IFEval-style<br><span class="table-note-inline">Prompt-strict 변화 (pp)</span></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>함수 호출 구조 중심 구성</td>
          <td class="align-right"><code>+4.67</code></td>
          <td class="align-right"><code>-0.45</code></td>
          <td class="align-right"><code>-6.25</code><br><span class="table-note-inline">[-11.46, -1.04]</span></td>
        </tr>
        <tr>
          <td>호출 판단 중심 구성</td>
          <td class="align-right"><code>+1.33</code></td>
          <td class="align-right"><code>+4.86</code></td>
          <td class="align-right"><code>-5.21</code><br><span class="table-note-inline">[-11.46, 0.00]</span></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 1.</strong> 기록된 50-step DPO 점수에서 SFT 점수를 뺀 차이(pp). 대괄호는 공개된 IFEval prompt-strict bootstrap 95% 신뢰구간이다. 양수는 더 높은 점수다. 생성 길이 조건이 일치하지 않아 학습만의 효과로 귀속할 수 없다.</figcaption>
</figure>

지원되는 지시가 있는 IFEval `96`문항 중 SFT는 `61`개, 구조 중심 구성은 `55`개, 판단 중심 구성은 `56`개를 통과했다. SFT에서 실패했지만 DPO에서 통과한 문항은 구조 중심 1개, 판단 중심 1개였다. SFT에서 통과했지만 DPO에서 실패한 문항은 구조 중심 7개, 판단 중심 6개였다. 문항 ID·hash·지원 지시 수는 일치했다. 이는 생성 조건이 일치하지 않는 평가의 채점 상태 변화이며, bootstrap 구간이 이 교란을 없애 주지는 않는다.

## Appendix B. 체크포인트·필터링·혼합의 탐색적 결과

Appendix Table 2는 체크포인트별 점수와 소스를 혼합한 구성의 점수를 보여준다. 이 비교는 주요 구성 간 비교보다 반복 검증이 적다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>조건</th>
          <th>체크포인트</th>
          <th class="align-right">BFCL core</th>
          <th class="align-right">W2C macro F1</th>
          <th class="align-right">IFEval-style<br><span class="table-note-inline">Prompt-strict</span></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td rowspan="2">함수 호출 구조 중심 구성</td>
          <td>50 steps</td>
          <td class="align-right"><code>0.713</code></td>
          <td class="align-right"><code>0.477</code></td>
          <td class="align-right"><code>0.573</code></td>
        </tr>
        <tr>
          <td>Final</td>
          <td class="align-right"><code>0.693</code></td>
          <td class="align-right"><code>0.479</code></td>
          <td class="align-right"><code>0.521</code></td>
        </tr>
        <tr>
          <td rowspan="2">호출 판단 중심 구성</td>
          <td>50 steps</td>
          <td class="align-right"><code>0.680</code></td>
          <td class="align-right"><code>0.530</code></td>
          <td class="align-right"><code>0.583</code></td>
        </tr>
        <tr>
          <td>Final</td>
          <td class="align-right"><code>0.660</code></td>
          <td class="align-right"><code>0.528</code></td>
          <td class="align-right"><code>0.562</code></td>
        </tr>
        <tr>
          <td>50:50 소스 혼합</td>
          <td>50 steps</td>
          <td class="align-right"><code>0.700</code></td>
          <td class="align-right"><code>0.513</code></td>
          <td class="align-right"><code>0.521</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 2.</strong> 품질 필터를 적용한 DPO 조건의 절대 점수. 모든 지표는 높을수록 좋으며, IFEval-style은 Table 2의 채점 정의를 따른다.</figcaption>
</figure>

- **체크포인트:** 50-step에서 final로 갈 때 구조 중심 구성의 BFCL은 `-2.00` pp, IFEval-style은 `-5.21` pp 변했다(95% CI `[-10.42, 0.00]`). 판단 중심 구성의 W2C macro F1은 `-0.19` pp, IFEval-style은 `-2.08` pp 변했다(`[-6.25, +2.08]`). 각 목표 지표와 IFEval-style의 점추정치는 앞선 체크포인트가 높지만, 두 IFEval 구간 모두 0을 포함하고 50-step은 결과를 본 뒤 선택했다.
- **필터링:** 50-step에서 quality-gated 점수에서 ungated 점수를 뺀 차이는 구조 중심 구성의 BFCL `+0.33` pp(`[0.00, +1.08]`), 판단 중심 구성의 W2C macro F1 `+0.55` pp(`[-0.83, +1.81]`)였다. 학습 쌍의 유효성 검사가 여기서 뚜렷한 후속 성능 향상으로 이어지지는 않았다.
- **혼합:** `50:50` 실행은 소스당 `1500`쌍을 사용한다. BFCL과 W2C 점수는 두 전문화 구성 사이에 있고, IFEval-style(`0.521`)은 둘보다 낮다. 소스당 학습 쌍이 절반이고 혼합 실행의 반복 검사가 없어, 유해한 간섭이 입증된 것은 아니다.

## 공개 산출물

{% include model-mention-cards.html label="GitHub 저장소" aria_label="Tool-use DPO 고정 예산 보고서 GitHub 저장소" models="Artifact release|muted-color/tool-use-dpo-fixed-budget-report|https://github.com/muted-color/tool-use-dpo-fixed-budget-report" %}

{% include model-mention-cards.html label="논문" aria_label="Tool-use DPO 고정 예산 보고서 논문 PDF" models="Paper PDF|paper.pdf|https://github.com/muted-color/tool-use-dpo-fixed-budget-report/blob/main/paper.pdf" %}

고정 버전의 보고서에는 집계 표, 문항별 채점 행, 평가 manifest, bootstrap 결과가 포함된다 <a class="citation-ref" href="#ref-artifact-release" aria-label="참고문헌 3">[3]</a>. Figure 1과 행동 라벨 수는 그 공개 행을 추가로 분석한 결과다. 공개 자료로 점수 수준의 검증은 가능하지만, 원래 질문과 생성 답변은 포함되지 않는다.

## References

<div class="reference-list" markdown="1">

<ol>
  <li id="ref-qwen3">Yang, An et al. <strong>Qwen3 Technical Report</strong>. arXiv:2505.09388, 2025. <a href="https://arxiv.org/abs/2505.09388">arXiv</a>; Qwen Team. <strong>Qwen3-8B</strong>. Hugging Face model repository. <a href="https://huggingface.co/Qwen/Qwen3-8B">Model card</a></li>
  <li id="ref-dpo">Rafailov, Rafael et al. <strong>Direct Preference Optimization: Your Language Model is Secretly a Reward Model</strong>. NeurIPS, 2023. <a href="https://arxiv.org/abs/2305.18290">arXiv</a></li>
  <li id="ref-artifact-release">Ahn, Ilho. <strong>Reporting Tool-Use DPO Under Fixed Budgets: Recipe–Checkpoint Profiles and Guardrail Trade-offs</strong>. Artifact release, June 5, 2026. <a href="https://github.com/muted-color/tool-use-dpo-fixed-budget-report/tree/arxiv-v1">Pinned artifact snapshot</a>; <a href="https://github.com/muted-color/tool-use-dpo-fixed-budget-report/blob/main/paper.pdf">Current paper PDF</a></li>
  <li id="ref-bfcl">Patil, Shishir G. et al. <strong>The Berkeley Function Calling Leaderboard (BFCL): From Tool Use to Agentic Evaluation of Large Language Models</strong>. ICML, 2025. <a href="https://proceedings.mlr.press/v267/patil25a.html">PMLR</a>; <a href="https://gorilla.cs.berkeley.edu/leaderboard.html">Project page</a></li>
  <li id="ref-when2call">Ross, Hayley, Mahabaleshwarkar, Ameya Sunil, and Suhara, Yoshi. <strong>When2Call: When (not) to Call Tools</strong>. NAACL, 2025. DOI: <a href="https://doi.org/10.18653/v1/2025.naacl-long.174">10.18653/v1/2025.naacl-long.174</a>; <a href="https://huggingface.co/datasets/nvidia/When2Call">Dataset card</a></li>
  <li id="ref-ifeval">Zhou, Jeffrey et al. <strong>Instruction-Following Evaluation for Large Language Models</strong>. arXiv:2311.07911, 2023. <a href="https://arxiv.org/abs/2311.07911">arXiv</a></li>
  <li id="ref-lora">Hu, Edward J. et al. <strong>LoRA: Low-Rank Adaptation of Large Language Models</strong>. ICLR, 2022. <a href="https://arxiv.org/abs/2106.09685">arXiv</a></li>
  <li id="ref-qlora">Dettmers, Tim et al. <strong>QLoRA: Efficient Finetuning of Quantized LLMs</strong>. NeurIPS, 2023. <a href="https://arxiv.org/abs/2305.14314">arXiv</a></li>
</ol>

</div>

## Citation

Text citation:

```text
Ilho Ahn, "고정 예산 Tool-Use DPO: 호출 정확도와 추가 질문 판단", Mini Research, June 27, 2026.
```

BibTeX:

```bibtex
@article{ahn2026toolusedporeportingprofile,
  author = {Ilho Ahn},
  title = {고정 예산 Tool-Use DPO: 호출 정확도와 추가 질문 판단},
  journal = {Mini Research},
  year = {2026},
  month = jun,
  url = {https://muted-color.github.io/research/2026/06/27/tool-use-dpo-fixed-budget-reporting-profile/ko/}
}
```
