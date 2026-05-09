---
title: "DPO로 본 단백질 변이 reranking의 preference learning 신호"
date: 2026-05-03 10:08:36 +0900
last_modified_at: 2026-05-07 09:48:37 +0900
hidden: true
published: false
publication_status: "unpublished"
hide_reason: "현재 결과만으로 preference learning의 protein variant reranking 적용성을 일반화하기는 어렵다. 다만 일반화 주장 없이 이 케이스에 한정한 실험 노트로 정리해 발행할 가능성은 남긴다."
categories: ["PROTEIN ML"]
tags: [protein, proteingym, dms, dpo, preference-learning, reranking, protein-language-model, lora]
lab_path: "experiment-lab/projects/proteingym-dms-dpo"
excerpt: "ProteinGym DMS 후보 변이 reranking에서 DPO delta로 preference learning 신호가 남는 조건과 position baseline에 묻히는 조건을 분리한다."
description: "ProteinGym DMS 후보 변이 reranking에서 preference learning 신호를 DPO delta로 측정하고, general fitness predictor가 아니라 reference-relative reranker로 남는 조건을 SQSTM, IF1, BLAT, KCNE1, MBD11, RASK binding 사례로 정리한 실험 노트."
permalink: /research/2026/05/03/proteingym-dms-dpo-reranking/
image: /assets/images/posts/proteingym-dms-dpo-reranking/social-thumbnail.png
image_alt: "ProteinGym DMS 후보 변이 reranking에서 DPO delta, position baseline, fixed hybrid를 비교한 소셜 썸네일"
hero_image: /assets/images/posts/proteingym-dms-dpo-reranking/hero-dpo-context.svg
hero_alt: "Same-position ProteinGym DMS reranking 조건에서 DPO delta와 Position baseline의 top-25 hit rate를 막대로 비교하고 Random과 Fixed hybrid를 marker로 표시한 차트"
hero_caption: "<strong>Figure 1.</strong> same-position 및 fixed hybrid 점검에서 DPO delta, Position baseline, Fixed hybrid의 top-25 hit rate를 같은 축에 놓은 요약이다. 진한 보라 막대는 DPO delta, 해치 보라 막대는 position baseline, 하늘색 막대는 fixed hybrid, 회색 세로선은 random을 뜻한다. DPO delta가 random보다 높아도 position baseline보다 낮으면 보완 신호로 제한해 읽고, fixed hybrid가 position baseline을 넘는 조건은 현재 SQSTM으로 좁혀진다."
hero_frame: true
hero_compact: true
math: true
---

Protein engineering에서 다음 후보를 고르는 일은 좋은 sequence를 새로 생성하는 문제만은 아니다. 이미 측정된 DMS(deep mutational scanning) 후보 집합 안에서도 어떤 변이를 먼저 볼지 정렬해야 한다. 이 분석은 ProteinGym DMS substitution 후보를 대상으로, preference learning 신호를 DPO delta로 구체화했을 때 high-fitness variant를 상위권으로 더 잘 올리는지 평가한다 <a class="citation-ref" href="#ref-proteingym" aria-label="Reference 1">[1]</a>.

평가 질문은 **DPO 학습 뒤 reference 대비 log-likelihood 변화량으로 후보를 다시 정렬했을 때, high-fitness 후보의 top-25 hit rate가 random 또는 raw likelihood보다 높아지는지, 그리고 그 이득이 position baseline 대비 보완 신호로도 남는지**다.

비교에서 가장 중요한 기준선은 position baseline이다. 이 기준선은 변이가 어떤 amino acid로 바뀌었는지는 보지 않고, train split에서 mutation position별 평균 fitness만 계산해 eval 후보를 정렬한다. position-level tolerance는 DMS 해석에서 오래전부터 알려진 강한 신호이므로, DPO delta가 random을 넘는지만으로는 충분하지 않다.

DPO delta의 효과는 조건부로 관찰됐다. 일부 assay에서는 random과 raw likelihood보다 high-fitness 후보를 더 위로 올렸지만, 많은 조건에서는 position baseline 자체가 더 강했다. 따라서 이 결과는 "preference learning이 protein fitness를 일반적으로 예측한다"는 주장보다, **DPO delta로 측정한 preference learning 신호가 reference-relative reranker로 작동할 수 있는 조건**을 구분한 결과로 해석한다.

> **DMS**는 deep mutational scanning assay다. 이 분석에서는 이미 측정된 mutant 후보를 새로 생성하지 않고, 후보 집합 안에서 점수로 다시 정렬한다.
>
> **DPO delta**는 final policy likelihood 자체가 아니라, DPO 이후 reference 대비 log-likelihood가 얼마나 움직였는지를 보는 reference-relative score다 <a class="citation-ref" href="#ref-dpo" aria-label="Reference 2">[2]</a>.

{% include model-mention-cards.html label="사용한 주요 리소스" aria_label="사용한 핵심 데이터와 모델 리소스" models="ProteinGym v1 DMS|DMS substitutions|https://huggingface.co/datasets/OATML-Markslab/ProteinGym_v1;ProtGPT2|nferruz/ProtGPT2|https://huggingface.co/nferruz/ProtGPT2" %}

## 요약

- 이 글은 preference learning을 general fitness predictor로 주장하지 않고, DPO delta가 후보 집합 안에서 reranking 신호로 남는 조건을 평가한다.
- DPO delta는 일부 assay/readout에서 random 또는 raw likelihood보다 높은 top-25 high-fitness hit rate를 보였다.
- 핵심 기준은 position baseline이다. DPO delta가 random을 넘더라도 position baseline보다 낮으면 보완 신호로 제한해 읽는다.
- 가장 안정적인 양성 조건은 SQSTM이다. IF1은 약한 양성, VG08/REV는 global-pair caution, BLAT/KCNE1/MBD11/RASK binding은 음성 또는 평탄한 경계로 남았다.
- 후속 실험은 preference objective, reference policy, pair construction을 바꿔도 position baseline 위에 남는 reranking 신호가 반복되는지 확인하는 방향이 적절하다.

## 문제 설정

