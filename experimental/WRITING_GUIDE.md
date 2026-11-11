# Writing and working guide for the author's papers in this repo

Status: written 11 Nov 2026 from the Note B revision session (the author's own words and reactions, and the reviewer rounds that the author directed). It applies to every paper and note in `experimental/` and `fci_note/` and supersedes the evidence-only draft `fin_shocks/paper/STYLE_GUIDE_DRAFT.md`, which stays as the record of what the author's earlier papers do (quotations in `fin_shocks/paper/style_evidence/`). Read it before writing or editing any text. Where it conflicts with a default habit, follow the guide.

## 1. What the author wants a paper to be
- **An economics paper about an economic issue, not a technical report of numbers.** The reader should leave understanding why the result matters and what it says about policy. Numbers support an idea; they do not carry it.
- **Self-contained main text.** Readers do not read appendices. Whatever a reader needs to follow the method and judge the result is in the main text, with good intuition and a simple flow. The main text should be balanced against the appendix (about 30 or more pages in a 65-page draft, not 23). Appendices hold detail, full tables, alternative specifications and derivations.
- **A few exhibits that carry the argument, early.** A matched comparison (same surprise, sample, normalization, horizon, changing one thing) leads the results. Robustness cases never come before the main results.
- **Honest about what holds.** Results that hold across specifications are stated as holding. The exception is stated once, where it belongs (usually Section 4 or the section that tests it), as a fact. The abstract and conclusion state the finding that travels, with its sample, and attach a qualification only when a reader would otherwise be misled.

## 2. Prose rules (apply to all drafts)
1. **Ideas before numbers.** State the idea in words first; add the number that supports it, and no more. Not every case or every cell belongs in the text.
2. **Short, direct, active sentences.** One claim per sentence. First person singular ("I"). The object of study or "I" is the subject.
3. **No hedging for its own sake.** Hedge only where the evidence requires it, and then say exactly what is uncertain. No "somewhat", "borderline", "arguably", apology, or "it is worth noting".
4. **Avoid repetition.** State a point once, or as often as the reader needs it, and no more. Numbers quoted in the abstract, introduction and body should be the few that matter; the introduction names a result, the body proves it.
5. **No AI speak and no abrupt technical transitions.** No "delve", "landscape", "it is important to note", stacked "furthermore" chains, or sentences that announce what will be said. Introduce a concept before comparing with it or testing it. Do not discuss a result before the object it concerns has been defined (a comparison with real versions comes after the real version is introduced).
6. **Write forward.** The question, the approach, the core results, then robustness. Do not mention later results to set up the next point; no forward references that stand in for an argument.
7. **Plain words.** Prefer the simple word. "Associated with" for associations, not causal verbs. One term for one thing, used identically throughout.
8. **Verdicts in words, intervals in tables.** Significance at the 5 and 10 percent levels (`**`, `*`); 90 percent intervals, 68 percent bands in figures that show paths. No percentage shares where the total is small.
9. **Define units and the experiment once and use them everywhere** (here: per +1 pp on the two-year yield in the window).
10. **Do not claim more than the tables show.** Before a sentence says "every", "never", "in all variations", check it against the appendix tables. One exception (for example, one lag length in one specification) breaks a categorical claim; rewrite it as the matched result that is true.

## 3. Structure the author prefers
- **Abstract:** short declaratives; the question, the finding that travels across specifications (with its sample), the mechanism, the policy number (here the sacrifice ratio), the qualification the reader needs. No process language.
- **Introduction:** the question and why it matters for policy; the answer; one early figure that makes the matched comparison (Figure 1); the approach as First / Second / Finally; the literature after, short, with a precise statement of what differs from the closest papers (for example, fixing the conventional rate-news direction versus selecting the shock for its macroeconomic content).
- **Methods:** build the measurement in the order a reader meets the problems (nominal index, its trend problem, the real index, the remaining trend, the neutral-rate version). Give an economic example for each identifying assumption (earnings news versus a discount-rate move). State what the design can and cannot show (a yield-only model is not wrong by construction; the claim is about this experiment and these data).
- **Results:** the matched table first, then the decomposition that explains it, then the policy ratio (with the 'undefined' cases reported as undefined, with a 68 percent set where it exists, never "unbounded"), then the tests of the key assumptions.
- **Robustness:** its own section, each variation introduced by why it is a good test, results stated plainly and briefly.
- **Discussion and conclusion:** what the results mean for the stance of policy and the cost of price restraint; what they do not show. The conclusion is short and ends on the most durable finding and its policy reading.
- **Exhibits:** compact in the main text (a few rows, the baseline in bold); full versions in the appendix; tables in numerical order with notes attached; wide tables shrunk to the page, tall tables as longtables. A reader should not meet a large table before the idea it tests.
- **Proportionality or weights material** is a minor check, not a headline, unless the data make it central (in Note B it turned out to matter for prices from 1996; it is stated once in the abstract and tested in its own subsection).
- **LaTeX house style** (the FOMC papers): `article` 11pt, 1 inch margins, 1.5 spacing, `[tp]` floats, Title Case headings and captions, `Notes:` line under floats, `natbib` with `aea.bst`, `appendices` environment, title footnote with affiliation, views disclaimer and AI-tools statement.

## 4. How the author likes to work
- **Fewer round trips.** "This is very slow." Execute a complete instruction set end to end, then report. Do not stop to ask about choices that have a conventional default; state the choice and proceed.
- **Independent judgment is valued.** When the author's premise is only partly supported by the data, say so plainly with the numbers and propose what the data do support (the Goldman comparison: the premise was supported once the right series was used; I had first used the wrong one). Disagree with evidence, not deference.
- **Reviewers are a tool.** The author directs two or more independent reads (one against the author's standards, one against the target journals' standards), asks for the common lessons, and later asks for a fresh read of the previous and current versions. Welcome new reactions; they sharpen once other issues are fixed.
- **Reproducible by construction.** Every number in the text is a macro generated by the scripts; every qualitative claim is asserted in code and fails the build if it stops being true; every table and figure is read from `report/`. The paper, scripts and documentation are kept in sync, and a sync check (re-running steps and comparing stored results) is part of closing a block of work. Document in `FS_QA.md` (decisions), `PROJECT_MEMORY.md` section 9 (status) and the package README (run order, exhibit-to-script table).
- **Compare like for like and pair the draws.** Nominal with nominal, real with real, r* with r*; contrasts on common bootstrap draws; one change at a time. Verify the baseline reproduces before extending it.
- **Verify, tag and flag.** Tag claims [verified] / [secondhand] / [inference]; check citations (Crossref, original sources); say plainly what could not be checked. Unverified inputs stay on a visible list.
- **Branches.** Short branches from `main`, merged at the end of each block; update `PROJECT_MEMORY.md` section 9 before ending a session.

## 5. How these rules show up in the Note B draft (`fin_shocks/paper/mp_transmission.tex`)
- Figure 1 in the introduction is the matched comparison (r*-gap yield alone against yield plus FCI). Table 3 repeats it for the nominal, real and neutral-rate versions with paired intervals. The decomposition (Table 5, Figure 6) explains the difference; the sacrifice ratio (Table 6, compact) gives it its policy meaning.
- The index is built in the order of its problems (Section 2.2): nominal version and the Goldman comparison, the trend, the real version, the remaining trend, the neutral-rate version, the three together.
- The unemployment finding is stated as the matched 0.6 percentage-point shift across the three yield measures. The price result is stated with its sample and with the test that qualifies it (Section 3.6), not as "in every variation".
- Robustness is Section 4, each variation with its reason. The 3/6/12-lag table, persistence table, full multiplier table and alternative standard-method samples are in the appendix; the one-sentence versions are in the text.
- Wording corrections the author or readers required during the session are the pattern to avoid: a categorical robustness claim contradicted by an appendix table; a comparison discussed before its object was defined; a yield-only comparison made against the wrong (nominal) baseline; a large table placed before the results it qualifies; a direction error in a sentence about r*.

## 6. Checklist before sending a draft
1. Does the abstract lead with the question and the finding that travels, with its sample? Is every sentence checkable in the body?
2. Is each number in the text one the reader needs? Is any idea carried only by a number?
3. Is anything stated more strongly than the appendix tables allow? (Search for "every", "never", "all", "in any".)
4. Is any concept discussed before it is defined? Any forward reference doing the work of an argument?
5. Does the main text stand alone for a reader who skips the appendix? Is it balanced against the appendix?
6. Are tables in numerical order with notes attached, wide ones fitted, and no robustness table before the main results?
7. Do the macros all resolve, the claims all pass, the paper and the results match (run the sync check), and are the docs updated?
8. Are the open items (unverified citations, inputs) listed?
