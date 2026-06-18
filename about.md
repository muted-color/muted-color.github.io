---
layout: default
title: About Me
permalink: /about/
---

{% assign author_name = site.author.name | default: site.title %}
{% assign author_name_ko = site.author.name_ko %}

<img class="about-profile__photo" src="/assets/images/common/ilho-ahn-profile.png" alt="{% if author_name_ko %}{{ author_name_ko }} {% endif %}{{ author_name }} profile photo">
<p class="about-profile__eyebrow">Applied LLM Research Engineer</p>
<h1>{{ author_name | upcase }}</h1>

My interests center on applied LLM research, especially generation quality, evaluation, preference data, and alignment for product-facing language tasks.

## Experience

- CJ Olive Young, Data Scientist / Modeling Lead
- MUSINSA, AI Engineer
- KPMG Lighthouse, Data Scientist / R&D Lead
- KRAFTON, Data Scientist / Data Engineering Lead
- Yello Mobile, Data Engineer

## Selected Work

- Built Gemma-based sLLM workflows for recommendation-card generation, including QLoRA/PEFT training, NLL-based quality evaluation, and DPO/GRPO alignment.
- Trained semantic retrieval models with weak supervision from search logs and product interaction signals.
- Developed multimodal classification and document-understanding pipelines across fashion, finance, and game-service domains.

## Awards & Sharing

- AWS Summit Seoul 2019 Speaker
  Presented a case study on MMORPG anomaly detection. [Video](https://www.youtube.com/watch?v=9tkGgR9xyNs){:target="_blank" rel="noopener noreferrer"}, [Slides](https://www.slideshare.net/awskorea/mmorpg-abuser-detection-with-sagemaker-krafton-krafton-aws-summit-seoul-2019-141257125){:target="_blank" rel="noopener noreferrer"}
- Big Contest 2016, Korea National Information Society Agency Award
- OSS World Challenge 2015, Gold Prize for [ErRabbit](https://github.com/soleaf/ErRabbit){:target="_blank" rel="noopener noreferrer"}

## Links

- LinkedIn: [linkedin.com/in/soleaf](https://www.linkedin.com/in/soleaf/){:target="_blank" rel="noopener noreferrer"}
- Blog: [flonelin.wordpress.com](https://flonelin.wordpress.com){:target="_blank" rel="noopener noreferrer"}
- GitHub: [github.com/muted-color](https://github.com/muted-color){:target="_blank" rel="noopener noreferrer"}
- GitHub: [github.com/oy-ilho](https://github.com/oy-ilho){:target="_blank" rel="noopener noreferrer"}
