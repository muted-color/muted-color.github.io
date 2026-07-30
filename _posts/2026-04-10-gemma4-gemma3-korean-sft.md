---
title: "4B급 Gemma3와 Gemma4 한국어 SFT 비교: 품질, 학습, 노이즈"
date: 2026-04-12 09:00:00 +0900
last_modified_at: 2026-04-19 15:45:00 +0900
categories: ["LLM EVAL"]
tags: [gemma, korean, sft, eval]
excerpt: "Gemma3와 Gemma4를 한국어 instruction 환경에서 비교했다. base 품질, QLoRA SFT 후 성능, 학습 효율, 입력 노이즈 안정성을 정리한다."
description: "Gemma3와 Gemma4 4B급 한국어 instruction 모델을 base 품질, QLoRA SFT 반응, 입력 노이즈 안정성 관점에서 비교한 실험 노트."
permalink: /research/2026/04/12/gemma3-e4b-korean-sft/
image: /assets/images/posts/gemma3-e4b-korean-sft/social-thumbnail.png
image_alt: "Gemma3와 Gemma4 한국어 SFT 비교 결과를 질문별 evidence map으로 요약한 소셜 썸네일"
hero_image: /assets/images/posts/gemma3-e4b-korean-sft/evidence-map.svg
hero_alt: "Gemma4와 Gemma3 한국어 비교의 핵심 질문별 결과 요약"
hero_caption: "<strong>Figure 1.</strong> 전체 결과를 먼저 압축한 요약이다. 각 행은 서로 다른 단위의 지표이므로 행 안에서 두 모델의 상대 차이만 읽으면 된다. 모든 행은 값이 클수록 좋은 방향으로 맞췄고, <code>Format alignment</code>는 <code>1 - Violation</code>으로 계산했다. 세부 수치는 본문에서 따로 설명한다."
---

이 글은 <code>google/gemma-3-4b-it</code>와 <code>google/gemma-4-E4B-it</code>를 같은 한국어 instruction 평가 조건에서 비교한다. Gemma4는 judge가 더 자주 선택했고, 출력 형식도 더 잘 지켰다. 질문에 오타나 전사 오류가 섞여도 답변이 더 읽을 만하게 남았고, 같은 100-step QLoRA SFT도 더 빨리 끝났다. Gemma3는 일부 reference overlap 지표와 다중 답안 SFT의 상대 개선폭에서 볼 만한 신호를 보였다. 그래서 이 비교는 단순한 승패보다 응답 품질, 학습 반응, 입력 노이즈 안정성이 어디서 갈라지는지를 본다.

{% include model-mention-cards.html label="비교 대상 모델" aria_label="비교 대상 Hugging Face 모델" models="Gemma3|google/gemma-3-4b-it|https://huggingface.co/google/gemma-3-4b-it;Gemma4|google/gemma-4-E4B-it|https://huggingface.co/google/gemma-4-E4B-it" %}

## 평가 방법

평가는 세 축으로 나눴다. 첫째, base 모델의 한국어 응답 품질을 본다. 둘째, 같은 데이터로 SFT한 뒤 응답 품질과 학습 효율이 어떻게 달라지는지 본다. 셋째, 질문 본문에 타이핑 오타나 음성 전사체 오류가 들어갔을 때 답변이 얼마나 흔들리는지 본다.

모든 생성 평가는 같은 출력 제약 아래에서 진행했다.

- 한국어 일반 문장으로 답변하기
- 한 문단으로 쓰고, 400자와 5문장을 넘기지 않기
- Markdown, 제목, 표, 목록, 불릿, 코드, 굵게 쓰기 금지

### 평가 메트릭

메트릭은 네 가지 축으로 나눠 읽었다.

