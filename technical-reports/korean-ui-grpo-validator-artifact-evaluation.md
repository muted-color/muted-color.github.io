---
lang: ko
title: "한국어 UI 문구 생성에서 GRPO 형식 보정의 구조 아티팩트 분석"
layout: post
date: 2026-06-08 09:00:00 +0900
last_modified_at: 2026-09-06 10:58:01 +0900
categories: ["LLM ALIGNMENT"]
tags: [korean-ui-copy, structured-generation, grpo, dpo, reward-hacking, llm-judge, format-validation, automatic-evaluation]
excerpt: "한국어 추천 카드에서 GRPO의 형식 통과율 회복과 슬롯 과다 나열, 표적 페널티 이후 기본 슬롯 조합으로의 이동을 분석한다."
description: "Gemma 3 4B의 한국어 추천 카드 생성에서 GRPO가 형식 통과율을 회복하면서 슬롯 과다 나열을 늘리고, 표적 페널티가 출력을 기본 슬롯 조합으로 이동시키는 현상을 분석한다."
permalink: /technical-reports/korean-ui-grpo-validator-artifact-evaluation/
image: /assets/images/common/editorial-hero-social.png
image_alt: "한국어 UI 문구 생성의 GRPO 형식 보정 구조 아티팩트 분석을 나타내는 소셜 썸네일"
hero_image: /assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/hero.svg
hero_alt: "Minimal summary cards comparing partial format recovery, slot stuffing, anti-stuffing mitigation, and signal separation"
hero_caption: "<strong>Figure 1.</strong> DPO 이후 GRPO 형식 보정의 요약 도식이다. 공개 검증 통과율 회복, slot stuffing 증가, anti-stuffing 완화, 품질 프록시와 구조 부산물의 분리를 함께 보여준다."
hero_frame: true
hero_variant: rounded-wide
hidden: true
publication_status: "technical-report"
report_scope: "technical report"
lab_path: "experiment-lab/projects/ui-grade-copy-generation-reward-analysis"
---

[원글](/technical-reports/korean-ui-nll-proxy-alignment/)은 한국어 추천 카드 생성에서 직접 선호 최적화(DPO) 이후 낮아진 형식 통과율을 GRPO로 일부 회복하는 현상을 다뤘다. 이번 글은 Gemma 3 4B 계열에서 이 형식 보정이 출력 구조에 남기는 반복적 패턴, 즉 구조 아티팩트를 분석한다 <a class="citation-ref" href="#ref-gemma-3">[1]</a>.

GRPO는 형식 통과율을 회복하면서 **슬롯 값을 과다하게 나열하는 현상(slot stuffing)**도 늘렸다. 이를 억제하는 페널티는 출력을 기본 슬롯 조합으로 이동시켰다(Figure 1). 이러한 구조 변화는 참조 언어모델의 음의 로그우도(NLL)와 LLM 평가자(judge)의 문맥 점수에 충분히 반영되지 않았다. 이번 GRPO 변형 간 품질을 직접 비교한 인간 평가는 없다.

## 요약

- GRPO는 DPO의 형식 통과율 `0.389`를 `0.587-0.694`로 회복했고, DPO가 얻은 `NLL_ctx` 개선도 대체로 유지했다.
- 통과 여부만 보상하는 binary와 항목별 부분 점수를 주는 dense 보상은 slot stuffing을 DPO 대비 약 3배로 늘렸다. judge와 NLL 문맥 프록시는 이 구조 변화를 잘 구분하지 못했다.
- anti-stuffing 페널티는 과다 나열을 줄이면서 기본 슬롯 조합으로의 쏠림을 키웠다. 결합 페널티는 이 쏠림을 줄였고, stuffing은 dense보다 낮게 유지됐다.
- 학습 시드 추가, 슬롯 기준값 변경, 입력 단위 집계와 생성 반복에서도 핵심 구조 변화는 유지됐다. judge gap의 감소 추세는 무작위 표본에서 재현되지 않았다.
- 이번 제약 디코딩(constrained decoding)은 슬롯 값 개수 상한을 강제했지만, 길이·어미를 포함한 전체 형식 통과율은 충분히 회복하지 못했다.

## 관련 연구

Rafailov et al.의 DPO는 선호쌍으로 정책을 직접 조정하며 <a class="citation-ref" href="#ref-dpo">[2]</a>, Shao et al.의 GRPO(Group Relative Policy Optimization)는 생성 그룹 내 상대 보상을 사용한다 <a class="citation-ref" href="#ref-grpo">[3]</a>. 여기서는 DPO 정책에 GRPO 형식 보상을 추가했을 때의 출력 변화를 본다.

