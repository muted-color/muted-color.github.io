---
layout: post
title: "Alignment Data Map: 측정값에서 선호 학습 쌍까지"
date: 2026-08-23 20:10:32 +0900
last_modified_at: 2026-08-24 18:14:54 +0900
lang: ko
categories: ["LLM ALIGNMENT"]
tags: [llm, alignment, preference-data, data-selection, adm, simpo, ultrafeedback]
lab_host: "dgx1"
lab_path: "projects/adm-toolcall"
excerpt: "Alignment Data Map의 상대 좌표가 reference answer와 텍스트 처리에 따라 달라지고, 지시문 선택 뒤 실제 선호 학습 쌍의 구성이 다시 달라지는 과정을 추적한다."
description: "UltraFeedback 4,500개 지시문에서 Alignment Data Map의 측정 민감도, 코호트 구성, 실제 선호 쌍과 단일 seed SimPO 결과를 연결해 분석한 미니 리서치 노트."
permalink: /research/2026/08/23/adm-measurement-to-preference-pairs/ko/
translation_url: /research/2026/08/23/adm-measurement-to-preference-pairs/
image: /assets/images/posts/adm-measurement-to-preference-pairs/social-thumbnail.png
image_alt: "Alignment Data Map의 reference 기반 측정에서 영역 선택과 선호 학습 쌍 구성으로 이어지는 과정을 요약한 소셜 썸네일"
hero_image: /assets/images/posts/adm-measurement-to-preference-pairs/adm-measurement-to-training-pairs.svg
hero_alt: "Four-stage flow from measuring four candidate responses for each of 4,500 instructions to mapping instructions into three ADM regions, instantiating 17,301 training pairs, and evaluating region-specific SimPO pipelines on a shared 600-pair set."
hero_caption: "<strong>Figure 1.</strong> Data path from reference-conditioned candidate measurement to region-specific SimPO evaluation. ADM selects instructions, whereas training uses instantiated response pairs; the highlighted stage marks this change in analysis unit. Counts are observed totals, but box widths are conceptual and do not encode scale."
hero_frame: true
hero_variant: flow-diagram
math: true
published: true
publication_status: "published"
---

Lee et al.의 Alignment Data Map(ADM) <a class="citation-ref" href="#ref-adm" aria-label="Reference 1">[1]</a>은 한 지시문의 후보 응답에서 계산한 alignment score의 평균과 분산으로 선호 데이터를 구분해 학습 데이터를 선택하는 방법이다. 그러나 이 좌표가 reference answer와 텍스트 처리 방식에 얼마나 민감한지, 지시문 선택이 실제 학습 쌍의 구성으로 어떻게 이어지는지는 별도의 검증이 필요하다. 이 글에서는 4,500개 지시문을 대상으로 측정 조건에 따른 좌표와 영역의 변화부터, 선택된 지시문이 실제 선호 학습 쌍으로 변환되는 과정까지 추적했다.

ADM 영역은 reference answer, 장문 처리 방식, 코호트 구성에 따라 달라졌다. 지시문 할당량을 같게 맞춰도 응답 쌍으로 확장한 뒤에는 방향·점수 차이·반복 노출 구조가 달랐다.

> 이 글에서 **quality**는 후보 응답과 reference answer 사이의 평균 문장 임베딩 유사도다. 응답 품질 전반이나 인간 선호와의 일치를 뜻하지 않는다.

## 요약

- 4,500개 지시문과 지시문당 후보 응답 4개를 대상으로 ADM 측정값이 실제 선호 학습 쌍으로 바뀌는 과정을 추적했다.
- Reference answer 생성 정책과 장문 처리 방식이 달라지면 같은 지시문의 ADM 영역도 달라졌다.
- 지시문 구성을 맞춰도 실제 응답 쌍의 점수 차이, 선호 방향, 반복 노출은 같아지지 않았다.
- 단일 seed 학습 비교에서는 영역별 결과 차이가 관찰됐지만, ADM 영역 자체의 효과로 분리되지는 않았다.

## 문제 설정

ADM은 후보 응답별 alignment score의 평균과 변동으로 HighAvg·LowAvg·HighVar 영역을 구성한다. 평균과 변동으로 데이터의 특성을 구분한다는 관점은 Swayamdipta et al.의 Dataset Cartography <a class="citation-ref" href="#ref-dataset-cartography" aria-label="Reference 2">[2]</a>에서 이어지지만, ADM은 이를 선호 데이터 선택에 적용한다.

