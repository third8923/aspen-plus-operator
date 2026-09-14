# Excel 插件三件套（选型与要点）

完整案例教学建议自建三个案例：甲醇回收塔灵敏度扫描（Sensitivity）、脂肪酸物性查询（APXL）、水解塔多工况批量运行（Calc+VBA）。

## ASW（Aspen Simulation Workbook）

- 把模型链接进 Excel，做案例研究表（Scenario/Active/Input/Output 行式布局）。
- 适合：批量灵敏度扫描、给操作人员的仪表盘。
- 安装位置含 `AspenSimulationWorkbook.xla` / `AspenOSEWorkbook.xla` + ASWXL Addin。

## APXL（Aspen Properties Excel Add-in）

- 函数前缀 `APXL_`，按官方 properties.xls 的单元格标签布局（Package/Components/状态/方法）自动算物性。
- 适合：设计期查物性（脂肪酸/甘油/甲醇体系 300 K / 1 atm 液相样例见教学文档）。

## Calc Excel Add-in + VBA

- `CreateObject("Apwn.Document.40.0")` 与 Python COM 是同一对象模型。
- 适合：把批量运行固化成 Excel 宏工具。

```vb
Sub RunCases()
    Dim apwn As Object
    Set apwn = CreateObject("Apwn.Document.40.0")
    apwn.SuppressDialogs = True
    apwn.InitFromFile Cells(5, 1).Value
    apwn.Engine.Reinit
    apwn.Run2 1
    Do While apwn.Engine.IsRunning
        DoEvents
    Loop
    Cells(5, 3).Value = apwn.Tree.FindNode( _
        "\Data\Streams\PRODUCT\Output\MASSFLOW3\MEOLEATE").Value
    apwn.Close
End Sub
```