<div class="content-tabs">
  <input class="content-tabs__radio" type="radio" name="evaluation-metric-tabs" id="evaluation-metric-tab-judge" checked="checked">
  <input class="content-tabs__radio" type="radio" name="evaluation-metric-tabs" id="evaluation-metric-tab-reference">
  <input class="content-tabs__radio" type="radio" name="evaluation-metric-tabs" id="evaluation-metric-tab-format">
  <input class="content-tabs__radio" type="radio" name="evaluation-metric-tabs" id="evaluation-metric-tab-noise">

  <div class="content-tabs__list" aria-label="평가 메트릭">
    <label class="content-tabs__tab" id="evaluation-metric-tab-label-judge" for="evaluation-metric-tab-judge">Judge Preference</label>
    <label class="content-tabs__tab" id="evaluation-metric-tab-label-reference" for="evaluation-metric-tab-reference">Reference Match</label>
    <label class="content-tabs__tab" id="evaluation-metric-tab-label-format" for="evaluation-metric-tab-format">Format Alignment</label>
    <label class="content-tabs__tab" id="evaluation-metric-tab-label-noise" for="evaluation-metric-tab-noise">Noise Readability</label>
  </div>

  <div class="content-tabs__panels">
    <section class="content-tabs__panel content-tabs__panel--judge" aria-labelledby="evaluation-metric-tab-label-judge">
      <p><code>Judge Preference</code>는 <code>gpt-oss-120b</code>를 판정기로 쓴 pairwise 선택률이다. 같은 질문에 대한 두 모델 답변을 나란히 보여주고, 답변 순서는 섞은 뒤 더 나은 쪽을 고르게 했다. 핵심 비교는 기준 답안을 보여주지 않는 <code>blind_to_reference</code>로 진행했다.</p>
      <p class="metric-detail__eyebrow">Rubric</p>
      <ul>
        <li>질문에 직접 답하는가</li>
        <li>사실적으로 무리한 설명이 적은가</li>
        <li>한국어 문장이 자연스럽고 완결적인가</li>
        <li>요청한 출력 형식을 지키는가</li>
      </ul>
      <p>이 rubric은 한 가지 점수만 보지 않기 위한 장치다. 따라서 <code>Judge Preference</code>는 절대 점수라기보다, 같은 질문에서 두 답 중 어느 쪽이 더 좋아 보였는지를 나타내는 상대 지표다. 표의 <code>Judge Score</code>는 같은 rubric으로 개별 답변에 부여한 1-10점 평균이다.</p>
      <p class="metric-detail__eyebrow">Formula</p>
      <div class="metric-formulas">
        <div class="metric-formula">
          <span class="metric-formula__label">Judge Preference</span>
          <span class="metric-formula__body">selected answers / total pairwise comparisons</span>
        </div>
      </div>
      <p>예를 들어 <code>0.70</code>은 같은 질문 100개에서 해당 모델 답변이 70번 선택됐다는 뜻이다.</p>
    </section>

    <section class="content-tabs__panel content-tabs__panel--reference" aria-labelledby="evaluation-metric-tab-label-reference">
      <p><code>Reference Match</code>는 기준 답안과 표현이 얼마나 겹치는지를 보는 자동 지표다. 여기서는 <code>Char F1</code>과 <code>ROUGE-L F1</code>을 함께 봤다. 이 값은 기준 답안에 가까운 표현을 잘 잡지만, 더 자연스러운 패러프레이즈나 더 짧고 완결적인 답을 과소평가할 수 있다.</p>
      <p><code>Char F1</code>은 예측 답변과 기준 답안의 문자 overlap을 precision과 recall로 나눠 본 뒤 F1로 합친 값이다.</p>
      <div class="metric-formulas">
        <div class="metric-formula">
          <span class="metric-formula__label">Char Precision</span>
          <span class="metric-formula__body"><var>P</var><sub>char</sub> = |C(pred) ∩ C(ref)| / |C(pred)|</span>
        </div>
        <div class="metric-formula">
          <span class="metric-formula__label">Char Recall</span>
          <span class="metric-formula__body"><var>R</var><sub>char</sub> = |C(pred) ∩ C(ref)| / |C(ref)|</span>
        </div>
        <div class="metric-formula">
          <span class="metric-formula__label">Char F1</span>
          <span class="metric-formula__body"><var>F1</var><sub>char</sub> = 2PR / (P + R)</span>
        </div>
      </div>
      <p><code>ROUGE-L F1</code>은 두 텍스트 사이의 longest common subsequence, 즉 순서를 유지한 최장 공통 부분열을 기반으로 한다.</p>
      <div class="metric-formulas">
        <div class="metric-formula">
          <span class="metric-formula__label">ROUGE-L Precision</span>
          <span class="metric-formula__body"><var>P</var><sub>LCS</sub> = LCS(pred, ref) / |pred|</span>
        </div>
        <div class="metric-formula">
          <span class="metric-formula__label">ROUGE-L Recall</span>
          <span class="metric-formula__body"><var>R</var><sub>LCS</sub> = LCS(pred, ref) / |ref|</span>
        </div>
        <div class="metric-formula">
          <span class="metric-formula__label">ROUGE-L F1</span>
          <span class="metric-formula__body"><var>F1</var><sub>LCS</sub> = 2PR / (P + R)</span>
        </div>
      </div>
    </section>

    <section class="content-tabs__panel content-tabs__panel--format" aria-labelledby="evaluation-metric-tab-label-format">
      <p><code>Violation</code>은 출력 형식 제약을 어긴 비율이다. 이 글에서는 모든 생성 평가에 같은 출력 제약을 걸었다.</p>
      <p class="metric-detail__eyebrow">Checked Constraints</p>
      <ul>
        <li>한국어 일반 문장으로 답변하기</li>
        <li>한 문단으로 쓰기</li>
        <li>400자와 5문장을 넘기지 않기</li>
        <li>Markdown, 제목, 표, 목록, 불릿, 코드, 굵게 쓰기 금지</li>
      </ul>
      <p><code>Violation</code>이 낮을수록 형식을 더 잘 지킨 것이다.</p>
      <p>Figure 1에서는 모든 행을 “높을수록 좋음” 방향으로 맞추기 위해 <code>Format alignment</code>로 바꿔 표시했다.</p>
      <div class="metric-formulas">
        <div class="metric-formula">
          <span class="metric-formula__label">Format Alignment</span>
          <span class="metric-formula__body">1 - violation rate</span>
        </div>
      </div>
      <p>예를 들어 base 조건에서 Gemma4의 violation은 <code>0.11</code>이므로 <code>Format alignment = 0.89</code>가 된다. Gemma3의 violation은 <code>0.90</code>이므로 <code>Format alignment = 0.10</code>으로 표시했다.</p>
    </section>

    <section class="content-tabs__panel content-tabs__panel--noise" aria-labelledby="evaluation-metric-tab-label-noise">
      <p>질문 손상 안정성은 시스템 프롬프트나 템플릿을 바꾸지 않고, 질문 본문만 손상시켜 봤다. <code>Real typo</code>는 타이핑 오타와 띄어쓰기 붕괴, <code>ASR noise</code>는 음성 전사체처럼 구두점이 사라지거나 발음 유사 표현이 섞인 입력이다. 즉 모델이 사용자의 불완전한 입력을 얼마나 안정적으로 처리하는지를 보는 축이다.</p>
      <p>여기서 <code>Readability</code>는 <code>Judge Preference</code>와 같은 <code>gpt-oss-120b</code>를 사용하지만, 방식은 다르다. <code>Judge Preference</code>는 두 모델 답변을 직접 비교하는 pairwise 선택률이고, <code>Readability</code>는 각 답변 하나를 1-10점으로 채점한 단일 답변 judge 점수다.</p>
      <p class="metric-detail__eyebrow">How to read</p>
      <ul>
        <li><code>Noise Avg</code>: 손상된 질문 답변을 <code>gpt-oss-120b</code> <code>Readability</code> judge가 1-10점으로 평가한 평균</li>
        <li><code>Raw Avg</code>: 같은 질문을 손상하지 않았을 때의 답변을 같은 <code>Readability</code> judge로 평가한 평균</li>
        <li><code>Delta</code>: 같은 모델 안에서 손상 질문 평균에서 원래 질문 평균을 뺀 값</li>
      </ul>
      <p class="metric-detail__eyebrow">Readability Rubric</p>
      <ul>
        <li>문장으로 자연스럽게 읽히는가</li>
        <li>손상된 질문의 의도를 대체로 복원했는가</li>
        <li>반복이나 중간 끊김이 적은가</li>
        <li>설명이 과도하게 무너지지 않았는가</li>
      </ul>
      <p>이 rubric은 정답과 똑같은 표현을 쓰는지를 보는 기준이 아니다. 손상 입력에서도 답변이 읽을 만하게 남는지를 <code>gpt-oss-120b</code>가 1-10점으로 평가한 judge 점수다.</p>
    </section>
  </div>
</div>

### 평가 설계 요약

