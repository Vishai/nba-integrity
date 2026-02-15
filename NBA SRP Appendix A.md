# Appendix A: Historical Backtesting Framework

## Purpose

This appendix applies the Tanking Integrity Index retroactively to historical NBA team-seasons to answer three questions:

1. **Detection validity:** Does the TII correctly identify teams that were widely understood to be tanking?
2. **False positive resistance:** Does the TII correctly clear teams that were legitimately bad, injured, or experiencing natural variance?
3. **Threshold calibration:** Do the proposed Green/Yellow/Orange/Red cutoffs produce classifications that match informed consensus about each team's behavior?

If the TII cannot correctly sort known historical cases, the thresholds need adjustment before the framework is viable. If it can, the framework has empirical grounding that pure theoretical arguments cannot provide.

---

## Case Study Selection Criteria

Each backtesting case must include at least one team from each of these archetypes:

|Archetype|What It Tests|Target Classification|
|---|---|---|
|**The Obvious Tank**|Detection sensitivity — can the TII catch what everyone already knows?|Orange or Red|
|**The Legitimate Rebuild**|False positive resistance — does the TII leave honest bad teams alone?|Green|
|**The Injury-Wrecked Contender**|Context separation — can the TII distinguish bad luck from manipulation?|Green or Yellow|
|**The Mid-Season Pivot**|Temporal resolution — can the TII handle a team that competed early and tanked late?|Yellow or Orange|
|**The Systemic Cluster**|BTCA calibration — does the league-wide component activate when multiple teams tank simultaneously?|Tests ETP tier thresholds|

---

## Selected Case Studies

|Case|Team-Season|Archetype|Expected Classification|
|---|---|---|---|
|A|2013-14 Philadelphia 76ers (Process Year 1)|The Obvious Tank|Red|
|B|2015-16 Philadelphia 76ers (Process Year 3)|The Obvious Tank (sustained)|Red|
|C|2022-23 Portland Trail Blazers|Mid-Season Pivot / Integrity Failure|Orange or Red|
|D|2023-24 Washington Wizards|Legitimate Rebuild vs. Obvious Tank (ambiguous)|Yellow or Orange|
|E|2024-25 Utah Jazz|The Obvious Tank (current)|Red|
|F|2014-15 Minnesota Timberwolves|Legitimate Rebuild (control)|Green|
|G|2018-19 Golden State Warriors (post-KD/Klay injuries)|Injury-Wrecked Contender (control) — _Note: Use 2019-20 season_|Green|
|H|2025-26 league-wide cluster (Wizards, Pacers, Kings, Jazz)|Systemic Cluster — ETP tier calibration|Tests Tier 1-2 activation|

---

## Backtesting Template — Per Team-Season

Each case study follows this standardized evaluation structure. Data is organized by TII component with the same inputs, flag triggers, and scoring methodology specified in the main document (Section IV).

---

### CASE [LETTER]: [Team] — [Season]

**Archetype:** [Category from selection table] **Expected Classification:** [Green / Yellow / Orange / Red] **Final Record:** [W-L] **Lottery Position:** [Xth-worst record] **Key Context:** [1-2 sentence summary of what happened this season]

---

#### Component 1: Star Availability Score (SAS) — Weight: 30%

**1a. Identify Qualified Players (25+ min/game)**

|Player|Avg Minutes|Games Played|Games Missed|Verified Injury?|Notes|
|---|---|---|---|---|---|
|||||||
|||||||
|||||||

**1b. Absence Clustering Analysis**

|Metric|Value|Flag?|
|---|---|---|
|Total star-player games missed|||
|League age-adjusted baseline for this roster profile|||
|Standard deviations above baseline|||
|% of absences in games with competitive significance|||
|% of absences in games within 3 games of standings tiebreaker|||
|Absences in nationally televised games vs. expected rate|||

**1c. Severity Multiplier Check**

|Metric|Value|
|---|---|
|Star absences in games where team was within 5 at half||
|Star absences in projected blowouts (15+ spread)||
|Weighted absence ratio (1.5x competitive / 1.0x blowout)||

**1d. Exclusions Applied**

|Exclusion Type|Players Affected|Games Excluded|
|---|---|---|
|Season-ending injury (verified)|||
|Scheduled rest (PPP-compliant)|||
|Post-elimination chronic condition rest|||

**1e. SAS Component Score: _____ / 100**

**Scoring rationale:** [Narrative explanation of how the data maps to a score. What drove the number? What ambiguities exist?]

---

#### Component 2: Net Rating Collapse Index (NRCI) — Weight: 25%

**2a. Rolling 15-Game Net Rating Windows**

|Window (Games)|Net Rating|Expected NR (opponent-adjusted)|Residual|Schedule Strength|
|---|---|---|---|---|
|1-15|||||
|16-30|||||
|31-45|||||
|46-60|||||
|61-75|||||
|76-82|||||

**2b. Fourth-Quarter Isolation**

|Metric|Value|Flag?|
|---|---|---|
|Season-average Q4 net rating|||
|Post-ASB Q4 net rating|||
|Q4 net rating in games within 10 entering Q4|||
|Drop from season average|||
|Exceeds 6.0-point critical flag threshold?|||

**2c. Post-Trade Recalibration (if applicable)**

|Metric|Value|
|---|---|
|Trade deadline activity summary||
|Cumulative roster impact lost (EPM/RAPTOR)||
|Exceeds 15% roster impact threshold?||
|Recalibrated expected net rating (post-trade)||
|Performance vs. recalibrated expectation||
|Grace period (5 games) applied?||

**2d. Flag Assessment**

|Flag Type|Trigger Threshold|Actual Value|Triggered?|
|---|---|---|---|
|Standard flag|Actual NR below expected by 4.0+ for 15+ consecutive games|||
|Critical flag|Q4 NR drops 6.0+ below season avg in competitive games|||
|Roster talent loss exceeding 30%? (clears flag if yes)||||

**2e. NRCI Component Score: _____ / 100**

**Scoring rationale:**

---

#### Component 3: Rotation Integrity Score (RIS) — Weight: 25%

**3a. Baseline Rotation Pattern (First 50 Games)**

|Player|Avg Minutes (Gm 1-50)|Role|Net Rating|
|---|---|---|---|
|||||
|||||
|||||
|||||
|||||

**3b. Post-Elimination / Late-Season Rotation Pattern**

|Player|Avg Minutes (Post-Elim)|Change from Baseline|Net Rating|Deployment Context|
|---|---|---|---|---|
||||||
||||||
||||||
||||||
||||||

**3c. Minutes-Quality Correlation**

|Metric|Value|Flag?|
|---|---|---|
|Does minutes allocation invert relative to player quality post-elimination?|||
|DNP-CD frequency for rotation players post-elimination|||
|Starter designation changes post-elimination|||
|Negative-NR lineup minutes in close games (within 10 in Q4) vs. baseline|||

**3d. Blowout vs. Competitive Game State Weighting**

|Game State|Rotation Changes Detected|Weight Applied|
|---|---|---|
|Blowout (20+ differential)||Minimal|
|Moderate (10-20 differential)||0.5x|
|Competitive (within 10 in Q4)||1.0x (full)|

**3e. RIS Component Score: _____ / 100**

**Scoring rationale:**

---

#### Component 4: Bottom-Tier Clustering Analysis (BTCA) — Weight: 20%

**4a. League Context**

|Metric|Value|
|---|---|
|This team's final win total||
|Bottom-6 team win totals this season||
|20-season historical average for bottom-6 win totals||
|Standard deviation of historical baseline||
|Current season deviation from baseline||
|Number of teams on pace for <22 wins||
|League-wide flag triggered (4+ teams <22 wins)?||

**4b. Individual Team Temporal Pattern**

|Metric|Value|Flag?|
|---|---|---|
|Pre-ASB win percentage|||
|Post-ASB win percentage|||
|Post-ASB rate as % of pre-ASB rate|||
|Below 50% threshold?|||
|Corresponding roster talent loss >30%? (clears flag if yes)|||

**4c. Calendar Correlation**

|Period|Win Rate|Draft-Relevant Event|
|---|---|---|
|Pre-trade deadline|||
|Post-trade deadline to ASB|||
|Post-ASB to elimination|||
|Post-elimination to season end|||

**4d. BTCA Component Score: _____ / 100**

**Scoring rationale:**

---

#### TII Composite Calculation

|Component|Raw Score|Weight|Weighted Score|
|---|---|---|---|
|SAS|/100|× 0.30||
|NRCI|/100|× 0.25||
|RIS|/100|× 0.25||
|BTCA|/100|× 0.20||
|**Composite TII**|||**_____ / 100**|

#### Classification

|TII Score|Classification|Expected?|Calibration Notes|
|---|---|---|---|
|||||

---

#### Dual Penalty Application (Hypothetical)

If this team-season had been subject to the Stewardship Reform Plan:

|Penalty|Application|Impact|
|---|---|---|
|Combination reduction|___% of ___ combinations = ___ forfeited|Odds drop from ___% to ___%|
|Position displacement|___ positions downward|Picks ___th instead of ___th (if outside top 4)|
|ETP contribution|Forfeitures feed ETP pool|___ combinations added to pool|
|ETP tier impact|This team's classification pushes league to Tier ___|ETP holds ___% of forfeitures|

---

#### Calibration Assessment

**Did the TII produce the expected classification?** [ ] Yes — classification matches informed consensus [ ] Close — within one tier of expected (e.g., Orange vs. Red) [ ] No — classification is clearly wrong

**If No or Close, what needs adjustment?**

- [ ] SAS weight too high / too low
- [ ] NRCI flag threshold too sensitive / too lenient
- [ ] RIS baseline period needs modification
- [ ] BTCA league-wide threshold miscalibrated
- [ ] Specific exclusion missing (describe: _______________)
- [ ] Component interaction producing unexpected composite result

**Key insight from this case:**

---

<!-- APPENDIX_A_AUTOGEN_START -->

# Autogenerated Case Data (MVP)

### CASE A: Philadelphia 76ers — 2013-14

**Archetype:** The Obvious Tank
**Expected Classification:** Red
**Final Record:** 19-63
**Lottery Position:** 2nd-worst record
**Computed Elimination Date:** 2014-03-02 (game 60 of 82)

---

#### Component 1: Star Availability Score (SAS) — Weight: 30%

**1a. Identify Qualified Players (25+ min/game)**

|Player|Avg Min|Avg Pts|Games Played|Games Missed|DNPs|Absent|
|---|---|---|---|---|---|---|
|Evan Turner|34.9|17.4|54|28|0|28|
|Michael Carter-Williams|34.5|16.7|70|12|0|12|
|Thaddeus Young|34.4|17.9|79|3|0|3|
|Spencer Hawes|31.4|13.0|53|29|0|29|
|James Anderson|28.9|10.1|80|2|0|2|
|Henry Sims|27.2|11.8|26|56|0|56|

