# 응답 서식

- CLI 환경에 맞게 짧은 헤딩, 굵은 요점, 글머리 기호, 단순 표를 사용한다.
- 긴 줄글보다 구조화된 Markdown을 우선한다.
- 코드, 경로, front matter key는 백틱이나 파일 링크로 명확히 표시한다.

# 작업 방식

- 작업 범위가 넓거나 확인 지점이 여럿이면 Sub Agent를 활용한다.
- 기존 파일의 의도와 스타일을 먼저 확인하고 최소 범위로 수정한다.
- 사용자 변경, 미추적 파일, 관련 없는 작업트리 변경은 되돌리지 않는다.

# 블로그 글 작성

## 템플릿 우선

- 새 글을 작성하거나 큰 구조를 바꿀 때는 먼저 `_posts/2026-04-08-template.md`를 확인한다.
- 표, 모델 카드, 탭, 비교 샘플, 수식, appendix, citation 형식은 템플릿 예시를 따른다.
- 새 표현 형식을 만들었다면 재사용 가능하도록 템플릿에도 짧은 예시를 추가한다.

## 서식 폴리싱

- 글 초안이나 큰 수정 뒤에는 필요시 프로젝트 커스텀 Sub Agent인 `format_polisher`에게 **서식 폴리싱 리뷰**를 맡긴다.
- `format_polisher` 설정은 `.codex/agents/format-polisher.toml`에 둔다. Sub Agent 설정을 바꿀 때는 이 파일을 먼저 수정한다.
- 서식 폴리싱 Sub Agent는 `_posts/2026-04-08-template.md`와 비슷한 성격의 기존 글 1-2개를 먼저 확인한 뒤, 현재 글에 적용할 수 있는 서식만 제안하거나 수정한다.
- 폴리싱 범위는 문체, 구조, 표/그림/수식/appendix/readability에 한정한다. 실험 결론, 수치, 방법론의 의미를 바꾸지 않는다.
- 표는 column명, 본문 설명, caption의 용어가 서로 맞는지 확인한다. 긴 method명은 `<br>`와 `table-note-inline`으로 의미 단위 줄바꿈을 넣고, 숫자 column은 `align-right`를 사용한다.
- 작은 2-column 숫자표는 `table-figure--compact-metrics`와 `metrics-table--compact-two-col`을 우선 검토한다.
- Figure와 Table은 본문에서 번호로 언급하고, caption은 “무엇을 보여주며 어떻게 읽어야 하는지”를 짧게 설명한다.
- 수식은 `<code>`로 쓰지 않고 LaTeX로 작성한다. 수식이 있는 글은 front matter에 `math: true`를 둔다.
- Mermaid를 쓰는 글은 front matter에 `mermaid: true`를 두고, `<figure class="media-figure" markdown="1">` 안에 넣어 caption을 붙인다.
- 모델, 데이터셋, 약어가 처음 등장할 때 독자 이해에 필요한 최소 정의를 짧은 blockquote나 문단으로 추가한다. 단, 글을 튜토리얼처럼 길게 만들지 않는다.
- Appendix는 내부 실험 경로 목록보다 공개 독자가 필요한 benchmark contract, method glossary, metric caveat를 우선한다. 내부 경로는 front matter의 `lab_path`로 충분한지 먼저 판단한다.
- 공통 CSS를 바꿀 때는 기존 글에 미치는 영향을 고려하고, 재사용 가능한 작은 utility로 만든다.
- 폴리싱 후에는 `rg`로 용어 불일치와 내부 경로 노출을 확인하고, 로컬 서버가 떠 있으면 `curl`로 HTML 반영 여부를 확인한다.

Sub Agent에게 맡길 때는 다음처럼 구체적으로 요청한다.

```text
format_polisher를 사용해서 이 글을 공개용 미니 리서치 노트 기준으로 서식 폴리싱해줘.
범위는 표/그림 caption, 용어 통일, 수식/mermaid/front matter, appendix, 긴 table cell 줄바꿈, 읽기 흐름이다.
실험 결론이나 수치는 바꾸지 말고, 필요한 경우 파일을 직접 수정한 뒤 변경한 위치를 요약해줘.
```

## Front Matter

- 공개 글은 `image:`를 반드시 둔다.
- `image:`는 Open Graph, LinkedIn, Twitter/X 썸네일용이며 PNG/JPG를 사용한다.
- `hero_image:`는 본문 hero용이며 `image:`를 대체하지 않는다.
- 공개 글은 `description:`, `last_modified_at:`, `image_alt:`를 둔다.
- SEO 관련 세부 규칙은 `SEO.md`를 참고한다.
- 실험 기반 글은 `lab_path:`를 둔다.
- `lab_path:`는 로컬 전체 경로가 아니라 `~/lab/` 뒤쪽 상대 경로만 기록한다.