Skalse et al.은 reward gaming이 발생하는 조건을 형식적으로 분석했고 <a class="citation-ref" href="#ref-reward-gaming">[4]</a>, Gao et al.은 합성 보상 실험에서 프록시 보상 개선이 별도 기준 보상의 개선을 보장하지 않음을 보였다 <a class="citation-ref" href="#ref-overoptimization">[5]</a>. 이번 분석은 형식 보상과 보상 밖의 구조 휴리스틱을 비교한다.

Zheng et al.은 LLM judge와 인간 판단의 일치도 및 평가 편향을 조사했다 <a class="citation-ref" href="#ref-llm-judge">[6]</a>. 여기서는 judge의 인간 일치도와 표본 선택을 점검하고, 생성 중 문법·스키마를 강제하는 제약 디코딩 <a class="citation-ref" href="#ref-constrained-decoding">[7]</a>, <a class="citation-ref" href="#ref-cd-json">[8]</a>을 형식 제어의 보조 비교로 포함한다.

## 문제 설정

평가 대상은 한국어 추천 카드 문구다. 출력은 `reason`, `title`, `subtitle` 같은 짧은 문구 필드와 `season`, `time`, `place` 같은 메타 슬롯을 포함한다. 이처럼 메타 슬롯을 포함한 카드는 자유 형식 문장보다 충족해야 할 조건이 많다. 문장이 자연스러워도 길이, 어미, 슬롯 범주, 빈 값 제약을 어기면 UI에 배치하기 어렵다.

형식 검증기 `V_public`은 학습 보상에 쓰인 검사기로, 필드 존재, 길이 상한, 허용 어미, `season`/`time` 카테고리, 비어 있지 않은 `place`를 검사한다. binary와 dense는 이 규칙을 보상으로 사용하고, 완화 변형은 슬롯 관련 페널티를 추가한다. 이하의 “공개 검증기”라는 명칭은 보상에 사용된 규칙을 judge 평가와 구분한다. 검증기 코드가 공개 배포되었다는 의미는 아니다.

Table 1은 평가 신호의 역할을 구분한다. `public_pass`는 공개 검증 통과율, `hidden_auto_pass`는 judge 평가 표본 중 형식 검증과 judge 기준을 모두 만족한 비율이다. 별도 인간 정답에 대한 정확도가 아니라 두 검사를 결합한 자동 지표다. `NLL_ctx`는 입력 문맥에 대한 참조 언어모델의 음의 로그우도(NLL)로, 낮을수록 높은 확률을 부여받은 출력이다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>신호</th>
          <th>무엇을 측정하나</th>
          <th>해석 기준</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>공개 검증기</td>
          <td>보상이 직접 보는 형식 규칙 통과 여부</td>
          <td>UI 배치 가능한 구조인지 보는 1차 형식 제약</td>
        </tr>
        <tr>
          <td>구조 휴리스틱</td>
          <td>슬롯 과다 나열, 기본 슬롯 집중, 어미·접미 패턴 집중</td>
          <td>검증기가 통과시킬 수 있는 구조적 아티팩트 감지</td>
        </tr>
        <tr>
          <td>고정 LLM judge</td>
          <td>자연성 <code>nat</code>과 입력-출력 문맥 적합도 <code>ctx</code></td>
          <td>형식과 구분한 문구 품질의 보조 평가</td>
        </tr>
        <tr>
          <td>NLL 프록시</td>
          <td>참조 LM 기준 조건부 NLL</td>
          <td>DPO 이후 문맥 프록시 변화 추적</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> 평가에서 분리한 신호다. 공개 검증기는 보상이 직접 보는 신호이고, 구조 휴리스틱은 형식 통과 여부만으로 드러나지 않는 출력 패턴을 확인한다. 완화 변형에서는 일부 슬롯 패턴도 페널티에 포함된다.</figcaption>
</figure>

judge는 Gemini 2.5 Flash로 고정했다 <a class="citation-ref" href="#ref-gemini-25">[9]</a>. 별도 인간 검토 500건의 0/1/2 점수와 비교한 이차 가중 카파(QWK, 점수 차이에 가중치를 둔 일치도)는 문맥 적합도에서 `0.059`, 자연성에서 `0.143`이었다. 정확 일치율은 약 `0.53-0.56`, 1점 이내 일치율은 약 `0.94-0.95`였지만 QWK는 낮아, judge를 보조 신호로 사용한다.

