---
title: "Looped Transformer는 어디서 안 맞는가: BioML task screen에서 드러난 narrow task fit"
date: 2026-05-05 08:27:16 +0900
last_modified_at: 2026-05-05 08:27:16 +0900
categories: ["BIOML"]
tags: [bioml, looped-transformer, esm2, remote-homology, protein-language-model, model-architecture, negative-result]
lab_path: "experiment-lab/projects/bio-lt-task-screen-stage0"
excerpt: "BioML task screen에서 Looped Transformer가 전반적 개선법이 아니라 제한적 task-fit 방법으로 남는 조건을 정리한다."
description: "BioML task screen에서 Looped Transformer가 전반적 개선법이 아니라 제한적 task-fit 방법으로 보인 조건과 remote homology 예외를 정리한 실험 노트."
permalink: /research/2026/05/05/looped-transformer-bioml-task-fit/
image: /assets/images/posts/looped-transformer-bioml-task-fit/social-thumbnail.png
image_alt: "반복 loop, 좁은 평가 관문, fold-like sequence trace를 함께 보여주는 Looped Transformer BioML task-fit 대표 이미지"
hero_image: /assets/images/posts/looped-transformer-bioml-task-fit/hero-task-fit.svg
hero_alt: "Looped Transformer의 반복 pass가 좁은 task-fit 관문을 지나 fold-level signal로 이어지는 추상 도식"
hero_caption: "<strong>Figure 1.</strong> 이 글의 핵심 해석을 도식화한 그림이다. Looped Transformer의 반복 pass가 항상 이득으로 이어지는 것이 아니라, 전역 표현 갱신이 실제 병목인 task에서만 좁게 맞는다는 점을 나타낸다. 그림은 실험 수치를 새로 인코딩하지 않고, 본문 주장 범위를 시각적으로 압축한다."
hero_frame: true
hero_compact: true
---

Looped Transformer는 같은 Transformer block 또는 소수 block을 여러 번 반복 적용해 effective depth를 늘리는 구조다. 직관적으로는 static 3-layer 모델을 looped 1-layer, recurrence `r=3`으로 바꾸면 더 적은 파라미터로 비슷한 깊이 효과를 얻을 수 있을 것처럼 보인다. 이 글은 그 기대가 BioML task screen에서 어디까지 버텼는지를 정리한다.

평가 질문은 단순하다. **Looped Transformer가 BioML task 전반에 붙일 수 있는 일반 개선법인가, 아니면 반복적인 전역 표현 갱신이 필요한 일부 task에만 맞는 방법인가.**

현재 결과의 답은 후자에 가깝다. 이번 평가 recipe와 task 묶음 기준에서 LT는 전반적 parameter-efficiency 해법으로 보이지 않았다. 다만 remote homology에서는 matched-data-exposure accuracy 기준으로 static보다 높은 예외가 있었다. 따라서 이 글의 결론은 "LT는 BioML에 맞지 않는다"가 아니라, **LT의 이득 조건은 BioML이라는 도메인 이름보다 task의 signal 구조에 더 강하게 묶인다**는 것이다.

> **Looped Transformer / LT**: 이 글에서는 같은 trainable block을 여러 pass에 반복 적용하는 recurrent-depth Transformer 계열을 뜻한다.
>
> **matched-data-exposure 양성 신호**: 같은 labeled data exposure 기준에서는 LT가 static보다 높았다는 뜻이다. compute, warmup, layer aggregation까지 모두 맞춘 효율성 비교라는 뜻은 아니다.

{% include model-mention-cards.html label="사용한 주요 리소스" aria_label="Looped Transformer와 BioML 평가 관련 주요 리소스" models="Looped Transformers as Programmable Computers|arXiv:2301.13196|https://arxiv.org/abs/2301.13196;Reasoning with Latent Thoughts|arXiv:2502.17416|https://arxiv.org/abs/2502.17416;ESM2-8M|facebook/esm2_t6_8M_UR50D|https://huggingface.co/facebook/esm2_t6_8M_UR50D;TAPE remote homology|arXiv:1906.08230|https://arxiv.org/abs/1906.08230" %}

