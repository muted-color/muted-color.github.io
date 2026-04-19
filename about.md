---
layout: default
title: About Me
permalink: /about/
---

{% assign author_name = site.author.name | default: site.title %}
{% assign author_name_ko = site.author.name_ko %}

<img class="about-profile__photo" src="/assets/images/common/ilho-ahn-profile.png" alt="{% if author_name_ko %}{{ author_name_ko }} {% endif %}{{ author_name }} 프로필 사진">
<p class="about-profile__eyebrow">About Me</p>
<h1>{{ author_name | upcase }}</h1>
Applied AI Researcher로서 자연어와 비전 모델링을 통해 다양한 도메인의 문제를 해결하고 있습니다.

## Experience

- CJ 올리브영, Data Scientist / Modeling Lead
- 무신사, AI Engineer
- KPMG Lighthouse, Data Scientist / Technical Lead
- 크래프톤, Data Scientist / DE Team Lead
- 옐로모바일, Data Scientist

## Awards & Sharing

- AWS Summit Seoul 2019 Speaker
  MMORPG 이상 행위 탐지 모델 사례를 발표 [Video](https://www.youtube.com/watch?v=9tkGgR9xyNs){:target="_blank" rel="noopener noreferrer"}, [Slides](https://www.slideshare.net/awskorea/mmorpg-abuser-detection-with-sagemaker-krafton-krafton-aws-summit-seoul-2019-141257125){:target="_blank" rel="noopener noreferrer"}
- Big Contest 2016 한국정보화진흥원장상
  보험 사기 예측 모델 프로젝트로 수상
- OSS World Challenge 2015 금상
  서버 로그 시각화 서비스 [ErRabbit](https://github.com/soleaf/ErRabbit){:target="_blank" rel="noopener noreferrer"} 프로젝트로 수상

## Links

- LinkedIn: [linkedin.com/in/soleaf](https://www.linkedin.com/in/soleaf/){:target="_blank" rel="noopener noreferrer"}
- GitHub: [github.com/oy-ilho](https://github.com/oy-ilho){:target="_blank" rel="noopener noreferrer"}
- Blog: [flonelin.wordpress.com](https://flonelin.wordpress.com){:target="_blank" rel="noopener noreferrer"}