평가 범위는 preference learning의 일반적인 fitness 예측력이 아니라, **reference policy 대비 선호 이동이 high-fitness 후보를 같은 candidate set 안에서 더 위로 올리는지**로 제한한다. 이 글에서는 그 신호를 DPO delta로 측정한다. 따라서 평가 설계도 생성 성능이나 raw likelihood 개선보다, 같은 후보 집합 안의 reranking과 position baseline 대비 보완 신호에 맞춘다.

이 범위는 DPO의 학습 방식과 맞물린다. DPO는 절대적인 DMS score를 회귀하는 모델이 아니라, 같은 맥락에서 `chosen`이 `rejected`보다 더 선호되도록 policy와 reference의 log-ratio를 움직이는 pairwise preference 학습이다. 따라서 분석의 기본 단위도 절대 fitness 예측이 아니라, 고정된 후보 집합 안에서 reference 대비 선호 이동이 순서를 바꾸는지에 둔다.

DPO delta가 유효할 가능성이 있는 task는 고정된 후보 집합을 다시 정렬하는 문제다. position 평균만으로 high-fitness bin이 거의 설명되는 assay에서는 DPO delta가 추가할 여지가 작다. 반대로 같은 position 안에서도 chosen/rejected 방향이 유지되고, 특정 residue 또는 readout preference가 reference 대비 변화량으로 남는 assay라면 DPO delta를 보완 score로 쓸 가능성이 있다.

## 평가 설계

평가 대상은 ProteinGym DMS substitution benchmark의 mutant candidate다. 실험에는 Hugging Face의 `OATML-Markslab/ProteinGym_v1` 중 `DMS_substitutions` split에서 뽑은 assay를 사용했다. 각 assay 안에서 DMS score가 높은 변이를 `chosen`, 낮은 변이를 `rejected`로 두고 preference pair를 만들었다. 기본 모델은 ProtGPT2 계열 causal protein language model이며, 학습은 LoRA adapter로 수행했다 <a class="citation-ref" href="#ref-protgpt2" aria-label="Reference 3">[3]</a><a class="citation-ref" href="#ref-lora" aria-label="Reference 4">[4]</a>. 비교한 recipe는 `base`, `SFT`, `base -> DPO`, `SFT -> DPO`다.

중심 score는 final policy의 raw likelihood가 아니다.

$$
s_{\mathrm{DPO}}(x)
= \log p_{\pi_{\theta}}(x)
- \log p_{\pi_{\mathrm{ref}}}(x)
$$

이 값은 sequence 자체가 얼마나 자연스럽게 보이는지를 재는 점수가 아니다. DPO 이후 reference model 대비 해당 sequence의 선호도가 얼마나 증가했는지를 나타낸다.

Final policy likelihood만 쓰면 DPO 학습 전부터 reference model이 갖고 있던 protein language model prior가 그대로 섞인다. 그러면 높은 likelihood가 원래 자연스러운 sequence 때문인지, DPO가 high-fitness preference 방향으로 올렸기 때문인지 분리하기 어렵다. 같은 sequence에 대해 policy와 reference의 log-likelihood 차이를 보면, DPO 학습으로 새로 생긴 선호 이동만 분리할 수 있다.

본문에서는 reranking용 operational score로 log-likelihood 차이만 사용했다. DPO 논문의 implicit reward에는 양의 scale factor가 붙지만, 고정된 양의 scale은 ranking을 바꾸지 않는다. 수치는 full sequence의 summed log-likelihood 차이인 `delta_sum_logprob`를 기준으로 하며, 같은 assay의 substitution 후보는 길이가 같아 length normalization이 메인 순위를 바꾸는 요인이 되지 않았다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <colgroup>
        <col style="width: 28%;">
        <col style="width: 36%;">
        <col style="width: 36%;">
      </colgroup>
      <thead>
        <tr>
          <th>항목</th>
          <th>설정</th>
          <th>해석</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>평가 과제</td>
          <td>ProteinGym DMS 후보 변이 reranking</td>
          <td>이미 측정된 후보를 점수로 다시 정렬한다.</td>
        </tr>
        <tr>
          <td>Preference pair</td>
          <td>같은 assay 안의 high-fitness mutant를 <code>chosen</code>, low-fitness mutant를 <code>rejected</code>로 구성</td>
          <td>pair 방향이 평가 landscape에서도 유지되는지 확인한다.</td>
        </tr>
        <tr>
          <td>Primary score</td>
          <td>$\log p_{\pi_\theta}(x)-\log p_{\pi_{\mathrm{ref}}}(x)$</td>
          <td>raw likelihood가 아니라 reference 대비 선호 변화량을 사용한다.</td>
        </tr>
        <tr>
          <td>Primary metric</td>
          <td>top-25 high-fitness hit rate</td>
          <td>상위 25개 후보 중 high-fitness bin 비율이다.</td>
        </tr>
        <tr>
          <td>주요 baseline</td>
          <td>random, raw likelihood, position baseline</td>
          <td>random을 넘는지와 position effect를 넘는지를 분리한다.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> 이 글의 평가 범위다. 생성 성능이나 raw likelihood 개선을 주장하지 않고, ProteinGym DMS 후보 집합 안에서 reference 대비 변화량이 high-fitness 후보를 상위권에 올리는지 확인한다.</figcaption>
</figure>

### 평가 조건