## 요약

- 이번 평가 recipe와 task 묶음 기준에서 LT는 BioML 전반의 일반 개선법으로 작동하지 않았다.
- 가장 좋은 양성 신호는 ESM2-8M 기반 remote homology에서 나왔다. pass aggregation과 recurrent MLM warmup을 포함한 LT recipe는 matched-data-exposure static보다 accuracy `+0.01593`, macro-F1 `+0.00547` 높았다.
- 그러나 static longer-training stress baseline은 accuracy `0.52592`, macro-F1 `0.21621`로 현재 LT recipe보다 높았다. 따라서 이 결과는 compute/warmup-fair efficiency 주장이 아니다.
- adjacent ESM2 task screen, exact depth check, weighted macro-F1 follow-up은 전반적 LT 주장을 지지하지 않았다.
- 현재 가장 안전한 결론은 LT가 BioML 전체용 방법이 아니라, recurrent global refinement가 실제로 필요한 task에 맞는 제한적 task-fit method라는 점이다.

## 평가 질문

이 screen의 출발점은 `looped 1-layer r=3`이 static 3-layer 대비 적은 파라미터로 비슷하거나 더 나은 성능을 낼 수 있는지였다. 하지만 결과를 본 뒤의 질문은 조금 바뀌었다. 중요한 것은 "BioML인가?"가 아니라, label을 맞히는 데 반복적인 전역 표현 갱신이 실제 병목인지였다.

따라서 이 글은 LT가 생물학 데이터에서 일반적으로 좋은지를 주장하지 않는다. 같은 평가 조건에서 LT가 static control을 넘는 task가 있는지, 그 이득이 warmup, pass aggregation, training budget과 분리되는지, 그리고 어떤 task에서는 이 구조가 맞지 않는지를 확인한다.

## 평가 설계

평가는 서로 다른 역할의 근거를 하나로 모은다. remote homology는 중심 양성 사례이고, adjacent ESM2 task screen은 그 신호가 주변 sequence classification task로 옮겨가는지 보는 점검이다. exact depth check는 "1-layer loop `r=3`이 static 3-layer를 대체한다"는 단순 가설을 보는 진단용 ablation이다. weighted macro-F1 follow-up은 long-tail class imbalance가 LT 실패의 주원인인지 확인한다.

중요한 제한은 각 결과의 목적이 다르다는 점이다. 일부 screen은 최종 판정용이 아니라 다음 실험 후보를 거르기 위한 신호이고, static longer-training 결과는 같은 protocol을 모두 맞춘 definitive control이 아니라 강한 stress baseline이다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <colgroup>
        <col style="width: 17%;">
        <col style="width: 19%;">
        <col style="width: 22%;">
        <col style="width: 10%;">
        <col style="width: 32%;">
      </colgroup>
      <thead>
        <tr>
          <th>Evidence block</th>
          <th>역할</th>
          <th>비교</th>
          <th class="align-right">Seeds</th>
          <th>공개 해석의 제한</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Remote homology</td>
          <td>중심 양성 사례</td>
          <td>ESM2-8M static vs LT variants</td>
          <td class="align-right">3</td>
          <td>matched-data-exposure 양성 신호이며, compute/warmup-fair 양성 신호는 아니다.</td>
        </tr>
        <tr>
          <td>Adjacent ESM2 screen</td>
          <td>전이 가능성 점검</td>
          <td>여러 sequence task의 static vs LT slice</td>
          <td class="align-right">1-3/task</td>
          <td>task별 seed와 budget이 균일하지 않아 최종 채택보다 후속 관찰/중단 판단에 가깝다.</td>
        </tr>
        <tr>
          <td>Exact depth check</td>
          <td>단순 depth replacement 점검</td>
          <td><code>static_3l</code> vs <code>lt_1l_r3</code></td>
          <td class="align-right">1</td>
          <td>bounded decoder 진단이다. 모든 LM continuation recipe를 부정하지는 않는다.</td>
        </tr>
        <tr>
          <td>Weighted macro-F1</td>
          <td>long-tail 설명 점검</td>
          <td>weighted static vs weighted LT</td>
          <td class="align-right">3</td>
          <td>class imbalance만으로 LT의 약한 결과를 설명할 수 있는지 보는 follow-up이다.</td>
        </tr>
        <tr>
          <td>Static longer stress</td>
          <td>fairness caveat</td>
          <td>longer-trained static vs best LT recipe</td>
          <td class="align-right">3</td>
          <td>강한 stress baseline이다. 이 결과가 LT의 efficiency 주장을 크게 제한한다.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> 평가 블록별 비교 조건이다. 이 표는 서로 다른 결과를 단일 평균으로 합치기보다, 각 결과가 어떤 주장 범위를 지지하거나 제한하는지 구분하기 위한 읽기 틀이다.</figcaption>
