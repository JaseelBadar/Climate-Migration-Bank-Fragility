#  VARIABLES  CODEBOOK  +  CODING  PROTOCOL  (v1.6)
**Project**:  Climate  Shocks,  Displacement,  and  Bank  Liquidity  Risk:  Evidence  from  Night-Lights  in  India  (2015–2024)    
**Document  Type**:  Variables  codebook  +  enforceable  coding  protocol    
**Version**:  1.6  (Script  21  bug  fix  implemented;  overnight  VIIRS  regeneration  in  progress)
**Date**:  January  20,  2026

---

##  0)  Non-negotiable  principles  (read  first)

1.  **Raw  data  is  read-only**:  Never  modify  anything  inside  `01_Data_Raw/`.  All  transformations  must  write  to  `02_Data_Intermediate/`  or  `03_Data_Clean/`.    
2.  **No  silent  drops**:  Any  row/observation  dropped  must  be  logged  with  counts  and  reasons.    
3.  **No  endogeneity  by  construction**:  Never  use  VIIRS  outcomes  to  define  flood  treatment.  (No  “flood  =  1  if  lights  drop”.)    
4.  **One  script  =  one  responsibility**:  Each  script  produces  one  named  output  dataset  and  one  log  file.    
5.  **Reproducibility  beats  cleverness**:  Prefer  simple,  auditable  transformations  over  complex  heuristics.    
6.  **Do  not  overclaim**:  If  a  variable  is  a  proxy  (urban,  migration,  exposure),  label  it  as  such  in  outputs  +  paper.
7.  **No  district-name  dissolve:  Never  dissolve  GADM  districts  using  NAME_2  alone  (homonymous  districts  across  states  will  merge).  If  dissolve  is  needed,  it  must  include  state  (NAME_1)  or  a  stable  unique  ID;  otherwise,  do  not  dissolve.


---

##  I)  Panel  structure

**Canonical  unit**:  Indian  district  polygons  from  **GADM  v4.1  Level-2**.    
RBI  districts  are  mapped  to  GADM  using  a  crosswalk  (RBI  is  not  the  canonical  geography).    

**Target  period**:  Quarterly,  2015Q1  to  2024Q4  (40  quarters).    

**Important  implementation  reality  (must  be  documented,  not  hidden)**:
-  The  “analysis  sample”  may  drop  quarters  with  missing  deposits  and  may  drop  districts  with  zero  deposit  coverage  (this  is  a  sample  restriction,  not  a  data  “feature”).    

**Key  index  variables  (must  exist  in  final  analysis  panel)**    
(Names  are  aligned  to  the  implemented  pipeline  /  Script  24  conventions.)
-  `districtgadm`:  canonical  district  name  (GADM).
-  `stategadm`:  canonical  state  name  (GADM).
-  `quarter`:  string  like  `2015Q1`.
-  `year`:  2015–2024.
-  `q`:  1–4.
-  `quarternum`:  sequential  index  (1–40)  used  for  sorting/lags.

**Sorting  rule  (locked)**:
-  Always  sort  by  `districtgadm`,  `stategadm`,  `quarternum`  before  constructing  lags/differences.

---

##  II)  Outcome  variables  (banking)

###  A)  Deposits  (levels)
**Variable**:  `depositscrores`    
-  **Definition**:  Total  deposits  in  district-quarter.    
-  **Unit**:  ₹  crores  (verify  from  RBI  tables;  treat  as  nominal  unless  deflated).    
-  **Construction**:  RBI  extraction  aggregates  across  population  groups  where  needed.

**Variable**:  `logdepositscrores`    
-  **Definition**:  natural  log  of  deposits.    
-  **Construction**:  `logdepositscrores  =  ln(depositscrores)`    
-  **Rule**:  Do  not  add  arbitrary  constants  unless  deposits  can  be  zero;  if  a  constant  is  used,  it  must  be  fixed  and  logged.

###  B)  Deposits  (growth)
**Variable**:  `depositchangeqt`    
-  **Definition**:  quarter-over-quarter  log  change  in  deposits  (approx  %  change).    
-  **Construction**:  within  district,
    -  `depositchangeqt  =  logdepositscrores  -  L1(logdepositscrores)`    
-  **Missingness  rule**:  first  observed  quarter  per  district  will  have  missing  change  by  construction.

