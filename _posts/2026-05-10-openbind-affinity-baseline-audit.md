---
title: "OpenBind affinity score의 MW+cLogP confounding 점검"
date: 2026-05-10 18:40:00 +0900
last_modified_at: 2026-05-10 20:37:58 +0900
categories: ["CHEM ML"]
tags: [openbind, affinity-prediction, structure-based-ai, ligand-baseline, benchmark-audit, rdkit, ecfp]
lab_path: "experiment-lab/projects/openbind-affinity-baseline-stress"
excerpt: "OpenBind EV-A71 2A affinity release에서 raw pKD 상관과 MW+cLogP residual signal을 분리해 공개 prediction files와 동일 campaign supervised ligand-only control을 비교한 sanity-check audit."
description: "OpenBind EV-A71 2A compound-level affinity release에서 MW/cLogP/series progression confounding을 공개 artifact 기준으로 수치화하고, raw pKD correlation 해석의 한계를 정리한 sanity-check audit."
permalink: /research/2026/05/10/openbind-affinity-baseline-audit/
image: /assets/images/posts/openbind-affinity-baseline-audit/social-thumbnail.png
image_alt: "OpenBind EV-A71 2A affinity audit에서 raw Spearman과 MW+cLogP residual Spearman을 method별로 비교한 대표 차트"
hero_image: /assets/images/posts/openbind-affinity-baseline-audit/raw-vs-residual-spearman.png
hero_alt: "OpenBind EV-A71 2A compound-level audit에서 published prediction files와 ligand-only controls의 raw pKD Spearman 및 MW+cLogP residual Spearman을 비교한 차트"
hero_caption: "<strong>Figure 1.</strong> OpenBind EV-A71 2A compound-level affinity audit에서 raw pKD Spearman과 MW+cLogP residual Spearman을 나란히 비교했다. ECFP ridge는 published prediction files의 직접 경쟁자가 아니라, 기본 확인 항목인 동일 campaign supervised ligand-only control로 둔다."
hero_frame: true
hero_compact: true
hidden: true
published: false
---

OpenBind의 첫 공개 release는 EV-A71 2A protease를 대상으로 structure, affinity measurement, reference benchmark를 함께 제공한다 <a class="citation-ref" href="#ref-openbind-first-release" aria-label="Reference 1">[1]</a>. 이 글은 그중 affinity prediction 결과를 compound-level retrospective audit으로 다시 읽는다. 목적은 새로운 confounding을 발견하는 것이 아니라, ligand size, lipophilicity, series progression이 raw affinity ranking에 섞일 수 있다는 기본 점검을 이 공개 release에서 실제 수치로 고정하는 데 있다.

평가 질문은 좁다. **published affinity prediction score의 raw pKD 상관이 MW와 cLogP 같은 ligand-property signal을 제거한 뒤에도 남는가**를 확인한다. 이 release에서는 published prediction files가 raw pKD signal은 보였지만, MW+cLogP residual target에서는 동일 campaign label을 사용한 supervised ligand-only control보다 약한 signal을 남겼다.

이 결과는 OpenBind 전체나 structure-based affinity prediction 일반에 대한 판정이 아니다. MW/cLogP confounding 자체가 뜻밖의 발견이라는 주장도 아니다. OpenBind release의 장점은 이런 기본 sanity check를 공개 artifact 위에서 수치화할 수 있을 만큼 데이터와 benchmark가 정리되어 있다는 데 있다.

> **pKD**는 binding affinity를 로그 스케일로 표현한 값이다. 이 글에서는 affinity가 높은 compound가 더 높은 pKD를 갖는 ranking 문제로 해석한다.
>
> **MW+cLogP residual target**은 pKD를 molecular weight와 cLogP로 설명한 뒤, 그 선형 trend로 설명되지 않고 남은 부분을 뜻한다. 이는 structure-aware affinity signal의 정답이 아니라, ligand-property confounding을 점검하기 위한 diagnostic target이다.