</figure>

## 핵심 결과

가장 강한 양성 결과는 remote homology에서 나왔다. ESM2-8M 기반 fold-label classification에서 pass aggregation과 recurrent MLM warmup을 포함한 LT recipe는 matched-data-exposure static보다 accuracy가 높았다. 하지만 이 비교는 static warmup, static layer aggregation, longer training까지 맞춘 효율성 비교가 아니다.

반대로 adjacent ESM2 task screen, exact depth check, weighted macro-F1 follow-up은 전반적 주장을 약하게 만들었다. SignalP와 solubility는 관찰을 이어갈 만한 신호로 남았지만, seed consistency나 macro-F1 방향이 충분히 안정적이지 않았다. DeepLoc, SCOPe slice, Pfam, exact depth check, weighted macro-F1 결과는 LT를 BioML 전반의 일반 개선법으로 올리기 어렵게 만든다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <colgroup>
        <col style="width: 22%;">
        <col style="width: 32%;">
        <col style="width: 25%;">
        <col style="width: 21%;">
      </colgroup>
      <thead>
        <tr>
          <th>Evidence</th>
          <th>Main observation</th>
          <th>Safe interpretation</th>
          <th>지지하지 않는 주장</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Remote homology</td>
          <td><code>lt_mlm2_warmup_learned</code> Acc <code>0.37185</code> vs static <code>0.35592</code>; macro-F1 delta <code>+0.00547</code></td>
          <td>global fold-level classification에서는 LT가 제한적으로 도움을 줄 수 있다.</td>
          <td>BioML 전반 양성 신호</td>
        </tr>
        <tr>
          <td>Static longer stress</td>
          <td>static longer Acc <code>0.52592</code>, macro-F1 <code>0.21621</code></td>
          <td>현재 LT 결과는 compute/warmup-fair efficiency 주장이 아니다.</td>
          <td>LT compute-efficiency win</td>
        </tr>
        <tr>
          <td>Adjacent ESM2 screen</td>
          <td>SignalP/solubility는 약한 후속 관찰 신호, DeepLoc/SCOPe/Pfam은 중단 판단 쪽</td>
          <td>remote homology 양성 신호가 주변 sequence task 전반으로 옮겨가지는 않았다.</td>
          <td>sequence BioML 전반 개선</td>
        </tr>
        <tr>
          <td>Exact depth check</td>
          <td><code>static_3l</code> NLL <code>2.88969</code>, <code>lt_1l_r3</code> NLL <code>2.89345</code></td>
          <td>단순한 tied-depth recurrence가 untied static depth를 자동 대체하지 않았다.</td>
          <td><code>1L loop r=3 = 3L static</code></td>
        </tr>
        <tr>
          <td>Weighted macro-F1</td>
          <td>LT macro-F1 delta <code>+0.00007</code>, Acc delta <code>-0.00729</code></td>
          <td>class imbalance만 고쳐서는 LT의 약한 결과가 해결되지 않았다.</td>
          <td>long-tail objective만으로 해결</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> 핵심 결과의 읽기 요약이다. remote homology 양성 신호는 LT task-fit 가능성을 보여주지만, 다른 control들은 BioML 전반 주장과 compute-efficiency 주장을 제한한다.</figcaption>
