# Data dictionary — `country_crisis_dataset.csv`

One row per country (177 rows), built by `src/build_dashboard.py` on 2026-10-30. See `notebooks/01_dataset_and_preprocessing.ipynb` for every step.

| column | description |
|---|---|
| iso3 | ISO 3166-1 alpha-3 code (index) |
| name | country name (Natural Earth) |
| region | UN M49 region label from Natural Earth |
| pop_est | population estimate (Natural Earth, 2019) |
| ucdp_deaths_3y | conflict deaths, last 36 months of data (UCDP; Palestine: Gaza MoH + West Bank) |
| ucdp_civilian_3y | civilian deaths, last 36 months (UCDP; Palestine: children + women, lower bound) |
| ucdp_deaths_90d | conflict deaths, last 90 days of data (UCDP) |
| deaths_per100k_3y | conflict deaths per 100,000 people |
| civilian_per100k_3y | civilian deaths per 100,000 people |
| deaths_source | source of the death counts |
| ghi_2026 | Global Hunger Index 2026 score (provisional categories at range midpoint) |
| ghi_2018 | Global Hunger Index 2018 score |
| ghi_provisional | GHI value is a provisional category |
| ifrc_requested | active IFRC appeals: amount requested (CHF) |
| ifrc_funded_pct | active IFRC appeals: % funded |
| aid_usd | humanitarian aid per year, all OECD-reporting donors, 2023-2024 mean (USD) |
| need_people | people in severe need (estimate) = population x protracted suffering above 0.3 |
| aid_per_person | humanitarian aid per person in severe need (USD/year), recognised crises only |
| news_independent | news items, last 30 days, 15 independent outlets |
| news_western | news items, last 30 days, BBC/Guardian/NYT |
| gdelt_western | GDELT, 30 days: articles by 24 Western mainstream outlets about this country (USA/UK stories excluded) |
| gdelt_turkish | GDELT, 30 days: articles by Turkish outlets about this country (Türkiye stories excluded) |
| gdelt_all | GDELT, 30 days: articles by all outlets (excl. domestic stories of Western/Turkish outlets) |
| recent_monthly | mean conflict deaths per month, last 3 months |
| base_monthly | median conflict deaths per month, 12 months before |
| trend_ratio | (recent+5)/(base+5) |
| heavy_months_12 | months with heavy violence in the last 12 |
| status | trajectory label |
| vulnerability | 0-1, max(hunger level, ongoing violence) |
| n_civilian_harm | civilian deaths per 100k / 200, capped at 1 |
| n_conflict | deaths per 100k / 500, capped at 1 |
| n_hunger | GHI / 50, capped at 1 (Palestine: documented starvation deaths) |
| n_conflict_recent | recent violence 0-1 |
| n_acute | max(natural hazard x vulnerability, new IFRC appeal, recent violence) |
| n_aid_gap | 0-1, $5/person -> 1, $300 -> 0 |
| n_neglect | 1 - IFRC funded share |
| n_att_western | Western media attention 0-1 |
| n_att_indep | independent media attention 0-1 |
| n_prot | protracted suffering 0-1 |
| escalation | worsening bonus 0-1 |
| att_share_western | share of Western outlets' foreign-news articles about this country |
| need_share | this country's share of total need (max of protracted and recent-violence components) |
| coverage_ratio | att_share_western / need_share: 1 = covered in proportion to need, <1 = under-covered |
| ignored_by_western_media | flag: protracted need >= 0.4 and coverage_ratio < 1/3 |
| silence | silence index 0-1 = need x (1 - min(coverage_ratio, 1)) |
