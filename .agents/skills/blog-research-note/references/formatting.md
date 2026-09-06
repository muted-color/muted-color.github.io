# 서식과 읽기 흐름

표·모델 카드·탭·sample 비교·수식·Appendix는 `_posts/2026-04-08-template.md`의 해당 예시를 따른다. 공통 CSS는 기존 글에 미치는 영향을 확인하고 작은 재사용 utility로 확장한다.

- 표의 column명, 본문, caption 용어를 맞춘다. 숫자 열은 `align-right`, 긴 method명은 의미 단위 `<br>`와 `table-note-inline`을 사용한다.
- 숫자표에는 `metrics-table`, 조건 설명표에는 `comparison-table`을 검토한다. 작은 2열 숫자표는 `table-figure--compact-metrics`와 `metrics-table--compact-two-col`을 우선한다.
- `is-better`와 굵은 수치는 비교 단위와 지표 방향이 명확할 때 사용한다.
- Figure/Table 번호를 본문에서 언급하고 caption은 무엇을 보여주며 어떻게 읽는지 설명한다. hero caption이 Figure 1이면 본문은 Figure 2부터 시작한다. Sample과 Appendix 번호는 각각의 계열을 유지한다.
- 수학 표현은 `<code>`가 아닌 LaTeX로 쓴다. 렌더링 flag와 이미지 메타데이터는 `SEO.md`를 따른다.
- Mermaid는 `<figure class="media-figure" markdown="1">`로 감싸 caption을 붙인다. Plotly는 템플릿의 `plot-card` / `js-plotly-chart` 패턴을 따른다.
- 서식 편집이 caption·본문의 주장 강도나 방법 의미를 바꾸면 안 된다. 수치·결론의 모순은 근거 위치와 함께 보고한다.
- DOI·저자·BibTeX의 사실 확인은 인용 검토로, 자산 변경과 시각 QA는 시각화 작업으로 넘긴다. 역할 경계는 기초적인 자체 확인을 생략할 이유가 아니다.

수정 부분의 용어·번호·경로·flag를 점검한다. HTML 확인이나 공통 스타일 검증은 `WORKFLOW.md`의 변경별 검증 범위를 따른다.
