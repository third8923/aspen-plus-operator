# 单位制：原生 SI 切换与英制→SI 换算

2026-09 实测确认：**Aspen Plus V14 原生支持 SI 单位制**，不需要全部手工换算。默认模板是英制（ENG），但可切换内置 SI 单位集；切换后 COM 读取 Output（引擎结果）自动返回 SI 值。

## 一、单位集机制（实测）

- bkp 文本里全局单位集由 `? SETUP GLOBAL ? \ "IN-UNITS" INSET = X \` 控制。本机 V14 已定义单位集：ENG（默认）、MET、METCBAR、METCKGCM、**SI-CBAR**、SI。
- SI-CBAR 定义为 `UNITSET BASESET = SI (...)`，即"SI 基准 + °C + bar + /hr"单位组合，最贴合国内工程习惯。
- **切换方法**：
  1. bkp 文本层：把 `"IN-UNITS" INSET = ENG` 替换为 `INSET = SI-CBAR` 保存即生效（无需开 GUI）。
  2. GUI：Setup → Units-Sets（Setup/Global 的 Units 下拉）选 SI-CBAR；新建文件时选带 Metric 的模板（File → New → 如 "General with Metric Units"）。
- 引擎内部存储永远是英制（bkp 文本带单位代码 `<22>`=°F、`<20> <2>`=psi、`<-89>`=lbmol/hr），**INSET 只影响 GUI 显示与 COM 读取 Output 时的换算，不影响文本层存储**。

## 二、COM 读写行为（实测对照，同一模型只切 INSET）

| 读出项（节点） | ENG | SI-CBAR | SI |
|-|-|-|-|
| 组分质量流 `Output\MASSFLOW3\<组分>` | lb/hr（如 OLEIC 4144.4） | **kg/hr（1879.87）** | kg/s（0.5222） |
| 总摩尔流 `Output\L1_FLOW` | lbmol/hr（59.166） | **kmol/hr（26.837）** | kmol/s（0.007455） |
| 热负荷 `Blocks\<块>\Output\QCALC` | Btu/hr（−1123542.9） | **W（−329277.9）** | W（−329277.9） |
| 块温度 `Blocks\<块>\Output\R_TEMP` | °F（419） | **°C（215.0）** | K（488.15） |
| 汽化率 `Streams\<流股>\Output\VFRAC_OUT\MIXED` | 无量纲 | 不变 | 不变 |
| **Input 读回**（`Input\TEMP\MIXED` 等） | 原始存储值 220.6 | **仍是 220.6（=220.6°F，不换算）** | 220.6 |

**结论（三条铁律，2026-09 补充写参数实测）**：
1. **读 Output（取数）**：SI-CBAR 下直接是 °C / kg/hr / kmol/hr / W——**零换算**。SI 下更基准（K / kg/s / kmol/s）。
2. **写 Input（改参数）**：COM 节点**没有 Units 属性**，Value 永远按 bkp 内部英制解释——实测铁证：SI-CBAR 下写 REACTOR Input TEMP Value=215.0，引擎按 **215°F** 跑（R_TEMP 显示 101.7°C = 215°F）。所以 COM 写参数不可能"界面直接填 SI"。
3. **解决办法（业务层全 SI）**：用脚本封装模板 `scripts/aspen_com_run_si.py`——业务代码只写 SI（°C/bar/kmol/h），`set_temp/set_pres/set_flow` 内部自动换算英制再写；读结果也用 `get_*` 返回 SI。**你写的、日志输出的全是 SI，英制只存在于封装函数一行里，不可见。**

## 三、换算表（ENG 取值 + 手工换算备用）

| 物理量 | Aspen ENG | 中国常用（SI） | 换算系数 |
|-|-|-|-|
| 温度 | °F | °C / K | °C=(°F-32)×5/9；K=°C+273.15 |
| 压力 | psia | MPa / bar / kPa | 1 psia=6.8948 kPa=0.06895 bar=0.006895 MPa |
| 质量流量 | lb/hr | kg/h / t/h | 1 lb/hr=0.45359 kg/h |
| 摩尔流量 | lbmol/hr | kmol/h | 1 lbmol/hr=0.45359 kmol/h |
| 热负荷 | Btu/hr | kW / kJ/h | 1 Btu/hr=1.05506 kJ/h=0.0002931 kW |
| 体积流量 | cuft/hr | m³/h | 1 cuft=0.02832 m³ |
| 密度 | lb/cuft | kg/m³ | 1 lb/cuft=16.018 kg/m³ |
| 比焓 | Btu/lb | kJ/kg | 1 Btu/lb=2.326 kJ/kg |

## 四、处理原则（国内工程实践，2026-09 更新）

- **首选：SI-CBAR 单位集取数**。建模时把 bkp 的 INSET 置 `SI-CBAR`，COM 取 Output 直接是 kg/hr / °C / bar / W，免去手工换算与单位错配风险（历史踩过 1000 倍量纲错误）。
- **写参数用 `scripts/aspen_com_run_si.py` 封装**：业务层全 SI（set_temp °C / set_pres bar / set_flow kmol-h），引擎英制转换收敛在封装函数，用户全程看不见英制。严禁在业务代码里手写 419/267 这类英制裸值。
- **GUI 全 SI**：Setup → Units-Sets 选 SI-CBAR 后，界面输入框、报告、数据浏览器全部 °C/bar/kg/hr——GUI 建模型/改参数天然无英制。
- **SI-CBAR 热负荷单位是 W**：QCALC 读出 −329277.9 W = −329.28 kW，汇报时 ÷1000。
- **GUI 显示**：Setup → Units-Sets 选 SI-CBAR 后，界面、报告、数据浏览器全部 SI。
- **汇报交付**：面向国内一律 SI（°C/kPa/kg/h/kW）；与美国工程公司交换时保留原值并标注单位。
- **bkp 交换**：单位集随模型保存，换机打开不变；文本层永远英制，直接改文本参数必须用英制代码单位。
