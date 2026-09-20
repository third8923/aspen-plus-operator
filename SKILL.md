---
name: aspen-plus-operator
description: Aspen Plus V14 自动化建模、COM 批量求解、bkp 文本层诊断与单位代码破译技能（生产实战沉淀）。用 COM 驱动引擎批量建模/工况扫描/参数寻优、bkp 文本层诊断修复、Excel 三插件（ASW/APXL/Calc+VBA）联动、GUI 启动与排错验证；独家包含 bkp 单位代码字典（<维度> <子码> 两级结构，203 个官方 bkp 实测）、COM 单位安全读写（UnitString/SetValueAndUnit）、水饱和压 Psat 与全液相窗口判定；另含官方物性方法决策树（活度系数法 10 atm 上限警告）、203 个官方示例流程模式库、收敛失败诊断手册（CVSTAT/SENSSTAT 纯 COM 判定收敛）。适用于：Aspen 工况扫描、灵敏度分析、RStoic 固定转化率模型核查、反应器是否还有液相、精馏/水解/生物柴油流程模拟与降本增效、修损坏模型、读引擎报错定位根因、英制→SI 换算与国内口径汇报。触发词：Aspen、bkp、Aspen COM、Apwn.Document、Engine.Run2、RStoic、工况扫描、单位代码、汽化率、Psat、物性方法选择、不收敛、收敛诊断。
---

# Aspen Plus V14 操作技能（aspen-plus-operator）

本技能沉淀自脂肪酸产业链（精馏/水解/生物柴油）实际建模。只收录在本机（Aspen Plus V14，aspenONE V14 全家桶）跑通的经验；死路与弯路不记录。

## 通道选型（先选通道再动手）

| 通道 | 干什么 | 速度 | 典型场景 |
|-|-|-|-|
| COM 自动化 | Python 驱动本机引擎：开模型、改参数、运行、取数 | 最快（秒级/工况） | 批量工况扫描、参数寻优、自动出数（默认首选） |
| bkp 文本层 | 读写 bkp 文本：看结构、修损坏模型 | 即时 | 模型诊断修复、配置速查 |
| GUI 手工 | 在豆包虚拟桌面打开软件界面操作 | 慢 | 单点操作、教学演示、看引擎报错提示 |

- **通道分界（硬规则）**：GUI 操作必须启动在**用户可见的桌面会话**里（本机真实桌面与远程/虚拟桌面不是同一显示会话，启动错位置用户看不到窗口，等同白启动）；COM 操作才在本机后台运行。两者互不感知，以同一个 bkp 文件为交换介质。
- **WorkBuddy 环境下**：GUI 通道用 **`workbuddy-computer-use`** skill（点击/输入/截图）；
  `references/gui-operation.md` 里的「豆包虚拟桌面 / computer_use」是另一套 agent 环境的写法，已加适配说明。
- **报错文本优先用 COM 取**：`doc.Export(2, "<路径>.rep")`（HAPEXP_REPORT=2）或 `Export(6, …)`（RUNMSG），不必为一个弹窗开 GUI。
- 批量工作一律 COM；只有看报错提示/单点演示才开 GUI。
- GUI 启动必须遵守「GUI 启动纪律」（见 references/gui-operation.md）——**禁止用 Bash 直接启动本地 GUI，也禁止把 GUI 启动在本机真实桌面**（用户不可见，等同无效操作）。

## 工作流

1. **定位模型文件**：`.bkp`（文本，可直接读）。官方完整模型与文本修补模型均可。
   - **建新模型前**：先查 `references/pattern-library.md` 检索同类流程模式与可复用模板（203 个官方 bkp 已结构化）；
     物性方法查 `references/property-method-decision.md` 的官方决策树，**别凭印象选**。
   - **读已有模型的拓扑**：`FLOWSHEET GLOBAL` 段的 `BLOCK BLKID/BLKTYPE/IN/OUT` 自带权威连接关系
     （203 个官方 bkp 中 129 个可反推），比关键词猜连接可靠得多。
2. **COM 驱动**：读 `references/com-automation.md`，按「连接 → 改参数 → Reinit → Run2(1) → 轮询 IsRunning → 取数」协议执行。运行序列不能错，漏 Reinit 引擎空转。
3. **bkp 诊断**：引擎报错（如 ZERO FEED TO THE BLOCK、Required input incomplete）先看 bkp 文本与 GUI 报错对话框，定位根因再改，禁止瞎试参数。见 `references/bkp-diagnostics.md`。
4. **取数换算（单位制，2026-09 复核版）**：Aspen 原生支持 SI，但**别靠"单位集"猜单位**。
   bkp 文本层每个数值自带 `<维度> <子码>` 两段代码（如 `<22><2>`=°F、`<22><4>`=°C、`<20><2>`=psi、`<20><5>`=bar），
   **代码是绝对值、可被单个参数覆盖**，单位集是 SI 的文件里也可能有 °F 参数。
   COM 侧 `IHNode` 有 `UnitString` / `ValueForUnit` / `SetValueAndUnit`（unitcol 是**整数代码**），
   **取数先回读 `UnitString`、写参用 `SetValueAndUnit` 显式给码**，不必死记换算。
   完整字典见 `references/units-codebook.md`，工具见 `scripts/aspen_units.py`。
5. **验证**：结果必须验证——GUI 报告与 COM 取数交叉核对；截图确认界面/弹窗；运行状态确认 converged 而非 ready-但空转。
   **纯 COM 判定收敛的入口**（看不到 GUI 时用）：
   `Tree.Data.Results Summary.Run-Status.Output` 下的 **`CVSTAT`**（流程收敛）/ **`SENSSTAT`**（灵敏度/设计规定），
   取值 `0`=通过 / `1`=错误 / `2`=警告。需要误差细节时把诊断级别调到 5 写 history file，读 `Max Err/Tol < 1.0`。
   详见 `references/convergence-playbook.md` §1.1、§2.2。

## 可复用脚本

- `scripts/aspen_com_run_si.py`：**COM 全 SI 封装模板（首选起点）**——业务代码只写 °C/bar/kmol/hr，`set_temp/set_pres/set_flow` 内部转英制；取数 `get_*` 直接返回 kg/hr/kW/°C（需模型 INSET=SI-CBAR）。已验证与引擎真数一致。
- `scripts/aspen_com_run.py`：COM 批量工况扫描模板（参数化：模型路径、要改的节点、要读的节点、工况表）。
- `scripts/aspen_units.py`：**单位代码工具**（`probe <bkp>` 统计代码分布、`inset` 查单位集、
  `sub_value()` 带单位码校验的文本替换、COM 侧 `set_value_with_unit` / `node_value_with_unit`）。
- `scripts/unit_convert.py`：英制→SI 换算函数库（温度/压力/流量/热负荷/密度/比焓，已逐项复核）。
- 实战生成器（<workspace>，水解体系示例）：
  - `gen_hydrolysis_f12.py`：单甘油三酯（TRIOLEIN）水解模型生成器（w_o/conv/T/P/flash 参数化）。
  - `gen_hydrolysis_mix.py`：**混合进料双甘油三酯水解生成器**（地沟油/皂角酸化油场景 × 进料温度 × 水油比 × 转化率），场景组成质量 % → 摩尔流量换算，双反应 TRIOLEIN+PPP 同时水解。
  - `com_run_mix.py`：COM 运行取数（流股 MASSFLOW3 组分、REACTOR QNET/R_TEMP、COOL QCALC，全容错 None）。
  - `scan_hydro_mix.py`：24 工况批量扫描 → CSV。

