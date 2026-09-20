# Aspen Plus V14 收敛失败诊断与修复知识库

> 面向：通过 COM 批量驱动 Aspen Plus V14 的 AI Agent（看不到 GUI 报错面板）
> 素材来源：本机离线帮助 `C:\ProgramData\AspenTech\Aspen Plus V14.0\HtmlHelp\`（9875 个 HTML）
> 与官方示例 `C:\Program Files\AspenTech\Aspen Plus V14.0\GUI\Examples\`（203 个 bkp）
> 生成日期：2026-09-15

---

## 0. 阅读约定与来源标注

| 标记 | 含义 |
|---|---|
| **【官方原文】** | 直接摘自本机离线帮助页面的文字（附相对路径，可原文核对） |
| **【官方数据】** | 从 203 个官方示例 bkp 文本层统计出的实测数字 |
| **【推断】** | 帮助里没有明说，由本文档作者基于官方文档语义 + 工程经验推导。AI 采用时需自行承担风险 |
| **【未找到】** | 在 9875 个帮助页中确实检索不到，不做任何编造 |

帮助根目录下文简写为 `HH` = `C:\ProgramData\AspenTech\Aspen Plus V14.0\HtmlHelp\`
示例根目录下文简写为 `EX` = `C:\Program Files\AspenTech\Aspen Plus V14.0\GUI\Examples\`

---

## 1. 收敛失败诊断决策树

### 1.0 第 0 步：先分清「哪一层失败了」

**【官方原文】**（`Subsystems\userguide3\Content\html\Checking the Status of Runs from Automation.htm`）

> After a run is complete, in order to check the status of it, there are several status flags accessible in
> `Application.Tree.Data.Results Summary.Run-Status.Output`:
> **CSSTAT**: case studies … **CVSTAT**: convergence blocks … **PCESSTAT**: property estimation …
> **PPSTAT**: property tables … **PROPSTAT**: property calculation … **RSTAT**: Calculator and Transfer blocks …
> **SENSSTAT**: Sensitivity blocks
> In general, a value of **0** for one of these means there was no error of the indicated type.
> **1** means an error. **2** means a warning. A missing value (RMISS or NaN, or 2 for cases where there
> cannot be warnings) means there was no occurrence of this feature in the run.

这是**纯 COM 可读**的收敛判定入口，AI 必须优先用它，而不是靠猜。

| 状态位 | 管辖对象 | AI 判据 |
|---|---|---|
| `CVSTAT` | 收敛块（撕裂流 / 设计规定） | 0=通过，1=错误，2=警告，NaN=本次无收敛块 |
| `SENSSTAT` | 灵敏度块 | 同上 |
| `RSTAT` | Calculator / Transfer 块 | 同上 |
| `PROPSTAT` / `PCESSTAT` / `PPSTAT` | 物性 | 同上 |

**【推断】** `CVSTAT` 只能告诉 AI「有错」，不能告诉「错在哪」。要拿到错在哪，需要再导出运行消息文件（见 1.1）。

### 1.1 第 1 步：取证（AI 看不到 GUI，必须先拿到文本）

**【官方原文】**（`Subsystems\userguide1\Content\html\runmessagesfiles___cpm_.htm`）

> Aspen Plus Run Messages files are text files that include the error, warning, and diagnostic messages from
> the run. These are the messages displayed on the Control Panel during a run. The number of messages and the
> detail can be controlled globally on the Setup | Specifications | Diagnostics sheet.
> Run Messages files are similar to history files (*.his). The diagnostic level for history files and the
> control panel can be adjusted independently. **If you need a high level of diagnostics, print to the history
> file (not to the control panel). This prevents any performance degradation that might result from lengthy
> diagnostics on the screen.**

**【官方原文】**（`Subsystems\converge\Content\html\convergencediagnosticmessagelevels.htm`）—— 收敛诊断级别

| 级别 | 官方描述 |
|---|---|
| 0 | 仅列出收敛块**终止性**错误消息 |
| 1 | 级别 0 + 收敛块 **severe error** |
| 2 | 级别 1 + 收敛块 **error** |
| 3 | 级别 2 + 收敛块 **warning** |
| 4 | 级别 3 + 简要诊断信息（**默认级别**） |
| 5 | 级别 4 + **每一迭代的未收敛变量明细** |
| 6 | 级别 4 + **每一迭代的全部变量** |
| 7–8 | 级别 6 + 各算法额外的分析诊断 |

**【推断 · 关键操作建议】** 批量扫描时日常跑在级别 3（省时间、少噪音）；一旦 `CVSTAT != 0`，把收敛诊断级别提到 **5**（能给出未收敛变量表，是判断「哪个撕裂流变量卡住」的唯一文本依据），**写进 history file 而不是 control panel**（官方明确说这样不会拖慢）。不要长期开 6+，输出量会淹没 LLM 上下文。

**【官方原文】**（`Subsystems\userguide2\Content\html\convergencediagnostics.htm`）—— 级别 5 的消息长这样：

```
> Loop C-1 Method: BROYDEN Iteration 1
Converging tear streams: 4
Converging specs: H2RATE
NEW X              G(X)               X               ERR/TOL
TOTAL MOLEFLOW (1) 0.135448E-01 ...
...
8 vars not converged, Max Err/Tol 0.17679E+05
```

变量类型括号里的数字：**1**=不被收敛算法更新的撕裂流变量；**2**=被收敛方法更新的撕裂流变量；**3**=设计规定的操纵变量；**4**=Calculator 撕裂变量。
（同页官方原文：「The value in parentheses indicates the type of variable」）

**【官方原文】**（`Subsystems\userguide2\Content\html\controlpanelmessages.htm`）

> `> Loop CV Method: WEGSTEIN Iteration 9` / `Converging tear streams: 3` / `4 vars not converged, Max Err/Tol 0.18603E+02`
> `>` = 最外层循环，`>>` = 嵌套一层，`>>>` = 嵌套两层
> **Convergence is achieved when the value of Max Err/Tol becomes less than 1.0.**

> 这是 AI 的**硬判据**：`Max Err/Tol < 1.0` = 收敛。抓历史文件时直接正则抽 `Max Err/Tol` 后面的数。

### 1.2 决策树主干

```
Run2 结束
   │
   ├─ 读 Tree.Data.Results Summary.Run-Status.Output → CVSTAT / SENSSTAT / RSTAT
   │
   ├─ CVSTAT = 0 ? ──否──▶ 进入【A. 循环/撕裂流类】
   │
   ├─ 导出 .cpm / .rep，正则抓 "ERROR" / "SEVERE ERROR" / "WARNING" 行
   │
   └─ 按消息文本分诊：
        ├─ "IS NOT IN MASS BALANCE"                          → 【A1】
        ├─ "STREAMS CROSSING THE LOOP ... NOT IN MASS BALANCE"→ 【A2】
        ├─ "WAS NEVER EXECUTED"                              → 【A3】
        ├─ "CONTAINS THE FOLLOWING DESIGN SPECS FROM ANOTHER
        │   MAXIMAL CYCLIC SUBSYSTEM"                        → 【A4】
        ├─ "1 INFORMATION TEAR(S) ... WILL NOT BE CONVERGED" → 【A5】
        ├─ "ZERO FEED TO THE BLOCK. BLOCK BYPASSED"          → 【B1】
        ├─ "RADFRAC FAILED TO CONVERGE IN 25 ITERATIONS"     → 【C1】
        ├─ "COMPONENT BALANCE EQUATION FAILED TO CONVERGE"   → 【C2】
        ├─ "STAGES DRIED UP" / "FLOW ... TENDING TO BLOW UP" → 【C3】
        ├─ "DESIGN SPEC IS NOT SATISFIED BECAUSE ONE OR MORE
        │   MANIPULATED VARIABLE IS AT ITS BOUND"            → 【D1】
        ├─ "JACOBIAN IS NUMERICALLY SINGULAR"                → 【C4】
        ├─ "BLOCK NOT CONVERGED / QUADRATIC SUBPROBLEM
        │   INFEASIBLE / NLIMIT/MAX-STEP"                    → 【E1】
        ├─ SENSSTAT != 0                                     → 【F. 灵敏度中断】
        └─ 无任何 ERROR，但 Max Err/Tol 停在 >1              → 【G. 按 Err/Tol 曲线形状分治】
```

### 1.3 【A】物料平衡不闭合 / 撕裂流不收敛

#### A1 `BLOCK (name) IS NOT IN MASS BALANCE`
**【官方原文】**（`Content\html\Error Block is Not in Mass Balance.htm`）

> **Cause**: As suggested, some sort of flowsheet manipulation may have changed the flow after the block was
> executed. This can happen with a Design Spec, Calculator, Transfer, Sensitivity, Optimization, or Regression.
>
> **Solution**: Usually, the automatic flowsheet sequencing algorithm will generate a sequence which ensures
> blocks are properly re-run after such manipulations. If you have specified a sequence, ensure that all blocks
> which can be affected by the manipulation are in the loop after that manipulation. **If a property parameter
> is manipulated, it can affect any block with a relevant component and property method, potentially the
> entire flowsheet.**

> **AI 操作提示【官方支持】**：这是**批量扫描的高频坑**——Sensitivity/Design Spec/Calculator 改了量之后，序列没把受影响的块排进去。若 AI 自己指定了 Sequence，必须自查；若改的是**物性参数**，影响面可能是全厂。

#### A2 `STREAMS CROSSING THE LOOP CONVERGED BY <block> ARE NOT IN MASS BALANCE`
**【官方原文】**（`Content\html\Flowsheet_Warning__Streams_Crossing_the_Loop_are_not_in_Mass_Balance.htm`）

> **Cause 1**: …this can be caused when the recycle flow is much larger than the flows in and out of the loop.
> In this case, the tear stream may be converged to its relative tolerance, but the absolute error is magnified
> when applied to the much smaller flows in and out of the loop.
>
> **Solution 1**: …specify tolerances **tighter than the default of 0.0001** for these streams. This will cause
> the loops to be closed more tightly to avoid this problem.
>
> **Cause 2**: …user-specified manipulations to the convergence sequence and/or EO manipulations …
> **Solution 2**: …you may disable the check on the Setup | Calculation Options | Check Results sheet …

> **关键**：这个警告的解法是**收紧**容差（< 1e-4），不是放宽。与直觉相反，AI 容易搞反。

#### A3 `CONVERGENCE BLOCK <name> WAS NEVER EXECUTED`
**【官方原文】**（`Content\html\Error__Convergence_Block_Never_Executed.htm`）

> **Cause**: This is almost always caused by **Initialization being set to Single Pass or Single Pass: Changed**.
> …In these single pass modes, intended for initializing the flowsheet for an equation-oriented (EO)
> calculation, each block is only executed once, so there is no need for convergence blocks and they are not
> executed.
>
> **Solution**: …change the **Initialization** field to **Solve**.

> **AI 操作提示【官方支持】**：批量扫描时若某个 case 报这个，先查 Initialization 模式，不要去调收敛参数。

#### A4 `CONVERGENCE BLOCK (name) CONTAINS THE FOLLOWING DESIGN SPECS FROM ANOTHER MAXIMAL CYCLIC SUBSYSTEM`
**【官方原文】**（`Content\html\flowsheet_maximal_cyclic_subsystem_errors.htm`）

> The sequencing algorithm … partitions the flowsheet into an ordered set of subsystems which can be solved
> separately, called **maximal cyclic subsystems (MCS)**. … The sequence algorithm does not allow a convergence
> block to include tear streams and/or design specs from more than one MCS …
> **Solution**: Remove the named flowsheet object from the named convergence block.

#### A5 `1 INFORMATION TEAR(S) IN SUBSYSTEM #1 WILL NOT BE CONVERGED BY CONVERGENCE BLOCK`
**【官方原文】**（`Content\html\flowsheet_information_tears_warning.htm`）