아래 세부는 공개 독자가 결론을 따라가기 위해 필요한 실험 조건만 압축한 것이다. 여러 assay에서 recipe를 비교했기 때문에, Figure 2의 `best recipe`는 사전 고정된 단일 recipe의 일반 성능이 아니라 선별 조건에서 해석에 필요한 recipe를 모은 요약으로 읽어야 한다. Appendix Table 1의 global/best recipe 수치와 Table 5의 same-position ablation 수치는 서로 다른 비교 단위다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <colgroup>
        <col style="width: 24%;">
        <col style="width: 38%;">
        <col style="width: 38%;">
      </colgroup>
      <thead>
        <tr>
          <th>항목</th>
          <th>원본 실험 설정</th>
          <th>해석상 의미</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>데이터 범위</td>
          <td><code>ProteinGym_v1/DMS_substitutions</code>에서 선택한 assay/readout</td>
          <td>indel이나 free generation이 아니라 측정된 substitution 후보 reranking이다.</td>
        </tr>
        <tr>
          <td>Pair 구성</td>
          <td>기본은 assay 안의 q75/q25 high/low pair, 최대 5000 train pair</td>
          <td>chosen/rejected 방향이 held-out ranking으로 일반화되는지 평가한다.</td>
        </tr>
        <tr>
          <td>Same-position</td>
          <td>같은 mutation position 안에서 q75/q25 pair를 다시 구성</td>
          <td>global pair가 position shortcut을 탄 것인지 분리한다.</td>
        </tr>
        <tr>
          <td>High-fitness bin</td>
          <td>eval 후보의 상위 25% DMS score bin</td>
          <td>top-25 hit rate는 상위 25개 후보 중 이 bin에 들어간 비율이다.</td>
        </tr>
        <tr>
          <td>Seed와 tie 처리</td>
          <td>주요 DPO 수치는 3 seed 평균, tie-aware p05/p50은 동점 후보의 순서를 작게 흔들어 반복 계산</td>
          <td>동점 후보가 top-k 경계에서 잘릴 때 결론이 얼마나 흔들리는지 확인한다.</td>
        </tr>
        <tr>
          <td>Mutation budget</td>
          <td>SQSTM, IF1, VG08, REV, ENVZ, RASK abundance, Q53Z42 binding eval 후보는 모두 single mutant</td>
          <td>현재 핵심 분석에서는 same-mutation-budget 재학습이 새 정보를 거의 주지 않는다.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> 평가 프로토콜의 공개용 요약이다. pair design, high-fitness bin, tie-aware 처리, mutation budget을 고정해야 DPO delta와 position baseline의 차이를 과장하지 않고 읽을 수 있다.</figcaption>
</figure>

## 결과

결과는 다섯 층으로 나눠 읽는다. 먼저 DPO delta가 random보다 나은 조건을 확인하고, 그다음 position baseline 위에 남는지 분리한다. 이후 global pair에서 보인 양성 신호가 same-position pair에서도 유지되는지, preference 방향과 readout 변화에 민감한지 점검한다.

### Random 개선과 position 기준 분리

가장 먼저 분리해야 할 것은 `random 기준을 넘었는지`와 `position baseline까지 넘었는지`다. DPO delta는 여러 assay에서 random보다 높았지만, mutation position별 평균 fitness만 쓰는 단순 baseline이 더 강한 경우도 많았다. 이 baseline 자체가 이미 강하기 때문에, 본문에서는 random 대비 개선보다 position baseline 대비 해석을 더 엄격한 기준으로 둔다. Figure 2는 선별 조건의 assay/setting별 best recipe를 random, raw likelihood, DPO delta, position baseline과 함께 놓는다. 이 그림은 단일 recipe의 평균 성능을 주장하기보다, 이후에 자세히 볼 조건을 압축해 보여준다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/proteingym-dms-dpo-reranking/best-recipe-top25.svg" alt="선별된 ProteinGym DMS 조건에서 Random, Raw likelihood, DPO delta, Position baseline의 top-25 high-fitness hit rate를 점으로 비교한 그림">
  <figcaption><strong>Figure 2.</strong> 선별 조건의 assay/setting별 best DPO recipe를 Random, Raw likelihood, Position baseline과 함께 비교한 요약이다. 각 점은 top-25 high-fitness hit rate이며, DPO delta가 random 또는 raw likelihood보다 높아도 position baseline보다 낮은 조건은 보완 신호로만 읽는다.</figcaption>
</figure>

이 비교는 DPO delta를 쓰는 이유를 실험적으로도 확인해 준다. IF1에서는 raw likelihood top-25가 `0.280`인 반면 `base -> DPO` delta는 `0.493`까지 올라갔고, SQSTM에서는 raw likelihood `0.360` 대비 `SFT -> DPO` delta가 `0.627`이었다. VG08도 raw likelihood는 `0.240`에 머물렀지만 `SFT -> DPO` delta는 `0.467`까지 올라갔다. 즉 DPO가 유용하게 작동한 조건에서는 final/reference model이 원래 높게 보던 sequence를 그대로 고른 것이 아니라, DPO 학습 뒤 reference 대비 likelihood가 움직인 방향이 high-fitness 후보와 더 잘 맞았다.

반대로 MBD11처럼 raw likelihood 자체가 `0.427-0.440`으로 비교적 높고 position baseline이 `0.920`으로 강한 조건에서는 delta top-25가 `0.280-0.307`에 그쳤다. 이 경우 차감값을 쓰더라도 DPO가 position-level tolerance 위에 충분한 추가 신호를 만들지 못했다. 따라서 raw likelihood와 DPO delta를 함께 놓는 비교는 단순한 score 선택 문제가 아니라, DPO 학습으로 새로 생긴 preference shift가 실제 평가 landscape와 맞았는지 확인하는 진단이다.

Table 3은 결과를 다섯 층으로 압축한다. 여기서 `random 대비 양성`은 top-25 hit-rate가 random보다 높다는 뜻이고, position 보완 여부는 position baseline 또는 fixed hybrid 비교로 따로 판단한다. 이 구분 때문에 IF1, VG08, REV처럼 random 기준에서는 좋아 보이는 조건도 SQSTM과 같은 결론 단위로 묶지 않는다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <colgroup>
        <col style="width: 22%;">
        <col style="width: 30%;">
        <col style="width: 48%;">
      </colgroup>
      <thead>
        <tr>
          <th>관찰</th>
          <th>조건</th>
          <th>해석</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>same-position과 hybrid까지 유지</td>
          <td>SQSTM</td>
          <td>same-position에서 유지되고 label-flip control을 통과했으며, fixed hybrid가 position baseline을 넘었다.</td>
        </tr>
        <tr>
          <td>random 기준 신호</td>
          <td>IF1</td>
          <td>same-position에서도 random보다 높지만, tie-aware 하한과 position baseline에는 밀린다.</td>
        </tr>
        <tr>
          <td>global pair 의존</td>
          <td>VG08, REV</td>
          <td>global pair에서는 양성이지만 same-position pair에서 약해져 position shortcut 가능성을 조심해야 한다.</td>
        </tr>
        <tr>
          <td>random은 넘지만 제한적</td>
          <td>RASK abundance, Q53Z42 binding, ENVZ same-position</td>
          <td>random은 넘지만 position baseline 위의 residue-level 신호로 과장하기 어렵다.</td>
        </tr>
        <tr>
          <td>position baseline 우세</td>
          <td>BLAT, KCNE1, MBD11, RASK binding, VKOR1 abundance</td>
          <td>DPO delta가 약하거나 음수이고, position baseline이 더 강하게 남는다.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> best recipe와 보강 실험을 합쳐 읽은 관찰별 요약이다. 이 표는 단일 순위표가 아니라, random 대비 신호와 position baseline 대비 보완 신호를 분리해 어떤 근거까지 통과했는지 구분하기 위한 읽기 틀이다.</figcaption>
