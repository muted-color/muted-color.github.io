---
title: "희소 클릭 라벨에서 다국어 상품 검색 임베딩 평가와 Matryoshka 압축"
layout: post
date: 2026-05-30 16:30:00 +0900
last_modified_at: 2026-05-30 20:49:21 +0900
categories: ["RETRIEVAL EVAL"]
tags: [retrieval, embeddings, product-search, multilingual-retrieval, contrastive-learning, click-labels, llm-judge, matryoshka-representation-learning, embedding-compression, ablation-study]
excerpt: "희소 클릭 라벨 환경에서 다국어 상품 검색 임베딩을 평가하고, Matryoshka fine-tuning의 저차원 검색 품질 보존을 점검한다."
description: "다국어 상품 검색 임베딩에서 sparse click-label 평가의 한계를 LLM-judged 보조 평가로 점검하고, base model 교체, effective in-batch negatives, Matryoshka fine-tuning이 click-label MAP@10 및 저차원 검색 품질에 미치는 영향을 정리한다."
permalink: /technical-reports/noisy-click-mrl-retrieval/
image: /assets/images/common/editorial-hero-social.png
image_alt: "희소 클릭 라벨 검색 평가와 Matryoshka 임베딩 압축 분석 노트를 나타내는 소셜 썸네일"
hero_image: /assets/images/posts/noisy-click-mrl-retrieval/hero.svg
hero_alt: "희소 클릭 positive, LLM 보조 평가, contrastive fine-tuning, Matryoshka 저차원 색인 선택지를 연결한 파이프라인 도식"
hero_caption: "<strong>Figure 1.</strong> 희소 클릭 라벨 기반 상품 검색에서는 학습 개선과 평가 노이즈를 분리해야 한다. 이 보고서는 click-label metric, LLM-judged relevance audit, contrastive fine-tuning lever, Matryoshka 저차원 임베딩을 하나의 평가 흐름으로 연결한다."
hero_frame: true
hero_variant: rounded-wide
math: true
hidden: true
publication_status: "technical-report"
report_scope: "technical report"
lab_path: "projects/serach-lm"
---

상품 검색 임베딩의 성능을 클릭 로그로만 평가하면 절대 점수가 낮게 보일 수 있다. 사용자는 하나의 상품을 클릭하지만, 짧고 넓은 검색어에는 관련 상품이 여러 개 존재한다. 모델이 클릭되지 않은 관련 상품을 상위에 올리면 click-label metric에서는 오답으로 처리된다. 본 분석은 이 문제를 단순한 모델 학습 문제가 아니라 **희소 positive 라벨 아래에서 retrieval 개선을 어떻게 측정하고, 저차원 색인으로 옮길 수 있는지**를 묻는 문제로 정의한다.

평가 질문은 세 가지다. 첫째, click-label MAP@10은 라벨 노이즈가 있어도 어떤 범위에서 모델 간 상대 비교 신호로 쓸 수 있는가. 둘째, 어떤 학습 lever가 다국어 상품 검색 임베딩에서 반복적으로 남는 개선을 만드는가. 셋째, Matryoshka fine-tuning은 768차원 품질을 유지하면서 256차원 임베딩을 저차원 색인 후보로 만들 수 있는가 <a class="citation-ref" href="#ref-mrl" aria-label="Reference 3">[3]</a>.

현 test contract에서 반복적으로 남은 개선 신호는 base model 교체와 batch/loss 변경을 통한 effective in-batch negative 규모 확대 쪽에 집중됐다. 데이터 합성, hard negative mining, weighted resampling, 단순 step 연장은 같은 데이터 분포 안에서는 안정적인 추가 개선을 만들지 못했다. Matryoshka fine-tuning은 dim 768 click-label 성능을 거의 유지하면서, LLM-judged 기준 dim 256 MAP@10을 dim 768과 0.002 이내로 맞췄다. 다만 작은 delta의 순위 판정에는 반복 seed나 bootstrap CI가 없으므로 보수적으로 해석한다.

이 글은 특정 서비스의 원천 데이터를 공개하는 문서가 아니다. 서비스명, 개별 상품명, 상품 식별자, 내부 경로는 제거했고, 데이터와 샘플은 역할 중심으로 익명화했다. 따라서 핵심 비교 대상은 특정 카탈로그의 절대 성능보다, 희소 click-label retrieval에서 평가 보정과 저차원 임베딩 선택을 어떻게 함께 다룰 수 있는지다.