> **Cause**: Information tears occur when **Calculator blocks perform feedback operations**. …they are not
> automatically converged, but the warning is issued.
>
> **Solution**: On the Convergence | Options | Defaults | Sequencing sheet, select the checkbox
> **Tear Calculator export variables**. Also be sure to set the **Information flow** for each variable on the
> Calculator | Input | Define sheet to **Import or Export**.

#### A6 循环不收敛的通用排查（最重要的一页）
**【官方原文】**（`Content\html\troubleshooting_flowsheet_convergence.htm`）

> **General Strategies**
> - Look for error and warning messages, especially concerning block convergence, zero flow rates, and
>   temperature crossovers.
> - Provide reasonable initial estimates. Look for unusual results, extreme temperatures, unexpected
>   separations in columns, and step changes in profile results.
> - Review physical property parameters and methods.
> - **Evaluate tear stream choice.** Choose streams that remain relatively constant, or streams with fewer
>   variables (such as heat streams or all-vapor streams in electrolyte simulations).
> - **Simplify or restate the problem.** If appropriate, use Mixer to reduce the number of tear streams.
>   Consider using component groups … (for example, a **TP specification in RGibbs is more stable than PQ**).
> - Additional control over the simulation increases stability. Add design specs to enforce design goals …
>   Internal RadFrac specifications will improve stability. Prevent rigorous blocks (rigorous HeatX, tough
>   separations) from entering infeasible operating conditions.
> - Confirm the calculation sequence.

五个具体 Cause（全部官方原文）：

| # | 官方 Cause | 官方 Solution |
|---|---|---|
| 1 | 某组分在循环里**累积、无出口**（常表现为每次直接迭代后流量增加同一数量） | 确保每个组分（**含反应产物**）都有出路 |
| 2 | 流量变化破坏了规定 | 用**与流量无关**的方式规定：用 split fraction 而不是流量；RadFrac 用 **D:F** 而不是 D；加少量 Calculator 块当前馈控制器（算 makeup/purge） |
| 3 | 循环**内部**块的容差太松（典型表现：Err/Tol 降到 ~10 就不动了） | 循环内块必须比循环收敛得更**紧**（循环默认 1e-4）。在 Setup\|Calculation Options\|Flash Convergence 收紧全局闪蒸 Error Tolerance；循环内 RadFrac 在 RadFrac\|Convergence\|Basic 收紧 Error Tolerance。**放宽容差只能作为最后手段**（Relax the convergence block tolerance only as a last resort）。嵌套循环要逐层收紧。 |
| 4 | 对压力高度敏感的模型跑进了无法收敛的工况 | 显式设定压力，而不是让压降取默认 0 |
| 5 | 循环里**所有块**都只给了压降（有的还是 0），没有任何一个设定压力 → 撕裂流压力一路下降，永不收敛 | 至少在一个块里设定**压力**而非压降 |

> **AI 操作提示【官方支持】**：Cause 5 是批量扫描的典型杀手——改工况后压降叠加。扫描前可静态检查：循环内是否至少一个块设定了绝对压力。

### 1.4 【B】单元模块内部失败

- **B1 零进料**：`ZERO FEED TO THE BLOCK. BLOCK BYPASSED`（`Content\html\flowsheet_errors_or_warnings.htm` 官方列出的 flowsheet 警告之一）。**【推断】** 批量扫描里意味着被扫参数把某股进料推到 0，该块被旁路 → 下游全变。应把"零进料"视为工况越界信号，而不是收敛问题。
- **B2 RadFrac / HeatX / RCSTR / RPlug / RBatch / HTFS** 各有独立排错页（见第 2 节表）。

### 1.5 【C】RadFrac（精馏塔）内部失败

**【官方原文】**（`Subsystems\apunitop\Content\html\troubleshooting_radfrac_convergence_problems.htm`）
`RADFRAC FAILED TO CONVERGE IN 25 ITERATIONS; RESULTS FOR FINAL ITERATION ARE RETURNED.`

| Cause | 官方 Solution |
|---|---|
| 1 规定不可行（每个组分都得有出路）或规定选得差 | 见 Troubleshooting RadFrac Specifications |
| 2 热平衡问题：回流比/再沸比给太小 | 确保加入的热量足以汽化馏出液+回流；确保移出的热量足以冷凝全部蒸汽 |
| 3 物性问题 | 见 Troubleshooting RadFrac Physical Property Problems |
| 4 收敛算法选型/调参差 | **若 Err/Tol 在下降，可能只是需要增加迭代次数** |
| 5 Newton 算法 + 组分 > 20 时相平衡公式不够 | 改 Convergence \| Advanced 上的 **Pheqm-form** |
| 6 塔径太小 | 用更大塔径，或先 sizing 得到估计值（即使你知道实际塔径） |

**【官方原文】**（`Subsystems\apunitop\Content\html\troubleshooting_radfrac_convergence_fails_err_tol_diverging.htm`）

> If Err/Tol diverges: Provide initial estimates / Check specifications / Try different algorithms or tune
> algorithm parameters / 若用 free-water 计算而有机相在部分塔段不存在 → 改用严格三相计算。
> **If Err/Tol is oscillating, increase the Damping level on the RadFrac | Convergence | Basic sheet. With
> more damping, you may also need to increase the Maximum iterations on this sheet.**

### 1.6 【D】设计规定（Design Spec）无解

**【官方原文】**（`Subsystems\userguide2\Content\html\diagnosingdesignspecificationconvergence.htm`）

| Err/Tol 曲线 | 官方 Cause | 官方 Solution |
|---|---|---|
| 稳定下降 | — | Maxit 提到 30 以上 |
| **Err/Tol 不变** | Spec 函数对操纵变量不敏感 / 在某区间平坦 | ①检查 Spec 函数写对没 ②检查操纵变量选对没 ③**用 Sensitivity 研究操纵变量对 Spec 的影响** ④Secant 法设 **Bracket=Yes**（区间二分） |
| 降到阈值不动 | 嵌套循环，内层容差太松 | ①收紧内层块/收敛块容差 ②放宽外层容差 ③用 Broyden/Newton **同时**收敛内外层（Options\|Defaults\|Sequencing 的 **Design Spec Nesting**） |
| 收敛到变量边界 | Spec 函数非单调 | ①Secant 设 **Bracket=Check bounds** ②用 Sensitivity 摸清敏感度，调整边界或换初值 |

补充通用策略（官方原文）：
> Formulate specifications to **avoid discontinuities**. … reduce non-linearity …（例如浓度接近零时，对**浓度的对数**做规定）
> Make sure the limits are reasonable. **Try to avoid limits spanning more than one order of magnitude.**
> **Confirm the existence of a solution by replacing a Design specification with a Sensitivity block.**
> Make sure the tolerance is reasonable, especially when compared with the tolerance of blocks inside the
> Design specification convergence block.

### 1.7 【E】优化（SQP）失败

**【官方原文】**（`Subsystems\userguide3\Content\html\Error__NLIMIT_MAX-STEP_Settings_May_Be_Too_Restrictive.htm`）

```
BLOCK NOT CONVERGED
QUADRATIC SUBPROBLEM INFEASIBLE
CONSTRAINTS MAY BE INCONSISTENT OR VARIABLE BOUNDS
AND/OR NLIMIT/MAX-STEP SETTINGS MAY BE TOO RESTRICTIVE
```
> **Cause**: …typically caused by the maximum step size being set too low for the solver to reach the solution
> and/or the step size limit being enforced for too many iterations.
> **Solution**: ①在 Convergence \| Convergence \| SQP \| Input \| Parameters 降低 **Iterations to enforce
> maximum step size**；②在 SQP \| Input \| Optimization 增大 **Maximum step size**（若为空则取 Model Analysis
> Tools \| Optimization \| Input \| Vary 上的值）。

### 1.8 【F】灵敏度分析中断

**【官方原文】**（`Subsystems\mdanmstr\Content\html\sensitivityinputoptionalsheet.htm`）

> You can choose to reinitialize no blocks, all blocks, or selected **unit operation and convergence blocks**.
> …Normally, **you should not reinitialize blocks and streams**, because it is usually most efficient to begin
> the calculations for a new row evaluation with the results of the previous row evaluation.
> …When you reinitialize a tear stream, its component flows are set to their initial values. **If you choose
> not to reinitialize a tear stream, the results from one sensitivity loop pass are used as initial estimates
> for the next pass.**
>
> **Note: Variables changed by a Sensitivity will remain at their last values at the start of the next run if
> you do not reinitialize the problem**; this may be different than the base case values if you do not run the
> base case last.

> **AI 操作提示【官方支持】**：这条 note 是**批量扫描的状态污染陷阱**——灵敏度/工况扫描跑完后，被扫变量会停留在最后一行的值。下一次 Run 若不 Reinitialize，起点就不是基准工况。**建议在每批扫描结束或每个独立 Run 前显式 Reinitialize。**

