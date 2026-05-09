---
title: "Looped Transformer는 BioML 평가에서 안정적 개선으로 분리되지 않았다"
date: 2026-05-05 08:27:16 +0900
last_modified_at: 2026-05-09 09:47:57 +0900
categories: ["BIO ML"]
tags: [bioml, looped-transformer, esm2, remote-homology, protein-language-model, model-architecture, negative-result]
lab_path: "experiment-lab/projects/protein-lt-boundary-conditions"
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

Looped Transformer는 같은 Transformer block 또는 소수 block을 여러 번 반복 적용해 유효 깊이를 늘리는 구조다. 직관적으로는 반복 pass가 전역 표현을 조금씩 정제하고, 적은 파라미터로 Static depth 일부를 대체할 수 있을 것처럼 보인다. BioML에는 장거리 서열 관계, fold/superfamily-level classification, protein interface처럼 반복 갱신이 도움이 될 수 있다고 가정할 만한 문제가 있다.

이 글은 Looped Transformer가 이런 BioML 평가에서 안정적 개선을 만드는지 검토한 결과를 정리한다. 결론은 뚜렷한 양성 결과보다 경계 결과에 가깝다. **LT는 이 평가 묶음에서 일반적인 개선법으로 분리되지 않았다.** 일부 전역 표현 평가에서는 약한 양성 신호가 있었지만, 더 강한 Static baseline과 비교했을 때 LT 구조에 고유한 개선으로 남지 않았다.

핵심 해석은 개선 부재가 무작위로 흩어지지 않았다는 점이다. local/compositional 신호가 강하거나, pretrained Static 표현이 이미 충분하거나, supervision/readout이 반복적 관계 정제를 요구하지 않는 문제에서는 반복 pass가 성능을 제한하는 지점을 직접 건드리지 못했다. 세부 수치와 조건별 해석은 아래 요약과 표에서 분리해 정리한다.

> **Looped Transformer / LT**: 이 글에서는 같은 trainable block을 여러 pass에 반복 적용하는 recurrent-depth Transformer 계열을 뜻한다.
>
> **안정적 개선**: 평균 delta가 반복 실행별 방향성, 더 강한 Static baseline, scale 변화에서도 같은 주장 범위로 유지되는 경우를 뜻한다.

{% include model-mention-cards.html label="사용한 주요 리소스" aria_label="Looped Transformer와 BioML 평가 관련 주요 리소스" models="Looped Transformers as Programmable Computers|arXiv:2301.13196|https://arxiv.org/abs/2301.13196;Reasoning with Latent Thoughts|arXiv:2502.17416|https://arxiv.org/abs/2502.17416;ESM2-8M|facebook/esm2_t6_8M_UR50D|https://huggingface.co/facebook/esm2_t6_8M_UR50D;TAPE remote homology|arXiv:1906.08230|https://arxiv.org/abs/1906.08230" %}

## 요약

- LT는 RNA regulation, mutation scoring, fold-level classification, subcellular localization, solubility, PPI/contact 평가 축에서 전반적인 안정적 개선법으로 분리되지 않았다.
- Remote homology와 DeepLoc에서는 약한 평균 양성 신호가 있었지만, 반복 실행별 방향성과 더 강한 Static baseline 비교를 지나며 LT 구조에 고유한 개선으로 분리되지 않았다.
- RNA/k-mer, mutation scoring, PPI/contact/PINDER interface-contact에서는 local signal, readout, supervision 구조가 반복 갱신의 장점을 드러내지 못했다.
- 반복된 패턴은 LT 전체의 부정이 아니라, local/compositional 신호가 강하거나 pretrained Static 표현이 충분하거나 supervision/readout이 반복적 관계 정제를 요구하지 않는 조건에서는 recurrence가 안정적 개선으로 남기 어렵다는 제한적 결론이다.

## 문제 설정

평가 가설은 일부 생물학 서열 문제가 local motif나 composition만으로 설명되지 않고, 서열 전체의 관계를 여러 번 갱신하는 과정에서 개선될 수 있다는 것이었다. Remote homology는 sequence-level representation으로 fold 또는 superfamily-level class를 예측하는 평가 설정이고, protein interface/contact는 두 chain 사이의 residue-pair 관계를 예측하는 평가 설정이다. 이런 문제에서는 반복적인 전역 표현 정제가 도움이 될 수 있다고 가정했다.

다만 BioML이라는 범주는 서로 다른 신호 구조를 가진 평가 문제를 함께 묶는다. RNA MRL, mutation scoring, solubility, localization, remote homology, interface contact는 모두 sequence 또는 structure 관련 문제지만, label이 의존하는 단위는 motif, local window, protein-level class, residue-pair relation처럼 다르다.