</figure>

## Remote Homology 예외

Remote homology는 이번 screen에서 LT가 가장 잘 맞은 예외다. 이 task의 label은 단일 local motif보다 fold-level representation에 더 가깝고, sequence 전체의 관계를 압축한 표현이 필요하다. 작은 ESM2 backbone에서는 recurrent refinement와 pass aggregation이 이런 전역 표현을 일부 보완했을 가능성이 있다.

그러나 이 예외를 승리 benchmark로 읽으면 안 된다. 양성 신호는 matched-data-exposure accuracy 기준에서 확인됐고, macro-F1 long-tail 문제와 static longer stress baseline은 남아 있다. 따라서 remote homology는 "BioML 전반 양성 신호"가 아니라, "LT가 맞을 수 있는 task 구조"를 보여주는 진단 사례에 가깝다.

## 안 맞은 조건

다수의 평가/이전 task에서는 local cue, composition, static pretrained representation, 또는 shallow baseline이 강한 신호를 제공했다. 이런 조건에서는 같은 block을 반복하는 recurrence가 새로운 정보를 만들기보다 이미 잡힌 표현을 다시 변환하는 쪽에 가까워질 수 있다.

이 패턴은 RNA MRL의 k-mer ridge, BEACON SSI의 local-window ridge, mutation scoring의 local/readout engineering, adjacent ESM2 task screen의 후속 관찰/중단 판단 결과와 일관된다. 다만 이것은 causal proof가 아니라 현재 관측을 설명하는 가설이다. 공개 주장은 "local cue가 강한 task에서는 LT가 불리할 수 있다" 정도로 제한한다.

static transformer의 untied layer diversity도 강한 기준선이다. static layer는 서로 다른 파라미터를 가지며, pretrained backbone에서는 layer마다 다른 정보를 담을 수 있다. 반면 LT는 같은 block을 반복한다. recurrence는 effective depth를 늘리지만, 서로 다른 layer가 가진 function diversity를 자동으로 복제하지는 않는다.

## Pass Aggregation과 Warmup

remote homology 양성 신호에서 pass aggregation과 recurrent warmup은 LT를 살리는 recipe로 보인다. 마지막 pass 하나보다 여러 pass의 trajectory를 함께 읽을 때 결과가 좋아졌다면, 정보가 recurrent states에 분산되어 있을 가능성이 있다.

하지만 이 관찰은 동시에 공정성 문제를 만든다. LT가 pass aggregation과 recurrent MLM warmup을 받는다면, static도 layer aggregation, learned layer mixing, static warmup, longer training control을 받을 수 있어야 한다. 이 control이 없으면 LT architecture의 이득과 training support의 이득을 분리할 수 없다.

이 점 때문에 현재 remote homology result는 "LT가 될 수 있는 조건"을 보여주지만, "LT가 compute-efficient하게 static을 이겼다"는 결론으로 올라가지는 않는다.

## Class Imbalance 점검

Remote homology에는 class imbalance와 long-tail 문제가 있다. 그래서 weighted macro-F1 objective를 적용하면 LT가 더 좋아질 수 있다는 가설이 있었다. 그러나 weighted follow-up에서는 LT의 macro-F1 이득이 사실상 묶였고, accuracy는 static보다 낮았다.

이 결과는 class imbalance가 문제의 일부일 수는 있어도 충분한 설명은 아님을 보여준다. objective를 바꿔도 tied recurrence, static representation의 강함, task signal 구조의 mismatch가 남는다.

## 주장 범위

