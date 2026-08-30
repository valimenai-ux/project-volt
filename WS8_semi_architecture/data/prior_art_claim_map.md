# WS8 TASK 0 — PRIOR-ART CLAIM MAP
## Vehicle One semi-scale architecture trial · candidate S3 (tandem split: diesel axle on ONE fixed ratio, no gearbox anywhere, + disconnectable e-axle owning launch)

---

## 0. EVIDENCE-QUALITY STATEMENT — READ FIRST, AND CARRY IT INTO `REPORT_WS8.md`

**All five sweeps hit the same wall.** Every lens reports that the organisation egress proxy refused CONNECT to essentially every load-bearing host — `patents.google.com`, `worldwide.espacenet.com`, `image-ppubs.uspto.gov`, `sciencedirect.com`, `mdpi.com`, `osti.gov`, `epa.gov`, `nhtsa.gov`, `ecfr.gov`, `theicct.org`, `eur-lex.europa.eu`, `unece.org`, `saemobilus.sae.org`, `docs.nrel.gov`, `nationalacademies.org`, `en.wikipedia.org` — returning 403 `connect_rejected` to both WebFetch and curl. Two lenses additionally exhausted the 200-call WebSearch budget (lens 4 after 4 queries; lens 5 on its first call). Only `github.com` / `raw.githubusercontent.com` resolved anywhere.

**Consequence, stated bluntly:** *no primary document was read in full anywhere in this sweep.* No patent independent claim was read verbatim. No regulatory clause was read from the register (two EU clauses were extracted verbatim **by the search engine** from primary law and are the strongest textual evidence in the corpus). No SAE/journal full text was read. No spreadsheet or engine map was retrieved.

**Provenance classes used throughout this document.** Nothing in class (1)–(3) may be promoted into a `REPORT_WS8.md` headline number without re-verification. Per the E13 precedent named in the assignment, everything below is **PROVISIONAL-CITED**:

| Class | Meaning | Permitted use |
|---|---|---|
| **(1) SEARCH-SUMMARY** | Figure quoted by a server-side search result summary, source URL attached, page never opened | Bracketing a corridor; naming a case. **Not** a citation. |
| **(2) RECALL** | Model knowledge only; URL is a *verification worklist entry*, not a page read | Direction of travel only. Flag loudly. |
| **(3) DERIVED (lens)** | Physics computed inside a sweep from the assignment vehicle definition | Usable, re-runnable, but re-check the input ratio/mass assumptions — see §3.0 |
| **(4) DERIVED (this synthesis, repo-checked)** | Computed here against `ws8_params.py` / `ws8_engine.py` / `ws8_candidates.py` on disk | Safe; auditable by re-running |

**Task 0 is therefore PARTIAL, not complete.** The claim map is populated and the S3 contradictions are established, but the freedom-to-operate and novelty positions in §2 are **lead lists, not opinions**, and would need a re-run with patent-database access or outside counsel.

---

# PART 1 — OCCUPIED GROUND

Merged across all five lenses. Duplicates collapsed; the strongest quantified statement of each claim retained with its URL.

## 1.A — Through-the-road / P4 e-axle overlays (S3's axle B, with the AMT LEFT IN)

This is the densest occupied territory in the whole map and the closest commercial analogue to S3. **Every member leaves the diesel's multi-speed transmission completely untouched — that is the product's selling point, not an oversight.**

