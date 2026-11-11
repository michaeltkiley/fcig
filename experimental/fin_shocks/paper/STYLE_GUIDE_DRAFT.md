> Superseded on 11 Nov 2026 by `experimental/WRITING_GUIDE.md` (the confirmed guide). This file keeps the evidence from the author's earlier papers.

# Style guide for Note B: DRAFT FOR THE AUTHOR TO CONFIRM (11 Nov 2026)

Nothing in the note is changed on the basis of this draft until it is confirmed. Every point below is tied to a quotation in `style_evidence/` (four files: `ev_jmcb.md`, `ev_ijcb.md`, `ev_ramey.md`, `ev_notes.md`). Labels used: **OBSERVED** = in the text of a source; **AUTHOR RULE** = recorded in the author's FOMC project logs as the author's instruction (second-hand: the logs are written by Claude sessions); **AI REVIEW** = a reviewer agent's comment in those logs, not an author rule; **INTERPRETATION** = mine.

## 0. What the evidence is, and what it is not
- **JMCB paper**: read as the FEDS working paper 2024-032 (the 2026 JMCB version was not accessible, Wiley returned 403). It is a theory note: no data, tables or appendix, so robustness habits cannot be read from it.
- **IJCB paper**: read as FEDS 2022-016 (the IJCB version was not accessible). About 14 text pages against 23 in print, so it probably differs.
- **Ramey (2016)**: your upload; read in part (abstract, sections 1, 2.1-2.2, 3 with 3.4-3.6 closely, parts of 4, 5.5, 7). It is a survey chapter, so its "what have we learned" framing may not transfer; its "Explorations" sections are the closest match to a research note.
- **FOMC repos**: no standing style file in any repo. The author's own file `[[Kiley_papers_writing_style]]` is referenced in `fomc_evolution/PaperV3/DECISION_LOG.md` but lives outside the repos and was not available. The rules below come from what the logs record. The benchmark paper `PaperV3/paper/draft5_revised.tex` was not read.
- My own crude counts (pdftotext of each paper, tables included, so rough): average sentence length JMCB 27, IJCB 28, Ramey 21.5, Note B 23; "rather than" per 1,000 words 0.2 / 0.0 / 0.3 / 0.3; numeric tokens per 1,000 words 43 / 70 / 58 / 125; "significan*" per 1,000 words 0.2 / 0.0 / 0.6 / 2.3; "Section n" references per 1,000 words 0.3 / 0.3 / 0.8 / 1.4; modal hedge words (may, might, could, likely) per 1,000 words 3.2 / 3.2 / 2.1 / 0.6. The note is not longer-winded or more hedged than the sources by these counts; it is denser in numbers, significance language and section references.

## 1. Patterns found in the sources (each with quotes in the evidence files)

**1.1 Open with the fact or the claim, and ask the question plainly.**
- OBSERVED (IJCB, abstract and intro): opens on facts: "Inflation was low and stable in the United States during the first two decades of the 21 st century and broke out of its stable range in 2021." The question is a method choice in one sentence: "A critical consideration in any work pursuing these questions is how to weigh data from different time periods."
- OBSERVED (JMCB, abstract and first paragraph): the main result comes first: "Activity shortfalls are more costly than strong activity." / "I examine the consequences of monetary policy approaches resulting from asymmetries in the losses associated with employment shortfalls and strength." Motivation follows in paragraph 2.
- OBSERVED (Ramey, section 1 and 3): plain questions, answered at once: "If many macroeconomists now believe that monetary policy shocks themselves contribute little to macroeconomic outcomes, why is there such a large literature trying to identify them? The reason is that we want to identify nonsystematic movements in monetary policy so that we can estimate causal effects of money on macroeconomic variables."
- OBSERVED: no "to our knowledge", no gap claim, no "this paper makes N contributions" in either Kiley paper or Ramey.

**1.2 Contribution is stated as what the approach offers or what the results can inform, in First / Second / Finally.**
- OBSERVED (IJCB): "The approach of the Bayesian decisionmaker has several advantages relative to other approaches. The first advantage is ... The second advantage is ... Finally, ..."
- OBSERVED (JMCB): "These results may inform discussions of monetary policy in several ways. First, ... Second, ... Finally, ..."

**1.3 Results are previewed early; literature comes after, in a run-in paragraph or in footnotes.**
- OBSERVED (IJCB): "The results that emerge from the analysis are very clear. ..." then "Previous literature: The analysis is related to ..."; roadmap as a run-in label.
- OBSERVED (JMCB): literature in footnotes and "For example" lists, no literature section.

