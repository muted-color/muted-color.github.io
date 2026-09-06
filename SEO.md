# SEO 작성 가이드

블로그 글의 SEO는 숨김 텍스트나 `meta keywords`가 아니라, 검색엔진이 읽기 쉬운 front matter와 구조화 데이터로 관리한다.

## 필수 Front Matter

공개 연구 글은 아래 값을 둔다. `hero_image`와 `hero_alt`는 본문 hero가 있을 때만 필요하다. 일반 소개·목록 페이지에 연구 글의 필수 항목을 일괄 적용하지 않는다.

```yaml
title: "검색 결과에서 잘려도 핵심 질문이 남는 제목"
date: 2026-04-19 10:50:00 +0900
last_modified_at: 2026-04-19 15:45:00 +0900
categories: ["PROTEIN ML"]
tags: [protein, esm2, low-label]
excerpt: "목록 카드와 RSS에서 쓸 짧은 요약."
description: "검색 결과 snippet 후보로 쓸 한 문장 요약. 실험 대상, 질문, 결론 또는 한계를 함께 담는다."
image: /assets/images/posts/post-slug/social-thumbnail.png
image_alt: "소셜/검색 대표 이미지가 무엇을 요약하는지 설명"
hero_image: /assets/images/posts/post-slug/hero.svg
hero_alt: "본문 hero 이미지의 내용 설명"
```

## 작성 규칙

- `description`은 `excerpt`보다 검색 결과용으로 더 명확하게 쓴다.
- `description`에는 실험 대상, 비교 축, 결론 또는 caveat를 한 문장으로 넣는다.
- `last_modified_at`은 본문, 수치, 해석, 메타 설명을 실제로 고친 날만 갱신한다.
- `tags`는 사람이 읽는 주제 분류이자 JSON-LD `keywords`로 쓰인다.
- `categories`의 첫 값은 JSON-LD `articleSection`으로 쓰인다.
- `image`는 PNG/JPG 대표 이미지로 둔다. SVG hero만 두지 않는다.
- `image_alt`는 대표 이미지 설명이다. 키워드를 반복하지 않는다.
- `hero_alt`는 본문 이미지 접근성 설명이다. `image_alt`와 역할이 다를 수 있다.

## 렌더링과 URL

- LaTeX는 `math: true`, Mermaid는 `mermaid: true`, Plotly는 `plotly: true`를 둔다. 사용하지 않는 flag는 새로 추가하지 않는다.
- `_posts`의 URL은 `_config.yml`의 permalink 규칙을 기본으로 쓴다. 모든 글에 개별 `permalink`를 강제하지 않는다. 기존 공개 URL과 발행일은 요청 없이 변경하지 않는다.
- 영문 원문·국문 번역은 각각 `lang`과 서로를 가리키는 `translation_url`을 둔다. 국문 page의 `layout: post`와 `permalink` 예시는 템플릿의 다국어 섹션을 따른다.
- `hidden: true`는 목록·feed·sitemap에서 제외하고 robots meta에 `noindex, nofollow, noarchive`를 넣지만 URL 접근을 막지 않는다. 검색만 제외하려면 `noindex: true`, 빌드 대상에서 제외할 초안에는 `published: false`를 사용한다.
- 대표 이미지 기본 크기·스타일과 Figure 제작은 글쓰기 스킬의 `references/visuals.md`, 실제 embedding은 템플릿을 따른다.

## 실험 출처

실험 기반 글은 확인된 `lab_host`와 `lab_path`를 함께 둔다. `lab_path`는 `~/lab/` 뒤의 상대 경로다. 실제 프로젝트 위치를 확인하지 않고 host나 예전 경로를 일괄 보정하지 않는다. 현재 템플릿의 host 값은 `dgx1` 또는 `dgx3`이며, 다른 위치가 확인되면 그 근거에 따라 기록한다.

```yaml
lab_host: "dgx1"
lab_path: "projects/project-slug"
```

이 두 필드는 원문 위치를 찾는 편집용 메타데이터다. 본문·caption·자산·코드 주석에 절대 로컬 경로나 비공개 run 식별자를 복사하지 않는다. 공개된 코드 예제의 일반 상대 경로는 비공개 노출로 단정하지 않는다. Git 저장소 자체에 남기는 정보도 공개 가능한 범위인지 확인한다.

## 피할 것

- 검색용 숨김 텍스트를 추가하지 않는다.
- `display: none`으로 키워드나 이름을 넣지 않는다.
- `meta keywords`를 추가하지 않는다.
- `alt`에 검색 키워드를 나열하지 않는다.
- 제목과 설명에서 과장된 승패 선언을 하지 않는다.

## 구조화 데이터

`_includes/head.html`에서 다음 값을 자동으로 구조화 데이터에 연결한다.

- `author.name`, `author.alternate_names`, `author.same_as`
- `page.title`
- `page.description`
- `page.date`
- `page.last_modified_at`
- `page.image`
- `page.image_alt`
- `page.tags`
- `page.categories`

Google 문서 기준으로 Article 구조화 데이터에는 `author`, `datePublished`, `dateModified`, `headline`, `image` 같은 값이 도움이 된다. 이미지 SEO에서는 표준 `<img>`와 자연스러운 `alt` 설명을 권장한다.

## 참고

- [Google Search Central: Article structured data](https://developers.google.com/search/docs/appearance/structured-data/article)
- [Google Search Central: Meta descriptions](https://developers.google.com/search/docs/appearance/snippet)
- [Google Search Central: Image SEO](https://developers.google.com/search/docs/appearance/google-images)