세 축을 한 번에 비교하기 위한 해석 가이드다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>평가 축</th>
          <th>무엇을 봤나</th>
          <th>대표 지표</th>
          <th>주의할 점</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Base</strong></td>
          <td>한국어 instruction 응답의 기본 품질</td>
          <td><code>Judge Preference</code>, <code>Char F1</code>, <code>ROUGE-L</code>, <code>Violation</code></td>
          <td><code>Violation</code>은 출력 형식 제약을 어긴 비율</td>
        </tr>
        <tr>
          <td><strong>SFT</strong></td>
          <td>학습 후 품질, loss 변화, runtime</td>
          <td><code>Judge Preference</code>, <code>Train loss</code>, runtime</td>
          <td>모델 간 절대 loss만으로 품질을 비교하면 안 됨</td>
        </tr>
        <tr>
          <td><strong>Noise</strong></td>
          <td>질문 본문 손상에 대한 안정성</td>
          <td><code>Noise Avg</code>, <code>Raw Avg</code>, <code>Char F1</code>, <code>Violation</code></td>
          <td>같은 모델 안의 하락폭과 noise 상태의 절대 품질을 분리해서 봐야 함</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> 이 글에서 사용한 세 평가 축이다. 세 축은 서로 다른 능력을 보기 때문에 한 지표만으로 전체 결론을 내리지 않았다.</figcaption>
</figure>

상단 Figure 1은 이 평가 설계를 따라 전체 결과를 먼저 압축한 요약이다. 각 행은 서로 다른 단위의 지표이므로, 막대 길이는 행 안에서 두 모델의 상대 차이를 보여준다. 세부 해석은 이어지는 `Base`, `SFT`, `노이즈` 섹션에서 따로 풀어본다.

## Base: 품질과 형식 제어

base 비교는 `beomi/KoAlpaca-v1.1a` holdout 100문항에서 진행했다. `Judge Preference`는 Gemma4를 `0.70` 비율로 더 자주 골랐다. 반면 `Char F1`과 `ROUGE-L`은 두 모델이 거의 같은 범위에 있었고, Gemma3가 아주 근소하게 높았다.

> **자동 지표 차이는 작았고, 형식 차이는 컸다**
>
> 같은 출력 제약을 걸었는데도 Gemma4는 답을 짧게 닫고 형식을 더 잘 지켰다. 반면 Gemma3는 기준 답안과 겹치는 표현이 약간 많게 나온 대신 평균 출력이 길고 5문장 제한을 자주 넘겼다.

따라서 base 결과는 단순한 품질 승패가 아니라, 작은 기준 답안 유사도 차이와 큰 지시 준수 차이가 함께 나온 사례로 읽어야 한다. 이 조건에서는 Gemma3의 형식 위반과 장황함이 `Judge Preference`를 끌어내린 주요 요인이었을 가능성이 크다. 자동 지표의 근소한 차이는 유의미한 품질 차이로 해석하기 어렵다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table">
      <thead>
        <tr>
          <th rowspan="2">모델</th>
          <th colspan="2">Judge-based Eval</th>
          <th colspan="2">Reference Match</th>
          <th colspan="2">Output Control</th>
        </tr>
        <tr>
          <th>Preference</th>
          <th>Score</th>
          <th>Char F1</th>
          <th>ROUGE-L</th>
          <th>Avg chars</th>
          <th>Violation</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Gemma4</strong></td>
          <td class="is-better">0.70</td>
          <td class="is-better">6.25</td>
          <td>0.5532</td>
          <td>0.3175</td>
          <td class="is-better">353.2</td>
          <td class="is-better">0.11</td>
        </tr>
        <tr>
          <td><strong>Gemma3</strong></td>
          <td>0.30</td>
          <td>4.86</td>
          <td class="is-better">0.5644</td>
          <td class="is-better">0.3268</td>
          <td>516.9</td>
          <td>0.90</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> Base 조건의 100문항 비교다. <code>Reference Match</code> 차이는 작았고, 더 뚜렷한 차이는 <code>Judge Preference</code>와 출력 제약 준수에서 나타났다.</figcaption>
</figure>

<figure class="sample-compare">
  <div class="sample-compare__question">
    <strong>Base sample</strong>
    <p>구급차나 경찰차는 왜 특정한 색을 사용하는 걸까요?</p>
  </div>
  <div class="sample-compare__grid">
    <article class="sample-compare__card">
      <div class="sample-compare__label">Gemma4</div>
      <div class="sample-compare__body">
        <p>차량의 색상은 각 차량의 기능과 역할을 시각적으로 명확하게 구분하고 긴급 상황에서 높은 주목도를 확보하기 위해 사용됩니다. 구급차가 흰색을 주로 사용하는 것은 의료 서비스의 전문성과 신뢰성을 전달하며, 경찰차가 흰색과 파란색 또는 빨간색을 사용하는 것은 법 집행 및 공공 안전 유지라는 권위적인 역할을 나타내기 위함입니다.</p>
      </div>
      <div class="sample-compare__scores" aria-label="Gemma4 sample scores">
        <div class="sample-compare__score-bar" style="--score: 80%;">
          <span>Judge Score</span>
          <i aria-hidden="true"><b></b></i>
          <strong>8/10</strong>
        </div>
        <div class="sample-compare__score-bar" style="--score: 63.4%;">
          <span>Char F1</span>
          <i aria-hidden="true"><b></b></i>
          <strong>0.634</strong>
        </div>
        <div class="sample-compare__score-bar" style="--score: 100%;">
          <span>Format</span>
          <i aria-hidden="true"><b></b></i>
          <strong>Pass</strong>
        </div>
      </div>
    </article>
    <article class="sample-compare__card">
      <div class="sample-compare__label">Gemma3</div>
      <div class="sample-compare__body">
        <p>구급차, 경찰차, 소방차 등 특정 색상이 사용되는 이유는 안전과 인지도를 높이기 위한 전통적인 이유와 심리적인 효과가 결합된 결과입니다.</p>
        <p>1. <strong>흰색:</strong> 구급차와 경찰차의 흰색은 ‘상징적인 색’으로, 멀리서도 쉽게 눈에 띄어 사람들에게 신속하게 접근해야 하는 긴급 상황의 차량임을 알려줍니다.</p>
      </div>
      <div class="sample-compare__scores" aria-label="Gemma3 sample scores">
        <div class="sample-compare__score-bar is-weak" style="--score: 30%;">
          <span>Judge Score</span>
          <i aria-hidden="true"><b></b></i>
          <strong>3/10</strong>
        </div>
        <div class="sample-compare__score-bar" style="--score: 56.5%;">
          <span>Char F1</span>
          <i aria-hidden="true"><b></b></i>
          <strong>0.565</strong>
        </div>
        <div class="sample-compare__score-bar is-fail" style="--score: 0%;">
          <span>Format</span>
          <i aria-hidden="true"><b></b></i>
          <strong>Fail</strong>
        </div>
      </div>
    </article>
  </div>
  <figcaption><strong>Sample 1.</strong> Base 단계의 실제 답변 일부다. Gemma3가 더 길고 구조화된 답을 내기도 했지만, 이 조건에서는 Markdown과 번호 매기기를 쓰지 말라는 지시를 어겼다. 이런 형식 위반과 장황함이 점수 차이에 영향을 준 것으로 해석할 수 있다.</figcaption>
