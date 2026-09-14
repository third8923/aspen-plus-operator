# bkp 文本层诊断与修复

bkp 是文本文件，可直接搜索关键段，无需打开 GUI。

## 模型结构速览

| 找什么 | 搜什么 |
|-|-|
| 块清单 | `BLOCK BLKID = xxx BLKTYPE = "RADFRAC"` |
| 流股连接 | `IN = ... / OUT = ...` |
| 块参数 | `PARAM NSTAGE / TEMP / PRES` |
| 报告选项 | `STREAM-REPOR` |

内置工厂实例（convtest）：MEOHCOL（甲醇回收塔，NSTAGE=7，CONDENSER=TOTAL，进料 REACOUT，塔顶出 MEOHREC）、ESTCOL（酯化塔，NSTAGE=6，CONDENSER=PARTIAL-V-L，出 FAME）、GLYCRCOL（甘油塔，NSTAGE=6，CONDENSER=TOTAL，出 GLYCEROL）。

## 修复经验：进料段缺失

引擎报 **ZERO FEED TO THE BLOCK** 时，根因通常是 FEED 段嵌在 STREAM-GROUP DESCRIPTION 里、缺 `STREAM MATERIAL` 前缀。

修复：把 FEED 独立成段并补齐 DESCRIPTION 结束符，引擎即可识别进料（280 lbmol/h 进料经此修复后全流程跑通）。

## 配置提取

RadFrac 的进料板、冷凝器类型、设计规定（如「Bottoms rate, 25, 250」）都能在文本层直接搜到，适合不打开 GUI 快速核对塔配置。

运行后的 bkp 里 STREAM-REPOR 是报告选项段；完整流股结果需配合 COM 取数或打开报告。

## 单位在 bkp 中的记录（实测破译，重要）

单位随模型保存，文本层用**双单位代码**记录 `值 <类别> <子单位>`：

| 代码 | 含义 |
|-|-|
| `<22> <2>` | 温度，°F（TEMP/T1 等） |
| `<20> <2>` | 压力，**psi**（PRES / STAGE-PRES / PRES1） |
| `<20> <5>` | 压力，**bar**（误用会把 0.334 读成 0.334 bar=33 kPa，导致「FEED PRESSURE LOWER THAN STAGE」） |
| `<-80> <3>` | 质量流量基准，**kg/hr**（BASIS-D / BASIS-B） |
| `<-89> <0/2>` | 摩尔流量基准，lbmol/hr（TOTAL / MOLE-FLOW） |
| `<75> <5>` | 压降，psi（DP-COL） |

**教训**：`<20> <5>` 与 `<20> <2>` 差 14.5 倍，压力写错一个代码塔压差一个量级。COM 输出全是英制（°F/psia/lb/hr/Btu/hr），交付 SI 必须换算。

## RadFrac 真空精馏塔建模速查（实测沉淀）

### 段标记与换行（决定性规则）
- 段名行首**必须有 `? `**（`? STREAM MATERIAL FEED ? ; "ENG_MOLE" ; \`），缺了流股会被吞进前一段 PROPERTIES；
- 列表项 `/` **后必须换行**（组分 `CID = X / CID = \nY`、流股 `MOLE-FLOW ... / SSID1 = \n`、产品 `PROD-PHASE = L / PROD-STREAM = \n`）；
- 塔段换行照 convtest 抄：`PARAM \n`、`/  \nPROD-STREAM`、`PRES-STAGE = 1 \nSTAGE-PRES`、`"COL-SPECS" \nBASIS-RDV`——否则报「不匹配的引号」。

### 塔规格两种模式
| 模式 | 写法 | 适用 |
|-|-|-|
| 双流量规格 | `D-BASIS = MASS BASIS-D = 10000 <-80> <3> RR-BASIS = MASS BASIS-RR = 2.0` | **最稳，直接收敛**；D 单位是 **kg/hr** |
| 设计规定 | `B-BASIS + RR + SPEC(MASS-RECOV/MASS-FRAC) + VARY(VARTYPE = B LB/UB)` | convtest 模式；**必须带 B-BASIS 初值**，否则 Ready=False |

**D-BASIS 设多少塔顶就采多少**（收率主控）；RR 只影响再沸器热负荷（蒸汽主控）。

### 塔不收敛的根因排查顺序
1. **「FEED PRESSURE LOWER THAN STAGE n」** → 压力单位代码写错（`<20> <5>` 误用），修 `<20> <2>`；
2. **塔顶 D≈0、无蒸气** → 进料温度低于轻关键组分泡点（油酸在 2.3 kPa 泡点约 250–280 °C，进料须高于它）；
3. **「COLUMN NOT IN MASS BALANCE / STAGES DRIED UP」** → 规格超出塔能力（如 12 板要求 95% 回收，而油酸/硬脂酸相对挥发度仅 ~1.01 需数百理论板）→ **把规格降到与塔板数匹配**（12 板收率约 50–76%），或用 D-BASIS 直接给定采出量；
4. **重组分太重**（如三油酸甘油酯 MW 885，塔底泡点 440 °C+）→ 塔底温度爆表必不收敛，换工艺上真实的塔底组分（硬脂酸，塔底 ~237 °C）。

### 假组分定义陷阱
`replace` 换组分名时**分子式、库名必须同步**：`ANAME / DBNAME1 / ANAME1` 三件套都改，否则引擎按旧分子式算分子量（如把 STEARIC 按 C57H104O6=885 算），物料平衡表面错乱。正确例：`CID = STEARIC ANAME = C18H36O2 OUTNAME = STEARIC DBNAME1 = "N-OCTADECANOIC-ACID" ANAME1 = "C18H36O2"`。

### 收敛硬证据（COM 可读）
- 物料平衡：`BAL_MASI_TFL`（进料总质量）= `BAL_MASO_FLW`（出料总质量），`BAL_MASR_TFL` 残差 < 1e-6 → **塔真收敛**；
- 塔顶温度：`Data\Streams\D\Output\TEMP_OUT\MIXED`（°F）；
- 塔底温度：`Data\Blocks\TOWER\Output\REB_TOUT`（°F）——**红线验证看它**（油酸塔 ≤265 °C）；
- 热负荷：`REB_DUTY`（+）/ `COND_DUTY`（−），单位 Btu/hr。