> **click-label metric**은 검색 로그에서 관측된 클릭 상품만 positive로 둔 평가다. broad query의 관련 상품을 많이 놓치므로 절대 점수는 낮게 보일 수 있다.
>
> **LLM-judged metric**은 고정된 쿼리 샘플의 상위 후보를 relevance rubric으로 다시 라벨링한 보조 평가다. click-label을 대체하기보다 false-negative가 절대 점수에 미치는 영향을 추정하는 용도로 사용한다.
>
> **Matryoshka fine-tuning**은 하나의 embedding에서 앞쪽 차원 prefix가 각각 retrieval에 쓸 수 있도록 여러 차원에서 동시에 학습하는 방식이다. 이 설정에서는 768차원으로 encode한 뒤 앞 256차원을 slice하고 재정규화하는 사용법을 평가했다.

{% include model-mention-cards.html label="사용한 주요 리소스" aria_label="사용한 검색 임베딩과 평가 리소스" models="EmbeddingGemma 300M|google/embeddinggemma-300m|https://huggingface.co/google/embeddinggemma-300m;multilingual-e5-base|intfloat/multilingual-e5-base|https://huggingface.co/intfloat/multilingual-e5-base;Matryoshka Representation Learning|Kusupati et al. 2022|https://arxiv.org/abs/2205.13147;Sentence-Transformers|retrieval training toolkit|https://www.sbert.net/" %}

## 분석 포인트

- 희소 click positive와 broad query false negative가 있는 다국어 상품 검색 평가 문제를 정리했다.
- base model, prompt, batch/loss, Matryoshka fine-tuning, 데이터 합성, hard negative, step 연장 같은 lever를 같은 test contract 안에서 비교했다.
- click-label metric과 LLM-judged relevance audit의 역할을 분리해, 상대 개선과 expanded relevance 기준 보조 해석을 따로 제시했다.
- Matryoshka fine-tuning이 dim 768 품질을 거의 유지하면서 dim 256 저차원 색인 선택지를 제공하는지 측정했다.
- 추가 개선의 병목이 학습 설정 조정보다 semantic intent 데이터, 카탈로그 전체 검증, 사람 agreement 측정으로 이동했음을 정리했다.

## 요약

- 학습 전 EmbeddingGemma-300M은 click-label test MAP@10 `0.6558`이었다. 같은 평가 조건에서 대표 MRL 설정은 `0.8146`까지 올라갔다. 상대 개선은 `+24.2%`다.
- multilingual-e5-base fine-tuning 최고치 `0.7732`에서 EmbeddingGemma-300M 기준선으로 바꾸면 MAP@10이 `0.7953`으로 올라갔다. base model 교체만으로 `+0.0221`이 남았다.
- title prompt와 longer training을 포함한 레시피 개선 뒤, CachedMultipleNegativesRankingLoss와 per-device batch `192` 조합은 MAP@10을 `0.8082 -> 0.8151`로 올렸다. 이 비교는 in-batch negatives 규모 확대와 일관된 신호로 해석한다.
- Matryoshka fine-tuning은 dim 768 click-label MAP@10을 `0.8151 -> 0.8146`으로 거의 유지했다. 대신 LLM-judged dim 256 MAP@10을 non-MRL `0.9321`에서 `0.9506`으로 회복했다.
- click-label test에서는 대표 MRL 설정이 KO MAP@10 `0.8034`로 보였지만, KO 100개 stratified query와 상위 30개 후보군을 다시 라벨링한 LLM-judged 평가에서는 dim 768 MAP@10 `0.9525`, Hit@1 `1.0000`이었다. 이는 click-label 절대값이 broad query false negative로 낮아질 수 있음을 보여주는 보조 근거다.
- LLM-judged 평가는 모델별 top-30 후보를 라벨링하고 `(query_id, goodsNo)` 단위 라벨 캐시를 누적하는 audit이다. 전체 카탈로그 후보를 완전 pooling한 relevance benchmark는 아니다.
- query augmentation, hard negative mining, weighted resampling, gradient clipping, uniform language sampling, 단순 step 연장은 같은 데이터 분포에서는 안정적인 추가 이득을 만들지 못했다.

## 문제 설정

검색 태스크는 asymmetric retrieval이다. 입력 query는 사용자가 검색창에 입력한 짧은 문자열이고, document는 상품명, 브랜드, 카테고리, 성별, 가격대, 속성 텍스트를 결합한 익명화 상품 문서다. 모델은 query embedding과 document embedding의 cosine similarity로 같은 언어 카탈로그 안에서 top-K 상품을 찾는다.