## 평가 설계

비교의 질문은 형식 보상을 높이는 과정에서 슬롯 과다 나열이 늘어나는지, 그 패턴을 감점하면 출력이 어디로 이동하는지다. 모든 GRPO 변형은 지도 미세조정(SFT)을 거쳐 DPO로 학습한 정책에서 시작한다. Table 2는 네 보상 변형을 비교한다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>초기화</th>
          <th>보상</th>
          <th>역할</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>DPO</td>
          <td>SFT</td>
          <td>선호쌍 DPO</td>
          <td>GRPO step 0 기준점</td>
        </tr>
        <tr>
          <td>GRPO-binary</td>
          <td>DPO</td>
          <td><code>V_public</code>를 통과하면 1, 아니면 0</td>
          <td>가장 단순한 형식 보상 기준선</td>
        </tr>
        <tr>
          <td>GRPO-dense</td>
          <td>DPO</td>
          <td>파싱, 필드 존재, 길이, 어미, 슬롯 유효성, 빈 슬롯 여부를 나눠 부분 점수화</td>
          <td>완전 통과/실패 대신 형식 구성요소별로 보상</td>
        </tr>
        <tr>
          <td>GRPO-antistuff</td>
          <td>DPO</td>
          <td>dense에서 총 슬롯 값 3개를 넘는 값 하나당 0.25 감점</td>
          <td>slot stuffing 표적 완화</td>
        </tr>
        <tr>
          <td>GRPO-antistuff2</td>
          <td>DPO</td>
          <td>antistuff에서 season과 time이 모두 ‘전체’이면 0.40 추가 감점</td>
          <td>기본 슬롯 조합으로의 쏠림 완화</td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> DPO 기준점과 GRPO 보상 변형이다. dense는 형식 조건별 부분 보상, antistuff와 antistuff2는 관찰된 슬롯 패턴을 억제하는 완화 설정이다.</figcaption>
</figure>

slot stuffing은 `place`, `time`, `season` 세 필드의 값 개수가 합계 3개를 넘는 경우다. 필드마다 하나씩을 강제하는 기준은 아니다. dense 보상은 대체로 `0.0-1.0` 범위이며, 완화 계수는 슬롯 과다 나열과 기본 슬롯 집중을 억제했을 때의 변화를 확인하기 위해 수작업으로 정했다.

원글과 같은 학습 외 1,026개 테스트 입력을 사용하되, 이번 분석은 평가 시 입력당 K=4개 생성에서 얻은 약 5.5-6천 카드를 집계한다. 한 생성이 여러 카드를 낼 수 있다. K는 평가의 반복 생성 수이며 GRPO 학습 그룹 크기를 뜻하지 않는다. 원글의 출력 단위 통과율·형식 통과 출력 NLL과 이번 카드 단위 집계는 구분한다.

공개 검증기와 구조 휴리스틱은 전체 카드에서, judge는 체크포인트마다 고정 시드로 무작위 추출한 400카드에서 계산한다. 공개 통과율 상승에 더해 judge 결합 통과율, NLL, 구조 휴리스틱과 보상 상관을 각각 점검한다.

## 결과

### 전체 결과

Figure 2에서 DPO는 SFT의 public_pass `0.724`를 `0.389`로 낮춘다. NLL_ctx는 `3.152 -> 2.641`로 낮아지고, 이후 GRPO는 이 프록시 개선을 유지하면서 public_pass를 `0.587-0.694`로 회복한다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/lineage-recheck.svg" alt="Shared-test comparison of public pass, hidden auto pass, and slot stuffing across SFT, DPO, and GRPO variants">
  <figcaption><strong>Figure 2.</strong> 공유 테스트셋에서 SFT, DPO, GRPO 변형을 다시 비교한 결과다. DPO는 <code>NLL_ctx</code>를 낮추지만 형식 통과율을 떨어뜨리고, GRPO는 형식 통과율을 회복하는 동시에 형식 보상 조건에서 slot stuffing을 키운다.</figcaption>
</figure>

동시에 slot stuffing은 SFT `0.191`, DPO `0.218`에서 GRPO-binary `0.640`, GRPO-dense `0.668`로 상승한다. 기반 정책에도 있던 슬롯 과다 나열이 GRPO 형식 보정 단계에서 커진다.