원 ADM 연구는 LLM-as-a-judge, reward model, reference-based scoring으로 만든 서로 다른 지도에서도 HighAvg 선택의 집계 학습 성능 우위가 유지됐다고 보고했다 <a class="citation-ref" href="#ref-adm" aria-label="Reference 1">[1]</a>. 집계 성능을 다시 검증하는 대신, **측정 조건에 따른 동일 지시문의 좌표·영역 유지와 실제 학습 쌍으로의 변환 구조**를 분석했다. 집계 성능의 안정성과 개별 표본 영역의 안정성은 서로 다른 질문이다.

Song의 data-centric alignment pipeline <a class="citation-ref" href="#ref-data-centric-alignment" aria-label="Reference 3">[3]</a>은 alignment data construction을 response synthesis, preference evaluation, preference instantiation으로 나눈다. 이 글의 기여는 이 파이프라인 관점 자체가 아니라, ADM의 reference-based measurement에서 실제 SimPO 선호 쌍까지 이어지는 변환을 한 사례에서 수치화한 데 있다.

선호 데이터에서 응답 쌍의 점수 차이(pair margin)와 구성은 Yang et al. <a class="citation-ref" href="#ref-pair-efficiency" aria-label="Reference 4">[4]</a>, Deng et al. <a class="citation-ref" href="#ref-preference-selection" aria-label="Reference 5">[5]</a>, Xiao et al. <a class="citation-ref" href="#ref-sweet-spot" aria-label="Reference 6">[6]</a>이 각각 다뤘고, Pan et al.은 chosen 응답의 품질을 분석했다 <a class="citation-ref" href="#ref-what-matters-dpo" aria-label="Reference 7">[7]</a>. 이 글은 특정 selection rule의 일반적 우위를 평가하지 않는다. 분석 대상은 지시문 단위 선택 뒤에 형성되는 응답 쌍 단위 학습 신호다.

## 평가 설계

### Reference 기반 측정과 영역 구성

측정 코호트는 UltraFeedback <a class="citation-ref" href="#ref-ultrafeedback" aria-label="Reference 8">[8]</a>에서 원천 데이터셋, 과제 유형, 지시문 길이를 고려해 뽑은 4,500개 지시문과 지시문당 후보 응답 4개로 구성했다. Reference answer는 <a href="https://huggingface.co/Qwen/Qwen3.5-122B-A10B"><code>Qwen3.5-122B-A10B</code></a>의 non-thinking 설정에서 temperature 0, 최대 4,096토큰으로 생성했다.

각 후보 응답은 Sentence-BERT 계열의 <a href="https://huggingface.co/sentence-transformers/all-mpnet-base-v2"><code>all-mpnet-base-v2</code></a> <a class="citation-ref" href="#ref-sentence-bert" aria-label="Reference 9">[9]</a> <a class="citation-ref" href="#ref-mpnet" aria-label="Reference 10">[10]</a>로 reference answer와의 cosine similarity를 계산했다. 앞부분 기준선은 최대 384토큰을 사용한다. 지시문별 네 유사도의 평균을 quality, 모분산을 variability로 두고, 전체 코호트의 상대 순위에 따라 LowAvg·HighAvg·HighVar를 각 1,500개로 나눴다. 따라서 영역은 절대 등급이 아니라 해당 reference answer·채점 방식·코호트 안의 상대적 위치다.

실제 학습 쌍 분석에는 중첩 창 평균으로 다시 계산하고 출처×과제 유형별로 나눈 지도를 사용했다. 이 조건은 전체 코호트에서 직접 나눈 초기 지도와 동일하지 않다.

### 선호 쌍과 학습 비교

ADM은 지시문을 선택하지만, Meng et al.의 SimPO <a class="citation-ref" href="#ref-simpo" aria-label="Reference 11">[11]</a>는 chosen–rejected 응답 쌍을 학습한다. 이 분석에서는 출처 평점이 다른 모든 후보 응답 쌍을 만들고, 출처×과제 유형별 지시문 할당량을 세 영역에서 맞췄다. 최종 학습 데이터는 총 17,301쌍이다.