## 평가 문제 축

평가는 반복 갱신이 유리할 가능성이 있는 문제를 여러 축으로 나누어 구성했다. RNA MRL과 mutation scoring은 local motif, k-mer, mutation position처럼 짧은 범위의 신호가 강한 축이다. Remote homology와 DeepLoc/Solubility는 protein-level 표현이 label로 이어지는 축이고, PPI/contact/PINDER는 pair-level interaction 또는 residue contact를 다루는 축이다.

따라서 Table 1은 결과 표가 아니라 평가 축의 인덱스로 둔다. 각 축에서 봐야 할 것은 생물학적 이름보다 label이 어떤 단위의 정보를 요구하고 어떤 baseline과 비교해야 하는지다.

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

결과의 중심은 단순한 승패보다, LT의 반복 pass가 어떤 제한 요인을 줄이지 못했는가에 있다. 이 평가에서 개선 부재는 무작위로 흩어지지 않았다. **반복된 패턴은 label이 요구하는 정보 단위와 Static baseline이 이미 설명한 범위에 더 가까웠다.** local/compositional 신호가 강한 문제, pretrained Static 표현이 이미 충분한 문제, 또는 pairwise/interface readout이 실제 반복적 관계 갱신을 요구하지 않는 문제에서 LT delta는 안정적으로 남지 않았다.

반대로 **Remote homology와 DeepLoc처럼 protein-level 전역 표현을 쓰는 축에서는 약한 평균 양성 신호가 남았다.** 하지만 이 신호도 실행별 방향성, Static ensemble, longer Static, scale 변화까지 지나면 LT 구조에 고유한 안정적 개선으로 분리되지 않았다. 따라서 이 글의 중심 결과는 "LT가 모든 BioML 평가에서 실패했다"가 아니라, LT가 안정적 개선으로 남기 어려운 조건들이 반복적으로 관찰됐다는 쪽에 가깝다.

Table 2는 이 해석을 뒷받침하는 대표 수치를 요약한다. 세부 수치를 모두 나열하기보다, LT가 어디서 약한 양성 신호를 보였고 어디서 개선 부재가 반복됐는지를 한 번에 비교하기 위한 결과 개요다.

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
          <td><code>++</code></td>
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
          <td><code>---</code></td>
          <td>local/k-mer 신호가 우세</td>
        </tr>
        <tr>
          <td>Mutation scoring</td>
          <td>ranking score</td>
          <td class="align-right"><code>0.43957</code></td>
          <td class="align-right"><code>0.32921</code></td>
          <td><code>--</code></td>
          <td>local-window Static 우세</td>
        </tr>
        <tr>
          <td>PPI pooled pair-MLP</td>
          <td>AUPRC</td>
          <td class="align-right"><code>0.92363</code></td>
          <td class="align-right"><code>0.91998</code></td>
          <td><code>0/-</code></td>
          <td>차이는 작지만 Static 우세</td>
        </tr>
        <tr>
          <td>PINDER interface-contact</td>
          <td>test AUPRC</td>
          <td class="align-right"><code>0.26890</code></td>
          <td class="align-right"><code>0.25809</code></td>
          <td><code>--</code></td>
          <td>세 PINDER 설정 모두 음성</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> 평가 축별 대표 결과다. 방향은 LT 기준의 상대 방향을 요약한다. <code>+</code>는 약한 양성, <code>++</code>는 비교적 큰 양성, <code>0/-</code>는 거의 동률 또는 약한 음성, <code>-</code>/<code>--</code>/<code>---</code>는 음성 방향을 뜻한다. 세부 delta와 반복 실행 요약은 Appendix에 둔다.</figcaption>
</figure>

### 약한 양성 신호와 안정성 한계

Table 2에서 양성 방향으로 남은 축은 Remote homology와 DeepLoc이다. 이 둘은 음성 결과와 구분해 따로 볼 필요가 있다. 다만 평균 delta가 양수였다는 사실만으로 LT 구조에 고유한 안정적 개선이라고 보기는 어렵다.

Remote homology 8M의 5회 반복 실행에서는 LT가 Static보다 평균 accuracy와 macro-F1이 높았다. 그러나 실행별 accuracy 우세는 `3/5`였다. 반복 실행 대부분에서 같은 방향이 유지되는 결과를 안정적 개선의 근거로 본다면, 이 결과는 "재현된 평균 양성 신호"이지 안정적 근거는 아니다.

