# SEO 작성 가이드

블로그 글의 SEO는 숨김 텍스트나 `meta keywords`가 아니라, 검색엔진이 읽기 쉬운 front matter와 구조화 데이터로 관리한다.

## 필수 Front Matter

공개 글은 아래 값을 둔다.

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