<a href="https://huggingface.co/Qwen/Qwen2.5-3B-Instruct"><code>Qwen2.5-3B-Instruct</code></a>는 LoRA·SimPO로 최대 5 epoch 학습했다. 학습률은 5e-6, global batch는 63이다. 영역별 전용 개발 세트에서 선호 방향 일치 쌍 수, loss, 이른 시점 순으로 모델을 선택한 뒤, 학습 데이터와 prompt·pair가 겹치지 않는 동일한 600쌍 개발 세트에서 비교했다. 분석에서는 ADM이 선택하는 지시문과 SimPO가 학습하는 응답 쌍을 구분해 추적했다.

## 결과

### Reference answer와 장문 처리 민감도

같은 100개 지시문과 동일한 후보 응답에 GPT-4o와 Qwen3.5의 reference answer 생성 정책을 적용했을 때 후보 순서 일치율은 .760이었고, 95% bootstrap CI는 .710–.808이었다. 분산 순위 상관은 .854, 영역 macro-F1은 .7395였으며, 64/100개 지시문에서 적어도 한 번의 후보 순서 반전이 있었다.

별도의 공통 60개 표본에 gpt-oss-120B를 추가한 비교에서는 세 reference answer 정책의 쌍별 비교와 반복 실행에서 후보 순서 일치율 .7722–.8472, 영역 macro-F1 .6500–.8000이 관찰됐다.

후보 응답과 reference answer를 고정하고 장문 처리 방식만 바꿔도 영역 이동이 남았다. Figure 2에서 세 지표는 높을수록 앞부분 기준선에 가깝다. Overlapping-window mean은 모든 지표에서 Head–tail segment mean보다 기준선에서 더 멀었다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/adm-measurement-to-preference-pairs/long-text-processing-stability.svg" alt="Dot plot comparing head–tail segment mean and overlapping-window mean against a 100 percent prefix baseline. Overlapping-window mean is lower for candidate-pair order agreement, region macro-F1, and original HighAvg retention.">
  <figcaption><strong>Figure 2.</strong> Stability under long-text processing changes with the same MPNet model, reference answers, and candidate responses. Head–tail segment mean changed 453 of 4,500 region assignments, while overlapping-window mean changed 615; the largest movement remained near the LowAvg–HighAvg boundary. The figure reports agreement with the prefix baseline.</figcaption>
</figure>

### 코호트 구성과 영역 연관

Figure 3은 전체 4,500개 지시문의 ADM 좌표와 상대 순위 경계를 보여 준다. 세 영역은 각각 1,500개지만, 그 안의 데이터 출처, 지시문 길이, 과제 유형 구성은 같지 않았다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/adm-measurement-to-preference-pairs/adm-cohort-measured-map.svg" alt="Two-panel scatter plot of mean cosine similarity versus population variance across four candidate responses for 4,500 instructions. The left panel shows the full range and the right panel enlarges variability from 0 to 0.03; HighAvg, LowAvg, and HighVar each contain 1,500 instructions, with dashed cohort-relative boundaries.">
  <figcaption><strong>Figure 3.</strong> ADM coordinate distribution for a fixed cohort of 4,500 instructions. The left panel shows the full measured range, while the right panel enlarges the variability range from 0 to 0.03. Dashed lines mark the cohort-relative boundaries at variability 0.015260 and quality 0.7882 within the low-variability region. Each region contains 1,500 instructions, and quality is the mean cosine similarity to the Qwen reference answer. This is a Qwen-defined cohort map.</figcaption>
</figure>

데이터 출처와 ADM 영역 배정 사이의 연관성은 Cramér's V .388이었다. 영역별 구성을 보면 HighAvg 표본의 69.7%는 Evol-Instruct에서, HighVar 표본의 58.4%는 FLAN/NIV2에서 왔다. 지시문 길이 사분위와 영역 배정 사이의 Cramér's V는 .192였으며, 평균 지시문 길이는 HighAvg 487자, HighVar 888자였다. 과제 유형과 영역 배정 사이의 Cramér's V는 .160이었고, Code 지시문의 44.83%와 Multi-constraint 지시문의 23.54%가 HighAvg에 배정됐다.