**1b. Absence Summary**

- Qualified players: 6
- Total star-game absences: 130
- Total possible appearances: 492
- Absence rate: 0.264

**1c. Absence Clustering (Pre vs Post Elimination)**

|Period|Games|Absences|Absence Rate|
|---|---|---|---|
|Pre-elimination|60|82|0.228|
|Post-elimination|22|48|0.364|

- Cluster ratio (post/pre): **1.6x**
- Flag (>=2.0x): **No**

**1d. Absence Distribution by Game Outcome**

|Outcome|Team Games|Star Absences|Absence Rate|
|---|---|---|---|
|Wins|19|25|0.219|
|Losses|63|105|0.278|

**1e. SAS Component Score: 35.9 / 100**


---

#### Component 2: Net Rating Collapse Index (NRCI) — Weight: 25%

**2a. Rolling 15-Game Net Rating**

- Peak rolling net rating: **-5.3** (game 15)
- Trough rolling net rating: **-19.7** (game 66)
- Maximum decline (peak to trough): **14.4**
- Season-long net rating: -10.0
- First 15 games net rating: -5.3
- Last 15 games net rating: -5.6

|Through Game #|Rolling Net Rating|
|---|---|
|15|-5.3|
|25|-12.0|
|35|-9.4|
|45|-7.3|
|55|-14.2|
|65|-18.8|
|75|-12.5|

**2b. Close-Game Performance (games within 8 pts net rating)**

- Close games: 27
- Close game record: 13-14
- Close game win %: **0.481**
- Blowout losses: 24 (0.293)

**2c. Pre/Post Elimination Net Rating**

|Period|Games|Off Rating|Def Rating|Net Rating|
|---|---|---|---|---|
|Pre-elimination|60|98.3|108.6|-10.3|
|Post-elimination|22|101.0|110.0|-9.0|

- Net rating change: **1.3**
- Collapse flag (change < -3.0): **No**

**2e. NRCI Component Score: 33.2 / 100**


---

#### Component 3: Rotation Integrity Score (RIS) — Weight: 25%

**3a. Pre-Elimination Baseline Rotation (Top 8 by Minutes)**

Pre-elimination games: 60

|Player|Avg Min (Pre)|Games (Pre)|Avg Net Rating|USG%|
|---|---|---|---|---|
|Evan Turner|34.3|55|-10.5|0.234|
|Thaddeus Young|31.9|60|-12.7|0.22|
|Spencer Hawes|30.3|55|-12.9|0.18|
|James Anderson|28.6|60|-12.1|0.154|
|Michael Carter-Williams|27.5|60|-7.1|0.209|
|Tony Wroten|21.4|60|-12.5|0.243|
|Henry Sims|19.7|5|-13.1|0.104|
|Hollis Thompson|19.6|60|-12.1|0.101|

**3b. Post-Elimination Rotation Changes**

- Post-elimination games: 22
- Significant minute decreases (>=20%): **2**
- Average minutes change: -5.0
- Rotation disruption flag (>=3 sig decreases): **No**
- New rotation players: 2

|Player|Pre Avg Min|Post Avg Min|Change|Change %|
|---|---|---|---|---|
|Evan Turner|34.3|0|-34.3|-100.0%|
|Thaddeus Young|31.9|36.4|4.5|14.1%|
|Spencer Hawes|30.3|0|-30.3|-100.0%|
|James Anderson|28.6|26.9|-1.7|-5.9%|
|Michael Carter-Williams|27.5|34.8|7.3|26.5%|
|Tony Wroten|21.4|21.9|0.5|2.3%|
|Henry Sims|19.7|27.6|7.9|40.1%|
|Hollis Thompson|19.6|25.8|6.2|31.6%|

**New rotation players post-elimination:**

- Elliot Williams — 21.2 min/game (22 games)
- Jarvis Varnado — 14.5 min/game (22 games)

**3c. Minutes-Quality Correlation Shift**

- Pre-elimination correlation: -0.43
- Post-elimination correlation: -0.121
- Correlation shift: **0.308**

**3d. Lineup Experimentation**

- Pre-elimination unique players/game: 11.9
- Post-elimination unique players/game: 12.2
- Experimentation increase: **0.3**

**3e. RIS Component Score: 33.0 / 100**


---

#### Component 4: Bottom-Tier Clustering Analysis (BTCA) — Weight: 20%

**4a. League Context — Bottom-6 Analysis**

- Team record: **19-63**
- Current bottom-6 avg wins: **22.3**
- Historical baseline (20 seasons): mean=22.5, σ=2.5
- Deviation from baseline: **-0.09σ**
- Teams on pace for <22 wins: 2
- League-wide cluster flag (>=4 teams): **No**

|Rank|Team|Wins|
|---|---|---|
|1|Bucks|15|
|2|76ers|19|
|3|Magic|23|
|4|Celtics|25|
|5|Jazz|25|
|6|Lakers|27|

**4b. Individual Team Temporal Pattern (Pre/Post ASB)**

|Split|Record|Win%|Net Rating|
|---|---|---|---|
|Pre-ASB|15-39|0.278|-9.6|
|Post-ASB|4-24|0.143|-10.9|

- Post-ASB as % of pre-ASB: **51.4%**
- Below 50% threshold flag: **No**

**4c. Calendar Correlation — Win Rates by Period**

|Period|Games|Record|Win Rate|
|---|---|---|---|
|Pre-trade deadline|55|15-40|0.273|
|Post-ASB to elimination|5|0-5|0.0|
|Post-elimination|23|4-19|0.174|

- Trade deadline: 2014-02-20
- All-Star break: 2014-02-14
- Elimination date: 2014-03-02

**4d. BTCA Component Score: 47.9 / 100**


---

#### Supplemental Indicators (contextual — not scored)

**5a. Draft Pick Incentive (DPI)**

- Final record: 19-63
- Draft lottery position: **2nd**-worst record
- In bottom 3: Yes
- In bottom 5: Yes
- Wins gap to next better draft slot: 4
- Bottom-5 cluster size (teams within 3 wins): 1
- Wins needed to exit bottom 5: 7

**5b. Veteran Shelving Index (VSI)**

- Total unique players used: 23
- Regular rotation size (40%+ games, 15+ min): 9
- One-off players (<5 games): 2
- **Shelved post-elimination: 4**

|Player|Pre-Elim Avg Min|Post-Elim Avg Min|Pre GP|Post GP|Minutes Drop|
|---|---|---|---|---|---|
|Spencer Hawes|31.4|0|53|0|31.4|
|Evan Turner|34.9|0|54|0|34.9|
|Darius Morris|16.1|0|12|0|16.1|
|Lavoy Allen|18.8|0|51|0|18.8|

**5c. Margin of Defeat Profile (MDP)**

- Total losses: 63
- Average loss margin (net rating): -15.2
- Blowout losses (NR < -15): 24 (0.381)
- Competitive losses (NR > -5): 6 (0.095)
- 1st-half season NR: -8.2
- 2nd-half season NR: -11.7
- **Trajectory (2nd half − 1st half): -3.5**
- Pre-elimination avg NR: -10.3
- Post-elimination avg NR: -9.0
- Post-elim margin change: **1.3**

**5d. Trade Deadline Roster Churn (LOI)**

- Trade deadline date: 2014-02-20
- Total players departed: 6
- **Meaningful departures (10+ min/game): 6**
- Total players arrived: 8
- **Meaningful arrivals (10+ min/game): 6**
- Total roster churn: 14

Key departures:

- Darius Morris (16.1 min/game pre-deadline)
- Lavoy Allen (18.8 min/game pre-deadline)
- Daniel Orton (11.4 min/game pre-deadline)
- Dewayne Dedmon (13.7 min/game pre-deadline)
- Evan Turner (34.9 min/game pre-deadline)
- Spencer Hawes (31.4 min/game pre-deadline)

Key arrivals:

- Eric Maynor (14.0 min/game post-deadline)
- Casper Ware (12.9 min/game post-deadline)
- Byron Mullens (13.7 min/game post-deadline)
- James Nunnally (12.4 min/game post-deadline)
- Henry Sims (27.2 min/game post-deadline)
- Jarvis Varnado (14.7 min/game post-deadline)

- Total unique players used (season): 23
- First-half unique players: 14
- Second-half unique players: 21


---

#### TII Composite Calculation

|Component|Raw Score|Weight|Weighted Score|
|---|---|---|---|
|SAS|35.9 /100|x 0.30|10.8|
|NRCI|33.2 /100|x 0.25|8.3|
|RIS|33.0 /100|x 0.25|8.2|
|BTCA|47.9 /100|x 0.20|9.6|
|**Composite TII**|||**36.9 / 100**|

**Classification: Yellow** (Expected: Red) — **MISMATCH**



### CASE B: Philadelphia 76ers — 2015-16

**Archetype:** The Obvious Tank (sustained)
**Expected Classification:** Red
**Final Record:** 10-72
**Lottery Position:** 1st-worst record
**Computed Elimination Date:** 2016-01-24 (game 45 of 82)

---

#### Component 1: Star Availability Score (SAS) — Weight: 30%

**1a. Identify Qualified Players (25+ min/game)**

|Player|Avg Min|Avg Pts|Games Played|Games Missed|DNPs|Absent|
|---|---|---|---|---|---|---|
|Ish Smith|32.4|14.7|50|32|0|32|
|Jahlil Okafor|30.0|17.5|53|29|0|29|
|Nerlens Noel|29.3|11.1|67|15|0|15|
|Robert Covington|28.4|12.8|67|15|0|15|
|Hollis Thompson|28.0|9.8|77|5|0|5|
|Jerami Grant|26.8|9.7|77|5|0|5|
|Isaiah Canaan|25.5|11.0|77|5|0|5|

**1b. Absence Summary**

- Qualified players: 7
- Total star-game absences: 106
- Total possible appearances: 574
- Absence rate: 0.185

**1c. Absence Clustering (Pre vs Post Elimination)**

|Period|Games|Absences|Absence Rate|
|---|---|---|---|
|Pre-elimination|45|55|0.175|
|Post-elimination|37|51|0.197|

- Cluster ratio (post/pre): **1.13x**
- Flag (>=2.0x): **No**

**1d. Absence Distribution by Game Outcome**

|Outcome|Team Games|Star Absences|Absence Rate|
|---|---|---|---|
|Wins|10|7|0.1|
|Losses|72|99|0.196|

**1e. SAS Component Score: 39.9 / 100**


---

#### Component 2: Net Rating Collapse Index (NRCI) — Weight: 25%

**2a. Rolling 15-Game Net Rating**

- Peak rolling net rating: **-3.9** (game 46)
- Trough rolling net rating: **-15.3** (game 36)
- Maximum decline (peak to trough): **11.4**
- Season-long net rating: -10.2
- First 15 games net rating: -13.6
- Last 15 games net rating: -8.4