데이터셋은 익명화된 click-derived query-product pair, product metadata, 다국어 keyword source를 결합해 만들었다. query source는 한국어 click-derived query, 글로벌 keyword source, product-name n-gram으로 나뉜다. train/valid/test는 상품 단위로 분리해 같은 상품이 여러 split에 동시에 등장하지 않도록 했다. 학습 split은 `282,263` pair, validation은 `14,877`, test는 `15,883` pair다.

학습 pair의 대부분은 한국어 click-derived source에서 왔다. raw train 기준 KO 비중은 약 `81%`였고, temperature-based language sampling으로 학습 노출 비중을 KO `63%`, EN `25%`, JP `12%` 수준으로 완화했다. 이 조정은 KO 우위를 완전히 지우기보다 EN/JP가 contrastive batch 안에서 충분히 노출되도록 하는 목적이다.

문서 텍스트는 필드 라벨을 포함한다. 학습과 추론에서는 상품명을 title로 분리하고 나머지 필드를 text로 둔다.

```text
query: task: search result | query: <user query>
document: title: <product name> | text: brand/category/gender/price_range/attributes
```

문서 필드 누락에 대한 강건성을 보기 위해 document field-dropout variant를 train에만 사용했다. train에서는 full document를 절반으로 두고, name/brand/category/price 일부를 남기는 variant를 나머지 절반에 배분했다. validation/test는 full document만 유지했다. 본문에서 말하는 성능 수치는 모두 full document 평가 기준이다.

## 평가 설계

### Click-label 평가

기본 평가는 click-label test set과 same-language retrieval corpus로 수행했다. query와 같은 언어의 corpus 안에서 top-K를 찾고, 원본 클릭 상품이 상위 결과에 포함되는지 측정한다. 주요 지표는 MAP@10, Hit@1, Recall@10, MRR@10, NDCG@10이다. 본문에서 `test MAP@10`이라고 쓰면 이 click-label 평가를 의미한다.

이 평가는 noisy하다. 한 query의 positive 수가 평균적으로 적고, 특히 `립`, `선크림`처럼 넓은 검색어에는 클릭되지 않았지만 관련 있는 상품이 많다. 그래서 click-label MAP@10의 절대값은 실제 사용자가 보는 관련성보다 낮을 수 있다. 학습 전후처럼 효과 크기가 큰 비교에서는 상대 개선 방향이 LLM-judged 평가와 함께 움직였다. 반면 `0.001-0.007` 수준의 근접 run 차이는 반복 seed나 bootstrap CI 없이 순위를 확정하는 근거로 보지 않았다.

### LLM-judged 보조 평가

click-label 절대값의 하한 편향을 보기 위해 KO test query 중 100개를 길이 bucket으로 stratified sampling했다. 1-2자 broad query 20개, 3-5자 query 50개, 6자 이상 specific query 30개를 고정했다. 각 평가 모델이 반환한 query별 상위 30개 후보에 대해 relevance를 0/1/2로 라벨링했다.

판정 단위는 `(query_id, goodsNo)`이고, 한 번 라벨링한 후보는 캐시에 저장해 후속 모델과 차원 평가에서 재사용했다. 따라서 이 평가는 모델별 top-30 결과에서 새로 등장한 후보를 누적 보정하는 audit에 가깝다. 모든 비교 모델의 후보를 사전에 합친 complete pooling 평가나 전체 카탈로그 relevance benchmark는 아니다.

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

LLM-judged MAP@10은 relevance `1` 이상을 binary positive로 두고 계산했다. relevance 강도 차이는 MAP보다 NDCG@10에 더 직접 반영되므로, LLM-judged 결과에서는 MAP@10, Hit@1, NDCG@10을 함께 보되 Recall@10의 절대값은 보조로만 둔다.

LLM judge는 한 query의 상위 30개 후보를 한 번에 보고 라벨을 반환한다. LLM-as-a-judge는 rubric과 prompt에 민감하므로, 여기서는 주 평가자보다 click-label의 false negative를 진단하는 보조 라벨러로 제한해 사용했다 <a class="citation-ref" href="#ref-llm-judge" aria-label="Reference 6">[6]</a> <a class="citation-ref" href="#ref-geval" aria-label="Reference 7">[7]</a>. judge call은 structured output으로 JSON label array만 반환하도록 제한했다. self-consistency를 위해 temperature가 다른 3회 호출의 majority vote를 사용했고, tie는 false-negative를 줄이는 방향으로 높은 relevance를 선택했다.

