# COM 自动化（主通道）

本机实测（Aspen Plus V14）。**本文所有接口签名以本机 COM 类型库
`C:\Program Files\AspenTech\AprSystem V14.0\GUI\Xeq\happ.tlb`（类型库名 `Happ`）枚举结果为准**，
不再是"试出来"的。

ProgID：`Apwn.Document` / `Apwn.Document.40.0`（两者均已注册）。

## 连接与生命周期

```python
import win32com.client, pythoncom
pythoncom.CoInitialize()
doc = win32com.client.Dispatch("Apwn.Document.40.0")
doc.SuppressDialogs = True            # 必须：抑制引擎弹窗，防不可见会话挂起
doc.InitFromArchive2(r"<path>\model.bkp", 0)   # 第二个参数 0 是官方写法，别省
tree = doc.Tree
# ... 改参、运行、取数 ...
doc.SaveAs2(r"<path>\output.bkp", True)
doc.Close(0)                          # IHapp.Close(reserved)，给个实参更安全
pythoncom.CoUninitialize()
```

`IHapp` 上确认存在的初始化方法：

| 方法 | 签名（类型库） |
|---|---|
| `InitFromArchive2` | `(filename, host_type, node, username, password, working_directory, failmode)` |
| `InitFromArchive3` | `(filename, open_type, host_type, …)` |
| `InitFromFile` / `InitFromFile2` | `(filename, readonly[, …])` |
| `InitFromTemplate` / `InitFromTemplate2` | `(filename[, …])` |
| `InitNew` / `InitNew2`、`InitFromXML` | 新建 |

## 运行协议（顺序不能错）

```python
eng = doc.Engine
eng.Reinit()                 # 见下方说明：SuppressDialogs 下优先用 Engine.Reinit
doc.Run2(1)                  # IHapp.Run2(async)；1=异步
import time
while eng.IsRunning:
    time.sleep(2)
```

- `Run2` 在 **`IHapp` 和 `IHAPEngine` 上都存在**，签名均为 `Run2(async)`。
  → **务必写 `Run2(1)` 并轮询 `IsRunning`**，不要写无参 `Run2()`。
- **`Reinit` 选型（重要，官方实锤）**：`Compatibility_Notes_for_Aspen_Plus_V7.3.htm` 原文——
  *"A bug … caused HappLS.Reinit() to not actually reinitialize the simulation if dialogs
  were suppressed. … The bug did not affect HappLS.Engine.Reinit()"*
  → 在 `SuppressDialogs=True`（COM 必开）下**优先 `Engine.Reinit()`**。
  `IHAPEngine.Reinit(object_type, object_id)`，`IAP_REINIT_SIMULATION = 4`。
- `IHAPEngine` 其它可用方法：`Run()`、`Run2(async)`、`Stop()`、`Step()`、`ProcessInput()`、
  `MoveTo()`、`Host()`、`RunControl`、`OptionSettings`、`EngineFilesSettings`、
  `ExportReport(filename, contents, object_id)`（**三个参数**，少传会报"无效的参数数目"）。

## 取报错：不用开 GUI（旧结论已推翻）

```python
doc.Export(2, r"<path>\model.rep")     # HAPEXP_REPORT = 2
doc.Export(6, r"<path>\runmsg.txt")    # HAPEXP_RUNMSG = 6
```

`HAPEXPType` 枚举（本机类型库）：`HAPEXP_BACKUP=1`、`HAPEXP_REPORT=2`、`HAPEXP_SUMMARY=3`、
`HAPEXP_INPUT=4`、`HAPEXP_RUNMSG=6`、`HAPEXP_REPORT_INPUT=7`、`HAPEXP_PDF=15`。

官方示例（`exportingfilesfromanautomationclient.htm`）：

```vb
MySim = CreateObject("Apwn.Document")
Call MySim.InitFromArchive2("pfdtut.bkp", 0)
Call MySim.Export(HAPEXP_REPORT, "pfdtut.rep")
```

