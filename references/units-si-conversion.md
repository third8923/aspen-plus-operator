# 单位制：原生 SI 切换、代码字典与英制→SI 换算

> 2026-09 复核（本次核查基于 203 个官方 bkp + COM 类型库 + 官方 HtmlHelp 原文重写）。
> **旧版"COM 节点没有 Units 属性、写参数只能手工换算英制"的结论是错的，已删除。**

## 一、首选路线（按优先级）

1. **读结果**：`node.Value` + **`node.UnitString` 回读单位**（不要凭单位集猜）。
   需要特定单位时用 `node.ValueForUnit(unitrow, unitcol)`，或先把
   `node.AttributeValue(HAP_UNITCOL=3, True) = <码>` 再读 `.Value`。
2. **写参数**：`node.SetValueAndUnit(值, unitcol)` —— **unitcol 是整数代码，不是 "C"/"bar"**。
   写完立刻回读 `UnitString` 校验。
3. **改 bkp 文本**：按目标数值**自带的** `<维度> <子码>` 换算，见 `references/units-codebook.md`。
4. **整体切换**：把 `"IN-UNITS" INSET = X` 换成 `SI-CBAR` 之类，影响 GUI 显示与 COM 读 Output。

## 二、单位集机制（实测）

- bkp 文本：`? SETUP GLOBAL ? \ "IN-UNITS" INSET = X \`
  （⚠️ **没有 `IN-UNITS = ENG` 这种写法**）
- 本机 V14 已定义：ENG、MET、METCBAR、METCKGCM、SI-CBAR、SI 等。
  SI-CBAR = `BASESET = SI`，即"SI 基准 + °C + bar + /hr"，最贴合国内习惯。
- 切换：文本层改 INSET 保存即生效；GUI 走 Setup → Units-Sets。

### 203 个官方 .bkp 的 INSET 分布（别把 ENG 当默认）

| INSET | 数量 | 温/压默认码 |
|---|---|---|
| SI | 53 | `<22><1>` K / `<20><1>` Pa |
| METCBAR | 37 | `<22><4>` °C / `<20><5>` bar |
| ENG | 24 | `<22><2>` °F / `<20><2>` psi |
| SET1（自定义） | 19 | `<22><4>` / `<20><5>` |
| MET | 3 | `<22><3>` **K** / `<20><3>` atm |

**ENG 仅占约 12%。**

### ⚠️ MET 的温度是 K，不是 °C

INSET=MET 的官方 bkp 里 TEMP 全是 `288.150 / 323.150 / 273.0 / 573.15`（= °C 整数 +273.15）。
而 METCBAR 才是 °C。**MET 与 METCBAR 只差一个压力单位，温度却差 273**——切换时极易踩。

## 三、COM 读写行为（类型库实证，非记忆）

`IHNode` 上真实存在的单位相关成员：

| 成员 | 说明 |
|---|---|
| `UnitString`（String，只读） | 节点当前单位名 |
| `ValueForUnit(unitrow, unitcol)` | 按指定单位码取值 |
| `SetValueAndUnit(Value, unitcol, [force])` | **带单位写入**，unitcol 为整数 |
| `SetValueUnitAndBasis(Value, unitcol, basis, [force])` | 带单位 + 基准写入 |
| `AttributeValue(HAP_UNITCOL=3, True) = <码>` | 切换节点单位后再读 `.Value` |

常量：`HAP_VALUE=0`、`HAP_UNITROW=2`、`HAP_UNITCOL=3`、`HAP_UOM=81`、`HAP_UOMSET=82`。

官方示例（`Subsystems\userguide3\Content\html\exampleofchangingunitsofmeasure.htm`）：

```vb
ihPres = ihAPsim.Tree.Data.Blocks.B3.Output.B_PRES
MsgBox ihPres.Value & Chr(9) & ihPres.UnitString
ihPres.AttributeValue(Happ.HAPAttributeNumber.HAP_UNITCOL, True) = 5   ' → bar
MsgBox ihPres.Value & Chr(9) & ihPres.UnitString
```

### 三条纪律

1. **取数先读 UnitString**，再写进报告。单位集是 SI 也可能有参数自带 °F（实测存在）。
2. **写参数用 SetValueAndUnit 显式给码**，不要裸写 `.Value`——裸写按节点内部单位解释。
   （旧版记录的现象"SI-CBAR 下写 215 被当成 215°F"是真的，但那是**裸写 `.Value`** 的后果，
   不是接口限制。）
3. **切换 INSET 只影响 GUI 显示与 COM 读 Output**，不改变 bkp 文本层的存储代码。

## 四、换算表（ENG 取值 + 手工换算备用）

| 物理量 | Aspen ENG | 中国常用 | 换算系数 | 复核 |
|---|---|---|---|---|
| 温度 | °F | °C / K | °C=(°F−32)×5/9；K=°C+273.15 | ✅ |
| 压力 | psia | MPa / bar / kPa | 1 psia=6.8948 kPa=0.06895 bar=0.006895 MPa；1 MPa=145.0377 psia | ✅ |
| 质量流量 | lb/hr | kg/h | 1 lb/hr=0.45359 kg/h | ✅ |
| 摩尔流量 | lbmol/hr | kmol/h | 1 lbmol=0.45359237 kmol | ✅ |
| 热负荷 | Btu/hr | kW / kJ/h | 1 Btu/hr=1.05506 kJ/h=0.000293071 kW | ✅ |
| 体积流量 | cuft/hr | m³/h | 1 cuft=0.02832 m³ | ✅ |
| 密度 | lb/cuft | kg/m³ | 1 lb/cuft=16.018 kg/m³ | ✅ |
| 比焓 | Btu/lb | kJ/kg | 1 Btu/lb=2.326 kJ/kg | ✅ |

（上表全部经 Python 重算核对通过。）

## 五、处理原则

- **取数零换算靠 UnitString，不靠猜**：SI-CBAR 模型读 Output 直接是 kg/hr / °C / bar / W；
  但混批多个 bkp 时必须**逐个记录 INSET 并回读 UnitString**（不同模型之间不互通）。
- **SI-CBAR 热负荷单位是 W**（−329277.9 W = −329.28 kW），汇报时 ÷1000。
- **改 bkp 文本必须按该数值自带的代码换算**（`scripts/aspen_units.py` 的 `sub_value` 会在
  代码不符时直接抛错，防静默量纲事故）。
- **汇报交付**：面向国内一律 SI（°C / MPa / kg/h / kW）；与美国工程公司交换时保留原值并标注单位。
- **bkp 交换**：单位集随模型保存，换机打开不变；文本层代码与 INSET 无关，改文本必须查代码。
