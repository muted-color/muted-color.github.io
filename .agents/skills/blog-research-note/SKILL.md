---
name: blog-research-note
description: Draft, revise, format, or review research posts in this Jekyll blog, including citations and evidence figures. Use for article work, not unrelated infrastructure, model experiments, or general coding.
---

# Blog research note

공개 독자가 평가 조건과 근거의 한계를 확인할 수 있는 미니 리서치 노트를 만든다. 사용자의 요청 범위, 대상 글의 언어, 기존 데이터와 해석을 보존한다.

## 작업 선택

저장소 루트를 기준으로 파일을 찾는다. 현재 작업에 필요한 참조만 읽고, 여러 종류의 작업을 요청받았을 때만 경로를 조합한다.

| 작업 | 읽을 참조 | 산출물 |
| --- | --- | --- |
| 새 글·큰 구조 개정 | [editorial.md](references/editorial.md), `_posts/2026-04-08-template.md`의 관련 예시 | 근거에 연결된 초안, 남은 정보 공백 |
| 문체·표·수식·caption·Appendix | [formatting.md](references/formatting.md), 문체 변경 시 editorial.md | 의미를 보존한 최소 수정 |
| 본문 도식·차트·대표 이미지 | [visuals.md](references/visuals.md) | 요청된 자산, 재생성 원천, 해당 QA 결과 |
| 논문·모델·데이터셋·BibTeX 확인 | [citations.md](references/citations.md) | 확인한 원출처와 일치하는 인용 |
| Front matter·공개 준비 검토 | `SEO.md`, `WORKFLOW.md`의 검증 표 | 위치가 있는 발견 사항과 검증 한계 |

## 적용 기준

- 대상 파일, 요청된 수정 또는 읽기 전용 범위, 공개 가능한 근거를 확인한다. 오탈자 수정에 전체 스타일 비교나 모든 리뷰 역할을 추가하지 않는다.
- 새 글과 큰 구조 변경은 템플릿을 확인한다. 스타일 선택이 필요한 경우에만 비슷한 기존 글 1–2개를 비교한다. 전체 글 검색은 사이트 전체 감사에 한정한다.
- 수치·방법 의미·순위·결론을 원자료에 연결한다. 충돌하는 값은 임의로 고르지 않는다. 작성 중 필요한 근거가 없으면 정확한 `[TODO: 필요한 근거]`를 남기고 독립 부분을 완성한다. 읽기 전용 검토는 TODO를 삽입하지 않고 보고한다.
- 메타데이터는 `SEO.md`, 표현 예시는 템플릿, 실행과 완료 검증은 `WORKFLOW.md`가 기준이다. 같은 규칙을 에이전트 설정과 README에 복제하지 않는다.
- 공개 연구 글은 관련 `References` / `Experiment Resources` 목록을 `<div class="reference-list" markdown="1">`로 감싸고, 마지막 `## Citation`에 복사 가능한 text citation과 BibTeX를 함께 둔다. 원출처의 사실 확인은 인용 경로를 따른다.
- 근거·필수 자산·인용이 미완성인 새 글은 `published: false` 초안으로 둔다. 기존 공개 글은 요청 밖의 발행 상태 변경이나 근거 없는 TODO 삽입 대신 미확인 항목을 보고한다.
- 기존 영어/한국어와 `translation_url`을 유지한다. 새 글의 언어는 사용자 선택을 우선하고 선택이 없으면 요청 언어를 기본으로 삼는다.
- 관련 없는 환경 변경·실험 실행·배포는 이 스킬의 일부가 아니다. 필요한 도구가 없으면 해당 산출물의 미확인 범위를 명시하고 가능한 작업을 계속한다.

완료 보고에는 변경 파일, 근거 또는 인용 공백, 실제 수행한 검증을 포함한다. 검토만 요청받았다면 파일·위치·영향·수정 제안을 반환한다.