|Through Game #|Rolling Net Rating|
|---|---|
|15|-13.6|
|25|-12.1|
|35|-13.5|
|45|-5.6|
|55|-6.1|
|65|-9.3|
|75|-10.2|

**2b. Close-Game Performance (games within 8 pts net rating)**

- Close games: 28
- Close game record: 4-24
- Close game win %: **0.143**
- Blowout losses: 24 (0.293)

**2c. Pre/Post Elimination Net Rating**

|Period|Games|Off Rating|Def Rating|Net Rating|
|---|---|---|---|---|
|Pre-elimination|45|95.8|106.6|-10.8|
|Post-elimination|37|101.6|111.2|-9.6|

- Net rating change: **1.2**
- Collapse flag (change < -3.0): **No**

**2e. NRCI Component Score: 54.2 / 100**


---

#### Component 3: Rotation Integrity Score (RIS) — Weight: 25%

**3a. Pre-Elimination Baseline Rotation (Top 8 by Minutes)**

Pre-elimination games: 45

|Player|Avg Min (Pre)|Games (Pre)|Avg Net Rating|USG%|
|---|---|---|---|---|
|Ish Smith|31.0|14|-9.9|0.288|
|Jahlil Okafor|28.1|45|-13.6|0.248|
|Hollis Thompson|25.4|45|-9.3|0.144|
|Nerlens Noel|25.3|45|-12.3|0.155|
|Jerami Grant|24.4|45|-10.5|0.163|
|Isaiah Canaan|24.3|45|-13.0|0.185|
|T.J. McConnell|21.2|45|-8.6|0.165|
|Robert Covington|21.1|45|-9.1|0.17|

**3b. Post-Elimination Rotation Changes**

- Post-elimination games: 37
- Significant minute decreases (>=20%): **1**
- Average minutes change: -0.7
- Rotation disruption flag (>=3 sig decreases): **No**
- New rotation players: 1

|Player|Pre Avg Min|Post Avg Min|Change|Change %|
|---|---|---|---|---|
|Ish Smith|31.0|32.1|1.1|3.5%|
|Jahlil Okafor|28.1|20.5|-7.6|-27.0%|
|Hollis Thompson|25.4|27.3|1.9|7.5%|
|Nerlens Noel|25.3|22.3|-3.0|-11.9%|
|Jerami Grant|24.4|26.2|1.8|7.4%|
|Isaiah Canaan|24.3|23.6|-0.7|-2.9%|
|T.J. McConnell|21.2|17.6|-3.6|-17.0%|
|Robert Covington|21.1|25.7|4.6|21.8%|

**New rotation players post-elimination:**

- Nik Stauskas — 25.6 min/game (35 games)

**3c. Minutes-Quality Correlation Shift**

- Pre-elimination correlation: -0.446
- Post-elimination correlation: -0.391
- Correlation shift: **0.056**

**3d. Lineup Experimentation**

- Pre-elimination unique players/game: 12.8
- Post-elimination unique players/game: 12.9
- Experimentation increase: **0.1**

**3e. RIS Component Score: 16.0 / 100**


---

#### Component 4: Bottom-Tier Clustering Analysis (BTCA) — Weight: 20%

**4a. League Context — Bottom-6 Analysis**

- Team record: **10-72**
- Current bottom-6 avg wins: **21.7**
- Historical baseline (20 seasons): mean=22.5, σ=2.5
- Deviation from baseline: **-0.35σ**
- Teams on pace for <22 wins: 3
- League-wide cluster flag (>=4 teams): **No**

|Rank|Team|Wins|
|---|---|---|
|1|76ers|10|
|2|Lakers|17|
|3|Nets|21|
|4|Suns|23|
|5|Timberwolves|29|
|6|Pelicans|30|

**4b. Individual Team Temporal Pattern (Pre/Post ASB)**

|Split|Record|Win%|Net Rating|
|---|---|---|---|
|Pre-ASB|8-45|0.151|-10.3|
|Post-ASB|2-27|0.069|-10.1|

- Post-ASB as % of pre-ASB: **45.7%**
- Below 50% threshold flag: **YES**

**4c. Calendar Correlation — Win Rates by Period**

|Period|Games|Record|Win Rate|
|---|---|---|---|
|Pre-trade deadline|53|8-45|0.151|
|Post-elimination|38|4-34|0.105|

- Trade deadline: 2016-02-18
- All-Star break: 2016-02-12
- Elimination date: 2016-01-24

**4d. BTCA Component Score: 63.0 / 100**


---

#### Supplemental Indicators (contextual — not scored)

**5a. Draft Pick Incentive (DPI)**

- Final record: 10-72
- Draft lottery position: **1st**-worst record
- In bottom 3: Yes
- In bottom 5: Yes
- Wins gap to next better draft slot: 7
- Bottom-5 cluster size (teams within 3 wins): 1
- Wins needed to exit bottom 5: 20

**5b. Veteran Shelving Index (VSI)**

- Total unique players used: 18
- Regular rotation size (40%+ games, 15+ min): 10
- One-off players (<5 games): 0
- **Shelved post-elimination: 1**

|Player|Pre-Elim Avg Min|Post-Elim Avg Min|Pre GP|Post GP|Minutes Drop|
|---|---|---|---|---|---|
|Tony Wroten|18.0|0|8|0|18.0|

**5c. Margin of Defeat Profile (MDP)**

- Total losses: 72
- Average loss margin (net rating): -13.2
- Blowout losses (NR < -15): 24 (0.333)
- Competitive losses (NR > -5): 13 (0.181)
- 1st-half season NR: -12.1
- 2nd-half season NR: -8.4
- **Trajectory (2nd half − 1st half): 3.7**
- Pre-elimination avg NR: -10.8
- Post-elimination avg NR: -9.6
- Post-elim margin change: **1.2**

**5d. Trade Deadline Roster Churn (LOI)**

- Trade deadline date: 2016-02-18
- Total players departed: 3
- **Meaningful departures (10+ min/game): 3**
- Total players arrived: 2
- **Meaningful arrivals (10+ min/game): 2**
- Total roster churn: 5

Key departures:

- JaKarr Sampson (14.7 min/game pre-deadline)
- Phil Pressey (12.1 min/game pre-deadline)
- Tony Wroten (18.0 min/game pre-deadline)

Key arrivals:

- Elton Brand (13.2 min/game post-deadline)
- Sonny Weems (11.1 min/game post-deadline)

- Total unique players used (season): 18
- First-half unique players: 16
- Second-half unique players: 16


---

#### TII Composite Calculation

|Component|Raw Score|Weight|Weighted Score|
|---|---|---|---|
|SAS|39.9 /100|x 0.30|12.0|
|NRCI|54.2 /100|x 0.25|13.6|
|RIS|16.0 /100|x 0.25|4.0|
|BTCA|63.0 /100|x 0.20|12.6|
|**Composite TII**|||**42.2 / 100**|

**Classification: Yellow** (Expected: Red) — **MISMATCH**



### CASE C: Portland Trail Blazers — 2022-23

**Archetype:** Mid-Season Pivot / Integrity Failure
**Expected Classification:** Orange/Red
**Final Record:** 33-49
**Lottery Position:** 5th-worst record
**Computed Elimination Date:** 2023-03-27 (game 75 of 82)

---

#### Component 1: Star Availability Score (SAS) — Weight: 30%

**1a. Identify Qualified Players (25+ min/game)**

|Player|Avg Min|Avg Pts|Games Played|Games Missed|DNPs|Absent|
|---|---|---|---|---|---|---|
|Damian Lillard|36.3|32.2|58|24|0|24|
|Jerami Grant|35.6|20.5|63|19|0|19|
|Anfernee Simons|35.0|21.1|62|20|0|20|
|Josh Hart|33.4|9.5|51|31|0|31|
|Skylar Mays|31.5|15.3|6|76|0|76|
|Matisse Thybulle|27.7|7.4|22|60|0|60|
|Cam Reddish|27.6|10.9|20|62|0|62|
|Jusuf Nurkić|26.8|13.3|52|30|0|30|
|Justise Winslow|26.8|6.8|29|53|0|53|
|Nate Williams|25.3|10.6|5|77|0|77|

**1b. Absence Summary**

- Qualified players: 10
- Total star-game absences: 452
- Total possible appearances: 820
- Absence rate: 0.551

**1c. Absence Clustering (Pre vs Post Elimination)**

|Period|Games|Absences|Absence Rate|
|---|---|---|---|
|Pre-elimination|75|388|0.517|
|Post-elimination|7|64|0.914|

- Cluster ratio (post/pre): **1.77x**
- Flag (>=2.0x): **No**

**1d. Absence Distribution by Game Outcome**

|Outcome|Team Games|Star Absences|Absence Rate|
|---|---|---|---|
|Wins|33|171|0.518|
|Losses|49|281|0.573|

**1e. SAS Component Score: 53.7 / 100**


---

#### Component 2: Net Rating Collapse Index (NRCI) — Weight: 25%

**2a. Rolling 15-Game Net Rating**

- Peak rolling net rating: **3.9** (game 37)
- Trough rolling net rating: **-16.3** (game 82)
- Maximum decline (peak to trough): **20.2**
- Season-long net rating: -4.0
- First 15 games net rating: 2.0
- Last 15 games net rating: -16.3

|Through Game #|Rolling Net Rating|
|---|---|
|15|2.0|
|25|-2.1|
|35|0.9|
|45|-0.7|
|55|0.3|
|65|-4.2|
|75|-11.5|

**2b. Close-Game Performance (games within 8 pts net rating)**

- Close games: 31
- Close game record: 14-17
- Close game win %: **0.452**
- Blowout losses: 19 (0.232)

**2c. Pre/Post Elimination Net Rating**

|Period|Games|Off Rating|Def Rating|Net Rating|
|---|---|---|---|---|
|Pre-elimination|75|114.9|117.5|-2.6|
|Post-elimination|7|105.1|123.9|-18.8|

- Net rating change: **-16.2**
- Collapse flag (change < -3.0): **YES**

**2e. NRCI Component Score: 70.0 / 100**


---

#### Component 3: Rotation Integrity Score (RIS) — Weight: 25%

**3a. Pre-Elimination Baseline Rotation (Top 8 by Minutes)**

Pre-elimination games: 75

|Player|Avg Min (Pre)|Games (Pre)|Avg Net Rating|USG%|
|---|---|---|---|---|
|Jerami Grant|35.6|63|-1.9|0.228|
|Anfernee Simons|35.0|62|-2.0|0.248|
|Josh Hart|32.2|53|2.8|0.118|
|Damian Lillard|31.0|68|1.7|0.282|
|Cam Reddish|27.6|20|-16.5|0.171|
|Matisse Thybulle|27.3|19|-6.3|0.121|
|Jusuf Nurkić|25.3|55|-3.0|0.212|
|Justise Winslow|24.2|32|-4.1|0.127|

**3b. Post-Elimination Rotation Changes**