</figure>

## SFT: 성능과 학습 효율

### 성능 비교

QLoRA learning curve에서는 base부터 step500까지 같은 평가셋으로 비교했다. `Judge Preference` 기준으로는 모든 stage에서 Gemma4가 우세했다. step50에서 `0.92`, step200에서 `0.85`, step500에서 `0.79`를 기록했다.

다만 자동 지표는 한 방향으로만 움직이지 않았다. `ROUGE-L`은 두 모델이 비슷한 범위에서 오갔고, step200과 step500에서는 Gemma3가 아주 근소하게 높았다. 그래서 이 결과는 "Gemma4가 모든 숫자에서 이겼다"가 아니라, "SFT 후 `Judge Preference`와 출력 제어는 Gemma4 쪽으로 기울었고, reference match 차이는 유의미한 품질 차이로 보기 어려웠다"로 읽는 편이 정확하다.

> **SFT 후 품질 차이는 Judge Preference에서 더 분명했다**
>
> Gemma4는 learning curve와 100-step 구성 비교 모두에서 더 자주 선택됐다. 반면 `ROUGE-L` 차이는 작아서 품질 우세의 근거로 삼기 어렵다. 따라서 SFT 성능 비교의 중심은 기준 답안 유사도가 아니라 `Judge Preference`와 출력 제어다.

<figure class="media-figure">
  <img src="/assets/images/posts/gemma3-e4b-korean-sft/sft-learning-curve.svg" alt="QLoRA SFT 단계별 Judge Preference와 ROUGE-L 비교">
  <figcaption><strong>Figure 2.</strong> QLoRA learning curve를 두 지표로 나눠 본 결과다. 왼쪽 <code>Judge Preference</code>는 같은 질문에서 judge가 해당 모델 답변을 선택한 비율이고, 오른쪽 <code>ROUGE-L</code>은 reference 답안과의 overlap이다. 두 패널은 축 범위가 다르므로 각 패널 안에서 방향성을 읽어야 한다. <code>Judge Preference</code>는 Gemma4 쪽으로 뚜렷했지만, ROUGE-L 차이는 유의미한 품질 차이로 보기 어려웠다.</figcaption>
</figure>

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table">
      <thead>
        <tr>
          <th rowspan="2">Stage</th>
          <th colspan="2">Judge Preference</th>
          <th colspan="2">ROUGE-L</th>
          <th colspan="2">Violation</th>
        </tr>
        <tr>
          <th>Gemma4</th>
          <th>Gemma3</th>
          <th>Gemma4</th>
          <th>Gemma3</th>
          <th>Gemma4</th>
          <th>Gemma3</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>base</strong></td>
          <td class="is-better">0.70</td>
          <td>0.30</td>
          <td>0.3175</td>
          <td class="is-better">0.3268</td>
          <td class="is-better">0.11</td>
          <td>0.90</td>
        </tr>
        <tr>
          <td><strong>step50</strong></td>
          <td class="is-better">0.92</td>
          <td>0.08</td>
          <td class="is-better">0.3219</td>
          <td>0.2942</td>
          <td class="is-better">0.05</td>
          <td>0.53</td>
        </tr>
        <tr>
          <td><strong>step200</strong></td>
          <td class="is-better">0.85</td>
          <td>0.15</td>
          <td>0.3270</td>
          <td class="is-better">0.3329</td>
          <td class="is-better">0.09</td>
          <td>0.24</td>
        </tr>
        <tr>
          <td><strong>step500</strong></td>
          <td class="is-better">0.79</td>
          <td>0.21</td>
          <td>0.3289</td>
          <td class="is-better">0.3326</td>
          <td class="is-better">0.09</td>
          <td>0.17</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> QLoRA learning curve 결과다. <code>Violation</code>은 출력 형식 제약을 어긴 비율이다. 낮을수록 좋다.</figcaption>
</figure>

100-step SFT 구성 비교는 답안 다양성 효과와 단순 반복 효과를 분리하기 위해 세 조건으로 나눴다.

- 단일 답안(`single`): 질문마다 기준 답안 1개만 붙인 기본 구성
- 다중 답안(`multi`): 같은 질문에 여러 답안 변형을 붙여 답안 다양성을 늘린 구성
- 반복 대조군(`duplicate`): `multi`와 row 수를 맞추기 위해 `single` 데이터를 반복한 대조 구성

이 비교에서도 `Judge Preference`와 `Judge Score`는 Gemma4가 우세했다. 단일 답안, 다중 답안, 반복 대조군 모두 Gemma4가 더 자주 선택됐고, `Judge Score`도 더 높았다. 다만 다중 답안 조건에서는 Gemma3의 `Judge Preference`가 `0.0667`에서 `0.3333`으로 올라 격차가 줄었다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table">
      <thead>
        <tr>
          <th rowspan="2">SFT 구성</th>
          <th rowspan="2">Model</th>
          <th colspan="2">Judge-based Eval</th>
        </tr>
        <tr>
          <th>Preference</th>
          <th>Score</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>single</strong></td>
          <td><strong>Gemma4</strong></td>
          <td class="is-better">0.9333</td>
          <td class="is-better">7.1333</td>
        </tr>
        <tr>
          <td><strong>single</strong></td>
          <td><strong>Gemma3</strong></td>
          <td>0.0667</td>
          <td>3.8333</td>
        </tr>
        <tr>
          <td><strong>multi</strong></td>
          <td><strong>Gemma4</strong></td>
          <td class="is-better">0.6667</td>
          <td class="is-better">6.4667</td>
        </tr>
        <tr>
          <td><strong>multi</strong></td>
          <td><strong>Gemma3</strong></td>
          <td>0.3333</td>
          <td>5.4667</td>
        </tr>
        <tr>
          <td><strong>duplicate</strong></td>
          <td><strong>Gemma4</strong></td>
          <td class="is-better">0.9667</td>
          <td class="is-better">7.7667</td>
        </tr>
        <tr>
          <td><strong>duplicate</strong></td>
          <td><strong>Gemma3</strong></td>
          <td>0.0333</td>
          <td>3.7000</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> QLoRA 100-step SFT 구성별 <code>Judge Preference</code>와 <code>Judge Score</code> 비교다. 다중 답안 조건에서는 격차가 줄었지만, 선택률과 평균 점수는 세 구성 모두 Gemma4가 높았다.</figcaption>
