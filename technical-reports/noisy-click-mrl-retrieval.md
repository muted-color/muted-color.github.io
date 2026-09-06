---
lang: ko
title: "희소 클릭 라벨에서 다국어 상품 검색 임베딩 평가와 Matryoshka 압축"
layout: post
date: 2026-05-25 16:30:00 +0900
last_modified_at: 2026-09-06 00:00:00 +0900
categories: ["RETRIEVAL EVAL"]
tags: [retrieval, embeddings, product-search, multilingual-retrieval, contrastive-learning, click-labels, llm-judge, matryoshka-representation-learning, embedding-compression, ablation-study]
excerpt: "희소 클릭 라벨의 평가 한계를 점검하고, MRL 256차원의 통합 후보 풀 MAP@10 0.0049 감소와 벡터 저장량 1/3 절충을 분석한다."
description: "다국어 상품 검색에서 클릭 라벨과 LLM 보조 평가의 범위를 구분하고, KO 100개 통합 후보 풀 평가로 MRL 768→256차원의 MAP@10 0.9430→0.9381과 벡터 메모리 1/3 절충을 정리한다."
permalink: /technical-reports/noisy-click-mrl-retrieval/
image: /assets/images/posts/noisy-click-mrl-retrieval/social-thumbnail.png
image_alt: "KO 100개 union-pool 평가에서 MRL 768차원과 256차원의 MAP@10 0.9430·0.9381 및 fp16 벡터 저장량 1536·512 MB를 비교한 그림"
hero_image: /assets/images/posts/noisy-click-mrl-retrieval/hero.svg
hero_alt: "KO 100개 union-pool 평가에서 MRL 768차원과 256차원의 MAP@10 0.9430·0.9381 및 fp16 벡터 저장량 1536·512 MB를 비교한 산점도"
hero_caption: "<strong>Figure 1.</strong> KO 100개 union-pool 평가에서 MRL 768→256차원은 MAP@10 0.0049 감소와 fp16 벡터 저장량 1/3을 교환한다. 저장량은 1M 벡터 기준이며 색인 부가 메모리는 제외한다. Encoder 출력은 768차원으로 유지된다. y축은 차이를 읽기 위한 0.930–0.950 국소 범위이며, 점의 연결은 두 설정의 비교만 나타낸다. <a href='/assets/images/posts/noisy-click-mrl-retrieval/hero.svg'>원본 그림 확대</a>."
hero_frame: true
hero_variant: featured-plot
hero_fit: contain
math: true
hidden: true
publication_status: "technical-report"
report_scope: "technical report"
technical_report_index: false
lab_path: "experiment-lab/projects/serach-lm"
---

상품 검색 임베딩의 성능을 클릭 로그로만 평가하면 절대 점수가 낮게 보일 수 있다. 사용자는 하나의 상품을 클릭하지만, 짧고 넓은 검색어에는 관련 상품이 여러 개 존재한다. 모델이 클릭되지 않은 관련 상품을 상위에 올리면 click-label metric에서는 오답으로 처리된다. 본 분석은 이 문제를 단순한 모델 학습 문제가 아니라 **관련 상품 라벨이 희소할 때 검색 개선을 어떻게 측정하고, 저차원 색인으로 옮길 수 있는지**를 묻는 문제로 정의한다.

평가 질문은 세 가지다. 첫째, click-label MAP@10은 라벨 노이즈가 있어도 어떤 범위에서 모델 간 상대 비교 신호로 쓸 수 있는가. 둘째, 어떤 학습 변경이 다국어 상품 검색 임베딩에서 구분 가능한 개선을 보이는가. 셋째, Kusupati et al.의 Matryoshka Representation Learning(MRL)을 이용한 fine-tuning에서 256차원 압축은 768차원 대비 얼마의 품질을 포기하는가 <a class="citation-ref" href="#ref-mrl" aria-label="Reference 3">[3]</a>.

**최종 차원 선택의 근거는 모델들이 같은 관련 상품 집합으로 평가된 통합 후보 풀(union-pool) 결과다.** MRL 768차원의 MAP@10은 `0.9430`, 256차원은 `0.9381`이었다. 256차원은 약 `0.0049`의 점수 감소와 fp16 벡터 저장량 1/3을 교환하는 후보이며, 이 결과는 KO 100개 쿼리의 보조 평가에 한정된다. 본문은 먼저 이 절충을 제시하고, 학습 개선과 평가 보정이 각각 어떤 근거에 기대는지 살펴본다.

이 글은 특정 서비스의 원천 데이터를 공개하는 문서가 아니다. 서비스명, 개별 상품명, 상품 식별자, 내부 경로는 제거했고, 데이터와 샘플은 역할 중심으로 익명화했다. 따라서 핵심 비교 대상은 특정 카탈로그의 절대 성능보다, 희소 click-label retrieval에서 평가 보정과 저차원 임베딩 선택을 어떻게 함께 다룰 수 있는지다.

> **click-label metric**은 검색 로그에서 관측된 클릭 상품만 positive로 둔 평가다. 범위가 넓은 검색어의 관련 상품을 놓칠 수 있어 절대 점수는 낮게 보일 수 있다.
>
> **LLM-judged metric**은 고정된 쿼리 샘플의 상위 후보를 관련성 기준으로 다시 라벨링한 보조 평가다. 클릭 라벨에서 오답으로 처리된 관련 상품(false negative)이 있는지 점검하는 용도로 사용한다.
>
> **Matryoshka fine-tuning**은 하나의 임베딩 벡터에서 앞부분(prefix)만으로도 검색할 수 있도록 여러 차원에서 동시에 학습하는 방식이다. 이 설정에서는 768차원으로 encode한 뒤 앞 256차원을 slice하고 재정규화하는 사용법을 평가했다.

{% include model-mention-cards.html label="사용한 주요 리소스" aria_label="사용한 검색 임베딩과 평가 리소스" models="EmbeddingGemma 300M|google/embeddinggemma-300m|https://huggingface.co/google/embeddinggemma-300m;multilingual-e5-base|intfloat/multilingual-e5-base|https://huggingface.co/intfloat/multilingual-e5-base;Matryoshka Representation Learning|Kusupati et al. 2022|https://arxiv.org/abs/2205.13147;Sentence-Transformers|retrieval training toolkit|https://www.sbert.net/" %}

## 요약