초기 후보-라벨 쌍 `4,585`건 기준으로 3/3 일치 비율은 `94.9%`였다. label별 3/3 일치 비율은 strongly relevant `98.1%`, unrelated `94.5%`, partially relevant `91.0%`였다. 이후 Matryoshka dim 검증까지 누적된 judge 판정 쌍은 `7,130`건이다. 이 값은 사람 평가와의 agreement가 아니라 judge 내부 안정성이다. 따라서 LLM-judged metric은 click-label 절대 점수의 하한 편향을 설명하는 보조 증거로만 해석한다.

LLM 호출이 실패한 경우에는 보수적으로 원본 click-label만 남겼다. 따라서 LLM-judged metric은 모든 관련 상품을 완전히 찾은 값이 아니라, 고정된 상위 30개 후보군 안에서 false negative를 일부 보정한 추정치다.

### Matryoshka 차원 평가

Matryoshka 모델은 전체 768차원 embedding을 만든 뒤 앞쪽 prefix만 잘라 사용할 수 있다. 사용할 차원이 $d$일 때의 벡터는 다음처럼 정의한다.

$$
z_d = \mathrm{normalize}(z_{1:d})
$$

본문에서는 `768`, `512`, `256`, `128` 차원을 비교했다. dim 256은 저장 공간과 검색 index 비용을 768 대비 약 1/3로 줄일 수 있는 저차원 후보로 두었다. 단, 이 보고서는 index latency 실측까지 포함하지 않고, retrieval quality 보존 여부만 다룬다.

## 실험 설계

모든 주요 비교는 동일한 v1 데이터셋, same-language retrieval corpus, click-label test contract를 기준으로 해석한다. 이 보고서의 주요 수치는 단일 run 계보에서 나온 결과이므로, 표에서 `측정 노이즈 수준`이라고 부르는 작은 차이는 통계적 유의성 판정이 아니라 실질 차이로 해석하지 않겠다는 보수적 표기다. 실험 계보는 크게 네 단계다.

1. multilingual-e5-base fine-tuning을 기준선으로 둔다 <a class="citation-ref" href="#ref-e5" aria-label="Reference 2">[2]</a>.
2. base model을 EmbeddingGemma-300M으로 바꿔 capacity와 multilingual embedding prior의 효과를 확인한다 <a class="citation-ref" href="#ref-embeddinggemma" aria-label="Reference 1">[1]</a>.
3. title prompt, longer training, CachedMultipleNegativesRankingLoss, larger batch를 묶어 contrastive 학습 신호를 강화한다. 구현은 Sentence-Transformers의 retrieval training 구성과 Matryoshka loss wrapper를 사용했다 <a class="citation-ref" href="#ref-sbert" aria-label="Reference 4">[4]</a> <a class="citation-ref" href="#ref-sentence-transformers" aria-label="Reference 5">[5]</a>.
4. 같은 데이터와 레시피 위에서 MatryoshkaLoss를 감싸 저차원 prefix 품질을 보존한다.

대표 학습 설정은 다음과 같다.

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

비교 실험에는 개선 신호가 남은 lever만 넣지 않았다. document augmentation ratio, source/variant weighted sampling, hard negative mining, brand-aware hard negative mining, query augmentation, gradient clipping, step 연장, uniform language sampling도 같은 평가 기준으로 확인했다. 이 추가 비교군은 결론에서 중요하다. 같은 데이터 분포 안에서 더 복잡한 데이터 조정이 반복적으로 개선을 만들지 못했기 때문이다.

## 결과

### 전체 성능과 누적 개선

학습 전 EmbeddingGemma-300M의 click-label test MAP@10은 `0.6558`이었다. 대표 Matryoshka 설정은 `0.8146`이었다. 모든 언어에서 개선이 확인됐고, JP의 상대 개선이 가장 컸다.

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
  <figcaption><strong>Table 3.</strong> 학습 전 EmbeddingGemma-300M과 대표 Matryoshka 모델의 click-label test 비교다. 전체 test는 KO/EN/JP를 포함하며, 같은 prompt와 same-language retrieval corpus를 사용했다.</figcaption>
</figure>