중첩 창 평균 지도에서 과제 유형만 고려한 HighAvg 학습–개발 세트의 출처 분포 TV는 .289였다. 출처×과제 유형별로 재구성한 뒤에는 .030으로 감소했다. 이는 출처 구성을 직접 맞춘 결과지만, 이 과정에서 1,387/4,500개의 영역과 선택된 지시문·응답 쌍이 함께 바뀌었다. 따라서 이후 학습 차이에는 여러 데이터 구성 변화가 함께 포함된다.

### 지시문 선택과 실제 선호 쌍

별도의 HighAvg 데이터 구성에서 종합 품질 평점 방향과 alignment score 방향은 동점이 아닌 3,229쌍 중 862쌍, 즉 26.7%에서 반대였다. ADM의 지시문 선택과 응답 쌍의 선호 레이블 결정은 같은 단계가 아니다.

출처×과제 유형별 지시문 할당량을 맞춘 세 영역에서도 실제 학습 쌍의 구성이 달랐다. Table 1에서 출처 평점과 alignment score의 차이는 절댓값이다. 두 점수의 방향 반대 비율은 낮을수록 두 기준이 더 자주 일치한다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Region</th>
          <th class="align-right">Training pairs</th>
          <th class="align-right">Source-rating gap<br><span class="table-note-inline">median</span></th>
          <th class="align-right">Alignment-score gap<br><span class="table-note-inline">median</span></th>
          <th class="align-right">Alignment-score gap<br><span class="table-note-inline">&lt;.05</span></th>
          <th class="align-right">Opposite direction</th>
          <th class="align-right">Mean pairs<br><span class="table-note-inline">per instruction</span></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>LowAvg</td>
          <td class="align-right">5,774</td>
          <td class="align-right">1.000</td>
          <td class="align-right">.0727</td>
          <td class="align-right">36.91%</td>
          <td class="align-right">37.51%</td>
          <td class="align-right">5.346</td>
        </tr>
        <tr>
          <td>HighAvg</td>
          <td class="align-right">5,682</td>
          <td class="align-right">.750</td>
          <td class="align-right">.0490</td>
          <td class="align-right">50.70%</td>
          <td class="align-right">32.95%</td>
          <td class="align-right">5.261</td>
        </tr>
        <tr>
          <td>HighVar</td>
          <td class="align-right">5,845</td>
          <td class="align-right">1.250</td>
          <td class="align-right">.2047</td>
          <td class="align-right">17.74%</td>
          <td class="align-right">26.48%</td>
          <td class="align-right">5.412</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> Composition of instantiated training pairs derived from source ratings. HighAvg had the smallest median alignment-score gap and the largest share of pairs below .05.</figcaption>
</figure>

지시문 기준 출처×과제 유형 TV는 0이었지만, 응답 쌍 확장 뒤 출처×과제 유형 TV는 .0101–.0127, 길이 구간 TV는 .0418–.0728로 남았다. 지시문 구성을 맞추는 것만으로 응답 쌍의 방향, 점수 차이, 반복 노출까지 같아지지는 않았다.

### 단일 seed 파이프라인 비교

Reward accuracy는 모델이 chosen 응답에 rejected 응답보다 높은 reward를 부여한 쌍의 비율이며 높을수록 좋다. Reward margin은 두 reward의 평균 차이이며 높을수록 좋다. SimPO loss는 목표 margin 미달과 음수 margin 꼬리에 민감하며 낮을수록 좋다.

Table 2는 영역별 모델 선택을 포함한 세 파이프라인과 기초 모델을 동일한 600쌍 공통 개발 세트에서 비교한다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Pipeline</th>
          <th class="align-right">Preferred-direction matches</th>
          <th class="align-right">Reward accuracy</th>
          <th class="align-right">Reward accuracy Δ<br><span class="table-note-inline">vs. base model</span></th>
          <th class="align-right">SimPO loss</th>
          <th class="align-right">Reward margin</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Qwen base</td>
          <td class="align-right">378/600</td>
          <td class="align-right">63.00%</td>
          <td class="align-right">—</td>
          <td class="align-right">1.253075</td>
          <td class="align-right">1.395679</td>
        </tr>
        <tr>
          <td>LowAvg</td>
          <td class="align-right">421/600</td>
          <td class="align-right">70.17%</td>
          <td class="align-right">+7.17pp</td>
          <td class="align-right">1.031459</td>
          <td class="align-right">1.506562</td>
        </tr>
        <tr>
          <td>HighVar</td>
          <td class="align-right">431/600</td>
          <td class="align-right">71.83%</td>
          <td class="align-right">+8.83pp</td>
          <td class="align-right">1.031298</td>
          <td class="align-right">1.573699</td>
        </tr>
        <tr>
          <td>HighAvg</td>
          <td class="align-right">442/600</td>
          <td class="align-right">73.67%</td>
          <td class="align-right">+10.67pp</td>
          <td class="align-right">1.019236</td>
          <td class="align-right">2.149893</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> Region pipelines, including region-specific model selection, evaluated on the same shared 600-pair development set. Higher reward accuracy and reward margin are better; lower SimPO loss is better.</figcaption>
