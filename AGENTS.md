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

## Front Matter

- 공개 글은 `image:`를 반드시 둔다.
- `image:`는 Open Graph, LinkedIn, Twitter/X 썸네일용이며 PNG/JPG를 사용한다.
- `hero_image:`는 본문 hero용이며 `image:`를 대체하지 않는다.
- 실험 기반 글은 `lab_path:`를 둔다.
- `lab_path:`는 로컬 전체 경로가 아니라 `~/lab/` 뒤쪽 상대 경로만 기록한다.

```yaml
lab_path: "experiment-lab/projects/project-slug"
image: /assets/images/posts/post-slug/social-thumbnail.png
hero_image: /assets/images/posts/post-slug/hero.svg
```

## 문체

- Gemma4 비교 글과 ESM2/LoRA 글처럼 담백한 연구 노트 톤을 따른다.
- 초반에 질문과 빠른 결론을 제시하고, 바로 조건과 한계를 붙인다.
- 긴 실험 글은 앞쪽에 `## 요약`을 두고 4-6개 bullet로 핵심과 caveat를 먼저 고정한다.
- 단락은 `관찰 -> 해석 -> 주의점` 흐름을 기본으로 한다.
- 수치와 표는 값만 나열하지 말고 읽는 법과 한계를 함께 설명한다.
- 자동 지표, judge 지표, runtime, variance는 역할을 분리해 해석한다.
- 약한 신호, 반례, 흔들린 지점을 숨기지 않는다.
- 과장된 승패 선언, 근거 없는 일반화, `압도적`, `완벽`, `명백히 SOTA` 같은 표현은 피한다.

## Citation

- 관련 논문, 데이터셋, 모델, 실험 리소스가 있으면 끝부분에 `## References` 또는 `## Experiment Resources`로 정리한다.
- 공개 글은 마지막 섹션을 반드시 `## Citation`으로 끝낸다.
- `Citation`에는 사람이 바로 복사할 수 있는 text citation과 BibTeX를 함께 둔다.
