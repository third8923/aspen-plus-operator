# Aspen Plus V14 物性方法（Property Method）选择决策树 — 本机知识提取

> **提取来源**：本机 Aspen Plus V14.0 离线帮助 `C:\ProgramData\AspenTech\Aspen Plus V14.0\HtmlHelp\`（12,594 个 HTML 文件，另含 Aspen Properties V14.0 镜像）。
> **标注约定**：
> - 【官方原文】= 直接译写自某一 HTML 文件的明确表述，注明来源文件
> - 【推断】= 由多份官方文档拼合的结论，注明依据
> - 【未找到】= 在本机 12,594 个帮助文件中全文检索无结果
>
> 核心官方文件（下文以短名引用，完整路径见 ⑥）：
> - **REF-CLASS**：`ref2\...\classificationofpropertymethodsandrecommendeduse.htm`（按应用领域的官方推荐总表）
> - **GUIDE**：`apr-ug2\...\guidelinesforchoosingapropertymethod.htm`（官方决策图 1，含 GIF 流程图 help0089_wmf.gif）
> - **GUIDE-POLAR**：`apr-ug2\...\guidelinesforchoosingapropertymethodforpolarnon_electrolytesystems.htm`（官方决策图 2，help0090_wmf.gif）
> - **GUIDE-ACT**：`apr-ug2\...\guidelinesforchoosinganactivitycoefficientpropertymethod.htm`（官方决策图 3，help0091_wmf.gif）
> - **PMA**：`props\Content\pma\*.htm`（Property Method Selection Assistant 交互式决策向导的 40 个节点页）
> - **CH2-\<名称\>**：`ref2\Content\html\` 下 Physical Property Methods Chapter 2 各方法详情页

---

## ① 快速决策树

### 1.1 官方决策图存在性确认

**找到了，共 3 张官方流程图 + 1 个交互式向导**（此前不确定是否存在，现已确证）：

| 资产 | 位置 | 形式 |
|---|---|---|
| 总决策图（极性/电解质/实虚组分/压力） | GUIDE 引用的 `apr-ug2\Content\image\help0089_wmf.gif` | GIF 流程图 |
| 极性非电解质决策图（压力/液液分层/参数可得性） | GUIDE-POLAR 引用的 `help0090_wmf.gif` | GIF 流程图 |
| 活度系数法细分图（汽相缔合/二聚） | GUIDE-ACT 引用的 `help0091_wmf.gif` | GIF 流程图 |
| Property Method Selection Assistant | `props\Content\pma\`（40 个节点页，GUI 内的交互向导） | HTML 链接树 |

GUIDE 原文（【官方原文】）：*"The following diagrams show the process for choosing a property method. Note: For a more detailed way of choosing a property method, including consideration of process type, use the Property Method Selection Assistant."*

### 1.2 决策图 1：顶层（help0089_wmf.gif，官方原文还原）

```
体系 → 极性？
├─ 极性 (Polar)
│   └─ 含电解质？
│       ├─ 否（非电解质）→ * 转决策图 2（极性非电解质）
│       └─ 是（电解质）→ ELECNRTL
└─ 非极性 (Nonpolar)
    └─ Real 还是 Pseudo 组分？
        ├─ Real → PENG-ROB, RK-SOAVE, LK-PLOCK, PR-BM, RKS-BM
        └─ Pseudo（假组分/石油馏分）
            └─ 压力？
                ├─ ≥ 1 atm → CHAO-SEA, GRAYSON, BK10
                └─ 真空 (Vacuum) → BK10, IDEAL
```
（来源：GUIDE 附属图 help0089_wmf.gif，逐节点转录）

### 1.3 决策图 2：极性非电解质体系（help0090_wmf.gif，官方原文还原）

```
极性非电解质 → 压力？
├─ P < 10 bar
│   └─ 是否出现液液两相 (LL)？
│       ├─ 是 → 有交互作用参数(IP)？
│       │    ├─ 有 → NRTL, UNIQUAC 及其变体
│       │    └─ 无 → WILSON, NRTL, UNIQUAC 及其变体
│       └─ 否 → UNIFAC, UNIF-LBY, UNIF-DMD（基团贡献预测）
└─ P > 10 bar
    └─ 有交互作用参数？
        ├─ 有（关联型模型 correlative）→ SR-POLAR, PRWS, RKSWS, PRMHV2, RKSMHV2
        └─ 无（预测型 predictive）→ PSRK, RKSMHV2