Table 3은 최종 체크포인트를 비교한다. `public_judge_gap`은 judge 400카드 안에서 공개 통과율과 결합 통과율의 차이다. `default_slot_rate`는 season과 time이 모두 ‘전체’인 비율, `suffix_concentration`은 특정 어미·접미 패턴의 집중도를 나타낸다.

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>지표</th>
          <th class="align-right">DPO</th>
          <th class="align-right">binary</th>
          <th class="align-right">dense</th>
          <th class="align-right">antistuff</th>
          <th class="align-right">antistuff2</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>public_pass<br><span class="table-note-inline">전체 카드</span></td>
          <td class="align-right"><code>0.389</code></td>
          <td class="align-right"><code>0.587</code></td>
          <td class="align-right"><code>0.669</code></td>
          <td class="align-right"><code>0.694</code></td>
          <td class="align-right"><code>0.647</code></td>
        </tr>
        <tr>
          <td>hidden_auto_pass<br><span class="table-note-inline">judge 400카드</span></td>
          <td class="align-right"><code>0.278</code></td>
          <td class="align-right"><code>0.460</code></td>
          <td class="align-right"><code>0.517</code></td>
          <td class="align-right"><code>0.580</code></td>
          <td class="align-right"><code>0.535</code></td>
        </tr>
        <tr>
          <td>public_judge_gap<br><span class="table-note-inline">judge 400카드</span></td>
          <td class="align-right"><code>0.110</code></td>
          <td class="align-right"><code>0.138</code></td>
          <td class="align-right"><code>0.122</code></td>
          <td class="align-right"><code>0.115</code></td>
          <td class="align-right"><code>0.135</code></td>
        </tr>
        <tr>
          <td>slot_stuffing</td>
          <td class="align-right"><code>0.218</code></td>
          <td class="align-right"><code>0.640</code></td>
          <td class="align-right"><code>0.668</code></td>
          <td class="align-right"><code>0.016</code></td>
          <td class="align-right"><code>0.141</code></td>
        </tr>
        <tr>
          <td>default_slot_rate</td>
          <td class="align-right"><code>0.072</code></td>
          <td class="align-right"><code>0.066</code></td>
          <td class="align-right"><code>0.056</code></td>
          <td class="align-right"><code>0.345</code></td>
          <td class="align-right"><code>0.068</code></td>
        </tr>
        <tr>
          <td>suffix_concentration</td>
          <td class="align-right"><code>0.268</code></td>
          <td class="align-right"><code>0.344</code></td>
          <td class="align-right"><code>0.390</code></td>
          <td class="align-right"><code>0.417</code></td>
          <td class="align-right"><code>0.308</code></td>
        </tr>
        <tr>
          <td>NLL_ctx median</td>
          <td class="align-right"><code>2.641</code></td>
          <td class="align-right"><code>2.613</code></td>
          <td class="align-right"><code>2.625</code></td>
          <td class="align-right"><code>2.621</code></td>
          <td class="align-right"><code>2.621</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> 최종 체크포인트의 카드 단위 평가다. 구조 비율은 전체 카드, NLL은 카드 단위 중앙값이다. gap은 judge 표본 안에서 계산하므로 표의 전체 카드 public_pass에서 hidden_auto_pass를 뺀 값과 다를 수 있다.</figcaption>
</figure>

binary와 dense에서는 공개 통과율과 judge 결합 통과율이 함께 오른다. 공개 통과 카드 중 judge 실패율은 DPO `0.284`에서 binary `0.230`, dense `0.191`로 낮아졌다. 반면 slot stuffing은 약 3배로 늘어, 문맥 프록시와 구조 휴리스틱이 서로 다른 변화를 포착했다.

step 810에서 보상과 judge 문맥 점수의 상관은 binary `-0.016`, dense `-0.071`, antistuff `-0.086`, antistuff2 `+0.047`로 작았다. 보상과 NLL_ctx의 상관도 `-0.086`에서 `-0.108` 사이였다. 학습 로그에서 DPO 기준 정책과의 분포 차이를 나타내는 KL 발산은 최종 체크포인트에서 `1.077-1.182`였다.

### 슬롯 과다 나열과 페널티 이후 이동

Figure 3에서 binary와 dense는 학습이 진행될수록 공개·judge 결합 통과율과 slot stuffing이 함께 상승한다. dense는 binary보다 높은 형식 통과율에 도달하지만, 두 설정 모두 슬롯 과다 나열이 높은 수준으로 수렴한다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/overoptimization-curves.svg" alt="Step-wise public pass, hidden auto pass, and slot stuffing curves for binary and dense GRPO">
  <figcaption><strong>Figure 3.</strong> binary와 dense GRPO의 학습 step별 검증기 신호다. 두 보상 모두 <code>public_pass</code>와 <code>hidden_auto_pass</code>를 올리지만, 같은 구간에서 slot stuffing도 상승한다. dense는 더 높은 통과율에 도달하지만 구조 실패를 제거하지는 못한다.</figcaption>