- **256차원은 작은 품질 손실을 허용하는 선택지다.** KO 100개 통합 후보 풀(union-pool)에서 MRL MAP@10은 768차원 `0.9430`, 256차원 `0.9381`이었다. 1M fp16 벡터 저장량은 `1,536 MB`에서 `512 MB`로 줄며, encoder는 계속 768차원을 출력한다.
- **학습 전후 개선은 두 평가에서 같은 방향이었다.** 전체 KO/EN/JP click-label MAP@10은 `0.6558 → 0.8146`으로 `+24.2%` 높아졌다. KO 100개 self-pool 보조 평가도 개선됐지만, 두 평가의 절대값 차이는 쿼리 구성과 라벨 변경이 함께 반영되어 있다.
- **모델 교체와 batch/loss 조합에서 개선이 관찰됐다.** e5 기준선 `0.7732 → 0.7953`, cached loss와 batch 확대 `0.8082 → 0.8151`이었다. 후자의 paired bootstrap 차이는 `+0.0068`, 95% CI `[+0.0035, +0.0101]`이었다. 모델 교체 효과를 capacity 하나로 분리한 실험은 아니다.
- **MRL의 주된 역할은 저차원 prefix 학습이었다.** dim 768 click-label MAP@10은 non-MRL `0.8151`, MRL `0.8146`으로 가까웠다. self-pool의 256차원 점수 `0.9321 → 0.9506`은 보조 결과로 남기고, 차원 선택은 union-pool 비교를 우선한다.
- **작은 차이와 비용 측정에는 남은 불확실성이 있다.** query augmentation, hard negative mining, weighted resampling, gradient clipping, uniform language sampling, 단순 step 연장은 현 비교에서 안정적인 추가 이득을 보이지 않았다. query bootstrap은 학습 seed 변동을 측정하지 않으며, 검색 latency/QPS 기록은 측정 조건이 충분히 남아 있지 않아 실제 서빙 개선폭으로 일반화할 수 없다.

## 문제 설정

검색 과제는 짧은 검색어와 긴 상품 문서를 비교하는 비대칭 검색(asymmetric retrieval)이다. 입력 쿼리(query)는 사용자가 검색창에 입력한 짧은 문자열이고, 문서(document)는 상품명, 브랜드, 카테고리, 성별, 가격대, 속성 텍스트를 결합한 익명화 상품 문서다. 모델은 query embedding과 document embedding의 cosine similarity로 같은 언어 카탈로그 안에서 top-K 상품을 찾는다.

데이터셋은 익명화된 click-derived query-product pair, product metadata, 다국어 keyword source를 결합해 만들었다. query source는 한국어 click-derived query, 글로벌 keyword source, product-name n-gram으로 나뉜다. train/valid/test는 상품 단위로 분리해 같은 상품이 여러 split에 동시에 등장하지 않도록 했다. 학습 split은 `282,263` pair, validation은 `14,877`, test는 `15,883` pair다.

학습 쌍 대부분은 한국어 클릭 로그에서 왔다. 언어 표기는 한국어(KO), 영어(EN), 일본어(JP)다. 원래 학습 데이터의 KO 비중은 약 `81%`였고, temperature-based language sampling으로 학습 노출 비중을 KO `63%`, EN `25%`, JP `12%` 수준으로 완화했다. 이 조정은 KO 우위를 완전히 지우기보다 EN/JP가 contrastive batch 안에서 충분히 노출되도록 하는 목적이다.

문서 텍스트는 필드 라벨을 포함한다. 학습과 추론에서는 상품명을 title로 분리하고 나머지 필드를 text로 둔다.

```text
query: task: search result | query: <user query>
document: title: <product name> | text: brand/category/gender/price_range/attributes
```

문서 필드 누락에 대한 강건성을 보기 위해 document field-dropout variant를 train에만 사용했다. train에서는 full document를 절반으로 두고, name/brand/category/price 일부를 남기는 variant를 나머지 절반에 배분했다. validation/test는 full document만 유지했다. 본문에서 말하는 성능 수치는 모두 full document 평가 기준이다.

## 평가 설계

### Click-label 평가

기본 평가는 click-label test set과 same-language retrieval corpus로 수행했다. 보고서에는 상품 단위 split과 학습 데이터에서 구성한 corpus가 함께 기록되어 있지만, test positive를 검색 corpus에 어떻게 포함했는지와 corpus–split 교집합 집계는 남아 있지 않다. 따라서 아래 점수는 기록된 평가 내부의 비교로 읽으며, 새 상품에 대한 일반화나 후보 포함률까지 검증한 결과로 해석하지 않는다. query와 같은 언어의 corpus 안에서 top-K를 찾고, 원본 클릭 상품이 상위 결과에 포함되는지 측정한다. 주요 지표는 MAP@10, Hit@1, Recall@10, MRR@10, NDCG@10이다. 본문에서 `test MAP@10`이라고 쓰면 이 click-label 평가를 의미한다.

이 평가에는 관련 상품을 오답으로 처리할 수 있는 라벨 불완전성이 있다. 한 query의 positive 수가 평균적으로 적고, 특히 `립`, `선크림`처럼 넓은 검색어에는 클릭되지 않았지만 관련 있는 상품이 많다. 그래서 click-label MAP@10의 절대값은 실제 사용자가 보는 관련성보다 낮을 수 있다. 학습 전후처럼 효과 크기가 큰 비교에서는 상대 개선 방향이 LLM-judged 평가와 함께 움직였다. 근접 run 차이는 query-level paired bootstrap으로 다시 점검했다. test의 `15,883`개 pair는 `10,934`개 `(query, lang)` 그룹으로 묶여 query-level bootstrap의 재표집 단위가 됐다. 기존 집계에 보고된 overall MAP@10의 95% 불확실성 규모는 약 `±0.003`이지만, 이를 모든 비교에 공통인 임계값으로 적용하지 않고 비교별 paired CI를 우선한다. 학습 seed 간 변동은 이 CI에 포함되지 않는다.

### LLM-judged 보조 평가

클릭되지 않은 관련 상품을 점검하기 위해 KO test query 중 100개를 길이 bucket으로 stratified sampling했다. 1-2자 broad query 20개, 3-5자 query 50개, 6자 이상 specific query 30개를 고정했다. 각 평가 모델이 반환한 query별 상위 30개 후보에 대해 relevance를 0/1/2로 라벨링했다.

판정 단위는 `(query_id, goodsNo)`이고, 한 번 라벨링한 후보는 캐시에 저장해 후속 모델과 차원 평가에서 재사용했다. 따라서 기본 LLM-judged 평가는 모델별 top-30 결과에서 새로 등장한 후보를 누적 보정하는 audit에 가깝다. 이후 보강 검증에서는 학습 전 모델, 직전 non-MRL fine-tuned 모델, 대표 MRL 모델의 dim 768/256/128 top-30을 query별로 합친 통합 후보 풀(union-pooled) audit을 수행했다. 다만 이것도 전체 카탈로그 relevance benchmark는 아니다.

relevance rubric은 다음처럼 두었다.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>Label</th>
          <th>이름</th>
          <th>해석</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>2</code></td>
          <td>strongly relevant</td>
          <td>검색어를 입력한 사용자가 주답으로 받아들일 수 있는 상품</td>
        </tr>
        <tr>
          <td><code>1</code></td>
          <td>partially relevant</td>
          <td>의도나 카테고리는 관련되지만 직접적인 주답은 아닌 상품</td>
        </tr>
        <tr>
          <td><code>0</code></td>
          <td>unrelated</td>
          <td>다른 의도나 카테고리의 상품</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> LLM-judged relevance rubric이다. <code>expanded positives</code>는 원본 click positive와 relevance 1 이상 candidate의 합집합으로 정의했다.</figcaption>
