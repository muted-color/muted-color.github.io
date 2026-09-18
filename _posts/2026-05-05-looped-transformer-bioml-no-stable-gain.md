---
lang: ko
title: "BioML에서 검증한 Looped Transformer: 안정적 개선으로 이어지지 않은 반복 구조"
date: 2026-05-05 08:27:16 +0900
last_modified_at: 2026-09-06 00:00:00 +0900
categories: ["BIO ML"]
tags: [bioml, looped-transformer, esm2, remote-homology, protein-language-model, model-architecture, negative-result]
lab_path: "experiment-lab/projects/protein-lt-boundary-conditions"
published: false
publication_status: "unpublished"
excerpt: "Looped Transformer를 여러 BioML 평가 문제에 적용했지만 안정적 개선으로 분리되지 않은 경계 결과를 정리한다."
description: "RNA MRL, mutation scoring, remote homology, DeepLoc, PINDER contact 등 BioML 평가 문제에서 Looped Transformer를 시험하고, 어떤 조건에서 안정적 개선으로 분리되지 않았는지 정리한 연구 노트."
permalink: /research/2026/05/05/looped-transformer-bioml-no-stable-gain/
image: /assets/images/posts/looped-transformer-bioml-no-stable-gain/social-thumbnail.png
image_alt: "흰 배경 위에서 투명한 층상 흐름이 여러 평가 패널을 지나며 옅은 파란 신호로 흩어지는 Looped Transformer BioML 경계 결과 대표 이미지"
hero_image: /assets/images/posts/looped-transformer-bioml-no-stable-gain/hero.png
hero_alt: "투명한 층상 흐름이 여러 평가 패널을 통과하며 옅은 파란 신호로 분산되는 Looped Transformer BioML 경계 결과 추상 이미지"
hero_frame: true
hero_compact: true
---

같은 Transformer block을 반복 적용하면 생물학 서열의 예측 성능이 좋아지는가? 이 글은 Looped Transformer(LT)를 여러 BioML 과제에 적용하고 Static Transformer와 비교한 결과를 정리한다. 핵심은 **Remote homology에서 LT accuracy 0.44460이 기본 Static 0.43054보다 높았지만, 더 오래 학습한 Static은 0.52592였다는 점**이다. 약한 평균 개선은 있었으나, 이것만으로 반복 구조의 효과와 학습 예산의 효과를 분리할 수 없었다.

Giannou et al.의 *Looped Transformers as Programmable Computers*와 Saunshi et al.의 *Reasoning with Latent Thoughts*는 반복 구조의 계산 능력을 연구한다 <a class="citation-ref" href="#ref-looped-computers" aria-label="Reference 1">[1]</a><a class="citation-ref" href="#ref-latent-thoughts" aria-label="Reference 2">[2]</a>. 이 글의 BioML 실험은 그 이론의 직접 재현이 아니라, 같은 trainable block을 여러 pass에 적용하는 구조가 실제 예측 과제에서 유용한지 확인한 별도 비교다.

## 요약

- Remote homology 8M의 5회 반복 평균 accuracy는 LT 0.44460, Static 0.43054였고 LT가 앞선 실행은 3/5였다.
- Longer Static accuracy는 0.52592였다. 이는 더 강한 비교군의 필요성을 보여주지만 동일 연산 예산에서 LT가 열등하다는 증거는 아니다.
- 35M 비교에서는 LT 0.58817, Static 0.58984로 기본 8M 비교의 LT 우위가 유지되지 않았다.
- DeepLoc에서도 작은 평균 양성 신호가 있었으나, RNA MRL·mutation scoring·PPI/contact에서는 해당 기준선을 넘지 못했다.
- 표현이 이미 충분하거나 supervision이 반복 갱신을 요구하지 않았다는 설명은 결과 해석을 위한 가설이다. 원인을 분리하는 ablation은 현재 자료에 없다.
- 과제별 block 공유 범위·loop 수·학습 step·연산 예산의 통합 명세가 부족하므로, 결론은 이 비교 묶음에서 안정적 개선을 확인하지 못했다는 범위로 둔다.