**1.4 Abstracts: short declarative sentences, one claim each, plain verbs; no robustness sentence; no numbers.**
- OBSERVED (JMCB, 11 sentences, ~150 words): "The asymmetric loss function and resulting optimal monetary policy exacerbates shortfalls in activity." / "Greater symmetry lowers the magnitude of activity shortfalls. Greater symmetry also reduces inflation bias."
- OBSERVED (IJCB, 7 sentences): the result, then a plain restatement: "In other words, 21st century data contains very little information to dissuade a Bayesian decisionmaker of the view that inflation fluctuations are persistent, or “unanchored”." Last sentence: "The intuition for, and implications of, this finding are discussed."
- OBSERVED (Ramey, abstract end): an unhedged closing claim: "It concludes that we are much closer to understanding the shocks that drive economic fluctuations than we were 20 years ago."
- AUTHOR RULE (FOMC DissentNote): abstract 175-225 words; hedge wording identical in abstract, introduction and conclusion; abstract claims must be checkable in the body.

**1.5 Prose: plain declaratives, one claim per sentence, the object of study as subject, first person or "the analysis".**
- OBSERVED (JMCB): "I use a simple static model." / "Output above potential raises inflation." / "Inflation is positively related to expected inflation."
- OBSERVED (IJCB, third person): "The approach herein is the one a Bayesian decisionmaker would follow." / "Two results emerge clearly. First, ... Second, ..."
- OBSERVED (Ramey): "The Federal funds rate jumps up temporarily but then falls back to 0 by 6 months. This temporary blip in the funds rate, however, sets off a prolonged recession. Industrial production begins to fall in the next month and troughs 21 months later."
- OBSERVED: plain glosses after results ("In words,", "Intuitively,", "Heuristically,") and one-phrase verdicts ("very modest", "change dramatically", "An odd feature").
- OBSERVED: numbers sit in the clause or with their test ("the coefficient is 0.31 with a robust standard error of 0.11"); the sources use few "significant" tallies.
- AUTHOR RULE (FOMC logs): split stacked sentences; avoid causal verbs for associations ("governs", "causes", "does not survive": use "is associated with"); keep terminology identical; no process talk or file paths in reader-facing text; gloss or cut jargon at first use; rewrite end to end rather than patch (no tonal seams).
- AI REVIEW (not an author rule): limit "X, not Y / rather than" antithesis; open sections with the finding; "kitchen-sink" is a colloquialism.

**1.6 Robustness and limits: reported as a test with an outcome, in one plain sentence; hedging attaches to interpretation, not to estimates; no apology.**
- OBSERVED (Ramey): "In this case, the price puzzle is even worse and the initial expansionary effects on output and unemployment are no better." / "The point estimates are similar if more lags are included." (footnote) / "The results (not shown) were still puzzling."
- OBSERVED (Ramey, 3.6): an own result reversed in a sentence: "This rosy reconciliation picture disappears, however, when the specifications are subjected to some robustness tests." Interpretation separated and marked: "I would argue that the most likely reason ... is simply that we can no longer identify monetary policy shocks well."
- OBSERVED (IJCB): "The results are generally similar for the overall CPI ..." / "alternative choices for the lag structure yielded similar results (see section 3.3)" / "essentially identical results". A real limit stated once in the body: "This comparison also highlights a potential weakness of the approach of a Bayesian decisionmaker for a researcher that views a structural break as likely." Robustness is one short subsection ("Robustness and Implications"); no appendix.
- OBSERVED (JMCB): cautions are one-sentence reports of what is assumed and which way the result would move, in a body section titled "Additional considerations" and in footnotes: "This consideration would likely carry over to the asymmetric loss function, all else equal." The word "limitation" never occurs.
- AUTHOR RULE (FOMC logs): each caveat stated once and cross-referenced, not repeated; a null is "evidence of no detected association at this power", not proof; report honestly what is weak ("TWO robust findings ... not three"); run the cheap check before softening a claim.

**1.7 Cross-references.**
- OBSERVED: forward references concentrated in the introduction roadmap (Ramey one paragraph per section; Kiley three plain sentences). In bodies, back-references are short and numbered ("As discussed in Section 2.5"; "Recall from equation (4) ..."); forward teasers are rare. Counts: IJCB about 4 forward and 6 backward in 14 pages; JMCB about 4 forward and 8 backward in 15 pages.
- AUTHOR RULE (FOMC DECISION_LOG, superseding an earlier note): heavy preview and review scaffolding ("as discussed above/below") is "a sign of weak writing where paragraphs can't stand on their own"; long section-opening roadmaps cut to the thesis sentence; the introduction's roadmap is the one conventional exception; main-text pointers to appendices are footnotes or very short.