이 양성 신호는 더 엄격한 Static 비교를 지나며 좁아졌다. 여기서 더 엄격한 비교란 단일 Static이 아니라 Static 3회 반복 ensemble, 더 오래 학습한 longer Static, 그리고 35M scale Static을 함께 보는 것이다. Static ensemble은 LT 단일 모델보다 약간 높았고, longer Static은 LT를 크게 앞섰다. 35M scale 평가에서는 LT의 accuracy 우위도 유지되지 않았다. 이 패턴은 Remote homology가 "LT 성공 사례"라기보다 "가장 오래 유지된 예외적 양성 신호"였다는 해석을 지지한다. Table 3은 이 축에서 평균 양성 신호가 비교 조건을 지나며 어떻게 좁아졌는지 수치만 분리해 정리한다.

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

### 일반화된 제한 요인

Table 2와 Table 3을 함께 보면 결과는 단순한 task별 승패보다, LT의 recurrence가 어떤 조건에서 추가 정보를 만들지 못했는가로 정리된다. 평균 delta가 양수였던 Remote homology와 DeepLoc도 더 엄격한 Static 비교를 지나며 좁아졌고, 음성 축에서는 local signal이나 pairwise readout이 먼저 성능을 설명했다. 따라서 이 결과에서 일반화할 수 있는 것은 특정 평가 축의 승패보다, **어떤 제한 요인이 남아 있을 때 LT가 안정적 개선으로 분리되기 어려운가**에 가깝다.

<p class="metric-detail__eyebrow">Label을 결정하는 신호의 단위</p>

RNA MRL과 BEACON 계열에서는 k-mer, local window, composition이 강했고, mutation scoring에서는 mutation position과 local readout이 더 큰 영향을 줬다. 이런 task에서는 반복적인 전역 표현 갱신이 주된 병목이 아니므로, recurrence는 새 정보를 만드는 대신 이미 충분한 local signal 위에 추가 변환을 더하는 데 머물 수 있다.

<p class="metric-detail__eyebrow">Static baseline이 이미 설명한 범위</p>

Remote homology와 DeepLoc의 약한 양성 신호는 protein-level 전역 표현이 필요한 축에서 관찰됐지만, Static ensemble, longer Static, 35M scale 비교를 지나며 LT 구조에 고유한 개선으로 남지 않았다. pretrained Static 표현이 이미 전역 정보를 충분히 담고 있다면, 같은 block을 반복하는 recurrence는 새로운 inductive bias라기보다 기존 표현의 재가공에 가까워진다.

<p class="metric-detail__eyebrow">Supervision과 readout의 형태</p>

PPI/contact는 평가 유형만 보면 반복적인 관계 갱신을 요구할 가능성이 커 보인다. 하지만 기존 pooled pairwise 평가와 PINDER interface-contact 평가에서 Static은 LT보다 강하거나 비슷했다. 이 평가에서는 label과 readout이 실제 cross-chain 관계 정제를 충분히 요구하지 않았을 가능성이 있다. 즉 관계형 평가처럼 보인다는 사실만으로 LT의 recurrent update가 직접적인 제한 요인 완화로 이어지지는 않았다.

<p class="metric-detail__eyebrow">Tied recurrence와 Static depth의 차이</p>

Static Transformer의 여러 layer는 서로 다른 파라미터를 갖고, pretrained backbone에서는 layer마다 다른 정보를 담을 수 있다. 반면 LT는 같은 block을 반복한다. 따라서 `1-layer loop r=3`이 `static 3-layer`를 자동으로 대체한다는 기대는 성립하지 않았다. 실제 depth 비교에서도 `static_3l` NLL `2.88969`, `lt_1l_r3` NLL `2.89345`로 LT가 Static 3-layer를 넘지 못했다.

<p class="metric-detail__eyebrow">보조 설정 의존성</p>

Remote homology에서 가장 유리했던 LT 설정은 pass aggregation과 recurrent MLM warmup을 포함했다. 이것은 LT가 마지막 pass 하나로 바로 좋은 표현을 만드는 것이 아니라, 여러 pass trajectory에 정보가 분산될 수 있음을 시사한다.

하지만 이 관찰은 동시에 비교 설계의 문제를 만든다. LT가 pass aggregation과 recurrent warmup을 받아야 약한 양성 신호를 만든다면, Static도 layer aggregation, learned layer mixing, static warmup, longer training을 받아야 한다. 이 대조군을 주면 LT 구조에 고유한 개선 범위는 더 좁아진다.

따라서 pass aggregation과 warmup은 "가장 높은 성능의 LT 설정"을 찾았다는 의미보다, LT 구조 고유의 효과를 주장하려면 Static 대조군도 같이 확장해야 함을 시사한다. Table 4는 위 해석을 조건별 체크리스트로 압축한 것이다.

### 안정적 개선이 분리되지 않은 조건