</figure>

이 단일 seed 비교에서 HighAvg는 HighVar보다 선호 방향 일치가 11쌍 많았고, reward accuracy·reward margin·SimPO loss에서 가장 좋은 관측값을 기록했다.

## 파이프라인 해석

ADM 좌표는 reference answer와 텍스트 처리 방식에 의존하는 상대적 측정값이며, 지도에서 선택되는 단위와 실제 학습 단위도 각각 지시문과 응답 쌍으로 다르다. 지시문 할당량을 같게 맞춰도 pair margin, 방향 불일치, 지시문당 반복 노출은 달라졌다.

데이터 선택을 재현하고 학습 결과의 범위를 해석하려면 ADM 영역 이름뿐 아니라 reference answer 생성 조건, 후보 응답 집합, 텍스트 처리 방식, 코호트와 영역 경계, 응답 쌍 구성 규칙, 실제 응답 쌍 단위 분포를 함께 기록해야 한다.

## 한계와 후속 비교

- Reference answer 비교에서는 모델과 생성 설정을 함께 바꿨고, 60개 표본의 범위는 신뢰구간이 아니라 쌍별 비교와 반복 실행을 요약한 값이다. 측정 타당성을 확인하려면 같은 4,500개 지시문과 후보 응답 집합에 여러 reference answer를 적용하고, 장문 채점 방식을 사람 평가나 과제 정답에 근거한 주석과 비교해야 한다.
- 공통 600쌍은 반복 사용된 개발 세트이며 쌍 단위 신뢰구간을 계산하지 않았다. 파이프라인 비교에는 무작위 선택과 전체 데이터 조건이 없고, 모든 학습 결과는 하나의 seed에서 나왔다. 영역별 모델 선택과 응답 쌍 구성도 함께 달라져 ADM 영역 자체의 효과를 분리할 수 없다. 후속 비교에서는 데이터 구성·모델·학습 설정을 고정하고 응답 쌍 방향만 바꾼 조건을 여러 seed로 확인해야 한다.
- 외부 데이터와 downstream benchmark에 대한 일반화는 평가 범위에 포함하지 않았다.

## Appendix: 주요 지표

- **Reference answer와의 평균 유사도:** 네 후보 응답과 reference answer 사이의 MPNet cosine similarity 평균.
- **Variability:** 네 유사도 점수의 모분산(`ddof=0`).
- **후보 응답 순서 일치율:** 네 후보가 만드는 여섯 쌍에서 두 reference answer에 따른 순서가 같은 비율.
- **영역 macro-F1:** 두 ADM 영역 배정의 클래스별 F1을 동일 가중 평균한 값.
- **Cramér's V:** 영역과 출처·과제 유형·길이 범주의 연관 크기.
- **출처 분포 거리(TV):** 두 세트의 출처 비율 차이인 $\frac{1}{2}\sum_i\lvert p_{1,i}-p_{2,i}\rvert$.
- **Reward accuracy·reward margin·SimPO loss:** 각각 선호 방향 일치 비율, 평균 reward 차이, 목표 margin 미달과 음수 margin 꼬리를 반영한 loss.

## References

<div class="reference-list" markdown="1">