현재 결과는 주장 범위를 세 단계까지만 허용한다. remote homology 양성 신호, pass aggregation/warmup의 중요성, 전반적 개선 주장 부정까지는 말할 수 있다. compute/warmup-fair efficiency win이나 BioML 전체 부정은 아직 말할 수 없다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <colgroup>
        <col style="width: 16%;">
        <col style="width: 56%;">
        <col style="width: 28%;">
      </colgroup>
      <thead>
        <tr>
          <th>단계</th>
          <th>주장</th>
          <th>현재 가능 여부</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Level 1</td>
          <td>LT는 remote homology에서 matched-data-exposure static보다 약간 좋다.</td>
          <td>가능</td>
        </tr>
        <tr>
          <td>Level 2</td>
          <td>현재 best LT recipe에서는 pass aggregation과 recurrent warmup이 중요하다.</td>
          <td>가능</td>
        </tr>
        <tr>
          <td>Level 3</td>
          <td>이번 평가 task 기준에서 LT는 전반적 개선법이 아니다.</td>
          <td>가능</td>
        </tr>
        <tr>
          <td>Level 4</td>
          <td>LT는 compute/warmup-fair하게 static보다 효율적이다.</td>
          <td>불가</td>
        </tr>
        <tr>
          <td>Level 5</td>
          <td>LT는 BioML 전반에 맞지 않는다.</td>
          <td>불가</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> 현재 결과로 가능한 주장과 불가능한 주장을 분리한 요약이다. 이 글의 결론은 Level 1-3에 머문다.</figcaption>
</figure>

## 해석

가장 안정적으로 남는 결론은 단순하다. LT는 생물학 데이터라는 도메인 이름에 맞는 방법이 아니라, 반복적인 전역 표현 갱신이 실제로 필요한 task 구조에 맞는 방법이다.

이 관점에서는 remote homology 양성 신호와 다수의 음성/약한 양성 근거가 충돌하지 않는다. remote homology는 matched-data-exposure accuracy 기준의 예외이고, local cue나 static layer diversity가 강한 task에서는 LT의 inductive bias가 중립적이거나 불리하게 작동할 수 있다.

따라서 다음 task를 고를 때는 "BioML인가?"보다 아래 질문이 먼저다.

- label이 local cue로 많이 설명되는가, global relation으로 설명되는가?
- cheap baseline이 이미 강한가?
- static layer aggregation이나 frozen embedding baseline이 강한가?
- recurrence를 늘렸을 때 validation에서 안정적인 optimum이 생기는가?
- 마지막 pass만이 아니라 pass trajectory 전체가 정보를 갖는가?

## 한계

이 결론은 현재 평가 task와 tested recipe 안에서만 유효하다. task별 seed 수와 budget이 균일하지 않고, 일부 screen은 최종 채택보다 후속 관찰/중단 판단에 가깝다. exact depth check도 bounded diagnostic이므로 모든 decoder 또는 continuation recipe를 부정하지 않는다.

가장 큰 남은 control은 static warmup, static layer aggregation, compute-accounted longer training이다. 이 control을 통과하기 전에는 LT를 compute-efficient 방법으로 주장할 수 없다. 반대로 LT 구조 전체를 부정하는 결론도 현재 결과로는 과하다.

## 다음 확인

후속 실험은 새 task를 무작정 늘리는 것보다, 현재 양성 신호가 어떤 control을 견디는지 확인하는 쪽이 우선이다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <colgroup>
        <col style="width: 12%;">
        <col style="width: 34%;">
        <col style="width: 30%;">
        <col style="width: 24%;">
      </colgroup>
      <thead>
        <tr>
          <th class="align-right">우선순위</th>
          <th>확인할 비교</th>
          <th>목적</th>
          <th>해석</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="align-right">1</td>
          <td>static MLM warmup + static layer aggregation</td>
          <td>LT warmup/aggregation 이득과 architecture 이득 분리</td>
          <td>static이 따라오면 LT 주장 범위는 더 좁아진다.</td>
        </tr>
        <tr>
          <td class="align-right">2</td>
          <td>compute/data-accounted static longer vs LT</td>
          <td>efficiency 주장 검증</td>
          <td>static이 계속 이기면 LT는 진단용 방법으로 제한된다.</td>
        </tr>
        <tr>
          <td class="align-right">3</td>
          <td>remote homology pass/readout 진단</td>
          <td>pass trajectory가 실제 정보를 갖는지 확인</td>
          <td>pass별 feature가 다르면 aggregation 해석이 강해진다.</td>
        </tr>
        <tr>
          <td class="align-right">4</td>
          <td>후속 관찰 task의 cheap/local baseline gate</td>
          <td>SignalP/solubility가 LT-worthy인지 확인</td>
          <td>cheap baseline이 강하면 architecture 주장이 흐려진다.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> 후속 확인의 우선순위다. 현재 가장 큰 불확실성은 새 task 부족보다, remote homology 양성 신호가 static warmup과 aggregation control을 견디는지다.</figcaption>
