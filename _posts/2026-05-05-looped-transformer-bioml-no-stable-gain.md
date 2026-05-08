---
title: "Looped Transformer는 BioML에서 안정적 이득을 남기지 못했다"
date: 2026-05-05 08:27:16 +0900
last_modified_at: 2026-05-07 15:48:21 +0900
categories: ["BIOML"]
tags: [bioml, looped-transformer, esm2, remote-homology, protein-language-model, model-architecture, negative-result]
lab_path: "experiment-lab/projects/protein-lt-boundary-conditions"
excerpt: "Looped Transformer를 여러 BioML 문제에 적용했지만 안정적 구조 이득으로 남지 않은 경계 결과를 정리한다."
description: "RNA, mutation scoring, remote homology, DeepLoc, PINDER contact 등 BioML 평가 문제에서 Looped Transformer를 시험했지만 안정적 이득이 남지 않았고, 그 실패가 어떤 조건에서 반복되는지 정리한 실험 노트."
permalink: /research/2026/05/05/looped-transformer-bioml-no-stable-gain/
image: /assets/images/posts/looped-transformer-bioml-task-fit/social-thumbnail.png
image_alt: "반복 loop, local signal, static representation, fold-like sequence trace를 함께 보여주는 Looped Transformer BioML 경계 결과 대표 이미지"
hero_image: /assets/images/posts/looped-transformer-bioml-task-fit/hero-task-fit.svg
hero_alt: "Looped Transformer의 반복 pass가 local signal과 static representation 병목 앞에서 안정적 이득으로 이어지지 못하는 추상 도식"
hero_caption: "<strong>Figure 1.</strong> 이 글의 핵심 해석을 추상화한 그림이다. Looped Transformer의 반복 pass가 여러 BioML 평가 문제에서 안정적 이득으로 분리되지 않은 상황을 나타낸다."
hero_frame: true
hero_compact: true
---

Looped Transformer는 같은 Transformer block 또는 소수 block을 여러 번 반복 적용해 effective depth를 늘리는 구조다. 직관적으로는 반복 pass가 전역 표현을 조금씩 정제하고, 적은 파라미터로 static depth 일부를 대체할 수 있을 것처럼 보인다. BioML에는 long-range sequence relation, fold-level label, protein interface처럼 이런 반복 갱신이 맞아 보이는 문제가 많다.

이 글은 그 가설을 여러 BioML 평가 문제에 적용해 본 결과를 정리한다. 결론은 성공 사례보다 경계 결과에 가깝다. **LT는 이번 BioML 평가 설정에서 안정적 이득을 남기지 못했다.** Remote homology와 DeepLoc에서 약한 평균 양성 신호는 있었지만, 반복 실행별 확인, Static ensemble, longer Static, 35M scale 확인, interface-contact 확인을 지나면서 전반적 구조 이득 주장 범위를 지지하지 못했다.

더 좁고 실용적인 결론은 이것이다. **이번 실험에서 LT가 실패한 지점들은 무작위가 아니라, 몇 가지 조건으로 반복됐다.** label이 local/compositional 신호로 설명되거나, pretrained Static 표현이 이미 전역 정보를 담고 있거나, tied recurrence가 새 생물학적 변수를 만들지 못하는 경우에는 LT의 반복 pass가 안정적 이득으로 남지 않았다.

> **Looped Transformer / LT**: 이 글에서는 같은 trainable block을 여러 pass에 반복 적용하는 recurrent-depth Transformer 계열을 뜻한다.
>
> **안정적 이득**: 평균 delta가 반복 실행별 방향성, 강화된 Static 비교, scale 변화에서도 같은 주장 범위로 유지되는 경우를 뜻한다.

{% include model-mention-cards.html label="사용한 주요 리소스" aria_label="Looped Transformer와 BioML 평가 관련 주요 리소스" models="Looped Transformers as Programmable Computers|arXiv:2301.13196|https://arxiv.org/abs/2301.13196;Reasoning with Latent Thoughts|arXiv:2502.17416|https://arxiv.org/abs/2502.17416;ESM2-8M|facebook/esm2_t6_8M_UR50D|https://huggingface.co/facebook/esm2_t6_8M_UR50D;TAPE remote homology|arXiv:1906.08230|https://arxiv.org/abs/1906.08230" %}

## 요약