</figure>

LLM-judged MAP@10은 Table 1의 rubric으로 확장한 positive 집합을 이진 라벨로 계산했다. 원본 click positive를 유지하고 relevance `1` 이상인 후보를 더했다. relevance 강도 차이는 MAP보다 NDCG@10에 더 직접 반영되므로, LLM-judged 결과에서는 MAP@10, Hit@1, NDCG@10을 함께 보되 Recall@10의 절대값은 보조로만 둔다.

LLM judge는 한 query의 상위 30개 후보를 한 번에 보고 라벨을 반환한다. LLM-as-a-judge는 rubric과 prompt에 민감하므로, 여기서는 주 평가자보다 click-label의 false negative를 진단하는 보조 라벨러로 제한해 사용했다 <a class="citation-ref" href="#ref-llm-judge" aria-label="Reference 6">[6]</a> <a class="citation-ref" href="#ref-geval" aria-label="Reference 7">[7]</a>. judge call은 structured output으로 JSON label array만 반환하도록 제한했다. self-consistency를 위해 temperature가 다른 3회 호출의 majority vote를 사용했고, tie는 false-negative를 줄이는 방향으로 높은 relevance를 선택했다.

초기 후보-라벨 쌍 `4,585`건 기준으로 3/3 일치 비율은 `94.9%`였다. label별 3/3 일치 비율은 strongly relevant `98.1%`, unrelated `94.5%`, partially relevant `91.0%`였다. 이후 Matryoshka dim 검증까지 누적된 judge 판정 쌍은 `7,130`건이다. 이 값은 사람 평가와의 agreement가 아니라 judge 내부 안정성이다. 따라서 LLM-judged metric은 click-label 절대 점수의 하한 편향을 설명하는 보조 증거로만 해석한다.

LLM 호출이 실패한 경우에는 보수적으로 원본 click-label만 남겼다. 따라서 LLM-judged metric은 모든 관련 상품을 완전히 찾은 값이 아니라, 고정된 상위 30개 후보군 안에서 false negative를 일부 보정한 추정치다.

### Matryoshka 차원 평가

Google의 EmbeddingGemma는 사전학습 모델부터 MRL 차원 축소를 지원한다 <a class="citation-ref" href="#ref-embeddinggemma" aria-label="Reference 1">[1]</a>. 이 글의 non-MRL은 이번 상품 검색 fine-tuning에서 MRL loss를 쓰지 않은 비교군을 뜻한다. Matryoshka 모델은 전체 768차원 embedding을 만든 뒤 앞쪽 prefix만 잘라 사용할 수 있다. 사용할 차원이 $d$일 때의 벡터는 다음처럼 정의한다.

$$
z_d = \mathrm{normalize}(z_{1:d})
$$

본문에서는 `768`, `512`, `256`, `128` 차원을 비교했다. dim 256은 저장 공간과 검색 index 비용을 768 대비 약 1/3로 줄일 수 있는 저차원 후보로 두었다. 검색 latency와 throughput은 추가로 exact cosine search 기준에서 실측했다. 단, 모델은 항상 768차원을 출력하므로 차원 축소는 encode 비용이 아니라 vector index 저장과 검색 비용을 줄이는 선택지다.

## 실험 설계

모든 주요 비교는 동일한 v1 데이터셋, same-language retrieval corpus, click-label 평가 조건을 기준으로 해석한다. 이 보고서의 주요 수치는 단일 run 계보에서 나온 결과이지만, 근접한 MAP@10 차이는 query-level paired bootstrap으로 사후 점검했다. 표에서 `측정 노이즈 수준`이라고 부르는 작은 overall 차이는 대체로 95% CI가 0을 포함했다. 사후 점검에서 `0.0005-0.0009` 수준의 차이는 구분되지 않았지만, 이는 동등성을 입증한 결과가 아니다. 실험 계보는 크게 네 단계다.

1. multilingual-e5-base fine-tuning을 기준선으로 둔다 <a class="citation-ref" href="#ref-e5" aria-label="Reference 2">[2]</a>.
2. base model을 Google의 EmbeddingGemma-300M으로 바꿔 모델 교체의 효과를 비교한다 <a class="citation-ref" href="#ref-embeddinggemma" aria-label="Reference 1">[1]</a>.
3. title prompt, longer training, CachedMultipleNegativesRankingLoss, larger batch를 묶어 contrastive 학습 신호를 강화한다. 구현은 Sentence-Transformers의 retrieval training 구성과 Matryoshka loss wrapper를 사용했다 <a class="citation-ref" href="#ref-sbert" aria-label="Reference 4">[4]</a> <a class="citation-ref" href="#ref-sentence-transformers" aria-label="Reference 5">[5]</a>.
4. 같은 데이터와 레시피 위에서 MatryoshkaLoss를 감싸 저차원 prefix 품질을 보존한다.

대표 학습 설정은 Table 2와 같다.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>축</th>
          <th>대표 설정</th>
          <th>역할</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Base model</td>
          <td><code>EmbeddingGemma-300M</code></td>
          <td>다국어 상품 검색 embedding prior</td>
        </tr>
        <tr>
          <td>Loss</td>
          <td><code>CachedMultipleNegativesRankingLoss</code></td>
          <td>단일 GPU에서 더 큰 effective in-batch negative 사용</td>
        </tr>
        <tr>
          <td>Batch</td>
          <td><code>192</code></td>
          <td>in-batch negatives 규모 확대</td>
        </tr>
        <tr>
          <td>Sampling</td>
          <td>same-language no-duplicate batch</td>
          <td>같은 언어 안의 query-document contrast 유지</td>
        </tr>
        <tr>
          <td>MRL dims</td>
          <td><code>[768, 512, 256, 128]</code></td>
          <td>저차원 prefix가 retrieval에 쓸 수 있도록 동시 학습</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> 대표 비교의 학습 설정이다. Matryoshka fine-tuning은 데이터, optimizer, sampler를 유지하고 loss 구조만 바꾼 비교로 해석한다.</figcaption>
</figure>

비교 실험에는 개선이 관찰된 조정 외에도 여러 설정을 포함했다. document augmentation ratio, source/variant weighted sampling, hard negative mining, brand-aware hard negative mining, query augmentation, gradient clipping, step 연장, uniform language sampling도 같은 평가 기준으로 확인했다. 이 비교군은 각 조정의 적용 범위를 보여준다. 여러 학습 seed의 반복 실험으로 효과 부재를 확정한 것은 아니다.

## 결과

### 통합 후보 풀에서의 768→256차원 절충

