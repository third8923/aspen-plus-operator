# COM 自动化（主通道）

本机实测（Aspen Plus V14，ProgID `Apwn.Document.40.0`）。

## 连接与生命周期

```python
import win32com.client, pythoncom
pythoncom.CoInitialize()
doc = win32com.client.Dispatch("Apwn.Document.40.0")
doc.SuppressDialogs = True            # 必须：抑制引擎弹窗，防不可见会话挂起
doc.InitFromFile(r"<workspace>\biodiesel_example.bkp")
tree = doc.Tree
# ... 改参、运行、取数 ...
doc.SaveAs2(r"<workspace>\output.bkp")  # 保存运行结果
doc.Close()
pythoncom.CoUninitialize()
```

## 运行协议（顺序不能错）

唯一有效序列：**Reinit → Run2(1) → 轮询 IsRunning**。

```python
eng = doc.Engine
eng.Reinit()                  # 必须先重初始化，漏掉会引擎空转（Ready 但不出数）
doc.Run2(1)                   # 同步运行
import time
while eng.IsRunning:
    time.sleep(2)
```

已验证无效的其它运行方式：ExecuteScript / Solve / Step / RunControl 均不可用。

## 变量读写矩阵（全部实测有效）

| 用途 | 节点路径 | 单位 | 说明 |
|-|-|-|-|
| 改进料温度 | `Data\Streams\<流股>\Input\TEMP\MIXED` | 模型单位 | 输入可写 |
| 改块温度/压力 | `Data\Blocks\<块>\Input\TEMP` / `PRES` | °F / psia | 写后需 Reinit+Run2 生效 |
| 改反应转化率 | `Data\Blocks\REACTOR\Input\CONV\1` | - | RStoic 第 1 个反应转化率 |
| 读组分质量流 | `Data\Streams\<流股>\Output\MASSFLOW3\<组分>` | lb/hr | 最常用输出 |
| 读液相摩尔流 | `Data\Streams\<流股>\Output\L1_FLOW` | lbmol/hr | 全液相流股总摩尔流量 |
| 读块热负荷 | `Data\Blocks\<块>\Output\QCALC` | Btu/hr | 反应器/换热器 DUTY |
| 读块气相分率 | `Data\Blocks\<块>\Output\VFRAC` | - | 判断闪蒸是否两相区 |

## 能力边界（实测结论，避免走死路）

- 流股标量（TEMP/PRES/VFRAC/ENTHALPY）在 COM 树中不存在，不可读；需要温度读上游块 Output。
- `Output\MASSFLOW=1.0` 是报告开关 flag，不是流量值；总摩尔流量读 L1_FLOW 或按组分 MASSFLOW3 累加。
- 组分分率（MASSFRAC/MOLEFRAC）没有 MIXED 子节点可读；用组分质量流 ÷ 总质量流自行计算。
- 块 ID 决定路径：块名是模型里定义的（如 MEOHCOL/ESTCOL/GLYCRCOL），不是 B1/B2 序号。

## 批量工况扫描模板

```python
import win32com.client, pythoncom, time
pythoncom.CoInitialize()
doc = win32com.client.Dispatch("Apwn.Document.40.0")
doc.SuppressDialogs = True
doc.InitFromFile(r"<workspace>\biodiesel_example.bkp")
tree = doc.Tree; eng = doc.Engine

def getval(path):
    try:
        return tree.FindNode(path).Value
    except Exception:
        return None

for temp in [110, 120, 130, 140]:
    tree.FindNode(r"Data\Blocks\SEP1\Input\TEMP").Value = temp
    eng.Reinit(); doc.Run2(1)
    while eng.IsRunning:
        time.sleep(2)
    print(temp, "FAME=", getval(r"Data\Streams\PRODUCT\Output\MASSFLOW3\MEOLEATE"),
          "MEOH=", getval(r"Data\Streams\RECYCLE\Output\MASSFLOW3\METHANOL"))
doc.Close(); pythoncom.CoUninitialize()
```

> 生产环境用 `scripts/aspen_com_run.py`（参数化，支持从 CSV/JSON 读工况表）。