</figure>

다중 답안 조건은 별도로 볼 만하다. 같은 질문에 여러 답안 변형을 보여줬을 때 Gemma3의 `Judge Preference`는 `0.0667 -> 0.3333`으로 올랐다. Gemma4도 여전히 이겼지만 `0.9333 -> 0.6667`로 격차가 줄었다. 그래서 Gemma3는 답안 다양성에 더 크게 반응한 것으로 보인다. 다만 그것이 최종 품질 우세로 전환되지는 않았다.

<figure class="sample-compare">
  <div class="sample-compare__question">
    <strong>SFT sample</strong>
    <p>여름에도 계곡이 시원한 이유는 무엇인가요? 계곡은 다른 물과 비교해서 왜 더 시원한 걸까요?</p>
  </div>
  <div class="sample-compare__grid">
    <article class="sample-compare__card">
      <div class="sample-compare__label">Gemma4</div>
      <div class="sample-compare__body">
        <p>계곡물이 다른 물보다 더 시원한 이유는 지표수를 따라 흐르면서 지하 깊은 곳에서 차가워진 물이 지표로 솟아나오기 때문이야. 이 과정에서 물은 오랜 시간 동안 땅속을 흐르면서 온도를 낮추고, 주변 공기와 접촉하면서 더 차가워져. 또한, 계곡은 주변 산림의 영향을 많이 받아서 그늘이 지고 바람이 잘 통하지 않아 더 시원하게 느껴지는 거야. 그래서 계곡물은 다른 물보다 더 시원하고 깨끗한 특성을 가지고 있지.</p>
      </div>
      <div class="sample-compare__scores" aria-label="Gemma4 SFT sample scores">
        <div class="sample-compare__score-bar" style="--score: 90%;">
          <span>Judge Score</span>
          <i aria-hidden="true"><b></b></i>
          <strong>9/10</strong>
        </div>
        <div class="sample-compare__score-bar" style="--score: 59.3%;">
          <span>Char F1</span>
          <i aria-hidden="true"><b></b></i>
          <strong>0.593</strong>
        </div>
        <div class="sample-compare__score-bar" style="--score: 100%;">
          <span>Format</span>
          <i aria-hidden="true"><b></b></i>
          <strong>Pass</strong>
        </div>
      </div>
    </article>
    <article class="sample-compare__card">
      <div class="sample-compare__label">Gemma3</div>
      <div class="sample-compare__body">
        <p>계곡은 다른 물보다 시원한 이유는 지표면과 지하수면의 온도 차이 때문입니다. 지표면은 햇빛을 직접 받아 열이 가해지기 때문에 온도가 높고, 지하수면은 지표면보다 깊이 들어가 있어 햇빛을 받지 못하고 온도가 낮습니다. 따라서 계곡의 물은 지표면보다 온도가 낮아 시원하게 느껴집니다.</p>
      </div>
      <div class="sample-compare__scores" aria-label="Gemma3 SFT sample scores">
        <div class="sample-compare__score-bar is-weak" style="--score: 70%;">
          <span>Judge Score</span>
          <i aria-hidden="true"><b></b></i>
          <strong>7/10</strong>
        </div>
        <div class="sample-compare__score-bar is-weak" style="--score: 54.8%;">
          <span>Char F1</span>
          <i aria-hidden="true"><b></b></i>
          <strong>0.548</strong>
        </div>
        <div class="sample-compare__score-bar" style="--score: 100%;">
          <span>Format</span>
          <i aria-hidden="true"><b></b></i>
          <strong>Pass</strong>
        </div>
      </div>
    </article>
  </div>
  <figcaption><strong>Sample 2.</strong> step500 SFT 후 샘플이다. 두 모델 모두 형식은 지켰다. Gemma4는 더 많은 요인을 연결해 설명했지만 일부 표현은 거칠고, Gemma3는 온도 차이 중심으로 더 짧게 답했다.</figcaption>
</figure>

### 학습 효율 비교

학습 효율도 위 세 구성의 100-step SFT 조건에서 비교했다. loss는 모델 간 절대값을 그대로 품질 순위로 바꾸면 안 된다. tokenizer와 출력 분포가 다르기 때문이다. 여기서는 같은 모델 안에서 loss가 내려갔는지, 그리고 같은 100-step 조건에서 어느 쪽이 더 빠르게 학습을 마쳤는지를 봤다.

> **둘 다 학습됐지만, 같은 step은 Gemma4가 더 빨랐다**
>
> loss 감소는 양쪽 모델 모두에서 SFT가 실제로 진행됐다는 확인용 신호다. 효율 비교에서 더 직접적인 차이는 runtime이었다. 같은 100-step 조건을 끝내는 데 걸린 시간은 세 구성 모두 Gemma4가 짧았다.

<figure class="media-figure">
  <img src="/assets/images/posts/gemma3-e4b-korean-sft/sft-efficiency.svg" alt="QLoRA 100-step SFT의 loss remaining과 runtime 비교">
  <figcaption><strong>Figure 3.</strong> DGX Spark GB10에서 측정한 100-step QLoRA SFT 결과다. 왼쪽은 loss가 같은 run 안에서 얼마나 남았는지 보는 sanity check이고, 오른쪽은 같은 100-step을 끝내는 데 걸린 시간이다.</figcaption>
</figure>

Figure 3의 `Loss Remaining`은 마지막 step loss가 첫 step loss의 몇 퍼센트로 남았는지를 뜻한다. 낮을수록 같은 run 안에서 loss가 더 많이 줄었다는 의미지만, 모델 간 절대 품질 비교로 읽으면 안 된다. 여기서는 SFT가 실제로 진행됐는지 확인하는 sanity check로만 사용했다.