Table 3은 두 차원에 공통인 judged positive 집합으로 평가한 최종 보조 결과다. 학습 전 모델, non-MRL, MRL dim 768/256/128의 query별 top-30을 합친 union-pool을 사용했다. 이 방식은 모델별 후보만 라벨링하는 self-pool의 상대적 유리함을 줄이지만, 후보 풀 밖의 관련 상품까지 판정한 것은 아니다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead><tr><th>측정 항목</th><th class="align-right">MRL 768</th><th class="align-right">MRL 256</th><th>해석</th></tr></thead>
      <tbody>
        <tr><td>Union-pool MAP@10 ↑<br><span class="table-note-inline">KO 100개 query</span></td><td class="align-right"><code>0.9430</code></td><td class="align-right"><code>0.9381</code></td><td>256차원이 <code>0.0049</code> 낮음</td></tr>
        <tr><td>fp16 벡터 저장량 ↓<br><span class="table-note-inline">1M vectors, MB</span></td><td class="align-right"><code>1,536</code></td><td class="align-right"><code>512</code></td><td>256차원은 1/3</td></tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> MRL 차원 선택의 주요 근거다. MAP@10은 높을수록 좋고, 동일 개수·dtype의 벡터 저장량은 작을수록 좋다. 저장량은 벡터 자체의 크기이며 모델·메타데이터·검색 작업 메모리를 포함한 총 서비스 메모리는 아니다. 이 차원 간 MAP 차이의 CI와 사람 평가 agreement는 보고되지 않았다.</figcaption>
</figure>

768차원이 가장 높은 union-pool MAP@10을 보였고 Hit@1은 `1.0000`이었다. 기존 집계에는 256차원이 non-MRL 768차원보다도 높은 것으로 보고되어 있으나, 해당 non-MRL union-pool 수치가 제시되지 않아 여기서 차이를 정량화하지 않는다. 압축 후보 판단의 직접 근거는 표에 있는 MRL 두 차원의 비교다.

### 전체 성능과 누적 개선

학습 전 EmbeddingGemma-300M의 click-label test MAP@10은 `0.6558`이었다. 대표 Matryoshka 설정은 `0.8146`이었다. Table 4에서 모든 언어의 개선을 확인할 수 있고, JP의 상대 개선이 가장 컸다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Metric</th>
          <th class="align-right">Pretrained</th>
          <th class="align-right">MRL representative</th>
          <th class="align-right">Delta</th>
          <th class="align-right">Relative</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Overall MAP@10</td>
          <td class="align-right"><code>0.6558</code></td>
          <td class="align-right"><code>0.8146</code></td>
          <td class="align-right"><code>+0.1588</code></td>
          <td class="align-right"><code>+24.2%</code></td>
        </tr>
        <tr>
          <td>Overall Hit@1</td>
          <td class="align-right"><code>0.6034</code></td>
          <td class="align-right"><code>0.7691</code></td>
          <td class="align-right"><code>+0.1657</code></td>
          <td class="align-right"><code>+27.5%</code></td>
        </tr>
        <tr>
          <td>Overall Recall@10</td>
          <td class="align-right"><code>0.8074</code></td>
          <td class="align-right"><code>0.9344</code></td>
          <td class="align-right"><code>+0.1270</code></td>
          <td class="align-right"><code>+15.7%</code></td>
        </tr>
        <tr>
          <td>EN MAP@10</td>
          <td class="align-right"><code>0.6990</code></td>
          <td class="align-right"><code>0.8632</code></td>
          <td class="align-right"><code>+0.1642</code></td>
          <td class="align-right"><code>+23.5%</code></td>
        </tr>
        <tr>
          <td>JP MAP@10</td>
          <td class="align-right"><code>0.6225</code></td>
          <td class="align-right"><code>0.8580</code></td>
          <td class="align-right"><code>+0.2355</code></td>
          <td class="align-right"><code>+37.8%</code></td>
        </tr>
        <tr>
          <td>KO MAP@10</td>
          <td class="align-right"><code>0.6482</code></td>
          <td class="align-right"><code>0.8034</code></td>
          <td class="align-right"><code>+0.1552</code></td>
          <td class="align-right"><code>+24.0%</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> 학습 전 EmbeddingGemma-300M과 대표 Matryoshka 모델의 click-label test 비교다. 전체 test는 KO/EN/JP를 포함하며, 같은 prompt와 same-language retrieval corpus를 사용했다.</figcaption>
</figure>

Table 5의 모델 계보에서는 개선 폭이 초반에 크고 뒤로 갈수록 작아졌다. multilingual-e5-base 기준선의 최고치는 `0.7732`였고, EmbeddingGemma-300M으로 바꾸면 `0.7953`이 됐다. 이후 title prompt, step 수, CachedMNRL, batch size를 묶은 레시피 개선으로 `0.8151`까지 올라갔다. 이 설정 묶음 안에서 별도로 비교된 batch/loss 변경은 `0.8082 -> 0.8151`의 `+0.0069` 신호로 남았다. 사후 paired bootstrap에서도 이 양성 대조 비교는 `+0.0068`, 95% CI `[+0.0035, +0.0101]`로 0을 배제했다. Matryoshka fine-tuning은 dim 768 기준 `0.8146`으로 거의 같은 수준을 유지했다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>단계</th>
          <th>역할</th>
          <th class="align-right">Test MAP@10</th>
          <th class="align-right">Delta</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>multilingual-e5 fine-tuned</td>
          <td>baseline</td>
          <td class="align-right"><code>0.7732</code></td>
          <td class="align-right">-</td>
        </tr>
        <tr>
          <td>EmbeddingGemma fine-tuned</td>
          <td>base model 교체</td>
          <td class="align-right"><code>0.7953</code></td>
          <td class="align-right"><code>+0.0221</code></td>
        </tr>
        <tr>
          <td>recipe bundle</td>
          <td>title prompt, step, batch, loss 개선</td>
          <td class="align-right"><code>0.8151</code></td>
          <td class="align-right"><code>+0.0198</code></td>
        </tr>
        <tr>
          <td>MRL representative</td>
          <td>저차원 prefix 학습</td>
          <td class="align-right"><code>0.8146</code></td>
          <td class="align-right"><code>-0.0005</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 5.</strong> 모델 계보별 누적 개선이다. MRL 단계는 dim 768 점수 개선보다 저차원 prefix 품질을 보존하는 단계로 해석한다.</figcaption>
</figure>

### 학습 변경별 해석

Table 6에서 구분 가능한 개선이 남은 축은 두 가지였다. 첫째는 base model 교체다. e5-base에서 EmbeddingGemma-300M으로 바꾸면 KO/EN/JP 모두 개선됐다. 둘째는 설정 묶음 안에서 확인된 batch/loss 변경 신호다. CachedMultipleNegativesRankingLoss와 batch 192 조합은 batch 48 MNRL 대비 `+0.0069`를 만들었고, paired bootstrap에서도 구분 가능한 개선으로 남았다. 이는 한 배치에서 대조 학습에 쓰는 비정답 후보(in-batch negatives)를 늘린 효과와 일관된다. 다만 loss와 batch를 함께 바꾼 비교이므로 두 요소의 기여를 따로 추정하지 않는다. 모델 교체 역시 architecture, 사전학습 데이터와 embedding prior가 함께 달라져 capacity만의 인과 효과로 읽을 수 없다.

