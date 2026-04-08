---
title: "첫 글: 이 블로그를 어떻게 쓸지"
date: 2026-04-08 19:00:00 +0900
categories: [template]
tags: [template, github-pages]
excerpt: "미니 리서치 블로그를 어떤 단위의 글로 운영할지 정리한 시작 메모."
hero_image: /assets/images/editorial-hero.svg
math: true
---

이 저장소는 아주 작은 단위의 연구 메모를 빠르게 쌓기 위한 GitHub Pages 템플릿으로 시작합니다.

## 이 블로그에 올릴 것

- 짧은 리서치 요약
- 실험 로그
- 읽은 자료 메모
- 구현 중 발견한 작은 인사이트

## 권장 글쓰기 패턴

1. 질문을 먼저 적기
2. 관찰한 사실만 짧게 적기
3. 임시 결론을 한 줄로 정리하기
4. 다음에 볼 항목을 남기기

## 공통 서식 테스트

이 섹션은 이후 새 글을 쓸 때 자주 쓸 수 있는 서식을 한 페이지에서 빠르게 확인하기 위한 샘플입니다.[^sample-note]

### Plot

![샘플 plot](/assets/images/template-plot.svg)

위 플롯은 실험 step에 따른 validation score 변화를 단순화해서 그린 예시입니다.

### Table

| Setting | Train Loss | Eval Score | Note |
|:--|--:|--:|:--|
| Baseline | 1.92 | 68.4 | no retrieval |
| Retrieval + Rerank | 1.71 | 72.9 | stable |
| Retrieval + Rerank + CoT | 1.66 | 74.1 | best latency/quality tradeoff |

### LaTeX

inline 수식 예시: $L(\theta) = \sum_{i=1}^{N} \log p_\theta(y_i \mid x_i)$

display 수식 예시:

$$
\hat{y} = \arg\max_{y \in \mathcal{Y}} p_\theta(y \mid x), \qquad
\mathcal{L}_{\mathrm{rank}} = - \log \frac{\exp(s^+)}{\exp(s^+) + \sum_j \exp(s_j^-)}
$$

행렬 표기도 같이 테스트합니다:

$$
W' = W + \Delta W,\qquad
\Delta W = BA,\qquad
B \in \mathbb{R}^{d \times r},\ A \in \mathbb{R}^{r \times k}
$$

### Code Block

```python
def summarize_run(metrics: dict[str, float]) -> str:
    gain = metrics["retrieval_cot"] - metrics["baseline"]
    return f"retrieval+cot improved score by {gain:.1f} points"


print(summarize_run({"baseline": 68.4, "retrieval_cot": 74.1}))
```

```json
{
  "experiment": "retrieval-rerank-cot",
  "dataset": "internal_eval_v3",
  "best_checkpoint": "step-4200",
  "avg_latency_ms": 812
}
```

### Quote, Callout, Details

> 좋은 리서치 메모는 결론보다 관찰을 먼저 남긴다.
> 그래야 나중에 실험 맥락을 복원할 수 있다.

---

<details>
  <summary>추가 메모 펼치기</summary>

  retrieval 품질이 충분하지 않을 때는 reasoning step을 늘리는 것보다
  candidate filtering을 먼저 손보는 편이 더 효율적일 수 있습니다.
</details>

### List Variants

- unordered list item
- another item with `inline code`
  - nested item

1. ordered item one
2. ordered item two
3. ordered item three

- [x] task style checked
- [ ] task style unchecked

### Definition List

Retrieval
: 외부 지식 소스에서 관련 문서를 찾아오는 단계

Reranking
: retrieved candidate를 다시 점수화해서 순서를 재배치하는 단계

### Footnote

간단한 각주도 테스트합니다.[^latency-note]

[^sample-note]: 실제 운영에서는 이 섹션을 복사해서 새 글 초안의 출발점으로 써도 됩니다.
[^latency-note]: latency는 모델 크기, prompt 길이, retrieval depth에 모두 영향을 받습니다.
