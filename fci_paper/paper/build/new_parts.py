# New text of the restructured paper (stance question). Numbers are macros \bl{...} from replication/report/numbers.tex.
ABSTRACT = r"""How much do financial conditions add to the stance of monetary policy beyond the policy rate? I measure conditions in policy units, as the move in the two-year yield that would bring the same change, and relative to the neutral rate $\rs$. The weights on the 10-year yield, equity valuation and the dollar come from their responses to monetary policy news in announcement windows. Over 1976--2026 the index explains unemployment a year ahead beyond the real funds rate relative to $\rs$, and the funds-rate gap adds nothing to the index. The information is in the 12-month change of the index, not in its level, and it is absent for core inflation. In 2004--06 the index read \bl{abs:st:ep0:diff:point} points looser than the funds-rate gap, and in 2022--24 \bl{abs:st:ep1:diff:point} points. The index complements the Chicago Fed's NFCI, which carries the longer horizons and recession risk. Removing what lagged unemployment and inflation explain cuts its unemployment response by \bl{pg:fall:full} to \bl{pg:fall:rec} percent. Put on a common basis (nominal, real, relative to $\rs$), the main indexes agree on direction and differ by about one point in level. The results hold on 1996--2026, with smaller effects."""

INTRO = r"""\section{Introduction}
\label{sec:intro}
Is monetary policy tight or loose? The policy rate does not answer by itself. Policy works through long yields, stock prices and the dollar, and these respond to much else, so the same funds rate can be more or less restrictive at different times. An index of financial conditions has long been proposed as a guide to the stance of policy, a counterpart of the Taylor rule \citep{hatzius2010}, and policymakers describe policy this way. In November 2023 the Chair noted that ``Financial conditions have tightened significantly in recent months, driven by higher longer-term bond yields, among other factors'' \citep{powell2023}. The indexes do not always agree. In March 2024 the Chair said that ``there are many different financial conditions indicators, and you can kind of, you know, see different answers to that question'' \citep{powell2024}.

I ask how much financial conditions add to the stance of policy beyond the policy rate, and whether the difference says anything about the economy ahead.

They add, and the addition is informative about unemployment. I measure financial conditions with a market index in policy units: a one-point move in the index is the change in conditions that a policy move raising the two-year yield by one percentage point brings. The index and the funds rate are both measured relative to the neutral rate $\rs$. Over 1976--2026, adding the index to the real funds rate relative to $\rs$ raises the adjusted $R^2$ of the change in the unemployment gap a year ahead by \bl{st:du:flow:gain} ($t=$ \bl{st:du:flow:t}), while adding the funds-rate gap to the index adds \bl{st:du:flow:gainff}. The information is in the index's 12-month change, as it is in the Board's FCI-G, and not in its level. The index adds nothing for core inflation. In 2004--06 the index read \bl{abs:st:ep0:diff:point} points looser than the funds-rate gap, and in 2022--24 \bl{abs:st:ep1:diff:point} points looser (Figure~\ref{fig:wedge}).

\begin{figure}[tp]
\centering
\includegraphics[width=0.93\textwidth]{../replication/report/fig_wedge.pdf}
\caption{The Market Index and the Funds-Rate Gap}
\label{fig:wedge}
\begin{flushleft}\footnotesize\textit{Notes:} Monthly. The funds-rate gap is the effective funds rate less one-year expected inflation less $\rs$ (Laubach--Williams); the market index is relative to $\rs$ in two-year-yield points; each is shown less its 1973--2026 mean. The wedge is the index less the gap, with a 90 percent interval from bootstrap samples of the announcements that set the index's weights. Shaded: 2004--06 and 2022--24.\end{flushleft}
\end{figure}

The index complements the Chicago Fed's NFCI instead of replacing it: the NFCI carries the longer horizons and recession risk, and the market index carries the next six to twelve months. A third to two thirds of the index's unemployment response is activity that lagged unemployment and inflation explain. The results hold on 1996--2026, the sample of the weights, at smaller size, and fail for payrolls. Put on a common basis, the major indexes agree on direction and differ by about one point in level.

The approach has three features. First, I build the index and put it on a common basis. Its weights are the responses of the 10-year yield, equity valuation and the real dollar to monetary policy news in narrow windows around FOMC announcements, combined to recover the news as precisely as possible. A two-variable VAR with the unemployment gap gives it a level and a flow. I measure every index in three steps, nominal rates, real rates and gaps to $\rs$, and at each step I compare like with like: my nominal index with nominal versions of the Goldman Sachs index, FCI-G and an index weighted with FRB/US, my real index with real versions, and my $\rs$ index with $\rs$ versions. Second, I compare the index with the real funds rate relative to $\rs$ and ask whether it adds for unemployment, payrolls and inflation, in sample and out of sample, with the uncertainty of the weights and of $\rs$ in the statements about episodes. Finally, I ask whether the flow is only activity reflected back, how it relates to the NFCI, whether the neutral-rate step and the weights matter for outcomes, and whether the results hold on 1996--2026 and with data as known at the time.

\subsection{Connection to the Literature}
\textbf{The stance of policy.} The first purpose of a financial conditions index in \citet{hatzius2010} is to serve as one guide to the effective stance of policy after taking into account all other factors, as a Taylor rule does; their examples are the conundrum of 2004--06, when conditions stayed easy as the funds rate rose, and late 2008, when conditions were restrictive at a zero funds rate. \citet{dudley2010} adds that higher stock prices and faster productivity growth raise the equilibrium rate, so that the same funds rate is less restrictive. I measure the wedge between an index and the funds-rate gap in common units and test whether it matters.

\textbf{Units and flows.} \citet{ajello2023} express conditions as their drag on GDP growth over the next year, with weights from FRB/US multipliers applied to changes, so that FCI-G is a flow with zero neutral for growth. \citet{caballero2026} define FCI$^*$, the level of FCI-G consistent with output at potential, as the analogue of $\rs$. I express indexes in policy units, give the market index a flow of the FCI-G form, and measure rates relative to $\rs$; I do not estimate a neutral level for the index itself.

\textbf{Stress, risk and the tail.} The Chicago Fed's NFCI and ANFCI summarize 105 indicators of risk, credit and leverage by a dynamic factor model \citep{brave2011}; \citet{adrian2019} show that conditions shift the lower quantiles of growth. I treat them as a different kind of index, set the market index beside the NFCI, and report the lower tail in sample only.

\textbf{Weights and comparisons.} Weights come from effects on output \citep{dudley2000,hatzius2018,ajello2023}, from principal components \citep{brave2011} or, as here, from event-study regressions \citep{kuttner2001,gurkaynak2005,bernanke2005,nakamura2018,bauer2023}. \citet{aramonte2013} compare twelve indexes by correlations of standardized series, \citet{arnaut2024} estimate the response of the Goldman Sachs index to policy surprises, and \citet{sack2023} relate FCI-G to policy-induced changes in the two-year yield. I put the indexes on one basis and ask what the market index adds to the stance, and I report the sampling error of its weights.

\textbf{The neutral rate.} What matters is the rate relative to the neutral rate, which fell from the 1990s to the 2010s \citep{laubach2003,holston2017,holston2023,hamilton2016,bauer2020,kiley2020}. I test whether measuring the inputs relative to $\rs$ improves what the index says about the economy and report the answer as it is.
\FloatBarrier
"""