반면 데이터 조정 계열에서는 안정적인 신호가 거의 남지 않았다. query augmentation은 brand/category lexical overlap이 큰 query를 늘렸지만, 이미 해당 query군에서는 추가 개선 여지가 작았다. hard negative mining은 학습 신호를 더 어렵게 만들었지만, 같은 click-label test에서는 회귀했다. step을 6,000에서 12,000으로 늘려도 overall MAP@10 변화는 `+0.0008`에 그쳤고 bootstrap CI도 0을 포함했다. JP MAP@10 하락은 별도 언어별 bootstrap에서 `-0.0219`, 95% CI `[-0.0414, -0.0032]`로 확인됐다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Lever</th>
          <th>비교 기준</th>
          <th class="align-right">MAP@10 delta</th>
          <th>판정</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Base model 교체</td>
          <td>e5 기준선 -> EmbeddingGemma 기준선</td>
          <td class="align-right"><code>+0.0221</code></td>
          <td>유효 신호</td>
        </tr>
        <tr>
          <td>CachedMNRL + batch 192</td>
          <td>batch 48 long-run 대비</td>
          <td class="align-right"><code>+0.0069</code></td>
          <td>유효 신호</td>
        </tr>
        <tr>
          <td>MRL wrapper</td>
          <td>dim 768 기준</td>
          <td class="align-right"><code>-0.0005</code></td>
          <td>dim 768 유지, 저차원 품질 회복</td>
        </tr>
        <tr>
          <td>Document augmentation ratio</td>
          <td>short run baseline 대비</td>
          <td class="align-right"><code>+0.0005</code></td>
          <td>측정 노이즈 수준</td>
        </tr>
        <tr>
          <td>Weighted resampling</td>
          <td>short run baseline 대비</td>
          <td class="align-right"><code>+0.0006</code></td>
          <td>측정 노이즈 수준</td>
        </tr>
        <tr>
          <td>Hard negative mining</td>
          <td>cached baseline 대비</td>
          <td class="align-right"><code>-0.0057</code></td>
          <td>회귀</td>
        </tr>
        <tr>
          <td>Query augmentation</td>
          <td>short probe / full run</td>
          <td class="align-right"><code>-0.0131 / -0.0117</code></td>
          <td>회귀</td>
        </tr>
        <tr>
          <td>Gradient clipping 5.0</td>
          <td>short run baseline 대비</td>
          <td class="align-right"><code>-0.0063</code></td>
          <td>회귀</td>
        </tr>
        <tr>
          <td>Step 6,000 -> 12,000</td>
          <td>cached baseline 대비</td>
          <td class="align-right"><code>+0.0008</code></td>
          <td>overall 측정 노이즈 수준<br><span class="table-note-inline">JP MAP@10 <code>-0.0220</code></span></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 6.</strong> 주요 학습 변경의 요약이다. delta는 각 실험의 직접 비교 기준 대비 값이다. 전체 점수의 불확실성 규모 약 ±0.003을 공통 판정선으로 쓰지 않고, 비교별 paired bootstrap CI를 우선한다. batch/loss 변경의 CI는 0을 포함하지 않았다.</figcaption>
</figure>

이 결과는 추가 개선 신호가 약했던 비교군도 해석상 중요하다는 점을 보여준다. 현재 데이터 분포에서는 lexical overlap이 강한 query/document pair가 많았고, 그런 영역은 이미 상위 retrieval이 강했다. Bootstrap으로 점검한 비교에서는 overall `+0.001` 안팎의 변화가 구분되지 않았다. 이 관찰을 모든 후속 비교의 최소 효과 기준으로 적용하지는 않는다. 추가 개선은 같은 pair를 더 세게 학습하는 것보다, 의미 의도 query나 카탈로그 전체 후보군처럼 평가 난이도를 바꾸는 쪽에서 나올 가능성이 크다.

### Click-label과 LLM-judged 평가의 차이

click-label test에서 대표 MRL 설정의 KO MAP@10은 `0.8034`였다. 같은 모델을 KO 100개 stratified query의 상위 30개 후보군에 대한 LLM-judged metric으로 보면 MAP@10은 `0.9525`, Hit@1은 `1.0000`이었다. 두 값은 쿼리 모집단과 라벨 정의가 모두 다르다. 따라서 그 차이를 라벨 보정량으로 계산할 수 없다. 라벨 변경 효과만 분리하려면 동일한 KO 100개 query와 동일 ranking에 click-label과 expanded-label을 각각 적용한 짝지은 집계가 필요하지만, 그 값은 여기 제시되지 않았다.

중요한 점은 개선 방향이다. 학습 전후 개선 폭은 click-label과 LLM-judged에서 모두 컸다. Table 7의 click-label 전체 MAP@10은 `0.6558 -> 0.8146`, LLM-judged MAP@10은 `0.7739 -> 0.9525`였다. 두 평가에서 학습 전후의 방향이 일치한 것은 확인할 수 있다. 다만 서로 다른 쿼리 집합이므로 개선폭의 크기까지 직접 비교하지는 않는다. 작은 delta의 모델 순위는 paired bootstrap과 LLM 보조 평가를 함께 보아야 한다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>평가</th>
          <th class="align-right">Pretrained</th>
          <th class="align-right">Non-MRL fine-tuned</th>
          <th class="align-right">MRL fine-tuned</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Click-label test MAP@10<br><span class="table-note-inline">전체 KO/EN/JP test</span></td>
          <td class="align-right"><code>0.6558</code></td>
          <td class="align-right"><code>0.8151</code></td>
          <td class="align-right"><code>0.8146</code></td>
        </tr>
        <tr>
          <td>LLM-judged MAP@10<br><span class="table-note-inline">KO stratified 100, dim 768</span></td>
          <td class="align-right"><code>0.7739</code></td>
          <td class="align-right"><code>0.9493</code></td>
          <td class="align-right"><code>0.9525</code></td>
        </tr>
        <tr>
          <td>LLM-judged dim 256 MAP@10</td>
          <td class="align-right">-</td>
          <td class="align-right"><code>0.9321</code></td>
          <td class="align-right"><code>0.9506</code></td>
        </tr>
        <tr>
          <td>LLM-judged dim 128 MAP@10</td>
          <td class="align-right">-</td>
          <td class="align-right"><code>0.8950</code></td>
          <td class="align-right"><code>0.9332</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 7.</strong> click-label과 LLM-judged 평가의 역할 차이다. click-label은 전체 실험 비교의 기본 지표이고, 표의 LLM-judged 수치는 별도의 KO 표본에서 모델별 top-30 후보 풀(self-pool)의 관련성을 보완한 보조 지표다. 행 간 차이는 라벨 보정 효과와 쿼리 구성 효과를 분리하지 못한다.</figcaption>