</figure>

Figure 4에서 GRPO-binary의 길이 위반(`LEN_EXCEEDED`)은 step 50의 `0.539`에서 step 810의 `0.225`로 줄었다. 어미 위반(`BAD_SUFFIX`)은 `0.291 -> 0.275`로 소폭 줄었고, 카테고리 위반(`INVALID_CATEGORY`)은 거의 0이었다. 슬롯 과다 나열은 주로 허용된 카테고리 값 안에서 발생했다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/failure-taxonomy.svg" alt="Failure taxonomy curves for LEN_EXCEEDED, BAD_SUFFIX, and INVALID_CATEGORY in GRPO-binary">
  <figcaption><strong>Figure 4.</strong> GRPO-binary의 실패 유형 변화다. 길이 위반은 줄어들지만 <code>BAD_SUFFIX</code>는 남고 카테고리 위반은 거의 0에 가깝다. stuffing은 잘못된 카테고리 선택보다 유효 슬롯 값을 과도하게 나열하는 문제에 가깝다.</figcaption>
</figure>

구조 휴리스틱 중 가장 크게 움직인 것은 slot stuffing이었다. 템플릿 반복은 감소하고 다양성은 개선됐으며, 슬롯-문맥 충돌과 복사/문자 이상은 거의 0이었다. 어미·접미 패턴 집중은 모든 GRPO 변형에서 상승했지만 antistuff2에서 가장 낮았다.

최종 체크포인트 카드를 합친 슬롯 값 개수와 NLL_ctx의 Spearman 상관은 약 `-0.008`이었다. stuffing이 있는 카드와 없는 카드의 NLL 평균은 `2.635` 대 `2.643`, judge 문맥 점수 평균은 `1.697` 대 `1.724`였다. 추가 슬롯 값에 따른 뚜렷한 문맥 프록시 이득은 관찰되지 않았다.

Figure 5는 형식 통과율과 함께 슬롯 과다 나열·기본 슬롯 집중이 어떻게 달라지는지 비교한다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/endpoint-evaluation-matrix.svg" alt="Endpoint trade-off map comparing public pass against slot stuffing and default slot rate">
  <figcaption><strong>Figure 5.</strong> 최종 체크포인트에서 <code>public_pass</code>와 구조 부산물의 관계를 나눠 본 그림이다. 왼쪽은 slot stuffing, 오른쪽은 기본 슬롯 비율과의 관계를 보여준다. binary와 dense는 형식 통과율을 올리지만 stuffing도 키우고, antistuff는 stuffing을 낮추는 대신 기본 슬롯 조합으로 이동하며, antistuff2는 기본 슬롯 집중을 다시 낮춘다.</figcaption>
</figure>

`antistuff`는 dense의 stuffing `0.668`을 `0.016`으로 낮추면서 공개 통과율 `0.694`, judge 결합 통과율 `0.580`을 얻었다. 과다 나열을 줄여도 두 통과율은 유지되거나 높아졌다(Table 3).

동시에 기본 슬롯 비율은 dense `0.056`에서 antistuff `0.345`로 올랐다. 이 조합도 감점한 `antistuff2`는 기본 슬롯 비율을 `0.068`로 낮췄다. stuffing은 `0.141`로 antistuff보다 다시 올랐지만 dense `0.668`보다는 낮았다. 공개 통과율은 dense `0.669`에서 antistuff2 `0.647`로 약 2.2%p 낮아졌다.

같은 헤어스타일링 제품 입력에서 dense는 `time=[아침, 저녁, 밤]`, `place=[집, 미용실]`처럼 값을 나열했다. antistuff는 season·time·place가 모두 ‘전체’에 가까운 조합으로, antistuff2는 `time=아침`, `place=헤어샵`처럼 구체적인 슬롯으로 이동했다.

### 불확실성과 반복 평가

binary/dense의 stuffing 증가와 antistuff의 감소는 DPO와 95% 신뢰구간(CI)이 겹치지 않을 정도로 크다(Appendix Table 1).