{% include model-mention-cards.html label="사용한 주요 리소스" aria_label="Looped Transformer와 BioML 평가 관련 주요 리소스" models="Looped Transformers as Programmable Computers|arXiv:2301.13196|https://arxiv.org/abs/2301.13196;Reasoning with Latent Thoughts|arXiv:2502.17416|https://arxiv.org/abs/2502.17416;ESM2-8M|facebook/esm2_t6_8M_UR50D|https://huggingface.co/facebook/esm2_t6_8M_UR50D;TAPE remote homology|arXiv:1906.08230|https://arxiv.org/abs/1906.08230" %}

## 문제 설정

평가 가설은 일부 생물학 서열 문제가 local motif나 composition만으로 설명되지 않고, 서열 전체의 관계를 여러 번 갱신하는 과정에서 개선될 수 있다는 것이었다. Remote homology는 sequence-level representation으로 fold 또는 superfamily-level class를 예측하는 평가 설정이고, protein interface/contact는 두 chain 사이의 residue-pair 관계를 예측하는 평가 설정이다. 이런 문제에서는 반복적인 전역 표현 정제가 도움이 될 수 있다고 가정했다.

다만 BioML이라는 범주는 서로 다른 신호 구조를 가진 평가 문제를 함께 묶는다. RNA MRL, mutation scoring, solubility, localization, remote homology, interface contact는 모두 sequence 또는 structure 관련 문제지만, label이 의존하는 단위는 motif, local window, protein-level class, residue-pair relation처럼 다르다.

## 평가 설계

평가는 반복 갱신이 유리할 가능성이 있는 문제를 여러 축으로 나누어 구성했다. RNA MRL과 mutation scoring은 local motif, k-mer, mutation position처럼 짧은 범위의 신호가 강한 축이다. Remote homology와 DeepLoc/Solubility는 protein-level 표현이 label로 이어지는 축이고, PPI/contact/PINDER는 pair-level interaction 또는 residue contact를 다루는 축이다.

ESM2는 Lin et al.의 pretrained protein language model이며 <a class="citation-ref" href="#ref-esm2" aria-label="Reference 3">[3]</a>, remote homology의 관련 benchmark는 Rao et al.의 TAPE다 <a class="citation-ref" href="#ref-tape" aria-label="Reference 4">[4]</a>. 구조 분류 체계의 배경은 SCOPe를 참고할 수 있다 <a class="citation-ref" href="#ref-scope" aria-label="Reference 5">[5]</a>. 이 출처들이 아래 자체 실험 수치의 재현을 보증하지는 않는다. Table 1은 과제별 비교 축을 정리한다.

파라미터 수를 맞추는 비교와 연산량을 맞추는 비교는 다른 질문이다. 같은 block을 반복하면 파라미터를 공유해도 pass만큼 계산이 늘어난다. Static ensemble은 여러 모델의 추론 비용을, longer Static은 추가 학습 비용을 쓴다. 따라서 이 비교들은 강한 대조군에 대한 민감도를 확인하며, 하나의 동일 예산 구조 ablation으로 합쳐 해석하지 않는다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <colgroup>
        <col style="width: 28%;">
        <col style="width: 34%;">
        <col style="width: 38%;">
      </colgroup>
      <thead>
        <tr>
          <th>문제 축</th>
          <th>예측 단위</th>
          <th>주요 비교 포인트</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>RNA MRL / BEACON</td>
          <td>sequence-level regulation score</td>
          <td>k-mer / local motif / composition baseline</td>
        </tr>
        <tr>
          <td>Mutation scoring</td>
          <td>variant effect ranking</td>
          <td>local readout / mutation position / window-level representation</td>
        </tr>
        <tr>
          <td>Remote homology</td>
          <td>fold/superfamily-level class</td>
          <td>seed 방향성 / Static baseline / scale 변화</td>
        </tr>
        <tr>
          <td>DeepLoc / Solubility</td>
          <td>protein-level class 또는 property</td>
          <td>Remote homology 신호의 protein-level 전이</td>
        </tr>
        <tr>
          <td>PPI / contact / PINDER</td>
          <td>pair-level interaction 또는 contact</td>
          <td>pairwise readout과 interface supervision이 반복 갱신의 장점을 드러내는지</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> LT를 시험한 BioML 평가 문제 축이다. 표는 각 축의 예측 단위와 비교 포인트만 남기고, 결과 수치는 다음 Table 2에서 따로 요약한다.</figcaption>