</figure>

LLM-judged 평가에서 Recall@10은 주의해서 읽어야 한다. expanded positives를 쓰면 positive 분모가 원본 click-label보다 크게 늘어난다. top-10 안의 관련 상품 수가 늘어도 분모가 더 빠르게 커지면 Recall@10 비율은 낮아질 수 있다. 그래서 LLM-judged 환경에서는 binary relevance 기준 MAP@10, top-1 만족 여부를 보는 Hit@1, relevance grade를 반영하는 NDCG@10을 주요 해석 지표로 두었다.

추가로 통합 후보 풀(union-pooled) audit을 수행해 모델별 후보 풀(self-pool) 편향을 확인했다. 학습 전 모델, non-MRL, MRL dim 768/256/128의 top-30을 query별로 합치고 같은 judged positive set으로 재채점하자, self-pool MAP@10은 전반적으로 `0.009-0.023` 높게 잡혔다. 그래도 MRL dim 768은 union-pool MAP@10 `0.9430`으로 가장 높았고, Hit@1은 여전히 `1.0000`이었다. 따라서 LLM-judged `0.95`대 수치는 self-pool audit 기준으로 읽고, union-pool에서는 약 `0.943` 수준의 보수적 점수로 보는 편이 맞다.

### Matryoshka 차원 절충

Matryoshka fine-tuning의 가치는 dim 768 click-label 점수에서 거의 보이지 않는다. non-MRL 모델과 MRL 모델은 click-label dim 768에서 거의 같은 수준이다. 차이는 저차원 slice의 품질 회복과 색인 비용 절충에서 나타난다.

동일 모델의 차원 선택은 Table 3의 union-pool MAP@10 `0.9430 → 0.9381`을 기준으로 본다. 기존 self-pool에서는 `0.9525 → 0.9506`으로 0.002 이내였고 Hit@1은 둘 다 `1.0000`이었다. 후보 풀을 통합하면 남는 차이가 커지므로, self-pool에서 가까운 점수만으로 무손실 압축을 주장할 수 없다. 차원별 self-pool 그림과 전체 값은 Appendix Figure 1과 Appendix Table 5에 남겼다.

### 벡터 저장량과 검색 비용의 범위

모델은 항상 768차원 embedding을 출력하므로 prefix를 잘라도 encoder 연산은 줄지 않는다. 기존 기록의 단일 query encode는 `47.6 ms`, batch encode는 `455 docs/s`였다. 저장 쪽에서는 1M fp16 벡터가 768차원 `1,536 MB`, 256차원 `512 MB`로, 메모리 비율은 `0.333`이다. 이는 차원 수와 dtype에서 계산되는 벡터 payload 크기와 일치한다.

같은 기록의 GPU exact-search는 query당 `6.47 ms → 2.23 ms`, QPS는 `8,070 → 14,545`이며, QPS 비율은 `1.80x`였다. latency는 query 처리 시간, QPS는 초당 처리한 query 수지만, 이 수치들은 단일 직렬 요청에서 기대되는 역수 관계가 아니다. 하드웨어, query batch 크기, 동시성, warm-up, 반복 횟수와 시간 측정 범위가 제시되지 않아 두 지표를 하나의 서비스 처리 방식으로 연결할 수 없다. 따라서 검색 비용 감소의 관찰 기록으로 보존하되, end-to-end 응답속도나 운영 QPS 개선폭으로 사용하지 않는다.

## 결론 및 해석

본 실험에서는 모델 교체와 batch/loss 조합의 변경에서 개선이 관찰됐다. 모델 교체는 여러 조건이 함께 달라지는 비교이며, capacity 하나의 효과를 분리하지는 못했다. 한편 batch/loss 변경은 effective in-batch negative 규모 확대와 일관된 추가 개선을 보였다. 같은 데이터 분포 안에서 query augmentation, hard negative mining, weighted resampling, 단순 step 연장은 안정적인 추가 개선을 만들지 못했다. 이는 현재 데이터의 주요 신호가 lexical overlap과 클릭 로그 기반 pair에 이미 많이 담겨 있었음을 시사한다.

두 번째 결론은 평가 병목이다. click-label metric은 학습 전후처럼 효과가 큰 비교에서 유용했고, LLM-judged audit은 클릭되지 않은 관련 후보가 존재할 수 있음을 점검하는 보조 장치였다. 서로 다른 쿼리 집합의 점수 차이로 편향의 크기를 추정할 수는 없다. 이 결과는 클릭 라벨이 큰 학습 효과의 방향을 확인하는 데 유용함을 보여준다. 작은 점수 차이로 모델 순위를 정하거나 절대 점수를 해석할 때는 관련 상품 라벨을 확장한 보조 평가와 불확실성 점검이 함께 필요하다.

세 번째 결론은 Matryoshka fine-tuning의 색인 차원 관점 의미다. MRL은 dim 768 ranking을 크게 올리는 기술이 아니었다. 그러나 fine-tuning 과정에서 약화될 수 있는 저차원 prefix 품질을 회복했고, dim 256을 비용 절감 후보로 만들었다. 통합 후보 풀 audit을 반영하면 dim 256은 dim 768과 완전히 같은 품질이 아니라 약 `0.005` MAP@10 낮은 후보로 보는 편이 정확하다. 1M fp16 벡터의 저장량은 1/3이며, 기록된 GPU QPS 비율은 `1.80x`였다. 후자는 측정 조건이 충분하지 않아 서빙 성능의 일반적 개선폭으로 제시할 수 없다. 따라서 dim 256의 의미는 무손실 압축이 아니라 retrieval 품질과 vector index 비용 사이의 명시적 절충이다.

따라서 다음 연구 질문은 "같은 데이터로 어떤 학습 설정을 더 붙일 것인가"보다 "평가와 데이터 분포를 어떻게 바꿀 것인가"에 가깝다. 후보는 세 가지다. 첫째, 실제 카탈로그 전체 후보군에서 retrieval이 같은 패턴을 보이는지 확인한다. 둘째, LLM-judged metric과 사람 relevance 평가의 agreement를 측정한다. 셋째, lexical overlap이 약한 semantic intent query를 별도 데이터 분포로 구성한다.

## 한계

