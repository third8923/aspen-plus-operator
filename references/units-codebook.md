# Aspen .bkp 单位代码字典（实测破译）

> 数据来源：本机 Aspen Plus V14 `GUI\Examples` **203 个 .bkp** 全量统计 +
> `happ.tlb` 类型库枚举 + `C:\ProgramData\AspenTech\Aspen Plus V14.0\HtmlHelp` 官方原文。
> 全部结论可复现，不依赖记忆。

## 一、结构：`<维度> <子码>` 两级

bkp 里每个带量纲数值后面跟两段尖括号：**第一个是维度编号，第二个才是具体单位**。

```
PARAM TEMP = 419 <22> <2>   PRES = 267 <20> <2>
             ↑    ↑          ↑    ↑
             │    └─ 子码 2 = °F  │    └─ 子码 2 = psi
             └────── 维度 22 = 温度 └────── 维度 20 = 压力
```

**验证方式**：bkp 里的 `UNITSET BASESET = MET ( 3 3 3 … )` 是一个 **155 维向量，下标即维度编号**。
METCBAR 在第 20 位写 `5`（bar）、第 22 位写 `4`（°C），与本文表格完全吻合。

⚠️ **`<22>` 不等于 °F**。技能里"`<22>`=°F"只在 ENG 模型上碰巧成立。

## 二、温度 `<22>`

| 子码 | 单位 | 典型所属单位集 | 实测取值特征 |
|---|---|---|---|
| `<1>` | **K** | SI | 20.9–800，中位 371 |
| `<2>` | **°F** | ENG / ENGPETRO | −307–1670，中位 200 |
| `<3>` | **K** | MET | 273.0 / 288.150 / 323.150 / 573.15（都是 °C 整数 +273.15） |
| `<4>` | **°C** | METCBAR / 自定义 °C 集 | 20 / 25 / 70 / 84 / 105 |

## 三、压力 `<20>`

| 子码 | 单位 | 实测特征 |
|---|---|---|
| `<1>` | **Pa (N/m²)** | 中位 2.26e7 |
| `<2>` | **psi** | 中位 60；ENG 默认 |
| `<3>` | **atm** | 中位 1，区间 0.132–50；MET 默认。**含 `1.0` 共 21 次** |
| `<5>` | **bar** | 中位 1.5；METCBAR 默认。含 `1.0` 共 70 次 |
| `<6>` | **mmHg** | 出现 750.0616827（=1 bar）、760.0 |
| `<8>` | **kgf/cm²** | 出现 **1.03322745（6 次）**＝1 atm 的 kgf/cm² 值 |
| `<10>` | **kPa** | 中位 168，区间 12.5–3000 |
| `<12>` | **mbar** | 中位 1010 |
| `<13>` | **mmHg / torr** | 中位 780，区间 0.29–1610 |
| `<20>` | **MPa** | 出现 0.00689475729（=1 psi）；中位 0.517 |

**`<20><2>`(psi) 与 `<20><5>`(bar) 相差 14.5038 倍** —— 这是 bkp 文本层最经典的量纲事故。

> ⚠️ **`<20><3>` 是 atm，不是 kg/cm²**（2026-09-15 专项复测裁定，曾有误判）。
> 裁定方法：1 atm = 1.033227 kgf/cm²。`<3>` 下"标准大气压"写作 `1.0`（21 次）→ atm；
> `<8>` 下写作 `1.03322745`（6 次）→ kgf/cm²。两者相差 3.32%，**判错会静默引入该量级误差**。
> 不要凭单位集名称（如 MET 的 KG/SQCM）推断子码，必须用数值特征判定。

## 四、流量与其它

| 维度 | 含义 | 常见子码 |
|---|---|---|
| `<-80>` | 质量流量 | `<3>` = kg/hr（MET/METCBAR 体系下 `BASIS-D` / `BASIS-B` 用这个） |
| `<-89>` | 摩尔流量 | `<3>` 最常见；ENG 体系下为 lbmol/hr |
| `<75>` | 压降（DP-COL 等） | `<5>` = psi |
| `<17>` | 长度 | `<1>` = m，`<7>` = inch（PIPE 的 LENGTH / IN-DIAM） |
| `<39>` | 摩尔能量（活化能） | `<3>` = cal/mol |
| `<0> <0>` | **无量纲** | 分数、效率等 |

