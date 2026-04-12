# Ilho Ahn Research Blog

GitHub Pages로 운영하는 `미니 리서치 블로그`용 최소 템플릿입니다.

## 포함된 것

- GitHub Pages + Jekyll 기반 최소 구조
- 홈 페이지 1개
- 샘플 포스트 1개
- 기본 스타일 1개
- 404 페이지

## 구조

```text
.
|-- .gitignore
|-- 404.html
|-- Gemfile
|-- README.md
|-- _config.yml
|-- _includes/
|   `-- footer.html
|-- _posts/
|   `-- 2026-04-08-template-kickoff.md
|-- scripts/
|   `-- dev-serve.sh
|-- assets/
|   `-- css/
|       `-- style.scss
`-- index.md
```

## 로컬 실행

권장 실행 스크립트:

```bash
bash scripts/dev-serve.sh
```

필수 조건:

- Ruby 3.2 이상
- macOS 기본 `/usr/bin/ruby` 2.6 환경은 `github-pages` 의존성과 호환되지 않음
- Homebrew 사용 시 `brew install ruby@3.2`

접속 주소:

```text
http://127.0.0.1:8666
```

직접 실행하고 싶다면:

```bash
PATH="/opt/homebrew/opt/ruby@3.2/bin:$PATH" bundle _2.4.22_ install
PATH="/opt/homebrew/opt/ruby@3.2/bin:$PATH" bundle _2.4.22_ exec jekyll serve --port 8666
```

## 글 작성 규칙

- 위치: `_posts/`
- 파일명: `YYYY-MM-DD-title.md`
- Front matter 권장 필드:

```yaml
---
title: "LLM Eval Notes"
date: 2026-04-09 09:00:00 +0900
categories: [research]
tags: [llm, eval]
excerpt: "포스트 목록에 보일 짧은 요약"
---
```

## GitHub Pages 배포

1. 이 저장소를 GitHub에 push
2. `Settings > Pages` 이동
3. 기본 브랜치 루트를 배포 소스로 선택
4. 프로젝트 페이지라면 `_config.yml`의 `baseurl`을 `/<repo-name>`으로 수정

## 시작 전에 바꿀 값

- `_config.yml`의 `title`
- `_config.yml`의 `description`
- `_config.yml`의 `author.name`
