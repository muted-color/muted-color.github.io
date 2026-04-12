# Ilho Ahn Research Blog

GitHub Pages와 Jekyll로 운영하는 개인 리서치 블로그입니다.

Site: <https://muted-color.github.io>

## Overview

이 저장소는 정적 블로그의 소스 코드와 글 원고를 관리합니다.

주요 목적은 다음 내용을 공개 가능한 범위에서 정리하는 것입니다.

- LLM 실험 기록
- 모델 fine-tuning 및 evaluation 노트
- 구현 과정에서 얻은 기술 메모
- 연구 결과 요약과 시각화 자료

## Tech Stack

- GitHub Pages
- Jekyll
- Minima theme
- kramdown
- jekyll-feed
- jekyll-seo-tag
- Ruby / Bundler

## Local Development

권장 실행 방법:

```bash
bash scripts/dev-serve.sh
```

기본 접속 주소:

```text
http://127.0.0.1:8666
```

필수 조건:

- Ruby 3.2 이상
- Bundler

macOS 기본 Ruby 환경은 GitHub Pages 의존성과 호환되지 않을 수 있습니다.

## Writing Posts

새 글은 `_posts/` 아래에 작성합니다.

파일명 규칙:

```text
YYYY-MM-DD-title.md
```

Front matter 예시:

```yaml
---
title: "Post Title"
date: 2026-04-12 09:00:00 +0900
categories: [research]
tags: [llm, eval]
excerpt: "포스트 목록에 표시될 짧은 요약"
---
```

## Project Structure

```text
.
├── _config.yml          # Jekyll 설정
├── _includes/           # 공통 HTML 조각
├── _layouts/            # 페이지 레이아웃
├── _posts/              # 블로그 글
├── assets/              # 스타일과 이미지
├── scripts/dev-serve.sh # 로컬 개발 서버 실행 스크립트
├── 404.html             # 404 페이지
├── about.md             # 소개 페이지
└── index.md             # 홈
```

## Deployment

이 저장소는 GitHub Pages로 배포합니다.

배포 흐름:

1. 변경 사항을 기본 브랜치에 push합니다.
2. GitHub Pages가 Jekyll 사이트를 빌드합니다.
3. 빌드가 완료되면 사이트에 반영됩니다.

배포 설정은 GitHub repository의 `Settings > Pages`에서 확인할 수 있습니다.

## Public Content Guidelines

이 저장소는 공개될 수 있으므로 글이나 설정 파일에 아래 내용을 포함하지 않습니다.

- API key, access token, password, private key
- 비공개 데이터셋, 원본 로그, 고객 또는 회사 내부 정보
- 공개 허가를 받지 않은 실험 결과나 벤치마크 수치
- 개인 연락처, 계정 정보, 로컬 환경 경로
- 재배포 권한이 불명확한 이미지, 표, 문서, 코드

민감할 수 있는 내용은 공개 가능한 수준으로 요약하거나 익명화한 뒤 작성합니다.

## Configuration

주요 사이트 설정은 `_config.yml`에서 관리합니다.

- 사이트 제목과 설명
- 사이트 URL과 base URL
- 작성자 표시 이름
- 언어와 시간대
- Jekyll 플러그인 설정
