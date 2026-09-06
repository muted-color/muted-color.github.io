# 작업과 검증

실행 명령은 저장소 루트 기준이다. 에이전트의 공통 작업 규칙은 [AGENTS.md](AGENTS.md), 글 편집은 [blog-research-note](.agents/skills/blog-research-note/SKILL.md), 메타데이터는 [SEO.md](SEO.md)를 따른다.

## 환경 준비

Ruby 3.2 이상과 `Gemfile.lock`에 기록된 Bundler를 사용한다. `.ruby-version`은 버전 관리자용 선택이며 스크립트의 최소 요구사항과 구분한다. 필요한 Ruby를 먼저 PATH에 연결한 뒤 처음 설치하거나 의존성이 바뀐 경우에 실행한다.

```bash
bash scripts/jekyll.sh setup
```

`setup`만 Bundler와 gem을 설치한다. 나머지 명령은 설치와 Bundler 설정 쓰기를 하지 않고, 잠금 파일 변경을 막는 `BUNDLE_FROZEN=true`로 실행한다. 새 아키텍처 때문에 lockfile 플랫폼 추가가 필요하면 별도 의존성 변경으로 다룬다.

```bash
bash scripts/jekyll.sh check
bash scripts/check-site.sh
```

`check-site.sh`는 임시 디렉터리에 production/strict-front-matter 빌드를 한 번 수행하고, 홈 출력과 운영 문서 제외를 확인한 뒤 정리한다. 실행 중인 서버의 `_site`를 빌드 대상으로 쓰지 않는다. 이 명령만으로 인용의 정확성, 모든 글의 필수 메타데이터나 시각적 가독성이 검증되지는 않는다.

## 미리보기

```bash
bash scripts/dev-serve.sh
```

기본은 `127.0.0.1:8666`이다. `HOST`와 `PORT`로 변경할 수 있다. LAN binding은 인증 없는 개발 서버를 네트워크에 노출하므로 실제 공유 요청 범위에 맞춘다.

이미 `blog-jekyll.service`가 실행 중인 호스트에서는 두 번째 서버를 시작하지 않는다. 상태 확인은 `systemctl --user status blog-jekyll.service`, 의도한 재시작은 `systemctl --user restart blog-jekyll.service`를 사용한다. 일반 글/지침 검증을 위해 서비스를 재시작할 필요는 없다.

## 글 작업

1. 대상 글, 근거, 언어, 편집 범위와 기존 변경을 확인한다. 신규·큰 개정은 템플릿의 관련 예시를 읽고 근거와 공백을 구분해 작성한다.
2. 필요한 전문 검토만 선택한다. 같은 글을 여러 에이전트가 수정할 때는 영역 소유권을 나누거나 편집을 직렬화한다. 독립적인 읽기 전용 인용·서식 검토는 병렬화할 수 있다.
3. 발견한 문제를 반영하고 아래 표의 해당 검증을 완료한다. 전문가가 확인한 최종 자산의 hash·QA 결과는 변경이 없으면 재사용한다.
4. 결과, 변경 파일, 수행한 검증, 미확인 항목을 보고한다. 공개 준비 검토는 기술 검증이며 배포 승인이나 자동 push를 뜻하지 않는다.

## 변경별 검증

| 변경 | 필요한 확인 |
| --- | --- |
| AGENTS·skill·역할 설정만 수정 | diff, 문서 링크/trigger/역할 충돌, TOML·skill front matter. 현실적인 작업 예로 과도한 읽기·위임·중단 여부 확인. 사이트 빌드는 불필요 |
| 오탈자·작은 문장 수정 | 해당 diff와 근거/용어 보존. HTML 구조·front matter가 안 바뀌면 전체 빌드 불필요 |
| 글 구조·front matter·템플릿·Liquid | 해당 메타데이터/flag/URL, 자산 존재, 번호와 최종 Citation; 격리 빌드 한 번 |
| 본문 SVG·정적 차트 | 시각화 스킬의 validator와 1200px/600px 실제 preview 확인, source 값과 caption 대조. embedding 변경 시 해당 HTML 확인 |
| 공통 CSS·layout·렌더러 | 영향받는 대표 컴포넌트와 모바일 폭 확인, 격리 빌드. 관련 없는 글 전체를 반복 검토하지 않음 |
| 인용 | 해당 원출처의 정체성·metadata와 본문 인용 대응. 구조 변경 시에만 추가 렌더 확인 |
| 실행 스크립트·의존성 | `bash -n` 등 구문 검사, 관련 명령의 성공/실패 동작, 설치된 환경에서 격리 빌드. 설치 테스트는 필요한 경우에만 |
| 최종 공개 준비 | SEO 필수값, 자산·번역 링크, 렌더 flag, 번호, references/Citation, TODO·확인된 비공개 노출, 최종 파일에 해당하는 빌드·시각 QA 근거 |

로컬 서버가 해당 소스를 최신 상태로 제공하면 `curl -fsS --max-time 10 <post-url>`로 필요한 HTML hook을 확인한다. HTTP 200은 시각적 검증을 대신하지 않는다. 서버가 없으면 격리 빌드 결과를 필요한 범위에서 확인하고, 장기 실행 서버를 새로 시작할 필요는 없다.

경로·용어 탐색은 후보 탐지다. 공개 코드의 `outputs/` 같은 일반 경로와 실제 내부 경로를 구분한다. 도구 부재로 확인하지 못한 항목은 실패로 단정하지 않고 검증 공백으로 보고한다. 새 코드 테스트는 실제 동작이나 중요한 불변 조건을 확인할 때 추가한다.

## 발행

이 저장소는 GitHub Pages를 사용하며 현재 저장소에는 `.github/workflows` 배포 정의가 없다. 실제 배포 branch와 build 방식은 원격 `Settings > Pages`를 확인한다. 로컬 지침 감사나 발행 준비 검토만으로 push·배포 설정 변경을 수행하지 않는다. 사용자가 해당 작업을 이미 승인했다면 필요한 로컬 준비와 검증 뒤 진행하며 재승인을 요구하지 않는다.

## 에이전트 설정 유지보수

프로젝트에서 모델을 고정하지 않고 사용자 설정과 세션의 모델 선택을 따른다. 부모의 reasoning effort는 사용자 설정을 유지하고, 좁은 전문 역할은 기존 `medium`을 유지한다. 난도에 따른 effort 변경은 실제 품질·시간 비교로 판단한다. 세션에서 이미 읽은 지침과 역할 설정은 파일 수정만으로 소급 교체되지 않을 수 있으므로 새 세션에서 적용 상태를 확인한다.

공식 가이드 검토 근거와 검증 한계는 [.codex/audit-2026-09-06.md](.codex/audit-2026-09-06.md)에 기록한다. 이 문서는 작업별로 필요한 명령과 완료 조건을 관리하고, 감사 기록은 상시 지침으로 읽지 않는다.
