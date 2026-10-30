# Assignment 2 — screen-recording script (2–3 minutes, English)

**Before recording**
- Start the app: `python app.py` → open http://localhost:8000. Browser window ~1600 px wide, zoom 100 %.
- If you use the live LLM: OpenCode installed and logged in, `.env` contains `LLM_ENGINE=opencode`.
  Generate one campaign once *before* recording (first call is slower), then record.
- Close other tabs and notifications. Record with Windows **Win + Alt + R** (Xbox Game Bar) or OBS.
- Speak slowly. Time per part is a guide; total ≈ 2:40.

---

**0:00 – 0:15 · Opening** *(app opens on the Silence view)*
> "This is STK Asistanı, an AI tool that shows NGOs where help is needed most — especially the crises that mainstream media ignore. After the feedback on Assignment 1, we put this 'silence' idea at the centre: the app now opens on the Silence view."

**0:15 – 0:45 · Silence view** *(hover Sudan, Congo, Burundi on the map; point at the ranking)*
> "The silence index is need times the lack of Western media attention. Attention now comes from GDELT: about 275,000 articles from more than 7,000 outlets in the last 30 days, instead of 90 RSS items. Sudan, Congo and Burundi are at the top: very high need, almost no Western coverage."

**0:45 – 1:10 · Country file** *(click Sudan → Summary, then the Data tab)*
> "Each country has a file: why it scores high, the trend, aid per person in need, and a verified local partner from the Red Crescent. Every number comes from an independent source that is named here."

**1:10 – 1:45 · AI drafting** *(click "Generate campaign recommendation", wait, scroll the result)*
> "Here the LLM — DeepSeek V4.1 Flash — writes a campaign draft. It may only use the facts we give it. A validator then checks every number and partner name; anything not in our data is flagged. A human always approves the final text."
>
> *(If the LLM is not available, say instead: "Without an LLM the app falls back to a template, so it always works.")*

**1:45 – 2:10 · Project ideas** *(Afghanistan → Project ideas → click Herat on the map)*
> "For each province the tool matches climate, security and project types. In Herat it suggests a saffron and pomegranate cooperative; in Kabul, with recent violence, emergency aid instead."

**2:10 – 2:40 · Models** *(switch to the README on GitHub, scroll to the model comparison chart)*
> "We compared seven approaches on 12,000 expert-labelled test texts: keyword rules, Naive Bayes, SVM, logistic regression, multilingual embeddings, a fine-tuned transformer and an LLM. The linear models were best, about 0.78 F1, and retrain in a minute. Fine-tuning on a laptop CPU was too limited, and we report that honestly. But our old model could not read Turkish or Arabic: only 0.34 and 0.20. So the app now detects the language and uses a multilingual model for Turkish and Arabic, which reaches 0.70. All results and code are on GitHub. Thank you."

---

**Checklist after recording**
- Length 2–3 minutes · sound clear · the map and text readable.
- Upload to YouTube (Unlisted) or Google Drive (anyone with the link can view) and put the link in the README.