> ⚠️ 负维度（`<-80>` / `<-89>`）的子码含义尚未像温压那样被 203 个样本完整标定。
> **动手前用 `scripts/aspen_units.py` 的 `probe_code()` 在目标 bkp 上实测一次再定。**

## 五、单位集（INSET）的真实写法与分布

bkp 里的形态是（注意：**没有 `IN-UNITS = ENG` 这种写法**）：

```
? SETUP GLOBAL ? \ "IN-UNITS" INSET = METCBAR \
```

203 个官方 .bkp 的分布（前 10）：

| INSET | 文件数 | 温/压默认码 |
|---|---|---|
| SI | 53 | `<22><1>` / `<20><1>` |
| METCBAR | 37 | `<22><4>` / `<20><5>` |
| ENG | 24 | `<22><2>` / `<20><2>` |
| SET1（自定义） | 19 | `<22><4>` / `<20><5>` |
| ENGPETRO | 5 | `<22><2>` / `<20><2>` |
| METSOLID | 5 | `<22><4>` / `<20><5>` |
| METSPEC / H2 / REPORT | 各 4 | 混合 |
| MET | 3 | `<22><3>` / `<20><3>` |

**ENG 只占约 12%。别把 ENG 当默认。**

## 六、铁律：代码是绝对值，不能由单位集推断

实测存在这样的文件：**INSET = SI，但某个 TEMP 却是 `<22><2>`（°F）、PRES 是 `<20><13>`（mmHg）**。
Aspen 允许单个参数覆盖全局单位集。

> ✅ 正确：读目标数值**自己身上**的那两个尖括号 → 查本字典 → 换算。
> ❌ 错误：看 `INSET` 是 SI 就以为所有温度都是 K。

## 七、COM 侧的单位 API（类型库实证，推翻旧结论）

`IHNode` 上真实存在（此前文档误记为"没有 Units 属性"）：

| 成员 | 说明 |
|---|---|
| `UnitString` (String, 只读) | 该节点当前单位名，**取数后务必回读校验** |
| `ValueForUnit(unitrow, unitcol)` | 按指定单位码取值 |
| `SetValueAndUnit(Value, unitcol, [force])` | **带单位写入**；⚠️ `unitcol` 是**整数**，不是 `"C"`/`"bar"` |
| `SetValueUnitAndBasis(Value, unitcol, basis, [force])` | 带单位 + 基准写入 |
| `AttributeValue(HAP_UNITCOL=3, True) = <码>` | 切换节点单位，之后 `.Value` 即为新单位下的值 |

官方示例（`Subsystems\userguide3\…\exampleofchangingunitsofmeasure.htm`）：

```vb
ihPres = ihAPsim.Tree.Data.Blocks.B3.Output.B_PRES
MsgBox ihPres.Value & Chr(9) & ihPres.UnitString
ihPres.AttributeValue(Happ.HAPAttributeNumber.HAP_UNITCOL, True) = 5   ' → bar
MsgBox ihPres.Value & Chr(9) & ihPres.UnitString
```

**实践建议**：写参数先 `SetValueAndUnit(v, code)`，随后立刻读一次 `UnitString` 确认没被解释错。

## 八、安全改写模板

```python
CODE = {(22, 2): "degF", (22, 4): "degC", (22, 1): "K", (22, 3): "K",
        (20, 2): "psi", (20, 5): "bar", (20, 20): "MPa", (20, 1): "Pa",
        (20, 3): "atm", (20, 10): "kPa"}

def sub_value(txt, key, new_val, expect_dim, expect_code):
    """只在维度/子码与预期一致时才替换，否则抛错——防止静默算错。"""
    import re
    pat = re.compile(r"(%s\s*=\s*)[-+0-9\.Ee]+(\s*<%d>\s*<%d>)" % (key, expect_dim, expect_code))
    new, n = pat.subn(lambda m: m.group(1) + repr(new_val) + m.group(2), txt, count=1)
    if n != 1:
        raise RuntimeError(
            "替换失败或单位码不符：%s 期望 <%d><%d>，文件里不是这个单位，先 probe 再改"
            % (key, expect_dim, expect_code))
    return new
```
