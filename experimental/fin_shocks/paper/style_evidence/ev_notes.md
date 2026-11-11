# Style notes from fomc_evolution / fomc_1990s / fomc-participant-statements

Labels: (a) AUTHOR = rule/instruction the author (Kiley) wrote or approved, as recorded in the repo's logs (the logs are written by Claude sessions and record the author's instructions, so these are second-hand records of the author's words unless quoted); (b) AI REVIEW = reviewer/debate agent comment; (c) INTERPRETATION = mine.
Paths are under /home/user/fomc_evolution/ unless stated.

## Files read
- DissentNote/debate_round3/style_review.md (in full)
- DissentNote/PLAN.md (targeted: lines ~1650, 2345-2372, 2455-2490, 2745-2770)
- DissentNote/draft4_to_draft5_change_log.md (lines 1-64, 145-215)
- DissentNote/round5_content_audit.md (lines 1-20, 104-140, 198-210)
- PaperV3/DECISION_LOG.md (targeted: ~388-396, 559-612, 836-842, 932-938, 966-992, 1306-1332, 1575-1580, 1605-1670, 1785-1800)
- PaperRepivot/SIX_POINTS.md (first 40 lines)
## Skipped / not read in full
- Grep-only (matched 'style|plain|voice|abstract' but are content/analysis, not style): all debate_round1/2/4 agent files, PaperV3 review_round1 and debate*/ files, RESULTS.md files, StaffMaterials, RiskSplit, SpeakerViewDecomposition, Foundations, lit_review, replication*, DissentNote/OUTLINE_DRAFT.md, other runbooks.
- fomc_1990s: docs/*.md (How-To guides are pipeline/output docs), project_plan.md, TRANSITION.md, prompts/, data/anchor_documents (third-party texts), paper/Proposals/*.tex (not opened). No style guide found.
- fomc-participant-statements: README.txt, DECISIONS_LOG.md, COVERAGE.md grep hits are data-engineering only ('plain HTML', 'abstract' as a field name). RESUME_CHECKLIST.md not present in the listing. No style content found.
- No CLAUDE.md or AGENTS.md exists in any of the three repos.
- NOT FOUND: the author's standing style file, referenced as `[[Kiley_papers_writing_style]]` (a Claude memory file under /home/michaelkiley/.claude/..., not in the repos). Only the rules quoted below, as described in the logs, are available. The benchmark paper `PaperV3/paper/draft5_revised.tex` was not read.

---
## 1. Prose and sentence-level rules

AI REVIEW (DissentNote/debate_round3/style_review.md, "Overall verdict"; 25 numbered findings; stage d of a pipeline, scored draft2.tex against draft5_revised.tex as benchmark):
- "The benchmark ... builds its argument out of short-to-medium declarative sentences, each carrying one claim, with hedges and statistical support attached as brief trailing clauses."
- "The single biggest fix is mechanical: take the long em-dash-laden sentences ... and split each into two or three sentences at the natural clause boundaries."
- Finding 1: one sentence defining two axes in a parenthetical and asking a three-part question -> "asks three separate short questions in three separate sentences".
- Finding 3/4: "welded together with 'so... and.'"; "a single sentence with three semicolon-joined independent clauses ... it would give each clause its own sentence."
- Finding 6 (abstract): central result "arrives after a 40-word parenthetical ... A reader has to hold the whole aside in memory before reaching the verb."
- Finding 14: "Kitchen-sink specification ... is a colloquialism ... the only one in the document — everywhere else the register is formal." Use "full specification".
- Finding 22: "X, not Y" / "rather than Z" antithesis ~71 times in draft2 vs ~11 in benchmark (about six times the density): "Used occasionally this is a strong rhetorical device ... Used this often it reads as a verbal tic and flattens the emphasis". Recommends cutting about half, "stating the rest as plain positive claims."
- Scope note: "Every suggested rewrite preserves the original hedge, caveat, and finding — only the sentence-level packaging changes."
- Adopted? PLAN.md ~2751-2765: draft3.tex had "All specific, quoted findings applied (sentence splits, hedge de-stacking, jargon removed in favor of plain descriptions ..., section openings rewritten to lead with the finding ...)". PLAN.md ~2482: "colon/semicolon sentence-splitting is the highest-yield tactic" (author's later sessions self-reviewed against it). draft5 change log: "Overall 'rather than' count reduced from 37 to 31 instances (was 3.4 per 1,000 words vs. the companion paper's 1.5; still above benchmark ...)". So adopted, with the density target of the companion paper being checked.

AUTHOR (as recorded, PaperV3/DECISION_LOG.md ~1306-1330, "Scenario Analysis subsection: holistic prose smoothing"): the user asked "whether the writing here was as smooth as elsewhere in the paper." Problems named in the log: "a semicolon-stitched clause in the opening sentence, three short choppy same-shaped sentences in a row ..., ... and a tonal mismatch between the vivid new ... sentence and the flatter ... sentence". Fix: rewrite the subsection end to end rather than patching ("accreted three separate rounds of incremental edits ... and it showed").
INTERPRETATION: author wants a single, even register; incremental edits that leave seams are unwelcome; avoid both stitched long sentences and runs of short same-shaped ones.

AUTHOR (DECISION_LOG.md ~561-583, "Second follow-up: prose/style problems on a closer read"; user flagged four problems, all agreed):
- "Table referenced only after all three statistics were already discussed — bad structure; should be introduced at the first statistic and referenced again for each subsequent one".
- "'ANOVA-decomposable' framing forced/irrelevant ... It's unexplained jargon at first use, dropped in without payoff at this location". Cut.
- "Six separate appendix pointers in one short subsection ... excessive." Collapsed to one footnote.

AUTHOR (DECISION_LOG.md ~1793): "New standing style rule saved to [[Kiley_papers_writing_style]]: proactively hunt for main-text shortening opportunities every pass, not just when asked; appendix references in main text must be footnotes or very short, never a dedicated sentence."

AUTHOR, terminology (draft4_to_draft5_change_log.md "Terminology and framing fixes"):
- '"Governs"/"causes" removed; replaced with "is associated with," "organizes," or "predicts in this specification" except where describing the turnover-vs.-within-person variance decomposition itself, where plain descriptive language is appropriate.'
- '"Disposition" removed everywhere it stood in for the classifier's actual output; replaced with "voiced disagreement" throughout.'
- Round-5 audit: 'reserve "shadow dissent" as the measure's name and use "voiced disagreement" in prose'.
- Round-5 audit calls "governs" "overstated causal language" ("(d) overstated causal language").
- "do not describe PC1 as 'not a proxy'; call it a language-derived measure" (quoted in round5_content_audit.md Section 3 as a "Stage 5" instruction; "banned language").

## 2. How to frame questions and contributions
AI REVIEW (style_review.md Finding 1, 16, 20): ask the question as short separate questions; state the finding first then the statistic ("The strategy axis is the organizing dimension of who dissents. Policymaker-eras with at least one dissent sit significantly higher on it ... ($t=2.43$, $p=0.016$)").
AUTHOR (draft4_to_draft5_change_log.md "Abstract, Introduction, Conclusion rewrites (Stage 4)"; DissentNote PLAN.md ~2490+): three contribution categories "Independent Validation / New Perspectives / Reassessing and Reconciling Research — used identically in the abstract, intro, section titles, and conclusion" (PLAN.md Turn 2: "User provided a complete target architecture (their own synthesis ...)"). Intro "three contribution paragraphs now correspond exactly, in order, to Sections 4/5/6, matching the abstract's own three-part structure."
AUTHOR (change log): "No repeated 'not an appendix'-style defense of the note's independence."; independence "is now demonstrated through the findings themselves, per the round-5 instruction, not asserted in a closing line." Removed: "It is a genuine complement ... not a robustness check appended to it" and "not a paper and its appendix".
AUTHOR (change log): "'Entirely separate dataset' removed. The introduction now states plainly that the two papers share a transcript corpus and a taxonomy, differing only in the outcome each is used to explain."
AUTHOR (PLAN.md ~2857, DissentNote): "Lead with the substantive claim" (in a debate-round synthesis context; context not fully read).
AUTHOR (PaperV3/DECISION_LOG.md ~1422): "the abstract explicitly promises a joint comparison" -> table must deliver what the abstract promises. INTERPRETATION: abstract claims must be checkable in the body.
AUTHOR (DECISION_LOG.md ~966-992, Item I): user rejected a precedence story ("which pillar emerged first"): "i lean toward deleting this section and also deleting anything in the paper that suggests one preceded the other"; adopt "co-occurring, mutually reinforcing trends" framing; do not give one institution (SEP vs scenario analysis) asymmetric weight. INTERPRETATION: author prefers the less sequential/less asymmetric story when the evidence is a three-lens disagreement.
AUTHOR (DECISION_LOG ~1450 area / ~608): when extending a cited paper, "state the parallel plainly, but do NOT preview the 'not disagreeing with HMP, building on/extending them ...' framing here — that emerges organically later".
AI REVIEW + AUTHOR use (round5_content_audit.md Finding 1): verify what cited papers actually measure; "reword to 'an experience/tenure mechanism in the spirit of HMP's ...,' not 'HMP's mechanism tested directly'"; "Per the round-5 instruction not to guess and to narrow wording where sources are thin, findings ... reported at the confidence level the sources actually support."

## 3. Abstract and introduction conventions
AUTHOR (change log): abstract "within the 175-225 target", final version 224/225 words; abstract uses "macro-domain axis" throughout (terminology kept consistent), defines the rates it reports correctly, "summarizes the three literature strands", "has no final coequal-status sentence". Two abstract errors found by user on reading the PDF: reversed rate/wedge, and "the strategy pillar" (wrong; "strategy-domain axis").
AUTHOR (change log, draft5 second pass): "added an economically interpretable magnitude for the central ... result (average marginal effect +23 to +25 percentage points ...)".
AUTHOR (change log): "'Does not survive' (introduction, abstract) removed; replaced with 'is almost entirely committee turnover' ... and general causal language softened elsewhere." Later softened to "appears to reflect ... rather than a detectable within-person change".
AUTHOR (DECISION_LOG ~391-393): hedge wording must be the same across abstract, introduction and conclusion ("'discipline dominates' was softened to 'the balance of evidence favors discipline' in the Conclusion ... but NOT in the Abstract/Introduction, an inconsistent register — normalized across all three locations").
AUTHOR (change log): Conclusion "rewritten to the five-paragraph structure specified (question, validation, new findings, three literature strands, limitations)", "portability list cut to one sentence", "Limitations paragraph states each caveat once, cross-referencing rather than repeating the Data Quality section's fuller versions."
AI REVIEW (style_review.md Findings 18-21): section openings should lead with the finding/question, not "This section applies X to Y". Benchmark exception: "the Conclusion's opening ('This note set out to ask ...') is not flagged — the benchmark's own Conclusion opens the identical way ... in-register specifically for a Conclusion, just not for body sections." Adopted per PLAN.md ("section openings rewritten to lead with the finding").
AI REVIEW (Finding 15): do not call back in the Conclusion to a term the Introduction never used in prose ("formalization wedge", appeared only in title); adopted ("now grounded in the Introduction's own prose").
AUTHOR (DECISION_LOG ~1631-1670): preview/review scaffolding. "excessive 'preview' (forward-pointing 'as discussed below/in Section X') and 'review' (backward-pointing 'as discussed above') scaffolding -- flagged as a sign of weak writing where paragraphs can't stand on their own, not thoroughness." Logged as superseding an earlier note that had listed forward-references as positive. Long section-opening preambles enumerating subsections are the same problem: "cut to just the thesis sentence alone" (user pushed further than the AI's proposal). Exception kept: the Introduction's "I structure the analysis as follows" roadmap "is the conventional, expected place for a full paper roadmap". A Methods section "pre-announcing Section 4's actual quantitative results before any evidence is shown" was cut.

## 4. How to characterize robustness and limitations
AUTHOR (round5_content_audit.md; "Stage-3 instructions" quoted verbatim there): a null result is not proof the axis behaves as it should: 'close to the banned "a null result proves the macro axis correctly stays silent" pattern'; "A null is evidence of no detected association at this power, not proof the axis is behaving as it should." Fix recorded: '"Stays silent, correctly" ... and "lit up everywhere" ... removed; replaced with direct statements of the asymmetry itself.'
AUTHOR (change log #7): softened '"only possible if the axis identifies something real"' to '"supports the interpretation that the axis captures something real"'; '"has nothing to do with who breaks with the committee"' to '"is not detectably associated with who breaks with the Committee in these specifications."'
AUTHOR (round5_content_audit.md Section 8): keep an appropriately hedged limitation: "keep that hedge, do not strengthen it even if Script 34's fuller specification is ...".
AUTHOR (change log #3-4 and addendum): run the cheap robustness checks before softening claims ("rather than just softening the language without checking").
AUTHOR (PaperV3/DECISION_LOG.md ~838-841, ~936): "softened the keyword-vocabulary claim to avoid overclaiming precision from a small clean sample (n=7) while still reporting the directionally consistent pattern"; "explicitly not overclaiming about the whole corpus, scoped to 'the pole most representative of X deliberation.'"
AUTHOR (DECISION_LOG ~659): "Honest limitation, surfaced proactively rather than left implicit" (e.g., meeting-length confound). Also reports small/ambiguous results as such: "the paper is now honest that it has TWO robust findings (dimension, specificity), not three"; peak-meetings null "honest non-forcing".
AUTHOR (PLAN.md ~1656): "Any future write-up should lead with the funds-rate/macro result and describe the unemployment/strategy result with more hedging, not present them as equally strong twin findings."
PLAN.md ~538: "never report the bare p-value/stars for this result without the accompanying ..." (cut off; context not read).
AI REVIEW (style_review.md Findings 8-12, 23): hedges should be kept but "de-stacked": one result, then its support, then each caveat as its own plain sentence; do not name your own hedges ("Two further hedges apply" -> "Two caveats apply." followed by one sentence each). The benchmark hedges with one clause: "Earlier work ... may therefore have overstated transparency's role in reducing dissent." Phrases like "worth reporting as a real, honest result" were flagged as self-announcing. Adopted per PLAN.md.
AI REVIEW: "Data Quality and Robustness" should open with the number ("Recall against the recorded vote is 88.8 percent"), "The methodological justification sentence can follow rather than lead." (Whether adopted: draft3 notes say "section openings rewritten"; not verified per section.)
AUTHOR (draft5 pass): the Data Quality/robustness section demoted and merged into "Robustness and What the Two Axes Do Not Explain"; "No content deleted, only ..." reorganized.

## 5. Things to avoid (collected)
AUTHOR: causal verbs for associations ("governs", "causes", "does not survive"); "disposition" for the classifier output; "not a proxy ..., but a projection" for PC1; "stays silent, correctly"; "lit up everywhere"; closing "coequal status" sentences; "strategy pillar" (the strategy axis contains both pillars; "second pillar" must not name the macro axis); research-process material in reader-facing text ("every RiskSplit/output/... file-path reference and 34_*.csv filename was removed from the main prose and table notes"; "'the two fixes flagged as required in the previous draft are complete' was replaced with a direct statement of the findings"); dedicated main-text sentences pointing to appendices; excessive preview/review scaffolding; long section-opening roadmaps; unexplained jargon at first use; redundant restatement of a prior section's result ("Shortened Section 5.1's opening so it stops re-deriving Section 4's result"); duplicate verbatim phrases reused in two sections; "as discussed above" style bookends ("pure bookend redundancy").
AI REVIEW (not necessarily author-adopted verbatim): colloquialisms such as "kitchen-sink"; psychometric terms ("discriminant validity", "construct validity") without a plain gloss; meta-commentary about the act of stating a claim ("The claim this note makes ... is best stated explicitly"); heavy "X, not Y" / "rather than" antithesis.
Note: the "banned phrase list" and "Stage-3/Stage-5 instructions" are cited by the audit but the full list is NOT in the repo; only the phrases quoted above are known.

## 6. Structure and length
AUTHOR: abstract 175-225 words; paper target 24-26 pages for DissentNote (draft5 was 29, "flagged honestly to the user rather than claimed as hitting their 24-26 target"); long note PaperV3 repeatedly trimmed (page counts tracked, "total page count and main-text length are different things, and the directive was specifically about the latter").
AUTHOR: standing rule to shorten main text every pass, with demotion to appendix (and wholesale deletion when the user says so: "Went beyond the appendix-demotion option to full deletion", DECISION_LOG ~1338).
AUTHOR: conclusion = five paragraphs (question, validation, new findings, three literature strands, limitations); each caveat stated once in the paper and cross-referenced elsewhere.
AUTHOR: introduction contribution paragraphs map one-to-one to body sections 4/5/6 and to the abstract's three parts; section titles are noun phrases ("matching Section 4's existing noun-phrase title convention" replacing "old question-style title", DECISION_LOG ~1389).
AUTHOR: tables introduced at first mention and then referred back to ("the table's next two columns"); sideways table when too wide; table conventions matched to existing paper style ("matching this note's existing table style", PLAN.md ~87).
AUTHOR: figures: "keep the direct-comparison dot-plot style" (PLAN.md ~1816); new figures "regenerated in the same visual style".
AUTHOR (PLAN.md ~87-96, 2300): when the user asks for "very short bullet points" with no analysis prose, deliver tables plus short factual bullets and no prose yet.
AI REVIEW (style_review.md Finding 24-25): cut closing sentences that restate what a table already shows; cut opening "preview" sentences that the paragraph then re-derives at its close.

## 7. INTERPRETATION (mine)
- The strongest, most repeatedly confirmed author preferences: plain declarative sentences with trailing hedges; claims scoped to what was measured (association, not causation); one statement of each caveat; no scaffolding or process talk; consistent terminology; lead with the finding.
- The AI style review's numeric targets (antithesis density; sentence counts) are reviewer metrics, not author rules, though the author's later sessions used them as checks.
- The style benchmark is the author's own earlier paper (PaperV3/paper/draft5_revised.tex, "Two Pillars"); style comparisons were measured against its text. I did not read it, so I cannot quote its register directly.