결과는 두 가지로 읽을 수 있다. 먼저 세 구성 모두에서 마지막 step loss가 첫 step loss보다 크게 낮아졌으므로, 양쪽 모델 모두 SFT가 진행됐다는 점은 확인된다. 그러나 같은 100-step을 끝내는 시간은 모든 구성에서 Gemma4가 짧았다. 단일 답안은 `1348s` 대 `2411s`, 다중 답안은 `1427s` 대 `2682s`, 반복 대조군은 `1510s` 대 `2683s`였다. 따라서 이 실험에서 학습 효율 차이는 loss의 절대값이 아니라 runtime에서 더 분명하게 나타났다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table">
      <thead>
        <tr>
          <th rowspan="2">SFT 구성</th>
          <th rowspan="2">Model</th>
          <th colspan="3">Training Signal</th>
        </tr>
        <tr>
          <th>Step loss first->last</th>
          <th>Train loss</th>
          <th>Runtime</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>single</strong></td>
          <td><strong>Gemma4</strong></td>
          <td>16.05 -> 0.42</td>
          <td>2.3239</td>
          <td class="is-better">1348s</td>
        </tr>
        <tr>
          <td><strong>single</strong></td>
          <td><strong>Gemma3</strong></td>
          <td>4.33 -> 0.04</td>
          <td>0.9212</td>
          <td>2411s</td>
        </tr>
        <tr>
          <td><strong>multi</strong></td>
          <td><strong>Gemma4</strong></td>
          <td>16.36 -> 1.23</td>
          <td>2.6546</td>
          <td class="is-better">1427s</td>
        </tr>
        <tr>
          <td><strong>multi</strong></td>
          <td><strong>Gemma3</strong></td>
          <td>4.25 -> 0.57</td>
          <td>1.2520</td>
          <td>2682s</td>
        </tr>
        <tr>
          <td><strong>duplicate</strong></td>
          <td><strong>Gemma4</strong></td>
          <td>16.54 -> 0.51</td>
          <td>2.4186</td>
          <td class="is-better">1510s</td>
        </tr>
        <tr>
          <td><strong>duplicate</strong></td>
          <td><strong>Gemma3</strong></td>
          <td>4.52 -> 0.04</td>
          <td>0.9257</td>
          <td>2683s</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 5.</strong> QLoRA 100-step SFT의 학습 신호와 runtime이다. 두 모델 모두 loss는 내려갔지만, 같은 step을 끝내는 데 걸린 시간은 Gemma4가 더 짧았다.</figcaption>
</figure>

## 노이즈: 질문이 흔들릴 때

노이즈 실험에서는 SFT된 모델에 실제 사용자 입력 오류에 가까운 질문을 넣어 봤다. 여기서 손상은 시스템 프롬프트나 템플릿이 아니라 질문 본문에만 적용했다. `Real typo`는 타이핑 오타와 띄어쓰기 붕괴, `ASR noise`는 음성 전사체처럼 구두점이 사라지거나 발음 유사 표현이 섞인 입력이다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>Noise</th>
          <th>무엇을 흉내 냈나</th>
          <th>예시</th>
          <th>해석 범위</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Real typo</strong></td>
          <td>사람이 직접 입력할 때 생기는 오타와 띄어쓰기 붕괴</td>
          <td><code>저작권이 있나요</code> -> <code>저작권이 나있요</code></td>
          <td>타이핑 실수에 가까운 입력 손상</td>
        </tr>
        <tr>
          <td><strong>ASR noise</strong></td>
          <td>음성 인식 전사체처럼 구두점이 사라지거나 발음 유사 표현이 섞인 입력</td>
          <td><code>어떻게 되나요</code> -> <code>어떡해되나요</code></td>
          <td>말을 텍스트로 옮기는 과정의 가벼운 전사 오류</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 6.</strong> 현실형 노이즈 2종의 의미다. 두 조건 모두 질문 본문만 흔들고, 시스템 프롬프트와 출력 형식 제약은 그대로 유지했다.</figcaption>
</figure>

결과는 두 층으로 읽어야 한다. 두 현실형 노이즈 조건 모두에서 raw 입력보다 손상 입력의 `Readability` 점수가 낮아졌다. 중요한 점은 손상된 입력 상태의 절대 `Readability`가 Gemma4 쪽에 더 높게 남았다는 것이다. 두 가지 현실형 노이즈 평균에서 Gemma4는 `5.50`, Gemma3는 `3.93`이었다.

> **둘 다 흔들렸지만, 흔들린 뒤의 품질은 Gemma4가 높았다**
>
> 이 실험은 노이즈가 성능을 올리는지 보는 것이 아니다. 원래 질문과 손상 질문을 같은 모델 안에서 비교하고, 손상된 입력에서도 답변이 얼마나 읽을 만하게 남는지를 `Readability`로 본다. 두 현실형 노이즈 조건에서 손상 입력의 `Readability` 평균은 Gemma4가 더 높았다.

<figure class="media-figure">
  <img src="/assets/images/posts/gemma3-e4b-korean-sft/robustness-contrast.svg" alt="손상 질문에서 모델별 Readability 평균과 raw 대비 변화량 비교">
  <figcaption><strong>Figure 4.</strong> 왼쪽 패널은 손상 입력 답변의 <code>Readability</code> 평균, 즉 Table 7의 <code>Readability</code> 값이다. 높을수록 손상된 질문에서도 답변이 더 읽기 좋게 남았다는 뜻이다. 오른쪽 패널은 같은 질문셋에서 <code>Noise Avg - Raw Avg</code>로 계산한 raw 대비 변화량이다. 0에 가까울수록 raw 대비 하락폭이 작다.</figcaption>
</figure>

따라서 노이즈 결과는 Figure 4의 두 패널을 함께 봐야 한다. 왼쪽은 손상된 입력을 받았을 때 어느 모델 답변이 더 읽을 만하게 남았는지를 보여준다. 오른쪽은 같은 모델 안에서 raw 대비 얼마나 흔들렸는지를 보여준다. 이 둘은 같은 결론을 말하는 지표가 아니다.