###  C)  Optional  “withdrawal  event”  proxy  (only  if  used  in  paper)
**Variable**:  `depositwithdrawalbinary`  (optional)    
-  **Definition**:  indicator  for  unusually  large  deposit  decline  (shadow-run  proxy).    
-  **Pre-commitment  rule**:
    -  Define  threshold  `k`  from  a  baseline  distribution  BEFORE  any  mechanism  regressions.
    -  Example  baseline:  bottom  decile  of  `depositchangeqt`  among  non-flood  observations  OR  a  fixed  −10%  rule,  whichever  is  more  conservative.
-  **Construction**:  `1[depositchangeqt  <  k]`.

---

##  III)  Treatment  variables  (flood  shocks)

Flood  exposure  is  constructed  from  EM-DAT  and  mapped  into  quarters,  then  into  districts  using  a  documented  rule  set.    

###  A)  Exposure  indicators  (two  precision  regimes;  both  required)
**Variable**:  `floodexposureruleAqt`    
-  **Rule  A  (full  sample  /  lower-bound)**:  if  event  location  is  only  state-level,  code  flood  exposure  for  **all  districts  in  that  state**  for  that  quarter.    
-  **Interpretation  constraint**:  attenuation  bias  is  expected  due  to  false  positives.

**Variable**:  `floodexposureruleBqt`    
-  **Rule  B  (high-precision  /  credibility  spec)**:  code  exposure  only  when  districts  are  explicitly  identified  (Admin  Units  and/or  verified  parsing).    
-  **Interpretation  constraint**:  smaller  effective  treatment  variation;  may  weaken  power.

###  B)  Lags  (timing  tests)
**Variable**:  `floodlag1qt`    
-  **Definition**:  one-quarter  lag  of  flood  exposure  (baseline:  Rule  A  unless  explicitly  running  Rule  B  spec).    
-  **Construction**:  `L1(floodexposureruleAqt)`  within  district.

**Variable**:  `floodlag2qt`  (optional  if  used)    
-  **Construction**:  `L2(floodexposureruleAqt)`  within  district.

###  C)  Severity  (optional;  only  if  available  and  logged  cleanly)
**Variable**:  `floodseverityqt`  (optional)    
-  **Preferred  construction**:  `ln(affected  +  deaths  +  1)`  if  both  are  available  with  acceptable  completeness.    
-  If  missingness  is  large,  severity  must  be  treated  as  exploratory  (not  a  main  result).

---

##  IV)  Migration  /  disruption  proxy  (VIIRS  night  lights)

###  A)  Quarterly  lights  level
**Variable**:  `meanradiance`    
-  **Definition**:  district-quarter  mean  VIIRS  radiance  (after  monthly  extraction  and  quarterly  aggregation).    
-  **Rule**:  This  variable  must  be  constructed  only  from  VIIRS  (never  influenced  by  flood  coding).

**Variable**:  `loglightsqt`    
-  **Definition**:  log-transformed  quarterly  lights  level.    
-  **Construction  (as  implemented  in  Script  24)**:  `loglightsqt  =  ln(meanradiance  +  c)`  with  a  fixed  constant.    
-  **Constant  rule  (locked)**:
    -  If  a  constant  `c`  is  used  to  handle  zeros,  it  must  be  fixed  globally  and  written  into  logs;  never  tuned  for  results.
    -  Current  pipeline  uses  a  +1  offset  (record  and  keep  fixed  unless  a  formal  change  is  logged).

###  B)  Quarterly  lights  change
**Variable**:  `lightschangeqt`    
-  **Definition**:  quarter-over-quarter  change  in  log  lights  (approx  %  change).    
-  **Construction**:  within  district,
    -  `lightschangeqt  =  loglightsqt  -  L1(loglightsqt)`.

###  C)  Optional  migration/disruption  event  indicator  (only  if  used)
**Variable**:  `migrationproxyqt`  (optional)    
-  **Definition**:  indicator  for  a  large  negative  lights  shock.    
-  **Construction**:  `1[lightschangeqt  <  -theta]`.    
-  **Threshold  discipline**:
    -  `theta`  must  be  chosen  from  the  empirical  distribution  in  flood-exposed  district-quarters  in  the  high-precision  sample  (Rule  B),  and  recorded  before  estimating  final  H2  event-spec  regressions.
    -  Robustness:  theta  ∈  {0.10,  0.15,  0.20}.