- LT를 RNA regulation, mutation scoring, fold-level classification, subcellular localization, solubility, PPI/contact 같은 BioML 평가 축에 적용했지만, 전반의 안정적 개선법으로 남지는 않았다.
- Remote homology는 가장 오래 유지된 후보였다. 5회 반복 실행에서 LT는 Static보다 `+0.01405` accuracy, `+0.00842` macro-F1 높았지만 실행별 accuracy 우세는 `3/5`였고, 강화된 Static 비교에서 구조 이득으로 남지 않았다.
- 강화된 Static 기준선은 더 강했다. Static ensemble은 LT와 동률권이거나 약간 높았고, longer Static은 `0.52592` accuracy / `0.21621` macro-F1로 LT보다 크게 높았다. 35M scale 확인에서도 LT의 accuracy 우위는 사라졌다.
- DeepLoc은 약한 두 번째 global-task 후보로 남았다. 하지만 Solubility는 불안정했고, PPI/contact/PINDER interface-contact 확인은 현재 평가 설정에서 음성 경계로 남았다.
- 실패는 다섯 가지 조건으로 일반화된다. local/compositional 신호가 강한 문제, pretrained Static 표현이 이미 충분한 문제, tied recurrence가 static depth를 대체하지 못하는 문제, 약한 이득이 pass aggregation/warmup에 의존하는 문제, 관계 갱신이 필요해 보여도 supervision이 그 병목을 직접 압박하지 않는 문제에서는 LT가 안정적으로 남지 않았다.

## 문제 설정

LT를 BioML에 적용한 이유는 단순했다. 생물학 sequence 문제 중 일부는 local motif나 composition만으로 풀리지 않고, sequence 전체의 관계를 여러 번 갱신해야 좋아질 것처럼 보인다. Remote homology는 fold-level label을 예측하고, protein interface/contact는 두 chain 사이의 residue 관계를 봐야 한다. 이런 문제에서는 반복적인 global representation refinement가 도움이 될 수 있다고 봤다.

하지만 BioML이라는 이름 자체는 좋은 task prior가 아니었다. RNA MRL, mutation scoring, solubility, localization, fold classification, interface contact는 모두 BioML로 묶이지만 label을 결정하는 신호 구조는 다르다. 어떤 task는 k-mer나 local window가 강하고, 어떤 task는 pretrained static layer가 이미 충분한 정보를 담고 있다. 이 경우 LT의 recurrence는 실제 병목을 건드리지 못한다.

## 평가 축

실험은 LT가 맞아 보이는 문제를 여러 평가 축으로 나눠 확인하고, 각 축에서 실패가 어떤 형태로 나타나는지 비교하는 방식으로 진행됐다. Table 1은 각 축이 왜 후보였고, 어떤 실패 조건이 남았는지를 요약한다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <colgroup>
        <col style="width: 20%;">
        <col style="width: 27%;">
        <col style="width: 31%;">
        <col style="width: 22%;">
      </colgroup>
      <thead>
        <tr>
          <th>문제 축</th>
          <th>LT를 기대한 이유</th>
          <th>관찰</th>
          <th>현재 해석</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>RNA MRL / BEACON</td>
          <td>짧은 sequence에서 regulation signal을 재사용 depth로 잡을 수 있는지 확인</td>
          <td>MRL에서는 k-mer ridge Spearman <code>0.77079</code>, LT <code>0.47935</code>.<br><span class="table-note-inline">BEACON도 LT에 맞는 깨끗한 task 조건을 찾지 못했다.</span></td>
          <td>local/k-mer 기준선에서 탈락</td>
        </tr>
        <tr>
          <td>Mutation scoring</td>
          <td>protein representation을 반복 갱신하면 variant effect ranking이 좋아질지 확인</td>
          <td>local-window Static <code>0.43957</code>, best LT <code>0.32921</code>.</td>
          <td>global recurrence보다 local readout / position signal이 중요</td>
        </tr>
        <tr>
          <td>Remote homology</td>
          <td>fold-level label은 global sequence representation을 요구할 가능성이 있음</td>
          <td>5회 반복 실행에서 LT delta <code>+0.01405</code> Acc / <code>+0.00842</code> F1.<br><span class="table-note-inline">실행별 accuracy 우세는 <code>3/5</code>였다.</span></td>
          <td>가장 강한 후보지만 안정적 확인은 아님</td>
        </tr>
        <tr>
          <td>DeepLoc / Solubility</td>
          <td>sequence-level classification으로 remote homology 신호가 전이되는지 확인</td>
          <td>DeepLoc은 LT delta <code>+0.01250</code> Acc / <code>+0.03299</code> F1. Solubility는 더 약하고 불안정.</td>
          <td>DeepLoc은 약한 두 번째 global-task 후보</td>
        </tr>
        <tr>
          <td>PPI / contact / PINDER</td>
          <td>cross-chain interface와 residue contact는 반복적인 관계 갱신이 맞아 보임</td>
          <td>PINDER interface-contact 반복 확인에서 test AUPRC delta는 <code>-0.01892</code>, <code>-0.02402</code>, <code>-0.01081</code>.</td>
          <td>현재 interface-contact 평가 설정에서는 음성 경계</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> LT를 적용한 BioML 문제 축과 현재 해석이다. 대부분의 결과는 “어떤 task에서 성공했는가”보다 “어떤 조건에서 recurrence가 실제 병목을 건드리지 못했는가”를 보여준다.</figcaption>
