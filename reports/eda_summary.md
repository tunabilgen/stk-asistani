# EDA summary (auto-generated)

## 1. HumSet (training data for the sector classifier)

- Rows: **148,621** excerpts from 16,857 documents, 46 humanitarian response projects.
- Languages: {'en': 91134, 'fr': 30268, 'es': 27219}
- Missing/empty excerpt: 0; duplicated excerpts: 2,057
- Excerpts **without any sector label**: 22.5% (dropped for training — annotators tagged only pillars there).
- Labels per labelled excerpt: mean 1.32, max 11 → genuinely multi-label.
- Excerpt length (words): median 49, 95th pct 116

![humset_sectors.png](figures/humset_sectors.png)

Imbalance ratio largest/smallest sector: **13×** (Health vs Logistics) → class weighting + per-class thresholds.

![humset_cooccurrence.png](figures/humset_cooccurrence.png)

Strongest co-occurrences: Agriculture→Food Security 29%; WASH→Health 28%; Agriculture→Livelihoods 27%

![humset_length_lang.png](figures/humset_length_lang.png)

- Annotation years: {'2018': 4621, '2019': 27274, '2020': 113289, '2021': 3437} → older crises dominate; live news may drift (motivates self-training).

## 2. Independent (non-UN) crisis data

| source                                         |   rows |   countries | period                  |
|:-----------------------------------------------|-------:|------------:|:------------------------|
| UCDP GED 26.1 + candidate 2026 (Uppsala Univ.) | 210115 |         109 | 2016 – 2026-08-31       |
| Global Hunger Index 2026                       |    130 |         130 | 2021–2026 data          |
| IFRC GO active appeals                         |    165 |          79 | active today            |
| IFRC national societies                        |    220 |         220 | current                 |
| Tech for Palestine (Gaza MoH daily)            |   1105 |           1 | 2023-10-07 – 2026-10-15 |

→ **Coverage gaps**: GHI gives only provisional categories for Sudan, South Sudan, Yemen, Burundi (used at range midpoint) and does not cover Palestine (starvation deaths from Gaza MoH data used instead); GHI does not score every country (e.g. Palestine); UCDP codes Gaza events under Israel (we re-assign them by admin-1). Gaps are recorded in `data/known_gaps.json` and shown in the UI; missing data is never scored as 'no need'.

![ucdp_top15.png](figures/ucdp_top15.png)

- Top conflict-death countries (3 y): Ukraine 264,002, Sudan 89,846, Palestine 63,232, Iran 25,141, Mexico 21,824, Dem. Rep. Congo 18,073

![ucdp_trend.png](figures/ucdp_trend.png)

![ghi_hist.png](figures/ghi_hist.png)

- GHI ≥ 20 (serious or worse): **44** countries; ≥ 35 (alarming): 8

- IFRC active appeals: 165 (35 emergency appeals), requested CHF 2,236M, funded **51%**

## 3. News: independent vs Western coverage, and resulting scores

- News items collected: **941** from 18 outlets (754 independent, 187 Western); 74% tagged with ≥1 country by the gazetteer.

![attention_gap.png](figures/attention_gap.png)

- The 15 highest-need countries receive **29%** of independent coverage but **12%** of Western coverage.

![need_vs_attention.png](figures/need_vs_attention.png)

Flagged as ignored by Western media: Dem. Rep. Congo, Somalia, Sudan

## 3b. Descriptive statistics and correlations (final dataset)

|                       |   count |   mean |   median |   std |    max |   skew |
|:----------------------|--------:|-------:|---------:|------:|-------:|-------:|
| deaths /100k          |     177 |   17.6 |      0   | 130.9 | 1621.7 |   11.1 |
| civilian deaths /100k |     177 |    6.1 |      0   |  54.3 |  702.6 |   12.3 |
| GHI 2026              |     127 |   15.4 |     12.9 |  11.4 |   47   |    0.8 |
| aid $/person in need  |      18 |  154.2 |    115.8 | 146.6 |  535.6 |    1.4 |
| news indep.           |     177 |    4.6 |      0   |  13.8 |  106   |    4.4 |
| news Western          |     177 |    0.7 |      0   |   3   |   27   |    6.5 |
| IFRC funded %         |      76 |   79.9 |    100   |  28.9 |  100   |   -1.1 |

→ Death counts are extremely right-skewed (skew > 5: a few countries hold most deaths). We still use a **linear per-capita** scale with a cap, because a log scale compressed an 84× gap between Palestine and Israel; the cap limits the influence of extreme values.

![component_correlation.png](figures/component_correlation.png)

Pairs with |ρ| ≥ 0.85 (excluding the composite): n_civilian_harm–n_conflict 0.91. Components carry distinct information, so all are kept; civilian harm and conflict are related by construction but answer different questions (who is killed vs how many).

## 4. Models

| model                  |   micro-F1 |   macro-F1 |
|:-----------------------|-----------:|-----------:|
| keyword baseline       |     0.5578 |     0.5392 |
| tfidf+logreg (t=0.5)   |     0.7793 |     0.7439 |
| tfidf+logreg (tuned t) |     0.7795 |     0.7393 |

![model_f1_per_sector.png](figures/model_f1_per_sector.png)

By language (fairness check): {'en': {'n': 7501, 'micro_f1': 0.7963, 'macro_f1': 0.7462}, 'es': {'n': 2292, 'micro_f1': 0.7363, 'macro_f1': 0.6212}, 'fr': {'n': 2591, 'micro_f1': 0.7687, 'macro_f1': 0.714}}

Crisis-dynamics (pillar) model: macro-F1 0.6395, per class {'Casualties': 0.627, 'Displacement': 0.745, 'Shock/Event': 0.592, 'Humanitarian Access': 0.593}