- Post-elimination games: 7
- Significant minute decreases (>=20%): **7**
- Average minutes change: -26.0
- Rotation disruption flag (>=3 sig decreases): **YES**
- New rotation players: 7

|Player|Pre Avg Min|Post Avg Min|Change|Change %|
|---|---|---|---|---|
|Jerami Grant|35.6|0|-35.6|-100.0%|
|Anfernee Simons|35.0|0|-35.0|-100.0%|
|Josh Hart|32.2|0|-32.2|-100.0%|
|Damian Lillard|31.0|0|-31.0|-100.0%|
|Cam Reddish|27.6|0.0|-27.6|-100.0%|
|Matisse Thybulle|27.3|30.4|3.1|11.4%|
|Jusuf Nurkić|25.3|0|-25.3|-100.0%|
|Justise Winslow|24.2|0|-24.2|-100.0%|

**New rotation players post-elimination:**

- Skylar Mays — 31.5 min/game (6 games)
- Kevin Knox II — 30.5 min/game (7 games)
- Shaedon Sharpe — 30.1 min/game (7 games)
- Nassir Little — 25.8 min/game (2 games)
- Nate Williams — 25.3 min/game (5 games)
- Shaquille Harrison — 24.0 min/game (5 games)
- John Butler Jr. — 23.6 min/game (7 games)

**3c. Minutes-Quality Correlation Shift**

- Pre-elimination correlation: 0.417
- Post-elimination correlation: 0.035
- Correlation shift: **-0.382**

**3d. Lineup Experimentation**

- Pre-elimination unique players/game: 12.1
- Post-elimination unique players/game: 11.0
- Experimentation increase: **-1.1**

**3e. RIS Component Score: 80.0 / 100**


---

#### Component 4: Bottom-Tier Clustering Analysis (BTCA) — Weight: 20%

**4a. League Context — Bottom-6 Analysis**

- Team record: **33-49**
- Current bottom-6 avg wins: **25.8**
- Historical baseline (20 seasons): mean=22.5, σ=2.5
- Deviation from baseline: **1.31σ**
- Teams on pace for <22 wins: 1
- League-wide cluster flag (>=4 teams): **No**

|Rank|Team|Wins|
|---|---|---|
|1|Pistons|17|
|2|Rockets|22|
|3|Spurs|22|
|4|Hornets|27|
|5|Trail Blazers|33|
|6|Magic|34|

**4b. Individual Team Temporal Pattern (Pre/Post ASB)**

|Split|Record|Win%|Net Rating|
|---|---|---|---|
|Pre-ASB|28-30|0.483|-0.3|
|Post-ASB|5-19|0.208|-12.7|

- Post-ASB as % of pre-ASB: **43.1%**
- Below 50% threshold flag: **YES**

**4c. Calendar Correlation — Win Rates by Period**

|Period|Games|Record|Win Rate|
|---|---|---|---|
|Pre-trade deadline|55|27-28|0.491|
|Post-deadline to ASB|3|1-2|0.333|
|Post-ASB to elimination|16|4-12|0.25|
|Post-elimination|8|1-7|0.125|

- Trade deadline: 2023-02-09
- All-Star break: 2023-02-17
- Elimination date: 2023-03-27

**4d. BTCA Component Score: 77.3 / 100**


---

#### Supplemental Indicators (contextual — not scored)

**5a. Draft Pick Incentive (DPI)**

- Final record: 33-49
- Draft lottery position: **5th**-worst record
- In bottom 3: No
- In bottom 5: Yes
- Wins gap to next better draft slot: 1
- Bottom-5 cluster size (teams within 3 wins): 4
- Wins needed to exit bottom 5: 1

**5b. Veteran Shelving Index (VSI)**

- Total unique players used: 24
- Regular rotation size (40%+ games, 15+ min): 9
- One-off players (<5 games): 2
- **Shelved post-elimination: 7**

|Player|Pre-Elim Avg Min|Post-Elim Avg Min|Pre GP|Post GP|Minutes Drop|
|---|---|---|---|---|---|
|Damian Lillard|36.3|0|58|0|36.3|
|Jerami Grant|35.6|0|63|0|35.6|
|Jusuf Nurkić|26.8|0|52|0|26.8|
|Justise Winslow|26.8|0|29|0|26.8|
|Gary Payton II|17.0|0|15|0|17.0|
|Josh Hart|33.4|0|51|0|33.4|
|Anfernee Simons|35.0|0|62|0|35.0|

**5c. Margin of Defeat Profile (MDP)**

- Total losses: 49
- Average loss margin (net rating): -13.5
- Blowout losses (NR < -15): 19 (0.388)
- Competitive losses (NR > -5): 9 (0.184)
- 1st-half season NR: -0.3
- 2nd-half season NR: -7.7
- **Trajectory (2nd half − 1st half): -7.4**
- Pre-elimination avg NR: -2.6
- Post-elimination avg NR: -18.8
- Post-elim margin change: **-16.2**

**5d. Trade Deadline Roster Churn (LOI)**

- Trade deadline date: 2023-02-09
- Total players departed: 4
- **Meaningful departures (10+ min/game): 3**
- Total players arrived: 9
- **Meaningful arrivals (10+ min/game): 9**
- Total roster churn: 13

Key departures:

- Josh Hart (33.4 min/game pre-deadline)
- Gary Payton II (17.0 min/game pre-deadline)
- Justise Winslow (26.8 min/game pre-deadline)

Key arrivals:

- Kevin Knox II (17.1 min/game post-deadline)
- Justin Minaya (22.2 min/game post-deadline)
- Nate Williams (25.3 min/game post-deadline)
- Skylar Mays (31.5 min/game post-deadline)
- Ryan Arcidiacono (16.2 min/game post-deadline)
- Shaquille Harrison (24.0 min/game post-deadline)
- Matisse Thybulle (27.7 min/game post-deadline)
- Chance Comanche (20.8 min/game post-deadline)
- Cam Reddish (27.6 min/game post-deadline)

- Total unique players used (season): 24
- First-half unique players: 15
- Second-half unique players: 23


---

#### TII Composite Calculation

|Component|Raw Score|Weight|Weighted Score|
|---|---|---|---|
|SAS|53.7 /100|x 0.30|16.1|
|NRCI|70.0 /100|x 0.25|17.5|
|RIS|80.0 /100|x 0.25|20.0|
|BTCA|77.3 /100|x 0.20|15.5|
|**Composite TII**|||**69.1 / 100**|

**Classification: Orange** (Expected: Orange/Red) — **MATCH**



### CASE D: Washington Wizards — 2023-24

**Archetype:** Legitimate Rebuild vs. Obvious Tank (ambiguous)
**Expected Classification:** Yellow/Orange
**Final Record:** 15-67
**Lottery Position:** 2nd-worst record
**Computed Elimination Date:** 2024-02-23 (game 56 of 82)

---

#### Component 1: Star Availability Score (SAS) — Weight: 30%

**1a. Identify Qualified Players (25+ min/game)**

|Player|Avg Min|Avg Pts|Games Played|Games Missed|DNPs|Absent|
|---|---|---|---|---|---|---|
|Kyle Kuzma|32.6|22.2|70|12|0|12|
|Deni Avdija|30.1|14.7|75|7|0|7|
|Jordan Poole|30.1|17.4|78|4|0|4|
|Tyus Jones|29.3|12.0|66|16|0|16|
|Bilal Coulibaly|27.2|8.4|63|19|0|19|
|Daniel Gafford|26.5|10.9|45|37|0|37|
|Corey Kispert|25.8|13.4|80|2|0|2|

**1b. Absence Summary**

- Qualified players: 7
- Total star-game absences: 97
- Total possible appearances: 574
- Absence rate: 0.169

**1c. Absence Clustering (Pre vs Post Elimination)**

|Period|Games|Absences|Absence Rate|
|---|---|---|---|
|Pre-elimination|56|16|0.041|
|Post-elimination|26|81|0.445|

- Cluster ratio (post/pre): **10.9x**
- Flag (>=2.0x): **YES**

**1d. Absence Distribution by Game Outcome**

|Outcome|Team Games|Star Absences|Absence Rate|
|---|---|---|---|
|Wins|15|17|0.162|
|Losses|67|80|0.171|

**1e. SAS Component Score: 38.6 / 100**


---

#### Component 2: Net Rating Collapse Index (NRCI) — Weight: 25%

**2a. Rolling 15-Game Net Rating**

- Peak rolling net rating: **-4.8** (game 52)
- Trough rolling net rating: **-14.0** (game 35)
- Maximum decline (peak to trough): **8.5**
- Season-long net rating: -8.7
- First 15 games net rating: -7.9
- Last 15 games net rating: -6.0

|Through Game #|Rolling Net Rating|
|---|---|
|15|-7.9|
|25|-11.3|
|35|-14.0|
|45|-6.8|
|55|-7.6|
|65|-8.9|
|75|-8.0|

**2b. Close-Game Performance (games within 8 pts net rating)**

- Close games: 37
- Close game record: 9-28
- Close game win %: **0.243**
- Blowout losses: 20 (0.244)

**2c. Pre/Post Elimination Net Rating**

|Period|Games|Off Rating|Def Rating|Net Rating|
|---|---|---|---|---|
|Pre-elimination|56|110.6|119.8|-9.2|
|Post-elimination|26|109.4|116.9|-7.5|

- Net rating change: **1.7**
- Collapse flag (change < -3.0): **No**

**2e. NRCI Component Score: 41.2 / 100**


---

#### Component 3: Rotation Integrity Score (RIS) — Weight: 25%

**3a. Pre-Elimination Baseline Rotation (Top 8 by Minutes)**

Pre-elimination games: 56

|Player|Avg Min (Pre)|Games (Pre)|Avg Net Rating|USG%|
|---|---|---|---|---|
|Kyle Kuzma|31.6|54|-13.4|0.3|
|Tyus Jones|28.9|56|-13.8|0.166|
|Jordan Poole|28.1|56|-12.0|0.235|
|Deni Avdija|27.6|56|-9.2|0.188|
|Bilal Coulibaly|27.1|55|-11.7|0.135|
|Daniel Gafford|26.5|45|-9.2|0.137|
|Marvin Bagley III|23.4|13|-10.4|0.217|
|Corey Kispert|22.6|55|-12.9|0.196|

**3b. Post-Elimination Rotation Changes**

- Post-elimination games: 26
- Significant minute decreases (>=20%): **2**
- Average minutes change: -2.4
- Rotation disruption flag (>=3 sig decreases): **No**
- New rotation players: 1

|Player|Pre Avg Min|Post Avg Min|Change|Change %|
|---|---|---|---|---|
|Kyle Kuzma|31.6|33.8|2.2|7.0%|
|Tyus Jones|28.9|20.9|-8.0|-27.7%|
|Jordan Poole|28.1|29.7|1.6|5.7%|
|Deni Avdija|27.6|30.8|3.2|11.6%|
|Bilal Coulibaly|27.1|25.2|-1.9|-7.0%|
|Daniel Gafford|26.5|0|-26.5|-100.0%|
|Marvin Bagley III|23.4|24.7|1.3|5.6%|
|Corey Kispert|22.6|31.8|9.2|40.7%|