```yaml
lab_path: "experiment-lab/projects/project-slug"
description: "검색 결과에 노출될 수 있도록 실험 질문, 대상, 핵심 결론과 한계를 한 문장으로 정리한다."
last_modified_at: 2026-04-19 15:45:00 +0900
image: /assets/images/posts/post-slug/social-thumbnail.png
image_alt: "소셜/검색 대표 이미지가 무엇을 요약하는지 설명"
hero_image: /assets/images/posts/post-slug/hero.svg
```

## 문체

- Gemma4 비교 글과 ESM2/LoRA 글처럼 담백한 연구 노트 톤을 따른다.
- 공개용 실험 글은 에세이, 기사, 독백, 튜토리얼, 가이드처럼 쓰지 않고 **미니 리서치 노트**처럼 쓴다.
- 문장은 건조하게 유지하되, 단순 요약문이 아니라 `문제 설정 -> 평가 설계 -> 관찰 -> 해석 -> 한계`가 드러나게 구성한다.
- 도입부는 개인적 서사나 수사적 문장보다, 왜 이 평가 문제가 필요한지와 어떤 조건에서 해석해야 하는지를 먼저 고정한다.
- 초반에 연구 질문 또는 평가 질문과 빠른 결론을 제시하고, 바로 조건과 한계를 붙인다.
- 긴 실험 글은 앞쪽에 `## 요약`을 두고 4-6개 bullet로 핵심과 caveat를 먼저 고정한다.
- 단락은 `관찰 -> 해석 -> 주의점` 흐름을 기본으로 한다.
- 헤딩은 되도록 명사형 또는 주제형으로 쓴다. `~인가`, `~나`, `무엇을 배웠나` 같은 질문형 헤딩은 피한다.
- `이 프로젝트의 첫 질문은...`, `목표는 ...였다`처럼 에세이식 전개나 가이드식 선언문은 피하고, 연구 대상과 평가 조건을 직접 서술한다.
- 수치와 표는 값만 나열하지 말고 읽는 법과 한계를 함께 설명한다.
- 자동 지표, judge 지표, runtime, variance는 역할을 분리해 해석한다.
- 약한 신호, 반례, 흔들린 지점을 숨기지 않는다.
- 과장된 승패 선언, 근거 없는 일반화, `압도적`, `완벽`, `명백히 SOTA` 같은 표현은 피한다.

## 용어 선택

- 공개용 미니 리서치 글은 내부 운영 문서 표현보다, 독자가 바로 이해할 수 있는 연구 문장을 우선한다.
- 새 모델을 이미 제안한 것처럼 보이는 표현을 피한다. 모델 개발 전 단계의 글에서는 `새 모델`, `모델을 붙인다`, `모델을 쌓는다`보다 `문제를 다루기 위한 방법`, `방법 비교`, `평가 문제`, `benchmark 설계`, `신호 조합`을 우선한다.
- `최종 모델`, `winner`처럼 단일 승자를 암시하는 말은 실제 결론이 그럴 때만 쓴다. calibration reference와 primary-score 조합이 나뉘면 `calibrated reference`, `primary score 기준 조합`, `가장 안정적인 비교 기준`처럼 역할을 분리한다.
- `Stage 0`, `Stage 1` 같은 이름은 꼭 필요할 때만 괄호로 1회 병기하고, 본문에서는 `초기 가능성 점검`, `본 평가`, `후속 비교`처럼 풀어쓴다.
- `열렸다`, `opening`, `benchmark opened` 대신 `의미 있는 성능 차이가 확인됐다`, `benchmark로 성립했다`, `비교할 가치가 있는 평가 문제로 남았다`를 우선한다.
- `closeout`, `line closed` 대신 `현재 단계의 결론`, `여기까지를 정리한다`, `현 설정에서의 마무리`를 우선한다.
- 단일 승자를 말해야 할 때도 `winner`보다 `현재 기준선`, `가장 강한 기준 모델`, `가장 안정적인 비교 기준`을 우선한다.
- `same-contract`, `frozen question`, `residual` 같은 내부 표현은 각각 `동일한 평가 조건`, `고정된 평가 질문`, `남는 오류` 또는 `구조적으로 남는 한계`처럼 바꿔 쓴다.
- 용어를 새로 도입할 때는 숫자나 표보다 먼저, 그 말이 독자에게 무엇을 뜻하는지 한 문장으로 풀어준다.

## Citation

- 관련 논문, 데이터셋, 모델, 실험 리소스가 있으면 끝부분에 `## References` 또는 `## Experiment Resources`로 정리한다.
- `References`와 `Experiment Resources`의 목록은 공통 CSS가 적용되도록 `<div class="reference-list" markdown="1">`로 감싼다.
- 공개 글은 마지막 섹션을 반드시 `## Citation`으로 끝낸다.
- `Citation`에는 사람이 바로 복사할 수 있는 text citation과 BibTeX를 함께 둔다.