**1.8 Sections open on a declarative sentence and close on an implication or a plain verdict, not a summary or a teaser.**
- OBSERVED: JMCB "I use a simple static model." / IJCB "The study analyses inflation in the United States." / Ramey ends 3.6 with "Monetary policy can have big effects, but it is likely that monetary shocks are no longer an important source of macro instability."

**1.9 Conclusions.**
- OBSERVED (both Kiley papers): short; the first paragraph repeats the abstract almost verbatim; no limitations paragraph; no policy list; one pointer to further work. IJCB: two paragraphs, ~170 words.
- OBSERVED (Ramey): returns to the introduction's question and answers it in one sentence; states one limit in a subordinate clause of the last sentence.
- AUTHOR RULE (FOMC DissentNote): five paragraphs: question, validation, new findings, literature strands, limitations, each caveat once. **This differs from the two Kiley papers read; see question 5.**

**1.10 Tables and figures.**
- OBSERVED: introduced by number and by what they contain in a sentence ("Table 1 summarizes some of the main results ... "), then the text reads the rows or lines ("Rows 3 and 4 of Table 2 show ..."); each carries "Source: ... author's calculations."; table titles are plain descriptive phrases.
- AUTHOR RULE (FOMC logs): introduce a table at the first statistic it supports; keep table style consistent.

## 2. How the current note compares (my reading; quotes from the current draft; confirm or reject each)
1. **Abstract.** Carries four numbers and a ~45-word sentence: "We measure the response of the two-year yield and of a broad financial conditions index (the 10-year yield, equity valuation and the real dollar) in the announcement window, both relative to the neutral rate r*, and carry it forward with a daily and a monthly model." Both Kiley abstracts and Ramey's have no results numbers and are built of short declaratives.
2. **Introduction order.** The first results appear after the literature bullets and two mechanism paragraphs. Both Kiley introductions give the result in the first paragraph (JMCB) or in the first paragraphs (IJCB) and put the literature after the results.
3. **Significance and tally language.** "significan*" appears 2.3 times per 1,000 words against 0.0 to 0.6 in the sources. Example, Section 3.2: "The unemployment rise is significant after 36 months at every step but after 24 months only at the r* step." The sources give a verdict ("very modest", "no better", "still puzzling") and leave the intervals to the table.
4. **Number density.** Example: "Unemployment falls, to -0.81 percentage point after 12 months at its lowest, and is still -0.25 after 36 months; the price level hardly moves (within 0.15 percent of zero at every horizon in Table 4)." Compare Ramey: "Industrial production begins to fall in the next month and troughs 21 months later."
5. **Cross-references.** "Section n" appears 1.4 times per 1,000 words against 0.3 to 0.8; the 3.x subsections contain several "of Section 3.1"-type links. (Already trimmed once; some remain.)
6. **Robustness section.** Four subsections, each with a table and a paragraph of numbers, about 2,000 words; the sources give robustness one short subsection or a clause. Ramey's "Explorations" are longer than the Kiley papers' robustness, so the right length is a question for you (question 6).
7. **Voice.** The note uses "we"; the JMCB paper uses "I", the IJCB paper "the analysis". See question 1.
8. **Contribution sentence.** "Our contribution is to hold the surprise fixed and change only the variables that carry it to the economy." The sources frame it as what the approach offers or what the results may inform, in First / Second / Finally.
9. **Not a problem by these counts:** average sentence length (23 against 21-28), "rather than" density (0.3 per 1,000), modal hedging (0.6 per 1,000, the lowest of the four).

## 3. Questions for the author (these decide the rules; I will not assume)
1. Voice: "I", "we" or "the analysis"? (JMCB: "I"; IJCB: third person; the note is currently "we".)
2. Abstract: no results numbers (as in both Kiley abstracts and Ramey), or keep the headline numbers? Length: 150 (JMCB) or the 175-225 of the FOMC note?
3. Introduction: results in the first paragraph(s) with the literature after, as in the Kiley papers?
4. Contribution: First / Second / Finally framing of what the approach offers, as in both Kiley papers?
5. Conclusion: short, repeating the abstract, no limitations paragraph (both Kiley papers), or the five-paragraph FOMC structure with one limitations paragraph?
6. Robustness: one short subsection with a table, or the current four subsections? How long?
7. Numbers and "significant": report verdicts in words and leave intervals to tables?
8. Which FOMC-note rules do you want carried over (causal-language rule, one-statement-per-caveat, consistent hedge wording, appendix pointers as footnotes)?