- LLM-judged 평가는 고정된 KO 100개 stratified query에 대한 보조 평가다. self-consistency는 높았지만, 사람 평가자와의 agreement는 아직 직접 측정하지 않았다. judge 모델/version, 전체 prompt와 호출 실패율도 제시되지 않아 판정 재현에는 한계가 있다. 동점에서 높은 relevance를 택한 정책은 positive를 늘리는 방향이다.
- click-label test와 LLM-judged test의 query 범위가 다르다. click-label test는 전체 KO/EN/JP test이고, LLM-judged 평가는 KO stratified subset이다.
- retrieval corpus는 학습 데이터에서 구성한 same-language corpus로 기록되어 있다. 상품 단위 split과의 교집합, test positive 포함 규칙과 후보 포함률을 확인할 자료가 없어 새로운 상품에 대한 일반화는 판단하지 않는다. 전체 카탈로그, 품절/신상품, dynamic ranking feature, 가격 필터, personalization은 포함하지 않았다.
- dim 256의 벡터 저장량은 줄지만 encode 비용은 줄지 않는다. exact-search latency/QPS는 batch·하드웨어·warm-up·측정 범위가 불명확한 기록이다. ANN index, quantization, batch serving, 실제 vector DB 설정에서는 절감폭이 달라질 수 있다.
- hard negative와 augmentation에서 추가 이득이 확인되지 않은 것은 현재 정책과 데이터 분포에 대한 결과다. semantic intent query처럼 분포를 바꾼 데이터에서는 다른 결과가 나올 수 있다.
- 본문은 특정 카탈로그의 공개 벤치마크를 제안하지 않는다. 개별 상품명과 서비스 식별자를 제거했기 때문에, 공개 독자는 방법과 평가 설계를 검토할 수 있지만, 원 점수의 독립 재계산은 할 수 없다.

## Appendix: 실험 표기와 보조 결과

Appendix Table 1은 데이터 구성, Appendix Table 2는 학습 연장에 따른 점수 변화, Appendix Table 3은 주요 모델의 click-label 지표를 정리한다. Appendix Table 4의 길이별 보조 점수는 전체 집계와의 대응에 미확인 부분이 있어 별도로 읽는다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>항목</th>
          <th>설정</th>
          <th class="align-right">규모</th>
          <th>해석</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Train split</td>
          <td>상품 단위 분리</td>
          <td class="align-right"><code>282,263</code></td>
          <td>같은 상품이 train/valid/test에 동시에 등장하지 않도록 구성했다.</td>
        </tr>
        <tr>
          <td>Validation split</td>
          <td>full document only</td>
          <td class="align-right"><code>14,877</code></td>
          <td>학습용 document variant를 평가에는 사용하지 않았다.</td>
        </tr>
        <tr>
          <td>Test split</td>
          <td>full document only</td>
          <td class="align-right"><code>15,883</code></td>
          <td>본문의 click-label metric은 모두 이 split 기준이다.</td>
        </tr>
        <tr>
          <td>Query source</td>
          <td>click-derived query / global keyword / product-name n-gram</td>
          <td class="align-right"><code>237,054 / 34,221 / 10,988</code></td>
          <td>한국어 click-derived source 중심 분포에 EN/JP keyword와 long-tail query를 보강했다.</td>
        </tr>
        <tr>
          <td>Language exposure</td>
          <td>temperature sampling</td>
          <td class="align-right"><code>KO 63% / EN 25% / JP 12%</code></td>
          <td>raw KO 비중이 높은 상태에서 다국어 contrastive batch 노출을 보정했다.</td>
        </tr>
        <tr>
          <td>Train document variants</td>
          <td>field-dropout</td>
          <td class="align-right"><code>50 / 20 / 15 / 10 / 5%</code></td>
          <td>full, name-brand-category-price, name-brand-category, name-brand, name-only 비율이다.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 1.</strong> 공개 가능한 데이터 구성과 평가 조건의 요약이다. 개별 상품명과 식별자는 제거했지만, split, query source, language exposure, document variant 정책은 설계 검토를 위해 남겼다. 이 표만으로 검색 corpus의 구성이나 원 점수를 재현할 수는 없다.</figcaption>
</figure>

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th class="align-right">Step</th>
          <th class="align-right">Valid MAP@10</th>
          <th>해석</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="align-right"><code>2,000</code></td>
          <td class="align-right"><code>0.8245</code></td>
          <td>초기 수렴 구간이다.</td>
        </tr>
        <tr>
          <td class="align-right"><code>4,000</code></td>
          <td class="align-right"><code>0.8368</code></td>
          <td>주요 개선이 남아 있다.</td>
        </tr>
        <tr>
          <td class="align-right"><code>6,000</code></td>
          <td class="align-right"><code>0.8424</code></td>
          <td>대표 cached contrastive recipe와 같은 구간이다.</td>
        </tr>
        <tr>
          <td class="align-right"><code>8,000</code></td>
          <td class="align-right"><code>0.8452</code></td>
          <td>이 probe의 best checkpoint다.</td>
        </tr>
        <tr>
          <td class="align-right"><code>10,000</code></td>
          <td class="align-right"><code>0.8448</code></td>
          <td>best 대비 변화가 작다.</td>
        </tr>
        <tr>
          <td class="align-right"><code>12,000</code></td>
          <td class="align-right"><code>0.8445</code></td>
          <td>단순 step 연장이 안정적인 추가 개선으로 이어지지 않았다.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 2.</strong> cached contrastive recipe의 12k-step probe에서 본 validation trajectory다. 6k-8k 이후 개선 폭이 줄어들어, 같은 데이터 분포에서 단순 학습 연장보다 평가·데이터 분포 변경이 더 중요한 후속 질문으로 남았다.</figcaption>
</figure>

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>역할 기반 이름</th>
          <th>핵심 변경</th>
          <th class="align-right">MAP@10</th>
          <th class="align-right">Hit@1</th>
          <th class="align-right">Recall@10</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Pretrained EmbeddingGemma</td>
          <td>fine-tuning 없음</td>
          <td class="align-right"><code>0.6558</code></td>
          <td class="align-right"><code>0.6034</code></td>
          <td class="align-right"><code>0.8074</code></td>
        </tr>
        <tr>
          <td>e5 fine-tuned baseline</td>
          <td>multilingual-e5-base</td>
          <td class="align-right"><code>0.7732</code></td>
          <td class="align-right"><code>0.7261</code></td>
          <td class="align-right"><code>0.9039</code></td>
        </tr>
        <tr>
          <td>EmbeddingGemma baseline</td>
          <td>base model 교체</td>
          <td class="align-right"><code>0.7953</code></td>
          <td class="align-right"><code>0.7465</code></td>
          <td class="align-right"><code>0.9221</code></td>
        </tr>
        <tr>
          <td>Longer title-prompt recipe</td>
          <td>title prompt, batch 48, longer training</td>
          <td class="align-right"><code>0.8082</code></td>
          <td class="align-right"><code>0.7610</code></td>
          <td class="align-right"><code>0.9306</code></td>
        </tr>
        <tr>
          <td>Cached contrastive recipe</td>
          <td>batch 192, cached MNRL</td>
          <td class="align-right"><code>0.8151</code></td>
          <td class="align-right"><code>0.7691</code></td>
          <td class="align-right"><code>0.9326</code></td>
        </tr>
        <tr>
          <td>Representative MRL recipe</td>
          <td>MatryoshkaLoss wrapper</td>
          <td class="align-right"><code>0.8146</code></td>
          <td class="align-right"><code>0.7691</code></td>
          <td class="align-right"><code>0.9344</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 3.</strong> 역할 기반 주요 실험표다. 모든 수치는 click-label test, same-language corpus, dim 768 기준이다.</figcaption>