</figure>

### Position baseline 위에 남는 신호

Position baseline은 train split에서 mutation position별 평균 fitness를 계산하고, eval 후보를 그 값으로 정렬한다. train에서 관측되지 않은 position은 이 baseline에서 마지막으로 밀리지만, 본문 핵심 조건들은 train/eval position overlap이 충분한 조건에서 해석했다. 단순한 baseline이지만 DPO 해석에는 중요하다. DPO delta가 random을 넘더라도 position baseline보다 낮으면, 그 신호가 residue substitution preference인지, 오래전부터 알려진 position-level tolerance에 묻힌 것인지 분리하기 어렵다.

Figure 3은 이 차이를 assay/recipe 단위로 보여준다. 대각선 위에 있는 점은 DPO delta가 position baseline보다 높은 조건이고, 아래에 있는 점은 position baseline이 더 강한 조건이다. 라벨이 붙은 진한 점은 본문 해석의 핵심 조건이고, 연한 점은 비교 맥락으로 함께 둔 recipe다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/proteingym-dms-dpo-reranking/delta-vs-position.svg" alt="DPO delta top-25 hit rate를 y축, position baseline top-25 hit rate를 x축에 놓고 assay recipe별 점을 대각선 기준으로 비교한 산점도">
  <figcaption><strong>Figure 3.</strong> DPO delta와 position baseline의 top-25 hit rate를 같은 assay/recipe 단위로 비교한 산점도다. 대각선 위의 점은 DPO delta가 position baseline보다 높고, 아래의 점은 position baseline이 더 높다. 진한 라벨 점은 본문 핵심 조건, 연한 점은 비교 맥락이다. REV_HV1H2는 global pair 기준으로 대각선 위에 있지만, same-position 평가에서는 신호가 약해져 별도로 제한해 해석한다.</figcaption>
</figure>

SQSTM은 여기서 중요한 예외다. DPO delta 단독은 position baseline보다 낮지만, 두 신호를 고정된 방식으로 더하면 position baseline을 넘었다. 따라서 SQSTM의 의미는 DPO가 position baseline을 대체한다는 것이 아니라, position-level 신호 위에 얹을 수 있는 보완 정보가 남았다는 데 있다.

$$
s_{\mathrm{hybrid}}(x)
= z_{\mathcal{C}}\!\left(\mathrm{position\_mean}(x)\right)
+ z_{\mathcal{C}}\!\left(s_{\mathrm{DPO}}(x)\right)
$$

여기서 $\mathcal{C}$는 같은 assay/recipe의 eval candidate set이다. `position_mean`과 `DPO delta`를 각각 eval candidate 안에서 z-score로 표준화한 뒤 같은 가중치로 더했다. eval set에서 alpha를 고른 grid search는 사후 확인으로만 두고, 본문 주장은 fixed hybrid에 한정했다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Assay</th>
          <th>Pair design</th>
          <th class="align-right">Random</th>
          <th class="align-right">Position</th>
          <th class="align-right">DPO delta</th>
          <th class="align-right">Fixed hybrid</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>SQSTM</td>
          <td>same-position</td>
          <td class="align-right">0.255</td>
          <td class="align-right">0.720</td>
          <td class="align-right">0.627</td>
          <td class="align-right">0.813</td>
        </tr>
        <tr>
          <td>SQSTM</td>
          <td>global</td>
          <td class="align-right">0.255</td>
          <td class="align-right">0.720</td>
          <td class="align-right">0.627</td>
          <td class="align-right">0.800</td>
        </tr>
        <tr>
          <td>IF1</td>
          <td>same-position</td>
          <td class="align-right">0.253</td>
          <td class="align-right">0.760</td>
          <td class="align-right">0.427</td>
          <td class="align-right">0.653</td>
        </tr>
        <tr>
          <td>REV_HV1H2</td>
          <td>same-position</td>
          <td class="align-right">0.252</td>
          <td class="align-right">0.160</td>
          <td class="align-right">0.280</td>
          <td class="align-right">0.227</td>
        </tr>
        <tr>
          <td>RASK abundance</td>
          <td>same-position</td>
          <td class="align-right">0.251</td>
          <td class="align-right">0.720</td>
          <td class="align-right">0.347</td>
          <td class="align-right">0.640</td>
        </tr>
        <tr>
          <td>VG08</td>
          <td>same-position</td>
          <td class="align-right">0.255</td>
          <td class="align-right">0.640</td>
          <td class="align-right">0.280</td>
          <td class="align-right">0.493</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> fixed hybrid는 $z_{\mathcal{C}}(\mathrm{position\_mean}) + z_{\mathcal{C}}(s_{\mathrm{DPO}})$로 계산했다. eval set에서 alpha를 고른 post-hoc grid search가 아니라 고정 조합이므로, position baseline 위에 남는 보완 신호를 확인하는 기준으로 읽는다.</figcaption>
</figure>

Table 4에서 결론 단위로 남는 조건은 SQSTM이다. IF1, RASK, VG08은 random 대비 신호가 있어도 fixed hybrid가 position baseline을 안정적으로 넘지 못했고, REV는 position baseline 자체가 약한 예외로 제한해 읽는다.

### Pair 구성과 same-position 점검

Global pair는 assay 전체에서 high-fitness 변이와 low-fitness 변이를 묶는다. 이 경우 DPO가 residue-level preference를 배웠을 수도 있지만, 단순히 좋은 position과 나쁜 position을 구분했을 수도 있다. 그래서 같은 mutation position 안에서만 chosen/rejected를 만드는 same-position pair를 따로 확인했다.