**New rotation players post-elimination:**

- Landry Shamet — 20.6 min/game (7 games)

**3c. Minutes-Quality Correlation Shift**

- Pre-elimination correlation: -0.202
- Post-elimination correlation: -0.025
- Correlation shift: **0.177**

**3d. Lineup Experimentation**

- Pre-elimination unique players/game: 14.2
- Post-elimination unique players/game: 12.5
- Experimentation increase: **-1.7**

**3e. RIS Component Score: 25.0 / 100**


---

#### Component 4: Bottom-Tier Clustering Analysis (BTCA) — Weight: 20%

**4a. League Context — Bottom-6 Analysis**

- Team record: **15-67**
- Current bottom-6 avg wins: **19.7**
- Historical baseline (20 seasons): mean=22.5, σ=2.5
- Deviation from baseline: **-1.15σ**
- Teams on pace for <22 wins: 4
- League-wide cluster flag (>=4 teams): **YES**

|Rank|Team|Wins|
|---|---|---|
|1|Pistons|14|
|2|Wizards|15|
|3|Trail Blazers|21|
|4|Hornets|21|
|5|Spurs|22|
|6|Raptors|25|

**4b. Individual Team Temporal Pattern (Pre/Post ASB)**

|Split|Record|Win%|Net Rating|
|---|---|---|---|
|Pre-ASB|9-45|0.167|-8.5|
|Post-ASB|6-22|0.214|-9.0|

- Post-ASB as % of pre-ASB: **128.1%**
- Below 50% threshold flag: **No**

**4c. Calendar Correlation — Win Rates by Period**

|Period|Games|Record|Win Rate|
|---|---|---|---|
|Pre-trade deadline|50|9-41|0.18|
|Post-deadline to ASB|4|0-4|0.0|
|Post-ASB to elimination|1|0-1|0.0|
|Post-elimination|27|6-21|0.222|

- Trade deadline: 2024-02-08
- All-Star break: 2024-02-16
- Elimination date: 2024-02-23

**4d. BTCA Component Score: 35.0 / 100**


---

#### Supplemental Indicators (contextual — not scored)

**5a. Draft Pick Incentive (DPI)**

- Final record: 15-67
- Draft lottery position: **2nd**-worst record
- In bottom 3: Yes
- In bottom 5: Yes
- Wins gap to next better draft slot: 6
- Bottom-5 cluster size (teams within 3 wins): 2
- Wins needed to exit bottom 5: 8

**5b. Veteran Shelving Index (VSI)**

- Total unique players used: 24
- Regular rotation size (40%+ games, 15+ min): 8
- One-off players (<5 games): 2
- **Shelved post-elimination: 1**

|Player|Pre-Elim Avg Min|Post-Elim Avg Min|Pre GP|Post GP|Minutes Drop|
|---|---|---|---|---|---|
|Daniel Gafford|26.5|0|45|0|26.5|

**5c. Margin of Defeat Profile (MDP)**

- Total losses: 67
- Average loss margin (net rating): -12.6
- Blowout losses (NR < -15): 20 (0.299)
- Competitive losses (NR > -5): 14 (0.209)
- 1st-half season NR: -9.0
- 2nd-half season NR: -8.3
- **Trajectory (2nd half − 1st half): 0.7**
- Pre-elimination avg NR: -9.2
- Post-elimination avg NR: -7.5
- Post-elim margin change: **1.7**

**5d. Trade Deadline Roster Churn (LOI)**

- Trade deadline date: 2024-02-08
- Total players departed: 6
- **Meaningful departures (10+ min/game): 3**
- Total players arrived: 3
- **Meaningful arrivals (10+ min/game): 3**
- Total roster churn: 9

Key departures:

- Mike Muscala (14.1 min/game pre-deadline)
- Danilo Gallinari (14.8 min/game pre-deadline)
- Daniel Gafford (26.5 min/game pre-deadline)

Key arrivals:

- Richaun Holmes (18.7 min/game post-deadline)
- Tristan Vukcevic (15.3 min/game post-deadline)
- Justin Champagnie (15.7 min/game post-deadline)

- Total unique players used (season): 24
- First-half unique players: 20
- Second-half unique players: 20


---

#### TII Composite Calculation

|Component|Raw Score|Weight|Weighted Score|
|---|---|---|---|
|SAS|38.6 /100|x 0.30|11.6|
|NRCI|41.2 /100|x 0.25|10.3|
|RIS|25.0 /100|x 0.25|6.2|
|BTCA|35.0 /100|x 0.20|7.0|
|**Composite TII**|||**35.1 / 100**|

**Classification: Yellow** (Expected: Yellow/Orange) — **MATCH**



### CASE E: Utah Jazz — 2024-25

**Archetype:** The Obvious Tank (current)
**Expected Classification:** Red
**Final Record:** 17-65
**Lottery Position:** 1st-worst record
**Computed Elimination Date:** 2025-02-26 (game 58 of 82)

---

#### Component 1: Star Availability Score (SAS) — Weight: 30%

**1a. Identify Qualified Players (25+ min/game)**

|Player|Avg Min|Avg Pts|Games Played|Games Missed|DNPs|Absent|
|---|---|---|---|---|---|---|
|Keyonte George|31.5|16.8|67|15|0|15|
|Lauri Markkanen|31.4|19.0|47|35|0|35|
|John Collins|30.5|18.9|40|42|0|42|
|Walker Kessler|30.0|11.1|58|24|0|24|
|Collin Sexton|27.9|18.4|63|19|0|19|
|Jordan Clarkson|26.0|16.2|37|45|0|45|
|Isaiah Collier|25.9|8.7|71|11|0|11|

**1b. Absence Summary**

- Qualified players: 7
- Total star-game absences: 191
- Total possible appearances: 574
- Absence rate: 0.333

**1c. Absence Clustering (Pre vs Post Elimination)**

|Period|Games|Absences|Absence Rate|
|---|---|---|---|
|Pre-elimination|58|102|0.251|
|Post-elimination|24|89|0.53|

- Cluster ratio (post/pre): **2.11x**
- Flag (>=2.0x): **YES**

**1d. Absence Distribution by Game Outcome**

|Outcome|Team Games|Star Absences|Absence Rate|
|---|---|---|---|
|Wins|17|33|0.277|
|Losses|65|158|0.347|

**1e. SAS Component Score: 48.7 / 100**


---

#### Component 2: Net Rating Collapse Index (NRCI) — Weight: 25%

**2a. Rolling 15-Game Net Rating**

- Peak rolling net rating: **-0.8** (game 40)
- Trough rolling net rating: **-18.4** (game 82)
- Maximum decline (peak to trough): **17.6**
- Season-long net rating: -9.3
- First 15 games net rating: -10.3
- Last 15 games net rating: -18.4

|Through Game #|Rolling Net Rating|
|---|---|
|15|-10.3|
|25|-9.2|
|35|-4.0|
|45|-4.5|
|55|-8.6|
|65|-7.9|
|75|-14.5|

**2b. Close-Game Performance (games within 8 pts net rating)**

- Close games: 30
- Close game record: 7-23
- Close game win %: **0.233**
- Blowout losses: 26 (0.317)

**2c. Pre/Post Elimination Net Rating**

|Period|Games|Off Rating|Def Rating|Net Rating|
|---|---|---|---|---|
|Pre-elimination|58|111.3|118.5|-7.2|
|Post-elimination|24|107.9|122.2|-14.3|

- Net rating change: **-7.1**
- Collapse flag (change < -3.0): **YES**

**2e. NRCI Component Score: 92.2 / 100**


---

#### Component 3: Rotation Integrity Score (RIS) — Weight: 25%

**3a. Pre-Elimination Baseline Rotation (Top 8 by Minutes)**

Pre-elimination games: 58

|Player|Avg Min (Pre)|Games (Pre)|Avg Net Rating|USG%|
|---|---|---|---|---|
|Lauri Markkanen|31.3|44|-6.0|0.223|
|John Collins|30.6|37|-2.6|0.232|
|Keyonte George|29.7|51|-9.2|0.224|
|Walker Kessler|29.2|47|-6.7|0.121|
|Collin Sexton|26.8|49|-4.8|0.246|
|Jordan Clarkson|25.0|34|-10.1|0.252|
|Taylor Hendricks|24.8|3|-13.9|0.113|
|Isaiah Collier|24.0|50|-11.7|0.169|

**3b. Post-Elimination Rotation Changes**

- Post-elimination games: 24
- Significant minute decreases (>=20%): **6**
- Average minutes change: -8.2
- Rotation disruption flag (>=3 sig decreases): **YES**
- New rotation players: 4

|Player|Pre Avg Min|Post Avg Min|Change|Change %|
|---|---|---|---|---|
|Lauri Markkanen|31.3|19.4|-11.9|-38.0%|
|John Collins|30.6|22.4|-8.2|-26.8%|
|Keyonte George|29.7|28.2|-1.5|-5.1%|
|Walker Kessler|29.2|19.3|-9.9|-33.9%|
|Collin Sexton|26.8|21.2|-5.6|-20.9%|
|Jordan Clarkson|25.0|18.5|-6.5|-26.0%|
|Taylor Hendricks|24.8|0.0|-24.8|-100.0%|
|Isaiah Collier|24.0|26.6|2.6|10.8%|

**New rotation players post-elimination:**

- Kyle Filipowski — 26.3 min/game (24 games)
- Brice Sensabaugh — 25.0 min/game (24 games)
- Johnny Juzang — 23.0 min/game (24 games)
- Cody Williams — 21.2 min/game (18 games)

**3c. Minutes-Quality Correlation Shift**

- Pre-elimination correlation: -0.025
- Post-elimination correlation: -0.167
- Correlation shift: **-0.142**

**3d. Lineup Experimentation**

- Pre-elimination unique players/game: 12.6
- Post-elimination unique players/game: 12.2
- Experimentation increase: **-0.4**

**3e. RIS Component Score: 64.5 / 100**


---

#### Component 4: Bottom-Tier Clustering Analysis (BTCA) — Weight: 20%

**4a. League Context — Bottom-6 Analysis**

- Team record: **17-65**
- Current bottom-6 avg wins: **20.8**
- Historical baseline (20 seasons): mean=22.5, σ=2.5
- Deviation from baseline: **-0.69σ**
- Teams on pace for <22 wins: 4
- League-wide cluster flag (>=4 teams): **YES**

|Rank|Team|Wins|
|---|---|---|
|1|Jazz|17|
|2|Wizards|18|
|3|Hornets|19|
|4|Pelicans|21|
|5|76ers|24|
|6|Nets|26|

