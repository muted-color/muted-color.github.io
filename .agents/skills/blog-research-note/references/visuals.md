# 시각 자료

본문 Figure는 이미 있는 근거 하나를 압축한다. 정확한 숫자 조회가 핵심이면 표를 유지한다. 단순 graph를 Markdown 안에서 관리할 이유가 있으면 Mermaid, hover·zoom·legend toggle이 해석에 필요하면 Plotly를 선택한다.

## 본문 도식과 정적 차트

- 새 도식과 compact 정적 차트는 `$editorial-systems-figure`를 기본 경로로 사용한다. 설치된 스킬의 `SKILL.md`와 해당 reference를 읽고 그 위치에서 스크립트를 찾는다. 사용자 홈의 절대 경로를 저장소에 고정하지 않는다.
- `palette: editorial`이 기본이다. 출처가 정의한 색 자체에 의미가 있을 때만 `palette: source`를 쓴다. 범주마다 새 색을 부여하지 않는다.
- SVG에는 작은 sentence-case 제목 하나만 둔다. subtitle, takeaway, 해석, 출처와 caption은 SVG 밖에 둔다.
- 원자료의 수치, 단위, 축 범위, 구간, 순서, 결측 의미를 보존하고 conceptual/measured scale을 구분한다. local axis, normalization, z-score, 방향 반전, smoothing을 사용하면 caption에 밝힌다. 보기 좋게 하려고 값을 만들거나 비교점을 제거하지 않는다.
- 불확실성, seed/split 변동, candidate-space filter와 calibration 조건이 해석을 바꾸면 표시한다. 지표 방향이 불명확한 우열 강조는 하지 않는다. 참조 구조 이미지는 직접 실험 근거가 아니면 context로 표시한다.
- `assets/images/posts/<post-slug>/`에 descriptive kebab-case 이름으로 저장한다. JSON이 재생성 원천이면 `<figure-name>.figure.json`을 SVG 옆에 보존하고 비공개 경로·식별자를 제거한다.
- `render_figure.py`, `validate_figure.py`, `rasterize_figure.py`를 사용한다. 1200px와 600px preview를 실제로 열어 overflow, collision, palette, 축소 가독성을 확인한다. preview는 임시 위치에 둔다. 작은 글자로 밀도를 해결하지 않고 구성이나 문구를 조정한다.
- 새 custom SVG도 viewBox, title, desc, editable text와 같은 검증을 갖춘다. legacy SVG에 새 renderer 출처를 소급해서 요구하지 않는다.
- `<figure class="media-figure">` 또는 `media-figure--wide-visual` 안에 유용한 `alt`, 번호가 맞는 `<figcaption>`과 함께 넣는다. alt는 보이는 요소와 변수를 설명한다.

## 대표 이미지와 hero

- 본문 Figure와 별도 자산이다. 기본 대표 이미지는 HSPC hierarchy / TrpB local fitness 글처럼 흰 배경, 반투명 glass/gel 과학 오브젝트, 옅은 파란색 강조, 텍스트 없는 `1200x627` PNG/JPG다.
- 기본 위치는 `assets/images/posts/<post-slug>/social-thumbnail.png`; `image`와 `image_alt`를 함께 갱신한다. hero 메타데이터는 `SEO.md`를 따른다.
- SVG hero를 대표 이미지로 쓰려면 별도 raster 자산을 연결한다. 대표 이미지가 반드시 hero의 복제일 필요는 없다. AI bitmap 생성·편집은 사용 가능한 이미지 생성 도구와 해당 스킬을 쓴다.

자산 제작이 할당 범위 밖이거나 근거가 없으면 필요한 값, 단위·방향, scale, caption/alt와 누락 사항을 부모에게 전달한다. 완료 보고에는 renderer 검증과 두 preview의 확인 여부를 구분하고, 이후 변경이 없으면 최종 검토자가 이 QA를 재사용할 수 있게 한다.