<ol>
  <li id="ref-adm">Lee, S., Kim, E., Lee, H., and Chang, B. <strong>Alignment Data Map for Efficient Preference Data Selection and Diagnosis</strong>. <em>Findings of ACL 2026</em>, 38225–38241, 2026. <a href="https://aclanthology.org/2026.findings-acl.1906/">ACL Anthology</a>; <a href="https://arxiv.org/abs/2505.23114">arXiv</a></li>
  <li id="ref-dataset-cartography">Swayamdipta, S. et al. <strong>Dataset Cartography: Mapping and Diagnosing Datasets with Training Dynamics</strong>. <em>EMNLP 2020</em>, 9275–9293, 2020. <a href="https://aclanthology.org/2020.emnlp-main.746/">ACL Anthology</a></li>
  <li id="ref-data-centric-alignment">Song, H. <strong>Alignment Tuning for Large Language Models: A Data-Centric Lens on Alignment Data Pipelines</strong>. <em>Findings of ACL 2026</em>, 2541–2561, 2026. <a href="https://aclanthology.org/2026.findings-acl.121/">ACL Anthology</a></li>
  <li id="ref-pair-efficiency">Yang, S. et al. <strong>Not All Preference Pairs Are Created Equal: A Recipe for Annotation-Efficient Iterative Preference Learning</strong>. <em>Findings of EMNLP 2024</em>, 6549–6561, 2024. <a href="https://aclanthology.org/2024.findings-emnlp.382/">ACL Anthology</a></li>
  <li id="ref-preference-selection">Deng, X. et al. <strong>Less is More: Improving LLM Alignment via Preference Data Selection</strong>. arXiv:2502.14560, 2025. <a href="https://arxiv.org/abs/2502.14560">arXiv</a></li>
  <li id="ref-sweet-spot">Xiao, Y. et al. <strong>Finding the Sweet Spot: Preference Data Construction for Scaling Preference Optimization</strong>. <em>ACL 2025</em>, 12538–12552, 2025. <a href="https://aclanthology.org/2025.acl-long.615/">ACL Anthology</a></li>
  <li id="ref-what-matters-dpo">Pan, Y. et al. <strong>What Matters in Data for DPO?</strong> <em>NeurIPS 2025</em>, 44689–44716, 2025. <a href="https://proceedings.neurips.cc/paper_files/paper/2025/hash/3f37b8fbd43303106dd141a602838ad5-Abstract-Conference.html">NeurIPS</a></li>
  <li id="ref-ultrafeedback">Cui, G. et al. <strong>UltraFeedback: Boosting Language Models with Scaled AI Feedback</strong>. <em>ICML 2024</em>, 9722–9744, 2024. <a href="https://proceedings.mlr.press/v235/cui24f.html">PMLR</a>; <a href="https://huggingface.co/datasets/openbmb/UltraFeedback">Dataset</a></li>
  <li id="ref-sentence-bert">Reimers, N. and Gurevych, I. <strong>Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks</strong>. <em>EMNLP-IJCNLP 2019</em>, 3982–3992, 2019. <a href="https://aclanthology.org/D19-1410/">ACL Anthology</a></li>
  <li id="ref-mpnet">Song, K., Tan, X., Qin, T., Lu, J., and Liu, T.-Y. <strong>MPNet: Masked and Permuted Pre-training for Language Understanding</strong>. <em>NeurIPS 2020</em>, 16857–16867, 2020. <a href="https://proceedings.neurips.cc/paper/2020/hash/c3a690be93aa602ee2dc0ccab5b7b67e-Abstract.html">NeurIPS</a></li>
  <li id="ref-simpo">Meng, Y., Xia, M., and Chen, D. <strong>SimPO: Simple Preference Optimization with a Reference-Free Reward</strong>. <em>NeurIPS 2024</em>, 124198–124235, 2024. <a href="https://proceedings.neurips.cc/paper_files/paper/2024/hash/e099c1c9699814af0be873a175361713-Abstract-Conference.html">NeurIPS</a></li>
</ol>

**모델 및 데이터셋 리소스:** [Qwen3.5-122B-A10B](https://huggingface.co/Qwen/Qwen3.5-122B-A10B), [Qwen2.5-3B-Instruct](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct), [all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2), [UltraFeedback](https://huggingface.co/datasets/openbmb/UltraFeedback).

</div>

## Citation

Text citation:

```text
Ilho Ahn, "Alignment Data Map: 측정값에서 선호 학습 쌍까지", Mini Research, August 23, 2026.
```

BibTeX:

```bibtex
@article{ahn2026admmeasurementpreferencepairs,
  author = {Ilho Ahn},
  title = {Alignment Data Map: 측정값에서 선호 학습 쌍까지},
  journal = {Mini Research},
  year = {2026},
  month = aug,
  url = {https://muted-color.github.io/research/2026/08/23/adm-measurement-to-preference-pairs/ko/}
}
```