**4b. Individual Team Temporal Pattern (Pre/Post ASB)**

|Split|Record|Win%|Net Rating|
|---|---|---|---|
|Pre-ASB|13-41|0.241|-7.0|
|Post-ASB|4-24|0.143|-13.4|

- Post-ASB as % of pre-ASB: **59.3%**
- Below 50% threshold flag: **No**

**4c. Calendar Correlation — Win Rates by Period**

|Period|Games|Record|Win Rate|
|---|---|---|---|
|Pre-trade deadline|49|12-37|0.245|
|Post-deadline to ASB|5|1-4|0.2|
|Post-ASB to elimination|3|1-2|0.333|
|Post-elimination|25|3-22|0.12|

- Trade deadline: 2025-02-06
- All-Star break: 2025-02-14
- Elimination date: 2025-02-26

**4d. BTCA Component Score: 56.4 / 100**


---

#### Supplemental Indicators (contextual — not scored)

**5a. Draft Pick Incentive (DPI)**

- Final record: 17-65
- Draft lottery position: **1st**-worst record
- In bottom 3: Yes
- In bottom 5: Yes
- Wins gap to next better draft slot: 1
- Bottom-5 cluster size (teams within 3 wins): 3
- Wins needed to exit bottom 5: 8

**5b. Veteran Shelving Index (VSI)**

- Total unique players used: 20
- Regular rotation size (40%+ games, 15+ min): 14
- One-off players (<5 games): 1
- **Shelved post-elimination: 2**

|Player|Pre-Elim Avg Min|Post-Elim Avg Min|Pre GP|Post GP|Minutes Drop|
|---|---|---|---|---|---|
|Patty Mills|15.3|0|17|0|15.3|
|Drew Eubanks|15.4|0|37|0|15.4|

**5c. Margin of Defeat Profile (MDP)**

- Total losses: 65
- Average loss margin (net rating): -14.7
- Blowout losses (NR < -15): 26 (0.4)
- Competitive losses (NR > -5): 14 (0.215)
- 1st-half season NR: -6.9
- 2nd-half season NR: -11.7
- **Trajectory (2nd half − 1st half): -4.8**
- Pre-elimination avg NR: -7.2
- Post-elimination avg NR: -14.3
- Post-elim margin change: **-7.1**

**5d. Trade Deadline Roster Churn (LOI)**

- Trade deadline date: 2025-02-06
- Total players departed: 3
- **Meaningful departures (10+ min/game): 3**
- Total players arrived: 2
- **Meaningful arrivals (10+ min/game): 2**
- Total roster churn: 5

Key departures:

- Drew Eubanks (15.4 min/game pre-deadline)
- Taylor Hendricks (24.8 min/game pre-deadline)
- Patty Mills (15.3 min/game pre-deadline)

Key arrivals:

- Jaden Springer (13.2 min/game post-deadline)
- KJ Martin (22.7 min/game post-deadline)

- Total unique players used (season): 20
- First-half unique players: 18
- Second-half unique players: 19


---

#### TII Composite Calculation

|Component|Raw Score|Weight|Weighted Score|
|---|---|---|---|
|SAS|48.7 /100|x 0.30|14.6|
|NRCI|92.2 /100|x 0.25|23.1|
|RIS|64.5 /100|x 0.25|16.1|
|BTCA|56.4 /100|x 0.20|11.3|
|**Composite TII**|||**65.1 / 100**|

**Classification: Orange** (Expected: Red) — **MISMATCH**



### CASE F: Minnesota Timberwolves — 2014-15

**Archetype:** Legitimate Rebuild (control)
**Expected Classification:** Green
**Final Record:** 16-66
**Lottery Position:** 1st-worst record
**Computed Elimination Date:** 2015-01-30 (game 46 of 82)

---

#### Component 1: Star Availability Score (SAS) — Weight: 30%

**1a. Identify Qualified Players (25+ min/game)**

|Player|Avg Min|Avg Pts|Games Played|Games Missed|DNPs|Absent|
|---|---|---|---|---|---|---|
|Andrew Wiggins|36.2|16.9|82|0|0|0|
|Thaddeus Young|33.4|14.3|48|34|0|34|
|Kevin Martin|33.4|20.0|39|43|0|43|
|Ricky Rubio|31.5|10.3|22|60|0|60|
|Gorgui Dieng|30.0|9.7|73|9|0|9|
|Corey Brewer|28.3|10.5|24|58|0|58|
|Mo Williams|28.0|12.2|41|41|0|41|
|Nikola Pekovic|26.3|12.5|31|51|0|51|

**1b. Absence Summary**

- Qualified players: 8
- Total star-game absences: 296
- Total possible appearances: 656
- Absence rate: 0.451

**1c. Absence Clustering (Pre vs Post Elimination)**

|Period|Games|Absences|Absence Rate|
|---|---|---|---|
|Pre-elimination|46|141|0.383|
|Post-elimination|36|155|0.538|

- Cluster ratio (post/pre): **1.4x**
- Flag (>=2.0x): **No**

**1d. Absence Distribution by Game Outcome**

|Outcome|Team Games|Star Absences|Absence Rate|
|---|---|---|---|
|Wins|16|45|0.352|
|Losses|66|251|0.475|

**1e. SAS Component Score: 45.5 / 100**


---

#### Component 2: Net Rating Collapse Index (NRCI) — Weight: 25%

**2a. Rolling 15-Game Net Rating**

- Peak rolling net rating: **-1.7** (game 59)
- Trough rolling net rating: **-14.3** (game 20)
- Maximum decline (peak to trough): **5.2**
- Season-long net rating: -9.1
- First 15 games net rating: -9.5
- Last 15 games net rating: -11.7

|Through Game #|Rolling Net Rating|
|---|---|
|15|-9.5|
|25|-12.9|
|35|-9.1|
|45|-8.7|
|55|-6.1|
|65|-5.2|
|75|-10.3|

**2b. Close-Game Performance (games within 8 pts net rating)**

- Close games: 26
- Close game record: 9-17
- Close game win %: **0.346**
- Blowout losses: 19 (0.232)

**2c. Pre/Post Elimination Net Rating**

|Period|Games|Off Rating|Def Rating|Net Rating|
|---|---|---|---|---|
|Pre-elimination|46|101.1|111.0|-9.8|
|Post-elimination|36|102.8|110.9|-8.1|

- Net rating change: **1.7**
- Collapse flag (change < -3.0): **No**

**2e. NRCI Component Score: 21.0 / 100**


---

#### Component 3: Rotation Integrity Score (RIS) — Weight: 25%

**3a. Pre-Elimination Baseline Rotation (Top 8 by Minutes)**

Pre-elimination games: 46

|Player|Avg Min (Pre)|Games (Pre)|Avg Net Rating|USG%|
|---|---|---|---|---|
|Andrew Wiggins|33.7|46|-10.6|0.215|
|Thaddeus Young|32.6|41|-9.6|0.219|
|Gorgui Dieng|30.0|46|-10.7|0.152|
|Corey Brewer|28.3|24|-16.2|0.191|
|Ricky Rubio|24.1|6|5.7|0.159|
|Lorenzo Brown|23.8|2|-6.7|0.147|
|Mo Williams|22.2|46|-7.3|0.174|
|Zach LaVine|21.4|46|-19.3|0.178|

**3b. Post-Elimination Rotation Changes**

- Post-elimination games: 36
- Significant minute decreases (>=20%): **4**
- Average minutes change: -4.9
- Rotation disruption flag (>=3 sig decreases): **YES**
- New rotation players: 3

|Player|Pre Avg Min|Post Avg Min|Change|Change %|
|---|---|---|---|---|
|Andrew Wiggins|33.7|39.4|5.7|16.9%|
|Thaddeus Young|32.6|38.4|5.8|17.8%|
|Gorgui Dieng|30.0|23.2|-6.8|-22.7%|
|Corey Brewer|28.3|0|-28.3|-100.0%|
|Ricky Rubio|24.1|15.2|-8.9|-36.9%|
|Lorenzo Brown|23.8|13.9|-9.9|-41.6%|
|Mo Williams|22.2|21.2|-1.0|-4.5%|
|Zach LaVine|21.4|25.5|4.1|19.2%|

**New rotation players post-elimination:**

- Kevin Martin — 27.1 min/game (36 games)
- Adreian Payne — 24.0 min/game (30 games)
- Nikola Pekovic — 19.4 min/game (21 games)

**3c. Minutes-Quality Correlation Shift**

- Pre-elimination correlation: -0.088
- Post-elimination correlation: -0.328
- Correlation shift: **-0.24**

**3d. Lineup Experimentation**

- Pre-elimination unique players/game: 12.5
- Post-elimination unique players/game: 12.6
- Experimentation increase: **0.1**

**3e. RIS Component Score: 62.5 / 100**


---

#### Component 4: Bottom-Tier Clustering Analysis (BTCA) — Weight: 20%

**4a. League Context — Bottom-6 Analysis**

- Team record: **16-66**
- Current bottom-6 avg wins: **21.0**
- Historical baseline (20 seasons): mean=22.5, σ=2.5
- Deviation from baseline: **-0.62σ**
- Teams on pace for <22 wins: 4
- League-wide cluster flag (>=4 teams): **YES**

|Rank|Team|Wins|
|---|---|---|
|1|Timberwolves|16|
|2|Knicks|17|
|3|76ers|18|
|4|Lakers|21|
|5|Magic|25|
|6|Kings|29|

**4b. Individual Team Temporal Pattern (Pre/Post ASB)**

|Split|Record|Win%|Net Rating|
|---|---|---|---|
|Pre-ASB|11-42|0.208|-9.0|
|Post-ASB|5-24|0.172|-9.1|

- Post-ASB as % of pre-ASB: **82.7%**
- Below 50% threshold flag: **No**

**4c. Calendar Correlation — Win Rates by Period**

|Period|Games|Record|Win Rate|
|---|---|---|---|
|Pre-trade deadline|53|11-42|0.208|
|Post-elimination|37|8-29|0.216|

- Trade deadline: 2015-02-19
- All-Star break: 2015-02-13
- Elimination date: 2015-01-30

**4d. BTCA Component Score: 31.3 / 100**


---

#### Supplemental Indicators (contextual — not scored)

**5a. Draft Pick Incentive (DPI)**

- Final record: 16-66
- Draft lottery position: **1st**-worst record
- In bottom 3: Yes
- In bottom 5: Yes
- Wins gap to next better draft slot: 1
- Bottom-5 cluster size (teams within 3 wins): 3
- Wins needed to exit bottom 5: 10

**5b. Veteran Shelving Index (VSI)**

- Total unique players used: 25
- Regular rotation size (40%+ games, 15+ min): 10
- One-off players (<5 games): 2
- **Shelved post-elimination: 1**

|Player|Pre-Elim Avg Min|Post-Elim Avg Min|Pre GP|Post GP|Minutes Drop|
|---|---|---|---|---|---|
|Corey Brewer|28.3|0|24|0|28.3|