Table 7은 손상 입력에서의 모델 간 차이를 원래 평가 지표 중심으로 다시 정리한 것이다. 같은 손상 질문에 대해 `gpt-oss-120b`가 1-10점으로 평가한 `Readability`, 기준 답안 overlap인 `Char F1`, 출력 형식 위반율인 `Violation`을 나란히 놓았다. raw 대비 하락폭은 Figure 4의 오른쪽 패널에서 따로 보고, 이 표에서는 손상된 입력을 받은 뒤 어느 모델의 답변이 더 읽을 만하게 남았는지를 본다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table">
      <thead>
        <tr>
          <th rowspan="2">Noise</th>
          <th colspan="2">Readability</th>
          <th colspan="2">Char F1</th>
          <th colspan="2">Violation</th>
        </tr>
        <tr>
          <th>G4</th>
          <th>G3</th>
          <th>G4</th>
          <th>G3</th>
          <th>G4</th>
          <th>G3</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Real typo</td>
          <td class="is-better">5.32</td>
          <td>3.86</td>
          <td class="is-better">0.542</td>
          <td>0.474</td>
          <td class="is-better">0.14</td>
          <td>0.32</td>
        </tr>
        <tr>
          <td>ASR noise</td>
          <td class="is-better">5.68</td>
          <td>4.00</td>
          <td class="is-better">0.534</td>
          <td>0.496</td>
          <td class="is-better">0.16</td>
          <td>0.26</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 7.</strong> 현실형 손상 질문 2종의 모델 간 비교다. <code>G4</code>와 <code>G3</code>는 각각 Gemma4와 Gemma3를 줄인 표기다. <code>Readability</code>는 <code>gpt-oss-120b</code>가 평가한 1-10점 평균이고, <code>Char F1</code>은 기준 답안 overlap이다. 둘은 높을수록 좋고, <code>Violation</code>은 낮을수록 좋다. raw 대비 변화량은 Figure 4의 오른쪽 패널에서 따로 본다.</figcaption>
</figure>

<figure class="sample-compare">
  <div class="sample-compare__question">
    <strong>Realistic noise sample</strong>
    <p>아로마와 허브의 차ㅣ는엇뭐인가요? 아직도 아로마에포함될 수 있는 식물들이 더 추가될 수 있나요?</p>
  </div>
  <div class="sample-compare__grid">
    <article class="sample-compare__card">
      <div class="sample-compare__label">Gemma4</div>
      <div class="sample-compare__body">
        <p>아로마는 식물에서 추출한 에센셜 오일의 향을 말하며, 이 향을 이용해 심신 안정, 스트레스 완화, 기분 전환 등에 도움을 주는 것입니다. 반면에 허브는 식물의 줄기, 잎, 꽃, 열매 등을 약재나 향료로 사용하는 것입니다. 아로마테라피는 식물에서 추출한 에센셜 오일의 향을 이용하여 심신 안정, 스트레스 완화, 기분 전환 등에 도움을 주는 것으로, 식물 전체를 사용하는 것이 아니라 그 향을 이용하는 것입니다. 따라서 아로마와 허브는 서로 다른 개념으로, 식물 전체를 사용하는 것이 아니라 그 향을 이용하는 것이 아로마테라피의 핵심입니다.</p>
      </div>
      <div class="sample-compare__scores" aria-label="Gemma4 realistic noise sample scores">
        <div class="sample-compare__score-bar" style="--score: 70%;">
          <span>Readability</span>
          <i aria-hidden="true"><b></b></i>
          <strong>7/10</strong>
        </div>
        <div class="sample-compare__score-bar" style="--score: 59.5%;">
          <span>Char F1</span>
          <i aria-hidden="true"><b></b></i>
          <strong>0.595</strong>
        </div>
        <div class="sample-compare__score-bar" style="--score: 100%;">
          <span>Length</span>
          <i aria-hidden="true"><b></b></i>
          <strong>Pass</strong>
        </div>
      </div>
    </article>
    <article class="sample-compare__card">
      <div class="sample-compare__label">Gemma3</div>
      <div class="sample-compare__body">
        <p>아로마와 허브는 같은 의미로 사용되지만, 아로마는 향기로운 식물 전체를 가리키는 용어이고, 허브는 향기로운 식물의 종류 중 하나입니다. 따라서, 아로마는 향기로운 식물 전체를 가리키는 용어이며, 허브는 향기로운 식물의 종류 중 하나입니다. 아로마에 포함될 수 있는 식물들은 아직도 추가될 가능성이 있습니다.</p>
      </div>
      <div class="sample-compare__scores" aria-label="Gemma3 realistic noise sample scores">
        <div class="sample-compare__score-bar is-weak" style="--score: 60%;">
          <span>Readability</span>
          <i aria-hidden="true"><b></b></i>
          <strong>6/10</strong>
        </div>
        <div class="sample-compare__score-bar is-weak" style="--score: 43.6%;">
          <span>Char F1</span>
          <i aria-hidden="true"><b></b></i>
          <strong>0.436</strong>
        </div>
        <div class="sample-compare__score-bar is-weak" style="--score: 100%;">
          <span>Length</span>
          <i aria-hidden="true"><b></b></i>
          <strong>Pass</strong>
        </div>
      </div>
    </article>
  </div>
  <figcaption><strong>Sample 3.</strong> 같은 Real typo 입력에 대한 Gemma4와 Gemma3의 실제 답변이다. 노이즈 전 원 질문은 “아로마와 허브의 차이는 무엇인가요? 아직도 아로마에 포함될 수 있는 식물들이 더 추가될 수 있나요?”였다. 두 모델 모두 답변 형식은 지켰지만, Gemma4는 아로마를 향과 추출물 중심으로, 허브를 식물 부위와 활용 중심으로 나누어 설명했다. Gemma3는 답변이 무너지지는 않았지만 아로마와 허브의 관계를 반복적으로 단순화해 개념 구분이 덜 선명했다.</figcaption>
</figure>

## 결론

이 비교에서 가장 안정적으로 남는 결론은 단순하다. Gemma4는 base와 SFT 모두에서 `Judge Preference`와 `Judge Score`, 출력 형식 제어, 현실형 질문 손상 조건의 절대 `Readability`에서 더 강했다. SFT도 실제로 진행됐고, 100-step SFT 조건에서는 runtime도 더 짧았다.

Gemma3의 장점은 더 좁게 써야 한다. `ROUGE-L`과 `Char F1`에서 보인 차이는 작아서 유의미한 품질 우세로 해석하기 어렵다. 더 분명하게 남는 신호는 같은 질문에 여러 답안 변형을 보여준 학습에서 개선폭이 더 크게 나타났다는 점이다. 하지만 그것도 최종 품질 우세나 일반적인 노이즈 안정성 우세로 넓히면 과장된다.

> 4B급 한국어 SFT 비교에서 Gemma4는 `Judge Preference`, `Judge Score`, 형식 제어, 학습 효율, 현실형 질문 손상 조건의 절대 `Readability`에서 더 일관되게 앞섰다. Gemma3는 답안 다양성에 더 크게 반응하는 모습이 있었지만, 기준 답안 유사도 차이는 품질 우세로 보기 어려웠다.