<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Assay</th>
          <th>Recipe</th>
          <th class="align-right">Global / same-position</th>
          <th class="align-right">Same-position lift</th>
          <th class="align-right">Tie p05/p50</th>
          <th>판정</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>SQSTM</td>
          <td><code>SFT -&gt; DPO</code></td>
          <td class="align-right">0.627 / 0.627</td>
          <td class="align-right">+0.371</td>
          <td class="align-right">0.627 / 0.640</td>
          <td>유지</td>
        </tr>
        <tr>
          <td>IF1</td>
          <td><code>base -&gt; DPO</code></td>
          <td class="align-right">0.493 / 0.427</td>
          <td class="align-right">+0.174</td>
          <td class="align-right">0.253 / 0.373</td>
          <td>random 대비 유지, position에는 밀림</td>
        </tr>
        <tr>
          <td>VG08</td>
          <td><code>SFT -&gt; DPO</code></td>
          <td class="align-right">0.467 / 0.280</td>
          <td class="align-right">+0.025</td>
          <td class="align-right">0.147 / 0.267</td>
          <td>same-position에서 약화</td>
        </tr>
        <tr>
          <td>REV_HV1H2</td>
          <td><code>base -&gt; DPO</code></td>
          <td class="align-right">0.360 / 0.280</td>
          <td class="align-right">+0.028</td>
          <td class="align-right">0.227 / 0.280</td>
          <td>global 신호를 과장하면 안 됨</td>
        </tr>
        <tr>
          <td>RASK abundance</td>
          <td><code>base -&gt; DPO</code></td>
          <td class="align-right">0.373 / 0.347</td>
          <td class="align-right">+0.095</td>
          <td class="align-right">0.293 / 0.347</td>
          <td>약한 유지</td>
        </tr>
        <tr>
          <td>Q53Z42 binding</td>
          <td><code>base -&gt; DPO</code></td>
          <td class="align-right">0.400 / 0.347</td>
          <td class="align-right">+0.093</td>
          <td class="align-right">0.173 / 0.293</td>
          <td>random은 넘지만 tie-aware 하한이 낮음</td>
        </tr>
        <tr>
          <td>ENVZ</td>
          <td><code>base -&gt; DPO</code></td>
          <td class="align-right">0.267 / 0.320</td>
          <td class="align-right">+0.070</td>
          <td class="align-right">0.267 / 0.333</td>
          <td>pair design을 바꾸면 약한 개선</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 5.</strong> global pair와 same-position pair의 비교다. <code>Global / same-position</code>은 pair design을 바꾸기 전후의 DPO delta top-25 hit rate이고, <code>Same-position lift</code>는 same-position DPO delta의 random 대비 차이다. tie-aware p05/p50은 동점 후보를 random jitter로 반복 해소했을 때의 top-25 hit-rate 하한과 중앙값이다.</figcaption>
</figure>

Table 5에서는 IF1과 SQSTM의 근거 수준이 분리된다. IF1은 same-position DPO delta가 random보다 높지만, strict tie-aware p05가 random 근처까지 내려가고 hybrid도 position baseline을 넘지 못했다. SQSTM은 same-position 유지, label-flip control, fixed hybrid까지 함께 통과한 조건이다.

### Preference 방향 통제

SQSTM에서는 chosen/rejected 방향을 100% 뒤집은 label-flip control을 수행했다. true preference에서는 top-25 hit rate가 높았지만, label-flip에서는 random 아래로 내려갔다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/proteingym-dms-dpo-reranking/sqstm-label-flip.svg" alt="SQSTM에서 true preference SFT -> DPO와 100퍼센트 label-flip SFT -> DPO의 top-25 hit rate를 random 근사선과 함께 비교한 막대그래프">
  <figcaption><strong>Figure 4.</strong> SQSTM label-flip control이다. true preference 조건의 <code>SFT -&gt; DPO</code>는 top-25 hit rate가 높게 남지만, 100% label-flip 조건은 random 근사선 아래로 내려간다. 작은 error bar는 seed 간 변동을 표시한다. 이 control은 SQSTM에서 관찰된 DPO delta 신호가 preference 방향에 민감하다는 점을 보여준다.</figcaption>
</figure>

RASK abundance에서도 같은 방향의 control이 나왔다. true preference는 top-25 `0.373`이었지만 label-flip은 `0.253`, shuffled-label은 `0.240`이었다. 이 결과는 DPO delta가 preference pair 방향에 민감하다는 점을 확인하는 보조 점검으로 둔다. Table 6의 strict same-position 행은 동점 민감도를 더 보수적으로 보기 위해 p01까지 함께 적었다. ESM2-t6 행은 DPO 학습 recipe가 아니라 같은 후보 집합에서 계산한 zero-shot top-25 high-fitness hit rate다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <colgroup>
        <col style="width: 30%;">
        <col style="width: 34%;">
        <col style="width: 36%;">
      </colgroup>
      <thead>
        <tr>
          <th>점검 항목</th>
          <th>핵심 수치</th>
          <th>해석</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>SQSTM true vs label-flip</td>
          <td>0.627 vs 0.080</td>
          <td>preference 방향을 뒤집으면 신호가 사라짐</td>
        </tr>
        <tr>
          <td>RASK true / label-flip / shuffled</td>
          <td>0.373 / 0.253 / 0.240</td>
          <td>true preference만 random 대비 양성</td>
        </tr>
        <tr>
          <td>SQSTM strict same-position</td>
          <td>DPO 0.627<br><span class="table-note-inline">tie p01/p05/p50 0.613/0.627/0.640</span><br><span class="table-note-inline">hybrid 0.813</span></td>
          <td>tie-aware와 hybrid 기준까지 양성</td>
        </tr>
        <tr>
          <td>IF1 strict same-position</td>
          <td>DPO 0.427<br><span class="table-note-inline">tie p01/p05/p50 0.213/0.253/0.373</span><br><span class="table-note-inline">hybrid 0.653</span></td>
          <td>random 대비 양성이지만 position baseline보다 약함</td>
        </tr>
        <tr>
          <td>ESM2-t6 간단 점검</td>
          <td>SQSTM logp/odds 0.320/0.280<br><span class="table-note-inline">IF1 0.320/0.320</span></td>
          <td>masked mutant amino-acid score 기준의 작은 ESM zero-shot 점검 <a class="citation-ref" href="#ref-esm2" aria-label="Reference 5">[5]</a></td>
        </tr>
        <tr>
          <td>Same-mutation-budget check</td>
          <td>주요 assay 모두 single mutant</td>
          <td>현재 메인 분석에서는 mutation budget 재학습이 새 정보를 거의 주지 않음</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 6.</strong> 통제 실험과 간단 점검의 압축 요약이다. 위쪽 행은 preference 방향과 tie 처리에 대한 검증이고, ESM2-t6 결과는 masked position의 mutant amino-acid log probability와 mutant-vs-wildtype log odds로 계산한 작은 zero-shot baseline 확인용이다. 더 큰 protein LM 비교는 후속 연구로 남는다.</figcaption>