judge 결합 통과는 공개 통과의 부분집합이다. Table 4는 이 두 통과율의 차이가 모델 간에 얼마나 변했는지를 비교한다. 모든 CI가 0을 포함해 gap 변화는 확인되지 않았으며, 이를 품질 동등성의 근거로 사용하지 않는다.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>비교</th>
          <th class="align-right">Δ public_judge_gap</th>
          <th class="align-right">95% CI</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>binary - DPO</td>
          <td class="align-right"><code>+0.028</code></td>
          <td class="align-right"><code>[-0.018, +0.073]</code></td>
        </tr>
        <tr>
          <td>dense - DPO</td>
          <td class="align-right"><code>+0.013</code></td>
          <td class="align-right"><code>[-0.032, +0.057]</code></td>
        </tr>
        <tr>
          <td>antistuff - dense</td>
          <td class="align-right"><code>-0.008</code></td>
          <td class="align-right"><code>[-0.052, +0.037]</code></td>
        </tr>
        <tr>
          <td>antistuff2 - dense</td>
          <td class="align-right"><code>+0.012</code></td>
          <td class="align-right"><code>[-0.033, +0.057]</code></td>
        </tr>
        <tr>
          <td>antistuff2 - antistuff</td>
          <td class="align-right"><code>+0.020</code></td>
          <td class="align-right"><code>[-0.025, +0.065]</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> 모델 간 검증기-judge gap 차이와 bootstrap 95% CI다. 양수는 앞 모델의 gap이 더 크다는 뜻이다.</figcaption>
</figure>

두 번째 학습 시드에서도 binary의 slot stuffing은 DPO 기준점 `0.218`보다 높았고(`0.640`, `0.696`), antistuff는 낮게 유지됐다(`0.016`, `0.023`). 슬롯 값 개수 기준을 `>3`, `>4`, `>5`로 바꾸거나 카드 단위 대신 입력 단위 평균을 써도 결론은 바뀌지 않았다.

Table 5는 step-810 체크포인트를 고정하고 다섯 생성 시드로 다시 평가한 결과다. 구조 휴리스틱의 시드별 표준편차는 핵심 효과보다 작았다.

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>변형</th>
          <th class="align-right">public_pass</th>
          <th class="align-right">slot_stuffing</th>
          <th class="align-right">default_slot_rate</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>binary</td>
          <td class="align-right"><code>0.598 +/- 0.007</code></td>
          <td class="align-right"><code>0.647 +/- 0.008</code></td>
          <td class="align-right"><code>0.061 +/- 0.002</code></td>
        </tr>
        <tr>
          <td>dense</td>
          <td class="align-right"><code>0.666 +/- 0.007</code></td>
          <td class="align-right"><code>0.663 +/- 0.005</code></td>
          <td class="align-right"><code>0.060 +/- 0.002</code></td>
        </tr>
        <tr>
          <td>antistuff</td>
          <td class="align-right"><code>0.684 +/- 0.004</code></td>
          <td class="align-right"><code>0.016 +/- 0.001</code></td>
          <td class="align-right"><code>0.354 +/- 0.004</code></td>
        </tr>
        <tr>
          <td>antistuff2</td>
          <td class="align-right"><code>0.649 +/- 0.007</code></td>
          <td class="align-right"><code>0.138 +/- 0.006</code></td>
          <td class="align-right"><code>0.067 +/- 0.001</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 5.</strong> 다섯 생성 시드의 step-810 평균과 표준편차다. 생성 반복에 따른 분산은 핵심 효과에 비해 작다.</figcaption>
</figure>

### judge 표본 선택의 영향

Figure 6에서 체크포인트의 앞쪽 400카드를 연속으로 쓰면 judge gap이 학습과 함께 감소하지만, 무작위 400카드에서는 평탄하거나 소폭 상승한다. 카드 순서가 입력 순서를 따르므로, 앞쪽 연속 표본이 특정 입력 하위집단을 과표집한 것으로 보인다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/sampling-bias-gap.svg" alt="Public judge gap trends under first-400 and random-400 judge samples for binary and dense GRPO">
  <figcaption><strong>Figure 6.</strong> judge 부분표본에 따른 gap 추세다. 앞쪽 연속 표본의 감소 추세는 무작위 표본에서 재현되지 않는다.</figcaption>
</figure>

### 제약 디코딩 비교

Figure 7은 DPO 정책의 추론에 JSON schema와 배열 길이 상한(array cap)을 적용한 비교다. 학습을 바꾸지 않고 출력 구조를 제한했을 때의 형식 회복 범위를 점검한다.