---

##  V)  Controls  and  fixed  effects

###  A)  Minimum  viable  controls  (baseline)
-  **District  fixed  effects**:  absorb  time-invariant  district  differences.
-  **Quarter  fixed  effects**:  absorb  national  seasonality  and  macro  shocks.

###  B)  Optional  seasonality  marker  (redundant  but  sometimes  useful)
**Variable**:  `monsoonquarter`  (optional)    
-  **Construction**:  `1[q  ==  3]`  (Jul–Sep),  else  0.    
-  **Rule**:  If  quarter  FE  are  included,  monsoon  indicator  is  not  required  for  identification;  use  only  for  exposition  or  robustness.

###  C)  Weather  controls  (preferred  extension)
**Variable**:  `rainfallqt`  (optional)    
-  Must  be  spatially  aggregated  to  district  polygons  and  then  to  quarters  with  a  documented  method.

---

##  VI)  Heterogeneity  variables  (core  only  if  actually  used)

Heterogeneity  variables  must  be  defined  **pre-treatment**  (time-invariant  or  baseline-period  constructs)  or  explicitly  lagged  so  they  are  not  mechanically  affected  by  contemporaneous  floods.

Examples  (choose  only  if  defensible  +  logged):
-  “Urban  proxy”  based  on  baseline  deposits  (time-invariant  classification).
-  “High  exposure”  based  on  pre-period  flood  history.

Rule:  any  proxy  must  be  labeled  a  proxy;  do  not  rewrite  it  as  “urbanization”  without  census  validation.

---

##  VII)  IV  /  causal  pipeline  constructs  (audit  variables)

These  are  not  “nice  to  have.”  They  exist  to  keep  the  IV  pipeline  auditable.

**Variable**:  `lightshatqt`  (optional  storage,  but  recommended)    
-  **Definition**:  fitted  values  from  first  stage  (flood  →  lights).    
-  **Rule**:  store  for  diagnostics  only;  do  not  interpret  as  observed  lights.

**Metric**:  `firststageF`    
-  **Definition**:  first-stage  instrument  strength  statistic.    
-  **Rule**:  weak-IV  risk  must  be  reported;  never  buried.

---

##  VIII)  File  IO  contract  (locked)

-  Inputs:  only  from  `01_Data_Raw/`    
-  Intermediate  outputs:  `02_Data_Intermediate/`    
-  Final  analysis  panels:  `03_Data_Clean/`    
-  Figures/tables:  `05_Outputs/Figures/`,  `05_Outputs/Tables/`    
-  Logs:  `05_Outputs/Logs/`

---

##  IX)  Script  contract  (locked)

Every  script  must:
1.  Log  start/end  time.
2.  Log  exact  input  file  paths  and  output  file  paths.
3.  Log  row  counts  before/after  major  steps.
4.  Log  any  constant  choices  (e.g.,  lights  log  offset  `c`).
5.  Write  a  log  file  to  `05_Outputs/Logs/`.

---

##  X)  Versioning  rule

-  The  codebook  is  allowed  to  evolve,  but  **only**  via  version  bumps  with  explicit  changelogs.
-  Hypotheses  are  not  allowed  to  drift  to  match  results;  codebook  updates  must  be  about  measurement  feasibility,  naming  consistency,  or  reproducibility  discipline.

---

##  XI)  Data  quality  issues  identified  (2026-01-18  audit)

**Context**:  Phase  4  regressions  (H1-H4)  executed  with  preliminary  results.  Critical  data  quality  issues  discovered  during  descriptive  statistics  review.  **All  regressions  require  re-execution  after  corrections  applied.**

###  Issue  1:  Extreme  outliers  in  deposit  changes
**Variable  affected**:  `depositchangeqt`    
**Problem**:  Min  =  -2.73  (93%  decline),  Max  =  +6.56  (656%  increase)  in  single  quarters    
**Likely  causes**:
-  District  boundary  changes  or  mergers  (administrative)
-  Bank  branch  reclassification  between  districts  (RBI  reporting)
-  Data  entry  errors  in  RBI  source  Excel  files

**Impact**:  Outliers  bias  OLS  coefficients  and  inflate  standard  errors    
**Correction  required**:  Winsorize  at  1st/99th  percentile  before  final  regressions    
**Status**:  Pending  (scheduled  2026-01-19)