</figure>

## 약한 양성 신호가 사라지는 방식

Remote homology와 DeepLoc은 완전히 음성이라고만 말하기 어렵다. 둘 다 평균 delta는 남았다. 문제는 그 평균 delta가 안정적 이득으로 승격되지 않았다는 점이다.

Remote homology 8M의 5회 반복 실행에서는 LT가 Static보다 평균 accuracy와 macro-F1이 높았다. 그러나 실행별 accuracy 우세는 `3/5`였다. 반복 실행 대부분에서 같은 방향이 유지되는 결과를 안정적 확인으로 본다면, 이 결과는 "재현된 평균 양성 신호"이지 "안정적 확인"은 아니다.

더 강한 Static 기준선에서는 주장 범위가 더 좁아졌다. Static 3회 반복 ensemble은 LT 단일 모델보다 약간 높았고, longer Static은 LT를 크게 앞섰다. 35M scale 확인에서는 LT의 accuracy 우위도 사라졌다. 이 패턴은 remote homology가 "LT 성공 사례"라기보다 "가장 오래 유지된 예외 후보"라는 해석을 지지한다. Table 2는 이 축에서 평균 양성 신호가 좁아지는 과정을 정리한다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <colgroup>
        <col style="width: 25%;">
        <col style="width: 31%;">
        <col style="width: 24%;">
        <col style="width: 20%;">
      </colgroup>
      <thead>
        <tr>
          <th>비교 조건</th>
          <th>관찰</th>
          <th>구조 이득으로 남는가</th>
          <th>해석</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Remote homology 5회 반복 실행</td>
          <td>LT <code>0.44460</code> Acc / <code>0.12609</code> F1, Static <code>0.43054</code> / <code>0.11768</code></td>
          <td>평균 신호만 남음</td>
          <td>부분 지지</td>
        </tr>
        <tr>
          <td>실행별 방향성</td>
          <td>Accuracy 우세 <code>3/5</code></td>
          <td>불충분</td>
          <td>안정적 확인 아님</td>
        </tr>
        <tr>
          <td>Static ensemble</td>
          <td>LT 단일 모델 <code>0.44149</code> / <code>0.12411</code>, Static ensemble <code>0.44285</code> / <code>0.12485</code></td>
          <td>아님</td>
          <td>단일 모델 우위가 강화된 기준선에서 약해짐</td>
        </tr>
        <tr>
          <td>Longer Static</td>
          <td>Longer Static <code>0.52592</code> / <code>0.21621</code></td>
          <td>아님</td>
          <td>실용적 학습 예산 주장 불가</td>
        </tr>
        <tr>
          <td>35M scale 확인</td>
          <td>LT <code>0.58817</code> Acc, Static <code>0.58984</code> Acc</td>
          <td>아님</td>
          <td>scale-robust accuracy 주장 불가</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> Remote homology에서 약한 평균 양성 신호가 강화된 Static 비교를 지나며 좁아지는 과정이다. 이 결과는 LT가 fold-level task에서 완전히 무의미했다는 뜻이 아니라, 평균 신호가 구조 이득으로 분리되지 않았다는 뜻이다.</figcaption>
</figure>

DeepLoc은 최신 경계 조건 확인에서 양의 평균 신호가 남았다. 5회 반복 실행에서 LT는 Static보다 `+0.01250` accuracy, `+0.03299` macro-F1 높았고, accuracy 우세는 `4/5`였다. 하지만 longer Static 관련 주의점은 여전히 남고, Solubility는 다른 확인에서 약해졌다. 따라서 DeepLoc은 remote homology 다음의 후보일 수는 있어도, BioML 전반의 안정적 이득을 만들지는 못한다.