모델 계보를 보면 개선 폭은 초반에 크고 뒤로 갈수록 작아졌다. multilingual-e5-base 기준선의 최고치는 `0.7732`였고, EmbeddingGemma-300M으로 바꾸면 `0.7953`이 됐다. 이후 title prompt, step 수, CachedMNRL, batch size를 묶은 레시피 개선으로 `0.8151`까지 올라갔다. 이 bundle 안에서 별도로 비교된 batch/loss 변경은 `0.8082 -> 0.8151`의 `+0.0069` 신호로 남았지만, 반복 seed가 없으므로 독립적인 causal attribution보다 effective in-batch negative 확대와 일관된 관찰로 본다. Matryoshka fine-tuning은 dim 768 기준 `0.8146`으로 거의 같은 수준을 유지했다.

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
  <figcaption><strong>Table 4.</strong> 모델 계보별 누적 개선이다. MRL 단계는 dim 768 점수 개선보다 저차원 prefix 품질을 보존하는 단계로 해석한다.</figcaption>
</figure>

### Lever별 해석

가장 안정적으로 남은 개선은 두 축이었다. 첫째는 base model 교체다. e5-base에서 EmbeddingGemma-300M으로 바꾸면 KO/EN/JP 모두 개선됐다. 둘째는 recipe bundle 안에서 확인된 batch/loss 변경 신호다. CachedMultipleNegativesRankingLoss와 batch 192 조합은 batch 48 MNRL 대비 `+0.0069`를 만들었고, 이는 effective in-batch negatives 확대와 일관된다.

반면 데이터 조정 계열에서는 안정적인 신호가 거의 남지 않았다. query augmentation은 brand/category lexical overlap이 큰 query를 늘렸지만, 이미 해당 query군에서는 추가 개선 여지가 작았다. hard negative mining은 학습 신호를 더 어렵게 만들었지만, 같은 click-label test에서는 회귀했다. step을 6,000에서 12,000으로 늘려도 overall MAP@10 변화는 `+0.0008`에 그쳤고, JP MAP@10은 낮아졌다.

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
  <figcaption><strong>Table 5.</strong> 주요 lever의 역할 기반 요약이다. delta는 각 실험의 직접 비교 기준 대비 값이며, 동일한 test contract에서 해석한다.</figcaption>
</figure>

이 결과는 추가 개선 신호가 약했던 비교군도 해석상 중요하다는 점을 보여준다. 현재 데이터 분포에서는 lexical overlap이 강한 query/document pair가 많았고, 그런 영역은 이미 상위 retrieval이 강했다. 추가 개선은 같은 pair를 더 세게 학습하는 것보다, 의미 의도 query나 카탈로그 전체 후보군처럼 평가 난이도를 바꾸는 쪽에서 나올 가능성이 크다.

### Click-label과 LLM-judged 평가의 차이

click-label test에서 대표 MRL 설정의 KO MAP@10은 `0.8034`였다. 같은 모델을 KO 100개 stratified query의 상위 30개 후보군에 대한 LLM-judged metric으로 보면 MAP@10은 `0.9525`, Hit@1은 `1.0000`이었다. 이 차이는 모델 자체의 품질 차이만을 의미하지 않는다. broad query에서 click-label이 관련 상품을 충분히 positive로 보지 못하는 문제가 함께 반영된 결과로 해석한다.

중요한 점은 개선 방향이다. 학습 전후 개선 폭은 click-label과 LLM-judged에서 모두 컸다. click-label 전체 MAP@10은 `0.6558 -> 0.8146`, LLM-judged MAP@10은 `0.7739 -> 0.9525`였다. 따라서 click-label은 절대값을 낮게 보일 수 있지만, 효과 크기가 큰 비교에서는 같은 방향의 상대 개선 신호로 쓸 수 있었다. 다만 이 결과만으로 작은 delta의 모델 순위까지 click-label이 안정적으로 판정한다고 보지는 않는다.

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
  <figcaption><strong>Table 6.</strong> click-label과 LLM-judged 평가의 역할 차이다. click-label은 전체 실험 비교의 기본 지표이고, LLM-judged metric은 sparse positive 때문에 낮아진 절대 점수를 보정해 해석하는 보조 지표다.</figcaption>
</figure>