| Item | Architecture | Quantified claim | URL |
|---|---|---|---|
| **Hyliion 6X4HE** (2017–2024) | P4 tandem split — diesel keeps its own axle + full AMT, e-machine drives the other tandem axle. **The only commercial "tandem split" ever built.** | 115 hp / 1,500 lb-ft (86 kW / 2,034 Nm) motorised axle. **15% fuel from the hybrid axle alone, best-case rolling hilly terrain**; the marketed 30% = 15% hybrid + 12% APU + 3% aero. Mass **+800 lb (363 kg)**, net +400 lb against the federal APU allowance. $37–40k. Battery never disclosed in kWh. | [truckinginfo](https://www.truckinginfo.com/news/electric-axle-for-trucks-saves-up-to-15-in-fuel-hyliion-says) · [fleetequipmentmag](https://www.fleetequipmentmag.com/hyliion-6x4he-hybrid-electric-truck-axle/) |
| Hyliion electric-drive **trailer tandem** (predecessor) | P4 on the trailer | Claim fell **21% → 15%** as it moved from concept to a measured tractor-mounted axle | [truckinginfo](https://www.truckinginfo.com/articles/hybrid-electric-drive-trailer-tandem-promises-quick-payback) |
| **Revoy EV dolly** (2026, $27M raise) | P4 inserted in the coupling; tractor unmodified | **525–575 kWh LFP, 400 kW**, 200–250 mi electric at 36 t. Claimed 90–95% diesel reduction (MVTS measured **90.4% flat terrain**). **MASS ~10 t / 22,000 lb**, +13 ft length | [electrek](https://electrek.co/2026/08/04/revoy-ev-promises-to-electrify-diesel-semis-in-minutes/) |
| **Range Energy RA-01 / RB-01** eTrailer | P4, **800 V single-speed** e-axle | 200 kWh (RA-01) / 200–300 kWh (RB-01); 250–350 kW; **14,000 Nm at the wheels** — the best-documented single-speed Class 8 e-axle torque figure in the record. MVT-certified **+36.3%** (3.82 mpg on vs off); 48% heavy city, 41% mixed, **LOWEST on long-haul** | [newatlas](https://newatlas.com/automotive/range-energy-electrified-trailer/) · [m-v-t-s](https://www.m-v-t-s.com/certified-technology/drivetrain/range-ra-01-powered-trailer/) |
| **Trailer Dynamics / KRONE** eTrailer | P4, orderable from KRONE since 2024 | eAxle **360 kW cont. / 580 kW peak**; claimed **40% average** diesel and CO₂ reduction; €25M raised on that claim | [motortransport](https://motortransport.co.uk/freightcarbonzero/trailer-dynamics-secures-25m-to-invest-in-e-trailers-that-cuts-fuel-use-by-40/88523.article) |
| Hyliion **TTR patent family** — US20180086227A1, US10245972, US10596913, US10744888, US11833905, US12024029, US12319150, US10889288, US11046302, US11351979, US11932232, US20240034298A1 | Claims: supplement an **unmodified** primary drivetrain with supplemental torque at e-axles; adaptive-ECMS at the e-axle **without participating in engine or primary-drivetrain control**; BSFC-adaptation to the paired engine; regen off brake-line pressure; **predictive slip/traction assistance from cloud + route data** | Claim text NOT read (403) | [patents.google](https://patents.google.com/patent/US20180086227A1/en) |
| **EP0492152A1** (~1991) | Recites as **admitted prior art**: "the internal combustion engine with clutch and conventional change-speed gearbox acts on one axle of the vehicle and an electric machine acts directly on the other axle" | — | [patents.google](https://patents.google.com/patent/EP0492152A1) |
| US6481519B1 / US6499549B2 / US6604591B2 (~2000–03) | Single planetary-reduction e-axle paired with an engine axle = through-the-road 4WD hybrid | — | [patents.google](https://patents.google.com/patent/US6481519B1/en) |
| US20090223725A1 | Heavy-duty multi-driven-axle trucks hybridised with a motor **before, between or after the rear axles** | — | [patents.google](https://patents.google.com/patent/US20090223725) |

**Merged finding:** the bare S3 *topology* — engine on one axle, electric machine on the other — was admitted prior art in Europe in 1991, productised at Class 8 exactly once (Hyliion 6X4HE), and is unencumbered. **Nobody in this class has ever monetised, claimed or even discussed AMT deletion.** Its absence is structural: every overlay advertises "no modification to the tractor" as a *feature*.

## 1.B — Pre-transmission parallel (P2/P3): the OEM consensus

| Item | Architecture | Quantified claim | URL |
|---|---|---|---|
| **Scania hybrid / PHEV** (DC09 + 130 kW; **GE281**) | P2 — two electric machines **merged into the Opticruise gearbox itself**; the AMT is the structural host | Up to **40% fuel, explicitly in city areas**, conditional on hilliness and stop count | [scania](https://www.scania.com/uk/en/home/about-scania/newsroom/news/2021/Scania-introduces-world-class-versatile-hybrid-trucks.html) |
| **Volvo I-SAM / FE Hybrid** | P2, retains I-Shift | Headline "up to 35%"; **realistic 15–20%** distribution/refuse; up to 30% refuse with electrified compactor | [volvogroup](https://www.volvogroup.com/en/news-and-media/news/2008/sep/news-48550.html) |
| **Freightliner M2e Hybrid** (Eaton HEV drive unit) | P2 sandwiched between Cummins ISB and Eaton UltraShift AMT | Up to 30% (some sources ~40%); up to 60% utility/PTO | [worktruckonline](https://www.worktruckonline.com/articles/freightliner-m2e-hybrid-gets-down-to-business) |
| **Great Wall Hi4-G** heavy truck | P2 + P2.5 dual-motor with a **purpose-built 8-SPEED DHT** — "three engines, eight gears, ten modes" | **29.7 L/100 km vs 35.8 L/100 km** China stage-4 class standard = **17% reduction** (note 49 t GCW) | [chinatruck](https://www.chinatruck.net/news/great-wall-heavy-duty-truck-releases-hi4-g-hybrid-technology/) |
| **Foton Auman EST / GTL Star HEV** | Series-parallel with a direct-drive *mode* on top of a multi-speed box | 730 hp / 3,900 Nm; **10% overall, 26% mountainous, 16% highway** — the best terrain-resolved HD hybrid dataset located | [yunshuren](https://en.yunshuren.com/article-50554.html) |
| **BAE HybriDrive Parallel** | Single machine between engine and transmission; transmission retained | **30% average across standard cycles, BEST between 5 and 20 mph**; motor 95–145 hp / 300–400 lb-ft supporting 350–600 hp engines | [baesystems](https://www.baesystems.com/en-us/article/bae-systems-hybridrive-parallel-system-for-heavy-duty-trucks-achieves-30-percent-fuel-economy-savings) |
| **US8875819B2** (BAE, filed 2010) | **Closest structural analogue to S3 in the patent record**: ICE as primary motive power to front-most + middle drive axle; **clutched electric motor to the rear-most drive axle** | Engine path retains conventional (multi-ratio) drive | [patents.google](https://patents.google.com/patent/US8875819) |
| **DE102016006206A1 / EP3246188A1** (MAN lineage) | P3 "adaptation transmission" carrying a motor-generator — but **alongside a retained main gearbox**, not instead of it | — | [patents.google](https://patents.google.com/patent/EP3246188A1/en) |
| **WO2019165167A1** (Scania) | **Cross-axle electric torque-fill**: second axle's machine temporarily raises torque to compensate the shift disturbance on the first axle | Presupposes the gearbox exists | [patents.google](https://patents.google.com/patent/WO2019165167A1/en) |
| Torque-fill cluster — US6629026B1, US20110168469A1, US20130296127A1, EP2490909A1, DE10163382A1, IEEE 1023222 | Electric torque-fill across an AMT shift | **Published benefit is driveability / elimination of traction interruption — NOT a quantified fuel saving.** No source fills the ratios themselves | [ieee](https://ieeexplore.ieee.org/document/1023222) |

**Merged finding, and the sharpest cross-lens agreement in the map:** the peer-reviewed comparison states that P2 is the predominant non-plug-in Class 8 configuration, "offering superior fuel conversion efficiency compared to series hybrid and other types of parallel hybrid architectures (P0, P1, P3, and P4)", because "in P3 and P4 a larger and more expensive electric machine is necessary to achieve pure electric drive, since there is **no torque amplification by the transmission**", and "the P4 system cannot benefit from the variable transmission gear ratio." ([sciencedirect S0196890424003923](https://www.sciencedirect.com/science/article/pii/S0196890424003923))

## 1.C — Series diesel-electric and range-extenders (S1 / S4 territory; the ONLY gearbox-free heavy path)

| Item | Architecture | Quantified claim | URL |
|---|---|---|---|
| **Hyliion Hypertruck ERX** (Peterbilt 579) | **SERIES.** Generator bolted to the rear of the engine *literally where the transmission used to be*. Tandem Meritor 14Xe e-axles — **EACH WITH A TWO-SPEED GEARBOX** | **211 kWh**, 670 hp, 75 mi electric, 1,000+ mi combined. Discontinued Nov-2023/Q1-2024 for complexity, cost, CARB recertification | [fleetequipmentmag](https://www.fleetequipmentmag.com/heavy-duty-hyliion-hybrid-powertrain/) · [electrive](https://www.electrive.com/2021/08/10/meritor-to-supply-drive-systems-for-hyliion/) |
| **ePower Engine Systems** (US8783396B2) | **SERIES**, thesis was explicitly to "eliminate the need for complex heavy truck transmissions" by running the engine at constant rpm — **and it fitted an off-the-shelf FIVE-SPEED AUTOMATIC to a 150 hp traction motor to move 80,000 lb** | ~35% claimed (real-world reported ~30%). Gen-1: 197 hp John Deere, Marathon 128 kW gen @1,800 rpm, 150 hp motor, 56 PbC cells. Patent spec asserts 50–65% vs a stated 5.5 mpg / ≤38% driveline baseline (**unverified spec assertion — do not calibrate to it**) | [eepower](https://eepower.com/news/series-diesel-electric-hybrid-drive-saves-class-8-truckers-35-in-fuel-costs/) · [patents.google](https://patents.google.com/patent/US8783396) |
| **ReVolt Motors** (2025–26, in fleet service) | SERIES retrofit of Peterbilt 579/379; 9 L Scania genset | **210 kWh**, 670 hp / 3,500 lb-ft (4,745 Nm), ~12 mpg, **~40% fuel-cost reduction**, ~1,200 mi total / ~100 mi battery | [businesswire](https://www.businesswire.com/news/home/20250205294975/en/ReVolt-Motors-Debuts-with-First-Series-Hybrid-Truck-in-the-U.S.-With-About-40-Fuel-Savings) |
| **Edison Motors BDE-Series** | SERIES, "no transmission connecting the engine to the wheels", two driven e-axles | Logging: **280 kWh LFP**, 2×250 kW e-axles, Cat C9, ~670 hp at wheels, **~26,000 lb (mass parity with a comparable diesel rig)**. Semi: Scania genset to 500 kW, 110 kWh LMO, 740 V. Claimed up to 50% (own field data), 70–100% plug-in | [edisonmotors](https://edisonmotors.ca/trucks/semi/) |
| **Wrightspeed Route 1000** (Mack LR) | SERIES, 80 kW Fulcrum microturbine + battery; traction unit "**GTD**" is **a two-speed gearbox with integrated motor** | 730 kW regen; rated 66,000 lb GVW and **40% grades** | [fleetowner](https://www.fleetowner.com/equipment/powertrain/article/21693716/mack-tests-wrightspeed-electric-powertrain-with-turbine-generator) |
| **Oshkosh ProPulse** | SERIES, modular per-axle electric drive | **Up to 20%** fuel economy improvement | [oshkoshdefense](https://oshkoshdefense.com/wp-content/uploads/2019/02/ProPulse_SS_6-13-11.pdf) |
| **Walmart WAVE** (2014, Peterbilt/Capstone/Great Dane) | SERIES with Capstone microturbine REx | **45.5 kWh** Li-polymer (7 Corvus modules); 20% aero reduction vs Peterbilt 386. Never productionised | [greencarcongress](https://www.greencarcongress.com/2014/03/20140328-wave.html) |
| **US7338335B1** (Messano, 2008) | Series diesel-electric **Class 8**, constant-speed genset, modular motor suspension units | Direct prior art against **S1**, not S3 | [patents.google](https://patents.google.com/patent/US7338335B1/en) |
| **Scania + DHL EREV** (Berlin–Hamburg, 100 days) | Series REx on a 40 t BEV | **416 kWh, 230 kW cont./295 kW peak, 120 kW generator, up to 800 km.** Measured over **~22,000 km / 100 days: >90% electric, REx active on only 8.1% of km, 90% CO₂ saving** | [dhl](https://group.dhl.com/en/media-relations/press-releases/2025/100-day-dhl-test-new-scania-e-truck-with-fuel-powered-backup-generator-saved-90-percent-co2-emissions.html) |
| **MAHLE integrated REx module** (IAA Sep-2026) | Series REx module droppable into BEV platforms | **110–130 kW** generator; >800 km (~400 battery + ~400 REx); **replaces ~1/3 of the battery and CUTS VEHICLE WEIGHT BY ~600 kg**; ~80% less CO₂ | [electrive](https://www.electrive.com/2026/08/18/mahle-unveils-range-extender-for-battery-electric-trucks/) |
| Horse Powertrain / Scania timber-truck REx (Dec-2025) | Series REx pilot | Ratings not disclosed | [electriccarsreport](https://electriccarsreport.com/2025/12/horse-powertrain-supplies-range-extender-for-scania-electric-timber-truck-pilot/) |
| Tevva 7.5 t H₂ REx | FC REx | 105 kWh → ~140 mi; with REx ~350 mi | [electrive](https://www.electrive.com/2021/09/28/tevva-presents-7-5-tonne-truck-with-range-extender/) |

## 1.D — Primary-drive e-axle supplier catalogue (the decisive ratio evidence)

**Every Class 8 e-axle sold for primary traction carries multiple ratios.** Suppliers designing clean-sheet in the 2020s, with no legacy constraint, all chose 2 or 3.

| Product | Ratios | Rating | URL |
|---|---|---|---|
| **ZF AxTrax 2 dual** (explicit Class 8 variant) | **THREE-SPEED** | 380 kW cont., **54,800 Nm (40,418 lb-ft) peak**, 2 motors, 2 inverters | [zf](https://www.zf.com/products/en/cv/products_75912.html) |
| ZF AxTrax 2 single | **THREE-SPEED** | 210 kW cont., 25,980 Nm peak | same |
| **Allison eGen Power 100D / 130D** | **TWO-SPEED** integrated | >450 kW cont., 650 kW peak; **130D max 47,000 Nm at the wheels**. Allison's stated rationale, verbatim: *"enabling the high torque required to get heavy loads moving, while also offering superior efficiency at cruise speed"* | [allison IR](https://ir.allisontransmission.com/news-releases/news-release-details/allison-transmission-expands-egen-power-e-axle-portfolio-address) |
| **Cummins/Accelera-Meritor 17Xe** | **single / two / THREE-speed**; multi-speed dual-countershaft is what gets specified for heavy work | 420 kW cont. / 450 kW peak, **44 t GCW** | [cummins](https://www.cummins.com/components/drivetrain-systems/epowertrains/17xe) |
| Cummins-Meritor **14Xe** (the Hypertruck ERX axle) | two-speed as fitted | 150/180/200 kW cont., 250 kW peak — **Class 6-7 duty** | [cummins](https://www.cummins.com/components/drivetrain-systems/epowertrains/14xe) |
| **Dana Spicer Zero-8 / eS9000r** | explicitly **MULTI-SPEED** for Class 7/8; adds an electronically controlled **parking pawl**, "an important feature for vehicles without a traditional transmission" | 4x2 / 6x2 / 6x4 | [dana](https://www.dana.com/newsroom/press-releases/dana-launches-e-axles-for-class-7-and-8-vehicles-expanding-commercially-available-heavy-duty-e-powertrain-offerings/) |
| **Bosch CV eAxle** (Nikola) | motor + power electronics + **transmission** as one inseparable unit | platform 50–300 kW, 1,000–6,000 Nm at module | [wardsauto](https://www.wardsauto.com/internal-combustion-engines/bosch-eaxle-key-to-startup-s-class-8-fuel-cell-truck) |
| **Meritor patents US11054009 / US11460096** | "**Single electric motor drive axle with MULTIPLE RATIOS**"; background states current designs add a multi-speed gearbox between motor and axle **plus** hub reduction to reach the required overall ratio | — | [uspto](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11460096) |
| **Dana WO2017100258A1 / US11001134 / US11639094** | "Distributed drivetrain architectures … with **DUAL RANGE DISCONNECT AXLES**". Background: commercial vehicles uniquely need "a low speed, high torque mode … while also having a high speed, low torque mode" | Priority 2015-12-07 | [patents.google](https://patents.google.com/patent/WO2017100258A1/tr) |

**The only SINGLE-speed Class 8 e-axles in the entire record are pure overlays that never have to launch the vehicle alone**: Range Energy's trailer axle (14,000 Nm) and Revoy's dolly axle (400 kW).

## 1.E — Battery-electric Class 8 (the analogous ratio problem, solved with gears or with more motors)

| Item | Ratios | Quantified | URL / status |
|---|---|---|---|
| **Tesla Semi** | one highway-optimised motor on a **single-speed** reduction permanently engaged + **two torque motors engaged for acceleration and grade** | up to 800 kW (~1,000 hp), three rear motors | [insideevs](https://insideevs.com/news/624742/tesla-semi-beast-tri-motor-system/) — **the strongest supporting prior art for S3's control philosophy**, but it buys the ratio spread with *extra machines*, not gears |
| **Nikola Tre BEV / FCEV** | e-axle | BEV 738 kWh, ~530 km, 645 hp FPT (US to 1,140 hp); FCEV ~70 kg H₂, ~800 km, 2×70 kWh, 2×100 kW FC used *solely* to replenish packs | [prnewswire](https://www.prnewswire.com/news-releases/iaa-2022-nikola-and-iveco-begin-taking-orders-on-the-european-nikola-tre-bev-heavy-duty-truck-with-best-in-class-range-301627087.html) |
| **Mercedes eActros 600 (4-speed), Volvo FH Electric (adapted I-Shift), Scania BEV (2-speed), Nikola Tre (2-speed)** | 2–12 | **[RECALL / UNVERIFIED — lens 4 could not confirm; VERIFY BEFORE USE]** | manufacturer product pages |
| **Chinese NE HDT market** | mixed | ZE heavy trucks **~82,300 (2024) → ~232,000 (2025)**; NE tractor sales +216%, hybrid tractors +213%; tractor-trailers ~38% ZE share | [icct](https://theicct.org/publication/zero-emission-medium-and-heavy-duty-vehicle-market-in-china-a-2025-update-may26/) |

## 1.F — Fixed-ratio / gearbox-deletion art (light vehicle, and the one heavy off-highway filing)

**This is the ground S3's *reasoning* occupies — and it is all light-vehicle or off-highway.**

| Item | Claim substance (paraphrase from search summary; **claim text NOT read**) | Status | URL |
|---|---|---|---|
| **US5343970A** — Severinsky / Paice (filed 1992-09-21, granted 1994) | ICE + traction motor + starter + battery; engine run only above ~30% of max torque; **motor alone at low speed; ENGINE ALONE at steady highway cruise; engine sized for best efficiency at cruise; coupled to the wheels at a FIXED RATIO with no variable-ratio transmission — "no transmission is employed"** | **EXPIRED (~2012-13).** FTO-neutral; the **strongest novelty obstacle** to any concept-level S3 claim | [patents.google](https://patents.google.com/patent/US5343970A/en) |
| Paice continuation family — US6209672, US6338391, US7104347, US7455134, US7520353, US7559388, US7597164, US8214097, US8630761, US9050972, US9463698, US9573585, EP2289750A1, CA2556195C | Setpoint-fraction engine-on logic; SOC arbitration; turbo above sustained max-torque load. **Own disclosure states "a two-speed transmission may further be provided, to further broaden the vehicle's load range."** | Live end of the family; **control-claim exposure** | [patents.google](https://patents.google.com/patent/US9573585B2/en) |
| **US9663101B2** — Audi (granted 2017) | Stated principle is to **reduce or avoid the engine-to-axle clutch because the electric machine starts the vehicle**; control unit operates the machine **exclusively** to launch up to a **threshold speed**, above which the ICE drives | **LIVE. Occupies S3's control law in substance** (light vehicle) | [patents.google](https://patents.google.com/patent/US9663101) |
| **US9005077** (2015) | Method of starting an ICE coupled to a first axle at a **FIXED ENGINE-SPEED-TO-AXLE-SPEED RATIO** via a selectable clutch: **spin/fuel the engine so the speed ratio EXCEEDS the fixed ratio, then engage** | **Closest hit on S3's rev-matched clutch, expressed in S3's own terms** | [uspto](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/9005077) |
| **US8695738** (2014) | Removes the transmission; **constant gear ratio (~10:1 example)** to power the vehicle at highway speed; motor needs no transmission because the inverter gives torque from zero rpm | Light vehicle; occupies the *efficiency rationale* | [uspto](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8695738) |
| **US7470215** (2008) | **Single-speed** off-road vehicle; transmission transfers torque at a **CONSTANT RATIO**; first clutch **automatically engages above a threshold engine speed** | Light off-road, non-hybrid. Proves the bare mechanism is old | [uspto](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7470215) |
| **CN115416473A** — Zhonglian Hengtong (filed 2022-08-09) | Multi-axle hybrid, mechanical + electric drive units driving independently or cooperatively, framed around **eliminating the traditional transmission (无变速箱)** | **Closest non-US neighbour and the ONLY heavy multi-axle filing with explicit gearbox elimination.** Off-highway engineering vehicle. **HIGHEST-PRIORITY RE-CHECK** | [patents.google](https://patents.google.com/patent/CN115416473A/zh) |
| **US12539861 / EP4331885** — LCB International | "Software-defined hybrid powertrain": many-to-many mapping between output-shaft and engine operating points so road-load and engine power control are **essentially independent** | Recent, live; **claim-scope risk against S3's justification** | [patents.google](https://patents.google.com/patent/EP4331885A4/de) |
| **Honda i-MMD / e:HEV** | **[RECALL]** the one production single-fixed-ratio-ICE topology in any vehicle class — engages its lockup ratio only **above ~70 km/h on light load and REVERTS TO SERIES below that** | The fallback S3 does not have | [greencarcongress](https://www.greencarcongress.com/2019/07/20190709-honda.html) |

## 1.G — Axle disconnect and tandem-disconnect art (S3's disconnect is fully occupied — and therefore purchasable)

US11155160 · US20200215907A1 · US9656545 / US20150072826A1 (tandem disconnect with **synchronized overdrive**) · US10857881 (electric drivetrain for a tandem drive axle with axle disconnect clutch) · US8562479B2 / WO2008019759A1 / DE102006045007A1 · US6793034B2 (wheel-end and centre disconnects for an EV/HEV) · US11274735 / US11674575 · US12409727 (differential-disconnect e-axle engaged on SOC) · US11794714 (sensorless driveline-disconnect control and diagnostic). Collectively: **decoupling motors and driveline from the wheels to cut non-conservative friction/churning losses, and disengaging one drive axle during CRUISE specifically to cut friction.** ([representative](https://patents.google.com/patent/US20200215907A1/en))

**Two consequences for WS8:** (i) S3 gets **no novelty** from the disconnect; (ii) more usefully, the spin-drag deletion S3 assumes is a **real, purchasable capability**, not a modelling convenience — but its actuator mass, control complexity and failure modes are documented obligations. **No source in any lens publishes a spin-drag NUMBER for a disconnected Class 8 e-axle.**

## 1.H — Funded programs (SuperTruck I/II and catenary)

| Program | Architecture | Quantified | URL |
|---|---|---|---|
| **Navistar/International SuperTruck II** (Bosch) | **The only ST-II that hybridised the TRACTION path.** HV parallel on an S13 13 L, **multi-speed AMT retained.** Control law as reported: *electric at stops and for higher launch torque, then "as the vehicle reaches a specific speed or load, the system switches from electric to diesel operation"* | **150 kW motor, 30 kWh battery, 16 mpg, 170% freight-efficiency, 55% engine BTE** | [prnewswire](https://www.prnewswire.com/news-releases/navistar-reveals-international-supertruck-ii-results-with-improved-fuel-and-freight-efficiency-goals-for-hybridization-301853836.html) |
| **Daimler/Freightliner SuperTruck II** | Conventional diesel + AMT + 48 V. **DOWNSPED: 1.75:1 AXLE, 950 rpm AT HIGHWAY CRUISE** | 12 mpg; 5.7% vs ST-I; >12% aero | [daimlertruck](https://www.daimlertruck.com/en/newsroom/pressrelease/daimler-truck-is-taking-efficiency-to-the-next-level-the-freightliner-supertruck-ii-52151593) |
| **Volvo SuperTruck II** | Conventional + AMT + **48 V micro-hybrid only, no traction hybridisation** | **134% freight-efficiency (goal 100%), >12 mpg — at 65,000 lb GCVWR, NOT 80,000 lb** | [volvotrucks](https://www.volvotrucks.us/news-and-stories/press-releases/2023/october/volvo-trucks-supertruck-exceeds-freight-efficiency-goals-with-focus-on-aerodynamics-and-advanced-engineering/) |
| **Kenworth/PACCAR SuperTruck 2** | 48 V mild hybrid on MX-11 + **TX-12 12-SPEED AMT** | 12–12.8 mpg; 136% freight-efficiency; **record 55.7% engine BTE vs ~47% production** | [kenworth](https://www.kenworth.com/about-us/news/kenworth-unveils-supertruck-2-at-act-expo/) |
| **Cummins/Peterbilt SuperTruck I** | Conventional + AMT + **ORC WHR** (R245fa; heat from charge air, EGR, coolant, exhaust; ~5 kWe) | **10.7 mpg on US-287 Denton→Vernon TX**; 86% freight-efficiency; 50.2% BTE; **WHR contribution ~3.6 percentage points of BTE** | [dieselnet](https://dieselnet.com/news/2014/03cummins.php) · [osti](https://www.osti.gov/biblio/1375960) |
| **Daimler SuperTruck I** | Rankine WHR | 12.2 mpg; 115% freight-efficiency; 50.2% BTE. **Daimler subsequently deprioritised WHR** [RECALL — verify wording] | [energy.gov](https://www.energy.gov/eere/vehicles/supertruck) |
| **Navistar SuperTruck I** | **NO WHR** — aero, mass, downspeeding only | **~13.0 mpg, the highest of the ST-I cohort** [RECALL — MEDIUM-HIGH confidence, HIGH value if confirmed] | [energy.gov](https://www.energy.gov/eere/vehicles/supertruck) |
| **Detroit SuperTruck** | WHR decomposition | **48.1% BTE = 46.8% engine + 1.3% WHR** → **WHR = 2.7% relative** | [energy.gov](https://www.energy.gov/eere/vehicles/articles/supertruck-program-engine-project-review) |
| **Siemens eHighway / Scania R450 pantograph** (A5/A1/B462) | Catenary overlay on a hybrid truck — tractor keeps its conventional driveline and gearbox | 22 trucks, 3 tracks, >80% claimed OCL efficiency, 90 km/h under wire | [scania](https://www.scania.com/group/en/home/newsroom/news/2020/first-german-e-road-trial-now-fully-operational.html) |

## 1.I — Academic corpus: the line-haul hybrid ceiling

| Paper | Result | URL |
|---|---|---|
| **Gao, LaClair, Smith & Daw (ORNL), TRR 2502, 2015** — measured freeway-dominated cycle, 2010-compliant 15 L | **Parallel and dual-mode 7–8%. SERIES: NO SIGNIFICANT BENEFIT** (internal energy-exchange inefficiency). Hybrid + reduced CdA + Crr → **>15% synergistic** | [sagepub](https://journals.sagepub.com/doi/10.3141/2502-12) · [osti](https://www.osti.gov/biblio/1265853-exploring-fuel-saving-potential-long-haul-truck-hybridization) |
| **Gao, Finney, Daw, LaClair (ORNL), SAE 2014-01-2326** — component energy-loss audit | **Motor+generator loss: 7.4% series vs 1.0% parallel vs 0.8% dual-mode.** Series "absolutely negative" for long-haul; parallel + 50% aux reduction = **5–7%** | [saemobilus](https://saemobilus.sae.org/articles/comparative-study-hybrid-powertrains-fuel-saving-emissions-component-energy-loss-hd-trucks-2014-01-2326) |
| **Karbowski, Delorme, Rousseau (ANL PSAT), SAE 2010-01-1931** | Urban **20–40%** full hybrid, ~10% mild; **highway cycles fall to SINGLE DIGITS**; regional/long-haul non-plug-in **~5–8%**; up to ~8% from recuperating moderate short grades. **Benefit is a function of terrain; a short standard highway cycle misstates it vs a long cruising scenario** | [saemobilus](https://saemobilus.sae.org/papers/modeling-hybridization-a-class-8-line-haul-truck-2010-01-1931) |
| **Moghadasi et al., Energy 320 (2025)** — refines SAE J2807 gradeability **specifically for hybridised HD trucks with DOWNSIZED engines**, benchmarked against 14 steep real highways (US/CA/EU/CN) | P2 with refined sizing: **3.4% to 8.9% lower** equivalent fuel than conventional | [sciencedirect](https://www.sciencedirect.com/science/article/pii/S0360544225007704) |
| Optimised series-parallel vs series HEV, HD truck | Series-parallel beats series by **20.99% on a highway cycle** (⚠ series-relative baseline — cite for direction only, never as an S3-style gain) | [academia](https://www.academia.edu/38259973/Optimized_Design_and_Analysis_of_a_Series_Parallel_Hybrid_Electric_Vehicle_Powertrain_for_a_Heavy_Duty_Truck) |
| **Heliyon 2022 (S2405844022013160)** — 5 transmission designs × thousands of ratio sets for a **heavy-duty ELECTRIC** truck | **3-speed single transmission meets gradeability at lowest energy consumption**; dual e-motor at matched speed up to 5% benefit | [sciencedirect](https://www.sciencedirect.com/science/article/pii/S2405844022013160) |
| **MDPI Energies 15(7) 2407 (2022)** — multi-speed on an e-retrofitted HD truck | Multi-speed **significantly improves traction and gradeability**; effect on powertrain efficiency and energy consumption is **"rather minor"** | [doi](https://doi.org/10.3390/en15072407) |
| **NREL/TP-5600-53502 (2012)** — Coca-Cola, 5 hybrid Kenworth T370 vs 5 conventional M2106, 13 months | **On-road 13.7%** higher FE, 12% lower fuel cost/mi. **Chassis dyno up to 30%**; **up to 32.1% ton-miles/gallon** | [nrel](https://docs.nrel.gov/docs/fy12osti/53502.pdf) |
| **NACFE 6x2 Confidence Report** | **2.5% average fuel saving (range 1.6–4.6%)**; 300–400 lb weight saving; adoption rose only **2% (2003) → 4–5% (2016) BECAUSE OF TRACTION CONCERNS**, manageable only with load shifting, traction control, locking diffs, driver training | [nacfe](https://nacfe.org/research/technology/chassis/6x2-axles/) |
| **US7572201B2 / US20070093341A1** | HD hybrid adding **multiple-ratio gearing (two forward ratios) expressly to improve GRADEABILITY and supply the increased traction-wheel and REVERSE torque required for heavy-duty truck powertrains** | [patents.google](https://patents.google.com/patent/US7572201B2/en) |

## 1.J — Off-highway series (the boundary of the gearbox-free precedent)

Komatsu 930E (first AC-traction haul truck, 1996, 290 t payload) · Cat 795F (AC wheel motors at 2,600 V) · Liebherr T 264 (**40:1 planetary final drive**, 240 t payload); DC bus 1,800–2,100 V. **The precedent exists only where all three hold: engine fully decoupled (series) AND final ratio enormous (40:1) AND cruise speed low.** None holds for a 36.3 t tractor at 85–105 km/h. ([cat](https://www.cat.com/en_US/products/new/equipment/off-highway-trucks/mining-trucks/1000021630.html))

---

# PART 2 — OPEN GROUND

Each stated as a **falsifiable gap**, with the scan bound and what a deeper scan must check. **Absence of evidence from a bounded, egress-crippled scan is weak evidence of absence.** In several cases below the ground is open *because the industry judged it unworkable*, not because nobody looked — that distinction is marked.

### O-1 · The S3 topology at Class 8 is UNOCCUPIED, and cleanly so
**Gap:** No on-highway Class 7/8 vehicle in the commercial, funded-program or patent record couples a combustion engine to a drive axle through a **single fixed ratio with no change-speed gearbox anywhere in the vehicle**, jointly with a **disconnectable e-axle on the other tandem axle owning launch**. Across ~35 products/programs on four continents over 30 years the count is **ZERO**. The two halves are each well occupied but **at different scales**: fixed-ratio/no-gearbox + electric launch exists only on light vehicles (US5343970 expired, Audi US9663101, US8695738, US7470215); heavy-duty tandem split exists only **with the gearbox retained** (BAE US8875819, Dana WO2017100258, EP0812720A1, MAN DE102016006206A1, Hyliion TTR family, Scania WO2019165167A1). **Six independent heavy-vehicle actors over thirty years converged on the choice S3 reverses.**
**Falsifier:** any issued claim or fielded vehicle reciting an ICE driving a road axle at a single fixed ratio, with no change-speed transmission in the vehicle, at GCW ≥ 30 t.
**A deeper scan must check:** CN115416473A claim scope in full (heavy, multi-axle, explicit 无变速箱); the CPC B60K6/48 + B60W20 intersection restricted to CV classifications; Chinese and Korean HDT filings post-2022; the LCB US12539861/EP4331885 claim set.

### O-2 · The AMT-deletion credit has never been claimed by anyone
**Gap:** every overlay product (Hyliion, Revoy, Range, Trailer Dynamics) advertises "no modification to the tractor" as a *feature* and therefore books **zero** mass, cost or efficiency credit from the gearbox. **WS8 will be the first place that credit is quantified — so it must be derived from first principles and cannot be cited to anyone.** See §4.4: WS8's own 325 kg AMT figure is the number at risk.

### O-3 · Cross-axle rev-matched engagement of a fixed-ratio diesel axle at 36.3 t — the most defensible narrow claim S3 could support
**Gap:** the bare rev-match mechanism is taken (US9005077: over-speed past the fixed engine-speed-to-axle-speed ratio, then close the selectable clutch). **What is NOT claimed anywhere:** using the *second axle's* electric machine to hold vehicle speed and torque steady while the *first axle's* fixed-ratio clutch is synchronised and closed under load on a heavy combination. Zero product literature on the engagement transient, driveline torsionals, clutch thermal duty, NVH, or the mis-matched-engagement failure mode into a 36.3 t driveline.
**Counter-signal:** the industry is moving to *reduce* clutch events (Beijing Heavy Duty's i-Zhuimeng sells "no clutch disengagement during gear shifting to reduce wear"), not to add a high-speed one.

### O-4 · Spin drag of a DISCONNECTED Class 8 e-axle — NOT FOUND, and load-bearing
**Gap:** no churning, bearing, seal or residual-magnet drag number for a 400+ kW disconnected axle at 105 km/h exists in any supplier, regulatory or academic source located. S2 and S3 both hinge on "disconnect makes the drag zero". 40 CFR 1037.528 treats **axle spin loss as a first-class road-load term distinct from rolling resistance**, so "deleted" has to be *argued against that standard*, not asserted. This is the member that cost the Vehicle Zero locked path **1.77 pp** in the G1 attribution.
**WS8 must:** derive it from first principles and show it, per the assignment's "both G1 taxes deleted by construction" requirement. `ws8_candidates.py` already charges spin drag only on samples where the disconnect is closed, which makes the deletion auditable — good, but the *magnitude* when closed is still unsourced.

### O-5 · Grade-hold, creep and low-speed manoeuvring with a below-idle diesel — open, and open for a reason
**Gap:** every product either keeps a first gear or sizes the electric path for the whole vehicle. S3 has neither once the pack depletes after a long climb. **Note US7572201B2 names heavy-duty REVERSE drive torque as a reason to ADD ratios** — so this ground is open partly because others judged it unworkable.

### O-6 · e-axle-fault limp for a transmissionless ICE path — a warning, not an opportunity
**Gap:** no patent, paper or product addresses degraded-mode operation of a transmissionless fixed-ratio engine axle. Every overlay in the market limps home on the untouched diesel + AMT — *that is precisely why they are overlays.* S3 inverts the dependency: **a single e-axle fault leaves a vehicle that physically cannot start from rest.** This is a homologation and fleet-pricing question, not just an efficiency one.
**Internal precedent to cite, not resolve:** BASELINE_v3 R22(c) already records the genset-or-pack-fault = tow asymmetry program-wide; S3 adds a *second independent single point of total immobilisation* while **reintroducing the clutch that Gate G1 deleted** (and with it the clutch-fault class that the F-1 deletion had closed). **Escalate per CLAUDE.md rule 8 — do not self-resolve.**

### O-7 · Reverse and park — absent from the S3 description entirely
Deleting the gearbox deletes reverse (must come wholly from the e-axle, dragging the fixed-ratio diesel axle backwards through its clutch) and deletes park lock. Dana explicitly added an electronically controlled parking pawl "for vehicles without a traditional transmission". Neither function appears anywhere in the S3 specification.

### O-8 · Fuel energy per PAYLOAD tonne-km is reported by essentially NOBODY
**Gap:** the entire literature reports L/100 km, mpg or % fuel saving. Revoy's ~10 t dolly, Range's e-trailer, Trailer Dynamics' e-trailer and Hyliion's +800 lb are **never charged against payload**. The single near-analogue is NREL/TP-5600-53502's 32.1% ton-miles/gallon (vocational duty). **Published percentages are therefore systematically OPTIMISTIC relative to WS8's metric of record** — ORNL's 7–8% is fuel-only, before any payload displacement. WS8's numbers should come in *below* the literature's, and that gap is correct, not an error.
**Lawful offsets (the only ones):** 23 U.S.C. 127 — APU up to **400 lb** (many states) / **550 lb** under §127(a)(12) since EPAct 2005; NGV and electric up to **2,000 lb** above the comparable limit, capped at **82,000 lb GVW**. **S4 can likely claim the 2,000 lb line; S3, as a diesel, almost certainly cannot claim more than the APU line.** That asymmetry deserves an explicit row in the candidate table. ([fhwa](https://www.fhwa.dot.gov/fastact/factsheets/trucksizeweightfs.cfm))

### O-9 · Mission-integrated (duty-averaged) WHR reporting
**Gap:** the published HD WHR corpus is overwhelmingly rated-point or peak-BTE. A duty-averaged ORC/ETC figure integrated over a real line-haul grade-and-load distribution is scarce. **WS8's load-dependent formulation is doing something the literature mostly does not** — state that as a contribution rather than defend it as an assumption.

### O-10 · Cold (−10 °C) Class 8 line-haul hybrid data — NOT FOUND anywhere
No quantified −10 °C result was located for battery power fade, e-axle capability, engine warm-up fuel penalty, or the interaction between a cold pack and S3's e-axle-owns-launch dependency. **This matters more for S3 than any other candidate because S3 has no mechanical launch path at all.** Task 5's −10 °C corner should be treated as a potential S3 **kill condition** and exported as an enumerated governing case (R14), not folded into an average.

### O-11 · e-axle stall and creep THERMAL ratings at Class 8 GCW
Vendors publish peak and continuous *power*; almost nothing on near-zero-speed torque duty and its time limits. Both S2 and S3 depend on this; **S3 depends on it absolutely.** This is an unquantified *risk* in the trial, not merely an unverified number.

### O-12 · Honest mass-boundary conventions for e-axle comparison
Vendor e-axle masses bundle housing, wheel ends and brakes; `ws8_params.MassLedger.m_drive_axle_housings = 620.0` charges those separately. **Comparing a vendor e-axle mass directly against WS8's motor + inverter + reduction rows would double-count ~600 kg.** A stated boundary convention in `REPORT_WS8.md` is a genuine contribution and protects the ledger at the next review.

### O-13 · Two-speed diesel axle at Class 8 — the repair S3's own failure points at
**Gap, and it appears genuinely unoccupied.** Every decisive contradiction in Part 3 traces to one number: the ~5.4:1 gap between the launch-capable and cruise-capable ratio. Two ratios spanning ~45–105 km/h keep the engine above its rpm floor on **both** the mandated 3% sustained and 6% mountain grades, close C-1/C-2, restore compression-brake authority on descent, and collapse the pack requirement by orders of magnitude — for perhaps **+60–90 kg** over the 145 kg fixed box (`ML.m_fixed_ratio_box`). Corroborating pattern: this is exactly the ratio count BEV Class 8 trucks settled on facing an *easier* version of the same problem. **Not refuted by anything in this sweep.**

### O-14 · A small clutched generator on axle A (a P1) — the minimal repair to S3's premise
Adds a series path **exactly and only where S3 is structurally missing one** (below the coupling floor), without carrying a full genset's mass at cruise. Occupies the gap between S1 and S3, and is the member every successful real-world analogue has (Honda i-MMD, locomotives, every series product in §1.C).

### O-15 · Explicit NEGATIVE search results (these define the open ground)
- **No** single-fixed-ratio ENGINE-axle claim from Eaton, Cummins, Volvo, Scania, ZF, Bosch, Daimler/Mercedes, PACCAR, Allison, BorgWarner, Nikola or Tesla. All substantive hits from those names were multi-ratio, P2/P3 driveline-mounted, or e-axle-only.
- **No** claim phrased "wherein the vehicle does not include a change-speed transmission" (or paraphrase) on a heavy vehicle.
- German sweep (*Verbrennungsmotor / feste Übersetzung / ohne Schaltgetriebe / Nutzfahrzeug / Anfahren*): only gearbox-retaining architectures; the one find was EP0492152A1's 1991 admission.
- **No** Hyliion filing touches the transmission at all.
- **No** academic or patent document proposes single-fixed-ratio diesel drive on a line-haul tractor.
- **Prior transmissionless heavy-truck ATTEMPTS: the targeted query was never run** (budget exhausted in lens 4). ⚠ **Do NOT report "tried and failed" as substantiated.** The refutation in Part 3 rests on physics and regulation, not on documented precedent. The nearest real-world analogue needs no citation and should be stated plainly: *a conventional Class 8 truck in direct-drive top gear IS a single-fixed-ratio diesel axle at i ≈ 2.5:1, and what happens to a loaded 36 t combination left in top gear on a grade is not in dispute.*

**What a deeper scan would need (priority order):**
1. `patents.google.com` / Espacenet full claim text for: **CN115416473A**, US8875819B2, Dana WO2017100258A1, US9005077, US9663101B2, US12539861/EP4331885, the live Paice continuations. (FTO and novelty both currently unsupported.)
2. **Kharrazi & Karlsson (VTI), performance-based standards for vehicle combinations** — [diva-portal PDF](https://www.diva-portal.org/smash/get/diva2:867038/FULLTEXT01.pdf). It states the **assumed tyre-road friction coefficient** behind PBS startability/gradeability, which would turn contradiction C-4 from *derived-decisive* to *cited-decisive*. **Highest-value unread document in the entire sweep.**
3. **UN R13 Annex 4** Type-II (6 km, 6% down, 30 km/h, laden, endurance braking) and Type-IIA (7%) text, to firm up C-8.
4. NHTSA/SwRI **DD15 14.8 L base map + 12.3 L delta map** Excel files (§4.3) — retrieve and SHA-pin before any S0 run.
5. [truckinginfo 6X4HE drive review](https://www.truckinginfo.com/316197/driving-hyliions-6x4he-hybrid-electric-system) — likeliest source of a direct engineer statement on **why the AMT was retained**. The assignment asked for this; it could not be delivered. **UNRESOLVED.**
6. Eaton Endurant HD dry weight (§4.4) — decides S3's gearbox-deletion credit.

---

# PART 3 — CONTRADICTIONS TO S3

## 3.0 · FIRST: the lenses disagree with each other and with the repo on the fixed ratio. Resolve this before weighting anything below.

Four lenses independently derived a coupling-speed floor, each from a *different assumed ratio*, and **none of them used the ratio the WS8 code actually implements.** [DERIVED — this synthesis, repo-checked against `ws8_candidates.py:1106` and `ws8_params.py`]

| Source | Assumed / actual ratio | v at 1,000 rpm (coupling floor) | rpm at 85 / 105 km/h |
|---|---|---|---|
| Lens 3 (academic) | 1.75:1 (Daimler ST-II axle) → 2.4:1 | 58.3 – 83.3 km/h | — |
| Lens 4 (adversarial) | **2.381** (1,200 rpm @ 95 km/h) | **79.2 km/h** (63.3 at idle 800) | 1,074 / 1,326 |
| Lens 5 (WHR/scaling) | **2.618** (1,250 rpm @ 90 km/h) | **72.0 km/h** | 1,181 / 1,458 |
| **`ws8_candidates.py` AS IMPLEMENTED** | **`RATIO_A = 3.40`**, `RPM_COUPLE_MIN = 1000`, `RPM_MAX = 2100` | **55.4 km/h** | **1,533 / 1,894** |

**This is the fixed-ratio trade expressed in one table, and it is the single most useful synthesis result in this document:**
- At the lenses' downsped ratios (2.38–2.62) the engine sits near its BSFC island (~1,300 rpm) at cruise **but the coupling floor is 72–79 km/h.**
- At WS8's implemented 3.40 the floor drops to a much more workable **55.4 km/h**, **but the engine now runs 1,533–1,894 rpm across the whole 85–105 km/h corridor — i.e. ABOVE the island for the entire cruise duty**, forfeiting most of the "engine sits at its best point" premise that justifies deleting the gearbox in the first place.

**You can have the island or you can have the floor. You cannot have both with one ratio.** The lenses' contradictions C-1/C-2 must be re-read against the ratio actually swept in `run_ws8.py`, and the sweep must report the *pair* (island error, coupling floor) at every ratio, not just fuel.

**The window is provably empty.** [DERIVED — this synthesis; K = 5.3052 rpm per (km/h) per unit ratio at r_dyn = 0.50 m]
- Constraint A (over-speed): 105 km/h ≤ 2,100 rpm ⟹ **i ≤ 3.770**
- Constraint B (6% mountain stays coupled, 350 kW engine settling at 49.5 km/h): 49.5 km/h ≥ 1,000 rpm ⟹ **i ≥ 3.808**
- **Intersection is EMPTY** — narrowly (by 1.0%) for the 13 L engine.
- With the **S3 downsized 11 L** (`ENG-11L`, 265 kW, settling at 37.7 km/h on 6%): **i ≥ 5.000** vs i ≤ 3.770. **Empty by 33%.**
- Relaxing the lugging limit to 900 rpm: 13 L needs i ≥ 3.427 vs i ≤ 3.770 — **a window opens** (3.43–3.77); the 11 L still needs i ≥ 4.500 and **stays empty**.

⟹ **The whole S3 verdict turns on `RPM_COUPLE_MIN`, which is tagged `[WS8-PROV]` at 1,000 rpm and is not cited to anything.** Make it an enumerated R14 case (900 / 1,000 / 1,100 rpm), and report the ratio window as a feasibility interval, not a point.

---

## 3.1 · DECISIVE

### C-1 · FIXED-RATIO SPEED FLOOR: the diesel is mechanically dead on the mandated 6% mountain segment
`[DERIVED — lenses 3, 4, 5; repo-checked here]`
On a 6% grade at 36,300 kg the grade force alone is **21,370 N**; holding 90 km/h would need **633.5 kW at the wheel**. Actual settle speeds: **49.5 km/h with a 350 kW engine, 37.7 km/h with the S3 265 kW `ENG-11L`.** The coupling floor at every ratio that respects the 2,100 rpm ceiling is **≥ 50.5 km/h**. The clutch must therefore be open for the entire climb. **`run_ws8.py:134` confirms S3 has no genset**, so there is no electrical path either: the e-axle and buffer pack must supply the whole climb.
**Energy required from the bus for one climb** (independent derivations, two lenses, consistent): 10 km/600 m rise at 45–50 km/h ⟹ **66.1–73.9 kWh**; 14 km ⟹ **103.4 kWh**; 20 km/1,200 m ⟹ **133–148 kWh**. WS8's implemented S3 pack is **`PACK_KWH = 60.0`** (`ws8_candidates.py:1109`) — short by **1.1× to 2.5×** on a single climb, before any SOC floor (`SOC_FLOOR = 0.15`, so usable ≈ 48 kWh at best ⟹ short by **1.4× to 3.1×**).
**Strength: DECISIVE.** Not sensitive to the ratio disagreement in §3.0 — it holds at 2.381, 2.618, 3.40, 3.73 and 4.10.
[assignment ASSIGNMENT.md; `ws8_candidates.py`; corroborated by [sciencedirect S0360544225007704](https://www.sciencedirect.com/science/article/pii/S0360544225007704)]

### C-2 · The same drop-out on the ORDINARY sustained 2–3% grade — ⚠ LENSES DISAGREE, AND THE DISAGREEMENT MATTERS
`[DERIVED — lens 5 claims decisive; this synthesis DOWNGRADES it to ratio-conditional]`
Lens 5 computed a 3%-grade settle speed of **65.1 km/h** with the 265 kW engine against a 72.0 km/h floor at i = 2.618, and called this decisive. **At WS8's implemented i = 3.40 the floor is 55.4 km/h and the 3% grade stays coupled.** The 350 kW engine holds **82.4 km/h** on 3%, which is coupled at any i ≥ 2.288.
**Resolution:** this is **NOT** a decisive contradiction at the implemented ratio; it is decisive only for i ≥ 2.895 (11 L) or i ≥ 2.288 (13 L) *combined with* a 1,000 rpm lugging limit. **State it as a conditional in `REPORT_WS8.md`, with the ratio and the rpm floor named — do not average the two lens verdicts.**
**Strength: CONDITIONAL (decisive in part of the ratio sweep, dissolved in the rest).** Enumerate per R14.

### C-3 · LUGGING RUNAWAY: no stable equilibrium on grade, because there is nothing to downshift to
`[DERIVED — lens 4, /tmp/.../s3_refute2.py]`
At i = 2.381 with a plausible downsized ~9 L curve (1,600 N·m plateau 1,000–1,400 rpm, off-boost collapse below 1,000, η = 0.95), available wheel power vs road speed: **95 km/h → 191 kW; 85 → 171; 80 → 161; 75 → 117; 70 → 74.7; 65 → 40.2; 60 → 14.2; ≤55 → 0.** Demand on a 2% grade is 300 kW at 95 km/h falling only to 150 kW at 55 km/h; on 6% it is 675 kW → 367 kW. **Supply falls off a cliff (P = T(n)·n with n ∝ road speed and T itself collapsing off-boost) while demand is nearly flat because gravity dominates. The curves never re-cross.** Positive feedback to a dead stop. This also demolishes the obvious rescue ("let it slow down on grades"): **S0 slows and downshifts; S3 slows and DISCONNECTS.**
**Strength: DECISIVE.**
Industry corroboration, verbatim: *"a truck engine is only able to muster enough torque in a narrow rev range of 300-400 rpm"*; *"Large trucks can increment their speeds by only a small amount in any given gear, making it necessary to employ large numbers of gears to cover the full speed range."* [drivingtests.co.nz](https://www.drivingtests.co.nz/resources/why-do-trucks-have-a-lot-of-gears/)

### C-4 · ADHESION at the regulatory launch: **μ = 0.587 required from ONE axle**
`[Regulation text: SEARCH-SUMMARY VERBATIM. Arithmetic: DERIVED — lens 4]`
Commission Regulation (EU) No 1230/2012, verbatim as extracted: *"vehicles designed to tow a trailer shall be capable of starting five times within five minutes at an up-hill gradient of at least 12%. For performing this test, the towing vehicle and the trailer shall be laden so as to equal the technically permissible maximum laden mass of the combination."*
At 36,300 kg: grade force **42.43 kN** + rolling **1.94 kN** = **44.37 kN** required = **22.19 kN·m of wheel torque**. At the US legal split (5,443 / 15,422 / 15,435 kg — matching `ws8_params.Vehicle`), the drive tandem is 42.5% of GCW and **one axle is 21.2%**. Therefore **μ_req = 0.293 for a conventional tandem** (which is exactly why real trucks pass) **vs 0.587 for S3's single launching axle.** Longitudinal load transfer on the 12% grade (tractor 20,860 kg, 4.0 m wheelbase, CG 1.2 m: 7,314 N rearward) eases it only to **0.535** single / 0.280 tandem.
Against `ws8_params.Adhesion`: **μ_dry = 0.70, μ_wet = 0.45, μ_snow = 0.20, μ_ice = 0.10.** S3's requirement of 0.535–0.587 is **beyond wet asphalt entirely and marginal on dry** — against WS8's own ruled case set.
**Strength: DECISIVE.** ⚠ **Scope caveat (lens 4, honestly flagged): this is an EU/UNECE homologation gate. There is no equivalent US federal standard** — no FMVSS mandates gradeability or startability; the US handles it through AASHTO design-truck guidance (~120 kg/kW; S3 at 265 kW/36,300 kg = **202 kg/kW**) and state minimum-speed and chain laws. So the *regulatory framing* is market-specific; the *physics* is not.
[eur-lex](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32012R1230)

### C-5 · SINGLE-SPEED e-axle at 36.3 t: the torque is not there, and the industry says so in its own words
`[SEARCH-SUMMARY + DERIVED]`
Required at the wheel for a 20% grade at 36.3 t (r = 0.50 m): **~35,600–36,600 N·m** plus rolling. Against that:

| Product | Ratios | Wheel torque |
|---|---|---|
| Range RA-01 (best-documented **single-speed** Class 8 e-axle) | 1 | **14,000 Nm** — *fails by 2.6×* |
| Allison eGen Power 130D | 2 | 47,000 Nm — passes |
| ZF AxTrax 2 dual | **3** | 54,800 Nm — passes |

Allison states S3's exact design tension and resolves it with a gearbox: *"enabling the high torque required to get heavy loads moving, while also offering superior efficiency at cruise speed."* Independent trade analysis: for heavy vehicles that must both start on grade and hold highway speed, *"a single-speed setup would require an enormous motor"*; early direct-drive adopters *"require excessively large and heavy motors that still cannot perform to the same level as diesel trucks"*; multi-speed delivers **10–15% better drivetrain efficiency**, with a worked example replacing a **1,200 kW single-speed** motor with an **800 kW motor + multi-speed and BETTER gradeability**.
**Compounding, from WS8's own code:** `EDRIVE_RATIO = 12.0` with the comment that it *"puts the machine at ~7,073 rpm — under the limit with ~2% margin. A numerically higher ratio would buy startability but would over-speed WS2's rotor."* **S3's launch ratio is pinned by a borrowed component constraint (WS2's 7,200 rpm rotor limit), not by the launch requirement.** That is an admission on the record.
**Strength: DECISIVE.** [zf](https://www.zf.com/products/en/cv/products_75912.html) · [truckinginfo](https://www.truckinginfo.com/news/can-multi-speed-ev-transmissions-can-solve-heavy-truckings-biggest-electric-vehicle-problems)

### C-6 · Deleting the ICE transmission has been demonstrated FOUR times, and gearing came straight back on the electric side every time
`[SEARCH-SUMMARY]`
1. **Hyliion Hypertruck ERX** — generator mounted *literally where the transmission had been*, then **two Meritor 14Xe axles EACH with a TWO-SPEED gearbox**.
2. **ePower Engine Systems** — whose stated thesis was "eliminating the need for complex heavy truck transmissions" — fitted an off-the-shelf **FIVE-SPEED AUTOMATIC** to a 150 hp traction motor to move 80,000 lb.
3. **Wrightspeed Route 1000** — traction unit is "a **two-speed gearbox** with integrated motor".
4. **Off-highway series haul trucks** — gearbox-free only via a **40:1 planetary final drive** at low road speeds.
**Nobody who removed the ICE gearbox ended up with no gearbox.** S3 asserts "no gearbox ANYWHERE" on a vehicle with an *additional* fixed-ratio diesel constraint that none of these four carried.
**Strength: DECISIVE.** [fleetequipmentmag](https://www.fleetequipmentmag.com/heavy-duty-hyliion-hybrid-powertrain/)

### C-7 · NO SERIES PATH ⟹ deadlock and ZERO limp capability
`[DERIVED — lens 4; repo-confirmed]`
S3's engine is coupled to axle A alone; there is **no generator** (`run_ws8.py:134`). Fuel can reach the battery only through the road, which requires the clutch closed, which requires exceeding the coupling floor (55–79 km/h depending on ratio). Three consequences follow **by construction**:
- **(i)** every launch, every urban/regional km, every work zone and traffic slowdown is **battery-only**;
- **(ii)** **DEADLOCK** — if the pack depletes at low speed the truck cannot move and cannot recharge, because recharging requires exceeding the floor, which requires propulsion, which requires the pack. A genuine absorbing state with no exit but a tow;
- **(iii)** Task 5 requires "e-axle-fault limp capability": with axle B faulted, **S3's limp capability is ZERO** — the only device with low-speed authority is the failed one.
**Strength: DECISIVE.** Strictly worse than BASELINE_v3 R22(c)'s recorded genset-or-pack-fault = tow asymmetry, and it **reintroduces the clutch-fault class the G1 F-1 deletion had closed.** → escalate, do not self-resolve.

### C-8 · Series double-conversion tax reappears wherever the fixed ratio is out of band
`[SEARCH-SUMMARY + DERIVED]`
ORNL's component audit: **motor+generator energy loss 7.4% (series) vs 1.0% (parallel) vs 0.8% (dual-mode)**; series "absolutely negative" for long-haul, "not attractive for Class 8 trucks, especially at high vehicle speeds". The companion TRR 2502 study: parallel/dual-mode **7–8%**, series **no significant benefit**. **S3 is a parallel architecture only in the speed window where its diesel axle is actually connected.** Below that window all tractive power routes through the battery and e-axle — a series path **with an added battery round-trip loss on top of the 7.4%.**
**WS8 must therefore compute S3's connected-fraction over each cycle and charge the series penalty on the remainder.** Assuming parallel-path efficiency across the whole corridor overstates S3.
**Strength: DECISIVE (for the mechanism); the magnitude is ratio-conditional.** [saemobilus](https://saemobilus.sae.org/articles/comparative-study-hybrid-powertrains-fuel-saving-emissions-component-energy-loss-hd-trucks-2014-01-2326)

### C-9 · Dana states the class requirement and answers it with MORE ratios, not fewer
`[SEARCH-SUMMARY]`
Dana Heavy Vehicle's own commercial-vehicle hybrid family background: commercial vehicles have the unique demand of needing *"a low speed, high torque mode of operation while also having a high speed, low torque mode of operation"* — and Dana's answer, in the patent title, is **DUAL RANGE DISCONNECT AXLES.** The largest heavy-axle supplier, 2015 priority, states two operating regimes as a *requirement of the vehicle class* and solves it by **adding ratios to the axles**.
**Strength: DECISIVE.** [patents.google](https://patents.google.com/patent/WO2017100258A1/tr)

### C-10 · The fixed-ratio idea's own authors added a second ratio — on a vehicle 1/24th of S3's mass
`[SEARCH-SUMMARY]`
The Paice/Severinsky family — the disclosure that *originated* "engine at a fixed ratio, no variable-ratio transmission, motor for low speed, engine for cruise" — provides in its own continuations that *"a two-speed transmission may further be provided, **to further broaden the vehicle's load range**"*, and separately adds a turbocharger for sustained above-max-torque load. **One ratio was found insufficient for load range on a ~1.5 t passenger car. S3 makes the same bet at 36,300 kg on a duty that includes a sustained 6% grade.**
**Strength: DECISIVE.** [patents.google](https://patents.google.com/patent/US20030217876)

### C-11 · CLUTCH LAUNCH ENERGY — a pincer with no third reading
`[DERIVED — lens 4]`
Slipping the fixed-ratio clutch from rest to the ratio's synchronous speed dissipates ≈ the vehicle's KE at that speed. At 36,300 kg: sync 95 km/h → **12.639 MJ**; 80 → 8.963; 60 → 5.042; 40 → 2.241; 20 → 0.560; 15 → 0.315 MJ. A heavy-truck dry clutch handles **~0.1–0.3 MJ per engagement**; a cooled wet multi-plate ~1–2 MJ. **So a 0.3 MJ budget caps synchronous speed at 14.6 km/h, requiring i = 12.9:1 — which puts 105 km/h at 7,174 rpm.** Launch-capable ÷ cruise-capable ratio = **5.4:1. That number IS the gearbox.**
**The pincer:** if "rev-matched" means near-zero slip (which is what `ML.m_revmatch_clutch = 105.0` assumes — *"sized to SYNC only, no launch slip duty"*), the thermal objection **dissolves entirely** — and hard-confirms C-1: a zero-slip clutch can only close above the floor, so the diesel is definitionally a highway-only device with **no low-speed authority whatsoever**. Either reading kills something.
**Strength: DECISIVE (as a disjunction). WS8's implementation takes the second horn, which is the correct bookkeeping — and which makes C-1 and C-7 unavoidable.**

## 3.2 · STRONG

### C-12 · Sustained 2–3% grades demand 40–85 kWh per event — S3 silently becomes S4
`[DERIVED — lens 4]` Holding speed at 36,300 kg: **2% @ 95 km/h = 300.2 kW at the wheel; 3% @ 90 km/h = 367.5 kW.** A cruise-plus-margin engine delivers ~112 kW at the wheel. Deficits and pack draw: **2%/20 km → 39.6 kWh; 2%/40 km → 79.2 kWh; 3%/15 km → 42.6 kWh; 3%/30 km → 85.1 kWh.** Against `PACK_KWH = 60.0` with `SOC_FLOOR = 0.15` (usable ≈ 48 kWh), a single 30 km 3% grade drains the pack. **Sizing the pack to cover it turns S3 into a range-extended BEV with a highway-only diesel — which is S4, an existing separate candidate — and it must then carry S4's pack mass against the payload denominator.** S3 does not survive as a *distinct* architecture; it collapses into its neighbour. [assignment Task 1(a) mandates "sustained 2-3%"]

### C-13 · "Downsized" and "fixed low-rpm ratio" are mutually contradictory
`[DERIVED — lens 4]` P = T·ω. The fixed ratio pins engine speed, so available power is `T_max(n_pinned)·ω` and **the engine cannot rev up to make more, because revving up means going faster, which needs more power.** From BMEP (T = BMEP·V_d/4π) at 1,200 rpm **at full load, zero reserve**: 9 L at 20/22/24 bar → 180/198/216 kW; 11 L → 220/242/264 kW; 13 L → 260/286/312 kW. A 2% grade at 95 km/h asks **300 kW at the wheel**. The deficit is ~180 kW with **no rpm headroom anywhere to find it.** *Small AND pinned low AND with margin* are not simultaneously satisfiable; an AMT resolves exactly this by letting a small engine reach rated speed in a lower gear.
⚠ Note this bites hardest at the lenses' downsped ratios; at WS8's i = 3.40 the corridor rpm is 1,533–1,894, which relieves the power ceiling **and forfeits the BSFC-island premise instead** (see §3.0).

### C-14 · DESCENT: zero engine-brake authority for the whole mandated 6% descent
`[DERIVED — lens 4; regulation clause UNVERIFIED]` Task 1(a) mandates "one 6% mountain segment with full descent." Retardation required at 36,300 kg: **6% down @ 30 km/h = 159.5 kW to absorb; 7% @ 30 km/h = 189.0 kW; 6% @ 60 km/h = 307.6 kW.** Total PE over a 6 km 6% descent = **35.5 kWh.** But at those speeds the diesel sits at **379 rpm (30 km/h) / 758 rpm (60 km/h) at i = 2.381** — clutch necessarily open, **engine/compression brake contributes exactly 0 kW.** In S0 this is precisely what the gearbox buys: downshift to hold high rpm, because compression-brake retarding power scales with engine speed (a 13 L gives 300–400 kW at 2,100 rpm; `ws8_candidates.py` charges S3 `p_engine_brake_kw = 240.0` for an 11 L, which is only available *when coupled*). S3 forfeits it and must absorb 160–310 kW on the e-axle (`RESISTOR_KW = 200.0`) plus friction brakes.
⚠ At WS8's i = 3.40 the floor is 55.4 km/h, so a 60 km/h descent **is** coupled and this softens materially — **another item that must be re-derived at the implemented ratio.**
**Homologation claim UNVERIFIED:** UN R13 Annex 4 Type-II (laden, 6 km, 6% down, 30 km/h, endurance braking) and Type-IIA (7%) — `unece.org` was egress-blocked. **Physics stands regardless; the regulation citation does not.**

### C-15 · e-axle THERMAL duty: 22.2 kN·m five times in five minutes at near-stall
`[Regulation SEARCH-SUMMARY; duty DERIVED — lens 4]` The 12% test demands 5 starts in 5 minutes at combination TPMLM, all assigned to axle B: **22.19 kN·m from ONE axle**, at the top of a single heavy e-axle's *peak* rating. Duty: to 10 km/h in 15 s ⟹ ~123 kW at very low speed and **75 s at near-peak torque within the 300 s test = 25% duty**; to 15 km/h in 20 s ⟹ ~185 kW and **33% duty**. **Peak e-machine ratings are 30–60-SECOND ratings, not 25–33% duty ratings**, and near-stall is the machine's worst thermal point (max current, min back-EMF, min rotor cooling, no speed-dependent convection).
**Internal precedent — this programme has already found this limit binding:** BASELINE_v3 R21 sets the crawl continuous basis at **311.7 Arms (×0.685)** and raises R13's continuous-limit floor to **80.1 W/K**; WS7 carries a crawl heat-run at **G_ws ≥ 90 W/K**. S3 asks one e-axle to do a *harder* version of a duty already known to be limiting.

### C-16 · Single-driven-axle traction is an adoption-limiting problem with 20 years of fleet evidence
`[SEARCH-SUMMARY + DERIVED]` NACFE 6x2: uptake crept only **2% (2003) → 4–5% (2016)** because of traction, manageable only with load shifting, traction control, locking diffs and driver training. **S3 is worse placed than a 6x2 in one specific respect: a 6x2's unpowered axle can be a LIFTABLE pusher whose load is actively transferred onto the drive axle; S3's second tandem axle carries an e-machine and cannot be lifted**, so the classic mitigation is unavailable.
μ required from ONE driven axle `[DERIVED]`: 2% @ 95 km/h → **0.150**; 3% @ 90 km/h → **0.194**; 3% @ 60 km/h → 0.179; **6% @ 40–45 km/h → 0.314–0.315**; 6% @ 60 km/h → 0.321. Against `ADH`: packed snow **μ = 0.20** ⟹ the 3% cruise grade is **AT the limit with no margin** and 6% **fails outright**; ice (0.10) fails even the 2% grade. Full tandem passes packed snow comfortably (0.157–0.166).
**Offsetting credit S3 may legitimately claim while disconnected: NACFE's 2–2.5% (range 1.6–4.6%) fuel and 300–400 lb weight saving from undriving one axle.**
Also: **Hyliion filed specifically on predictive traction assistance (US20240034298A1)** — a company operating split-drive Class 8 tractors in the field found single-axle slip enough of a live problem to patent a countermeasure.

### C-17 · The literature ceiling is 5–8%, and WS8's 3% gate sits inside its scatter
`[SEARCH-SUMMARY — four independent convergent sources]` ORNL TRR 2502: parallel/dual-mode **7–8%**, series none. Argonne PSAT SAE 2010-01-1931: highway single digits, regional/long-haul **~5–8%**. Energy 320 (2025), P2 refined sizing on 14 steep real highways: **3.4–8.9%**. Volvo's own long-haul Concept Truck with I-See topography look-ahead: **hybrid path alone 5–10%**, by shutting the engine off up to 30% of driving time (the famous 30% is the whole vehicle including aero). Foton production data resolves it by terrain: **26% mountain / 16% highway / 10% overall.**
**WS8's ≥3% advance gate sits INSIDE the scatter of the published literature**, and S3 must clear it *while carrying an e-axle, a 60 kWh pack, a 145 kg fixed box, a 105 kg rev-match clutch and its actuation against payload*.

### C-18 · Multi-speed's published value is TRACTION AND GRADEABILITY — exactly what S3 gives up
`[SEARCH-SUMMARY]` MDPI Energies 15(7) 2407: multi-speed on an e-retrofit HD truck **"significantly improved traction performance and gradeability"** while the effect on powertrain efficiency and energy consumption was **"rather minor."** Heliyon 2022 across 5 designs and thousands of ratio sets: a **3-speed** meets gradeability at lowest energy — **on a BEV, the case where single-speed should win if it ever wins.**
**Reframing that WS8 should adopt:** S3's premise is defensible exactly where it is cheapest (steady cruise, where deleting ratios costs little) and attacks exactly the function ratios actually perform. ⟹ **Be suspicious of any S3 result showing a large cruise gain — the mechanism for one is absent.** Task 5's "fixed-ratio grade-hold floor" and "diesel-axle-only adhesion" are **not sensitivities; they are the main event, and should be reported as governing cases.**

### C-19 · Every shipping heavy e-overlay deliberately kept the gearbox — including the one that most wanted not to
`[SEARCH-SUMMARY]` Hyliion 6X4HE's *entire commercial proposition* is that the base truck (engine, clutch, AMT, both drive axles) is untouched, which is why it can be retrofitted to in-service trucks. Its stated function, verbatim: *"electric power is applied when necessary to keep diesel engines at their most efficient RPM delivering hybrid fuel savings"* — **the job S3 asks a bare fixed ratio to do WITHOUT a gearbox, done here WITH one still in place.** Same pattern: Revoy (tractor untouched), Range, Trailer Dynamics, ZF TraXon Hybrid and Eaton–Cummins P2 (machine **upstream** of a retained 12-speed so the gearbox multiplies it).
⚠ **HONEST LIMIT, flagged by two lenses:** no direct engineer statement on *why* the AMT was retained could be obtained — the drive review that would most likely contain one was egress-blocked. **UNRESOLVED.** The ZF/Eaton P2 claims are **[RECALL/UNVERIFIED]**.

### C-20 · The AMT-deletion credit is not where the savings are
`[SEARCH-SUMMARY]` Hyliion's published accounting for the 6X4HE is **30% total = 15% hybrid drive axle + 12% APU + 3% aero** — i.e. the e-axle overlay on a **completely unmodified diesel-plus-AMT driveline** already delivers the drive-axle share, with the gearbox left in. **S3 must show that removing the transmission adds enough on top of a plain overlay to justify losing launch capability, grade hold, reverse, park and limp-home.** Nothing in the record suggests it does.

## 3.3 · SUGGESTIVE

### C-21 · Mass ledger will not close positive on the AMT deletion
`[SEARCH-SUMMARY + RECALL]` No commercial data point supports a net mass **credit** for this class of change. Hyliion's far simpler overlay cost **+363 kg** with the AMT untouched; Revoy's dolly is **~10 t**; MAHLE's opposite trade (swap 1/3 of a BEV pack for a 110–130 kW genset) returns **~600 kg**. Against that, deleting the AMT forces mass back in: a launch-capable e-axle at 36.3 t (17Xe class, **420–450 kW**, vs a 150–250 kW Class 6-7 unit), a bigger buffer, a rev-matched clutch and actuation, plus park/hold and reverse functions the gearbox provided. **See §4.4 — WS8 may be over-crediting the deletion by 45–115 kg.**

### C-22 · DISSOLVED: Directive 97/27/EC "≥25% of M on driving axles" is NOT a blocker
`[Lens 4, reported as dissolving]` Verbatim: *"The mass corresponding to the load on the driving axle or the sum of the masses corresponding to the loads on the driving axles must be at least 25 % of M."* Against **combination** mass one driven axle gives 7,710/36,300 = **21.2%** (fails); against the **tractor's own M** (20,860 kg) it gives **37.0%** (passes comfortably; tandem 73.9%). The reference mass could not be confirmed (EUR-Lex blocked). **Do not lead with this. The adhesion constraint that actually bites is C-4 (physics), which does not depend on it.**

### C-23 · PARTIALLY DISSOLVED: single-axle drive at cruise on flat/mild grades is FINE
`[Lens 4, reported honestly]` One driven axle needs **μ = 0.150** at 2%/95 km/h and **0.194** at 3%/90 km/h — comfortably inside wet asphalt (0.45) and far inside dry (0.70). **Any refutation claiming one driven axle "cannot hold a loaded combination" in general is overreaching and should be withdrawn.** The adhesion problem is real in exactly two places: the 12% regulatory launch (C-4) and low-friction surfaces on grade (C-16).

### C-24 · Commercial-outcome evidence (weak, and about economics not physics)
`[RECALL/UNVERIFIED]` Hyliion wound down its powertrain business (6X4HE / Hypertruck ERX) ~2024 to pivot to KARNO. Walmart WAVE never productionised. ePower and Wrightspeed did not scale. Hypertruck ERX was cancelled for **complexity, cost and CARB engine recertification — not for physics.** Relevant to WS8's advance/kill *economics*, not to the architecture question. Verify dates and claim history before quoting.

---

# PART 4 — CALIBRATION AND MASS DATA

Everything WS8's physics model can actually use. **Every row is PROVISIONAL-CITED per E13.** Disagreements flagged inline.

## 4.1 · Class 8 line-haul fuel reference bands (Task 2 calibration)

| Quantity | Value | Basis / payload / cycle | Class | URL |
|---|---|---|---|---|
| EU **typical** tractor-trailer | **32.6 L/100 km** | VECTO regulatory **Long Haul** cycle | (1) | [icct](https://theicct.org/publication/fuel-consumption-testing-of-tractor-trailers-in-the-european-union-and-the-united-states/) |
| EU **best-in-class** | **29.9 L/100 km** (typical is 9% higher) | same | (1) | same |
| EU Long Haul at regulatory payload | **33.1 L/100 km @ 19.3 t payload** | VECTO | (1) | same |
| VECTO declared payloads | **12.9 t** (Urban/Regional), **19.3 t** (Long Haul), **25.6 t** full; also empty | Group 5 = 4x2 tractor chassis | (1) | [icct briefing](https://theicct.org/wp-content/uploads/2021/06/EU_HDV_Testing_BriefingPaper_20180515a.pdf) |
| US national average | **6.4–6.9 mpg = 36.8–34.1 L/100 km** | NACFE stated national average | (1) | [nacfe](https://nacfe.org/research/run-on-less/) |
| US **best-practice fleet** average | **7.62 mpg (2022) / 7.77 mpg (2023) = 30.9 / 30.3 L/100 km** | NACFE Annual Fleet Fuel Study, 14 fleets | (1) | [nacfe AFFS](https://nacfe.org/research/affs/) |
| ⚠ **NACFE Run on Less 2017** | **10.1 mpg = 23.3 L/100 km** | 7 trucks, 17 days, real freight | (1) | [nacfe](https://nacfe.org/research/run-on-less/) |
| China stage-4 class standard vs Hi4-G | **35.8 → 29.7 L/100 km** | **49 t GCW — not directly transferable** | (1) | [chinatruck](https://www.chinatruck.net/news/great-wall-heavy-duty-truck-releases-hi4-g-hybrid-technology/) |

**Recommendation:** calibrate S0 to **32–34 L/100 km** on the line-haul corridor, citing ICCT 32.6 / 33.1 as primary anchor with NACFE 30.3–36.8 as corroborating band. The assignment's 30–38 L/100 km corridor spans exactly *"US fleet average"* to *"US best-practice fleet"*, with the EU regulatory measurement mid-band.
**EXPLICIT EXCLUSION: do NOT calibrate to Run on Less 10.1 mpg.** Those trucks were aero- and driver-optimised and not uniformly loaded to 36.3 t; calibrating a loaded S0 there would **understate S0 fuel by ~25% and silently inflate every candidate's margin.**
**Transfer caveats to state as named adjustments:** EU Group 5 is 4x2 at ~40 t regulatory max and typically speed-limited 85–90 km/h; WS8 is 6x4 at 36.3 t over 85–105 km/h.

**Independent physics cross-check** `[DERIVED — lens 3]` at 36,300 kg / CdA 5.5 / Crr 0.0055 / ρ = 1.184: wheel power **89.1 kW @ 85 km/h (48.1% aero), 124.2 kW @ 100 (56.2% aero), 137.9 kW @ 105 (58.6% aero)**. At η_driveline 0.95, 0.832 kg/L, 42.7 MJ/kg: 100 km/h steady = **29.9 L/100 km @ 190 g/kWh, 32.2 @ 205, 34.6 @ 220**; 105 km/h @ 205 → 34.1; 100 km/h @ η 0.92 and 205 → 33.3. **If S0 lands below ~30 the model is missing a real loss; above ~38 it has double-counted one.**
⚠ **Note ρ discrepancy:** lens 3 used **ρ = 1.184**; `ws8_params.Vehicle` uses **ρ_air = 1.196** (20 °C) and **ρ_air_cold = 1.341** (−10 °C). A 1.0% ρ difference is ~0.6% of wheel power at 100 km/h — small, but re-derive the cross-check at the repo value before quoting it.

## 4.2 · Road-load parameters

| Quantity | Value | Note | URL |
|---|---|---|---|
| **CdA (assignment provisional)** | **5.5 m²** | `ws8_params` `[ASSIGNMENT]` | — |
| GEM **heavy-haul default CdA** | **5.0 m²** | EPA Phase 2 regulatory default | [epa GEM](https://www.epa.gov/regulations-emissions-vehicles-and-engines/greenhouse-gas-emissions-model-gem-medium-and-heavy-duty) |
| GEM MY2027 high-roof credit | **−0.3 m²** subtracted internally (improved box trailer w/ rear fairing) | | same |
| 21CTP baseline / target Cd | **0.69 → 0.55**; at ~10 m² frontal ⟹ **~6.9 m² legacy, ~5.5 m² at target** | | [nap](https://www.nationalacademies.org/read/13288/chapter/7) |
| ⚠ **VERDICT on CdA 5.5** | **CONSERVATIVE (draggier) end, not mid-band** — the regulatory heavy-haul default is 5.0 and MY2027 gets a further −0.3 | **BASELINE_v3 records CdA 5.4 as the sole break-even condition in the G1 kill ⟹ CdA is a known program hinge. Carry it as an enumerated R14 case, not a point value.** | |
| **Crr (assignment provisional)** | **0.0055** | `ws8_params` `[ASSIGNMENT]` | — |
| Regulatory coastdown test-tire threshold | **Crr ≤ 5.1 kg/t (0.0051)** or SmartWay-verified | 40 CFR 1037.528; road-load decomposition explicitly separates **axle spin loss** from rolling resistance | [cornell](https://www.law.cornell.edu/cfr/text/40/1037.528) |
| SmartWay Crr targets (SAE J1269) | **steer 6.6, drive 7.0, trailer 5.5 kg/t** | | [epa](https://www.epa.gov/verified-diesel-tech/requirements-smartway-verification-low-rolling-resistance-tires-and-retread) |
| **Load-weighted combination Crr** `[DERIVED]` | **(5443×6.6 + 15422×7.0 + 15422×5.5)/36287 = 6.32 kg/t = 0.0063** | **15% ABOVE the assignment's 0.0055** | same |
| ⚠ **VERDICT on Crr 0.0055** | **BEST-IN-CLASS, not typical** — it presumes better-than-verification-threshold tyres on every position | **Carry 0.0055 / 0.0063 as an enumerated R14 case pair.** 15% on Crr moves rolling drag ~8 kW at 100 km/h `[DERIVED]` ≈ 6% of wheel power = **twice the ADVANCE margin** | |
| ⚠ **SOURCES DISAGREE** | CdA 5.5 is conservative; Crr 0.0055 is optimistic. **They push opposite ways and partly cancel — do not "fix" one without the other.** | | |

## 4.3 · Driveline efficiencies, BSFC, engine maps

| Quantity | Value | Source | URL |
|---|---|---|---|
| 21CTP energy audit of dissipative losses | **60% engine / 21% aero / 13% rolling / 6% drivetrain + auxiliary**; aero + Crr together consume **60–85%** of power depending on speed | 21CTP / NAS | [nap](https://www.nationalacademies.org/read/13288/chapter/7) |
| Achievable **axle efficiency** | **up to 97%** with advanced low-viscosity lubricants | GEM / 21CTP | same |
| 21CTP driveline goal | **−50%** powertrain + driveline losses | | same |
| **Mass→fuel sensitivity** | **1.5% fuel economy per 1,000 lb (454 kg)** ⟹ **~3.3% per 1,000 kg** — *more than the entire 3% ADVANCE margin* | 21CTP | same |
| **Downspeeding sensitivity** | **~1% fuel economy per 100 rpm** of cruise engine-speed reduction | HD line-haul practice, multiple independent trade sources | [truckinginfo](https://www.truckinginfo.com/156330/the-downspeeding-learning-curve) |
| Aggressive downspeeding axle ratios | **2.15–2.47 / 2.64 (direct drive)**; restricted to operators in the **top two gears 80–90% of the time with ≥30 mi between stops** | | [fleetequipmentmag](https://www.fleetequipmentmag.com/inside-truck-axle-ratios-downspeeding/) |
| Daimler ST-II downspeeding extreme | **1.75:1 axle, 950 rpm at highway cruise** | | [daimlertruck](https://www.daimlertruck.com/en/newsroom/pressrelease/daimler-truck-is-taking-efficiency-to-the-next-level-the-freightliner-supertruck-ii-52151593) |
| **Lowest BSFC, mainstream volume-production HD diesel** | **182 g/kWh = 46% BTE** | | [energy.gov](https://www.energy.gov/eere/vehicles/articles/supertruck-program-engine-project-review) |
| Detroit DD15 claimed peak BTE | **>48%** | | same |
| Detroit SuperTruck BTE decomposition | **48.1% = 46.8% engine + 1.3% WHR** | | same |
| Kenworth ST-2 record BTE | **55.7%** vs **~47% modern production** — ⚠ **a research peak, NOT a fleet value; do not build the Willans calibration on it** | | [kenworth](https://www.kenworth.com/about-us/news/kenworth-unveils-supertruck-2-at-act-expo/) |
| **WS8's own island targets** `[repo]` | **ENG-13L 185.0 · ENG-11L 187.0 · ENG-7L 196.0 · ENG-5L 205.0 g/kWh** | `ws8_engine.py`; comment: "modern production on-highway HD diesels sit in the 182-190 g/kWh island (~45-46% peak BTE); SuperTruck demonstrators go lower but are not production and are not used here" | ✅ **Consistent with the 182 g/kWh literature floor** |
| **RECOMMENDED MAP OF RECORD** | **NHTSA/SwRI Phase 2 public Excel: Detroit 14.8 L DD15 base map + 12.3 L variant DELTA map** — federally funded, publicly released, machine-readable, GT-POWER + experimentally validated, exactly the 12.3–14.8 L band | The 12.3 L delta map gives a **CITED** basis for S3's downsizing instead of an invented scaling law. **Retrieve and SHA-pin before any S0 run.** R12's 7.01 pp map-vs-scalar swing in the G1 attribution is the precedent | [nhtsa](https://www.nhtsa.gov/document/notice-proposed-rulemaking-docket-memo-swri-engine-maps) · [delta maps](https://www.nhtsa.gov/document/dd15-fuel-maps-percent-change-relative-baseline-spreadsheet) |
| Map **form** convention | fuel rate looked up on **speed × torque** (Autonomie convention), NOT a BSFC scalar with a part-load correction | Cummins ISB 6.7 L NHTSA spreadsheet (wrong displacement for S0 — use for the *form*, not the numbers) | [nhtsa](https://www.nhtsa.gov/document/cummins-ram-isb-diesel-engine-fuel-maps-spreadsheet) |
| **Engine-map scaling law** for S3's downsizing | ASME DSCC 2019 dimensionless BSFC map fits **min-BSFC regions of four diesels to within 2.5%** | ⚠ **2.5% ≈ the entire 3% ADVANCE margin — carry as explicit uncertainty on S3.** ⚠ The fit is validated **only in the min-BSFC region**, NOT at the off-point excursions S3 actually incurs | [osti 1561789](https://www.osti.gov/biblio/1561789) |
| Independent HD engine audit cross-check | Cummins ISM test point **400 hp (298 kW) / 1,250 lb-ft (1,695 Nm)**; energy audit is the published template for WS6's rejected-heat ledger by component | WVU for ICCT, Oct 2014 | [icct](https://theicct.org/wp-content/uploads/2021/06/HDV_engine-efficiency-eval_WVU-rpt_oct2014.pdf) |
| Startability practice, total launch ratio | **~46:1** (800 lb-ft × 3.73 axle × 12.45 first gear ⟹ startability factor 20.6, i.e. ~20% grade at 80,000 lb) — described as merely **"adequate for general linehaul"** | | [volvo VBI](https://vbi.truck.volvo.com/portal/perfman/010_perf_manual/150_startability.htm) |
| 18-speed low ratios / axle pairing | **12–14:1 low with 3.55–4.10 axles**; a DD15 at 1,850 lb-ft × 12:1 low × 4:1 axle **exceeds 50,000 lb-ft at the tyres** | Kenworth recommends **15–20% startability** for most heavy-haul | [fleetequipmentmag](https://www.fleetequipmentmag.com/automated-automatic-transmissions-heavy-haul/) |
| HD diesel usable band | pulling band **1,000–1,500 rpm (1.5:1)**; effective torque band only **300–400 rpm wide**; **200–250 rpm per shift step** in an 18-speed | trade/driver-education grade — adequate for the qualitative band | [drivingtests](https://www.drivingtests.co.nz/resources/why-do-trucks-have-a-lot-of-gears/) |
| **WS8's own driveline values** `[repo]` | η_amt_direct **0.985** · η_amt_indirect **0.965** · η_axle_tandem **0.955** · η_axle_single_reduction **0.970** · η_fixed_ratio_box **0.985** · η_edrive_reduction **0.970** [WS2-r4] · η_driveshaft **0.995** | Combined transmission+axle ≈ **0.94** — ✅ consistent with 21CTP's 6% drivetrain+aux share and below the 97% single-axle optimistic bound | `ws8_params.py` |

## 4.4 · Component masses ⚠ THE SECTION WITH THE MOST AT STAKE

| Component | WS8 ledger `[repo]` | External datum | Class | Verdict |
|---|---|---|---|---|
| **12-speed AMT** | **`m_amt_12sp = 325.0` kg** | **Eaton Endurant HD 12-sp ~208 kg (459 lb) dry**, marketed lightest-in-class; Endurant XD ~240 kg; I-Shift / DT12 ~260–290 kg incl. clutch; legacy 18-sp Fuller ~330 kg | (2) RECALL | 🔴 **HIGHEST-CONSEQUENCE ITEM IN THE MAP.** If the true figure is 210–280 kg, **S3's gearbox deletion is over-credited by 45–115 kg = 0.22–0.55% of the metric of record** (on a 20,785 kg payload) against a **3% advance threshold and a ≥0% sensitivity floor** — and **the over-credit flows to the candidate under test.** **VERIFY BEFORE THE S3 VERDICT IS WRITTEN.** 325 kg is defensible only if it bundles clutch, shift-air, oil charge and cooler — **say so explicitly if it does.** [eaton](https://www.eaton.com/us/en-us/catalog/transmissions/endurant-transmission.html) |
| **13 L engine, wet + cooling** | **`m_engine_13L_wet = 1215.0` kg** (`ENG-13L` 12.8 L) | X15 ~1,325 kg dry · DD15 ~1,270 · DD13 ~1,140 · D13 ~1,145 · MX-13 ~1,132 (all **DRY**, no oil/coolant/cooling package). A 13 L **WET with flywheel, clutch housing AND radiator/CAC** would plausibly be **1,350–1,450 kg** | (2) RECALL | 🟡 WS8 looks **LIGHT by ~150–230 kg**. Mostly **common-mode** (S0/S1/S2 all carry a 13 L) so it barely moves the comparison — but becomes a **differential** error where displacement differs (S3's `ENG-11L` = 1,035 kg, S4's `ENG-5L` = 470 / `ENG-7L` = 640 kg). **Errata note, not an escalation.** [cummins](https://www.cummins.com/engines/x15-efficiency-series) |
| **Class 8 e-axle, complete** | separate rows (motor + inverter + reduction) + `m_drive_axle_housings = 620.0` | **~800–1,200 kg** including housing, wheel ends and brakes; peak 300–460 kW, continuous ~half | (2) RECALL — **LOW CONFIDENCE, weakest item in the map** | 🔴 **DOUBLE-COUNT TRAP:** a vendor e-axle mass **includes** the 620 kg WS8 charges separately. Reconcile the boundary before any comparison. **Verify every number.** [allison](https://www.allisontransmission.com/propulsion-solutions/electric-hybrid-propulsion) |
| **S3 fixed-ratio box** | `m_fixed_ratio_box = 145.0` kg | NOT FOUND externally | — | Provisional; nothing to check it against |
| **S3 rev-match clutch** | `m_revmatch_clutch = 105.0` kg, "sized to SYNC only, no launch slip duty" | NOT FOUND externally | — | ⚠ The "sync only" sizing is what makes C-11's second horn (and therefore C-1/C-7) unavoidable |
| Hyliion 6X4HE overlay | — | **+800 lb / 363 kg** (net +400 lb vs the 400 lb APU allowance) | (1) | The only measured heavy e-overlay mass in the record |
| Revoy dolly | — | **~10 t / 22,000 lb**, +13 ft | (1) | Catastrophic in payload-tonne-km; nobody charges it |
| MAHLE REx trade | — | swapping **1/3 of a BEV pack for a 110–130 kW genset returns ~600 kg** | (1) | Quantified external anchor for the payload charge |
| HD **traction motor** specific power | WS2 base: **529.5 Nm peak / 96 kg = 5.5 Nm/kg**; ~2.6 kW/kg peak at a ~4,500 rpm corner; **chain with inverter (16 kg) + reduction (32 kg) = ~1.74 kW/kg** | published band: **1.5–3.5 kW/kg cont., 2.5–6 kW/kg peak, 5–15 Nm/kg** | (2)+(4) | ✅ **WS2 sits at the CONSERVATIVE end** — S3's failure is **not** caused by a pessimistic motor assumption; it survives that defence |
| **SiC traction inverter** | WS2: **16 kg at ~250 kW peak = ~15.6 kW/kg** | **15–30 kW/kg cont., up to ~50 peak, 30–60 kW/L**. ⚠ DOE/US DRIVE 2025 targets of **33 kW/kg, 100 kW/L are LIGHT-DUTY** — do not apply to an HD inverter | (2)+(4) | ✅ Conservative, consistent with HD duty; largely common-mode |
| **HD battery PACK-level Wh/kg** | WS3 model **1.55 × cell mass + 35 kg** ⟹ **~161 Wh/kg from a 250 Wh/kg cell** | Energy-NMC **140–180 Wh/kg pack** (Volvo VNR Electric ~565 kWh / ~3,500 kg ⟹ ~160 Wh/kg); LFP CTP **120–160**; power-LFP **80–105**; LTO **45–70** | (2)+(4) | ✅ **WS3's pack-overhead model is VALIDATED** against real HD packs. ⟹ **the open S4 escalation is correctly localised: it is about WS3's CELL SET being power-optimised, not about the pack model penalising S4.** Sharpen the escalation accordingly. [volvotrucks](https://www.volvotrucks.us/trucks/models/vnr-electric/) |
| **System sanity check** `[DERIVED — repo]` | Tractor side (glider 5,150 + engine 1,215 + ATS 155 + AMT 325 + shafts 65 + axle gearsets 530 + housings 620 + fuel 555 + driver 100) = **8,715 kg (~19,200 lb)**; trailer 6,800 kg (~15,000 lb); **payload 20,785 kg = 45,823 lb** vs real-world **44,000–46,000 lb at 80,000 lb GCW** | — | (4) | ✅ **The ledger passes at system level** — the engine row runs light and the AMT row runs heavy and they partly cancel. Part B findings are **errata affecting individual candidate margins, not a repudiation of the payload denominator** |

## 4.5 · WHR gains and masses (Task 4) — and the arithmetic that settles the gate

**WS8's model as implemented** (`ws8_whr.py`): `net_gain(φ) = gain_rated · clip((φ−φ_on)/(1−φ_on),0,1)^shape`
- **ETC:** `gain_rated = 0.030, φ_on = 0.30, shape = 1.3, mass = 85 kg`
- **ORC:** `gain_rated = 0.045, φ_on = 0.35, shape = 1.6, mass = 215 kg`
- **ETC+ORC:** `1−(1−g₁)(1−g₂)` less a 15% interaction penalty on the smaller; masses add (300 kg)
- **`GATE_PCT = 2.5`** — pre-committed, net of mass charge

| Source | Gross gain | Mass | Class | URL |
|---|---|---|---|---|
| **Detroit SuperTruck decomposition** | **1.3 pp of 48.1% BTE = 2.7% relative** — *at or below the gate BEFORE any mass charge* | — | (1) | [energy.gov](https://www.energy.gov/eere/vehicles/articles/supertruck-program-engine-project-review) |
| Cummins SuperTruck ORC | **+3.6% BTE**; "up to 6%" fuel; ~5 kWe recovered | ORC install commonly cited **~200–300 kg** | (1)/(2) | [osti](https://www.osti.gov/biblio/1375960) |
| ORC review literature | **4.48–7.52%** (max **at FULL LOAD**); 3.8% coolant+EGR → 7.5% with raised coolant temp; projected BTE gain generally **2–4 pp** | Only mass datum found anywhere: a **10.4 kg scroll expander** (122 cm³) — inside a system also needing boiler, recuperator, condenser, pump, fluid and added cooling. **FULL SYSTEM MASS: NOT FOUND** | (1) | [dieselnet](https://dieselnet.com/tech/engine_whr_rankine.php) |
| **PACCAR/Cummins conclusion** | *"for optimum freight efficiency, the fuel savings under transient conditions don't outweigh the additional weight, and impact on aerodynamics"* | — | (1) | **A prior kill from the two OEMs with the most direct ORC experience, stated in WS8's own metric** |
| Electric turbocompound | claimed **up to 10%**; **NESCCAF/ICCT 4.2% INCLUDING accessory electrification** (so the TC-only share is lower); Caterpillar modelled **3–5%**; John Deere investigated 10%; research turbine up to **15.8 kW**, **up to 4% BSFC**; modelling **1–4% at high load, 5–6% at peak power** | Bowman ETC turbo-generator **~30–70 kg + power electronics** | (1)/(2) | [dieselnet](https://dieselnet.com/tech/engine_whr_turbocompound.php) · [bowmanpower](https://www.bowmanpower.com/) |
| **Volvo D13TC (IN PRODUCTION)** | package-level up to **~6.5%** vs prior D13; **turbocompound member alone commonly attributed ~2–3%**; Volvo axial-turbine figure **3%** | **~50 kg** (second turbine + gear train + coupling) | (2) | [volvotrucks](https://www.volvotrucks.us/powertrain/engines/) |
| Detroit DD15 Gen 5 turbocompound | up to **~5%** for the Gen 5 *package* vs Gen 4; **16–30 kW returned to crank at cruise** | **~50 kg** | (2) | [demanddetroit](https://demanddetroit.com/engines/dd15/) |
| Ricardo/AVL/IAV consultancy studies | **Rated-point 3–5% for ORC; real-drive-cycle averaged 1–2.5% — roughly HALF the rated figure.** *The most robust and reusable finding in the WHR literature* | — | (2), qualitative HIGH confidence | [ricardo](https://www.ricardo.com/) |
| **Navistar SuperTruck I** | **~13.0 mpg, highest of the ST-I cohort, WITHOUT WHR** | — | (2) | [energy.gov](https://www.energy.gov/eere/vehicles/supertruck) |
| EU projects NoWaste / LONGRUN / TEMPO | **NOT FOUND** at the level of a defensible net figure | — | — | [cordis](https://cordis.europa.eu/) — *the negative commercial result (three decades, zero production HD ORCs) is itself the finding* |

### The gate arithmetic — this settles Task 4 without needing any literature number
`[DERIVED — lens 5, repo-checked: S0 tare 15,515 kg ⟹ payload 20,785 kg]`

| System | Mass | Payload loss | **Duty-averaged fuel gain REQUIRED** | WS8 model returns at φ = 0.35 / 0.45 / 0.55 |
|---|---|---|---|---|
| ETC | 85 kg | 0.41% | **≥ 2.91%** | 0.10 / 0.40 / **0.79%** |
| ORC | 215 kg | 1.03% | **≥ 3.53%** | 0.00 / 0.23 / **0.68%** |
| ETC+ORC | 300 kg | 1.44% | **≥ 3.94%** | — |

**Robustness check with a MUCH gentler linear-in-load law (`gain = rated × φ`, i.e. discarding WS8's steep roll-off entirely): ETC nets 0.64 / 0.94 / 1.24%; ORC nets 0.54 / 0.99 / 1.44%. Still far below 2.5%.**

**The decisive structure is an inversion, and it is what should be reported:** the gate demands a **DUTY-AVERAGED** gain (2.91% / 3.53% / 3.94%) that is **LARGER than the best published RATED-POINT gains in the entire HD literature** (3–5% ORC, 3–4.2% ETC, and only 2.7% relative from the one funded demonstrator that decomposed it). Applying the literature's own ~50% halving to the best rated figure (4.5%) gives ~2.25% duty-averaged — **below the ORC's 3.53% requirement before its mass charge.** **WHR fails on the literature's own duty-averaged numbers, not merely on WS8's roll-off choice.** Say this explicitly, because the steep roll-off is otherwise the obvious thing an adjudicator would attack.

### Engine load fraction at cruise — the input that decides every WHR number
`[DERIVED — lens 5]` Level road at 36,300 kg: **89.5 kW at the wheel @ 85 km/h, 100.4 @ 90, 138.7 @ 105.** At η ≈ 0.94 + 4 kW accessory (`AUX.p_aux_mech_avg_kW = 4.0`) ⟹ **~99 / 111 / 152 kW at the crank.** On a 350 kW `ENG-13L` that is **28–43% of rated**; on the S3 265 kW `ENG-11L`, **37–57%**. **WHR is being asked to work at ~1/3 of rated power for the overwhelming majority of a line-haul mission — exactly where exhaust enthalpy is least available.** Sustained grades for contrast: **2% @ 85 km/h needs 257.7 kW at the wheel; 3% needs 341.6 kW; 6% needs 593.0 kW.**

---

# PART 5 — NOT FOUND REGISTER: what WS8 must therefore ASSUME and FLAG AS PROVISIONAL

| # | NOT FOUND | WS8 must assume | Flag |
|---|---|---|---|
| N-1 | **Spin drag of a disconnected Class 8 e-axle** (churning, bearing, seal, residual-magnet) at 105 km/h | First-principles derivation, shown not asserted. The `disconnect ⟹ charged only when closed` bookkeeping in `ws8_candidates.py` is correct but the *magnitude when closed* is unsourced | **PROVISIONAL — obvious adjudicator target; the G1 attribution charged 1.77 pp for this member** |
| N-2 | **Rev-matched engagement transient** at 36.3 t — clutch thermal duty, torsionals, NVH, mis-match failure mode | Derived from first principles. `m_revmatch_clutch = 105 kg` "sync only" is unsourced | **PROVISIONAL. Also reintroduces the clutch-fault class the G1 F-1 deletion closed → escalate** |
| N-3 | **WHR full system mass** (only a 10.4 kg expander component found anywhere) | Report the gate result as **mass-conditional**; treat system mass as the governing uncertainty; **expect and report a FAIL rather than defending the technology** | **PROVISIONAL — but the gate fails even at zero mass for the ORC's roll-off, see §4.5** |
| N-4 | **Any −10 °C Class 8 line-haul hybrid result** | Derived. Battery power fade, e-axle capability, engine warm-up penalty all unsourced | **PROVISIONAL — treat as a potential S3 KILL CONDITION; export as an enumerated governing case per R14** |
| N-5 | **e-axle stall/creep thermal ratings at Class 8 GCW** | Derived from WS2 r4's loss surface + WS7's crawl heat-run precedent (R21 311.7 Arms ×0.685; R13 floor 80.1 W/K; G_ws ≥ 90 W/K) | **PROVISIONAL — an unquantified RISK, not just an unverified number** |
| N-6 | **Fuel energy per payload tonne-km for any comparable vehicle** | WS8's own metric of record; nearest analogue is NREL 32.1% ton-miles/gal (vocational) | **Expect WS8's numbers to sit BELOW the literature's — that gap is correct, not an error** |
| N-7 | **Any documented transmissionless / single-fixed-ratio ICE heavy-truck ATTEMPT** — the targeted query was **never run** | ⚠ **Do NOT write "tried and failed."** Rest the case on physics + regulation. State the uncontroversial analogue: a conventional Class 8 in direct-drive top gear **is** a single-fixed-ratio diesel axle at i ≈ 2.5:1 | **NEGATIVE RESULT FROM AN UNRUN QUERY — absence of evidence, not evidence of absence** |
| N-8 | **A direct engineer statement on why Hyliion retained the AMT** (the assignment asked for this) | Nothing — report as UNRESOLVED | **UNRESOLVED. Re-fetch [truckinginfo drive review](https://www.truckinginfo.com/316197/driving-hyliions-6x4he-hybrid-electric-system)** |
| N-9 | **PBS assumed friction coefficient** for startability/gradeability | `ADH` case set (0.70/0.45/0.20/0.10) `[WS8-PROV]` | **PROVISIONAL. [VTI PDF](https://www.diva-portal.org/smash/get/diva2:867038/FULLTEXT01.pdf) would turn C-4 from derived-decisive to cited-decisive** |
| N-10 | **UN R13 Annex 4 Type-II/IIA text** | The C-14 physics stands regardless; the regulation citation does not | **UNVERIFIED — do not cite R13 clause numbers** |
| N-11 | **Quantified results in the patent corpus generally** — "NONE FOUND" on nearly every patent item | Nothing. The only product-level numbers are vendor-sourced (Hyliion 15%; ePower's unverified 50–65% spec assertion) | **Neither is a calibration source. Calibrate to §4.1 only** |
| N-12 | **Verified assignee/date for US10933736, US12539861, US9188200, US5508574, US6167979** | Leads only | **UNVERIFIED — do not attribute** |

---

# PART 6 — HEADLINE VERDICT AND RECOMMENDATIONS TO THE LEAD

1. **S3's topology is genuinely novel.** Across ~35 products/programs on four continents and 30 years, the number of on-highway Class 8 vehicles in which a combustion engine drove the road wheels through a single fixed ratio with no gearbox anywhere is **ZERO**. **The risk is physics, not precedent.**

2. **But the open ground is open for a documented reason.** Six independent heavy-vehicle actors over thirty years arrived at the opposite choice (BAE, Dana, MAN, Scania, Hyliion, EP0812720A1), the fixed-ratio idea's own originators added a second ratio for load range on a vehicle 1/24th of S3's mass, and every one of the four programmes that *did* delete the ICE gearbox reinstated 2-, 3- or 5-speed gearing on the electric side. **Prior art has told us where S3 breaks. The trial should go looking there first.**

3. **Three pre-identified kill mechanisms for Task 5 — hand these over as kill mechanisms, not generic sensitivities:**
   - **(a) the fixed-ratio grade-hold floor** (C-1, C-3, C-13) — and with it the **ratio feasibility window of §3.0, which is provably EMPTY** for the downsized `ENG-11L` at a 1,000 rpm lugging limit;
   - **(b) diesel-axle-only adhesion on cruise grades** (C-4, C-16) — decisive at the 12% regulatory launch and on snow/ice at grade, **dissolved on dry/wet pavement at modest grade (C-23), so state it narrowly or it will not survive scrutiny**;
   - **(c) the single-speed e-axle's launch-vs-top-speed conflict at a ratio pinned by WS2's rotor limit** (C-5) — with the code's own admission on the record.

4. **Report the mandated segments as INFEASIBLE, not as a number.** C-1, C-3, C-7 and C-11 are structural: below the coupling floor S3 has **no fuel-to-wheels path and no fuel-to-battery path**. Any WS8 model producing a finite fuel-per-payload-tonne-km for S3 on the 6% mountain segment is necessarily modelling a *different architecture*. **An honest infeasibility is a cleaner result than a fuel figure obtained by quietly relaxing the premise.**

5. **Escalate, do not self-resolve** (CLAUDE.md rule 8): S3's **single-fault total immobilisation** (C-7) is strictly worse than the asymmetry BASELINE_v3 **R22(c)** already records program-wide, and S3 **reintroduces the clutch that Gate G1 deleted** — reopening the clutch-fault class the **F-1 deletion** had closed. Cite G1, R22(c) and the F-1 deletion directly.

6. **Task 4 (WHR): FAIL, and it fails robustly.** Report the inversion in §4.5 — the gate demands a duty-averaged gain larger than the best published rated-point gains — plus the PACCAR/Cummins prior kill in WS8's own metric, and the Navistar SuperTruck I result (best mpg of the cohort, no WHR). **Drop it without ceremony, as pre-committed.**

7. **Three verification items that must clear before the S3 verdict is written:** (i) the **AMT mass** (§4.4 — over-credit of 45–115 kg flows to the candidate under test); (ii) **`RPM_COUPLE_MIN`** (§3.0 — the whole verdict turns on an uncited `[WS8-PROV]` 1,000 rpm); (iii) **CdA 5.5 / Crr 0.0055** as an enumerated R14 case pair rather than point values, given that CdA 5.4 was the sole break-even condition in the G1 kill.

8. **Two repairs are cheap, unoccupied and not refuted by anything here (O-13, O-14):** a **two-speed axle A** closes C-1/C-2/C-3/C-11/C-14 for perhaps +60–90 kg over the 145 kg fixed box; a **small clutched generator on axle A** dissolves C-7 entirely and is the member every real-world analogue has. **S2 is untouched by C-1 through C-11 and should absorb S3's trial budget if S3 is killed.** And note honestly: **S3's actual insight — that a direct mechanical path beats a series path at steady highway cruise — is never contradicted by this sweep. What is refuted is the claim that ONE ratio can serve the whole duty.**