## 병목 해석

실패의 공통점은 LT가 "생물학 데이터"라는 이름에 반응한 것이 아니라는 점이다. LT가 필요하려면 반복 pass가 실제 병목을 줄여야 한다. 그런데 많은 BioML task에서는 다른 신호가 먼저 문제를 설명했다.

RNA MRL과 BEACON 계열에서는 k-mer, local window, composition이 강했다. Mutation scoring에서는 mutation position과 local readout이 더 큰 영향을 줬다. PPI/contact에서도 기존 pooled pairwise 평가와 PINDER interface-contact 확인은 LT보다 Static이 강하거나 비슷했다. 이런 경우 recurrence는 새 정보를 만드는 것이 아니라 이미 만들어진 static representation을 다시 변환하는 데 머물 수 있다.

PPI/contact는 이름만 보면 반복적인 관계 갱신과 잘 맞아 보인다. 하지만 현재 평가에서는 label과 readout이 실제 cross-chain iterative refinement를 충분히 요구하지 않았을 가능성이 있다. 즉 "관계형 문제"라는 이름만으로 LT의 recurrent update가 직접적인 병목 해결로 이어지지는 않았다.

또 하나의 문제는 static depth다. static Transformer의 여러 layer는 서로 다른 파라미터를 갖고, pretrained backbone에서는 layer마다 다른 정보를 담을 수 있다. 반면 LT는 같은 block을 반복한다. 따라서 `1-layer loop r=3`이 `static 3-layer`를 자동으로 대체한다는 기대는 너무 강했다. 실제 depth 비교에서도 `static_3l` NLL `2.88969`, `lt_1l_r3` NLL `2.89345`로 LT가 static 3-layer를 넘지 못했다.

**보조 설정 의존성도 별도 병목이었다.** Remote homology에서 가장 나은 LT 설정은 pass aggregation과 recurrent MLM warmup을 포함했다. 이것은 LT가 마지막 pass 하나로 바로 좋은 representation을 만드는 것이 아니라, 여러 pass trajectory에 정보가 분산될 수 있음을 시사한다.

하지만 이 관찰은 동시에 공정성 문제를 만든다. LT가 pass aggregation과 recurrent warmup을 받아야 약한 양성 신호를 만든다면, Static도 layer aggregation, learned layer mixing, static warmup, longer training을 받아야 한다. 이 대조군을 주면 LT 고유의 구조 이득은 더 좁아진다.

따라서 pass aggregation과 warmup은 "가장 나은 LT 설정"이라기보다 "LT 주장을 공정하게 비교하려면 Static 대조군도 같이 키워야 한다"는 신호로 읽어야 한다.

## 일반화 가능한 실패 조건