```
（来源：GUIDE-POLAR 附属图 help0090_wmf.gif，逐节点转录；图中原文即区分 "Y (correlative models)" 与 "N (predictive models)"）

### 1.4 决策图 3：活度系数法内部细分（help0091_wmf.gif，官方原文还原）

```
起点：WILSON, NRTL, UNIQUAC, UNIFAC
└─ 汽相是否存在缔合 (VAP)？
    ├─ 是 → 缔合度 (DPP)？
    │    ├─ 六聚体（HF 类）→ WILS-HF
    │    └─ 二聚体（羧酸类）→ WILS-NTH, WILS-HOC, NRTL-NTH, NRTL-HOC,
    │                          UNIQ-NTH, UNIQ-HOC, UNIF-HOC
    └─ 否 → WILSON, WILS-RK, WILS-PR, WILS-GLR, NRTL, NRTL-RK, NRTL-2,
             UNIQ-2, UNIQUAC, UNIF-LL, UNIF-2, UNIFAC, UNIF-LBY, UNIF-DMD
```
（来源：GUIDE-ACT 附属图 help0091_wmf.gif，逐节点转录）

### 1.5 Selection Assistant 文字版决策链（PMA 页面，官方原文要点）

- 入口二选一：按**组分类型**（Chemical / Hydrocarbon / Special / Refrigerants）或按**过程类型**（Chemical, Electrolyte, Environmental, Gas processing, Oil and gas, Petrochemical, Polymer, Power, Refining, Pharmaceuticals…）（PMA `Intro.htm`, `COMPONENTTYPE.htm`, `PROCESSTYPE.htm`）
- Chemical 体系高压判断的官方阈值：**"Is the system at high pressure (> 10 bars)?"**（PMA `CHEMSYSTEM.htm`）
- Chemical 低压：**"Use an activity coefficient method, such as NRTL, Wilson, UNIQUAC or UNIFAC"**；并提示需进一步考虑：羧酸、电解质、Henry 组分、HF、两液相（PMA `LOWPRES.htm`）
- Chemical 高压：**"Use an equation of state method with advanced mixing rules, such as the Wong-Sandler, MHV2 or Mathias-Klotz-Prausnitz mixing rules. Options include SR-POLAR, PRWS, RKSWS, PRMHV2, RKSMVH2, SRK, PSRK, HYSGLYCO, VTPR. …如果没有任何二元交互作用参数，用预测型方法如 SR-POLAR 或 PSRK"**（PMA `HIGHPRES.htm`）
- Gas processing：**"an equation of state-based property method is appropriate, such as PENG-ROB, SRK, PC-SAFT, or CPA"**；天然气贸易计量用 GERG2008（PMA `GAS.htm`）
- Water only：蒸汽表五选一 STEAM-TA / STEAM-NBS / STEAMNBS2 / IAPWS-95 / IF97，**"IAPWS-95 is the current standard for properties of water and steam and is recommended"**（PMA `WATERONLY.htm`）

---

## ② 按体系类型推荐表

以下全部为【官方原文】译写，主表出自 REF-CLASS（分类总表），细节行注明补充来源。

| 体系 | 官方推荐 | 来源 |
|---|---|---|
| **油藏/平台分离/管道输送**（Oil & Gas Production） | 高压烃类状态方程法（PR-BM, RKS-BM, BWR-LS, BWRS, LK-PLOCK） | REF-CLASS |
| **炼厂低压**（< 数 atm：减压塔、常压塔） | 石油 fugacity/K 值关联法（CHAO-SEA, GRAYSON, BK10）+ 实沸点蒸馏分析 | REF-CLASS |
| **炼厂中压**（< 数十 atm：焦化/催化分馏塔） | 石油 K 值关联法；石油调谐状态方程（BK10, CHAO-SEA, GRAYSON; [BK10/]） | REF-CLASS |
| **富氢环境**（Reformer / Hydrofiner） | GRAYSON；或 SRK / PENG-ROB | REF-CLASS；PMA `H2RICH.htm` |
| **炼厂高压加氢（含氢物流）** | 所选石油 fugacity 关联、石油调谐 EOS；中压含轻气体用 CHAO-SEA 或 GRAYSON | REF-CLASS；CH2-`bk10.htm` |
| **气体加工·烃分离**（脱甲烷塔、C3 分离器） | 高压烃 EOS **（带 kij）** | REF-CLASS |
| **深冷气体加工 / 空分** | 高压烃 EOS；柔性/预测 EOS | REF-CLASS |
| **乙二醇脱水** | 柔性/预测 EOS（专用：HYSGLYCO） | REF-CLASS；CH2 组表 |
| **酸性气吸收·甲醇(Rectisol)/NMP(Purisol)** | 柔性/预测 EOS（PSRK, SR-POLAR 等） | REF-CLASS |
| **酸性气吸收·水/氨/胺液/碱液/石灰/热碳酸钾** | **电解质活度系数法** | REF-CLASS |
| **胺液脱硫（MEA/DEA/DIPA/DGA）** | AMINES（Kent-Eisenberg）；或 ELECNRTL / ENRTL-RK | PMA `AMINES.htm`；CH2-`amines.htm` |
| **酸性水汽提（Sour water, H2O-NH3-CO2-H2S）** | APISOUR（快速）；"For more accurate results, use the ELECNRTL property method" | CH2-`apisour.htm` |
| **Claus 过程** | 柔性/预测 EOS | REF-CLASS |
| **乙烯装置** | 初馏塔 CHAO-SEA/GRAYSON；轻烃分离与急冷塔 PENG-ROB/RK-SOAVE | apr-ug2 `petrochemicals.htm` |
| **芳烃 BTX 萃取** | 活度系数法（WILSON/NRTL/UNIQUAC；官方特别注明"对参数极敏感"） | REF-CLASS |
| **MTBE/ETBE/TAME 醚化** | 活度系数法 | REF-CLASS |
| **羧酸（乙酸/脂肪酸）体系** | **活度系数法 + 汽相缔合模型：NRTL-HOC, WILS-HOC, UNIQ-HOC, NRTL-NTH, WILS-NTH**（"Organic acids such as acetic acid form dimers in the vapor phase and require special model"） | apr-ug2 `chemicals.htm`；PMA `CARBOXACID.htm`；决策图 3 |
| **醇-水/共沸分离** | 活度系数法：WILSON（"recommended for highly nonideal systems, especially alcohol-water systems"）、NRTL、UNIQUAC 及变体；初设可用 UNIFAC/UNIF-DMD | apr-ug2 `chemicals.htm`；CH2-`wilson2.htm`；PMA `CHEM.htm` |
| **酚/酯化液相反应** | WILSON, NRTL, UNIQUAC 及变体 | apr-ug2 `chemicals.htm` |
| **合成氨（高压含 N2/H2）** | PENG-ROB, RK-SOAVE（总表强调"with kij"） | REF-CLASS；apr-ug2 `chemicals.htm` |
| **无机酸碱（NaOH/硫酸/盐酸等）** | ELECNRTL；HF 体系用 ENRTL-HF | apr-ug2 `chemicals.htm` |
| **聚合物** | PC-SAFT, POLYNRTL, POLYFH, POLYSL, POLYSRK, POLYUF, POLYUFV, POLYPCSF, EPNRTL | PMA `POLY.htm` |
| **固体加工（煤/火法冶金）** | SOLIDS；水法冶金/浸出→电解质法 | REF-CLASS；CH2-`solidshandlingpropertymethod.htm`（"Hydrometallurgical applications cannot be handled by the SOLIDS property method"） |
| **蒸汽系统/冷却剂（纯水）** | STEAMNBS, STEAM-TA；推荐 IAPWS-95 | apr-ug2 `waterandsteam.htm`；PMA `WATERONLY.htm` |
| **含非传统组分（煤/生物质，NC 子流）** | 专用非传统组分焓模型（HCOALGEN 等） | apr-ug2 `propertymethodsfornonconventionalcomponents.htm` |

---

## ③ 各主要方法适用边界表

**活度系数法 vs 状态方程法的官方边界**：

- 【官方原文】液相活度系数法适用 **"nonideal and strongly nonideal mixtures at low pressures (maximum 10 atm)"**，且 **"These property methods are not suited for electrolytes … Model polar mixtures at high pressures with flexible and predictive equations of state. Non-polar mixtures are more conveniently modeled with equations-of-state."**（`ref2\...\liquidactivitycoefficientpropertymethods.htm`）
- 【官方原文】电解质法同样有压力上限："You can use these property methods at low pressures (maximum 10 atm)"；ENRTL-HF 更严：**maximum 3 atm**（`ref2\...\electrolytepropertymethods.htm`）
- 【推断】综合三处（决策图 2 的 "P > 10 bar" 分支、PMA `CHEMSYSTEM.htm` 的 ">10 bars" 提问、活度系数法 "maximum 10 atm" 上限）：**官方对"高压"的定义口径统一为约 10 bar（1 MPa）**；2–6 MPa 明确属于必须用状态方程法或高级混合规则的区间。官方**没有**给出"活度系数法 MPa 级精确上限"，10 atm/10 bar 是唯一量化口径。

### 单方法明细（全部【官方原文】，"Range / Mixture Types"栏目为 Chapter 2 固定栏目）

| 方法 | 模型构成 | 适用/范围（官方原文要点） | 来源 |
|---|---|---|---|
| **IDEAL** | γ=1 + 理想气体 + Rackett | 真空体系、低压同分异构体；汽相偏差仅在 **P ≤ 2 bar 或极高温** 时可容忍；"You should not use IDEAL for nonideal mixtures"；混合热为零 | `ref2\...\idealpropertymethod.htm` |
| **NRTL / UNIQUAC / WILSON** | 活度系数（+理想气体或 RK 汽相） | "can handle any combination of polar and non-polar compounds, up to very strong nonideality"；**参数须在操作 T/P/组成范围内回归，且任何组分不得接近临界温度** | `ref2\...\nrtl.htm`, `uniquac1.htm`, `wilson1.htm` |
| **WILSON 限制** | — | **"cannot handle two liquid phases"**（不能算 LLE，改用 NRTL/UNIQUAC）；特别推荐醇-水 | `ref2\...\wilson1.htm`, `wilson2.htm` |
| **NRTL-RK** | NRTL + RK 汽相 + Rackett + Henry | NRTL 系的水力口径方法；ELECNRTL 与之**完全自洽**（"fully consistent with the NRTL-RK property method"） | `props\...\nrtl_rkpropertymethod.htm`；`ref2\...\elecnrtl.htm` |
| **UNIFAC 族** | 基团贡献 + RK 汽相 | UNIFAC：**290–420 K（约 20–150 °C）**；UNIF-LL（LLE 参数集）：**280–310 K**；UNIF-DMD/UNIF-LBY/UNIF-HOC：290–420 K；"No component should be close to its critical temperature"；**"you should not use it for final design calculations"**（预测法仅宜初设）；"gas-solvent interactions are not predicted by UNIFAC" | `ref2\...\unifac1.htm`, `unifac_dortmundmodified_.htm`；`props\...\unifacpropertymethod.htm` |
| **PENG-ROB** | PR + Boston-Mathias | 非极性/弱极性烃+轻气体（CO2/H2S/H2）；"particularly suitable in the high temperature and high pressure regions"；**"reasonable results at all temperatures and pressures"**（临界区一致性，混合临界点附近最不准）；**必须配二元参数（PRKBV）否则 VLE/LLE 精度无保证** | `ref2\...\peng_rob.htm` |
| **RK-SOAVE (SRK)** | SRK | 与 PENG-ROB 对等；推荐 gas-processing/refinery/petrochemical；**"please select STEAMNBS as the free-water method. The NBS steam table provides greater accuracy and SRK is designed to work with it"**；配 Kabadi-Danner 混合规则可算水-烃不互溶（SRK-KD） | `ref2\...\srk.htm`；`props\...\srk.htm` |
| **PR-BM / RKS-BM** | PR/RKS + BM | 高压烃应用四件套（BWR-LS, LK-PLOCK, PR-BM, RKS-BM）；"can deal with high pressures and temperatures, and mixtures close to their critical point"；**立方 EOS 液相密度不准**；无拟合 kij 时临界区"no great accuracy should be expected" | `ref2\...\equation_of_statepropertymethodsforhigh_pressurehydrocarbonapplications.htm`, `rks_bm.htm` |
| **PSRK** | RKS + Holderbaum-Gmehling(UNIFAC) | 非极性+极性+轻气体；"up to high temperatures and pressures"；有 UNIFAC 参数即可预测；临界区最不准 | `ref2\...\psrk.htm` |
| **SR-POLAR** | RKS + Schwarzentruber-Renon | 非极性+极性+轻气体；**"fair predictions up to about 50 bar"**；"up to high temperatures and pressures" | `ref2\...\sr_polar.htm` |
| **RK-ASPEN** | RKS + Mathias 混合规则 | 小/大分子组合与富氢体系（如 N2–正癸烷）；高温高压 | `ref2\...\rk_aspen.htm` |
| **ELECNRTL / ENRTL-RK / ENRTL-SR** | 电解质 NRTL + RK | "the most versatile electrolyte property method…very low and very high concentrations, aqueous and mixed solvent"；**汽相性质"accurately up to medium pressures"**；参数应在操作范围回归；ELECNRTL 汽相不能描述羧酸/HF 缔合 | `ref2\...\elecnrtl.htm`, `ENRTL-RK.htm` |
| **PITZER** | Pitzer + RKS | 仅纯水溶剂，**"up to 6 molal ionic strength"**；"PITZER cannot be used for systems with any other solvent or mixed solvents" | `ref2\...\pitzer.htm`；`ref2\...\electrolytepropertymethods.htm` |
| **PC-SAFT** | Copolymer PC-SAFT | 聚合物/缔合体系；气加工选项之一（PMA `GAS.htm` 把它列为 gas processing 推荐）；CH2 页仅一句话描述 | `props\...\PC-SAFT_Property_Method.htm`；PMA |
| **CPA** | CPAs EOS | 非极性或**缔合**混合物（醇类）；"particularly suitable in the high temperature and high pressure regions"；"reasonable results at all temperatures and pressures" | `ref2\...\CPA_method.htm` |
| **STEAMNBS / STMNBS2 / STEAM-TA / IAPWS-95 / IF97** | NBS/NRC 1984；ASME 1967；IAPWS 1995 | 纯水/蒸汽全热力学性质；**STEAM-TA 与 STMNBS2 分区关联在边界不连续，"can lead to convergence problems and predict wrong trends"；STEAMNBS 无此问题、外推更好**；IAPWS-95 为现行标准 | `ref2\...\steamtables.htm`, `steamnbs_steamnbs2.htm`, `steam_ta.htm`；PMA `WATERONLY.htm` |
| **BK10** | Braun K-10 | **真空与低压（up to several atm）**；K10 图 133–800 K（可用至 1100 K）；高压改用石油调谐 EOS | `ref2\...\bk10.htm` |
| **CHAO-SEA / GRAYSON** | Chao-Seader / Grayson-Streed | 石油 K 值关联；含氢中压体系（Grayson 特别用于富氢） | `ref2\...\chao_seader.htm`, `grayson_streed.htm`；PMA `MEDPRES.htm` |
| **BWR-LS / LK-PLOCK** | BWR-Lee-Starling / Lee-Kesler-Plöcker | LK-PLOCK："reasonable results at all temperatures and pressures"；BWR-LS：中压内合理，**极高压力下可能预测出不真实的液液分层** | `ref2\...\lk_plock.htm`, `bwr_ls.htm` |
| **GERG2008** | 多参数 EOS（经 RefProp） | 天然气/LPG/LNG/氢-烃；正常范围 **90–450 K、p ≤ 35 MPa**；组分限于表列 21 种 | `ref2\...\GERG2008_Property_Method.htm` |

---

## ④ 官方警告与禁忌（逐条【官方原文】）

1. **活度系数法压力红线**："nonideal and strongly nonideal mixtures at low pressures (**maximum 10 atm**)"——`ref2\...\liquidactivitycoefficientpropertymethods.htm`
2. **电解质法勿用于非电解质**："**Do not use the electrolyte property methods for nonelectrolyte systems.**"——`ref2\...\electrolytepropertymethods.htm`
3. **电解质法压力红线**：max 10 atm；ENRTL-HF max 3 atm——同上
4. **柔性/预测 EOS 勿用于电解质**："The flexible and predictive equations of state are **not suited for electrolyte solutions**."——`ref2\...\flexibleandpredictiveequation_of_statepropertymethods.htm`
5. **PITZER 只能纯水**："cannot be used for systems with any other solvent or mixed solvents. Any non-water molecular components are considered solutes and treated as Henry components."——`ref2\...\pitzer.htm`
6. **UNIFAC 三禁**：不能用于最终设计（预测性）；组分不得接近临界温度；气-溶剂相互作用不可预测——`ref2\...\unifac1.htm`；`props\...\unifacpropertymethod.htm`
7. **WILSON 不能算 LLE**："cannot handle two liquid phases"——`ref2\...\wilson1.htm`
8. **立方 EOS 液相密度不准 + 临界区需拟合 kij**："Liquid densities are not accurately predicted for the cubic equations of state… Unless you use fitted binary interaction parameters, no great accuracy should be expected close to the critical point."——`ref2\...\equation_of_statepropertymethodsforhigh_pressurehydrocarbonapplications.htm`
9. **BWR-LS 极高压假分层**："At very high pressures, unrealistic liquid-liquid demixing may be predicted."——`ref2\...\bwr_ls.htm`
10. **STEAM-TA 分区不连续**："do not provide continuity at the boundaries, which can lead to convergence problems and predict wrong trends"；建议优先 STEAMNBS——`ref2\...\steamtables.htm`
11. **数据回归禁用 "-2" 方法**："Do not use property methods ending in -2 in Data Regression…用 UNIQUAC 回归的参数可直接用于 UNIQ-2"——`apr-ug2\...\selectingapropertymethod.htm`
12. **ENRTL-RK 与 ELECNRTL 不要混用**："Avoid using ENRTL-RK in the same problem with ELECNRTL, if the option Require Engine to use special parameters for electrolyte method is set…may be inappropriate to use with ENRTL-RK."——`ref2\...\ENRTL-RK.htm`
13. **回归与使用要同一方法**（HOC 类）：要用 UNIQ-HOC 计算就必须用 UNIQ-HOC 回归——`apr-ug2\...\selectingapropertymethod.htm`
14. **WATSOL/HCSOL 参数不可回归**（free-water/dirty-water 闪蒸选项不进回归）——同上

---

## ⑤ 本项目专项：2–6 MPa 高压含水油酸（脂肪酸）体系

### 5.1 官方对"高压含水"的直接依据

| 本项目原有认知 | 官方核验结果 |
|---|---|
| "NRTL 族与纯水蒸汽表自洽" | **部分证实、部分未找到**。【官方原文】只确认 *ELECNRTL 与 NRTL-RK 完全自洽*（分子相互作用计算方式相同，可共用二元参数库，`ref2\...\elecnrtl.htm`）；free-water 相可选 STEAMNBS 并注明比 ASME 更准（`apr-ug2\...\specifyingpropertiesforthefree_waterphase.htm`）。但**未找到**"NRTL 族在 2–6 MPa 与蒸汽表数值自洽"的成文说法。 |
| "SRK 族对水的饱和压力偏保守、汽化率高估 1.5–2 倍" | **定量数字未找到**。官方 12,594 个文件中无此量化表述。【官方原文】仅可佐证方向：SRK 页明确 *"please select STEAMNBS as the free-water method. The NBS steam table provides greater accuracy and SRK is designed to work with it"*（`props\...\srk.htm`、`ref2\...\srk.htm`）——即官方承认 SRK 对水性质的默认处理精度不足、必须挂 NBS 蒸汽表补救；含水体系建议改用 SRK-KD（Kabadi-Danner 混合规则处理水-烃不互溶）。"1.5–2 倍汽化率高估"属本项目实测经验，官方无对应文档。 |
| "UNIF-DMD 族对水不保守" | 【未找到】UNIF-DMD 的 290–420 K 参数范围（`ref2\...\unifac1.htm`）与"预测法不用于最终设计"是官方仅有的边界；关于水饱和压偏差无官方表述。 |

### 5.2 按官方决策树走本项目（推断，标注依据）

油酸+水体系、2–6 MPa（= 20–60 bar，超过 10 bar/10 atm 官方红线）：

1. 脂肪酸是**极性非电解质**（无盐、无离子化学）→ 走决策图 2（依据：决策图 1 的极性分支）。
2. P > 10 bar → 官方路线是**高级混合规则状态方程**：有交互参数 → SR-POLAR/PRWS/RKSWS/PRMHV2/RKSMHV2；无参数 → PSRK/RKSMHV2（依据：决策图 2；PMA `CHEM.htm`、`HIGHPRES.htm`）。SR-POLAR 官方精度承诺仅到约 50 bar（`ref2\...\sr_polar.htm`），2–6 MPa（≤60 bar）恰好压线，属官方边界内偏高端。
3. **脂肪酸缔合问题**：油酸在汽相二聚，官方明确羧酸需汽相缔合模型 HOC/NTH（PMA `CARBOXACID.htm`；决策图 3 的 "Dimers" 分支）——但 HOC/NTH 是活度系数法配套，撞上 10 atm 上限。**官方没有给出"高压+羧酸"两约束同时满足的现成方法**；此为官方文档覆盖缺口（【推断】：可用 PRWS/RKSMHV2 并把 UNIQUAC/NRTL 挂入 W-S 混合规则的能量项、或用 CPA 的缔合项近似处理，但这两条均在帮助中无"脂肪酸"字样直接背书）。
4. 水相性质：free-water method 官方口径是 STEAMNBS（SRK 体系强制）；IAPWS-95 为现行标准（PMA `WATERONLY.htm`）。若主方法选 EOS 族，free-water 挂 STEAMNBS/IAPWS-95 与官方做法一致。
5. 灵敏度建议（【推断】，非官方）：对本项目"汽化率对水饱和压敏感"的问题，可做双方法对照（ENRTL-RK vs PRWS+STEAMNBS）——ENRTL-RK 的 NRTL-RK 自洽性有官方背书，但其汽相 RK 的官方精度口径只有 "medium pressures"，6 MPa 已超官方承诺区。

### 5.3 示例库统计偏差提醒（用户侧观察）

"ENRTL-RK 出现 34 次居首、系 37 个 Carbon Capture 示例堆积所致"是**用户侧对示例库的统计**，官方帮助文档中没有方法使用频率统计，也无对此的解释或背书。本文档按原样记录为观察，不建议由该分布直接推出"ENRTL-RK 万能"的结论；且官方警告 ENRTL-RK 汽相精度仅 "medium pressures"（`ref2\...\ENRTL-RK.htm`），高压场景选它需谨慎。

---

## ⑥ 来源清单

基础路径：`C:\ProgramData\AspenTech\Aspen Plus V14.0\HtmlHelp\`（下表省略前缀）。Aspen Properties V14.0\HtmlHelp 下存在同构镜像（内容一致）。

**决策图与向导**
- `Subsystems\apr-ug2\Content\html\guidelinesforchoosingapropertymethod.htm`（GUIDE）
- `Subsystems\apr-ug2\Content\image\help0089_wmf.gif`（决策图 1 原图）
- `Subsystems\apr-ug2\Content\html\guidelinesforchoosingapropertymethodforpolarnon_electrolytesystems.htm`（GUIDE-POLAR）
- `Subsystems\apr-ug2\Content\image\help0090_wmf.gif`（决策图 2 原图）
- `Subsystems\apr-ug2\Content\html\guidelinesforchoosinganactivitycoefficientpropertymethod.htm`（GUIDE-ACT）
- `Subsystems\apr-ug2\Content\image\help0091_wmf.gif`（决策图 3 原图）
- `Subsystems\props\Content\pma\`：Intro / COMPONENTTYPE / PROCESSTYPE / CHEMSYSTEM / HCSYSTEM / HIGHPRES / LOWPRES / MEDPRES / CHEM / GAS / POLY / ELEC / SPECIAL / AMINES / CARBOXACID / TWOLIQUID / WATERONLY / H2RICH 等 40 页
- `Subsystems\apr-ug2\Content\html\using_the_property_method_assistant_to_choose_a_property_method.htm`

**分类总表与应用推荐**
- `Subsystems\ref2\Content\html\classificationofpropertymethodsandrecommendeduse.htm`（REF-CLASS）
- `Subsystems\apr-ug2\Content\html\chemicals.htm` / `petrochemicals.htm` / `environmental.htm` / `waterandsteam.htm` / `recommendedpropertymethodsfordifferentapplications.htm` / `propertymethodsfornonconventionalcomponents.htm`

**方法族总论（ref2）**
- `thermodynamicpropertymethods.htm`（EOS 法 vs 活度系数法的数学框架）
- `liquidactivitycoefficientpropertymethods.htm`（10 atm 上限）
- `equation_of_statepropertymethodsforhigh_pressurehydrocarbonapplications.htm`
- `flexibleandpredictiveequation_of_statepropertymethods.htm`
- `electrolytepropertymethods.htm`（10 atm / 3 atm、禁用于非电解质）
- `solidshandlingpropertymethod.htm`

**Chapter 2 单方法详情（ref2）**
- `idealpropertymethod.htm`、`nrtl.htm`、`wilson1.htm`、`wilson2.htm`、`uniquac1.htm`、`unifac1.htm`、`unifac_dortmundmodified_.htm`、`unifac_lyngbymodified_.htm`
- `peng_rob.htm`、`srk.htm`、`rk_soave.htm`、`rks_bm.htm`、`psrk.htm`、`sr_polar.htm`、`rk_aspen.htm`、`bwr_ls.htm`、`lk_plock.htm`、`bk10.htm`、`chao_seader.htm`、`grayson_streed.htm`、`CPA_method.htm`、`GERG2008_Property_Method.htm`
- `elecnrtl.htm`、`ENRTL-RK.htm`、`ENRTL-SR.htm`、`pitzer.htm`、`amines.htm`、`apisour.htm`
- `steamtables.htm`、`steamnbs_steamnbs2.htm`、`steam_ta.htm`、`IAPWS-95_Steam_Table.htm`

**GUI/表单说明（props）**
- `nrtlpropertymethod.htm`、`nrtl_rkpropertymethod.htm`、`unifacpropertymethod.htm`、`peng_robpropertymethod.htm`、`srk.htm`、`stmnbs2.htm`、`PC-SAFT_Property_Method.htm`、`ENRTL-RK_Property_Method.htm` 等
- `physicalpropertiesspecificationsglobalpropertymethodsandmodelsprocesstype.htm`
- `apr-ug2\...\specifyingpropertiesforthefree_waterphase.htm`、`selectingapropertymethod.htm`、`specifyingtheglobalpropertymethod.htm`

**提取过程留档**（本目录）：`scan_help.py`（全量清单 `_all_files.txt`，12,594 个）、`extract.py`、`txt/`、`txt2/`、`txt3/`、`txt4/`（各页纯文本，每份首行标 SOURCE 路径）、`q1..q3\hits.txt`（全文检索证据）。

---

*生成：2026-09-15，本机离线提取，未联网。*