SEC5 = r"""
% ============================================================
\section{The Stance beyond the Policy Rate}\label{sec:stance}
\subsection{The Funds-Rate Gap and the Wedge}\label{sec:wedge}
The stance of policy read from the policy rate is the funds-rate gap: the effective federal funds rate less one-year expected inflation less $\rs$. The stance read from financial conditions is the market index relative to $\rs$. Each is measured relative to its 1973--2026 mean. They differ in units, two-year-yield points for the index and funds-rate points for the gap, and the comparison treats a point of each as a point of policy. The wedge is the index less the gap. A policy move that raises the two-year yield raises both. A rise in the dollar or a fall in equity valuation that policy did not cause raises only the index, and the wedge is the part of conditions that the funds rate does not carry. Levels of the two correlate \bl{corr:mkt:rstar:level:full} over 1976--2026 and their 12-month changes \bl{corr:mkt:rstar:flow:full}; they are \bl{corr:mkt:rstar:level:p0406} and \bl{corr:mkt:rstar:flow:p0406} in 2004--06, when the funds rate rose and conditions did not follow.

\subsection{Does the Wedge Matter for the Economy Ahead?}\label{sec:stancetest}
Table~\ref{tab:stance} adds the index to the funds-rate gap in projections of the change in the unemployment gap, payroll growth and core inflation 12 months ahead.

\input{../replication/report/tab_stance}

\textbf{Unemployment.} The funds-rate gap alone explains little (the $t$-statistic of its 12-month change is \bl{st:du:flow:tff}), and the index alone explains much (\bl{st:du:flow:tidx}). Given the gap, the index raises the adjusted $R^2$ by \bl{st:du:flow:gain} in the flow form and by \bl{st:du:mixed:gain} when the gap enters as a level; given the index, the gap adds \bl{st:du:flow:gainff} and \bl{st:du:mixed:gainff}. In levels the index adds \bl{st:du:level:gain} ($t=$ \bl{st:du:level:t}). The result holds for the Goldman Sachs index (gain \bl{st:du:gs:gain}) and the FRB/US index (\bl{st:du:frbus:gain}), and the $t$-statistic of the market index rises with the step, from \bl{st:du:nominal:t} in nominal terms to \bl{st:du:real:t} in real terms and \bl{st:du:flow:t} relative to $\rs$.

\textbf{Out of sample.} Recursive forecasts from 1995 cut the root mean squared error by \bl{st:du:flow:rmse} (flow) and \bl{st:du:mixed:rmse} (mixed) relative to the gap alone, with Clark--West statistics of \bl{st:du:flow:cw} and \bl{st:du:mixed:cw}. The primary family has nine tests, three outcomes in three forms; five reject at the 10 percent level before adjustment, and one survives the Holm correction (the mixed form for unemployment, adjusted $p=$ \bl{st:prim:mixed:holm}). The out-of-sample gains are modest.

\textbf{Payrolls and inflation.} For payrolls the gain is \bl{st:pay:flow:gain} in the flow form and the out-of-sample statistic is \bl{st:pay:flow:cw}; for core inflation the index adds nothing (gain \bl{st:pi:flow:gain}). The claim is about unemployment.

\textbf{Which periods.} In 2009--15, when the policy rate was at its lower bound, the funds-rate gap forecasts worse than the own lags (RMSE ratio \bl{st:du:zlb:rmseff}); the index adds in sample ($t=$ \bl{st:du:zlb:t}, \bl{st:du:zlb:n} months) and not significantly out of sample (Clark--West \bl{st:du:zlb:cw}). In 2022--26 the sample is about three independent years and the index has $t=$ \bl{st:du:post:t}.

\subsection{Episodes and Today}\label{sec:episodes}
Table~\ref{tab:stancepisodes} gives the wedge in three episodes and for September 2026.

\input{../replication/report/tab_episodes_stance}

In June 2004 to June 2006 the funds-rate gap averaged \bl{st:ep0:ffg} and the index \bl{st:ep0:index_point}, a wedge of \bl{st:ep0:diff:point} with a 90 percent interval from \bl{st:ep0:diff:lo} to \bl{st:ep0:diff:hi}; the interval is below zero in \bl{st:ep0:share} percent of the bootstrap samples. With the estimate of \citet{kiley2020} for $\rs$ the wedge is \bl{st:ep0:kiley}. This is the conundrum of \citet{hatzius2010}: conditions stayed easy while the funds rate rose. From March 2022 to December 2024 the wedge is \bl{st:ep1:diff:point} (interval \bl{st:ep1:diff:lo} to \bl{st:ep1:diff:hi}; Kiley \bl{st:ep1:kiley}). It depends on the end date: to December 2023 it is \bl{st:ep2:diff:point} and the interval includes zero. For September 2026 the funds-rate gap is \bl{st:today:ffg} and the index \bl{st:today:index}, a wedge of \bl{st:today:wedge} (interval \bl{st:today:lo} to \bl{st:today:hi}; negative in \bl{st:today:share} percent of the samples). The intervals cover the uncertainty of the weights and the choice of $\rs$ between two estimates. They do not cover the uncertainty of $\rs$ itself or of the funds-rate gap's expected inflation.

\subsection{What Carries the Wedge}\label{sec:carries}
Equity valuation carries it. Entering the three variables' contributions separately, equity valuation raises the adjusted $R^2$ for unemployment by \bl{cp:du:equities:gain} ($t=$ \bl{cp:du:equities:t}), the 10-year yield and the rates group by \bl{cp:du:rates:gain}, and the dollar by \bl{cp:du:dollar:gain}. The index is not a summary of rates. Equity prices also lead the cycle, which Section~\ref{sec:purge} takes up.
\FloatBarrier

% ============================================================
\section{What the Index Says about Activity}\label{sec:activity}
\subsection{The Flow, Not the Level}\label{sec:levelflow}
Table~\ref{tab:levelflow} enters the level and the 12-month change of each index together. For the market, Goldman Sachs and FRB/US indexes relative to $\rs$ the flow has $t$-statistics of \bl{lf:du:mkt:t:flw:both}, \bl{lf:du:gs:t:flw:both} and \bl{lf:du:frbus:t:flw:both} for unemployment and the level \bl{lf:du:mkt:t:lvl:both}, \bl{lf:du:gs:t:lvl:both} and \bl{lf:du:frbus:t:lvl:both}. The NFCI and ANFCI are the reverse: the level has $t=$ \bl{lf:du:nfci:t:lvl:both} and \bl{lf:du:anfci:t:lvl:both} and the flow \bl{lf:du:nfci:t:flw:both} and \bl{lf:du:anfci:t:flw:both}. FCI-G, a flow by construction, carries it in its reading.

\input{../replication/report/tab_levelflow}

The Granger test on the 12 lags of the level in the VAR is strongly significant ($p=$ \bl{lf:mkt:p:all}), which looks like a conflict. Table~\ref{tab:granger} resolves it. Rewriting the 12 lags as the current level and 11 one-month changes, the current level is not significant ($p=$ \bl{lf:mkt:p:sum}) and the changes are ($p=$ \bl{lf:mkt:p:diff}): the test picks up the movement of the level within the year, not where it stands. The result for the level depends on 2008--15. Excluding those years the level has $t=$ \bl{ck:c12:tlevel} (Table~\ref{tab:checks96}).

\input{../replication/report/tab_granger}

\textbf{The lower tail.} Following \citet{adrian2019}, I estimate quantile regressions for payroll growth. In sample the market index's flow shifts the 10th percentile, with a coefficient of \bl{lf:q10:b} (90 percent interval \bl{lf:q10:lo} to \bl{lf:q10:hi}), the same as in the mean. The NFCI level shifts it by \bl{lf:q10:nfci:b} (\bl{lf:q10:nfci:lo} to \bl{lf:q10:nfci:hi}). Out of sample the tail cannot be tested: the evaluation sample has \bl{levelflow:oos:recessions} recessions.

\subsection{The NFCI}\label{sec:nfci}
The NFCI and ANFCI beat the common-basis indexes for unemployment at long horizons and for recessions. They are a different index: a level index of credit, risk and leverage, mostly spreads. The three variables of the market index explain \bl{nfci:decomp:level:nfci:3:vars:R2} of the NFCI's level, and \bl{nfci:decomp:level:nfci:3:vars:plus:spread:R2} when the Baa--10-year spread is added. Table~\ref{tab:nfci} enters the market flow and the NFCI level together. For unemployment at 6 and 12 months both keep their coefficients ($t=$ \bl{nf:du6:mkt:t} and \bl{nf:du12:mkt:t} for the market flow, \bl{nf:du6:nfci:t} and \bl{nf:du12:nfci:t} for the NFCI). At 24 months only the NFCI remains (\bl{nf:du24:nfci:t}, against \bl{nf:du24:mkt:t}), and for recessions the NFCI has $t=$ \bl{nf:rec1212:nfci:t} against \bl{nf:rec1212:mkt:t}. The two are complements: the market index is a policy-channel flow in policy units that carries the next six to twelve months, and the NFCI carries the longer horizons and recession risk. It is not a stress or recession monitor.

\input{../replication/report/tab_nfci}

\subsection{Is the Flow Only Activity Reflected Back?}\label{sec:purge}
Asset prices respond to expected activity, and \citet{hatzius2010} purge each indicator of current and lagged growth and inflation so that the index reflects exogenous conditions; the ANFCI does the same. I regress each input on the unemployment gap and core inflation (current and 12 lags), on the full sample and recursively, and rebuild the index from the residuals with the same weights. Table~\ref{tab:purge} gives the VAR response. The 12-month response of the market index falls from \bl{pg:market:unpurged} to \bl{pg:market:full} with the full-sample purge and \bl{pg:market:recursive} with the recursive purge, and every interval stays above zero; the Goldman Sachs index is similar. Purging is not identification, and it removes too much when asset prices rightly respond to expected activity. The flow carries both a channel and an anticipation component, and for payrolls it does not survive the purge.

\input{../replication/report/tab_purge}

\subsection{The Neutral Rate and the Weights}\label{sec:rstarweights}
\textbf{The neutral rate.} The $\rs$ step makes the level of the index mean the same thing across regimes to a degree. At a zero unemployment gap the index level in 2009--19 is \bl{nu:nominalma} lower than in 1990--2007 in nominal terms and \bl{nu:realma} lower in real terms, and \bl{nu:rstarma} different relative to $\rs$ (Laubach--Williams) and \bl{nu:rstar:kileyma} with Kiley's estimate (Table~\ref{tab:neutrality}). The step shrinks the post-2008 drift but does not remove the fall in the unemployment response after 1989, and the unit restriction it imposes on $\rs$ cannot be tested at this power. For outcomes, the $\rs$ versions have lower out-of-sample error than the nominal versions in \bl{lad:rstar:vs:nominal:all:n:ratio:below1} of \bl{lad:rstar:vs:nominal:all:n:tests} comparisons across seven index families, five outcomes and horizons; \bl{lad:rstar:vs:nominal:all:n:dm:sig10:better} Diebold--Mariano tests favor $\rs$ and \bl{lad:rstar:vs:nominal:all:n:dm:sig10:worse} the nominal version at the 10 percent level, none survives the Holm correction at 5 percent, and the mean error ratio is \bl{lad:rstar:vs:nominal:all:mean:rmse:ratio}. The tests share data, so the counts are descriptive. For unemployment the in-sample gain of the $\rs$ version over the nominal version is \bl{ld:p96:dr2} on 1996--2026 (interval \bl{ld:p96:lo} to \bl{ld:p96:hi}) and \bl{ld:pre96:dr2} before 1996. The outcomes lean toward the $\rs$ basis without proving it; it rests on the argument of \citet{dudley2010} and \citet{caballero2026} that the rate relative to neutral is what matters.

\input{../replication/report/tab_neutrality}

\textbf{The weights.} No alternative weights beat the market weights. Replacing them with the FRB/US weights, the first principal component, equal weights or weights fitted to activity gives mean squared errors 1.04 to 1.07 times those of the market weights for the 12-month change, \bl{w:rstar:n:raw:sig10} of \bl{w:rstar:n:primary:tests} paired tests reject at 10 percent before adjustment and \bl{w:rstar:n:holm:sig10} after. Weights fitted to activity are too imprecise to rank any set. Outcomes cannot settle the weights question; the policy-news weights are not beaten.
\FloatBarrier
"""