이 실험에서 얻은 것은 개별 수치의 승패보다 실패 조건에 가깝다. 서로 다른 BioML 문제에서 관찰된 음성 결과는 아래 다섯 가지 조건으로 묶인다. 이 조건들은 LT가 원천적으로 불가능하다는 일반화가 아니라, **어떤 종류의 BioML 문제에서 LT의 recurrence가 구조적 이득으로 남기 어려운지**에 대한 제한적 일반화다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <colgroup>
        <col style="width: 30%;">
        <col style="width: 39%;">
        <col style="width: 31%;">
      </colgroup>
      <thead>
        <tr>
          <th>실패 조건</th>
          <th>이번 결과에서 보인 형태</th>
          <th>LT와 어긋난 이유</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Local 또는 compositional 신호가 label을 충분히 설명한다.</td>
          <td>RNA MRL에서는 k-mer ridge가 LT보다 크게 높았고, mutation scoring에서는 local-window Static이 best LT보다 강했다.</td>
          <td>반복적인 전역 표현 갱신이 주 병목이 아니면 recurrence는 새 정보를 만들지 못하고 이미 충분한 local signal 위에 추가 변환만 더한다.</td>
        </tr>
        <tr>
          <td>Pretrained Static 표현이 이미 전역 정보를 담고 있다.</td>
          <td>Remote homology와 DeepLoc에서는 평균 양성 신호가 있었지만 Static ensemble, longer Static, scale 확인에서 구조 이득으로 분리되지 않았다.</td>
          <td>LT가 기대한 전역 refinement가 pretrained layer에 이미 상당 부분 들어 있으면, 같은 block 반복은 새로운 inductive bias보다 재가공에 가까워진다.</td>
        </tr>
        <tr>
          <td>Tied recurrence가 static depth를 대체하지 못한다.</td>
          <td>Depth 비교에서 <code>lt_1l_r3</code>은 <code>static_3l</code>을 넘지 못했다.</td>
          <td>Static depth는 서로 다른 파라미터와 layer별 표현을 갖지만, LT는 같은 block을 반복한다. 반복 횟수는 깊이처럼 보이지만 표현 다양성까지 보장하지 않는다.</td>
        </tr>
        <tr>
          <td>약한 이득이 recurrence 자체보다 보조 설정에 의존한다.</td>
          <td>Remote homology에서 가장 나은 LT 설정은 pass aggregation과 recurrent MLM warmup을 포함했다.</td>
          <td>이득이 aggregation과 warmup을 통해 생기면, 같은 보조 조건을 Static에도 주어야 한다. 그러면 LT 고유의 구조 이득은 더 좁아진다.</td>
        </tr>
        <tr>
          <td>관계 갱신이 필요해 보여도 supervision이 그 병목을 직접 압박하지 않는다.</td>
          <td>PPI/contact/PINDER에서는 interface/contact가 recurrence와 맞아 보였지만 현재 평가 설정에서는 Static을 넘지 못했다.</td>
          <td>문제 이름이 관계 추론처럼 보여도, 학습 신호와 readout이 실제 cross-chain refinement를 요구하지 않으면 반복 pass의 장점이 드러나기 어렵다.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> 이번 실험에서 일반화할 수 있는 실패 조건이다. 조건들은 BioML 전체에 대한 부정 명제가 아니라, LT의 recurrence가 구조 이득으로 남기 어려운 문제 구조를 요약한다.</figcaption>
</figure>

## 현재 결론

이번 평가 설정에서는 LT의 안정적 이득이 남지 않았다. Remote homology와 DeepLoc은 약한 평균 양성 후보였지만, 강한 Static 비교를 더하면 구조 이득으로 분리되지 않았다. RNA/k-mer, mutation scoring, PPI/contact/PINDER interface-contact는 현재 평가 설정에서 음성 경계로 남았다.

따라서 현재 단계의 결론은 다음처럼 둔다.

> LT는 BioML이라는 도메인에 맞는 일반 개선법으로 확인되지 않았다. 이번 실험에서 일반화할 수 있는 것은 실패의 방향이다. label이 local/compositional 신호로 설명되거나, pretrained Static 표현이 이미 충분하거나, tied recurrence가 static depth의 표현 다양성을 대체하지 못하거나, 이득이 aggregation/warmup에 묶이는 조건에서는 LT의 반복 pass가 안정적 구조 이득으로 남기 어렵다.

## 한계

이 글은 현재 실험 설정과 평가 문제 묶음 안에서의 경계 결과다. LT 구조 전체를 부정하지 않고, BioML 전체에 대한 보편 명제를 만들지도 않는다. 특히 decoder continuation에서 보인 약한 양성 신호는 encoder-style BioML 평가 문제 선별과 분리해서 읽어야 한다.

또한 일부 선별 실험은 반복 횟수와 학습 예산이 균일하지 않다. Remote homology와 DeepLoc은 추가 확인 가치가 있었지만, 그 확인은 성공 선언보다 실패 조건을 더 선명하게 만들었다. PINDER/contact도 현재 표본화된 평가 설정에서의 실패이지, 모든 interface formulation의 실패는 아니다. 따라서 일반화 범위는 "LT가 BioML에서 안 된다"가 아니라, 위 조건에서 LT의 recurrence가 안정적 이득으로 분리되지 않았다는 수준에 둔다.

## Appendix: 세부 수치