이 글에서 **published prediction files**는 OpenBind benchmark repository에 공개된 affinity prediction files를 뜻한다. **supervised ligand-only control**은 같은 campaign의 affinity label로 학습한 ECFP/RDKit 계열 control이며, published files와 같은 조건의 외부 예측 제출물이 아니라 campaign-level residual SAR 기준선이다.

{% include model-mention-cards.html label="사용한 공개 리소스" aria_label="OpenBind release와 benchmark 리소스" models="OpenBind first release|EV-A71 2A structure-affinity dataset|https://openbind.uk/news/blog-openbinds-first-release-a-structure-affinity-dataset-for-structure-based-ai/;Affinity data note|OpenBind affinity and kinetics data|https://openbind.uk/news/blog-affinity-and-kinetics-data-in-the-ev-a71-2a-openbind-release/;EV-A71 2A benchmark|OpenBind GitHub affinity files|https://github.com/OpenBind-Consortium/EV-A71_2A_benchmark/tree/main/affinity;Zenodo release|OpenBind structure-affinity data|https://zenodo.org/records/20026661" %}

## 요약

- OpenBind EV-A71 2A affinity release를 compound-level retrospective audit으로 점검했다. 핵심은 새로운 confounding의 발견이 아니라, MW/cLogP/series progression confounding을 공개 release에서 수치화한 sanity check다.
- Clean compound-level table은 `494` compounds, `494` valid RDKit molecules, `7` published prediction methods로 고정됐고, MW alone raw pKD Spearman은 `0.484`였다.
- MW+cLogP descriptive model은 pKD variance `R2 = 0.299`를 설명했다. 이후 비교는 이 두 property로 residualize한 target에서 진행했다.
- Best published raw method는 `gnina_crystal` raw Spearman `0.453`였지만, best published residual method는 `boltz_2` residual Spearman `0.097`에 머물렀다.
- 동일 campaign label을 사용한 supervised ligand-only control인 `cv_ecfp_ridge`는 residual Spearman `0.430`을 보였다. Grouped sensitivity에서도 published-minus-ligand-control residual delta는 `-0.323`으로 유지됐다.
- Simple distance-count pose-contact feature는 ECFP residual model에 additive signal을 보이지 않았다. `ECFP+pose_contacts - ECFP = -0.081`, bootstrap CI `[-0.146, -0.012]`였다.

## 평가 설정

OpenBind release는 EV-A71 2A protease에 대해 crystallographic binding events, affinity measurements, benchmark files를 함께 제공한다. OpenBind의 benchmark repository는 row-level affinity file, reference table, prediction files, score conversion, compound-level averaging 규칙을 공개한다 <a class="citation-ref" href="#ref-openbind-github" aria-label="Reference 3">[3]</a>. Affinity note는 `all_affinity_data_release_v1.csv`가 analyte-cycle fit 단위의 row-level measurement를 담고, `Used in analysis` flag로 analysis inclusion을 표시한다고 설명한다 <a class="citation-ref" href="#ref-openbind-affinity-note" aria-label="Reference 2">[2]</a>.

이 audit의 첫 단계인 `r001`은 official compound-level prediction table을 method/SMILES key level에서 재현했다. 분석 단위는 row-level affinity가 아니라 clean compound-level table이다. 이 설정은 prospective discovery split이나 새 모델 비교가 아니라, 공개 release 안에서 raw affinity correlation과 residual affinity signal을 분리하는 retrospective sanity check다.