</figure>

## 결과

### 결과 개요

Table 2는 각 과제에서 사용한 지표와 기준선을 나란히 놓는다. Accuracy, macro-F1, Spearman, AUPRC는 서로 다른 지표이므로 행 사이의 차이 크기를 직접 비교할 수 없다. Remote homology와 DeepLoc의 평균 양성 결과를 먼저 인정한 뒤, Table 3에서 기준선을 확장했을 때도 그 우위가 유지되는지 확인한다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <colgroup>
        <col style="width: 22%;">
        <col style="width: 18%;">
        <col style="width: 16%;">
        <col style="width: 16%;">
        <col style="width: 8%;">
        <col style="width: 20%;">
      </colgroup>
      <thead>
        <tr>
          <th>문제 축</th>
          <th>대표 지표</th>
          <th class="align-right">Baseline</th>
          <th class="align-right">LT</th>
          <th>방향</th>
          <th>비고</th>
        </tr>
      </thead>
      <tbody>
        <tr class="table-section-row">
          <td colspan="6"><strong>약한 양성 신호</strong></td>
        </tr>
        <tr>
          <td rowspan="2">Remote homology</td>
          <td class="metric-label">accuracy</td>
          <td class="align-right"><code>0.43054</code></td>
          <td class="align-right"><code>0.44460</code></td>
          <td><code>+</code></td>
          <td>accuracy 우세 <code>3/5</code></td>
        </tr>
        <tr>
          <td class="metric-label">macro-F1</td>
          <td class="align-right"><code>0.11768</code></td>
          <td class="align-right"><code>0.12609</code></td>
          <td><code>+</code></td>
          <td>평균 양성</td>
        </tr>
        <tr>
          <td rowspan="2">DeepLoc</td>
          <td class="metric-label">accuracy</td>
          <td class="align-right"><code>0.44922</code></td>
          <td class="align-right"><code>0.46172</code></td>
          <td><code>+</code></td>
          <td>accuracy 우세 <code>4/5</code></td>
        </tr>
        <tr>
          <td class="metric-label">macro-F1</td>
          <td class="align-right"><code>0.33337</code></td>
          <td class="align-right"><code>0.36636</code></td>
          <td><code>+</code></td>
          <td>F1 우세 <code>3/5</code></td>
        </tr>
        <tr class="table-section-row">
          <td colspan="6"><strong>개선 부재 또는 음성 신호</strong></td>
        </tr>
        <tr>
          <td>RNA MRL</td>
          <td>Spearman</td>
          <td class="align-right"><code>0.77079</code></td>
          <td class="align-right"><code>0.47935</code></td>
          <td><code>-</code></td>
          <td>local/k-mer 신호가 우세</td>
        </tr>
        <tr>
          <td>Mutation scoring</td>
          <td>ranking score</td>
          <td class="align-right"><code>0.43957</code></td>
          <td class="align-right"><code>0.32921</code></td>
          <td><code>-</code></td>
          <td>local-window Static 우세</td>
        </tr>
        <tr>
          <td>PPI pooled pair-MLP</td>
          <td>AUPRC</td>
          <td class="align-right"><code>0.92363</code></td>
          <td class="align-right"><code>0.91998</code></td>
          <td><code>-</code></td>
          <td>차이는 작지만 Static 우세</td>
        </tr>
        <tr>
          <td>PINDER interface-contact</td>
          <td>test AUPRC</td>
          <td class="align-right"><code>0.26890</code></td>
          <td class="align-right"><code>0.25809</code></td>
          <td><code>-</code></td>
          <td>세 PINDER 설정 모두 음성</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> 평가 축별 대표 결과다. 모두 높을수록 좋은 지표이며 방향은 LT minus baseline의 부호다. 부호는 효과 크기나 통계적 유의성을 뜻하지 않는다. Mutation scoring의 원 지표명은 추가 확인이 필요하다. 세부 delta와 반복 실행 요약은 Appendix에 둔다.</figcaption>