## 模块0 环境与界面地图（2026-09 实测）
- **模板库位置**：`C:\Program Files\AspenTech\Aspen Plus V14.0\GUI\Templates\`（.apt 文本，可读）。行业子目录：User/Chemicals/Gas Processing/Refinery/Mining and Minerals/Specialty Chemicals and Pharmaceuticals；另 `GUI\Stream Summary Templates\*.apsst`（物流报告模板）。
- **模板默认配置对比（实测）**：通用公制 INSET=METCBAR（bar）；化工公制 METCHEM；炼油公制 METPETRO；常减压 ENGPETRO + 物性 GRAYSON + 预置 8 组分（H2/N2/O2/H2S/CO2/C2A/C3A/NC4A）；生物过程 MET + 预置 8 组分（含 GLUCOSE/NH3）。通用/化工模板无预置组分。
- **GUI 六大表单 ↔ bkp 段映射（实证）**：
  | GUI 表单 | bkp 段 | 说明 |
  |-|-|-|
  | Setup（设置） | `? SETUP GLOBAL ?` | 标题、`"IN-UNITS" INSET=` 单位集、`"RUN-MODE" MODE=` |
  | Components（组分） | `? COMPONENTS MAIN ?` | 组分表 + DATABANKS（`AUTO-PARAM=YES`） |
  | Properties（物性） | `? PROPERTIES MAIN ?` | GPROPERTIES 物性方法、OPTION-SETS、X-PROPS |
  | Streams（物流） | `STREAM MATERIAL <名> ?` | 流股数据（TEMP/PRES/MOLE-FLOW） |
  | Blocks（单元） | `BLOCK <类型> <名> ?` | 块参数（PARAM/SPEC 等） |
  | Flowsheet（流程） | `FLOWSHEET GLOBAL ?` | 块清单 + IN/OUT 连接（BLKTYPE/MDLTYPE） |
- **模板即 bkp 基底**：新建流程最省事的方式 = 复制对应行业模板改组分，而不是空白新建（模板自带单位集/物性/报告设置）。

### 模块1 组分与物性（2026-09 实测）
- **三种组分定义写法（bkp 文本实证，生成器 ab_SRK）**：库组分 `CID = OLEIC ANAME = C18H34O2 OUTNAME = OLEIC DBNAME1 = "OLEIC-ACID" ANAME1 = "C18H34O2"`；别名写法 `CID = PPP ... DBNAME1 = "TRIPALMITIN"`（库名→自定义别名）；自定义组分 = 自定 ANAME/OUTNAME + DBNAME1（无库参数时依赖基团贡献估算，见下）。五件套（CID/ANAME/OUTNAME/DBNAME1/ANAME1）必须同步，缺一个引擎按旧分子式算 MW。
- **8 种物性方法适用边界（215°C/2.6MPa 水-油混合体系，同一模型只换物性，引擎真数）**：
  | 方法 | 类型 | 出口汽化率 | 适用性判定 |
  |-|-|-|-|
  | NRTL | 活度系数 | **0%（全液相）** | 高压含水优先（与蒸汽表自洽） |
  | STEAMNBS | 蒸汽表 | 0% | **仅纯水体系**，混合体系结果不可信 |
  | IDEAL | 理想 | 0% | 只有定性参考，无活度/逸度校正 |
  | SRK / RK-SOAVE | 状态方程 | 68.7% | 高估近饱和水汽化 |
  | PENG-ROB | 状态方程 | 72.7% | 同上 |
  | PR-BM | 状态方程 | 72.8% | 同上 |
  | UNIF-DMD | 基团活度 | **停算（None）** | PPP 缺 UFGPRD 基团参数（已知坑） |
  **铁律**：固定转化率模型（RStoic）中，物性方法**不影响产物组成**（8 方法 OLEIC 全部 1618.9 kg/hr 逐位一致），只影响相态/能耗/密度——所以"物性方法选错了结论只错在能耗与相态，不错在物料平衡"。
- **流股物性输出节点（COM 可读，ENG 单位）**：`Output\MASSFLOW\MIXED`=1 是报告开关 flag（不是流量）；`L1_FLOW`（总摩尔流 lbmol/hr）、`RHOMX\MIXED`（混合密度 lb/cuft，汽化率高时远小于液密度——0.063 vs 液相 0.4）、`L1_RHO`（液相摩尔密度 lbmol/cuft）、`VFRAC_OUT\MIXED` 均可读；**MW 读不到（None）**。
- **NRTL 二元参数来源**：切 NRTL 后引擎直接跑通（T1.2 实证）——库中 OLEIC/H2O 等常用体系二元参数由 Aspen 库自动提供（AUTO-PARAM），**无需手工回归**；Data Regression 只在库参数缺失/精度不足时用（需实验数据点，GUI Data Regression 表）。
- **电解质（T1.5）**：需要 ELECNRTL 物性 + Chemistry 向导生成电离反应，文本层手工加非常繁琐，GUI 依赖高——此类体系暂不需要，方法论记录即可。
- **基团贡献估算（T1.6）**：Aspen 对无库参数的分子结构用 UNIFAC 估算缺失物性；但基团参数缺失会**整体停算**（PPP 的 UFGPRD 即铁证）——自定义组分必须核对基团结构参数是否存在，别指望"估算"兜底。

### 模块2 单元操作全家桶（2026-09 实测，核心资产：标准块格式库）
- **块替换三件套（文本层换块类型的唯一正确方法，缺一无效）**：① 头部注册段 `>VERSION 0\n<块名>\n<GUI名>\nBuilt-In\n<图标>`（如 REACTOR→Pump→PUMP）；② FLOWSHEET 行 `BLKID/BLKTYPE/MDLTYPE/IN/OUT`；③ 块定义段 `? BLOCK <TYPE> <块名> ?`（**类型在前、块名在后**，写反被静默丢弃，引擎按旧块跑——曾误判多次）。只改①②引擎行为不变（块类型权威在③）。
- **标准块定义格式（从 Aspen V14 GUI\Examples 提取，可直接套用）**：
  | 块 | 格式要点 | 引擎实测 |
  |-|-|-|
  | PUMP | `PARAM PRES = X <20> <2> EFF = 0.7 <0> <0> OPT-SPEC = PRES` | ✓ 升压（90.4°F/500 psia） |
  | COMPR | `PARAM TYPE = ISENTROPIC OPT-SPEC = PRES PRES = X <20> <2> NPHASE = 2` | ✓ |
  | VALVE | `PARAM P-OUT = X <20> <2>`（**参数名 P-OUT 不是 POUT**） | ✓ 节流（90.6°F/300 psia） |
  | FSPLIT | `PARAM SID = "出1" FRAC = 0.5 <0> <0> / SID = 出2`（出2为余量） | ✓ |
  | MIXER | `PARAM VISITED = 1`（无参数也跑通） | ✓ |
  | FLASH2 | `PARAM TEMP/PRES ... SPEC-OPT = TP` + 段尾 `FRAC SUBSTREAM = MIXED` | ✓（ab_SRK SEP1） |
  | HEATER | `PARAM TEMP/PRES ... SPEC-OPT = TP` | ✓（ab_SRK COOL） |
  | FLASH3 | 需 `L2-COMP = <第二液相组分>` + SPEC-OPT = TP，三出口均需定义 | ✗ SRK 三相难收敛，建议 GUI 或双 Flash2 替代 |
  | SEP | `PARAM PARAM-STREAM = <目标流股> SUBSTREAM = MIXED COMPS = <组分> / ...` | ✗ 文本层易错，建议 GUI 或 Flash2 替代 |
  | HEATX | `PARAM SPEC = DUTY VALUE = X ... PROGRAM-MODE = DESIGN MODE = SHORTCUT` + `FEEDS FCOLD = ...` + `OUTLETS-COLD COLD-SID = ...` + `REFERENCE HOT-UTIL = HPS` | ✗ 需 utility 定义，建议 GUI |
  | PIPE | `PARAM LENGTH = X <17> <1> IN-DIAM = X <17> <7> OPT-OUTLET = STREAM` | ✓（2 英寸管 10m 压降 300+ psia 出口汽化，合理） |
  | REQUIL | `PARAM NREAC = 1 TEMP/PRES SPEC-OPT = TP` + STOIC 反应 + `EXTENT-SPEC ... DELT = 0.0 <31> <2>` | ✗ 文本层平衡不收敛，待 GUI |
  | RGibbs | `PARAM TEMP/PRES SPEC-OPT = TP` + `PRODUCTS SID = ...` | ✗ 同上 |
  | RCSTR | `PARAM SPEC-TYPE = "RES-TIME" TEMP/PRES SPEC-OPT = TEMP` + `PRODUCTS` + `REACTIONS RXN-ID = (...)`（需动力学） | 格式已验证 |
  | RPLUG | `PARAM TYPE = ADIABATIC LENGTH/DIAM/NPHASE/PHASE/NPOINT` + `PRODUCTS` + `REACTIONS` | 格式已验证 |
- **引擎实测物理规律**：液体进料过 PUMP 温升极小（90→90.4°F）、COMPR 液体压缩温升小（液不可压）、VALVE 节流 377→300 psia、FSPLIT 无压降、PIPE 压降与管径强相关（2in 管 10m 压降 300+ psia 出口汽化）。
- **停算判读**：文本层替换后流股 Output 全 None = 块参数格式不被接受（"Required input incomplete"）→ 先核对标准格式（见上表），再考虑 GUI 补参；不要盲改参数。
- **示例模型库位置**：`C:\Program Files\AspenTech\Aspen Plus V14.0\GUI\Examples\`（**203 个 bkp**，24 个分类，含生物柴油/水解/精馏等工业案例）——块格式、Design-Spec、Sensitivity 等现成写法从这里抄，别自己发明。

### 模块3 收敛与优化（2026-09 实测）
- **DESIGN-SPEC 完整格式（生物柴油示例，可直接套）**：`? "DESIGN-SPEC" <名> ? ; "SET1_MOLE" ; \ DEFINE FVN = <变量> FVN-VARTYPE = "MASS-FRAC" FVN-STREAM = <流股> FVN-SUBS = MIXED FVN-COMPONEN = <组分> \ \ SPEC EXPR1 = "<变量>" EXPR2 = "<目标值>" \ \ "TOL-SPEC" TOL = "<目标值>*1.0E-4" \ \ VARY VARY-VARTYPE = "STREAM-VAR" VARYSTREAM = <操作流股> VARYSUBS = MIXED VARYVARIABLE = "MASS-FLOW" VARYUOM = "kg/hr" \ \ LIMITS LOWER = "10" UPPER = "1000" \`。四段式：DEFINE（被控量）→ SPEC（目标）→ VARY（操作量）→ LIMITS（限幅）。示例控制"反应器出口甲醇质量分数=0.092，变甲醇进料流量"。
- **CONVERGENCE（T3.1，循环流股收敛）格式**：`? CONVERGENCE BROYDEN "C-1" ? \ TEAR SID = <撕裂流股1> / SID = <流股2> \ \ SPEC SPECID = <关联的 DESIGN-SPEC> \`。方法名（BROYDEN/WEGSTEIN/NEWTON/DIRECT）+ TEAR 撕裂流股 + 可选关联 SPEC。无循环流程不需要收敛段（默认序贯模块法）。
- **灵敏度引擎实测（T3.3，9 工况，COOL 热负荷 Btu/hr）**：FEED 温度 46/77/104°F 下结果**逐位相同**（-1270296/-815755/-807513）——**等温 RStoic 反应器把进料都加热到反应温度，抹平进料温度差异，反应器后冷却负荷与进料温度无关**；压力 2.6→4→6 MPa 时 COOL 负荷 -1270296→-815755→-807513——压力主导（汽化潜热 vs 显热）。推论：进料温度差异的显热体现在 REACTOR 的 QNET（预热段），不在 COOL；用 COM 双层循环（温度×压力）做灵敏度是标准做法。
- **Calculator（T3.4）**：ab_SRK 生成器内建 Calculator F-1（"Pressure Drop of block COOL = 1e-9 × Volumetric flow of REAC-OUT"）随模型跑通——计算器在文本层/生成器中可用；独立段格式 `? CALCULATOR <名> ? ; <流股类> ; \ DEFINE ... \ F ... \ EXECUTE ...`。
- **Optimization（T3.5）**：Aspen 优化器（GUI Flowsheet → Optimization）以 Design Spec/Calculator 变量构造目标函数+约束；文本层 OPTIMIZATION 段格式与 DESIGN-SPEC 类似（目标函数表达式 + 约束 + 变变量）。实际寻优用 Python COM 外循环更灵活（目标函数用引擎真数，约束在脚本内实现），GUI 优化器仅适合单目标小问题。
- **多工况并行（T3.6）**：批处理模式即多工况引擎（COM 循环 + 每 ~12 工况重开 doc 防 RPC 错误）；可复制多个 doc 会话并行（许可允许时）。

### 模块4 动力学与高级反应（2026-09 实测）
- **POWERLAW 动力学段完整格式（生物柴油酯交换三步可逆动力学，Aspen 官方示例，可直接套）**：`? REACTIONS POWERLAW "PALM-OIL" ? ; "SET1_MOLE" ; \ REAC-DATA R-D-REACNO = 1 R-D-CBASIS = MOLARITY PRE-EXP = 0.0231107550 <0> <0> ACT-ENERGY = 13500.0 <39> <3> T-REF = 50.0 <22> <4> \ ...`（5 个反应，每个 R-D-REACNO 一条：浓度基准 MOLARITY、指前因子 PRE-EXP、活化能 ACT-ENERGY（cal/mol）、参考温度 T-REF（°F）。）RStoic→RCSTR/RPlug 的升级路径 = 加这段 + 块定义 `REACTIONS RXN-ID = ("PALM-OIL")`。
- **官方示例 Biodiesel Production from Vegetable Oil.bkp 引擎实测**：`GUI\Examples\Biofuel and Biochemicals\Biodiesel\`（含 PDF 说明书）。OIL/MEOH/REACOUT 流股跑通（RCSTR 酯交换动力学段 OK）；**DECANTEROUT 之后全 STOP——官方示例的 DECANTER 在我们的物性环境下也崩**（再次印证 T4 结论：DECANTER 需 LLE 参数，此示例自带 DECANTER 但需要其物性设置，复用时注意）。
- **T4.3 逆流水解塔**：工业 96%+ 靠多级逆流（塔内局部低甘油浓度）。建模路径：多级 RStoic/REquil 串联（每级产物甜水移出 + 补新水）或用 RPlug 轴向模型；单级反应器平衡上限即 Lascaray 上限（水油比 1.2→93.8%），超过必须逆流。下一步建模建议用"3 级逆流串联 + 甜水虚拟分离"最简实现。

### 模块5 特殊体系（2026-09 方法论记录，暂不急需）
- **T5.1 电解质**：ELECNRTL 物性 + Chemistry 向导（GUI 生成电离反应与组分），文本层手工极繁琐——脂肪酸盐皂化/中和等体系如涉电解质再走 GUI 向导。
- **T5.2 固体**：Solids 模板 + 固体物性（PSD 粒径分布），RStoic/RCSTR 可处理固体组分（CI-SOLID 流类型）；暂不涉及。
- **T5.3 石油假组分**：Petroleum 模板（METPETRO/ENGPETRO + GRAYSON 物性 + 预置 8 组分）用 Assay 向导（TBP 蒸馏曲线）生成假组分——炼油/油品体系入口；脂肪酸/油脂体系用真实组分建模更准，不需要假组分。

### 模块6 经济与能量（2026-09 实测）
- **T6.1 夹点分析**：Aspen Energy Analyzer（GUI 插件）做换热网络；文本层不涉及——需要时开 GUI。
- **T6.2 资本评估 APEA**：Aspen Process Economic Analyzer（GUI）按设备尺寸估投资；方法论记录，用真数据时再开。
- **T6.3/T6.4 经济性汇总方法论（口径已对齐）**：精馏（卡 D 压 RR）蒸汽节省、水解收率提升、甲醇回收三条收益线；价格均为可配置输入（当地市场价/模拟价），**结论看增量与量级而非具体金额**；敏感项 = 甲醇价、油酸价、蒸汽价（±20% 敏感性区间）。
- **★ 量纲铁律（模块6 踩坑实录）**：蒸汽 kg/h → t/年 必须 **/1000**（×8000 h 后 ÷1000 才是吨）；元/t → 万元 再 /1e4。`kg/h × 8000 × 200 元/t` 会得到正确值 1000 倍的错误——曾算成 7.2 亿 vs 72 万元。年收益 = 流量(kg/h)×8000/1000×单价(元/t)/1e4。

### 模块7 工具联动（2026-09 实测）
- **本机已装 Excel 三插件入口**：`Aspen Excel Add-In Manager 64bit`（GUI 应用，Add-In Manager 管理 ASW/APXL/Calc+VBA 加载）；APXL 的 DLL 实证存在（`Aspen Properties V14.0\Engine\Xeq\APXLAddinLoaderx64.dll`）。ASW（Aspen Simulation Workbook）：GUI 内对模型建 Excel 工作簿，绑定变量后批量算（适合给不会用 Aspen 的人发"操作界面"）；APXL：Excel 直接调用属性数据（物性查询表）；Calc+VBA：Excel 宏里建 Calc 块驱动 Aspen。详见 references/excel-addins.md。
- **Python COM 全 SI 封装库**：`scripts/aspen_com_run_si.py`（业务层全 SI：set_temp °C/set_pres bar/set_flow kmol-h 内部转英制；get_* 返回 SI）——已就位，是 T7.4 的标准起点。
- **一键报告（T7.5）**：引擎真数 → 内联 SVG 单文件 HTML 报告生成器已验证（历史交付：水解工段最优生产方案.html 9 节 5 图）。

### 模块8 GUI 专项（2026-09 实测：启动可见成功、交互输入受限）
- **T8.1 GUI 启动已验证成功**：computer_use `list_apps` + `launch_app("Aspen Plus V14")` → 虚拟桌面截图确认窗口可见（`<无文档> - Aspen Plus V14 - aspenONE` 欢迎页，最近模型列表显示本机全部 _u_*.bkp）——GUI 启动纪律完整跑通一次。
- **本机 Aspen V14 全家桶（list_apps 实证，供"能用 Aspen 做什么"回答）**：Plus / HYSYS / EDR（换热器设计）/ Energy Analyzer（夹点换热网络）/ Process Economic Analyzer + Capital Cost Estimator + In-Plant Cost Estimator（投资估算）/ Excel Add-In Manager / OnLine（在线优化服务）/ Operator Training（OTS 仿真培训）/ Adsorption / Flare System Analyzer / Properties Desktop / Multi-Case（多工况）/ Batch Process Developer / AI Model Builder / aspenONE SLM License Manager（许可）。
- **T8.2 输入注入受限（环境边界）**：当前 VM 的 GUI 点击注入报 `Windows input injection failed`（历史已知：左键/截图可用，点击/热键常失败）——**GUI 交互操作受限时不要死磕**，排错回退 bkp 文本层 + 引擎行为（模块 2 方法论），GUI 只作"可见性/启动"验证。
- **REquil 停算根因（文本层排错实证）**：我的 REQUIL 段与官方示例（igcc.bkp）**逐位一致**（NREAC/TEMP/PRES/SPEC-OPT=TP/STOIC/STOIC1/EXTENT-SPEC DELT=0.0）→ 停算不是格式问题，是**高压水-油体系平衡计算的数值收敛/物性问题**（SRK 活度系数 + 三相）——平衡类块（REquil/RGibbs）对高压含水体系建议 GUI 或改用外部平衡迭代（技能 Lascaray 节）。
- **T8.3 虚拟桌面提速**：去桌面图标/壁纸、降分辨率（需用户在虚拟桌面设置操作，agent 不可直接改）；GUI 只做单点目标操作，批量仍走 COM。

### 模块9 综合实战（2026-09 实测）
- **T9.1 全厂集成衡算（三线一条主线）**：原料油→水解（油酸 1970 kg/h 引擎真数 + 甘油 ~204 kg/h）→精馏（精制油酸 D 采出）→酯化/酯交换（FAME 17685 kg/h 引擎真数 + 甘油副产）；副产甘油（水解+酯交换双来源）→蒸发浓缩→精甘油；回收线两条：甲醇回路（SEP1）+ 甜水甘油。集成汇报主线 = "蒸汽、收率、原料循环"。
- **T9.2 真实数据替换五步流程（建模完成后接真实数据的标准路径）**：① 数据清单（进料组分/流量/温度、塔压、水油比、转化率、产品规格——用户可对照收集）；② 单位制核对（DCS 读数 ℃/MPa/kg-h → bkp 英制 °F/psia/lb-h，用封装库转换）；③ 参数替换（COM 写 Input 或文本层）；④ 引擎重跑（Reinit→Run2）并验证收敛；⑤ 与 DCS 画面读数比对（如 215℃/1.84MPa 应逐位复现）→ 偏差>5% 查物性/进料口径。
- **T9.3 甘油精制蒸发模型（引擎真数，新建模型 `_u_GLY.bkp`）**：10% 甘油水溶液 220°F/14.7psia 蒸发 → 顶部蒸汽几乎纯水（甘油 9 vs 水 7077 lb/hr——甘油高沸点 290°C 不挥发）、底部浓缩液甘油浓度 **10%→50.2%**。一级蒸发脱水到 50%，工业精甘油 99% 需多效蒸发+真空精馏（下一级建模方向）。**块隐式流股教训**：模板里 FEED/REAC-OUT 由块 PRODUCTS/FEEDS 隐式生成、无独立 STREAM 段——加新流股要在显式流股段（如 RECYCLE）后插空壳定义，改 FEED 组分用 COM 树（`Data\Streams\FEED\Input\FLOW\MIXED\<组分>`），不要试图改文本 FEED 段。

### 模块10 版本演进与 V14 能力地图（2026-09 学习：本机官方帮助 26 份 What's New/Compatibility Notes）
- **版本认知（防坑）**：本机 V14 = **64 位程序**（Intel Fortran 2021 + VS2019 编译）——整厂大模型可行，第三方 Fortran DLL 必须 64 位编译（32 位 DLL 从 V11 起不可用）；AspenTech **从未发布 V13**（V12.2 2021-11 → V14.0 2022-11，网上"V13"多为误标）；bkp 文件头 `MM "40.0" VERSION "40.0"` 是**文件格式版本**不是产品版本——别用它判断文件存于哪个 Aspen 版本，判产品版本用 `Help|About`。
- **GUI 菜单路径映射（Ribbon 革命 V7.3.2，老教材路径全部失效）**：`Data|Model Analysis Tools|Sensitivity`→`Home|Analysis|Sensitivity`；`Data|Flowsheeting Options|Pres Relief`→`Home|Analysis|Pressure Relief`；`View|Control Panel`→`Home|Run|Control Panel`；`Tools|Options`→`File|Options`；`View|Model Library`→`View|Show|Model Palette`；Setup/Streams/Blocks 在左侧导航窗格同名节点。2011 年后出版的中文教材若写 V7 菜单路径、按书找不到菜单=正常，不是软件坏了；用官方映射表反查：`C:\ProgramData\AspenTech\Aspen Plus V14.0\HtmlHelp\Content\html\Mapping_of_Commands_to_the_Ribbon.htm`。
- **并行扫工况（Multi-Case，V12+）**：`Home|Multi-Case|Project` 或 Sensitivity 的 Vary 页 `Send to Aspen Multi-Case`；三种项目型：Case Study（敏感性分析升级版）/ Multi-File Analysis（多文件多拓扑）/ Reduced Order Model（生成数据喂 AI Model Builder）；结果可视化含二维/三维图与矩阵，不必导 Excel。**注意：独立许可产品**，需确认许可是否含。"水油比×温度×塔压"三维寻优最该用（当前 COM 串行 7 工况/20 分钟，Multi-Case 多核并行）。
- **AI Training（V12.1+，把"假设"变"实测"）**：`Home|AI Training`，流程：Excel/历史库导数据→Analyze Data（趋势线/箱线图/离群）→Build Model（自变量/权重/变量重要性）→Analyze Results（R²）；可反算**塔效率、传热系数、干燥速率**等暴露参数——水解工段把 DCS 进料量/塔温/塔压/甜水浓度按时间对齐导出，即可用 AI Training 反算真实反应接近度与塔效率回填严格模型（"先测别先改"的官方技术手段）。Excel 导入默认 FlexCel，可在 `Plant Data|Advanced|Options` 切回 Microsoft Excel。
- **碳核算（V14）**：`Setup|Emission Options`（独立面板）：scope 1 工艺排放 + scope 2 燃料/公用工程排放，支持 IPCC AR5/AR6，Utility 块可设 CO₂ 调整因子（反映绿电比例）——光伏/绿电评估可直接建模。V14 新增：生物组分库（BIOFEED/FERMENT）、发酵反应、Electrolyzer 电解槽+电力流股、聚合物热解反应、Makeup 补料单元、PubChem 在线检索、PURE40（DIPPR 2021 版）。可持续样本在 `GUI\Examples\`（100+ 样本，含 7 个可持续：MEA 碳捕集/生物燃料/碱性电解绿氢，均配 PDF 建模依据）。
- **兼容性机制（"同文件不同结果"三查）**：打开旧版本文件弹 **Upward Compatibility** 对话框——勾"Maintain Upward Compatibility"=忽略新特性、复现老结果（建议同时锁定数据库版本如 NISTV120）；不勾=用新特性拿新结果。**结果变了先查三件事**：① 兼容模式是否被勾选 → ② 数据库版本是否变化（V14 带 PURE40，基于 2021 DIPPR；可在 `Components|Specifications|Enterprise Database` 指定旧版）→ ③ 收敛路径不同（官方明示：难收敛流程跨版本"尤其可能收敛不同或干脆不收敛"）。**报告标注纪律**：每份正式报告模型页注明 `版本/物性方法/数据库`（如 V14.0 / UNIF-DMD / NISTV140），否则半年后自己都复现不了。
- **官方帮助文档库（离线，排错/学习第一手来源）**：`C:\ProgramData\AspenTech\Aspen Plus V14.0\HtmlHelp\`（113 个文档子系统/9764 页/338MB，免联网免账号）；26 份 What's New + Compatibility Notes（V7.3 起每代全保留）是版本差异的权威出处；`apwn.htm` 为总入口。HYSYS/Properties/EDR/经济评价等模块有各自的版本档案（7-44 份）。
- **历史遗留模型版本风险**：`水解工段_DCS基准.bkp` 用的 UNIF-DMD 物性/数据库在后续版本有更新——正是"同文件不同结果"的典型来源；正式报告必须标版本，否则无法复现。


### PPP/TRIPALMITIN 与 UNIF-DMD 的坑（已定位根因）
- **症状**：模型 Open/Ready/Reinit 全正常，Run2 后 IsRunning 短暂 True 后 False，所有流股 Output 全 None；GUI 控制面板报：
  `DORTMUND MODIFIED UNIFAC MODEL: GMUFDMD HAS MISSING PARAMETERS: UFGPRD ... MISSING FOR COMPONENT PPP; DEFAULTS NOT FOUND IN DATA BANK` → `Calculations stopped because of missing property parameters`。
- **根因**：TRIPALMITIN（CID=PPP, DBNAME1="TRIPALMITIN"）在 Aspen 库里**无 UNIFAC 基团结构参数（UFGPRD）**；UNIF-DMD 主方法做液相闪蒸（Flash2/SEP1 算 PHIMX）时必失败。组分定义本身没错（convtest 用 RCSTR 无闪蒸可跑）。
- **解决方案（已验证）**：GPROPERTIES `GBASEOPSET = "UNIF-DMD"` → `"SRK"`（同模型 SRK 下 24 工况全部收敛，物料衡算闭合）。SRK 对水-油体系精度略低于 UNIFAC，工程估算可用；要保 UNIFAC 精度需手写 UFGPRD 基团数据。
- 判别要点：**含新甘油三酯组分的模型若带 Flash2/闪蒸，先查 UFGPRD；组分只进 RCSTR/塔（无汽液平衡）时 UNIF-DMD 可能正常**。

### 引擎"运行 5 秒即停、无结果"的排查顺序
1. `tasklist` 查 `AspenPlus.exe -Automation -Embedding` 孤儿引擎进程（COM 会话残留，多个并存会占许可/资源）→ `taskkill /F /T /PID` 清理后重跑基线验证；
2. 确认基线模型（已验证模板）能跑，再用二分法定位模型差异（组分/反应/进料逐项加减）；
3. 最后才开 GUI 看控制面板具体报错（排错第一现场）。

### bkp 生成器防呆（踩过的坑）
- 替换 FEED 段时终点必须是下一个 `? STREAM MATERIAL`（如 RECYCLE），不是 `? "EO-VARS"`——用后者会连 RECYCLE 定义一起删掉；
- 反应器温度与进料温度是两个参数：RStoic PARAM TEMP=反应温度（如 215°C=419°F），FEED 段 TEMP=进料温度（随季节 8~32°C=46~90°F），别混用；
- 组分替换必须同步改 `ANAME / DBNAME1 / ANAME1` 三件套（PPP 定义：`CID = PPP ANAME = C51H98O6 OUTNAME = PPP DBNAME1 = "TRIPALMITIN" ANAME1 = "C51H98O6"`）。

### RStoic 水解模型的行为边界（实测）
- 反应器等温（固定 T/P）下，**出料组成只受转化率影响**；进料温度/水油比只影响热负荷与分离（进料温度影响预热能耗，水油比↑→QNET/QCALC↑）。
- 转化率 0.92→0.95：地沟油场景油酸 +15.8 kg/h（每 1000 kg/h 油脂基）、皂角 +10.0 kg/h；QNET 反而略降（未转化 TG 减少）。
- 水油比 3→5：QNET +34.7 kW（每 1000 kg/h 油脂基），冷却负荷同步上升——水油比是能耗杠杆。

### RStoic 固定转化率的物理局限（Lascaray 平衡，重要）- **RStoic 按指定转化率强行出料（物料守恒），不校验化学平衡**——低水油比下 92/95% 转化率是"不可能实现的假设"，引擎仍会跑出流股，易误导结论。
- **Lascaray (1952, JAOCS 29,362-366) 平衡关系**：平衡水解度只取决于甜水（水相）甘油浓度，与温度无关：`X_e = 1 − 0.8·y_ge`（y_ge=甜水甘油质量分数）。
- 平衡自洽迭代法（已验证）：conv 初值 → 引擎算甘油/水相水 → y_ge → X_e → 若 X_e<conv 则 conv=X_e 重跑，直至自洽。
- **量化结论（引擎真数，每 1000 kg/h 油脂基）**：
  - 原 24 工况 w_o=3/5/7（化学计量倍数，实际总水油质量比≈0.24/0.34/0.49）→ 平衡上限仅 **64.5% / 77.2% / 83.3%**（地沟油）；
  - 工业质量比 0.3/0.6/1.0 → 平衡转化率 **82.4% / 90.9% / 94.5%**（地沟油）、**86.0% / 92.7% / 95.0%**（皂角）；
  - **95% 平衡水解度需总水油质量比 ≈1.0–1.15**（目标 y_ge≈0.06）。
- **工业水油比（搜索核实）**：连续高压逆流水解油水质量比 1:0.4–0.6（专利）；脂肪酸工艺手册 0.8–0.85；酸化油 1:0.3；甜水甘油 10–25%。工业 0.4–0.85 能达到 96%+ 靠**逆流塔**（塔内局部低甘油浓度），单级反应器达不到——**模型升级方向：多级/逆流 + 平衡约束（REquil/RGibbs 或外部迭代）**。
- 修正结论：水解"转化率 0.92→0.95"方向仍成立，但**前提是水油比提到 ≥1.0 质量比**（或改逆流）；原"水油比 5→3 省能耗"结论重写为"在保证目标水解度前提下的最小水油比寻优"。
- 生成器已支持 `mode=mass`：第 8 参数传 `mass` 时 w_o 解释为**质量比**（kg 水/kg 油脂），与工业区间直接对照；默认 `mol` 为化学计量倍数（向后兼容 24 工况）。

### 流股汽化率读取（重要修正 + 汽化率-压力验证）
- **技能旧结论"流股 VFRAC 在 COM 树中不存在"已修正**：`Data\Streams\<名>\Output\VFRAC_OUT\MIXED` 与 `...\Output\B_VFRAC` **可读**（引擎运行后），直接给汽化率小数（如 0.787）；`TEMP_OUT\MIXED`/`PRES_OUT\MIXED` 也可读（419.0/267.0，英制）。流股结果不入 bkp 文本（VFRAC count=0），只能 COM 读。
- **汽化率-压力引擎验证（R=0.49 质量比、215°C、地沟油混合进料）**：1.84 MPa → VFRAC **0.787**；2.60 → 0.687；4.00 → 0.034；6.00 → 0.029。**结论：215°C 下水饱和压约 2.1 MPa，1.84 MPa 下反应器内约 8 成水汽化——非液相水解条件；全液相需 ≥4.0 MPa**（工业 Colgate-Emery 塔即 4–6 MPa）。**⚠ 此条为早期 SRK/UNIF-DMD 数据，"≥4.0 MPa"已被 NRTL 修正为 ~2.2 MPa（见"物性方法敏感性"节）；SRK 族对高压水体系系统性高估汽化，引用时以 NRTL + 蒸汽表为准。**
- **水油比口径陷阱（重要）**：同一"3:1"在水解原模型是**纯摩尔比（45 lbmol 油 : 135 lbmol 水 = 质量比 0.061，水零过量）**；在 gen_hydrolysis_mix 默认模式是**化学计量倍数（9:1 摩尔比 = 0.19 质量比）**。两者物理含义差 3 倍，引用/汇报前必须标注口径。水解原模型（bkp FEED 段 TRIOLEIN 45.0 + H2O 135.0 lbmol/h）经核验为纯摩尔比、质量比 0.061——比工业区间（0.4–1.5）低约一个数量级，且平衡水解度仅约 50%（Lascaray 校验）。

### 物性方法敏感性（2026-09 实测，决定性）
- **高压水-油体系（2–6 MPa）物性方法选择是生死线**：同一工况（215°C/2.6MPa/R=0.49）只换物性方法，出口汽化率 **0%～73%**：
  - SRK 68.7%、PENG-ROB 72.7%、PR-BM 72.8%、**NRTL 0%（全液相）**。
- **物理基准（蒸汽表，与模型无关）**：Psat(215°C)=2.104 MPa、Psat(205°C)=1.74 MPa。NRTL 结果与蒸汽表完全自洽（215°C 需 ~2.2 MPa、205°C 需 ~1.9 MPa 全液相）；SRK/PR 族对水近饱和区汽液平衡**预测偏差大、系统性偏保守**（放大 1.5–2 倍）。
- **工程结论**：高压含水体系优先 NRTL（活度系数）；用 SRK/UNIF-DMD 得到的"全液相压力"要按蒸汽表 Psat 复核，别直接采信。**"1.84 MPa 不够"（Psat>塔压）方向性结论不受物性影响**，但具体数量级（2.2 vs 3.5 vs 4.0 MPa）完全由物性方法决定。
- **bkp 文本替换物性的坑（本轮实测）**：必须同时改 `GPROPERTIES GBASEOPSET = "X" GOPSETNAME = "X"` 两处同名；只改 GBASEOPSET 时 GOPSETNAME 仍指向旧 OPTION-SETS，引擎照旧物性跑（四方法 VFRAC 逐位相同即铁证）。OPTION-SETS 段已有定义的方法（NRTL/UNIF-DMD/SRK/STEAMNBS）可直接切换；PENG-ROB/PR-BM 用内置名也生效。
- **零改造路线（NRTL 一体寻优 12 工况，全部现状可行）**：205°C/1.84MPa（DCS 现状）/R=1.2 → **VFRAC=0 全液相、conv 95.6%、油酸 753 kg/h、年收益 4195 万**；R=1.5 给 4221 万但水量偏大。215°C 需 2.2 MPa。**降温保液相 < 提压保液相**（Psat 随温度骤降），代价是动力学变慢需核停留时间。

### 批量多 bkp 处理（2026-09 实测）
- **框架**：COM 串行打开每个 bkp → Reinit → Run2 → 读流股关键值 → 汇总 CSV（每模型一条）。4 模型（水解校准版/精馏定案/生成器 2 例）约 2 分钟跑完。
- **状态判定**：流股 Output 有值 = OK；全 None = STOPPED（停算）。**BLKSTAT 不可用作收敛标志**（本机实测全为 0）。
- **混跑单位陷阱（重要）**：不同 bkp 单位集不同——精馏塔案例（ENG）读 `MASSFLOW3\OLEIC` 是 **lb/hr**（18756.90），水解校准版（SI-CBAR）读同字段是 **kg/hr**（1879.87）。批量汇总必须**记录每个 bkp 的 INSET**，按单位制换算对齐后再合并分析（读 Output 随 INSET 自动换算，但不同模型之间不互通）。
- **SRK 水饱和压低估第三实测点**：混合进料 205 °C / 1.9 MPa（纯水 Psat=1.74 MPa，本应全液相）SRK 给 VFRAC=0.755——坐实 SRK/UNIF-DMD 族对近饱和水体系系统性高估汽化，高压含水体系优先 NRTL。

### 错误诊断闭环与 COM 读错边界（2026-09 实测）
- **COM 引擎没有 `Errors`/`Messages`/`RunStatus` 属性**（实测不存在）；`eng.ControlPanel` 访问抛 com_error。
  **但报错文本可以拿到**：`doc.Export(2, "<path>.rep")`（`HAPEXP_REPORT=2`）或
  `doc.Export(6, "...")`（`HAPEXP_RUNMSG=6`）直接导出报告/运行消息文件读。
  （`IHAPEngine.ExportReport(filename, contents, object_id)` 是**三参数**，少传会报"无效的参数数目"。）
- **"没数"分两种，别混淆**：
  - **流股 Output 全 None = 引擎停算（有错）**：物性缺失/参数错误等，模型根本没算完；
  - **流股 Output = 0.0 = 跑通了但产物为零**：如零进料时 RStoic 静默输出 0，不报错。排错先区分这两种。
- **物性缺失闭环（T8 实测）**：ab_SRK 切 `UNIF-DMD`（GBASEOPSET/GOPSETNAME 两处同改）→ 引擎停算（REAC-OUT OLEIC=None）；文本层切回 `"SRK"` → 恢复，油酸 1618.87349 kg/hr 与基线逐位一致。文本层改物性是可靠通道，修坏即切回。

### 全液相窗口细扫与纯水 Psat 基准验证（2026-09 实测，决定性）
- **混合体系（R=0.206 校准版，低水油比）**：
  - **NRTL**：205/210/215/220 °C × 1.7/1.9/2.1/2.3/2.5 MPa **全部 VFRAC=0（全液相）**——混合物泡点压力远低于纯水（油酸/甘油降低水活度）。
  - **SRK 同模型**：215 °C / 1.84 MPa → **VFRAC=0.40**。同一模型只换物性，**0% vs 40%**。
- **纯水进料基准（NRTL, 215 °C）**：VFRAC 转折点在 **2.1→2.2 MPa**，与蒸汽表 Psat=2.104 MPa **自洽（偏差 <5%）**——证明 NRTL 水基准可信，混合体系全液相是真实的"混合物效应"，不是物性误差。
- **工程裁决**：低水油比 R=0.206 时汽化问题比 R=0.49 缓和得多（SRK 40% vs 57-67%），但**"是否全液相"仍由物性方法分叉（0 vs 40%），只能现场实测塔顶汽相流量裁决**；水多（R↑）则汽化加剧，加水与保液相必须同做。
- **校准版读输出直接 SI**：INSET=SI-CBAR 的 bkp，COM 读 `Output\TEMP_OUT\MIXED`=215.0（°C）、`PRES_OUT\MIXED`=18.409（bar）、`VFRAC_OUT\MIXED`=0.0 都是 SI——**读输出随 INSET 自动换算**（与技能单位制铁律一致）；写 Input 仍按引擎英制（TEMP 写 °F、PRES 写 psia，1 MPa=145.038 psia 勿写 14.5）。

### 混合进料组分扩展（2026-09：GUI 版文本补组分停算，用生成器）
- **坑（本轮实测）**：在 GUI 版 bkp 文本上补组分（COMPONENTS MAIN 段加 PPP、RStoic 加反应 2、FEED 加组分流量）后，**引擎整体停算**（所有流股 Output 全 None）——即使物性两处同改（GBASEOPSET/GOPSETNAME + X-PROPS BOPSETNAME）切 SRK 也一样。COMP-LIST/DATABANKS/物性段与可跑模板对比无差异，根因未完全定位（疑 GUI 版内部另有组分索引）。**教训：混合进料组分扩展一律在生成器模板（<workspace>/ab_*.bkp，从零生成、已验证收敛）上做，不要直接在 GUI 版 bkp 文本上补组分。**
- **混合进料组分比例敏感性（SRK 生成器，引擎真数，进料总甘油三酯摩尔恒定）**：
  | TRIOLEIN:PPP（lbmol/hr） | 油酸 kg/hr | 棕榈酸 kg/hr | 甘油 kg/hr |
  |---|---|---|---|
  | 1.78 : 0 | 1938.5 | 0 | 150.9 |
  | 1.42 : 0.36 | 1657.9 | 254.8 | 150.9 |
  | 1.07 : 0.71 | 1385.0 | 502.5 | 150.9 |
  **规律**：PPP 比例↑ → 油酸线性↓、棕榈酸线性↑；甘油只由总甘油三酯摩尔决定（恒定）。批次组分变化对产物组成的影响可用该线性规律快速估算，不必每批重跑引擎。

### DECANTER 液-液分离探索（2026-09：NRTL 体系跑不通，需 LLE 参数）
- **文本层加块格式（实测可写入）**：FLOWSHEET 段插 `BLOCK BLKID = DEC BLKTYPE = "DECANTER" ... IN = ( X ) OUT = ( OIL-PH WAT-PH )`，块定义段插 `BLOCK DECANTER DEC ? ; "ENG_MOLE" ; ; ICON1 ; \ PARAM TEMP = 104 <22> <2> PRES = 14.7 <20> <2> \ \ PRODUCTS PROD-STREAM = OIL-PH STAGE = 1 /  PROD-STREAM = WAT-PH STAGE = 1`，产品流股需在 STREAM 段预定义空壳。
- **失败根因**：NRTL 物性无液-液（LLE）二元交互参数时，DECANTER 导致**整个 flowsheet 失败**（连上游 RStoic 的流股 Output 都清空，不只是 DEC 自身无输出）——诊断特征：所有流股 MASSFLOW3 读回 None。解法：物性换 UNIF-LLE（带 LLE 基团参数）再试，或不用 DECANTER。
- **甜水分离工程近似（替代 DECANTER）**：用脚本按"甘油 100% 入水相、油酸/油入油相"虚拟分离即可。**油相带水敏感性**（R=0.49/conv0.855 引擎真数）：油相带水 0→20% 时甜水 y_ge 0.169→0.203、平衡上限 Xe 0.865→0.838——影响 <3 个百分点，**总产物 y_ge 近似足够工程用**，无需精确 LLE。

### 精馏塔操作规律（2026-09 引擎实测，12 板真空精馏塔）
- **收率唯一由塔顶采出 D 决定**（D 规格质量流量，kg/hr；bkp 单位代码 `<-80>`=kg/hr）：D=8000→49.8%、10000→62.6%、12000→76.3%、15000→96.0%（油酸收率 ≈ 线性，每 +2000 kg/hr 约 +13 个百分点）。
- **回流比 RR 对收率零影响**（1.5/2/3/4 实测收率恒定 62.6%）——RR 只增再沸能耗不增收率；操作最优 = 最低可行 RR。**"卡住 D、压低 RR"有定量铁证。**
- **板数 10/12/15 无差异**（62.7/62.6/62.5%）——12 板已到该体系分离极限，加板不提升收率。
- **纯度-收率权衡**：D 每增大，硬脂酸/棕榈酸被更多带入塔顶（D=15000 时杂质 4.3k lb/hr），油酸纯度约 85-87% 恒定区间内波动不大但杂质绝对量上升——按产品酸值指标选 D，不是越高越好。
- COM 读塔流股组分（MASSFLOW3）可靠；塔 Q1/Q2/板温等块 Output 在 GUI 版 bkp 的 COM 树读不到（返回 None/0），GUI 版块输出也不写入 bkp 文本——**精馏塔能耗需用 RR 代理或从流股焓另算，别在 COM 树里找塔热负荷**。

### 批次 RTO 寻优（多批次组分 × 进料温度，2026-09 实测 180 工况）
- **场景**：原料按批次进料（组分非简单混合）。对 批次组成 × 进料温度 组合寻优 水油比 R × 反应温度 T × 全液相压力。
- **实现**：每批次改写 FEED 全部组分节点（`Data\Streams\FEED\Input\FLOW\MIXED\<组分>`，lbmol/h = kg/h/MW×2.20462）+ H2O 按 R；RStoic 等温下**进料温度只影响 Q（预热显热），不必重跑引擎**，作为经济性快照（冬10/春秋25/夏40°C）即可——大幅省工况。
- **物性/压力**：NRTL，P 按温度档直接取实测最低全液相（205–210°C→1.90 MPa、215°C→2.20 MPa），不逐工况扫压。
- **180 工况真数结论**：
  - **最优操作参数对批次不敏感**：全部批次最优 = R=1.5 / T=205°C / P=1.9 MPa（Lascaray 平衡由水油比主导）。
  - 收益天花板由批次组分+原料价决定（皂角酸化油 4543 万最高，地沟油高酸 3699 万最低）；进料温度季节差约 **23 万/年**（预热显热）。
  - R=1.5 vs 1.2：收益 +7~43 万/年、油酸 +0.7%，但多 30% 水量（甜水成本未计）——有无甜水浓缩装置决定取舍。
- **经济性量纲铁律（踩坑）**：显热 q_heat [kJ/h] = (m_oil_kg×cp_oil + m_w_kg×cp_w)×ΔT，**不要额外乘 1000**（m 用 kg/h 时）；温差必须同单位制（°C−°C，禁止混入 104 这类华氏值）。写错一次收益差 1000 倍。

### 单位制切换实测（2026-09：Aspen 原生支持 SI，取数零换算）
- **Aspen 不是只能英制**：内置多套单位集，bkp 文本 `? SETUP GLOBAL ? \ "IN-UNITS" INSET = ENG \` 中 INSET 可切（ENG 默认）。本机 V14 已定义 MET、METCBAR、METCKGCM、**SI-CBAR**（`BASESET = SI`，描述 "International System Units with C, BAR, and /HR"）。
- **切换方法**：文本层把 `"IN-UNITS" INSET = ENG` 改为 `INSET = SI-CBAR` 保存即生效（无需 GUI）；GUI 路径 Setup → Units-Sets（或 Global Units 下拉）选 SI-CBAR；新建模板选带 Metric 的模板。
- **COM 读 Output 自动换算（实测对照，同一模型只切 INSET）**：
  | 读出项 | ENG | SI-CBAR | SI |
  |---|---|---|---|
  | 组分质量流 MASSFLOW3 OLEIC | 4144.4 lb/hr | **1879.87 kg/hr** | 0.5222 kg/s |
  | 摩尔流 L1_FLOW | 59.166 lbmol/hr | **26.837 kmol/hr** | 0.007455 kmol/s |
  | 热负荷 QCALC（COOL） | −1123542.9 Btu/hr | **−329277.9 W** | −329277.9 W |
  | 温度 R_TEMP（REACTOR） | 419 °F | **215.0 °C** | 488.15 K |
  | 汽化率 VFRAC | 无量纲不变 | 不变 | 不变 |
- **关键边界**：**Input 节点读回不换算**（FEED Input TEMP 在 SI-CBAR 下仍返回 220.6 = 220.6°F 原始存储值）→ **COM 写参数永远写英制**（bkp 内部存储英制），改参脚本里 °C→°F、MPa→psia 的换算不能省；只有**读 Output 可以免换算**（SI-CBAR 下直接 kg/hr/kW/°C）。
- **推荐口径**：脚本 `InitFromFile` 前先把 bkp 的 INSET 置 SI-CBAR（或保留 ENG 读 Output 后按旧换算表转），两种都行；SI-CBAR 最贴合国内（°C/bar/kg/hr），比手工换算快且少出错。注意 SI-CBAR 热负荷单位是 W（数值 = kW×1000，汇报时 /1000）。

### 平衡自洽引擎实测（2026-09，P0-1 修正 + 新发现）
- **外部自洽迭代法跑通**：给定 R → 引擎算产物甘油/水 → y_ge=甘油/(甘油+水) → X_e=1−0.8·y_ge → 若 X_e<conv 则降 conv 重跑，2 次收敛。
- **引擎实测平衡上限**（215°C/1.84MPa/NRTL，总产物 y_ge 口径，每 2135 kg/hr 油基）：R=0.206→**约 72%**、R=0.49→**约 86%**、R=1.2→**约 93.8%**（与技能旧插值 64.5/83.3/94.5% 同量级，引擎口径更准）。
- **两处模型超限（都要修正）**：
  1. DCS 基准 R=0.206 + conv 0.92：上限仅 ~72%，**0.92 物理不可达**（P0-1 实锤）；
  2. **零改造最优 R=1.2 + conv 95.6%：上限 93.8%，同样超限**——95.6% 是引擎按 RStoic 强制跑出的，实际应下调到 ≤93.8%，油酸约 753→739 kg/hr（每 1000 kg/hr 油基，−1.9%），收益结论需微调。
- **迭代算法注意**：只降不升会停在 conv<X_e 处（返回的是最后一次 conv 而非收敛点）；严谨做法是二分法在 conv 与 X_e 之间收敛（工程上取两者均值即可，误差 <3 个百分点）。
- **甜水 y_ge 口径**：用总产物甘油/(甘油+水)是乐观上界；真实甜水相（油相带走部分水）甘油浓度更高 → 平衡上限更低。要精确须先做 DECANTER 液-液分离再取水相 y_ge（见 T4）。

### 一体寻优（平衡×水油比×压力耦合，2026-09 已验证）
- **方法论**：决策变量 (T, R质量比)，约束 ① Lascaray 平衡自洽（引擎裁决 y_ge）② 全液相 VFRAC≤5%（压力步进扫描）③ 装置压力上限（现状 3.8 MPa）。目标 = 年净收益（产物×价 − 原料 − 蒸汽 − 冷却）。
- **实现（COM 会话复用，已验证 30 工况收敛）**：
  - 改参数节点（RStoic）：`REACTOR.Input\TEMP`/`PRES`/`CONV\1`/`CONV\2`、`FEED.Input\FLOW\MIXED\<组分>`（lbmol/h）、`FEED.Input\TEMP\MIXED`（°F）——同一 doc 内改参→Reinit→Run2 循环，**勿反复重开 doc**（重开有 RPC 内部错误风险）；每 ~12 工况可重开一次保险。
  - 平衡迭代：解析预解 conv 初值（物料守恒+Lascaray）→ 引擎在 6.0 MPa 全液相下复核 y_ge/X_e → 偏差 >1% 则用引擎值重跑一次（一般 1 次收敛）。
  - 压力扫描：6.0→5.0→4.0→3.5→3.0→2.6 MPa 降档，保留最后一个 VFRAC≤5% 的结果。
- **30 工况真数结论（SRK 版，已被 NRTL 修正，保留供对照）**：
  - 最优（SRK）：T=215°C、R=1.2、P≥3.5 MPa、conv=95.6%、油酸 753 kg/h、年净收益（模拟示例）。
  - **该压力结论被 NRTL 修正**（见"物性方法敏感性"节）：真实全液相 215°C≈2.2 MPa、205°C≈1.9 MPa，205°C/1.84 MPa 现状压力直接可行。
- **温度不是杠杆**：205–235°C 收益单调微降（升 T 只增显热成本，平衡不变）；205°C 因省蒸汽反高于 215°C。
- R=1.5 增量 +25 万/年但水量/甜水处理成本上升，最优实操点 R=1.2。
- **SRK 对水饱和压偏保守（已被 NRTL 节取代，保留一句）**：SRK/UNIF-DMD 的全液相压力值偏保守 1.5–2 倍，交付前按蒸汽表 Psat 复核。
- 经济性口径：净收益 = Σ(产物×价) − 原料油成本 − 蒸汽(理论显热/2200kJ·kg⁻¹) − 冷却(温升10°C)；反应热绝对值不可用（生成焓基准问题），只用显热。

## 参考文件（按需读取）

- `references/units-codebook.md` — **bkp 单位代码字典**（`<维度> <子码>` 两级结构，203 个官方 bkp 实测统计）
- `references/units-si-conversion.md` — SI 单位集切换、COM 单位 API、英制→SI 换算表
- `references/com-automation.md` — COM 连接、运行协议、变量读写矩阵、能力边界（接口签名以类型库为准）
- `references/bkp-diagnostics.md` — bkp 结构速览、进料段缺失修复、配置提取
- `references/excel-addins.md` — ASW / APXL / Calc+VBA 三插件选型与要点
- `references/gui-operation.md` — **GUI 启动纪律、排错、提速、验证**（重要，先读这条）
- `references/property-method-decision.md` — **物性方法选择决策树**（官方帮助原文还原 + 各方法 P/T 边界 + 官方警告）。选方法前读「①快速决策树」「②按体系推荐」两节即可
- `references/pattern-library.md` — **203 个官方 bkp 流程模式库**：单元操作频率、物性方法分布、高频拓扑组合、25 个可复用模板清单。建新模型前先来检索，别从零发明
- `references/pattern-index.csv` — 模式库逐文件结构化索引（203 行 × 8 维，UTF-8 BOM，Excel 可开）。**用 Python/Grep 查询，不要整体读**
- `references/convergence-playbook.md` — **收敛失败诊断与修复手册（72KB，最大）**：诊断决策树、错误消息对照、收敛参数调节、203 个 bkp 收敛配置实测统计。**务必 Grep 定位章节后定向读，禁止整体读入**

> 📖 **大文件读取纪律**：`convergence-playbook.md`（72KB）与 `pattern-index.csv`（45KB）体量大，
> 先 `grep -n "章节关键词"` 定位行号，再用 Read 的 `offset/limit` 定向读取，避免一次性吃掉几十 K token。

## 未决冲突（待实测裁定，不要当结论用）

- **物性方法与压力的冲突**：官方帮助称**活度系数法压力上限 10 atm、ENRTL-HF 仅 3 atm**，"高压"
  统一口径 >10 bar 应走高级混合规则 EOS（PRWS/PSRK/SR-POLAR）。而本项目用 **NRTL 跑 2–6 MPa**，
  超出官方口径 20–60 倍。官方同时明确 **SRK 须配 STEAMNBS**（方向上验证本项目判断），
  但"SRK 高估汽化率 1.5–2 倍"这个**定量数字官方帮助中查不到**，属本项目实测经验。
  → 交付结论前**必须做双方法对照并声明方法**，详见 `references/property-method-decision.md` 第⑤节。
- 官方帮助**未给出"高压 + 羧酸缔合"同时满足的现成方法**（HOC/NHT 是活度系数法配套，撞 10 atm 上限），
  属官方文档覆盖缺口。油酸体系选方法时须知悉此边界。

## 关键禁忌

- **GUI 必须启动在豆包虚拟桌面**（用户可见会话），禁止 Bash 直启、禁止启动在本机真实桌面（显示会话错位，用户/截图看不到窗口，会傻等/误排错）——必须 computer_use `list_apps` + `launch_app`，启动后截图确认窗口出现在虚拟桌面；不可见即视为失败，立即停手回退 COM，不得盲试。
- 禁止绕过运行协议（Reinit → Run2(1)）；漏 Reinit 引擎空转。
- 禁止把 COM 的 `Output\MASSFLOW=1.0` 当流量值（那是报告开关 flag）；组分流量读 `MASSFLOW3\<组分>`。
- 禁止在未看报错内容前反复试参数；报错先看 GUI 对话框 / bkp / 诊断信息。
- 流股 TEMP/PRES/ENTHALPY 在 COM 树中不存在，不要尝试读取；温度读上游块 Output（R_TEMP/TEMP，单位随单位集）；**VFRAC 可读**（`Data\Streams\<流股>\Output\VFRAC_OUT\MIXED`，单位集无关）。
- **bkp 单位代码是 `<维度> <子码>` 两级，维度不是单位**：`<22>`=温度（`<1>`K / `<2>`°F / `<3>`K / `<4>`°C）、`<20>`=压力（`<1>`Pa / `<2>`psi / `<3>`atm / `<5>`bar / `<10>`kPa / `<20>`MPa）、`<-80>` 质量流量、`<-89>` 摩尔流量。**不能由单位集推断代码**（存在 SI 文件里带 °F 参数），必须读数值自带的代码；`<20><2>` 与 `<20><5>` 差 14.5038 倍。详见 `references/units-codebook.md`。
- **COM 取数必须回读 `UnitString`**，写参用 `SetValueAndUnit(值, 整数码)`（不是 "C"/"bar" 字符串）；写完再回读校验一次。
- **MET 单位集的温度是 K 不是 °C**（METCBAR 才是 °C），两者只差一个压力单位却差 273。
- `Reinit` 在 `SuppressDialogs=True` 下优先 `Engine.Reinit()`（官方 V7.3 兼容性说明：`HappLS.Reinit()` 在抑制对话框时有不真正 reinit 的 bug）；`Run2` 一律写 `Run2(1)` 并轮询 `IsRunning`。
- 塔不收敛先查：进料温度是否高于轻组分泡点、D/RR 规格是否超出塔板能力（12 板油酸/硬脂酸体系收率只能到 50–76%）、重组分是否过重（MW>600 的甘油酯会使塔底温度爆表）。
- 组分替换必须同步改 `ANAME / DBNAME1 / ANAME1` 三件套，否则引擎按旧分子式算分子量，物料平衡假性错乱。
