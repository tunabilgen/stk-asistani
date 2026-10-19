# STK Asistanı — Presentation script (simple English, about 7 minutes)

Tip: speak slowly, one sentence at a time. **Bold** = the number to say clearly.
Suggested split: Tuna → slides 1–6, Ufuk → slides 7–12 (change as you like).

---

### Slide 1 — Cover (20 sec)
Good morning, everyone. We are Group 6: Tuna Bilgen and Ufuk Gündoğar.
Our project is called STK Asistanı. "STK" means NGO in Turkish.
It is an AI tool that helps NGOs decide where help is needed most.

### Slide 2 — The problem (45 sec)
Let us start with the problem.
Small NGOs do not have analysts. They cannot follow more than one hundred crises.
So they often follow the news.
But the news is not fair.
In the last 30 days, **38 percent** of the world news of BBC, The Guardian and The New York Times was about Ukraine and Russia.
And **zero percent** was about Sudan, Congo, Somalia, Syria or Lebanon.
But Sudan had almost **90,000** conflict deaths in three years.
So aid follows the headlines, not the need.

### Slide 3 — Our answer (40 sec)
Our answer is STK Asistanı.
It helps NGO teams find the most urgent and the most forgotten crises in their own work areas.
Any NGO in the world can use it. Our first pilot users are small NGOs in Türkiye.
Our main SDG target is 17.17, civil-society partnerships. We also support 16.1, less violence, and 2.1, zero hunger.
We will measure success with model accuracy, checks against expert knowledge, and tests with different NGO profiles.

### Slide 4 — How it works (40 sec)
This diagram shows how the tool works.
On the left are the inputs: the NGO's profile, an optional note from the field, and data that comes in automatically every day.
In the middle is the AI part: two classifiers read the news, the model learns from new data, and a scoring step ranks the crises.
On the right are the outputs: a world map, a file for each country, and a draft for a campaign or a project.
A human always makes the final decision.

### Slide 5 — Data (35 sec)
We use only independent data sources.
For example: conflict data from Uppsala University, the Global Hunger Index, the Red Cross and Red Crescent, and casualty data from the Gaza Ministry of Health.
We also read 15 independent news sources every day.
We use the three Western news sources only to measure which crises they ignore.

### Slide 6 — Preprocessing (40 sec)
Cleaning the data changed our results a lot. Here are some examples.
In our training data, we removed texts without labels. We kept **115,000** clean texts.
The conflict dataset puts Gaza events under Israel, so we moved more than **8,000** events to Palestine.
And our most important rule: missing data is never counted as "no need".

### Slide 7 — Attention gap (35 sec)
This chart compares the news coverage of the highest-need crises.
Green is independent media, grey is Western media.
Palestine gets **12.5 percent** of independent news, but only **3.3 percent** of Western news.
Sudan gets zero in Western news. Ukraine is the opposite.
We use this gap as a "silence index" in our tool.

### Slide 8 — Deaths per person (40 sec)
Total numbers can hide the truth, so we count deaths per person.
For every 100,000 people, Palestine has **1,622** deaths. Israel has **16**. That is about one hundred times more.
Also, in Ukraine only **3 percent** of recorded deaths are civilians.
So we measure violence against civilians as a separate part of the score.

### Slide 9 — First model (45 sec)
Now our first model.
We trained a TF-IDF and logistic regression model on **115,000** texts labelled by experts.
It reaches an F1 score of **0.78**. Simple keyword rules reach only **0.56**.
We also found a language bias: the model is weaker in Spanish. We report this openly.
The model can also learn from new news. After the first update, its accuracy stayed the same, so the update was accepted.

### Slide 10 — Prototype (30 sec + demo)
We also built a working prototype.
It has a world map with three views: priority, silence and worsening.
Each country has its own file with data, trends and a verified local partner.
And for each province, the tool suggests projects. For example, in Herat it suggests saffron and pomegranate farming.
Let me show you quickly. *(Live demo: open the map → click Palestine → open "Project ideas" for Afghanistan.)*

### Slide 11 — Ethics (45 sec)
Ethics was very important for us.
We checked our results many times, and we found real mistakes.
For example, in the first version Gaza was ranked too low, because missing data was counted as zero.
We also learned that money sent is not always aid delivered, for example under a blockade.
We fixed all of these problems. And a human approves every campaign.

### Slide 12 — Next steps (25 sec)
In Assignment 2, we will compare our model with a transformer model and an LLM.
In Assignment 3, we will test the tool with different NGO profiles and add more African news sources.
Our code is on GitHub.
Thank you for listening. We are happy to answer your questions.

---

## Possible questions — short answers

**Why not use UN data?**
We wanted independent sources. In our first version, a single institutional data source gave Gaza a rank that was too low, because some populations were not counted.

**Is the LLM working?**
The code is ready. Right now the tool uses a template. We will test the live LLM in Assignment 2.

**How do you know the ranking is correct?**
We check it against expert knowledge. Every time we found a mistake, we found the reason and fixed it. We will test it with NGO profiles in Assignment 3.

**Why is Israel shown grey on the map?**
This is an NGO policy setting called "excluded countries". The user can change it. We did not change the data.