</figure>

### 약한 양성 신호와 안정성 한계

Table 2에서 양성 방향으로 남은 축은 Remote homology와 DeepLoc이다. 이 둘은 음성 결과와 구분해 따로 볼 필요가 있다. 다만 평균 delta가 양수였다는 사실만으로 LT 구조에 고유한 안정적 개선이라고 보기는 어렵다.

Remote homology 8M의 5회 반복 실행에서는 LT가 Static보다 평균 accuracy와 macro-F1이 높았다. 그러나 실행별 accuracy 우세는 `3/5`였다. 이는 평균과 실행별 방향성을 구분해야 한다는 뜻이다. Seed별 분포나 불확실성 구간 없이 3/5만으로 유의성이나 재현 확률을 판단할 수 없다.

기준선을 확장하면 판단도 달라진다. Static 3회 반복 ensemble은 LT 단일 모델보다 약간 높고, longer Static은 더 큰 차이로 앞섰다. 35M 비교에서도 LT의 accuracy 우위는 유지되지 않았다. 이는 기본 8M Static 하나에 대한 개선을 구조 전반의 우위로 확대하기 어렵다는 근거다. 다만 ensemble·장기 학습·모델 scale은 각각 비용과 설정을 바꾸므로, 어느 비교도 단독으로 반복 구조의 인과적 효과를 확정하지 않는다. Table 3은 이 구분을 위해 비교 조건을 나눠 제시한다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--numeric-columns metrics-table--paired-rows">
      <colgroup>
        <col style="width: 28%;">
        <col style="width: 18%;">
        <col style="width: 18%;">
        <col style="width: 20%;">
        <col style="width: 16%;">
      </colgroup>
      <thead>
        <tr>
          <th>비교 조건</th>
          <th>지표</th>
          <th class="align-right">LT</th>
          <th class="align-right">Static / 비교군</th>
          <th class="align-right">delta</th>
        </tr>
      </thead>
      <tbody>
        <tr class="metric-pair-start">
          <td rowspan="2">5회 반복 실행</td>
          <td class="metric-label">accuracy</td>
          <td class="align-right"><code>0.44460</code></td>
          <td class="align-right"><code>0.43054</code></td>
          <td class="align-right"><code>+0.01405</code></td>
        </tr>
        <tr class="metric-pair-end">
          <td class="metric-label">macro-F1</td>
          <td class="align-right"><code>0.12609</code></td>
          <td class="align-right"><code>0.11768</code></td>
          <td class="align-right"><code>+0.00842</code></td>
        </tr>
        <tr class="metric-pair-start">
          <td rowspan="2">Static ensemble</td>
          <td class="metric-label">accuracy</td>
          <td class="align-right"><code>0.44149</code></td>
          <td class="align-right"><code>0.44285</code></td>
          <td class="align-right"><code>-0.00135</code></td>
        </tr>
        <tr class="metric-pair-end">
          <td class="metric-label">macro-F1</td>
          <td class="align-right"><code>0.12411</code></td>
          <td class="align-right"><code>0.12485</code></td>
          <td class="align-right"><code>-0.00074</code></td>
        </tr>
        <tr class="metric-pair-start">
          <td rowspan="2">Longer Static</td>
          <td class="metric-label">accuracy</td>
          <td class="align-right"><code>0.44460</code></td>
          <td class="align-right"><code>0.52592</code></td>
          <td class="align-right"><code>-0.08132</code></td>
        </tr>
        <tr class="metric-pair-end">
          <td class="metric-label">macro-F1</td>
          <td class="align-right"><code>0.12609</code></td>
          <td class="align-right"><code>0.21621</code></td>
          <td class="align-right"><code>-0.09012</code></td>
        </tr>
        <tr>
          <td>35M scale 평가</td>
          <td class="metric-label">accuracy</td>
          <td class="align-right"><code>0.58817</code></td>
          <td class="align-right"><code>0.58984</code></td>
          <td class="align-right"><code>-0.00167</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> Remote homology에서 약한 평균 양성 신호가 더 엄격한 Static 비교와 scale 평가를 지나며 좁아지는 과정이다. 실행별 방향성은 본문에서 따로 언급하고, 표는 수치 비교만 분리해 제시한다.</figcaption>
