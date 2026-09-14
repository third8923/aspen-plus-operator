# aspen-plus-operator

Aspen Plus V14 自动化操作技能包：COM 批量建模 / bkp 文本层诊断 / GUI 启动纪律 / 单位制（SI）切换 / 单元块格式库。

沉淀自脂肪酸产业链（水解 / 精馏 / 生物柴油）生产建模实战，面向想用代码高效驱动 Aspen Plus 的工艺工程师与开发者。

## 为什么会有这个项目

Aspen Plus 的传统用法是纯 GUI 点击，批量工况扫描、参数寻优、多模型维护都非常慢。本项目把这套工作拆成三个可编程通道，并固化了一条条实测结论（含踩坑记录），让"建模—扫描—寻优—汇报"全流程可复现：

| 通道 | 干什么 | 速度 | 典型场景 |
|-|-|-|-|
| COM 自动化 | Python 驱动本机引擎：开模型、改参数、运行、取数 | 最快（秒级/工况） | 批量工况扫描、参数寻优、自动出数 |
| bkp 文本层 | 读写 bkp 文本：看结构、修损坏模型 | 即时 | 模型诊断修复、配置速查 |
| GUI 手工 | 在可见桌面打开软件界面操作 | 慢 | 单点操作、教学演示、看引擎报错提示 |

## 核心资产

- **标准块格式库**：14 种单元操作（PUMP / COMPR / VALVE / FSPLIT / MIXER / FLASH2 / HEATER / FLASH3 / SEP / HEATX / PIPE / REQUIL / RGibbs / RCSTR / RPLUG）的 bkp 文本层写法，从官方示例提取、逐条引擎实测
- **块替换三件套**：注册段 + FLOWSHEET 行 + 块定义段，缺一无效（"Required input incomplete" 的常见根因）
- **COM 运行协议**：`Reinit → Run2(1) → 轮询 IsRunning`，漏 Reinit 引擎空转
- **单位制铁律**：Aspen 原生支持 SI 单位集（SI-CBAR 读 Output 零换算）；写 Input 恒按引擎英制（封装函数收敛转换）
- **GUI 启动纪律**：GUI 必须启动在用户可见会话（computer_use 通道），禁止命令行直启到不可见会话
- **Design-Spec / Convergence 完整格式**：DEFINE→SPEC→TOL→VARY→LIMITS 四段式
- **POWERLAW 动力学格式**：酯交换三步可逆动力学参数（PRE-EXP / ACT-ENERGY / T-REF）
- **版本演进地图**：V7.3→V14 关键能力跃迁、Ribbon 菜单映射、兼容性三查、碳核算（scope 1/2）

## 环境要求

- Windows（x64）
- Aspen Plus V14（COM 对象 `Apwn.Document.40.0`；V11 起 64 位程序，第三方 DLL 必须 64 位编译）
- Python 3.8+，`pip install pywin32`
- 模型 bkp 建议 INSET=SI-CBAR（读 Output 免换算）

## 快速开始

```bash
pip install pywin32

# 1. COM 批量工况扫描（模板）
python scripts/aspen_com_run.py <模型.bkp> <工况表.json>

# 2. COM 全 SI 封装（业务层只写 °C / bar / kmol/h）
python scripts/aspen_com_run_si.py
```

工况表 JSON 示例（`aspen_com_run.py`）：

```json
{
  "blocks": {"SEP1": {"TEMP": ["110", "120", "130", "140"]}},
  "read": [
    {"name": "FAME", "path": "Data\\Streams\\PRODUCT\\Output\\MASSFLOW3\\MEOLEATE"},
    {"name": "MEOH", "path": "Data\\Streams\\RECYCLE\\Output\\MASSFLOW3\\METHANOL"}
  ],
  "output": "results.csv"
}
```

## 目录结构

```
aspen-plus-operator/
├── SKILL.md                      # 主技能：工作流 + 模块 0-10 实测结论
├── references/
│   ├── com-automation.md         # COM 连接、运行协议、变量读写矩阵、能力边界
│   ├── bkp-diagnostics.md        # bkp 结构速览、进料段修复、单位代码表、精馏塔建模速查
│   ├── gui-operation.md          # GUI 启动纪律、排错、提速、验证
│   ├── units-si-conversion.md    # 单位集机制、COM 读写行为、换算表
│   └── excel-addins.md           # ASW / APXL / Calc+VBA 三插件选型
└── scripts/
    ├── aspen_com_run.py          # COM 批量工况扫描模板（参数化）
    ├── aspen_com_run_si.py       # COM 全 SI 封装模板（业务层零英制）
    └── unit_convert.py           # 英制→SI 换算函数库
```

## 文档导航

- `SKILL.md`：先读这个。工作流 → 可复用脚本 → 模块 0-10 实测经验（环境地图 / 组分物性 / 单元操作 / 收敛优化 / 动力学 / 特殊体系 / 经济能量 / 工具联动 / GUI 专项 / 综合实战 / 版本演进）
- `references/`：按需读取的专项手册
- 官方离线帮助（本机安装）：`C:\ProgramData\AspenTech\Aspen Plus V14.0\HtmlHelp\`（113 子系统 / 9764 页，含 V7.3 起每代 What's New 与 Compatibility Notes）

## 注意事项

- 文中所有工况数值均为**模拟示例数据**，用于演示方法；落地前请用贵司真实数据替换
- COM 写参数恒按引擎英制（°F / psia / lb-hr），单位集只影响读回显示——业务层务必用 SI 封装函数，防止 1000 倍量纲错误
- 高压含水体系（2-6 MPa）的物性方法选择是生死线：NRTL 族与蒸汽表自洽，SRK/UNIF-DMD 族对水饱和压偏保守（放大约 1.5-2 倍），结论按蒸汽表 Psat 复核
- 本项目与 AspenTech 无任何关联；Aspen Plus 是 AspenTech 的注册商标

## License

MIT License。详见 [LICENSE](LICENSE)。