Table 1은 이 글에서 비교 단위로 고정한 compound-level data contract를 요약한다.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table metrics-table--compact-two-col">
      <thead>
        <tr>
          <th>item</th>
          <th class="align-right">value</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>row-level affinity rows</td><td class="align-right"><code>2733</code></td></tr>
        <tr><td>rows marked <code>Used in analysis</code></td><td class="align-right"><code>1613</code></td></tr>
        <tr><td>structure reference rows</td><td class="align-right"><code>925</code></td></tr>
        <tr><td>official compound prediction rows</td><td class="align-right"><code>3458</code></td></tr>
        <tr><td>clean compound-level rows</td><td class="align-right"><code>494</code></td></tr>
        <tr><td>valid RDKit molecules</td><td class="align-right"><code>494</code></td></tr>
        <tr><td>prediction methods</td><td class="align-right"><code>7</code></td></tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 1.</strong> 이 audit에서 고정한 compound-level data contract다. Row-level affinity measurement를 직접 모델링하지 않고, official compound-level prediction table과 같은 method/SMILES key 단위에서 sanity check를 수행했다.</figcaption>
</figure>

## Ligand-property 기준선

Raw pKD에서는 molecular weight 자체가 Spearman `0.484`를 보였다. MW+cLogP descriptive model도 pKD variance `R2 = 0.299`를 설명했다. Simple ligand-property baseline을 확인해야 한다는 점은 affinity benchmark 해석의 기본 전제다. 이 audit에서 수치화한 부분은 그 전제가 OpenBind EV-A71 2A compound-level release 안에서 raw pKD correlation을 해석할 때 어느 정도의 크기로 작동하는지다.

Figure 2는 molecular weight와 pKD의 raw 관계를 먼저 보여준다.

<figure class="media-figure">
  <img src="/assets/images/posts/openbind-affinity-baseline-audit/pkd-vs-mw.png" alt="OpenBind EV-A71 2A compound-level table에서 molecular weight와 pKD의 양의 관계를 보여주는 산점도">
  <figcaption><strong>Figure 2.</strong> Molecular weight와 pKD의 raw 관계다. MW alone Spearman은 <code>0.484</code>였고, 이는 raw affinity ranking을 해석할 때 먼저 확인해야 하는 ligand-property sanity check로 사용했다.</figcaption>
</figure>

이후 비교는 pKD를 MW+cLogP에 대해 residualize한 target에서 진행했다. 이 residual target은 실제 medicinal chemistry에서 제거해야 할 모든 signal을 뜻하지 않는다. Compound elaboration, lipophilicity, potency progression은 campaign 안에서 실제 SAR와 얽힐 수 있다. 따라서 residualization은 “진짜 affinity signal”의 정답이 아니라, raw correlation이 얼마나 coarse property trend에 의존하는지 보는 diagnostic이다.

Table 2는 residual target을 만들기 전에 확인한 ligand-property 기준선이다.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>baseline</th>
          <th>metric</th>
          <th class="align-right">value</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>molecular weight</td>
          <td>raw pKD Spearman</td>
          <td class="align-right"><code>0.484</code></td>
        </tr>
        <tr>
          <td>MW+cLogP linear model</td>
          <td>descriptive <code>R2</code></td>
          <td class="align-right"><code>0.299</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 2.</strong> Raw pKD를 해석하기 전에 확인한 ligand-property baseline이다. MW+cLogP는 model comparison의 최종 기준이 아니라, 공개 release에서 confounding 규모를 고정하기 위한 descriptive control이다.</figcaption>
</figure>

## Residual affinity 신호

MW+cLogP residual target에서 best published prediction은 `boltz_2`였고 residual Spearman은 `0.097`이었다. 반면 `cv_ecfp_ridge`는 residual Spearman `0.430`을 보였다.

여기서 `cv_ecfp_ridge`는 published prediction files의 직접 경쟁자가 아니다. 같은 campaign 안에서 affinity label을 사용해 학습한 supervised ligand-only control이다. 이 control의 역할은 published score를 대체하는 것이 아니라, 단순한 ligand representation만으로도 residual SAR가 얼마나 잡히는지 확인하는 데 있다.