</figure>

### Readout별 경계

같은 단백질이어도 readout이 바뀌면 DPO 효과가 달라질 수 있다. 가장 선명한 예는 RASK다. RASK abundance는 random 대비 양성이었지만, RASK binding-DARPin_K55는 음수였다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <colgroup>
        <col style="width: 30%;">
        <col style="width: 24%;">
        <col style="width: 46%;">
      </colgroup>
      <thead>
        <tr>
          <th>Protein/readout</th>
          <th>DPO lift pattern</th>
          <th>해석</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>RASK<br><span class="table-note-inline">abundance vs binding</span></td>
          <td>positive / negative</td>
          <td>readout-dependent 근거</td>
        </tr>
        <tr>
          <td>VKOR1<br><span class="table-note-inline">activity vs abundance</span></td>
          <td>positive / flat</td>
          <td>activity는 양성이지만 variance 주의, abundance는 평탄</td>
        </tr>
        <tr>
          <td>BLAT<br><span class="table-note-inline">three readouts</span></td>
          <td>negative / flat</td>
          <td>readout끼리 비슷해도 DPO는 음수 또는 평탄</td>
        </tr>
        <tr>
          <td>KCNE1<br><span class="table-note-inline">function vs expression</span></td>
          <td>flat / flat</td>
          <td>둘 다 평탄, position 지배</td>
        </tr>
        <tr>
          <td>Q53Z42<br><span class="table-note-inline">binding vs expression</span></td>
          <td>random positive</td>
          <td>random은 넘지만 position에는 크게 밀림</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 7.</strong> multi-readout 확장의 읽기 요약이다. RASK는 readout-dependent 신호의 핵심 근거지만, BLAT/KCNE1/Q53Z42는 readout 차이가 곧바로 강한 DPO 효과로 이어지지 않음을 보여준다. 정확한 top-25 수치와 position baseline은 Appendix Table 2에 따로 둔다.</figcaption>
</figure>

원본 실험에서는 readout 사이의 mutant overlap과 score similarity도 확인했다. BLAT 세 readout은 overlap이 `4782-4996`개이고 score rho도 `0.603-0.937`이었지만 DPO delta는 음수 또는 평탄했다. KCNE1 function/expression은 overlap이 `2312`개, score rho가 `0.054`였고 둘 다 평탄했다. Q53Z42 binding/expression은 overlap이 `3344`개, score rho가 `0.482`였으며 둘 다 random은 넘지만 position baseline에는 밀렸다.

Readout-dependent 신호는 readout이 바뀌면 항상 한쪽에서 효과가 난다는 주장과 다르다. 현재 결과가 보여주는 범위는 같은 protein family 안에서도 DPO 효과의 크기와 안정성이 달라질 수 있다는 점이다. 그 차이가 곧 position baseline 위의 일반 residue-level fitness 신호를 의미하지는 않는다.

## 해석과 결론

### 작동 조건

현재 결과를 기준으로, DPO delta reranking 신호가 남은 조건은 다섯 가지다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table">
      <thead>
        <tr>
          <th>현재 실험에서 신호가 남은 조건</th>
          <th>신호가 약해진 조건</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>학습 pair의 high/low 방향이 eval landscape에서도 유지된다.</td>
          <td>functional constraint가 복잡해 단순 high/low pair가 일반화되지 않는다.</td>
        </tr>
        <tr>
          <td>base reference와 SFT reference 중 더 맞는 출발점이 assay마다 다를 수 있다.</td>
          <td>SFT -&gt; DPO 또는 base -&gt; DPO를 universal default처럼 둔다.</td>
        </tr>
        <tr>
          <td>raw likelihood만으로는 부족하지만 DPO shift가 추가 정보를 줄 headroom이 있다.</td>
          <td>position baseline이 이미 너무 강해 추가로 얻을 여지가 작다.</td>
        </tr>
        <tr>
          <td>same-position pair에서도 신호가 유지된다.</td>
          <td>global pair 양성 신호가 same-position에서 무너진다.</td>
        </tr>
        <tr>
          <td>position baseline 위에 DPO delta를 얹었을 때 성능이 유지되거나 좋아진다.</td>
          <td>DPO가 random 기준만 넘고 position baseline에는 크게 밀린다.</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 8.</strong> 현재 실험에서 신호가 남은 조건과 약해진 조건이다. 이 표는 일반 적용 가이드가 아니라, 본문 조건에서 어떤 점검 항목이 결론을 갈랐는지 정리한 것이다.</figcaption>
</figure>

이 기준에서 가장 안정적으로 남는 조건은 SQSTM이다. IF1은 같은 조건을 일부 통과하지만 position baseline 위의 보완 신호로는 남지 않았다. VG08과 REV는 global pair에서 나온 양성 신호를 same-position 평가 없이 residue-level 신호로 읽으면 과장된다. BLAT, KCNE1, MBD11, RASK binding처럼 음수 또는 평탄한 조건은 반대쪽 경계를 만든다. 즉 DPO delta는 assay 전반의 fitness predictor라기보다, reference policy 대비 선호 이동이 후보 순서를 유용하게 바꾸는 조건에서만 의미가 있다.

Reference 선택도 단일 recipe로 고정하기 어렵다. 기존 ablation에서 IF1, REV, ENVZ same-position은 `base -> DPO`가 더 강했고, SQSTM과 VG08은 `SFT -> DPO`가 더 강했다. 따라서 이 글에서 말하는 reference 조건은 특정 reference가 생물학적으로 옳다는 뜻이 아니라, 같은 DPO objective라도 policy가 출발하는 reference family에 따라 delta 신호가 달라진다는 뜻이다.

