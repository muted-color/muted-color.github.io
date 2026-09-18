---
title: "Gemma3 4B와 Gemma4 E4B의 한국어 SFT 비교"
date: 2026-04-12 09:00:00 +0900
last_modified_at: 2026-09-06 08:39:03 +0900
lang: ko
categories: ["LLM EVAL"]
tags: [gemma, korean, sft, eval]
excerpt: "한국어 holdout에서 Gemma3 4B와 Gemma4 E4B의 추가 SFT, 답안 구성, 입력 노이즈를 비교했다. Judge 선택률·형식 준수와 표현 중복, 절대 점수·하락폭을 구분해 해석한다."
description: "Gemma3 4B와 Gemma4 E4B의 한국어 SFT 비교에서 Gemma4의 judge 선택률과 형식 준수가 높았지만, 답안 다양성 효과와 일반적 강건성은 분리해 해석해야 했다."
permalink: /research/2026/04/12/gemma3-e4b-korean-sft/
image: /assets/images/posts/gemma3-e4b-korean-sft/social-thumbnail.png
image_alt: "Gemma3와 Gemma4 한국어 SFT 비교 결과를 질문별 evidence map으로 요약한 소셜 썸네일"
hero_image: /assets/images/posts/gemma3-e4b-korean-sft/evidence-map.svg
hero_alt: "Gemma4와 Gemma3 한국어 비교의 핵심 질문별 결과 요약"
hero_caption: "<strong>Figure 1.</strong> 기록된 결과의 요약. 행마다 척도가 다르므로 같은 행 안에서만 비교한다. Format alignment는 형식 준수율이며, Noise readability는 두 손상 조건의 평균이다. Training speed는 100-step 소요시간의 역비율(Gemma3/Gemma4)을 약 1.8배로 요약한 값으로, 토큰 처리량 측정이 아니다. <a href='/assets/images/posts/gemma3-e4b-korean-sft/evidence-map.svg'>그림 원본 크게 보기</a>."
---

한국어 instruction 응답 비교에서는 답변 내용과 출력 형식이 같은 judge 점수에 반영될 수 있다. 이 글은 Gemma3 4B와 Gemma4 E4B를 추가 지도 미세조정(supervised fine-tuning, SFT) 전후로 비교하고, judge 선택률·기준 답안과의 표현 중복·형식 준수가 같은 방향으로 움직이는지 확인한다. 답안 구성과 입력 손상에 따른 변화도 별도로 살폈다.

## 요약

- **추가 SFT 전 100문항:** Gemma4의 Judge Preference는 0.70, Gemma3는 0.30이었다. 형식 위반율은 0.11 대 0.90으로 차이가 컸지만, judge 차이 중 형식과 내용이 각각 기여한 비중은 분리하지 않았다.
- **SFT checkpoint 비교:** Gemma4의 선택률은 step50·200·500에서 0.92·0.85·0.79였다. 학습이 길어질수록 모델 간 상대 격차가 계속 커지는 패턴은 아니었다.
- **답안 구성 30문항 비교:** 다중 답안 조건에서 모델 간 judge 격차가 줄었다. 두 모델의 답변이 함께 바뀌므로, 선택률 변화만으로 특정 모델의 답안 다양성 효과를 확정할 수 없다.
- **100-step 소요시간:** DGX Spark GB10의 세 구성 모두 Gemma4가 짧았다. 같은 step 수를 맞춘 결과이며, 총 파라미터·처리 토큰·연산량을 맞춘 효율 비교는 아니다.
- **입력 손상 50문항 비교:** 손상 후 Readability는 Gemma4가 높았지만, 원본 대비 하락폭은 Gemma3가 작았다. 절대 점수 우위와 변화에 대한 민감도는 구분해야 한다.

아래는 기존 노트에 남은 집계값·설정·답변 예시를 정리한 결과다. 이번 개정에서는 원자료 재분석이나 실험 재실행을 하지 않았으며, 반복 실행의 변동과 통계적 유의성은 확인하지 않았다.