→ 纯 COM 下即可导出报告文本读报错；"只能开 GUI 看报错"不再是硬约束。

## 变量读写矩阵（单位一律回读 UnitString 确认）

| 用途 | 节点路径 | 备注 |
|---|---|---|
| 改进料温度 | `Data\Streams\<流股>\Input\TEMP\MIXED` | 用 `SetValueAndUnit` 给单位码 |
| 改进料组分流量 | `Data\Streams\<流股>\Input\FLOW\MIXED\<组分>` | 摩尔流量，单位看 `UnitString` |
| 改块温度/压力 | `Data\Blocks\<块>\Input\TEMP` / `PRES` | 写后需 Reinit+Run2 生效 |
| 改反应转化率 | `Data\Blocks\REACTOR\Input\CONV\1` | RStoic 第 1 个反应 |
| 读组分质量流 | `Data\Streams\<流股>\Output\MASSFLOW3\<组分>` | 最常用输出 |
| 读液相摩尔流 | `Data\Streams\<流股>\Output\L1_FLOW` | 全液相流股总摩尔流量 |
| 读块热负荷 | `Data\Blocks\<块>\Output\QCALC` | 单位随单位集（W / Btu/hr） |
| 读块温度 | `Data\Blocks\<块>\Output\B_TEMP` / `R_TEMP` | |
| 读汽化率 | `Data\Streams\<流股>\Output\VFRAC_OUT\MIXED`、`Blocks\<块>\Output\B_VFRAC` | 无量纲 |

**单位写法**（见 `references/units-si-conversion.md` 与 `units-codebook.md`）：

```python
node = tree.FindNode(r"Data\Blocks\REACTOR\Input\TEMP")
node.SetValueAndUnit(215.0, 4)        # 4 = °C 的整数代码
print(node.Value, node.UnitString)    # 立刻回读校验
```

## 能力边界（实测结论，避免走死路）

- 流股标量（TEMP/PRES/VFRAC/ENTHALPY）**部分**可读：`Output\TEMP_OUT\MIXED`、
  `PRES_OUT\MIXED`、`VFRAC_OUT\MIXED` 均实测可读（引擎运行后）；拿不到时读上游块 Output。
- `Output\MASSFLOW\MIXED` = 1.0 是**报告开关 flag**，不是流量；组分流量读 `MASSFLOW3\<组分>`。
- 组分分率（MASSFRAC/MOLEFRAC）没有 MIXED 子节点可读；用组分质量流 ÷ 总质量流自算。
- 块 ID 是模型里定义的名字（MEOHCOL/ESTCOL/GLYCRCOL…），不是 B1/B2 序号。
- `BLKSTAT` 实测全为 0，**不可用作收敛标志**。

## 批量工况扫描模板

```python
import win32com.client, pythoncom, time
pythoncom.CoInitialize()
doc = win32com.client.Dispatch("Apwn.Document.40.0")
doc.SuppressDialogs = True
doc.InitFromArchive2(r"<path>\model.bkp", 0)
tree, eng = doc.Tree, doc.Engine


def val(path):
    try:
        n = tree.FindNode(path)
        return n.Value, n.UnitString
    except Exception:
        return None, None


for t_c in (205, 210, 215):
    tree.FindNode(r"Data\Blocks\REACTOR\Input\TEMP").SetValueAndUnit(t_c, 4)  # °C
    eng.Reinit()
    doc.Run2(1)
    while eng.IsRunning:
        time.sleep(2)
    print(t_c, val(r"Data\Streams\REAC-OUT\Output\MASSFLOW3\OLEIC"))

doc.Close(0)
pythoncom.CoUninitialize()
```

> 生产环境用 `scripts/aspen_com_run.py`（参数化，支持从 CSV/JSON 读工况表）。
> 每约 12 个工况重开一次 doc，规避 RPC 内部错误；同一 doc 内不要反复重开。