### 1.9 【G】按 Err/Tol 曲线形状分治（总表）

**【官方原文】**（`Subsystems\userguide2\Content\html\diagnosingtearstreamconvergence.htm`）

| Err/Tol vs 迭代数 | 官方 Cause | 官方 Solution |
|---|---|---|
| 稳定收敛 | — | **Maxit 提到 30 以上** |
| 稳定但很慢 | 组分累积 | ①确认所有组分有出口（否则可能工程上无稳态解）②**加大加速步长**：Wegstein **Lower bound = 20**；若有效试 **50** |
| 振荡 | — | **Wegstein upper bound 设为 0.5** 以阻尼振荡 |
| 降到阈值不动 | 嵌套循环且内层容差太松 | ①收紧内层块/收敛块容差 ②放宽外层 ③用 **Broyden/Newton 同时收敛内外层**（Design Spec Nesting） |
| Broyden/Newton 失败 | — | ①**Wait 提到 4** ②若撕裂流与设计规定在同一收敛块，先用 **Tear Tolerance / Tear Tolerance Ratio** 只收敛撕裂流 ③**改回 Wegstein** |

其他官方通用策略（同页）：
> - Provide a good initial guess for the Tear stream on the Streams form.
> - **Select a Tear stream that will not vary a great deal.**（Heater 出口通常比 Reactor 出口更适合做撕裂流）
> - **Disconnect the recycle stream** to get a good initial estimate and to examine the sensitivity.
> - 简化：加 Mixer 减少撕裂流数量 / 用 MHeatX 替 HeatX / 用 component group 减少变量数 / 选组分少的撕裂流 / 选出口温度被设定的块的撕裂流
> - **Reinitialize，然后用 Wegstein 上下界都 = 0（等价于直接迭代）跑**，观察是否有组分持续累积
> - 换方法：Broyden / Newton 而不是默认的 Wegstein
> - 确认计算序列合理

### 1.10 官方给出的 9 步排查流程（可直接固化为 AI 的 SOP）

**【官方原文】**（`Subsystems\userguide2\Content\html\resolvingsequenceandconvergenceproblems.htm`）

1. 先用 Aspen Plus 自动生成的默认序列跑。
2. 检查结果：**找被跳过的块和未收敛的块**，查 Control Panel / 结果页里没正常完成、报错、或结果异常的块。常见原因表：
   - 块规定错误 → 改正
   - 进料条件离谱 → 给更好的撕裂流/设计变量初值
   - 收敛规定 → 换规定、换算法选项、或增加迭代次数
   - 算法选项 → 换选项
   - 迭代次数不够 → 增加
   （若做了修正，跳到第 9 步）
3. 检查容差：「**If the maximum error/tol for convergence blocks reduces to around 10 quickly, but fluctuates
   after that, tolerance adjustments may be necessary.**」 → 另一办法：用 Broyden/Newton 收敛块同时收敛多个设计规定。
4. Wegstein 收敛慢 → 试 **Wait=4, Consecutive Direct Substitution Steps=4, Lower Bound=-50**，并给撕裂流更好初值。
5. 撕裂流振荡 → **改用 Direct 方法**。若仍振荡，检查每个组分是否有出口。振荡也可能来自撕裂流循环内部的设计规定循环未收敛。
6. 检查 Spec Summary 里未收敛的设计规定（原因→动作表见 1.6）。
7. （高级）必要时改计算序列：Nesting Order / 部分 Sequence / 指定撕裂流。
8. 若所有收敛块都收敛但总物料不平衡 → 检查 Calculator 块。建议用 Import/Export Variables 排序常规 Calculator，用 Execute 排序初始化 Calculator。
9. 若改了流程，重跑并回到第 2 步。

**【官方原文 · 一条极容易被忽略的坑】**（`Content\html\Changing a Convergence Block Tolerance.htm`）

> **Problem**: 只改了收敛块的规格（例如收紧容差）、没改别的，重跑时 Aspen Plus 不做任何计算，直接宣布该块已收敛。
> **Cause**: **Use affected block logic** 被打开了……
> **Solution**: **Turn off the option Use affected block logic before running the problem after only changing
> convergence parameters.**

> **AI 操作提示【官方支持 · 高频】**：AI 的自动修复流程本质是"改收敛参数 → 重跑"。如果 `Use affected block
> logic` 开着，**第二次重跑会空转并假报收敛**。自动修复循环里必须先把这个选项关掉。

---

## 2. 常见错误消息 → 原因 → 修复动作 对照表

### 2.0 关于「官方错误消息清单」的核查结论

**【未找到】**：在 9875 个帮助页中，**不存在**集中式的「Error Messages / 错误代码表 / 错误消息附录」。核查过程：

- 标题以 `Error` / `Warning` / `Severe` / `Fatal` 开头的页面仅 **13 个**，全部是**针对单个错误的独立页面**，不是清单。
- 全文检索 `error number` / `message number` / `error index` → **0 命中**；`error code` → 仅 1 处命中，且是 ACM（自定义模型）的错误捕获，与求解器错误无关。
- 帮助的 TOC / 索引文件（`.js` / `.xml`）中检索 `error message` → 无对应章节节点。

**替代方案**：官方提供的是**按模块分散的 troubleshooting 页面**，最接近"清单"的三页是：

| 页面 | 覆盖内容 |
|---|---|
| `Content\html\flowsheet_errors_or_warnings.htm` | **flowsheet 级**错误/警告总入口（下含 6 条） |
| `Subsystems\apunitop\Content\html\troubleshooting_radfrac_errors_and_warnings.htm` | RadFrac 错误消息索引（最丰富，约 15 条） |
| `Subsystems\physprop\Content\html\troubleshooting_physical_property_errors_and_warnings.htm` | 物性错误/警告 |

**【官方原文】**（`Content\html\flowsheet_errors_or_warnings.htm`）—— 官方 flowsheet 级错误/警告**完整清单**（6 条，原文摘录）：

1. `ZERO FEED TO THE BLOCK. BLOCK BYPASSED`（或 MIXER 的 `ZERO FEED TO BLOCK.`）
2. `ERROR DURING FLOWSHEET ANALYSIS — CONVERGENCE BLOCK (name) CONTAINS THE FOLLOWING DESIGN SPECS FROM ANOTHER MAXIMAL CYCLIC SUBSYSTEM. (name) THEREFORE IT CANNOT BE USED. IT WILL BE IGNORED.`
3. `WARNING DURING FLOWSHEET ANALYSIS — 1 INFORMATION TEAR(S) IN SUBSYSTEM #1 WILL NOT BE CONVERGED BY CONVERGENCE BLOCK WHICH MIGHT CAUSE CONVERGENCE PROBLEM. PLEASE TRY THE NEW TEAR-VAR OPTION IN CONV-OPTIONS.`
4. `WARNING WHILE IN SEQUENCE MONITOR — STREAMS CROSSING THE LOOP CONVERGED BY <block> ARE NOT IN MASS BALANCE: MASS INLET FLOW = <value>, MASS OUTLET FLOW = <value> RELATIVE DIFFERENCE = <value> IMBALANCE MAY BE DUE TO A LARGE RECYCLE FLOW, AND A RELATIVELY LOOSE TEAR STREAM TOLERANCE.`
5. `ERROR — BLOCK (name) IS NOT IN MASS BALANCE: MASS INLET FLOW = (value), MASS OUTLET FLOW = (value) ABSOLUTE DIFFERENCE = (value) A STREAM FLOW MAY HAVE BEEN CHANGED BY A FORTRAN, TRANSFER, OR BALANCE BLOCK AFTER THE BLOCK HAD BEEN EXECUTED.`
6. `CONVERGENCE BLOCK <name> WAS NEVER EXECUTED`

### 2.1 对照表

> 「来源」列给出可核对的相对路径。所有"修复动作"除标注【推断】外，均为官方原文转述。