Table 3은 이 역할 구분을 유지한 채 residual Spearman의 주 비교만 압축한다.

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>method role</th>
          <th>best method</th>
          <th class="align-right">residual Spearman</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>published prediction file</td>
          <td><code>boltz_2</code></td>
          <td class="align-right"><code>0.097</code></td>
        </tr>
        <tr>
          <td>동일 campaign supervised<br><span class="table-note-inline">ligand-only control</span></td>
          <td><code>cv_ecfp_ridge</code></td>
          <td class="align-right"><code>0.430</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 3.</strong> MW+cLogP residual target에서의 주 비교다. Delta는 best published residual Spearman에서 best supervised ligand-only residual Spearman을 뺀 값이며, unrounded values 기준 <code>-0.334</code>였다.</figcaption>
</figure>

Figure 1은 같은 결과를 raw Spearman과 residual Spearman으로 나눠 보여준다. `gnina_crystal`은 published methods 중 raw pKD Spearman이 가장 높았지만, residual target에서는 약해졌다. 반대로 ECFP/RDKit 계열 supervised ligand-only controls는 raw signal뿐 아니라 residual target에서도 더 강하게 남았다.

이 차이는 “ECFP가 structure-aware affinity model보다 좋은 일반 모델”이라는 결론이 아니다. 같은 dense campaign 안에서는 ligand-only supervised control이 close analog SAR를 잡을 수 있다. 그럼에도 이 control이 필요한 이유는 분명하다. Raw pKD correlation만 보고 published score의 structure-aware affinity signal을 주장하면, molecular size, cLogP, series progression, close analog similarity가 섞인 signal을 과대 해석할 수 있다.

## Grouped sensitivity 점검

Bootstrap interval은 published residual signal이 완전히 0으로만 고정되지는 않는다는 점을 남긴다. `boltz_2` residual Spearman mean은 `0.096`, 95% CI `[0.008, 0.179]`였고, `cv_ecfp_ridge`는 `0.429`, 95% CI `[0.354, 0.497]`였다.

Table 4는 residual Spearman bootstrap interval을 method별로 정리한다.

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>method</th>
          <th class="align-right">residual Spearman mean</th>
          <th class="align-right">95% CI</th>
        </tr>
      </thead>
      <tbody>
        <tr><td><code>cv_ecfp_ridge</code></td><td class="align-right"><code>0.429</code></td><td class="align-right"><code>[0.354, 0.497]</code></td></tr>
        <tr><td><code>cv_rdkit_descriptor_rf</code></td><td class="align-right"><code>0.337</code></td><td class="align-right"><code>[0.258, 0.413]</code></td></tr>
        <tr><td><code>cv_rdkit_descriptor_ridge</code></td><td class="align-right"><code>0.263</code></td><td class="align-right"><code>[0.175, 0.345]</code></td></tr>
        <tr><td><code>boltz_2</code></td><td class="align-right"><code>0.096</code></td><td class="align-right"><code>[0.008, 0.179]</code></td></tr>
        <tr><td><code>gnina_crystal</code></td><td class="align-right"><code>0.015</code></td><td class="align-right"><code>[-0.073, 0.104]</code></td></tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 4.</strong> Residual Spearman bootstrap interval이다. Best published residual signal은 약하게 양수로 남지만, 이 sanity check에서는 supervised ligand-only controls와 같은 범위로 올라오지는 않았다.</figcaption>
</figure>

Grouped sensitivity에서도 결론은 뒤집히지 않았다. Best grouped published residual mean은 `0.098`, best grouped supervised ligand-only residual mean은 `0.421`, grouped delta는 `-0.323`이었다.

Figure 3과 Table 5는 이 sensitivity check의 결과와 group support를 나눠 보여준다.

<figure class="media-figure">
  <img src="/assets/images/posts/openbind-affinity-baseline-audit/butina-grouped-residual-spearman.png" alt="Butina Tanimoto 0.6 cluster grouping에서 method별 residual Spearman 분포를 비교한 차트">
  <figcaption><strong>Figure 3.</strong> Butina Tanimoto 0.6 cluster 기준 grouped residual Spearman sensitivity다. 결론은 뒤집히지 않았지만, grouping 자체는 singleton-heavy라 prospective scaffold split이 아니라 민감도 점검으로 해석한다.</figcaption>