</figure>

## Appendix: 세부 수치

<details>
  <summary>Adjacent ESM2 task screen</summary>
  <div class="details-content">
    <figure class="table-figure table-figure--metrics">
      <div class="table-shell">
        <table class="metrics-table metrics-table--numeric-columns">
          <thead>
            <tr>
              <th>Task</th>
              <th class="align-right">Seeds</th>
              <th class="align-right">Mean Acc delta</th>
              <th class="align-right">Win count</th>
              <th class="align-right">Win rate</th>
              <th class="align-right">Mean macro-F1 delta</th>
              <th>판정</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>solubility</td>
              <td class="align-right"><code>3</code></td>
              <td class="align-right"><code>+0.02734</code></td>
              <td class="align-right"><code>1/3</code></td>
              <td class="align-right"><code>0.33</code></td>
              <td class="align-right"><code>+0.02148</code></td>
              <td>후속 관찰</td>
            </tr>
            <tr>
              <td>signalp</td>
              <td class="align-right"><code>2</code></td>
              <td class="align-right"><code>+0.00586</code></td>
              <td class="align-right"><code>2/2</code></td>
              <td class="align-right"><code>1.00</code></td>
              <td class="align-right"><code>-0.01209</code></td>
              <td>후속 관찰</td>
            </tr>
            <tr>
              <td>deeploc</td>
              <td class="align-right"><code>2</code></td>
              <td class="align-right"><code>-0.00293</code></td>
              <td class="align-right"><code>1/2</code></td>
              <td class="align-right"><code>0.50</code></td>
              <td class="align-right"><code>-0.01325</code></td>
              <td>중단 판단</td>
            </tr>
            <tr>
              <td>scope_fold</td>
              <td class="align-right"><code>1</code></td>
              <td class="align-right"><code>+0.00000</code></td>
              <td class="align-right"><code>0/1</code></td>
              <td class="align-right"><code>0.00</code></td>
              <td class="align-right"><code>-0.00001</code></td>
              <td>중단 판단</td>
            </tr>
            <tr>
              <td>pfam_family</td>
              <td class="align-right"><code>1</code></td>
              <td class="align-right"><code>-0.16211</code></td>
              <td class="align-right"><code>0/1</code></td>
              <td class="align-right"><code>0.00</code></td>
              <td class="align-right"><code>-0.17204</code></td>
              <td>중단 판단</td>
            </tr>
          </tbody>
        </table>
      </div>
      <figcaption><strong>Appendix Table 1.</strong> adjacent ESM2 task screen의 세부 수치다. Solubility는 평균 delta가 양수지만 seed consistency가 약했고, SignalP는 accuracy win이 일관적이지만 macro-F1이 내려갔다. 두 조건은 최종 양성 신호가 아니라 후속 관찰 대상으로 둔다.</figcaption>
    </figure>
  </div>
</details>

