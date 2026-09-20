# Aspen Plus V14 官方示例流程模式库

> 来源：`C:\Program Files\AspenTech\Aspen Plus V14.0\GUI\Examples\` 下全部 **203 个 .bkp**
> 生成方式：纯文本解析（bkp 为 ASCII，按 `latin-1` 读取），未运行 Aspen 引擎、未联网。
> 配套数据：`pattern-index.csv`（逐文件 8 维结构化索引，UTF-8 BOM，Excel 可直接打开）

## 0. 解析成功率与精度限制

| 字段 | 成功 | 总数 | 成功率 |
|---|---|---|---|
| 文件读取 / 整体解析 | 203 | 203 | 100.0% |
| 单元操作类型（unit_ops） | 197 | 203 | 97.0% |
| 组分数（n_comp） | 202 | 203 | 99.5% |
| 流股数（n_streams） | 197 | 203 | 97.0% |
| 物性方法（prop_method） | 203 | 203 | 100.0% |
| 单位集（in_units） | 201 | 203 | 99.0% |
| 温度量级（temp_range） | 197 | 203 | 97.0% |
| 压力量级（pres_range） | 182 | 203 | 89.7% |
| 连接关系（n_conn） | 129 | 203 | 63.5% |

**失败/缺失字段在 CSV 中一律写 `-`，未做任何填充或猜测。**

缺失原因（均已核认为真实情况，非程序缺陷）：

- **6 个文件无单元操作**：`Chemapp\Chemsage.bkp`、`Getting Started\Process\thiazole.bkp`、`How To\Data Regression\drs1.bkp`、`Getting Started\Petroleum\blend.bkp`、`Polymers\polydrs.bkp`、`Polymers\polypro.bkp`。它们的 `RUN-CLASS` 为 `PCES` / `DRS` / `PROP`，是纯物性估算、数据回归或石油调和文件，头部 block 计数为 `0`，本就没有流程图。
- **6 个文件无温度**：同上 6 个（另含 `Getting Started\Process\flash.bkp`，其流股流量为 0、未给温度）。
- **21 个文件无压力**：多为 rate-based 胺吸收塔（压力写在塔的 `PRES1/PRES2` 段且未带单位码）、间歇模型与结垢模型。压力已扩抓 `PRES/PRES1/PRES2/PRESN/P-OUT` 五种写法。
- **74 个文件 `n_conn` 为 0**：其中 65 个是 `n_units=1` 的间歇单塔（BATCHSEP），单块本就无连接；其余为纯物性文件或块间无共享流股。

**精度限制（务必知悉）**：

1. **连接关系是推断的，不是直接读取的。** bkp 的 `FLOWSHEET` 段只给出每个块的 `IN=(...)` / `OUT=(...)` 流股清单（形如 `BLOCK BLKID="STAGE-1" BLKTYPE="FLASH2" MDLTYPE="Flash2" IN=( BRINE M0-1 "Q-1" Q1-2 ) OUT=( "BRINE-1" M1-2 "V-1" M0-1 )`），本库按「A 的出口流股 == B 的入口流股」反推 A→B 有向边。**方向正确，但端口级（第几股进、第几股出）信息未解析。**热流股（`Q-1` 等）也计入连接。
2. **流股数按 `FLOWSHEET` 中出现的唯一流股名统计**（含量流、热流、功流），与 Aspen GUI 里「Material 流股数」不完全等价；CSV 中另保留 `DEF-STREAMS` 口径供核对。
3. **组分数**取 `COMPONENTS MAIN` 段内 `CID =` 出现次数（电解质表观组分与真实组分一并计入）。
4. **物性方法**取 `GPROPERTIES GBASEOPSET / GOPSETNAME`，补充 `PROPERTIES "OPTION-SETS"` 中的 `BASE`。少数文件会同时列出主方法与辅助方法（如 `NRTL / STEAMNBS`），CSV 以 `/` 分隔，第一个为主方法。
5. **工况量级**来自全文 `TEMP =` / `PRES =` 数值采样（含流股初值与各块操作参数），**是该文件的取值范围，不是「典型操作点」**；未做加权。采样时剔除了 `TEMP = 0` / `PRES = 0`——那是 Aspen「参数未填写」的默认值而非真实工况（H₂ 液化示例里有 30 余处 `PRES = 0.0`，不过滤会把压力下限拉成 0）。

**单位代码映射表**（数值后的 `<维度> <子码>`）：

| 维度 | 子码 | 含义 | 依据 |
|---|---|---|---|
| `<22>` | `<1>` / `<3>` | K | 实测量级 20.85~800 K（H₂ 液化低温端吻合） |
| `<22>` | `<2>` | °F | 实测 -306.67~1670，且集中在 ENG / ENGPETRO 单位集 |
| `<22>` | `<4>` | °C | 实测 -151.11~2445，集中在 METCBAR / SET1 |
| `<20>` | `<1>` | N/m² (Pa) | SI 单位集默认压力单位，实测量级 1e5~6.08e7 |
| `<20>` | `<2>` | psi | 实测出现 14.696（=1 atm）|
| `<20>` | `<3>` | kg/cm² | MET 单位集定义为 KG/SQCM |
| `<20>` | `<5>` | bar | 实测出现 1.01（=1 atm）|
| `<20>` | `<10>` | kPa | 自定义单位集，实测出现 101.325（=1 atm）|

未映射子码（`<20><8>/<13>/<20>/<12>/<6>/<9>/<35>/<23>`，合计约 190 个数值点）出现在 `ENERGY`/`US-2`/`SET1` 等自定义单位集里，含义未确认，**未做换算、直接跳过**。

## 1. 统计摘要

### 1.1 单元操作使用频率（Top 20，按出现该类型的文件数 / 203）

| 单元操作 | 文件数 | 占比 |
|---|---|---|
| FLASH2 | 92 | 45.3% |
| MIXER | 71 | 35.0% |
| HEATER | 67 | 33.0% |
| RADFRAC | 63 | 31.0% |
| PUMP | 36 | 17.7% |
| FSPLIT | 36 | 17.7% |
| COMPR | 36 | 17.7% |
| RSTOIC | 23 | 11.3% |
| HEATX | 18 | 8.9% |
| DRYER | 17 | 8.4% |
| HIERARCHY | 16 | 7.9% |
| CYCLONE | 13 | 6.4% |
| RGIBBS | 13 | 6.4% |
| SCREEN | 12 | 5.9% |
| CRUSHER | 12 | 5.9% |
| VALVE | 11 | 5.4% |
| BATCHSEP | 10 | 4.9% |
| RPLUG | 10 | 4.9% |
| BATCHOP | 9 | 4.4% |
| HXFLUX | 9 | 4.4% |

库内共出现 **50 种**单元操作类型。

### 1.2 物性方法分布（主方法，Top 20）

| 物性方法 | 文件数 | 占比 |
|---|---|---|
| ENRTL-RK | 34 | 16.7% |
| SRK | 25 | 12.3% |
| ELECNRTL | 23 | 11.3% |
| IDEAL | 18 | 8.9% |
| NRTL | 15 | 7.4% |
| PC-SAFT | 15 | 7.4% |
| PENG-ROB | 15 | 7.4% |
| POLYNRTL | 11 | 5.4% |
| RK-SOAVE | 9 | 4.4% |
| BK10 | 5 | 2.5% |
| PR-BM | 4 | 2.0% |
| UNIFAC | 4 | 2.0% |
| HYSPR | 4 | 2.0% |
| BIOIDEAL | 3 | 1.5% |
| UNIF-DMD | 2 | 1.0% |
| NRTL-HOC | 2 | 1.0% |
| NRTL-RK | 2 | 1.0% |
| FACT | 2 | 1.0% |
| SR-POLAR | 2 | 1.0% |
| CPA | 1 | 0.5% |

> **读法提醒**：这是「官方示例库」的分布，不是工业真实分布。ENRTL-RK（34）高居第一，是因为本库含 37 个 Carbon Capture 示例（其中 24 个是胺液 rate-based 模型）；PC-SAFT 的 15 次几乎全部来自 PVT Experiments 与物理溶剂。**建新模型时应按体系选方法，不要按本分布选。**

### 1.3 单位集分布

| 单位集 | 文件数 |
|---|---|
| SI | 53 |
| METCBAR | 37 |
| ENG | 24 |
| SET1 | 19 |
| US-1 | 15 |
| US-2 | 6 |
| ENGPETRO | 5 |
| METSOLID | 5 |
| METSPEC | 4 |
| REPORT | 4 |
| H2 | 4 |
| MET | 3 |
| 其余 17 种自定义集 | 24 |

三大标准集合计 114 / 203（56%）。

### 1.4 分析类对象 / 动力学

| 对象 | 真实存在（文件数） | 仅关键词命中 |
|---|---|---|
| DESIGN-SPEC | 32 | 1 |
| SENSITIVITY | 38 | 0 |
| OPTIMIZATION | 11 | 192 |
| CALCULATOR | 71 | 1 |
| CONV-OPTIONS | 0 | 83 |

> **判定规则**：真实存在 = 头部 block 清单 / FLOWSHEET 中存在该类型对象，或文件里有正式声明段 `? SENSITIVITY "S-1" ? ; "ENG_MOLE" ;`。`OPTIMIZATION` 的纯关键词命中高达 192，全部来自求解器默认段 `DMO-PARAMS MODE = OPTIMIZATION`，**是假阳性**。

- 含反应单元（RSTOIC/RGIBBS/RPLUG/RBATCH/RCSTR 等）的文件：**47**
- 含明确动力学关键词（POWERLAW / LHHW / RK-PLUG / USER-KIN）的文件：**12**
- 含 RADFRAC 反应精馏段 `REAC-DIST` 的文件：**33**

### 1.5 规模分布

| 指标 | 中位数 | 均值 | 最大 | 备注 |
|---|---|---|---|---|
| 单元操作数 | 4 | 11.1 | 282 | >10 单元的有 50 个 |
| 组分数 | 11 | 12.0 | 51 | 最大 51（igcc）|
| 流股数 | 10 | 17.8 | 256 | 最大 256（igcc）|

**分布高度右偏**：中位数仅 4 个单元，但均值 11.1——少量超大型示例（igcc 282、pipelinegas 89、H₂ 液化 62）拉高了均值。多数示例是「小而完整」的教学模型。

## 2. 高频模式 Top N

### 2.1 高频单元操作组合（完整类型集，Top 12）

| 次数 | 组合 |
|---|---|
| 40 | FLASH2 |
| 24 | RADFRAC |
| 10 | BATCHSEP |
| 6 | FLASH2 + MIXER |
| 5 | FLASH2 + FSPLIT + MIXER |
| 4 | PETROFRAC |
| 4 | RBATCH |
| 3 | COMPR + FLASH2 + FSPLIT + HEATER + HXFLUX + MIXER + PUMP + RADFRAC + RPLUG |
| 3 | HEATER + HXFLUX + RADFRAC |
| 3 | SCREEN |
| 2 | BATCHOP |
| 2 | RGIBBS + RPLUG |

### 2.2 高频 2 项组合 Top 12

| 次数 | 组合 |
|---|---|
| 45 | HEATER + MIXER |
| 39 | FLASH2 + MIXER |
| 34 | HEATER + RADFRAC |
| 32 | HEATER + PUMP |
| 32 | FSPLIT + MIXER |
| 31 | FLASH2 + HEATER |
| 31 | COMPR + MIXER |
| 30 | COMPR + HEATER |
| 27 | MIXER + PUMP |
| 25 | MIXER + RADFRAC |
| 25 | FSPLIT + HEATER |
| 24 | FLASH2 + FSPLIT |

### 2.3 高频 3 项组合 Top 12

| 次数 | 组合 |
|---|---|
| 26 | HEATER + MIXER + PUMP |
| 26 | COMPR + HEATER + MIXER |
| 24 | FLASH2 + HEATER + MIXER |
| 23 | FLASH2 + FSPLIT + MIXER |
| 23 | FSPLIT + HEATER + MIXER |
| 22 | HEATER + MIXER + RADFRAC |
| 20 | HEATER + PUMP + RADFRAC |
| 20 | COMPR + FSPLIT + MIXER |
| 19 | COMPR + FSPLIT + HEATER |
| 17 | FLASH2 + HEATER + PUMP |
| 17 | FLASH2 + MIXER + PUMP |
| 17 | COMPR + FLASH2 + MIXER |

**可直接复用的三条骨架**（由上面统计归纳）：

1. `HEATER + MIXER + PUMP`（26 次）— 最通用的「混合-升压-调温」进料段，几乎所有连续流程的开头。
2. `COMPR + HEATER + MIXER`（26 次）— 气体流程版进料段（压缩替代泵）。
3. `FLASH2 + FSPLIT + MIXER`（23 次）— 闪蒸 + 分流 + 循环混合，分离与循环回路的最小骨架。
4. `HEATER + MIXER + RADFRAC`（22 次）/`HEATER + PUMP + RADFRAC`（20 次）— 精馏工段标准配置。

## 3. 按流程类型分组

分组规则（单一主标签，按优先级判定）：聚合 → 固体/结晶 → 萃取 → 吸收解吸 → 精馏 → 反应 → 换热 → 闪蒸 → 其他。

| 流程类型 | 文件数 | 占比 |
|---|---|---|
| 精馏 Distillation | 42 | 20.7% |
| 反应 Reaction | 14 | 6.9% |
| 吸收解吸 Absorption-Stripping | 38 | 18.7% |
| 蒸发结晶/固体 Evap-Cryst-Solids | 30 | 14.8% |
| 换热网络 HEN | 6 | 3.0% |
| 萃取 Extraction | 2 | 1.0% |
| 聚合 Polymerization | 15 | 7.4% |
| 闪蒸/通用分离 Flash-Sep | 50 | 24.6% |
| 其他 Other | 6 | 3.0% |

> 这是**单一主标签**统计。含反应单元的文件实际有 47 个（见 1.4），但其中多数同时含精馏塔或固体设备，按优先级被归入精馏 / 固体 / 吸收解吸等组，主标签为「反应」的只剩 14 个。**检索某组时请同时看 1.4 的交叉统计。**

### 精馏 Distillation（42 个）

- **典型拓扑**（单元操作频次 Top 8）：RADFRAC(27)、HEATER(19)、MIXER(11)、BATCHSEP(10)、FLASH2(9)、FSPLIT(8)、HXFLUX(8)、COMPR(7)
- **典型物性方法**：SRK(11)、RK-SOAVE(8)、NRTL(7)、BK10(5)、UNIFAC(4)
- **典型工况范围**：温度 42 个文件有温度：总范围 -151 ~ 910 °C，中位下界 25 °C / 中位上界 70 °C；压力 41 个文件有压力：总范围 -1.03 ~ 92 bar，中位下界 1.00 bar / 中位上界 4.14 bar
- **规模中位数**：单元 2 / 组分 4 / 流股 7
- **代表 bkp**（按规模×连接数排序）：

| bkp | 单元 | 组分 | 流股 | 连接 | 主物性方法 | 单元操作 |
|---|---|---|---|---|---|---|
| `Bulk Chemicals/Methanol/methanol synthesis - ici syntex quench reactor process.bkp` | 40 | 16 | 56 | 49 | SRK | COMPR + FLASH2 + FSPLIT + HEATER + HXFLUX + MIXER |
| `Bulk Chemicals/Methanol/methanol synthesis-data regression.bkp` | 40 | 16 | 56 | 49 | SRK | COMPR + FLASH2 + FSPLIT + HEATER + HXFLUX + MIXER |
| `Biofuel and Biochemicals/Biomass pyrolysis/Biomass pyrolysis with RYIELD/Softwood biomass conversion to bio-fuel through pyrolysis with RYIELD.bkp` | 38 | 33 | 54 | 38 | PR-BM | COMPR + DECANTER + FLASH2 + FSPLIT + HEATER + HEATX |
| `Bulk Chemicals/Methanol/methanol synthesis-lurgi two stage process.bkp` | 33 | 16 | 47 | 40 | SRK | COMPR + FLASH2 + FSPLIT + HEATER + HXFLUX + MIXER |
| `Energy Analysis/1. Ethylene Plant Base Case Model.bkp` | 22 | 12 | 36 | 30 | SRK | COMPR + FLASH2 + FSPLIT + HEATER + HEATX + MIXER |
| `Plant Data/C2 Splitter/C2SEO.bkp` | 19 | 12 | 28 | 21 | SRK | COMPR + FLASH2 + FSPLIT + HEATER + HXFLUX + MIXER |
| `Energy Analysis/2.2 Cumene Plant New Heat Exchanger Model.bkp` | 18 | 6 | 31 | 22 | SRK | HEATER + HEATX + MIXER + PUMP + RADFRAC + RPLUG |
| `Energy Analysis/2.1 Cumene Plant Base Case Model.bkp` | 15 | 6 | 24 | 17 | SRK | HEATER + HEATX + MIXER + PUMP + RADFRAC + RPLUG |

  > 上表 8 个代表中，有 7 个同时含反应单元（`methanol synthesis - ici syntex quench reactor process.bkp`、`methanol synthesis-data regression.bkp`、`Softwood biomass conversion to bio-fuel through pyrolysis with RYIELD.bkp`、`methanol synthesis-lurgi two stage process.bkp`、`1. Ethylene Plant Base Case Model.bkp`、`2.2 Cumene Plant New Heat Exchanger Model.bkp`、`2.1 Cumene Plant Base Case Model.bkp`）——它们因含本组特征设备而归入本组，但实际是复合流程。

### 反应 Reaction（14 个）

- **典型拓扑**（单元操作频次 Top 8）：RGIBBS(8)、FLASH2(7)、RSTOIC(6)、MIXER(5)、HEATER(4)、FSPLIT(4)、PUMP(4)、RPLUG(3)
- **典型物性方法**：SRK(2)、IDEAL(2)、PC-SAFT(2)、NRTL(1)、RK-SOAVE(1)
- **典型工况范围**：温度 14 个文件有温度：总范围 15 ~ 2445 °C，中位下界 25 °C / 中位上界 146 °C；压力 13 个文件有压力：总范围 -0.01 ~ 76.5 bar，中位下界 1.00 bar / 中位上界 2.00 bar
- **规模中位数**：单元 4 / 组分 10 / 流股 9
- **代表 bkp**（按规模×连接数排序）：

| bkp | 单元 | 组分 | 流股 | 连接 | 主物性方法 | 单元操作 |
|---|---|---|---|---|---|---|
| `Power/Cogeneration/cogeneration.bkp` | 57 | 9 | 52 | 38 | PR-BM | COMPR + FLASH2 + FSPLIT + HEATX + HIERARCHY + MIXER |
| `Hydrogen/Ammonia decomposition/Ammonia decomposition furnace reactor.bkp` | 32 | 10 | 32 | 28 | PC-SAFT | COMPR + FSPLIT + HEATER + HXFLUX + PUMP + RGIBBS |
| `Power/Gas Turbine/Natural Gas Combined Cycle (NGCC) Power Plant.bkp` | 31 | 11 | 51 | 46 | PENG-ROB | COMPR + FLASH2 + FSPLIT + HEATER + HEATX + MIXER |
| `Hydrogen/Alkaline electrolysis/Industrial Scale Alkaline Electrolyzer/Industrial Scale Alkaline Electrolyzer.bkp` | 11 | 8 | 17 | 12 | ENRTL-RK | ELECTROLYZER + FLASH2 + FSPLIT + HEATER + MIXER + PUMP |
| `Metals and Minerals/Blast Furnace for Production of Iron.bkp` | 6 | 13 | 17 | 10 | SOLIDS | MHEATX + MIXER + RGIBBS |
| `Biofuel and Biochemicals/Biomass characterization/Biomass feedstock pure and NC compositions.bkp` | 6 | 30 | 13 | 5 | NRTL | MIXER + RSTOIC + SEP |
| `Getting Started/Solids/solid2.bkp` | 5 | 16 | 11 | 4 | IDEAL | FLASH2 + RGIBBS + RSTOIC + RYIELD + SSPLIT |
| `Bulk Chemicals/cumene.bkp` | 3 | 3 | 5 | 3 | SRK | FLASH2 + HEATER + RSTOIC |

### 吸收解吸 Absorption-Stripping（38 个）

- **典型拓扑**（单元操作频次 Top 8）：RADFRAC(30)、HEATER(14)、FLASH2(13)、PUMP(11)、MIXER(10)、CHARGEBAL(6)、HEATX(5)、VALVE(3)
- **典型物性方法**：ENRTL-RK(16)、ELECNRTL(15)、PC-SAFT(6)、CPA(1)
- **典型工况范围**：温度 38 个文件有温度：总范围 -37 ~ 200 °C，中位下界 22 °C / 中位上界 58 °C；压力 32 个文件有压力：总范围 0 ~ 68.9 bar，中位下界 1.00 bar / 中位上界 6.35 bar
- **规模中位数**：单元 2 / 组分 16 / 流股 7
- **代表 bkp**（按规模×连接数排序）：

| bkp | 单元 | 组分 | 流股 | 连接 | 主物性方法 | 单元操作 |
|---|---|---|---|---|---|---|
| `Bulk Chemicals/Ethylene Glycol/Ethylene Glycol Plant Example.bkp` | 15 | 6 | 29 | 19 | CPA | FLASH2 + FSPLIT + HEATER + MIXER + RADFRAC + RPLUG |
| `Carbon Capture/Industrial Scale/CO2 capture from syngas for IGCC using DEPG.bkp` | 14 | 9 | 21 | 17 | PC-SAFT | COMPR + FLASH2 + HEATER + MIXER + PUMP + RADFRAC |
| `Carbon Capture/Amines ENRTL-RK/ENRTL-RK_Rate_Based_MEA_Model.bkp` | 10 | 19 | 19 | 12 | ENRTL-RK | FLASH2 + HEATER + HEATX + MIXER + PUMP + RADFRAC |
| `Carbon Capture/Industrial Scale/CO2 capture from coal power plant using MEA.bkp` | 10 | 14 | 18 | 12 | ENRTL-RK | CHARGEBAL + HEATER + MAKEUP + PUMP + RADFRAC |
| `Carbon Capture/Industrial Scale/CO2 capture from natural gas power plant using MEA.bkp` | 10 | 14 | 18 | 12 | ENRTL-RK | CHARGEBAL + HEATER + MAKEUP + PUMP + RADFRAC |
| `Carbon Capture/Industrial Scale/CO2 and H2S Removal using K2CO3.bkp` | 10 | 17 | 16 | 10 | ENRTL-RK | CHARGEBAL + FLASH2 + HEATER + MIXER + PUMP + RADFRAC |
| `Carbon Capture/Industrial Scale/CO2 capture using K2CO3.bkp` | 10 | 15 | 16 | 10 | ENRTL-RK | CHARGEBAL + FLASH2 + HEATER + MIXER + PUMP + RADFRAC |
| `Carbon Capture/Amines ENRTL-RK/ENRTL-RK_Rate_Based_MDEA_Model.bkp` | 9 | 16 | 17 | 11 | ENRTL-RK | CHARGEBAL + HEATER + HEATX + MIXER + RADFRAC |

  > 上表 8 个代表中，有 1 个同时含反应单元（`Ethylene Glycol Plant Example.bkp`）——它们因含本组特征设备而归入本组，但实际是复合流程。

### 蒸发结晶/固体 Evap-Cryst-Solids（30 个）

- **典型拓扑**（单元操作频次 Top 8）：MIXER(23)、HEATER(18)、COMPR(18)、DRYER(16)、CYCLONE(13)、FSPLIT(13)、SCREEN(12)、CRUSHER(12)
- **典型物性方法**：IDEAL(14)、ELECNRTL(6)、NRTL(3)、ENRTL-RK(3)、PENG-ROB(1)
- **典型工况范围**：温度 30 个文件有温度：总范围 -188 ~ 908 °C，中位下界 20 °C / 中位上界 123 °C；压力 28 个文件有压力：总范围 -4.41 ~ 174 bar，中位下界 1.00 bar / 中位上界 1.02 bar
- **规模中位数**：单元 9 / 组分 5 / 流股 15
- **代表 bkp**（按规模×连接数排序）：

| bkp | 单元 | 组分 | 流股 | 连接 | 主物性方法 | 单元操作 |
|---|---|---|---|---|---|---|
| `Power/Coal Gasification/igcc.bkp` | 282 | 45 | 256 | 186 | PENG-ROB | COMPR + CRUSHER + FLASH2 + FSPLIT + HEATER + HEATX |
| `Power/Coal Gasification/pipelinegas.bkp` | 89 | 18 | 76 | 51 | PR-BM | COMPR + CRUSHER + FLASH2 + FSPLIT + HEATER + HEATX |
| `Solids Modeling/Fluidized Bed Dryer/Multi Stage Fluidized Bed Dryer.bkp` | 39 | 3 | 30 | 12 | IDEAL | CLASSIFIER + COMPR + CYCLONE + DRYER + ESP + FSPLIT |
| `Solids Modeling/Potassium Chloride and Economics/2. Potassium Chloride Crystallization_DesignAlternative.bkp` | 37 | 8 | 45 | 47 | ELECNRTL | CFUGE + CLASSIFIER + COMPR + CRUSHER + CRYSTALLIZER + CYCLONE |
| `Solids Modeling/Granulation/Granulation Example.bkp` | 34 | 8 | 39 | 20 | SR-POLAR | CLASSIFIER + COMPR + CRUSHER + DRYER + FSPLIT + GRANULATOR |
| `Solids Modeling/Potassium Chloride and Economics/1. Potassium Chloride Crystallization_BaseCase Demo.bkp` | 33 | 8 | 43 | 35 | ELECNRTL | CFUGE + CLASSIFIER + COMPR + CRUSHER + CRYSTALLIZER + CYCLONE |
| `Solids Modeling/Belt Dryer/2 Belt Dryer With Cooling Stage.bkp` | 28 | 3 | 42 | 38 | IDEAL | COMPR + DRYER + FSPLIT + HEATER + MIXER |
| `Solids Modeling/Belt Dryer/1 Belt Dryer Base Case.bkp` | 27 | 3 | 40 | 36 | IDEAL | COMPR + DRYER + FSPLIT + HEATER + MIXER |

  > 上表 8 个代表中，有 4 个同时含反应单元（`igcc.bkp`、`pipelinegas.bkp`、`2. Potassium Chloride Crystallization_DesignAlternative.bkp`、`1. Potassium Chloride Crystallization_BaseCase Demo.bkp`）——它们因含本组特征设备而归入本组，但实际是复合流程。

### 换热网络 HEN（6 个）

- **典型拓扑**（单元操作频次 Top 8）：PUMP(5)、FLASH2(5)、COMPR(5)、VALVE(5)、MHEATX(4)、HEATER(4)、MIXER(3)、HEATX(2)
- **典型物性方法**：HYSPR(4)、NRTL(1)、PENG-ROB(1)
- **典型工况范围**：温度 6 个文件有温度：总范围 -252 ~ 616 °C，中位下界 -15 °C / 中位上界 27 °C；压力 5 个文件有压力：总范围 0.46 ~ 80 bar，中位下界 3.00 bar / 中位上界 80.00 bar
- **规模中位数**：单元 13 / 组分 10 / 流股 19
- **代表 bkp**（按规模×连接数排序）：

| bkp | 单元 | 组分 | 流股 | 连接 | 主物性方法 | 单元操作 |
|---|---|---|---|---|---|---|
| `Hydrogen/Liquefaction/H2 cryogenic process.bkp` | 62 | 15 | 96 | 88 | HYSPR | COMPR + FLASH2 + HEATER + MHEATX + MIXER + PUMP |
| `Hydrogen/Liquefaction/Cascade mixed refrigerant (CMR) precooling.bkp` | 18 | 10 | 29 | 23 | HYSPR | COMPR + FLASH2 + HEATER + MHEATX + MIXER + PUMP |
| `Hydrogen/Liquefaction/Alternative single mixed refrigerant (SMR+) PRICO precooling.bkp` | 15 | 10 | 22 | 16 | HYSPR | ANALYZER + COMPR + FLASH2 + HEATER + MHEATX + MIXER |
| `Safety/Pressure Relief/Safety Analysis Without PRD.bkp` | 12 | 7 | 17 | 7 | PENG-ROB | COMPR + FLASH2 + HEATX + HIERARCHY + PUMP + VALVE |
| `Hydrogen/Liquefaction/Single mixed refrigerant (SMR) PRICO precooling.bkp` | 7 | 10 | 12 | 8 | HYSPR | ANALYZER + COMPR + HEATER + MHEATX + VALVE |
| `Batch Modeling/Batch Distillation/Batch evaporator loop.bkp` | 4 | 4 | 7 | 4 | NRTL | BATCHOP + FLASH2 + HEATX + PUMP |

### 萃取 Extraction（2 个）

- **典型拓扑**（单元操作频次 Top 8）：RSTOIC(2)、EXTRACT(2)、MIXER(1)、SEP(1)、RADFRAC(1)、PUMP(1)、RCSTR(1)、HEATER(1)
- **典型物性方法**：UNIF-DMD(1)、NRTL(1)
- **典型工况范围**：温度 2 个文件有温度：总范围 5 ~ 60 °C，中位下界 12 °C / 中位上界 32 °C；压力 2 个文件有压力：总范围 0.1 ~ 4 bar，中位下界 0.54 bar / 中位上界 2.49 bar
- **规模中位数**：单元 9 / 组分 22 / 流股 16
- **代表 bkp**（按规模×连接数排序）：

| bkp | 单元 | 组分 | 流股 | 连接 | 主物性方法 | 单元操作 |
|---|---|---|---|---|---|---|
| `Biofuel and Biochemicals/Biodiesel/Biodiesel Production from Vegetable Oil.bkp` | 16 | 39 | 27 | 17 | UNIF-DMD | EXTRACT + HEATER + MIXER + PUMP + RADFRAC + RCSTR |
| `Pharmaceuticals/Penicillin/pen.bkp` | 2 | 6 | 5 | 1 | NRTL | EXTRACT + RSTOIC |

  > 上表 2 个代表中，有 2 个同时含反应单元（`Biodiesel Production from Vegetable Oil.bkp`、`pen.bkp`）——它们因含本组特征设备而归入本组，但实际是复合流程。

### 聚合 Polymerization（15 个）

- **典型拓扑**（单元操作频次 Top 8）：RBATCH(6)、RCSTR(4)、MIXER(4)、FLASH2(4)、FSPLIT(2)、BATCHOP(2)、RADFRAC(2)、COMPR(2)
- **典型物性方法**：POLYNRTL(11)、PC-SAFT(1)、PNRTL-IG(1)、POLYSL(1)、POLYFH(1)
- **典型工况范围**：温度 13 个文件有温度：总范围 -10 ~ 220 °C，中位下界 39 °C / 中位上界 65 °C；压力 14 个文件有压力：总范围 -2 ~ 30 bar，中位下界 0.98 bar / 中位上界 1.49 bar
- **规模中位数**：单元 2 / 组分 8 / 流股 4
- **代表 bkp**（按规模×连接数排序）：

| bkp | 单元 | 组分 | 流股 | 连接 | 主物性方法 | 单元操作 |
|---|---|---|---|---|---|---|
| `Polymers/polyacrylate.bkp` | 11 | 14 | 20 | 12 | PNRTL-IG | CFUGE + COMPR + DRYER + FLASH2 + FSPLIT + HEATER |
| `Polymers/Polystyrene/sty_dist.bkp` | 8 | 8 | 15 | 10 | POLYNRTL | PUMP + RADFRAC + RCSTR |
| `Polymers/Polypropylene/pp.bkp` | 6 | 9 | 17 | 6 | PC-SAFT | COMPR + FLASH2 + MHEATX + MIXER + RCSTR |
| `Batch Modeling/Batch Distillation/Polyester adhesive batch process using RADFRAC.bkp` | 6 | 10 | 10 | 5 | POLYNRTL | BATCHOP + FSPLIT + RADFRAC + TRANSFER |
| `Polymers/Polystyrene/ps.bkp` | 6 | 8 | 10 | 5 | POLYNRTL | FLASH2 + HEATER + RCSTR + RPLUG |
| `Polymers/polytut.bkp` | 3 | 8 | 5 | 2 | POLYNRTL | MIXER + RCSTR |
| `Polymers/Polystyrene/psea.bkp` | 2 | 6 | 4 | 1 | POLYNRTL | MIXER + RBATCH |
| `Polymers/pmma.bkp` | 2 | 5 | 4 | 1 | POLYNRTL | FLASH2 + RBATCH |

### 闪蒸/通用分离 Flash-Sep（50 个）

- **典型拓扑**（单元操作频次 Top 8）：FLASH2(47)、MIXER(14)、FSPLIT(8)、HEATER(5)、BATCHOP(2)、SSPLIT(2)、USER2(2)、SEP(1)
- **典型物性方法**：PENG-ROB(12)、SRK(12)、ENRTL-RK(11)、PC-SAFT(6)、NRTL(2)
- **典型工况范围**：温度 49 个文件有温度：总范围 5 ~ 527 °C，中位下界 73 °C / 中位上界 98 °C；压力 45 个文件有压力：总范围 0.125 ~ 608 bar，中位下界 1.01 bar / 中位上界 304.30 bar
- **规模中位数**：单元 5 / 组分 14 / 流股 13
- **代表 bkp**（按规模×连接数排序）：

| bkp | 单元 | 组分 | 流股 | 连接 | 主物性方法 | 单元操作 |
|---|---|---|---|---|---|---|
| `PVT Experiments/PR/Constant_Mass_Expansion_PR_Model_Tuning_Step I.bkp` | 52 | 22 | 82 | 52 | PENG-ROB | FLASH2 + MIXER |
| `PVT Experiments/PR/Constant_Mass_Expansion_PR_Model_Tuning_Step II.bkp` | 52 | 22 | 82 | 52 | PENG-ROB | FLASH2 + MIXER |
| `PVT Experiments/SAFT/Constant_Mass_Expansion_PC-SAFT_Model_Tuning.bkp` | 52 | 22 | 82 | 52 | PC-SAFT | FLASH2 + MIXER |
| `PVT Experiments/SRK/Constant_Mass_Expansion_SRK_Model_Tuning_Step I.bkp` | 52 | 22 | 82 | 52 | SRK | FLASH2 + MIXER |
| `PVT Experiments/SRK/Constant_Mass_Expansion_SRK_Model_Tuning_Step II.bkp` | 52 | 22 | 82 | 52 | SRK | FLASH2 + MIXER |
| `PVT Experiments/PR/Constant_Volume_Depletion_PR_Model_Tuning_Step I.bkp` | 23 | 22 | 39 | 29 | PENG-ROB | FLASH2 + FSPLIT + MIXER |
| `PVT Experiments/PR/Constant_Volume_Depletion_PR_Model_Tuning_Step II.bkp` | 23 | 22 | 39 | 29 | PENG-ROB | FLASH2 + FSPLIT + MIXER |
| `PVT Experiments/SAFT/Constant_Volume_Depletion_PC-SAFT_Model_Tuning.bkp` | 23 | 22 | 39 | 29 | PC-SAFT | FLASH2 + FSPLIT + MIXER |

  > 上表前 8 行来自 `PVT Experiments`，其「52 单元 / 82 流股」是同一 FLASH2+MIXER 结构按实验点反复串联，**不代表流程复杂度**，仅适合查「某状态方程如何配 PVT 回归」。

### 其他 Other（6 个）

- **典型拓扑**（单元操作频次 Top 8）：BATCHOP(2)、HIERARCHY(1)
- **典型物性方法**：BIOIDEAL(2)、ENRTL-RK(2)、IDEAL(1)、WILSON(1)
- **典型工况范围**：温度 3 个文件有温度：总范围 30 ~ 910 °C，中位下界 35 °C / 中位上界 72 °C；压力 2 个文件有压力：总范围 0.981 ~ 3.1 bar，中位下界 1.01 bar / 中位上界 2.14 bar
- **规模中位数**：单元 0 / 组分 6 / 流股 0
- **代表 bkp**（按规模×连接数排序）：

| bkp | 单元 | 组分 | 流股 | 连接 | 主物性方法 | 单元操作 |
|---|---|---|---|---|---|---|
| `Biofuel and Biochemicals/BDO via fermentation/BDO via fermentation.bkp` | 2 | 14 | 7 | 0 | BIOIDEAL | BATCHOP + HIERARCHY |
| `Batch Modeling/Bioethanol via fermentation/Bioethanol via fermentation.bkp` | 1 | 10 | 4 | 0 | BIOIDEAL | BATCHOP |
| `Chemapp/Chemsage.bkp` | 0 | 0 | 0 | 0 | ENRTL-RK |  |
| `Getting Started/Petroleum/blend.bkp` | 0 | 11 | 0 | 0 | IDEAL |  |
| `Getting Started/Process/thiazole.bkp` | 0 | 1 | 0 | 0 | ENRTL-RK |  |
| `How To/Data Regression/drs1.bkp` | 0 | 2 | 0 | 0 | WILSON |  |

## 4. 可直接复用的模板清单

共 30 个，按场景挑出；括号内数据均为从 bkp 实测解析所得。

| # | 场景 | bkp 路径（相对 Examples） | 单元 | 组分 | 流股 | 物性方法 | 单位集 | 为什么适合当模板 |
|---|---|---|---|---|---|---|---|---|
| 1 | 多效蒸发 | `Bulk Chemicals/Triple-Effect Evaporator.bkp` | 6 | 6 | 14 | ELECNRTL | METCBAR | 三效蒸发 + 逐效降圧；FLASH2 蒸发室 + HEATER 加热盘管交替串联，用 Design-Spec 串起各效热负荷。做多效蒸发 / 蒸发结晶 / 盐水浓缩类问题的起手模板。 |
| 2 | 烧碱蒸发（强电解质） | `Metals and Minerals/Caustic Evaporators.bkp` | 2 | 31 | 5 | ENRTL-RK | US-1 | 2 个 FLASH2 串联，31 组分（NaOH/NaCl/Na₂SO₄/Na₂CrO₄ + 离子 + NAOH(S)/NACL(S) 等固相盐），主物性 ENRTL-RK，工况 75~130 °C。做高浓度碱液 / 强非理想电解质 + 固相盐析出设置的参考。 |
| 3 | 反应-分离入门 | `Bulk Chemicals/cumene.bkp` | 3 | 3 | 5 | SRK | ENG | RSTOIC 反应器 + HEATER 冷却 + FLASH2 闪蒸的最小闭环，并挂了 Design-Spec 与 Calculator。做「固定转化率反应器 + 简单分离」类模型的最小骨架。 |
| 4 | 甲醇合成（激冷反应器） | `Bulk Chemicals/Methanol/methanol synthesis - ici syntex quench reactor process.bkp` | 40 | 16 | 56 | SRK | US-2 | RPLUG/RK-PLUG 动力学反应器 + 多级激冷 + 循环回路 + HXFLUX。做气固催化放热反应 + 移热 + 未反应气循环的标准模板。 |
| 5 | 甲醇合成（两段） | `Bulk Chemicals/Methanol/methanol synthesis-lurgi two stage process.bkp` | 33 | 16 | 47 | SRK | US-2 | 同体系的两段流程变体，可与上例对比「单段激冷 vs 两段」的建模差异。 |
| 6 | 乙二醇装置（含优化） | `Bulk Chemicals/Ethylene Glycol/Ethylene Glycol Plant Example.bkp` | 15 | 6 | 29 | CPA | SET1 | 反应 + 多塔分离 + 全流程级 OPTIMIZATION 对象（11 个含优化的文件之一）。做「流程级优化」建模的参考。 |
| 7 | 三相反应精馏 | `Bulk Chemicals/Distillation/3phase.bkp` | 3 | 4 | 8 | NRTL-RK | SET1 | TITLE 为 “Three-phase Reactive Distillation Application”：HEATER + RADFRAC + DECANTER，酯化反应挂在再沸器（REAC-DIST + KINETIC），NRTL-RK，1.013 bar。做共沸 / 三相分层 / 反应精馏的模板。 |
| 8 | 带循环的中型连续流程 | `Bulk Chemicals/advchex.bkp` | 10 | 6 | 19 | RK-SOAVE | ENG | TITLE 为 “HYDROGENATION OF BENZENE TO CYCLOHEXANE”：MIXER + HEATER + RSTOIC + FLASH2 + 2×FSPLIT + RADFRAC + 3×HEATER，10 单元 / 6 组分 / RK-SOAVE，含未反应气循环。做「中小规模连续流程 + 循环回路」的通用骨架。 |
| 9 | 胺法脱碳·精简版（Rate-Based） | `Carbon Capture/Amines ELECNRTL/ELECNRTL_Rate_Based_MEA_Model.bkp` | 4 | 16 | 8 | ELECNRTL | SI | ELECNRTL + 2 座 RADFRAC（ABSORBER / STRIPPER）+ HEATER + PUMP，仅 4 单元，RADFRAC 内含 REAC-DIST 动力学反应段（非平衡级）。做「化学吸收速率建模」的最小骨架；同目录另有 14 个同构变体可直接换胺（DEA/MDEA/PZ/DGA/DIPA/AMP/K2CO3/NH3/TEA/NaOH 及多种复配）。 |
| 10 | 胺法脱碳·完整版（ENRTL-RK） | `Carbon Capture/Amines ENRTL-RK/ENRTL-RK_Rate_Based_MEA_Model.bkp` | 10 | 19 | 19 | ENRTL-RK | SET1 | **比上例更完整**：ABSORBER + STRIPPER 之外还含 HEATX（贫富液换热）、3×HEATER、2×MIXER、FLASH2，共 10 单元 / 19 组分，物性换为 ENRTL-RK。做工业级胺液循环回路的建模参考；同目录另有 10 个变体（含 Sulfolane-DIPA / Sulfolane-MDEA 混合溶剂）。 |
| 11 | 工业级烟气脱碳全厂 | `Carbon Capture/Industrial Scale/CO2 capture from coal power plant using MEA.bkp` | 10 | 14 | 18 | ENRTL-RK | METCBAR | 从烟气到压缩 CO2 的完整工业流程（吸收塔 + 再生塔 + 换热 + 压缩）。做碳捕集全厂级模型的规模与结构参考。 |
| 12 | 物理溶剂脱碳 | `Carbon Capture/Physical Solvents/Aspen_Plus_DEPG_Model.bkp` | 2 | 13 | 8 | PC-SAFT | ENG | DEPG（Selexol 类）物理吸收，PC-SAFT。做物理溶剂（与化学吸收对照）建模的模板；同目录另有 NMP / PC / MEOH。 |
| 13 | 原油常压蒸馏 | `Energy/cdu.bkp` | 2 | 10 | 9 | BK10 | CRUDE | TITLE 为 “Atmospheric Crude Distillation Column”：PREHEAT(HEATER) + CDU(PETROFRAC)，组分是 H₂O/C1~NC5/H₂S + 一个 CRUDE assay，物性 BK10，塔顶 3.0 / 塔底 5.0 kg/cm²。示例重点是塔径计算（tray-sizing / tray-rating），做炼油常压塔与石油馏分切割的起始点。 |
| 14 | 减压蒸馏 | `Getting Started/Petroleum/vacuum.bkp` | 3 | 11 | 21 | BK10 | ENGPETRO | 减压塔（真空操作 + 汽提蒸汽）。做减压深拔 / 真高空塔的参考。 |
| 15 | Design-Spec 教学 | `Getting Started/Process/mchspec.bkp` | 1 | 3 | 4 | UNIFAC | ENG | 最小 RADFRAC 流程上挂 Design-Spec（用回流量调产品纯度）。做「设计规范收敛」建模的最小示例。 |
| 16 | Sensitivity 教学 | `Getting Started/Process/mchsens.bkp` | 1 | 3 | 4 | UNIFAC | ENG | 同上流程挂 Sensitivity 分析。做工况扫描 / 灵敏度分析的模板（本库 38 个文件含真实 Sensitivity 对象）。 |
| 17 | 氢气深冷液化 | `Hydrogen/Liquefaction/H2 cryogenic process.bkp` | 62 | 15 | 96 | HYSPR | H2 | 62 单元 / 96 流股，MHEATX 多股流换热 + 多级压缩 + 节流膨胀 + 低温闪蒸，最低 -252 °C。做深冷 / 液化 / 多股流换热网络的顶级模板。 |
| 18 | 级联制冷预冷 | `Hydrogen/Liquefaction/Cascade mixed refrigerant (CMR) precooling.bkp` | 18 | 10 | 29 | HYSPR | H2 | CMR 级联混合制冷剂预冷流程。做制冷循环 / 混合工质配比类问题的模板。 |
| 19 | TEG 天然气脱水 | `Midstream/Dehydration/teg.bkp` | 1 | 21 | 4 | SR-POLAR | ENG | 单塔 RADFRAC 吸收脱水 + 再生回路，21 组分。做天然气 / 气体脱水（TEG/MEG）的标准模板。 |
| 20 | NGL 回收 | `Midstream/NGL/ngl.bkp` | 6 | 16 | 11 | RK-SOAVE | ENG | MHEATX + 多级压缩/膨胀 + 闪蒸的轻烃回收流程。做天然气凝液回收 / 透平膨胀机流程的模板。 |
| 21 | MMA 聚合（间歇动力学） | `Polymers/pmma.bkp` | 2 | 5 | 4 | POLYNRTL | MET | RBATCH 间歇反应器 + 自由基聚合动力学（POLYNRTL 物性）+ FLASH2。做聚合动力学建模 / 聚合物体系物性设置的模板。 |
| 22 | 聚苯乙烯连续聚合 | `Polymers/Polystyrene/ps.bkp` | 6 | 8 | 10 | POLYNRTL | METCBAR | 连续搅拌/管式聚合 + 脱挥。做连续聚合 + 单体脱除的参考。 |
| 23 | IGCC 全流程 | `Power/Coal Gasification/igcc.bkp` | 282 | 45 | 256 | PENG-ROB | ENG | 本库规模之最：282 单元 / 256 流股 / 45 组分 / 186 条连接，含气化、净化、联合循环。做超大型全流程的规模上限参考与分层（HIERARCHY）组织方式参考。 |
| 24 | NGCC 联合循环 | `Power/Gas Turbine/Natural Gas Combined Cycle (NGCC) Power Plant.bkp` | 31 | 11 | 51 | PENG-ROB | US-2 | 31 单元燃气-蒸汽联合循环电厂。做动力循环 / 余热锅炉 / 蒸汽循环的模板。 |
| 25 | KCl 结晶 + 干燥 + 经济性 | `Solids Modeling/Potassium Chloride and Economics/1. Potassium Chloride Crystallization_BaseCase Demo.bkp` | 33 | 8 | 43 | ELECNRTL | REPORT | CRYSTALLIZER + CFUGE + DRYER + SCREEN/CLASSIFIER + CRUSHER 的结晶后处理全流程，并带经济性评估。做结晶-分离-干燥-造粒类固流程的主模板。 |
| 26 | 带式干燥 | `Solids Modeling/Belt Dryer/1 Belt Dryer Base Case.bkp` | 27 | 3 | 40 | IDEAL | SI | 27 单元带式干燥机（多段空气/固体换热）。做对流干燥 / 干燥机选型的模板。 |
| 27 | 生物柴油 | `Biofuel and Biochemicals/Biodiesel/Biodiesel Production from Vegetable Oil.bkp` | 16 | 39 | 27 | UNIF-DMD | SET1 | EXTRACT 萃取 + RADFRAC 精馏 + 39 组分甘油三酯体系。做油脂转化 / 生物柴油 / 液液萃取耦合精馏的模板。 |
| 28 | 硫酸体系电解质物性 | `Fertilizers/Sulfuric Acid/Aspen_Plus_H2SO4_Model.bkp` | 1 | 8 | 4 | ENRTL-SR | SI | **注意：只有 1 个 FLASH2（ABSORBER），不是硫酸全流程。** 价值在于 8 组分的硫酸电解质体系定义（H₂O / H₂SO₄ / H₃O⁺ / HSO₄⁻ / SO₄²⁻ / SO₃ / H₅O₂⁺ / H₂S₂O₇）与 CHEMISTRY 设置，90 °C / 2 kg/cm²。做硫酸、磷酸等无机酸电解质建模的物性起点。 |
| 29 | 溶剂回收 | `Pharmaceuticals/solvent.bkp` | 3 | 3 | 8 | NRTL | ENGPHARM | MIXER + RADFRAC 的小规模溶剂回收。做医药/精细化工溶剂回收的轻量骨架。 |
| 30 | 结垢预测 | `Upstream/Aspen_Plus_Scaling_Model.bkp` | 1 | 30 | 3 | ENRTL-RK | SI | 30 组分的电解质结垢模型（单 FLASH2）。做油气田水结垢 / 无机沉淀平衡建模的模板。 |

### 4.1 换物性方法 / 换溶剂的同构变体（最省事的复用方式）

- **胺法脱碳（ELECNRTL，15 个）**：`Carbon Capture\Amines ELECNRTL\` — AMP / DEA / DEA+MDEA / DGA / DIPA / K2CO3 / MDEA / MEA / MEA+MDEA / NaOH / NH3 / PZ / PZ+MDEA / PZ+MEA / TEA。结构同构（4 单元），只换胺种与 CHEMISTRY。
- **胺法脱碳（ENRTL-RK，11 个）**：`Carbon Capture\Amines ENRTL-RK\` — DEA / DGA / DIPA / MDEA / MEA / NH3 / PZ / PZ+MDEA / TEA + Sulfolane-DIPA / Sulfolane-MDEA。结构比上组更完整（10 单元，含贫富液换热），是「同一流程换物性方法 + 换溶剂」的双对照。
- **PVT 实验回归（30 个）**：`PVT Experiments\` 下分 PR / SRK / PC-SAFT 三套，每套 6 组实验（Constant Mass Expansion、Constant Volume Depletion、Differential Liberation、Separator Test、Swelling Test、Viscosity）；PR 与 SRK 套每组再分 Step I / Step II。是「同一组实验数据、换状态方程做参数回归」的标准对照集。
- **间歇精馏**：`Batch Modeling\Batch Distillation\` 下 13 个文件，同为 BATCHSEP 单塔结构，差异只在物性与进料：Benzene-Toluene / Hept-Hex-Oct / 3phase / Azeotrope / Water-Methanol / SolventSwap / ReactiveDistillation 等。
- **固流程**：`Solids Modeling\` 下 22 个文件覆盖破碎、筛分、造粒、流化床、闪蒸干燥、带式干燥、喷雾干燥、气力输送、结晶，可按需拼接。

## 5. 给 AI 建新模型时的检索建议

1. **先按「流程类型 + 物性方法」两维检索**，不要只匹配单元操作名。例如「胺法脱碳」应命中 `ELECNRTL/ENRTL-RK + RADFRAC(Rate-Based)`，而不是泛泛的 RADFRAC。
2. **优先复用同构变体**（见 4.1）。换胺种、换状态方程、换进料这三类改动，在同目录里几乎都有现成答案，比从零搭可靠得多。
3. **注意示例库的分布偏差**：ENRTL-RK / PC-SAFT / POLYNRTL 的高占比是 Carbon Capture、PVT、Polymers 三个目录堆出来的，不代表通用化工体系。
4. **大流程不要照抄 igcc**：282 单元 / 186 连接的模型适合查「有没有某种单元的用法」，不适合当起手模板；同类问题优先看 `cogeneration`（57）或 `H2 cryogenic process`（62）。
5. **单位集优先选 SI / METCBAR / ENG**：三者覆盖 114/203（56%）的示例，其余 30 余种为自定义集，复用前需先确认单位含义。

---

_本文件由 `_workshop/build_library.py` 从 `_workshop/_pattern-raw.json` 自动生成；逐文件明细见 `_workshop/pattern-index.csv`。_