## Appendix: 실험 조건

본문에는 결론을 읽는 데 필요한 수치만 남겼다. 재현을 위해 필요한 조건은 아래에 따로 정리한다. 핵심은 같은 데이터 분할과 같은 판정 조건에서 `base`, `SFT`, 질문 본문 손상 평가를 분리해 본 것이다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>항목</th>
          <th>조건</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>비교 모델</strong></td>
          <td><code>google/gemma-4-E4B-it</code>, <code>google/gemma-3-4b-it</code></td>
        </tr>
        <tr>
          <td><strong>데이터셋</strong></td>
          <td><code>beomi/KoAlpaca-v1.1a</code>, <code>train</code> split</td>
        </tr>
        <tr>
          <td><strong>분할 방식</strong></td>
          <td><code>random_holdout</code>, <code>split_seed = 42</code>, 같은 평가 index 사용</td>
        </tr>
        <tr>
          <td><strong>Base / learning curve 평가</strong></td>
          <td>100문항 holdout, <code>base</code>, <code>step50</code>, <code>step200</code>, <code>step500</code> 비교</td>
        </tr>
        <tr>
          <td><strong>SFT 구성 비교 평가</strong></td>
          <td>30문항 holdout, <code>single</code>, <code>multi</code>, <code>duplicate</code> arm 비교</td>
        </tr>
        <tr>
          <td><strong>질문 본문 손상 평가</strong></td>
          <td>50문항 holdout, <code>raw</code>, <code>real_typo</code>, <code>asr_noise</code> 비교</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 1.</strong> 공통 데이터와 평가 분할 조건이다. 본문 수치는 모두 같은 seed와 holdout 방식에서 나온 결과만 사용했다.</figcaption>
</figure>

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>항목</th>
          <th>조건</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Judge 모델</strong></td>
          <td><code>gpt-oss-120b</code> GGUF를 <code>llama.cpp</code> server로 실행</td>
        </tr>
        <tr>
          <td><strong>Preference 산출 방식</strong></td>
          <td>두 답변을 pairwise로 제시하고 순서를 섞은 뒤 더 나은 답을 선택</td>
        </tr>
        <tr>
          <td><strong>Reference 노출</strong></td>
          <td>핵심 모델 간 비교는 <code>blind_to_reference</code>로 진행</td>
        </tr>
        <tr>
          <td><strong>Judge 실행 설정</strong></td>
          <td><code>reasoning_effort = low</code>, <code>judge_concurrency = 2</code>, <code>judge_max_tokens = 1024</code></td>
        </tr>
        <tr>
          <td><strong>자동 지표</strong></td>
          <td><code>Char F1</code>, <code>ROUGE-L F1</code>; 기준 답안과의 표현 overlap 측정</td>
        </tr>
        <tr>
          <td><strong>Readability 산출</strong></td>
          <td>같은 <code>gpt-oss-120b</code>로 각 답변을 1-10점 채점; 본문에는 손상 입력 답변의 <code>Readability</code> 평균과 raw 대비 변화량을 사용</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 2.</strong> 평가 지표와 판정 조건이다. <code>Judge Preference</code>는 절대 점수가 아니라 같은 질문에서 두 답변 중 선택된 비율이다.</figcaption>
</figure>

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>항목</th>
          <th>조건</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>학습 방식</strong></td>
          <td>QLoRA SFT; 4-bit로 base model을 load한 뒤 LoRA adapter만 학습</td>
        </tr>
        <tr>
          <td><strong>Quantization</strong></td>
          <td><code>BitsAndBytesConfig(load_in_4bit = true)</code>, <code>nf4</code>, double quant, <code>bfloat16</code> compute</td>
        </tr>
        <tr>
          <td><strong>Adapter 설정</strong></td>
          <td><code>r = 16</code>, <code>lora_alpha = 32</code>, <code>lora_dropout = 0.05</code>, <code>bias = none</code></td>
        </tr>
        <tr>
          <td><strong>Adapter 대상</strong></td>
          <td>text <code>language_model</code>의 attention/MLP projection 계열에만 adapter 부착</td>
        </tr>
        <tr>
          <td><strong>K-bit 학습 준비</strong></td>
          <td><code>prepare_model_for_kbit_training</code>, <code>bf16 = true</code>, gradient checkpointing 사용</td>
        </tr>
        <tr>
          <td><strong>SFT step</strong></td>
          <td>learning curve는 <code>step50</code>, <code>step200</code>, <code>step500</code>; SFT 구성 비교는 100-step</td>
        </tr>
        <tr>
          <td><strong>학습 데이터 구성</strong></td>
          <td><code>single</code> 100 rows, <code>multi</code> 300 rows, <code>duplicate</code> 300 rows</td>
        </tr>
        <tr>
          <td><strong>100-step SFT batch</strong></td>
          <td><code>per_device_batch_size = 16</code>, <code>gradient_accumulation_steps = 1</code>, <code>max_length = 1024</code></td>
        </tr>
        <tr>
          <td><strong>출력 형식 제약</strong></td>
          <td>한국어 일반 문장, Markdown/표/제목/목록/불릿/코드/굵게 금지, 한 문단 400자 이내, 5문장 제한</td>
        </tr>
        <tr>
          <td><strong>생성 설정</strong></td>
          <td><code>max_new_tokens = 512</code>, <code>generation_batch_size = 16</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 3.</strong> QLoRA SFT와 생성 조건이다. 서로 다른 모델의 절대 loss는 품질 비교가 아니라 학습이 실제로 일어났는지 확인하는 sanity check로만 사용했다.</figcaption>
</figure>

## Citation

이 글을 인용할 때는 아래 형식을 사용할 수 있다.

```text
Ilho Ahn, "4B급 Gemma3와 Gemma4 한국어 SFT 비교: 품질, 학습, 노이즈", Mini Research, Apr 2026.
```

또는 BibTeX 형식으로는 다음처럼 적을 수 있다.

```bibtex
@article{ahn2026gemma3gemma4korean,
  author = {Ilho Ahn},
  title = {4B급 Gemma3와 Gemma4 한국어 SFT 비교: 품질, 학습, 노이즈},
  journal = {Mini Research},
  year = {2026},
  month = apr,
  url = {https://muted-color.github.io/research/2026/04/12/gemma3-e4b-korean-sft/}
}
```