</figure>

<figure class="table-figure table-figure--comparison table-figure--compact-metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>group type</th>
          <th class="align-right">groups</th>
          <th class="align-right">singleton fraction</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Murcko scaffold</td>
          <td class="align-right"><code>275</code></td>
          <td class="align-right"><code>82.2%</code></td>
        </tr>
        <tr>
          <td>Butina Tanimoto 0.6</td>
          <td class="align-right"><code>175</code></td>
          <td class="align-right"><code>71.4%</code></td>
        </tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 5.</strong> Grouping sensitivity의 support 상태다. Singleton fraction이 높기 때문에 이 결과는 결론이 쉽게 뒤집히는지 보는 sensitivity check이며, strict prospective scaffold split은 아니다.</figcaption>
</figure>

## Pose-contact 후속 점검

Residual comparison만으로는 published score가 약해진 이유를 분리하기 어렵다. 그래서 후속 점검에서는 experimental pose 기반의 단순 interaction feature가 residual target에 보조 신호를 더하는지 확인했다. 925 prepared structures에서 pose-derived contact count features를 만들고, 494 compounds에 aggregate했다. Feature는 protein-element by ligand-element contact counts를 3.5, 4.5, 6.0, 8.0 Angstrom cutoff로 세고, simple contact와 pocket-residue summary를 더해 총 312 columns로 구성했다.

결과는 additive signal을 지지하지 않았다. `pose_contacts_only`는 residual Spearman `0.156`이었고, `ECFP + pose_contacts`는 `0.279`로 `ECFP only`의 `0.360`보다 낮았다.

Table 6은 pose-contact feature follow-up의 residual Spearman을 요약한다.

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>model</th>
          <th class="align-right">residual Spearman</th>
        </tr>
      </thead>
      <tbody>
        <tr><td><code>ECFP only</code></td><td class="align-right"><code>0.360</code></td></tr>
        <tr><td><code>pose contacts only</code></td><td class="align-right"><code>0.156</code></td></tr>
        <tr><td><code>ECFP + pose contacts</code></td><td class="align-right"><code>0.279</code></td></tr>
        <tr><td><code>descriptors + ECFP</code></td><td class="align-right"><code>0.369</code></td></tr>
        <tr><td><code>descriptors + ECFP</code><br><span class="table-note-inline">+ <code>pose contacts</code></span></td><td class="align-right"><code>0.283</code></td></tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Table 6.</strong> Simple distance-count pose-contact feature follow-up다. Primary follow-up delta는 <code>ECFP+pose_contacts - ECFP = -0.081</code>였고, bootstrap CI는 <code>[-0.146, -0.012]</code>였다.</figcaption>
</figure>

이 결과도 좁게 읽어야 한다. 구조 정보가 무의미하다는 결론이 아니다. 이 단순 distance-count feature design에서는 ECFP residual model 위에 additive signal이 확인되지 않았다는 뜻이다. Richer interaction fingerprints, label-aware model, local matched-pair analysis는 별도 질문으로 남는다.

## 해석

이 audit에서 가장 안정적으로 남는 결론은 raw pKD correlation만으로 published score의 structure-aware affinity signal을 주장하기 어렵다는 점이다. 이는 새로운 발견이라기보다 ligand-property와 series progression이 섞인 campaign에서 먼저 해야 하는 sanity check에 가깝다. OpenBind EV-A71 2A release는 이 기본 점검을 공개 artifact 위에서 수치화할 수 있게 해준다는 점에서 유용하다. Ligand-property baseline, supervised ligand-only control, grouped sensitivity를 함께 두면 published prediction files의 raw signal과 residual signal을 분리해 읽을 수 있다.