SEC8 = r"""
% ============================================================
\section{Robustness and Limits}\label{sec:rob}
The results rest on one sample, one set of weights, one estimate of $\rs$ and data revised after the fact. I vary each in turn. Table~\ref{tab:checks96} gives the main checks.

\subsection{The Sample: 1996--2026}\label{sec:sample96}
The weights come from announcements since 1996, so the sample of 1996--2026 is the one on which the index is estimated, and the sample of Note B. I re-estimate the VAR and the regressions from 1996. The response of unemployment after 12 months is \bl{ck:a12:phi} (\bl{ck:a12:lo} to \bl{ck:a12:hi}) on 1973--2026, and \bl{ck:b12:phi} (\bl{ck:b12:lo} to \bl{ck:b12:hi}) with 12 lags and \bl{ck:b4:phi} (\bl{ck:b4:lo} to \bl{ck:b4:hi}) with four lags on 1996--2026: it does not change sign, and the interval is about 1.6 times as wide. The estimate from VARs on shorter spans is \bl{vs:197389} for 1973--89, \bl{vs:19902007} for 1990--2007, \bl{vs:19962007} for 1996--2007, \bl{vs:19962019} for 1996--2019 and \bl{vs:20092026} for 2009--26. The flow has $t=$ \bl{ck:b12:tflow} for unemployment (\bl{ck:a12:tflow} on the long sample), with a gain of \bl{ck:b12:gain} in adjusted $R^2$ against \bl{ck:a12:gain}; the index adds \bl{ck:b12:stgain} to the funds-rate gap, with a Clark--West statistic of \bl{ck:b12:cw} (one recession in the out-of-sample period). The payroll flow has $t=$ \bl{ck:b12:payt} and the payroll result does not hold. The $\rs$ step helps on 1996--2026 and not before.

\input{../replication/report/tab_checks96}

\subsection{Weights That Move}\label{sec:drift}
The weights define the unit, so I hold them fixed and show how they would drift. Re-estimating on an expanding window of announcements from 2006 keeps the 10-year and dollar weights inside the 90 percent band of the full-sample estimate at every date after 2010; the equity weight is outside at \bl{exp:post2010:n:out:eq} dates in 2011--14, by at most \bl{exp:post2010:min:eq} against a band edge of \bl{base:lo:eq} (Figure~\ref{fig:weightpath}). A 20-year rolling window fails after 2021, because it drops the announcements of 1996--2005 (the 10-year weight is outside the band at \bl{roll:post2010:n:out:ten} dates). The 10-year weight is imprecise throughout (interval \bl{base:lo:ten} to \bl{base:hi:ten}). The index built with the expanding-window weights correlates \bl{corr:level:1996:rstar} with the baseline in levels, \bl{corr:d12:1996:rstar} in 12-month changes and \bl{corr:fi:basePhi:1996:rstar} in forward impetus, and the VAR response is \bl{phi12:rt:rstar} against \bl{phi12:base:rstar}. The weights drift less than their own sampling error.

\begin{figure}[tp]
\centering
\includegraphics[width=\textwidth]{../replication/report/fig_weight_path.pdf}
\caption{The Weights on an Expanding and a Rolling Window}
\label{fig:weightpath}
\begin{flushleft}\footnotesize\textit{Notes:} Weights of the market index re-estimated on announcements to each date (expanding window, from the 80th announcement) and on the latest 20 years (rolling). Shaded: 90 percent bootstrap interval of the full-sample weights; the horizontal line is the full-sample weight.\end{flushleft}
\end{figure}

\subsection{Data as Known at the Time}\label{sec:realtime}
Nothing in the baseline is real time. I rebuild the unemployment and payroll inputs from ALFRED vintages (unemployment and payrolls from 1977, the CBO natural rate from 2011) and the $\rs$ input from the New York Fed's real-time Laubach--Williams estimates (from 2005). The weights, the Kiley $\rs$, the earnings in CAPE and expected inflation are not real time, so this is pseudo real time in the macro variables and in $\rs$ from 2005, and not in the weights. Table~\ref{tab:realtime} gives the unemployment results. Vintage data leave them unchanged ($t=$ \bl{rt:vin1976:t} against \bl{rt:rev1976:t}, Clark--West \bl{rt:vin1976:cw} against \bl{rt:rev1976:cw}); with the vintage natural rate from 2011 the flow has $t=$ \bl{rt:vinn2011:t}; and with real-time $\rs$ from 2006 the gain falls from \bl{rt:revf2006:gain} to \bl{rt:revr2006:gain} ($t=$ \bl{rt:revr2006:t}), with the mixed form no longer significant ($t=$ \bl{rt:revr2006:mt}). Real-time $\rs$ weakens the flow.

\input{../replication/report/tab_realtime}

\subsection{The Neutral Rate, the Dynamics, the Weights and the Zero Point}\label{sec:robother}
Table~\ref{tab:robust} varies the construction. In every row the market index's correlation is at least \bl{rb:min:mkt:gs} with the Goldman Sachs index and at least \bl{rb:min:mkt:frbus} with the FRB/US index, and the 90 percent interval of the yardstick lies above zero.

\input{../replication/report/tab_robust}

With the estimate of \citet{kiley2020} the market index reads \bl{rb:1:latest:market} in September 2026 against \bl{rb:0:latest:market}, and the Goldman Sachs and FRB/US readings move by less than half a point. With four lags the yardstick is \bl{rb:2:phi12}. Re-estimating the weights with the two-year yield as the policy news, with announcements through 2019, or without the lower-bound years (Appendix Table~\ref{tab:wvar}) moves the September 2026 reading from \bl{rb:6:latest:market} to \bl{rb:5:latest:market}, a spread of \bl{rb:spread:weights} points, as wide as the bootstrap interval of Section~\ref{sec:precision}. The readings follow the equity weight, which is \bl{wv:two:year:w:eq}, \bl{wv:to:2019:w:eq} and \bl{wv:no:lower:bound:w:eq} against \bl{w:eq} in the baseline. With 1990--2026 as the base period the market index reads \bl{rstar:latest90:market}, the Goldman Sachs index \bl{rstar:latest90:gs} and the FRB/US index \bl{rstar:latest90:frbus}, shifts of about a point.

\subsection{Limits of the Design}\label{sec:limits}
The $\rs$ step is the largest effect in the paper, and the outcomes lean toward it without proving it. The uncertainty of $\rs$ is not in the intervals, and $\rs$ is not neutral to outcomes, because the Laubach--Williams model uses output, inflation and unemployment. The weights come from announcements since 1996 and are applied from 1973; they assume that the responses reflect policy rather than information effects \citep{nakamura2018}, and if policy came to target financial conditions the responses could change, the Lucas-critique concern that \citet{hatzius2010} raise for all indexes. The bootstrap treats the FRB/US and Goldman Sachs weights, the Goldman Sachs conversion and the VAR as fixed. The sample has five recessions, two out of sample, and 12-month outcomes overlap, so the counts of tests are descriptive. The VAR is linear and describes the mean. The Goldman Sachs index and FCI-G are my replications, and the FRB/US index is my construction at one horizon. The readings for September 2026 use $\rs$ through 2026Q2 and interpolate October 2025.
\FloatBarrier
"""