<figure class="media-figure media-figure--wide-visual">
  <img src="/assets/images/posts/korean-ui-grpo-validator-artifact-evaluation/constrained-decoding.svg" alt="Constrained decoding comparison of public pass, slot stuffing, length boundary, and hidden auto pass">
  <figcaption><strong>Figure 7.</strong> DPO 정책 위에 constrained decoding을 적용한 결과와 학습 기반 보정을 비교한 그림이다. array cap은 slot stuffing을 0으로 낮추지만 <code>public_pass</code>는 0.44 수준에 머물고 length boundary 문제가 커진다. RL antistuff는 <code>public_pass</code>와 <code>hidden_auto_pass</code>를 더 크게 회복한다.</figcaption>
</figure>

모든 출력이 파싱 가능해졌지만 public_pass는 `0.389 -> 0.403-0.440`으로 올랐다. `+array-cap`은 stuffing을 `0.000`으로 낮추면서 길이 경계 비율(length_boundary_rate)을 `0.202 -> 0.394`로 높였고, judge 결합 통과율은 `0.265`였다. antistuff의 public_pass `0.694`, judge 결합 통과율 `0.580`과 비교하면, 이번 제약은 슬롯 과다 나열을 제거했지만 길이·어미를 포함한 전체 형식 통과율은 충분히 회복하지 못했다.

## 해석

DPO 이후 GRPO를 적용한 설정에서 NLL 문맥 프록시 개선과 형식 통과율 회복을 함께 유지했다. 동시에 슬롯 과다 나열이 증가했으며, judge와 NLL 점수는 이 구조 변화를 뚜렷하게 구분하지 못했다. 무작위 judge 표본에서 gap 감소가 재현되지 않았고 직접 인간 비교도 없으므로, 이 결과만으로 형식 보상이 문구 품질을 지속해서 높였다고 판단하기는 어렵다. 이번 결과의 중심은 통과율 회복과 구조 패턴 변화가 함께 나타났다는 관찰이다.

표적 페널티는 과다 나열을 줄이면서 기본 슬롯 집중을 키웠다. 결합 페널티는 이 집중을 줄였고, stuffing은 dense보다 낮게 유지됐다. 따라서 구조화 생성의 보상 보정은 통과율뿐 아니라 보상 밖의 구조 휴리스틱을 함께 측정하고, 완화 이후 출력이 어디로 이동하는지 추적할 필요가 있다.

## 한계

- 본문은 보상 구성요소와 완화 계수를 보고하지만 dense의 항목별 정확한 가중치, GRPO 학습 그룹 크기·학습률·배치 구성, judge 통과 임계값을 재현 가능한 명세로 제공하지 않는다. 이 값이 확인되기 전에는 동일 설정의 재현이나 다른 구현과의 직접 비교가 어렵다.
- 별도 judge 검증 자료는 있지만, 이번 GRPO 변형 간 품질을 직접 비교한 인간 평가는 없다. judge는 인간 일치도가 낮고 체크포인트별 400카드 표본에 한정된다.
- 카드 집합 bootstrap이 같은 입력에서 반복 생성된 카드 사이의 의존성을 반영했는지는 확인되지 않았다. 입력 단위 평균에서도 구조 변화의 방향은 유지됐지만, 이는 입력을 묶어 재표집한 신뢰구간을 제공한 것과는 다르다.
- 학습 곡선은 대부분 단일 학습 시드다. binary와 antistuff는 seed 43으로 반복했으며, 다섯 생성 시드 평가는 고정 체크포인트의 생성 변동만 측정한다.
- 슬롯 기준값, 페널티 계수와 judge 통과 임계값은 수작업 설정이다. 인접 슬롯 기준값에서도 방향은 유지됐지만 절대 비율은 설정에 의존한다.
- 범위는 Gemma 3 4B 계열의 한국어 추천 카드와 DPO 이후 GRPO 보정이다. constrained decoding도 DPO 위의 특정 JSON schema·array cap 비교에 한정된다.

## Appendix: 주요 비율의 신뢰구간