###  Issue  2:  Nominal  growth  confound  (no  deflation  applied)
**Variable  affected**:  `depositscrores`,  `depositchangeqt`    
**Problem**:  Mean  deposit  growth  =  11.9%  quarterly  (47.6%  annualized,  compounded)    
**Root  cause**:  RBI  deposits  measured  in  nominal  rupees;  no  CPI  deflation  applied    
**Impact**:  Inflation  trends  confound  flood  treatment  effects;  cannot  distinguish  real  shock  from  price  growth    
**Correction  options**:
1.  Deflate  deposits  by  CPI  (preferred  if  district-level  deflator  available)
2.  Disclose  limitation  explicitly  in  paper  and  interpret  coefficients  as  nominal  effects

**Status**:  Decision  pending  (scheduled  2026-01-19)

###  Issue  3:  Zero-inflation  in  deposit  changes
**Variable  affected**:  `depositchangeqt`    
**Problem**:  25th  percentile  =  0.00  →  25%  of  district-quarters  have  exactly  zero  deposit  change    
**Possible  causes**:
-  Rounding  in  RBI  source  data  (deposits  reported  in  crores)
-  Static  rural  districts  with  no  actual  banking  activity
-  Copy-forward  errors  (same  value  repeated  across  quarters)

**Impact**:  Potential  measurement  error;  may  reflect  true  absence  of  activity  OR  data  quality  issue    
**Investigation  required**:  Identify  which  districts,  which  periods,  whether  systematic  pattern  exists    
**Status**:  Pending  (scheduled  2026-01-19)

###  Issue  4:  VIIRS  data  contamination  (Script  21  dissolve  bug)  —  CRITICAL
**Variables  affected**:  `meanradiance`,  `loglightsqt`,  `lightschangeqt`    
**Problem  discovered**:  Script  21  used  `.dissolve(by='NAME_2')`  which  merged  homonymous  districts  across  states    
**Contamination  details**:
-  17  districts  lost  (Aurangabad  Bihar  merged  with  Aurangabad  Maharashtra,  etc.)
-  2,040  monthly  observations  missing  (17  districts  ×  120  months)
-  680  quarterly  observations  missing  (17  districts  ×  40  quarters)
-  Remaining  7  district-pairs  share  identical  contaminated  VIIRS  values

**Root  cause**:  Line  53  of  Script  21  grouped  by  district  name  alone,  ignoring  state  boundaries    
**Impact**:  All  Phase  4  H1-H4  regression  coefficients  contaminated  by  measurement  error  (classical  attenuation  bias)    
**Fix  implemented**:  Deleted  dissolve  block  (Lines  52-55);  added  validation  assertion  for  676  districts    
**Status**:  Overnight  regeneration  running  (2026-01-20  23:00  →  2026-01-21  ~06:00);  Scripts  22-30  pending

###  Audit  checklist  (all  regressions  affected)
**VIIRS  BUG  FIX  (Priority  1  —  overnight  2026-01-20→21)**:
-  [x]  Identify  Script  21  dissolve  bug  (2026-01-20  17:00  IST)
-  [x]  Delete  dissolve  block  (Lines  52-55)  from  Script  21
-  [x]  Add  district  count  validation  (assert  676  districts  loaded)
-  [x]  Backup  all  contaminated  files  to  *_CONTAMINATED_BACKUP/  folders
-  [x]  Delete  contaminated  VIIRS  panels,  analysis  files,  regression  outputs
-  [⏳]  Script  21  extraction  running  (overnight,  ~6-8  hours)
-  [  ]  Verify  output:  81,120  rows  (676  districts  ×  120  months)
-  [  ]  Run  Script  22:  Aggregate  to  quarterly  (expected  27,040  rows)
-  [  ]  Run  Scripts  23-30:  Merge,  engineer,  validate,  regress

**DATA  QUALITY  CORRECTIONS  (Priority  2  —  after  VIIRS  regeneration)**:
-  [  ]  Apply  winsorization  to  `depositchangeqt`  (1%/99%)
-  [  ]  Decide  on  CPI  deflation  vs.  disclosure  strategy
-  [  ]  Investigate  zero-change  quarters  (run  diagnostic  script)
-  [  ]  Diagnose  213  extra  missing  observations
-  [  ]  Update  all  descriptive  statistics  tables
-  [  ]  Compare  contaminated  vs  clean  H1-H4  coefficients
-  [  ]  Update  regression  output  CSVs  and  log  files
-  [  ]  Document  all  corrections  in  ResearchLog.txt