<details>
  <summary>Remote homology LT recipe</summary>
  <div class="details-content">
    <figure class="table-figure table-figure--metrics">
      <div class="table-shell">
        <table class="metrics-table metrics-table--numeric-columns">
          <thead>
            <tr>
              <th>Condition</th>
              <th class="align-right">Acc mean</th>
              <th class="align-right">Acc std</th>
              <th class="align-right">Acc delta</th>
              <th class="align-right">Macro-F1 delta</th>
              <th class="align-right">Selected r</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>static</td>
              <td class="align-right"><code>0.35592</code></td>
              <td class="align-right"><code>0.01146</code></td>
              <td class="align-right"><code>0.00000</code></td>
              <td class="align-right"><code>0.00000</code></td>
              <td class="align-right">-</td>
            </tr>
            <tr>
              <td><code>lt_tied_last</code></td>
              <td class="align-right"><code>0.35853</code></td>
              <td class="align-right"><code>0.00941</code></td>
              <td class="align-right"><code>+0.00260</code></td>
              <td class="align-right"><code>-0.00391</code></td>
              <td class="align-right"><code>2</code></td>
            </tr>
            <tr>
              <td><code>lt_tied_mean</code></td>
              <td class="align-right"><code>0.36654</code></td>
              <td class="align-right"><code>0.01048</code></td>
              <td class="align-right"><code>+0.01062</code></td>
              <td class="align-right"><code>-0.00128</code></td>
              <td class="align-right"><code>2</code></td>
            </tr>
            <tr>
              <td><code>lt_mlm2_warmup_learned</code></td>
              <td class="align-right"><code>0.37185</code></td>
              <td class="align-right"><code>0.01796</code></td>
              <td class="align-right"><code>+0.01593</code></td>
              <td class="align-right"><code>+0.00547</code></td>
              <td class="align-right"><code>2</code></td>
            </tr>
          </tbody>
        </table>
      </div>
      <figcaption><strong>Appendix Table 2.</strong> remote homology LT recipe의 세부 수치다. last-pass-only보다 pass aggregation과 recurrent warmup이 중요했을 가능성을 보여주지만, 동시에 static layer aggregation과 static warmup control이 필요하다는 caveat도 만든다.</figcaption>
    </figure>
  </div>
</details>

<details>
  <summary>Exact depth check와 weighted macro-F1 follow-up</summary>
  <div class="details-content">
    <figure class="table-figure table-figure--metrics">
      <div class="table-shell">
        <table class="metrics-table metrics-table--numeric-columns">
          <thead>
            <tr>
              <th>Condition</th>
              <th class="align-right">Trainable params</th>
              <th class="align-right">Selected eval-r</th>
              <th class="align-right">Test NLL</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><code>static_3l</code></td>
              <td class="align-right"><code>5,432,448</code></td>
              <td class="align-right"><code>1</code></td>
              <td class="align-right"><code>2.88969</code></td>
            </tr>
            <tr>
              <td><code>static_1l</code></td>
              <td class="align-right"><code>1,883,520</code></td>
              <td class="align-right"><code>1</code></td>
              <td class="align-right"><code>2.88998</code></td>
            </tr>
            <tr>
              <td><code>lt_1l_r3</code></td>
              <td class="align-right"><code>1,883,520</code></td>
              <td class="align-right"><code>3</code></td>
              <td class="align-right"><code>2.89345</code></td>
            </tr>
          </tbody>
        </table>
      </div>
      <figcaption><strong>Appendix Table 3.</strong> exact depth check 결과다. <code>lt_1l_r3</code>이 <code>static_3l</code>을 넘지 못했으므로 단순한 tied-depth replacement 주장은 제한된다.</figcaption>
    </figure>

    <figure class="table-figure table-figure--metrics">
      <div class="table-shell">
        <table class="metrics-table metrics-table--numeric-columns">
          <thead>
            <tr>
              <th>Condition</th>
              <th class="align-right">Seeds</th>
              <th class="align-right">Test Acc mean</th>
              <th class="align-right">Test macro-F1 mean</th>
              <th class="align-right">Selected r</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><code>lt_mlm2_warmup_learned_weighted_sqrt_macro</code></td>
              <td class="align-right"><code>3</code></td>
              <td class="align-right"><code>0.27139</code></td>
              <td class="align-right"><code>0.03976</code></td>
              <td class="align-right"><code>3</code></td>
            </tr>
            <tr>
              <td><code>static_weighted_sqrt_macro</code></td>
              <td class="align-right"><code>3</code></td>
              <td class="align-right"><code>0.27868</code></td>
              <td class="align-right"><code>0.03969</code></td>
              <td class="align-right">-</td>
            </tr>
          </tbody>
        </table>
      </div>
      <figcaption><strong>Appendix Table 4.</strong> weighted macro-F1 follow-up이다. LT의 macro-F1 delta는 <code>+0.00007</code>에 그쳤고, accuracy는 <code>-0.00729</code> 낮았다.</figcaption>
    </figure>
  </div>