**5c. Margin of Defeat Profile (MDP)**

- Total losses: 66
- Average loss margin (net rating): -13.1
- Blowout losses (NR < -15): 19 (0.288)
- Competitive losses (NR > -5): 12 (0.182)
- 1st-half season NR: -10.3
- 2nd-half season NR: -7.9
- **Trajectory (2nd half − 1st half): 2.4**
- Pre-elimination avg NR: -9.8
- Post-elimination avg NR: -8.1
- Post-elim margin change: **1.7**

**5d. Trade Deadline Roster Churn (LOI)**

- Trade deadline date: 2015-02-19
- Total players departed: 7
- **Meaningful departures (10+ min/game): 4**
- Total players arrived: 6
- **Meaningful arrivals (10+ min/game): 6**
- Total roster churn: 13

Key departures:

- Thaddeus Young (33.4 min/game pre-deadline)
- Corey Brewer (28.3 min/game pre-deadline)
- Mo Williams (28.0 min/game pre-deadline)
- Jeff Adrien (12.7 min/game pre-deadline)

Key arrivals:

- Kevin Garnett (19.6 min/game post-deadline)
- Adreian Payne (24.8 min/game post-deadline)
- Justin Hamilton (24.9 min/game post-deadline)
- Gary Neal (23.8 min/game post-deadline)
- Sean Kilpatrick (17.9 min/game post-deadline)
- Arinze Onuaku (11.4 min/game post-deadline)

- Total unique players used (season): 25
- First-half unique players: 18
- Second-half unique players: 22


---

#### TII Composite Calculation

|Component|Raw Score|Weight|Weighted Score|
|---|---|---|---|
|SAS|45.5 /100|x 0.30|13.7|
|NRCI|21.0 /100|x 0.25|5.2|
|RIS|62.5 /100|x 0.25|15.6|
|BTCA|31.3 /100|x 0.20|6.3|
|**Composite TII**|||**40.8 / 100**|

**Classification: Yellow** (Expected: Green) — **MISMATCH**



### CASE G: Golden State Warriors — 2019-20

**Archetype:** Injury-Wrecked Contender (control)
**Expected Classification:** Green
**Final Record:** 15-50
**Lottery Position:** 1st-worst record
**Computed Elimination Date:** 2020-01-12 (game 41 of 65)

---

#### Component 1: Star Availability Score (SAS) — Weight: 30%

**1a. Identify Qualified Players (25+ min/game)**

|Player|Avg Min|Avg Pts|Games Played|Games Missed|DNPs|Absent|
|---|---|---|---|---|---|---|
|Andrew Wiggins|33.6|19.4|12|53|0|53|
|D'Angelo Russell|32.1|23.6|33|32|0|32|
|Glenn Robinson III|31.6|12.9|48|17|0|17|
|Mychal Mulder|29.1|11.0|7|58|0|58|
|Damion Lee|29.0|12.7|49|16|0|16|
|Alec Burks|29.0|16.1|48|17|0|17|
|Draymond Green|28.4|8.0|43|22|0|22|
|Stephen Curry|27.9|20.8|5|60|0|60|
|Eric Paschall|27.6|13.9|60|5|0|5|

**1b. Absence Summary**

- Qualified players: 9
- Total star-game absences: 280
- Total possible appearances: 585
- Absence rate: 0.479

**1c. Absence Clustering (Pre vs Post Elimination)**

|Period|Games|Absences|Absence Rate|
|---|---|---|---|
|Pre-elimination|41|168|0.455|
|Post-elimination|24|112|0.519|

- Cluster ratio (post/pre): **1.14x**
- Flag (>=2.0x): **No**

**1d. Absence Distribution by Game Outcome**

|Outcome|Team Games|Star Absences|Absence Rate|
|---|---|---|---|
|Wins|15|63|0.467|
|Losses|50|217|0.482|

**1e. SAS Component Score: 32.5 / 100**


---

#### Component 2: Net Rating Collapse Index (NRCI) — Weight: 25%

**2a. Rolling 15-Game Net Rating**

- Peak rolling net rating: **-4.3** (game 33)
- Trough rolling net rating: **-13.2** (game 59)
- Maximum decline (peak to trough): **8.9**
- Season-long net rating: -8.7
- First 15 games net rating: -8.5
- Last 15 games net rating: -9.6

|Through Game #|Rolling Net Rating|
|---|---|
|15|-8.5|
|25|-10.2|
|35|-5.6|
|45|-6.0|
|55|-9.7|
|65|-9.6|

**2b. Close-Game Performance (games within 8 pts net rating)**

- Close games: 21
- Close game record: 4-17
- Close game win %: **0.19**
- Blowout losses: 20 (0.308)

**2c. Pre/Post Elimination Net Rating**

|Period|Games|Off Rating|Def Rating|Net Rating|
|---|---|---|---|---|
|Pre-elimination|41|102.6|111.1|-8.5|
|Post-elimination|24|107.3|116.3|-9.0|

- Net rating change: **-0.5**
- Collapse flag (change < -3.0): **No**

**2e. NRCI Component Score: 48.4 / 100**


---

#### Component 3: Rotation Integrity Score (RIS) — Weight: 25%

**3a. Pre-Elimination Baseline Rotation (Top 8 by Minutes)**

Pre-elimination games: 41

|Player|Avg Min (Pre)|Games (Pre)|Avg Net Rating|USG%|
|---|---|---|---|---|
|Glenn Robinson III|31.8|40|-10.5|0.16|
|Alec Burks|29.1|38|-10.3|0.223|
|Stephen Curry|28.0|4|-16.1|0.297|
|Damion Lee|26.8|26|-3.8|0.189|
|Eric Paschall|25.0|39|-10.7|0.185|
|Draymond Green|24.2|36|-9.1|0.136|
|Willie Cauley-Stein|22.7|36|-8.4|0.154|
|Ky Bowman|22.5|36|-5.3|0.162|

**3b. Post-Elimination Rotation Changes**

- Post-elimination games: 24
- Significant minute decreases (>=20%): **4**
- Average minutes change: -5.1
- Rotation disruption flag (>=3 sig decreases): **YES**
- New rotation players: 5

|Player|Pre Avg Min|Post Avg Min|Change|Change %|
|---|---|---|---|---|
|Glenn Robinson III|31.8|22.1|-9.7|-30.5%|
|Alec Burks|29.1|26.0|-3.1|-10.7%|
|Stephen Curry|28.0|9.1|-18.9|-67.5%|
|Damion Lee|26.8|31.6|4.8|17.9%|
|Eric Paschall|25.0|28.3|3.3|13.2%|
|Draymond Green|24.2|15.9|-8.3|-34.3%|
|Willie Cauley-Stein|22.7|20.3|-2.4|-10.6%|
|Ky Bowman|22.5|15.8|-6.7|-29.8%|

**New rotation players post-elimination:**

- Andrew Wiggins — 31.0 min/game (13 games)
- D'Angelo Russell — 30.5 min/game (11 games)
- Mychal Mulder — 29.1 min/game (7 games)
- Marquese Chriss — 23.5 min/game (23 games)
- Jordan Poole — 23.0 min/game (24 games)

**3c. Minutes-Quality Correlation Shift**

- Pre-elimination correlation: -0.09
- Post-elimination correlation: 0.153
- Correlation shift: **0.244**

**3d. Lineup Experimentation**

- Pre-elimination unique players/game: 11.4
- Post-elimination unique players/game: 11.2
- Experimentation increase: **-0.2**

**3e. RIS Component Score: 47.5 / 100**


---

#### Component 4: Bottom-Tier Clustering Analysis (BTCA) — Weight: 20%

**4a. League Context — Bottom-6 Analysis**

- Team record: **15-50**
- Current bottom-6 avg wins: **19.0**
- Historical baseline (20 seasons): mean=22.5, σ=2.5
- Deviation from baseline: **-1.42σ**
- Teams on pace for <22 wins: 6
- League-wide cluster flag (>=4 teams): **YES**

|Rank|Team|Wins|
|---|---|---|
|1|Warriors|15|
|2|Cavaliers|19|
|3|Timberwolves|19|
|4|Hawks|20|
|5|Pistons|20|
|6|Knicks|21|

**4b. Individual Team Temporal Pattern (Pre/Post ASB)**

|Split|Record|Win%|Net Rating|
|---|---|---|---|
|Pre-ASB|12-43|0.218|-8.5|
|Post-ASB|3-7|0.3|-9.2|

- Post-ASB as % of pre-ASB: **137.6%**
- Below 50% threshold flag: **No**

**4c. Calendar Correlation — Win Rates by Period**

|Period|Games|Record|Win Rate|
|---|---|---|---|
|Pre-trade deadline|52|12-40|0.231|
|Post-deadline to ASB|3|0-3|0.0|
|Post-elimination|25|6-19|0.24|

- Trade deadline: 2020-02-06
- All-Star break: 2020-02-14
- Elimination date: 2020-01-12

**4d. BTCA Component Score: 37.3 / 100**


---

#### Supplemental Indicators (contextual — not scored)

**5a. Draft Pick Incentive (DPI)**

- Final record: 15-50
- Draft lottery position: **1st**-worst record
- In bottom 3: Yes
- In bottom 5: Yes
- Wins gap to next better draft slot: 4
- Bottom-5 cluster size (teams within 3 wins): 1
- Wins needed to exit bottom 5: 6

**5b. Veteran Shelving Index (VSI)**

- Total unique players used: 22
- Regular rotation size (40%+ games, 15+ min): 12
- One-off players (<5 games): 3
- **Shelved post-elimination: 0**

**5c. Margin of Defeat Profile (MDP)**

- Total losses: 50
- Average loss margin (net rating): -14.5
- Blowout losses (NR < -15): 20 (0.4)
- Competitive losses (NR > -5): 5 (0.1)
- 1st-half season NR: -8.1
- 2nd-half season NR: -9.2
- **Trajectory (2nd half − 1st half): -1.1**
- Pre-elimination avg NR: -8.5
- Post-elimination avg NR: -9.0
- Post-elim margin change: **-0.5**

**5d. Trade Deadline Roster Churn (LOI)**

- Trade deadline date: 2020-02-06
- Total players departed: 6
- **Meaningful departures (10+ min/game): 6**
- Total players arrived: 7
- **Meaningful arrivals (10+ min/game): 7**
- Total roster churn: 13

Key departures:

- Alec Burks (29.0 min/game pre-deadline)
- D'Angelo Russell (32.1 min/game pre-deadline)
- Willie Cauley-Stein (22.9 min/game pre-deadline)
- Glenn Robinson III (31.6 min/game pre-deadline)
- Jacob Evans (15.3 min/game pre-deadline)
- Omari Spellman (18.1 min/game pre-deadline)

Key arrivals:

- Zach Norvell Jr. (12.0 min/game post-deadline)
- Jeremy Pargo (14.8 min/game post-deadline)
- Chasson Randle (13.5 min/game post-deadline)
- Andrew Wiggins (33.6 min/game post-deadline)
- Dragan Bender (21.6 min/game post-deadline)
- Mychal Mulder (29.1 min/game post-deadline)
- Juan Toscano-Anderson (20.9 min/game post-deadline)

- Total unique players used (season): 22
- First-half unique players: 14
- Second-half unique players: 22


---

#### TII Composite Calculation

|Component|Raw Score|Weight|Weighted Score|
|---|---|---|---|
|SAS|32.5 /100|x 0.30|9.8|
|NRCI|48.4 /100|x 0.25|12.1|
|RIS|47.5 /100|x 0.25|11.9|
|BTCA|37.3 /100|x 0.20|7.5|
|**Composite TII**|||**41.3 / 100**|

**Classification: Yellow** (Expected: Green) — **MISMATCH**



### CASE H: Oklahoma City Thunder — 2023-24

**Archetype:** Competitive Team — Strategic Rest/Shelving
**Expected Classification:** Yellow
**Final Record:** 57-25
**Lottery Position:** 28th-worst record
**Computed Elimination Date:** Team finished 57-25, cutoff was 46 wins (seed 10). Not mathematically eliminated (or eliminated on final game).

---

#### Component 1: Star Availability Score (SAS) — Weight: 30%

**1a. Identify Qualified Players (25+ min/game)**

|Player|Avg Min|Avg Pts|Games Played|Games Missed|DNPs|Absent|
|---|---|---|---|---|---|---|
|Shai Gilgeous-Alexander|34.0|30.1|75|7|0|7|
|Jalen Williams|31.3|19.1|71|11|0|11|
|Chet Holmgren|29.4|16.5|82|0|0|0|
|Luguentz Dort|28.4|10.9|79|3|0|3|
|Josh Giddey|25.1|12.3|80|2|0|2|

**1b. Absence Summary**

- Qualified players: 5
- Total star-game absences: 23
- Total possible appearances: 410
- Absence rate: 0.056

**1c. Absence Clustering:** No elimination date — clustering N/A


**1d. Absence Distribution by Game Outcome**

|Outcome|Team Games|Star Absences|Absence Rate|
|---|---|---|---|
|Wins|57|12|0.042|
|Losses|25|11|0.088|

**1e. SAS Component Score: 30.0 / 100**


---

#### Component 2: Net Rating Collapse Index (NRCI) — Weight: 25%

**2a. Rolling 15-Game Net Rating**

- Peak rolling net rating: **12.6** (game 38)
- Trough rolling net rating: **-0.7** (game 79)
- Maximum decline (peak to trough): **13.3**
- Season-long net rating: 7.1
- First 15 games net rating: 9.0
- Last 15 games net rating: 5.5

|Through Game #|Rolling Net Rating|
|---|---|
|15|9.0|
|25|11.1|
|35|7.6|
|45|9.2|
|55|5.8|
|65|5.8|
|75|3.8|

**2b. Close-Game Performance (games within 8 pts net rating)**

- Close games: 35
- Close game record: 22-13
- Close game win %: **0.629**
- Blowout losses: 5 (0.061)

**2c. Pre/Post Elimination:** No elimination date — split N/A

**2e. NRCI Component Score: 29.9 / 100**


---

#### Component 3: Rotation Integrity Score (RIS) — Weight: 25%

RIS not yet computed. Run `python tii.py compute --case H`.


---

#### Component 4: Bottom-Tier Clustering Analysis (BTCA) — Weight: 20%

**4a. League Context — Bottom-6 Analysis**

- Team record: **57-25**
- Current bottom-6 avg wins: **19.7**
- Historical baseline (20 seasons): mean=22.5, σ=2.5
- Deviation from baseline: **-1.15σ**
- Teams on pace for <22 wins: 4
- League-wide cluster flag (>=4 teams): **YES**

|Rank|Team|Wins|
|---|---|---|
|1|Pistons|14|
|2|Wizards|15|
|3|Trail Blazers|21|
|4|Hornets|21|
|5|Spurs|22|
|6|Raptors|25|

**4b. Individual Team Temporal Pattern (Pre/Post ASB)**

|Split|Record|Win%|Net Rating|
|---|---|---|---|
|Pre-ASB|37-17|0.685|7.3|
|Post-ASB|20-8|0.714|7.2|

- Post-ASB as % of pre-ASB: **104.2%**
- Below 50% threshold flag: **No**

**4c. Calendar Correlation — Win Rates by Period**

|Period|Games|Record|Win Rate|
|---|---|---|---|
|Pre-trade deadline|51|35-16|0.686|
|Post-deadline to ASB|3|2-1|0.667|
|Post-ASB|28|20-8|0.714|

- Trade deadline: 2024-02-08
- All-Star break: 2024-02-16

**4d. BTCA Component Score: 17.2 / 100**


---

#### Supplemental Indicators (contextual — not scored)

**5a. Draft Pick Incentive (DPI)**

- Final record: 57-25
- Draft lottery position: **28th**-worst record
- In bottom 3: No
- In bottom 5: No
- Wins gap to next better draft slot: 0
- Bottom-5 cluster size (teams within 3 wins): 3
- Wins needed to exit bottom 5: 0

**5b. Veteran Shelving Index (VSI)**

- Total unique players used: 22
- Regular rotation size (40%+ games, 15+ min): 8
- One-off players (<5 games): 1
- **Shelved post-elimination: 0**

**5c. Margin of Defeat Profile (MDP)**

- Total losses: 25
- Average loss margin (net rating): -11.8
- Blowout losses (NR < -15): 5 (0.2)
- Competitive losses (NR > -5): 7 (0.28)
- 1st-half season NR: 8.1
- 2nd-half season NR: 6.2
- **Trajectory (2nd half − 1st half): -1.9**

**5d. Trade Deadline Roster Churn (LOI)**

- Trade deadline date: 2024-02-08
- Total players departed: 3
- **Meaningful departures (10+ min/game): 1**
- Total players arrived: 4
- **Meaningful arrivals (10+ min/game): 1**
- Total roster churn: 7

Key departures:

- Vasilije Micic (12.0 min/game pre-deadline)

Key arrivals:

- Gordon Hayward (17.2 min/game post-deadline)

- Total unique players used (season): 22
- First-half unique players: 18
- Second-half unique players: 21


---

#### TII Composite Calculation

|Component|Raw Score|Weight|Weighted Score|
|---|---|---|---|
|SAS|30.0 /100|x 0.30|9.0|
|NRCI|29.9 /100|x 0.25|7.5|
|RIS|0.0 /100|x 0.25|0.0|
|BTCA|17.2 /100|x 0.20|3.4|
|**Composite TII**|||**19.9 / 100**|

**Classification: Green** (Expected: Yellow) — **MISMATCH**




<!-- APPENDIX_A_AUTOGEN_END -->

## Cross-Case Calibration Matrix

After all cases are scored, populate this summary to identify systemic calibration issues:

|Case|Team|Expected|Actual TII|Actual Class.|Match?|Primary Driver|Problem Component (if any)|
|---|---|---|---|---|---|---|---|
|A|PHI 2013-14|Red||||||
|B|PHI 2015-16|Red||||||
|C|POR 2022-23|Orange/Red||||||
|D|WAS 2023-24|Yellow/Orange||||||
|E|UTA 2024-25|Red||||||
|F|MIN 2014-15|Green||||||
|G|GSW 2019-20|Green||||||
|H|League 2025-26|Tier 1-2 ETP||||||

### Calibration Questions This Matrix Must Answer

1. **Separation:** Is there clear daylight between the scores of known tankers (A, B, C, E) and known legitimate teams (F, G)? If the scores overlap, the thresholds are wrong.
    
2. **Ambiguity handling:** Does the ambiguous case (D — Washington) land in the Yellow/Orange zone where it belongs, rather than being pushed to an extreme?
    
3. **Component consistency:** Does any single component produce scores that are dramatically out of line with the other three across multiple cases? If SAS is flagging every team while RIS flags none, the weights or thresholds need rebalancing.
    
4. **False positive rate:** Do the control cases (F, G) score safely in Green territory, or are they uncomfortably close to Yellow? If a legitimately injured Warriors team scores 40+, the system has a false positive problem.
    
5. **ETP tier accuracy:** In the systemic cluster case (H), does the BTCA produce tier classifications that match the severity of the real-world situation? If 4 teams are clearly tanking and the system only reaches Tier 1, the escalation thresholds are too conservative.
    

---

## Data Source Requirements

Each backtesting case requires the following data, all of which is publicly available through NBA statistics platforms and media reporting:

|Data Category|Source(s)|Required For|
|---|---|---|
|Game-by-game results and box scores|NBA.com/stats, Basketball Reference|All components|
|Player minutes per game|NBA.com/stats, Basketball Reference|SAS, RIS|
|Injury reports and designations|NBA official injury reports, Rotoworld archives|SAS exclusions|
|Net rating (team and lineup level)|NBA.com/stats, Cleaning the Glass|NRCI, RIS|
|Opponent offensive/defensive efficiency|Basketball Reference, Cleaning the Glass|NRCI (expected NR)|
|Player impact metrics (EPM, RAPTOR, etc.)|Dunks & Threes (EPM), FiveThirtyEight (RAPTOR)|NRCI (roster talent), RIS (quality correlation)|
|Trade transaction records|Basketball Reference, Spotrac|NRCI (recalibration)|
|Strength of schedule|Basketball Reference|NRCI (normalization)|
|Historical bottom-6 win totals (20 seasons)|Basketball Reference|BTCA (baseline)|
|National broadcast schedule|ESPN/TNT schedule archives|SAS (absence clustering)|
|Standings snapshots (weekly)|Basketball Reference|SAS (competitive significance), BTCA (calendar correlation)|

---

## Backtesting Execution Order

**Phase 1: Anchor Cases** Score the two clearest cases first — one obvious tank (Case A: Process Sixers Year 1) and one obvious control (Case F: 2014-15 Timberwolves or Case G: 2019-20 Warriors). These establish the scoring range endpoints. If the system can't clearly separate these two, no further testing is meaningful until thresholds are adjusted.

**Phase 2: Stress Cases** Score the ambiguous and mid-severity cases (C, D, E). These test whether the system produces graduated classifications rather than binary all-or-nothing results. The Portland case is particularly important because it involves a mid-season behavioral shift.

**Phase 3: Systemic Case** Score the league-wide cluster (Case H) last. This is the only case that tests ETP tier activation and requires multiple teams to be scored simultaneously. It depends on calibrated component scores from Phases 1-2.

**Phase 4: Recalibration** Populate the cross-case matrix. Identify any threshold adjustments needed. Re-score affected cases. Document final calibrated thresholds with justification.

---

_Template Version 1.0 — Ready for data population_