**CONTAMINATED  results  (2026-01-18  execution  —  DO  NOT  CITE)**:
-  H1  (Flood  →  Lights):  β  =  -0.0126***  (p  <  0.001)  —  CONTAMINATED  (attenuated)
-  H2  (Lights  →  Deposits,  IV):  β  =  0.120  (p  =  0.538)  —  CONTAMINATED  (unreliable)
-  H3  (Timing):  All  lags  insignificant  —  CONTAMINATED
-  H4a  (Urban  ×  Flood):  β  =  -0.0404**  (p  =  0.005)  —  CONTAMINATED  (wrong  clustering)

**Critical  warning**:  All  Phase  4  results  generated  from  contaminated  VIIRS  data  (17  missing  districts,  measurement  error  in  7  district-pairs).  These  coefficients  are  INVALID  and  preserved  only  for  comparison  after  regeneration.

**Expected  changes  after  Script  21  fix**:
-  H1  β:  -0.0126  →  approximately  -0.025  to  -0.030  (reduced  attenuation)
-  H2  first-stage  F-stat:  Will  increase  (stronger  instrument)
-  H4  standard  errors:  Will  change  (correct  clustering  with  676  districts)

**Interpretation  caveat**:  All  mechanistic  claims  suspended  pending  clean  data  regeneration  (expected  2026-01-21  morning).  Additional  data  quality  issues  (outliers,  nominal  growth,  zero-inflation)  remain  unaddressed.

---

##  END  OF  DOCUMENT
**Status**:  v1.6  documents  Script  21  bug  fix  and  overnight  VIIRS  regeneration  status  (2026-01-20  23:45  IST).  All  Phase  4  results  contaminated;  clean  regeneration  in  progress.    

**Changelog  (v1.5  →  v1.6)**:
-  Updated  Issue  4:  "Weak  migration  signal"  →  "VIIRS  data  contamination  (Script  21  dissolve  bug)"
-  Documented  bug  details:  17  missing  districts,  2,040  missing  monthly  observations
-  Expanded  audit  checklist:  Split  into  VIIRS  bug  fix  (Priority  1)  and  data  quality  corrections  (Priority  2)
-  Updated  results  status:  "Preliminary"  →  "CONTAMINATED  —  DO  NOT  CITE"
-  Added  expected  coefficient  changes  after  regeneration  (pre-registered  predictions)

**Next  review  trigger**:  Post-VIIRS  regeneration  completion  (2026-01-21  ~06:00  IST).  After  verifying  Script  21  output  (81,120  rows,  676  districts),  execute  Scripts  22-30  sequentially.  Update  to  v1.7  with  clean  descriptive  statistics,  corrected  regression  coefficients,  and  quantified  measurement  error  impact  (contaminated  vs  clean  comparison).**Status**:  v1.6  documents  Script  21  bug  fix  and  overnight  VIIRS  regeneration  status  (2026-01-20  23:45  IST).  All  Phase  4  results  contaminated;  clean  regeneration  in  progress.    

**Changelog  (v1.5  →  v1.6)**:
-  Updated  Issue  4:  "Weak  migration  signal"  →  "VIIRS  data  contamination  (Script  21  dissolve  bug)"
-  Documented  bug  details:  17  missing  districts,  2,040  missing  monthly  observations
-  Expanded  audit  checklist:  Split  into  VIIRS  bug  fix  (Priority  1)  and  data  quality  corrections  (Priority  2)
-  Updated  results  status:  "Preliminary"  →  "CONTAMINATED  —  DO  NOT  CITE"
-  Added  expected  coefficient  changes  after  regeneration  (pre-registered  predictions)

**Next  review  trigger**:  Post-VIIRS  regeneration  completion  (2026-01-21  ~06:00  IST).  After  verifying  Script  21  output  (81,120  rows,  676  districts),  execute  Scripts  22-30  sequentially.  Update  to  v1.7  with  clean  descriptive  statistics,  corrected  regression  coefficients,  and  quantified  measurement  error  impact  (contaminated  vs  clean  comparison).