</details>

<details>
  <summary>이전 음성/약한 양성 근거</summary>
  <div class="details-content">
    <figure class="table-figure table-figure--comparison">
      <div class="table-shell">
        <table class="comparison-table">
          <colgroup>
            <col style="width: 25%;">
            <col style="width: 41%;">
            <col style="width: 34%;">
          </colgroup>
          <thead>
            <tr>
              <th>이전 slice</th>
              <th>핵심 관찰</th>
              <th>이 글에서의 역할</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>RNA MRL tiny LT</td>
              <td>k-mer ridge가 Spearman <code>0.77079</code>로 강했고, LT core2는 <code>0.47935</code>에 머물렀다.</td>
              <td>cheap/local baseline이 강하면 LT architecture 주장이 흐려질 수 있다.</td>
            </tr>
            <tr>
              <td>RNA BEACON SSI</td>
              <td>cheap local-window ridge test R2 <code>0.28217</code>, neural variants는 크게 낮았다.</td>
              <td>local-window baseline gate가 중요하다.</td>
            </tr>
            <tr>
              <td>ESM2 mutation scoring LT</td>
              <td>recurrence보다 z-score/local-window readout engineering이 더 큰 신호였다.</td>
              <td>mutation scoring은 global recurrence와 병목이 어긋날 수 있다.</td>
            </tr>
            <tr>
              <td>ESM2 contact / PPI pilot</td>
              <td>LT 내부 eval-r scaling은 있었지만 static 8M을 넘지 못했다.</td>
              <td>LT 내부 scaling과 static 대비 개선 판단은 다르다.</td>
            </tr>
            <tr>
              <td>Protein decoder continuation</td>
              <td>일부 continuation 조건에서는 LT가 static/same-param보다 좋았지만 same-FLOPs보다는 뒤였다.</td>
              <td>LT는 전면 실패가 아니라 좁은 양성 축을 가질 수 있다.</td>
            </tr>
          </tbody>
        </table>
      </div>
      <figcaption><strong>Appendix Table 5.</strong> 이전 음성/약한 양성 근거 요약이다. 이 표는 직접 합산하는 meta-analysis가 아니라, 반복해서 나타난 failure mode를 설명하는 보조 근거로만 사용한다.</figcaption>
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

## Experiment Resources

<div class="reference-list" markdown="1">

- Project-level result notes and canonical result tables are tracked under `lab_path: "experiment-lab/projects/bio-lt-task-screen-stage0"`.
- The main evidence blocks are remote homology, adjacent ESM2 task screen, exact depth check, weighted macro-F1 follow-up, and static longer-training stress baseline.
- Earlier boundary cases are used as qualitative support for recurring failure modes, not as a pooled meta-analysis.

</div>

## Citation

이 글을 인용할 때는 아래 형식을 사용할 수 있다.

```text
Ilho Ahn, "Looped Transformer는 어디서 안 맞는가: BioML task screen에서 드러난 narrow task fit", Mini Research, May 5, 2026.
```

또는 BibTeX 형식으로는 다음처럼 적을 수 있다.

```bibtex
@article{ahn2026loopedtransformerbiomltaskfit,
  author = {Ilho Ahn},
  title = {Looped Transformer는 어디서 안 맞는가: BioML task screen에서 드러난 narrow task fit},
  journal = {Mini Research},
  year = {2026},
  month = may,
  url = {https://muted-color.github.io/research/2026/05/05/looped-transformer-bioml-task-fit/}
}
```
