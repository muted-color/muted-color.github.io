# Ilho Ahn Research Blog

GitHub Pages와 Jekyll로 운영하는 연구 블로그입니다. LLM·생명과학 모델의 실험, 평가와 구현 결과를 공개 가능한 근거와 함께 정리합니다.

Site: <https://muted-color.github.io>

## Local development

Ruby 3.2 이상이 필요합니다. 최초 의존성 설치와 일상 실행을 구분합니다.

```bash
bash scripts/jekyll.sh setup
bash scripts/check-site.sh
bash scripts/dev-serve.sh
```

기본 주소는 `http://127.0.0.1:8666`입니다. 이미 서비스가 실행 중이면 두 번째 서버를 시작하지 않습니다. 자세한 환경 준비, 검증 범위, 서비스와 발행 절차는 [WORKFLOW.md](WORKFLOW.md)를 따릅니다.

## Writing

새 글은 `_posts/YYYY-MM-DD-slug.md`로 작성합니다.

| 기준 | 문서 |
| --- | --- |
| 표·Figure·탭·수식·다국어·Citation 예시 | [_posts/2026-04-08-template.md](_posts/2026-04-08-template.md) |
| 연구 노트 편집과 전문 검토 | [.agents/skills/blog-research-note/SKILL.md](.agents/skills/blog-research-note/SKILL.md) |
| 필수 front matter·이미지·출처·검색 노출 | [SEO.md](SEO.md) |
| Codex 작업 범위와 위임 | [AGENTS.md](AGENTS.md) |

비공개 데이터·원본 로그·인증 정보·미승인 실험 결과·내부 경로를 공개 소스에 포함하지 않습니다. `hidden: true`는 접근 제어가 아니며, 웹 빌드에서 제외한 운영 문서도 Git 저장소에는 남습니다.

## Structure

- `_config.yml`: 사이트와 Jekyll 설정
- `_includes/`, `_layouts/`: 공통 HTML과 레이아웃
- `_posts/`, `ko/`, `technical-reports/`: 글과 번역·리포트
- `assets/`: CSS, JavaScript, 이미지
- `scripts/`: 환경 실행·검증과 개별 Figure 생성
- `.agents/skills/`, `.codex/`: 작업별 스킬과 에이전트 설정

기술 구성은 Jekyll, Minima, kramdown, jekyll-seo-tag와 커스텀 Atom feed/sitemap입니다. 실제 GitHub Pages 배포 설정은 원격 `Settings > Pages`에서 확인합니다.