<figure class="table-figure table-figure--comparison">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--numeric-columns">
      <thead>
        <tr>
          <th>모델</th>
          <th class="align-right">public_pass<br><span class="table-note-inline">전체 카드 · 95% CI</span></th>
          <th class="align-right">slot_stuffing<br><span class="table-note-inline">전체 카드 · 95% CI</span></th>
          <th class="align-right">hidden_auto_pass<br><span class="table-note-inline">judge 400카드 · 95% CI</span></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>DPO</td>
          <td class="align-right"><code>0.389 [0.377, 0.402]</code></td>
          <td class="align-right"><code>0.218 [0.207, 0.229]</code></td>
          <td class="align-right"><code>0.278 [0.232, 0.323]</code></td>
        </tr>
        <tr>
          <td>binary</td>
          <td class="align-right"><code>0.587 [0.575, 0.599]</code></td>
          <td class="align-right"><code>0.640 [0.628, 0.653]</code></td>
          <td class="align-right"><code>0.460 [0.412, 0.510]</code></td>
        </tr>
        <tr>
          <td>dense</td>
          <td class="align-right"><code>0.669 [0.657, 0.680]</code></td>
          <td class="align-right"><code>0.668 [0.656, 0.681]</code></td>
          <td class="align-right"><code>0.517 [0.468, 0.568]</code></td>
        </tr>
        <tr>
          <td>antistuff</td>
          <td class="align-right"><code>0.694 [0.682, 0.705]</code></td>
          <td class="align-right"><code>0.016 [0.012, 0.019]</code></td>
          <td class="align-right"><code>0.580 [0.532, 0.627]</code></td>
        </tr>
        <tr>
          <td>antistuff2</td>
          <td class="align-right"><code>0.647 [0.635, 0.659]</code></td>
          <td class="align-right"><code>0.141 [0.132, 0.150]</code></td>
          <td class="align-right"><code>0.535 [0.486, 0.584]</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 1.</strong> 주요 비율과 95% CI다. public_pass와 slot_stuffing은 전체 카드 집합 bootstrap, hidden_auto_pass는 judge 400카드 표본의 이항 CI다.</figcaption>
</figure>

## References

<div class="reference-list" markdown="1">

1. <span id="ref-gemma-3"></span>Google DeepMind. [Gemma 3 model card](https://huggingface.co/google/gemma-3-4b-it). 2025.
2. <span id="ref-dpo"></span>Rafael Rafailov et al. [Direct Preference Optimization: Your Language Model is Secretly a Reward Model](https://proceedings.neurips.cc/paper_files/paper/2023/hash/a85b405ed65c6477a4fe8302b5e06ce7-Abstract-Conference.html). NeurIPS 2023.
3. <span id="ref-grpo"></span>Zhihong Shao et al. [DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models](https://arxiv.org/abs/2402.03300). arXiv:2402.03300, 2024.
4. <span id="ref-reward-gaming"></span>Joar Skalse et al. [Defining and Characterizing Reward Gaming](https://proceedings.neurips.cc/paper_files/paper/2022/hash/3d719fee332caa23d5038b8a90e81796-Abstract-Conference.html). NeurIPS 2022.
5. <span id="ref-overoptimization"></span>Leo Gao, John Schulman, and Jacob Hilton. [Scaling Laws for Reward Model Overoptimization](https://proceedings.mlr.press/v202/gao23h.html). ICML 2023.
6. <span id="ref-llm-judge"></span>Lianmin Zheng et al. [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://proceedings.neurips.cc/paper_files/paper/2023/hash/91f18a1287b398d378ef22505bf41832-Abstract-Datasets_and_Benchmarks.html). NeurIPS 2023.
7. <span id="ref-constrained-decoding"></span>Brandon T. Willard and Rémi Louf. [Efficient Guided Generation for Large Language Models](https://arxiv.org/abs/2307.09702). arXiv:2307.09702, 2023.
8. <span id="ref-cd-json"></span>Saibo Geng et al. [Grammar-Constrained Decoding for Structured NLP Tasks without Finetuning](https://aclanthology.org/2023.emnlp-main.674/). EMNLP 2023.
9. <span id="ref-gemini-25"></span>Gheorghe Comanici et al. [Gemini 2.5: Pushing the Frontier with Advanced Reasoning, Multimodality, Long Context, and Next Generation Agentic Capabilities](https://arxiv.org/abs/2507.06261). arXiv:2507.06261, 2025.

</div>

## Citation

Text citation:

```text
Ahn, I. (2026). 한국어 UI 문구 생성에서 GRPO 형식 보정의 구조 아티팩트 분석. Technical report.
```

BibTeX:

```bibtex
@techreport{ahn2026grpoValidatorArtifactEvaluation,
  title = {한국어 UI 문구 생성에서 GRPO 형식 보정의 구조 아티팩트 분석},
  author = {Ahn, Ilho},
  year = {2026},
  type = {Technical report},
  url = {https://muted-color.github.io/technical-reports/korean-ui-grpo-validator-artifact-evaluation/}
}
```