LLM-judged 평가에서 Recall@10은 주의해서 읽어야 한다. expanded positives를 쓰면 positive 분모가 원본 click-label보다 크게 늘어난다. top-10 안의 관련 상품 수가 늘어도 분모가 더 빠르게 커지면 Recall@10 비율은 낮아질 수 있다. 그래서 LLM-judged 환경에서는 binary relevance 기준 MAP@10, top-1 만족 여부를 보는 Hit@1, relevance grade를 반영하는 NDCG@10을 주요 해석 지표로 두었다.

### Matryoshka 차원 절충

Matryoshka fine-tuning의 가치는 dim 768 점수에서 거의 보이지 않는다. non-MRL 모델과 MRL 모델은 click-label dim 768에서 거의 같은 수준이다. 차이는 저차원 slice에서 나타난다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/noisy-click-mrl-retrieval/mrl-dim-tradeoff.svg" alt="MRL fine-tuned 모델과 non-MRL fine-tuned 모델의 768, 512, 256, 128 차원 LLM-judged MAP@10을 비교한 선 그래프">
  <figcaption><strong>Figure 2.</strong> Matryoshka 차원별 LLM-judged MAP@10이다. non-MRL 모델은 dim 256과 dim 128에서 품질 손실이 커졌지만, MRL fine-tuning은 dim 256을 dim 768과 거의 같은 수준으로 유지했다.</figcaption>
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
  <figcaption><strong>Table 7.</strong> Matryoshka 차원별 품질이다. top-1 변경은 dim 768 결과와 같은 query에서 1위 상품이 바뀐 횟수다. dim 256은 top-1 상품이 자주 바뀌지만 relevance 기준 MAP@10과 Hit@1은 거의 유지됐다.</figcaption>
</figure>

현재 same-language corpus와 KO 100개 LLM-judged audit의 retrieval quality 기준으로는 dim 256이 가장 유력한 저차원 후보였다. LLM-judged MAP@10은 `0.9506`으로 dim 768의 `0.9525`와 0.002 이내였고, Hit@1은 둘 다 `1.0000`이었다. 128차원도 쓸 수는 있지만 MAP@10 drop이 `0.0193`으로 커지고 Hit@1도 `0.9900`으로 낮아졌다. 따라서 이 보고서의 결론은 "더 낮은 차원이 항상 충분하다"가 아니라, **MRL을 거친 dim 256은 현재 평가 조건에서 저차원 색인 후보로 볼 만하다**에 가깝다. 실제 선택에는 전체 카탈로그 평가, index latency, vector DB 설정 실측이 별도로 필요하다.

## 결론 및 해석

본 실험에서 가장 안정적으로 남은 관찰은 학습 개선의 출처가 분리됐다는 점이다. base model capacity는 다국어 상품 검색 retrieval 품질을 올리는 방향의 신호로 남았고, batch/loss 변경은 effective in-batch negative 규모 확대와 일관된 추가 개선을 보였다. 같은 데이터 분포 안에서 query augmentation, hard negative mining, weighted resampling, 단순 step 연장은 안정적인 추가 개선을 만들지 못했다. 이는 현재 데이터의 주요 신호가 lexical overlap과 클릭 로그 기반 pair에 이미 많이 담겨 있었음을 시사한다.

두 번째 결론은 평가 병목이다. click-label metric은 학습 전후처럼 효과가 큰 비교에서는 유용했지만, broad query의 절대 점수를 낮게 보았다. LLM-judged audit은 이 차이를 설명하는 보조 장치였다. 학습 전후 개선 폭이 click-label과 LLM-judged 모두에서 크게 나타났기 때문에, click-label을 버릴 필요는 없었다. 대신 작은 delta의 모델 순위와 절대 점수 해석에는 expanded relevance 기준의 보조 점수와 불확실성 점검을 함께 제시해야 했다.

세 번째 결론은 Matryoshka fine-tuning의 색인 차원 관점 의미다. MRL은 dim 768 ranking을 크게 올리는 기술이 아니었다. 그러나 fine-tuning 과정에서 약화될 수 있는 저차원 prefix 품질을 회복했고, 관찰된 평가 조건에서는 dim 256을 dim 768과 거의 같은 relevance 품질로 유지했다. 이 결과는 retrieval quality와 vector index 비용을 함께 보는 환경에서 의미가 있지만, 운영 선택으로 확정하려면 full-catalog retrieval과 latency 실측이 필요하다.