## Experimental Setup

### 모델과 데이터

비교 대상은 Google의 instruction-tuned checkpoint `google/gemma-3-4b-it`와 `google/gemma-4-E4B-it`이다. 이 글의 **base는 추가 SFT 전 상태**를 뜻하며, 사전학습 전용 모델을 뜻하지 않는다. [[1]](#ref-gemma3), [[2]](#ref-gemma4)

{% include model-mention-cards.html label="비교 대상 모델" aria_label="비교 대상 Hugging Face 모델" models="Gemma3 4B|google/gemma-3-4b-it|https://huggingface.co/google/gemma-3-4b-it;Gemma4 E4B|google/gemma-4-E4B-it|https://huggingface.co/google/gemma-4-E4B-it" %}

> Gemma4 E4B의 E는 effective를 뜻한다. 공식 모델카드는 4.5B effective, 임베딩을 포함하면 8B로 기재한다. 따라서 두 모델의 총 파라미터 수를 맞춘 비교로 해석할 수 없다. 이하에서는 각각 Gemma3와 Gemma4로 줄여 쓴다. [[2]](#ref-gemma4)

한국어 instruction 데이터는 `beomi/KoAlpaca-v1.1a`의 train split을 사용했다. 기록된 분할 방식은 random holdout, 분할 seed는 42이며, 각 비교 안에서 두 모델에 같은 평가 index를 적용했다. 평가별 문항 수와 변경 조건은 Table 1에 정리했다. [[3]](#ref-koalpaca)

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead><tr><th>비교</th><th class="align-right">평가 문항 수</th><th>변경 조건</th><th>주요 관찰</th></tr></thead>
      <tbody>
        <tr><td><strong>Base</strong></td><td class="align-right">100</td><td>추가 SFT 전 두 모델</td><td>Judge·표현 중복·형식 준수</td></tr>
        <tr><td><strong>SFT checkpoint</strong></td><td class="align-right">100</td><td>base, step50, step200, step500</td><td>같은 평가셋에서 학습 단계별 변화</td></tr>
        <tr><td><strong>SFT 구성</strong></td><td class="align-right">30</td><td>single, multi, duplicate; 각 100-step</td><td>답안 구성에 따른 점수와 소요시간</td></tr>
        <tr><td><strong>입력 손상</strong></td><td class="align-right">50</td><td>원본, Real typo, ASR noise</td><td>손상 후 점수와 원본 대비 변화량</td></tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> 평가별 문항 수와 비교 조건. 100문항 checkpoint 평가와 30문항 구성 평가는 별도 비교이므로 선택률을 직접 이어 읽지 않는다.</figcaption>
</figure>

추가 학습에는 Dettmers et al.의 **QLoRA**를 사용했다. 4-bit로 불러온 모델의 가중치는 고정하고 LoRA adapter를 학습하는 방식이다. 기록된 adapter·batch·생성 설정은 Appendix Table 3에 모았다. [[5]](#ref-qlora)

### 출력 제약과 지표

모든 생성 평가는 한국어 일반 문장, 한 문단, 400자 이내, 최대 5문장을 요구했다. Markdown·제목·표·목록·불릿·코드·굵은 글씨는 금지했다.

판정기는 `gpt-oss-120b` GGUF를 llama.cpp로 실행했다. Judge Preference 비교에서는 기준 답안을 보여주지 않고 두 답변의 순서를 섞었다. 질문에 직접 답하는지, 사실적으로 무리한 설명이 적은지, 한국어가 자연스러운지, 출력 형식을 지키는지를 평가했다. [[4]](#ref-gpt-oss)

- **Judge Preference / Score:** Preference는 같은 질문에서 두 답변 중 선택된 비율이다. Score는 개별 답변에 부여한 1–10점의 평균이다. 형식 준수가 rubric에 포함되어 있어 내용 품질만의 지표는 아니다.
- **Char F1 / ROUGE-L F1:** 기준 답안과의 문자 중복 및 순서를 유지한 공통 부분열을 측정한다. 표현 유사도이며 사실 정확도나 완결성을 직접 검증하지 않는다. ROUGE의 출처는 Lin의 지표 논문이다. [[6]](#ref-rouge)
- **Violation:** 공통 출력 제약의 위반율로 낮을수록 좋다. Figure 1의 Format alignment는 이를 형식 준수율로 바꾼 값이다.
- **Readability:** 같은 judge가 답변별로 자연스러움·질문 의도 복원·반복과 끊김·설명의 유지 정도를 1–10점으로 평가했다. 손상 입력의 평균과 원본 입력 대비 변화량을 따로 읽는다.

## Results

### 추가 SFT 전: judge 선택률과 형식 준수

Table 2에서 Gemma4의 Preference는 0.70으로 높았고, Gemma3의 Char F1과 ROUGE-L F1은 소폭 높았다. 가장 큰 차이는 형식 위반율 0.11 대 0.90이었다. 평균 출력 길이도 353.2자 대 516.9자로 달랐다.

Judge rubric이 형식 준수를 포함하므로 선택률 차이에 형식이 기여했을 가능성이 있다. 다만 형식을 맞춘 답변끼리의 비교나 내용만의 별도 판정이 없어 그 비중은 알 수 없다. 작은 표현 중복 차이 역시 품질 우위의 근거로 충분하지 않다.

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
          <th class="align-right">Preference</th>
          <th class="align-right">Score</th>
          <th class="align-right">Char F1</th>
          <th class="align-right">ROUGE-L F1</th>
          <th class="align-right">평균 글자 수</th>
          <th class="align-right">Violation</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Gemma4</strong></td>
          <td class="is-better align-right">0.70</td>
          <td class="is-better align-right">6.25</td>
          <td class="align-right">0.5532</td>
          <td class="align-right">0.3175</td>
          <td class="align-right">353.2</td>
          <td class="is-better align-right">0.11</td>
        </tr>
        <tr>
          <td><strong>Gemma3</strong></td>
          <td class="align-right">0.30</td>
          <td class="align-right">4.86</td>
          <td class="is-better align-right">0.5644</td>
          <td class="is-better align-right">0.3268</td>
          <td class="align-right">516.9</td>
          <td class="align-right">0.90</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> 추가 SFT 전 100문항 결과. Preference는 상대 선택률, Score는 개별 답변의 1–10점 평균이다. Char F1과 ROUGE-L F1은 기준 답안과의 표현 중복을 측정하며, Violation은 낮을수록 형식 위반이 적다.</figcaption>
</figure>

Sample 1은 형식 위반이 드러나는 실제 답변 일부다. 이 사례의 점수 차이를 전체 100문항의 원인 설명으로 일반화할 수는 없다.

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
  <figcaption><strong>Sample 1.</strong> 추가 SFT 전 실제 답변 일부. Gemma3의 번호 목록과 굵은 글씨는 공통 출력 제약을 어긴다. 표시 점수는 judge의 기록이며, 개별 설명의 사실성을 별도로 검증한 결과는 아니다.</figcaption>
</figure>

### SFT checkpoint: 선택률과 표현 중복의 다른 움직임

Figure 2와 Table 3은 같은 100문항에서 base부터 step500까지 비교한 결과다. Gemma4의 Preference는 모든 checkpoint에서 높았지만, step50의 0.92에서 step500의 0.79로 낮아졌다. 이 비율은 매 단계에서 두 모델을 비교한 값이므로 한 모델의 절대 품질 변화로 읽을 수 없다. step500의 실제 출력과 judge 점수 예시는 Appendix Sample 1에 모았다.

두 모델 모두 base보다 형식 위반율이 낮아졌다. ROUGE-L F1은 step50에서 Gemma4가 높고, step200·500에서는 Gemma3가 소폭 높았다. Judge 선택률과 표현 중복이 일치하지 않는다는 관찰은 남지만, 반복 변동이 없는 이 표만으로 작은 차이의 유의성을 판정할 수는 없다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/gemma3-e4b-korean-sft/sft-learning-curve.svg" alt="QLoRA SFT 단계별 Judge Preference와 ROUGE-L 비교">
  <figcaption><strong>Figure 2.</strong> SFT checkpoint별 Preference와 ROUGE-L F1. 가로축은 base·50·200·500을 등간격으로 놓은 범주 축이므로 선의 기울기로 step당 변화 속도를 비교할 수 없다. 오른쪽 ROUGE-L F1 축은 0.29–0.34를 확대했으며, 두 패널의 척도는 다르다.</figcaption>
</figure>

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table">
      <thead>
        <tr>
          <th rowspan="2">Checkpoint</th>
          <th colspan="2">Judge Preference</th>
          <th colspan="2">ROUGE-L F1</th>
          <th colspan="2">Violation</th>
        </tr>
        <tr>
          <th class="align-right">Gemma4</th>
          <th class="align-right">Gemma3</th>
          <th class="align-right">Gemma4</th>
          <th class="align-right">Gemma3</th>
          <th class="align-right">Gemma4</th>
          <th class="align-right">Gemma3</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>base</strong></td>
          <td class="is-better align-right">0.70</td>
          <td class="align-right">0.30</td>
          <td class="align-right">0.3175</td>
          <td class="is-better align-right">0.3268</td>
          <td class="is-better align-right">0.11</td>
          <td class="align-right">0.90</td>
        </tr>
        <tr>
          <td><strong>step50</strong></td>
          <td class="is-better align-right">0.92</td>
          <td class="align-right">0.08</td>
          <td class="is-better align-right">0.3219</td>
          <td class="align-right">0.2942</td>
          <td class="is-better align-right">0.05</td>
          <td class="align-right">0.53</td>
        </tr>
        <tr>
          <td><strong>step200</strong></td>
          <td class="is-better align-right">0.85</td>
          <td class="align-right">0.15</td>
          <td class="align-right">0.3270</td>
          <td class="is-better align-right">0.3329</td>
          <td class="is-better align-right">0.09</td>
          <td class="align-right">0.24</td>
        </tr>
        <tr>
          <td><strong>step500</strong></td>
          <td class="is-better align-right">0.79</td>
          <td class="align-right">0.21</td>
          <td class="align-right">0.3289</td>
          <td class="is-better align-right">0.3326</td>
          <td class="is-better align-right">0.09</td>
          <td class="align-right">0.17</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> 동일한 100문항에서 비교한 SFT checkpoint별 집계값. Gemma4의 Preference는 step50에서 가장 높았고 이후 낮아졌다. 두 모델의 Violation은 base보다 낮았지만, 이 표는 반복 실행의 변동을 보여주지 않는다.</figcaption>
</figure>

### SFT 답안 구성: 다중 답안 조건에서 줄어든 격차

Table 4는 별도 30문항에서 평가한 100-step 비교다. 질문마다 기준 답안 하나를 둔 **single**은 100 rows, 같은 질문에 여러 답안 변형을 둔 **multi**는 300 rows였다. **duplicate**는 single을 반복해 multi와 300 rows를 맞춘 대조군이다. Batch 16과 최대 길이 1,024를 공통으로 사용했다.

Gemma4의 선택률과 평균 Score는 세 구성 모두 높았다. 다만 multi에서는 Gemma3의 Preference가 single의 0.0667에서 0.3333으로 올라 모델 간 격차가 줄었다. 개별 Score도 Gemma3는 3.8333에서 5.4667로, Gemma4는 7.1333에서 6.4667로 서로 다른 방향으로 움직였다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table">
      <thead>
        <tr>
          <th rowspan="2">SFT 구성</th>
          <th rowspan="2">모델</th>
          <th colspan="2">Judge-based Eval</th>
        </tr>
        <tr>
          <th class="align-right">Preference</th>
          <th class="align-right">Score</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>single</strong></td>
          <td><strong>Gemma4</strong></td>
          <td class="is-better align-right">0.9333</td>
          <td class="is-better align-right">7.1333</td>
        </tr>
        <tr>
          <td><strong>single</strong></td>
          <td><strong>Gemma3</strong></td>
          <td class="align-right">0.0667</td>
          <td class="align-right">3.8333</td>
        </tr>
        <tr>
          <td><strong>multi</strong></td>
          <td><strong>Gemma4</strong></td>
          <td class="is-better align-right">0.6667</td>
          <td class="is-better align-right">6.4667</td>
        </tr>
        <tr>
          <td><strong>multi</strong></td>
          <td><strong>Gemma3</strong></td>
          <td class="align-right">0.3333</td>
          <td class="align-right">5.4667</td>
        </tr>
        <tr>
          <td><strong>duplicate</strong></td>
          <td><strong>Gemma4</strong></td>
          <td class="is-better align-right">0.9667</td>
          <td class="is-better align-right">7.7667</td>
        </tr>
        <tr>
          <td><strong>duplicate</strong></td>
          <td><strong>Gemma3</strong></td>
          <td class="align-right">0.0333</td>
          <td class="align-right">3.7000</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> 30문항에서 평가한 100-step SFT 구성 비교. Preference와 Score는 각각 상대 선택률과 개별 답변의 1–10점 평균이다. multi에서 모델 간 격차가 줄었으며, 두 모델의 답변이 함께 바뀌는 비교다.</figcaption>
</figure>

이 결과는 답안 구성에 따라 모델 간 비교가 달라졌다는 탐색적 신호다. Pairwise 선택률은 상대 모델의 변화에도 영향을 받고, 문항별 결과와 반복 실행이 제시되어 있지 않다. 따라서 “Gemma3가 답안 다양성에 더 잘 반응한다”는 일반적 학습 특성까지 확정하기는 어렵다.

### 100-step 학습 소요시간

Table 5에서 Gemma4/Gemma3의 소요시간은 single 1348s/2411s, multi 1427s/2682s, duplicate 1510s/2683s였다. DGX Spark GB10에서 기록한 세 구성 모두 Gemma4가 짧았다.

같은 step·batch·최대 길이는 맞췄지만, tokenizer와 모델 구조가 다르고 실제 처리 토큰이나 연산량은 보고되어 있지 않다. 이 결과가 보여주는 것은 해당 실행 조건의 소요시간 차이다. 두 모델 모두 첫 step 대비 마지막 step의 loss는 낮아졌으나, 학습 데이터에 대한 loss 감소를 일반화 성능의 근거로 삼지는 않는다. Loss Remaining 도표는 Appendix Figure 1에 두었다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table">
      <thead>
        <tr>
          <th rowspan="2">SFT 구성</th>
          <th rowspan="2">모델</th>
          <th colspan="3">Training Signal</th>
        </tr>
        <tr>
          <th class="align-right">Step loss<br><span class="table-note-inline">first → last</span></th>
          <th class="align-right">Train loss</th>
          <th class="align-right">Runtime</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>single</strong></td>
          <td><strong>Gemma4</strong></td>
          <td class="align-right">16.05 -> 0.42</td>
          <td class="align-right">2.3239</td>
          <td class="is-better align-right">1348s</td>
        </tr>
        <tr>
          <td><strong>single</strong></td>
          <td><strong>Gemma3</strong></td>
          <td class="align-right">4.33 -> 0.04</td>
          <td class="align-right">0.9212</td>
          <td class="align-right">2411s</td>
        </tr>
        <tr>
          <td><strong>multi</strong></td>
          <td><strong>Gemma4</strong></td>
          <td class="align-right">16.36 -> 1.23</td>
          <td class="align-right">2.6546</td>
          <td class="is-better align-right">1427s</td>
        </tr>
        <tr>
          <td><strong>multi</strong></td>
          <td><strong>Gemma3</strong></td>
          <td class="align-right">4.25 -> 0.57</td>
          <td class="align-right">1.2520</td>
          <td class="align-right">2682s</td>
        </tr>
        <tr>
          <td><strong>duplicate</strong></td>
          <td><strong>Gemma4</strong></td>
          <td class="align-right">16.54 -> 0.51</td>
          <td class="align-right">2.4186</td>
          <td class="is-better align-right">1510s</td>
        </tr>
        <tr>
          <td><strong>duplicate</strong></td>
          <td><strong>Gemma3</strong></td>
          <td class="align-right">4.52 -> 0.04</td>
          <td class="align-right">0.9257</td>
          <td class="align-right">2683s</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 5.</strong> DGX Spark GB10에서 측정한 100-step SFT의 loss와 소요시간. Train loss는 기존 기록의 집계값이며 상세 집계 방식은 명시되어 있지 않다. 첫·마지막 step loss와 함께 학습 기록으로 보존하되, 모델 간 품질 순위로 해석하지 않는다.</figcaption>
</figure>

### 입력 손상: 절대 점수와 하락폭의 분리

SFT된 모델에 대해 50문항의 질문 본문만 손상시켰다. Table 6의 Real typo는 타이핑 오류와 띄어쓰기 붕괴, ASR noise는 음성 인식 전사체를 모사한 텍스트 오류다. 시스템 프롬프트와 출력 제약은 유지했다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>Noise</th>
          <th>모사한 입력 오류</th>
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
          <td>전사 오류를 모사한 텍스트 손상; 실제 음성 인식기 평가는 아님</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 6.</strong> 질문 본문에 적용한 두 입력 손상 유형. 시스템 프롬프트와 출력 형식 제약은 유지했다. ASR noise는 음성 인식 전사 오류를 모사한 텍스트 조건이다.</figcaption>
</figure>

Table 7에서 손상 후 Readability는 두 조건 모두 Gemma4가 높았다. 두 조건의 평균은 Gemma4 5.50, Gemma3 3.93이었다. 그러나 Figure 3의 원본 대비 하락폭은 Gemma3가 더 작다. 따라서 **손상 후 더 높은 점수를 유지하는 모델**과 **원본 대비 점수 변화가 작은 모델**은 이 기록에서 다르다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/gemma3-e4b-korean-sft/robustness-contrast.svg" alt="손상 질문에서 모델별 Readability 평균과 raw 대비 변화량 비교">
  <figcaption><strong>Figure 3.</strong> 왼쪽은 손상 입력 답변의 Readability 평균으로, 점수 척도는 1–10이고 표시 축은 0–8이다. 오른쪽은 같은 모델·질문셋에서 손상 입력 평균에서 원본 입력 평균을 뺀 변화량이다. 0에 가까울수록 하락폭이 작으며, 절대 점수와 하락폭은 서로 다른 비교다.</figcaption>
</figure>

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
          <th class="align-right">Gemma4</th>
          <th class="align-right">Gemma3</th>
          <th class="align-right">Gemma4</th>
          <th class="align-right">Gemma3</th>
          <th class="align-right">Gemma4</th>
          <th class="align-right">Gemma3</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Real typo</td>
          <td class="is-better align-right">5.32</td>
          <td class="align-right">3.86</td>
          <td class="is-better align-right">0.542</td>
          <td class="align-right">0.474</td>
          <td class="is-better align-right">0.14</td>
          <td class="align-right">0.32</td>
        </tr>
        <tr>
          <td>ASR noise</td>
          <td class="is-better align-right">5.68</td>
          <td class="align-right">4.00</td>
          <td class="is-better align-right">0.534</td>
          <td class="align-right">0.496</td>
          <td class="is-better align-right">0.16</td>
          <td class="align-right">0.26</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 7.</strong> 50문항의 손상 입력 평가. Readability는 개별 답변의 1–10점 평균, Char F1은 기준 답안과의 문자 중복, Violation은 형식 위반율이다. 원본 입력 대비 변화량은 Figure 3에 별도로 표시했다.</figcaption>
</figure>

Sample 2는 오타가 섞인 동일 질문의 실제 출력이다. 반복과 설명 구성 차이를 볼 수 있지만, Readability는 개념 설명의 사실성을 별도로 검증한 점수가 아니다.

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
  <figcaption><strong>Sample 2.</strong> 같은 Real typo 입력에 대한 실제 답변. 원래 질문은 “아로마와 허브의 차이는 무엇인가요? 아직도 아로마에 포함될 수 있는 식물들이 더 추가될 수 있나요?”였다. Gemma3 답변에는 같은 정의의 반복이 보인다. Length Pass는 길이 조건의 판정이며 전체 형식이나 사실성 검증을 뜻하지 않는다.</figcaption>
</figure>

## 해석과 한계

여러 비교 조건에서 관찰된 것은 Gemma4의 높은 judge 선택률과 낮은 형식 위반율이다. SFT 답안 구성을 바꾸면 격차가 달라졌고, 입력 손상 후 절대 Readability와 원본 대비 하락폭은 서로 다른 모델을 가리켰다. 한국어 instruction 평가에서 내용·형식·표현 중복·입력 변화에 대한 민감도를 구분해야 하는 이유를 보여주는 사례다.

결론의 범위는 다음 조건에 한정된다.

- **판정의 독립성:** 단일 judge를 사용했다. 형식과 내용의 기여를 분해하거나 인간 평가로 사실성을 검증한 결과는 제시되어 있지 않다.
- **표본과 변동:** 평가 크기는 비교별 100·30·50문항이다. 현재 노트에 문항별 결과와 반복 실행 분포가 제시되어 있지 않아 신뢰구간이나 작은 차이의 안정성을 새로 계산하지 않았다.
- **학습 비교:** 동일한 step 수가 동일한 계산 예산을 뜻하지는 않는다. SFT 구성의 관찰은 현재 데이터·모델·학습 설정의 범위를 넘어서 일반화하지 않는다.
- **재현 정보:** 현재 노트에는 learning rate, 정확한 모델·데이터 revision, GGUF 파일, 모델별 thinking·sampling 설정, 동률 처리와 전체 judge prompt가 남아 있지 않다. 공개 리소스 링크는 출처를 확인해 주지만 당시 실행을 완전히 복원하지는 못한다.

## Appendix: 기록된 실험 조건과 보조 자료

Appendix Table 1–3은 기존 노트에 남아 있는 설정이다. 본문에서 축약한 데이터 분할·판정·학습 조건을 모았으며, 누락된 설정을 추정해 채우지는 않았다.

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
          <td>30문항 holdout, <code>single</code>, <code>multi</code>, <code>duplicate</code> 구성 비교</td>
        </tr>
        <tr>
          <td><strong>질문 본문 손상 평가</strong></td>
          <td>50문항 holdout, <code>raw</code>, <code>real_typo</code>, <code>asr_noise</code> 비교</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 1.</strong> 기존 노트에 기록된 데이터 분할과 평가 크기. 각 비교 안에서 같은 평가 index를 사용했다는 조건을 보존했다. 서로 크기가 다른 세 평가셋의 문항 관계까지 확인한 것은 아니다.</figcaption>
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
          <td>QLoRA SFT; 4-bit로 추가 SFT 전 모델을 불러온 뒤 LoRA adapter만 학습</td>
        </tr>
        <tr>
          <td><strong>Quantization</strong></td>
          <td><code>BitsAndBytesConfig(load_in_4bit = true)</code><br><span class="table-note-inline"><code>nf4</code>, double quant, <code>bfloat16</code> compute</span></td>
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
          <td><code>per_device_batch_size = 16</code><br><code>gradient_accumulation_steps = 1</code><br><code>max_length = 1024</code></td>
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
  <figcaption><strong>Appendix Table 3.</strong> 기록된 QLoRA SFT와 생성 설정. 학습률, 모델별 전체 생성 옵션과 정확한 revision은 이 표에 남아 있지 않아, 완전한 재현 명세로 볼 수는 없다.</figcaption>
</figure>

### 학습 신호의 보조 시각화

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/gemma3-e4b-korean-sft/sft-efficiency.svg" alt="QLoRA 100-step SFT의 loss remaining과 runtime 비교">
  <figcaption><strong>Appendix Figure 1.</strong> 100-step SFT의 loss 변화와 소요시간. Loss Remaining은 첫 step loss 대비 마지막 step loss의 백분율이며, 같은 실행 안의 loss 감소를 표시한다. 토큰화와 학습 대상 분포가 다른 모델 사이의 품질 척도로 사용할 수 없다.</figcaption>
</figure>

### SFT 출력과 judge 점수 예시

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
  <figcaption><strong>Appendix Sample 1.</strong> step500 이후의 실제 답변과 기록된 점수. 두 모델 모두 형식 판정은 Pass였다. 높은 Judge Score가 각 인과 설명의 사실성을 보증하지는 않으므로, 이 샘플은 정답 예시가 아니라 판정 결과의 해석 범위를 보여준다.</figcaption>
</figure>

## References

<div class="reference-list" markdown="1">

1. <span id="ref-gemma3"></span>Google DeepMind. *Gemma 3 4B instruction-tuned model*. 공식 모델카드: [google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it).
2. <span id="ref-gemma4"></span>Google DeepMind. *Gemma 4 E4B instruction-tuned model*. 공식 모델카드: [google/gemma-4-E4B-it](https://huggingface.co/google/gemma-4-E4B-it).
3. <span id="ref-koalpaca"></span>beomi. *KoAlpaca-v1.1a*. Hugging Face 데이터셋: [beomi/KoAlpaca-v1.1a](https://huggingface.co/datasets/beomi/KoAlpaca-v1.1a).
4. <span id="ref-gpt-oss"></span>OpenAI. *gpt-oss-120b*. 공식 모델카드: [openai/gpt-oss-120b](https://huggingface.co/openai/gpt-oss-120b).
5. <span id="ref-qlora"></span>Tim Dettmers, Artidoro Pagnoni, Ari Holtzman, and Luke Zettlemoyer. *QLoRA: Efficient Finetuning of Quantized LLMs*. arXiv:2305.14314, 2023. [논문](https://arxiv.org/abs/2305.14314).
6. <span id="ref-rouge"></span>Chin-Yew Lin. *ROUGE: A Package for Automatic Evaluation of Summaries*. Text Summarization Branches Out, pp. 74–81, Association for Computational Linguistics, 2004. [논문](https://aclanthology.org/W04-1013/).

</div>

## Experiment Resources

<div class="reference-list" markdown="1">

- ggml-org. [llama.cpp](https://github.com/ggml-org/llama.cpp). Judge GGUF 실행에 사용한 추론 소프트웨어의 공식 저장소.

</div>

## Citation

이 글을 인용할 때는 아래 형식을 사용할 수 있다.

```text
Ilho Ahn, "Gemma3 4B와 Gemma4 E4B의 한국어 SFT 비교", Ilho’s Notes, Apr 2026.
```

또는 BibTeX 형식으로는 다음처럼 적을 수 있다.

```bibtex
@article{ahn2026gemma3gemma4korean,
  author = {Ilho Ahn},
  title = {Gemma3 4B와 Gemma4 E4B의 한국어 SFT 비교},
  journal = {Ilho’s Notes},
  year = {2026},
  month = apr,
  url = {https://muted-color.github.io/research/2026/04/12/gemma3-e4b-korean-sft/}
}
```