| # | 错误消息（正则可匹配的关键串） | 层 | 官方原因 | 修复动作 | 来源 |
|---|---|---|---|---|---|
| 1 | `IS NOT IN MASS BALANCE` + `ABSOLUTE DIFFERENCE` | 块 | Design Spec / Calculator / Transfer / Sensitivity / Optimization / Regression 在块执行后改了流量 | 检查自定义序列是否把受影响块排在该操作之后；若改的是**物性参数**，影响面可能是全厂 | `Content\html\Error Block is Not in Mass Balance.htm` |
| 2 | `STREAMS CROSSING THE LOOP ... ARE NOT IN MASS BALANCE` | 循环 | 循环流量远大于进/出流量，撕裂流虽满足相对容差但绝对误差被放大 | **收紧**撕裂流容差到 < 1e-4（默认 1e-4）；或确认无误后在 Setup\|Calculation Options\|Check Results 关闭该检查 | `Content\html\Flowsheet_Warning__Streams_Crossing_the_Loop_are_not_in_Mass_Balance.htm` |
| 3 | `CONVERGENCE BLOCK <name> WAS NEVER EXECUTED` | 全局 | Initialization 设成了 Single Pass / Single Pass: Changed | 把 Initialization 改为 **Solve** | `Content\html\Error__Convergence_Block_Never_Executed.htm` |
| 4 | `CONTAINS THE FOLLOWING DESIGN SPECS FROM ANOTHER MAXIMAL CYCLIC SUBSYSTEM` | 序列 | 一个收敛块跨越了两个 MCS | 从该收敛块中移除被点名的对象 | `Content\html\flowsheet_maximal_cyclic_subsystem_errors.htm` |
| 5 | `INFORMATION TEAR(S) ... WILL NOT BE CONVERGED` | 序列 | Calculator 块被用作反馈 | 勾选 **Tear Calculator export variables**；Calculator\|Input\|Define 上把 Information flow 设为 Import/Export | `Content\html\flowsheet_information_tears_warning.htm` |
| 6 | `ZERO FEED TO THE BLOCK. BLOCK BYPASSED` | 块 | 进料为零 | 【推断】视为工况越界信号，扫描步长过大或参数组合使该股被推到 0 | `Content\html\flowsheet_errors_or_warnings.htm` |
| 7 | `RADFRAC FAILED TO CONVERGE IN 25 ITERATIONS` | 塔 | 见 1.5 的 6 条 Cause | Err/Tol 在降 → 加迭代；振荡 → 加 Damping 并相应加迭代；>20 组分 + Newton → 改 Pheqm-form | `...\troubleshooting_radfrac_convergence_problems.htm` |
| 8 | `COMPONENT BALANCE EQUATION FAILED TO CONVERGE` | 塔 | 严重错误（官方列为 SEVERE） | 归入 1.5 流程 | `...\troubleshooting_radfrac_errors_and_warnings.htm` |
| 9 | `THE FOLLOWING STAGES DRIED UP` | 塔 | 汽/液相流量趋零（下限 = 1e-4 × 总进料，或 V/L、L/V 比下限 1e-4） | 同 1.5：检查热平衡、规定可行性 | 同上 |
| 10 | `FLOW OF ONE OR MORE STAGES IS TENDING TO BLOW UP`（上限 = 1e+6 × 总进料） | 塔 | 塔内流量发散 | 同 1.5 | 同上 |
| 11 | `DESIGN SPEC IS NOT SATISFIED BECAUSE ONE OR MORE MANIPULATED VARIABLE IS AT ITS BOUND` | 设计规定 | 操纵变量撞边界 | 见 1.6"收敛到变量边界"：Secant 设 Bracket=Check bounds；用 Sensitivity 摸敏感度；调边界/换初值 | 同上 |
| 12 | `JACOBIAN IS NUMERICALLY SINGULAR. CHECK COLUMN/PUMPAROUND SPECIFICATIONS` | 塔 | Jacobian 奇异 | 官方直接给出指引：**检查塔/中段回流规定，必要时换一套规定** | 同上 |
| 13 | `Middle loop did not converge to requested tolerance` (UDL3ZR.7) | 塔 | 外层容差满足但设计规定（中层）迭代未达容差 | 官方原文：**`Try to specify EXTRA-ML=1 in Convergence | Advanced.`** | 同上 |
| 14 | `AQUEOUS PHASE SHOULD BE THE 1ST LIQUID PHASE` (UDL03Y.6) | 塔（电解质） | 三相电解质塔 + 计算平衡反应常数 | 调整液相顺序 | 同上 |
| 15 | `A LIQUID FEED/PUMPAROUND TO THE TOP(/BOTTOM) STAGE IS REQUIRED WHEN "Q1=0"(/QN=0) IS SPECIFIED` | 塔 | 指定了 Q1=0/QN=0 但无液相进料/中段回流 | 增加液相进料或中段回流 | 同上 |
| 16 | `SINGLE PHASE TEMPERATURE CALCULATIONS FAILED IN 6 ITERATIONS` | 塔（报告生成阶段） | 单相温度计算失败 | 检查物性与焓规定一致性 | 同上 |
| 17 | `BLOCK NOT CONVERGED` + `QUADRATIC SUBPROBLEM INFEASIBLE` + `NLIMIT/MAX-STEP` | 优化(SQP) | 最大步长太小 / 步长限制施加的迭代数太多 | ①降低 Iterations to enforce maximum step size ②增大 Maximum step size | `Subsystems\userguide3\Content\html\Error__NLIMIT_MAX-STEP_Settings_May_Be_Too_Restrictive.htm` |
| 18 | `RCSTR Error: RES_TIME_LOOP_FAILURE - RESIDUAL_AT_MINIMUM_NOT_VARYING` | 反应器 | RCSTR 停留时间循环失败 | 见 `Subsystems\apunitop\Content\html\RCSTR_Error__RES_TIME_LOOP_FAILURE_-_RESIDUAL_AT_MINIMUM_NOT_VARYING.htm` | apunitop |
| 19 | `HTFS+ Error: Analysis Did Not Converge to a Solution` | 换热器 | HTFS 严格计算失败 | 见 `Subsystems\apunitop\Content\html\HTFS+_Error__Analysis_Did_Not_Converge_to_a_Solution.htm` | apunitop |
| 20 | `HeatX Error: Cold Stream is Hotter than Hot Stream` | 换热器 | 温度交叉 | 官方在 troubleshooting 页单列；**【推断】** 属规格不可行，非数值问题 | apunitop |