따라서 다음 연구 질문은 "같은 데이터로 어떤 학습 설정을 더 붙일 것인가"보다 "평가와 데이터 분포를 어떻게 바꿀 것인가"에 가깝다. 후보는 세 가지다. 첫째, 실제 카탈로그 전체 후보군에서 retrieval이 같은 패턴을 보이는지 확인한다. 둘째, LLM-judged metric과 사람 relevance 평가의 agreement를 측정한다. 셋째, lexical overlap이 약한 semantic intent query를 별도 데이터 분포로 구성한다.

## 한계

- LLM-judged 평가는 고정된 KO 100개 stratified query에 대한 보조 평가다. self-consistency는 높았지만, 사람 평가자와의 agreement는 아직 직접 측정하지 않았다.
- click-label test와 LLM-judged test의 query 범위가 다르다. click-label test는 전체 KO/EN/JP test이고, LLM-judged 평가는 KO stratified subset이다.
- retrieval corpus는 학습 데이터에서 구성한 same-language corpus다. 전체 카탈로그, 품절/신상품, dynamic ranking feature, 가격 필터, personalization은 포함하지 않았다.
- dim 256의 index 저장 비용 감소는 차원 수 기준의 계산이다. 실제 latency, memory bandwidth, vector DB 설정, quantization, batch serving 성능은 별도 실측이 필요하다.
- hard negative와 augmentation에서 추가 이득이 확인되지 않은 것은 현재 정책과 데이터 분포에 대한 결과다. semantic intent query처럼 분포를 바꾼 데이터에서는 다른 결과가 나올 수 있다.
- 본문은 특정 카탈로그의 공개 벤치마크를 제안하지 않는다. 개별 상품명과 서비스 식별자를 제거했기 때문에, 재현성은 방법과 평가 contract 수준에 한정된다.

## Appendix: 실험 표기와 보조 결과

본문에서는 내부 run name 대신 역할 기반 이름을 사용했다. Appendix에는 전체 실험을 해석하는 데 필요한 최소 보조 집계만 남긴다.

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
  <figcaption><strong>Appendix Table 1.</strong> 공개 가능한 dataset contract 요약이다. 개별 상품명과 식별자는 제거했지만, split, query source, language exposure, document variant 정책은 평가 재현에 필요한 수준으로 남겼다.</figcaption>
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
  <figcaption><strong>Appendix Table 4.</strong> KO LLM-judged 100 query의 길이 bucket별 MAP@10이다. 짧은 query에서 MRL 모델의 보조 평가 점수가 가장 크게 올라갔지만, 표본 수가 작으므로 bucket-level 결론은 후속 검증 대상으로 둔다.</figcaption>
</figure>

## References

<div class="reference-list" markdown="1">

1. <span id="ref-embeddinggemma"></span>Google. [EmbeddingGemma 300M model card](https://huggingface.co/google/embeddinggemma-300m). 2025.
2. <span id="ref-e5"></span>Liang Wang et al. [Text Embeddings by Weakly-Supervised Contrastive Pre-training](https://arxiv.org/abs/2212.03533). 2022.
3. <span id="ref-mrl"></span>Aditya Kusupati et al. [Matryoshka Representation Learning](https://arxiv.org/abs/2205.13147). NeurIPS 2022.
4. <span id="ref-sbert"></span>Nils Reimers and Iryna Gurevych. [Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks](https://aclanthology.org/D19-1410/). EMNLP-IJCNLP 2019.
5. <span id="ref-sentence-transformers"></span>UKPLab. [Sentence-Transformers documentation: training losses and Matryoshka embeddings](https://www.sbert.net/). 
6. <span id="ref-llm-judge"></span>Lianmin Zheng et al. [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://proceedings.neurips.cc/paper_files/paper/2023/hash/91f18a1287b398d378ef22505bf41832-Abstract-Datasets_and_Benchmarks.html). NeurIPS 2023.
7. <span id="ref-geval"></span>Yang Liu et al. [G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment](https://aclanthology.org/2023.emnlp-main.153/). EMNLP 2023.

</div>

## Citation

Text citation:

```text
Ahn, I. (2026). 희소 클릭 라벨에서 다국어 상품 검색 임베딩 평가와 Matryoshka 압축. Technical report.
```

BibTeX:

```bibtex
@techreport{ahn2026noisyclickmrlretrieval,
  title = {희소 클릭 라벨에서 다국어 상품 검색 임베딩 평가와 Matryoshka 압축},
  author = {Ahn, Ilho},
  year = {2026},
  institution = {Independent},
  type = {Technical report}
}
```