방법론적으로도 결론은 같다. DPO를 이 문제에 쓰려면 final policy likelihood를 그대로 fitness score처럼 쓰지 않고, reference 대비 변화량인 DPO delta를 먼저 분리해야 한다. 그다음 random lift, same-position 유지, position baseline 비교, label-flip control, fixed hybrid 비교를 차례로 통과하는지 확인해야 한다. 이 필터를 통과하지 못하면 delta는 residue-level preference가 아니라 position effect나 pair design shortcut일 수 있다.

### 결론과 후속 비교

이 실험에서 찾은 의미는 preference learning이 protein fitness를 일반적으로 예측한다는 것이 아니다. DPO delta는 reference-relative score이고, 후보 집합 안에서의 reranking 신호다. SQSTM positive, IF1 weaker positive, BLAT/KCNE1/MBD11/RASK binding negative를 함께 놓으면 결론은 더 좁아진다. 이 글의 DPO 결과는 preference learning을 general fitness predictor가 아니라, reference 대비 선호 이동이 특정 조건에서 후보 순위를 보정하는 reranker로 다룰 때 해석 가능하다. 좋은 protein sequence를 새로 생성한다는 free generation 주장은 이 글의 범위 밖이다.

DPO delta가 유효할 가능성이 있는 task는 다음처럼 제한된다. 첫째, 이미 주어진 DMS 후보 집합의 reranking이어야 한다. 둘째, position-level tolerance가 강하더라도 그것만으로 상위 후보가 완전히 설명되지 않아야 한다. 셋째, same-position pair에서도 preference 방향이 유지되어야 한다. 넷째, fixed hybrid처럼 position baseline 위에 delta를 얹었을 때 성능이 유지되거나 좋아져야 한다. 현재 데이터에서 이 조건을 가장 잘 통과한 사례는 SQSTM이고, IF1은 보조 양성, VG08/REV는 global-pair caution, BLAT/KCNE1/MBD11/RASK binding은 음성 경계로 남는다.

후속 비교에서 가장 중요한 것은 SQSTM과 비슷하게 same-position 및 fixed hybrid에서 position baseline을 넘는 조건을 더 찾는 일이다. 현재 가장 안정적인 조건이 SQSTM 하나이므로, 같은 패턴이 반복되는 assay가 늘어나면 protein variant reranking에서 preference learning을 별도 실험 라인으로 가져갈 근거가 강해진다. 반대로 그런 조건이 늘지 않으면 DPO는 특정 landscape에서만 작동하는 조건부 reranker로 남는다.

후속 실험은 DPO 하나로 닫기보다 preference objective, reference policy, pair construction을 분리해 비교하는 방향이 적절하다. 즉 같은 DMS 후보 집합에서 어떤 preference learning 신호가 position baseline 위에 남는지, 그리고 그 신호가 assay/readout을 바꿔도 반복되는지를 보는 reranking benchmark로 확장할 수 있다. 더 큰 protein LM baseline도 함께 필요하다. 현재 분석에서는 작은 `facebook/esm2_t6_8M_UR50D` zero-shot scoring만 간단 점검으로 확인했으므로, ProGen2-small이나 더 큰 ESM 계열과의 비교는 별도 실험으로 분리해 볼 만하다.

## Appendix: 핵심 수치

아래 표들은 본문 해석에 사용한 주요 DPO delta top-25 결과를 확인하기 위한 보조 표다. 본문 결론은 Table 3-8에서 이미 분리해 설명했으므로, 이 Appendix는 수치 조회와 재현 맥락을 복원할 때만 보면 된다. `DPO delta`는 3 seed 평균 top-25 high-fitness hit rate다. 첫 표는 핵심 reranking 사례, 둘째 표는 readout 및 negative boundary 사례만 따로 묶었다. 표 폭을 줄이기 위해 해석 문장은 넣지 않았고, 각 수치의 의미는 본문 결과 표와 함께 읽는다.

<details class="appendix-detail">
  <summary>핵심 reranking 사례</summary>
  <div class="details-content">
<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Assay/readout</th>
          <th>Recipe</th>
          <th class="align-right">Random</th>
          <th class="align-right">DPO delta</th>
          <th class="align-right">Lift</th>
          <th class="align-right">Position</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>SQSTM</td>
          <td><code>SFT -&gt; DPO</code></td>
          <td class="align-right">0.255</td>
          <td class="align-right">0.627</td>
          <td class="align-right">+0.371</td>
          <td class="align-right">0.720</td>
        </tr>
        <tr>
          <td>IF1</td>
          <td><code>base -&gt; DPO</code></td>
          <td class="align-right">0.253</td>
          <td class="align-right">0.493</td>
          <td class="align-right">+0.241</td>
          <td class="align-right">0.760</td>
        </tr>
        <tr>
          <td>VG08</td>
          <td><code>SFT -&gt; DPO</code></td>
          <td class="align-right">0.255</td>
          <td class="align-right">0.467</td>
          <td class="align-right">+0.211</td>
          <td class="align-right">0.640</td>
        </tr>
        <tr>
          <td>MBD11</td>
          <td><code>SFT -&gt; DPO</code></td>
          <td class="align-right">0.251</td>
          <td class="align-right">0.307</td>
          <td class="align-right">+0.056</td>
          <td class="align-right">0.920</td>
        </tr>
        <tr>
          <td>REV_HV1H2</td>
          <td><code>base -&gt; DPO</code></td>
          <td class="align-right">0.252</td>
          <td class="align-right">0.360</td>
          <td class="align-right">+0.108</td>
          <td class="align-right">0.160</td>
        </tr>
        <tr>
          <td>RASK abundance</td>
          <td><code>base -&gt; DPO</code></td>
          <td class="align-right">0.251</td>
          <td class="align-right">0.373</td>
          <td class="align-right">+0.122</td>
          <td class="align-right">0.720</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 1.</strong> 핵심 reranking 사례의 global/best recipe 수치다. 이 표는 수치 조회용이며, 각 조건의 해석과 same-position 안정성은 Table 3-5와 함께 읽어야 한다.</figcaption>