</figure>

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Query length bucket</th>
          <th class="align-right">n</th>
          <th class="align-right">Pretrained MAP@10</th>
          <th class="align-right">Non-MRL MAP@10</th>
          <th class="align-right">MRL MAP@10</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>short 1-2 chars</td>
          <td class="align-right"><code>20</code></td>
          <td class="align-right"><code>0.806</code></td>
          <td class="align-right"><code>0.928</code></td>
          <td class="align-right"><code>0.9628</code></td>
        </tr>
        <tr>
          <td>mid 3-5 chars</td>
          <td class="align-right"><code>50</code></td>
          <td class="align-right"><code>0.726</code></td>
          <td class="align-right"><code>0.941</code></td>
          <td class="align-right"><code>0.9527</code></td>
        </tr>
        <tr>
          <td>long 6+ chars</td>
          <td class="align-right"><code>30</code></td>
          <td class="align-right"><code>0.833</code></td>
          <td class="align-right"><code>0.948</code></td>
          <td class="align-right"><code>0.9449</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 4.</strong> KO LLM-judged 100 query의 길이 bucket별 MAP@10이다. 표의 non-MRL 값을 표본 수 20/50/30으로 가중하면 약 0.9405로, 본문 전체 self-pool 값 0.9493과 일치하지 않는다. 동일 모델·후보 풀 집계인지 확인할 근거가 없어, 길이별 개선폭의 정량 비교는 보류한다. 기존 bucket 값을 보존하되 본문 전체 결과와 합쳐 해석하지 않는다.</figcaption>
</figure>

### 모델별 후보 풀의 차원별 보조 결과

Appendix Figure 1과 Appendix Table 5는 통합 후보 풀을 쓰기 전의 self-pool 결과다. 본문의 최종 차원 선택을 대체하지 않으며, prefix별 순위 변화가 어떻게 나타났는지 살펴보는 용도로 남긴다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/noisy-click-mrl-retrieval/mrl-dim-tradeoff.svg" alt="MRL fine-tuned 모델과 non-MRL fine-tuned 모델의 768, 512, 256, 128 차원 LLM-judged MAP@10을 비교한 선 그래프">
  <figcaption><strong>Appendix Figure 1.</strong> Matryoshka 차원별 LLM-judged 모델별 후보 풀(self-pool) MAP@10이다. non-MRL 모델은 dim 256과 dim 128에서 품질 손실이 커졌지만, MRL fine-tuning은 self-pool 기준 dim 256을 dim 768과 가깝게 유지했다. 모델별 positive 집합이 달라질 수 있으므로 최종 차원 선택에는 본문 Table 3의 union-pool 결과를 우선한다.</figcaption>
</figure>

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Dim</th>
          <th class="align-right">Non-MRL MAP@10</th>
          <th class="align-right">MRL MAP@10</th>
          <th class="align-right">MRL drop vs 768</th>
          <th class="align-right">Top-1 변경<br><span class="table-note-inline">vs 768</span></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><code>768</code></td>
          <td class="align-right"><code>0.9493</code></td>
          <td class="align-right"><code>0.9525</code></td>
          <td class="align-right"><code>0.0000</code></td>
          <td class="align-right"><code>0/100</code></td>
        </tr>
        <tr>
          <td><code>512</code></td>
          <td class="align-right"><code>0.9472</code></td>
          <td class="align-right"><code>0.9505</code></td>
          <td class="align-right"><code>-0.0020</code></td>
          <td class="align-right"><code>26/100</code></td>
        </tr>
        <tr>
          <td><code>256</code></td>
          <td class="align-right"><code>0.9321</code></td>
          <td class="align-right"><code>0.9506</code></td>
          <td class="align-right"><code>-0.0019</code></td>
          <td class="align-right"><code>36/100</code></td>
        </tr>
        <tr>
          <td><code>128</code></td>
          <td class="align-right"><code>0.8950</code></td>
          <td class="align-right"><code>0.9332</code></td>
          <td class="align-right"><code>-0.0193</code></td>
          <td class="align-right"><code>47/100</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 5.</strong> Matryoshka 차원별 모델별 후보 풀(self-pool) 품질이다. top-1 변경은 dim 768 결과와 같은 query에서 1위 상품이 바뀐 횟수다. dim 256은 top-1 상품이 자주 바뀌지만 self-pool relevance 기준 MAP@10과 Hit@1은 거의 유지됐다.</figcaption>
</figure>

## References

<div class="reference-list" markdown="1">

1. <span id="ref-embeddinggemma"></span>Google. [EmbeddingGemma 300M model card](https://huggingface.co/google/embeddinggemma-300m). 2025.
2. <span id="ref-e5"></span>Liang Wang et al. [Multilingual E5 Text Embeddings: A Technical Report](https://arxiv.org/abs/2402.05672). arXiv, 2024. [multilingual-e5-base model card](https://huggingface.co/intfloat/multilingual-e5-base).
3. <span id="ref-mrl"></span>Aditya Kusupati et al. [Matryoshka Representation Learning](https://arxiv.org/abs/2205.13147). NeurIPS 2022.
4. <span id="ref-sbert"></span>Nils Reimers and Iryna Gurevych. [Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks](https://aclanthology.org/D19-1410/). EMNLP-IJCNLP 2019.
5. <span id="ref-sentence-transformers"></span>UKPLab. [Sentence-Transformers: training losses](https://www.sbert.net/docs/package_reference/sentence_transformer/losses.html) 및 [Matryoshka embeddings](https://www.sbert.net/examples/sentence_transformer/training/matryoshka/README.html).
6. <span id="ref-llm-judge"></span>Lianmin Zheng et al. [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://proceedings.neurips.cc/paper_files/paper/2023/hash/91f18a1287b398d378ef22505bf41832-Abstract-Datasets_and_Benchmarks.html). NeurIPS 2023.
7. <span id="ref-geval"></span>Yang Liu et al. [G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment](https://aclanthology.org/2023.emnlp-main.153/). EMNLP 2023.

</div>

## Citation

Text citation:

```text
Ahn, I. (2026). 희소 클릭 라벨에서 다국어 상품 검색 임베딩 평가와 Matryoshka 압축. Technical report. https://muted-color.github.io/technical-reports/noisy-click-mrl-retrieval/
```

BibTeX:

```bibtex
@techreport{ahn2026noisyclickmrlretrieval,
  title = {희소 클릭 라벨에서 다국어 상품 검색 임베딩 평가와 Matryoshka 압축},
  author = {Ahn, Ilho},
  year = {2026},
  institution = {Independent},
  type = {Technical report},
  url = {https://muted-color.github.io/technical-reports/noisy-click-mrl-retrieval/}
}
```