DISCUSSION = r"""
% ============================================================
\section{Discussion}\label{sec:discussion}
Three points follow for reading the stance of policy.

\textbf{Financial conditions add to the policy rate, through changes.} The funds-rate gap tells little about unemployment a year ahead once the index is in, and the index tells much once the gap is in. What it tells is in how conditions have moved over the year, in policy units and relative to $\rs$, not in where they stand. In 2004--06 and in 2022--24 the index read more than a point looser than the gap, and in September 2026 the wedge is \bl{st:today:wedge}. These are readings of the stance with intervals, and the stance from the policy rate alone misses them.

\textbf{The index is a channel measure, not a forecaster or a stress monitor.} It carries the next six to twelve months of unemployment, in a form that survives purging of lagged activity at about half its size. It does not carry inflation, payrolls on 1996--2026 or recession risk, and the NFCI carries the longer horizons. Out-of-sample gains are modest.

\textbf{The neutral rate changes the readings.} In nominal terms the market index reads \bl{nominal:latest:market} points for September 2026, relative to $\rs$ \bl{rstar:latest:market}, and the step reverses the picture after 2008. The indexes agree on direction (12-month changes correlate \bl{rstar:mkt:gs:chg} with the Goldman Sachs index and \bl{rstar:mkt:frbus:chg} with the FRB/US index) and differ in level by about \bl{rstar:range:long} point on average, of the order of the sampling error of the market index's weights. Outcomes lean toward the $\rs$ basis, and the policy-news weights are not beaten.

\textbf{What the results do not show.} There is no ground truth for financial conditions. Zero is the 1973--2026 average of each variable, not a neutral level of conditions. The index measures the policy-equivalent tightening and treats movements that policy did not cause as if it had; the unemployment response is the claim, and the index carries both a channel and an anticipation component.
\FloatBarrier

% ============================================================
\section{Conclusion}\label{sec:conclusion}
Financial conditions add to the stance of policy beyond the policy rate. Measured in policy units and relative to the neutral rate, the market index explains unemployment a year ahead beyond the real funds rate relative to $\rs$, through its 12-month change, and not inflation. It complements the NFCI, which carries the longer horizons and recession risk, and it holds on 1996--2026 at smaller size. The wedge between the index and the funds-rate gap was about \bl{abs:st:ep0:diff:point} points in 2004--06 and \bl{abs:st:ep1:diff:point} points in 2022--24. On a common basis the indexes agree on direction and differ by about a point in level, and the neutral rate changes the reading most. The most durable finding is the wedge and what it says for unemployment, and the answer to what a statement about the stance should say is a range, relative to $\rs$.

"""