</figure>
  </div>
</details>

<details class="appendix-detail">
  <summary>readout 및 경계 사례</summary>
  <div class="details-content">
<figure class="table-figure table-figure--metrics">
  <div class="table-shell">
    <table class="metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>Assay/readout</th>
          <th>Recipe</th>
          <th class="align-right">Random</th>
          <th class="align-right">DPO delta</th>
          <th class="align-right">Lift</th>
          <th class="align-right">Position</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>RASK<br><span class="table-note-inline">binding-DARPin_K55</span></td>
          <td><code>base -&gt; DPO</code></td>
          <td class="align-right">0.251</td>
          <td class="align-right">0.173</td>
          <td class="align-right">-0.078</td>
          <td class="align-right">0.840</td>
        </tr>
        <tr>
          <td>VKOR1 activity</td>
          <td><code>base -&gt; DPO</code></td>
          <td class="align-right">0.252</td>
          <td class="align-right">0.360</td>
          <td class="align-right">+0.108</td>
          <td class="align-right">0.360</td>
        </tr>
        <tr>
          <td>VKOR1 abundance</td>
          <td><code>base -&gt; DPO</code></td>
          <td class="align-right">0.250</td>
          <td class="align-right">0.267</td>
          <td class="align-right">+0.016</td>
          <td class="align-right">0.800</td>
        </tr>
        <tr>
          <td>BLAT Deng / Stiffler /<br><span class="table-note-inline">Firnberg</span></td>
          <td><code>base -&gt; DPO</code></td>
          <td class="align-right">0.250 / 0.250 / 0.253</td>
          <td class="align-right">0.200 / 0.133 / 0.280</td>
          <td class="align-right">-0.050 / -0.117 / +0.027</td>
          <td class="align-right">0.880 / 0.840 / 0.960</td>
        </tr>
        <tr>
          <td>KCNE1 function /<br><span class="table-note-inline">expression</span></td>
          <td><code>base -&gt; DPO</code></td>
          <td class="align-right">0.251 / 0.250</td>
          <td class="align-right">0.293 / 0.280</td>
          <td class="align-right">+0.043 / +0.030</td>
          <td class="align-right">0.520 / 0.720</td>
        </tr>
        <tr>
          <td>Q53Z42 binding /<br><span class="table-note-inline">expression</span></td>
          <td><code>base -&gt; DPO</code></td>
          <td class="align-right">0.254 / 0.253</td>
          <td class="align-right">0.400 / 0.320</td>
          <td class="align-right">+0.146 / +0.067</td>
          <td class="align-right">0.800 / 0.760</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 2.</strong> readout 차이와 음성 경계를 확인하기 위한 보조 수치다. 여러 readout을 한 행에 묶은 경우 숫자는 assay/readout 표기 순서와 대응한다. 해석은 Table 7과 결론부의 boundary 설명을 기준으로 읽는다.</figcaption>
</figure>
  </div>
</details>

## References

<div class="reference-list" markdown="1">

<ol>
  <li id="ref-proteingym">Notin, P. et al. <strong>ProteinGym: Large-Scale Benchmarks for Protein Fitness Prediction and Design</strong>. NeurIPS Datasets and Benchmarks, 2023.<br>
    <a href="https://proceedings.neurips.cc/paper_files/paper/2023/hash/cac723e5ff29f65e3fcbb0739ae91bee-Abstract-Datasets_and_Benchmarks.html">NeurIPS proceedings</a> · <a href="https://proteingym.org/">ProteinGym website</a>
  </li>
  <li id="ref-dpo">Rafailov, R. et al. <strong>Direct Preference Optimization: Your Language Model is Secretly a Reward Model</strong>. NeurIPS, 2023.<br>
    <a href="https://proceedings.neurips.cc/paper_files/paper/2023/hash/a85b405ed65c6477a4fe8302b5e06ce7-Abstract-Conference.html">NeurIPS proceedings</a> · <a href="https://arxiv.org/abs/2305.18290">arXiv</a>
  </li>
  <li id="ref-protgpt2">Ferruz, N., Schmidt, S. & Höcker, B. <strong>ProtGPT2 is a deep unsupervised language model for protein design</strong>. <em>Nature Communications</em>, 2022.<br>
    <a href="https://doi.org/10.1038/s41467-022-32007-7">Paper / DOI</a> · <a href="https://huggingface.co/nferruz/ProtGPT2">Hugging Face model</a>
  </li>
  <li id="ref-lora">Hu, E. J. et al. <strong>LoRA: Low-Rank Adaptation of Large Language Models</strong>. ICLR, 2022.<br>
    <a href="https://openreview.net/forum?id=nZeVKeeFYf9">OpenReview</a> · <a href="https://arxiv.org/abs/2106.09685">arXiv</a>
  </li>
  <li id="ref-esm2">Lin, Z. et al. <strong>Evolutionary-scale prediction of atomic-level protein structure with a language model</strong>. <em>Science</em>, 2023.<br>
    <a href="https://doi.org/10.1126/science.ade2574">Paper / DOI</a> · <a href="https://huggingface.co/facebook/esm2_t6_8M_UR50D">ESM2-t6 model</a>
  </li>
</ol>

</div>

## Experiment Resources

<div class="reference-list" markdown="1">

- ProteinGym v1 DMS substitution data used for the extracted assay candidates.  
  [Hugging Face dataset](https://huggingface.co/datasets/OATML-Markslab/ProteinGym_v1)
- ProtGPT2 model used as the causal protein language model backbone.  
  [Hugging Face](https://huggingface.co/nferruz/ProtGPT2)

</div>

## Citation

이 글을 인용할 때는 아래 형식을 사용할 수 있다.

```text
Ilho Ahn, "DPO로 본 단백질 변이 reranking의 preference learning 신호", Mini Research, May 3, 2026.
```

또는 BibTeX 형식으로는 다음처럼 적을 수 있다.

```bibtex
@article{ahn2026proteingymdmsdpo,
  author = {Ilho Ahn},
  title = {DPO로 본 단백질 변이 reranking의 preference learning 신호},
  journal = {Mini Research},
  year = {2026},
  month = may,
  url = {https://muted-color.github.io/research/2026/05/03/proteingym-dms-dpo-reranking/}
}
```