이번 release artifact에 대한 결과는 제한적인 negative result로 정리한다. 그렇게 보는 이유는 published affinity prediction files가 MW+cLogP residual target에서 supervised ligand-only control만큼 남지 않았기 때문이다. 유용한 지점은 OpenBind release를 이용해 affinity benchmark를 해석할 때 어떤 baseline과 caveat를 먼저 둬야 하는지 공개 release 기준의 audit protocol로 남긴다는 데 있다.

현재 단계의 후속은 큰 model training이 아니라 label aggregation sensitivity가 먼저다. OpenBind affinity note가 강조하듯 KD-derived value는 sensorgram fitting과 analysis choice를 거친 해석값이다 <a class="citation-ref" href="#ref-openbind-affinity-note" aria-label="Reference 2">[2]</a>. 따라서 row-level `all_affinity_data_release_v1.csv`에서 `Used in analysis`, fit uncertainty, KD aggregation rule이 residual conclusion에 얼마나 영향을 주는지 먼저 확인하는 편이 더 직접적이다.

## 한계

- 이 결과는 EV-A71 2A compound-level retrospective audit에 한정되며, OpenBind 전체나 structure-based affinity prediction 일반을 판정하지 않는다.
- `cv_ecfp_ridge`는 published prediction files의 직접 경쟁자가 아니라, 동일 campaign supervised ligand-only residual SAR control이다.
- MW+cLogP residualization은 diagnostic이다. Medicinal chemistry campaign에서는 property trend와 series progression 자체도 실제 SAR와 얽힐 수 있으므로, residual target을 구조 정보의 정답으로 해석하지 않는다.
- Grouped sensitivity는 결론을 뒤집지 않았지만, Murcko singleton fraction `82.2%`, Butina singleton fraction `71.4%`로 strict prospective scaffold split은 아니다.
- KD-derived affinity label의 row-level aggregation, fit uncertainty, `Used in analysis` 선택에 대한 민감도는 아직 확인하지 않았다.
- Pose-contact follow-up은 simple distance-count feature design만 평가했다. Richer interaction fingerprint나 label-aware structural model을 배제하지 않는다.

## Appendix

본문에는 해석에 필요한 수치만 남겼다. Appendix Table 1은 전체 method의 raw Spearman과 residual Spearman을 함께 보기 위한 보조 자료다. 이 표도 model ranking을 확정하기보다 raw correlation과 residual correlation의 차이를 점검하는 용도로 둔다.