</figure>

DeepLoc에서도 비슷한 한계가 있었다. 5회 반복 실행에서 LT는 Static보다 `+0.01250` accuracy, `+0.03299` macro-F1 높았고, accuracy 우세는 `4/5`였다. 하지만 longer Static 관련 주의점이 남아 있고, Solubility에서는 같은 패턴이 약했다. 따라서 DeepLoc은 remote homology 다음의 약한 양성 축일 수는 있어도, BioML 전반의 안정적 개선을 뒷받침하지는 않는다.

## 해석: 원인 후보와 필요한 통제

Local/k-mer와 local-window 기준선이 강했다는 관찰은 해당 과제에서 짧은 범위의 신호가 유용함을 보여준다. 그러나 그 신호만으로 label이 충분히 설명된다거나 LT가 추가 정보를 만들지 못한다는 인과는 확인하지 않았다. 마찬가지로 PPI/contact의 음성 결과만으로 supervision이 관계 정제를 요구하지 않았다고 결론낼 수 없다. 모델 구성, 최적화, readout 또는 데이터 규모가 영향을 주었을 가능성도 남아 있다.

Tied recurrence와 독립적인 Static depth도 구분해야 한다. 기록된 depth 비교는 `static_3l` NLL `2.88969`, `lt_1l_r3` NLL `2.89345`로, 낮을수록 좋은 NLL에서 LT가 앞서지 않았다. 이 한 비교는 반복 횟수가 독립 layer의 표현 다양성을 보장하지 않는다는 해석과 맞지만, 모든 tied 구조의 한계를 입증하지는 않는다.

Remote homology에서 가장 유리했던 LT 설정은 pass aggregation과 recurrent MLM warmup을 포함했다. 이는 해당 조합의 결과이며 recurrence 단독 효과가 아니다. Pass별 표현에 정보가 분산됐다는 설명을 확인하려면 pass별 readout을 비교하고, Static에도 layer aggregation·learned layer mixing·warmup을 제공해야 한다. 추가 학습 step과 연산량까지 맞춰야 구조 효과와 보조 학습 효과가 구분된다.

## 결론과 한계

이 평가 묶음은 LT의 일반적인 BioML 개선을 뒷받침하지 않는다. 가장 유망했던 Remote homology도 기본 Static 대비 작은 평균 개선에서 출발해, 더 강하거나 다른 예산의 Static과 비교하면 우위가 유지되지 않았다. 후속 실험의 핵심은 양성 과제를 더 나열하는 것보다 같은 예산에서 recurrence가 추가하는 효과를 확인하는 것이다.