**【推断】** 上表 18–20 及更细的模块级错误（RCSTR/RPlug/RBatch/BatchSep/HeatX/Extract/RateSep/物性/电解质）在
`Subsystems\apunitop\Content\html\` 与 `Subsystems\physprop\Content\html\` 下各有独立页面。**建议 AI 的取证
流程**：从 `.cpm` 里正则出错误串 → 用错误串去 `HH` 的文本缓存里做模糊检索 → 命中页面即为官方解法。这比维护一张
静态大表更可扩展。

### 2.2 结果页上的收敛判据（供 AI 读取）

**【官方原文】**（`Subsystems\results\Content\html\resultssummaryconvergencetearsummarysheet.htm`）
Tear Summary 表字段：**Tear Stream / Status / Variable with maximum error / Maximum error/Tolerance /
Maximum relative error / Absolute error / Convergence block**，其中
> A value smaller than 1 indicates that the tear is converged.
> Pressure and enthalpy values are scaled by a factor of 10⁻⁸.

**【官方原文】**（`Subsystems\results\Content\html\resultssummaryconvergencedesignspecsummarysheet.htm`）
DesignSpec Summary 字段：**Design Spec / Status / Error / Tolerance / Error/Tolerance / Variable Value /
Convergence Block**
> A value smaller than 1 indicates that the tear is converged.
> Status: **Converged and Not Converged indicate that the manipulated variable is at its lower or upper
> bound, respectively.**
> （注：这句官方原文措辞有歧义/疑似笔误，**【推断】** 应理解为 Status 字段会标识操纵变量是否停在边界；判据仍以
> Error/Tolerance < 1 为准。）

---

## 3. 收敛参数调节手册

### 3.1 收敛方法全景与选型

**【官方原文】**（`Subsystems\converge\Content\html\Convergence Blocks.htm`）—— V14 可用的收敛块类型：

| 方法 | 官方用途（原文要点） | 能收敛什么 |
|---|---|---|
| **Wegstein** | "the quickest and most reliable method for tear stream convergence"；"**the default method for Aspen Plus tear stream convergence**"；忽略变量间相互作用，**变量强耦合时不好用** | **仅撕裂流**（可对任意多股同时） |
| **Direct** | "convergence is slow but sure"；"available for those rare cases where other methods may be unstable"；**等价于 Wegstein 上下界都设 0**；便于诊断组分累积 | 仅撕裂流 |
| **Broyden** | 拟牛顿，用**近似**线性化 → 比 Newton 快，但**偶尔不如 Newton 可靠** | 撕裂流 + 多个设计规定 + 撕裂流与设计规定**同时** |
| **Newton** | 改进牛顿法；仅在收敛速率不满意时才算导数；含变量边界与线搜索；数值导数计算频繁 | 撕裂流 + 设计规定。**撕裂流仅在组分少、或其他方法都不行时用** |
| **Secant** | 割线法 + 高阶增强；可选 bracketing/区间二分（函数不连续、非单调、或有平坦区时开） | **单个**设计规定；"**the default method for design specification convergence, and is recommended for user generated convergence blocks**" |
| **SQP** | 优化问题 | 带/不带撕裂流的优化 |
| **BOBYQA** | 优化问题 | 不带撕裂流的优化 |
| **Complex** | 优化问题 | 带/不带撕裂流的优化 |

**【官方原文 · 选型决策句摘录】**
- 撕裂流默认 → **Wegstein**（`wegsteinmethod.htm`）
- 撕裂流振荡 / 其他方法不稳定 → **Direct**（`resolvingsequenceandconvergenceproblems.htm` 第 5 步；`directmethod.htm`）
- 多股撕裂流 + 多个设计规定、变量高度相互依赖、或循环与设计规定耦合到嵌套不可行 → **Broyden**（`broydenmethod.htm`）
- Broyden 也搞不定的高度耦合循环/设计规定 → **Newton**（`newtonmethod.htm`）。原文明确警告：
  > "Use Newton for tear streams only when the number of components is small or when convergence cannot be
  > achieved by the other methods."
- Broyden/Newton 失败 → **退回 Wegstein**（`diagnosingtearstreamconvergence.htm`）

**【推断 · 选型速查表】**（官方未给此表，以下为综合官方各页语义后整理的工程化建议）

| 症状 | 首选 | 次选 | 依据 |
|---|---|---|---|
| 一般循环，无耦合 | Wegstein（默认） | — | 官方 |
| Err/Tol 持续振荡 | Direct | Wegstein upper bound = 0.5 | 官方 |
| 多撕裂流 + 多设计规定 | Broyden | Newton | 官方 |
| 强耦合、Broyden 失败 | Newton | — | 官方 |
| Newton/Broyden 均失败 | 退回 Wegstein | — | 官方 |
| 组分多的撕裂流 | **不要**用 Newton | Wegstein / Broyden | 官方（>20 组分 + Newton 需改 Pheqm-form） |
| 怀疑组分累积（无稳态解） | Direct（上下界=0） | — | 官方（用于识别累积） |

### 3.2 各方法默认值（官方原文，来自 userguide2 各 method 页）

**Wegstein**（`Subsystems\userguide2\Content\html\wegsteinmethod.htm`）

| 字段 | 默认 |
|---|---|
| Maximum Flowsheet Evaluations | **30** |
| Wait（首次加速前的直接迭代次数） | **1** |
| Consecutive Direct Substitution Steps | **0** |
| Consecutive Acceleration Steps | **1** |
| Lower Bound (q 下界) | **-5** |
| Upper Bound (q 上界) | **0** |

**Broyden**（`Subsystems\userguide2\Content\html\broydenmethod.htm`）

| 字段 | 默认 |
|---|---|
| Maximum Flowsheet Evaluations | **30** |
| X Tolerance | **0.001** |
| Wait | **2** |
| （Advanced）Lower Bound / Upper Bound | -5 / 0 |
| （Advanced）Tear Tolerance / Tear Tolerance Ratio / Maximum Iterations | 空（用于"先只收敛撕裂流"） |

**Newton**（`Subsystems\userguide2\Content\html\newtonmethod.htm`）

| 字段 | 默认 |
|---|---|
| Maximum Newton Iterations | **30** |
| Maximum Flowsheet Evaluations | **9999** |
| Wait | **2** |
| X Tolerance | **0.0001** |
| Reduction Factor（决定何时重算 Jacobian） | **0.2** |
| Iterations to Reuse Jacobian | 空（默认按 Reduction Factor 决定） |
| （Advanced）Lower/Upper Bound | -5 / 0 |

**Secant**（`Subsystems\userguide2\Content\html\secantmethod.htm`）

| 字段 | 默认 |
|---|---|
| Maximum Flowsheet Evaluations | **30** |
| Step Size | **0.01** |
| Maximum Step Size | **1** |
| X Tolerance | **1e-8** |
| X Final on Error | **Last value**（可选 Initial value / Minimum value of function / Lower bound / Upper bound） |
| Bracket | **No**（可选 Yes / Check Bounds） |
| Find Minimum Function Value if Bracketing Fails… | 不勾选 |

**【官方原文 · Bracket 三个取值的区别】**（`secantmethod.htm`）
- `No`：不用区间二分。嵌套 secant 循环时可能需要设为 No（区间二分会增加迭代）。
- `Yes`：函数不变时尝试二分。适用于**函数在某段平坦**的情况。
- `Check Bounds`：函数不变 **或** 算法撞到变量边界时尝试二分。适用于平坦函数，也适用于**非单调函数**；保证算法卡在某一边界时会去试另一个边界。

### 3.3 容差与最大迭代次数

**容差相关默认值（官方原文）**

| 参数 | 默认值 | 来源 |
|---|---|---|
| Tear \| Specifications 的 **Tolerance** | **0.001** | `userguide2\specifyingtearstreams.htm` |
| Tear \| Specifications 的 **Trace** | **Tolerance/100** | 同上 |
| 循环（收敛块）容差 | **1e-4**（原文："which defaults to 10⁻⁴"） | `Content\html\troubleshooting_flowsheet_convergence.htm` Solution 3；`Content\html\Flowsheet_Warning__Streams_Crossing_the_Loop_are_not_in_Mass_Balance.htm` |
| RadFrac Error Tolerance（inside-out 的外层容差） | **1e-4**；Newton 法下为给定值的 **1e-3 倍**（可用 Advanced 上的 `Tolilmin` 覆盖） | `radfrac\radfracconvergencebasicsheet.htm` |
| 组件组（Component group） | **All components** | `userguide2\specifyingtearstreams.htm` |
| State variables | **Pressure & Enthalpy** | 同上 |

> 注意 Tear 表单默认 0.001 与循环默认 1e-4 **不一致**，两处官方页面各自陈述。**【推断】** 0.001 是"在 Tear 表单手动
> 指定撕裂流时"的字段默认，1e-4 是系统收敛块实际使用的循环容差。AI 改动时应显式写死目标值，不要依赖默认值。

**容差调节的官方原则（极其重要，AI 极易搞反）**

**【官方原文】**（`Content\html\troubleshooting_flowsheet_convergence.htm` Solution 3）
> Blocks inside the loop must be converged to **tighter (smaller) tolerances than the recycle loop** …
> **Relax the convergence block tolerance only as a last resort.**

**【官方原文】**（`userguide2\diagnosingtearstreamconvergence.htm` / `diagnosingdesignspecificationconvergence.htm`）
> Err/Tol 降到阈值不动时：**Set a tighter tolerance for the blocks and convergence blocks in the inner loop**
> 或 **Relax the tolerance for the outside loop.**（两者二选一，但**收紧内层是首选**）

> **结论【官方支持】**：放宽容差**不是首选修复手段**，而是最后手段；真正该做的是**收紧内层的块/闪蒸容差**。

**最大迭代次数**

**【官方原文】** 多处重复同一条：「**Increase Maxit above 30**」（默认 Maximum Flowsheet Evaluations = 30）。
调参建议（官方原文，`resolvingsequenceandconvergenceproblems.htm` 第 4 步）：
> If Wegstein convergence blocks converge slowly, try **Wait=4, Consecutive Direct Substitution Steps=4,
> Lower Bound=-50**. Providing better estimates for tear streams would also help.

**【官方原文 · Wegstein q 的语义】**（`userguide2\wegsteinaccelerationparameter.htm`）

| q | 效果 |
|---|---|
| q < 0 | **加速** |
| q = 0 | **直接迭代** |
| 0 < q < 1 | **阻尼** |

> Normally, you should use an **Upper Bound of 0**. If iterations move the variables slowly toward convergence,
> **smaller values of the lower bound**（perhaps **-25 or -50**）may give better results. If oscillation occurs
> with direct substitution, **values of the lower and upper bounds between 0 and 1** may help.
> Because oscillation or divergence can occur if q is unbounded, limits are set on q. The default lower and
> upper bounds on q are **-5 and 0**.

**【推断】** 注意官方在不同页面给了看似矛盾的 Wegstein 上界建议：`diagnosingtearstreamconvergence.htm` 说振荡时
"set upper bound to .5"（阻尼），而 `wegsteinaccelerationparameter.htm` 说"Normally, you should use an Upper
Bound of 0"。两者其实一致：**0 是常规值，0.5 是振荡时的临时对策**。

### 3.4 撕裂流选择与初值

**【官方原文 · 撕裂流选择原则】**（`Content\html\troubleshooting_flowsheet_convergence.htm`）
> Choose streams that **remain relatively constant**, or streams with **fewer variables** (such as heat streams
> or all-vapor streams in electrolyte simulations).

**【官方原文 · 具体化】**（`userguide2\diagnosingtearstreamconvergence.htm`）
> - Select a Tear stream that will not vary a great deal. For example, **the outlet stream of a Heater block is
>   generally a better choice than the outlet stream from a Reactor block.**
> - Choose a Tear stream that has **fewer components** present.
> - Choose a Tear stream from a block that **sets an outlet temperature**.

**【官方原文 · 撕裂集合的注意事项】**（`Subsystems\converge\Content\html\tearform.htm`）
> If you specify an **incomplete** tear set for your flowsheet, Aspen Plus automatically chooses the remaining
> set of streams. If you specify a **redundant** tear set (too many tear streams), **Aspen Plus may ignore some
> tears or find an inefficient sequence.**

**【官方原文 · 撕裂流收敛变量与 Trace】**（`userguide2\specifyingtearconvergenceparameters.htm`）
> For streams, the default convergence variables are **total mole flow, all component mole flows, pressure, and
> enthalpy**. When the **Trace Option** is **Cutoff** …Aspen Plus bypasses this convergence test for components
> that have a mole fraction less than the Trace threshold (default = Tolerance/100). The alternative Trace
> Option, **Gradual**, adds a 100×Trace threshold term to the denominator.

**【官方原文 · 初值】**（`userguide2\initialestimatesfortearstreams.htm`）
> An initial estimate generally aids recycle convergence, and is **sometimes necessary, especially for recycle
> loops involving distillation blocks.**

**【官方原文 · 撕裂算法权重】**（`userguide2\specifyingsequencingparameters.htm`）

| 字段 | 默认 | 含义 |
|---|---|---|
| Design Spec Nesting | **Inside** | 设计规定嵌套在撕裂流循环**内** / 外 / 与撕裂流同时收敛 |
| User Nesting | **Outside** | 优先于 Design Spec Nesting |
| Variable Weight | **1** | 大 → 撕裂算法最小化**被撕变量数** |
| Loop Weight | **1** | 大 → 撕裂算法最小化**被撕回路数** |
| Tear Fortran Export Variables | 未勾选 | Fortran 块变量是否可被撕 |
| Check Sequence | **勾选** | 是否检查用户序列确保所有回路都被撕开 |

**【官方原文 · 两个收敛相关的开关】**（`Subsystems\converge\Content\html\conv_optionsdefaultstearconvergencesheet.htm`）
- **Restore tears on error**：收敛出错时把撕裂变量**恢复成上一次的值**。不勾选则显示最后一次计算值作为结果。
  > **AI 操作提示【官方支持】**：批量扫描中，这个开关是"不要让一次失败污染下一次起点"的官方机制。**建议打开。**
- **Flash tear streams**：是否对撕裂流做闪蒸。若要用中间结果、或通过内联 Fortran 访问撕裂流的温度/密度/熵 → 勾上；
  想省时间、不需要中间结果 → 不勾。若撕裂流关联 chemistry，此选项被忽略。

### 3.5 初值 / 重初始化（AI 的"④ 降级为上次收敛结果"在此有官方依据）

**【官方原文】**（`Subsystems\userguide1\Content\html\reinitializingsmsimulationcalculations.htm`）
> When you change your simulation specifications, **by default, Aspen Plus uses any previously generated results
> as a starting point** the next time you run the simulation.
> You may need to reinitialize if a block or the flowsheet:
> - **Fails to converge for no apparent reason**, after you changed the block or specifications that affect its
>   inlet streams
> - Has **multiple solutions** and you can obtain the one you want only by starting from your specified initial
>   block or stream estimates

| 重初始化对象 | 官方效果 |
|---|---|
| Block | 清除块结果，下次从初值运行该块 |
| Stream | 清除物流结果 → 对外部进料或**撕裂流**触发初始闪蒸 |
| Simulation | 清除全部结果 |
| Convergence | **重置迭代计数器**，收敛块标记为 Not Converged，**不使用任何先前的迭代历史**来预测下一轮猜测值；清除收敛变量终值等结果 |

**【官方原文 · 块级等价开关】**（`Subsystems\common\Content\html\blockoptionssimulationoptionssheet.htm`）
> **Use results from previous convergence pass**: By default, iterative calculations in Aspen Plus use any
> available previous results as an initial guess. If necessary, you can override this default and request that
> all calculations be reinitialized each calculation pass.
> Request reinitialization in either of these situations:
> - A block has multiple solutions and you can obtain the one you want only by starting from your own initial estimate
> - **A block or flowsheet fails to converge for no apparent reason, after one or more successful passes**

> **这两页官方原文直接支撑了两条相反的 AI 策略**：
> - **默认行为 = 用上一次结果作初值**（这正是用户设想的"④ 降级为上一次收敛结果作为初值"——它是 Aspen 的**默认行为**，
>   AI 什么都不用做就已在用；只有在需要"从干净初值重来"时才需要显式 Reinitialize）。**【官方支持】**
> - **"一个或多个 pass 成功后又莫名失败" → 官方明确建议 Reinitialize**。**【官方支持】**

### 3.6 RadFrac 收敛参数（塔在循环内时尤其重要）

**【官方原文】**（`Subsystems\radfrac\Content\html\radfracconvergencebasicsheet.htm`）
- **Maximum iterations**：对 inside-out 方法 = 外层循环最大迭代数；对 Newton 算法 = 最大 Newton 迭代数。
- **Error tolerance**：inside-out 下 = 外层收敛容差，**默认 1e-4**；Newton 下 = 给定值的 1e-3 倍，可用 Advanced 上的
  **Tolilmin** 覆盖。
- **Damping level**（阻尼级别）：Err/Tol 振荡时**增大**，同时相应增大 Maximum iterations
  （`troubleshooting_radfrac_convergence_fails_err_tol_diverging.htm`）。

**【官方原文】**（`Content\html\troubleshooting_flowsheet_convergence.htm` Solution 3）
> For RadFrac blocks within the loop, specify a **tighter Error Tolerance** on the RadFrac | Convergence | Basic
> sheet.

### 3.7 bkp 文本层参数名 → 含义映射（AI 直接改 bkp / 用 COM 写节点的抓手）

**【官方数据】** 以下关键字均为在 203 个官方示例 bkp 文本层中**实际出现**的字符串。
**【推断】** 右侧"含义/对应表单"是基于帮助描述的映射，参数名与表单字段的对应关系官方未在单一页面列出。

| bkp 文本层关键字 | 含义（推断） | 对应表单位置（推断） |
|---|---|---|
| `CONV-OPTIONS` / `PARAM` | 收敛选项全局段 | Convergence \| Options |
| `PARAM TOL = x` | 全局循环容差 | Convergence \| Options \| Defaults \| Tear Convergence |
| `PARAM TEAR-METHOD = X` | 默认撕裂流方法（WEGSTEIN/BROYDEN/DIRECT/NEWTON） | Convergence \| Options \| Defaults |
| `PARAM TRACEOPT = GRADUAL` | Trace 处理方式（另一取值 CUTOFF） | Tear Convergence |
| `PARAM CHECKSEQ = NO` | 是否检查用户序列所有回路都被撕开（默认 YES） | Options \| Defaults \| Sequencing |
| `PARAM TEAR-VAR = YES` | 新的 TEAR-VAR 选项（对应 A5 警告的官方建议） | CONV-OPTIONS |
| `PARAM VARITERHIST = YES` | 输出变量迭代历史 | Options \| Defaults |
| `PARAM COMPS = <group>` | 撕裂流收敛所用的组分组 | Tear Convergence |
| `PARAM TRACE = x` | Trace 阈值 | Tear Convergence |
| `WEGSTEIN WEG-MAXIT = n` | Wegstein 最大流股评估次数（默认 30） | Options \| Methods \| Wegstein |
| `WEG-QMIN` / `WEG-QMAX` | Wegstein 加速参数 q 的下/上界（默认 -5 / 0） | 同上 |
| `BROYDEN BR-MAXIT = n` | Broyden 最大评估次数 | Options \| Methods \| Broyden |
| `BR-XTOL = x` | Broyden X 容差 | 同上 |
| `BR-WAIT = n` | Broyden Wait | 同上 |
| `NEWTON NEW-XTOL = x` | Newton X 容差 | Options \| Methods \| Newton |
| `DIRECT DIR-MAXIT = n` | Direct 最大迭代 | Options \| Methods \| Direct |
| `SECANT SEC-MAXIT = n` / `BRACKET = YES` | Secant 迭代数 / 区间二分 | Options \| Methods \| Secant |
| `SQP SQP-TOL = x` | SQP 容差 | Options \| Methods \| SQP |
| `TEAR SID = <stream>` | 显式指定撕裂流 | Convergence \| Tear \| Specifications |
| `SID-TOL = x` | 单股撕裂流容差 | 同上 |
| `STATE = PH` / `STATE = H` | 收敛的状态变量（PH=压力+焓，H=仅焓） | 同上 |
| `CONVERGENCE <METHOD> "<name>"` | 用户自定义收敛块 | Convergence \| Convergence |
| `"BLOCK-OPTION" RESTART = YES` | 使用上次收敛结果作为初值 | Block Options \| Simulation Options |
| `"BLOCK-OPTION" TERM-LEVEL = n` / `TVAR-LEVEL = n` | 终止/变量诊断级别 | Block Options \| Diagnostics |
| `MAXOL` / `MAXIL`（RadFrac） | 外层/内层最大迭代 | RadFrac \| Convergence \| Basic / Advanced |
| `DAMPING = NONE\|MILD\|MEDIUM\|SEVERE` | RadFrac 阻尼级别 | RadFrac \| Convergence \| Basic |

---

## 4. 官方示例的收敛配置统计（203 个 bkp 实测）

> 方法：Python 遍历 `EX` 下全部 `.bkp`，`latin-1` 解码，在 `CONV-OPTIONS` 起到 `GRAPHICS_BACKUP` 之前的区间内做正则抽取。
> 统计口径：「出现该参数」= 用户**显式写入**（Aspen 只在用户改过默认值时才把参数写进 bkp）。

### 4.1 总体：绝大多数示例**不改**收敛设置

**【官方数据】**

| 指标 | 数值 | 占比 |
|---|---|---|
| 示例 bkp 总数 | **203** | 100% |
| **显式改写过**任意收敛参数 | **78** | **38.4%** |
| **完全使用默认**收敛设置 | **125** | **61.6%** |
| 含 `CONV-OPTIONS` 段（含空段） | 83 | 40.9% |
| 含系统生成收敛块 `$OLVER*` | 58 | 28.6% |
| 显式指定撕裂流 `TEAR SID =` | 23 | 11.3% |
| 显式建立 `CONVERGENCE` 块 | 18 | 8.9% |

> **结论【官方数据】**：**61.6% 的官方示例完全不动收敛设置**。这说明 Aspen 的默认收敛配置对多数工况是够用的，
> **AI 不应把"调收敛参数"当成默认动作**——先排查规格/物性/初值更可能命中真因。

### 4.2 明确指定方法时，官方示例用了什么

**【官方数据】**（按文件去重，同一文件同时用 TEAR-METHOD 与 CONVERGENCE 块只计一次）

| 方法 | 使用文件数 |
|---|---|
| **WEGSTEIN** | **13** |
| **BROYDEN** | **11** |
| **DIRECT** | **7** |
| SQP | 3 |
| SECANT | 1 |

分项拆解：

- **全局 `TEAR-METHOD`**（14 个文件）：**DIRECT 7 / BROYDEN 4 / WEGSTEIN 3**
  （`Subsystems\...` 典型：`Fertilizers\Potash\CrystallizationAndDrying.bkp` = `TEAR-METHOD = DIRECT TOL = 1E-005`；
  `Hydrogen\Alkaline electrolysis\...\Industrial Scale Alkaline Electrolyzer.bkp` = `TEAR-METHOD = WEGSTEIN TOL = 1E-06`）
- **用户自建 `CONVERGENCE` 块**（18 个文件，共 33 个块）：**WEGSTEIN 18 / BROYDEN 8 / SECANT 4 / SQP 3**
  （典型：`Bulk Chemicals\Methanol\methanol synthesis - ici syntex quench reactor process.bkp` 建了 3 个 WEGSTEIN 块；
  `Hydrogen\Ammonia decomposition\Ammonia decomposition furnace reactor.bkp` 建了 BROYDEN 块收敛 6 个设计规定）

> **【推断】** 值得注意：示例中 **DIRECT 作为全局 TEAR-METHOD 出现 7 次**，比帮助里"rare cases"的定位更常用。
> 这些多为**电解质/结晶/碳捕集**类强非线性、易振荡的流程（Potash 结晶、碱性电解、碳捕集 MEA）。
> **推断**：如果你的流程属于电解质/强非理想体系且 Wegstein 振荡，直接试 DIRECT 的成功率可能高于调 Wegstein 上界。
> 此为基于示例分布的统计推断，**非官方文档建议**。

### 4.3 各参数的取值分布（官方数据）

| 参数 | 出现文件数 | 观察到的取值（次数） |
|---|---|---|
| `WEG-MAXIT` | 10 | **100×4**, 50×3, 200×2, 1000×1 |
| `BR-MAXIT` | 10 | **1000×4**, 100×3, 60×1, 40×1, 200×1 |
| `DIR-MAXIT` | 7 | **300×4**, 100×1, 200×1, 500×1 |
| `SEC-MAXIT` | 6 | **100×5**, 300×1 |
| 全局 `TOL` | 11 | 0.0001×2, **1E-005×2**, .00010×1, .0010×1, 1E-05×1, **1E-028×1**, 1E-06×1, 0.01×1, .000010×1 |
| `SID-TOL`（单撕裂流） | 2 | 0.0005×4 |
| `BR-XTOL` | 2 | 1E-05, 1E-010 |
| `NEW-XTOL` | 1 | 1E-05 |
| `SQP-TOL` | 1 | 0.0001 |
| `WEG-QMIN` / `WEG-QMAX` | 1 / 2 | 均为 **.50**（`...\ENRTL-RK_Rate_Based_PZ+MDEA_Model.bkp` 上下界都设 0.5，即强阻尼） |
| `BR-WAIT` | 1 | 5（默认 2） |
| RadFrac `MAXOL` | 14 | **50×6, 100×6**, 200×4, 25×2 |
| `DAMPING`（RadFrac） | 12 | SEVERE×4, MILD×4, NONE×3, MEDIUM×3 |
| `TRACEOPT` | 9 | **GRADUAL 9 / 9**（无 CUTOFF） |
| `CHECKSEQ` | 22 | **NO 20**, YES 2 |
| `TEAR-VAR` | 5 | YES 5 / 5 |
| `VARITERHIST` | 7 | YES 8, NO 1 |
| `RESTART` | 5 | YES 4, NO 2 |

> **读数要点【官方数据 + 推断】**
> 1. **迭代次数普遍被调高一个数量级**：默认 30，示例里 WEG-MAXIT 常见 50–200，BR-MAXIT 常见 100–1000，
>    DIR-MAXIT 常见 300–500。说明"加大迭代上限"是官方示例最常用、最低风险的手段。**【官方数据支持】**
> 2. **容差多数被收紧而非放宽**：11 个显式设 TOL 的文件里，收紧到 1e-5 / 1e-6 的占多数，只有一个 0.01（放宽）。
>    与"放宽容差是最后手段"的官方原则一致。**【官方数据支持】**
> 3. **`TRACEOPT = GRADUAL` 出现 9 次、0 次 CUTOFF** —— 官方示例清一色选 Gradual。
>    **【推断】** 处理含微量组分的循环时，Gradual（把 100×Trace 阈值项加到分母，逐步放松对痕量组分的收敛判据）
>    比 Cutoff（直接跳过判据）更稳。
> 4. **`CHECKSEQ = NO` 出现 20 次** —— 大量示例关闭了序列检查。
>    **【推断】** 这些示例多半自定义了序列或撕裂流。**AI 若自定义序列，不要盲目模仿关掉 CHECKSEQ**；
>    关掉等于放弃了官方的"所有回路都被撕开"自动校验（见 3.4）。
> 5. **`TEAR-VAR = YES` 出现 5 次** —— 正是 A5 警告里官方建议的 "NEW TEAR-VAR OPTION IN CONV-OPTIONS"。
> 6. 示例里 **1 个文件设了 `TOL = 1E-028`**（极端收紧）。**【推断】** 这类极端值通常是为了压制特定警告，
>    **不建议 AI 在批量扫描中模仿**——会显著拖慢且易导致假不收敛。

### 4.4 典型示例的完整配置（可直接抄的范式）

**【官方数据】** 摘录三个代表性 bkp 的 `CONV-OPTIONS` 原文片段：

```
# 范式 A：碳捕集 MEA（严格 Rate-Based，强非线性）
Carbon Capture\Amines ENRTL-RK\ENRTL-RK_Rate_Based_MEA_Model.bkp
  PARAM TEAR-METHOD = BROYDEN  COMPS = LEANIN  TRACE = 2E-005  TRACEOPT = GRADUAL
  BROYDEN BR-MAXIT = 40