<figure class="table-figure table-figure--comparison table-figure--metrics">
  <div class="table-shell">
    <table class="comparison-table metrics-table">
      <thead>
        <tr>
          <th>method</th>
          <th class="align-right">raw Spearman</th>
          <th class="align-right">residual Spearman</th>
          <th class="align-right">delta vs ligand control</th>
        </tr>
      </thead>
      <tbody>
        <tr><td><code>cv_ecfp_ridge</code></td><td class="align-right"><code>0.672</code></td><td class="align-right"><code>0.430</code></td><td class="align-right"><code>0.000</code></td></tr>
        <tr><td><code>cv_rdkit_descriptor_rf</code></td><td class="align-right"><code>0.627</code></td><td class="align-right"><code>0.337</code></td><td class="align-right"><code>-0.093</code></td></tr>
        <tr><td><code>cv_rdkit_descriptor_ridge</code></td><td class="align-right"><code>0.605</code></td><td class="align-right"><code>0.264</code></td><td class="align-right"><code>-0.166</code></td></tr>
        <tr><td><code>boltz_2</code></td><td class="align-right"><code>0.397</code></td><td class="align-right"><code>0.097</code></td><td class="align-right"><code>-0.334</code></td></tr>
        <tr><td><code>smina_crystal</code></td><td class="align-right"><code>0.255</code></td><td class="align-right"><code>0.038</code></td><td class="align-right"><code>-0.392</code></td></tr>
        <tr><td><code>gnina_crystal</code></td><td class="align-right"><code>0.453</code></td><td class="align-right"><code>0.018</code></td><td class="align-right"><code>-0.412</code></td></tr>
        <tr><td><code>clogp</code></td><td class="align-right"><code>0.174</code></td><td class="align-right"><code>0.014</code></td><td class="align-right"><code>-0.416</code></td></tr>
        <tr><td><code>molecular_weight</code></td><td class="align-right"><code>0.484</code></td><td class="align-right"><code>-0.017</code></td><td class="align-right"><code>-0.448</code></td></tr>
        <tr><td><code>cv_mw_clogp_ridge</code></td><td class="align-right"><code>0.484</code></td><td class="align-right"><code>-0.020</code></td><td class="align-right"><code>-0.451</code></td></tr>
        <tr><td><code>aqaffinity</code></td><td class="align-right"><code>0.117</code></td><td class="align-right"><code>-0.057</code></td><td class="align-right"><code>-0.487</code></td></tr>
        <tr><td><code>aev_plig</code></td><td class="align-right"><code>0.227</code></td><td class="align-right"><code>-0.085</code></td><td class="align-right"><code>-0.516</code></td></tr>
      </tbody>
    </table>
  </div>
  <figcaption><strong>Appendix Table 1.</strong> Method-level raw Spearman과 MW+cLogP residual Spearman이다. Delta는 <code>cv_ecfp_ridge</code> residual Spearman의 unrounded value를 기준으로 계산했으며, direct leaderboard가 아니라 residual sanity check의 보조 표로 읽는다.</figcaption>
</figure>

## References

<div class="reference-list" markdown="1">

<ol>
  <li id="ref-openbind-first-release">OpenBind Consortium. <strong>OpenBind's first release: A structure-affinity dataset for structure-based AI</strong>. OpenBind, May 5, 2026. <a href="https://openbind.uk/news/blog-openbinds-first-release-a-structure-affinity-dataset-for-structure-based-ai/">OpenBind blog</a></li>
  <li id="ref-openbind-affinity-note">OpenBind Consortium. <strong>Affinity and Kinetics Data in the EV-A71 2A OpenBind Release</strong>. OpenBind, May 5, 2026. <a href="https://openbind.uk/news/blog-affinity-and-kinetics-data-in-the-ev-a71-2a-openbind-release/">OpenBind blog</a></li>
</ol>

</div>

## Experiment Resources

<div class="reference-list" markdown="1">

<ol start="3">
  <li id="ref-openbind-github">OpenBind Consortium. <strong>EV-A71_2A_benchmark affinity files</strong>. GitHub, 2026. <a href="https://github.com/OpenBind-Consortium/EV-A71_2A_benchmark/tree/main/affinity">Repository directory</a></li>
  <li id="ref-openbind-zenodo">OpenBind Consortium. <strong>OpenBind Structure-Affinity Data Release: Enterovirus A71 (EV-A71) / Coxsackievirus A16 (CVA16) 2A protease</strong>. Zenodo, version v1, May 5, 2026. DOI: <a href="https://doi.org/10.5281/zenodo.20026661">10.5281/zenodo.20026661</a></li>
</ol>

실험 provenance는 front matter의 `lab_path`로만 남겼다. 이 글에서 사용한 analysis contract는 Table 1과 Appendix Table 1에 요약했다.

</div>

## Citation

Text citation:

```text
Ilho Ahn, "OpenBind affinity score의 MW+cLogP confounding 점검", Mini Research, May 10, 2026.
```

BibTeX:

```bibtex
@misc{ahn2026openbind_affinity_baseline_audit,
  author = {Ahn, Ilho},
  title = {OpenBind affinity score의 MW+cLogP confounding 점검},
  year = {2026},
  month = {May},
  howpublished = {Mini Research},
  url = {https://muted-color.github.io/research/2026/05/10/openbind-affinity-baseline-audit/}
}
```