비교 예산은 완전히 균일하지 않다. 기록된 원고만으로는 각 과제의 공유 block 범위·loop 수·trainable parameter 수·학습 step과 연산 비용, split과 seed별 결과를 모두 확인할 수 없다. Mutation scoring의 정확한 지표명과 과제별 데이터 버전·표본 수에도 기록 공백이 있다. 그러므로 표의 aggregate는 해당 기준선과의 관찰로 읽고, 동일 예산에서의 구조 우열이나 과제 전반의 통합 효과 크기로 해석하지 않는다.

PINDER/contact의 음성 결과는 표본화된 interface-contact 설정에 한정된다. 모든 interface formulation이나 LT 구조 전체의 부정은 아니다. Decoder continuation의 일부 양성 NLL 결과 역시 encoder형 BioML 과제와 별도로 읽어야 한다. 표현의 충분성이나 supervision 형태는 이 관찰을 설명할 원인 후보로 남는다.

## Appendix: 세부 수치

<details>
  <summary>Remote homology, DeepLoc, Solubility 반복 실행 요약</summary>
  <div class="details-content">
    <figure class="table-figure table-figure--metrics">
      <div class="table-shell">
        <table class="metrics-table metrics-table--numeric-columns">
          <thead>
            <tr>
              <th>평가 문제 / 비교</th>
              <th class="align-right">Static</th>
              <th class="align-right">LT</th>
              <th class="align-right">Delta</th>
              <th>비고</th>
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
              <td>약한 두 번째 양성 신호, Acc 우세 <code>4/5</code></td>
            </tr>
            <tr>
              <td>DeepLoc<br><span class="table-note-inline">5회 반복 macro-F1</span></td>
              <td class="align-right"><code>0.33337</code></td>
              <td class="align-right"><code>0.36636</code></td>
              <td class="align-right"><code>+0.03299</code></td>
              <td>F1 우세 <code>3/5</code>, longer Static 관련 주의점 존재</td>
            </tr>
            <tr>
              <td>Solubility<br><span class="table-note-inline">5회 반복 Acc</span></td>
              <td class="align-right"><code>0.62539</code></td>
              <td class="align-right"><code>0.63320</code></td>
              <td class="align-right"><code>+0.00781</code></td>
              <td>작은 평균 양성, 안정성 제한</td>
            </tr>
          </tbody>
        </table>
      </div>
      <figcaption><strong>Appendix Table 1.</strong> Remote homology, DeepLoc, Solubility의 5회 반복 실행 평균 delta와 우세 횟수 요약이다. Table 3이 Remote homology의 Static 비교를 분리한다면, 이 표는 protein-level 축의 반복 실행 신호를 나란히 제시하는 보조 표다.</figcaption>
    </figure>
  </div>
</details>

<details>
  <summary>Local/interface/decoder 보조 수치</summary>
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
              <th>읽는 범위</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>RNA MRL</td>
              <td>k-mer ridge Spearman <code>0.77079</code>, LT <code>0.47935</code>.</td>
              <td>local/k-mer 조건</td>
            </tr>
            <tr>
              <td>Mutation scoring</td>
              <td>local-window Static <code>0.43957</code>, 최고 LT 설정 <code>0.32921</code>.</td>
              <td>local readout / position signal 조건</td>
            </tr>
            <tr>
              <td>PPI pooled pair-MLP</td>
              <td>AUPRC Static <code>0.92363</code>, LT <code>0.91998</code>, delta <code>-0.00364</code>.</td>
              <td>pooled pairwise 평가에서 Static 우세</td>
            </tr>
            <tr>
              <td>PINDER interface-contact</td>
              <td>test AUPRC delta는 frozen-head pilot <code>-0.01892</code>, MLP/full-finetune <code>-0.02402</code>, interface-summary <code>-0.01081</code>.<br><span class="table-note-inline">가장 완화된 interface-summary 설정 평균은 Static <code>0.26890</code>, LT <code>0.25809</code>.</span></td>
              <td>해당 interface-contact 설정의 음성 결과</td>
            </tr>
            <tr>
              <td>Protein decoder continuation</td>
              <td>일부 continuation NLL에서는 LT가 같은 파라미터 수의 Static보다 약간 좋았지만, 비슷한 연산량의 Static보다 뒤였다.</td>
              <td>별도 decoder 축의 약한 양성 신호</td>
            </tr>
          </tbody>
        </table>
      </div>
      <figcaption><strong>Appendix Table 2.</strong> Table 2에서 압축한 local/k-mer, mutation, interface/contact, decoder continuation 축의 보조 수치다. 본문 해석을 반복하기보다, 각 축의 읽는 범위를 짧게 덧붙인다.</figcaption>
    </figure>
  </div>