Table 4는 앞의 해석을 짧은 조건 목록으로 다시 정리한다. 표의 목적은 LT가 작동하지 않는 문제 목록을 나열하는 것이 아니라, **recurrence가 안정적 개선으로 분리되기 어려웠던 조건**을 빠르게 확인하는 것이다. 자세한 설명은 앞 섹션에 두고, 표에는 대표 관찰과 요약 해석만 남긴다.

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
          <td>Local / compositional signal이 label을 충분히 설명한다.</td>
          <td>RNA MRL k-mer ridge, mutation scoring local-window Static이 LT보다 강했다.</td>
          <td>전역 갱신이 주된 병목이 아니면 recurrence는 추가 정보보다 재변환에 머문다.</td>
        </tr>
        <tr>
          <td>Pretrained Static 표현이 전역 정보를 이미 담고 있다.</td>
          <td>Remote homology와 DeepLoc의 양성 신호는 Static ensemble, longer Static, scale 비교에서 좁아졌다.</td>
          <td>전역 정보가 이미 들어 있으면 같은 block 반복은 새로운 inductive bias보다 재가공에 가까워진다.</td>
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
          <td>Supervision / readout이 관계 갱신을 직접 요구하지 않는다.</td>
          <td>PPI/contact/PINDER는 관계 갱신과 맞아 보였지만 해당 설정에서는 Static을 넘지 못했다.</td>
          <td>학습 신호가 cross-chain refinement를 요구하지 않으면 반복 pass의 장점이 드러나기 어렵다.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> LT의 안정적 개선이 분리되지 않았던 조건 요약이다. 표는 개별 문제 이름보다 label signal, Static baseline, recurrence depth, 보조 설정, supervision/readout 구조를 기준으로 결과를 읽기 위한 체크리스트다.</figcaption>
</figure>

## 결론

본 평가 묶음에서 LT는 안정적 개선으로 분리되지 않았다. Remote homology와 DeepLoc에서는 약한 평균 양성 신호가 있었지만, 반복 실행별 방향성, Static ensemble, longer Static, scale 비교를 지나며 LT 구조에 고유한 개선으로 분리되지 않았다. RNA/k-mer, mutation scoring, PPI/contact/PINDER interface-contact에서는 local signal, readout, supervision 구조가 반복 pass의 장점을 드러내지 못했다.

따라서 이 결과는 LT의 반복 pass가 BioML 문제에서 자동으로 전역 정보 병목을 줄인다는 가정을 지지하지 않는다. 본 평가 묶음에서는 local/compositional signal, pretrained Static 표현, tied recurrence의 표현 한계, 또는 aggregation/warmup 같은 보조 설정의 영향이 더 크게 남았다. 반대로 LT가 의미 있는 후보가 되려면, 반복 pass가 local signal의 재가공을 넘어 매 단계 새 정보를 통합해야 한다. 그런 조건은 label과 supervision이 전역 표현 갱신이나 관계 정제를 직접 요구하고, 한 번의 Static 표현으로 충분히 압축되지 않는 문제에서 더 잘 드러날 가능성이 있다.

## 한계

이 글의 일반화 범위는 특정 평가 묶음과 비교 설정 안에 있다. LT 구조 전체나 BioML 전체에 대한 부정 명제가 아니라, 본문에서 정리한 조건에서 LT의 recurrence가 안정적 개선으로 분리되지 않았다는 결과로 읽어야 한다.

비교 예산도 완전히 균일하지 않다. 일부 선별 평가는 반복 횟수, 학습 예산, scale 조건이 서로 다르고, Remote homology와 DeepLoc은 추가 비교가 가능한 축으로 남아 있다. 다만 이 불완전성은 긍정 결론보다 조건부 해석을 더 필요하게 만든다.

마지막으로 PINDER/contact와 decoder continuation은 formulation에 민감하다. PINDER/contact의 음성 결과는 표본화된 interface-contact 설정에서의 결과이고, 모든 interface formulation에 대한 부정은 아니다. decoder continuation에서 보인 약한 양성 신호도 encoder-style BioML 평가 문제와 분리해서 읽어야 한다.

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
Ilho Ahn, "Looped Transformer는 BioML 평가에서 안정적 개선으로 분리되지 않았다", Mini Research, May 5, 2026.
```

또는 BibTeX 형식으로는 다음처럼 적을 수 있다.

```bibtex
@article{ahn2026loopedtransformerbiomlnostablegain,
  author = {Ilho Ahn},
  title = {Looped Transformer는 BioML 평가에서 안정적 개선으로 분리되지 않았다},
  journal = {Mini Research},
  year = {2026},
  month = may,
  url = {https://muted-color.github.io/research/2026/05/05/looped-transformer-bioml-no-stable-gain/}
}
```
