# Built-in criteria

Derived from the content expert's voice notes of 2026-11-03 and 2026-11-04 and the method meeting on video jobs. Each criterion is a yes or no question about the written script.

There is no length criterion. Duration is not good or bad by itself: it is only reported, and compared with something (the reference video's duration, or approved scripts below). Too short is judged by `complete`; too long by `simplicity` and `single_idea`.

| id | Question | Severity when it fails |
| --- | --- | --- |
| `hook_viewer_change` | Does the first line contrast the viewer's before and now, or promise what they get, instead of recounting the creator's feat? | blocker |
| `result_promise` | Do the first 8 seconds say what the viewer gains? | blocker |
| `so_what` | Does the video answer "what do I gain?" in the viewer's terms (money, time, safety, status)? | major |
| `demonstration` | Is something shown being done while it is explained, in most beats? | major |
| `visual_feasible` | Can the creator actually show each visual with their assets? | blocker |
| `simplicity` | Can a viewer follow it on first listen, with short spoken sentences and no essay tone? | major |
| `steps_explained` | In a non-visual niche, does each step carry an example from a real case and what it avoided? | major |
| `reason_why_kept` | If a reference was used, does the script keep its mechanism rather than only its block order? | major |
| `authority` | Is there one sourced reason to believe the speaker? | minor |
| `visceral_contrast` | Is there a concrete, sensory contrast (broken vs working, 3 days vs 1 hour)? | minor |
| `job` | Does the video do a clear job for the viewer: make laugh, "that's so me", "that's so us", help me do, make me feel or think? | major |
| `cta_pain` | Does the CTA name the audience's real worry or desire before offering the product, match the real offer, and avoid alarmism (no invented threat, no "AI will replace you" used to sell)? | major |
| `claims_sourced` | Is every number, employer, result, and date sourced or marked as a placeholder? | blocker |
| `single_idea` | Does the script hold together as one idea, instead of telling everything at once? Several facts or cases are fine when each one serves the same thesis and the whole makes sense on first listen: score 2. Score 1 when a secondary part is loose (it could be cut without loss) but the whole still holds, and 0 only when two theses or cases compete and the viewer loses the point. | major |
| `complete` | Is it whole, not truncated? Someone who never heard of the case understands what happened, what it means and why it matters on first listen, and every promise or term the script raises is resolved. Facts must connect to each other and to the thesis: loose statements set side by side (an employer next to a team habit, a personal story next to a conclusion it does not lead to) fail here. A short script that skips a needed link fails here; length alone never does. | blocker |
| `no_repetition` | Does each beat say something new? The same idea, date, or phrase said twice in different beats fails, even when each line is true. | major |
| `substance` | Does each line carry something real behind it (a fact, an example, a reason, a consistent line of thought), instead of slogans or assertions that sound good but say nothing? Abstract ideas are fine when they are consistent and actually say something. Example of failing: "O ano é o que te paga" with nothing that shows what the year was. | major |
| `theme` | Does the video start from and return to `creator.theme`, so that the viewer ends with something about that theme, even when the fact comes from another part of the creator's life? A life moment outside work (family, faith, a book) is inside the theme when the video shows what it says about the theme; a slight drift is fine. Score 2 when the theme carries the hook or promise and the close; 1 when it appears only at the end, outside the CTA; 0 when the lesson is about something else and the theme appears only in the CTA, or never. Skip when `creator.theme` is absent. | major |
| `voice` | Does it sound like the creator's own words and respect their constraints and enemies? | major |

## Calibration (the creator's own verdicts)

Use these to calibrate scores. The creator's verdict overrides a high score. Keep a creator's real verdicts in that creator's private context; the example below is fictional and only shows the shape of an entry.

- **Rejected** (fictional example), with revise and no blocker from this critique: "Precifiquei meu bolo errado por um ano" (about 240 words, about 95 s), from a home baker whose theme is running a profitable home kitchen: "Eu vendia bolo de pote a oito reais e achava que estava lucrando. [...] Imagina uma cliente que pede cem potes para um casamento: com a planilha certa, você cobra até o frete. [...] Eu vendia a oito reais, e isso não pagava nem o gás." Why, in the creator's words: "Essa cliente do casamento nunca existiu, e eu falo duas vezes que vendia a oito reais." Lessons: the wedding order was invented and spoken as a case, so `claims_sourced` and `complete` should fail; the price came twice, so `no_repetition` should fail; the video never says what the right price taught about running the kitchen, so `theme` should score 1.