<details>
  <summary>Remote homology, DeepLoc, Solubility 최신 경계 조건 확인</summary>
  <div class="details-content">
    <figure class="table-figure table-figure--metrics">
      <div class="table-shell">
        <table class="metrics-table metrics-table--numeric-columns">
          <thead>
            <tr>
              <th>평가 문제 / 확인</th>
              <th class="align-right">Static</th>
              <th class="align-right">LT</th>
              <th class="align-right">Delta</th>
              <th>해석</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Remote homology 8M<br><span class="table-note-inline">5회 반복 Acc</span></td>
              <td class="align-right"><code>0.43054</code></td>
              <td class="align-right"><code>0.44460</code></td>
              <td class="align-right"><code>+0.01405</code></td>
              <td>평균 양성, 실행별 우세 <code>3/5</code></td>
            </tr>
            <tr>
              <td>Remote homology 8M<br><span class="table-note-inline">5회 반복 macro-F1</span></td>
              <td class="align-right"><code>0.11768</code></td>
              <td class="align-right"><code>0.12609</code></td>
              <td class="align-right"><code>+0.00842</code></td>
              <td>평균 양성</td>
            </tr>
            <tr>
              <td>DeepLoc<br><span class="table-note-inline">5회 반복 Acc</span></td>
              <td class="align-right"><code>0.44922</code></td>
              <td class="align-right"><code>0.46172</code></td>
              <td class="align-right"><code>+0.01250</code></td>
              <td>약한 두 번째 후보, Acc 우세 <code>4/5</code></td>
            </tr>
            <tr>
              <td>DeepLoc<br><span class="table-note-inline">5회 반복 macro-F1</span></td>
              <td class="align-right"><code>0.33337</code></td>
              <td class="align-right"><code>0.36636</code></td>
              <td class="align-right"><code>+0.03299</code></td>
              <td>F1 우세 <code>3/5</code>, longer Static 관련 주의점 남음</td>
            </tr>
            <tr>
              <td>Solubility<br><span class="table-note-inline">5회 반복 Acc</span></td>
              <td class="align-right"><code>0.62539</code></td>
              <td class="align-right"><code>0.63320</code></td>
              <td class="align-right"><code>+0.00781</code></td>
              <td>불안정한 후속 관찰 신호</td>
            </tr>
          </tbody>
        </table>
      </div>
      <figcaption><strong>Appendix Table 1.</strong> Remote homology, DeepLoc, Solubility의 반복 실행별 metric 요약이다. 본문 Table 2가 해석 흐름을 보여준다면, 이 표는 평균 delta와 실행별 우세를 확인하기 위한 lookup table이다.</figcaption>
    </figure>
  </div>
</details>

<details>
  <summary>강화된 기준선과 scale 확인</summary>
  <div class="details-content">
    <figure class="table-figure table-figure--metrics">
      <div class="table-shell">
        <table class="metrics-table metrics-table--numeric-columns">
          <thead>
            <tr>
              <th>비교 조건</th>
              <th class="align-right">LT</th>
              <th class="align-right">Static / 비교군</th>
              <th class="align-right">LT delta</th>
              <th>해석</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Static 3회 반복<br><span class="table-note-inline">majority ensemble, Acc</span></td>
              <td class="align-right"><code>0.44149</code></td>
              <td class="align-right"><code>0.44285</code></td>
              <td class="align-right"><code>-0.00135</code></td>
              <td>단일 모델 우위가 ensemble에서 사라짐</td>
            </tr>
            <tr>
              <td>Static 3회 반복<br><span class="table-note-inline">majority ensemble, macro-F1</span></td>
              <td class="align-right"><code>0.12411</code></td>
              <td class="align-right"><code>0.12485</code></td>
              <td class="align-right"><code>-0.00074</code></td>
              <td>동률권 또는 Static 우세</td>
            </tr>
            <tr>
              <td>Longer Static<br><span class="table-note-inline">Acc</span></td>
              <td class="align-right"><code>0.44460</code></td>
              <td class="align-right"><code>0.52592</code></td>
              <td class="align-right"><code>-0.08132</code></td>
              <td>더 긴 학습 예산에서 Static 우세</td>
            </tr>
            <tr>
              <td>35M scale 확인<br><span class="table-note-inline">Acc</span></td>
              <td class="align-right"><code>0.58817</code></td>
              <td class="align-right"><code>0.58984</code></td>
              <td class="align-right"><code>-0.00167</code></td>
              <td>scale-robust accuracy 우위 없음</td>
            </tr>
          </tbody>
        </table>
      </div>
      <figcaption><strong>Appendix Table 2.</strong> Remote homology의 강화된 Static 비교 요약이다. 평균 양성 신호가 구조 이득으로 분리되는지 확인하기 위해 ensemble, 더 긴 학습, scale 조건을 따로 모았다.</figcaption>
    </figure>
  </div>
</details>