</details>

<details>
  <summary>후속 검증 가설</summary>
  <div class="details-content">
<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <colgroup>
        <col style="width: 32%;">
        <col style="width: 34%;">
        <col style="width: 34%;">
      </colgroup>
      <thead>
        <tr>
          <th>조건</th>
          <th>대표 관찰</th>
          <th>요약 해석</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Local / compositional signal의 설명력이 충분한가?</td>
          <td>RNA MRL k-mer ridge, mutation scoring local-window Static이 LT보다 강했다.</td>
          <td>Local signal을 통제한 뒤에도 recurrence 이득이 남는지 확인한다.</td>
        </tr>
        <tr>
          <td>Pretrained Static 표현만으로 충분한가?</td>
          <td>Remote homology의 양성 신호는 Static ensemble, longer Static, scale 비교에서 좁아졌다.</td>
          <td>표현 충분성은 관찰의 가능한 설명이며 별도 진단이 필요하다.</td>
        </tr>
        <tr>
          <td>Tied recurrence가 Static depth를 대체하지 못한다.</td>
          <td>Depth 비교에서 <code>lt_1l_r3</code>은 <code>static_3l</code>을 넘지 못했다.</td>
          <td>반복 횟수는 depth처럼 보이지만, layer별 표현 다양성까지 보장하지 않는다.</td>
        </tr>
        <tr>
          <td>약한 양성 신호가 보조 설정에 의존한다.</td>
          <td>가장 유리한 Remote homology LT 설정은 pass aggregation과 recurrent MLM warmup을 포함했다.</td>
          <td>양성 신호가 보조 설정에 묶이면 Static baseline도 같은 조건으로 확장해야 한다.</td>
        </tr>
        <tr>
          <td>Supervision / readout이 관계 갱신을 요구하는가?</td>
          <td>PPI/contact/PINDER는 관계 갱신과 맞아 보였지만 해당 설정에서는 Static을 넘지 못했다.</td>
          <td>Label/readout을 바꾸는 대조 실험으로 이 가설을 확인해야 한다.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 3.</strong> 관찰에서 도출한 후속 검증 가설이다. 인과적으로 확인된 조건 목록은 아니다. 표는 개별 문제 이름보다 label signal, Static baseline, recurrence depth, 보조 설정, supervision/readout 구조를 기준으로 결과를 읽기 위한 체크리스트다.</figcaption>
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
Ilho Ahn, "BioML에서 검증한 Looped Transformer: 안정적 개선으로 이어지지 않은 반복 구조", Ilho’s Notes, May 5, 2026.
```

또는 BibTeX 형식으로는 다음처럼 적을 수 있다.

```bibtex
@article{ahn2026loopedtransformerbiomlnostablegain,
  author = {Ilho Ahn},
  title = {BioML에서 검증한 Looped Transformer: 안정적 개선으로 이어지지 않은 반복 구조},
  journal = {Ilho’s Notes},
  year = {2026},
  month = may,
  url = {https://muted-color.github.io/research/2026/05/05/looped-transformer-bioml-no-stable-gain/}
}
```