# 范式 B：氢能液化/气化（多循环、严格容差 + Broyden）
Power\Coal Gasification\igcc.bkp
  PARAM TOL = 1E-005
  WEGSTEIN WEG-MAXIT = 100
  BROYDEN  BR-MAXIT = 100  BR-WAIT = 5  BR-XTOL = 1E-010
  SECANT   SEC-XTOL = 1.0000E-10

# 范式 C：结晶/干燥（易振荡 → Direct）
Fertilizers\Potash\CrystallizationAndDrying.bkp
  PARAM TEAR-METHOD = DIRECT  TOL = 1E-005  CHECKSEQ = NO
  DIRECT  DIR-MAXIT = 300
  BROYDEN BR-MAXIT = 1000
```

> **【推断】** 范式 B 与 C 的共同模式值得 AI 借鉴：**显式设定主方法 + 同时把备选方法的参数也配好**（Wegstein、
> Broyden、Secant 的参数可以同时写在 CONV-OPTIONS 里，切换方法时只需改 `TEAR-METHOD` 一行，不必重配全部参数）。
> 这对"批量扫描中按策略切换加速方法"非常有利——**AI 可以在扫描开始前一次性把几种方法的参数都写好，运行时只改
> 方法名**。此为工程推断，官方文档未明说此用法。

---

## 5. 给 AI 的操作化建议：批量扫描遇到不收敛时的自动修复顺序

### 5.0 先纠正一个常见误解

用户设想的顺序是「① 换加速方法 ② **放宽容差** ③ 重置初值 ④ 降级为上次收敛结果 ⑤ 跳过记日志」。
**依据官方文档，需要两处修正**：

1. **"放宽容差"应后移，且通常应该收紧内层而不是放宽外层。**
   **【官方原文】**（`Content\html\troubleshooting_flowsheet_convergence.htm` Solution 3）
   > "Blocks inside the loop must be converged to **tighter** (smaller) tolerances than the recycle loop …
   > **Relax the convergence block tolerance only as a last resort.**"
2. **"④ 降级为上一次收敛结果作为初值"是 Aspen 的**默认行为**，不需要 AI 做任何事。**
   **【官方原文】**（`Subsystems\common\Content\html\blockoptionssimulationoptionssheet.htm`）
   > "By default, iterative calculations in Aspen Plus use any available previous results as an initial guess."
   AI 真正需要做的决策是**反过来**：什么时候**关掉**这个默认（即显式 Reinitialize）。

### 5.1 自动修复序列（按成本从低到高）

> 图例：**[官]** = 有官方文档明确支持；**[推]** = 工程经验推断，官方文档未直接支持。

#### 阶段 0 · 取证（必做，不可跳过）
| 步 | 动作 | 依据 |
|---|---|---|
| 0.1 | 读 `Tree.Data.Results Summary.Run-Status.Output` 的 `CVSTAT`/`SENSSTAT`/`RSTAT`，判 0/1/2 | **[官]** `userguide3\Checking the Status of Runs from Automation.htm` |
| 0.2 | `CVSTAT != 0` 时，把收敛诊断级别提到 **5**，输出导向 **history file**（不是 control panel） | **[官]** `convergencediagnosticmessagelevels.htm` + `runmessagesfiles___cpm_.htm`（官方明确说写入 history 可避免性能损失） |
| 0.3 | 导出 `.cpm`／`.rep`，正则抽 `Max Err/Tol` 序列与 `ERROR`/`SEVERE ERROR`/`WARNING` 行 | **[官]** `controlpanelmessages.htm`（`Max Err/Tol < 1.0` = 收敛） |
| 0.4 | 用错误串去帮助文本库做模糊检索，命中官方页面 | **[推]** 可扩展，弥补无官方错误清单（见 2.0） |
| 0.5 | **关闭 `Use affected block logic`** | **[官 · 关键]** `Content\html\Changing a Convergence Block Tolerance.htm`。不关的话，改完收敛参数重跑会**空转并假报收敛**，整个修复循环失效 |

#### 阶段 1 · 低成本、无副作用的修复（先试这些）
| 步 | 动作 | 依据 |
|---|---|---|
| 1.1 | **提高迭代上限**（Wegstein/Broyden/Secant 默认 30；官方建议 "Maxit above 30"；示例实测常用 50–200，Broyden 甚至 1000） | **[官]** `diagnosingtearstreamconvergence.htm` + **[官方数据]** 4.3 |
| 1.2 | 若 Err/Tol 稳定但慢：Wegstein **Lower Bound → -20/-25/-50**（官方给了 20 → 50 的递进路径） | **[官]** `diagnosingtearstreamconvergence.htm` + `wegsteinaccelerationparameter.htm` |
| 1.3 | 若 Err/Tol 振荡：先 **Wegstein Upper Bound = 0.5**（阻尼）；无效则**改用 Direct 方法** | **[官]** 同上 + `resolvingsequenceandconvergenceproblems.htm` 第 5 步 |
| 1.4 | 若 Err/Tol 降到阈值不动（典型值 ~10）：**收紧内层**块/收敛块的容差（循环内 RadFrac → RadFrac\|Convergence\|Basic 的 Error Tolerance；全局闪蒸 → Setup\|Calculation Options\|Flash Convergence） | **[官 · 首选]** `troubleshooting_flowsheet_convergence.htm` Solution 3 |

#### 阶段 2 · 结构性修复（改动较小，收益大）
| 步 | 动作 | 依据 |
|---|---|---|
| 2.1 | **换方法**：Broyden/Newton 失败 → 退回 Wegstein；强耦合多撕裂流+多设计规定 → Broyden；Broyden 也不行 → Newton（但组分多时**别用** Newton） | **[官]** `diagnosingtearstreamconvergence.htm`、`broydenmethod.htm`、`newtonmethod.htm` |
| 2.2 | Broyden/Newton 失败时先 **Wait → 4**；若撕裂流与设计规定在同一收敛块，先用 **Tear Tolerance / Tear Tolerance Ratio** 只收敛撕裂流 | **[官]** `diagnosingtearstreamconvergence.htm` |
| 2.3 | 内外层耦合 → 用 **Design Spec Nesting** 让 Broyden/Newton 同时收敛内外层（默认 Inside） | **[官]** `specifyingsequencingparameters.htm` |
| 2.4 | 设计规定 Err/Tol 不变/撞边界 → Secant 设 **Bracket = Yes**（平坦）或 **Check Bounds**（非单调/撞边界） | **[官]** `secantmethod.htm` + `diagnosingdesignspecificationconvergence.htm` |
| 2.5 | **打开 Restore tears on error**（收敛出错时撕裂变量回滚到上次值） | **[官]** `conv_optionsdefaultstearconvergencesheet.htm` |
| 2.6 | **检查组分是否有出口**（含反应产物）；**检查循环内至少一个块设定了绝对压力而非压降** | **[官]** `troubleshooting_flowsheet_convergence.htm` Cause 1 / Cause 5 |

#### 阶段 3 · 需要改初值/结构的修复
| 步 | 动作 | 依据 |
|---|---|---|
| 3.1 | **"一个或多个 pass 成功后又莫名失败" → 显式 Reinitialize**（Block / Stream / Convergence / Simulation） | **[官]** `reinitializingsmsimulationcalculations.htm` + `blockoptionssimulationoptionssheet.htm`（官方明确列出此情形） |
| 3.2 | 给撕裂流**显式初值**（循环内含精馏塔时官方称"有时必要"） | **[官]** `initialestimatesfortearstreams.htm` |
| 3.3 | 重选撕裂流：变化小、组分少、来自设定出口温度的块、热流股或全气相流股；去掉冗余撕裂流 | **[官]** `diagnosingtearstreamconvergence.htm` + `tearform.htm` |
| 3.4 | 用 **component group / State variables** 减少收敛变量数（主要配合 Broyden/Newton/SQP 减矩阵规模与数值导数扰动次数） | **[官]** `specifyingtearstreams.htm` |
| 3.5 | 用 **Direct（q 上下界都 = 0）** 跑一遍，观察是否有组分持续累积 → 判断"是否根本不存在稳态解" | **[官]** `diagnosingtearstreamconvergence.htm` |
| 3.6 | 断开循环流单独跑，拿初值并做敏感度探查 | **[官]** 同上 |

#### 阶段 4 · 最后手段
| 步 | 动作 | 依据 |
|---|---|---|
| 4.1 | **放宽外层收敛块容差** | **[官]** 但官方明言 "only as a last resort" |
| 4.2 | 简化模型：Mixer 减少撕裂流、MHeatX 替 HeatX、RGibbs 用 TP 而非 PQ、避免严格 HeatX 进入不可行工况 | **[官]** `troubleshooting_flowsheet_convergence.htm` General Strategies |
| 4.3 | **跳过该工况并记审计日志**，日志必须含：工况参数、`CVSTAT`、错误串、`Max Err/Tol` 终值、已尝试的修复步骤、撕裂流变量 | **[推]** 工程实践。但"记录哪些字段"可依据 **[官]** 的 Run-Status 状态位与 Tear/Spec Summary 字段（见 2.2） |
| 4.4 | 缩小扫描步长 / 用上一个收敛点为起点做连续延拓 | **[推]** 工程经验；官方仅在 Sensitivity 页提到"不重初始化时上一行结果会作下一行初值"（`sensitivityinputoptionalsheet.htm`），可视为间接支撑 |

### 5.2 批量扫描的"预防性"配置（在开跑前一次性设好）

| 动作 | 理由 | 依据 |
|---|---|---|
| 一次性把 **Wegstein / Broyden / Direct / Secant** 的参数都写进 CONV-OPTIONS，运行时只切 `TEAR-METHOD` | 切换方法只需改一行，不必重配参数 | **[推]**（范式来自官方示例 B/C 的实际写法，见 4.4） |
| 打开 **Restore tears on error** | 防止失败工况污染下一次起点 | **[官]** `conv_optionsdefaultstearconvergencesheet.htm` |
| 打开 **VARITERHIST**（变量迭代历史） | 事后能复盘 Err/Tol 曲线 | **[官]** 参数存在于 Convergence Options；示例中使用 8 次 |
| 每个独立 Run 前显式 **Reinitialize**（或在 Sensitivity/扫描的 Options 里明确 Reinitialize 策略） | 被扫变量会停留在最后一行值，污染下一次 Run | **[官]** `sensitivityinputoptionalsheet.htm` 的 Note |
| 扫描前静态检查：循环内至少一个块设定了**绝对压力** | Cause 5 是批量扫描典型杀手 | **[官]** `troubleshooting_flowsheet_convergence.htm` Cause 5 |
| 日常诊断级别 3，失败时临时提到 5 并只写 history file | 平衡信息量与性能 | **[官]** `convergencediagnosticmessagelevels.htm` + `runmessagesfiles___cpm_.htm` |
| 改收敛参数前**先关 Use affected block logic** | 否则重跑空转假报收敛 | **[官]** `Changing a Convergence Block Tolerance.htm` |

### 5.3 一句话速查（AI 的 if-then）

```
CVSTAT==1?
├─ Max Err/Tol 稳定下降      → Maxit ↑（30 → 100 → 200）                    [官]
├─ 稳定但慢                  → Wegstein Lower Bound -20 → -50               [官]
├─ 振荡                      → Wegstein Upper Bound 0.5 → 改 Direct          [官]
├─ 降到 ~10 不动             → 收紧内层块/闪蒸容差（不是放宽外层！）          [官]
├─ Broyden/Newton 失败       → Wait=4 → 先只收敛撕裂流 → 退回 Wegstein        [官]
├─ 设计规定 Err/Tol 不变     → Secant Bracket=Yes                            [官]
├─ 设计规定撞边界            → Secant Bracket=Check bounds + 调边界/初值      [官]
├─ "WAS NEVER EXECUTED"      → Initialization = Solve（不是收敛问题）         [官]
├─ "NOT IN MASS BALANCE"     → 检查序列 / Calculator / 是否改了物性参数       [官]
├─ "CROSSING THE LOOP..."    → 收紧撕裂流容差到 <1e-4                        [官]
├─ 之前成功过、这次莫名失败   → 显式 Reinitialize                             [官]
├─ 怀疑组分累积              → Direct（q=0）跑一遍看是否持续累积              [官]
└─ 全部无效                  → 放宽容差（最后手段）→ 跳过 + 审计日志          [官]/[推]
```

---

## 附录 A · 本次核查的「未找到」清单（避免后续重复劳动）

| 想找的东西 | 结论 |
|---|---|
| 官方**集中式错误消息清单 / 错误代码表** | **【未找到】**。9875 个帮助页中不存在。替代：按模块分散的 troubleshooting 页；flowsheet 级有 6 条入口清单（`Content\html\flowsheet_errors_or_warnings.htm`） |
| 错误**编号 / 错误码**（如 "error number"） | **【未找到】**，`error number`/`message number`/`error index` 全文 0 命中 |
| Wegstein/Direct 的 `Maximum Flowsheet Evaluations` 在 `conv_optionsmethods*` 页的默认值 | **【未找到】**（这些是表单字段参考页，未列默认值）。默认值来自 `userguide2\wegsteinmethod.htm`（30）；Direct 的默认值**未在任何检索到的页面明确给出** |
| 收敛块 `Tolerance` 与 Tear 表单 `Tolerance` 为何默认不同（0.0001 vs 0.001） | **【未找到】**官方解释，见 3.3 的推断说明 |
| DesignSpec Summary 的 `Status` 字段中 "Converged / Not Converged" 与边界的准确对应 | 官方原文措辞疑似笔误，已标注，见 2.2 |
| Sensitivity 中断（而非单点失败）的专门排错页 | **【未找到】**。仅有 `sensitivityinputoptionalsheet.htm` 的 Reinitialize 说明与 `SENSSTAT` 状态位 |

## 附录 B · 关键页面速查（相对 `HH`）

| 主题 | 路径 |
|---|---|
| 循环不收敛通用排错（最重要） | `Content\html\troubleshooting_flowsheet_convergence.htm` |
| flowsheet 错误/警告清单 | `Content\html\flowsheet_errors_or_warnings.htm` |
| 块物料不平衡 | `Content\html\Error Block is Not in Mass Balance.htm` |
| 收敛块从未执行 | `Content\html\Error__Convergence_Block_Never_Executed.htm` |
| 跨循环物流不平衡 | `Content\html\Flowsheet_Warning__Streams_Crossing_the_Loop_are_not_in_Mass_Balance.htm` |
| 信息撕裂流警告 | `Content\html\flowsheet_information_tears_warning.htm` |
| MCS 错误 | `Content\html\flowsheet_maximal_cyclic_subsystem_errors.htm` |
| 改容差不重算（Use affected block logic） | `Content\html\Changing a Convergence Block Tolerance.htm` |
| 排错总入口 | `Content\html\troubleshooting_aspen_plus.htm` |
| 撕裂流诊断（Err/Tol 表） | `Subsystems\userguide2\Content\html\diagnosingtearstreamconvergence.htm` |
| 设计规定诊断（Err/Tol 表） | `Subsystems\userguide2\Content\html\diagnosingdesignspecificationconvergence.htm` |
| 9 步排查 SOP | `Subsystems\userguide2\Content\html\resolvingsequenceandconvergenceproblems.htm` |
| 各方法默认值 | `Subsystems\userguide2\Content\html\{wegstein,broyden,newton,secant,direct}method.htm` |
| q 参数语义 | `Subsystems\userguide2\Content\html\wegsteinaccelerationparameter.htm` |
| 诊断消息格式 / 级别 | `Subsystems\userguide2\Content\html\convergencediagnostics.htm`、`Subsystems\converge\Content\html\convergencediagnosticmessagelevels.htm` |
| Control Panel 消息格式 | `Subsystems\userguide2\Content\html\controlpanelmessages.htm` |
| 撕裂流指定与默认值 | `Subsystems\userguide2\Content\html\specifyingtearstreams.htm` |
| 撕裂/序列参数 | `Subsystems\userguide2\Content\html\specifyingsequencingparameters.htm` |
| **COM 运行状态位** | `Subsystems\userguide3\Content\html\Checking the Status of Runs from Automation.htm` |
| COM 错误处理 | `Subsystems\userguide3\Content\html\errorhandling.htm` |
| Run2 异步示例 | `Subsystems\userguide3\Content\html\run2interface.htm` |
| 重初始化 | `Subsystems\userguide1\Content\html\reinitializingsmsimulationcalculations.htm` |
| 运行消息文件 | `Subsystems\userguide1\Content\html\runmessagesfiles___cpm_.htm` |
| 块级"使用上次结果"开关 | `Subsystems\common\Content\html\blockoptionssimulationoptionssheet.htm` |
| 撕裂收敛默认（Restore/Flash） | `Subsystems\converge\Content\html\conv_optionsdefaultstearconvergencesheet.htm` |
| 收敛块类型一览 | `Subsystems\converge\Content\html\Convergence Blocks.htm` |
| RadFrac 错误清单 | `Subsystems\apunitop\Content\html\troubleshooting_radfrac_errors_and_warnings.htm` |
| RadFrac 收敛失败 | `Subsystems\apunitop\Content\html\troubleshooting_radfrac_convergence_problems.htm` |
| RadFrac 发散/振荡 | `Subsystems\apunitop\Content\html\troubleshooting_radfrac_convergence_fails_err_tol_diverging.htm` |
| RadFrac 收敛基本页 | `Subsystems\radfrac\Content\html\radfracconvergencebasicsheet.htm` |
| 灵敏度 Reinitialize 说明 | `Subsystems\mdanmstr\Content\html\sensitivityinputoptionalsheet.htm` |
| 收敛结果（Tear/Spec）汇总字段 | `Subsystems\results\Content\html\resultssummaryconvergence{tear,designspec}summarysheet.htm` |

## 附录 C · 复现脚本

本文档的全部统计可用以下脚本复现（已保存在同目录）：

| 脚本 | 作用 |
|---|---|
| `_workshop\scan_index.py` / `scan2.py` / `scan3.py` | HTML 索引、文件名关键词、错误消息清单核查 |
| `_workshop\extract.py` | HTML 剥标签 + 全文检索（`search` / `dump` 两种模式，结果写 `_search.txt` / `_dump.txt`） |
| `_workshop\bkp_scan.py` / `bkp_probe.py` / `bkp_probe2.py` | 203 个 bkp 列表与文本层结构探测 |
| `_workshop\bkp_analyze.py` / `bkp_analyze2.py` / `bkp_summary.py` | bkp 收敛配置统计（结果见 `_bkp_stat2.txt`、`_bkp_summary.txt`） |