<details>
  <summary>음성 경계와 별도 약한 양성 축</summary>
  <div class="details-content">
    <figure class="table-figure table-figure--comparison">
      <div class="table-shell">
        <table class="comparison-table">
          <colgroup>
            <col style="width: 25%;">
            <col style="width: 44%;">
            <col style="width: 31%;">
          </colgroup>
          <thead>
            <tr>
              <th>축</th>
              <th>관찰</th>
              <th>이 글에서의 역할</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>RNA MRL</td>
              <td>k-mer ridge Spearman <code>0.77079</code>, LT <code>0.47935</code>.</td>
              <td>local/k-mer 기준선 경계</td>
            </tr>
            <tr>
              <td>Mutation scoring</td>
              <td>local-window Static <code>0.43957</code>, best LT <code>0.32921</code>.</td>
              <td>local readout / position signal 경계</td>
            </tr>
            <tr>
              <td>PPI pooled pair-MLP</td>
              <td>AUPRC Static <code>0.92363</code>, LT <code>0.91998</code>, delta <code>-0.00364</code>.</td>
              <td>pooled pairwise 평가에서 Static 우세</td>
            </tr>
            <tr>
              <td>PINDER interface-contact</td>
              <td>PINDER interface-contact 반복 확인의 test AUPRC delta <code>-0.01892</code>, <code>-0.02402</code>, <code>-0.01081</code>.</td>
              <td>interface/contact 경로도 현재 평가 설정에서는 실패</td>
            </tr>
            <tr>
              <td>Protein decoder continuation</td>
              <td>일부 continuation NLL에서는 LT가 같은 파라미터 수의 Static보다 약간 좋았지만, 비슷한 연산량의 Static보다 뒤였다.</td>
              <td>별도 decoder 축의 약한 양성 신호</td>
            </tr>
          </tbody>
        </table>
      </div>
      <figcaption><strong>Appendix Table 3.</strong> Table 1에서 압축한 음성 경계와 별도 약한 양성 축의 원 수치 근거다. 본문 해석을 반복하기보다, local/k-mer, mutation, interface/contact, decoder continuation 축의 보조 수치를 모은다.</figcaption>
    </figure>
  </div>
</details>

## References

<div class="reference-list" markdown="1">

<ol>
  <li id="ref-looped-computers">Giannou, A. et al. <strong>Looped Transformers as Programmable Computers</strong>. arXiv, 2023.<br>
    <a href="https://arxiv.org/abs/2301.13196">arXiv</a>
  </li>
  <li id="ref-latent-thoughts">Saunshi, N. et al. <strong>Reasoning with Latent Thoughts: On the Power of Looped Transformers</strong>. arXiv, 2025.<br>
    <a href="https://arxiv.org/abs/2502.17416">arXiv</a>
  </li>
  <li id="ref-esm2">Lin, Z. et al. <strong>Evolutionary-scale prediction of atomic-level protein structure with a language model</strong>. <em>Science</em>, 2023.<br>
    <a href="https://doi.org/10.1126/science.ade2574">Paper / DOI</a> · <a href="https://huggingface.co/facebook/esm2_t6_8M_UR50D">ESM2-8M model</a>
  </li>
  <li id="ref-tape">Rao, R. et al. <strong>Evaluating Protein Transfer Learning with TAPE</strong>. NeurIPS, 2019.<br>
    <a href="https://arxiv.org/abs/1906.08230">arXiv</a>
  </li>
  <li id="ref-scope">Chandonia, J.-M. et al. <strong>SCOPe: improvements to the structural classification of proteins - extended database to facilitate variant interpretation and machine learning</strong>. <em>Nucleic Acids Research</em>, 2022.<br>
    <a href="https://academic.oup.com/nar/article/50/D1/D553/6447236">Journal page</a>
  </li>
</ol>

</div>

## Citation

이 글을 인용할 때는 아래 형식을 사용할 수 있다.

```text
Ilho Ahn, "Looped Transformer는 BioML에서 안정적 이득을 남기지 못했다", Mini Research, May 5, 2026.
```

또는 BibTeX 형식으로는 다음처럼 적을 수 있다.

```bibtex
@article{ahn2026loopedtransformerbiomlnostablegain,
  author = {Ilho Ahn},
  title = {Looped Transformer는 BioML에서 안정적 이득을 남기지 못했다},
  journal = {Mini Research},
  year = {2026},
  month = may,
  url = {https://muted-color.github.io/research/2026/05/05/looped-transformer-bioml-no-stable-gain/}
}
```
